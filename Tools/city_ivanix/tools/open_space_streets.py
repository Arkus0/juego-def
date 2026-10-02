"""Street centrelines as the medial axis of the town's open space (everything not built and not a garden, paved or
not), pruned of the spurs that run into gaps between houses, merged into streets and smoothed. Each street carries a
stable tangent and a local half width, so the parcel pass can lay facades on centreline +- half width.
"""

import json
import os
import math
from pathlib import Path

import cv2
import networkx as nx
import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from skimage.morphology import skeletonize

ROOT = Path(__file__).resolve().parents[1]
# the layout captures are not redistributed: point JD_IVX_REFS at the local survey folder's references/
REFS = Path(os.environ.get("JD_IVX_REFS", str(ROOT / "references")))
RES = 0.5            # m per raster pixel
PRUNE_M = 12.0       # spurs shorter than this are gaps between houses, not streets
MIN_HW = 1.4         # narrower than 2.8 m is not a street


def poly(p):
    shp = Polygon(p["outer"], [h for h in p["holes"] if len(h) >= 3])
    return shp if shp.is_valid else shp.buffer(0)


def chaikin_open(P, it=3):
    P = np.asarray(P, float)
    for _ in range(it):
        if len(P) < 3:
            return P
        q = 0.75 * P[:-1] + 0.25 * P[1:]
        r = 0.25 * P[:-1] + 0.75 * P[1:]
        new = np.empty((len(q) * 2, 2))
        new[0::2], new[1::2] = q, r
        P = np.vstack([P[0], new, P[-1]])
    return P


def open_space(tr, town, ante=None, extra_blocked=None):
    masses = unary_union([Polygon(m["outline"]).buffer(0) for m in tr["built_masses"]])
    roofs = unary_union([Polygon(r["rect"]).buffer(0) for r in tr["roofs"]])
    green = unary_union([poly(p) for p in tr["yards_green"]])
    area = town if ante is None else town.union(ante)
    blocked = unary_union([masses.buffer(0.4), roofs.buffer(0.2), green.buffer(-0.5)])
    if extra_blocked is not None:
        blocked = blocked.union(extra_blocked)
    sp = area.difference(blocked)
    # open/close: slivers between packed houses are not streets
    return sp.buffer(-0.9).buffer(0.9).buffer(0.6).buffer(-0.6)


def streets(open_poly, tan_m=7.0):
    minx, minz, maxx, maxz = open_poly.bounds
    W, H = int((maxx - minx) / RES) + 3, int((maxz - minz) / RES) + 3
    mask = np.zeros((H, W), np.uint8)
    geoms = list(open_poly.geoms) if hasattr(open_poly, "geoms") else [open_poly]
    to_px = lambda q: (int(round((q[0] - minx) / RES)) + 1, int(round((maxz - q[1]) / RES)) + 1)
    for g in geoms:
        cv2.fillPoly(mask, [np.array([to_px(q) for q in g.exterior.coords], np.int32)], 1)
        for h in g.interiors:
            cv2.fillPoly(mask, [np.array([to_px(q) for q in h.coords], np.int32)], 0)
    dist = cv2.distanceTransform(mask, cv2.DIST_L2, 5) * RES
    sk = skeletonize(mask > 0)
    ys, xs = np.nonzero(sk)
    G = nx.Graph()
    S = set(zip(ys.tolist(), xs.tolist()))
    for (y, x) in S:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if (dy or dx) and (y + dy, x + dx) in S:
                    G.add_edge((y, x), (y + dy, x + dx), w=math.hypot(dy, dx) * RES)

    def chains(G):
        """Maximal paths between nodes of degree != 2."""
        out, seen = [], set()
        ends = [n for n in G.nodes if G.degree(n) != 2]
        for a in ends:
            for nb in G.neighbors(a):
                if (a, nb) in seen:
                    continue
                path = [a, nb]
                seen.add((a, nb)); seen.add((nb, a))
                while G.degree(path[-1]) == 2:
                    nxt = [q for q in G.neighbors(path[-1]) if q != path[-2]]
                    if not nxt:
                        break
                    seen.add((path[-1], nxt[0])); seen.add((nxt[0], path[-1]))
                    path.append(nxt[0])
                    if path[-1] == a:
                        break
                out.append(path)
        return out

    def plen(path):
        return sum(math.hypot(path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1]) for i in range(1, len(path))) * RES

    for _ in range(12):
        removed = False
        for path in chains(G):
            leaf = G.degree(path[0]) == 1 or G.degree(path[-1]) == 1
            if leaf and plen(path) < PRUNE_M:
                inner = path[1:-1] if G.degree(path[0]) != 1 else path[:-1]
                if G.degree(path[-1]) == 1:
                    inner = path[1:] if G.degree(path[0]) != 1 else path
                G.remove_nodes_from([q for q in inner if q in G and G.degree(q) <= 2])
                removed = True
        G.remove_nodes_from([n for n in list(G.nodes) if G.degree(n) == 0])
        if not removed:
            break
    res = []
    for path in chains(G):
        if plen(path) < 6.0:
            continue
        P = np.array([[minx + (x - 1) * RES, maxz - (y - 1) * RES] for (y, x) in path])
        hw = np.array([dist[y, x] for (y, x) in path])
        if np.median(hw) < MIN_HW:
            continue
        P = chaikin_open(P[:: max(1, int(1.0 / RES))], 3)
        ls = LineString(P).simplify(0.8)
        n = max(2, int(ls.length // 1.0))
        R = np.array([ls.interpolate(k * ls.length / n).coords[0] for k in range(n + 1)])
        k = int(tan_m)
        T = np.array([R[min(len(R) - 1, i + k)] - R[max(0, i - k)] for i in range(len(R))])
        T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-6)
        N = np.stack([-T[:, 1], T[:, 0]], axis=1)
        hwR = []
        for q in R:
            px_ = to_px(q)
            yy, xx = min(H - 1, max(0, px_[1])), min(W - 1, max(0, px_[0]))
            hwR.append(dist[yy, xx])
        hwR = np.array(hwR)
        hwR = np.array([np.median(hwR[max(0, i - 5): i + 6]) for i in range(len(hwR))])
        seg = np.linalg.norm(np.diff(R, axis=0), axis=1)
        res.append({"pts": R, "tan": T, "nor": N, "hw": np.clip(hwR, MIN_HW, 15.0), "s": np.concatenate([[0.0], np.cumsum(seg)]), "len": float(seg.sum())})
    return res


if __name__ == "__main__":
    tr = json.loads((ROOT / "reconstruction" / "layout_trace_v1.json").read_text(encoding="utf-8"))
    seed = json.loads((ROOT / "reconstruction" / "city_seed_v4.json").read_text(encoding="utf-8"))
    ring = [(q[0], q[2]) for q in seed["river_wall"]["points"]]
    town = Polygon(ring).buffer(0).buffer(-2.4)
    op = open_space(tr, town)
    st = streets(op)
    print("streets", len(st), "total m", round(sum(x["len"] for x in st)))
    img = cv2.imread(str(REFS / "originals" / "REF0017H_city_cenital_calibrated_3840.png"))
    PL, M = (2200, 790), 0.16333
    px = lambda x, z: (int(round(PL[0] + x / M)), int(round(PL[1] - z / M)))
    vis = (img * 0.5).astype(np.uint8)
    for k, x in enumerate(st):
        col = [(0, 255, 255), (255, 128, 0), (0, 255, 0), (255, 0, 255), (0, 128, 255)][k % 5]
        cv2.polylines(vis, [np.array([px(*q) for q in x["pts"]], np.int32)], False, col, 3)
        for sgn in (-1, 1):
            E = x["pts"] + x["nor"] * x["hw"][:, None] * sgn
            cv2.polylines(vis, [np.array([px(*q) for q in E], np.int32)], False, (255, 255, 255), 1)
    for name, (x0, y0, x1, y1) in {"center": (1800, 300, 3000, 1300), "all": (700, 150, 3200, 1700)}.items():
        o = vis[y0:y1, x0:x1]
        if name == "all":
            o = cv2.resize(o, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(ROOT / "reconstruction" / f"openstreets_{name}.png"), o)

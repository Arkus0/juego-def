"""Street frontage lines for the parcel pass: the edge of the public space (streets, plazas, unpaved aprons), smoothed so
it reads as a built street wall, split into tramos where it turns sharply; each point carries the local tangent.

Used by city_seed_v4 (parcelisation + street frontage) and drawn over the capture for review.
"""

import json
import os
import math
from pathlib import Path

import cv2
import numpy as np
from shapely.geometry import LineString, MultiLineString, Point, Polygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
# the layout captures are not redistributed: point JD_IVX_REFS at the local survey folder's references/
REFS = Path(os.environ.get("JD_IVX_REFS", str(ROOT / "references")))
TRACE = ROOT / "reconstruction" / "layout_trace_v1.json"


def poly(p):
    shp = Polygon(p["outer"], [h for h in p["holes"] if len(h) >= 3])
    return shp if shp.is_valid else shp.buffer(0)


def chaikin(coords, it=2, closed=True):
    pts = np.array(coords, float)
    for _ in range(it):
        a = pts
        b = np.roll(pts, -1, axis=0) if closed else pts[1:]
        a2 = a if closed else pts[:-1]
        q = 0.75 * a2 + 0.25 * b
        r = 0.25 * a2 + 0.75 * b
        new = np.empty((len(q) * 2, 2))
        new[0::2], new[1::2] = q, r
        pts = new if closed else np.vstack([pts[0], new, pts[-1]])
    return pts


def public_space(tr, ante=None, open_r=1.2, close_r=2.5, min_area=40.0):
    """The stone-paved streets and squares of the layout (the unpaved aprons between houses are not streets)."""
    paving = unary_union([poly(p) for p in tr["public_paving"] if p.get("area_m2", 99) >= min_area])
    pub = paving if ante is None else paving.union(ante)
    # opening drops paving slivers between packed houses, closing fills the notches the packing cut into the street
    pub = pub.buffer(-open_r).buffer(open_r).buffer(close_r).buffer(-close_r)
    return pub.simplify(1.0)


def frontage_lines(pub, town, wall, min_len=6.0, turn_deg=38.0):
    """Rings of the public space inside the town, without the stretches that run along the town wall; smoothed and
    split into tramos at sharp turns. Returns a list of dicts with 'pts' (N x 2) and 'tan' (N x 2), 'side' normal
    pointing INTO the public space."""
    rings = []
    geoms = list(pub.geoms) if hasattr(pub, "geoms") else [pub]
    for g in geoms:
        for ring in [g.exterior] + list(g.interiors):
            rings.append(np.array(ring.coords)[:-1])
    out = []
    for r in rings:
        if len(r) < 4:
            continue
        sm = chaikin(r, 2, closed=True)
        # resample every 1 m
        ls = LineString(np.vstack([sm, sm[:1]]))
        n = max(4, int(ls.length // 1.0))
        pts = np.array([ls.interpolate(i * ls.length / n).coords[0] for i in range(n)])
        keep = np.array([town.buffer(0.5).contains(Point(*q)) and wall.distance(Point(*q)) > 3.2 for q in pts])
        # tangents (window +-3 m), and the normal pointing into the public space
        tan = np.roll(pts, -3, axis=0) - np.roll(pts, 3, axis=0)
        tan /= np.maximum(np.linalg.norm(tan, axis=1, keepdims=True), 1e-6)
        nor = np.stack([-tan[:, 1], tan[:, 0]], axis=1)
        probe = [pub.contains(Point(*(pts[i] + nor[i] * 0.8))) for i in range(len(pts))]
        nor[~np.array(probe)] *= -1
        # split into runs of kept points, then at sharp turns
        idx = np.where(keep)[0]
        if len(idx) == 0:
            continue
        runs, cur = [], [idx[0]]
        for a, b in zip(idx[:-1], idx[1:]):
            if b == a + 1:
                cur.append(b)
            else:
                runs.append(cur)
                cur = [b]
        runs.append(cur)
        if len(runs) > 1 and runs[0][0] == 0 and runs[-1][-1] == len(pts) - 1:
            runs[0] = runs[-1] + runs[0]
            runs.pop()
        for run in runs:
            seg = [run[0]]
            for k in range(1, len(run)):
                i0, i1 = run[k - 1], run[k]
                ang = math.degrees(math.acos(max(-1, min(1, float(np.dot(tan[seg[-1]], tan[i1]))))))
                if ang > turn_deg and len(seg) >= 3:
                    out.append(seg)
                    seg = [i1]
                else:
                    seg.append(i1)
            out.append(seg)
        out_lines = []
    lines = []
    for r in rings:
        pass
    return out, rings


def public_space_lanes(tr, open_r=1.6, close_r=2.0, min_area=60.0):
    """Streets including the unpaved lanes between houses (dirt), but not the green gardens."""
    paving = unary_union([poly(p) for p in tr["public_paving"]])
    yards = unary_union([poly(p) for p in tr["yards"]])
    green = unary_union([poly(p) for p in tr["yards_green"]])
    pub = unary_union([paving, yards.difference(green.buffer(0.5))])
    pub = pub.buffer(-open_r).buffer(open_r).buffer(close_r).buffer(-close_r)
    pub = unary_union([g for g in (pub.geoms if hasattr(pub, "geoms") else [pub]) if g.area >= min_area])
    return pub.simplify(1.0)


def build(tr, town, wall, ante=None):
    pub = public_space(tr, ante)
    return pub, lines_from(pub, town, wall)


def lines_from(pub, town, wall):
    lines = []
    geoms = list(pub.geoms) if hasattr(pub, "geoms") else [pub]
    for g in geoms:
        for ring in [g.exterior] + list(g.interiors):
            r = np.array(ring.coords)[:-1]
            if len(r) < 4:
                continue
            sm = chaikin(r, 3, closed=True)
            ls = LineString(np.vstack([sm, sm[:1]]))
            n = max(4, int(ls.length // 1.0))
            pts = np.array([ls.interpolate(i * ls.length / n).coords[0] for i in range(n)])
            tan = np.roll(pts, -4, axis=0) - np.roll(pts, 4, axis=0)
            tan /= np.maximum(np.linalg.norm(tan, axis=1, keepdims=True), 1e-6)
            nor = np.stack([-tan[:, 1], tan[:, 0]], axis=1)
            inside = np.array([pub.contains(Point(*(pts[i] + nor[i] * 0.8))) for i in range(len(pts))])
            nor[~inside] *= -1
            keep = np.array([town.buffer(0.5).contains(Point(*q)) and wall.distance(Point(*q)) > 3.2 for q in pts])
            # split at gaps of 'keep' and at sharp turns
            cur = []
            for i in range(len(pts)):
                if not keep[i]:
                    if len(cur) >= 4:
                        lines.append(cur)
                    cur = []
                    continue
                if cur:
                    ang = math.degrees(math.acos(max(-1.0, min(1.0, float(np.dot(tan[cur[-1][0]] if False else tan[i - 1], tan[i]))))))
                    if ang > 14.0:     # 4 m tangent window: > 14 deg per metre is a corner
                        if len(cur) >= 4:
                            lines.append(cur)
                        cur = []
                cur.append((i, pts[i], tan[i], nor[i]))
            if len(cur) >= 4:
                lines.append(cur)
    res = []
    for ln in lines:
        P = np.array([c[1] for c in ln])
        T = np.array([c[2] for c in ln])
        N = np.array([c[3] for c in ln])
        seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
        L = float(np.sum(seg))
        if L >= 5.0:
            res.append({"pts": P, "tan": T, "nor": N, "len": L, "s": np.concatenate([[0.0], np.cumsum(seg)])})
    return res


if __name__ == "__main__":
    tr = json.loads(TRACE.read_text(encoding="utf-8"))
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    seed = json.loads((ROOT / "reconstruction" / "city_seed_v4.json").read_text(encoding="utf-8"))
    ring = [(q[0], q[2]) for q in seed["river_wall"]["points"]]
    town = Polygon(ring).buffer(0)
    wall = LineString(ring + [ring[0]])
    ante = Polygon(seed["antepuerto"])
    pub, lines = build(tr, town, wall, ante)
    print("frontage lines", len(lines), "total m", round(sum(l["len"] for l in lines)))
    img = cv2.imread(str(REFS / "originals" / "REF0017H_city_cenital_calibrated_3840.png"))
    PL, M = (2200, 790), 0.16333
    px = lambda x, z: (int(round(PL[0] + x / M)), int(round(PL[1] - z / M)))
    vis = (img * 0.55).astype(np.uint8)
    for k, l in enumerate(lines):
        col = [(0, 255, 255), (255, 128, 0), (0, 255, 0), (255, 0, 255), (0, 128, 255)][k % 5]
        cv2.polylines(vis, [np.array([px(*q) for q in l["pts"]], np.int32)], False, col, 3)
        for i in range(0, len(l["pts"]), 4):
            q = l["pts"][i]
            cv2.line(vis, px(*q), px(*(q + l["nor"][i] * 2.0)), (255, 255, 255), 1)
    for name, (x0, y0, x1, y1) in {"center": (1800, 300, 3000, 1300), "all": (700, 150, 3200, 1700)}.items():
        o = vis[y0:y1, x0:x1]
        if name == "all":
            o = cv2.resize(o, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(ROOT / "reconstruction" / f"frontage_{name}.png"), o)

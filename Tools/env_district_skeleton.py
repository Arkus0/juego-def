"""CASCO district skeleton: authored trace + real reference -> Unity district spec (WP-PROD-ENV-01).

The trace (Env/Specs/districts/<id>.trace.json) is an authored, simplified street network drawn over the measured
reference (owner 2026-09-28: the reference is the soul of the casco, not a 1:1 trace): nodes with heights, streets
with a hierarchy role, plazas, the river. This tool derives everything else so the district is built from data:

  * street space (street/plaza buffers), the river channel, the urban blocks between them (cleaned: acute tips
    chamfered into a narrow "prow" plot, junction bevels removed);
  * one facade row per block edge, facing its street, with the corner rule at every block vertex (corner building
    with an exposed side, mitred tip at a bend, concave notch) and plots taken from the real plot subdivision (OSM
    footprints projected on the edge: frontage widths, depth, storeys, setback jogs), fitted to 2 m kit bays;
  * the terrain: street heights interpolated between authored nodes, a smooth surface everywhere else; building
    floors on it with a stone base down to the lowest ground around them (sloping streets, river walls);
  * heightfield ground meshes by paving zone (flag bands along facades, setts, lanes, plazas, yards, outer ring);
  * stairs, bridges, river walls/parapets, plaza dressing anchors;
  * grade shares by network length (owner rule 70 % comfortable / 20 % perceptible / 10 % strong-or-stairs).

    python Tools/env_district_skeleton.py --trace Unity/JuegoDef/Assets/JuegoDef/Env/Specs/districts/ENV01_Casco_District.trace.json \
        --osm <scratch>/osm.json --out Unity/JuegoDef/Assets/JuegoDef/Env/Specs/districts/ENV01_Casco_District.json \
        --plan Docs/evidence/WP-PROD-ENV-01/reference/casco_district_skeleton.png --metrics <scratch>/district_metrics.json

Needs numpy, Pillow and shapely >= 2.1. OSM extracts stay out of the repo; the spec carries the attributions.
"""
import argparse
import json
import math
import os
import random
import sys

import numpy as np
import shapely
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box as sbox
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(__file__))
from env_morphology import Frame  # noqa: E402
from env_district import load, grade_class  # noqa: E402

RANK = {"main": 3, "plaza": 3, "secondary": 2, "lane": 1, "steps": 1, "bridge": 2, "footbridge": 1, "river": 1, "boundary": 0}
PALETTES = [("core_lime_chestnut", 30), ("core_sandstone_chestnut", 25), ("core_ochre_chestnut", 15),
            ("core_lime_oxblood", 15), ("core_cream_oxblood", 15)]
TYPES = {  # frontage type mix per street role (FacadeGrammar types)
    "main": [("mixed_commercial", 60), ("lodging", 8), ("closed_residential", 32)],
    "plaza": [("mixed_commercial", 55), ("lodging", 15), ("closed_residential", 30)],
    "secondary": [("closed_residential", 60), ("mixed_commercial", 40)],
    "lane": [("closed_residential", 90), ("mixed_commercial", 10)],
    "steps": [("closed_residential", 100)],
    "bridge": [("mixed_commercial", 50), ("closed_residential", 50)],
    "footbridge": [("closed_residential", 100)],
    "river": [("closed_residential", 100)],
    "boundary": [("closed_residential", 100)],
}
FLOORS = {"main": (3, 4), "plaza": (3, 4), "secondary": (2, 4), "lane": (2, 3), "steps": (2, 3), "bridge": (3, 4),
          "footbridge": (2, 3), "river": (2, 4), "boundary": (2, 3)}


def pick(rng, table):
    total = sum(w for _, w in table)
    r = rng.uniform(0, total)
    for v, w in table:
        if r < w:
            return v
        r -= w
    return table[-1][0]


# ---------------------------------------------------------------- network + terrain

class Street:
    def __init__(self, s, nodes, roles):
        self.id = s["id"]
        self.role = s["role"]
        r = roles[self.role]
        self.profile = s.get("profile", r["profile"])
        self.width = float(s.get("width", r["width"]))
        pts = [nodes[s["from"]]] + [tuple(v) for v in s.get("via", [])] + [nodes[s["to"]]]
        xy = [(p[0], p[1]) for p in pts]
        self.line = LineString(xy)
        cum = [0.0]
        for a, b in zip(xy[:-1], xy[1:]):
            cum.append(cum[-1] + math.dist(a, b))
        self.cum = np.array(cum)
        y0, y1 = pts[0][2], pts[-1][2]
        ys = []
        for p, c in zip(pts, cum):
            ys.append(p[2] if len(p) > 2 and p is not pts[0] and p is not pts[-1] else y0 + (y1 - y0) * c / cum[-1])
        ys[0], ys[-1] = y0, y1
        self.ys = np.array(ys)
        self.a, self.b = s["from"], s["to"]

    def y_at(self, t):
        return np.interp(t, self.cum, self.ys)

    def grade(self):
        """Grade per polyline piece (constant between authored heights)."""
        return [(float(self.cum[i + 1] - self.cum[i]), abs(float(self.ys[i + 1] - self.ys[i])) / max(1e-6, float(self.cum[i + 1] - self.cum[i])))
                for i in range(len(self.cum) - 1)]


class Terrain:
    """Height of the ground anywhere: inverse-distance blend of the nearest street centrelines (their authored
    profiles), flat plazas where a plaza fixes its level."""

    def __init__(self, streets, flats):
        self.streets = streets
        self.flats = flats

    def __call__(self, P):
        P = np.asarray(P, float).reshape(-1, 2)
        pts = shapely.points(P)
        D = np.stack([shapely.distance(s.line, pts) for s in self.streets])
        T = np.stack([shapely.line_locate_point(s.line, pts) for s in self.streets])
        Y = np.stack([s.y_at(T[i]) for i, s in enumerate(self.streets)])
        dmin = D.min(axis=0)
        W = np.where(D <= dmin + 6.0, 1.0 / (D + 0.75) ** 3, 0.0)
        y = (W * Y).sum(axis=0) / W.sum(axis=0)
        for poly, yv in self.flats:
            d = shapely.distance(poly, pts)
            k = np.clip(d / 5.0, 0, 1)
            y = yv * (1 - k) + y * k
        return y


# ---------------------------------------------------------------- blocks

def angle_at(a, v, b):
    """Interior angle (deg) at v of a clockwise polygon a -> v -> b."""
    v1, v2 = np.subtract(a, v), np.subtract(b, v)
    ang = math.degrees(math.atan2(v1[0] * v2[1] - v1[1] * v2[0], v1[0] * v2[0] + v1[1] * v2[1]))
    ang = ang % 360.0
    return ang  # clockwise ring: convex vertices come out < 180


def line_x(p1, p2, p3, p4):
    d1, d2 = np.subtract(p2, p1), np.subtract(p4, p3)
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) < 1e-9:
        return None
    t = ((p3[0] - p1[0]) * d2[1] - (p3[1] - p1[1]) * d2[0]) / den
    return (p1[0] + d1[0] * t, p1[1] + d1[1] * t)


def clean_block(poly, report, force=()):
    p = orient(poly.simplify(0.35, preserve_topology=True), sign=-1.0)
    ring = [tuple(c) for c in p.exterior.coords][:-1]
    for _ in range(6):
        changed = False
        n = len(ring)
        # drop near-collinear vertices
        out = []
        for i in range(n):
            a, v, b = ring[i - 1], ring[i], ring[(i + 1) % n]
            if abs(angle_at(a, v, b) - 180) < 5 and math.dist(a, v) > 0.2:
                changed = True
                continue
            out.append(v)
        ring = out
        n = len(ring)
        # remove junction bevels: a short edge between two longer ones -> intersection of the neighbours
        for i in range(n):
            v0, v1 = ring[i], ring[(i + 1) % n]
            if math.dist(v0, v1) < 2.6 and n > 4:
                a, b = ring[i - 1], ring[(i + 2) % n]
                x = line_x(a, v0, v1, b)
                if x and math.dist(x, v0) < 3.5 and math.dist(x, v1) < 3.5:
                    cand = ring[:i] + [x] + ring[i + 2:] if i + 1 < n else [x] + ring[1:i]
                    q = Polygon(cand)
                    if q.is_valid and abs(q.area - Polygon(ring).area) < 12:
                        ring = cand
                        changed = True
                        break
        if not changed:
            break
    # acute tips -> a short chamfer (a narrow "prow" plot faces the junction); authored corners (bars) -> a chamfer
    out = []
    n = len(ring)
    chamfers = []
    for i in range(n):
        a, v, b = ring[i - 1], ring[i], ring[(i + 1) % n]
        th = angle_at(a, v, b)
        forced = any(math.dist(v, f) < 9 for f in force) and th < 165
        if th < 70 or forced:
            t = (1.6 if forced else 1.9) / max(0.2, math.sin(math.radians(th) / 2))
            u1 = np.subtract(a, v) / math.dist(a, v)
            u2 = np.subtract(b, v) / math.dist(b, v)
            if t < 0.45 * min(math.dist(a, v), math.dist(b, v)):
                p1, p2 = tuple(np.add(v, u1 * t)), tuple(np.add(v, u2 * t))
                out += [p1, p2]
                report["chamfers"] += 1
                if forced:
                    chamfers.append((p1, p2))
                continue
        out.append(v)
    q = orient(Polygon(out), sign=-1.0)
    if not q.is_valid:
        q = orient(p, sign=-1.0)
        chamfers = []
    report.setdefault("bar_chamfers", []).extend(chamfers)
    return q


# ---------------------------------------------------------------- build

def build(trace, doc, frame, authoring=None):
    if authoring is not None:
        authoring["_offset"] = trace["unityOffset"]
    rng = random.Random(1971)
    report = {"chamfers": 0, "dropped_plots": 0, "depth_reduced": 0, "rows": 0, "plots": 0, "fit_warnings": []}
    roles = trace["roles"]
    nodes = {k: tuple(v) for k, v in trace["nodes"].items()}
    streets = [Street(s, nodes, roles) for s in trace["streets"]]
    box = trace["reference"]["box"]
    m = trace.get("margin", 8)
    D = sbox(box[0] - m, box[1] - m, box[2] + m, box[3] + m)
    ox, oy = trace["unityOffset"]

    plazas = []
    for p in trace.get("plazas", []):
        poly = Point(p["disc"][:2]).buffer(p["disc"][2], 24) if "disc" in p else Polygon(p["poly"])
        plazas.append({"id": p["id"], "poly": poly, "y": p.get("y"), "name": p.get("name", "")})
    flats = [(p["poly"], p["y"]) for p in plazas if p["y"] is not None]
    T = Terrain(streets, flats)

    riv = trace["river"]
    rline = LineString(riv["pts"])
    C = rline.buffer(riv["width"] / 2, cap_style="flat", join_style="round")
    water = riv["water"]

    spoly = {s.id: s.line.buffer(s.width / 2, cap_style="square", join_style="mitre", mitre_limit=2.5) for s in streets}
    S = unary_union(list(spoly.values()) + [p["poly"] for p in plazas]).intersection(D)
    stairs = [s for s in streets if s.role == "steps"]
    bridges = [s for s in streets if s.role in ("bridge", "footbridge")]

    raw = D.difference(S).difference(C)
    geoms = list(raw.geoms) if isinstance(raw, MultiPolygon) else [raw]
    blocks, leftovers = [], []
    for g in geoms:
        if g.area < 30 or g.minimum_rotated_rectangle.length < 18:
            leftovers.append(g)
            continue
        blocks.append(clean_block(g, report, [tuple(f["at"]) for f in trace.get("features", []) if f["kind"] == "corner_bar"]))
    blocks.sort(key=lambda b: (-b.centroid.y, b.centroid.x))
    Bu = unary_union(blocks)
    street_space = D.difference(Bu).difference(C)

    # real plot subdivision
    real, _, _ = load(doc, frame, box, margin=m + 10)

    def classify(a, b):
        u = np.subtract(b, a) / math.dist(a, b)
        n_out = np.array([-u[1], u[0]])
        votes = {}
        for f in (0.25, 0.5, 0.75):
            q = np.add(a, np.subtract(b, a) * f) + n_out * 1.2
            pt = Point(q)
            if C.buffer(0.4).contains(pt):
                k = ("river", None)
            elif not D.contains(pt):
                k = ("boundary", None)
            elif any(p["poly"].contains(pt) and p["y"] is not None for p in plazas):
                k = ("plaza", None)
            else:
                s = min(streets, key=lambda s: s.line.distance(pt))
                k = (s.role, s.id) if s.line.distance(pt) < s.width / 2 + 4 else ("plaza", None)
            votes[k] = votes.get(k, 0) + 1
        return max(votes, key=votes.get)

    edges = []
    for bi, blk in enumerate(blocks):
        ring = [tuple(c) for c in blk.exterior.coords][:-1]
        n = len(ring)
        bedges = []
        for i in range(n):
            a, b = ring[i], ring[(i + 1) % n]
            L = math.dist(a, b)
            role, sid = classify(a, b) if L > 0.5 else ("boundary", None)
            u = np.subtract(b, a) / max(L, 1e-9)
            bedges.append({"block": bi, "i": i, "a": a, "b": b, "L": L, "u": u, "n_in": np.array([u[1], -u[0]]),
                           "role": role, "street": sid, "s0": 0.0, "s1": L, "start": "open", "end": "open", "plots": [],
                           "corner_keep_end": False})
        # vertex rule
        for i in range(n):
            e1, e2 = bedges[i - 1], bedges[i]
            th = angle_at(e1["a"], e1["b"], e2["b"])
            k1 = (RANK[e1["role"]], e1["L"])
            k2 = (RANK[e2["role"]], e2["L"])
            keep1 = k1 >= k2
            if th > 185:
                e1["end"], e2["start"] = "concave", "concave"
            elif th >= 175:
                e1["end"], e2["start"] = "hidden", "hidden"
            elif th >= 100:
                e1["end"], e2["start"] = ("tip_keep", "tip_cede") if keep1 else ("tip_cede", "tip_keep")
            else:
                d = 6.0 if th >= 85 else 4.0
                if keep1:
                    e1["end"], e2["start"] = "open", "hidden"
                    e2["s0"] = min(e2["L"], d / math.sin(math.radians(th)) + 0.02)
                    e1["corner_end_depth"] = d
                else:
                    e2["start"], e1["end"] = "open", "hidden"
                    e1["s1"] = max(0.0, e1["L"] - d / math.sin(math.radians(th)) - 0.02)
                    e2["corner_start_depth"] = d
        edges += bedges

    # plots per edge from the real subdivision
    for e in edges:
        U = e["s1"] - e["s0"]
        if e["role"] == "boundary":
            continue  # the district edge: backs and yards face outwards, no row
        if U < 1.6:
            e["filler"] = U > 0.05
            continue
        a, u, nin = np.array(e["a"]), e["u"], e["n_in"]
        strip = Polygon([a + u * e["s0"] - nin * 2, a + u * e["s1"] - nin * 2, a + u * e["s1"] + nin * 8, a + u * e["s0"] + nin * 8])
        deep = Polygon([a + u * e["s0"], a + u * e["s1"], a + u * e["s1"] + nin * 16, a + u * e["s0"] + nin * 16])
        iv = []
        for rb in real:
            if not rb["poly"].intersects(strip):
                continue
            inter = rb["poly"].intersection(strip)
            if inter.area < 2.5:
                continue
            cs = np.array(inter.convex_hull.exterior.coords) if inter.geom_type != "Point" else None
            if cs is None:
                continue
            t = (cs - a) @ u
            off = (cs - a) @ nin
            dp = rb["poly"].intersection(deep)
            depth = float(((np.array(dp.convex_hull.exterior.coords) - a) @ nin).max()) if dp.area > 1 else 6.0
            lv = rb["tags"].get("building:levels")
            iv.append({"t0": max(e["s0"], float(t.min())), "t1": min(e["s1"], float(t.max())), "off": float(np.median(off[off < 3])) if (off < 3).any() else 0.0,
                       "depth": depth, "levels": int(lv) if str(lv).isdigit() else None, "kind": rb["tags"].get("building")})
        iv = [v for v in iv if v["t1"] - v["t0"] > 1.0]
        iv.sort(key=lambda v: (v["t0"] + v["t1"]) / 2)
        cuts = [e["s0"]]
        src = []
        for j, v in enumerate(iv):
            if j == 0:
                if v["t0"] - e["s0"] > 3.0:
                    cuts.append(v["t0"]); src.append(None)
            else:
                prev = iv[j - 1]
                gap = v["t0"] - prev["t1"]
                if gap > 3.0:
                    cuts.append(prev["t1"]); src.append(prev)
                    cuts.append(v["t0"]); src.append(None)
                else:
                    cuts.append((prev["t1"] + v["t0"]) / 2); src.append(prev)
        if iv:
            if e["s1"] - iv[-1]["t1"] > 3.0:
                cuts.append(iv[-1]["t1"]); src.append(iv[-1])
                src.append(None)
            else:
                src.append(iv[-1])
        else:
            src.append(None)
        cuts.append(e["s1"])
        plots = [{"x0": cuts[k], "x1": cuts[k + 1], "src": src[k]} for k in range(len(cuts) - 1)]
        # split long unknown stretches / big buildings, merge slivers
        out = []
        for p in plots:
            w = p["x1"] - p["x0"]
            if w > 13:
                k = max(2, round(w / 7))
                for j in range(k):
                    out.append({"x0": p["x0"] + w * j / k, "x1": p["x0"] + w * (j + 1) / k, "src": p["src"]})
            else:
                out.append(p)
        merged = True
        while merged and len(out) > 1:
            merged = False
            for j, p in enumerate(out):
                if p["x1"] - p["x0"] < 3.4:
                    if j == 0:
                        k = 1
                    elif j == len(out) - 1:
                        k = j - 1
                    else:
                        k = j - 1 if out[j - 1]["x1"] - out[j - 1]["x0"] < out[j + 1]["x1"] - out[j + 1]["x0"] else j + 1
                    lo, hi = min(j, k), max(j, k)
                    keep = out[lo] if (out[lo]["x1"] - out[lo]["x0"]) >= (out[hi]["x1"] - out[hi]["x0"]) else out[hi]
                    out[lo:hi + 1] = [{"x0": out[lo]["x0"], "x1": out[hi]["x1"], "src": keep["src"]}]
                    merged = True
                    break
        # 2 m kit bays, row fitted by one scale factor in 0.88-1.14
        frontage = authoring.get("frontages", {}).get(f"K{e['block']}_{e['i']}") if authoring and f"K{e['block']}_{e['i']}" not in authoring.get("disabled", []) else None
        if frontage:
            import env_authoring
            env_authoring.guard(authoring, e)
            weights = frontage["bays"]
            x = e["s0"]
            out = []
            for weight, saved in zip(weights, frontage["source"]):
                width = U * weight / sum(weights)
                source = dict(saved) if saved["real"] else None
                out.append({"x0": x, "x1": x + width, "src": source})
                x += width
            bays = list(weights)
        else:
            bays = [max(1, min(7, round((p["x1"] - p["x0"]) / 2))) for p in out]
        for _ in range(0 if frontage else 12):
            sc = U / (2 * sum(bays))
            if 0.88 <= sc <= 1.14:
                break
            if sc > 1.14:
                j = min(range(len(bays)), key=lambda j: bays[j] * 2 - (out[j]["x1"] - out[j]["x0"]))
                bays[j] = min(7, bays[j] + 1)
            else:
                cand = [j for j in range(len(bays)) if bays[j] > 1]
                if not cand:
                    break
                j = max(cand, key=lambda j: bays[j] * 2 - (out[j]["x1"] - out[j]["x0"]))
                bays[j] -= 1
        sc = U / (2 * sum(bays))
        if len(bays) == 1 and not 0.72 <= sc <= 1.35:
            e["plots"] = [{"wall": True, "tall": True, "x0": e["s0"], "w": U}]  # too short for a building: close it with masonry
            continue
        if not (0.88 <= sc <= 1.14 or (len(bays) == 1 and 0.72 <= sc <= 1.35)):
            report["fit_warnings"].append(f"b{e['block']}e{e['i']} scale {sc:.2f} over {U:.1f} m")
        x = e["s0"]
        role = e["role"] if e["role"] in TYPES else "lane"
        for j, p in enumerate(out):
            w = bays[j] * 2 * sc
            s = p["src"] or {}
            real_depth = s.get("depth", 7.0)
            depth = 4 if real_depth < 5 else 6 if real_depth < 7.5 else 8
            lo, hi = FLOORS[role]
            floors = s.get("levels") or rng.randint(lo, hi)
            floors = min(hi, max(lo, floors))
            off = s.get("off", 0.0)
            setback = 0.0 if abs(off) < 0.3 or j in (0, len(out) - 1) else max(-0.4, min(1.2, round(off * 2) / 2))
            e["plots"].append({"x0": x, "w": w, "bays": bays[j], "depth": depth, "floors": floors, "setback": setback,
                               "real": bool(p["src"]), "type": pick(rng, TYPES[role])})
            x += w
        if e.get("corner_end_depth") and e["plots"]:
            e["plots"][-1]["depth"] = min(e["plots"][-1]["depth"], int(e["corner_end_depth"]))
            e["plots"][-1]["corner"] = "end"
        if e.get("corner_start_depth") and e["plots"]:
            e["plots"][0]["depth"] = min(e["plots"][0]["depth"], int(e["corner_start_depth"]))
            e["plots"][0]["corner"] = "start"

    def project(e, pt):
        a = np.array(e["a"])
        return float((np.subtract(pt, a)) @ e["u"]), float((np.subtract(pt, a)) @ e["n_in"])

    def nearest_plot(pt, pred=lambda e, p: True, maxd=12.0):
        best = None
        for e in edges:
            for p in e["plots"]:
                if p.get("wall") or not pred(e, p):
                    continue
                t, d = project(e, pt)
                if p["x0"] - 1 <= t <= p["x0"] + p["w"] + 1 and -4 <= d <= 12:
                    dist = abs(d) + max(0, p["x0"] - t, t - p["x0"] - p["w"])
                    if dist <= maxd and (best is None or dist < best[0]):
                        best = (dist, e, p, t)
        return best

    def split_plot(e, p, t, w):
        """Carves a plot of width w centred at t out of plot p; slivers under 3 m go to the new plot. A plot narrower
        than w first absorbs its neighbours on the same edge."""
        i = e["plots"].index(p)
        while p["w"] < w - 0.05:
            nxt = e["plots"][i + 1] if i + 1 < len(e["plots"]) and not e["plots"][i + 1].get("wall") else None
            prv = e["plots"][i - 1] if i > 0 and not e["plots"][i - 1].get("wall") else None
            if nxt is None and prv is None:
                break
            if nxt is not None:
                p["w"] += nxt["w"]
                e["plots"].pop(i + 1)
            else:
                p["x0"], p["w"] = prv["x0"], p["w"] + prv["w"]
                e["plots"].pop(i - 1)
                i -= 1
        x0, x1 = p["x0"], p["x0"] + p["w"]
        c0, c1 = max(x0, t - w / 2), min(x1, t + w / 2)
        parts = []
        if c0 - x0 >= 3.0:
            parts.append(dict(p, x0=x0, w=c0 - x0))
        else:
            c0 = x0
        new = dict(p, x0=c0, w=(c1 if x1 - c1 >= 3.0 else x1) - c0)
        parts.append(new)
        if x1 - c1 >= 3.0:
            parts.append(dict(p, x0=c1, w=x1 - c1))
        for q in parts:
            q["bays"] = max(1, round(q["w"] / 2))
        i = e["plots"].index(p)
        e["plots"][i:i + 1] = parts
        return new

    for lm in trace.get("landmarks", []):
        hit = nearest_plot(lm.get("anchorAt", lm["at"])[:2])
        if not hit:
            report.setdefault("landmark_misses", []).append(lm["id"])
            continue
        _, e, p, t = hit
        if lm.get("unit"):
            q = split_plot(e, p, t, min(4.0, e["s1"] - e["s0"]))
            q.update({"unit": lm["unit"], "type": "landmark", "bays": 2, "depth": 4, "floors": lm.get("floors", 5),
                      "setback": lm.get("setback", 0.0), "landmark": lm["id"]})
        else:
            q = split_plot(e, p, t, 10.0)
            q.update({"casona": True, "type": "closed_residential", "depth": 8, "floors": 3, "landmark": lm["id"]})

    bar_segs = report.pop("bar_chamfers", [])
    for bi, bes in enumerate([[e for e in edges if e["block"] == k] for k in range(len(blocks))]):
        for j, e in enumerate(bes):
            if any(math.dist(e["a"], p1) < 0.05 and math.dist(e["b"], p2) < 0.05 for p1, p2 in bar_segs) and e["plots"]:
                pal = pick(rng, PALETTES)
                for p in e["plots"]:
                    p.update({"type": "mixed_commercial", "rows": ["ES"] if p["bays"] == 2 else ["E"], "feature": "corner_bar",
                              "awning": "ENV_Canvas_Red", "palette_fixed": pal})
                for nb, first in ((bes[j - 1], False), (bes[(j + 1) % len(bes)], True)):
                    if nb["plots"] and not nb["plots"][0 if first else -1].get("wall"):
                        q = nb["plots"][0 if first else -1]
                        q.update({"type": "mixed_commercial", "feature": "corner_bar_side", "awning": "ENV_Canvas_Red", "palette_fixed": pal})
                report["bars"] = report.get("bars", 0) + 1

    zones = [{"id": z["id"], "kind": z["kind"], "poly": Polygon(z["poly"]), "keep": set(z.get("keep", [])),
              "casonas": [tuple(c) for c in z.get("casonas", [])]} for z in trace.get("zones", [])]
    for e in edges:
        if not e["plots"]:
            continue
        a = np.array(e["a"])
        mid = Point(a + e["u"] * (e["s0"] + e["s1"]) / 2 + e["n_in"] * 2)
        z = next((z for z in zones if z["poly"].contains(mid)), None)
        if not z or e["street"] in z["keep"] or any(p.get("landmark") for p in e["plots"]):
            continue
        e["zone"] = z["id"]
        anchors = []
        for c in z["casonas"]:
            t, d = project(e, c)
            if e["s0"] + 5 < t < e["s1"] - 5 and -3 < d < 14:
                anchors.append(t)
        items, cursor = [], e["s0"]
        for t in sorted(anchors):
            x0 = max(cursor, t - 5.0)
            x1 = min(e["s1"], x0 + 10.0)
            if x1 - x0 < 7:
                continue
            if x0 - cursor > 0.4:
                items.append({"wall": True, "x0": cursor, "w": x0 - cursor})
            items.append({"x0": x0, "w": x1 - x0, "bays": 5 if x1 - x0 >= 9 else 4, "depth": 8, "floors": 3, "setback": 0.0,
                          "real": False, "type": "closed_residential", "casona": True})
            cursor = x1
        if e["s1"] - cursor > 0.4:
            items.append({"wall": True, "x0": cursor, "w": e["s1"] - cursor})
        e["plots"] = items

    # depth fitting against the other rows of the block (back-to-back rows meet, never cross)
    def footprint(e, p, depth):
        a, u, nin = np.array(e["a"]), e["u"], e["n_in"]
        x0, x1 = p["x0"], p["x0"] + p["w"]
        z0, z1 = p["setback"], p["setback"] + depth
        return Polygon([a + u * x0 + nin * z0, a + u * x1 + nin * z0, a + u * x1 + nin * z1, a + u * x0 + nin * z1])

    by_block = {}
    for e in edges:
        by_block.setdefault(e["block"], []).append(e)
    for bi, bes in by_block.items():
        placed = []  # (edge index, polygon)
        blk = blocks[bi]
        order = sorted(bes, key=lambda e: (-RANK[e["role"]], -e["L"]))
        n = len(bes)
        for e in order:
            for p in e["plots"]:
                if p.get("wall"):
                    continue
                if p.get("landmark"):
                    # a singular building may stand proud of the street line (Demo C rule 7): never trimmed or dropped
                    p["fp"] = footprint(e, p, p["depth"])
                    placed.append((e["i"], p["fp"]))
                    continue
                ok = None
                for d in [x for x in (8, 6, 4) if x <= p["depth"]] or [4]:
                    fp = footprint(e, p, d)
                    if not blk.buffer(0.8).contains(fp):
                        continue
                    clash = False
                    for (oi, of) in placed:
                        if oi == e["i"] or (oi - e["i"]) % n in (1, n - 1):
                            continue  # same row, or the neighbouring row at a shared vertex (intended mitre/corner overlap)
                        if fp.buffer(-0.3).intersection(of).area > 0.5:
                            clash = True
                            break
                    if not clash:
                        ok = d
                        break
                if ok is None:
                    fp4 = footprint(e, p, 4)
                    if not blk.buffer(0.8).contains(fp4):
                        # the block is too thin here for any building: close the street wall with masonry instead
                        x0, w = p["x0"], p["w"]
                        p.clear()
                        p.update({"wall": True, "thin": True, "x0": x0, "w": w})
                        report["thin_walls"] = report.get("thin_walls", 0) + 1
                        continue
                    p["drop"] = True
                    report.setdefault("drops", []).append(fp4)
                    report["dropped_plots"] += 1
                    continue
                if ok < p["depth"]:
                    report["depth_reduced"] += 1
                p["depth"] = ok
                p["fp"] = footprint(e, p, ok)
                placed.append((e["i"], p["fp"]))

    # row ends that assumed a neighbour (corner cede, mitred tip, straight continuation, concave notch) are exposed
    # again when that neighbour's plot was dropped, walled or never built: a side wall must never be left open
    for bi, bes in by_block.items():
        n = len(bes)
        for k in range(n):
            e1, e2 = bes[k - 1], bes[k]
            live1 = [p for p in e1["plots"] if not p.get("drop") and not p.get("wall")]
            live2 = [p for p in e2["plots"] if not p.get("drop") and not p.get("wall")]
            has1 = bool(live1) and live1[-1] is e1["plots"][-1] and live1[-1]["x0"] + live1[-1]["w"] >= e1["s1"] - 0.5
            has2 = bool(live2) and live2[0] is e2["plots"][0] and live2[0]["x0"] <= e2["s0"] + 0.5
            if e2["start"] != "open" and not has1:
                e2["start"] = "open"
                report["reopened_ends"] = report.get("reopened_ends", 0) + 1
            if e1["end"] != "open" and not has2:
                e1["end"] = "open"
                report["reopened_ends"] = report.get("reopened_ends", 0) + 1

    # heights, palettes, eras, basements
    for e in edges:
        keep = [p for p in e["plots"] if not p.get("drop")]
        if authoring:
            import env_authoring
            e["plots"] = keep
            env_authoring.apply_plots(authoring, e)
            keep = e["plots"]
            for p in keep:
                if not p.get("wall"):
                    p["fp"] = footprint(e, p, p["depth"])
        e["plots"] = keep
        for p in keep:
            lm = next((lm for lm in trace.get("landmarks", []) if lm.get("id") == p.get("landmark") and lm.get("placement") == "direct"), None)
            if lm is not None:
                at = lm["at"]
                if len(at) != 3 or not all(math.isfinite(float(v)) for v in at) or not math.isfinite(float(lm.get("yaw", 0))):
                    raise ValueError("ENV_DIRECT_PLACEMENT_INVALID " + lm["id"])
                yaw = math.radians(lm.get("yaw", 0)); right = np.array([math.cos(yaw), -math.sin(yaw)]); back = np.array([-math.sin(yaw), -math.cos(yaw)])
                front = np.array(at[:2]); half = p["w"] / 2
                p["fp"] = Polygon([front-right*half, front+right*half, front+right*half+back*p["depth"], front-right*half+back*p["depth"]])
                p["directPlacement"] = {"at":[round(at[0]+ox,3),round(at[2],3),round(at[1]+oy,3)], "yaw":lm.get("yaw",0)}
        if not keep:
            continue
        report["rows"] += 1
        a, u, nin = np.array(e["a"]), e["u"], e["n_in"]
        for p in keep:
            if p.get("wall"):
                xs = np.arange(p["x0"], p["x0"] + p["w"] + 1e-6, 2.0)
                if xs[-1] < p["x0"] + p["w"] - 0.05:
                    xs = np.append(xs, p["x0"] + p["w"])
                p["ys"] = [round(float(v), 3) for v in T([a + u * x - nin * 0.4 for x in xs])]
                if not p.get("tall") and p["w"] > 7 and rng.random() < 0.6:
                    p["gate"] = round(rng.uniform(1.5, p["w"] - 2.5), 2)
                report["walls"] = report.get("walls", 0) + 1
                continue
            report["plots"] += 1
            mid = a + u * (p["x0"] + p["w"] / 2) + nin * p["setback"]
            front = a + u * (p["x0"] + p["w"] / 2) - nin * 0.8
            y = p["directPlacement"]["at"][1] if "directPlacement" in p else float(T([front])[0])
            corners = np.array(p["fp"].exterior.coords[:4])
            ground = T(np.vstack([corners, [a + u * p["x0"] - nin * 0.5, a + u * (p["x0"] + p["w"]) - nin * 0.5]]))
            base = y - float(ground.min())
            if e["role"] == "river":
                base = y - (water - 0.4)
            p["y"] = round(y, 3)
            p["basement"] = round(max(0.0, base) + (0.15 if base > 0.05 else 0.0), 2)
            p["palette"] = p.pop("palette_fixed", None) or pick(rng, PALETTES)
            p["seed"] = rng.randint(1, 9999)
            p["ground"] = "stone" if rng.random() < 0.7 else ""
            p["upper"] = "stone" if rng.random() < 0.12 else "plaster"
            # lebaniego vocabulary: solanas on the sunny upper floors of ordinary houses, sandstone window surrounds on
            # rendered fronts, a rare shield outside the casonas
            if p["type"] in ("closed_residential", "lodging") and p["floors"] >= 3 and e["role"] in ("lane", "secondary", "river", "steps", "plaza"):
                p["solana"] = rng.random() < 0.3
            if p["upper"] == "plaster" and p["type"] != "landmark":
                p["surrounds"] = rng.random() < 0.4
            if p["type"] == "closed_residential" and e["role"] in ("main", "plaza") and rng.random() < 0.04:
                p["escudo"] = True
            if p.get("casona"):
                p.update({"ground": "stone", "upper": "stone" if rng.random() < 0.6 else "plaster", "era": "old",
                          "palette": rng.choice(["core_sandstone_chestnut", "core_lime_chestnut"])})
            p["mid"] = mid

    # ground meshes by zone
    # the stair footprint is exactly between its end nodes (flat caps): a square cap would punch a hole in the
    # junction it starts from (the route probe fell through one)
    stair_polys = unary_union([s.line.buffer(s.width / 2, cap_style="flat") for s in stairs]) if stairs else Polygon()
    deck = unary_union([spoly[s.id] for s in bridges]).intersection(C) if bridges else Polygon()
    ground_space = street_space.difference(stair_polys)
    core_ids = {s.id for s in streets if s.profile == "core"}
    # casco paving (owner photo): canto rodado with a central strip of big flags along core streets and lanes
    strip = unary_union([s.line.buffer(0.6 if s.profile == "core" else 0.45, cap_style="flat")
                         for s in streets if s.profile in ("core", "lane")]).intersection(ground_space)
    strip = strip.difference(unary_union([p["poly"] for p in plazas if p["y"] is not None]))
    band = strip
    gz = {}

    def zone_of(pt, in_band):
        if any(p["poly"].contains(pt) and p["y"] is not None for p in plazas):
            return "plaza"
        s = min(streets, key=lambda s: s.line.distance(pt))
        if s.line.distance(pt) > s.width / 2 + 3.0:
            return "plaza"
        if s.profile == "core":
            return "core_band" if in_band else "core"
        if s.profile == "bridge":
            return "core"
        return "lane"

    def mesh(poly, label_fn, cell=3.0):
        out = {}
        if poly.is_empty:
            return out
        x0, y0, x1, y1 = poly.bounds
        for gx in np.arange(math.floor(x0 / cell) * cell, x1, cell):
            for gy in np.arange(math.floor(y0 / cell) * cell, y1, cell):
                c = poly.intersection(sbox(gx, gy, gx + cell, gy + cell))
                if c.is_empty or c.area < 1e-4:
                    continue
                for g in (c.geoms if hasattr(c, "geoms") else [c]):
                    if g.geom_type != "Polygon" or g.area < 1e-4:
                        continue
                    tris = shapely.constrained_delaunay_triangles(g)
                    for t in tris.geoms:
                        if t.area < 1e-5:
                            continue
                        cs = list(t.exterior.coords)[:3]
                        lab = label_fn(t.centroid)
                        out.setdefault(lab, []).append(cs)
        return out

    for lab, tris in mesh(band, lambda c: "strip").items():
        gz.setdefault(lab, []).extend(tris)
    for lab, tris in mesh(ground_space.difference(band), lambda c: zone_of(c, False)).items():
        gz.setdefault(lab, []).extend(tris)
    fps = unary_union([p["fp"] for e in edges for p in e["plots"] if "fp" in p])
    # the rim of every block (forecourts of set-back houses, gaps beside garden walls) is paved like a lane; only
    # the block interior is garden (a strip of lawn at the foot of a street facade read wrong)
    inner = Bu.buffer(-1.6, join_style="mitre")
    rim = Bu.difference(inner).difference(fps.buffer(-0.05))
    for lab, tris in mesh(rim, lambda c: "lane").items():
        gz.setdefault(lab, []).extend(tris)
    yards = inner.difference(fps.buffer(-0.05))
    for lab, tris in mesh(yards, lambda c: "huerta" if any(z["poly"].contains(c) for z in zones) else "yard").items():
        gz.setdefault(lab, []).extend(tris)
    outer = D.buffer(14, join_style="mitre").difference(D).difference(C)
    for lab, tris in mesh(outer, lambda c: "outer", cell=6.0).items():
        gz.setdefault(lab, []).extend(tris)

    ground = {}
    for lab, tris in gz.items():
        verts, index, tri_idx = [], {}, []
        flat = np.array([c for t in tris for c in t])
        ys = T(flat)
        for k, (c, yv) in enumerate(zip(flat, ys)):
            key = (round(c[0], 3), round(c[1], 3))
            if key not in index:
                index[key] = len(verts)
                verts.append([round(c[0] + ox, 3), round(float(yv) - (0.003 if lab == "core" else 0.0), 3), round(c[1] + oy, 3)])
            tri_idx.append(index[key])
        ground[lab] = {"v": verts, "t": tri_idx}

    # grades by network length inside the district
    shares = {"comfortable": 0.0, "perceptible": 0.0, "strong": 0.0}
    per_street = []
    for s in streets:
        inside = s.line.intersection(D).length / max(s.line.length, 1e-6)
        for L, g in s.grade():
            c = grade_class(g, s.role == "steps")
            shares[c] += L * inside
        per_street.append({"id": s.id, "role": s.role, "length_m": round(s.line.length, 1),
                           "grade_max": round(max(g for _, g in s.grade()), 3)})
    for rs in trace.get("riverStairs", []):
        shares["strong"] += rs.get("length", 8)
    tot = sum(shares.values())
    shares = {k: round(v / tot, 3) for k, v in shares.items()}

    U2 = lambda q: [round(q[0] + ox, 3), round(q[1] + oy, 3)]
    rows_out = []
    for e in edges:
        if not e["plots"] and not e.get("filler"):
            continue
        rows_out.append({
            "id": f"K{e['block']}_{e['i']}", "block": e["block"], "role": e["role"], "street": e["street"],
            "origin": U2(e["a"]), "dir": [round(float(e["u"][0]), 5), round(float(e["u"][1]), 5)], "length": round(e["L"], 3),
            "ends": {"west": e["start"], "east": e["end"]},
            "filler": [round(e["s0"], 3), round(e["s1"], 3)] if e.get("filler") else None,
            "plots": [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in p.items() if k not in ("fp", "mid", "src")}
                      for p in e["plots"]],
        })
    walls = []
    for side in (C.exterior,):
        pass
    bank = C.boundary.intersection(D.buffer(2))
    bank_lines = [list(g.coords) for g in (bank.geoms if hasattr(bank, "geoms") else [bank]) if g.length > 1]
    open_bank = C.buffer(1.2).boundary  # parapets where the bank is public space
    river_stairs = []
    bank_geoms = list(bank.geoms) if hasattr(bank, "geoms") else [bank]
    for rs in trace.get("riverStairs", []):
        pt = Point(rs["at"])
        g = min(bank_geoms, key=lambda g: g.distance(pt))
        t = g.project(pt)
        a0, a1 = g.interpolate(max(0.0, t - 1.0)), g.interpolate(min(g.length, t + 1.0))
        u = np.array([a1.x - a0.x, a1.y - a0.y])
        u /= max(np.linalg.norm(u), 1e-6)
        o = np.array(g.interpolate(t).coords[0])
        n = np.array([-u[1], u[0]])
        if not C.contains(Point(o + n * 1.5)):
            n = -n
        # the module runs along +x with +z over the water; a Unity yaw frame has +z to the left of +x, so n must be
        # to the left of u (cross > 0)
        if u[0] * n[1] - u[1] * n[0] < 0:
            u = -u
        river_stairs.append({"at": o, "u": u, "n": n, "y": float(T([o])[0]), "length": rs.get("length", 9)})
    parapets = []
    for g in (bank.geoms if hasattr(bank, "geoms") else [bank]):
        for k in np.arange(0, g.length, 2.0):
            p0 = g.interpolate(k)
            p1 = g.interpolate(min(g.length, k + 2.0))
            mid = LineString([p0, p1]).interpolate(0.5, normalized=True)
            probe = mid.buffer(1.6).difference(C)
            near_stairs = any(np.linalg.norm(np.array([mid.x, mid.y]) - (r["at"] + r["u"] * 3.0)) < 4.2 for r in river_stairs)
            if probe.intersection(Bu).area < 0.3 and D.contains(mid) and probe.intersection(deck.buffer(0.5)).area < 0.1 and not near_stairs:
                parapets.append([p0.x, p0.y, p1.x, p1.y])
    garden = []
    grng = random.Random(77)
    for poly, kind in ((yards, "yard"),):
        for g in (poly.geoms if hasattr(poly, "geoms") else [poly]):
            if g.geom_type != "Polygon" or g.area < 25:
                continue
            x0, y0, x1, y1 = g.bounds
            for gx in np.arange(x0 + 3, x1 - 2, 7.5):
                for gy in np.arange(y0 + 3, y1 - 2, 7.5):
                    q = Point(gx + grng.uniform(-2, 2), gy + grng.uniform(-2, 2))
                    if not g.buffer(-2.2).contains(q) or fps.distance(q) < 2.5:
                        continue
                    zone = next((z["id"] for z in zones if z["poly"].contains(q)), None)
                    r = grng.random()
                    item = "tree" if r < (0.35 if zone else 0.45) else "bush" if r < 0.8 else None
                    if item:
                        garden.append({"at": U2((q.x, q.y)), "y": round(float(T([(q.x, q.y)])[0]), 3), "item": item,
                                       "scale": round(grng.uniform(0.55, 0.85) if item == "tree" else grng.uniform(0.8, 1.4), 2),
                                       "rot": grng.randint(0, 359)})
    fountains = []
    for pz in trace.get("plazas", []):
        if pz["id"] != "Plazuela_Fuente":
            continue
        c = Point(pz["disc"][:2])
        ring = Bu.boundary
        q = ring.interpolate(ring.project(c))
        d = np.array([c.x - q.x, c.y - q.y])
        d /= max(np.linalg.norm(d), 1e-6)
        at = np.array([q.x, q.y]) + d * 0.35
        fountains.append({"at": U2(at), "y": round(float(T([at])[0]), 3), "face": [round(float(d[0]), 4), round(float(d[1]), 4)]})
    crossings = []
    for sb in bridges:
        seg = sb.line.intersection(C)
        if seg.is_empty:
            continue
        cs = list(seg.coords) if seg.geom_type == "LineString" else [c for g in seg.geoms for c in g.coords]
        a, b = np.array(cs[0]), np.array(cs[-1])
        mid = (a + b) / 2
        crossings.append({"id": sb.id, "mid": U2(mid), "dir": [round(float(v), 5) for v in (b - a) / max(np.linalg.norm(b - a), 1e-6)],
                          "span": round(float(np.linalg.norm(b - a)), 3), "width": sb.width, "y": round(float(sb.y_at(sb.line.project(Point(mid)))), 3)})
    # route probe: the authored node tour, sampled every ~6 m along the connecting street centrelines
    route = []
    tour = trace.get("route", [])
    for na, nb in zip(tour[:-1], tour[1:]):
        st = next((s for s in streets if {s.a, s.b} == {na, nb}), None)
        if st is None:
            report.setdefault("route_gaps", []).append(f"{na}-{nb}")
            continue
        L = st.line.length
        ts = np.linspace(0, L, max(2, int(L / 6) + 1))
        if st.a != na:
            ts = ts[::-1]
        for k, tt in enumerate(ts):
            if route and k == 0:
                continue
            q = st.line.interpolate(tt)
            route.append(U2((q.x, q.y)) + [round(float(st.y_at(tt)), 3)])
    spec = {
        "id": trace["id"], "brief": trace["brief"], "generatedBy": "Tools/env_district_skeleton.py",
        "reference": trace["reference"], "unityOffset": [ox, oy],
        "district": [U2((D.bounds[0], D.bounds[1])), U2((D.bounds[2], D.bounds[3]))],
        "grades": shares,
        "streets": [{"id": s.id, "role": s.role, "profile": s.profile, "width": s.width,
                     "pts": [U2(c) + [round(float(y), 3)] for c, y in zip(s.line.coords, s.ys)]} for s in streets],
        "plazas": [{"id": p["id"], "name": p["name"], "y": p["y"],
                    "poly": [U2(c) for c in p["poly"].exterior.coords]} for p in plazas],
        "river": {"pts": [U2(c) for c in riv["pts"]], "width": riv["width"], "water": water,
                  "channel": [U2(c) for c in C.intersection(D.buffer(12, join_style="mitre")).exterior.coords],
                  "banks": [[U2(c) + [round(float(T([c])[0]), 3)] for c in bl] for bl in bank_lines],
                  "parapets": [[U2((p[0], p[1])), U2((p[2], p[3])), round(float(T([((p[0] + p[2]) / 2, (p[1] + p[3]) / 2)])[0]), 3)] for p in parapets]},
        "bridges": [{"id": s.id, "role": s.role, "width": s.width,
                     "pts": [U2(c) + [round(float(y), 3)] for c, y in zip(s.line.coords, s.ys)]} for s in bridges],
        "stairs": [{"id": s.id, "width": s.width, "pts": [U2(c) + [round(float(y), 3)] for c, y in zip(s.line.coords, s.ys)]} for s in stairs],
        "riverStairs": [{"at": U2(r["at"]), "u": [round(float(v), 5) for v in r["u"]], "y": round(r["y"], 3)} for r in river_stairs],
        "bridgeArches": crossings,
        "fountains": fountains,
        "garden": garden,
        "route": route,
        "rows": rows_out,
        "ground": ground,
        "report": report,
    }
    geo = {"D": D, "C": C, "S": street_space, "blocks": blocks, "edges": edges, "streets": streets, "plazas": plazas,
           "stairs": stair_polys, "deck": deck, "parapets": parapets, "T": T}
    if authoring:
        import env_authoring
        env_authoring.finish(authoring, spec, T)
    return spec, geo, per_street


# ---------------------------------------------------------------- plan

def draw(geo, spec, per_street, out, ref_metrics=None, scale=4.0):
    from PIL import Image, ImageDraw, ImageFont
    D = geo["D"]
    win = [D.bounds[0] - 6, D.bounds[1] - 6, D.bounds[2] + 6, D.bounds[3] + 6]
    W, H = int((win[2] - win[0]) * scale), int((win[3] - win[1]) * scale)
    panels = 2 if ref_metrics else 1
    img = Image.new("RGB", (W * panels + (20 if panels == 2 else 0), H + 70), (250, 249, 245))
    dr = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype("arial.ttf", 13)
        fb = ImageFont.truetype("arialbd.ttf", 18)
        fs = ImageFont.truetype("arial.ttf", 11)
    except Exception:
        f = fb = fs = ImageFont.load_default()
    cls = {"comfortable": (60, 150, 70), "perceptible": (230, 160, 30), "strong": (210, 40, 40)}

    def panel(x_off, title):
        px = lambda q: (x_off + (q[0] - win[0]) * scale, 70 + (win[3] - q[1]) * scale)
        dr.text((x_off + 10, 8), title, fill=(20, 20, 20), font=fb)
        return px

    if ref_metrics:
        px = panel(0, "REFERENCIA medida (OSM + MDT05): red real, pendientes reales")
        dr.rectangle([px((D.bounds[0], D.bounds[3])), px((D.bounds[2], D.bounds[1]))], fill=(240, 237, 228))
        for w in ref_metrics["water"]:
            dr.line([px(p) for p in w["pts"]], fill=(110, 160, 215), width=int(3 * scale))
        for e in ref_metrics["edges"]:
            dr.line([px(p) for p in e["pts"]], fill=cls[e["class"]], width=3)
        sh = ref_metrics["summary"]["grade_share_reference"]
        dr.text((10, 40), f"comoda {sh['comfortable'] * 100:.0f} %   perceptible {sh['perceptible'] * 100:.0f} %   fuerte/escaleras {sh['strong'] * 100:.0f} %   ({ref_metrics['summary']['edges']} tramos)", fill=(0, 0, 0), font=f)
    x_off = W + 20 if ref_metrics else 0
    px = panel(x_off, "NUESTRO CASCO (trazado autorado): manzanas, parcelas, cotas")
    poly = lambda g, **kw: [dr.polygon([px(c) for c in p.exterior.coords], **kw) for p in (g.geoms if hasattr(g, "geoms") else [g]) if not p.is_empty and p.geom_type == "Polygon"]
    poly(D, fill=(238, 236, 228))
    poly(geo["S"], fill=(214, 208, 196))
    for b in geo["blocks"]:
        poly(b, fill=(222, 232, 210), outline=(150, 160, 140))
    poly(geo["C"], fill=(120, 165, 205))
    typ = {"mixed_commercial": (200, 120, 90), "closed_residential": (190, 160, 130), "lodging": (160, 110, 160)}
    for e in geo["edges"]:
        for p in e["plots"]:
            if p.get("wall"):
                a = np.array(e["a"])
                dr.line([px(a + e["u"] * p["x0"]), px(a + e["u"] * (p["x0"] + p["w"]))], fill=(110, 95, 80), width=3)
                continue
            if "fp" not in p:
                continue
            col = (120, 90, 60) if p.get("casona") else (90, 70, 110) if p.get("landmark") else (230, 90, 60) if p.get("feature") else typ.get(p["type"], (170, 150, 130))
            poly(p["fp"], fill=col, outline=(90, 60, 45))
    for fp in spec["report"].get("drops", []):
        dr.polygon([px(c) for c in fp.exterior.coords], outline=(230, 0, 0))
    poly(geo["deck"], fill=(170, 160, 150), outline=(80, 70, 60))
    for p in geo["parapets"]:
        dr.line([px((p[0], p[1])), px((p[2], p[3]))], fill=(60, 60, 60), width=2)
    poly(geo["stairs"], fill=(210, 190, 190))
    for s in geo["streets"]:
        for (a, b), (L, g) in zip(zip(s.line.coords[:-1], s.line.coords[1:]), s.grade()):
            c = cls[grade_class(g, s.role == "steps")]
            dr.line([px(a), px(b)], fill=c, width=3 if s.role != "steps" else 5)
        mid = s.line.interpolate(0.5, normalized=True)
        dr.text(px((mid.x, mid.y)), s.id.replace("_", " "), fill=(20, 20, 110), font=fs)
    for s in geo["streets"]:
        for c, y in ((s.line.coords[0], s.ys[0]), (s.line.coords[-1], s.ys[-1])):
            x, yy = px(c)
            dr.ellipse([x - 3, yy - 3, x + 3, yy + 3], fill=(0, 0, 0))
            dr.text((x + 4, yy - 13), f"{y:+.1f}", fill=(150, 0, 0), font=fs)
    sh = spec["grades"]
    dr.text((x_off + 10, 40), f"comoda {sh['comfortable'] * 100:.0f} %   perceptible {sh['perceptible'] * 100:.0f} %   fuerte/escaleras {sh['strong'] * 100:.0f} %   "
            f"(objetivo 70/20/10)  -  {len(spec['streets'])} calles, {spec['report']['plots']} edificios, cotas en m sobre la plaza del rio",
            fill=(0, 0, 0), font=f)
    lx = x_off + W - 250
    for i, (k, c) in enumerate(cls.items()):
        y = H + 40 - i * 18
        dr.line([(lx, y), (lx + 26, y)], fill=c, width=5)
        dr.text((lx + 32, y - 8), {"comfortable": "<= 5 %", "perceptible": "5-10 %", "strong": "> 10 % / escaleras"}[k], fill=(0, 0, 0), font=f)
    dr.text((10, H + 52), "(c) OpenStreetMap contributors ODbL - MDT05 (c) IGN CC BY 4.0", fill=(90, 90, 90), font=fs)
    img.save(out, quality=90)
    print(out, img.size)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trace", required=True)
    ap.add_argument("--osm", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--plan")
    ap.add_argument("--metrics", help="reference metrics from env_district.py measure (left panel of the plan)")
    a = ap.parse_args()
    trace = json.load(open(a.trace, encoding="utf-8"))
    doc = json.load(open(a.osm, encoding="utf-8"))
    frame = Frame(*trace["reference"]["origin"])
    import env_authoring
    authoring = env_authoring.load(a.trace)
    spec, geo, per_street = build(trace, doc, frame, authoring)
    drops = spec["report"].pop("drops", [])
    json.dump(spec, open(a.out, "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    spec["report"]["drops"] = drops
    print(json.dumps({"grades": spec["grades"], "report": {k: v for k, v in spec["report"].items() if k != "drops"}, "blocks": len(geo["blocks"]),
                      "ground": {k: len(v["t"]) // 3 for k, v in spec["ground"].items()}}, indent=1))
    if a.plan:
        ref = json.load(open(a.metrics, encoding="utf-8")) if a.metrics else None
        draw(geo, spec, per_street, a.plan, ref)


if __name__ == "__main__":
    main()

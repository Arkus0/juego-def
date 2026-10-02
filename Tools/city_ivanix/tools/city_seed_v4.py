"""Seed v4: Ivanix layout -> Cantabrian-Asturian town (ENV01 architecture), for CityIvanixSeed.

v4 (owner review 2026-10-02, "packing -> morfologia urbana"): buildings are no longer oriented one by one to fill
space. The streets and squares of the layout give smoothed frontage lines (tramos); every building belongs to a tramo,
its main facade sits on the line and follows the street's local tangent, neighbours share orientation and meet at
party walls (parcel widths in metres, the kit's 2 m bays scaled by up to +-20 %), plots run back into the block, and
the street edge left between facades is closed by garden walls (tapias) with gates, so there are no residual gaps.
Singular buildings (Torre, church, Finca) may break the grain.

v3:
Changes from v2: one building per traced roof (coherence trace) instead of per aggregated mass; El Alto as three
terraces with retaining walls and stairs; the Torre (casa-torre de silleria) on the top; the Finca del Cacique as a
walled casona with three entrances; earth aprons read as old cobbles (the space is kept, the surface becomes
Cantabrian); green yards become huertas; market stalls and the false boxes around the port gate are dropped;
default programme placement with consolidation only of contiguous footprints for the large interiors.
"""

import hashlib
import json
import math
from pathlib import Path

import sys

import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from shapely.prepared import prep

ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / "reconstruction" / "layout_trace_v1.json"
OUT = ROOT / "reconstruction" / "city_seed_v4.json"
CELL = 1.0
KEEP = np.array([-140.0, -12.0])
# El Alto follows the observable rings of the layout: keep plinth (Torre), inner ring street, ring of houses that
# holds the step (their basements open to the lower ring), open lower ring up to the outer wall.
R_KEEP, R_EDGE, R_RING2 = 19.0, 28.5, 64.0
LV_KEEP, LV_RING1, LV_RING2 = 19.0, 17.5, 14.0
# The north port in the layout is a walled forecourt (antepuerto) outside the town gate, funnelling down to a U-shaped
# timber pier; its inner arms are the town wall (gate between the two arm towers), its outer arms enclose the quay.
ANTE_INNER = [(33.16, 72.85), (12.9, 53.9), (-2.45, 54.06), (-24.66, 72.03), (-53.08, 68.76)]
ANTE = [(-2.45, 54.06), (12.9, 53.9), (33.16, 72.85), (24.17, 98.98), (-29.73, 99.14), (-24.66, 72.03)]
ANTE_ARMS = [[(33.16, 72.85), (24.17, 98.98)], [(-24.66, 72.03), (-29.73, 99.14)]]
QUAY_Y = 2.6
WALL_HALF = 2.2          # the XV-century wall: 4.4 m thick, its wall-walk is the paseo maritimo
PASEO_UP = 2.4           # paseo deck above the town ground at the wall's inner foot
PIER = [(-12.5, 83.5, 14.5, 90.0), (-12.5, 90.0, -8.5, 98.0), (10.5, 90.0, 14.5, 98.0)]
PIER_WATER = (-12.5, 83.5, 14.5, 104.0)
GATE_N = (5.2, 54.0)
# bridge axes (gate -> far landing); the capture ends at z = -150, the south bank and its road are synthesised
EAST_GATE = (79.4, -36.9)     # midpoint of its two cubos (74.5, -42.8) / (84.3, -31.0)
BRIDGES = [("puente_sur", (5.06, -127.56), (5.1, -153.0), 4.0), ("puente_este", EAST_GATE, (106.7, -56.7), 3.6)]
# the other bank of the river: an irregular shore (not a cut rectangle), the road south leaves through it (seam X5)
SOUTH_BANK = ([(x, round(-150.5 - 2.2 * math.sin(x / 11.0) - 1.3 * math.sin(x / 4.7 + 1.3) - 0.0006 * x * x, 2)) for x in range(-110, 131, 4)]
              + [(130.0, -205.0), (-110.0, -205.0)])
SOUTH_ROAD = [(1.2, -150.0), (9.0, -150.0), (9.4, -205.0), (0.8, -205.0)]
FINCA = {"towers": [[33.81, 39.53], [48.67, 33.81], [54.55, 48.67], [39.7, 54.4]]}

TOWN_CONTROL = [
    (0, 0, 10.0), (-30, 30, 9.5), (30, 20, 9.0), (-2, 52, 6.0), (44, 44, 13.0), (60, 30, 11.0), (80, -41, 5.5),
    (60, -60, 7.0), (5, -125, 4.5), (5, -90, 6.5), (-40, -80, 8.5), (-60, -40, 10.0), (90, 5, 8.0),
    (-70, 10, 11.0), (-90, 45, 11.0), (-75, -10, 12.5), (-110, 40, 12.5), (-110, -55, 12.5),
]

PROGRAMME_LOOK = {   # how a person recognises each programme from the street (main cell carries the entrance)
    "P_AYTO": {"type": "closed_residential", "stone": True, "escudo": True},
    "P_IGLESIA": {"type": "closed_residential", "stone": True, "church": True},
    "P_PENSION": {"type": "lodging"},
    "P_HOTEL": {"type": "lodging"},
    "P_COMANDANCIA": {"type": "closed_residential", "escudo": True},
    "P_BAR": {"type": "mixed_commercial"},
    "P_MERCADO": {"type": "warehouse"},
    "P_CULTURA": {"type": "closed_residential", "casona": True, "escudo": True},
    "P_HOGAR": {"type": "closed_residential"},
    "P_ALMACEN": {"type": "warehouse"},
}

PROGRAMME = [   # (id, name, anchor near (x, z), class, consolidate radius m, floors)
    ("P_AYTO", "Ayuntamiento", (-16.6, 25.4), "QUEST", 3.0, 3),
    ("P_IGLESIA", "Iglesia", (16.0, 24.5), "QUEST", 0.0, 2),
    ("P_PENSION", "Pensión", (12.0, 44.0), "QUEST", 2.5, 3),
    ("P_HOTEL", "Hotel", (16.2, -52.0), "QUEST", 2.5, 4),
    ("P_COMANDANCIA", "Comandancia (casa-cuartel)", (26.0, -104.0), "QUEST", 3.0, 3),
    ("P_BAR", "Bar de misión (taberna)", (50.2, -70.2), "QUEST", 2.0, 3),
    ("P_MERCADO", "Mercado de abastos", (33.0, -4.0), "QUEST", 2.5, 2),
    ("P_CULTURA", "Casa de Cultura", (-123.6, 63.4), "QUEST", 2.0, 3),
    ("P_HOGAR", "Hogar / Asociación vecinal", (-37.9, -49.8), "QUEST", 1.5, 2),
    ("P_ALMACEN", "Almacén / astillero de ribera", (124.1, -46.4), "QUEST", 2.0, 2),
]


def poly(p):
    shp = Polygon(p["outer"], [h for h in p["holes"] if len(h) >= 3])
    return shp if shp.is_valid else shp.buffer(0)


def idw(x, z, ctrl):
    num = den = 0.0
    for cx, cz, cy in ctrl:
        d2 = (cx - x) ** 2 + (cz - z) ** 2
        if d2 < 0.01:
            return cy
        w = 1.0 / d2 ** 1.5
        num += w * cy
        den += w
    return num / den


def level(x, z):
    r = float(np.hypot(x - KEEP[0], z - KEEP[1]))
    if r <= R_KEEP:
        return LV_KEEP
    if r <= R_EDGE:
        return LV_RING1
    if r <= R_RING2:
        return LV_RING2
    base = idw(x, z, TOWN_CONTROL)
    # blend down from the outer terrace edge so the hill meets the town smoothly
    t = min(1.0, (r - R_RING2) / 25.0)
    return round(LV_RING2 * (1 - t) + base * t, 2)


def stable(s):
    return int(hashlib.md5(s.encode()).hexdigest()[:6], 16)


def frontage(rect, pv):
    cs = list(rect.exterior.coords)[:4]
    best = None
    for k in range(4):
        a, c = np.array(cs[k]), np.array(cs[(k + 1) % 4])
        e = c - a
        Ln = float(np.linalg.norm(e))
        if Ln < 0.5:
            continue
        n = np.array([e[1], -e[0]]) / Ln
        if Point(*((a + c) / 2 + n * 0.5)).within(rect):
            n = -n
        probe = [Point(*(a + e * t + n * d)) for t in (0.2, 0.5, 0.8) for d in (1.0, 2.5, 4.0)]
        score = sum(1 for p in probe if pv.contains(p)) + 0.15 * Ln
        if best is None or score > best[0]:
            best = (score, Ln, a, c, n)
    others = []
    for k in range(4):
        a, c = np.array(cs[k]), np.array(cs[(k + 1) % 4])
        others.append(float(np.linalg.norm(c - a)))
    depth = min(o for o in others if abs(o - best[1]) > 0.01) if len({round(o, 2) for o in others}) > 1 else best[1]
    return best, depth


def spec_for(bid, flen, depth_len, kind, floors, btype):
    bays = max(2, int(round(flen / 2.0)))
    if depth_len <= 5:
        depth, roof = 4, "eaves"
    elif depth_len <= 7:
        depth, roof = 6, "eaves"
    elif depth_len <= 9.5 or bays > 4:
        depth, roof = 8, "eaves"
    else:
        depth, roof = int(min(12, 2 * round(depth_len / 2))), "gable"
    return {"id": bid, "type": btype, "bays": min(bays, 9), "depth": depth, "floors": floors, "roof": roof, "seed": stable(bid) % 100000}


def main():
    tr = json.loads(TRACE.read_text(encoding="utf-8"))
    island = unary_union([poly(p) for p in tr["island"]])
    banks = unary_union([poly(p) for p in tr["banks"]])
    water = unary_union([poly(p) for p in tr["water"]])
    paving = unary_union([poly(p) for p in tr["public_paving"]])
    yards = unary_union([poly(p) for p in tr["yards"]])
    green = unary_union([poly(p) for p in tr["yards_green"]])
    ring_pts = [tuple(q) for q in tr["outer_wall"]]
    near = lambda q: min(range(len(ring_pts)), key=lambda i: (ring_pts[i][0] - q[0]) ** 2 + (ring_pts[i][1] - q[1]) ** 2)
    i_e, i_w = near(ANTE[3]), near(ANTE[4])
    assert abs(i_e - i_w) == 1, (i_e, i_w)
    lo_i, hi_i = min(i_e, i_w), max(i_e, i_w)
    ring_pts = ring_pts[:lo_i] + ANTE_INNER + ring_pts[hi_i + 1:]      # the town wall runs along the inner arms
    town = Polygon(ring_pts).buffer(0)
    wall = LineString(ring_pts + [ring_pts[0]])
    ante = Polygon(ANTE).buffer(0)
    arms = unary_union([LineString(a) for a in ANTE_ARMS])
    stair_zone = Polygon([(GATE_N[0] - 4.5, GATE_N[1]), (GATE_N[0] + 4.5, GATE_N[1]), (GATE_N[0] + 4.5, GATE_N[1] + 11), (GATE_N[0] - 4.5, GATE_N[1] + 11)])
    finca_poly = Polygon(FINCA["towers"]).buffer(0)
    pv, yd, gr, tw, isl = prep(paving), prep(yards), prep(green), prep(town), prep(island)

    def ground(x, z):
        p = Point(x, z)
        if ante.contains(p):
            return QUAY_Y
        if Polygon(SOUTH_BANK).contains(p) and not island.contains(p) and not banks.contains(p):
            return 2.1
        if tw.contains(p):
            return level(x, z)
        return round(min(7.0, 1.6 + 0.035 * water.distance(p)), 2)

    # --------------------------------------------------------------- buildings: roofs + uncovered built masses
    plaza = Point(0, 0)
    bk = prep(banks)
    dropped = {"false_box": 0, "stall": 0, "wall_walk": 0, "keep": 0, "finca": 0, "port_clutter": 0, "outside": 0}

    def stall_like(rect, c):
        ring = rect.buffer(2.5).difference(rect)
        share = ring.intersection(paving).area / max(ring.area, 1e-6)
        if c.distance(plaza) < 21 or (c.distance(plaza) < 28 and rect.area < 60 and share > 0.3):
            return True
        return rect.area < 45 and share > 0.75                # free-standing on paving: stalls, carts, wells

    wall_zone = wall.buffer(2.2)
    stall_rects = []

    def admit(rect, c):
        if rect.area > 520:                                   # false boxes (rocks + walls around the port)
            dropped["false_box"] += 1
        elif stall_like(rect, c) or (Point(*KEEP).distance(c) > R_EDGE + 10 and Point(*KEEP).distance(c) < R_RING2 - 4 and rect.area < 60 and tw.contains(c)
                                     and rect.buffer(2.5).difference(rect).intersection(paving).area > 0.45 * rect.buffer(2.5).difference(rect).area):
            dropped["stall"] += 1                             # market stalls (plaza and the open lower ring): props later
            stall_rects.append([[round(x, 2), round(y, 2)] for x, y in list(rect.exterior.coords)[:4]])
        elif rect.intersection(wall_zone).area > 0.25 * rect.area or wall.distance(c) < 2.5:
            dropped["wall_walk"] += 1                         # wall walks and parapets read as roofs
        elif Point(*KEEP).distance(c) < R_KEEP:               # the keep is replaced by the Torre
            dropped["keep"] += 1
        elif finca_poly.buffer(1.5).contains(c) or rect.intersection(finca_poly).area > 2.0:   # the finca compound is rebuilt as a whole
            dropped["finca"] += 1
        elif ante.contains(c) and not (rect.area >= 60 and arms.distance(c) < 6 and not rect.intersects(stair_zone)):
            # the forecourt is an open quay: stalls come back as props; the pier and fishing gear read as roofs
            dropped["port_clutter"] += 1
            if rect.area < 45:
                stall_rects.append([[round(x, 2), round(y, 2)] for x, y in list(rect.exterior.coords)[:4]])
        elif not tw.contains(c) and not bk.contains(c) and not ante.contains(c):
            # outside the wall only the port suburb by the north gate and the far banks are built; the rest is shore rock
            dropped["outside"] += 1
        else:
            return True
        return False

    roofs = []
    for r in tr["roofs"]:
        rect = Polygon(r["rect"]).buffer(0)
        c = Point(*r["center"])
        if admit(rect, c):
            roofs.append({"id": r["id"], "rect": rect, "center": c, "roof": r["roof"], "src": "roof"})

    # the coherence trace misses dark slate and shaded roofs: fill the rest of each built mass with slabs
    covered = unary_union([rr["rect"] for rr in roofs]).buffer(0.6)
    added = 0
    for m in tr["built_masses"]:
        mp = Polygon(m["outline"]).buffer(0)
        rest = mp.difference(covered)
        parts = list(rest.geoms) if hasattr(rest, "geoms") else [rest]
        for k, part in enumerate(parts):
            part = part.buffer(-0.4).buffer(0.4)
            if part.is_empty or part.area < 16:
                continue
            for q in (list(part.geoms) if hasattr(part, "geoms") else [part]):
                mrr = q.minimum_rotated_rectangle
                cs = list(mrr.exterior.coords)[:4]
                e1, e2 = np.subtract(cs[1], cs[0]), np.subtract(cs[2], cs[1])
                l1, l2 = float(np.linalg.norm(e1)), float(np.linalg.norm(e2))
                if min(l1, l2) < 2.6:
                    continue
                axis, along_len = (e1 / l1, l1) if l1 >= l2 else (e2 / l2, l2)
                # slabs of 6-9 m along the long axis, split where the mass is thinnest is not observable here
                nslab = max(1, int(round(along_len / 7.5))) if (q.area / mrr.area < 0.6 or along_len > 11) else 1
                o = np.array(cs[0]) if l1 >= l2 else np.array(cs[1])
                perp = (e2 / l2) if l1 >= l2 else (-e1 / l1)
                width = l2 if l1 >= l2 else l1
                for s in range(nslab):
                    a0, a1 = along_len * s / nslab, along_len * (s + 1) / nslab
                    slab = Polygon([o + axis * a0 - perp * 50, o + axis * a1 - perp * 50, o + axis * a1 + perp * (width + 50), o + axis * a0 + perp * (width + 50)])
                    piece = q.intersection(slab)
                    if piece.is_empty or piece.area < 14:
                        continue
                    pr = piece.minimum_rotated_rectangle
                    pcs = list(pr.exterior.coords)[:4]
                    s1, s2 = float(np.linalg.norm(np.subtract(pcs[1], pcs[0]))), float(np.linalg.norm(np.subtract(pcs[2], pcs[1])))
                    if min(s1, s2) < 2.6 or max(s1, s2) / max(min(s1, s2), 1e-3) > 4.5 or piece.area / pr.area < 0.5:
                        continue
                    c = pr.centroid
                    if admit(pr, c):
                        added += 1
                        roofs.append({"id": f"{m['id']}_{k}{s}", "rect": pr, "center": c, "roof": m["roof"], "src": "mass"})
    print("roofs kept", sum(1 for r in roofs if r["src"] == "roof"), "mass slabs added", added, "dropped", dropped)

    # programme: consolidate contiguous footprints around each anchor
    taken = {}
    groups = []
    for pid, name, (ax, az), cls, rad, floors in PROGRAMME:
        cand = sorted((rr for rr in roofs if rr["id"] not in taken), key=lambda rr: rr["center"].distance(Point(ax, az)))
        if not cand or cand[0]["center"].distance(Point(ax, az)) > 25:
            continue
        core = [cand[0]]
        if rad > 0:
            changed = True
            while changed and len(core) < 4:
                changed = False
                union = unary_union([q["rect"] for q in core])
                for rr in cand[1:]:
                    if rr in core or rr["id"] in taken:
                        continue
                    if rr["rect"].distance(union) <= rad:
                        core.append(rr)
                        changed = True
                        break
        for q in core:
            taken[q["id"]] = pid
        groups.append((pid, name, cls, floors, core))

    buildings = []
    walkable = prep(unary_union([island, banks, ante]).buffer(0.5))
    PRIORITY = {"QUEST": 3, "SECONDARY": 2, "AMBIENT": 1}

    def kind_at(c):
        if ante.contains(c):
            return "ribera"
        if not tw.contains(c):
            return "huertas"
        dk = c.distance(Point(*KEEP))
        if dk < R_RING2 + 4:
            return "alta"
        if wall.distance(c) < 10:
            return "ribera"
        if c.distance(plaza) < 45 or abs(c.x) < 10:
            return "comercial"
        return "residencial"

    # ================= parcel pass: streets and squares -> frontage tramos -> parcels on them =================
    sys.path.insert(0, str(ROOT / "tools"))
    from open_space_streets import streets as open_streets
    # the town's open space between the admitted buildings (stalls, wells and trees do not cut streets), minus the
    # gardens, the finca and the Torre's plinth; its medial axis is the street network
    built_now = unary_union([rr["rect"] for rr in roofs])
    green_all = unary_union([poly(p_) for p_ in tr["yards_green"]])
    area_ = town.buffer(-WALL_HALF).union(ante)
    op = area_.difference(unary_union([built_now.buffer(0.35), green_all.buffer(-0.5), finca_poly.buffer(0.5), Point(*KEEP).buffer(R_KEEP)]))
    op = op.buffer(-0.9).buffer(0.9).buffer(0.6).buffer(-0.6)
    op = unary_union([Polygon(g.exterior, [h for h in g.interiors if Polygon(h).area > 30]) for g in (op.geoms if hasattr(op, "geoms") else [op]) if g.area > 20])
    pub_main = op
    pub_lanes = op
    # authored street plan (level design over the layout's corridors) + the open-space lanes it does not cover
    plan = json.loads((ROOT / "reconstruction" / "street_plan_v1.json").read_text(encoding="utf-8"))
    sys.path.insert(0, str(ROOT / "tools"))
    from open_space_streets import chaikin_open

    def resample(P, closed=False, tan_m=5):
        P = np.asarray(P, float)
        if closed:
            P = np.vstack([P, P[:1]])
        if not closed:
            P = chaikin_open(P, 3)
        ls = LineString(P)
        n = max(2, int(ls.length // 1.0))
        R = np.array([ls.interpolate(k * ls.length / n).coords[0] for k in range(n + 1)])
        m_ = len(R)
        T = np.array([R[(i + tan_m) % m_ if closed else min(m_ - 1, i + tan_m)] - R[(i - tan_m) % m_ if closed else max(0, i - tan_m)] for i in range(m_)])
        T /= np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-6)
        return R, T

    STREETS, LINES = [], []

    def add_street(R, T, hw, primary, sid, name):
        N = np.stack([-T[:, 1], T[:, 0]], axis=1)
        seg = np.linalg.norm(np.diff(R, axis=0), axis=1)
        STREETS.append({"id": sid, "name": name, "pts": R, "tan": T, "nor": N, "hw": np.full(len(R), hw), "len": float(seg.sum())})
        for sgn in (-1.0, 1.0):
            P = R + N * hw * sgn
            sg = np.linalg.norm(np.diff(P, axis=0), axis=1)
            LINES.append({"pts": P, "tan": T, "nor": -N * sgn, "s": np.concatenate([[0.0], np.cumsum(sg)]), "len": float(sg.sum()),
                          "primary": primary, "ls": LineString(P), "street": sid})

    for st in plan["streets"]:
        R, T = resample(st["pts"])
        add_street(R, T, st["width"] / 2, True, st["id"], st["name"])
    for st in plan["rings"]:
        R, T = resample(st["pts"], closed=True)
        add_street(R, T, st["width"] / 2, True, st["id"], st["name"])
    for pl in plan["plazas"]:
        # each plaza edge is a frontage line facing into the square
        Q = np.array(pl["poly"], float)
        cen = Q.mean(axis=0)
        for k in range(len(Q)):
            a_, b_ = Q[k], Q[(k + 1) % len(Q)]
            L_ = float(np.linalg.norm(b_ - a_))
            if L_ < 3:
                continue
            n_ = int(L_ // 1.0)
            P = np.array([a_ + (b_ - a_) * t / n_ for t in range(n_ + 1)])
            T = np.repeat(((b_ - a_) / L_)[None, :], len(P), axis=0)
            N = np.stack([-T[:, 1], T[:, 0]], axis=1)
            if np.dot(cen - (a_ + b_) / 2, N[0]) < 0:
                N = -N
            sg = np.linalg.norm(np.diff(P, axis=0), axis=1)
            LINES.append({"pts": P, "tan": T, "nor": N, "s": np.concatenate([[0.0], np.cumsum(sg)]), "len": float(sg.sum()),
                          "primary": True, "ls": LineString(P), "street": pl["id"]})
    authored_cl = unary_union([LineString(x["pts"]) for x in STREETS] + [Polygon(pl["poly"]).exterior for pl in plan["plazas"]])
    n_auth = len(LINES)
    for st in open_streets(op):
        far = np.array([authored_cl.distance(Point(*q)) > 7.0 for q in st["pts"]])
        idx = np.where(far)[0]
        runs, cur = [], []
        for i_ in idx:
            if cur and i_ != cur[-1] + 1:
                runs.append(cur)
                cur = []
            cur.append(i_)
        if cur:
            runs.append(cur)
        for r_ in runs:
            if len(r_) < 15 or sum(1 for i_ in r_ if ante.contains(Point(*st["pts"][i_]))) > len(r_) // 3:
                continue
            R = st["pts"][r_]
            T = st["tan"][r_]
            hw = float(np.clip(np.median(st["hw"][r_]), 1.5, 3.0))
            mid_ = R[len(R) // 2]
            near_ = min(range(n_auth), key=lambda k: LINES[k]["ls"].distance(Point(*mid_)))
            Ta = LINES[near_]["tan"][int(np.argmin(np.hypot(*(LINES[near_]["pts"] - mid_).T)))]
            Pa = np.array([-Ta[1], Ta[0]])
            Tl = R[-1] - R[0]
            Tl = Tl / max(1e-6, np.linalg.norm(Tl))
            grain = Ta if abs(np.dot(Tl, Ta)) >= abs(np.dot(Tl, Pa)) else Pa
            if np.dot(grain, Tl) < 0:
                grain = -grain
            # straight lane along the grain through the lane's own corridor (projected extent)
            u_ = (R - mid_) @ grain
            n_ = max(2, int((u_.max() - u_.min()) // 1.0))
            R = np.array([mid_ + grain * (u_.min() + (u_.max() - u_.min()) * k / n_) for k in range(n_ + 1)])
            T = np.repeat(grain[None, :], len(R), axis=0)
            add_street(R, T, hw, False, f"LANE_{len(STREETS)}", "callejón")
    print("streets:", len(plan["streets"]) + len(plan["rings"]), "authored +", len(STREETS) - len(plan["streets"]) - len(plan["rings"]), "lanes;",
          n_auth, "+", len(LINES) - n_auth, "frontage lines")
    ALLP = np.vstack([l["pts"] for l in LINES])
    ALLI = np.concatenate([[k] * len(l["pts"]) for k, l in enumerate(LINES)])
    ALLJ = np.concatenate([np.arange(len(l["pts"])) for l in LINES])
    print("frontage tramos:", sum(1 for l in LINES if l["primary"]), "street +", sum(1 for l in LINES if not l["primary"]),
          "lane;", round(sum(l["len"] for l in LINES)), "m")

    def at(li, sv):
        """Point, street direction and normal (into the street) of frontage line li at arc length sv (clamped)."""
        L = LINES[li]
        sv = min(max(sv, 0.0), L["s"][-1])
        j = int(np.searchsorted(L["s"], sv, side="right") - 1)
        j = min(max(j, 0), len(L["pts"]) - 2)
        t = (sv - L["s"][j]) / max(1e-6, L["s"][j + 1] - L["s"][j])
        P = L["pts"][j] * (1 - t) + L["pts"][j + 1] * t
        T = L["tan"][j] * (1 - t) + L["tan"][j + 1] * t
        T = T / max(1e-6, np.linalg.norm(T))
        N = np.array([-T[1], T[0]])
        if np.dot(N, L["nor"][j]) < 0:
            N = -N
        return P, T, N

    def emit(rr, sem_id, sem_name, cls, floors=None, btype=None):
        rect = rr["rect"]
        c = np.array(rect.centroid.coords[0])
        cs = np.array(rect.exterior.coords)[:4]
        kind = kind_at(rr["center"])
        d = np.hypot(*(ALLP - c).T)
        best = None
        for k in np.argsort(d)[:600]:
            if d[k] > 20:
                break
            li, pj = int(ALLI[k]), int(ALLJ[k])
            L = LINES[li]
            sv = L["ls"].project(Point(*c))
            P, T, N = at(li, sv)
            if np.dot(c - P, N) > 0.5:          # the building must stand on the block side of the line
                continue
            dist = rect.distance(Point(*P))
            if dist > (10.0 if L["primary"] else 6.0):
                continue
            score = dist + (0.0 if L["primary"] else 3.0)
            if best is None or score < best[0]:
                best = (score, li, sv)
        b = {"id": rr["id"], "semantic_id": sem_id, "semantic_name": sem_name, "class": cls, "kind": kind,
             "roof_seen": rr["roof"], "trace_area_m2": round(rect.area, 1), "floors": floors, "btype": btype, "rect": rect}
        if best is not None:
            _, li, sv = best
            L = LINES[li]
            P, T, N = at(li, sv)
            u = (cs - P) @ T
            v = (P - cs) @ N                       # depth into the block
            u0, u1, v0, v1 = u.min(), u.max(), max(0.0, v.min()), v.max()
            front = 0.0 if v0 < 5.0 else v0       # close to the street: the facade comes onto the line
            b.update(line=li, s0=float(sv + u0), s1=float(sv + u1), front=front,
                     D=float(min(12.0, max(4.0, v1 - front))), primary=L["primary"])
        else:
            # deep inside a block: keep the plot, align it with the nearest tramo (parallel to the block's streets)
            k = int(np.argmin(d))
            li_ = int(ALLI[k])
            _, T, _ = at(li_, LINES[li_]["ls"].project(Point(*c)))
            N = np.array([-T[1], T[0]])
            u, v = cs @ T, cs @ N
            opts = []
            for f in (N, -N, T, -T):
                ax = np.array([f[1], -f[0]])
                uu, vv = cs @ ax, cs @ f
                mid = ax * (uu.min() + uu.max()) / 2 + f * vv.max()
                opts.append((f, mid, float(uu.max() - uu.min()), float(vv.max() - vv.min())))
            b.update(line=None, opts=opts)
        buildings.append(b)

    for pid, name, cls, floors, core in groups:
        for q in core:
            emit(q, pid, name, cls, floors, "mixed_commercial" if pid in ("P_BAR", "P_MERCADO", "P_HOTEL", "P_PENSION") else "closed_residential")
    rest = [rr for rr in roofs if rr["id"] not in taken]
    for rr in rest:
        c = rr["center"]
        on_main = tw.contains(c) and (c.distance(plaza) < 45 or abs(c.x) < 12)
        emit(rr, f"S_{rr['id']}", "", "SECONDARY" if on_main else "AMBIENT")

    # ---- contiguity along each tramo: facades meet at party walls; a crack under 2.4 m is not a street
    merged = 0
    for li in range(len(LINES)):
        seq = sorted([b for b in buildings if b.get("line") == li and b["front"] == 0.0], key=lambda b: b["s0"])
        for a_, b_ in zip(seq[:-1], seq[1:]):
            gap = b_["s0"] - a_["s1"]
            if gap < 2.4:
                m_ = (a_["s1"] + b_["s0"]) / 2
                a_["s1"], b_["s0"] = m_, m_
        for i_, b_ in enumerate(seq):
            if b_["s1"] - b_["s0"] < 3.6:          # a sliver plot joins its neighbour
                nb = seq[i_ - 1] if i_ > 0 and not seq[i_ - 1].get("_drop") else (seq[i_ + 1] if i_ + 1 < len(seq) else None)
                if nb is not None and abs(nb["s1"] - b_["s0"]) < 0.01:
                    nb["s1"] = b_["s1"]
                elif nb is not None and abs(b_["s1"] - nb["s0"]) < 0.01:
                    nb["s0"] = b_["s0"]
                b_["_drop"] = True
                merged += 1
    buildings[:] = [b for b in buildings if not b.get("_drop")]

    # long frontages split into houses (a single house is rarely more than 16 m of street)
    extra = []
    for b in buildings:
        if b.get("line") is not None and b["s1"] - b["s0"] > 11.0 and b["class"] != "QUEST":
            n_ = int(math.ceil((b["s1"] - b["s0"]) / 7.0))
            w_ = (b["s1"] - b["s0"]) / n_
            for k in range(1, n_):
                nb = dict(b, id=f"{b['id']}_{k}", semantic_id=f"S_{b['id']}_{k}", s0=b["s0"] + k * w_, s1=b["s0"] + (k + 1) * w_)
                extra.append(nb)
            b["s1"] = b["s0"] + w_
    buildings.extend(extra)

    # ---- geometry in metres: facade on the tramo at the plot's centre, oriented with the street there
    for b in buildings:
        if b.get("line") is not None:
            sc = (b["s0"] + b["s1"]) / 2
            P, T, N = at(b["line"], sc)
            b["W"] = float(min(18.0, max(3.6, b["s1"] - b["s0"])))
            b["mid"] = P - N * b["front"]
            b["n"] = N
        else:
            best = None
            for f, mid, W, D in b["opts"]:
                ax = np.array([f[1], -f[0]])
                q = Point(*(mid + f * 1.5))
                sc_ = (2 if pub_lanes.contains(q) else 0) + (1 if walkable.contains(q) else 0) + 0.05 * W
                if best is None or sc_ > best[0]:
                    best = (sc_, f, mid, W, D)
            _, f, mid, W, D = best
            b.update(W=float(min(18.0, max(3.6, W))), D=float(min(12.0, max(4.0, D))), mid=mid, n=f)
            b.pop("opts", None)

    def foot(b):
        n = np.asarray(b["n"], float)
        xd = np.array([n[1], -n[0]])
        o = np.asarray(b["mid"], float) - xd * b["W"] / 2
        return o, n, xd, Polygon([o, o + xd * b["W"], o + xd * b["W"] - n * b["D"], o - n * b["D"]])

    def rank(b):
        return (PRIORITY.get(b["class"], 1), b.get("line") is not None and b.get("front", 1) == 0.0, b.get("line") is not None, b["W"] * b["D"])

    def trim(b, fr_b, inter):
        """Trim b out of inter: at the party wall (metres of frontage) or at the back; False if it cannot."""
        o, n, xd, _ = fr_b
        geoms = list(inter.geoms) if hasattr(inter, "geoms") else [inter]
        coords = [q for g in geoms if g.geom_type == "Polygon" for q in g.exterior.coords]
        if not coords:
            return True
        us = np.array([float(np.dot(np.array(q) - o, xd)) for q in coords])
        vs = np.array([float(np.dot(o - np.array(q), n)) for q in coords])
        umin, umax, vmin = us.min(), us.max(), vs.min()
        W = b["W"]
        if vmin > 3.9 and b["D"] - (b["D"] - vmin) >= 4.0:
            b["D"] = float(vmin - 0.05)
            return True
        if (umin <= 0.3 or umax >= W - 0.3) and umax - umin < 0.6 * W and W - (umax - umin) >= 3.6:
            cut = umax - umin + 0.05
            b["W"] = W - cut
            b["mid"] = np.asarray(b["mid"]) + xd * (cut / 2 if umin <= 0.3 else -cut / 2)
            if b.get("line") is not None:
                if umin <= 0.3:
                    b["s0"] += cut
                else:
                    b["s1"] -= cut
            return True
        return False

    tower_pts = [Point(*t["pos"]) for t in tr["towers"] if t["outer_wall"]] + [Point(*q) for q in ANTE_INNER + [ANTE[3], ANTE[4]]]
    fixed = unary_union([wall.buffer(WALL_HALF + 0.1), arms.buffer(WALL_HALF + 0.1), finca_poly.buffer(0.4)] + [q.buffer(3.4) for q in tower_pts])
    removed, trims = [], 0
    for it in range(16):
        changed = False
        fr = [foot(b) for b in buildings]
        for i, b in enumerate(buildings):
            inter = fr[i][3].intersection(fixed)
            if inter.area > 0.3 and not b.get("_drop"):
                if not trim(b, fr[i], inter):
                    b["_drop"] = True
                trims += 1
                changed = True
        fr = [foot(b) for b in buildings]
        for i in range(len(buildings)):
            for j in range(i + 1, len(buildings)):
                if buildings[i].get("_drop") or buildings[j].get("_drop"):
                    continue
                inter = fr[i][3].intersection(fr[j][3])
                if inter.area <= 0.3:
                    continue
                vi = i if rank(buildings[i]) < rank(buildings[j]) else j
                if not trim(buildings[vi], fr[vi], inter):
                    buildings[vi]["_drop"] = True
                trims += 1
                changed = True
        if any(b.get("_drop") for b in buildings):
            removed += [b["id"] for b in buildings if b.get("_drop")]
            buildings[:] = [b for b in buildings if not b.get("_drop")]
        if not changed:
            break
    left = sum(1 for i in range(len(buildings)) for j in range(i + 1, len(buildings)) if foot(buildings[i])[3].intersection(foot(buildings[j])[3]).area > 0.3)
    print("parcel pass: merged slivers", merged, "split long", len(extra), "trims", trims, "removed", len(removed), "overlaps left", left)

    # ---- kit dimensions: 2 m bays scaled to the plot (0.8-1.25), kit depths scaled to the plot's depth
    others_poly = None

    def finalize(b):
        W, D = b["W"], b["D"]
        bays = int(min(9, max(2, round(W / 2.0))))
        while W / (2 * bays) > 1.25 and bays < 9:
            bays += 1
        while W / (2 * bays) < 0.8 and bays > 2:
            bays -= 1
        if D >= 9.0 and bays <= 4:
            roof, depth = "gable", int(min(12, max(4, 2 * round(D / 2))))
        else:
            D = min(D, 9.6)
            roof = "eaves"
            depth = min((4, 6, 8), key=lambda k: abs(math.log(D / k)))
        b["D"] = D
        return bays, depth, roof, round(W / (2 * bays), 4), round(D / depth, 4)

    def door_ok(b, others):
        o, n, xd, poly_ = foot(b)
        mid = np.asarray(b["mid"])
        y0 = ground(*(mid + n * 0.4))
        for off in (0.0, -b["W"] / 3, b["W"] / 3):
            for dd in (1.0, 2.4):
                q = mid + xd * off + n * dd
                pq = Point(*q)
                if not walkable.contains(pq) or wall.distance(pq) < WALL_HALF + 0.3 or others.contains(pq):
                    return False
                if abs(ground(*q) - y0) > 0.6:
                    return False
        return True

    all_foot = [foot(b)[3] for b in buildings]
    for i, b in enumerate(buildings):
        others = prep(unary_union(all_foot[:i] + all_foot[i + 1:]))
        b["door"] = door_ok(b, others)
        q = np.asarray(b["mid"]) + np.asarray(b["n"]) * 2.0
        b["paving"] = 9 if pub_main.contains(Point(*q)) else (5 if pub_lanes.contains(Point(*q)) else 0)
        bays, depth, roof, sx, sz = finalize(b)
        floors = b.pop("floors") or (2 if b["W"] * b["D"] < 40 else 3)
        btype = b.pop("btype") or ("mixed_commercial" if (b["kind"] == "comercial" and b["paving"] >= 9 and b["door"]) else "closed_residential")
        mid = np.asarray(b["mid"])
        b["frontage_mid"] = [round(float(mid[0]), 2), 0.0, round(float(mid[1]), 2)]
        b["facing"] = [round(float(b["n"][0]), 4), round(float(b["n"][1]), 4)]
        b["spec"] = {"id": b["id"], "type": btype, "bays": bays, "depth": depth, "floors": floors, "roof": roof,
                     "seed": stable(b["id"]) % 100000, "sx": sx, "sz": sz}
        b["W"], b["D"] = round(b["W"], 2), round(b["D"], 2)
        b["tramo"] = b.get("line")

    # ---- orientation coherence along the tramos (owner metric: neighbours within 20-40 m differ by <= 5-15 deg)
    diffs, curve_ok = [], 0
    for li in range(len(LINES)):
        seq = sorted([b for b in buildings if b.get("line") == li], key=lambda b: b["s0"])
        for a_, b_ in zip(seq[:-1], seq[1:]):
            if b_["s0"] - a_["s1"] > 6:
                continue
            ang = math.degrees(math.acos(max(-1, min(1, float(np.dot(a_["n"], b_["n"]))))))
            diffs.append(ang)
    diffs = np.array(diffs) if diffs else np.zeros(1)
    COHERENCE = {"pairs": int(len(diffs)), "p50_deg": round(float(np.percentile(diffs, 50)), 1), "p90_deg": round(float(np.percentile(diffs, 90)), 1),
                 "max_deg": round(float(diffs.max()), 1), "over_15": int((diffs > 15).sum()),
                 "on_tramo": sum(1 for b in buildings if b.get("line") is not None), "interior": sum(1 for b in buildings if b.get("line") is None)}
    print("orientation coherence:", COHERENCE)

    # ---- tapias: the street edge between facades is closed by garden walls with a gate; alleys stay open
    TAPIAS = []
    for li, L in enumerate(LINES):
        occ_ = sorted([(b["s0"], b["s1"]) for b in buildings if b.get("line") == li and b["front"] == 0.0])
        free_, cur = [], 0.0
        for a0, a1 in occ_:
            if a0 - cur > 1.2:
                free_.append((cur, a0))
            cur = max(cur, a1)
        if L["s"][-1] - cur > 1.2:
            free_.append((cur, float(L["s"][-1])))
        for f0, f1 in free_:
            if f1 - f0 > 45:
                continue
            ss = np.linspace(f0 + 0.2, f1 - 0.2, max(2, int((f1 - f0) // 1.0) + 1))
            pts_, ok_ = [], True
            for sv in ss:
                P, T, N = at(li, sv)
                inner = P - N * 1.6
                pi_ = Point(*inner)
                if pub_lanes.contains(pi_) or not tw.contains(pi_) or fixed.contains(pi_) or water.contains(pi_):
                    ok_ = False      # an alley mouth, the wall or the water: no tapia here
                    if len(pts_) >= 2:
                        TAPIAS.append({"pts": pts_, "gate": len(pts_) >= 6})
                    pts_ = []
                    continue
                qq = P - N * 0.3
                pts_.append([round(float(qq[0]), 2), round(ground(*qq), 2), round(float(qq[1]), 2)])
            if len(pts_) >= 2:
                TAPIAS.append({"pts": pts_, "gate": len(pts_) >= 6})
    print("tapias:", len(TAPIAS), "runs,", round(sum(len(t["pts"]) for t in TAPIAS)), "m")
    for b in buildings:
        for k in ("rect", "mid", "n", "line", "s0", "s1", "front", "primary"):
            b.pop(k, None)

    # ---- one way in per semantic building: the main cell of a consolidated programme keeps the door
    for pid, name, cls, floors, core in groups:
        cells = [b for b in buildings if b["semantic_id"] == pid]
        if not cells:
            continue
        main = max(cells, key=lambda b: (b["door"], b["paving"], b["spec"]["bays"]))
        look = PROGRAMME_LOOK.get(pid, {})
        for b in cells:
            b["main"] = b is main
            if b is not main:
                b["door"] = False
            # one building, one character: the cells of a programme share seed (render, family), type and storeys
            b["spec"]["palette_key"] = pid
            b["spec"]["seed"] = stable(pid) % 100000
            b["spec"]["type"] = look.get("type", b["spec"]["type"])
            if b["spec"]["type"] == "lodging" and b["spec"]["roof"] == "gable":
                pass
            for k, v in look.items():
                if k != "type" and (b is main or k in ("stone", "casona")):
                    b["spec"][k] = v
    for b in buildings:
        b.setdefault("main", True)
        mx, _, mz = b["frontage_mid"]
        n = np.array(b["facing"])
        mid = np.array([mx, mz])
        door_y = ground(*(mid + n * 1.5))
        xd = np.array([n[1], -n[0]])
        o = mid - xd * b["W"] / 2
        back = mid - n * b["D"]
        b["frontage_mid"][1] = round(door_y, 2)
        b["spec"]["basement"] = round(max(0.0, min(4.0, door_y - min(ground(*back), ground(*o), ground(*(o + xd * b["W"]))))), 2)
        if not b["door"] and b["main"] and b["class"] != "QUEST":
            b["class"] = "AMBIENT"            # no reachable way in: an ordinary closed house
        b.pop("paving", None)

    def placed(b):
        """Footprint on the ground in metres (kit bays x scale)."""
        sp = b["spec"]
        mx, _, mz = b["frontage_mid"]
        n = np.array(b["facing"])
        xd = np.array([n[1], -n[0]])
        W = b.get("W", 2 * sp["bays"] * sp.get("sx", 1.0))
        D = b.get("D", sp["depth"] * sp.get("sz", 1.0))
        o = np.array([mx, mz]) - xd * W / 2
        return Polygon([o, o + xd * W, o + xd * W - n * D, o - n * D])

    church = next((b for b in buildings if b["semantic_id"] == "P_IGLESIA" and b["main"]), None)
    if church:
        sp = church["spec"]
        n = sp["bays"]
        sp["rows"] = ["".join("A" if i == n // 2 else "P" for i in range(n))] + ["".join("T" if i % 2 == 1 else "P" for i in range(n))] * (sp["floors"] - 1)
        sp["chimney"] = False
        sp["history"] = False
        nn = np.array(church["facing"])
        xd = np.array([nn[1], -nn[0]])
        o = np.array([church["frontage_mid"][0], church["frontage_mid"][2]]) - xd * church["W"] / 2
        others = unary_union([placed(b) for b in buildings if b is not church])
        for side in (-1, 1):
            # belfry 4 m square beside the front corner, flush with the facade
            base = o + xd * (-4.0 if side < 0 else church["W"])
            tw_poly = Polygon([base, base + xd * 4.0, base + xd * 4.0 - nn * 4.0, base - nn * 4.0])
            if not tw_poly.intersects(others) and walkable.contains(tw_poly.centroid):
                mid = base + xd * 2.0
                buildings.append({"id": "P_IGLESIA_CAMPANARIO", "semantic_id": "P_IGLESIA", "semantic_name": "Iglesia", "class": "QUEST", "kind": church["kind"],
                                  "frontage_mid": [round(float(mid[0]), 2), church["frontage_mid"][1], round(float(mid[1]), 2)],
                                  "facing": church["facing"], "roof_seen": "special", "trace_area_m2": 0.0, "door": False, "main": False, "W": 4.0, "D": 4.0,
                                  "spec": {"id": "P_IGLESIA_CAMPANARIO", "type": "landmark", "bays": 2, "depth": 4, "floors": sp["floors"] + 3,
                                           "roof": "tower", "seed": stable("P_IGLESIA") % 100000, "basement": sp.get("basement", 0.0), "stone": True,
                                           "palette_key": "P_IGLESIA"}})
                break

    # accessible share: QUEST + SECONDARY + a share of AMBIENT homes with a reachable door (visitable) up to 60 %
    sem = {}
    for b in buildings:
        if b["main"]:
            sem[b["semantic_id"]] = b
    sem_list = list(sem.values())
    need = math.ceil(0.6 * len(sem_list))
    acc = [x for x in sem_list if x["class"] in ("QUEST", "SECONDARY")]
    amb = sorted([x for x in sem_list if x["class"] == "AMBIENT" and x["door"]], key=lambda x: stable(x["semantic_id"]))
    for x in amb[: max(0, need - len(acc))]:
        x["class"] = "AMBIENT_ACCESSIBLE"
    access = {x["semantic_id"]: x["class"] for x in sem_list}
    for b in buildings:
        b["class"] = access.get(b["semantic_id"], b["class"])

    # --------------------------------------------------------------- special builds

    def add_special(bid, sem_id, name, cls, mid_xz, facing, spec, extra):
        y = extra.pop("y", None)
        b = {"id": bid, "semantic_id": sem_id, "semantic_name": name, "class": cls, "kind": "alta",
             "frontage_mid": [round(float(mid_xz[0]), 2), round(float(y if y is not None else ground(*mid_xz)), 2), round(float(mid_xz[1]), 2)],
             "facing": [round(float(facing[0]), 4), round(float(facing[1]), 4)], "roof_seen": "special", "trace_area_m2": 0.0,
             "spec": dict(spec, id=bid, seed=stable(bid) % 100000)}
        b["spec"].update(extra)
        buildings.append(b)
        return b

    # La Torre: casa-torre de silleria on the keep plinth, facing the town (east), with its palace wing to the south
    kx, kz = float(KEEP[0]), float(KEEP[1])
    add_special("P_TORRE", "P_TORRE", "La Torre (casa-torre)", "QUEST", (kx + 4.0, kz), (1.0, 0.0),
                {"type": "closed_residential", "bays": 4, "depth": 8, "floors": 5, "roof": "eaves", "basement": 0.0},
                {"y": LV_KEEP, "stone": True, "escudo": True, "chimney": False, "history": False,
                 "rows": ["PAPP", "PPTP", "TPPT", "PIPP", "TPTP"], "left": ["PPPP", "PTPP", "PPTP", "PTPP", "PPTP"],
                 "right": ["PPPP", "PPTP", "PTPP", "PPTP", "PTPP"]})
    add_special("P_TORRE_PALACIO", "P_TORRE", "La Torre (casa-torre)", "QUEST", (kx + 4.0, kz - 4.0 - 6.05), (1.0, 0.0),
                {"type": "closed_residential", "bays": 6, "depth": 8, "floors": 3, "roof": "eaves", "basement": 0.0},
                {"y": LV_KEEP, "stone": True, "escudo": True, "solana": True})

    # La Finca del Cacique: walled casona with three ways in (main gate, collapsed back wall, orujo cellars)
    fw = [np.array(p, float) for p in FINCA["towers"]]
    edges = []
    for k in range(4):
        a, c2 = fw[k], fw[(k + 1) % 4]
        e = c2 - a
        Ln = float(np.linalg.norm(e))
        n = np.array([e[1], -e[0]]) / Ln
        if finca_poly.contains(Point(*((a + c2) / 2 + n * 0.8))):
            n = -n
        probe = [Point(*(a + e * t + n * d)) for t in (0.2, 0.4, 0.6, 0.8) for d in (1.5, 3.0, 5.0)]
        edges.append({"k": k, "a": a, "b": c2, "len": Ln, "n": n, "paving": sum(1 for q in probe if pv.contains(q)),
                      "to_wall": water.distance(Point(*((a + c2) / 2)))})
    main_e = max(edges, key=lambda e: (e["paving"], -e["to_wall"]))
    back_e = edges[(main_e["k"] + 2) % 4]
    cellar_e = min((e for e in edges if e["k"] not in (main_e["k"], back_e["k"])), key=lambda e: e["to_wall"])
    fy = round(ground(*np.mean(fw, axis=0)), 2)
    # casona against the back wall, facing the patio and the main gate
    bn = -back_e["n"]                                     # inward from the back wall
    bmid = (back_e["a"] + back_e["b"]) / 2
    fbays = int(min(6, max(4, (back_e["len"] - 3.0) // 2)))
    add_special("P_FINCA_CASONA", "P_FINCA", "Finca del Cacique", "QUEST", bmid + bn * (8.0 + 0.9), bn,
                {"type": "closed_residential", "bays": fbays, "depth": 8, "floors": 3, "roof": "eaves", "basement": 0.0},
                {"y": fy, "escudo": True, "solana": True, "casona": True})
    finca = {"id": "P_FINCA", "name": "Finca del Cacique", "y": fy, "towers": [p.tolist() for p in fw],
             "wall_height": 3.4, "wall_thickness": 0.7,
             "edges": [{"a": e["a"].round(2).tolist(), "b": e["b"].round(2).tolist(),
                        "role": "porton" if e is main_e else "derrumbe" if e is back_e else "bodega" if e is cellar_e else "muro"} for e in edges],
             "porton_width": 3.2, "derrumbe_width": 4.5,
             "bodega": {"pos": ((cellar_e["a"] + cellar_e["b"]) / 2 + cellar_e["n"] * 1.6).round(2).tolist(), "facing": cellar_e["n"].round(4).tolist(),
                        "y": round(ground(*((cellar_e["a"] + cellar_e["b"]) / 2 + cellar_e["n"] * 1.6)), 2)}}

    # --------------------------------------------------------------- terrain
    corridors = []
    for bid_, g0, far, wdt in BRIDGES:
        d = np.subtract(far, g0) / np.linalg.norm(np.subtract(far, g0))
        corridors.append(LineString([np.add(g0, d * WALL_HALF), np.subtract(far, d * 1.0)]).buffer(wdt / 2 + 0.8, cap_style=2))
    corridor = prep(unary_union(corridors))
    south_bank, south_road = Polygon(SOUTH_BANK), prep(Polygon(SOUTH_ROAD))
    land = unary_union([island, banks, south_bank])
    minx, minz, maxx, maxz = land.bounds
    cols, rows = int((maxx - minx) / CELL) + 1, int((maxz - minz) / CELL) + 1
    lp = prep(land)
    cells = []
    for j in range(rows):
        for i in range(cols):
            x, z = minx + (i + 0.5) * CELL, minz + (j + 0.5) * CELL
            pt = Point(x, z)
            if not lp.contains(pt) and not ante.contains(pt):
                continue
            if corridor.contains(pt) and not tw.contains(pt):
                continue                                  # the bridge deck was traced as land: it is river
            if south_bank.contains(pt) and not (isl.contains(pt) or banks.contains(pt)):
                cells.append([i, j, 2.1 if south_road.contains(pt) else round(2.0 + 0.02 * max(0.0, -150.0 - z), 2), 0 if south_road.contains(pt) else 5])
                continue
            if PIER_WATER[0] <= x <= PIER_WATER[2] and PIER_WATER[1] <= z <= PIER_WATER[3]:
                continue
            if ante.contains(pt):
                cells.append([i, j, QUAY_Y, 0])
                continue
            inside = tw.contains(pt)
            if pv.contains(pt):
                cls = 0                                   # canto rodado (public)
            elif gr.contains(pt):
                cls = 2                                   # huerta / grass
            elif yd.contains(pt):
                cls = 1 if inside else 2                  # old cobbles inside the town; field outside
            elif inside:
                cls = 3                                   # ground under/around buildings
            else:
                cls = 4 if isl.contains(pt) else 5        # shore rock / bank grass
            cells.append([i, j, round(ground(x, z), 2), cls])

    wall_pts = []
    for k in range(int(wall.length // 2.0) + 1):
        p = wall.interpolate(k * 2.0)
        wall_pts.append([round(p.x, 2), round(level(p.x, p.y), 2), round(p.y, 2)])   # the town-side level
    # paseo deck height: the inner ground along the wall, smoothed (running max then mean over +-12 m) plus PASEO_UP,
    # so the walk rises and falls gently with the town instead of stepping at every house
    yin = np.array([q[1] for q in wall_pts])
    m = len(yin)
    k = 6
    ymax = np.array([max(yin[(i + d) % m] for d in range(-k, k + 1)) for i in range(m)])
    ytop = np.array([ymax[[(i + d) % m for d in range(-k, k + 1)]].mean() for i in range(m)]) + PASEO_UP
    gate_xy = [np.array([g[0], g[1]]) for g in (GATE_N, tr["landmarks_m"]["south_gate"], EAST_GATE)]
    gap = [any(np.hypot(q[0] - g[0], q[2] - g[1]) < 5.5 for g in gate_xy) for q in wall_pts]
    paseo_pts = [[q[0], q[1], q[2], round(float(ytop[i]), 2), bool(gap[i])] for i, q in enumerate(wall_pts)]

    def top_at(x, z):
        i = min(range(m), key=lambda j: (wall_pts[j][0] - x) ** 2 + (wall_pts[j][2] - z) ** 2)
        return float(ytop[i])

    towers = [{"pos": t["pos"], "top": round(top_at(*t["pos"]), 2), "role": "cubo-mirador"} for t in tr["towers"] if t["outer_wall"]]
    for q in ANTE_INNER + [ANTE[3], ANTE[4]]:
        if all((t["pos"][0] - q[0]) ** 2 + (t["pos"][1] - q[1]) ** 2 > 9 for t in towers):
            towers.append({"pos": list(q), "top": round(QUAY_Y + PASEO_UP if q in (ANTE[3], ANTE[4]) else top_at(*q), 2), "role": "cubo-antepuerto"})
    spurs = []
    for a, b in ANTE_ARMS:
        ln = LineString([a, b])
        ya = top_at(*a)
        npts = int(ln.length // 2.0) + 1
        pts_ = [[round(ln.interpolate(k2 * 2.0).x, 2), QUAY_Y, round(ln.interpolate(k2 * 2.0).y, 2)] for k2 in range(npts)] + [[b[0], QUAY_Y, b[1]]]
        # the arm's paseo comes down from the ring's height to the quay's own (QUAY_Y + PASEO_UP) towards its end
        tops = [round(ya + (QUAY_Y + PASEO_UP - ya) * min(1.0, k2 / max(1, len(pts_) - 4)), 2) for k2 in range(len(pts_))]
        spurs.append({"points": pts_, "tops": tops})
    foot = unary_union([placed(b) for b in buildings]).buffer(0.3)

    def ring(radius, low, high, targets, stair_len):
        """Retaining wall on a circle where no house holds the step, with stairs at the gaps nearest the targets."""
        n = 720
        pts = [(kx + radius * math.cos(2 * math.pi * i / n), kz + radius * math.sin(2 * math.pi * i / n)) for i in range(n)]
        free = [not foot.contains(Point(*q)) for q in pts]
        stairs = []
        for tdeg in targets:
            best = None
            for i in range(n):
                ang = 2 * math.pi * i / n
                q = np.array(pts[i])
                out = np.array([math.cos(ang), math.sin(ang)])
                side = np.array([-out[1], out[0]])
                fp = Polygon([q - side * 1.4, q + side * 1.4, q + side * 1.4 + out * stair_len, q - side * 1.4 + out * stair_len])
                span = int(math.ceil(1.6 / (2 * math.pi * radius / n)))
                if not all(free[(i + d) % n] for d in range(-span, span + 1)) or fp.intersects(foot) or not tw.contains(fp.centroid):
                    continue
                dd = abs((math.degrees(ang) - tdeg + 180) % 360 - 180)
                if best is None or dd < best[0]:
                    best = (dd, i, q, out)
            if best and best[0] < 50 and all(abs(best[1] - st["i"]) > 20 for st in stairs):
                stairs.append({"i": best[1], "top": [round(float(best[2][0]), 2), high, round(float(best[2][1]), 2)],
                               "dir": [round(float(best[3][0]), 4), round(float(best[3][1]), 4)], "width": 2.6, "low": low})
        segs, run = [], None
        blocked = set()
        for st in stairs:
            span = int(math.ceil(1.4 / (2 * math.pi * radius / n)))
            blocked |= {(st["i"] + d) % n for d in range(-span, span + 1)}
        for i in range(n + 1):
            ok = free[i % n] and (i % n) not in blocked and i < n
            if ok and run is None:
                run = i
            if (not ok) and run is not None:
                if i - run >= 2:
                    segs.append([[round(pts[j % n][0], 2), round(pts[j % n][1], 2)] for j in range(run, i, 6)] + [[round(pts[(i - 1) % n][0], 2), round(pts[(i - 1) % n][1], 2)]])
                run = None
        for st in stairs:
            st.pop("i")
        return {"center": [kx, kz], "radius": radius, "low": low, "high": high, "walls": segs, "stairs": stairs}

    terraces = [ring(R_KEEP, LV_RING1, LV_KEEP, [0, 90, 180, 270], 3.4),
                ring(R_EDGE, LV_RING2, LV_RING1, [10, 100, 190, 280], 7.8)]
    foot_all = unary_union([placed(b) for b in buildings])
    ring_ls = LineString([(q[0], q[2]) for q in wall_pts] + [(wall_pts[0][0], wall_pts[0][2])])
    paseo_stairs = []

    def stair_at(i, sense):
        """Stairs against the inner face: top landing beside the deck at point i, flight descending along the wall."""
        a = np.array([wall_pts[i][0], wall_pts[i][2]])
        b2 = np.array([wall_pts[(i + sense) % m][0], wall_pts[(i + sense) % m][2]])
        t = (b2 - a) / max(1e-6, np.linalg.norm(b2 - a))
        inner = np.array([-t[1], t[0]])
        if not tw.contains(Point(*(a + inner * 6))):
            inner = -inner
        drop = float(ytop[i]) - ground(*(a + inner * 3.3 + t * 5.5))
        if drop < 0.6 or drop > 4.5:
            return None
        run = math.ceil(drop / 0.15) * 0.32
        c0 = a + inner * (WALL_HALF + 0.05)
        fp = Polygon([c0 - t * 1.3, c0 - t * 1.3 + inner * 2.3, c0 + t * (run + 0.6) + inner * 2.3, c0 + t * (run + 0.6)])
        if fp.intersects(foot_all.buffer(0.3)) or not tw.contains(fp.centroid) or fp.intersects(fixed.difference(wall.buffer(WALL_HALF + 0.1))):
            return None
        landing = a + inner * (WALL_HALF + 1.15)
        return {"landing": [round(float(landing[0]), 2), round(float(ytop[i]), 2), round(float(landing[1]), 2)],
                "top": [round(float(landing[0] + t[0] * 0.6), 2), round(float(ytop[i]), 2), round(float(landing[1] + t[1] * 0.6), 2)],
                "dir": [round(float(t[0]), 4), round(float(t[1]), 4)], "width": 2.2, "low": round(drop and float(ytop[i]) - drop, 2), "i": i}

    for g in gate_xy:
        gi = [i for i in range(m) if gap[i]]
        near = [i for i in gi if np.hypot(wall_pts[i][0] - g[0], wall_pts[i][2] - g[1]) < 5.5]
        if not near:
            continue
        for sense in (-1, 1):
            edge = min(near, key=lambda i: -sense * ((i - near[0] + m // 2) % m))
            for step in range(2, 10):
                st = stair_at((edge + sense * step) % m, sense)
                if st:
                    paseo_stairs.append(st)
                    break
    last = -999
    for i in range(0, m, 3):
        if gap[i] or any(min((i - st["i"]) % m, (st["i"] - i) % m) < 28 for st in paseo_stairs):
            continue
        st = stair_at(i, 1)
        if st:
            paseo_stairs.append(st)
    for st in paseo_stairs:
        st.pop("i")
    gy = round(level(*GATE_N), 2)
    gates = [{"id": "puerta_muelle", "pos": [GATE_N[0], gy, GATE_N[1]]},
             {"id": "puerta_puente", "pos": [tr["landmarks_m"]["south_gate"][0], round(level(*tr["landmarks_m"]["south_gate"]), 2), tr["landmarks_m"]["south_gate"][1]]},
             {"id": "puerta_este", "pos": [EAST_GATE[0], round(level(*EAST_GATE), 2), EAST_GATE[1]]}]
    def bridge(bid, gate, far, width):
        """From inside the gate passage (town level, through the wall's thickness) to a landing 3 m into the far bank."""
        g = np.array([gate[0], gate[2]])
        f = np.array(far)
        d = (f - g) / np.linalg.norm(f - g)
        fr = g - d * (WALL_HALF + 0.6)
        to = f + d * 3.0
        return {"id": bid, "from": [round(float(fr[0]), 2), round(level(*fr), 2), round(float(fr[1]), 2)],
                "to": [round(float(to[0]), 2), round(ground(*to) + 0.05, 2), round(float(to[1]), 2)], "width": width}

    bridges = [
        bridge("puente_sur", gates[1]["pos"], BRIDGES[0][2], 4.0),
        bridge("puente_este", gates[2]["pos"], BRIDGES[1][2], 3.6),
    ]
    doc = {
        "schema": "juego-def.city-seed-ivanix/4",
        "provenance": "Ivanix88 'Medieval City Pack Demo' layout (public commercial-use reply by the author; Owner decision 2026-10-02). Own architecture (ENV01).",
        "rules": "Ivanix: urban composition · ENV01: architecture · gameplay: interiors",
        "terrain": {"origin": [round(minx, 3), round(minz, 3)], "cell": CELL, "cols": cols, "rows": rows, "cells": cells,
                    "classes": ["canto", "canto_viejo", "huerta", "suelo", "roca", "prado"]},
        "river_wall": {"points": wall_pts, "thickness": 2.4, "parapet": 1.0, "base_y": 1.2},
        "paseo": {"points": paseo_pts, "half_width": WALL_HALF, "base_y": 1.2, "stairs": paseo_stairs},
        "towers": towers, "gates": gates, "bridges": bridges, "terraces": terraces, "keep": KEEP.tolist(),
        "spurs": spurs, "antepuerto": [list(q) for q in ANTE],
        "stairs_extra": [{"id": "ESCALINATA_MUELLE", "top": [GATE_N[0], gy, GATE_N[1]], "dir": [0.0, 1.0], "width": 6.0, "low": QUAY_Y}],
        "pier": {"y": QUAY_Y, "decks": [list(d) for d in PIER], "post_bottom": -2.0},
        "finca": finca, "buildings": buildings, "stalls": stall_rects, "tapias": TAPIAS,
        "tramos": [{"primary": l["primary"], "pts": [[round(float(q[0]), 2), round(float(q[1]), 2)] for q in l["pts"][::2]]} for l in LINES],
        "streets": [{"id": st["id"], "name": st["name"], "pts": [[round(float(q[0]), 2), round(float(q[1]), 2)] for q in st["pts"][::2]], "hw": round(float(np.median(st["hw"])), 2)} for st in STREETS],
        "spawn": [12.0, level(12.0, 40.0), 40.0],
        "summary": {
            "buildings": len(buildings), "semantic_buildings": len(sem_list) + 2,
            "by_class": {k: sum(1 for s in sem_list if s["class"] == k) for k in ("QUEST", "SECONDARY", "AMBIENT_ACCESSIBLE", "AMBIENT")},
            "accessible_share": round((len(sem_list) - sum(1 for s in sem_list if s["class"] == "AMBIENT") + 2) / (len(sem_list) + 2), 3),
            "terraces": [{"radius": t["radius"], "walls": len(t["walls"]), "stairs": len(t["stairs"])} for t in terraces],
            "finca_edges": [e["role"] for e in finca["edges"]],
            "orientation_coherence": COHERENCE,
            "programme": {g[0]: [q["id"] for q in g[4]] for g in groups},
        },
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps(doc["summary"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

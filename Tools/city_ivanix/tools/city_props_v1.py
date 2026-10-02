"""Props v1 for the Ivanix-layout town: street life of a Cantabrian-Asturian port town around 2000, ENV01 modules only.

Placement is read from the same trace and seed the town was built from: the market goes where the layout has its stalls,
trees where it has green, terraces in front of the bars on the plaza, port gear on the quay and at the far bank,
benches on the El Alto lookouts, lamps on the plaza and the main axis. Heights are resolved in Unity by a ray onto the
ground (except boats, which sit on the water).
"""

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from shapely.prepared import prep

ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / "reconstruction" / "layout_trace_v1.json"
SEED = ROOT / "reconstruction" / "city_seed_v4.json"
OUT = ROOT / "reconstruction" / "city_props_v1.json"


def rnd(key):
    return int(hashlib.md5(key.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


def poly(p):
    shp = Polygon(p["outer"], [h for h in p["holes"] if len(h) >= 3])
    return shp if shp.is_valid else shp.buffer(0)


def main():
    tr = json.loads(TRACE.read_text(encoding="utf-8"))
    sd = json.loads(SEED.read_text(encoding="utf-8"))
    paving = unary_union([poly(p) for p in tr["public_paving"]])
    green = unary_union([poly(p) for p in tr["yards_green"]])
    town = Polygon(tr["outer_wall"]).buffer(0)
    wall = LineString(tr["outer_wall"] + [tr["outer_wall"][0]])
    pv, tw = prep(paving), prep(town)

    rects = {}
    for b in sd["buildings"]:
        sp = b["spec"]
        mx, _, mz = b["frontage_mid"]
        n = np.array(b["facing"])
        xd = np.array([n[1], -n[0]])
        W = b.get("W", 2 * sp["bays"] * sp.get("sx", 1.0))
        D = b.get("D", sp["depth"] * sp.get("sz", 1.0))
        o = np.array([mx, mz]) - xd * W / 2
        rects[b["id"]] = (Polygon([o, o + xd * W, o + xd * W - n * D, o - n * D]), b, n, xd)
    blocked = [r[0] for r in rects.values()]
    for t in sd["terraces"]:
        for seg in t["walls"]:
            if len(seg) >= 2:
                blocked.append(LineString(seg).buffer(1.0))
        for st in t["stairs"]:
            a = np.array([st["top"][0], st["top"][2]])
            blocked.append(LineString([a, a + np.array(st["dir"]) * 8.0]).buffer(2.2))
    for t in sd.get("tapias", []):
        blocked.append(LineString([(q[0], q[2]) for q in t["pts"]]).buffer(0.5))
    fw = sd["finca"]["towers"]
    blocked.append(Polygon(fw).buffer(1.0))
    occ = prep(unary_union(blocked))
    static = unary_union(blocked)
    placed_pts = []
    items = []

    def free(p, r, rs):
        if occ.contains(p) or static.distance(p) < rs:
            return False
        return all(p.distance(q) >= max(r, qr) for q, qr in placed_pts)

    def put(m, x, z, rot, group, clear=0.6, scale=1.0, y=None, force=False, sclear=None):
        p = Point(x, z)
        if not force and not free(p, clear, clear + 0.5 if sclear is None else sclear):
            return False
        it = {"m": m, "p": [round(float(x), 2), round(float(z), 2)], "r": round(float(rot) % 360, 1), "g": group}
        if scale != 1.0:
            it["s"] = round(scale, 2)
        if y is not None:
            it["y"] = y
        items.append(it)
        placed_pts.append((p, max(0.3, clear * 0.8)))
        return True

    def yaw(v):
        return math.degrees(math.atan2(v[0], v[1]))

    # --- weekly market (mercadillo, around 2000): folding tables under big parasols with plastic and wooden crates,
    #     only in the main square where the layout has its stalls; the vendors' van parked at the edge
    stall_pts = []
    for k, sr in enumerate(sd["stalls"]):
        r = Polygon(sr)
        c = np.array(r.centroid.coords[0])
        if np.hypot(*c) > 32:
            continue
        cs = np.array(sr)
        e1, e2 = cs[1] - cs[0], cs[2] - cs[1]
        axis, L = (e1, np.linalg.norm(e1)) if np.linalg.norm(e1) >= np.linalg.norm(e2) else (e2, np.linalg.norm(e2))
        axis = axis / L
        perp = np.array([axis[1], -axis[0]])
        front = perp if np.dot(perp, -c) > 0 else -perp          # vendors face the square's centre
        n = max(1, int(round(L / 3.2)))
        for i in range(n):
            q = c + axis * ((i - (n - 1) / 2) * 3.2)
            if not put("ENV_Prop_Table_Large", q[0], q[1], yaw(axis) - 90, "MERCADO", clear=1.4):
                continue
            stall_pts.append(q)
            put("ENV_Parasol", q[0], q[1], 0, "MERCADO", clear=0.0, force=True, scale=1.25)
            for j, off in enumerate((-0.85, 0.0, 0.85)):
                if rnd(f"g{k}{i}{j}") < 0.8:
                    m = ("ENV_Crate_Fish", "ENV_Prop_FarmCrate_Apple", "ENV_Prop_FarmCrate_Carrot")[int(rnd(f"gm{k}{i}{j}") * 3) % 3]
                    g = q + axis * off + front * 0.15
                    it = {"m": m, "p": [round(float(g[0]), 2), round(float(g[1]), 2)], "r": round((yaw(axis) - 90) % 360, 1), "g": "MERCADO", "dy": 0.81}
                    items.append(it)
            b = q - front * 1.0 + axis * (rnd(f"bx{k}{i}") - 0.5) * 1.6
            put("ENV_Box_Cardboard" if rnd(f"bm{k}{i}") < 0.6 else "ENV_Crate_Fish", b[0], b[1], 360 * rnd(f"br{k}{i}"), "MERCADO", clear=0.0, force=True)
    if stall_pts:
        far = max(stall_pts, key=lambda q: np.hypot(*q))
        out = far / np.linalg.norm(far)
        v = far + out * 4.5
        put("ENV_Vehicle_Van", v[0], v[1], yaw(np.array([-out[1], out[0]])), "MERCADO", clear=1.5)

    # --- paseo maritimo on the wall: lamps on the town edge, benches facing the sea, bins; terraces on two cubos
    pz = sd.get("paseo")
    if pz:
        ptsP = pz["points"]
        half = pz["half_width"]
        mP = len(ptsP)
        area = sum(ptsP[i][0] * ptsP[(i + 1) % mP][2] - ptsP[(i + 1) % mP][0] * ptsP[i][2] for i in range(mP))
        left_town = 1.0 if area > 0 else -1.0
        acc = 0.0
        for i in range(mP):
            a, b = ptsP[i], ptsP[(i + 1) % mP]
            if a[4] or b[4]:
                continue
            t = np.array([b[0] - a[0], b[2] - a[2]])
            L = float(np.linalg.norm(t))
            if L < 0.1:
                continue
            t /= L
            inn = np.array([-t[1], t[0]]) * left_town
            acc += L
            c = np.array([a[0], a[2]])
            k = int(acc // 2)
            if k % 12 == 0:
                q = c + inn * (half - 0.45)
                put("ENV_Lamp_Post", q[0], q[1], yaw(-inn), "PASEO", clear=0.0, force=True)
            elif k % 18 == 6:
                q = c + inn * (half - 0.75)
                put("ENV_Bench_Street", q[0], q[1], yaw(-inn), "PASEO", clear=0.0, force=True)
            elif k % 30 == 15:
                q = c + inn * (half - 0.4)
                put("ENV_Bin_Street", q[0], q[1], 0, "PASEO", clear=0.0, force=True)
        cubos = sorted(sd["towers"], key=lambda t: np.hypot(t["pos"][0], t["pos"][1]))
        for j, t in enumerate(cubos):
            c = np.array(t["pos"], float)
            out = c / max(1e-6, np.linalg.norm(c))
            if j < 2:
                # terraza del paseo: the bar on the nearest street sets three tables on the lookout
                for kk, off in enumerate((-1.6, 0.0, 1.6)):
                    q = c + np.array([-out[1], out[0]]) * off + out * 0.6
                    put("ENV_Cafe_Table", q[0], q[1], 0, "PASEO", clear=0.0, force=True)
                    put("ENV_Parasol", q[0], q[1], 0, "PASEO", clear=0.0, force=True)
                    put("ENV_Cafe_Chair", *(q + out * 0.7), yaw(-out), "PASEO", clear=0.0, force=True)
            elif j % 2 == 0:
                q = c + out * 1.6
                put("ENV_Bench_Street", q[0], q[1], yaw(-out), "PASEO", clear=0.0, force=True)

    # --- plaza: fountain, kiosk, phone box, lamps, trees with bench rings
    plaza = np.array([0.0, 0.0])
    for rr in range(0, 14):
        cand = [plaza + np.array([math.cos(a), math.sin(a)]) * rr for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)] if rr else [plaza]
        if any(put("ENV_Fountain_Monument", q[0], q[1], 0, "PLAZA", clear=8.2) for q in cand):
            break
    for name, ang in (("ENV_Kiosk_Plaza", 140), ("ENV_Phone_Booth", 300), ("ENV_Recycling_Bins", 230)):
        for rr in (22, 24, 26, 20, 28):
            q = plaza + np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))]) * rr
            if pv.contains(Point(*q)) and put(name, q[0], q[1], yaw(plaza - q), "PLAZA", clear=1.2):
                break
    for a in np.linspace(0, 2 * math.pi, 10, endpoint=False):
        for rr in (26, 29, 23, 32):
            q = plaza + np.array([math.cos(a), math.sin(a)]) * rr
            if pv.contains(Point(*q)) and put("ENV_Lamp_Post", q[0], q[1], yaw(plaza - q), "PLAZA", clear=1.0):
                break
    greens = list(green.geoms) if hasattr(green, "geoms") else [green]
    for gi, g in enumerate(greens):
        c = g.representative_point()
        inside = tw.contains(c)
        if not inside or g.area < 4:
            continue
        near_plaza = c.distance(Point(0, 0)) < 40
        if g.area <= 70:
            m = ("ENV_Tree_Plaza", "ENV_Tree_Plaza_B", "ENV_Tree_Plaza_C")[gi % 3] if near_plaza else ("ENV_Tree_Common_A", "ENV_Tree_Common_B", "ENV_Tree_Common_C")[gi % 3]
            if put(m, c.x, c.y, 360 * rnd(f"t{gi}"), "ARBOLADO", clear=1.5) and near_plaza and rnd(f"br{gi}") < 0.4:
                put("ENV_Tree_Bench_Ring", c.x, c.y, 0, "ARBOLADO", clear=0.0, force=True)
        else:
            # huerta: a couple of fruit trees and shrubs inside the garden
            for j in range(min(4, int(g.area // 40))):
                q = g.representative_point() if j == 0 else Point(*(np.array(g.centroid.coords[0]) + (np.array([rnd(f"hx{gi}{j}"), rnd(f"hz{gi}{j}")]) - 0.5) * math.sqrt(g.area)))
                if g.contains(q):
                    put(("ENV_Hill_Tree", "ENV_Shrub_Garden", "ENV_Plant_Bush", "ENV_Hill_Tree_B")[j % 4], q.x, q.y, 360 * rnd(f"hr{gi}{j}"), "HUERTAS", clear=1.2)

    # --- frontages: bar terraces on the plaza and the main axis; doorstep life elsewhere
    for bid, (r, b, n, xd) in rects.items():
        sp = b["spec"]
        mx, _, mz = b["frontage_mid"]
        mid = np.array([mx, mz])
        w = b.get("W", 2 * sp["bays"])
        on_plaza = Point(*mid).distance(Point(0, 0)) < 45
        is_bar = b["semantic_id"] in ("P_BAR",) or (sp["type"] == "mixed_commercial" and (on_plaza or abs(mx) < 10) and rnd("bar" + bid) < 0.35)
        if is_bar:
            for j in (-1, 1):
                t = mid + xd * (j * w / 4) + n * 3.0
                if pv.contains(Point(*t)) and put("ENV_Cafe_Table", t[0], t[1], yaw(n), "TERRAZAS", clear=1.0):
                    put("ENV_Cafe_Chair", *(t + xd * 0.75), yaw(-xd), "TERRAZAS", clear=0.0, force=True)
                    put("ENV_Cafe_Chair", *(t - xd * 0.75), yaw(xd), "TERRAZAS", clear=0.0, force=True)
                    if rnd("par" + bid + str(j)) < 0.5:
                        put("ENV_Parasol", t[0], t[1], 0, "TERRAZAS", clear=0.0, force=True)
            continue
        roll = rnd("door" + bid)
        if roll < 0.45:
            side = 1 if rnd("side" + bid) > 0.5 else -1
            t = mid + xd * (side * (w / 2 - 0.45)) + n * 0.45
            kind = b["kind"]
            if kind == "ribera":
                m = ("ENV_Net_Pile", "ENV_Prop_Rope_Coil", "ENV_Crate_Fish", "ENV_Prop_Bucket")[int(roll * 40) % 4]
            elif sp["type"] == "mixed_commercial":
                m = ("ENV_Prop_Barrel", "ENV_Prop_Crate_Wooden", "ENV_AFrame_Board", "ENV_Planter_Box")[int(roll * 40) % 4]
            else:
                m = ("ENV_Plant_Geranium", "ENV_Planter_Pot", "ENV_Plant_Hydrangea", "ENV_Prop_Bench", "ENV_Pot_Tin", "ENV_Prop_Bucket_Wood")[int(roll * 60) % 6]
            put(m, t[0], t[1], yaw(n) + (90 if m == "ENV_Prop_Bench" else 0), "PORTALES", clear=0.25, sclear=0.3)

    # --- main axis lamps (north gate to south gate), on the street edge
    for z in np.arange(-118, 52, 22):
        for side in (-1, 1):
            for dx in (3.5, 4.5, 2.8, 5.5):
                x = side * dx
                if pv.contains(Point(x, z)) and put("ENV_Lamp_Post", x, z, 90 * -side, "FAROLAS", clear=1.0):
                    break

    # --- El Alto: benches on the lookouts (plinth edge facing out) and under the outer wall
    kx, kz = sd["terraces"][0]["center"]
    for a in np.linspace(0, 2 * math.pi, 16, endpoint=False):
        q = np.array([kx, kz]) + np.array([math.cos(a), math.sin(a)]) * 16.6
        put("ENV_Bench_Stone", q[0], q[1], yaw(np.array([math.cos(a), math.sin(a)])) + 180, "MIRADORES", clear=0.9, sclear=0.3)

    # --- port: the antepuerto quay and its U-shaped timber pier (boats between the fingers and off the mouth),
    #     bollards on the deck edges, fishing gear on the quay; work yard on the far bank
    pier = sd.get("pier")
    if pier:
        main = pier["decks"][0]
        for x in np.arange(main[0] + 0.6, main[2], 3.2):
            put("ENV_Bollard_Mooring", x, main[1] + 0.4, 0, "PUERTO", clear=0.0, force=True)
        for d in pier["decks"][1:]:
            for z in np.arange(d[1] + 1.2, d[3], 3.0):
                put("ENV_Bollard_Mooring", (d[0] + d[2]) / 2, z, 0, "PUERTO", clear=0.0, force=True)
        lx, rx = pier["decks"][1][2], pier["decks"][2][0]
        for k, (x, z, rot) in enumerate(((lx + 2.4, 95.0, 0), (rx - 2.4, 94.0, 180), (main[0] - 4.0, 100.0, 90), (main[2] + 4.5, 101.0, 270), (main[2] + 9.0, 104.0, 250))):
            put("ENV_Boat_Small", x, z, rot, "PUERTO", clear=0.0, y=0.0, force=True)
        put("ENV_Quay_Ladder", (main[0] + main[2]) / 2, main[3] - 0.2, 0, "PUERTO", clear=0.0, force=True)
    ante = Polygon(sd["antepuerto"]) if sd.get("antepuerto") else None
    if ante is not None:
        gear = ("ENV_Net_Pile", "ENV_Crate_Fish", "ENV_Crate_Fish", "ENV_Prop_Rope_Coil", "ENV_Lifebuoy_Post", "ENV_Pallet",
                "ENV_Prop_Chain_Coil", "ENV_Net_Pile", "ENV_Prop_Barrel", "ENV_Crate_Fish", "ENV_Prop_Bucket", "ENV_Bench_Street")
        minx, minz, maxx, maxz = ante.bounds
        j = 0
        for t in range(220):
            if j >= len(gear) * 2:
                break
            x = minx + rnd(f"agx{t}") * (maxx - minx)
            z = 66 + rnd(f"agz{t}") * 16
            if ante.buffer(-2.0).contains(Point(x, z)) and put(gear[j % len(gear)], x, z, 360 * rnd(f"agr{t}"), "PUERTO", clear=1.2):
                j += 1
    alm = [rects[k] for k in rects if rects[k][1]["semantic_id"] == "P_ALMACEN"]
    for i, (r, b, n, xd) in enumerate(alm):
        mx, _, mz = b["frontage_mid"]
        for j, m in enumerate(("ENV_Pallet", "ENV_Prop_Crate_Wooden", "ENV_Prop_Crate_Metal", "ENV_Prop_Barrel", "ENV_Box_Cardboard")):
            t = np.array([mx, mz]) + n * (2.0 + 1.5 * rnd(f"ay{i}{j}")) + xd * (rnd(f"ax{i}{j}") - 0.5) * 6
            put(m, t[0], t[1], 360 * rnd(f"ar{i}{j}"), "ALMACEN", clear=0.3)
        if i == 0:
            t = np.array([mx, mz]) + n * 6.0
            put("ENV_Vehicle_Van", t[0], t[1], yaw(xd), "VEHICULOS", clear=2.0)

    # --- a few period cars where a road reaches the town (east gate bank, north port suburb)
    for j, (x, z, rot) in enumerate(((117.0, -66.5, 140), (124.0, -73.5, 140), (14.0, 66.0, 90))):   # parked on the bank road, never on a bridge
        put("ENV_Vehicle_Car", x, z, rot, "VEHICULOS", clear=1.5)

    groups = {}
    for it in items:
        groups[it["g"]] = groups.get(it["g"], 0) + 1
    doc = {"schema": "juego-def.city-props/1", "seed": SEED.name, "items": items, "summary": {"items": len(items), "groups": groups}}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps(doc["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()

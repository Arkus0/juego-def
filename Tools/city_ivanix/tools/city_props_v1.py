"""Props v1 for the Ivanix-layout town: street life of a Cantabrian-Asturian port town around 2000. The town's own
entities (CITY_*: market stalls, terrace sets, cars and vans, fishing boats, trees, hortensias, butane, letter box,
gumball) and ENV01 modules for the rest.

Placement is read from the same trace and seed the town was built from: the market goes where the layout has its stalls,
trees where it has green, terraces in front of the bars on the plaza, port gear on the quay and at the far bank,
benches on the El Alto lookouts, lamps on the plaza and the main axis. Heights are resolved in Unity by a ray onto the
ground (except boats, which sit on the water). In Unity every object is then an entity (CityEntities): seated on its
own footprint, pushed out of whatever it touches or not placed; "fix" marks the few that must stay exactly where they
are (boats on the water, bollards on the deck edge, a bench ring round its tree), "tilt" the vehicles that follow the
slope under their wheels.
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


DOORSTEP_DEPTH = {"ENV_Net_Pile": 1.33, "ENV_Prop_Rope_Coil": 0.8, "ENV_Crate_Fish": 0.4, "ENV_Prop_Bucket": 0.35, "ENV_Prop_Barrel": 0.65,
                  "ENV_Prop_Crate_Wooden": 0.91, "ENV_AFrame_Board": 0.6, "ENV_Planter_Box": 0.45, "ENV_Plant_Geranium": 0.45,
                  "ENV_Planter_Pot": 0.52, "ENV_Plant_Hydrangea": 0.98, "ENV_Bench_Stone": 0.48, "ENV_Pot_Tin": 0.35, "ENV_Prop_Bucket_Wood": 0.4,
                  "CITY_Hortensia_Azul": 1.05, "CITY_Hortensia_Rosa": 1.05, "CITY_Butane": 0.34}
CAR_COLOURS = ("Rojo", "Blanco", "Azul", "Verde", "Plata", "Beige")
BOAT_BANDS = ("Azul", "Rojo", "Verde")


def rnd(key):
    return int(hashlib.md5(key.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


def car(key, van=False):
    return ("CITY_Van_" if van else "CITY_Car_Hatch_") + CAR_COLOURS[int(rnd("col" + key) * len(CAR_COLOURS)) % len(CAR_COLOURS)]


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

    def put(m, x, z, rot, group, clear=0.6, scale=1.0, y=None, force=False, sclear=None, **flags):
        p = Point(x, z)
        if not force and not free(p, clear, clear + 0.5 if sclear is None else sclear):
            return False
        it = {"m": m, "p": [round(float(x), 2), round(float(z), 2)], "r": round(float(rot) % 360, 1), "g": group}
        if scale != 1.0:
            it["s"] = round(scale, 2)
        if y is not None:
            it["y"] = y
        it.update({k: v for k, v in flags.items() if v})
        items.append(it)
        placed_pts.append((p, max(0.3, clear * 0.8)))
        return True

    def yaw(v):
        return math.degrees(math.atan2(v[0], v[1]))

    # --- the plaza's fountain first: the square is built round it, the market sets up round it
    for rr in range(0, 14):
        cand = [np.array([math.cos(a), math.sin(a)]) * rr for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)] if rr else [np.zeros(2)]
        if any(put("ENV_Fountain_Monument", q[0], q[1], 0, "PLAZA", clear=8.2) for q in cand):
            break

    # --- weekly market (mercadillo, around 2000): each stall one entity (table, skirt, canvas roof and produce built
    #     together), only in the main square where the layout has its stalls; stock behind, the vendors' van at the edge
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
            r_ = rnd(f"kind{k}{i}")
            kind = "Fruta" if r_ < 0.5 else "Ropa" if r_ < 0.78 else "Quesos"      # fruit and veg most, clothes, the valley's products
            if not put("CITY_Market_Stall_" + kind, q[0], q[1], yaw(front), "MERCADO", clear=1.4):
                continue
            stall_pts.append(q)
            b = q - front * 1.25 + axis * (rnd(f"bx{k}{i}") - 0.5) * 1.2
            put("ENV_Box_Cardboard" if rnd(f"bm{k}{i}") < 0.6 else "ENV_Crate_Fish", b[0], b[1], 360 * rnd(f"br{k}{i}"), "MERCADO", clear=0.0, force=True)
    if stall_pts:
        far = max(stall_pts, key=lambda q: np.hypot(*q))
        out = far / np.linalg.norm(far)
        v = far + out * 4.5
        put(car("mercado", van=True), v[0], v[1], yaw(np.array([-out[1], out[0]])), "MERCADO", clear=1.5, tilt=1)

    # --- paseo maritimo on the wall: lamps on the town edge, benches facing the sea, bins; terraces on two cubos
    pz = sd.get("paseo")
    landings = [np.array([st["landing"][0], st["landing"][2]]) for st in (pz or {}).get("stairs", [])]
    landings += [np.array([st["top"][0], st["top"][2]]) for t_ in sd["terraces"] for st in t_["stairs"]]

    def near_landing(q):
        return any(np.hypot(*(q - l_)) < 3.2 for l_ in landings)

    if pz:
        ptsP = pz["points"]
        half = pz["half_width"]
        mP = len(ptsP)
        area = sum(ptsP[i][0] * ptsP[(i + 1) % mP][2] - ptsP[(i + 1) % mP][0] * ptsP[i][2] for i in range(mP))
        left_town = 1.0 if area > 0 else -1.0
        acc = 0.0
        for i in range(mP):
            a, b = ptsP[i], ptsP[(i + 1) % mP]
            if a[4] or b[4] or (len(a) > 5 and (a[5] or b[5])):
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
                near_landing(q) or put("ENV_Lamp_Post", q[0], q[1], yaw(-inn), "PASEO", clear=0.0, force=True)
            elif k % 18 == 6:
                q = c + inn * (half - 0.75)
                near_landing(q) or put("ENV_Bench_Street", q[0], q[1], yaw(-inn), "PASEO", clear=0.0, force=True)
            elif k % 30 == 15:
                q = c + inn * (half - 0.4)
                near_landing(q) or put("ENV_Bin_Street", q[0], q[1], 0, "PASEO", clear=0.0, force=True)
        cubos = sorted(sd["towers"], key=lambda t: np.hypot(t["pos"][0], t["pos"][1]))
        for j, t in enumerate(cubos):
            c = np.array(t["pos"], float)
            out = c / max(1e-6, np.linalg.norm(c))
            if j < 2:
                # terraza del paseo: the bar on the nearest street sets its terrace sets on the lookout
                for kk, off in enumerate((-1.3, 1.3)):
                    q = c + np.array([-out[1], out[0]]) * off + out * 0.4
                    put("CITY_Terrace_Set", q[0], q[1], yaw(-out) + 20 * kk, "PASEO", clear=0.0, force=True, shift=1.2)
            elif j % 2 == 0:
                q = c + out * 1.6
                put("ENV_Bench_Street", q[0], q[1], yaw(-out), "PASEO", clear=0.0, force=True)

    # --- plaza: fountain, kiosk, phone box, lamps, trees with bench rings
    plaza = np.array([0.0, 0.0])
    for name, ang in (("ENV_Kiosk_Plaza", 140), ("ENV_Phone_Booth", 300), ("CITY_Buzon_Correos", 312), ("ENV_Recycling_Bins", 230)):
        for rr in (22, 24, 26, 20, 28):
            q = plaza + np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))]) * rr
            if pv.contains(Point(*q)) and put(name, q[0], q[1], yaw(plaza - q), "PLAZA", clear=1.2, sclear=4.2 if name == "ENV_Kiosk_Plaza" else 1.2):
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
            m = "CITY_Tree_Platano" if near_plaza else ("CITY_Tree_Magnolio", "CITY_Tree_Platano", "CITY_Tree_Magnolio")[gi % 3]
            if put(m, c.x, c.y, 360 * rnd(f"t{gi}"), "ARBOLADO", clear=1.5, sclear=3.0, shift=2.5) and near_plaza and rnd(f"br{gi}") < 0.4:
                put("ENV_Tree_Bench_Ring", c.x, c.y, 0, "ARBOLADO", clear=0.0, force=True, fix=1)
        else:
            # huerta: a couple of fruit trees and shrubs inside the garden
            for j in range(min(4, int(g.area // 40))):
                q = g.representative_point() if j == 0 else Point(*(np.array(g.centroid.coords[0]) + (np.array([rnd(f"hx{gi}{j}"), rnd(f"hz{gi}{j}")]) - 0.5) * math.sqrt(g.area)))
                if g.contains(q):
                    put(("CITY_Tree_Manzano", "CITY_Hortensia_Azul", "CITY_Hortensia_Rosa", "CITY_Tree_Manzano")[j % 4], q.x, q.y, 360 * rnd(f"hr{gi}{j}"), "HUERTAS", clear=1.2, sclear=3.0 if j % 4 in (0, 3) else 1.2)

    # --- frontages: bar terraces on the plaza and the main axis; doorstep life elsewhere
    for bid, (r, b, n, xd) in rects.items():
        sp = b["spec"]
        if b.get("business"):
            continue                       # shopfronts (CityShopfronts) dress their own fronts
        mx, _, mz = b["frontage_mid"]
        mid = np.array([mx, mz])
        w = b.get("W", 2 * sp["bays"])
        on_plaza = Point(*mid).distance(Point(0, 0)) < 45
        is_bar = b["semantic_id"] in ("P_BAR",) or (sp["type"] == "mixed_commercial" and (on_plaza or abs(mx) < 10) and rnd("bar" + bid) < 0.35)
        if is_bar:
            for j in (-1, 1):
                t = mid + xd * (j * w / 4) + n * 2.6
                if pv.contains(Point(*t)):
                    put("CITY_Terrace_Set", t[0], t[1], yaw(n) + 15 * j, "TERRAZAS", clear=1.3)
            continue
        roll = rnd("door" + bid)
        if roll < 0.45:
            side = 1 if rnd("side" + bid) > 0.5 else -1
            kind = b["kind"]
            if kind == "ribera":
                m = ("ENV_Net_Pile", "ENV_Prop_Rope_Coil", "ENV_Crate_Fish", "ENV_Prop_Bucket")[int(roll * 40) % 4]
            elif sp["type"] == "mixed_commercial":
                m = ("ENV_Prop_Barrel", "ENV_Prop_Crate_Wooden", "ENV_AFrame_Board", "ENV_Planter_Box")[int(roll * 40) % 4]
            else:
                # the stone poyo by the door, hortensias, pots: a lived doorstep in the north
                m = ("ENV_Plant_Geranium", "ENV_Planter_Pot", ("CITY_Hortensia_Azul", "CITY_Hortensia_Rosa")[int(roll * 997) % 2], "ENV_Bench_Stone",
                     "CITY_Butane", "ENV_Prop_Bucket_Wood")[int(roll * 60) % 6]
            depth = DOORSTEP_DEPTH.get(m, 0.6)
            along = 0.6 + (0.9 if m == "ENV_Bench_Stone" else 0.0)
            t = mid + xd * (side * (w / 2 - along)) + n * (1.0 + depth / 2)   # the facade face and its rejas stand up to 0.85 m proud of the plot line
            put(m, t[0], t[1], yaw(n), "PORTALES", clear=0.3, sclear=0.25 + depth / 2, scale=0.7 if m.startswith("CITY_Hortensia") else 1.0)

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
            put("ENV_Bollard_Mooring", x, main[1] + 0.4, 0, "PUERTO", clear=0.0, force=True, fix=1)
        for d in pier["decks"][1:]:
            for z in np.arange(d[1] + 1.2, d[3], 3.0):
                put("ENV_Bollard_Mooring", (d[0] + d[2]) / 2, z, 0, "PUERTO", clear=0.0, force=True, fix=1)
        lx, rx = pier["decks"][1][2], pier["decks"][2][0]
        for k, (x, z, rot) in enumerate(((lx + 2.4, 95.0, 0), (rx - 2.4, 94.0, 180), (main[0] - 4.0, 100.0, 90), (main[2] + 4.5, 101.0, 270), (main[2] + 9.0, 104.0, 250))):
            put("CITY_Boat_Lancha_" + BOAT_BANDS[k % 3], x, z, rot, "PUERTO", clear=0.0, y=0.0, force=True, fix=1)
        put("ENV_Quay_Ladder", (main[0] + main[2]) / 2, main[3] - 0.2, 0, "PUERTO", clear=0.0, force=True, fix=1)
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
            put(car("almacen", van=True), t[0], t[1], yaw(xd), "VEHICULOS", clear=2.0, tilt=1)

    # --- a few period cars where a road reaches the town (east gate bank, north port suburb)
    for j, (x, z, rot) in enumerate(((117.0, -66.5, 140), (124.0, -73.5, 140), (14.0, 66.0, 90))):   # parked on the bank road, never on a bridge
        put(car(f"orilla{j}"), x, z, rot, "VEHICULOS", clear=1.5, tilt=1)

    # --- the finca of the indiano: two palms in the garden ring between the wall and the casona, the sign of a
    #     fortune made in America; as far from the house as the garden allows, apart from each other
    fp = Polygon(fw)
    casona = [r for r, b_, n_, x_ in rects.values() if b_["semantic_id"] == "P_FINCA"]
    if fp.is_valid and fp.area > 50:
        garden = fp.buffer(-2.2)
        for r in casona:
            garden = garden.difference(r.buffer(3.2))
        gx0, gz0, gx1, gz1 = fp.bounds
        cand = [Point(x, z) for x in np.arange(gx0, gx1, 0.5) for z in np.arange(gz0, gz1, 0.5) if garden.contains(Point(x, z))]
        house = unary_union(casona) if casona else Point(*np.array(fp.centroid.coords[0]))
        cand.sort(key=lambda q: -house.distance(q))
        palms = []
        for q in cand:
            if all(q.distance(o) >= 6.0 for o in palms):
                palms.append(q)
            if len(palms) == 2:
                break
        for k, q in enumerate(palms):
            put("CITY_Tree_Palmera", q.x, q.y, 360 * rnd(f"palm{k}"), "FINCA", clear=0.0, force=True, shift=1.5)

    # --- wide streets: the municipal containers every ~80 m, a few parked cars and a delivery van, the letter box
    streets = {st["id"]: st for st in sd["streets"]}
    for sid, every, cars in (("ANILLO_BAJO", 80.0, 3), ("MUELLE", 60.0, 2), ("PASEO_NORTE", 70.0, 1), ("MAYOR", 90.0, 1)):
        st = streets.get(sid)
        if not st:
            continue
        line = LineString(st["pts"])
        hw = st["hw"]
        acc, ncar = 20.0, 0
        while acc < line.length - 10:
            p0, p1 = np.array(line.interpolate(acc).coords[0]), np.array(line.interpolate(acc + 1.0).coords[0])
            tg = (p1 - p0) / max(1e-6, np.linalg.norm(p1 - p0))
            side = 1 if rnd(f"cs{sid}{acc}") < 0.5 else -1
            nrm = np.array([-tg[1], tg[0]]) * side
            q = p0 + nrm * (hw - 1.0)
            put("ENV_Recycling_Bins", q[0], q[1], yaw(tg), "CONTENEDORES", clear=2.2, sclear=0.6)
            if ncar < cars and hw >= 4.0:
                qc = p0 + tg * 12.0 - nrm * (hw - 1.3)
                m = car(f"{sid}{acc}", van=(sid == "MAYOR"))          # Calle Mayor: carga y descarga only
                if put(m, qc[0], qc[1], yaw(tg) + (180 if rnd(f"cd{sid}{acc}") < 0.5 else 0), "VEHICULOS", clear=2.6, sclear=0.8, tilt=1):
                    ncar += 1
            acc += every
    mayor = streets.get("MAYOR")
    if mayor:
        line = LineString(mayor["pts"])
        for d in (40.0, 25.0, 55.0):
            p0, p1 = np.array(line.interpolate(d).coords[0]), np.array(line.interpolate(d + 1.0).coords[0])
            tg = (p1 - p0) / max(1e-6, np.linalg.norm(p1 - p0))
            q = p0 + np.array([-tg[1], tg[0]]) * (mayor["hw"] - 0.9)
            if put("CITY_Buzon_Correos", q[0], q[1], yaw(-np.array([-tg[1], tg[0]])), "FAROLAS", clear=0.8, sclear=0.4):
                break

    groups = {}
    for it in items:
        groups[it["g"]] = groups.get(it["g"], 0) + 1
    doc = {"schema": "juego-def.city-props/1", "seed": SEED.name, "items": items, "summary": {"items": len(items), "groups": groups}}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps(doc["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()

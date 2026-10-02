"""The town's paving as a worker would lay it, at 12.5 cm: a class map the DC Ground shader reads
(Unity/JuegoDef/Assets/JuegoDef/City/Ground/CITY_PavingMap.png).

Owner review 2026-10-02: "los cortes son lineas rectas. Hay que buscar tambien circulos y transiciones entre cortes. Un
obrero no lo haria perfecto como esta ahora." The seed's 1 m ground grid gives each street its own paving by
proximity, so where two streets meet the change of paving runs along a straight bisector. Here the rules of the trade:

  - the main streets' granite flags (losa) run straight through every junction; a side street's paving stops against
    the main street's kerb line, not on a diagonal;
  - at each mouth where a side street meets a main street, a fan (abanico) of setts makes the transition;
  - the Plaza Mayor: setts with a granite ring round the fountain and granite bands from the ring to each street
    that enters the square;
  - every tree in the paving has its round pit (alcorque) of earth with a granite rim;
  - everything else keeps the seed's ground by meaning.

The shader then reads the map with a warped lookup (lines laid by hand, not by rule) and lays a granite band (cinta)
wherever two pavings meet. Classes: the seed's 0-10, 11 abanico, 12 granito (bands, rings, rims).

Run after city_seed_v4.py and city_props_v1.py.
"""

import json
from pathlib import Path

import numpy as np
import shapely
from PIL import Image
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "reconstruction" / "city_seed_v4.json"
PLAN = ROOT / "reconstruction" / "street_plan_v1.json"
PROPS = ROOT / "reconstruction" / "city_props_v1.json"
TRACE = ROOT / "reconstruction" / "layout_trace_v1.json"
OUT_DIR = ROOT.parents[1] / "Unity" / "JuegoDef" / "Assets" / "JuegoDef" / "City" / "Ground"
RES = 0.125
CANTO, CANTO_VIEJO, HUERTA, SUELO, ROCA, PRADO, LOSA, ADOQUIN, MUELLE, PATIO, CAMINO, ABANICO, GRANITO = range(13)
MAIN = {"MAYOR", "MUELLE"}
PAVED = {CANTO, CANTO_VIEJO, LOSA, ADOQUIN, CAMINO, ABANICO}


def main():
    sd = json.loads(SEED.read_text(encoding="utf-8"))
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    props = json.loads(PROPS.read_text(encoding="utf-8"))
    tr = json.loads(TRACE.read_text(encoding="utf-8"))
    t = sd["terrain"]
    ox, oz, cell, cols, rows = t["origin"][0], t["origin"][1], t["cell"], t["cols"], t["rows"]
    base = np.full((rows, cols), 255, np.uint8)
    for i, j, _, c in t["cells"]:
        base[j, i] = c
    k = int(round(cell / RES))
    W, H = cols * k, rows * k
    cls = np.repeat(np.repeat(base, k, axis=0), k, axis=1)          # [z, x] at 12.5 cm
    xs = ox + (np.arange(W) + 0.5) * RES
    zs = oz + (np.arange(H) + 0.5) * RES
    town = Polygon(tr["outer_wall"]).buffer(0)
    counts = {}
    # the seed's 1 m steps rounded off: each class's mask blurred (sigma 0.5 m), every texel takes the strongest
    from scipy.ndimage import gaussian_filter
    best = np.full(cls.shape, -1.0, np.float32)
    out = cls.copy()
    for c in np.unique(cls):
        v = gaussian_filter((cls == c).astype(np.float32), sigma=0.5 / RES, mode="nearest")
        take = v > best
        out[take] = c
        best[take] = v[take]
    cls = out
    del best, out

    def paint(geom, value, only=None, name=""):
        """Sets the class inside a geometry (only over the given classes); works on the geometry's bounding window."""
        if geom.is_empty:
            return
        x0, z0, x1, z1 = geom.bounds
        i0, i1 = max(0, int((x0 - ox) / RES) - 1), min(W, int((x1 - ox) / RES) + 2)
        j0, j1 = max(0, int((z0 - oz) / RES) - 1), min(H, int((z1 - oz) / RES) + 2)
        if i0 >= i1 or j0 >= j1:
            return
        gx, gz = np.meshgrid(xs[i0:i1], zs[j0:j1])
        inside = shapely.contains_xy(geom, gx, gz)
        win = cls[j0:j1, i0:i1]
        if only is not None:
            inside &= np.isin(win, list(only))
        win[inside] = value
        counts[name] = counts.get(name, 0) + int(inside.sum())

    streets = {st["id"]: st for st in sd["streets"]}
    # 1) the main streets' flags run through the junctions; side streets stop at the kerb line
    main_area = unary_union([LineString(streets[s]["pts"]).buffer(streets[s]["hw"] + 1.0, cap_style=2) for s in MAIN if s in streets]).intersection(town)
    paint(main_area, LOSA, only={CANTO, CANTO_VIEJO}, name="losa_through")

    # 2) a fan of setts at each mouth where a side street meets a main street
    fans = []
    main_lines = [LineString(streets[s]["pts"]) for s in MAIN if s in streets]
    kerb = main_area.boundary
    for sid, st in streets.items():
        if sid in MAIN or st["hw"] < 1.4:
            continue
        line = LineString(st["pts"])
        hit = line.intersection(kerb)
        pts = [hit] if hit.geom_type == "Point" else list(getattr(hit, "geoms", []))
        for p in pts:
            if p.geom_type != "Point" or not town.contains(p):
                continue
            r = st["hw"] + 0.7
            fan = p.buffer(r, quad_segs=24).difference(main_area)
            fans.append(fan)
    if fans:
        paint(unary_union(fans), ABANICO, only={CANTO, CANTO_VIEJO, CAMINO}, name="abanico")

    # 3) the Plaza Mayor: a granite ring round the fountain, granite bands from the ring to each street entering it
    plaza = unary_union([Polygon(p["poly"]).buffer(0.6) for p in plan["plazas"]])
    fountain = next((np.array(it["p"]) for it in props["items"] if it["m"] == "ENV_Fountain_Monument"), None)
    if fountain is None:
        fountain = np.array(plaza.centroid.coords[0])
    fc = Point(*fountain)
    ring = fc.buffer(6.4, quad_segs=48).difference(fc.buffer(5.7, quad_segs=48))
    inner = fc.buffer(4.6, quad_segs=48).difference(fc.buffer(4.15, quad_segs=48))
    bands = [ring, inner]
    for sid, st in streets.items():
        line = LineString(st["pts"])
        if line.distance(plaza) > 1.0:
            continue
        entry = line.intersection(plaza.boundary)
        epts = [entry] if entry.geom_type == "Point" else list(getattr(entry, "geoms", []))
        for e in epts:
            if e.geom_type != "Point":
                continue
            d = np.array(e.coords[0]) - fountain
            L = np.linalg.norm(d)
            if L < 7.0:
                continue
            u = d / L
            bands.append(LineString([fountain + u * 6.3, fountain + u * (L + 0.5)]).buffer(0.32, cap_style=2))
    paint(unary_union(bands).intersection(plaza), GRANITO, only={ADOQUIN, LOSA, CANTO, CANTO_VIEJO}, name="plaza_granito")

    # 4) every tree in the paving has its round pit of earth with a granite rim
    for it in props["items"]:
        if not (it["m"].startswith("CITY_Tree") or it["m"].startswith("ENV_Tree")):
            continue
        p = Point(*it["p"])
        i, j = int((p.x - ox) / cell), int((p.y - oz) / cell)
        if not (0 <= i < cols and 0 <= j < rows) or base[j, i] not in PAVED:
            continue
        paint(p.buffer(1.05, quad_segs=24), GRANITO, only=PAVED | {GRANITO}, name="alcorque_rim")
        paint(p.buffer(0.8, quad_segs=24), PATIO, only={GRANITO}, name="alcorque")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # image rows run north (top) to south: flip so texel (0,0) of the texture is the map's (ox, oz) corner in Unity
    Image.fromarray(np.flipud(cls), "L").save(OUT_DIR / "CITY_PavingMap.png", optimize=True)
    meta = {"schema": "juego-def.city-paving/1", "origin": [ox, oz], "texel": RES, "size": [W, H],
            "classes": ["canto", "canto_viejo", "huerta", "suelo", "roca", "prado", "losa", "adoquin", "muelle", "patio", "camino", "abanico", "granito"],
            "painted": counts, "fans": len(fans)}
    (ROOT / "reconstruction" / "paving_map_v1.json").write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"size": [W, H], "painted": counts, "fans": len(fans)}))


if __name__ == "__main__":
    main()

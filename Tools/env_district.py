"""District skeleton from a real reference (ENV composition input, WP-PROD-ENV-01 CASCO district).

Extends env_morphology.py from single streets to a whole district: the street network as a graph (nodes = junctions,
edges = street stretches), the urban blocks (manzanas) between streets with their facade lines and real plot
subdivision, junction types, plazas and the terrain (IGN MDT05). `measure` writes the reference metrics; `plan`
draws them. The skeleton builder (`skeleton`, next step) simplifies them for play under the owner rules
(Docs/production/ENV_COMPOSITION_RULES.md): widths snapped per hierarchy, grade classes 70 % comfortable / 20 %
perceptible / 10 % strong or stairs, a small channelled river on the edge.

    python Tools/env_district.py dem     --bbox 43.1495,-4.6265,43.1560,-4.6195 --out <scratch>/mdt05.tif
    python Tools/env_district.py measure --osm <scratch>/osm.json --dem <scratch>/mdt05.tif --origin 43.1542,-4.6237 \
                                         --box -60,-230,120,-10 --out district_metrics.json --plan district_reference.png

Raw OSM/DEM extracts stay out of the repository. Derived data carry "(c) OpenStreetMap contributors, ODbL 1.0" and
"MDT05 (c) Instituto Geografico Nacional, CC BY 4.0". Needs numpy, Pillow and shapely >= 2.1.
"""
import argparse
import json
import math
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from env_morphology import ATTRIBUTION, Frame  # noqa: E402

DEM_ATTRIBUTION = "MDT05 (c) Instituto Geografico Nacional (IGN), CC BY 4.0 (https://www.ign.es)"
WCS = ("https://servicios.idee.es/wcs-inspire/mdt?SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage"
       "&COVERAGEID=Elevacion4258_5&SUBSET=Lat({s},{n})&SUBSET=Long({w},{e})&FORMAT=image/tiff")
# street classes: which OSM highways are part of the walkable casco network, and which are left out
WALK = {"primary", "secondary", "tertiary", "residential", "unclassified", "living_street", "pedestrian", "service",
        "footway", "steps", "path", "track"}


# ---------------------------------------------------------------- terrain

def fetch_dem(bbox, out):
    s, w, n, e = bbox
    url = WCS.format(s=s, n=n, w=w, e=e)
    body = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "JuegoDef-ENV-district/1.0"}), timeout=120).read()
    if not body.startswith(b"II*") and not body.startswith(b"MM\0*"):
        sys.exit("ENV_DISTRICT_DEM_NOT_TIFF " + body[:200].decode("latin-1"))
    open(out, "wb").write(body)
    print(f"DEM {len(body)} bytes -> {out}")


class Dem:
    """IGN MDT05 GeoTIFF (EPSG:4258/4326, integer metres) sampled in the local frame, with optional smoothing."""

    def __init__(self, path, frame, smooth=0.0):
        import numpy as np
        from PIL import Image
        im = Image.open(path)
        t = im.tag_v2
        self.lon0, self.lat0 = t[33922][3], t[33922][4]
        self.dlon, self.dlat = t[33550][0], t[33550][1]
        self.Z = np.array(im).astype(float)
        self.frame = frame
        if smooth > 0:  # box blur of about `smooth` metres: the DEM is quantised to 1 m
            r = max(1, int(round(smooth / 5.0)))
            for ax in (0, 1):
                p = np.pad(self.Z, [(r + 1, r) if i == ax else (0, 0) for i in (0, 1)], mode="edge")
                cs = np.cumsum(p, axis=ax)
                self.Z = (np.take(cs, range(2 * r + 1, cs.shape[ax]), axis=ax)
                          - np.take(cs, range(0, cs.shape[ax] - 2 * r - 1), axis=ax)) / (2 * r + 1)

    def ground(self, x, y, r=4.0):
        """Street-level height: median of the DEM in a small disc, so a river channel or a terrace wall beside the
        street does not drag the centreline down."""
        vals = sorted(self.z(x + dx, y + dy) for dx in (-r, 0, r) for dy in (-r, 0, r))
        return vals[len(vals) // 2]

    def z(self, x, y):
        lon = self.frame.lon0 + x / self.frame.kx
        lat = self.frame.lat0 + y / self.frame.ky
        c = (lon - self.lon0) / self.dlon - 0.5
        r = (self.lat0 - lat) / self.dlat - 0.5
        c0 = min(max(int(math.floor(c)), 0), self.Z.shape[1] - 2)
        r0 = min(max(int(math.floor(r)), 0), self.Z.shape[0] - 2)
        fc, fr = min(max(c - c0, 0), 1), min(max(r - r0, 0), 1)
        Z = self.Z
        return float(Z[r0, c0] * (1 - fc) * (1 - fr) + Z[r0, c0 + 1] * fc * (1 - fr)
                     + Z[r0 + 1, c0] * (1 - fc) * fr + Z[r0 + 1, c0 + 1] * fc * fr)


def profile_grade(line, dem, step=2.0, window=10.0):
    """Representative grade of a street stretch: street-level heights every 2 m, grades over 10 m windows, 75th
    percentile (a single noisy DEM cell must not turn a street into a staircase)."""
    import numpy as np
    L = line.length
    if L < 4:
        return 0.0
    s = np.arange(0, L + 1e-6, step)
    z = np.array([dem.ground(*line.interpolate(v).coords[0]) for v in s])
    k = max(1, int(round(window / step)))
    if len(z) <= k:
        return abs(z[-1] - z[0]) / L
    g = np.abs(z[k:] - z[:-k]) / (s[k:] - s[:-k])
    return float(np.percentile(g, 75))


def grade_class(g, steps=False):
    """Owner rule 2026-09-28: 70 % comfortable, 20 % perceptible, 10 % strong or stairs."""
    if steps or g > 0.10:
        return "strong"
    if g > 0.05:
        return "perceptible"
    return "comfortable"


# ---------------------------------------------------------------- reference geometry

def load(doc, frame, box, margin=30.0):
    """Buildings (shapely polygons with tags) and walkable street ways (node ids + local points) near the box."""
    from shapely.geometry import Polygon, box as sbox
    area = sbox(box[0] - margin, box[1] - margin, box[2] + margin, box[3] + margin)
    buildings, ways, water = [], [], []
    for e in doc["elements"]:
        t = e.get("tags", {})
        g = e.get("geometry")
        if not g:
            continue
        pts = [tuple(frame.xy(p)) for p in g]
        if "building" in t and len(pts) >= 4:
            poly = Polygon(pts).buffer(0)
            if poly.is_valid and not poly.is_empty and poly.intersects(area):
                buildings.append({"id": e["id"], "poly": poly, "tags": t})
        elif "highway" in t and t["highway"] in WALK and "nodes" in e:
            if any(area.contains(_pt(p)) for p in pts):
                ways.append({"id": e["id"], "nodes": e["nodes"], "pts": pts, "tags": t})
        elif "waterway" in t:
            water.append({"id": e["id"], "pts": pts, "tags": t})
    return buildings, ways, water


def _pt(p):
    from shapely.geometry import Point
    return Point(p)


def graph(ways):
    """Street graph: junction nodes are OSM nodes shared by two or more ways (or way ends); each edge is the
    polyline between two junctions."""
    from collections import Counter
    use = Counter()
    for w in ways:
        for n in w["nodes"]:
            use[n] += 1
        use[w["nodes"][0]] += 1
        use[w["nodes"][-1]] += 1
    nodes, edges = {}, []
    for w in ways:
        cut = [i for i, n in enumerate(w["nodes"]) if use[n] >= 2]
        for a, b in zip(cut[:-1], cut[1:]):
            pts = w["pts"][a:b + 1]
            if len(pts) < 2:
                continue
            na, nb = w["nodes"][a], w["nodes"][b]
            nodes[na] = pts[0]
            nodes[nb] = pts[-1]
            edges.append({"a": na, "b": nb, "pts": pts, "highway": w["tags"]["highway"],
                          "name": w["tags"].get("name", ""), "way": w["id"]})
    deg = Counter()
    for e in edges:
        deg[e["a"]] += 1
        deg[e["b"]] += 1
    return nodes, edges, deg


def polylen(pts):
    return sum(math.dist(a, b) for a, b in zip(pts[:-1], pts[1:]))


# ---------------------------------------------------------------- measure

def measure(doc, dem, frame, box):
    import numpy as np
    from shapely.geometry import LineString, box as sbox
    from shapely.ops import polygonize, unary_union

    B = sbox(*box)
    buildings, ways, water = load(doc, frame, box)
    nodes, edges, deg = graph(ways)
    bunion = unary_union([b["poly"] for b in buildings])

    # facade-to-facade width of each edge: rays from the centreline to the nearest building on each side
    edges_b = [(b["poly"].exterior.coords, b["id"]) for b in buildings]
    EA = np.array([c[i] for c, _ in edges_b for i in range(len(c) - 1)])
    EB = np.array([c[i + 1] for c, _ in edges_b for i in range(len(c) - 1)])

    def ray(o, d, maxd=25.0):
        v1 = o - EA
        v2 = EB - EA
        v3 = np.array([-d[1], d[0]])
        den = v2 @ v3
        with np.errstate(divide="ignore", invalid="ignore"):
            t1 = (v2[:, 0] * v1[:, 1] - v2[:, 1] * v1[:, 0]) / den
            t2 = (v1 @ v3) / den
        ok = (np.abs(den) > 1e-9) & (t1 > 0.05) & (t1 < maxd) & (t2 >= 0) & (t2 <= 1)
        return float(t1[ok].min()) if ok.any() else None

    out_edges = []
    for k, e in enumerate(edges):
        line = LineString(e["pts"])
        inside = line.intersection(B)
        if inside.is_empty or inside.length < 1.0:
            continue
        L = line.length
        widths = []
        for s in np.arange(1.0, L - 1.0, 1.0):
            p = np.array(line.interpolate(s).coords[0])
            q = np.array(line.interpolate(min(L, s + 0.5)).coords[0]) - np.array(line.interpolate(max(0, s - 0.5)).coords[0])
            n = np.linalg.norm(q)
            if n < 1e-6:
                continue
            d = q / n
            nl = np.array([-d[1], d[0]])
            l, r = ray(p, nl), ray(p, -nl)
            if l is not None and r is not None:
                widths.append(l + r)
        za, zb = dem.ground(*e["pts"][0]), dem.ground(*e["pts"][-1])
        g = profile_grade(line, dem)
        out_edges.append({
            "id": f"e{k}", "a": str(e["a"]), "b": str(e["b"]), "name": e["name"], "highway": e["highway"],
            "length_m": round(L, 1), "inside_m": round(inside.length, 1),
            "width_p10_p50_p90": [round(float(x), 1) for x in np.percentile(widths, [10, 50, 90])] if len(widths) >= 3 else None,
            "z_ends": [round(za, 1), round(zb, 1)], "grade_mean": round(abs(zb - za) / max(L, 1), 3), "grade_max": round(g, 3),
            "class": grade_class(g, e["highway"] == "steps"),
            "pts": [[round(x, 2), round(y, 2)] for x, y in e["pts"]],
        })
    used = {e["a"] for e in out_edges} | {e["b"] for e in out_edges}
    out_nodes = []
    for nid, p in nodes.items():
        if str(nid) not in used:
            continue
        inc = [e for e in out_edges if str(nid) in (e["a"], e["b"])]
        kind = {1: "end", 2: "bend", 3: "T", 4: "X"}.get(len(inc), "multi")
        out_nodes.append({"id": str(nid), "xy": [round(p[0], 2), round(p[1], 2)], "z": round(dem.ground(*p), 1), "degree": len(inc),
                          "kind": kind, "inside": bool(B.contains(_pt(p)))})

    # urban blocks: faces of the street network (plus the box border), minus the street space
    lines = [LineString(e["pts"]) for e in out_edges] + [B.exterior]
    faces = [f for f in polygonize(unary_union(lines)) if f.area > 30 and B.buffer(0.5).contains(f)]
    blocks = []
    for i, f in enumerate(faces):
        bl = [b for b in buildings if b["poly"].representative_point().within(f)]
        built = unary_union([b["poly"] for b in bl]).intersection(f) if bl else None
        cover = built.area / f.area if built is not None else 0.0
        lv = [int(b["tags"]["building:levels"]) for b in bl if str(b["tags"].get("building:levels", "")).isdigit()]
        zs = [dem.z(*c) for c in f.exterior.coords]
        blocks.append({
            "id": f"b{i}", "area_m2": round(f.area), "perimeter_m": round(f.length), "buildings": len(bl),
            "built_share": round(cover, 2), "mean_depth_m": round(2 * f.area / f.length, 1),
            "levels_p50": sorted(lv)[len(lv) // 2] if lv else None, "z_min_max": [round(min(zs), 1), round(max(zs), 1)],
            "edge_of_box": bool(f.exterior.distance(B.exterior) < 0.5),
        })

    # terrain distribution by network length inside the box
    by = {"comfortable": 0.0, "perceptible": 0.0, "strong": 0.0}
    for e in out_edges:
        by[e["class"]] += e["inside_m"]
    tot = sum(by.values()) or 1
    fp = []
    for b in buildings:
        if not B.contains(b["poly"].representative_point()):
            continue
        p = np.array(b["poly"].minimum_rotated_rectangle.exterior.coords[:4])
        s1, s2 = np.linalg.norm(p[1] - p[0]), np.linalg.norm(p[2] - p[1])
        fp.append((min(s1, s2), max(s1, s2)))
    fp = np.array(fp)
    return {
        "attribution": [ATTRIBUTION, DEM_ATTRIBUTION],
        "osm_base": doc.get("osm3s", {}).get("timestamp_osm_base"),
        "box": box, "origin": [frame.lat0, frame.lon0],
        "summary": {
            "network_inside_m": round(tot), "edges": len(out_edges),
            "junctions": {k: sum(1 for n in out_nodes if n["kind"] == k and n["inside"]) for k in ("T", "X", "multi", "end", "bend")},
            "grade_share_reference": {k: round(v / tot, 2) for k, v in by.items()},
            "blocks": len(blocks), "buildings": int(len(fp)),
            "footprint_short_long_p50": [round(float(np.median(fp[:, 0])), 1), round(float(np.median(fp[:, 1])), 1)] if len(fp) else None,
            "built_share_box": round(bunion.intersection(B).area / B.area, 2),
            "z_range_network": [min(n["z"] for n in out_nodes if n["inside"]), max(n["z"] for n in out_nodes if n["inside"])],
        },
        "nodes": out_nodes, "edges": out_edges, "blocks": blocks,
        "water": [{"name": w["tags"].get("name", ""), "kind": w["tags"]["waterway"],
                   "pts": [[round(x, 1), round(y, 1)] for x, y in w["pts"]]} for w in water
                  if LineString(w["pts"]).intersects(B.buffer(20))],
    }


# ---------------------------------------------------------------- plan

def plan(doc, rep, frame, box, scale, out, margin=20):
    from PIL import Image, ImageDraw, ImageFont
    from shapely.geometry import LineString, box as sbox
    from shapely.ops import polygonize, unary_union
    win = [box[0] - margin, box[1] - margin, box[2] + margin, box[3] + margin]
    W, H = int((win[2] - win[0]) * scale), int((win[3] - win[1]) * scale)
    img = Image.new("RGB", (W, H), (244, 242, 235))
    dr = ImageDraw.Draw(img)
    px = lambda q: ((q[0] - win[0]) * scale, (win[3] - q[1]) * scale)
    try:
        font = ImageFont.truetype("arial.ttf", max(10, int(3.2 * scale)))
    except Exception:
        font = ImageFont.load_default()
    B = sbox(*box)
    lines = [LineString(e["pts"]) for e in rep["edges"]] + [B.exterior]
    faces = [f for f in polygonize(unary_union(lines)) if f.area > 30 and B.buffer(0.5).contains(f)]
    tones = [(233, 226, 205), (222, 229, 214), (230, 218, 222), (218, 226, 232), (236, 230, 214)]
    for i, f in enumerate(faces):
        dr.polygon([px(c) for c in f.exterior.coords], fill=tones[i % len(tones)])
    for w in rep["water"]:
        dr.line([px(p) for p in w["pts"]], fill=(110, 160, 215), width=max(3, int(3 * scale)))
    buildings, _, _ = load(doc, frame, box)
    for b in buildings:
        polys = [b["poly"]] if b["poly"].geom_type == "Polygon" else list(b["poly"].geoms)
        for p in polys:
            dr.polygon([px(c) for c in p.exterior.coords], fill=(196, 150, 120), outline=(90, 60, 45))
    cls = {"comfortable": (60, 150, 70), "perceptible": (230, 160, 30), "strong": (210, 40, 40)}
    for e in rep["edges"]:
        dr.line([px(p) for p in e["pts"]], fill=cls[e["class"]], width=max(2, int(1.2 * scale)))
    for n in rep["nodes"]:
        if n["kind"] in ("T", "X", "multi"):
            x, y = px(n["xy"])
            r = 1.2 * scale
            dr.ellipse([x - r, y - r, x + r, y + r], fill=(20, 20, 20))
    for i, (k, c) in enumerate(cls.items()):
        y = 12 + i * 5 * scale
        dr.line([(12, y), (40, y)], fill=c, width=5)
        dr.text((46, y - 7), {"comfortable": "<= 5 %", "perceptible": "5-10 %", "strong": "> 10 % / escaleras"}[k]
                + f"  ({rep['summary']['grade_share_reference'][k] * 100:.0f} % de la red)", fill=(0, 0, 0), font=font)
    dr.rectangle([px((box[0], box[3])), px((box[2], box[1]))], outline=(200, 30, 30), width=2)
    dr.line([(20, H - 20), (20 + 20 * scale, H - 20)], fill=(0, 0, 0), width=3)
    dr.text((20, H - 40), "20 m", fill=(0, 0, 0), font=font)
    dr.text((W - 560, H - 18), "(c) OpenStreetMap contributors ODbL - MDT05 (c) IGN CC BY 4.0", fill=(70, 70, 70), font=font)
    img.save(out, quality=90)
    print(out, W, H)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dem")
    d.add_argument("--bbox", required=True)
    d.add_argument("--out", required=True)
    m = sub.add_parser("measure")
    for a in ("--osm", "--dem", "--origin", "--box", "--out"):
        m.add_argument(a, required=True)
    m.add_argument("--plan")
    m.add_argument("--scale", type=float, default=4.0)
    a = ap.parse_args()
    if a.cmd == "dem":
        return fetch_dem([float(v) for v in a.bbox.split(",")], a.out)
    lat0, lon0 = (float(v) for v in a.origin.split(","))
    frame = Frame(lat0, lon0)
    box = [float(v) for v in a.box.split(",")]
    doc = json.load(open(a.osm, encoding="utf-8"))
    dem = Dem(a.dem, frame)
    rep = measure(doc, dem, frame, box)
    json.dump(rep, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps(rep["summary"], indent=1, ensure_ascii=False))
    if a.plan:
        plan(doc, rep, frame, box, a.scale, a.plan)


if __name__ == "__main__":
    main()

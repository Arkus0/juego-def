"""Fase 0 seed data for the Mapa F1 blockout (WP-CITY-SKELETON-00).

Reads the planning record `Docs/design/city/city_plan_v1.json` and writes the one-shot seed
`Docs/evidence/WP-CITY-SKELETON-00/city_blockout_seed.json` consumed by the Unity editor helper
`CityBlockoutSeed` (JuegoDef > CITY > Seed blockout). After the seed is materialised and saved, the authored Unity
scenes are the spatial authority; this file is never re-applied over them (the helper refuses to re-seed).

  python Tools/city_blockout.py seed   [--plan ...] [--out ...]
  python Tools/city_blockout.py render [--seed ...] [--out ...]

Assistance only, no procedural design decisions: streets follow the authored graph (bent so their length matches the
declared curvature factor), buildings are placed as simple frontage blocks next to their authored reference node, in
authored order, and anything that does not fit is reported as UNPLACED for manual placement in Unity.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon, box as sbox
from shapely.affinity import rotate, translate
from shapely.ops import unary_union
from shapely.prepared import prep

REPO = Path(__file__).resolve().parent.parent
PLAN = REPO / "Docs" / "design" / "city" / "city_plan_v1.json"
SEED = REPO / "Docs" / "evidence" / "WP-CITY-SKELETON-00" / "city_blockout_seed.json"

CELL = 6.5            # metres of frontage per FacadeCell (ENV01 median frontage 6.76 m)
DEPTH = {"G": 20.0, "M": 14.0, "P": 10.0, "C": 14.0}
MIN_WIDTH = {"G": 22.0, "M": 12.0, "P": 7.0, "C": 13.0}
STOREY = 3.0
SETBACK = 0.4
GRID = 2.0            # terrain cell size (m)


def stable_sign(text):
    return 1 if int(hashlib.md5(text.encode()).hexdigest(), 16) % 2 else -1


def bezier(p0, p1, p2, n):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [i / n for i in range(n + 1)]]


def bent_polyline(a, b, curvature, key):
    """Gentle meander between a and b (a bend every ~28 m) whose length ~= straight length * curvature."""
    ax, az = a
    bx, bz = b
    straight = math.hypot(bx - ax, bz - az)
    target = straight * curvature
    if curvature <= 1.001 or straight < 1:
        return [a, b]
    nx, nz = -(bz - az) / straight, (bx - ax) / straight
    sign = stable_sign(key)
    waves = max(1, round(straight / 28.0))
    n = max(8, waves * 8)

    def pts_for(amp):
        out = []
        for i in range(n + 1):
            t = i / n
            off = amp * math.sin(math.pi * waves * t) * sign
            out.append((ax + (bx - ax) * t + nx * off, az + (bz - az) * t + nz * off))
        return out

    lo, hi = 0.0, straight * 0.5
    for _ in range(40):
        amp = (lo + hi) / 2
        p = pts_for(amp)
        length = sum(math.hypot(p[i + 1][0] - p[i][0], p[i + 1][1] - p[i][1]) for i in range(n))
        if length < target:
            lo = amp
        else:
            hi = amp
    return pts_for(lo)


def with_heights(pts, ya, yb, stepped):
    """Linear grade between end heights; stair-class axes are quantised into real steps (riser <= 0.15 m)."""
    lengths = [0.0]
    for i in range(len(pts) - 1):
        lengths.append(lengths[-1] + math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]))
    total = lengths[-1] or 1.0
    out = []
    for (x, z), s in zip(pts, lengths):
        y = ya + (yb - ya) * s / total
        out.append([round(x, 3), round(y, 3), round(z, 3)])
    risers = 0
    if stepped:
        rise = abs(yb - ya)
        risers = max(1, math.ceil(rise / 0.15))
    return out, risers


def end_point(nodes, end):
    if "@" not in end:
        n = nodes[end]
        return (n["x"], n["z"], n["y"])
    eid, t = end.split("@")
    return ("edge", eid, float(t))


def seed(plan):
    nodes = {n["id"]: n for n in plan["nodes"]}
    streets, corridors = [], []
    street_lines = {}
    for e in plan["edges"]:
        a, b = nodes[e["a"]], nodes[e["b"]]
        pts2 = bent_polyline((a["x"], a["z"]), (b["x"], b["z"]), e["curvature"], e["id"])
        pts3, risers = with_heights(pts2, a["y"], b["y"], e["class"] == "stair")
        line = LineString(pts2)
        street_lines[e["id"]] = (line, pts3)
        corridors.append(line.buffer(e["width"] / 2 + SETBACK, cap_style=2))
        streets.append({"id": e["id"], "name": e["name"], "class": e["class"], "width": e["width"], "access": e["access"],
                        "points": pts3, "risers": risers, "length": round(line.length, 1)})

    def point_on_edge(eid, t):
        line, pts3 = street_lines[eid]
        p = line.interpolate(t, normalized=True)
        ya = pts3[0][1]
        yb = pts3[-1][1]
        return (p.x, p.y, ya + (yb - ya) * t)

    def resolve(end):
        r = end_point(nodes, end)
        if r[0] == "edge":
            return point_on_edge(r[1], r[2])
        return r

    links = []
    link_corr = []
    for k in plan["layerLinks"]:
        pa, pb = resolve(k["a"]), resolve(k["b"])
        pts = [[round(pa[0], 3), round(pa[2], 3), round(pa[1], 3)], [round(pb[0], 3), round(pb[2], 3), round(pb[1], 3)]]
        links.append({"id": k["id"], "name": k["name"], "layer": k["layer"], "access": k["access"], "condition": k["condition"],
                      "walkable": k["walkable"], "width": k["width"], "points": pts})
        if k["walkable"] and k["layer"] in ("service", "garden", "openspace") and k["width"] > 0:
            link_corr.append(LineString([(pa[0], pa[1]), (pb[0], pb[1])]).buffer(max(k["width"], 1.2) / 2 + 0.2, cap_style=2))

    opens = []
    open_polys = []
    for o in plan["openSpaces"]:
        n = nodes[o["node"]]
        w, d = o["size"]
        poly = sbox(n["x"] - w / 2, n["z"] - d / 2, n["x"] + w / 2, n["z"] + d / 2)
        open_polys.append(poly)
        opens.append({"id": o["id"], "name": o["name"], "access": o["access"], "y": n["y"],
                      "polygon": [[round(x, 2), round(z, 2)] for x, z in list(poly.exterior.coords)[:-1]]})

    zone_polys = {z["id"]: unary_union([Polygon(p) for p in z["polygons"]]) for z in plan["zones"]}
    land = unary_union(list(zone_polys.values()))
    river = Polygon(plan["river"]["polygon"])
    quays = unary_union([sbox(10, -60, 260, 10), sbox(-130, -20, 4, 12), sbox(296, -40, 400, 6)])
    seam_corr = []
    for s in plan["seams"]:
        f = nodes[s["from"]]
        seam_corr.append(LineString([(f["x"], f["z"]), tuple(s["stub"])]).buffer(s["corridorWidth"] / 2 + 0.5, cap_style=2))
    blocked = unary_union(corridors + link_corr + open_polys + seam_corr + [river, quays])
    buildable = land.difference(blocked)

    # street samples for heights
    samples = []
    for s in streets:
        pts = s["points"]
        for i in range(len(pts) - 1):
            (x0, y0, z0), (x1, y1, z1) = pts[i], pts[i + 1]
            seg = math.hypot(x1 - x0, z1 - z0)
            for j in range(max(1, int(seg // 4))):
                t = j / max(1, int(seg // 4))
                samples.append((x0 + (x1 - x0) * t, z0 + (z1 - z0) * t, y0 + (y1 - y0) * t))
        samples.append((pts[-1][0], pts[-1][2], pts[-1][1]))
    for n in plan["nodes"]:
        samples.append((n["x"], n["z"], n["y"]))

    def idw(x, z):
        num = den = 0.0
        for sx, sz, sy in samples:
            d2 = (sx - x) ** 2 + (sz - z) ** 2
            if d2 < 0.25:
                return sy
            w = 1.0 / (d2 * d2)
            num += w * sy
            den += w
        return num / den

    # buildings: frontage blocks on the street or plaza frontages nearest to the authored reference node
    frontages = []   # (id, LineString, ya, yb, half_offset)
    for e in plan["edges"]:
        line, pts3 = street_lines[e["id"]]
        frontages.append((e["id"], line, pts3[0][1], pts3[-1][1], e["width"] / 2 + SETBACK))
    for o, poly in zip(plan["openSpaces"], open_polys):
        cs = list(poly.exterior.coords)
        for i in range(4):
            frontages.append((f"{o['id']}:{i}", LineString([cs[i], cs[i + 1]]), nodes[o["node"]]["y"], nodes[o["node"]]["y"], SETBACK))
    for k in plan["layerLinks"]:
        if k["walkable"] and k["layer"] in ("service", "garden") and k["width"] > 0:
            pa, pb = resolve(k["a"]), resolve(k["b"])
            frontages.append((k["id"], LineString([(pa[0], pa[1]), (pb[0], pb[1])]), pa[2], pb[2], max(k["width"], 1.2) / 2 + 0.4))
    buildable_p = prep(buildable)
    out_buildings, unplaced, occupied = [], [], []
    order = sorted(plan["buildings"], key=lambda b: ("GMPC".index(b["scale"]), b["id"]))
    for bl in order:
        node = nodes[bl["nearNode"]]
        npt = Point(node["x"], node["z"])
        cells = bl["facadeCells"] * (2 if bl["scale"] == "C" else 1)
        width = max(MIN_WIDTH[bl["scale"]], cells * CELL)
        depth = DEPTH[bl["scale"]]
        near = sorted((f for f in frontages if f[1].distance(npt) <= 70.0), key=lambda f: f[1].distance(npt))
        best = None
        for shrink in (1.0, 0.85, 0.7, 0.55):
            if best:
                break
            w, dpt = max(5.0, width * shrink), max(6.0, depth * min(1.0, shrink + 0.15))
            for fid, line, ya, yb, half in near:
                L = line.length
                if L < w + 1:
                    continue
                s0 = min(max(line.project(npt) - w / 2, 0.5), L - w - 0.5)
                for k in range(0, 80):
                    s = s0 + (k // 2 + 1) * 1.5 * (1 if k % 2 == 0 else -1) if k else s0
                    if s < 0.5 or s + w > L - 0.5:
                        continue
                    pa, pb = line.interpolate(s), line.interpolate(s + w)
                    dx, dz = pb.x - pa.x, pb.y - pa.y
                    seg = math.hypot(dx, dz) or 1.0
                    for side in (1, -1):
                        nx, nz = -dz / seg * side, dx / seg * side
                        quad = Polygon([(pa.x + nx * half, pa.y + nz * half), (pb.x + nx * half, pb.y + nz * half),
                                        (pb.x + nx * (half + dpt), pb.y + nz * (half + dpt)), (pa.x + nx * (half + dpt), pa.y + nz * (half + dpt))])
                        if not quad.is_valid or quad.area < 1 or not buildable_p.contains(quad.buffer(-0.35)):
                            continue
                        core = quad.buffer(-0.05)
                        if any(core.intersects(o) for o in occupied):
                            continue
                        tm = (s + w / 2) / L
                        floor_y = ya + (yb - ya) * tm
                        door = ((pa.x + pb.x) / 2 + nx * half, (pa.y + pb.y) / 2 + nz * half)
                        best = (quad, floor_y, door, (-nx, -nz), fid)
                        break
                    if best:
                        break
                if best:
                    break
        if not best:
            unplaced.append(bl["id"])
            continue
        quad, floor_y, door, facing, eid = best
        occupied.append(quad)
        floors = bl["visualFloors"]
        out_buildings.append({**{k: bl[k] for k in ("id", "zone", "sector", "name", "scale", "interior", "access")},
                              "street": eid, "floorY": round(floor_y, 2), "floors": floors, "height": floors * STOREY,
                              "footprint": [[round(x, 2), round(z, 2)] for x, z in list(quad.exterior.coords)[:-1]],
                              "door": [round(door[0], 2), round(floor_y, 2), round(door[1], 2)],
                              "doorFacing": [round(facing[0], 3), round(facing[1], 3)],
                              "area": round(quad.area, 1)})

    # terrain grid (land minus river): exact street/plaza level inside their footprint, smooth IDW elsewhere
    zone_index = {"CASCO": 0, "MERCADO": 1, "MUELLE": 2, "TALLERES": 3, "VIVIENDAS": 4}
    flat_open = [(prep(poly.buffer(1.0)), nodes[o["node"]]["y"]) for o, poly in zip(plan["openSpaces"], open_polys)]
    street_bands = [(prep(street_lines[e["id"]][0].buffer(e["width"] / 2 + 1.2, cap_style=2)), street_lines[e["id"]][0],
                     street_lines[e["id"]][1][0][1], street_lines[e["id"]][1][-1][1]) for e in plan["edges"]]

    def ground_y(x, z):
        pt = Point(x, z)
        for pp, y in flat_open:
            if pp.contains(pt):
                return y
        best = None
        for pp, line, ya, yb in street_bands:
            if pp.contains(pt):
                d = line.distance(pt)
                if best is None or d < best[0]:
                    t = line.project(pt, normalized=True)
                    best = (d, ya + (yb - ya) * t)
        return best[1] if best else idw(x, z)
    minx, minz, maxx, maxz = land.bounds
    cols, rows = int(math.ceil((maxx - minx) / GRID)), int(math.ceil((maxz - minz) / GRID))
    cells = []
    zp = {k: prep(v) for k, v in zone_polys.items()}
    river_p = prep(river)
    for j in range(rows):
        for i in range(cols):
            cx, cz = minx + (i + 0.5) * GRID, minz + (j + 0.5) * GRID
            pt = Point(cx, cz)
            if river_p.contains(pt):
                continue
            zone = next((k for k, p in zp.items() if p.contains(pt)), None)
            if zone is None:
                continue
            cells.append([i, j, round(ground_y(cx, cz) - 0.12, 2), zone_index[zone]])

    def river_y(z):
        return max(0.0, min(9.0, 0.032 * z))

    river_out = {"polygon": plan["river"]["polygon"], "surfaceY": [[z, round(river_y(z), 2)] for z in range(0, 341, 20)]}
    seams = []
    for s in plan["seams"]:
        f = nodes[s["from"]]
        seams.append({"id": s["id"], "from": s["from"], "points": [[f["x"], f["y"], f["z"]], [s["stub"][0], f["y"], s["stub"][1]]],
                      "corridorWidth": s["corridorWidth"], "closure": s["closureToday"], "future": s["future"]})

    # edge guards: land boundary (water, river, envelope edge) minus every street/bridge/seam crossing
    openings = unary_union([street_lines[e["id"]][0].buffer(e["width"] / 2 + 0.8, cap_style=2) for e in plan["edges"]]
                           + seam_corr + open_polys)
    boundary = land.difference(river).boundary.difference(openings)
    guards = []
    lines = [boundary] if boundary.geom_type == "LineString" else list(getattr(boundary, "geoms", []))
    for ln in lines:
        if ln.geom_type != "LineString" or ln.length < 1.0:
            continue
        n = max(1, int(ln.length // 2.0))
        pts = []
        for i in range(n + 1):
            p = ln.interpolate(i / n, normalized=True)
            pts.append([round(p.x, 2), round(idw(p.x, p.y) - 0.12, 2), round(p.y, 2)])
        guards.append(pts)

    rp = plan["river"]["polygon"]
    half = len(rp) // 2
    east = rp[1:half + 1]
    west = [rp[0]] + list(reversed(rp[half + 1:]))
    river_strip = [[[w[0], round(river_y((w[1] + e[1]) / 2), 2), w[1]], [e[0], round(river_y((w[1] + e[1]) / 2), 2), e[1]]]
                   for w, e in zip(west, east)]

    built = unary_union([Polygon(b["footprint"]) for b in out_buildings])
    report = {
        "buildings_placed": len(out_buildings), "buildings_unplaced": unplaced,
        "footprint_m2": round(built.area), "land_m2": round(land.area),
        "manzana_land_without_building_m2": round(buildable.difference(built).area),
        "by_zone_footprint_m2": {z: round(built.intersection(p).area) for z, p in zone_polys.items()},
    }
    return {
        "schema": "juego-def.city-blockout-seed/1",
        "source": {"plan": "Docs/design/city/city_plan_v1.json", "planVersion": plan["version"]},
        "note": "One-shot seed. After materialisation the authored Unity scenes are the spatial authority.",
        "zones": [{"id": k, "index": zone_index[k], "polygons": [z for zz in plan["zones"] if zz["id"] == k for z in zz["polygons"]]} for k in zone_index],
        "terrain": {"origin": [round(minx, 3), round(minz, 3)], "cell": GRID, "cols": cols, "rows": rows, "cells": cells},
        "river": river_out,
        "riverStrip": river_strip,
        "guards": guards,
        "spawn": [nodes["L"]["x"] + 2.0, nodes["L"]["y"], nodes["L"]["z"] + 1.0],
        "harbour": {"y": 0.0, "polygon": [[-160, -80], [440, -80], [440, 0], [-160, 0]]},
        "streets": streets, "layerLinks": links, "openSpaces": opens, "seams": seams,
        "nodes": [{"id": n["id"], "x": n["x"], "y": n["y"], "z": n["z"], "zone": n["zone"], "role": n["role"], "anchorOf": n.get("anchorOf")} for n in plan["nodes"]],
        "buildings": out_buildings,
        "report": report,
    }


def render(seed_doc, out):
    from PIL import Image, ImageDraw, ImageFont
    xs = [p[0] for z in seed_doc["zones"] for poly in z["polygons"] for p in poly]
    zs = [p[1] for z in seed_doc["zones"] for poly in z["polygons"] for p in poly]
    X0, X1, Z0, Z1 = min(xs) - 20, max(xs) + 20, min(zs) - 20, max(zs) + 20
    S = 3.0
    W, H = int((X1 - X0) * S), int((Z1 - Z0) * S)
    px = lambda x, z: ((x - X0) * S, (Z1 - z) * S)
    img = Image.new("RGB", (W, H), (150, 178, 186))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 11)
        big = ImageFont.truetype("arialbd.ttf", 20)
    except OSError:
        font = big = ImageFont.load_default()
    colors = [(214, 186, 160), (232, 214, 170), (186, 200, 206), (196, 190, 178), (204, 214, 178)]
    for z in seed_doc["zones"]:
        for poly in z["polygons"]:
            d.polygon([px(x, zz) for x, zz in poly], fill=colors[z["index"]])
    d.polygon([px(x, z) for x, z in seed_doc["river"]["polygon"]], fill=(110, 150, 170))
    for s in seed_doc["streets"]:
        pts = [px(p[0], p[2]) for p in s["points"]]
        d.line(pts, fill=(235, 232, 225) if s["class"] != "stair" else (210, 90, 80), width=max(2, int(s["width"] * S)))
    for o in seed_doc["openSpaces"]:
        d.polygon([px(x, z) for x, z in o["polygon"]], outline=(60, 120, 60), fill=(222, 228, 205))
    for k in seed_doc["layerLinks"]:
        a, b = k["points"]
        d.line([px(a[0], a[2]), px(b[0], b[2])], fill=(150, 60, 150), width=2)
    col = {"G": (150, 30, 30), "M": (190, 110, 40), "P": (60, 110, 60), "C": (110, 105, 100)}
    for bl in seed_doc["buildings"]:
        d.polygon([px(x, z) for x, z in bl["footprint"]], fill=col[bl["scale"]], outline=(30, 30, 30))
        cx = sum(p[0] for p in bl["footprint"]) / 4
        cz = sum(p[1] for p in bl["footprint"]) / 4
        d.text(px(cx - 3, cz + 1), bl["id"], fill=(255, 255, 255), font=font)
        dx, dz = bl["door"][0], bl["door"][2]
        x, y = px(dx, dz)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 230, 0))
    r = seed_doc["report"]
    d.text((12, 10), f"Seed blockout Mapa F1 — {r['buildings_placed']} edificios colocados, {len(r['buildings_unplaced'])} sin colocar — huella {r['footprint_m2']} m²",
           fill=(10, 10, 10), font=big)
    img.save(out)
    return out


def measure(export, plan):
    """Budgets re-measured from the authored scene export (CityMetricsExport), same rules as Tools/city_plan.py."""
    items = export["items"]
    by_kind = lambda prefix: [i for i in items if i["kind"].startswith(prefix)]

    def plen(outline):
        return sum(math.hypot(outline[k + 1][0] - outline[k][0], outline[k + 1][2] - outline[k][2]) for k in range(len(outline) - 1))

    zone_polys = {}
    for z in by_kind("Zone"):
        zone_polys.setdefault(z["source"], []).append(Polygon([(p[0], p[2]) for p in z["outline"]]))
    zones = {k: unary_union(v) for k, v in zone_polys.items()}
    land = unary_union(list(zones.values()))
    area = {k: round(v.area) for k, v in zones.items()}
    streets = by_kind("StreetAxis")
    public = sum(plen(s["outline"]) for s in streets)
    grades = {"comfortable": 0.0, "perceptible": 0.0, "strong": 0.0}
    for s in streets:
        o = s["outline"]
        L = plen(o)
        if L <= 0:
            continue
        g = abs(o[-1][1] - o[0][1]) / L * 100
        k = "strong" if (":stair:" in s["kind"] or g > 10) else ("perceptible" if g > 5 else "comfortable")
        grades[k] += L
    links = by_kind("LayerLink")
    capped = [l for l in links if l["kind"].split(":")[2] in ("PUB", "PUB-H") and l["kind"].split(":")[1] in ("service", "garden", "water", "upper")]
    cap_total = public + sum(plen(l["outline"]) for l in capped)
    blds = by_kind("SemanticBuilding")
    scale = lambda b: b["kind"].split(":")[1]
    interior = lambda b: b["kind"].split(":")[2]
    zone_of = lambda b: b["kind"].split(":")[3]
    planned = {b["id"]: b for b in plan["buildings"]}
    in_scene = {b["id"] for b in blds}
    footprints = [Polygon(b["footprint"]) for b in blds]
    built = unary_union(footprints)
    overlaps = sum(1 for i, a in enumerate(footprints) for b in footprints[i + 1:] if a.intersection(b).area > 0.5)
    widths = {e["id"]: e["width"] for e in plan["edges"]}
    street_area = unary_union([LineString([(p[0], p[2]) for p in s["outline"]]).buffer(widths.get(s["id"], 4.0) / 2, cap_style=2) for s in streets])
    blocked_streets = [b["id"] for b, f in zip(blds, footprints) if f.intersection(street_area).area > 0.5]
    seams = by_kind("Seam")
    seam_corr = unary_union([LineString([(p[0], p[2]) for p in s["outline"]]).buffer(2.0) for s in seams])
    seam_blocked = [b["id"] for b, f in zip(blds, footprints) if f.intersects(seam_corr)]

    nav = {(p["a"], p["b"]): p for p in export["navPaths"]}
    def navlen(a, b):
        p = nav.get((a, b)) or nav.get((b, a))
        return p["length"] if p and p["status"] == "PathComplete" else None
    anchors = plan["anchors"]
    neighbours = {f"{a}-{b} ({rel})": navlen(anchors[a], anchors[b]) for a, b, rel in plan["neighbourRelations"]}
    public_nodes = sorted({e["a"] for e in plan["edges"]} | {e["b"] for e in plan["edges"]})
    failing = [(a, b) for (a, b), p in nav.items() if a in public_nodes and b in public_nodes and p["status"] != "PathComplete"]
    lens = [p["length"] for (a, b), p in nav.items() if a in public_nodes and b in public_nodes and p["status"] == "PathComplete"]
    extreme = max(lens) if lens else None
    accessible = sum(1 for b in blds if interior(b) != "CLOSED") + sum(1 for k in planned if k not in in_scene and planned[k]["interior"] != "CLOSED")
    total_planned = len(planned)
    budgets = plan["budgets"]
    out = {
        "source": "authored scene export (not the seed)",
        "zones_m2": area, "envelope_m2": round(land.area),
        "largest_to_smallest": round(max(area.values()) / min(area.values()), 2),
        "public_network_m": round(public), "public_plus_conditional_exterior_m": round(cap_total),
        "grade_share": {k: round(v / public, 3) for k, v in grades.items()},
        "buildings_in_scene": len(blds), "buildings_planned": total_planned,
        "buildings_pending_manual_placement": sorted(set(planned) - in_scene),
        "buildings_by_zone_in_scene": {z: sum(1 for b in blds if zone_of(b) == z) for z in sorted({zone_of(b) for b in blds})},
        "accessible_share_planned_ledger": round(accessible / total_planned, 3),
        "footprint_m2": round(built.area), "footprint_share": round(built.area / land.area, 3),
        "building_overlaps": overlaps, "buildings_intruding_streets": blocked_streets, "buildings_blocking_seams": seam_blocked,
        "navmesh": export["navmesh"],
        "nodes_not_on_navmesh": [k for k, v in export["nodeSnapped"].items() if not v],
        "public_pairs_without_navmesh_path": failing,
        "neighbour_routes_navmesh_m": neighbours,
        "extreme_route_navmesh_m": extreme,
    }
    checks = {
        "envelope<=max": out["envelope_m2"] <= budgets["envelopeMaxM2"],
        "public_plus_conditional<=max": cap_total <= budgets["publicNetworkMaxM"],
        "neighbours<=max (navmesh)": all(v is not None and v <= budgets["neighbourRouteMaxM"] for v in neighbours.values()),
        "extreme<=max (navmesh)": extreme is not None and extreme <= budgets["extremeRouteMaxM"],
        "largest>=2x_smallest": out["largest_to_smallest"] >= budgets["largestToSmallestMin"],
        "all_public_pairs_navigable": not failing,
        "no_building_overlaps": overlaps == 0,
        "no_buildings_on_streets": not blocked_streets,
        "seams_free": not seam_blocked,
        "all_planned_buildings_in_scene": not out["buildings_pending_manual_placement"],
    }
    out["checks"] = checks
    out["all_checks_pass"] = all(checks.values())
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["seed", "render", "measure"])
    ap.add_argument("--export", default=str(SEED.with_name("SCENE_EXPORT.json")))
    ap.add_argument("--plan", default=str(PLAN))
    ap.add_argument("--seed", default=str(SEED))
    ap.add_argument("--out")
    args = ap.parse_args()
    if args.command == "seed":
        doc = seed(json.loads(Path(args.plan).read_text(encoding="utf-8")))
        out = Path(args.out or args.seed)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps(doc["report"], ensure_ascii=False, indent=1))
        return 0
    if args.command == "measure":
        res = measure(json.loads(Path(args.export).read_text(encoding="utf-8")), json.loads(Path(args.plan).read_text(encoding="utf-8")))
        text = json.dumps(res, ensure_ascii=False, indent=1)
        Path(args.out or str(Path(args.export).with_name("SCENE_METRICS.json"))).write_text(text + "\n", encoding="utf-8", newline="\n")
        print(text)
        return 0 if res["all_checks_pass"] else 1
    doc = json.loads(Path(args.seed).read_text(encoding="utf-8"))
    print(render(doc, args.out or str(Path(args.seed).with_name("SEED_PLAN.png"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

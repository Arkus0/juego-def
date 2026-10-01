"""City master plan — reproducible metrics and scaled plan renders for `Docs/design/city/city_plan_v1.json`.

The JSON is a PLANNING RECORD (WP-CITY-MASTER-00). It is not spatial authority: once WP-CITY-SKELETON-00 seeds the
authored Unity scenes, the scene wins and these metrics are re-measured from a scene export with the same rules.

  python Tools/city_plan.py metrics [--plan Docs/design/city/city_plan_v1.json] [--out metrics.json]
  python Tools/city_plan.py render  [--plan ...] [--out-dir Docs/design/city]

Rules (COMPACT_SEMANTIC_CITY_REBASELINE + Owner amendment 2026-10-01):
- envelope = union of identity polygons (river channel inside, harbour water outside);
- public network = unique public axes (`edges`), length = straight span x declared curvature factor. Exterior links of
  the interconnection layer that are public at some hour (PUB/PUB-H, not dead-end open spaces) are added to the same
  cap; interior, service, private, controlled and progress links are reported per layer, never hidden;
- interconnection layer (`layerLinks`, Sapienza): attaches to nodes or to points `EDGE@t` on public axes; metrics
  compare public-only routes with all-walkable-layer routes (shortest length and edge-disjoint alternatives);
- grade classes by network length: comfortable <=5 %, perceptible 5-10 %, strong >10 % or stairs;
- neighbour routes = shortest public path between identity anchors of related identities (<=180 m),
  extremes = largest shortest path between any two public nodes (<=700 m);
- accessible = semantic buildings whose interior is walkable (LARGE/MEDIUM/SMALL), deep = LARGE.
"""

import argparse
import heapq
import itertools
import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLAN = REPO / "Docs" / "design" / "city" / "city_plan_v1.json"

ZONE_COLORS = {
    "CASCO": (214, 186, 160),
    "MERCADO": (232, 214, 170),
    "MUELLE": (186, 200, 206),
    "TALLERES": (196, 190, 178),
    "VIVIENDAS": (204, 214, 178),
}
CLASS_WIDTH_COLOR = {
    "main": (70, 70, 70), "commercial": (150, 60, 40), "secondary": (110, 110, 110),
    "stair": (190, 40, 40), "quay": (40, 90, 140), "bridge": (60, 60, 60),
    "alley": (150, 150, 150), "service": (150, 120, 60), "passage": (120, 70, 140),
}
LAYER_COLORS = {
    "service": (176, 120, 30), "interior": (150, 40, 150), "upper": (220, 90, 20),
    "water": (20, 110, 190), "garden": (40, 140, 60), "openspace": (90, 150, 200),
}
KEY_PAIRS = [
    ("L", "P", "pensión → puerto"), ("L", "C3", "pensión → Plaza Mayor"), ("A", "C1", "mercado → Calle de los Vinos"),
    ("S", "O", "tienda → terraza El Muro"), ("C1", "C3", "bar de misión → Plaza Mayor"), ("C3", "C5", "Plaza Mayor → iglesia"),
    ("P", "T2", "puerto → talleres"), ("E2", "T2", "Cantón → talleres"), ("V2", "T1", "Viviendas → Alto de la Cantera"),
    ("V1", "V4", "casa-cuartel → terrazas altas"), ("Q", "SL", "muelle → varadero"), ("C7", "C1", "Calle del Río → Vinos"),
]


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def shoelace(poly):
    s = 0.0
    for i in range(len(poly)):
        x1, z1 = poly[i]
        x2, z2 = poly[(i + 1) % len(poly)]
        s += x1 * z2 - x2 * z1
    return abs(s) / 2


def edge_length(nodes, e):
    a, b = nodes[e["a"]], nodes[e["b"]]
    return math.hypot(b["x"] - a["x"], b["z"] - a["z"]) * e["curvature"]


def grade_class(nodes, e, length):
    g = abs(nodes[e["a"]]["y"] - nodes[e["b"]]["y"]) / length * 100 if length else 0
    if e["class"] == "stair" or g > 10:
        return "strong", g
    return ("perceptible" if g > 5 else "comfortable"), g


def graph(nodes, edges):
    g = {k: [] for k in nodes}
    for e in edges:
        length = edge_length(nodes, e)
        g[e["a"]].append((e["b"], length))
        g[e["b"]].append((e["a"], length))
    return g


def counts_in_street_cap(link):
    """Exterior links that are public at some hour share the public-network cap (dead-end open spaces excluded)."""
    return link["layer"] in ("service", "garden", "water", "upper") and link["access"] in ("PUB", "PUB-H")


def layered_graph(plan):
    """Split public axes at every `EDGE@t` attach point; return point coordinates, public adjacency and all-layer adjacency.

    Adjacency entries are (neighbour, length, arc_id) so edge-disjoint alternatives can be counted.
    """
    nodes = {n["id"]: n for n in plan["nodes"]}
    edges = {e["id"]: e for e in plan["edges"]}
    pts = {k: (v["x"], v["z"], v["y"]) for k, v in nodes.items()}
    splits = {eid: {0.0, 1.0} for eid in edges}
    for link in plan.get("layerLinks", []):
        for end in (link["a"], link["b"]):
            if "@" in end:
                eid, t = end.split("@")
                splits[eid].add(float(t))
    pub, allg = {}, {}

    def add(adj, a, b, length, arc):
        adj.setdefault(a, []).append((b, length, arc))
        adj.setdefault(b, []).append((a, length, arc))

    for eid, e in edges.items():
        ts = sorted(splits[eid])
        full = edge_length(nodes, e)
        ax, az, ay = pts[e["a"]]
        bx, bz, by = pts[e["b"]]
        ids = []
        for t in ts:
            pid = e["a"] if t == 0.0 else e["b"] if t == 1.0 else f"{eid}@{t:g}"
            pts.setdefault(pid, (ax + (bx - ax) * t, az + (bz - az) * t, ay + (by - ay) * t))
            ids.append((pid, t))
        for (p, t0), (q, t1) in zip(ids, ids[1:]):
            arc = f"{eid}:{t0:g}-{t1:g}"
            add(pub, p, q, full * (t1 - t0), arc)
            add(allg, p, q, full * (t1 - t0), arc)
    for link in plan.get("layerLinks", []):
        if link["walkable"]:
            add(allg, end_id(link["a"]), end_id(link["b"]), link["length"], link["id"])
    return pts, pub, allg


def end_id(end):
    if "@" not in end:
        return end
    eid, t = end.split("@")
    return f"{eid}@{float(t):g}"


def shortest(adj, s, t):
    dist = {s: 0.0}
    pq = [(0.0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == t:
            return d
        if d > dist[u]:
            continue
        for v, w, _ in adj.get(u, []):
            if d + w < dist.get(v, math.inf):
                dist[v] = d + w
                heapq.heappush(pq, (d + w, v))
    return math.inf


def edge_disjoint(adj, s, t):
    """Number of edge-disjoint s–t routes (unit-capacity max flow on the undirected arcs)."""
    cap = {}
    for u, lst in adj.items():
        for v, _, arc in lst:
            cap[(u, v, arc)] = 1
    flow = 0
    while True:
        prev = {s: None}
        queue = [s]
        while queue and t not in prev:
            u = queue.pop(0)
            for v, _, arc in adj.get(u, []):
                if v not in prev and cap.get((u, v, arc), 0) > 0:
                    prev[v] = (u, arc)
                    queue.append(v)
        if t not in prev:
            return flow
        v = t
        while prev[v] is not None:
            u, arc = prev[v]
            cap[(u, v, arc)] -= 1
            cap[(v, u, arc)] = cap.get((v, u, arc), 0) + 1
            v = u
        flow += 1


def dijkstra(g, s):
    dist = {s: 0.0}
    pq = [(0.0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in g[u]:
            if d + w < dist.get(v, math.inf):
                dist[v] = d + w
                heapq.heappush(pq, (d + w, v))
    return dist


def metrics(plan):
    nodes = {n["id"]: n for n in plan["nodes"]}
    edges = plan["edges"]
    budgets = plan["budgets"]
    out = {"version": plan["version"], "status": "planning metrics (not scene measurements)"}

    zone_area = {z["id"]: round(sum(shoelace(p) for p in z["polygons"])) for z in plan["zones"]}
    total = sum(zone_area.values())
    out["zones_m2"] = zone_area
    out["envelope_m2"] = total
    out["largest_to_smallest"] = round(max(zone_area.values()) / min(zone_area.values()), 2)
    out["casco_share"] = round(zone_area["CASCO"] / total, 3)

    pub = 0.0
    by_class = {}
    grades = {"comfortable": 0.0, "perceptible": 0.0, "strong": 0.0}
    for e in edges:
        length = edge_length(nodes, e)
        pub += length
        by_class[e["class"]] = by_class.get(e["class"], 0.0) + length
        grades[grade_class(nodes, e, length)[0]] += length
    out["public_network_m"] = round(pub)
    out["public_by_class_m"] = {k: round(v) for k, v in sorted(by_class.items())}
    out["grade_share"] = {k: round(v / pub, 3) for k, v in grades.items()}
    links = plan.get("layerLinks", [])
    capped = [k for k in links if counts_in_street_cap(k)]
    street_cap_total = pub + sum(k["length"] for k in capped)
    out["public_plus_conditional_exterior_m"] = round(street_cap_total)
    out["conditional_exterior_in_cap"] = {k["id"] + " " + k["name"]: k["length"] for k in capped}
    by_layer = {}
    by_access = {}
    for k in links:
        by_layer.setdefault(k["layer"], [0, 0])
        by_layer[k["layer"]][0] += 1
        by_layer[k["layer"]][1] += k["length"]
        acc = k["access"].split("/")[0]
        by_access[acc] = by_access.get(acc, 0) + 1
    out["interconnection_layer"] = {
        "links": len(links),
        "walkable_m": sum(k["length"] for k in links if k["walkable"]),
        "by_layer_count_m": {k: v for k, v in sorted(by_layer.items())},
        "by_access_count": dict(sorted(by_access.items())),
        "vertical_points": len(plan.get("verticalPoints", [])),
    }
    node_zone = {n["id"]: n["zone"] for n in plan["nodes"]}
    for e in plan["edges"]:
        node_zone.setdefault(e["id"], node_zone[e["a"]])
    layers_by_zone = {}
    for k in links:
        for end in (k["a"], k["b"]):
            zone = node_zone.get(end.split("@")[0])
            if zone:
                layers_by_zone.setdefault(zone, set()).add(k["layer"])
    out["layers_by_zone"] = {z: ["street"] + sorted(v) for z, v in sorted(layers_by_zone.items())}
    pts, pub_adj, all_adj = layered_graph(plan)
    pairs = {}
    for s, t, label in KEY_PAIRS:
        pairs[f"{s}-{t} {label}"] = {
            "public_m": (lambda v: None if math.isinf(v) else round(v))(shortest(pub_adj, s, t)),
            "all_layers_m": (lambda v: None if math.isinf(v) else round(v))(shortest(all_adj, s, t)),
            "public_alternatives": edge_disjoint(pub_adj, s, t),
            "all_layer_alternatives": edge_disjoint(all_adj, s, t),
        }
    out["key_pairs"] = pairs

    used = {e["a"] for e in edges} | {e["b"] for e in edges}
    out["public_nodes"] = len(used)
    out["public_edges"] = len(edges)
    out["independent_cycles"] = len(edges) - len(used) + 1

    g = graph({k: v for k, v in nodes.items() if k in used}, edges)
    reach = dijkstra(g, next(iter(used)))
    out["connected"] = len(reach) == len(used)
    anchors = plan["anchors"]
    out["neighbour_routes_m"] = {f"{a}-{b} ({rel})": round(dijkstra(g, anchors[a])[anchors[b]]) for a, b, rel in plan["neighbourRelations"]}
    out["anchor_routes_m"] = {f"{a}-{b}": round(dijkstra(g, anchors[a])[anchors[b]]) for a, b in itertools.combinations(anchors, 2)}
    worst = (0.0, None, None)
    for s in used:
        for t, d in dijkstra(g, s).items():
            if d > worst[0]:
                worst = (d, s, t)
    out["extreme_route_m"] = {"length": round(worst[0]), "between": [worst[1], worst[2]]}

    bl = plan["buildings"]
    zones = sorted({b["zone"] for b in bl})
    out["buildings"] = {
        "total": len(bl),
        "by_zone": {z: sum(1 for b in bl if b["zone"] == z) for z in zones},
        "by_interior": {k: sum(1 for b in bl if b["interior"] == k) for k in ("LARGE", "MEDIUM", "SMALL", "CLOSED")},
        "accessible_by_zone": {z: f"{sum(1 for b in bl if b['zone'] == z and b['interior'] != 'CLOSED')}/{sum(1 for b in bl if b['zone'] == z)}" for z in zones},
    }
    acc = sum(1 for b in bl if b["interior"] != "CLOSED")
    deep = sum(1 for b in bl if b["interior"] == "LARGE")
    out["accessible_share"] = round(acc / len(bl), 3)
    out["deep_share"] = round(deep / len(bl), 3)

    checks = {
        "envelope<=max": total <= budgets["envelopeMaxM2"],
        "public_network<=max": pub <= budgets["publicNetworkMaxM"],
        "public_plus_conditional_exterior<=max": street_cap_total <= budgets["publicNetworkMaxM"],
        "every_zone_has>=3_extra_layers": all(len(v) >= 4 for v in out["layers_by_zone"].values()) and len(out["layers_by_zone"]) == 5,
        "key_pairs_gain_alternatives": all(p["all_layer_alternatives"] >= p["public_alternatives"] for p in pairs.values())
        and sum(p["all_layer_alternatives"] > p["public_alternatives"] for p in pairs.values()) >= len(pairs) // 2,
        "buildings<=max": len(bl) <= budgets["semanticBuildingsMax"],
        "casco_buildings<=max": out["buildings"]["by_zone"].get("CASCO", 0) <= budgets["cascoBuildingsMax"],
        "neighbours<=max": all(v <= budgets["neighbourRouteMaxM"] for v in out["neighbour_routes_m"].values()),
        "extreme<=max": worst[0] <= budgets["extremeRouteMaxM"],
        "largest>=2x_smallest": out["largest_to_smallest"] >= budgets["largestToSmallestMin"],
        "accessible>=target": out["accessible_share"] >= budgets["accessibleTarget"],
        "accessible>hard_min": out["accessible_share"] > budgets["accessibleHardMin"],
        "deep<=max": out["deep_share"] <= budgets["deepMax"],
        "network_connected": out["connected"],
        "unique_building_ids": len({b["id"] for b in bl}) == len(bl),
    }
    out["checks"] = checks
    out["all_checks_pass"] = all(checks.values())
    return out


def render(plan, out_dir):
    from PIL import Image, ImageDraw, ImageFont
    from shapely.geometry import LineString, Polygon, box as sbox
    from shapely.ops import unary_union

    nodes = {n["id"]: n for n in plan["nodes"]}
    S = 3.0
    xs = [x for z in plan["zones"] for poly in z["polygons"] for x, _ in poly] + [s["stub"][0] for s in plan["seams"]]
    zs = [zz for z in plan["zones"] for poly in z["polygons"] for _, zz in poly] + [s["stub"][1] for s in plan["seams"]]
    X0, X1, Z0, Z1 = min(xs) - 25.0, max(xs) + 25.0, min(zs) - 30.0, max(zs) + 25.0
    W, H = int((X1 - X0) * S), int((Z1 - Z0) * S)
    px = lambda x, z: ((x - X0) * S, (Z1 - z) * S)
    try:
        font = ImageFont.truetype("arial.ttf", 15)
        small = ImageFont.truetype("arial.ttf", 12)
        big = ImageFont.truetype("arialbd.ttf", 22)
    except OSError:
        font = small = big = ImageFont.load_default()

    land = unary_union([Polygon(p) for z in plan["zones"] for p in z["polygons"]])
    river = Polygon(plan["river"]["polygon"])
    streets = unary_union([LineString([(nodes[e["a"]]["x"], nodes[e["a"]]["z"]), (nodes[e["b"]]["x"], nodes[e["b"]]["z"])]).buffer(e["width"] / 2 + 0.5, cap_style=2)
                           for e in plan["edges"]])
    opens = unary_union([sbox(nodes[o["node"]]["x"] - o["size"][0] / 2, nodes[o["node"]]["z"] - o["size"][1] / 2,
                              nodes[o["node"]]["x"] + o["size"][0] / 2, nodes[o["node"]]["z"] + o["size"][1] / 2) for o in plan["openSpaces"]])
    quay_band = unary_union([sbox(10, -60, 260, 12), sbox(-130, -20, 4, 16), sbox(296, -40, 400, 10)])
    masses = land.difference(river).difference(streets).difference(opens).difference(quay_band)

    def fill(draw, geom, color, outline=None):
        geoms = [geom] if geom.geom_type == "Polygon" else list(getattr(geom, "geoms", []))
        for g in geoms:
            if g.geom_type != "Polygon" or g.area < 1:
                continue
            draw.polygon([px(x, z) for x, z in g.exterior.coords], fill=color, outline=outline)
            for hole in g.interiors:
                draw.polygon([px(x, z) for x, z in hole.coords], fill=(250, 248, 242))

    def relief_tint(base, y):
        k = min(max(y / 14.0, 0.0), 1.0)
        return tuple(int(c * (1.0 - 0.28 * k)) for c in base)

    def zone_y(zid):
        ys = [n["y"] for n in plan["nodes"] if n["zone"] == zid]
        return sum(ys) / len(ys)

    def base_image(title):
        img = Image.new("RGB", (W, H), (250, 248, 242))
        d = ImageDraw.Draw(img)
        d.rectangle([px(X0, 0)[0], px(0, 0)[1], W, H], fill=(150, 178, 186))
        for x in range(int(X0 // 50) * 50, int(X1) + 1, 50):
            d.line([px(x, Z0), px(x, Z1)], fill=(232, 228, 220), width=1)
        for z in range(int(Z0 // 50) * 50, int(Z1) + 1, 50):
            d.line([px(X0, z), px(X1, z)], fill=(232, 228, 220), width=1)
        for z in plan["zones"]:
            col = relief_tint(ZONE_COLORS[z["id"]], zone_y(z["id"]))
            for p in z["polygons"]:
                d.polygon([px(x, zz) for x, zz in p], fill=col, outline=(120, 110, 100))
        d.polygon([px(x, z) for x, z in plan["river"]["polygon"]], fill=(120, 160, 175))
        d.text((16, 12), title, fill=(30, 30, 30), font=big)
        d.line([(20, H - 30), (20 + 50 * S, H - 30)], fill=(0, 0, 0), width=4)
        d.text((20, H - 52), "50 m", fill=(0, 0, 0), font=font)
        nx, ny = W - 60, 70
        d.polygon([(nx, ny - 40), (nx - 12, ny), (nx + 12, ny)], fill=(30, 30, 30))
        d.text((nx - 6, ny + 4), "N", fill=(30, 30, 30), font=font)
        return img, d

    def idw_y(x, z):
        num = den = 0.0
        for n in plan["nodes"]:
            dd = (n["x"] - x) ** 2 + (n["z"] - z) ** 2
            if dd < 1e-6:
                return n["y"]
            w = 1.0 / dd
            num += w * n["y"]
            den += w
        return num / den

    def contours(draw, step=1.0, res=2.0):
        cols = int((X1 - X0) / res)
        rows = int((Z1 - Z0) / res)
        band = {}
        for i in range(cols):
            for j in range(rows):
                x, z = X0 + (i + 0.5) * res, Z0 + (j + 0.5) * res
                if z < -5:
                    continue
                band[(i, j)] = int(idw_y(x, z) // step)
        for (i, j), v in band.items():
            for di, dj in ((1, 0), (0, 1)):
                w = band.get((i + di, j + dj))
                if w is not None and w != v:
                    x, z = X0 + (i + 0.5) * res, Z0 + (j + 0.5) * res
                    if land.contains(Polygon([(x - 1, z - 1), (x + 1, z - 1), (x + 1, z + 1), (x - 1, z + 1)]).centroid):
                        cx, cy = px(x, z)
                        major = max(v, w) % 2 == 0
                        r = 1.6 if major else 0.9
                        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(90, 70, 50) if major else (140, 120, 100))

    # 1 — masas + relieve + red
    img, d = base_image("Mapa F1 (escala Kamurocho) v1.2 — masas, relieve (curvas cada 1 m) y red pública — planeamiento, no autoridad espacial")
    for zz in plan["zones"]:
        zpoly = unary_union([Polygon(p) for p in zz["polygons"]])
        base = ZONE_COLORS[zz["id"]]
        fill(d, masses.intersection(zpoly), tuple(int(c * 0.78) for c in base), outline=(110, 95, 80))
    contours(d)
    for e in plan["edges"]:
        a, b = nodes[e["a"]], nodes[e["b"]]
        d.line([px(a["x"], a["z"]), px(b["x"], b["z"])], fill=CLASS_WIDTH_COLOR[e["class"]], width=max(3, int(e["width"] * S * 0.6)))
    for o in plan["openSpaces"]:
        n = nodes[o["node"]]
        x0, y0 = px(n["x"] - o["size"][0] / 2, n["z"] + o["size"][1] / 2)
        x1, y1 = px(n["x"] + o["size"][0] / 2, n["z"] - o["size"][1] / 2)
        d.rectangle([x0, y0, x1, y1], outline=(60, 120, 60), width=2)
    for n in plan["nodes"]:
        x, y = px(n["x"], n["z"])
        r = 7 if "anchorOf" in n else 4
        d.ellipse([x - r, y - r, x + r, y + r], fill=(20, 20, 20) if "anchorOf" in n else (60, 60, 60))
        d.text((x + 8, y - 8), f"{n['id']} {n['y']:g}", fill=(10, 10, 10), font=small)
    for s in plan["seams"]:
        f = nodes[s["from"]]
        a, b = px(f["x"], f["z"]), px(*s["stub"])
        d.line([a, b], fill=(200, 60, 160), width=4)
        d.text((b[0] + 4, b[1] - 16), s["id"], fill=(200, 60, 160), font=font)
    for zz in plan["zones"]:
        p = Polygon(zz["polygons"][0]).representative_point()
        x, y = px(p.x, p.y)
        d.text((x - 30, y), zz["id"], fill=(40, 30, 20), font=big)
    legend = [("principal", "main"), ("comercial", "commercial"), ("secundaria", "secondary"), ("escalera", "stair"),
              ("muelle/paseo", "quay"), ("puente", "bridge"), ("paso cubierto", "passage")]
    lx, ly = int(px(150, -12)[0]), int(px(150, -12)[1])
    d.rectangle([lx - 10, ly - 18, lx + 520, ly + 20 * len(legend) + 52], fill=(250, 248, 242), outline=(120, 120, 120))
    for i, (label, k) in enumerate(legend):
        y = ly + i * 20
        d.line([(lx, y), (lx + 42, y)], fill=CLASS_WIDTH_COLOR[k], width=6)
        d.text((lx + 50, y - 9), label, fill=(20, 20, 20), font=font)
    d.text((lx, ly + len(legend) * 20), "masas = suelo de manzana: edificios + patios + huertas + patios de trabajo", fill=(20, 20, 20), font=small)
    d.text((lx, ly + len(legend) * 20 + 16), "(se particiona al 100 % en Fase 0) · nodo: id + cota Y · verde: espacio abierto · magenta: costura",
           fill=(20, 20, 20), font=small)
    p1 = Path(out_dir) / "CITY_PLAN_V1_masas_relieve_red.png"
    img.save(p1)

    # 3 — capa de interconexión (Sapienza): traseras, interiores, azoteas, agua, huertas
    pts, _, _ = layered_graph(plan)
    img, d = base_image("Mapa F1 (escala Kamurocho) v1.2 — interconexión por capas (más allá de la red pública)")
    fill(d, masses, (214, 204, 190))
    for e in plan["edges"]:
        a, b = nodes[e["a"]], nodes[e["b"]]
        d.line([px(a["x"], a["z"]), px(b["x"], b["z"])], fill=(150, 150, 150), width=5)

    def dashed(p, q, color, width, dash=10):
        (x0, y0), (x1, y1) = p, q
        length = math.hypot(x1 - x0, y1 - y0)
        steps = max(1, int(length // dash))
        for i in range(0, steps, 2):
            t0, t1 = i / steps, min(1.0, (i + 1) / steps)
            d.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0), (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)], fill=color, width=width)

    for k in plan.get("layerLinks", []):
        a, b = pts[end_id(k["a"])], pts[end_id(k["b"])]
        pa, pb = px(a[0], a[1]), px(b[0], b[1])
        col = LAYER_COLORS[k["layer"]]
        if k["walkable"]:
            dashed(pa, pb, col, 6 if k["access"].startswith("PUB") else 4)
        else:
            dashed(pa, pb, col, 3, dash=4)
        mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
        d.text((mx + 4, my - 14), f"{k['id']} {k['access']}", fill=col, font=small)
    for v in plan.get("verticalPoints", []):
        n = nodes[v["node"]]
        x, y = px(n["x"], n["z"])
        d.polygon([(x, y - 16), (x - 8, y - 2), (x + 8, y - 2)], fill=(220, 90, 20), outline=(60, 30, 10))
    for n in plan["nodes"]:
        x, y = px(n["x"], n["z"])
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(40, 40, 40))
        d.text((x + 6, y + 2), n["id"], fill=(40, 40, 40), font=small)
    legend = [("traseras y patios de trabajo", "service"), ("atravesar edificios (interior)", "interior"),
              ("azoteas / galerías", "upper"), ("cota de agua (muelle, canal, lancha)", "water"),
              ("huertas y patios privados", "garden"), ("espacio abierto sin salida", "openspace")]
    lx, ly = int(px(150, -12)[0]), int(px(150, -12)[1])
    d.rectangle([lx - 10, ly - 18, lx + 560, ly + 20 * len(legend) + 52], fill=(250, 248, 242), outline=(120, 120, 120))
    for i, (label, k) in enumerate(legend):
        y = ly + i * 20
        d.line([(lx, y), (lx + 42, y)], fill=LAYER_COLORS[k], width=6)
        d.text((lx + 50, y - 9), label, fill=(20, 20, 20), font=font)
    d.text((lx, ly + len(legend) * 20), "gris = red pública · trazo grueso = público por horario · triángulo = punto vertical/mirador",
           fill=(20, 20, 20), font=small)
    d.text((lx, ly + len(legend) * 20 + 16), "etiqueta = id + clase de acceso (PUB-H, SRV, PRV, CTL, PROG) · trazado indicativo",
           fill=(20, 20, 20), font=small)
    p3 = Path(out_dir) / "CITY_PLAN_V1_interconexion.png"
    img.save(p3)

    # 2 — programa: edificios semánticos por nodo
    img, d = base_image(f"Mapa F1 (escala Kamurocho) v1.2 — programa: {len(plan['buildings'])} edificios semánticos (G grande · M mediano · P pequeño · C cerrado)")
    fill(d, masses, (205, 190, 172))
    for e in plan["edges"]:
        a, b = nodes[e["a"]], nodes[e["b"]]
        d.line([px(a["x"], a["z"]), px(b["x"], b["z"])], fill=(170, 170, 170), width=3)
    col = {"G": (170, 30, 30), "M": (210, 120, 30), "P": (60, 120, 60), "C": (120, 120, 120)}
    groups = {}
    for bl in plan["buildings"]:
        groups.setdefault(bl["nearNode"], []).append(bl)
    for nid, bls in groups.items():
        n = nodes[nid]
        x, y = px(n["x"], n["z"])
        for i, bl in enumerate(sorted(bls, key=lambda q: "GMPC".index(q["scale"]))):
            cx, cy = x + (i % 4) * 26 - 39, y + (i // 4) * 16 + 10
            d.rectangle([cx, cy, cx + 24, cy + 14], fill=col[bl["scale"]])
            d.text((cx + 2, cy), bl["id"], fill=(255, 255, 255), font=small)
        d.text((x - 39, y - 8), nid, fill=(10, 10, 10), font=small)
    lx, ly = int(px(150, -12)[0]), int(px(150, -12)[1])
    d.rectangle([lx - 10, ly - 18, lx + 520, ly + 110], fill=(250, 248, 242), outline=(120, 120, 120))
    for i, (k, label) in enumerate([("G", "grande (misión, multiestancia)"), ("M", "mediano"), ("P", "pequeño"), ("C", "cerrado (identidad y uso registrados)")]):
        y = ly + i * 20
        d.rectangle([lx, y - 7, lx + 26, y + 7], fill=col[k])
        d.text((lx + 34, y - 9), label, fill=(20, 20, 20), font=font)
    d.text((lx, ly + 84), "agrupados junto a su nodo de referencia; la huella real se dibuja en Fase 0", fill=(20, 20, 20), font=small)
    p2 = Path(out_dir) / "CITY_PLAN_V1_programa.png"
    img.save(p2)

    areas = {"masses_m2": round(masses.area), "streets_m2": round(streets.intersection(land).area), "open_spaces_m2": round(opens.intersection(land).area)}
    return [str(p1), str(p2), str(p3)], areas


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["metrics", "render"])
    ap.add_argument("--plan", default=str(PLAN))
    ap.add_argument("--out")
    ap.add_argument("--out-dir", default=str(PLAN.parent))
    args = ap.parse_args()
    plan = load(args.plan)
    if args.command == "metrics":
        m = metrics(plan)
        text = json.dumps(m, ensure_ascii=False, indent=1)
        if args.out:
            Path(args.out).write_text(text + "\n", encoding="utf-8", newline="\n")
        print(text)
        return 0 if m["all_checks_pass"] else 1
    files, areas = render(plan, args.out_dir)
    print(json.dumps({"files": files, "approx_figure_ground": areas}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

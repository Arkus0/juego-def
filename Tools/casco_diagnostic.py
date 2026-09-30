#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""casco_diagnostic.py — mechanical, read-only diagnostic of the ENV01 CASCO district.

Purpose: a reproducible geometric inventory of the CURRENT casco (plots, neighbours,
distances, residual space and 2-6 plot grouping candidates) as neutral data input for
a future CASCO-V2. This tool NEVER modifies the spec, the trace, the scene or any
product asset. It reads JSON inputs and writes report files into --out only.
Candidates are pure geometry: this tool does not decide any grouping, use or design.

Mechanical sources (C# references of worker/prod-env-01 @ 246756c):
  * placement:    EnvDistrict.BuildRows (EnvDistrict.cs:600-666) — frame at
                  (origin.x, 0, origin.z), yaw = atan2(-dir.z, dir.x) deg; building
                  root local (x0, y, -setback), localScale (w/(bays*2), 1, 1).
  * footprint:    BuildingAssembler.Build — local x in [0, 2*bays] (scaled -> world
                  width == w exactly), z in [-depth, 0], Storey = 3 m.
  * party walls:  EnvStreet.ResolveNeighbours (EnvStreet.cs:29-93) — Covers/Shared
                  rules and row 'ends' kinds. Placed.north is never set true by the
                  current builder, so west = left / east = right for every row.
  * garden walls: EnvDistrict.GardenWall (EnvDistrict.cs:719+) — a thin ~0.6 m strip
                  around frame z = -0.1, approximated here as z in [-0.4, +0.2].
  * street space: Tools/env_district_skeleton.py:229 — street buffer(width/2,
                  cap square, join mitre 2.5); river channel polygon; plaza polygons.
  * basement:     spec basement + EnvDistrict.FootingMargin 0.10 (EnvDistrict.cs:334);
                  river rows clamped to >= 0.45 (EnvDistrict.cs:631); += raise.
  * unit plots:   units.json building spec (EnvDistrict.SpecOf, floors may come from
                  the plot); polish.json per-building overrides (EnvPolish.ApplyPlot).
  * facade cells: FacadeGrammar/BuildingAssembler — front floors*bays, back
                  floors*bays, each side floors*(depth/2) minus hidden party storeys.

Coordinate conventions inside the spec JSON (verified against the generator):
  * rows/plots/streets/river pts are [x, z, y_up] triples (x east, z south-north
    axis, y up) in Unity world metres, domain [[0,0],[196,236]];
  * ground zone vertices are Vector3 lists [x, y_up, z] (different order!);
  * plaza polygons and the river channel are flat [x, z] pair lists.

Every threshold lives in the config file: none of it is product truth.
"""

import argparse
import csv
import hashlib
import json
import math
import os
import sys
from collections import Counter, defaultdict

try:
    from shapely.geometry import LineString, Polygon, box
    from shapely.ops import unary_union
    from shapely.strtree import STRtree
except ImportError:  # pragma: no cover
    sys.exit("BLOCKER: shapely is required (same dependency as Tools/env_district.py).")

STOREY = 3.0            # BuildingAssembler.Storey
FOOTING_MARGIN = 0.10   # EnvDistrict.FootingMargin
WALL_Z0, WALL_Z1 = -0.4, 0.2   # garden-wall strip (module 0.6 deep around z=-0.1)
RIVER_BASEMENT_MIN = 0.45
PARTY_SETBACK_TOL = 0.01       # EnvStreet.Covers setback tolerance
END_HIDDEN = ("hidden", "tip_keep", "tip_cede")  # row ends with no side wall at all


def r3(x):
    return round(float(x), 3)


def rall(v):
    if isinstance(v, (list, tuple)):
        return [rall(x) for x in v]
    if isinstance(v, float):
        return r3(v)
    return v


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_polys(geom):
    """Yield the Polygon members of any shapely geometry."""
    if geom is None or geom.is_empty:
        return
    if geom.geom_type == "Polygon":
        yield geom
    elif geom.geom_type in ("MultiPolygon", "GeometryCollection"):
        for g in geom.geoms:
            if g.geom_type == "Polygon":
                yield g
    # lines/points are ignored by callers that ask for polygons


def poly_coords(geom, simplify_tol=None, decimals=2):
    """External rings of a geometry as rounded coord lists (for debug overlays)."""
    out = []
    for p in iter_polys(geom):
        if simplify_tol:
            p = p.simplify(simplify_tol)
        out.append([[round(x, decimals), round(z, decimals)] for x, z in p.exterior.coords])
    return out


# --------------------------------------------------------------------------- frame math

class Frame:
    """Row frame: exactly the transform EnvDistrict.BuildRows applies (lines 616-617, 642)."""

    def __init__(self, origin, dirv):
        self.ox, self.oz = float(origin[0]), float(origin[1])
        dx, dz = float(dirv[0]), float(dirv[1])
        self.yaw_deg = math.degrees(math.atan2(-dz, dx))
        rad = math.radians(self.yaw_deg)
        self.cos, self.sin = math.cos(rad), math.sin(rad)

    def to_world(self, lx, lz):
        # Unity Quaternion.Euler(0, yaw, 0): +X -> (cos, -sin), +Z -> (sin, cos)
        return (self.ox + lx * self.cos + lz * self.sin,
                self.oz - lx * self.sin + lz * self.cos)

    def to_local(self, wx, wz):
        dx, dz = wx - self.ox, wz - self.oz
        return (dx * self.cos - dz * self.sin, dx * self.sin + dz * self.cos)

    def rect(self, x0, x1, z0, z1):
        pts = [self.to_world(x0, z0), self.to_world(x1, z0),
               self.to_world(x1, z1), self.to_world(x0, z1)]
        return Polygon(pts)


# --------------------------------------------------------------------------- party walls

def shared_storeys(p, o):
    """Port of EnvStreet.Shared (EnvStreet.cs:46-57): storeys of p fully inside o's span."""
    if o is None or o["kind"] != "building":
        return 0
    # Covers(): the neighbour must be at least as deep and on the same building line
    if o["depth"] < p["depth"] or abs(o["setback"] - p["setback"]) >= PARTY_SETBACK_TOL:
        return 0
    bottom = o["y"] - o["basement_eff"] - 0.05
    top = o["y"] + o["floors"] * STOREY + 0.05
    n = 0
    for f in range(p["floors"]):
        if p["y"] + f * STOREY < bottom or p["y"] + (f + 1) * STOREY > top:
            break
        n += 1
    return n


def resolve_row_parties(row_plots, ends):
    """Port of EnvStreet.ResolveNeighbours for party storeys only (north is never
    true in the current builder, so left = west / right = east everywhere).
    row_plots: list of plot records (kind building/wall) in row order; walls act as
    the null gaps of EnvDistrict.BuildRows line 626."""
    west_kind = (ends or {}).get("west", "open") or "open"
    east_kind = (ends or {}).get("east", "open") or "open"
    out = {}
    for i, p in enumerate(row_plots):
        if p["kind"] != "building":
            continue
        west = row_plots[i - 1] if i > 0 else None
        east = row_plots[i + 1] if i < len(row_plots) - 1 else None
        wp = shared_storeys(p, west)
        if west is None and i == 0 and west_kind != "open":
            wp = p["floors"]                      # hidden/tip/concave start (line 58)
        if i == 0 and west is None and west_kind not in ("open", "hidden"):
            wp = p["floors"] if west_kind.startswith("tip") else 0   # lines 65-70
        ep = shared_storeys(p, east)
        if east is None and i == len(row_plots) - 1 and east_kind != "open":
            ep = p["floors"]
        if i == len(row_plots) - 1 and east is None and east_kind not in ("open", "hidden"):
            ep = p["floors"] if east_kind.startswith("tip") else 0
        out[p["id"]] = (wp, ep)
    return out


def side_cells(plot, party):
    """Facade cells of one side wall: storeys f >= party build (depth/2) cells each."""
    return (plot["floors"] - min(party, plot["floors"])) * (plot["depth"] // 2)


def end_party_cells(plot, end_kind):
    """Side cells of the outermost member when the run touches a row end.
    open/concave build the side wall; hidden/tip_* build none (EnvStreet.cs:31-32)."""
    if end_kind in END_HIDDEN or (end_kind or "").startswith("tip"):
        return 0
    return plot["floors"] * (plot["depth"] // 2)


# --------------------------------------------------------------------------- loading

def load_inputs(args):
    spec = json.load(open(args.spec, encoding="utf-8"))
    units = {}
    if args.units and os.path.exists(args.units):
        units = {u["id"]: u for u in json.load(open(args.units, encoding="utf-8")).get("units", [])}
    polish = {}
    if args.polish and os.path.exists(args.polish):
        polish = json.load(open(args.polish, encoding="utf-8")).get("plots") or {}
    cfg = json.load(open(args.config, encoding="utf-8"))
    return spec, units, polish, cfg


def build_records(spec, units, polish, cfg):
    """One record per plot (buildings + garden walls) with world-space geometry."""
    recs = []
    for ri, row in enumerate(spec["rows"]):
        frame = Frame(row["origin"], row["dir"])
        row_plots = []
        for k, p in enumerate(row.get("plots", [])):
            pid = "%s_%d" % (row["id"], k)
            if p.get("wall"):
                rect = frame.rect(float(p["x0"]), float(p["x0"]) + float(p["w"]), WALL_Z0, WALL_Z1)
                rec = {
                    "id": pid, "kind": "wall", "row_id": row["id"], "row_index": ri,
                    "plot_index": k, "street": row.get("street"), "role": row.get("role"),
                    "block": row.get("block"), "x0": float(p["x0"]), "w": float(p["w"]),
                    "tall": bool(p.get("tall")), "thin": bool(p.get("thin")),
                    "gate": p.get("gate"), "ys_count": len(p.get("ys", [])),
                    "frame": frame, "rect": rect,
                    "footprint_m2": round(float(p["w"]) * (WALL_Z1 - WALL_Z0), 3),
                }
            else:
                ubld = units.get(p.get("unit"), {}).get("building", {}) if p.get("unit") else {}
                # SpecOf (EnvDistrict.cs:676-715): unit building fields, plot floors wins
                bays = int(ubld.get("bays", p["bays"]))
                depth = int(ubld.get("depth", p["depth"]))
                floors = int(p.get("floors", ubld.get("floors", 3)))
                ov = polish.get(pid, {})
                floors = int(ov.get("floors", floors))
                raise_m = float(ov.get("raise", 0.0)) or 0.0
                basement = float(p.get("basement", 0.0)) + FOOTING_MARGIN
                if row.get("role") == "river":
                    basement = max(basement, RIVER_BASEMENT_MIN)
                    no_entrance = True
                else:
                    no_entrance = bool(ubld.get("noEntrance", False))
                basement += raise_m                       # EnvDistrict.cs:634
                y = float(p["y"]) + raise_m
                w = float(p["w"])
                setback = float(p.get("setback", 0.0))
                rect = frame.rect(p["x0"], p["x0"] + w, -setback - depth, -setback)
                cx, cz = rect.centroid.x, rect.centroid.y
                rec = {
                    "id": pid, "kind": "building", "row_id": row["id"], "row_index": ri,
                    "plot_index": k, "street": row.get("street"), "role": row.get("role"),
                    "block": row.get("block"),
                    "x0": float(p["x0"]), "w": w, "bays": bays,
                    "scale": w / (bays * 2.0), "depth": depth, "floors": floors,
                    "setback": setback, "y": y, "basement_eff": basement,
                    "type": ubld.get("type", p.get("type")),
                    "real": bool(p.get("real", False)),
                    "unit": p.get("unit"), "landmark": p.get("landmark"),
                    "casona": bool(p.get("casona")), "era": p.get("era"),
                    "corner": p.get("corner"), "feature": p.get("feature"),
                    "interior": ubld.get("interior", ""),
                    "door_override": ubld.get("door", ""),
                    "business": ov.get("business", ubld.get("business", "")),
                    "polish_fields": sorted(k2 for k2 in ov if k2 not in ("unit", "why", "class")),
                    "raise_m": raise_m, "no_entrance": no_entrance,
                    "frame": frame, "rect": rect,
                    "cx": cx, "cz": cz, "yaw_deg": frame.yaw_deg,
                    "footprint_m2": round(w * depth, 3),
                    "front_mid": frame.to_world(p["x0"] + w / 2.0, -setback),
                    "rect_xz": [[r3(x), r3(z)] for x, z in rect.exterior.coords],
                }
            row_plots.append(rec)
            recs.append(rec)
        # party storeys per row (mechanical, mirrors the C# resolver)
        parties = resolve_row_parties(row_plots, row.get("ends"))
        for rec in row_plots:
            if rec["kind"] != "building":
                continue
            pl, pr = parties[rec["id"]]
            rec["party_left"], rec["party_right"] = pl, pr
            rec["cells_front"] = rec["floors"] * rec["bays"]
            rec["cells_back"] = rec["floors"] * rec["bays"]
            rec["cells_side_left"] = side_cells(rec, pl)
            rec["cells_side_right"] = side_cells(rec, pr)
            rec["cells_total"] = (rec["cells_front"] + rec["cells_back"]
                                  + rec["cells_side_left"] + rec["cells_side_right"])
    return recs


# --------------------------------------------------------------------------- neighbours

def compute_neighbours(recs, cfg):
    """Geometric neighbours in world space: same-row left/right, back (other row,
    away from the street), front (other row, across the street). Distances are real
    rect-to-rect distances, never assumed from indices."""
    tol = cfg["heuristics"]["adjacency_tol_m"]
    search = cfg["heuristics"]["neighbor_search_m"]
    geoms = [r["rect"] for r in recs]
    tree = STRtree(geoms)
    for i, r in enumerate(recs):
        cands = tree.query(r["rect"].buffer(search))
        best = {"row_left": None, "row_right": None, "back": None, "front": None}
        touching = []
        for j in cands:
            j = int(j)
            if j == i:
                continue
            o = recs[j]
            d = r["rect"].distance(o["rect"])
            if d <= tol:
                touching.append({"id": o["id"], "kind": o["kind"], "distance_m": r3(d)})
            if d > search:
                continue
            lx, lz = r["frame"].to_local(o["cx"] if o["kind"] == "building" else o["rect"].centroid.x,
                                         o["cz"] if o["kind"] == "building" else o["rect"].centroid.y)
            if o["row_id"] == r["row_id"]:
                side = "row_left" if lx < 0 else "row_right"
            elif lz < -0.5:
                side = "back"
            elif lz > 0.5:
                side = "front"
            else:
                side = "back" if lz <= 0 else "front"   # near-lateral other-row plots
            entry = {"id": o["id"], "kind": o["kind"], "row_id": o["row_id"],
                     "side": side, "distance_m": r3(d)}
            cur = best[side]
            if cur is None or d < cur["distance_m"]:
                best[side] = entry
        if r["kind"] == "building":
            r["neighbors"] = {k: v for k, v in best.items() if v}
            r["contiguous"] = sorted(touching, key=lambda t: t["id"])
            r["contiguous_count"] = len(touching)


# --------------------------------------------------------------------------- classification

def ground_zone_union(spec, zone_keys):
    """Union of ground-zone triangle meshes (v = [x,y,z] vertices, t = flat indices)."""
    tris = []
    ground = spec.get("ground", {})
    for key in zone_keys:
        z = ground.get(key)
        if not z:
            continue
        v = z["v"]
        t = z["t"]
        for a in range(0, len(t), 3):
            i0, i1, i2 = t[a], t[a + 1], t[a + 2]
            tris.append(Polygon([(v[i0][0], v[i0][2]), (v[i1][0], v[i1][2]),
                                 (v[i2][0], v[i2][2])]))
    return unary_union(tris) if tris else Polygon()


def classify_surfaces(spec, recs, cfg):
    """Area classification of the district domain with an explicit priority order.
    Buffers mirror the generator (Tools/env_district_skeleton.py:226-229,662)."""
    cc = cfg["classification"]
    x0, z0 = cc["domain"][0]
    x1, z1 = cc["domain"][1]
    domain = box(min(x0, x1), min(z0, z1), max(x0, x1), max(z0, z1))

    def buf_params(key):
        p = dict(cc[key])
        p.pop("cap_style", None)
        return p

    def xz_line(pts):
        return LineString([(p[0], p[1]) for p in pts])

    street_parts = []
    for s in spec.get("streets", []):
        street_parts.append(xz_line(s["pts"]).buffer(s["width"] / 2.0,
                                                     cap_style=cc["street_buffer"]["cap_style"],
                                                     join_style=cc["street_buffer"]["join_style"],
                                                     mitre_limit=cc["street_buffer"]["mitre_limit"]))
    for s in spec.get("bridges", []) + spec.get("stairs", []):
        street_parts.append(xz_line(s["pts"]).buffer(s["width"] / 2.0,
                                                     cap_style=cc["flat_buffer"]["cap_style"]))
    street = unary_union(street_parts) if street_parts else Polygon()

    plaza = unary_union([Polygon(p["poly"]) for p in spec.get("plazas", [])]) \
        if spec.get("plazas") else Polygon()
    water = Polygon(spec["river"]["channel"]) if spec.get("river", {}).get("channel") else Polygon()
    building = unary_union([r["rect"] for r in recs if r["kind"] == "building"]) \
        if any(r["kind"] == "building" for r in recs) else Polygon()
    wall = unary_union([r["rect"] for r in recs if r["kind"] == "wall"]) \
        if any(r["kind"] == "wall" for r in recs) else Polygon()
    deliberate = ground_zone_union(spec, cc["deliberate_ground_zones"])

    raw = {"building": building, "wall": wall, "street": street, "plaza": plaza,
           "water": water, "deliberate_ground": deliberate}
    remaining = domain
    areas = {}
    for cls in cc["priority"]:
        part = raw[cls].intersection(remaining)
        areas[cls] = part
        remaining = remaining.difference(raw[cls])
    areas["residual"] = remaining

    # raw (pre-priority) areas and interesting overlaps, as diagnostics
    raw_areas = {k: r3(v.area) for k, v in raw.items()}
    overlaps = {
        "street_x_water": r3(street.intersection(water).area),
        "building_x_street": r3(building.intersection(street).area),
        "building_x_water": r3(building.intersection(water).area),
        "building_x_plaza": r3(building.intersection(plaza).area),
        "plaza_x_street": r3(plaza.intersection(street).area),
        "deliberate_x_building": r3(deliberate.intersection(building).area),
    }
    return domain, areas, raw_areas, overlaps, raw


def residual_components(areas, cfg, spec):
    """Residual = unclassified space. Split into components; tag thin near-row slivers
    that look like unbuilt frontage (heuristic, config-gated)."""
    res = areas["residual"]
    min_area = cfg["heuristics"]["residual_min_area_m2"]
    rows_by_id = {r["id"]: r for r in spec["rows"]}
    comps = []
    total = 0.0
    for g in iter_polys(res):
        a = g.area
        total += a
        if a < 0.05:
            continue
        c = g.centroid
        tag = None
        for rid, row in rows_by_id.items():
            f = Frame(row["origin"], row["dir"])
            lx, lz = f.to_local(c.x, c.y)
            if 0.0 <= lx <= row["length"] and abs(lz) < 2.0 and a < 25.0:
                tag = rid
                break
        comps.append({
            "area_m2": r3(a), "centroid": [r3(c.x), r3(c.y)],
            "bbox": [r3(v) for v in g.bounds],
            "near_row": tag,
            "negligible": a < min_area,
        })
    comps.sort(key=lambda c: (-c["area_m2"], c["centroid"]))
    return comps, r3(total)


def row_unbuilt_spans(spec):
    """Per row: plot coverage + filler vs row length (the generator's own bookkeeping).
    Uncovered spans are unbuilt frontage — data, not an error."""
    out = []
    for row in spec["rows"]:
        plots = row.get("plots", [])
        covered = sum(float(p.get("w", 0.0)) for p in plots)
        f = row.get("filler") or []
        fs = (f[1] - f[0]) if isinstance(f, (list, tuple)) and len(f) == 2 else 0.0
        unbuilt = row["length"] - covered - fs
        if unbuilt > 0.05:
            out.append({"row_id": row["id"], "street": row.get("street"),
                        "role": row.get("role"), "length_m": r3(row["length"]),
                        "plots_w_m": r3(covered), "filler_m": r3(fs),
                        "unbuilt_m": r3(unbuilt)})
    return out


# --------------------------------------------------------------------------- candidates

def enumerate_candidates(recs, recs_by_row, spec, cfg, residual_geom, classify_geoms):
    """All contiguous same-row runs of 2..6 buildings (no wall/gap inside).
    Pure geometry per candidate; no grouping is preferred or recommended here."""
    h = cfg["heuristics"]
    sizes = h["candidate_sizes"]
    tol = h["adjacency_tol_m"]
    absorb = h["absorb_buffer_m"]
    back_clear = h["back_clearance_m"]
    all_rects = [(r, r["rect"]) for r in recs if r["kind"] == "building"]
    cls_geoms = {"street": classify_geoms["street"], "plaza": classify_geoms["plaza"],
                 "water": classify_geoms["water"]}
    cands = []
    for row in spec["rows"]:
        row_recs = recs_by_row.get(row["id"], [])
        # maximal runs of geometrically contiguous buildings; walls and x-gaps break
        # a run. left_ctx tracks what stands immediately left of the run being built:
        # ("row_start", None) | ("wall", rec) | ("gap", rec) — mirrors EnvStreet's
        # null-entry semantics (a wall is a gap: the side wall stays exposed).
        runs, cur, left_ctx = [], [], ("row_start", None)
        for rec in row_recs:
            if rec["kind"] != "building":
                if cur:
                    runs.append((cur, left_ctx, ("wall", rec)))
                    cur = []
                left_ctx = ("wall", rec)
                continue
            if cur and abs(rec["x0"] - (cur[-1]["x0"] + cur[-1]["w"])) > tol:
                runs.append((cur, left_ctx, ("gap", rec)))
                cur = []
                left_ctx = ("gap", rec)
            cur.append(rec)
        if cur:
            runs.append((cur, left_ctx, ("row_end", None)))
        ends = row.get("ends") or {}
        for run, lctx, rctx in runs:
            for size in sizes:
                if size > len(run):
                    continue
                for s in range(0, len(run) - size + 1):
                    members = run[s:s + size]
                    left = lctx if s == 0 else ("building", run[s - 1])
                    right = rctx if s + size == len(run) else ("building", run[s + size])
                    cands.append(make_candidate(row, members, left, right, ends,
                                                all_rects, residual_geom, absorb,
                                                back_clear, tol, cls_geoms))
    return cands


def ctx_side_cells(plot, ctx, end_kind):
    """Side cells of an outermost member given what stands beyond the run:
    a building neighbour hides Shared() storeys; a wall/gap exposes the side
    (EnvStreet west==null && i>0); a row end follows the ends kind."""
    kind, rec = ctx
    if kind == "building":
        return side_cells(plot, shared_storeys(plot, rec))
    if kind in ("wall", "gap"):
        return plot["floors"] * (plot["depth"] // 2)
    return end_party_cells(plot, end_kind)


def make_candidate(row, members, left_ctx, right_ctx, ends, all_rects, residual_geom,
                   absorb, back_clear, tol, cls_geoms):
    size = len(members)
    mid = "%s_%02d_%d" % (members[0]["row_id"], members[0]["plot_index"], size)
    union = unary_union([m["rect"] for m in members])
    hull = union.convex_hull
    front = sum(m["cells_front"] for m in members)
    back = sum(m["cells_back"] for m in members)
    # side walls that survive a hypothetical merge: only the two outer ends
    left_cells = ctx_side_cells(members[0], left_ctx, ends.get("west"))
    right_cells = ctx_side_cells(members[-1], right_ctx, ends.get("east"))
    sides = left_cells + right_cells
    current_total = sum(m["cells_total"] for m in members)

    # back clearance vs buildings of other rows (local z < 0 of this row's frame)
    f = members[0]["frame"]
    back_min, back_id = None, None
    for other, orect in all_rects:
        if other["row_id"] == row["id"] or other["id"] in {m["id"] for m in members}:
            continue
        lx, lz = f.to_local(other["cx"], other["cz"])
        if lz > -0.5:
            continue
        d = union.distance(orect)
        if back_min is None or d < back_min:
            back_min, back_id = d, other["id"]
    if back_min is None:
        back_flag = "none_within_district"
    elif back_min <= tol:
        back_flag = "back_touching"
    elif back_min < back_clear:
        back_flag = "back_gap_lt_clearance"
    else:
        back_flag = "clear"

    # residual area that a merged parcel could potentially absorb (data only)
    absorbable = residual_geom.intersection(union.buffer(absorb)).area \
        if not residual_geom.is_empty else 0.0

    return {
        "id": mid, "row_id": row["id"], "street": row.get("street"),
        "role": row.get("role"), "block": row.get("block"), "size": size,
        "member_ids": [m["id"] for m in members],
        "frontage_combined_m": r3(sum(m["w"] for m in members)),
        "depth_min_m": min(m["depth"] for m in members),
        "depth_max_m": max(m["depth"] for m in members),
        "setback_min_m": r3(min(m["setback"] for m in members)),
        "setback_max_m": r3(max(m["setback"] for m in members)),
        "floors_min": min(m["floors"] for m in members),
        "floors_max": max(m["floors"] for m in members),
        "footprint_sum_m2": r3(sum(m["footprint_m2"] for m in members)),
        "union_area_m2": r3(union.area),
        "hull_area_m2": r3(hull.area),
        "hull_xz": [[r3(x), r3(z)] for x, z in hull.exterior.coords],
        "cells_front": front, "cells_back": back,
        "cells_sides_preservable": sides,
        "cells_total_preservable": front + back + sides,
        "cells_total_current": current_total,
        "entrances_assumed": sum(1 for m in members if not m["no_entrance"]),
        "n_no_entrance": sum(1 for m in members if m["no_entrance"]),
        "n_interior_programmed": sum(1 for m in members if m["interior"]),
        "n_corner_chamfer": sum(1 for m in members if m["corner"]),
        "n_unit": sum(1 for m in members if m["unit"]),
        "residual_absorbable_m2": r3(absorbable),
        "street_overlap_m2": r3(union.intersection(cls_geoms["street"]).area),
        "plaza_overlap_m2": r3(union.intersection(cls_geoms["plaza"]).area),
        "water_overlap_m2": r3(union.intersection(cls_geoms["water"]).area),
        "back_min_dist_m": r3(back_min) if back_min is not None else None,
        "back_neighbor_id": back_id, "back_flag": back_flag,
        "landmark_ids": [m["id"] for m in members if m["landmark"]],
        "unit_ids": [m["id"] for m in members if m["unit"]],
        "n_small_members": sum(1 for m in members
                               if m.get("flag_small_footprint") or m.get("flag_below_min_frontage")),
        "n_narrow_members": sum(1 for m in members if m.get("flag_narrow")),
        "end_left_kind": left_ctx[0] if left_ctx[0] != "row_start"
                         else "row_end:" + (ends.get("west") or "open"),
        "end_right_kind": right_ctx[0] if right_ctx[0] != "row_end"
                          else "row_end:" + (ends.get("east") or "open"),
    }


# --------------------------------------------------------------------------- stats

def hist(values, edges):
    """Counts per bin; the LAST bin is open-ended (values >= last edge)."""
    counts = []
    for i in range(len(edges) - 1):
        lo = edges[i]
        if i == len(edges) - 2:
            counts.append(sum(1 for v in values if v >= lo))
        else:
            counts.append(sum(1 for v in values if lo <= v < edges[i + 1]))
    return counts


def pct(values, q):
    if not values:
        return None
    vs = sorted(values)
    idx = min(int(round(q * (len(vs) - 1))), len(vs) - 1)
    return r3(vs[idx])


def distribution(values, edges, unit):
    return {
        "unit": unit, "n": len(values), "edges": edges, "counts": hist(values, edges),
        "min": r3(min(values)) if values else None,
        "p10": pct(values, 0.10), "p50": pct(values, 0.50), "p90": pct(values, 0.90),
        "max": r3(max(values)) if values else None,
        "mean": r3(sum(values) / len(values)) if values else None,
    }


def make_stats(spec, recs, cands, areas, domain, cfg, overlaps, raw_areas):
    blds = [r for r in recs if r["kind"] == "building"]
    walls = [r for r in recs if r["kind"] == "wall"]
    widths = [r["w"] for r in blds]
    foots = [r["footprint_m2"] for r in blds]
    depths = [r["depth"] for r in blds]
    floors = [r["floors"] for r in blds]
    bays = [r["bays"] for r in blds]
    front_d = [r["neighbors"]["front"]["distance_m"] for r in blds if r.get("neighbors", {}).get("front")]
    back_d = [r["neighbors"]["back"]["distance_m"] for r in blds if r.get("neighbors", {}).get("back")]
    area_cls = {k: r3(v.area) for k, v in areas.items()}
    domain_area = r3(domain.area)
    by_street = defaultdict(lambda: {"buildings": 0, "walls": 0, "frontage_m": 0.0})
    for r in recs:
        e = by_street[r["street"] or "?"]
        if r["kind"] == "building":
            e["buildings"] += 1
            e["frontage_m"] += r["w"]
        else:
            e["walls"] += 1
    return {
        "counts": {
            "rows": len(spec["rows"]),
            "rows_by_role": dict(Counter(r.get("role") for r in spec["rows"])),
            "plots_total": len(recs),
            "buildings": len(blds),
            "walls": len(walls),
            "unit_plots": sum(1 for r in blds if r["unit"]),
            "landmarks": sum(1 for r in blds if r["landmark"]),
            "casonas": sum(1 for r in blds if r["casona"]),
            "not_real_osm": sum(1 for r in blds if not r["real"]),
            "polished_plots": sum(1 for r in blds if r.get("polish_fields")),
            "spec_report_block": spec.get("report", {}),
        },
        "distributions": {
            "width_m": distribution(widths, cfg["bins"]["width_edges_m"], "m"),
            "footprint_m2": distribution(foots, cfg["bins"]["footprint_edges_m2"], "m2"),
            "depth_m": {"counts": {str(d): depths.count(d) for d in sorted(set(depths))}},
            "floors": {"counts": {str(fl): floors.count(fl) for fl in sorted(set(floors))}},
            "bays": {"counts": {str(b): bays.count(b) for b in sorted(set(bays))}},
            "front_across_distance_m": distribution(front_d, cfg["bins"]["front_distance_edges_m"], "m"),
            "back_distance_m_raw": {
                "n": len(back_d), "min": r3(min(back_d)) if back_d else None,
                "p50": pct(back_d, 0.5), "max": r3(max(back_d)) if back_d else None,
                "n_touching_or_lt_1m": sum(1 for d in back_d if d <= 1.0),
            },
            "candidate_frontage_m": distribution([c["frontage_combined_m"] for c in cands],
                                                 cfg["bins"]["candidate_frontage_edges_m"], "m"),
        },
        "heuristics_tally": {
            "small_footprint": sum(1 for r in blds if r.get("flag_small_footprint")),
            "below_min_frontage": sum(1 for r in blds if r.get("flag_below_min_frontage")),
            "narrow": sum(1 for r in blds if r.get("flag_narrow")),
            "footprint_sum_m2": r3(sum(foots)),
        },
        "candidates": {
            "total": len(cands),
            "by_size": {str(s): sum(1 for c in cands if c["size"] == s)
                        for s in cfg["heuristics"]["candidate_sizes"]},
            "back_flags": dict(Counter(c["back_flag"] for c in cands)),
            "with_below_minimum_member": sum(1 for c in cands if c["n_small_members"] > 0),
            "with_narrow_member": sum(1 for c in cands if c["n_narrow_members"] > 0),
            "with_landmark": sum(1 for c in cands if c["landmark_ids"]),
        },
        "surface_classification": {
            "domain_area_m2": domain_area,
            "deliberate_note": "deliberate_ground = clasificado intencionalmente por el generador (zonas taggeadas yard/huerta). NO implica validacion de uso, tamano o valor para CASCO-V2; el 46% no debe preservarse automaticamente por llevar esta etiqueta.",
            "priority": cfg["classification"]["priority"],
            "areas_m2": area_cls,
            "areas_pct": {k: r3(100.0 * v / domain_area) for k, v in area_cls.items()},
            "raw_areas_m2": raw_areas,
            "overlaps_m2": overlaps,
        },
        "by_street": {k: {"buildings": v["buildings"], "walls": v["walls"],
                          "frontage_m": r3(v["frontage_m"])}
                      for k, v in sorted(by_street.items())},
        "by_block": {str(b): {"buildings": n} for b, n in sorted(Counter(
            r["block"] for r in blds).items())},
    }


# --------------------------------------------------------------------------- checks

def run_checks(spec, recs, areas, domain, cfg, cands):
    tol = cfg["heuristics"]["adjacency_tol_m"]
    cov_tol = cfg["classification"]["coverage_tolerance_m2"]
    blds = [r for r in recs if r["kind"] == "building"]
    walls = [r for r in recs if r["kind"] == "wall"]
    rep = spec.get("report", {})

    # rect area equals w*depth (rect construction is exact; catch rotation mistakes)
    bad_area = [r["id"] for r in blds
                if abs(r["rect"].area - r["w"] * r["depth"]) > 0.01]

    # consecutive same-row building pairs must touch (generator advances x by w)
    by_row = defaultdict(list)
    for r in recs:
        by_row[r["row_id"]].append(r)
    sep_pairs = []
    for rid, rr in by_row.items():
        for a, b in zip(rr, rr[1:]):
            if a["kind"] == "building" and b["kind"] == "building":
                d = a["rect"].distance(b["rect"])
                if d > tol:
                    sep_pairs.append({"row": rid, "a": a["id"], "b": b["id"], "distance_m": r3(d)})

    total_classified = sum(v.area for v in areas.values())
    cov_ok = abs(total_classified - domain.area) <= cov_tol

    return {
        "rows_count": {"spec_report": rep.get("rows"), "array": len(spec["rows"]),
                       "note": "report.rows cuenta filas construidas; el array tiene mas (roles puente/pasarela etc.)"},
        "buildings_count": {"spec_report": rep.get("plots"), "actual": len(blds),
                            "ok": rep.get("plots") == len(blds)},
        "walls_count": {"spec_report": rep.get("walls"), "actual": len(walls),
                        "ok": rep.get("walls") == len(walls)},
        "rect_area_equals_w_times_depth": {"violations": bad_area, "ok": not bad_area},
        "same_row_consecutive_touch": {"violations": sep_pairs, "ok": not sep_pairs},
        "classification_coverage": {
            "sum_all_classes_m2": r3(total_classified), "domain_m2": r3(domain.area),
            "abs_error_m2": r3(abs(total_classified - domain.area)), "tolerance_m2": cov_tol,
            "ok": cov_ok},
        "candidates_enumerated": len(cands),
    }


# --------------------------------------------------------------------------- flags

def apply_flags(recs, cfg):
    h = cfg["heuristics"]
    for r in recs:
        if r["kind"] != "building":
            continue
        r["flag_small_footprint"] = r["footprint_m2"] < h["min_interior_footprint_m2"]
        r["flag_below_min_frontage"] = r["w"] < h["min_interior_frontage_m"]
        r["flag_narrow"] = r["w"] <= h["narrow_plot_max_w_m"]


# --------------------------------------------------------------------------- outputs

def write_outputs(args, spec, recs, cands, areas, domain, cfg, stats, checks,
                  residual_comps, residual_total, unbuilt, inputs_meta):
    out = args.out
    os.makedirs(out, exist_ok=True)
    do = cfg["debug_overlay"]

    def neighbor_str(r, side):
        n = r.get("neighbors", {}).get(side)
        return "%s:%s" % (n["id"], n["distance_m"]) if n else ""

    plots_csv = os.path.join(out, "plots.csv")
    with open(plots_csv, "w", newline="", encoding="utf-8") as f:
        wtr = csv.writer(f, lineterminator="\n")
        wtr.writerow(["id", "kind", "row", "street", "role", "block", "plot_index",
                      "x0_m", "w_m", "bays", "scale", "depth_m", "floors", "setback_m",
                      "y_m", "basement_eff_m", "type", "real_osm", "unit", "landmark",
                      "casona", "era", "corner", "interior", "no_entrance", "door_override",
                      "business", "raise_m", "footprint_m2", "world_cx", "world_cz",
                      "yaw_deg", "front_mid_x", "front_mid_z", "party_left", "party_right",
                      "cells_front", "cells_back", "cells_side_left", "cells_side_right",
                      "cells_total", "flag_small_footprint", "flag_below_min_frontage",
                      "flag_narrow", "neighbor_left", "neighbor_right", "neighbor_back",
                      "neighbor_front", "contiguous_count"])
        for r in recs:
            fm = r.get("front_mid", (None, None))
            wtr.writerow([
                r["id"], r["kind"], r["row_id"], r["street"] or "", r["role"] or "",
                r["block"], r["plot_index"],
                r3(r["x0"]), r3(r["w"]), r.get("bays", ""), r3(r["scale"]) if r.get("scale") is not None else "",
                r.get("depth", ""), r.get("floors", ""), r3(r.get("setback", 0.0)),
                r3(r.get("y", 0.0)), r3(r.get("basement_eff", 0.0)),
                r.get("type", ""), int(r.get("real", False)), r.get("unit") or "",
                r.get("landmark") or "", int(r.get("casona", False)), r.get("era") or "",
                r.get("corner") or "", r.get("interior", ""), int(r.get("no_entrance", False)),
                r.get("door_override", ""), r.get("business", ""), r3(r.get("raise_m", 0.0)),
                r.get("footprint_m2", ""), r3(r["cx"]) if r.get("cx") is not None else "",
                r3(r["cz"]) if r.get("cz") is not None else "",
                r3(r["yaw_deg"]) if r.get("yaw_deg") is not None else "",
                r3(fm[0]) if fm[0] is not None else "", r3(fm[1]) if fm[1] is not None else "",
                r.get("party_left", ""), r.get("party_right", ""),
                r.get("cells_front", ""), r.get("cells_back", ""),
                r.get("cells_side_left", ""), r.get("cells_side_right", ""),
                r.get("cells_total", ""),
                int(r.get("flag_small_footprint", False)),
                int(r.get("flag_below_min_frontage", False)),
                int(r.get("flag_narrow", False)),
                neighbor_str(r, "row_left"), neighbor_str(r, "row_right"),
                neighbor_str(r, "back"), neighbor_str(r, "front"),
                r.get("contiguous_count", ""),
            ])

    cands_csv = os.path.join(out, "candidates.csv")
    with open(cands_csv, "w", newline="", encoding="utf-8") as f:
        wtr = csv.writer(f, lineterminator="\n")
        cols = ["id", "row", "street", "role", "block", "size", "member_ids",
                "frontage_combined_m", "depth_min_m", "depth_max_m", "setback_min_m",
                "setback_max_m", "floors_min", "floors_max", "footprint_sum_m2",
                "union_area_m2", "hull_area_m2", "cells_front", "cells_back",
                "cells_sides_preservable", "cells_total_preservable", "cells_total_current",
                "entrances_assumed", "n_no_entrance", "n_interior_programmed",
                "n_corner_chamfer", "n_unit", "residual_absorbable_m2", "street_overlap_m2", "plaza_overlap_m2",
                "water_overlap_m2", "back_min_dist_m",
                "back_neighbor_id", "back_flag", "n_small_members", "n_narrow_members",
                "landmark_ids", "unit_ids", "end_left_kind", "end_right_kind"]
        wtr.writerow(cols)
        for c in cands:
            wtr.writerow([
                c["id"], c["row_id"], c["street"] or "", c["role"] or "", c["block"],
                c["size"], "|".join(c["member_ids"]), c["frontage_combined_m"],
                c["depth_min_m"], c["depth_max_m"], c["setback_min_m"], c["setback_max_m"],
                c["floors_min"], c["floors_max"], c["footprint_sum_m2"], c["union_area_m2"],
                c["hull_area_m2"], c["cells_front"], c["cells_back"],
                c["cells_sides_preservable"], c["cells_total_preservable"],
                c["cells_total_current"], c["entrances_assumed"], c["n_no_entrance"],
                c["n_interior_programmed"], c["n_corner_chamfer"], c["n_unit"],
                c["residual_absorbable_m2"], c["street_overlap_m2"], c["plaza_overlap_m2"],
                c["water_overlap_m2"], c["back_min_dist_m"] if c["back_min_dist_m"] is not None else "",
                c["back_neighbor_id"] or "", c["back_flag"], c["n_small_members"],
                c["n_narrow_members"], "|".join(c["landmark_ids"]), "|".join(c["unit_ids"]),
                c["end_left_kind"], c["end_right_kind"],
            ])

    # debug-overlay polygons (kept small: simplified, area-filtered)
    residual_geom = areas["residual"]
    deliberate_geom = areas["deliberate_ground"]
    overlay = {
        "residual_polys": [],
        "deliberate_polys": poly_coords(deliberate_geom, do["simplify_tol_m"]),
        "street_ribbons": [{"id": s["id"], "width": s["width"],
                            "pts": [[r3(p[0]), r3(p[1]), r3(p[2]) if len(p) > 2 else 0.0]
                                    for p in s["pts"]]} for s in spec.get("streets", [])],
        "plazas": [{"id": p["id"], "y": p.get("y", 0.0),
                    "poly": [[r3(x), r3(z)] for x, z in p["poly"]]}
                   for p in spec.get("plazas", [])],
        "water_poly": poly_coords(areas["water"], do["simplify_tol_m"]),
        "water_y": spec.get("river", {}).get("water", -3.0),
    }
    for g in iter_polys(residual_geom):
        if g.area >= do["residual_min_area_m2"]:
            overlay["residual_polys"].append(
                {"area_m2": r3(g.area),
                 "coords": [[round(x, 2), round(z, 2)]
                            for x, z in g.simplify(do["simplify_tol_m"]).exterior.coords]})
    overlay["residual_polys"].sort(key=lambda p: (-p["area_m2"], p["coords"][0]))

    doc = {
        "tool": "Tools/casco_diagnostic.py",
        "purpose": "diagnostico mecanico read-only del CASCO ENV01; input para CASCO-V2. Los candidatos son solo datos geometricos; ninguna agrupacion esta recomendada ni elegida.",
        "inputs": inputs_meta,
        "config_used": cfg,
        "constants": {
            "storey_m": STOREY, "footing_margin_m": FOOTING_MARGIN,
            "river_basement_min_m": RIVER_BASEMENT_MIN,
            "wall_strip_local_z": [WALL_Z0, WALL_Z1],
            "placed_north_note": "Placed.north nunca se asigna en el builder actual (EnvDistrict grep); left=west/right=east en todas las filas.",
            "facade_cell_formula": "front=floors*bays; back=floors*bays; side=(floors-party)*(depth/2) por lado; party por EnvStreet.Shared portado",
        },
        "stats": stats,
        "checks": checks,
        "rows_unbuilt_spans": unbuilt,
        "residual": {"total_area_m2": residual_total,
                     "components_over_0p05": residual_comps},
        "plots": [plot_public(r) for r in recs],
        "candidates": cands,
        "debug_overlay": overlay,
        "ambiguities": [
            "A1: no existe umbral autoritativo de 'interior jugable'; min_interior_footprint_m2 y min_interior_frontage_m son heuristicas del config.",
            "A2: zonas ground outer/strip/lane/core/plaza se asumen pavimento bajo calle/plaza (no clase propia); solo yard/huerta son 'ground deliberado'.",
            "A3: report.rows=161 vs 164 filas del array (el report cuenta filas construidas); el diagnostico cuenta el array.",
            "A4: contiguidad espalda-con-espalda entre filas opuestas se registra como neighbor back, pero los candidatos son solo same-row ('frontage combinado').",
            "A5: los 35 muros de jardin se inventarian pero se excluyen de candidatos.",
            "A6: tramos de fila sin plots ni filler ('unbuilt spans') se reportan como dato y caen en residual.",
            "A7: 'entrances_assumed' deriva de noEntrance (filas rio); el resto de edificios se asume con portal por diseno del grammar, sin ejecutar el grammar.",
        ],
    }

    def dump_roundtrip(obj):
        return json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False,
                          default=float) + "\n"

    with open(os.path.join(out, "casco_diagnostic.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(dump_roundtrip(doc))
    with open(os.path.join(out, "stats.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(dump_roundtrip({"stats": stats, "checks": checks,
                                "residual_total_m2": residual_total}))
    return doc


def plot_public(r):
    """Plot record without heavy/private fields (shapely objects, frame)."""
    if r["kind"] == "wall":
        return {"id": r["id"], "kind": "wall", "row_id": r["row_id"], "street": r["street"],
                "role": r["role"], "block": r["block"], "x0": r3(r["x0"]), "w": r3(r["w"]),
                "tall": r["tall"], "thin": r["thin"], "gate": r["gate"],
                "footprint_m2": r["footprint_m2"],
                "rect_xz": [[r3(x), r3(z)] for x, z in r["rect"].exterior.coords]}
    d = {k: v for k, v in r.items()
         if k not in ("frame", "rect", "contiguous")}
    d["x0"] = r3(d["x0"]); d["w"] = r3(d["w"]); d["scale"] = r3(d["scale"])
    d["y"] = r3(d["y"]); d["basement_eff"] = r3(d["basement_eff"])
    d["cx"] = r3(d["cx"]); d["cz"] = r3(d["cz"]); d["yaw_deg"] = r3(d["yaw_deg"])
    d["front_mid"] = [r3(v) for v in d["front_mid"]]
    d["contiguous_ids"] = sorted(t["id"] for t in r["contiguous"])
    return d


# --------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--spec", default="Unity/JuegoDef/Assets/JuegoDef/Env/Specs/districts/ENV01_Casco_District.json")
    ap.add_argument("--units", default="Unity/JuegoDef/Assets/JuegoDef/Env/Specs/units.json")
    ap.add_argument("--polish", default="Unity/JuegoDef/Assets/JuegoDef/Env/Specs/districts/ENV01_Casco_District.polish.json")
    ap.add_argument("--config", default="Tools/casco_diagnostic.config.json")
    ap.add_argument("--out", default="Docs/evidence/CASCO-V2-DIAG")
    args = ap.parse_args()

    spec, units, polish, cfg = load_inputs(args)
    recs = build_records(spec, units, polish, cfg)
    apply_flags(recs, cfg)
    compute_neighbours(recs, cfg)
    domain, areas, raw_areas, overlaps, raw_geoms = classify_surfaces(spec, recs, cfg)
    residual_comps, residual_total = residual_components(areas, cfg, spec)
    unbuilt = row_unbuilt_spans(spec)
    recs_by_row = defaultdict(list)
    for r in recs:
        recs_by_row[r["row_id"]].append(r)
    cands = enumerate_candidates(recs, recs_by_row, spec, cfg, areas["residual"], raw_geoms)
    stats = make_stats(spec, recs, cands, areas, domain, cfg, overlaps, raw_areas)
    checks = run_checks(spec, recs, areas, domain, cfg, cands)

    inputs_meta = {
        "spec": {"path": args.spec, "sha256": sha256_of(args.spec)},
        "units": {"path": args.units, "sha256": sha256_of(args.units)},
        "polish": {"path": args.polish, "sha256": sha256_of(args.polish)},
        "config": {"path": args.config, "sha256": sha256_of(args.config)},
        "tool": {"path": __file__, "sha256": sha256_of(os.path.abspath(__file__))},
        "env": {"python": sys.version.split()[0]},
    }
    try:
        import shapely
        inputs_meta["env"]["shapely"] = shapely.__version__
    except Exception:
        pass

    doc = write_outputs(args, spec, recs, cands, areas, domain, cfg, stats, checks,
                        residual_comps, residual_total, unbuilt, inputs_meta)

    b = stats["counts"]; s = stats["surface_classification"]["areas_m2"]
    print("CASCO diagnostic: rows=%d buildings=%d walls=%d candidates=%d" %
          (b["rows"], b["buildings"], b["walls"], stats["candidates"]["total"]))
    print("areas m2: " + ", ".join("%s=%.1f" % (k, v) for k, v in sorted(s.items())))
    print("checks ok:", all(v.get("ok", True) for v in checks.values() if isinstance(v, dict)))
    for k, v in checks.items():
        if isinstance(v, dict) and v.get("ok") is False:
            print("  CHECK FAIL:", k, json.dumps(v)[:400])
    print("out ->", args.out)


if __name__ == "__main__":
    main()

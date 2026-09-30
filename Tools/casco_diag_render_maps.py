#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""casco_diag_render_maps.py — deterministic top-down inspection maps rendered from
Docs/evidence/CASCO-V2-DIAG/casco_diagnostic.json: the SAME data the Unity overlay
(EnvCascoDiag) draws, rasterised with Pillow so the visual inspection does not depend
on an open Unity editor.

Read-only: reads the JSON, writes PNGs into --out (default .../captures/).
These are DATA renders, not Unity SceneView captures; the SceneView pass remains in
RUNBOOK_OVERLAY.md. No grouping is chosen and nothing is validated for CASCO-V2 here:
green means "above the current provisional minimum heuristic", nothing more.
"""

import argparse
import json
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import LineString

PX_PER_M = 7          # output scale (supersampled x2 while drawing)
DOMAIN = (0.0, 0.0, 196.0, 236.0)
SS = 2                # supersample factor

# palette (mirrors the Unity overlay; pastel context so flags pop)
STREET = (222, 222, 218)
PLAZA = (207, 235, 220)
WATER = (188, 212, 245)
DELIB = (127, 212, 232)
BUILDING_CTX = (226, 226, 224)
GREEN = (168, 220, 174)
RED = (230, 57, 43)
AMBER = (243, 153, 26)
RESID = (255, 216, 61)
RESID_EDGE = (184, 134, 11)
CAND = (42, 95, 208)
INK = (30, 30, 30)
WALL = (150, 150, 150)


def load_font(size):
    for name in ("consola.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(os.path.join(os.environ.get("WINDIR", "C:\\Windows"),
                                                   "Fonts", name), size)
        except Exception:
            continue
    return ImageFont.load_default()


class Map:
    def __init__(self, title, subtitle=""):
        self.sub_lines = textwrap.wrap(subtitle, 100) if subtitle else []
        w = int((DOMAIN[2] - DOMAIN[0]) * PX_PER_M * SS) + 160 * SS
        header = 46 + 17 * len(self.sub_lines)
        h = int((DOMAIN[3] - DOMAIN[1]) * PX_PER_M * SS) + header * SS + 40 * SS
        self.im = Image.new("RGB", (w, h), "white")
        self.d = ImageDraw.Draw(self.im)
        self.off_x = 70 * SS
        self.off_y = (header + 6) * SS
        self.title = title
        self.subtitle = subtitle

    def px(self, x, z):
        return (self.off_x + (x - DOMAIN[0]) * PX_PER_M * SS,
                self.off_y + (DOMAIN[3] - z) * PX_PER_M * SS)

    def poly(self, coords, fill=None, outline=None, width=1):
        pts = [self.px(x, z) for x, z in coords]
        if len(pts) > 2:
            self.d.polygon(pts, fill=fill, outline=outline, width=width * SS)

    def line(self, coords, color, width):
        pts = [self.px(x, z) for x, z in coords]
        self.d.line(pts, fill=color, width=width * SS, joint="curve")

    def label(self, x, z, text, size=13, color=INK, anchor="mm", bold=False):
        f = load_font(size * SS)
        self.d.text(self.px(x, z), text, font=f, fill=color, anchor=anchor)

    def frame(self):
        x0, z0 = self.px(DOMAIN[0], DOMAIN[3])
        x1, z1 = self.px(DOMAIN[2], DOMAIN[0])
        # clip every layer to the classification domain (the tool classifies only
        # inside [[0,0],[196,236]]; buffers bleeding past it are not data)
        W, H = self.im.size
        self.d.rectangle([0, 0, W - 1, z0 - 1], fill="white")
        self.d.rectangle([0, z1 + 1, W - 1, H - 1], fill="white")
        self.d.rectangle([0, z0, x0 - 1, z1], fill="white")
        self.d.rectangle([x1 + 1, z0, W - 1, z1], fill="white")
        self.d.rectangle([x0, z0, x1, z1], outline=INK, width=SS)
        f = load_font(20 * SS)
        self.d.text((self.off_x, 18 * SS), self.title, font=f, fill=INK)
        f2 = load_font(12 * SS)
        for i, line in enumerate(self.sub_lines):
            self.d.text((self.off_x, (42 + 17 * i) * SS), line, font=f2, fill=(90, 90, 90))
        # scale bar: 20 m
        sx0, sz = self.px(DOMAIN[2] - 45, DOMAIN[1] + 6)
        sx1, _ = self.px(DOMAIN[2] - 25, DOMAIN[1] + 6)
        self.d.line([sx0, sz, sx1, sz], fill=INK, width=2 * SS)
        self.d.text(((sx0 + sx1) // 2, sz - 12 * SS), "20 m", font=f2, fill=INK,
                    anchor="mm")

    def save(self, path):
        im = self.im.resize((self.im.width // SS, self.im.height // SS),
                            Image.LANCZOS)
        im.save(path, "PNG")
        return path


def ring(coords):
    return coords[:-1] if coords[0] == coords[-1] else list(coords)


def street_polys(ov):
    out = []
    for s in ov.get("street_ribbons", []):
        pts = [(p[0], p[1]) for p in s["pts"]]
        if len(pts) >= 2:
            out.append(LineString(pts).buffer(s["width"] / 2.0,
                                              cap_style="round", join_style="round"))
    return out


def draw_context(m, doc, with_deliberate=True):
    ov = doc["debug_overlay"]
    for g in street_polys(ov):
        for poly in ([g] if g.geom_type == "Polygon" else g.geoms):
            m.poly(poly.exterior.coords, fill=STREET)
    if with_deliberate:
        for p in ov.get("deliberate_polys", []):
            m.poly(p, fill=DELIB)
    for p in ov.get("plazas", []):
        m.poly([tuple(c) for c in p["poly"]], fill=PLAZA)
    for p in ov.get("water_poly", []):
        m.poly(p, fill=WATER)


def draw_plots(m, plots, ctx_color=BUILDING_CTX, green=True):
    for p in plots:
        if p["kind"] != "building":
            m.line(ring(p["rect_xz"]), WALL, 1)
            continue
        if p.get("flag_small_footprint") or p.get("flag_below_min_frontage"):
            c = RED
        elif p.get("flag_narrow"):
            c = AMBER
        else:
            c = GREEN if green else ctx_color
        m.poly(ring(p["rect_xz"]), fill=c, outline=(60, 60, 60), width=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="Docs/evidence/CASCO-V2-DIAG/casco_diagnostic.json")
    ap.add_argument("--out", default="Docs/evidence/CASCO-V2-DIAG/captures")
    args = ap.parse_args()
    doc = json.load(open(args.json, encoding="utf-8"))
    ov = doc["debug_overlay"]
    plots = doc["plots"]
    cands = doc["candidates"]
    res = ov["residual_polys"]
    os.makedirs(args.out, exist_ok=True)
    note = "data render from casco_diagnostic.json (same data as the Unity overlay) - not a Unity capture; green = above current provisional minimum heuristic"
    saved = []

    # 1 — overview
    m = Map("CASCO diagnostic - overview",
            note + "; deliberate = generator-tagged, NOT validated for V2")
    draw_context(m, doc)
    for r in res:
        m.poly(r["coords"], fill=RESID)
    draw_plots(m, plots)
    m.frame()
    saved.append(m.save(os.path.join(args.out, "map_01_overview.png")))

    # 2 — residual
    m = Map("Residual (unclassified) space", note)
    draw_context(m, doc, with_deliberate=False)
    for p in plots:
        if p["kind"] == "building":
            m.poly(ring(p["rect_xz"]), fill=BUILDING_CTX)
    top = res[:8]
    for r in res:
        m.poly(r["coords"], fill=RESID, outline=RESID_EDGE, width=1)
    for r in top:
        cx = sum(c[0] for c in r["coords"]) / len(r["coords"])
        cz = sum(c[1] for c in r["coords"]) / len(r["coords"])
        m.label(cx, cz, "%.0f m2" % r["area_m2"], size=15, color=(120, 80, 0))
    m.frame()
    saved.append(m.save(os.path.join(args.out, "map_02_residual.png")))

    # 3 — deliberate ground (generator tags)
    m = Map("Deliberate ground per GENERATOR tags (yard/huerta)",
            "deliberate = classified by the generator; NOT validated as useful for CASCO-V2 - " + note)
    for g_poly in ov.get("deliberate_polys", []):
        m.poly(g_poly, fill=DELIB, outline=(42, 139, 163), width=1)
    for g in street_polys(ov):
        for poly in ([g] if g.geom_type == "Polygon" else g.geoms):
            m.poly(poly.exterior.coords, fill=STREET)
    for p in ov.get("plazas", []):
        m.poly([tuple(c) for c in p["poly"]], fill=PLAZA)
    for p in ov.get("water_poly", []):
        m.poly(p, fill=WATER)
    for p in plots:
        if p["kind"] == "building":
            m.poly(ring(p["rect_xz"]), fill=BUILDING_CTX)
    m.frame()
    saved.append(m.save(os.path.join(args.out, "map_03_deliberate.png")))

    # 4 — deficient plots
    m = Map("Below-minimum (red) and narrow-only (amber) plots",
            "red < %s m2 or < %s m frontage; amber <= %s m; heuristic only - %s" % (
                doc["config_used"]["heuristics"]["min_interior_footprint_m2"],
                doc["config_used"]["heuristics"]["min_interior_frontage_m"],
                doc["config_used"]["heuristics"]["narrow_plot_max_w_m"], note))
    draw_context(m, doc, with_deliberate=False)
    for p in plots:
        if p["kind"] == "building":
            c = RED if (p.get("flag_small_footprint") or p.get("flag_below_min_frontage")) \
                else AMBER if p.get("flag_narrow") else BUILDING_CTX
            m.poly(ring(p["rect_xz"]), fill=c, outline=(60, 60, 60), width=1)
    for p in plots:
        if p["kind"] == "building" and p.get("bays") == 1:
            m.label(p["cx"], p["cz"], p["id"], size=11, color=(90, 0, 0))
    m.frame()
    saved.append(m.save(os.path.join(args.out, "map_04_deficient.png")))

    # 5 — all candidates
    m = Map("All 342 grouping candidates (2-6 plots, data only)", note)
    draw_context(m, doc, with_deliberate=False)
    for p in plots:
        if p["kind"] == "building":
            m.poly(ring(p["rect_xz"]), fill=BUILDING_CTX)
    for c in cands:
        m.line(ring(c["hull_xz"]), CAND, 1)
    m.frame()
    saved.append(m.save(os.path.join(args.out, "map_05_candidates_all.png")))

    # 6 — candidates containing a below-minimum (red) member
    red_c = [c for c in cands if c["n_small_members"] > 0]
    m = Map("Candidates containing a below-minimum member (%d of %d)" % (len(red_c), len(cands)),
            "data only - no grouping chosen - " + note)
    draw_context(m, doc, with_deliberate=False)
    for p in plots:
        if p["kind"] != "building":
            continue
        c = RED if (p.get("flag_small_footprint") or p.get("flag_below_min_frontage")) \
            else AMBER if p.get("flag_narrow") else BUILDING_CTX
        m.poly(ring(p["rect_xz"]), fill=c)
    for c in red_c:
        m.line(ring(c["hull_xz"]), CAND, 2)
    for c in red_c:
        xs = [v[0] for v in c["hull_xz"]]
        zs = [v[1] for v in c["hull_xz"]]
        m.label(sum(xs) / len(xs), sum(zs) / len(zs),
                "%dp %.0fm" % (c["size"], c["frontage_combined_m"]), size=10,
                color=(20, 40, 120))
    m.frame()
    saved.append(m.save(os.path.join(args.out, "map_06_candidates_red.png")))

    for p in saved:
        print("rendered", p)


if __name__ == "__main__":
    main()

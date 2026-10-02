"""Layout trace v1 of the Ivanix88 'Medieval City Pack Demo' from the Owner's survey captures (local image analysis
only — no further queries to Sketchfab). Use authorised by the author (Owner, 2026-10-02). The author's scene file,
if provided, supersedes this trace.

Output (metres, x = east, z = north, origin = centre of the central round plaza):
  reconstruction/layout_trace_v1.json  water / island / banks / public paving / yards / built masses / towers /
                                       outer wall / street graph with widths
  reconstruction/overlay_v1*.png       review overlays
"""

import json
import os
import math
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
# the layout captures are not redistributed: point JD_IVX_REFS at the local survey folder's references/
REFS = Path(os.environ.get("JD_IVX_REFS", str(ROOT / "references")))
REF = REFS / "originals" / "REF0017H_city_cenital_calibrated_3840.png"
CAM = REFS / "REF0017H_camera.json"
OUT = ROOT / "reconstruction"
PLAZA_PX = (2200, 790)
TOWER_REF = (2801, 651)


def camera():
    cam = json.loads(CAM.read_text(encoding="utf-8"))
    pos, tgt = np.array(cam["camera"]["position"], float), np.array(cam["camera"]["target"], float)
    view_h = 2 * np.linalg.norm(pos - tgt) * math.tan(math.radians(cam["fov"]) / 2)
    return tgt[0], tgt[1], view_h / cam["height"], cam["width"], cam["height"]


TX, TY, S, W, H = camera()
M_PER_PX = S / 100.0


def to_m(px, py):
    ox = TX + (PLAZA_PX[0] - W / 2) * S
    oy = TY + (H / 2 - PLAZA_PX[1]) * S
    wx, wy = TX + (px - W / 2) * S, TY + (H / 2 - py) * S
    return [round((wx - ox) / 100.0, 2), round((wy - oy) / 100.0, 2)]


def clean(m, o, c):
    m = m.astype(np.uint8) * 255
    if o:
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (o, o)))
    if c:
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (c, c)))
    return m > 0


def polys(mask, min_m2, eps_px=2.0):
    m = mask.astype(np.uint8) * 255
    cnts, hier = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    if hier is None:
        return out
    for i, c in enumerate(cnts):
        if hier[0][i][3] != -1:
            continue
        area = cv2.contourArea(c) * M_PER_PX ** 2
        if area < min_m2:
            continue
        holes, ch = [], hier[0][i][2]
        while ch != -1:
            if cv2.contourArea(cnts[ch]) * M_PER_PX ** 2 >= max(1.0, min_m2 / 4):
                holes.append([to_m(*p[0]) for p in cv2.approxPolyDP(cnts[ch], eps_px, True)])
            ch = hier[0][ch][0]
        out.append({"outer": [to_m(*p[0]) for p in cv2.approxPolyDP(c, eps_px, True)], "holes": holes, "area_m2": round(area, 1)})
    return out


def skeleton(mask):
    """Zhang-Suen thinning (vectorised)."""
    img = mask.astype(np.uint8).copy()
    while True:
        changed = False
        for step in range(2):
            P = np.pad(img, 1)
            p2, p3, p4, p5 = P[:-2, 1:-1], P[:-2, 2:], P[1:-1, 2:], P[2:, 2:]
            p6, p7, p8, p9 = P[2:, 1:-1], P[2:, :-2], P[1:-1, :-2], P[:-2, :-2]
            Bn = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
            seq = [p2, p3, p4, p5, p6, p7, p8, p9, p2]
            An = sum(((seq[i] == 0) & (seq[i + 1] == 1)).astype(np.uint8) for i in range(8))
            c = ((p2 * p4 * p6 == 0) & (p4 * p6 * p8 == 0)) if step == 0 else ((p2 * p4 * p8 == 0) & (p2 * p6 * p8 == 0))
            m = (img == 1) & (Bn >= 2) & (Bn <= 6) & (An == 1) & c
            if m.any():
                img[m] = 0
                changed = True
        if not changed:
            return img > 0


def street_graph(paving, dist, prune_m=7.0):
    small = cv2.resize(paving.astype(np.uint8), (W // 2, H // 2), interpolation=cv2.INTER_NEAREST)
    small = cv2.morphologyEx(small, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    sk = skeleton(small)
    f = 2.0
    pix = set(zip(*[a.tolist() for a in np.nonzero(sk)]))

    def nbrs(p):
        y, x = p
        return [(y + dy, x + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy or dx) and (y + dy, x + dx) in pix]

    for _ in range(3):                                   # prune short spurs
        deg = {p: len(nbrs(p)) for p in pix}
        ends = [p for p, d in deg.items() if d == 1]
        removed = 0
        for e in ends:
            path, cur, prev = [e], e, None
            while True:
                nx = [q for q in nbrs(cur) if q != prev and q in pix]
                if len(nx) != 1 or deg.get(nx[0], 0) > 2:
                    break
                prev, cur = cur, nx[0]
                path.append(cur)
                if len(path) * f * M_PER_PX > prune_m:
                    break
            if len(path) * f * M_PER_PX <= prune_m:
                for q in path:
                    pix.discard(q)
                removed += 1
        if not removed:
            break
    deg = {p: len(nbrs(p)) for p in pix}
    nodes = {p for p, d in deg.items() if d != 2}
    seen, edges = set(), []
    for n in nodes:
        for nb in nbrs(n):
            if (n, nb) in seen:
                continue
            path, prev, cur = [n, nb], n, nb
            while cur not in nodes:
                nxt = [q for q in nbrs(cur) if q != prev]
                if not nxt:
                    break
                prev, cur = cur, nxt[0]
                path.append(cur)
            seen.add((n, nb))
            seen.add((path[-1], path[-2]))
            length = sum(math.hypot(path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]) for i in range(len(path) - 1)) * f * M_PER_PX
            if length < 1.0:
                continue
            widths = [2 * dist[min(H - 1, int(y * f)), min(W - 1, int(x * f))] * M_PER_PX for y, x in path]
            simp = cv2.approxPolyDP(np.array([[x * f, y * f] for y, x in path], np.int32).reshape(-1, 1, 2), 4.0, False)
            edges.append({"points": [to_m(*p[0]) for p in simp], "length_m": round(length, 1),
                          "width_median_m": round(float(np.median(widths)), 2), "width_min_m": round(float(np.percentile(widths, 10)), 2)})
    return edges


def roofs_v2(img, L, A, B, land, water, wall_band, island, town):
    """Roof footprints from gradient-orientation coherence (roof courses are striped; shadows, earth, setts and grass
    are not), oriented by the structure tensor and split at the thinnest cross-section when several houses touch."""
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    gx, gy = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    k = (11, 11)
    Jxx, Jyy, Jxy = cv2.GaussianBlur(gx * gx, k, 0), cv2.GaussianBlur(gy * gy, k, 0), cv2.GaussianBlur(gx * gy, k, 0)
    tr = Jxx + Jyy
    coh = np.sqrt((Jxx - Jyy) ** 2 + 4 * Jxy ** 2) / (tr + 1e-3)
    en = np.sqrt(tr)
    lit_paving = (L > 186) & (np.abs(A - 133) < 6) & (B < 150)
    roof = ((coh > 0.5) & (en > 60)) | (A >= 140)
    roof &= land & ~water & ~wall_band & ~lit_paving
    roof = cv2.morphologyEx(roof.astype(np.uint8) * 255, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    cnts, _ = cv2.findContours(roof, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(roof)
    cv2.drawContours(filled, cnts, -1, 255, -1)                       # lit slopes inside a roof outline
    roof = cv2.morphologyEx(filled, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))) > 0
    n, lbl = cv2.connectedComponents(roof.astype(np.uint8))
    out = []

    def rect_of(ys, xs, theta):
        c, s = math.cos(theta), math.sin(theta)
        u = xs * c + ys * s
        v = -xs * s + ys * c
        return u, v

    def emit(ys, xs, depth=0):
        a_m2 = len(xs) * M_PER_PX ** 2
        if a_m2 < 9:
            return
        sxx, syy, sxy = Jxx[ys, xs].sum(), Jyy[ys, xs].sum(), Jxy[ys, xs].sum()
        theta = 0.5 * math.atan2(2 * sxy, sxx - syy)
        u, v = rect_of(ys.astype(np.float64), xs.astype(np.float64), theta)
        u0, u1, v0, v1 = u.min(), u.max(), v.min(), v.max()
        w, h = (u1 - u0) * M_PER_PX, (v1 - v0) * M_PER_PX
        fill = a_m2 / max(1e-6, w * h)
        split_needed = (fill < 0.62 and a_m2 > 55) or a_m2 > 110
        if split_needed and depth < 5:
            # split across the longer axis at the thinnest slice in the middle 70 %
            along, lo, hi = (u, u0, u1) if w >= h else (v, v0, v1)
            bins = np.histogram(along, bins=max(8, int((hi - lo) * M_PER_PX / 0.5)), range=(lo, hi))[0]
            m = len(bins)
            a0, a1 = int(m * 0.15), int(m * 0.85)
            if a1 > a0 + 1 and (fill < 0.62 or bins[a0:a1].min() < 0.6 * np.median(bins[a0:a1])):
                cut_bin = a0 + int(np.argmin(bins[a0:a1]))
                cut = lo + (cut_bin + 0.5) * (hi - lo) / m
                left = along < cut
                emit(ys[left], xs[left], depth + 1)
                emit(ys[~left], xs[~left], depth + 1)
                return
        short, long_ = min(w, h), max(w, h)
        if short < 2.6 or long_ / max(short, 1e-3) > 4.5:
            return
        cyi, cxi = int(np.clip(ys.mean(), 0, H - 1)), int(np.clip(xs.mean(), 0, W - 1))
        tile_share = (A[ys, xs] >= 139).mean()
        if L[ys, xs].mean() > 172 or (a_m2 < 22 and L[ys, xs].std() > 38):   # market stalls / striped canvas
            return
        if coh[ys, xs].mean() > 0.82:                                 # wall walks and stone parapets, not roofs
            return
        if not town[cyi, cxi] and tile_share < 0.25:                  # rocks and shore boulders outside the town wall
            return
        cu, cv_ = (u0 + u1) / 2, (v0 + v1) / 2
        c, s = math.cos(theta), math.sin(theta)
        cx, cy = cu * c - cv_ * s, cu * s + cv_ * c
        corners = []
        for du, dv in ((u0, v0), (u1, v0), (u1, v1), (u0, v1)):
            corners.append(to_m(du * c - dv * s, du * s + dv * c))
        mat = "tile" if (A[ys, xs] >= 139).mean() > 0.4 else ("slate" if (L[ys, xs] < 120).mean() > 0.5 else "light")
        out.append({"center": to_m(cx, cy), "rect": corners, "size_m": [round(w, 2), round(h, 2)], "area_m2": round(a_m2, 1),
                    "fill": round(fill, 2), "roof": mat, "zone": "island" if island[int(min(H - 1, max(0, cy))), int(min(W - 1, max(0, cx)))] else "banks"})

    for k2 in range(1, n):
        ys, xs = np.nonzero(lbl == k2)
        emit(ys, xs)
    for i, r in enumerate(out):
        r["id"] = f"R{i + 1:04d}"
    return out


def main():
    OUT.mkdir(exist_ok=True)
    img = cv2.imread(str(REF))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lab9 = cv2.cvtColor(cv2.medianBlur(img, 9), cv2.COLOR_BGR2LAB).astype(np.int16)
    L, A, B = lab9[..., 0], lab9[..., 1], lab9[..., 2]
    g = gray.astype(np.float32)
    gx = cv2.GaussianBlur(np.abs(cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)), (9, 9), 0)
    gy = cv2.GaussianBlur(np.abs(cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)), (9, 9), 0)
    iso = np.minimum(gx, gy) / (np.maximum(gx, gy) + 1e-3)
    energy = (gx + gy) / 2
    yy, xx = np.mgrid[0:H, 0:W]
    disc = ((xx - W / 2) ** 2 / (W * 0.43) ** 2 + (yy - H / 2) ** 2 / (H * 0.98) ** 2) < 1.0

    water = clean((L > 95) & (L < 140) & (A < 131) & (B < 157) & disc, 9, 25)
    n, lbl, st, _ = cv2.connectedComponentsWithStats(water.astype(np.uint8))
    water = lbl == (1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])))
    land = clean(disc & ~water, 0, 9)
    # bridges are ~3 m wide: erode 4 m, take the plaza component, grow it back inside the land
    k = int(round(4.0 / M_PER_PX)) * 2 + 1
    town_box = np.zeros((H, W), bool)
    town_box[150:1585, 940:2850] = True                      # walled-town extent in the calibrated capture
    eroded = cv2.erode((land & town_box).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    n, lbl, st, _ = cv2.connectedComponentsWithStats(eroded)
    core = (lbl == lbl[PLAZA_PX[1], PLAZA_PX[0]]).astype(np.uint8)
    island = (cv2.dilate(core, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k + 4, k + 4))) > 0) & land & town_box
    banks = land & ~island

    # towers by template matching on the rim (identical assets, identical light)
    R = 26
    tpl = gray[TOWER_REF[1] - R:TOWER_REF[1] + R + 1, TOWER_REF[0] - R:TOWER_REF[0] + R + 1]
    yyt, xxt = np.mgrid[-R:R + 1, -R:R + 1]
    rr = np.sqrt(xxt ** 2 + yyt ** 2)
    res = np.nan_to_num(cv2.matchTemplate(gray, tpl, cv2.TM_CCORR_NORMED, mask=(((rr >= 16) & (rr <= 23)) * 255).astype(np.uint8)))
    towers = []
    while True:
        _, mv, _, ml = cv2.minMaxLoc(res)
        if mv < 0.93:
            break
        x, y = ml[0] + R, ml[1] + R
        if island[min(H - 1, y), min(W - 1, x)] or cv2.dilate(island.astype(np.uint8), np.ones((25, 25), np.uint8))[y, x]:
            towers.append((x, y))
        cv2.circle(res, ml, 30, 0, -1)

    # outer wall: towers near the island edge, ordered along the island contour
    cnts, _ = cv2.findContours(island.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contour = max(cnts, key=cv2.contourArea).reshape(-1, 2)
    edge_d = cv2.distanceTransform(island.astype(np.uint8), cv2.DIST_L2, 5)
    outer = []
    for x, y in towers:
        d = edge_d[min(H - 1, y), min(W - 1, x)] * M_PER_PX
        if d < 14.0:
            idx = int(np.argmin(((contour - [x, y]) ** 2).sum(1)))
            outer.append((idx, x, y))
    outer.sort()
    wall_px = [(x, y) for _, x, y in outer]
    wall_band = np.zeros((H, W), np.uint8)
    if len(wall_px) > 2:
        cv2.polylines(wall_band, [np.array(wall_px, np.int32)], True, 255, int(round(3.4 / M_PER_PX)))
        for x, y in towers:
            cv2.circle(wall_band, (x, y), int(round(3.6 / M_PER_PX)), 255, -1)
    wall_band = wall_band > 0

    neutral = (np.abs(A - 133) < 6) & (B < 151)
    paving = clean(((L > 178) & neutral) | (neutral & (L > 95) & (L <= 178) & (iso > 0.62) & (energy > 14)), 5, 11)
    paving &= land & ~wall_band
    yard_raw = ((B >= 152) & (L > 110) & (A < 140)) | ((A < 131) & (B >= 147) & (L < 165))
    yard = clean(yard_raw & land & ~paving & ~wall_band, 5, 7)
    built = clean(land & ~paving & ~yard & ~wall_band, 5, 3)
    # drop tree crowns (greenish) and market stalls (tiny, striped) from built masses
    n, lbl, st, _ = cv2.connectedComponentsWithStats(built.astype(np.uint8))
    meanA = np.bincount(lbl.ravel(), weights=A.ravel(), minlength=n) / np.maximum(1, np.bincount(lbl.ravel(), minlength=n))
    area_m2 = st[:, cv2.CC_STAT_AREA] * M_PER_PX ** 2
    keep = (meanA >= 132) & (area_m2 >= 8)
    keep[0] = False
    built = keep[lbl]

    # split aggregated masses into roofs: neighbouring houses usually change material (tile / slate / thatch)
    roof_cls = np.zeros((H, W), np.uint8)
    roof_cls[built & (A >= 139)] = 1                                   # tile
    roof_cls[built & (A < 139) & (B >= 148) & (L > 112)] = 2           # thatch / light
    roof_cls[built & (roof_cls == 0)] = 3                              # slate (dark and lit slopes)
    roof_cls = cv2.medianBlur(roof_cls, 7)
    roof_cls[~built] = 0
    pieces = np.zeros((H, W), np.int32)
    nxt = 1
    for c in (1, 2, 3):
        m = cv2.morphologyEx((roof_cls == c).astype(np.uint8), cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
        nn, ll = cv2.connectedComponents(m)
        for k2 in range(1, nn):
            sel = ll == k2
            if sel.sum() * M_PER_PX ** 2 >= 7.0:
                pieces[sel] = nxt
                nxt += 1
    buildings = []
    n = nxt
    lbl = pieces
    st = np.zeros((n, 5), np.int64)
    st[:, cv2.CC_STAT_AREA] = np.bincount(pieces.ravel(), minlength=n)
    for k in range(1, n):
        comp = (lbl == k).astype(np.uint8)
        cnt = max(cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0], key=cv2.contourArea)
        (cx, cy), (w, h), ang = cv2.minAreaRect(cnt)
        a = st[k, cv2.CC_STAT_AREA] * M_PER_PX ** 2
        zone = "island" if island[int(cy), int(cx)] else "banks"
        mat = {1: "tile", 2: "thatch", 3: "slate"}.get(int(np.bincount(roof_cls[lbl == k], minlength=4)[1:].argmax()) + 1, "slate")
        buildings.append({"id": f"M{k:04d}", "zone": zone, "roof": mat, "center": to_m(cx, cy), "area_m2": round(a, 1),
                          "rect_size_m": [round(w * M_PER_PX, 2), round(h * M_PER_PX, 2)], "rect_angle_deg": round(float(ang), 1),
                          "rect_fill": round(a / max(1e-6, w * h * M_PER_PX ** 2), 2),
                          "outline": [to_m(*p[0]) for p in cv2.approxPolyDP(cnt, 2.0, True)]})

    town = np.zeros((H, W), np.uint8)
    if len(wall_px) > 2:
        cv2.fillPoly(town, [np.array(wall_px, np.int32)], 1)
    roofs = roofs_v2(img, L, A, B, land, water, wall_band, island, town > 0)
    dist = cv2.distanceTransform(paving.astype(np.uint8), cv2.DIST_L2, 5)
    graph = street_graph(paving & land, dist)

    doc = {
        "schema": "juego-def.ivanix-layout-trace/1",
        "status": "IMAGE TRACE v1 — author permission (Owner 2026-10-02); the author's scene file supersedes it",
        "source": {"model": "Ivanix88 / Medieval City Pack Demo (2043203b32b548cc84448e4ffe2be28c)", "image": REF.name, "m_per_px": round(M_PER_PX, 4)},
        "landmarks_m": {"plaza": [0.0, 0.0], "north_port_gate": to_m(2190, 450), "south_gate": to_m(2231, 1571)},
        "water": polys(water, 500, 4.0), "island": polys(island, 5000, 3.0), "banks": polys(banks, 500, 4.0),
        "public_paving": polys(paving, 6, 2.0), "yards": polys(yard, 6, 2.0),
        "yards_green": polys(yard & ((A < 131) & (B >= 147) & (L < 165)), 6, 2.0),
        "towers": [{"pos": to_m(x, y), "outer_wall": any(x == wx and y == wy for wx, wy in wall_px)} for x, y in towers],
        "outer_wall": [to_m(x, y) for x, y in wall_px],
        "built_masses": buildings, "roofs": roofs, "street_graph": graph,
        "summary": {"island_m2": round(island.sum() * M_PER_PX ** 2), "banks_m2": round(banks.sum() * M_PER_PX ** 2),
                    "paving_m2": round(paving.sum() * M_PER_PX ** 2), "yard_m2": round(yard.sum() * M_PER_PX ** 2),
                    "built_m2": round(built.sum() * M_PER_PX ** 2), "masses": len(buildings), "roofs": len(roofs),
                    "roofs_island": sum(1 for r in roofs if r["zone"] == "island"),
                    "masses_island": sum(1 for b in buildings if b["zone"] == "island"), "towers": len(towers),
                    "outer_wall_towers": len(wall_px), "street_edges": len(graph),
                    "street_length_m": round(sum(e["length_m"] for e in graph))},
    }
    (OUT / "layout_trace_v1.json").write_text(json.dumps(doc, ensure_ascii=False) + "\n", encoding="utf-8")

    vis = (img * 0.35).astype(np.uint8)
    vis[paving] = (225, 225, 225)
    vis[yard] = (60, 140, 160)
    vis[water] = (150, 100, 40)
    vis[built] = (50, 80, 210)
    vis[wall_band] = (120, 120, 120)
    for e in graph:
        pts = np.array([[int(round((p[0] * 100) / S + PLAZA_PX[0])), int(round(PLAZA_PX[1] - (p[1] * 100) / S))] for p in e["points"]], np.int32)
        cv2.polylines(vis, [pts], False, (0, 160, 0), 3)
    for x, y in towers:
        cv2.circle(vis, (x, y), 20, (0, 255, 255), 3)
    cv2.imwrite(str(OUT / "overlay_v1_full.png"), cv2.resize(vis, (1920, 855)))
    cv2.imwrite(str(OUT / "overlay_v1_center.png"), vis[300:1300, 1800:3000])
    print(json.dumps(doc["summary"], indent=1))


if __name__ == "__main__":
    main()

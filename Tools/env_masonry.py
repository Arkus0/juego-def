"""Stylised tileable masonry and paving textures for the ENV factory (owner audit 2026-09-29, points 3/13/14/23:
"la piedra es demasiado uniforme... aparece igual en casas, muros y río"; "el mismo adoquín domina casi toda la escena").

The kit has one rubble wall texture (T_UnevenBrick) and one cobble texture (T_RoundRocks); the casco needs several
bonds and scales. Each texture here is generated from a height field (stones laid out by a bond: periodic Voronoi for
rubble/slabs/cobbles, coursed rectangles for ashlar/setts), then painted in the Quaternius manner: flat stone tones with
soft bevel light, dark or lime joints, a little speckle. Outputs per type: <name>_BaseColor (neutral-warm, tinted by the
material colour), <name>_Normal and <name>_Roughness. One texture = SPAN x 2 m (materials tile it at 1/SPAN), so the
stone pattern repeats every 4 m instead of every kit bay (owner: "la piedra se repite con demasiada regularidad").

    python Tools/env_masonry.py --out Unity/JuegoDef/Assets/JuegoDef/Derived/ENV/Textures [--only NAME] [--size 512]
"""
import argparse
import math
import os

import numpy as np
from PIL import Image, ImageFilter


def periodic_noise(n, cells, rng):
    lat = rng.random((cells, cells))
    x = np.linspace(0, cells, n, endpoint=False)
    i0 = np.floor(x).astype(int)
    f = x - i0
    f = f * f * (3 - 2 * f)
    i1 = (i0 + 1) % cells
    a, b, c, d = lat[np.ix_(i0, i0)], lat[np.ix_(i0, i1)], lat[np.ix_(i1, i0)], lat[np.ix_(i1, i1)]
    fx, fy = f[None, :], f[:, None]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def fbm(n, rng, octaves=(4, 8, 16, 32), gains=(1.0, 0.5, 0.25, 0.12)):
    v = sum(g * periodic_noise(n, o, rng) for o, g in zip(octaves, gains))
    v -= v.min()
    return v / max(v.max(), 1e-9)


# ------------------------------------------------------------------ layouts: per pixel (cell id, distance to joint)

SPAN = 2          # 2 m kit tiles per texture


def voronoi(n, pts, stretch=(1.0, 1.0), warp=0.0, rng=None):
    """Periodic Voronoi on the unit torus. pts: (k, 2) in [0,1). Returns cell id and the half gap F2-F1 (in tile
    units, anisotropic metric) which is ~ the distance to the nearest joint. `warp` bends the straight Voronoi
    edges with a periodic noise offset (hand-laid stones, not cut polygons)."""
    sx, sy = stretch
    ys, xs = np.mgrid[0:n, 0:n] / n
    if warp > 0:
        o = tuple(k * SPAN for k in (6, 12, 24))
        xs = xs + (fbm(n, rng, o, (1, 0.5, 0.25)) - 0.5) * warp / SPAN
        ys = ys + (fbm(n, rng, o, (1, 0.5, 0.25)) - 0.5) * warp / SPAN
    cid = np.zeros((n, n), np.int32)
    gap = np.zeros((n, n), np.float32)
    step = 16
    for r0 in range(0, n, step):
        px = xs[r0:r0 + step, :, None]
        py = ys[r0:r0 + step, :, None]
        dx = (px - pts[None, None, :, 0] + 0.5) % 1.0 - 0.5
        dy = (py - pts[None, None, :, 1] + 0.5) % 1.0 - 0.5
        d = np.sqrt((dx * sx) ** 2 + (dy * sy) ** 2)
        part = np.partition(d, 1, axis=2)
        cid[r0:r0 + step] = np.argmin(d, axis=2)
        gap[r0:r0 + step] = (part[..., 1] - part[..., 0]) * 0.5 * SPAN   # joint widths stay in 2 m-tile units
    return cid, gap


def coursed_points(rng, rows, per_row, jitter_x=0.35, jitter_y=0.18):
    rows, per_row = rows * SPAN, per_row * SPAN
    pts = []
    for r in range(rows):
        y = (r + 0.5) / rows
        k = max(2, int(round(per_row * rng.uniform(0.8, 1.2))))
        off = rng.random()
        for i in range(k):
            x = (i + off + rng.uniform(-jitter_x, jitter_x) * 0.5) / k
            pts.append(((x) % 1.0, (y + rng.uniform(-jitter_y, jitter_y) / rows) % 1.0))
    return np.array(pts)


def courses(n, rng, heights, widths, stagger=True):
    """Coursed rectangles (ashlar, setts): row heights drawn from `heights`, block lengths from `widths` (tile units).
    Returns cell id and the distance to the nearest joint (tile units). Rows and blocks wrap exactly."""
    heights = [h / SPAN for h in heights]
    widths = [w / SPAN for w in widths]
    hs = []
    while sum(hs) < 1.0:
        hs.append(rng.choice(heights))
    hs = np.array(hs) / sum(hs)
    ys = np.arange(n) / n
    edges = np.concatenate([[0], np.cumsum(hs)])
    cid = np.zeros((n, n), np.int32)
    dist = np.zeros((n, n), np.float32)
    xs = np.arange(n) / n
    base = 0
    for r in range(len(hs)):
        y0, y1 = edges[r], edges[r + 1]
        rows = (ys >= y0) & (ys < y1)
        ws = []
        while sum(ws) < 1.0:
            ws.append(rng.choice(widths))
        ws = np.array(ws) / sum(ws)
        off = rng.random() if stagger else 0.0
        xe = (np.concatenate([[0], np.cumsum(ws)]) + off) % 1.0
        xr = (xs - off) % 1.0
        xedge = np.concatenate([[0], np.cumsum(ws)])
        k = np.clip(np.searchsorted(xedge, xr, side="right") - 1, 0, len(ws) - 1)
        dx = np.minimum(xr - xedge[k], xedge[k + 1] - xr)
        yy = ys[rows]
        dy = np.minimum(yy - y0, y1 - yy)
        cid[rows] = base + k[None, :]
        dist[rows] = np.minimum(dx[None, :], dy[:, None]) * SPAN
        base += len(ws)
    return cid, dist


# ------------------------------------------------------------------ painting

def paint(n, rng, cid, gap, joint, round_, tones, mortar, speckle=0.12, relief=1.0, flat_top=0.0, grain=0.0):
    """Height, albedo, normal and roughness from a layout. tones: (dark, light) stone RGB; mortar RGB (None = deep
    shadowed joint)."""
    k = int(cid.max()) + 1
    tone = rng.random(k)
    tint = rng.uniform(-1, 1, (k, 1)) * np.array([[0.035, 0.008, -0.03]])   # warm/cool drift, no candy colours
    stone = np.clip((gap - joint) / max(round_ * 0.35, 1e-4), 0, 1)
    dome = np.sqrt(np.clip((gap - joint) / max(round_, 1e-4), 0, 1))
    n1 = fbm(n, rng, tuple(o * SPAN for o in (8, 16, 32, 64)), (1, 0.6, 0.35, 0.2))
    h = stone * (0.55 + 0.45 * np.maximum(dome, flat_top)) + (n1 - 0.5) * 0.08 * stone
    h += tone[cid] * 0.06 * stone                                  # stones stand proud by different amounts
    # normal from height (wrapped gradients)
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 0.5 * n / (64 * SPAN) * relief
    gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 0.5 * n / (64 * SPAN) * relief
    nrm = np.stack([-gx, gy, np.ones_like(h)], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    # albedo: per-stone tone, speckle, bevel light from the upper left, joints
    dark, light = np.array(tones[0], float), np.array(tones[1], float)
    t = tone[cid][..., None]
    col = dark + (light - dark) * t
    col = col * (1 + tint[cid])
    sp = fbm(n, rng, tuple(o * SPAN for o in (32, 64, 128)), (1, 0.6, 0.4))
    col *= (1 - speckle / 2 + speckle * sp)[..., None]
    if grain > 0:                                                  # bedding lines in slate-like slabs
        g = periodic_noise(n, 96 * SPAN, rng)
        col *= (1 - grain / 2 + grain * g.mean(axis=1, keepdims=True))[..., None]
    light_dir = np.array([-0.45, 0.55, 0.7])
    light_dir /= np.linalg.norm(light_dir)
    lam = np.clip(nrm @ light_dir, 0, 1)
    col *= (0.78 + 0.34 * lam)[..., None]
    col = np.round(col / 6) * 6                                    # painterly banding
    if mortar is None:
        jc = col * 0.35
    else:
        jc = np.array(mortar, float)[None, None, :] * (0.9 + 0.2 * sp[..., None])
    col = jc + (col - jc) * stone[..., None]
    rough = 0.82 + 0.1 * (1 - stone) + (sp - 0.5) * 0.08
    return h, np.clip(col, 0, 255), nrm, np.clip(rough, 0, 1)


def save(out, name, col, nrm, rough, size):
    Image.fromarray(col.astype(np.uint8), "RGB").filter(ImageFilter.SMOOTH).resize((size, size), Image.LANCZOS) \
        .save(os.path.join(out, name + "_BaseColor.jpg"), quality=90)  # colour + roughness as JPEG (repo weight), normals lossless
    nm = ((nrm * 0.5 + 0.5) * 255).astype(np.uint8)
    Image.fromarray(nm, "RGB").resize((size, size), Image.LANCZOS).save(os.path.join(out, name + "_Normal.png"))
    Image.fromarray((rough * 255).astype(np.uint8), "L").resize((size, size), Image.LANCZOS) \
        .save(os.path.join(out, name + "_Roughness.jpg"), quality=88)


# ------------------------------------------------------------------ types (one tile = 2 m)

def rubble(n, rng):
    """Mampostería: irregular stones laid in rough courses, lime mortar showing."""
    cid, gap = voronoi(n, coursed_points(rng, 8, 6), (0.8, 1.0), 0.05, rng)
    return paint(n, rng, cid, gap, 0.006, 0.03, ((118, 108, 96), (182, 170, 150)), (170, 162, 146), relief=1.2)


def ashlar(n, rng):
    """Sillería: dressed coursed blocks with thin joints (casonas, tower, bridge, quay copings)."""
    cid, dist = courses(n, rng, (0.16, 0.2, 0.2, 0.24), (0.22, 0.3, 0.36, 0.42))
    return paint(n, rng, cid, dist, 0.004, 0.02, ((150, 138, 118), (196, 182, 158)), (120, 112, 100), 0.08, 0.6, 0.85)


def laja(n, rng):
    """Lajas: thin flat slabs dry-laid in long courses (field and huerta walls, backs)."""
    cid, gap = voronoi(n, coursed_points(rng, 16, 5, 0.4, 0.1), (0.35, 1.0), 0.03, rng)
    return paint(n, rng, cid, gap, 0.004, 0.012, ((84, 82, 78), (140, 134, 124)), None, 0.16, 1.4, grain=0.12)


def canto(n, rng):
    """Canto rodado masonry: rounded river stones in wide lime mortar (river walls, humble backs)."""
    cid, gap = voronoi(n, coursed_points(rng, 11, 9, 0.5, 0.35), (1.0, 1.1), 0.04, rng)
    return paint(n, rng, cid, gap, 0.008, 0.03, ((104, 100, 94), (170, 164, 152)), (178, 172, 158), 0.1, 1.3)


def pave_flags(n, rng):
    """Losas: big irregular flagstones (the old main street's strip, forecourts, plaza), worn flat."""
    cid, gap = voronoi(n, coursed_points(rng, 4, 3, 0.6, 0.3), (0.85, 1.0), 0.03, rng)
    return paint(n, rng, cid, gap, 0.004, 0.02, ((140, 134, 124), (186, 178, 164)), (112, 106, 96), 0.1, 0.5, 0.9)


def pave_setts(n, rng):
    """Adoquín: granite setts in straight rows (bridge decks, repaired stretches, the plaza's edges)."""
    cid, dist = courses(n, rng, (0.1, 0.1, 0.11), (0.1, 0.12, 0.14))
    return paint(n, rng, cid, dist, 0.004, 0.012, ((116, 114, 110), (168, 164, 156)), None, 0.14, 1.0, 0.6)


def pave_canto(n, rng):
    """Canto rodado paving: small dense river cobbles on edge (lanes)."""
    cid, gap = voronoi(n, coursed_points(rng, 18, 16, 0.5, 0.4), (1.0, 1.25), 0.025, rng)
    return paint(n, rng, cid, gap, 0.003, 0.012, ((96, 92, 86), (158, 150, 138)), None, 0.12, 1.3)


def pave_plaza(n, rng):
    """Enlosado de plaza: large square-cut slabs in regular courses."""
    cid, dist = courses(n, rng, (0.25, 0.25), (0.25, 0.25, 0.5), stagger=True)
    return paint(n, rng, cid, dist, 0.003, 0.02, ((160, 152, 138), (198, 190, 174)), None, 0.1, 0.45, 0.95)


TYPES = {
    "T_ENV_Stone_Rubble": rubble, "T_ENV_Stone_Ashlar": ashlar, "T_ENV_Stone_Laja": laja, "T_ENV_Stone_Canto": canto,
    "T_ENV_Pave_Flags": pave_flags, "T_ENV_Pave_Setts": pave_setts, "T_ENV_Pave_Canto": pave_canto, "T_ENV_Pave_Plaza": pave_plaza,
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--size", type=int, default=512 * SPAN)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    only = set(filter(None, a.only.split(",")))
    for i, (name, fn) in enumerate(TYPES.items()):
        if only and name not in only:
            continue
        rng = np.random.default_rng(100 + i)     # one stream per type: regenerating one never changes the others
        h, col, nrm, rough = fn(768 * SPAN, rng)
        save(a.out, name, col, nrm, rough, a.size)
        print(name)


if __name__ == "__main__":
    main()

"""Painted ground textures the paving map needs and the kit does not have (Dreamcast+ manner: joints, bevel light and
wear painted in, tileable):

  TX_Ground_Abanico.png - setts laid in fans (abanico), the classic pattern of a junction or a small square;
                          one tile = 1.2 m.
  TX_Ground_Granito.png - dressed light granite for the bands (cintas), kerbs and rims: speckled, worn smooth;
                          one tile = 2.0 m.

Output: Unity/JuegoDef/Assets/JuegoDef/City/Ground/
"""

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parents[1] / "Unity" / "JuegoDef" / "Assets" / "JuegoDef" / "City" / "Ground"
OUT.mkdir(parents=True, exist_ok=True)


def shade(c, k):
    return tuple(int(max(0, min(255, v * k))) for v in c)


def abanico():
    W = 1024                         # 1.2 m
    R = W // 2                       # fan radius 0.6 m
    rng = np.random.default_rng(3)
    img = Image.new("RGB", (W, W), (54, 50, 46))                      # the joints
    d = ImageDraw.Draw(img)
    stones = [(150, 146, 138), (132, 128, 120), (164, 158, 146), (120, 118, 114), (142, 136, 124)]
    ring_w, gap = 78, 7
    # fans on a staggered lattice: rows every R/2, each row shifted by R; four rows make the tile
    centres = sorted([(i * W + (j % 2) * R, j * (R // 2)) for i in range(-1, 2) for j in range(-2, 2 * W // R + 3)], key=lambda c: c[1])
    for (cx, cy) in centres:
        for tile_dx in (0,):
            for tile_dy in (0,):
                x0, y0 = cx + tile_dx, cy + tile_dy
                if x0 + R < -10 or x0 - R > W + 10 or y0 < -10 or y0 - R > W + 10:
                    continue
                # clear the fan's area (it lies over what is below), then its rings of setts
                d.pieslice([x0 - R, y0 - R, x0 + R, y0 + R], 180, 360, fill=(54, 50, 46))
                r = R
                while r > 30:
                    r0 = max(10, r - ring_w)
                    n = max(3, int(math.pi * (r + r0) / 2 / 78))
                    for k in range(n):
                        a0 = math.pi + math.pi * k / n
                        a1 = math.pi + math.pi * (k + 1) / n
                        ag = gap / max(20, r)
                        pts = []
                        for (rr, aa) in ((r - gap / 2, a0 + ag), (r - gap / 2, a1 - ag), (r0 + gap / 2, a1 - ag), (r0 + gap / 2, a0 + ag)):
                            pts.append((x0 + rr * math.cos(aa), y0 + rr * math.sin(aa)))
                        col = stones[int(rng.integers(0, len(stones)))]
                        col = shade(col, rng.uniform(0.9, 1.08))
                        d.polygon(pts, fill=col)
                        # the bevel: light on the upper edge, dark on the lower (light from the north-west)
                        d.line([pts[0], pts[1]], fill=shade(col, 1.18), width=4)
                        d.line([pts[2], pts[3]], fill=shade(col, 0.72), width=4)
                    r = r0
    img = img.filter(ImageFilter.SMOOTH)
    a = np.asarray(img).astype(np.float32)
    a *= rng.normal(1.0, 0.025, a.shape[:2])[..., None]                # grain
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(OUT / "TX_Ground_Abanico.png")


def granito():
    W = 512                          # 2 m
    rng = np.random.default_rng(5)
    base = np.array((150, 150, 146), np.float32)
    a = np.zeros((W, W, 3), np.float32) + base
    # a fine speckle (black mica, white feldspar), worn down: it reads as dressed stone, not as gravel
    for n, col, s in ((1600, (104, 104, 106), 1.0), (1100, (176, 174, 168), 1.0), (700, (132, 128, 122), 1.6)):
        ys, xs = rng.integers(0, W, n), rng.integers(0, W, n)
        for y, x in zip(ys, xs):
            r = max(1, int(rng.uniform(0.6, 1.0) * s))
            a[max(0, y - r):y + r, max(0, x - r):x + r] = col
    # worn smooth: soft tone drift, tileable (sum of periodic waves)
    yy, xx = np.mgrid[0:W, 0:W] / W * 2 * math.pi
    wear = 0.04 * np.sin(xx * 2 + 0.7) * np.cos(yy * 3 + 1.1) + 0.03 * np.sin((xx + yy) * 5)
    a *= (1.0 + wear)[..., None]
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.SMOOTH)
    img.save(OUT / "TX_Ground_Granito.png")


abanico()
granito()
print("ground textures ->", OUT)

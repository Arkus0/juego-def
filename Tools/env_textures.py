"""Stylized tileable ground textures for the ENV factory (hand-painted look, Quaternius-compatible).

The admitted kits have no tileable grass/earth ground (Nature's Grass.png is a gradient atlas for grass blades), so
gardens, huertas and the district's outer ground use these generated textures: soft painted blotches from periodic
value noise (seamless), short strokes for grass, furrows for tilled huertas. Palette from the Visual Bible (damp
green #4E7A43, timber/earth browns).

    python Tools/env_textures.py --out Unity/JuegoDef/Assets/JuegoDef/Derived/ENV/Textures
"""
import argparse
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

N = 512


def periodic_noise(n, cells, rng):
    """Seamless value noise: random lattice (cells x cells) wrapped, smooth-interpolated to n x n."""
    lat = rng.random((cells, cells))
    x = np.linspace(0, cells, n, endpoint=False)
    i0 = np.floor(x).astype(int)
    f = x - i0
    f = f * f * (3 - 2 * f)
    i1 = (i0 + 1) % cells
    a = lat[np.ix_(i0, i0)]
    b = lat[np.ix_(i0, i1)]
    c = lat[np.ix_(i1, i0)]
    d = lat[np.ix_(i1, i1)]
    fx, fy = f[None, :], f[:, None]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def fbm(n, rng, octaves=(4, 8, 16, 32), gains=(1.0, 0.5, 0.25, 0.12)):
    v = sum(g * periodic_noise(n, o, rng) for o, g in zip(octaves, gains))
    v -= v.min()
    return v / v.max()


def lerp(a, b, t):
    return a + (np.array(b, float) - np.array(a, float)) * t[..., None]


def quantise(v, steps):
    """Painterly banding: blotches read as flat brush areas, not photographic noise."""
    return np.round(v * steps) / steps


def grass(rng):
    n1 = quantise(fbm(N, rng), 5)
    n2 = fbm(N, rng, (8, 16, 32), (1, 0.5, 0.25))
    base = lerp(np.array([62, 96, 52], float), [98, 128, 66], n1)           # damp greens
    earth = n2 > 0.78
    base[earth] = base[earth] * 0.55 + np.array([108, 88, 60]) * 0.45       # worn earth spots
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB")
    dr = ImageDraw.Draw(img)
    for _ in range(2600):                                                   # grass strokes, wrapped
        x, y = rng.random() * N, rng.random() * N
        ang = math.radians(rng.uniform(60, 120))
        L = rng.uniform(4, 10)
        c = (int(46 + rng.random() * 30), int(78 + rng.random() * 40), int(40 + rng.random() * 20)) if rng.random() < 0.6 else \
            (int(110 + rng.random() * 30), int(140 + rng.random() * 25), int(70 + rng.random() * 20))
        for ox in (-N, 0, N):
            for oy in (-N, 0, N):
                dr.line([(x + ox, y + oy), (x + ox + L * math.cos(ang), y + oy - L * math.sin(ang))], fill=c, width=2)
    return img.filter(ImageFilter.SMOOTH)


def earth(rng):
    n1 = quantise(fbm(N, rng), 6)
    base = lerp(np.array([92, 70, 48], float), [128, 100, 70], n1)
    yy = np.arange(N)[:, None] + 6 * (periodic_noise(N, 8, rng) - 0.5) * 8
    furrow = 0.5 + 0.5 * np.sin(yy / N * 2 * math.pi * 8)                  # 8 tilled rows per tile
    base = base * (0.78 + 0.3 * furrow[..., None])
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB")
    dr = ImageDraw.Draw(img)
    for _ in range(900):                                                    # clods and pebbles
        x, y = rng.random() * N, rng.random() * N
        r = rng.uniform(1.5, 4)
        c = (int(70 + rng.random() * 30), int(54 + rng.random() * 22), int(38 + rng.random() * 18))
        for ox in (-N, 0, N):
            for oy in (-N, 0, N):
                dr.ellipse([x + ox - r, y + oy - r * 0.7, x + ox + r, y + oy + r * 0.7], fill=c)
    return img.filter(ImageFilter.SMOOTH)


def painted(rng, lo, hi, steps=5, streak=0.0, n=256):
    """Flat painted base with soft quantised mottling (hand-painted look); optional vertical brush streaks."""
    v = quantise(fbm(n, rng), steps)
    if streak > 0:
        s = periodic_noise(n, 32, rng)[:, :1].repeat(n, axis=1).T  # varies along x only -> vertical streaks
        v = np.clip(v * (1 - streak) + s * streak, 0, 1)
    return lerp(np.array(lo, float), hi, v)


def iron(rng):
    """Cast/wrought iron painted near-black green-grey, worn lighter edges read from the mottling, sparse rust."""
    n = 256
    base = painted(rng, (34, 40, 41), (62, 70, 70), 5, 0.25, n)
    rust = fbm(n, rng, (8, 16, 32), (1, 0.5, 0.25)) > 0.84
    base[rust] = base[rust] * 0.4 + np.array([112, 72, 48]) * 0.6
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").filter(ImageFilter.SMOOTH)


def galvanised(rng):
    n = 256
    base = painted(rng, (150, 156, 154), (196, 200, 196), 6, 0.35, n)
    spots = fbm(n, rng, (16, 32, 64), (1, 0.6, 0.3)) > 0.8
    base[spots] = base[spots] * 0.85
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").filter(ImageFilter.SMOOTH)


def canvas(rng, colour, stripes=True):
    """Awning canvas: 8 stripes per tile (colour / cream) with weave mottling; U runs across the stripes."""
    n = 256
    weave = painted(rng, (0.86, 0.86, 0.86), (1.0, 1.0, 1.0), 6, 0.2, n)
    x = np.arange(n)[None, :].repeat(n, axis=0)
    band = ((x // (n // 8)) % 2 == 0) if stripes else np.ones((n, n), bool)
    col = np.where(band[..., None], np.array(colour, float), np.array((226, 214, 186), float))
    return Image.fromarray(np.clip(col * weave, 0, 255).astype(np.uint8), "RGB").filter(ImageFilter.SMOOTH)


def terracotta(rng):
    n = 256
    base = painted(rng, (150, 78, 50), (196, 112, 70), 6, 0.0, n)
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").filter(ImageFilter.SMOOTH)


def foliage(rng):
    """Solid stylised tree crowns: leaf clusters painted as overlapping soft blobs, light from above."""
    n = 512
    base = lerp(np.array([44, 74, 38], float), [70, 104, 50], quantise(fbm(n, rng), 4))
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB")
    dr = ImageDraw.Draw(img)
    for _ in range(1400):
        x, y = rng.random() * n, rng.random() * n
        r = rng.uniform(5, 13)
        light = rng.random()
        c = (int(58 + light * 60), int(92 + light * 62), int(42 + light * 30))
        for ox in (-n, 0, n):
            for oy in (-n, 0, n):
                dr.ellipse([x + ox - r, y + oy - r * 0.8, x + ox + r, y + oy + r * 0.8], fill=c)
    return img.filter(ImageFilter.GaussianBlur(0.8))


def board(rng):
    """Painted sign board: cream paint over timber, grain showing through and worn edges (no lettering)."""
    n = 256
    grain = periodic_noise(n, 4, rng)[:, :1].repeat(n, axis=1) * 0.5 + fbm(n, rng) * 0.5
    base = lerp(np.array([206, 192, 160], float), [236, 226, 200], quantise(grain, 6))
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").filter(ImageFilter.SMOOTH)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(7)
    random.seed(7)
    for name, fn in (("T_ENV_Ground_Grass", grass), ("T_ENV_Ground_Earth", earth), ("T_ENV_Iron", iron),
                     ("T_ENV_Galvanised", galvanised), ("T_ENV_Canvas_Red", lambda r: canvas(r, (150, 52, 40))),
                     ("T_ENV_Canvas_Green", lambda r: canvas(r, (54, 98, 70))), ("T_ENV_Canvas_Cream", lambda r: canvas(r, (226, 214, 186), False)),
                     ("T_ENV_Terracotta", terracotta), ("T_ENV_Foliage", foliage), ("T_ENV_Sign_Board", board)):
        path = os.path.join(a.out, name + ".png")
        fn(rng).save(path)
        print(path)


if __name__ == "__main__":
    main()

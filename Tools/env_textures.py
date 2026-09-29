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


def periodic_noise(n, cells, rng, cells_y=None):
    """Seamless value noise: random lattice (cells_y x cells) wrapped, smooth-interpolated to n x n."""
    cy = cells_y or cells
    lat = rng.random((cy, cells))
    def axis(c):
        x = np.linspace(0, c, n, endpoint=False)
        i0 = np.floor(x).astype(int)
        f = x - i0
        return i0, (i0 + 1) % c, f * f * (3 - 2 * f)
    x0, x1, fx = axis(cells)
    y0, y1, fy = axis(cy)
    a = lat[np.ix_(y0, x0)]
    b = lat[np.ix_(y0, x1)]
    c = lat[np.ix_(y1, x0)]
    d = lat[np.ix_(y1, x1)]
    fx, fy = fx[None, :], fy[:, None]
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



def window_glow(rng):
    """Lit interior seen through a window at night (neutral grey: the emission colour gives warm lamp / cool TV):
    ceiling light falling off downwards, curtains drawn at both sides with soft vertical folds."""
    n = 128
    y = np.linspace(0, 1, n)[:, None]                     # 0 top .. 1 bottom (image rows)
    x = np.linspace(0, 1, n)[None, :]
    v = 0.92 - 0.38 * y                                   # ceiling lamp: brighter above
    v = v + 0.12 * np.exp(-(((x - 0.5) / 0.22) ** 2 + ((y - 0.08) / 0.18) ** 2))
    v = np.broadcast_to(v, (n, n)).copy()
    for side in (0, 1):
        w = 0.16 + 0.08 * rng.random()
        d = x if side == 0 else 1 - x
        folds = 0.5 + 0.5 * np.sin(d * 2 * math.pi * 9 + rng.random() * 6)
        curtain = np.broadcast_to(0.42 + 0.14 * folds + 0.1 * (1 - y), (n, n))
        edge = np.clip((w - np.broadcast_to(d, (n, n))) / 0.03, 0, 1)
        v = v * (1 - edge) + curtain * edge
    v = v * (0.94 + 0.06 * fbm(n, rng, (4, 8), (1, 0.5)))
    g = np.clip(v * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(np.stack([g, g, g], -1), "RGB").filter(ImageFilter.SMOOTH)


def weather_noise(rng):
    """Data texture for JuegoDef/ENV/Weathered Lit (linear, RGBA): R low fbm (macro tone), G mid fbm (hue drift,
    damp edge), B rain streaks (fine along x, slow along y), A soft blotches (moss, flaking)."""
    n = 512
    r = fbm(n, rng, (2, 4, 8), (1.0, 0.45, 0.2))
    g = fbm(n, rng, (8, 16, 32), (1.0, 0.5, 0.25))
    streak = periodic_noise(n, 24, rng, 3) * 0.75 + periodic_noise(n, 48, rng, 6) * 0.25
    b = (streak - streak.min()) / (streak.max() - streak.min())
    a = fbm(n, rng, (4, 8, 16, 32), (1.0, 0.55, 0.3, 0.12))
    a = np.clip((a - 0.5) * 1.35 + 0.5, 0, 1)
    rgba = np.stack([r, g, b, a], -1)
    return Image.fromarray(np.clip(rgba * 255, 0, 255).astype(np.uint8), "RGBA")


def stains(rng):
    """Stain atlas for JuegoDef/ENV/Stain (2x multiply: RGB around 0.5, A = mask), 4 x 2 cells of 256 px:
    0 downpipe splash + streak, 1 corner run-off, 2 sill streaks, 3 rising damp band, 4 algae patch, 5 rust streaks,
    6 extractor soot, 7 repair patch (lighter cement render)."""
    c = 256
    out = np.zeros((2 * c, 4 * c, 4))
    y = np.linspace(0, 1, c)[:, None].repeat(c, 1)          # 0 top .. 1 bottom (image rows)
    x = np.linspace(0, 1, c)[None, :].repeat(c, 0)
    n1 = fbm(c, rng, (4, 8, 16), (1, 0.5, 0.25))
    n2 = fbm(c, rng, (8, 16, 32), (1, 0.5, 0.25))
    streak = periodic_noise(c, 24, rng, 2)
    soft = lambda v: np.clip(v, 0, 1)

    def put(k, rgb, a):
        r, col = divmod(k, 4)
        out[r * c:(r + 1) * c, col * c:(col + 1) * c, :3] = rgb
        out[r * c:(r + 1) * c, col * c:(col + 1) * c, 3] = soft(a)

    dark = np.array([0.33, 0.34, 0.31])
    # 0 downpipe: splash widening at the foot, a thin run along the pipe line
    splash = soft((y - 0.45) / 0.55) ** 1.4 * soft(1 - np.abs(x - 0.5) / (0.18 + 0.32 * soft((y - 0.4) / 0.6)))
    run = soft(1 - np.abs(x - 0.5) / 0.07) * (0.35 + 0.3 * streak)
    put(0, dark + 0.05 * n2[..., None], (np.maximum(splash, run * 0.8) * (0.7 + 0.5 * n1)))
    # 1 corner run-off: darker along the left edge, streaky, fading to the right and up
    put(1, dark + 0.04 * n2[..., None], soft(1 - x / 0.55) ** 1.5 * (0.45 + 0.55 * streak) * (0.4 + 0.6 * y) * (0.7 + 0.5 * n1))
    # 2 sill streaks: a few thin streaks from the top edge downwards
    lines = soft(periodic_noise(c, 16, rng, 1) * 1.6 - 0.6)
    put(2, dark + 0.06, lines * soft(1 - y) ** 1.2 * (0.6 + 0.6 * n2))
    # 3 rising damp: tide line with a pale salt edge, darker below
    edge = 0.45 + 0.18 * (n1 - 0.5) * 2
    below = soft((y - edge) / 0.08)
    salt = np.exp(-((y - edge + 0.03) / 0.025) ** 2) * 0.5
    rgb3 = dark[None, None, :] * below[..., None] + np.array([0.54, 0.54, 0.53])[None, None, :] * (1 - below[..., None])
    put(3, rgb3, np.maximum(below * (0.6 + 0.4 * n2), salt) * soft(1 - np.abs(x - 0.5) * 1.6 + 0.5))
    # 4 algae patch: green-black blotch
    blot = soft((n1 - 0.45) * 3.0) * soft(1 - ((x - 0.5) ** 2 + (y - 0.55) ** 2) * 3.2)
    put(4, np.array([0.36, 0.41, 0.33]) + 0.04 * n2[..., None], blot)
    # 5 rust streaks under iron
    put(5, np.array([0.52, 0.43, 0.37]) + 0.03 * n2[..., None], lines * soft(1 - y) ** 1.6 * (0.7 + 0.5 * n1))
    # 6 soot plume rising from the bottom centre
    plume = soft(1 - np.abs(x - 0.5) / (0.1 + 0.35 * (1 - y))) * soft(y ** 0.8) * (0.6 + 0.5 * n2)
    put(6, np.array([0.28, 0.27, 0.26]), plume)
    # 7 repair patch: rough-edged rectangle of fresher, lighter render with a thin dark seam
    rect = soft((0.42 - np.maximum(np.abs(x - 0.5), np.abs(y - 0.5) * 1.15) + (n1 - 0.5) * 0.12) / 0.015)
    seam = soft(1 - np.abs(0.42 - np.maximum(np.abs(x - 0.5), np.abs(y - 0.5) * 1.15) + (n1 - 0.5) * 0.12) / 0.012) * 0.6
    rgb7 = np.array([0.535, 0.532, 0.525])[None, None, :] * (1 - seam[..., None]) + dark[None, None, :] * seam[..., None]
    put(7, rgb7 + 0.02 * (n2[..., None] - 0.5), np.maximum(rect * 0.85, seam))
    img = np.clip(out * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(img, "RGBA").filter(ImageFilter.GaussianBlur(0.6))


def paint_wear(rng):
    """Tintable worn paint for own street props (ENV_PropMat_* on Weathered Lit, _BaseColor = the paint colour): a
    near-white multiplier with soft painted mottling, faint vertical grime runs, sparse chips showing a dark primer
    with a lighter lip and a few fine scratches — the softly worn, hand-painted surface of the Quaternius props."""
    n = 512
    base = 0.86 + 0.1 * quantise(fbm(n, rng), 7)
    runs = periodic_noise(n, 40, rng, 3)
    base -= 0.07 * np.clip(runs * 2.0 - 1.1, 0, 1)
    chips = fbm(n, rng, (16, 32, 64), (1.0, 0.6, 0.35))
    lip = (chips > 0.765) & (chips <= 0.79)
    hole = chips > 0.79
    base = np.where(lip, np.minimum(base + 0.05, 1.0), base)
    base = np.where(hole, 0.5 + 0.06 * fbm(n, rng, (32, 64), (1.0, 0.5)), base)
    img = Image.fromarray(np.clip(base * 255, 0, 255).astype(np.uint8), "L")
    d = ImageDraw.Draw(img)
    for _ in range(70):
        x, y = rng.random() * n, rng.random() * n
        a, length = rng.random() * math.pi, rng.uniform(6, 22)
        c = int(255 * rng.uniform(0.94, 1.0))
        for ox in (-n, 0, n):
            for oy in (-n, 0, n):
                d.line([x + ox, y + oy, x + ox + math.cos(a) * length, y + oy + math.sin(a) * length], fill=c, width=1)
    return img.filter(ImageFilter.GaussianBlur(0.7)).convert("RGB")


def granite(rng):
    """Tintable plain dressed stone for own monolith props (benches, troughs, fountain steps): soft mottling and a
    fine two-tone speckle, no joints."""
    n = 512
    base = 0.8 + 0.13 * quantise(fbm(n, rng), 6)
    sp = rng.random((n, n))
    base = np.where(sp > 0.982, base * 0.66, base)
    base = np.where(sp < 0.014, np.minimum(base * 1.1, 1.0), base)
    return Image.fromarray(np.clip(base * 255, 0, 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(0.65)).convert("RGB")


def leaves_box(_rng):
    """Green copy of the Quaternius Nature bush leaf atlas (Leaves_TwistedTree_C, CC0, autumn red): same leaf cards
    and alpha, hue turned to the dark glossy green of clipped box and bay (ENV_Src_Leaves_Box on the Quaternius
    Bush_Common: box balls, laurel heads, garden shrubs)."""
    src = os.path.join(os.path.dirname(__file__), "..", "Unity", "JuegoDef", "Assets", "ThirdParty", "Quaternius", "Nature", "Textures", "Leaves_TwistedTree_C.png")
    im = Image.open(src).convert("RGBA")
    a = im.getchannel("A")
    h, sat, v = im.convert("RGB").convert("HSV").split()
    h = h.point(lambda _: 62)                       # ~88 degrees: leaf green
    sat = sat.point(lambda x: int(x * 0.62))
    v = v.point(lambda x: int(min(255, x * 0.82)))
    out = Image.merge("HSV", (h, sat, v)).convert("RGB")
    out.putalpha(a)
    return out


def water_normal(rng):
    """Tileable ripple normal map for JuegoDef/ENV/River Water: soft fbm swell plus finer cross ripples."""
    n = 512
    h = fbm(n, rng, (4, 8, 16), (1.0, 0.5, 0.25)) * 0.7 + fbm(n, rng, (16, 32, 64), (1.0, 0.5, 0.3)) * 0.3
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * n / 24
    gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * n / 24
    nrm = np.stack([-gx, gy, np.ones_like(h)], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    return Image.fromarray(((nrm * 0.5 + 0.5) * 255).astype(np.uint8), "RGB")


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
                     ("T_ENV_Terracotta", terracotta), ("T_ENV_Foliage", foliage), ("T_ENV_Sign_Board", board),
                     ("T_ENV_Window_Glow", window_glow), ("T_ENV_Weather_Noise", weather_noise), ("T_ENV_Stains", stains), ("T_ENV_Water_Normal", water_normal),
                     ("T_ENV_PaintWear", paint_wear), ("T_ENV_Granite", granite), ("T_ENV_Leaves_Box", leaves_box)):
        path = os.path.join(a.out, name + ".png")
        fn(rng).save(path)
        print(path)


if __name__ == "__main__":
    main()

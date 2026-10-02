"""Generate small, deterministic material grain + tangent-space relief for the civilian factory.

These are shared surface-response tiles, not character-specific painted atlases. Each fabric family has an
albedo tile (near-white, multiplied by the palette colour) and a normal map derived from the same height field so
weave, knit rows, twill and leather grain actually catch the sun at review distance (3-6 m).
"""
from pathlib import Path
import math
import random
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'Unity/JuegoDef/Assets/JuegoDef/Characters/Textures'
N = 128


def height_cloth(x, y, r):          # cotton / shirting: fine plain weave (per-texel noise kept low: it mip-blurred into smudges)
    return .8 * (((x % 2) ^ (y % 2)) * 1.0) + .2 * r.random()


def height_knit(x, y, r):           # chunky wool knit: columns of stitches with V ribs
    u = x % 8
    tri = abs(u - 3.5) / 3.5
    v = (y + int(4 * tri)) % 8
    return (math.sin(math.pi * u / 8) ** 1.2) * (.55 + .45 * math.sin(math.pi * v / 8)) + .08 * r.random()


def height_denim(x, y, r):          # diagonal twill
    return ((x + y) % 4) / 3.0 * .8 + .2 * r.random()


def height_canvas(x, y, r):         # basket weave
    a = ((x // 4) + (y // 4)) % 2
    return (((x % 4) / 3.0) if a else ((y % 4) / 3.0)) * .8 + .2 * r.random()


def height_leather(x, y, r):        # pebbled grain
    return .5 + .5 * math.sin(x * .9 + math.sin(y * .7) * 2.0) * math.sin(y * .8 + math.sin(x * .5) * 2.0) * .6 + .1 * r.random()


FAMILIES = {
    'Hair': (lambda x,y,r:.5+.5*math.cos(2*math.pi*(x*16/N+2*math.sin(2*math.pi*y/N)/N)),3010,248,42,.28),
    # name: (height fn, seed, albedo base, contrast in albedo, normal strength)
    'Cloth': (height_cloth, 3001, 240, 6, 1.6),
    'Knit': (height_knit, 3005, 236, 26, 3.2),
    'Canvas': (height_canvas, 3002, 237, 16, 2.6),
    'Denim': (height_denim, 3003, 232, 18, 3.0),
    'Leather': (height_leather, 3004, 244, 12, 2.2),
}


def build(name, fn, seed, base, contrast, strength):
    rnd = random.Random(seed)
    h = [[fn(x, y, rnd) for x in range(N)] for y in range(N)]
    lo = min(min(r) for r in h); hi = max(max(r) for r in h)
    h = [[(v - lo) / (hi - lo + 1e-9) for v in r] for r in h]
    albedo = Image.new('RGB', (N, N)); normal = Image.new('RGB', (N, N))
    for y in range(N):
        for x in range(N):
            val = max(0, min(255, round(base - contrast * (1 - h[y][x]) * .8)))
            albedo.putpixel((x, y), (val, val, val))
            dx = h[y][(x + 1) % N] - h[y][(x - 1) % N]
            dy = h[(y + 1) % N][x] - h[(y - 1) % N][x]
            nx, ny, nz = -dx * strength, -dy * strength, 1.0
            ln = math.sqrt(nx * nx + ny * ny + nz * nz)
            normal.putpixel((x, y), (round((nx / ln * .5 + .5) * 255), round((ny / ln * .5 + .5) * 255), round((nz / ln * .5 + .5) * 255)))
    OUT.mkdir(parents=True, exist_ok=True)
    albedo.save(OUT / f'T_CHAR_{name}.png', optimize=True)
    normal.save(OUT / f'T_CHAR_{name}_N.png', optimize=True)


if __name__ == '__main__':
    for name, (fn, seed, base, contrast, strength) in FAMILIES.items():
        build(name, fn, seed, base, contrast, strength)
    print('CHAR_TEXTURES', ','.join(FAMILIES))

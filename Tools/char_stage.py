"""Review-stage fixture textures for CHAR captures: muted northern-Spain cobble + plaster frontage.

These are neutral scale/light references so people are judged next to stone and render at human scale.
They are NOT environment production assets; ENV owns real streets. Palette anchors come from the Visual Bible.
"""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'Unity/JuegoDef/Assets/JuegoDef/Characters/Stage'
rng = np.random.default_rng(7)


def cobble(size=512, seeds=90):
    pts = rng.uniform(0, size, (seeds, 2))
    ys, xs = np.mgrid[0:size, 0:size]
    d = np.full((size, size), 1e9); d2 = np.full((size, size), 1e9); idx = np.zeros((size, size), int)
    for i, (px, py) in enumerate(pts):
        best = None
        for ox in (-size, 0, size):
            for oy in (-size, 0, size):
                dd = np.hypot(xs - (px + ox), ys - (py + oy))
                upd = dd < d
                d2 = np.where(upd, d, np.minimum(d2, dd)); idx = np.where(upd, i, idx); d = np.where(upd, dd, d)
    edge = np.clip((d2 - d) / 9.0, 0, 1)                  # 0 at mortar, 1 inside stone
    tones = np.array([[126, 117, 104], [140, 132, 119], [111, 103, 92], [145, 138, 126], [120, 112, 100], [133, 124, 108]], float)
    base = tones[rng.integers(0, len(tones), seeds)][idx]
    noise = rng.normal(0, 5, (size, size, 1))
    stone = (base + noise) * (.78 + .22 * edge[..., None])
    mortar = np.array([64, 58, 50], float)
    color = mortar * (1 - edge[..., None]) + stone * edge[..., None]
    height = edge
    gx, gy = np.gradient(height)
    nx, ny, nz = -gx * 6, -gy * 6, np.ones_like(gx)
    ln = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    normal = np.stack([(nx / ln * .5 + .5), (ny / ln * .5 + .5), (nz / ln * .5 + .5)], -1) * 255
    return Image.fromarray(np.clip(color, 0, 255).astype('uint8')), Image.fromarray(normal.astype('uint8'))


def plaster(size=256):
    base = np.array([201, 195, 182], float)
    n = rng.normal(0, 1, (size, size))
    blur = np.zeros_like(n)
    for k in (4, 16, 48):
        small = rng.normal(0, 1, (size // k + 2, size // k + 2))
        up = np.kron(small, np.ones((k, k)))[:size, :size]
        blur += up / (k ** .3)
    m = 1 + .035 * blur / blur.std() + .01 * n
    return Image.fromarray(np.clip(base * m[..., None], 0, 255).astype('uint8'))


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    a, n = cobble()
    a.save(OUT / 'T_Stage_Cobble.png', optimize=True); n.save(OUT / 'T_Stage_Cobble_N.png', optimize=True)
    plaster().save(OUT / 'T_Stage_Plaster.png', optimize=True)
    print('CHAR_STAGE_TEXTURES')

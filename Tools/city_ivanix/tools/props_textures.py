"""Painted textures for the town's own props (Docs/design/CITY_STYLE_DCPLUS.md): foliage cards with alpha, bark,
market produce, striped canvas, boat names. Painted the way Dreamcast-era artists did: clear shapes, light from the
upper left baked in, a few colours per material, no photographic noise.

Output: Unity/JuegoDef/Assets/JuegoDef/City/Props/Textures/*.png
"""

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parents[1] / "Unity" / "JuegoDef" / "Assets" / "JuegoDef" / "City" / "Props" / "Textures"
OUT.mkdir(parents=True, exist_ok=True)
FONTS = Path("C:/Windows/Fonts")


def shade(c, k):
    return tuple(int(max(0, min(255, v * k))) for v in c)


def leaf_cluster(name, base, n_leaves, size, shape, seed, alpha_pad=0.06, flowers=None):
    """A clump of leaves on a transparent card: dark leaves first, lit ones on top, light from the upper left."""
    r = np.random.default_rng(seed)
    W = 512
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = W / 2
    for i in range(n_leaves):
        t = i / n_leaves
        ang = r.uniform(0, 2 * math.pi)
        rad = (r.uniform(0, 1) ** 0.6) * W * (0.5 - alpha_pad)
        x, y = cx + math.cos(ang) * rad, cy + math.sin(ang) * rad * 0.9
        # lit from the upper left: leaves up/left are lighter, down/right darker; later leaves (on top) lighter
        light = 0.58 + 0.40 * t + 0.22 * ((cx - x) + (cy - y)) / W
        col = shade(base, light * r.uniform(0.9, 1.1))
        s = size * r.uniform(0.7, 1.25)
        rot = r.uniform(0, math.pi)
        if shape == "lobed":
            pts = []
            for k in range(10):
                a = rot + k * 2 * math.pi / 10
                rr = s * (1.0 if k % 2 == 0 else 0.62)
                pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
            d.polygon(pts, fill=col + (255,))
        else:
            a, b = s, s * 0.45
            pts = [(x + math.cos(rot) * a * math.cos(u) - math.sin(rot) * b * math.sin(u),
                    y + math.sin(rot) * a * math.cos(u) + math.cos(rot) * b * math.sin(u)) for u in np.linspace(0, 2 * math.pi, 14)]
            d.polygon(pts, fill=col + (255,))
            d.line([pts[0], pts[7]], fill=shade(col, 0.8) + (255,), width=1)
        if flowers and r.uniform() < flowers[1]:
            fc = flowers[0][r.integers(0, len(flowers[0]))]
            fr = s * 1.2
            for k in range(9):
                fx, fy = x + r.uniform(-fr, fr) * 0.7, y + r.uniform(-fr, fr) * 0.7
                d.ellipse([fx - fr * 0.32, fy - fr * 0.32, fx + fr * 0.32, fy + fr * 0.32], fill=shade(fc, r.uniform(0.85, 1.12)) + (255,))
    img = img.filter(ImageFilter.SMOOTH)
    img.save(OUT / f"{name}.png")


def frond(name, base, seed):
    """A palm frond on a transparent card: a rib with leaflets, drawn along the card's length."""
    r = np.random.default_rng(seed)
    W, H = 256, 1024
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0 = W / 2
    for y in range(40, H - 20, 14):
        t = y / H
        length = W * 0.48 * math.sin(math.pi * min(1, t * 1.1)) + 6
        for sgn in (-1, 1):
            tip = (x0 + sgn * length, y + 46 * (0.4 + t))
            col = shade(base, 0.75 + 0.35 * (1 - t) + r.uniform(-0.06, 0.06) + (0.08 if sgn < 0 else -0.05))
            d.polygon([(x0, y), (x0, y + 10), tip], fill=col + (255,))
    d.line([(x0, 10), (x0, H - 10)], fill=shade(base, 0.6) + (255,), width=6)
    img.filter(ImageFilter.SMOOTH).save(OUT / f"{name}.png")


def bark(name, base, seed):
    r = np.random.default_rng(seed)
    W = 256
    a = np.zeros((W, W, 3), np.float32) + np.array(base, np.float32)
    for x in range(W):
        a[:, x] *= 0.85 + 0.25 * (0.5 + 0.5 * math.sin(x * 0.21 + r.uniform(0, 6))) * (0.85 + 0.15 * math.sin(x * 0.05))
    a *= np.linspace(1.06, 0.92, W)[None, :, None] if False else 1.0
    a += r.normal(0, 6, a.shape)
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.SMOOTH_MORE).save(OUT / f"{name}.png")


def produce(name, items, seed, ground=(70, 120, 50)):
    """The top of a crate full of fruit or vegetables, seen from above."""
    r = np.random.default_rng(seed)
    W = 256
    img = Image.new("RGB", (W, W), shade(ground, 0.6))
    d = ImageDraw.Draw(img)
    for i in range(110):
        col, rad = items[i % len(items)]
        x, y = r.uniform(0, W), r.uniform(0, W)
        rr = rad * r.uniform(0.85, 1.15)
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=shade(col, 0.7))
        d.ellipse([x - rr * 0.92, y - rr * 0.95, x + rr * 0.75, y + rr * 0.7], fill=col)
        d.ellipse([x - rr * 0.55, y - rr * 0.6, x - rr * 0.1, y - rr * 0.2], fill=shade(col, 1.35))
    img.filter(ImageFilter.SMOOTH).save(OUT / f"{name}.png")


def stripes(name, color, white=(240, 236, 226)):
    W, H = 256, 256
    img = Image.new("RGB", (W, H), white)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 64):
        d.rectangle([x, 0, x + 31, H], fill=color)
    img.filter(ImageFilter.SMOOTH).save(OUT / f"{name}.png")


def boat_name(name, text, color):
    """The boat's name as the painter lettered it on the bow: the largest size that fits, a thin shadow line."""
    W, H = 1024, 128
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    size = 100
    while True:
        f = ImageFont.truetype(str(FONTS / "BRITANIC.TTF"), size)
        bb = d.textbbox((0, 0), text, font=f)
        if bb[2] - bb[0] <= W * 0.92 and bb[3] - bb[1] <= H * 0.8 or size <= 20:
            break
        size -= 4
    x, y = (W - (bb[2] - bb[0])) / 2 - bb[0], (H - (bb[3] - bb[1])) / 2 - bb[1]
    d.text((x + 3, y + 3), text, font=f, fill=shade(color, 0.55) + (160,))
    d.text((x, y), text, font=f, fill=color + (255,))
    img.save(OUT / f"{name}.png")


def apple_tree_leaves(name, seed):
    """Apple-tree leaf clump: small oval leaves, a few apples among them."""
    leaf_cluster(name, (78, 124, 50), 300, 20, "oval", seed)
    img = Image.open(OUT / f"{name}.png")
    d = ImageDraw.Draw(img)
    r = np.random.default_rng(seed + 100)
    a = np.array(img)[:, :, 3]
    for i in range(26):
        for _ in range(40):
            x, y = r.integers(30, 482), r.integers(30, 482)
            if a[y, x] > 200:
                break
        col = ((186, 40, 32), (170, 52, 30), (150, 170, 60))[i % 3]
        rr = r.uniform(7, 10)
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=shade(col, 0.75) + (255,))
        d.ellipse([x - rr * 0.9, y - rr * 0.95, x + rr * 0.7, y + rr * 0.65], fill=col + (255,))
        d.ellipse([x - rr * 0.5, y - rr * 0.6, x - rr * 0.1, y - rr * 0.2], fill=shade(col, 1.4) + (255,))
    img.save(OUT / f"{name}.png")


leaf_cluster("TX_Leaves_Platano", (78, 110, 56), 260, 34, "lobed", 11)
leaf_cluster("TX_Leaves_Magnolio", (40, 78, 44), 300, 26, "oval", 12)
leaf_cluster("TX_Leaves_Laurel", (58, 96, 46), 360, 18, "oval", 13)
apple_tree_leaves("TX_Leaves_Manzano", 25)
leaf_cluster("TX_Hortensia_Azul", (58, 104, 50), 220, 22, "oval", 14, flowers=([(92, 128, 214), (128, 152, 226), (150, 120, 210)], 0.32))
leaf_cluster("TX_Hortensia_Rosa", (58, 104, 50), 220, 22, "oval", 15, flowers=([(226, 132, 176), (236, 168, 196), (200, 110, 170)], 0.32))
frond("TX_Frond_Palmera", (78, 126, 54), 16)

bark("TX_Bark_Oscura", (92, 78, 64), 18)
bark("TX_Bark_Palmera", (120, 102, 78), 19)
produce("TX_Produce_Naranjas", [((235, 128, 30), 13), ((244, 150, 40), 12)], 21)
produce("TX_Produce_Manzanas", [((190, 40, 36), 12), ((120, 170, 50), 12), ((210, 60, 40), 11)], 22)
produce("TX_Produce_Lechugas", [((98, 168, 64), 20), ((130, 190, 80), 17)], 23)
produce("TX_Produce_Pimientos", [((200, 30, 28), 11), ((40, 130, 40), 11), ((236, 196, 40), 11)], 24)
for nm, c in (("Rojo", (178, 40, 36)), ("Verde", (40, 110, 60)), ("Azul", (36, 80, 150)), ("Amarillo", (226, 182, 40))):
    stripes(f"TX_Lona_{nm}", c)
for i, (t, c) in enumerate((("VIRGEN DEL CARMEN", (30, 50, 110)), ("NUEVO RIVAS", (140, 30, 30)), ("MAR DE LLANES", (20, 80, 50)), ("HERMANOS COBO", (30, 30, 30)))):
    boat_name(f"TX_BoatName_{i}", t, c)

def hand_font(size):
    for f in ("segoepr.ttf", "Inkfree.ttf", "comic.ttf", "arial.ttf"):
        if (FONTS / f).exists():
            return ImageFont.truetype(str(FONTS / f), size)
    return ImageFont.load_default()


def fit_text(d, text, font_fn, max_w, start):
    size = start
    while size > 10:
        f = font_fn(size)
        bb = d.textbbox((0, 0), text, font=f)
        if bb[2] - bb[0] <= max_w:
            return f, bb
        size -= 2
    f = font_fn(10)
    return f, d.textbbox((0, 0), text, font=f)


def price_card(name, item, price):
    """A market price card: white card, the product and the price per kilo in marker, pesetas (around 2000)."""
    W, H = 256, 160
    img = Image.new("RGB", (W, H), (244, 242, 232))
    d = ImageDraw.Draw(img)
    d.rectangle([2, 2, W - 3, H - 3], outline=(170, 160, 140), width=3)
    f, bb = fit_text(d, item, hand_font, W - 24, 46)
    d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], 12 - bb[1]), item, font=f, fill=(30, 50, 120))
    f, bb = fit_text(d, price, hand_font, W - 24, 52)
    d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], 80 - bb[1]), price, font=f, fill=(180, 30, 26))
    img.filter(ImageFilter.SMOOTH).save(OUT / f"{name}.png")


def cardboard_sign(name, lines):
    """A piece of cardboard with the offer in thick marker."""
    W, H = 512, 300
    r = np.random.default_rng(31)
    a = np.zeros((H, W, 3), np.float32) + np.array((176, 140, 92), np.float32)
    a += r.normal(0, 6, a.shape)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.SMOOTH_MORE)
    d = ImageDraw.Draw(img)
    y = 20
    for text, col, size in lines:
        f, bb = fit_text(d, text, hand_font, W - 40, size)
        d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], y - bb[1]), text, font=f, fill=col)
        y += (bb[3] - bb[1]) + 26
    img.save(OUT / f"{name}.png")


def chalkboard(name, lines):
    W, H = 384, 512
    r = np.random.default_rng(32)
    a = np.zeros((H, W, 3), np.float32) + np.array((38, 46, 42), np.float32)
    a += r.normal(0, 4, a.shape)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.SMOOTH_MORE)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=(120, 86, 52), width=16)
    y = 46
    for text, col, size in lines:
        f, bb = fit_text(d, text, hand_font, W - 70, size)
        d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], y - bb[1]), text, font=f, fill=col)
        y += (bb[3] - bb[1]) + 34
    img.filter(ImageFilter.SMOOTH).save(OUT / f"{name}.png")


def sobaos_label(name):
    """The printed end of a box of sobaos: blue and white, a cow, the word in red."""
    W, H = 256, 96
    img = Image.new("RGB", (W, H), (246, 244, 236))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 22], fill=(32, 76, 150))
    d.rectangle([0, H - 18, W, H], fill=(32, 76, 150))
    f = ImageFont.truetype(str(FONTS / "COOPBL.TTF"), 30)
    bb = d.textbbox((0, 0), "SOBAOS", font=f)
    d.text(((W - (bb[2] - bb[0])) / 2 - bb[0] + 20, 30 - bb[1]), "SOBAOS", font=f, fill=(190, 30, 26))
    d.ellipse([14, 30, 54, 70], fill=(250, 250, 250), outline=(20, 20, 20), width=3)     # the cow's head, as the logos do
    d.ellipse([22, 42, 30, 50], fill=(20, 20, 20))
    d.ellipse([38, 42, 46, 50], fill=(20, 20, 20))
    img.filter(ImageFilter.SMOOTH).save(OUT / f"{name}.png")


def garments(name):
    """Four hanging garments on a transparent 2x2 sheet: a shirt, jeans, a jumper, a print dress."""
    W = 512
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    def shirt(ox, oy, col):
        c = col + (255,)
        d.polygon([(ox + 70, oy + 30), (ox + 186, oy + 30), (ox + 236, oy + 80), (ox + 206, oy + 110), (ox + 186, oy + 92),
                   (ox + 186, oy + 236), (ox + 70, oy + 236), (ox + 70, oy + 92), (ox + 50, oy + 110), (ox + 20, oy + 80)], fill=c)
        d.polygon([(ox + 108, oy + 30), (ox + 148, oy + 30), (ox + 128, oy + 60)], fill=shade(col, 0.6) + (255,))
        d.line([(ox + 128, oy + 60), (ox + 128, oy + 236)], fill=shade(col, 0.8) + (255,), width=3)
    def jeans(ox, oy, col):
        c = col + (255,)
        d.polygon([(ox + 64, oy + 24), (ox + 192, oy + 24), (ox + 206, oy + 244), (ox + 140, oy + 244), (ox + 128, oy + 100),
                   (ox + 116, oy + 244), (ox + 50, oy + 244)], fill=c)
        d.rectangle([ox + 64, oy + 24, ox + 192, oy + 40], fill=shade(col, 0.75) + (255,))
    def dress(ox, oy, col):
        d.polygon([(ox + 90, oy + 24), (ox + 166, oy + 24), (ox + 176, oy + 90), (ox + 222, oy + 246), (ox + 34, oy + 246), (ox + 80, oy + 90)], fill=col + (255,))
        rr = np.random.default_rng(5)
        for _ in range(60):
            x, y = ox + rr.uniform(60, 196), oy + rr.uniform(100, 236)
            d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(246, 240, 220, 255))
    shirt(0, 0, (214, 206, 186))
    jeans(256, 0, (52, 76, 120))
    shirt(0, 256, (150, 40, 44))
    dress(256, 256, (40, 88, 70))
    img.save(OUT / f"{name}.png")


def bark_platano(name, seed):
    """Plane-tree bark: the camouflage of flaking patches, olive, grey and cream."""
    r = np.random.default_rng(seed)
    W = 256
    img = Image.new("RGB", (W, W), (128, 124, 100))
    d = ImageDraw.Draw(img)
    cols = [(150, 146, 118), (188, 180, 150), (112, 112, 92), (170, 164, 128), (96, 100, 82)]
    for i in range(70):
        x, y = r.uniform(0, W), r.uniform(0, W)
        w, h = r.uniform(18, 50), r.uniform(26, 80)
        col = cols[i % len(cols)]
        pts = [(x + math.cos(a) * w * r.uniform(0.7, 1.1), y + math.sin(a) * h * r.uniform(0.7, 1.1)) for a in np.linspace(0, 2 * math.pi, 9, endpoint=False)]
        for dx in (-W, 0, W):
            for dy in (-W, 0, W):
                d.polygon([(px + dx, py + dy) for px, py in pts], fill=col)
    img.filter(ImageFilter.SMOOTH_MORE).save(OUT / f"{name}.png")


for i, (it, pr) in enumerate((("Naranjas", "120 pts/kg"), ("Lechugas", "75 pts/u."), ("Manzanas", "150 pts/kg"))):
    price_card(f"TX_Precio_{i}", it, pr)
cardboard_sign("TX_Cartel_Ropa", [("TODO A", (20, 20, 20), 70), ("1.000 pts", (176, 24, 20), 96)])
chalkboard("TX_Cartel_Quesos", [("QUESOS", (240, 236, 220), 64), ("del valle", (236, 214, 120), 44), ("SOBAOS", (240, 236, 220), 60),
                                ("QUESADAS", (240, 236, 220), 50), ("MIEL", (236, 214, 120), 56)])
sobaos_label("TX_Sobaos")
garments("TX_Ropa")
bark_platano("TX_Bark_Platano", 17)

print("props textures ->", OUT)

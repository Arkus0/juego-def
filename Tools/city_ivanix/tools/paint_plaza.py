"""Painted surfaces for the hand-authored Plaza Mayor slice (WP-CITY-IVX-HUMAN-01).

Shenmue 2 manner (Docs/design/city_ivx/PLAZA_MAYOR_BRIEF.md, section 0): every surface the player sees at 3 m is a
unique painted texture that carries its own wear, light and lettering. Each function below paints ONE authored surface
(a shutter, a poster, a chalkboard, a plate...) whose text and look were decided in the brief; nothing is drawn by
quota. Light is painted in: contact shadow under ledges, darker joints, a lighter top where the sky reaches.

Output: Unity/JuegoDef/Assets/JuegoDef/City/Authored/PlazaMayor/Textures (PNG; decals with alpha).
Stain decals (JuegoDef/ENV/Stain, 2x multiply) are authored around mid grey: darker = dirt, A = mask.
Fonts: Windows faces for look-dev only, as the shop signs; to be swapped for OFL faces before release.
Usage: python paint_plaza.py [name ...]   (no names = all)
"""

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parents[1] / "Unity" / "JuegoDef" / "Assets" / "JuegoDef" / "City" / "Authored" / "PlazaMayor" / "Textures"
FONTS = Path("C:/Windows/Fonts")
RNG = np.random.default_rng(1887)          # the fountain's year: fixed seed, the paint is the same every run


# ------------------------------------------------------------------ helpers

def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def noise(w, h, cell, octaves=4, seed=0):
    """Smooth value noise in [0, 1] (bilinear upsampled lattices, summed octaves)."""
    rng = np.random.default_rng(seed)
    acc = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        c = max(1, int(cell / (2 ** o)))
        g = rng.random((h // c + 2, w // c + 2)).astype(np.float32)
        img = Image.fromarray((g * 255).astype(np.uint8)).resize(((w // c + 2) * c, (h // c + 2) * c), Image.BILINEAR)
        acc += amp * (np.asarray(img, np.float32)[:h, :w] / 255.0)
        tot += amp
        amp *= 0.5
    return acc / tot


def to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def mul(img, f):
    a = np.asarray(img.convert("RGB"), np.float32)
    if f.ndim == 2:
        f = f[:, :, None]
    return to_img(a * f)


def streaks(w, h, count, seed, length=(0.3, 0.9), width=(2, 7), strength=0.35):
    """Rain streaks from the top edge: a multiplicative darkening field (1 = clean)."""
    rng = np.random.default_rng(seed)
    f = np.ones((h, w), np.float32)
    for _ in range(count):
        x = rng.uniform(0, w)
        L = rng.uniform(*length) * h
        wd = rng.uniform(*width)
        y0 = rng.uniform(0, 0.15) * h
        ys = np.arange(h, dtype=np.float32)
        fall = np.clip(1 - (ys - y0) / L, 0, 1) * (ys >= y0)
        xs = np.arange(w, dtype=np.float32)
        prof = np.exp(-((xs[None, :] - x - 3 * np.sin(ys[:, None] / 40)) ** 2) / (2 * wd * wd))
        f -= strength * rng.uniform(0.4, 1) * fall[:, None] * prof
    return np.clip(f, 0.35, 1)


def edge_ao(w, h, top=0.0, bottom=0.0, left=0.0, right=0.0, size=0.12):
    """Painted contact shadow along chosen edges (multiplicative)."""
    ys = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    xs = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    f = np.ones((h, w), np.float32)
    f *= 1 - top * np.clip(1 - ys / size, 0, 1) ** 2
    f *= 1 - bottom * np.clip(1 - (1 - ys) / size, 0, 1) ** 2
    f *= 1 - left * np.clip(1 - xs / size, 0, 1) ** 2
    f *= 1 - right * np.clip(1 - (1 - xs) / size, 0, 1) ** 2
    return f


def text_center(d, box, text, f, fill, stroke=0, stroke_fill=None, spacing=4):
    x0, y0, x1, y1 = box
    bb = d.multiline_textbbox((0, 0), text, font=f, spacing=spacing, align="center")
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.multiline_text((x0 + (x1 - x0 - tw) / 2 - bb[0], y0 + (y1 - y0 - th) / 2 - bb[1]), text, font=f, fill=fill,
                     spacing=spacing, align="center", stroke_width=stroke, stroke_fill=stroke_fill)


def fit_font(d, text, name, w, h, start=None):
    size = start or h
    while size > 8:
        f = font(name, size)
        bb = d.multiline_textbbox((0, 0), text, font=f, align="center")
        if bb[2] - bb[0] <= w and bb[3] - bb[1] <= h:
            return f
        size -= 2
    return font(name, 8)


def paper(w, h, base, seed, wrinkle=0.08, age=0.15):
    """A printed sheet: base colour, fibre noise, a little yellowing at the edges, soft creases."""
    n = noise(w, h, 24, 3, seed)
    a = np.ones((h, w, 3), np.float32) * np.array(base, np.float32)
    a *= (1 - wrinkle / 2 + wrinkle * n)[:, :, None]
    yel = edge_ao(w, h, 0.5, 0.5, 0.5, 0.5, 0.18)
    a[:, :, 2] *= 1 - age * (1 - yel)
    return to_img(a)


def save(img, name):
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / f"{name}.png")
    print("painted", name, img.size)


def alpha_from(img_rgb, mask):
    rgba = img_rgb.convert("RGBA")
    rgba.putalpha(mask)
    return rgba


# ------------------------------------------------------------------ authored surfaces

def poster_fiestas(w=512, h=724, seed=15):
    """Programme poster of the fiestas (15-17 Sept 2000), two-ink print on yellow, as the town printer did it."""
    img = paper(w, h, (246, 214, 70), seed, 0.06, 0.1)
    d = ImageDraw.Draw(img)
    red, blue = (196, 30, 36), (26, 52, 128)
    d.rectangle([14, 14, w - 15, h - 15], outline=red, width=6)
    text_center(d, (24, 30, w - 24, 92), "FIESTAS DE", font("GILLUBCD.TTF", 52), red)
    text_center(d, (24, 88, w - 24, 196), "NUESTRA SEÑORA\nDEL MUELLE", font("GILLUBCD.TTF", 54), blue, spacing=0)
    # the woodcut: the Virgin's boat on three waves, a burst of fireworks over it
    cx, cy = w // 2, 300
    for k, r in enumerate((70, 52, 34)):
        for a in range(0, 360, 20):
            t = math.radians(a + k * 7)
            d.line([cx + 0.3 * r * math.cos(t), cy - 40 + 0.3 * r * math.sin(t), cx + r * math.cos(t), cy - 40 + r * math.sin(t)], fill=red, width=3)
    d.polygon([(cx - 110, 360), (cx + 110, 360), (cx + 80, 392), (cx - 80, 392)], fill=blue)
    d.line([cx, 360, cx, 300], fill=blue, width=5)
    d.polygon([(cx + 4, 302), (cx + 60, 350), (cx + 4, 350)], fill=(250, 240, 220), outline=blue)
    for k in range(3):
        y = 400 + k * 14
        d.arc([cx - 150, y, cx - 50, y + 22], 200, 340, fill=blue, width=4)
        d.arc([cx - 50, y, cx + 50, y + 22], 200, 340, fill=blue, width=4)
        d.arc([cx + 50, y, cx + 150, y + 22], 200, 340, fill=blue, width=4)
    text_center(d, (24, 448, w - 24, 500), "15 · 16 · 17 de SEPTIEMBRE · 2000", font("ariblk.ttf", 22), red)
    lines = ("Viernes 15 · 23:00 h  Pregón y VERBENA\ncon la orquesta  LOS SATÉLITES\n"
             "Sábado 16 · Concurso de pesca · Gigantes\ny cabezudos · Fuegos artificiales\n"
             "Domingo 17 · Misa y procesión marinera")
    text_center(d, (30, 504, w - 30, 650), lines, font("bahnschrift.ttf", 21), blue, spacing=5)
    text_center(d, (24, 656, w - 24, 696), "Organiza: Comisión de Fiestas · Colabora: Ayuntamiento", font("bahnschrift.ttf", 15), red)
    img = img.filter(ImageFilter.GaussianBlur(0.4))
    f = streaks(w, h, 6, seed + 1, (0.2, 0.6), (3, 10), 0.18) * edge_ao(w, h, 0.25, 0.1, 0.1, 0.1, 0.06)
    return mul(img, f)


def card_se_traspasa(w=360, h=260, seed=3):
    img = paper(w, h, (240, 238, 228), seed, 0.05, 0.25)
    d = ImageDraw.Draw(img)
    text_center(d, (10, 12, w - 10, 140), "SE\nTRASPASA", font("ariblk.ttf", 64), (200, 20, 24), spacing=0)
    text_center(d, (10, 150, w - 10, 250), "Razón:\n942 81 23 47", font("Inkfree.ttf", 40), (30, 30, 120), spacing=2)
    # tape at the corners
    for (x, y) in ((0, 0), (w - 46, 0), (0, h - 22), (w - 46, h - 22)):
        d.rectangle([x, y, x + 46, y + 22], fill=(226, 214, 168))
    return img


def shutter(variant, w=512, h=784):
    """Galvanised roller shutter of the closed shop (R0124, Tejidos Lavín, closed 1998), each bay its own story."""
    seed = 40 + variant
    rng = np.random.default_rng(seed)
    slat = 22
    ys = np.arange(h, dtype=np.float32)[:, None]
    band = 0.84 + 0.16 * np.cos((ys % slat) / slat * 2 * math.pi) ** 2
    groove = np.where((ys % slat) < 3, 0.62, 1.0)
    base = np.array((150, 158, 150), np.float32) if variant != 1 else np.array((96, 120, 98), np.float32)   # one painted green once
    n = noise(w, h, 40, 4, seed)
    a = base * (band * groove)[:, :, None] * (0.85 + 0.3 * n)[:, :, None]
    # galvanising showing through the old paint, rust at the bottom slats
    if variant == 1:
        peel = noise(w, h, 18, 3, seed + 5) > 0.62
        a[peel] = a[peel] * 0 + np.array((160, 163, 158))
    rust = (noise(w, h, 12, 3, seed + 9) * np.clip((ys - h * 0.7) / (h * 0.3), 0, 1)) > 0.42
    a[rust] = a[rust] * 0.55 + np.array((120, 64, 30)) * 0.45
    img = to_img(a)
    d = ImageDraw.Draw(img)
    # bottom bar, the two lock lugs and the padlock
    d.rectangle([0, h - 40, w, h - 22], fill=(84, 86, 82))
    for x in (w * 0.2, w * 0.8):
        d.rectangle([x - 12, h - 52, x + 12, h - 24], fill=(70, 70, 66))
    d.ellipse([w * 0.8 - 14, h - 30, w * 0.8 + 14, h - 4], fill=(150, 120, 40), outline=(60, 50, 20), width=3)
    if variant == 0:
        img.paste(card_se_traspasa().rotate(2, expand=True, fillcolor=(0, 0, 0)), (int(w * 0.16), int(h * 0.30)))
    elif variant == 1:
        old = poster_fiestas(320, 452, 99).crop((0, 140, 320, 452))          # last year's poster, torn
        oa = np.asarray(old.convert("RGBA"))
        tear = noise(320, 312, 30, 3, 7) > 0.45
        oa = oa.copy(); oa[~tear, 3] = 0
        img.paste(Image.fromarray(oa), (40, 430), Image.fromarray(oa))
        img.paste(poster_fiestas(300, 424, 15).rotate(-3, expand=True, fillcolor=(96, 120, 98)), (150, 70))
    else:
        d.text((40, 120), "PROHIBIDO FIJAR CARTELES", font=font("STENCIL.TTF", 30), fill=(40, 40, 40))
        d.text((60, 470), "kiko 99", font=font("Inkfree.ttf", 70), fill=(20, 20, 24))
        img.paste(poster_fiestas(220, 311, 16).rotate(4, expand=True, fillcolor=(150, 158, 150)), (250, 180))
        for k in range(5):                                                  # scraps of older stickers
            x, y = rng.integers(30, w - 90), rng.integers(300, 700)
            d.rectangle([x, y, x + rng.integers(30, 80), y + rng.integers(20, 50)], fill=tuple(int(c) for c in rng.integers(150, 240, 3)))
    f = streaks(w, h, 14, seed, (0.3, 1.0), (2, 6), 0.28) * edge_ao(w, h, 0.45, 0.35, 0.2, 0.2, 0.08)
    return mul(img, f)


def ghost_tejidos(w=1024, h=192, seed=8):
    """Where the draper's board hung: a cleaner rectangle of plaster, its dirty outline, holes, the painted letters
    under it surviving faded (stain decal: grey 128 = no change)."""
    a = np.full((h, w, 3), 128, np.float32)
    m = np.zeros((h, w), np.float32)
    x0, y0, x1, y1 = 40, 30, w - 40, h - 30
    inner = np.zeros((h, w), np.float32); inner[y0:y1, x0:x1] = 1
    blur = np.asarray(Image.fromarray((inner * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10)), np.float32) / 255
    ring = np.clip(blur * (1 - inner) * 3, 0, 1)
    a += (inner * 20)[:, :, None]                    # the plaster under the board stayed clean
    a -= (ring * 48)[:, :, None]                     # grime gathered round its edge
    txt = Image.new("L", (w, h), 0)
    ImageDraw.Draw(txt).text((w // 2, h // 2), "TEJIDOS  LAVÍN", font=font("ROCKEB.TTF", 92), fill=255, anchor="mm")
    t = np.asarray(txt, np.float32) / 255 * (noise(w, h, 10, 3, seed) > 0.38)
    a = a * (1 - 0.35 * t[:, :, None]) + np.array((150, 96, 60)) * 0.35 * t[:, :, None]
    for (x, y) in ((x0 + 14, y0 + 14), (x1 - 14, y0 + 14), (x0 + 14, y1 - 14), (x1 - 14, y1 - 14), (w // 2, y0 + 14)):
        a[y - 4:y + 4, x - 4:x + 4] = 60                                  # screw holes
    m = np.clip(blur * 1.3 + ring, 0, 1)
    return alpha_from(to_img(a), Image.fromarray((m * 255).astype(np.uint8)))


def chalkboard(w=384, h=560, seed=21):
    """Sidrería Casa Bustamante's A-frame, written this morning by Pepe."""
    n = noise(w, h, 30, 4, seed)
    a = np.ones((h, w, 3), np.float32) * np.array((34, 46, 40)) * (0.85 + 0.3 * n)[:, :, None]
    ghost = noise(w, h, 6, 2, seed + 3) > 0.7                               # rubbed-out chalk of other days
    a[ghost] += 14
    img = to_img(a)
    d = ImageDraw.Draw(img)
    chalk = (236, 234, 222)
    d.rectangle([0, 0, w - 1, h - 1], outline=(120, 82, 48), width=18)
    text_center(d, (24, 26, w - 24, 92), "Casa Bustamante", font("SCRIPTBL.TTF", 40), (250, 226, 150))
    text_center(d, (24, 96, w - 24, 150), "MENÚ DEL DÍA", font("Inkfree.ttf", 40), chalk)
    text_center(d, (24, 146, w - 24, 196), "1.200 pts", font("Inkfree.ttf", 44), (255, 214, 120))
    body = "Fabada\nMerluza a la sidra\n·\nArroz con leche\nQuesada\n\nSIDRA DEL AÑO"
    text_center(d, (24, 200, w - 24, 500), body, font("Inkfree.ttf", 34), chalk, spacing=6)
    d.line([80, 506, w - 80, 506], fill=chalk, width=3)
    text_center(d, (24, 508, w - 24, 545), "pincho de tortilla con la sidra", font("Inkfree.ttf", 22), chalk)
    img = img.filter(ImageFilter.GaussianBlur(0.5))
    return mul(img, edge_ao(w, h, 0.3, 0.2, 0.15, 0.15, 0.06))


def vinyl_sidreria(w=1024, h=512):
    """White cut-vinyl letters on the bar's display glass (alpha)."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    white = (245, 243, 236, 255)
    text_center(d, (0, 40, w, 150), "COMIDAS  y  RACIONES", font("COOPBL.TTF", 76), white)
    text_center(d, (0, 160, w, 250), "SIDRA NATURAL", font("COOPBL.TTF", 64), (226, 196, 90, 255))
    text_center(d, (0, 400, w, 460), "Cerrado los lunes", font("bahnschrift.ttf", 34), white)
    return img


def sawdust(w=512, h=512, seed=31):
    """Serrín at the bar door: specks on the setts, denser where the feet go (stain decal)."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w / 2) / (w * 0.45)) ** 2 + ((yy - h * 0.38) / (h * 0.42)) ** 2)
    dens = np.clip(1 - r, 0, 1) ** 0.7 * (0.6 + 0.6 * noise(w, h, 60, 3, seed))
    speck = (np.random.default_rng(seed).random((h, w)) < dens * 0.55).astype(np.float32)
    speck = np.asarray(Image.fromarray((speck * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)), np.float32) / 255
    a = np.full((h, w, 3), 128, np.float32) + speck[:, :, None] * np.array((80, 52, 10))
    return alpha_from(to_img(a), Image.fromarray(np.clip(speck * 255 * 1.4, 0, 255).astype(np.uint8)))


def caja_fascia(w=1024, h=160):
    blue, red = (22, 66, 140), (200, 36, 40)
    a = np.ones((h, w, 3), np.float32) * np.array(blue) * np.linspace(1.12, 0.88, h)[:, None, None]
    img = to_img(a)
    d = ImageDraw.Draw(img)
    d.rectangle([0, h - 12, w, h], fill=red)
    cx, cy, r = 86, 72, 50                                     # the logo: a white sun over two waves
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(250, 250, 250))
    d.ellipse([cx - 22, cy - 34, cx + 22, cy + 10], fill=(250, 200, 60))
    for k, yo in enumerate((12, 28)):
        d.arc([cx - 46, cy + yo - 12, cx, cy + yo + 12], 200, 340, fill=blue, width=7)
        d.arc([cx, cy + yo - 12, cx + 46, cy + yo + 12], 200, 340, fill=blue, width=7)
    text_center(d, (160, 10, w - 20, 100), "CAJA DE AHORROS DEL NORTE", font("bahnschrift.ttf", 62), (255, 255, 255))
    text_center(d, (160, 96, w - 20, 146), "Sucursal  Plaza Mayor  ·  Oficina 0217", font("bahnschrift.ttf", 30), (210, 222, 245))
    return mul(img, edge_ao(w, h, 0.2, 0.1, 0.05, 0.05, 0.1) * streaks(w, h, 5, 77, (0.3, 0.8), (3, 8), 0.12))


def caja_atm(w=512, h=768, seed=24):
    """The new cash machine set into the old wall (1999): steel fascia, blue header, the screen awake."""
    n = noise(w, h, 8, 2, seed)
    a = np.ones((h, w, 3), np.float32) * np.array((168, 172, 176)) * (0.9 + 0.12 * n)[:, :, None]
    img = to_img(a)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 110], fill=(22, 66, 140))
    text_center(d, (0, 4, w, 62), "24 HORAS", font("bahnschrift.ttf", 54), (255, 255, 255))
    text_center(d, (0, 60, w, 106), "CAJERO AUTOMÁTICO · CAJA NORTE", font("bahnschrift.ttf", 26), (210, 222, 245))
    d.rectangle([90, 150, w - 90, 370], fill=(30, 30, 34))                                  # screen bezel
    scr = np.ones((200, w - 200, 3), np.float32) * np.linspace(np.array((40, 90, 200)), np.array((20, 50, 140)), 200)[:, None, :]
    img.paste(to_img(scr), (100, 160))
    text_center(d, (100, 175, w - 100, 360), "BIENVENIDO\n\nIntroduzca\nsu tarjeta", font("bahnschrift.ttf", 32), (255, 255, 255), spacing=4)
    for i in range(4):                                                                      # side keys
        for x in (60, w - 84):
            d.rectangle([x, 175 + i * 46, x + 24, 175 + i * 46 + 26], fill=(110, 112, 116))
    for r_ in range(4):                                                                     # keypad
        for c in range(3):
            x, y = 150 + c * 58, 420 + r_ * 50
            d.rectangle([x, y, x + 46, y + 38], fill=(206, 208, 210), outline=(90, 90, 94), width=2)
            d.text((x + 23, y + 19), "123456789*0#"[r_ * 3 + c], font=font("bahnschrift.ttf", 24), fill=(30, 30, 30), anchor="mm")
    for k, col in enumerate(((200, 40, 40), (230, 200, 40), (40, 160, 70))):
        d.rectangle([340, 420 + k * 50, 400, 458 + k * 50], fill=col)
    d.rectangle([150, 640, 400, 660], fill=(40, 40, 42))                                    # cash slot
    d.rectangle([380, 140 - 20, 470, 136], fill=(60, 60, 62))                               # card slot (top right)
    text_center(d, (0, 690, w, 760), "Telebanco Norte  902 10 20 30", font("bahnschrift.ttf", 24), (50, 50, 60))
    f = edge_ao(w, h, 0.25, 0.3, 0.25, 0.25, 0.08) * streaks(w, h, 6, seed, (0.2, 0.6), (2, 5), 0.15)
    return mul(img, f)


def vinyl_caja(w=1024, h=512):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    card = poster_plan()
    img.paste(card, (60, 40))
    text_center(d, (560, 300, w - 30, 470), "Horario de atención al público\nde lunes a viernes\n8:30 a 14:00",
                font("bahnschrift.ttf", 34), (245, 245, 245, 255), spacing=6)
    return img


def poster_plan(w=420, h=440):
    img = Image.new("RGB", (w, h), (250, 250, 248))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 120], fill=(22, 66, 140))
    text_center(d, (10, 10, w - 10, 110), "PLAN DE\nPENSIONES NORTE", font("bahnschrift.ttf", 44), (255, 255, 255), spacing=0)
    text_center(d, (10, 140, w - 10, 260), "5,25 %\nTAE", font("ariblk.ttf", 64), (200, 36, 40), spacing=0)
    text_center(d, (10, 280, w - 10, 420), "Su futuro,\nen buenas manos.\nPregunte en su oficina.", font("georgiai.ttf", 30), (40, 50, 80), spacing=6)
    return img


def plate_calle_mayor(w=512, h=256, seed=12):
    """Glazed tile street plate (4 x 2 azulejos), blue on white, one chipped corner."""
    a = np.ones((h, w, 3), np.float32) * np.array((240, 240, 232))
    a *= (0.96 + 0.06 * noise(w, h, 20, 2, seed))[:, :, None]
    img = to_img(a)
    d = ImageDraw.Draw(img)
    blue = (32, 62, 150)
    d.rectangle([8, 8, w - 9, h - 9], outline=blue, width=14)
    d.rectangle([28, 28, w - 29, h - 29], outline=blue, width=3)
    for (x, y) in ((28, 28), (w - 29, 28), (28, h - 29), (w - 29, h - 29)):
        d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=blue)
    text_center(d, (40, 40, w - 40, h - 40), "CALLE\nMAYOR", font("georgiab.ttf", 70), blue, spacing=-4)
    for x in range(0, w, w // 4):                                             # tile joints
        d.line([x, 0, x, h], fill=(200, 196, 186), width=3)
    d.line([0, h // 2, w, h // 2], fill=(200, 196, 186), width=3)
    d.polygon([(w - 60, h), (w, h - 50), (w, h)], fill=(190, 170, 140))      # chipped corner
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    return mul(img, edge_ao(w, h, 0.2, 0.35, 0.15, 0.15, 0.1))


def banderines(w=1024, h=128, seed=17):
    """Plastic pennants on a cord, eight to the metre of texture (the ribbon tiles along its length)."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cols = [(214, 40, 40), (250, 214, 40), (250, 250, 246), (40, 120, 200), (50, 160, 80), (240, 130, 40)]
    n = 8
    for i in range(n):
        x0 = i * w / n + 4
        x1 = (i + 1) * w / n - 4
        c = cols[(i * 5 + 1) % len(cols)]
        d.polygon([(x0, 10), (x1, 10), ((x0 + x1) / 2, h - 6)], fill=c + (255,))
        d.line([(x0, 10), ((x0 + x1) / 2, h - 6)], fill=tuple(int(v * 0.75) for v in c) + (255,), width=2)
    d.rectangle([0, 6, w, 12], fill=(230, 230, 220, 255))                    # the cord
    return img


def streak_decal(variant, w=128, h=512):
    """A sill's drip down the render (stain decal)."""
    f = streaks(w, h, 3 + variant, 60 + variant, (0.5, 1.0), (5, 14), 0.5)
    a = np.full((h, w, 3), 128, np.float32) * f[:, :, None]
    a[:, :, 1] *= 1.02
    mask = np.clip((1 - f) * 3, 0, 1)
    return alpha_from(to_img(a), Image.fromarray((mask * 255).astype(np.uint8)))


def damp_plinth(w=512, h=256, seed=50):
    """Rising damp at the foot of a wall: darker and greener at the bottom, ragged tide line (stain decal)."""
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    edge = 0.35 + 0.25 * noise(w, 1, 40, 3, seed)[0][None, :]
    m = np.clip((yy - edge) / 0.12 + 0.5, 0, 1) * (0.7 + 0.3 * noise(w, h, 16, 3, seed + 1))
    a = np.full((h, w, 3), 128, np.float32) - m[:, :, None] * np.array((40, 30, 46))
    return alpha_from(to_img(a), Image.fromarray((np.clip(m, 0, 1) * 220).astype(np.uint8)))


def granite_flags(w=1024, h=1024, seed=6):
    """Calle Mayor: dressed granite slabs 50 x 33 cm in running courses (tile = 2 m), each slab its own grey, dark
    joints, worn polish down the middle, chewing-gum spots and an old oil stain (ground class LOSA)."""
    rng = np.random.default_rng(seed)
    px = w / 2.0                      # px per metre
    a = np.zeros((h, w, 3), np.float32)
    grain = noise(w, h, 3, 2, seed) * 0.5 + noise(w, h, 9, 2, seed + 1) * 0.5
    sw, sh = int(0.5 * px), int(round(h / 6))
    for row in range(6):
        y0 = row * sh
        off = (row % 2) * sw // 2
        for k in range(-1, w // sw + 2):
            x0 = k * sw + off
            tone = rng.uniform(0.82, 1.08)
            warm = rng.uniform(-6, 6)
            col = np.array((150 + warm, 148, 142 - warm)) * tone
            xa, xb = max(0, x0), min(w, x0 + sw)
            if xa >= xb:
                continue
            a[y0:y0 + sh, xa:xb] = col
    a *= (0.8 + 0.4 * grain)[:, :, None]
    joints = np.zeros((h, w), np.float32)
    for row in range(7):
        y = (row * sh) % h
        joints[max(0, y - 2):y + 2, :] = 1
    for row in range(6):
        off = (row % 2) * sw // 2
        for k in range(-1, w // sw + 2):
            x = k * sw + off
            if 0 <= x < w:
                joints[row * sh:(row + 1) * sh, max(0, x - 2):x + 2] = 1
    jb = np.asarray(Image.fromarray((joints * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)), np.float32) / 255
    a *= (1 - 0.55 * jb)[:, :, None]
    a *= (1 - 0.7 * joints)[:, :, None]
    for _ in range(40):                                                   # gum spots
        x, y, r = rng.integers(0, w), rng.integers(0, h), rng.integers(3, 7)
        a[max(0, y - r):y + r, max(0, x - r):x + r] *= 0.72
    oil = noise(w, h, 80, 3, seed + 9)
    a *= (1 - 0.25 * np.clip((oil - 0.62) * 6, 0, 1))[:, :, None]
    return to_img(a).filter(ImageFilter.GaussianBlur(0.5))


SURFACES = {
    "PM_Cartel_Fiestas": poster_fiestas,
    "PM_Persiana_A": lambda: shutter(0),
    "PM_Persiana_B": lambda: shutter(1),
    "PM_Persiana_C": lambda: shutter(2),
    "PM_Fantasma_Tejidos": ghost_tejidos,
    "PM_Pizarra_Sidreria": chalkboard,
    "PM_Vinilo_Sidreria": vinyl_sidreria,
    "PM_Serrin": sawdust,
    "PM_Caja_Rotulo": caja_fascia,
    "PM_Caja_Cajero": caja_atm,
    "PM_Caja_Vinilo": vinyl_caja,
    "PM_Placa_CalleMayor": plate_calle_mayor,
    "PM_Banderines": banderines,
    "PM_Chorreon_A": lambda: streak_decal(0),
    "PM_Chorreon_B": lambda: streak_decal(1),
    "PM_Zocalo_Humedad": damp_plinth,
}
GROUND = {"TX_Ground_LosaGranito": granite_flags}


def main(names):
    for name, fn in SURFACES.items():
        if not names or name in names:
            save(fn(), name)
    ground_dir = ROOT.parents[1] / "Unity" / "JuegoDef" / "Assets" / "JuegoDef" / "City" / "Ground"
    for name, fn in GROUND.items():
        if not names or name in names:
            fn().save(ground_dir / f"{name}.png")
            print("painted", name)


if __name__ == "__main__":
    main(sys.argv[1:])

"""Shop signs, blade-sign icons and notices for the CASCO ground floors (owner audit 2026-09-29, points 8/10/44:
"carteles/placas vacíos o genéricos", "locales demasiado genéricos"). Reads the programme in
Unity/JuegoDef/Assets/JuegoDef/Env/Grammar/businesses.json and paints, per business:

  T_ENV_Sign_<id>.png   fascia lettering panel (painted board / enamel / gilded glass / modern light box), 1280 x 256
  T_ENV_Blade_<id>.png  double-sided hanging sign for the wrought-iron bracket: trade icon + short name, 256 x 256
and per notice T_ENV_Notice_<id>.png (SE ALQUILA, VADO PERMANENTE, opening hours, chalk menu...), 512 x 256.

Fictional names only. Fonts are the system's (rendered into bitmaps, no font file is redistributed).

    python Tools/env_signs.py [--out Unity/JuegoDef/Assets/JuegoDef/Derived/ENV/Signs]
"""
import argparse
import json
import math
import os
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = Path(__file__).resolve().parents[1]
SPEC = REPO / "Unity/JuegoDef/Assets/JuegoDef/Env/Grammar/businesses.json"
OUT = REPO / "Unity/JuegoDef/Assets/JuegoDef/Derived/ENV/Signs"
FONTS = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def font(name, size):
    for n in (name, "arialbd.ttf"):
        try:
            return ImageFont.truetype(str(FONTS / n), size)
        except OSError:
            continue
    return ImageFont.load_default()


def fit(draw, text, fname, w, h):
    """Largest font size whose text fits w x h."""
    lo, hi = 8, 400
    while lo < hi:
        mid = (lo + hi + 1) // 2
        f = font(fname, mid)
        x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=f)
        if x1 - x0 <= w and y1 - y0 <= h:
            lo = mid
        else:
            hi = mid - 1
    return font(fname, lo)


def centred(draw, box, text, f, fill, shadow=None, stroke=0, stroke_fill=None):
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=f, stroke_width=stroke)
    cx = (box[0] + box[2]) / 2 - (x0 + x1) / 2
    cy = (box[1] + box[3]) / 2 - (y0 + y1) / 2
    if shadow:
        draw.text((cx + shadow[0], cy + shadow[1]), text, font=f, fill=shadow[2], stroke_width=stroke, stroke_fill=shadow[2])
    draw.text((cx, cy), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)


def grain(img, rng, amount, streak=True):
    """Painted-timber grain and wear so boards are not flat vector graphics."""
    a = np.asarray(img).astype(float)
    h, w = a.shape[:2]
    n = rng.normal(0, 1, (h, w))
    if streak:
        n = 0.6 * n + 0.4 * np.repeat(rng.normal(0, 1, (h, 1)), w, axis=1)
    a[..., :3] *= (1 + amount * n)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), img.mode).filter(ImageFilter.SMOOTH)


def wear(img, rng, spots, colour):
    d = ImageDraw.Draw(img)
    w, h = img.size
    for _ in range(spots):
        x, y = rng.random() * w, rng.random() * h
        r = rng.uniform(1.5, 5)
        if rng.random() < 0.7:           # wear concentrates on the edges
            if rng.random() < 0.5:
                y = rng.choice([rng.uniform(0, 14), rng.uniform(h - 14, h)])
            else:
                x = rng.choice([rng.uniform(0, 14), rng.uniform(w - 14, w)])
        d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=colour)
    return img


def sign(b, rng):
    w, h = 1280, 256
    bg, fg = hexc(b["bg"]), hexc(b["fg"])
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    style = b["style"]
    if style == "painted":
        d.rectangle([14, 14, w - 15, h - 15], outline=fg, width=5)
        f = fit(d, b["name"], b["font"], w * 0.86, h * 0.52)
        centred(d, (0, 0, w, h), b["name"], f, fg, shadow=(3, 3, tuple(int(c * 0.55) for c in bg)))
        img = grain(img, rng, 0.05)
        img = wear(img, rng, 70, tuple(min(255, int(c * 1.25 + 20)) for c in bg))
    elif style == "enamel":
        d.rounded_rectangle([6, 6, w - 7, h - 7], radius=26, outline=(236, 236, 230), width=10)
        d.rounded_rectangle([24, 24, w - 25, h - 25], radius=16, outline=fg, width=3)
        f = fit(d, b["name"], b["font"], w * 0.84, h * 0.5)
        centred(d, (0, 0, w, h), b["name"], f, fg)
        img = grain(img, rng, 0.02, streak=False)
        img = wear(img, rng, 25, (30, 28, 26))                  # enamel chips
    elif style == "gilded":
        d.rectangle([10, 10, w - 11, h - 11], outline=fg, width=4)
        d.rectangle([22, 22, w - 23, h - 23], outline=tuple(int(c * 0.6) for c in fg), width=2)
        f = fit(d, b["name"], b["font"], w * 0.84, h * 0.56)
        centred(d, (0, 0, w, h), b["name"], f, fg, shadow=(2, 3, (10, 8, 6)), stroke=1, stroke_fill=tuple(int(c * 0.7) for c in fg))
        img = grain(img, rng, 0.03, streak=False)
    else:  # modern light box / vinyl letters
        f = fit(d, b["name"], b["font"], w * 0.88, h * 0.62)
        centred(d, (0, 0, w, h), b["name"], f, fg)
        img = grain(img, rng, 0.012, streak=False)
    return img


def icon(d, kind, cx, cy, s, fg, bg):
    """Simple trade icons drawn with shapes (s = half size)."""
    lw = max(3, int(s * 0.09))
    if kind == "copa":
        d.pieslice([cx - s * 0.5, cy - s * 0.9, cx + s * 0.5, cy + s * 0.1], 0, 180, fill=fg)
        d.rectangle([cx - s * 0.5, cy - s * 0.55, cx + s * 0.5, cy - s * 0.4], fill=fg)
        d.line([cx, cy + s * 0.1, cx, cy + s * 0.75], fill=fg, width=lw)
        d.ellipse([cx - s * 0.35, cy + s * 0.68, cx + s * 0.35, cy + s * 0.85], fill=fg)
    elif kind == "jarra":
        d.rectangle([cx - s * 0.45, cy - s * 0.6, cx + s * 0.3, cy + s * 0.8], fill=fg)
        d.arc([cx + s * 0.1, cy - s * 0.35, cx + s * 0.75, cy + s * 0.45], -90, 90, fill=fg, width=lw * 2)
        for k in range(3):
            d.ellipse([cx - s * 0.5 + k * s * 0.28, cy - s * 0.85, cx - s * 0.1 + k * s * 0.28, cy - s * 0.45], fill=bg, outline=fg, width=lw)
    elif kind == "sidra":
        d.rectangle([cx - s * 0.55, cy - s * 0.3, cx - s * 0.2, cy + s * 0.85], fill=fg)
        d.rectangle([cx - s * 0.45, cy - s * 0.8, cx - s * 0.3, cy - s * 0.3], fill=fg)
        d.polygon([(cx + s * 0.05, cy - s * 0.1), (cx + s * 0.65, cy - s * 0.1), (cx + s * 0.55, cy + s * 0.85), (cx + s * 0.15, cy + s * 0.85)], outline=fg, width=lw)
        d.polygon([(cx + s * 0.1, cy + s * 0.35), (cx + s * 0.6, cy + s * 0.35), (cx + s * 0.55, cy + s * 0.85), (cx + s * 0.15, cy + s * 0.85)], fill=fg)
    elif kind == "taza":
        d.chord([cx - s * 0.6, cy - s * 0.4, cx + s * 0.4, cy + s * 0.6], 0, 180, fill=fg)
        d.rectangle([cx - s * 0.6, cy - s * 0.1, cx + s * 0.4, cy + s * 0.12], fill=fg)
        d.arc([cx + s * 0.25, cy - s * 0.1, cx + s * 0.75, cy + s * 0.35], -90, 90, fill=fg, width=lw)
        d.ellipse([cx - s * 0.85, cy + s * 0.6, cx + s * 0.65, cy + s * 0.8], fill=fg)
        for k in (-0.3, 0.0, 0.3):
            d.arc([cx + k * s - s * 0.12, cy - s * 0.95, cx + k * s + s * 0.12, cy - s * 0.35], 100, 260, fill=fg, width=lw)
    elif kind == "pan":
        d.ellipse([cx - s * 0.9, cy - s * 0.45, cx + s * 0.9, cy + s * 0.45], fill=fg)
        for k in (-0.45, 0.0, 0.45):
            d.line([cx + k * s - s * 0.12, cy + s * 0.25, cx + k * s + s * 0.18, cy - s * 0.25], fill=bg, width=lw)
    elif kind == "llave":
        d.ellipse([cx - s * 0.85, cy - s * 0.35, cx - s * 0.15, cy + s * 0.35], outline=fg, width=lw * 2)
        d.line([cx - s * 0.15, cy, cx + s * 0.85, cy], fill=fg, width=lw * 2)
        for k in (0.45, 0.7):
            d.line([cx + k * s, cy, cx + k * s, cy + s * 0.3], fill=fg, width=lw * 2)
    elif kind == "tijeras":
        for sy in (-1, 1):
            d.ellipse([cx - s * 0.85, cy + sy * s * 0.35 - s * 0.22, cx - s * 0.4, cy + sy * s * 0.35 + s * 0.22], outline=fg, width=lw)
            d.line([cx - s * 0.42, cy + sy * s * 0.3, cx + s * 0.85, cy - sy * s * 0.25], fill=fg, width=lw)
    elif kind == "libro":
        d.polygon([(cx - s * 0.85, cy - s * 0.55), (cx - s * 0.05, cy - s * 0.4), (cx - s * 0.05, cy + s * 0.6), (cx - s * 0.85, cy + s * 0.45)], fill=fg)
        d.polygon([(cx + s * 0.85, cy - s * 0.55), (cx + s * 0.05, cy - s * 0.4), (cx + s * 0.05, cy + s * 0.6), (cx + s * 0.85, cy + s * 0.45)], fill=fg)
    elif kind == "cama":
        d.rectangle([cx - s * 0.9, cy + s * 0.05, cx + s * 0.9, cy + s * 0.35], fill=fg)
        d.rectangle([cx - s * 0.9, cy - s * 0.45, cx - s * 0.75, cy + s * 0.7], fill=fg)
        d.rectangle([cx + s * 0.75, cy - 0.05 * s, cx + s * 0.9, cy + s * 0.7], fill=fg)
        d.ellipse([cx - s * 0.65, cy - s * 0.3, cx - s * 0.25, cy + s * 0.05], fill=fg)
        d.rectangle([cx - s * 0.2, cy - s * 0.15, cx + s * 0.75, cy + s * 0.05], fill=fg)
    elif kind == "queso":
        d.polygon([(cx - s * 0.85, cy + s * 0.5), (cx + s * 0.85, cy + s * 0.5), (cx + s * 0.85, cy - s * 0.1), (cx - s * 0.3, cy - s * 0.55)], fill=fg)
        for (ox, oy, r) in ((-0.2, 0.15, 0.12), (0.35, 0.2, 0.1), (0.5, -0.05, 0.07)):
            d.ellipse([cx + (ox - r) * s, cy + (oy - r) * s, cx + (ox + r) * s, cy + (oy + r) * s], fill=bg)


def blade(b, rng):
    n = 256
    bg, fg = hexc(b["bg"]), hexc(b["fg"])
    img = Image.new("RGB", (n, n), bg)
    d = ImageDraw.Draw(img)
    d.rectangle([8, 8, n - 9, n - 9], outline=fg, width=4)
    icon(d, b.get("icon", "copa"), n / 2, n * 0.42, n * 0.28, fg, bg)
    short = b["name"].split("·")[0].strip()
    words = short.split()
    label = " ".join(words[-2:]) if len(words) > 2 else short
    f = fit(d, label, b["font"], n * 0.8, n * 0.16)
    centred(d, (0, n * 0.72, n, n * 0.92), label, f, fg)
    return wear(grain(img, rng, 0.04), rng, 20, tuple(min(255, int(c * 1.3 + 15)) for c in bg))


def notice(nt, rng):
    w, h = 512, 256
    bg, fg = hexc(nt["bg"]), hexc(nt["fg"])
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    if nt.get("vado"):
        # the municipal "vado permanente" plate: no-parking disc and the text
        cx, cy, r = 92, h / 2, 70
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(200, 30, 30))
        d.ellipse([cx - r * 0.78, cy - r * 0.78, cx + r * 0.78, cy + r * 0.78], fill=(30, 70, 160))
        d.line([cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55], fill=(200, 30, 30), width=16)
        f = fit(d, nt["text"], nt["font"], w - 200, h * 0.26)
        centred(d, (180, 40, w - 10, 140), nt["text"], f, fg)
        f2 = fit(d, nt["sub"], nt["font"], w - 220, h * 0.2)
        centred(d, (180, 150, w - 10, 220), nt["sub"], f2, fg)
        d.rectangle([4, 4, w - 5, h - 5], outline=(30, 30, 30), width=4)
    elif nt.get("board"):
        # chalkboard (pizarra) for the bar's A-frame
        f = fit(d, nt["text"], nt["font"], w * 0.8, h * 0.34)
        centred(d, (0, 20, w, 120), nt["text"], f, fg)
        f2 = fit(d, nt["sub"], nt["font"], w * 0.85, h * 0.22)
        centred(d, (0, 140, w, 230), nt["sub"], f2, (226, 214, 150))
        img = grain(img, rng, 0.08, streak=False)
    else:
        f = fit(d, nt["text"], nt["font"], w * 0.86, h * 0.42)
        centred(d, (0, 10, w, 150), nt["text"], f, fg)
        f2 = fit(d, nt["sub"], nt["font"], w * 0.86, h * 0.18)
        centred(d, (0, 160, w, 230), nt["sub"], f2, fg)
        img = grain(img, rng, 0.03, streak=False)
    return img


def number(n, rng):
    """Enamel house-number plate: white number on blue with a white rim (the usual municipal plate)."""
    w, h = 128, 96
    img = Image.new("RGB", (w, h), (32, 62, 120))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([3, 3, w - 4, h - 4], radius=10, outline=(236, 236, 230), width=5)
    f = fit(d, str(n), "ARIALNB.TTF", w * 0.7, h * 0.66)
    centred(d, (0, 0, w, h), str(n), f, (240, 240, 236))
    return wear(img, rng, 6, (20, 20, 22))


def ghost(g, rng):
    """Faded painted advertisement on a blind side wall (anuncio pintado): washed-out colours, lime showing through,
    the lettering half gone — the kind of sign that has been there for sixty years."""
    w, h = 1024, 640
    bg, fg = np.array(hexc(g["bg"]), float), np.array(hexc(g["fg"]), float)
    img = Image.new("RGB", (w, h), tuple(int(c) for c in bg))
    d = ImageDraw.Draw(img)
    d.rectangle([18, 18, w - 19, h - 19], outline=tuple(int(c) for c in fg), width=10)
    f = fit(d, g["text"], g["font"], w * 0.86, h * 0.34)
    centred(d, (0, 40, w, h * 0.62), g["text"], f, tuple(int(c) for c in fg))
    f2 = fit(d, g["sub"], g["font"], w * 0.7, h * 0.16)
    centred(d, (0, h * 0.62, w, h - 40), g["sub"], f2, tuple(int(c) for c in fg))
    a = np.asarray(img).astype(float)
    lime = np.array([214, 206, 188], float)
    y = np.linspace(0, 1, h)[:, None]
    n = np.asarray(Image.fromarray((rng.random((h // 16, w // 16)) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(float) / 255
    fade = np.clip(0.35 + 0.45 * n + 0.2 * y, 0, 1)[..., None]           # more washed out low down and in patches
    a = a * (1 - fade) + lime * fade
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.SMOOTH)


def cross(rng):
    """Pharmacy cross light box (emissive green, used both sides of a blade)."""
    n = 256
    img = Image.new("RGB", (n, n), (20, 30, 24))
    d = ImageDraw.Draw(img)
    g = (70, 230, 110)
    a, b = n * 0.36, n * 0.64
    d.rectangle([a, n * 0.1, b, n * 0.9], fill=g)
    d.rectangle([n * 0.1, a, n * 0.9, b], fill=g)
    return img.filter(ImageFilter.GaussianBlur(1.2))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    n = 0
    for b in spec["businesses"]:
        rng = np.random.default_rng(sum(map(ord, b["id"])) * 7919)
        sign(b, rng).save(out / f"T_ENV_Sign_{b['id']}.jpg", quality=88)
        if b.get("icon"):
            blade(b, rng).save(out / f"T_ENV_Blade_{b['id']}.jpg", quality=88)
        n += 1
    for nt in spec["notices"]:
        rng = np.random.default_rng(sum(map(ord, nt["id"])) * 131)
        notice(nt, rng).save(out / f"T_ENV_Notice_{nt['id']}.jpg", quality=88)
    cross(np.random.default_rng(3)).save(out / "T_ENV_Cross_Pharmacy.jpg", quality=90)
    for g in spec.get("ghosts", []):
        ghost(g, np.random.default_rng(sum(map(ord, g["id"])))).save(out / f"T_ENV_Ghost_{g['id']}.jpg", quality=86)
    for k in (2, 3, 5, 7, 8, 11, 12, 14, 17, 19, 21, 26):
        number(k, np.random.default_rng(k)).save(out / f"T_ENV_Num_{k}.jpg", quality=90)
    print(f"ENV_SIGNS businesses={n} notices={len(spec['notices'])} -> {out}")


if __name__ == "__main__":
    main()

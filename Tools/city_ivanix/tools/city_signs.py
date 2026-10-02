"""Painted shop signs for the town (Docs/design/CITY_STYLE_DCPLUS.md: "rótulos a escala Shenmue").

For every business in the seed: a fascia board (1024x192), a blade sign (256x384) and an awning canvas (256x128),
painted like a 1990s sign-writer's work: a coloured ground with a lighter top, a fine border, bold letters with a
drop shadow, a little weathering. Output in the Unity project (Assets/JuegoDef/City/Signs) plus a manifest.
Fonts: Windows faces for the look-dev only; to be swapped for OFL faces before release.
"""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from businesses import CATEGORIES, PROGRAMME_STYLE  # noqa: E402

SEED = ROOT / "reconstruction" / "city_seed_v4.json"
UNITY_SIGNS = ROOT.parents[1] / "Unity" / "JuegoDef" / "Assets" / "JuegoDef" / "City" / "Signs"
FONTS = Path("C:/Windows/Fonts")


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rnd(key):
    return int(hashlib.md5(key.encode()).hexdigest()[:8], 16)


def font(name, size):
    try:
        return ImageFont.truetype(str(FONTS / name), size)
    except OSError:
        return ImageFont.truetype(str(FONTS / "arialbd.ttf"), size)


def fit(draw, text, fname, w, h):
    size = h
    while size > 10:
        f = font(fname, size)
        bb = draw.textbbox((0, 0), text, font=f)
        if bb[2] - bb[0] <= w and bb[3] - bb[1] <= h:
            return f, bb
        size -= 4
    f = font(fname, 10)
    return f, draw.textbbox((0, 0), text, font=f)


def board(w, h, bg, fg, text, fname, key, icon=None, border=True):
    img = Image.new("RGB", (w, h), bg)
    px = np.asarray(img).astype(np.float32)
    grad = np.linspace(1.08, 0.9, h)[:, None, None]
    px = np.clip(px * grad, 0, 255)
    img = Image.fromarray(px.astype(np.uint8))
    d = ImageDraw.Draw(img)
    pad = max(6, h // 14)
    if border:
        d.rectangle([pad, pad, w - pad - 1, h - pad - 1], outline=fg, width=max(2, h // 40))
    x0 = pad * 3
    if icon == "cross":
        cs = int(h * 0.62)
        cx, cy = pad * 3 + cs // 2, h // 2
        t = cs // 3
        d.rectangle([cx - t // 2, cy - cs // 2, cx + t // 2, cy + cs // 2], fill=fg)
        d.rectangle([cx - cs // 2, cy - t // 2, cx + cs // 2, cy + t // 2], fill=fg)
        x0 = pad * 4 + cs
    tw, th = w - x0 - pad * 3, int(h * 0.62)
    f, bb = fit(d, text, fname, tw, th)
    tx = x0 + (tw - (bb[2] - bb[0])) // 2 - bb[0]
    ty = (h - (bb[3] - bb[1])) // 2 - bb[1]
    shadow = tuple(int(c * 0.45) for c in bg)
    d.text((tx + max(2, h // 60), ty + max(2, h // 60)), text, font=f, fill=shadow)
    d.text((tx, ty), text, font=f, fill=fg)
    # weathering: a few specks and a soft grime at the foot
    r = np.random.default_rng(rnd(key))
    a = np.asarray(img).astype(np.float32)
    for _ in range(int(w * h / 9000)):
        y, x = r.integers(0, h), r.integers(0, w)
        rr = r.integers(1, 3)
        a[max(0, y - rr):y + rr, max(0, x - rr):x + rr] *= 0.82
    foot = np.linspace(1.0, 0.86, h)[:, None, None] ** 2
    a = np.clip(a * foot, 0, 255)
    return Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.SMOOTH)


def awning(bg, key):
    w, h = 256, 128
    img = Image.new("RGB", (w, h), (238, 232, 218))
    d = ImageDraw.Draw(img)
    stripe = 32
    for x in range(0, w, stripe * 2):
        d.rectangle([x, 0, x + stripe - 1, h], fill=bg)
    d.rectangle([0, h - 18, w, h], fill=tuple(int(c * 0.8) for c in bg))
    return img.filter(ImageFilter.SMOOTH)


def main():
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    UNITY_SIGNS.mkdir(parents=True, exist_ok=True)
    out = {}
    for b in seed["buildings"]:
        bz = b.get("business")
        if not bz:
            continue
        cat = bz["category"]
        if cat in CATEGORIES:
            c = CATEGORIES[cat]
            bg_h, fg_h = c["colors"][bz.get("color", 0) % len(c["colors"])]
            fname, blade_txt = c["font"], c["blade"]
        else:
            bg_h, fg_h, fname, blade_txt = PROGRAMME_STYLE[cat]
        bg, fg = rgb(bg_h), rgb(fg_h)
        sid = bz["id"]
        name = bz["name"].upper() if cat not in ("cafe", "peluqueria") else bz["name"]
        icon = "cross" if cat == "farmacia" else None
        fascia = board(1024, 192, bg, fg, name, fname, sid, icon)
        fascia.save(UNITY_SIGNS / f"SIGN_{sid}_fascia.png")
        rec = {"category": cat, "name": bz["name"], "bg": bg_h, "fg": fg_h, "fascia": f"Assets/JuegoDef/City/Signs/SIGN_{sid}_fascia.png"}
        if blade_txt:
            if cat == "farmacia":
                blade = board(384, 384, (240, 240, 236), (15, 122, 58), " ", fname, sid + "b", icon="cross")
            else:
                txt = {"ALIMENTACIÓN": "ULTRAMARINOS", "PELUQUERÍA": "PELUQUERÍA", "FERRETERÍA": "FERRETERÍA"}.get(blade_txt, blade_txt)
                blade = board(384 if len(txt) <= 7 else 512, 256, bg, fg, txt, fname, sid + "b")
            blade.save(UNITY_SIGNS / f"SIGN_{sid}_blade.png")
            rec["blade"] = f"Assets/JuegoDef/City/Signs/SIGN_{sid}_blade.png"
        if cat in CATEGORIES and CATEGORIES[cat]["goods"] in ("fruta", "pescado", "pan", "cajas", "terraza", "moda") or cat in ("bar", "cafe", "fruteria", "panaderia", "ultramarinos", "moda", "pescaderia", "hotel"):
            awning(bg, sid).save(UNITY_SIGNS / f"SIGN_{sid}_awning.png")
            rec["awning"] = f"Assets/JuegoDef/City/Signs/SIGN_{sid}_awning.png"
        rec["goods"] = CATEGORIES[cat]["goods"] if cat in CATEGORIES else None
        out[b["id"]] = rec
    (ROOT / "reconstruction" / "city_signs.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("signs:", len(out), "->", UNITY_SIGNS)


if __name__ == "__main__":
    main()

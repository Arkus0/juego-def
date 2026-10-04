"""The town's surface kit in the Shenmue 2 manner (Owner 2026-10-03: "copiarlo, no imitarlo, no adaptarlo").

What AM2 did, and what this script repeats: photographs of real surfaces, brought down to Dreamcast texture sizes with
a sharp filter (no smoothing), the cavities and joints dark as daylight leaves them, colour and contrast pushed so each
surface reads as its colour from across the street, a touch of sharpening, and 16-bit colour (RGB565). Structure stays
crisp (bricks, setts, slabs, tile rows, planks); nothing is blurred into blotches, no relief is baked from normal maps.
Measured targets (Docs/design/city_ivx/SHENMUE_TEXTURE_SPEC.md): within-surface luminance spread 0.14-0.24, crisp
detail (Laplacian at 640x480) 3-7, painted walls saturated ~0.5.

Sources: CC0 photographs from Poly Haven (polyhaven.com, public domain), ids and authors in
Tools/city_ivanix/provenance/SHENMUE_KIT_SOURCES.json; originals are fetched to JD_SK_SOURCES (default: the
scratchpad folder given on the command line) and are not committed; only the Dreamcast-sized results are.

Usage: python shenmue_kit.py <sources_dir> [name ...]
"""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parents[1] / "Unity" / "JuegoDef" / "Assets" / "JuegoDef" / "City" / "ShenmueKit" / "Textures"


def load(src_dir, pid, kind="diffuse"):
    p = Path(src_dir) / f"{pid}_{kind}.jpg"
    return Image.open(p).convert("RGB" if kind == "diffuse" else "L") if p.exists() else None


def rgb565(a):
    """Dreamcast 16-bit colour: 5-6-5 bits, no dithering (VQ textures did not dither)."""
    a = np.clip(a, 0, 255).astype(np.uint8)
    out = a.copy()
    out[..., 0] = (a[..., 0] >> 3) << 3 | (a[..., 0] >> 5)
    out[..., 1] = (a[..., 1] >> 2) << 2 | (a[..., 1] >> 6)
    out[..., 2] = (a[..., 2] >> 3) << 3 | (a[..., 2] >> 5)
    return out


def dreamcast(img, ao=None, px=256, sat=1.35, contrast=1.2, ao_strength=0.55, bright=1.0, warm=0.0, neutral=False,
              mean=None, sharpen=0.6, crop=None):
    """One photographed surface brought to a Dreamcast texture."""
    if crop:
        img = img.crop(crop)
        ao = ao.crop(crop) if ao else None
    img = img.resize((px, px), Image.LANCZOS)
    a = np.asarray(img, np.float32) / 255.0
    if ao is not None:
        o = np.asarray(ao.resize((px, px), Image.LANCZOS), np.float32) / 255.0
        a *= (1 - ao_strength + ao_strength * o ** 1.5)[..., None]
    L = a @ np.array([0.299, 0.587, 0.114], np.float32)
    if neutral:
        # a base for tinted paint: the photo's light and dark only, centred on `mean`
        Lc = L - L.mean()
        L2 = np.clip((mean if mean is not None else 0.82) + Lc * contrast, 0, 1)
        a = np.repeat(L2[..., None], 3, axis=2)
    else:
        m = L.mean()
        a = m + (a - m) * contrast                      # contrast around the surface's own mean
        g = (a @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
        a = g + (a - g) * sat                           # saturation
        a *= bright
        if warm:
            a[..., 0] *= 1 + warm
            a[..., 2] *= 1 - warm
        if mean is not None:
            a *= mean / max(1e-3, float((a @ np.array([0.299, 0.587, 0.114], np.float32)).mean()))
    out = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    if sharpen:
        out = out.filter(ImageFilter.UnsharpMask(radius=1.2, percent=int(sharpen * 100), threshold=2))
    return Image.fromarray(rgb565(np.asarray(out, np.float32)))


# ------------------------------------------------------------------ the kit: one entry per surface family
# name: (poly haven id, kwargs). Sizes: 256 px per 2 m tile (~128 px/m), the density Shenmue gave a street at 3 m.
KIT = {
    # render, tinted per colour family by its material; the clean painted lime and the old one with stones showing
    "SK_Revoco":         ("painted_plaster_wall", dict(neutral=True, mean=0.76, contrast=3.2, ao_strength=0.6)),
        "SK_Revoco_Viejo":   ("plaster_stone_wall_01", dict(neutral=True, mean=0.72, contrast=1.7, ao_strength=0.75)),
    # stone
    "SK_Silleria":       ("medieval_blocks_03",   dict(sat=1.45, contrast=1.3, ao_strength=0.7, bright=1.18)),
    "SK_Mamposteria":    ("old_stone_wall",       dict(sat=1.4, contrast=1.25, ao_strength=0.75, bright=1.12)),
    "SK_Sillar_Sucio":   ("large_sandstone_blocks", dict(sat=1.3, contrast=1.2, ao_strength=0.6, bright=1.3)),
    # roof
    "SK_Teja":           ("clay_roof_tiles_03",   dict(sat=1.3, contrast=1.25, ao_strength=0.7, bright=1.05)),
    # ground
    "SK_Losa_Granito":   ("granite_tile_04",      dict(sat=0.3, contrast=2.1, ao_strength=0.55, bright=1.15, warm=-0.02)),
    "SK_Adoquin":        ("cobblestone_square",   dict(sat=0.95, contrast=1.45, ao_strength=0.75, bright=1.05, warm=-0.02)),
    "SK_Canto":          ("cobblestone_05",       dict(sat=1.35, contrast=1.25, ao_strength=0.75, bright=1.15)),
    "SK_Canto_Rodado":   ("large_pebbles",        dict(sat=1.3, contrast=1.3, ao_strength=0.7, bright=1.45)),
    # painted wood
    "SK_Madera_Verde":   ("green_rough_planks",   dict(sat=1.45, contrast=1.25, ao_strength=0.5, bright=1.1)),
    "SK_Madera_Azul":    ("blue_painted_planks",  dict(sat=1.5, contrast=1.25, ao_strength=0.5, bright=1.1)),
    "SK_Madera_Gastada": ("distressed_painted_planks", dict(sat=1.4, contrast=1.2, ao_strength=0.5, bright=1.05)),
}


def neutral_light(img, mean=0.8, spread=1.0):
    """A photographed surface as light neutral grey (the material's tint gives the colour), structure kept."""
    a = np.asarray(img.convert("RGB"), np.float32) / 255.0
    L = a @ np.array([0.299, 0.587, 0.114], np.float32)
    L = np.clip(mean + (L - L.mean()) * spread, 0, 1)
    return Image.fromarray((np.repeat(L[..., None], 3, 2) * 255).astype(np.uint8))


def fill_band(atlas, y0, y1, tile, rotate=False):
    """Fills rows y0..y1 of the atlas with copies of `tile` scaled to the band height."""
    if rotate:
        tile = tile.rotate(90, expand=True)
    h = y1 - y0
    t = tile.resize((max(1, int(tile.width * h / tile.height)), h), Image.LANCZOS)
    for x in range(0, atlas.width, t.width):
        atlas.paste(t, (x, y0))


def bevel_lines(atlas, y0, y1, lines):
    """Baked light on a moulding: thin lighter and darker lines along it, as a lit profile."""
    a = np.asarray(atlas, np.float32)
    for frac, f in lines:
        y = int(y0 + (y1 - y0) * frac)
        a[max(0, y - 1):y + 2] *= f
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def atlases(src_dir):
    """The three Quaternius trim sheets the town's kit maps to, rebuilt band by band with photographed surfaces in
    the same layout (rows of 256: trim and wood 0-80 boards, 80-160 flat band, 160-200 ornament tiles, 200-243
    moulding, 243-256 edge; rock 0-82 small stones, 82-150 dressed band, 150-256 coursed blocks)."""
    S = 1024
    k = S / 256
    planks = dreamcast(load(src_dir, "distressed_painted_planks"), load(src_dir, "distressed_painted_planks", "ao"),
                       px=512, sat=1.0, contrast=1.3, ao_strength=0.5).rotate(90, expand=True)
    plaster = dreamcast(load(src_dir, "painted_plaster_wall"), load(src_dir, "painted_plaster_wall", "ao"),
                        px=512, neutral=True, mean=0.84, contrast=1.6, ao_strength=0.3)
    blocks = dreamcast(load(src_dir, "medieval_blocks_03"), load(src_dir, "medieval_blocks_03", "ao"),
                       px=512, sat=1.0, contrast=1.35, ao_strength=0.7)
    rubble = dreamcast(load(src_dir, "old_stone_wall"), load(src_dir, "old_stone_wall", "ao"),
                       px=512, sat=1.0, contrast=1.3, ao_strength=0.75)
    granite = dreamcast(load(src_dir, "granite_tile_04"), load(src_dir, "granite_tile_04", "ao"),
                        px=512, sat=1.0, contrast=1.3, ao_strength=0.2, crop=(40, 40, 480, 480))
    green = dreamcast(load(src_dir, "green_rough_planks"), load(src_dir, "green_rough_planks", "ao"),
                      px=512, sat=1.0, contrast=1.25, ao_strength=0.5)

    # painted trim (cornices, bands, surrounds; tinted stone or paint by the material)
    a = Image.new("RGB", (S, S), (200, 200, 200))
    fill_band(a, 0, int(80 * k), neutral_light(planks, 0.82, 1.1))
    fill_band(a, int(80 * k), int(160 * k), neutral_light(plaster, 0.80, 1.2))
    fill_band(a, int(160 * k), int(200 * k), neutral_light(blocks.crop((0, 0, 512, 160)), 0.86, 1.3))
    fill_band(a, int(200 * k), int(243 * k), neutral_light(plaster, 0.90, 0.8))
    fill_band(a, int(243 * k), S, neutral_light(plaster, 0.95, 0.6))
    a = bevel_lines(a, int(200 * k), int(243 * k), [(0.08, 1.12), (0.5, 0.82), (0.55, 1.1), (0.92, 0.8)])
    a.save(OUT / "SK_Atlas_Moldura.png")

    # joinery (window frames, doors, balconies; painted by the material's tint)
    w = Image.new("RGB", (S, S), (180, 180, 180))
    fill_band(w, 0, int(80 * k), neutral_light(green, 0.78, 1.25))
    fill_band(w, int(80 * k), int(160 * k), neutral_light(planks, 0.62, 1.25))
    fill_band(w, int(160 * k), int(200 * k), neutral_light(blocks.crop((0, 0, 512, 160)), 0.8, 1.2))
    fill_band(w, int(200 * k), int(243 * k), neutral_light(granite, 0.72, 1.1))
    fill_band(w, int(243 * k), S, neutral_light(granite, 0.8, 0.8))
    w.save(OUT / "SK_Atlas_Carpinteria.png")

    # dressed stone (plinths, steps, surrounds, retaining caps; tinted sandstone, limestone, grey)
    r = Image.new("RGB", (S, S), (180, 180, 180))
    fill_band(r, 0, int(82 * k), neutral_light(rubble, 0.74, 1.15))
    fill_band(r, int(82 * k), int(150 * k), neutral_light(granite, 0.78, 1.0))
    fill_band(r, int(150 * k), S, neutral_light(blocks, 0.8, 1.2))
    r.save(OUT / "SK_Atlas_PiedraLabrada.png")
    print("kit atlases: SK_Atlas_Moldura, SK_Atlas_Carpinteria, SK_Atlas_PiedraLabrada")


def build(src_dir, names):
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (pid, kw) in KIT.items():
        if names and name not in names:
            continue
        img = load(src_dir, pid)
        if img is None:
            print("missing source", pid)
            continue
        dreamcast(img, load(src_dir, pid, "ao"), **kw).save(OUT / f"{name}.png")
        print("kit", name, "<-", pid)
    if not names or "atlases" in names:
        atlases(src_dir)


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2:])

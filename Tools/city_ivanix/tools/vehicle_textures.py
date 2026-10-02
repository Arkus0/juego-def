"""Painted textures for the town's vehicles, the Dreamcast way: the shading a 2000-era artist painted into the map
instead of asking the hardware for it. Greyscale where Unity tints per colour variant (paint), colour elsewhere.

UV conventions (set by blender/build_vehicles.py):
  body paint and glass: u = position along the car (rear 0 -> front 1), v = height / 2.0 m
  lights, grille, plates, hubs, decals: each piece's own face normalised to 0..1

Output: Unity/JuegoDef/Assets/JuegoDef/City/Props/Textures/TXR_*.png (role textures) and TX_VanDecal_*.png
"""

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parents[1] / "Unity" / "JuegoDef" / "Assets" / "JuegoDef" / "City" / "Props" / "Textures"
OUT.mkdir(parents=True, exist_ok=True)
FONTS = Path("C:/Windows/Fonts")
RNG = np.random.default_rng(7)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def paint():
    """Body paint, greyscale (tinted by the variant colour): dark sill, the horizon line of the sky reflection along
    the flank, a bright beltline, a lighter roof, grime thrown up behind the wheels."""
    W, H = 512, 512
    v = (1 - (np.arange(H) + 0.5) / H)[:, None] * 2.0          # height in metres (v = z / 2.0)
    u = ((np.arange(W) + 0.5) / W)[None, :]
    z = np.repeat(v, W, axis=1)
    g = np.full((H, W), 0.80)
    g -= 0.30 * (1 - smoothstep(0.18, 0.34, z))                 # sill in shadow
    g += 0.10 * smoothstep(0.34, 0.60, z)                       # flank rising into the light
    horizon = 0.64
    g = np.where(z > horizon, g + 0.14 * np.exp(-(z - horizon) / 0.10), g - 0.07 * smoothstep(horizon - 0.16, horizon, z))
    g += 0.12 * np.exp(-((z - 0.86) / 0.035) ** 2)              # the beltline catching the sky
    g = np.where(z > 1.05, 0.93 - 0.05 * smoothstep(1.05, 1.5, z), g)
    g += 0.04 * np.sin(u * math.pi * 3.0) * smoothstep(1.2, 1.45, z)   # a soft streak on the roof
    # grime behind each wheel (u at the wheel stations of both models)
    for wu in (0.21, 0.79, 0.18, 0.82):
        d = np.abs(u - wu)
        g -= 0.18 * np.exp(-(d / 0.07) ** 2) * (1 - smoothstep(0.15, 0.55, z))
    g += RNG.normal(0, 0.008, g.shape)
    img = Image.fromarray(np.clip(g * 255, 0, 255).astype(np.uint8), "L").convert("RGB").filter(ImageFilter.SMOOTH)
    img.save(OUT / "TXR_Paint.png")


def glass():
    """Side glass and screens: deep blue-grey, the sky in the top third, a diagonal glint, the head restraints
    behind the side windows."""
    W, H = 512, 512
    img = Image.new("RGB", (W, H), (22, 28, 36))
    d = ImageDraw.Draw(img)
    for y in range(H):
        z = (1 - (y + 0.5) / H) * 2.0
        k = smoothstep(0.85, 1.5, z)
        c = tuple(int(a + (b - a) * k) for a, b in zip((34, 42, 52), (128, 142, 156)))
        d.line([(0, y), (W, y)], fill=c)
    for x0 in range(-200, W, 150):
        d.polygon([(x0, H * 0.28), (x0 + 40, H * 0.28), (x0 + 110, H * 0.62), (x0 + 70, H * 0.62)], fill=(118, 132, 146))
    # head restraints, seen through the side glass (z ~ 1.0-1.15 m)
    for uc in (0.36, 0.56, 0.62):
        x = int(uc * W)
        d.rounded_rectangle([x - 18, int(H * (1 - 1.17 / 2)), x + 18, int(H * (1 - 1.02 / 2))], 8, fill=(12, 14, 18))
    img.filter(ImageFilter.GaussianBlur(1.2)).save(OUT / "TXR_Glass.png")


def light_front():
    W, H = 256, 128
    img = Image.new("RGB", (W, H), (60, 62, 64))
    d = ImageDraw.Draw(img)
    d.rectangle([6, 6, W - 70, H - 6], fill=(214, 218, 220))
    for r in range(52, 6, -8):                                   # reflector rings
        c = 160 + (52 - r) * 2
        d.ellipse([90 - r, 64 - r, 90 + r, 64 + r], outline=(c, c, c + 4), width=3)
    d.ellipse([78, 52, 102, 76], fill=(250, 250, 240))
    d.polygon([(12, 12), (60, 12), (24, 54)], fill=(246, 248, 250))   # glint on the lens
    d.rectangle([W - 62, 6, W - 6, H - 6], fill=(232, 140, 30))     # amber indicator outboard
    for x in range(W - 58, W - 8, 10):
        d.line([(x, 8), (x, H - 8)], fill=(206, 112, 22), width=2)
    img.filter(ImageFilter.SMOOTH).save(OUT / "TXR_LightFront.png")


def light_rear():
    W, H = 128, 256
    img = Image.new("RGB", (W, H), (40, 10, 10))
    d = ImageDraw.Draw(img)
    d.rectangle([4, 4, W - 4, int(H * 0.55)], fill=(176, 22, 18))
    d.rectangle([4, int(H * 0.57), W - 4, int(H * 0.77)], fill=(226, 130, 30))     # indicator
    d.rectangle([4, int(H * 0.79), W - 4, H - 4], fill=(222, 222, 216))            # reversing light
    for y in range(8, H - 4, 12):
        d.line([(6, y), (W - 6, y)], fill=(0, 0, 0, 0) if False else (120, 12, 10) if y < H * 0.55 else (190, 100, 20) if y < H * 0.77 else (190, 190, 186), width=2)
    d.polygon([(10, 10), (60, 10), (14, 70)], fill=(232, 90, 80))
    img.filter(ImageFilter.SMOOTH).save(OUT / "TXR_LightRear.png")


def grille():
    W, H = 256, 64
    img = Image.new("RGB", (W, H), (18, 18, 20))
    d = ImageDraw.Draw(img)
    for y in range(6, H - 4, 9):
        d.rectangle([4, y, W - 4, y + 4], fill=(58, 60, 64))
    d.ellipse([W / 2 - 20, H / 2 - 12, W / 2 + 20, H / 2 + 12], fill=(182, 186, 190), outline=(90, 92, 96), width=3)
    img.filter(ImageFilter.SMOOTH).save(OUT / "TXR_Grille.png")


PLATES = ["S-7314-AZ", "O-2265-BG", "S-0918-AT", "S-5547-AB", "O-8830-AV", "S-1406-BC"]


def plates():
    """Spanish provincial plates of the late 1990s (S Cantabria, O Asturias): black on white, a thin black border."""
    for i, text in enumerate(PLATES):
        W, H = 512, 112
        img = Image.new("RGB", (W, H), (236, 236, 232))
        d = ImageDraw.Draw(img)
        d.rectangle([3, 3, W - 4, H - 4], outline=(20, 20, 20), width=5)
        f = ImageFont.truetype(str(FONTS / "arialbd.ttf"), 78)
        bb = d.textbbox((0, 0), text, font=f)
        d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], (H - (bb[3] - bb[1])) / 2 - bb[1]), text, font=f, fill=(18, 18, 18))
        img.filter(ImageFilter.SMOOTH).save(OUT / f"TXR_Plate_{i}.png")
    Image.open(OUT / "TXR_Plate_0.png").save(OUT / "TXR_Plate.png")


def hub():
    """The wheel seen from the side: tyre wall with its lettering band, a painted steel wheel with holes and a
    small hub cap (the plain wheels of an ordinary car of 2000)."""
    W = 256
    img = Image.new("RGB", (W, W), (14, 14, 15))
    d = ImageDraw.Draw(img)
    c = W / 2
    d.ellipse([4, 4, W - 4, W - 4], fill=(30, 30, 32))
    d.ellipse([18, 18, W - 18, W - 18], outline=(46, 46, 48), width=6)
    rim = 76
    d.ellipse([c - rim, c - rim, c + rim, c + rim], fill=(150, 154, 158))
    d.ellipse([c - rim + 8, c - rim + 8, c + rim - 8, c + rim - 8], fill=(118, 122, 126))
    for k in range(8):
        a = k * math.pi / 4
        x, y = c + math.cos(a) * 46, c + math.sin(a) * 46
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(40, 40, 42))
    d.ellipse([c - 26, c - 26, c + 26, c + 26], fill=(196, 200, 204))
    d.ellipse([c - 8, c - 8, c + 8, c + 8], fill=(120, 124, 128))
    d.arc([c - rim + 4, c - rim + 4, c + rim - 4, c + rim - 4], 200, 300, fill=(220, 224, 228), width=4)
    img.filter(ImageFilter.SMOOTH).save(OUT / "TXR_Hub.png")


DECALS = [("FRUTAS Y VERDURAS", "HNOS. SAIZ", (36, 110, 52)), ("PESCADOS LA BARCA", "Tfno. 942 71 30 18", (24, 64, 132)),
          ("FONTANERÍA RUIZ", "Calefacción · Gas", (150, 34, 30))]


def decals():
    """The trade lettering on a van's side panel, as the sign painter did it."""
    for i, (a, b, col) in enumerate(DECALS):
        W, H = 1024, 320
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        for text, font, size, y in ((a, "COOPBL.TTF", 96, 40), (b, "BRITANIC.TTF", 64, 180)):
            s = size
            while True:
                f = ImageFont.truetype(str(FONTS / font), s)
                bb = d.textbbox((0, 0), text, font=f)
                if bb[2] - bb[0] <= W * 0.94 or s < 20:
                    break
                s -= 4
            x = (W - (bb[2] - bb[0])) / 2 - bb[0]
            d.text((x + 3, y + 3), text, font=f, fill=(30, 30, 30, 120))
            d.text((x, y), text, font=f, fill=col + (255,))
        d.rectangle([60, 150, W - 60, 160], fill=col + (255,))
        img.save(OUT / f"TX_VanDecal_{i}.png")


paint()
glass()
light_front()
light_rear()
grille()
plates()
hub()
decals()
print("vehicle textures ->", OUT)

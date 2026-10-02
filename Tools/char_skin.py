"""Derive fair-skin atlases from the admitted Quaternius base-character skin textures.

The source 'Light' atlas is a medium tan (median RGB about 170,116,81). This tool supplies the selected light
palette baseline and recolours the SAME atlas by a per-channel
gain that maps its median skin tone to a pale-fair target while keeping all painted shading (lips, blush, wrinkles, stubble).
Deeper tones are then produced by multiplying with a per-person palette tint in Unity (multiplication can only darken).
Regional photographs are art references, not evidence for a single regional skin tone.

Source bytes stay untouched in the vault; outputs are owned derivatives at 1024 px JPEG (skin is not a hero-detail surface).
"""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
VAULT = Path('C:/Juego2-Assets/Base Characters/Base Characters/Textures')
OUT = ROOT / 'Unity/JuegoDef/Assets/JuegoDef/Derived/CHAR/Textures'
TARGET = np.array([241, 189, 156], float)            # pale peach mid tone in sRGB; deeper tones are multiplicative tints (see char_compatibility skinTones)

EYE_SOURCE = 'T_Eye_Brown.png'
EYE_COLOURS = {'brown': (100,75,47), 'blue': (102,125,150), 'green': (104,121,85), 'grey': (126,134,138)}

SOURCES = {
    'regular_male': 'T_Regular_Male_Light_BaseColor.png',
    'regular_female': 'T_Regular_Female_Light_BaseColor.png',
    'superhero_male': 'T_Superhero_Male_Ligh.png',
    'superhero_female': 'T_Superhero_Female_Light_BaseColor.png',
}


def derive(src: Path) -> Image.Image:
    a = np.asarray(Image.open(src).convert('RGB')).astype(float)
    skin = (a[..., 0] > a[..., 1]) & (a[..., 1] > a[..., 2]) & (a.sum(-1) > 250)
    base = np.median(a[skin], axis=0)
    ratio = a / base
    weights = np.array([.30, .59, .11])
    lum = (ratio * weights).sum(-1, keepdims=True)                    # relative luminance of each texel
    chroma = ratio / np.maximum(lum, 1e-3)                            # its colour direction (skin hue variation)
    # soft-limit luminance so highlights keep their hue instead of clipping to yellow-white, and lift shadows a touch
    knee = .96
    lum2 = np.where(lum > knee, knee + .12 * np.tanh((lum - knee) / .12), lum)
    lum2 = lum2 ** 1.04
    out = TARGET * lum2 * (1 + (chroma - 1) * .95)
    return Image.fromarray(np.clip(out, 0, 255).astype('uint8'))


def derive_eye(src: Path, colour) -> Image.Image:
    """Recolour the iris and soften the source's painted sclera/lid surround."""
    a = np.asarray(Image.open(src).convert('RGB')).astype(float)
    h, w = a.shape[:2]
    ys, xs = np.mgrid[0:h, 0:w]
    near = np.hypot((xs - w * .5) / w, (ys - h * .5) / h) < .135
    brown = (a[..., 0] > a[..., 2] * 1.25) & (a.max(-1) < 175) & near
    lum = a.mean(-1, keepdims=True)
    ref = lum[brown].mean() if brown.any() else 60.0
    tinted = np.array(colour, float) * (lum / ref) ** 0.85
    out = np.where(brown[..., None], tinted, a)
    # The source eye atlas also paints an abrupt red lid and a dirty grey
    # sclera. Give the civilian eye a quiet warm surround and a clean ivory
    # sclera; the mesh and real scene light supply the eyelid shadow.
    iris=np.hypot((xs-w*.5)/w,(ys-h*.5)/h)
    sclera=np.hypot((xs-w*.5)/(w*.235),(ys-h*.5)/(h*.165))
    whites=np.clip((1.1-sclera)/.22,0,1)*np.clip((iris-.112)/.016,0,1)
    out=out*(1-whites[...,None])+np.array([225,217,198])*whites[...,None]
    surround=np.clip((sclera-.98)/.28,0,1)
    out=out*(1-surround[...,None])+np.array([229,178,148])*surround[...,None]
    return Image.fromarray(np.clip(out, 0, 255).astype('uint8'))


# ---- Face variants -------------------------------------------------------------------------------------------
# All four Quaternius atlases share one face layout (measured on 720 px crops of the top-left 36 % of the atlas).
# The source paints every woman with blue-grey eyeshadow and glossy lips and every man with the same stubble, so
# a whole cast shares one face. Variants are deterministic paint-overs of the SAME atlas; they add identity (age,
# grooming, make-up) without new meshes. Recipe key `face`: default | natural | mature | older | clean.
CROP = .36 * 2048 / 720
LANDMARKS = {
    'female': {'eyes': [(262, 355), (475, 355)], 'nose': (370, 455), 'mouth': (370, 528), 'mouthHalf': 72},
    'male': {'eyes': [(272, 355), (472, 355)], 'nose': (370, 460), 'mouth': (370, 530), 'mouthHalf': 66},
}
FACES = {
    'female': {'natural': dict(makeup=1.0, lips=.72), 'mature': dict(makeup=1.0, lips=.72, age=.24), 'older': dict(makeup=1.0, lips=.76, age=.48)},
    'male': {'clean': dict(makeup=1.0, stubble=1.0), 'mature': dict(makeup=1.0, age=.24, stubble=.55), 'older': dict(makeup=1.0, age=.48, stubble=.65)},
}
FACE_BODIES = {'regular_female': 'female', 'superhero_female': 'female', 'regular_male': 'male', 'superhero_male': 'male'}


def _ellipse(h, w, c, rx, ry):
    ys, xs = np.mgrid[0:h, 0:w]
    return np.hypot((xs - c[0] * CROP) / (rx * CROP), (ys - c[1] * CROP) / (ry * CROP))


def _ref(a, mask):
    return np.median(a[mask], axis=0)


def _toward_skin(a, skin, wgt, lift):
    """Give texels the skin's colour direction (drops blue-grey shadow/stubble tint) and lift part of their darkness,
    keeping the painted form. A flat replacement left visible 'goggle' patches."""
    W = np.array([.30, .59, .11])
    lum = (a @ W)[..., None]; slum = float(skin @ W)
    new = (skin / slum) * (lum + (slum - lum) * lift)
    return a + (new - a) * wgt[..., None]


def face_variant(a: np.ndarray, sex: str, makeup=0., lips=0., age=0., stubble=0.) -> np.ndarray:
    from PIL import ImageDraw, ImageFilter
    a = a.copy(); h, w = a.shape[:2]; L = LANDMARKS[sex]
    # Atlas colour must not fight the authored calm expression. Remove the
    # source's deep painted socket/bag and red nasal shading, retaining a
    # small warm form cue. The real eyelid and light now supply that form.
    for c in L['eyes']:
        d = _ellipse(h,w,c,78,62)
        skin = _ref(a,(d>1.1)&(d<1.45))
        a = _toward_skin(a,skin,np.clip((1-d)/.50,0,1),.72)
    d = _ellipse(h,w,L['nose'],64,52)
    skin = _ref(a,(d>1.2)&(d<1.65))
    a = _toward_skin(a,skin,np.clip((1-d)/.5,0,1)*.72,.30)
    if makeup:
        for c in L['eyes']:
            d = _ellipse(h, w, c, 72, 52)
            skin = _ref(a, (d > 1.15) & (d < 1.45))
            socket = _ellipse(h, w, c, 35, 21)                   # lid opening (behind the eyeball mesh) keeps its paint
            wgt = np.clip((socket - 1.02) / .15, 0, 1) * np.clip((1 - d) / .45, 0, 1) * makeup
            a = _toward_skin(a, skin, wgt, .45)
    if sex=='female':
        # Remove the painted upper-lip/philtrum shadow, independently of
        # facial-hair admission. A warm lip edge remains on the lip itself.
        c=(L['mouth'][0],L['mouth'][1]-34)
        d=_ellipse(h,w,c,88,26)
        skin=_ref(a,(_ellipse(h,w,c,112,36)>1.05)&(_ellipse(h,w,c,112,36)<1.4))
        a=_toward_skin(a,skin,np.clip((1-d)/.50,0,1),.85)
    if lips:
        d = _ellipse(h, w, L['mouth'], L['mouthHalf'] + 8, 30)
        skin = _ref(a, (d > 1.3) & (d < 1.7))
        wgt = np.clip((1 - d) / .35, 0, 1) * lips
        lipcol = skin * .78 + np.array([199, 136, 126]) * .22            # restrained natural lip
        a = _toward_skin(a, lipcol, wgt, .50 if sex=='female' else .25)
    if stubble:
        cheek = _ref(a, _ellipse(h, w, (L['eyes'][0][0] - 10, 445), 30, 20) < 1)
        d = _ellipse(h, w, (L['mouth'][0], L['mouth'][1] + 25), 205, 135)
        mouth = _ellipse(h, w, L['mouth'], L['mouthHalf'], 24)
        nose = _ellipse(h, w, L['nose'], 55, 34)
        wgt = np.clip((1 - d) / .35, 0, 1) * np.clip((mouth - 1.0) / .15, 0, 1) * np.clip((nose - 1.0) / .3, 0, 1) * stubble
        a = _toward_skin(a, cheek, wgt, .55)
    if age:
        layer = Image.new('L', (w, h), 0); dr = ImageDraw.Draw(layer)
        P = lambda x, y: (x * CROP, y * CROP)
        (lx, ly), (rx_, ry_) = L['eyes']; mx, my = L['mouth']; nx, ny = L['nose']; mh = L['mouthHalf']
        for i, (y, x0, x1) in enumerate(((226, 300, 438), (250, 318, 424))):     # two soft forehead creases, not a stencil
            dr.arc([P(x0, y), P(x1, y + 36)], 200, 340, fill=105 - 30 * i, width=int(5 * CROP))
        for sx, ex in ((lx - 58, -1), (rx_ + 58, 1)):                              # crow's feet
            for k in (-1, 0, 1):
                dr.line([P(sx, ly + 4 * k), P(sx + ex * 26, ly + 12 * k - 2)], fill=150, width=int(4 * CROP))
        for cx in (lx, rx_):                                                       # under-eye bags
            dr.arc([P(cx - 42, ly + 8), P(cx + 38, ly + 50)], 20, 160, fill=120, width=int(7 * CROP))
        for sgn in (-1, 1):                                                        # nasolabial folds + marionette lines
            dr.line([P(nx + sgn * 38, ny + 14), P(nx + sgn * 62, ny + 45), P(mx + sgn * (mh + 8), my + 12)], fill=170, width=int(7 * CROP))
            dr.line([P(mx + sgn * (mh - 4), my + 14), P(mx + sgn * (mh + 2), my + 44)], fill=110, width=int(5 * CROP))
        for dx in (-9, 9):                                                         # frown lines between the brows
            dr.line([P(nx + dx, 312), P(nx + dx * 1.2, 338)], fill=110, width=int(4 * CROP))
        layer = np.asarray(layer.filter(ImageFilter.GaussianBlur(4 * CROP))).astype(float)[..., None] / 255
        a = a * (1 - .30 * age * layer) + np.array([150, 95, 80]) * .10 * age * layer   # soft, slightly warm creases
        grey = (a @ np.array([.30, .59, .11]))[..., None]
        a = a + (grey - a) * .10 * age                                             # a little less colour with age
    return a


def derive_faces(body: str, base: Image.Image):
    """Variants are painted on the 2048 derived atlas, then reduced like the base."""
    sex = FACE_BODIES[body]
    a = np.asarray(base).astype(float)
    for name, spec in FACES[sex].items():
        out = face_variant(a, sex, **spec)
        yield name, Image.fromarray(np.clip(out, 0, 255).astype('uint8')).resize((1024, 1024), Image.LANCZOS)


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for body, name in SOURCES.items():
        full = derive(VAULT / name)
        full.resize((1024, 1024), Image.LANCZOS).save(OUT / f'T_CHAR_Skin_{body}.jpg', quality=90, optimize=True)
        print('CHAR_SKIN', body)
        for face, img in derive_faces(body, full):
            img.save(OUT / f'T_CHAR_Skin_{body}_{face}.jpg', quality=90, optimize=True)
            print('CHAR_SKIN', body, face)
    for name, colour in EYE_COLOURS.items():
        derive_eye(VAULT / EYE_SOURCE, colour).save(OUT / f'T_CHAR_Eye_{name}.png', optimize=True)
        print('CHAR_EYE', name)

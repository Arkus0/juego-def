"""Repaint the town's textures in the "Dreamcast+" manner (Docs/design/CITY_STYLE_DCPLUS.md).

For every albedo in reconstruction/dc_manifest.json (written by Unity, CityDcPlus.Export):
  - relief: the normal map's form is baked into the colour with a soft upper-left light, as texture painters of the
    era did (the shader then carries no normal map);
  - cavities: steep normals (mortar joints, grooves, cracks) darkened;
  - edge-preserving smoothing: the photographic micro-noise goes, edges and shapes stay;
  - a little more saturation and a gentle S-curve; signs are only resized.
Output: the PNGs named in the manifest (Unity: Assets/JuegoDef/City/DCTextures).
"""

import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "reconstruction" / "dc_manifest.json"
LIGHT = np.array([-0.42, 0.52, 0.74])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def load(path):
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return None
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if img.dtype != np.uint8:
        img = (img / (256 if img.dtype == np.uint16 else 1)).astype(np.uint8)
    return img


def paint(item):
    img = load(item["albedo"])
    if img is None:
        return "unreadable"
    alpha = img[:, :, 3] if img.shape[2] == 4 else None
    bgr = img[:, :, :3].astype(np.float32) / 255.0
    h, w = bgr.shape[:2]
    m = item["max"]
    if max(h, w) > m:
        s = m / max(h, w)
        bgr = cv2.resize(bgr, (max(1, int(w * s)), max(1, int(h * s))), interpolation=cv2.INTER_AREA)
        if alpha is not None:
            alpha = cv2.resize(alpha, (bgr.shape[1], bgr.shape[0]), interpolation=cv2.INTER_AREA)
    kind = item["kind"]
    if kind != "sign":
        if item.get("normal"):
            nimg = load(item["normal"])
            if nimg is not None:
                nimg = cv2.resize(nimg[:, :, :3], (bgr.shape[1], bgr.shape[0]), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
                nx = nimg[:, :, 2] * 2 - 1           # R
                ny = nimg[:, :, 1] * 2 - 1           # G (OpenGL, +V up)
                nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
                ndl = nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]
                relief = np.clip(1.0 + 1.1 * (ndl - LIGHT[2]), 0.62, 1.32)
                cavity = 1.0 - 0.38 * np.power(np.clip(1 - nz, 0, 1), 0.7)
                shade = cv2.GaussianBlur(relief * cavity, (0, 0), 0.6)
                bgr = bgr * shade[:, :, None]
        # edge-preserving smoothing: the painted look, without the photo grain
        u8 = np.clip(bgr * 255, 0, 255).astype(np.uint8)
        d = 7 if max(u8.shape[:2]) >= 512 else 5
        u8 = cv2.bilateralFilter(u8, d, 26, 5)
        bgr = u8.astype(np.float32) / 255.0
    # colour: more saturation, a gentle S-curve on value
    hsv = cv2.cvtColor(np.clip(bgr, 0, 1), cv2.COLOR_BGR2HSV)
    sat = 1.06 if kind == "sign" else 1.14 if kind in ("wall", "wood", "roof", "metal") else 1.08
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * sat, 0, 1)
    v = hsv[:, :, 2]
    hsv[:, :, 2] = np.clip(v + 0.10 * (v - 0.5) * (1 - np.abs(v - 0.5) * 2), 0, 1)
    out = np.clip(cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR) * 255, 0, 255).astype(np.uint8)
    if alpha is not None:
        out = np.dstack([out, alpha])
    Path(item["out"]).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(item["out"], out)
    return "ok"


def main():
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    res = {}
    for it in doc["items"]:
        r = paint(it)
        res[r] = res.get(r, 0) + 1
    print("dc textures:", res, "of", len(doc["items"]))


if __name__ == "__main__":
    main()

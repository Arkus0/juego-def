"""Draw seed v4: frontage tramos, parcels (footprint in metres, facing tick), tapias, over the calibrated capture."""
import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
# the layout captures are not redistributed: point JD_IVX_REFS at the local survey folder's references/
REFS = Path(os.environ.get("JD_IVX_REFS", str(ROOT / "references")))
img = cv2.imread(str(REFS / "originals" / "REF0017H_city_cenital_calibrated_3840.png"))
seed = json.loads((ROOT / "reconstruction" / (sys.argv[1] if len(sys.argv) > 1 else "city_seed_v4.json")).read_text(encoding="utf-8"))
PL, M = (2200, 790), 0.16333
px = lambda x, z: (int(round(PL[0] + x / M)), int(round(PL[1] - z / M)))
COL = {"QUEST": (0, 0, 255), "SECONDARY": (0, 200, 255), "AMBIENT_ACCESSIBLE": (0, 200, 0), "AMBIENT": (200, 120, 255)}
vis = (img * 0.5).astype(np.uint8)
for t in seed.get("tramos", []):
    cv2.polylines(vis, [np.array([px(*q) for q in t["pts"]], np.int32)], False, (255, 255, 0) if t["primary"] else (160, 160, 0), 2)
for t in seed.get("tapias", []):
    cv2.polylines(vis, [np.array([px(q[0], q[2]) for q in t["pts"]], np.int32)], False, (40, 90, 200), 3)
for b in seed["buildings"]:
    sp = b["spec"]
    mx, _, mz = b["frontage_mid"]
    n = np.array(b["facing"])
    xd = np.array([n[1], -n[0]])
    W = b.get("W", 2 * sp["bays"])
    D = b.get("D", sp["depth"])
    o = np.array([mx, mz]) - xd * W / 2
    pts = np.array([px(*c) for c in (o, o + xd * W, o + xd * W - n * D, o - n * D)], np.int32)
    cv2.fillPoly(vis, [pts], tuple(int(c * 0.45) for c in COL[b["class"]]))
    cv2.polylines(vis, [pts], True, COL[b["class"]], 2)
    f = np.array([mx, mz])
    if b.get("door", True):
        cv2.line(vis, px(*f), px(*(f + n * 2.0)), (255, 255, 255), 2)
for name, (x0, y0, x1, y1) in {"center": (1800, 300, 3000, 1300), "castle": (900, 250, 1900, 1350), "south": (1900, 1000, 3000, 1650), "all": (700, 150, 3200, 1700)}.items():
    o_ = vis[y0:y1, x0:x1]
    if name == "all":
        o_ = cv2.resize(o_, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(ROOT / "reconstruction" / f"review_v4_{name}.png"), o_)
print("ok")

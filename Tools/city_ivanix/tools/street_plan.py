"""Authored street plan v1 (level design decision over the Ivanix layout's open corridors).

Centrelines in metres (x east, z north; plaza origin), widths in metres. Streets follow the layout's paved corridors
(read from the metric grids and the open-space medial axis); squares are polygons whose edges are frontage lines.
Writes reconstruction/street_plan_v1.json and a review image.
"""

import json
import os
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
# the layout captures are not redistributed: point JD_IVX_REFS at the local survey folder's references/
REFS = Path(os.environ.get("JD_IVX_REFS", str(ROOT / "references")))
KEEP = (-140.0, -12.0)


def ring(cx, cz, r, a0=0, a1=360, step=10):
    return [[round(cx + r * math.cos(math.radians(a)), 2), round(cz + r * math.sin(math.radians(a)), 2)] for a in range(a0, a1 + 1, step)]


STREETS = [
    # id, name, kind, width, centreline
    ("MAYOR", "Calle Mayor", "mayor", 10.0, [(-5, -17), (-4, -40), (-1, -65), (1, -90), (3, -108), (5, -124)]),
    ("MUELLE", "Calle del Muelle", "mayor", 11.0, [(-2, 21), (0, 34), (3, 45), (5, 52)]),
    ("IGLESIA", "Calle de la Iglesia", "calle", 5.0, [(4, 38), (18, 38), (28, 33), (32, 21)]),
    ("FINCA", "Calle de la Finca", "calle", 6.0, [(33, 16), (42, 25), (53, 25), (62, 17), (69, 4), (70, -10)]),
    ("LEVANTE", "Calle de Levante", "calle", 7.0, [(33, -12), (45, -18), (56, -24), (68, -30), (77, -38)]),
    ("LEVANTE_SUR", "Calle de Levante Sur", "calle", 6.0, [(2, -33), (15, -34), (30, -34), (45, -34), (58, -30)]),
    ("RONDA_LEVANTE", "Ronda de Levante", "calle", 5.0, [(58, -30), (62, -40), (64, -50), (62, -62)]),
    ("HOSPITAL", "Calle del Hospital", "calle", 5.0, [(30, -36), (33, -50), (36, -64), (36, -78), (40, -88), (46, -92)]),
    ("PONIENTE", "Calle de Poniente", "calle", 6.0, [(-18, 10), (-32, 13), (-46, 18), (-58, 24), (-67, 27)]),
    ("ALTA", "Calle Alta", "calle", 7.0, [(-5, 40), (-22, 45), (-42, 46), (-62, 47), (-78, 44)]),
    ("CERCA", "Calle de la Cerca", "calle", 6.0, [(-44, 45), (-45, 30), (-46, 18)]),
    ("RONDA_ALTO", "Ronda del Alto", "calle", 5.0, [(-78, 44), (-70, 28), (-74, 10), (-77, -5), (-78, -20), (-73, -32), (-71, -48), (-68, -58)]),
    ("POZO", "Callejón del Pozo", "callejon", 4.0, [(-52, 21), (-55, 3), (-40, -1), (-33, -15), (-22, -22)]),
    ("PONIENTE_SUR", "Calle de Poniente Sur", "calle", 6.0, [(-5, -27), (-22, -26), (-40, -28), (-56, -30), (-72, -32)]),
    ("HONDA", "Calle Honda", "calle", 5.0, [(-56, -30), (-57, -50), (-57, -70), (-54, -88)]),
    ("MURALLA_SUR", "Calle de la Muralla", "callejon", 4.5, [(-54, -88), (-40, -84), (-28, -88), (-15, -95), (-3, -104)]),
    ("MEDIO", "Calle del Medio", "callejon", 4.5, [(-3, -62), (-18, -60), (-32, -60), (-46, -56), (-57, -55)]),
    ("SOLANA", "Calle de la Solana", "callejon", 4.5, [(2, -66), (16, -66), (30, -64)]),
    ("PASEO_NORTE", "Paseo del Norte", "calle", 8.0, [(-155, 42), (-138, 50), (-122, 54), (-105, 54), (-92, 52), (-79, 46)]),
    ("CAMINO_RIBERA", "Camino de la Ribera", "camino", 5.0, [(97, -50), (110, -58), (120, -66), (133, -82), (142, -100), (146, -115)]),
    ("RIBERA_NORTE", "Camino del Prado", "camino", 5.0, [(97, -47), (108, -36), (122, -24), (140, -28), (152, -38)]),
]
RINGS = [
    ("ANILLO_ALTO", "Ronda de la Torre", "ronda", 5.0, ring(KEEP[0], KEEP[1], 24.5)),
    ("ANILLO_BAJO", "Paseo del Alto", "ronda", 12.0, ring(KEEP[0], KEEP[1], 47.0)),
]
PLAZAS = [
    ("PLAZA_MAYOR", "Plaza Mayor", [(-18, -15), (-8, -17), (8, -17), (32, -15), (34, 15), (24, 19), (-2, 22), (-18, 18)]),
]


def main():
    doc = {"schema": "juego-def.city-street-plan/1",
           "note": "authored over the Ivanix layout's open corridors; Ivanix composition, ENV01 architecture",
           "streets": [{"id": i, "name": n, "kind": k, "width": w, "pts": [list(map(float, q)) for q in pts]} for i, n, k, w, pts in STREETS],
           "rings": [{"id": i, "name": n, "kind": k, "width": w, "pts": pts, "closed": True} for i, n, k, w, pts in RINGS],
           "plazas": [{"id": i, "name": n, "poly": [list(map(float, q)) for q in pts]} for i, n, pts in PLAZAS]}
    (ROOT / "reconstruction" / "street_plan_v1.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    import cv2
    img = cv2.imread(str(REFS / "originals" / "REF0017H_city_cenital_calibrated_3840.png"))
    PL, M = (2200, 790), 0.16333
    px = lambda x, z: (int(round(PL[0] + x / M)), int(round(PL[1] - z / M)))
    vis = (img * 0.55).astype(np.uint8)
    for st in doc["streets"] + doc["rings"]:
        P = np.array(st["pts"])
        cv2.polylines(vis, [np.array([px(*q) for q in P], np.int32)], bool(st.get("closed")), (0, 255, 255), max(2, int(st["width"] / M / 6)))
        cv2.putText(vis, st["id"], px(*P[len(P) // 2]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    for pl in doc["plazas"]:
        cv2.polylines(vis, [np.array([px(*q) for q in pl["poly"]], np.int32)], True, (0, 128, 255), 3)
    o = cv2.resize(vis[150:1700, 700:3200], None, fx=0.6, fy=0.6, interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(ROOT / "reconstruction" / "street_plan_v1.png"), o)
    print(len(doc["streets"]), "streets,", len(doc["rings"]), "rings,", len(doc["plazas"]), "plazas")


if __name__ == "__main__":
    main()

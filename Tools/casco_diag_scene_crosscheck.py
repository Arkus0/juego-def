#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""casco_diag_scene_crosscheck.py — verify the diagnostic's plot geometry against the
COMMITTED ENV01 scene bytes, without opening Unity (read-only, streaming YAML parse).

For a deterministic sample of buildings (>= 24, across >= 6 rows / >= 3 streets, plus
specials: unit tower, landmark, polish-raised/floors plots, extreme widths, one
river/plaza/bridge-row building) it compares, per building:

  * local position   expected (x0, y, -setback)   vs the scene Transform
  * local scale      expected (w/(bays*2), 1, 1)  vs the scene Transform
  * frame position   expected (origin.x, 0, origin.z)
  * frame yaw        expected atan2(-dir.z, dir.x) vs the scene quaternion
  * transform father building -> its row frame transform (scene hierarchy linkage)
  * world rect centroid  tool rect vs frame_actual * local_actual

Expected values come from Tools/casco_diagnostic.build_records (the same code that
produced the diagnostic), so a green crosscheck proves the diagnostic's coordinate
conventions against the authoritative scene. Any mismatch is REPORTED AS DATA
(scene/spec divergence is a finding, never "fixed" here).

Usage: python Tools/casco_diag_scene_crosscheck.py [--out FILE]
"""

import argparse
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from casco_diagnostic import (FOOTING_MARGIN, RIVER_BASEMENT_MIN, build_records,
                              load_inputs, sha256_of)  # noqa: E402

SCENE = "Unity/JuegoDef/Assets/JuegoDef/Scenes/ENV/ENV01_Casco_District.unity"
TOL_POS = 0.002     # m — Unity YAML stores ~7 significant digits
TOL_YAW = 0.01      # deg
TOL_SCALE = 0.001

GO_HDR = re.compile(r"^--- !u!1 &(\d+)$")
TR_HDR = re.compile(r"^--- !u!4 &(\d+)$")
NAME = re.compile(r"^  m_Name: (.+?)\s*$")
COMP = re.compile(r"component: \{fileID: (\d+)\}")
POS = re.compile(r"m_LocalPosition: \{x: ([-\d.eE]+), y: ([-\d.eE]+), z: ([-\d.eE]+)\}")
ROT = re.compile(r"m_LocalRotation: \{x: ([-\d.eE]+), y: ([-\d.eE]+), z: ([-\d.eE]+), w: ([-\d.eE]+)\}")
SCL = re.compile(r"m_LocalScale: \{x: ([-\d.eE]+), y: ([-\d.eE]+), z: ([-\d.eE]+)\}")
FATHER = re.compile(r"m_Father: \{fileID: (\d+)\}")
KNAME = re.compile(r"^K\d+_\d+(?:_\d+)?$")


def parse_scene(path):
    """Single streaming pass: K-named GameObjects + ALL Transform components."""
    k_gos = {}       # name -> (go_fileid, [component ids])
    transforms = {}  # fileID -> dict
    dup = []
    cls = fid = None
    name = None
    comps = []
    pos = rot = scl = father = got = None

    def flush_go():
        if cls == 1 and name is not None and KNAME.match(name):
            if name in k_gos:
                dup.append(name)
            k_gos[name] = (fid, comps)

    def flush_tr():
        if cls == 4 and pos and rot and scl:
            transforms[fid] = {"pos": pos, "rot": rot, "scl": scl, "father": father, "go": got}

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("--- !u!"):
                flush_go()
                flush_tr()
                cls = fid = name = None
                comps = []
                pos = rot = scl = father = got = None
                m = GO_HDR.match(line.rstrip("\r\n"))
                if m:
                    cls, fid = 1, m.group(1)
                    continue
                m = TR_HDR.match(line.rstrip("\r\n"))
                if m:
                    cls, fid = 4, m.group(1)
                    continue
                cls = -1
                continue
            if cls == 1:
                if name is None:
                    m = NAME.match(line)
                    if m:
                        name = m.group(1)
                m = COMP.search(line)
                if m:
                    comps.append(m.group(1))
            elif cls == 4:
                if pos is None:
                    m = POS.search(line)
                    if m:
                        pos = tuple(float(v) for v in m.groups())
                if rot is None:
                    m = ROT.search(line)
                    if m:
                        rot = tuple(float(v) for v in m.groups())
                if scl is None:
                    m = SCL.search(line)
                    if m:
                        scl = tuple(float(v) for v in m.groups())
                if father is None:
                    m = FATHER.search(line)
                    if m:
                        father = m.group(1)
                if got is None:
                    m = re.search(r"m_GameObject: \{fileID: (\d+)\}", line)
                    if m:
                        got = m.group(1)
    flush_go()
    flush_tr()
    return k_gos, transforms, dup


def transform_of(name, k_gos, transforms):
    entry = k_gos.get(name)
    if not entry:
        return None
    for cid in entry[1]:
        if cid in transforms:
            return transforms[cid]
    return None


def yaw_of(rot):
    x, y, z, w = rot
    yaw = math.degrees(2.0 * math.atan2(y, w))
    while yaw <= -180.0:
        yaw += 360.0
    while yaw > 180.0:
        yaw -= 360.0
    return yaw


def min_angle_delta(a, b):
    d = (a - b) % 360.0
    if d > 180.0:
        d -= 360.0
    return abs(d)


def world_of(frame_t, local_pos, yaw_deg):
    rad = math.radians(yaw_deg)
    c, s = math.cos(rad), math.sin(rad)
    lx, ly, lz = local_pos
    fx, fy, fz = frame_t["pos"]
    return (fx + lx * c + lz * s, fy + ly, fz - lx * s + lz * c)


def pick_samples(recs):
    blds = [r for r in recs if r["kind"] == "building"]
    by_row = {}
    for r in blds:
        by_row.setdefault(r["row_id"], []).append(r)
    row_ids = sorted(by_row, key=lambda rid: by_row[rid][0]["row_index"])
    picked = []
    stride = max(1, len(row_ids) // 10)
    for rid in row_ids[::stride]:
        rs = by_row[rid]
        picked += [rs[0], rs[len(rs) // 2], rs[-1]]
    specials = ["K8_3_0", "K14_3_0", "K14_1_0", "K11_0_1", "K14_3_6"]
    widest = max(blds, key=lambda r: r["w"])
    narrow = min(blds, key=lambda r: r["w"])
    specials += [widest["id"], narrow["id"]]
    for role in ("river", "plaza", "bridge", "main", "lane"):
        rr = [r for r in blds if r["role"] == role]
        if rr:
            specials.append(rr[len(rr) // 2]["id"])
    seen = set()
    out = []
    for r in picked + [b for b in blds if b["id"] in specials]:
        if r["id"] not in seen:
            seen.add(r["id"])
            out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", default=SCENE)
    ap.add_argument("--spec", default="Unity/JuegoDef/Assets/JuegoDef/Env/Specs/districts/ENV01_Casco_District.json")
    ap.add_argument("--units", default="Unity/JuegoDef/Assets/JuegoDef/Env/Specs/units.json")
    ap.add_argument("--polish", default="Unity/JuegoDef/Assets/JuegoDef/Env/Specs/districts/ENV01_Casco_District.polish.json")
    ap.add_argument("--config", default="Tools/casco_diagnostic.config.json")
    ap.add_argument("--out", default="Docs/evidence/CASCO-V2-DIAG/scene_crosscheck.json")
    args = ap.parse_args()

    spec, units, polish, cfg = load_inputs(args)
    recs = build_records(spec, units, polish, cfg)
    k_gos, transforms, dup = parse_scene(args.scene)

    samples = pick_samples(recs)
    rows = []
    n_ok = 0
    streets = set()
    rows_used = set()
    for r in samples:
        streets.add(r["street"])
        rows_used.add(r["row_id"])
        bt = transform_of(r["id"], k_gos, transforms)
        ft = transform_of(r["row_id"], k_gos, transforms)
        entry = {"id": r["id"], "row": r["row_id"], "street": r["street"], "role": r["role"]}
        if bt is None or ft is None:
            entry["ok"] = False
            entry["error"] = "not found in scene" + ("" if bt else " (frame missing)")
            rows.append(entry)
            continue
        exp_pos = (r["x0"], r["y"], -r["setback"])
        d_pos = max(abs(a - b) for a, b in zip(exp_pos, bt["pos"]))
        exp_scale = r["scale"] if abs(r["scale"] - 1.0) > 0.001 else 1.0
        d_scale = max(abs(exp_scale - bt["scl"][0]),
                      abs(bt["scl"][1] - 1.0), abs(bt["scl"][2] - 1.0))
        frame_exp = (r["frame"].ox, 0.0, r["frame"].oz)
        d_frame = max(abs(a - b) for a, b in zip(frame_exp, ft["pos"]))
        d_yaw = min_angle_delta(yaw_of(ft["rot"]), r["frame"].yaw_deg)
        father_ok = bt["father"] and bt["father"] in transforms \
            and transforms[bt["father"]].get("go") == k_gos.get(r["row_id"], (None,))[0]
        # the four footprint corners as the scene itself would place them:
        # frame_actual * (x0|x0+w, ., -setback-depth|-setback)
        yaw = yaw_of(ft["rot"])
        corners_scene = [world_of(ft, (lx, 0.0, lz), yaw)
                         for lx, lz in ((r["x0"], -r["setback"] - r["depth"]),
                                        (r["x0"] + r["w"], -r["setback"] - r["depth"]),
                                        (r["x0"] + r["w"], -r["setback"]),
                                        (r["x0"], -r["setback"]))]
        corners_tool = r["rect_xz"][:4]
        d_world = max(max(abs(a[0] - b[0]), abs(a[2] - b[1]))
                      for a, b in zip(corners_scene, corners_tool))
        ok = d_pos <= TOL_POS and d_scale <= TOL_SCALE and d_frame <= TOL_POS \
            and d_yaw <= TOL_YAW and father_ok and d_world <= TOL_POS
        n_ok += ok
        entry.update({
            "ok": ok,
            "d_local_pos_m": round(d_pos, 6),
            "d_local_scale": round(d_scale, 6),
            "d_frame_pos_m": round(d_frame, 6),
            "d_frame_yaw_deg": round(d_yaw, 6),
            "d_world_center_m": round(d_world, 6),
            "father_is_frame": bool(father_ok),
            "expected_local": [round(v, 4) for v in exp_pos],
            "scene_local": list(bt["pos"]),
        })
        rows.append(entry)

    doc = {
        "tool": "Tools/casco_diag_scene_crosscheck.py",
        "purpose": "verificacion mecanica de las convenciones geometricas del diagnostico contra los bytes commitados de la escena; read-only",
        "inputs": {
            "scene": {"path": args.scene, "sha256": sha256_of(args.scene)},
            "spec": {"path": args.spec, "sha256": sha256_of(args.spec)},
        },
        "tolerances": {"pos_m": TOL_POS, "yaw_deg": TOL_YAW, "scale": TOL_SCALE},
        "summary": {
            "n_samples": len(samples), "n_ok": n_ok,
            "n_streets": len(streets), "n_rows": len(rows_used),
            "duplicate_go_names": dup,
            "scene_gameobjects_knamed": len(k_gos),
            "scene_transforms_total": len(transforms),
            "all_ok": n_ok == len(samples),
        },
        "samples": rows,
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(doc, sort_keys=True, indent=2, ensure_ascii=False) + "\n")
    print("crosscheck: %d/%d ok (rows=%d streets=%d) -> %s"
          % (n_ok, len(samples), len(rows_used), len(streets), args.out))
    for e in rows:
        if not e.get("ok"):
            print("  MISMATCH:", json.dumps({k: e[k] for k in e if k != "scene_local"}))


if __name__ == "__main__":
    main()

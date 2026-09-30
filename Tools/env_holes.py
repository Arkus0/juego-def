"""Counts holes in ENV walk captures made with a magenta background (EnvWalk.Street(..., holes: true)).

    python Tools/env_holes.py <folder> [--lower 0.45] [--min 4] [--csv out.csv]

Any magenta pixel in the lower part of a frame is a gap in the geometry (a crack between ground meshes, a wall/ground
joint) through which the background shows: the upper part is skipped because the sky is magenta too. Antialiased
hairlines blend with their surroundings, so a pixel counts when its magenta-ness (min(R,B) - G) is high.
"""
import argparse
import csv
from pathlib import Path

import numpy as np
from PIL import Image


def holes(path, lower):
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
    h = a.shape[0]
    part = a[int(h * (1 - lower)):]
    mag = np.minimum(part[..., 0], part[..., 2]) - part[..., 1]
    return int((mag > 90).sum()), int(part.shape[0] * part.shape[1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--lower", type=float, default=0.45, help="fraction of the frame, from the bottom, that is inspected")
    ap.add_argument("--min", type=int, default=4, help="report frames with at least this many hole pixels")
    ap.add_argument("--csv")
    args = ap.parse_args()
    rows = []
    for f in sorted(Path(args.folder).glob("*.jpg")):
        n, total = holes(f, args.lower)
        rows.append((f.name, n, total))
    flagged = [r for r in rows if r[1] >= args.min]
    total_px = sum(r[1] for r in rows)
    print(f"{len(rows)} frames, {len(flagged)} with >= {args.min} hole pixels, {total_px} hole pixels in total")
    for name, n, _ in sorted(flagged, key=lambda r: -r[1])[:15]:
        print(f"  {n:6d}  {name}")
    if args.csv:
        with open(args.csv, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["frame", "hole_pixels", "inspected_pixels"])
            w.writerows(rows)


if __name__ == "__main__":
    main()

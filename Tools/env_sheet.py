"""Contact sheets for ENV review shots (EnvShots.Capture output).

    python Tools/env_sheet.py grid  <folder> <out.jpg> [--cols 3] [--only S01,S02]
    python Tools/env_sheet.py pairs <before_folder> <after_folder> <out.jpg> [--only S01,S02]

`pairs` puts the same shot name side by side (before | after), one row per shot.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def font(size):
    for f in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def label(img, text):
    d = ImageDraw.Draw(img)
    f = font(max(14, img.width // 45))
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f)
    d.rectangle((0, 0, x1 - x0 + 16, y1 - y0 + 12), fill=(0, 0, 0))
    d.text((8, 5 - y0), text, fill=(255, 255, 255), font=f)
    return img


def shots(folder, only):
    files = sorted(Path(folder).glob("*.jpg"))
    return [f for f in files if not only or f.stem.split("_")[0] in only or f.stem in only]


def grid(args):
    files = shots(args.folder, args.only)
    tw = args.width
    ims = [label(Image.open(f).convert("RGB").resize((tw, tw * 9 // 16)), f.stem) for f in files]
    cols = args.cols
    rows = (len(ims) + cols - 1) // cols
    th = tw * 9 // 16
    sheet = Image.new("RGB", (cols * tw + (cols - 1) * 6, rows * th + (rows - 1) * 6), (20, 20, 20))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * (tw + 6), (i // cols) * (th + 6)))
    sheet.save(args.out, quality=88)
    print(f"sheet {len(ims)} -> {args.out}")


def pairs(args):
    b = {f.stem: f for f in shots(args.before, args.only)}
    a = {f.stem: f for f in shots(args.after, args.only)}
    names = [n for n in b if n in a]
    tw = args.width
    th = tw * 9 // 16
    sheet = Image.new("RGB", (2 * tw + 6, len(names) * (th + 6) - 6), (20, 20, 20))
    for i, n in enumerate(names):
        sheet.paste(label(Image.open(b[n]).convert("RGB").resize((tw, th)), n + "  antes"), (0, i * (th + 6)))
        sheet.paste(label(Image.open(a[n]).convert("RGB").resize((tw, th)), n + "  después"), (tw + 6, i * (th + 6)))
    sheet.save(args.out, quality=88)
    print(f"pairs {len(names)} -> {args.out}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("grid")
    g.add_argument("folder")
    g.add_argument("out")
    g.add_argument("--cols", type=int, default=3)
    g.add_argument("--width", type=int, default=640)
    g.add_argument("--only", type=lambda s: set(s.split(",")), default=None)
    p = sub.add_parser("pairs")
    p.add_argument("before")
    p.add_argument("after")
    p.add_argument("out")
    p.add_argument("--width", type=int, default=800)
    p.add_argument("--only", type=lambda s: set(s.split(",")), default=None)
    args = ap.parse_args()
    grid(args) if args.cmd == "grid" else pairs(args)


if __name__ == "__main__":
    main()

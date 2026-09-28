"""Urban morphology from a real reference (ENV composition input).

Measures the spatial structure of a small real town area from OpenStreetMap geometry (building footprints + street
centrelines) so a district layout can be traced from a reference instead of invented: facade-to-facade street widths
and how they vary, plot frontages, setback jogs between neighbours, straight-run lengths and bend angles, footprint
sizes. Used for the CASCO reference study (WP-PROD-ENV-01, owner request 2026-09-28; see
Docs/production/ENV_COMPOSITION_RULES.md).

    python Tools/env_morphology.py fetch   --bbox 43.1512,-4.6290,43.1572,-4.6185 --out <scratch>/osm.json
    python Tools/env_morphology.py measure --osm <scratch>/osm.json --origin 43.1542,-4.6237 --box -70,-210,200,-10 \
                                           --streets "ntabra|Cimavilla|Doctor Encinas" --out metrics.json
    python Tools/env_morphology.py plan    --osm <scratch>/osm.json --origin 43.1542,-4.6237 --box -70,-210,200,-10 \
                                           --scale 4 --out plan.png

Raw OSM extracts stay out of the repository (fetch them again); derived measurements carry the ODbL attribution
"(c) OpenStreetMap contributors". Needs numpy (measure) and Pillow (plan).
"""
import argparse
import json
import math
import statistics as st
import sys
import urllib.parse
import urllib.request

ATTRIBUTION = "(c) OpenStreetMap contributors, ODbL 1.0 (https://www.openstreetmap.org/copyright)"
MIRRORS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter",
           "https://maps.mail.ru/osm/tools/overpass/api/interpreter"]


# ---------------------------------------------------------------- fetch

def fetch(bbox, out):
    s, w, n, e = bbox
    b = f"({s},{w},{n},{e})"
    q = (f'[out:json][timeout:60];(way["building"]{b};way["highway"]{b};way["waterway"]{b};'
         f'way["place"="square"]{b};way["area:highway"]{b};relation["building"]{b};);out body geom;')
    data = urllib.parse.urlencode({"data": q}).encode()
    for url in MIRRORS:
        try:
            req = urllib.request.Request(url, data=data, headers={"User-Agent": "JuegoDef-ENV-morphology/1.0"})
            body = urllib.request.urlopen(req, timeout=90).read()
            doc = json.loads(body)
            json.dump(doc, open(out, "w", encoding="utf-8"))
            print(f"fetched {len(doc['elements'])} elements from {url} (OSM base {doc['osm3s']['timestamp_osm_base']})")
            return
        except Exception as ex:  # busy mirror: try the next one
            print(f"{url}: {ex}", file=sys.stderr)
    sys.exit("ENV_MORPHOLOGY_FETCH_FAILED")


# ---------------------------------------------------------------- geometry

class Frame:
    """Local metric frame (x east, y north) around an origin; equirectangular is exact enough for a few hundred m."""

    def __init__(self, lat0, lon0):
        self.lat0, self.lon0 = lat0, lon0
        self.kx = 111320 * math.cos(math.radians(lat0))
        self.ky = 110540

    def xy(self, p):
        import numpy as np
        return np.array(((p["lon"] - self.lon0) * self.kx, (p["lat"] - self.lat0) * self.ky))


def dp(line, eps):
    """Douglas-Peucker simplification of a 2D polyline."""
    import numpy as np
    if len(line) < 3:
        return line
    a, b = line[0], line[-1]
    ab = b - a
    L = np.linalg.norm(ab)
    d = np.linalg.norm(line - a, axis=1) if L < 1e-9 else np.abs(ab[0] * (line[:, 1] - a[1]) - ab[1] * (line[:, 0] - a[0])) / L
    i = int(np.argmax(d))
    if d[i] > eps:
        return np.vstack([dp(line[:i + 1], eps)[:-1], dp(line[i:], eps)])
    return np.array([a, b])


def chain(ways):
    """Joins the way polylines of one street into the longest connected chain."""
    import numpy as np
    segs = [list(map(tuple, w)) for w in ways]
    best = []
    for start in range(len(segs)):
        line = list(segs[start]); used = {start}; grew = True
        while grew:
            grew = False
            for j, s in enumerate(segs):
                if j in used: continue
                if np.allclose(s[0], line[-1], atol=0.5): line += s[1:]
                elif np.allclose(s[-1], line[-1], atol=0.5): line += s[::-1][1:]
                elif np.allclose(s[-1], line[0], atol=0.5): line = s[:-1] + line
                elif np.allclose(s[0], line[0], atol=0.5): line = s[::-1][:-1] + line
                else: continue
                used.add(j); grew = True
        if len(line) > len(best): best = line
    return np.array(best)


def resample(line, step=1.0):
    import numpy as np
    out = [line[0]]; acc = 0.0
    for a, b in zip(line[:-1], line[1:]):
        seg = np.linalg.norm(b - a)
        if seg < 1e-6: continue
        t = step - acc
        while t <= seg:
            out.append(a + (b - a) * t / seg); t += step
        acc = seg - (t - step)
    return np.array(out)


# ---------------------------------------------------------------- measure

def measure(doc, frame, box, streets):
    import numpy as np
    buildings = []
    for e in doc["elements"]:
        if "building" in e.get("tags", {}) and "geometry" in e:
            pts = np.array([frame.xy(p) for p in e["geometry"]])
            c = pts.mean(axis=0)
            if box[0] - 40 < c[0] < box[2] + 40 and box[1] - 40 < c[1] < box[3] + 40:
                buildings.append((e["id"], pts))
    edges = [(bid, pts[i], pts[i + 1]) for bid, pts in buildings for i in range(len(pts) - 1)]
    EA = np.array([e[1] for e in edges]); EB = np.array([e[2] for e in edges]); EID = [e[0] for e in edges]

    def ray(o, d, maxd=20.0):
        v1 = o - EA; v2 = EB - EA; v3 = np.array([-d[1], d[0]])
        den = v2 @ v3
        with np.errstate(divide="ignore", invalid="ignore"):
            t1 = (v2[:, 0] * v1[:, 1] - v2[:, 1] * v1[:, 0]) / den
            t2 = (v1 @ v3) / den
        ok = (np.abs(den) > 1e-9) & (t1 > 0.05) & (t1 < maxd) & (t2 >= 0) & (t2 <= 1)
        if not ok.any(): return None
        i = np.where(ok)[0][np.argmin(t1[ok])]
        return t1[i], EID[i]

    def pct(v):
        return [round(float(x), 1) for x in np.percentile(v, [10, 50, 90])] if v else None

    report = {"attribution": ATTRIBUTION, "osm_base": doc.get("osm3s", {}).get("timestamp_osm_base"), "streets": {}}
    for key in streets:
        ways = [np.array([frame.xy(p) for p in e["geometry"]]) for e in doc["elements"]
                if "highway" in e.get("tags", {}) and key in e["tags"].get("name", "") and "geometry" in e]
        if not ways: continue
        line = chain(ways)
        s = resample(line, 1.0)
        widths, sides = [], {"l": [], "r": []}
        for i in range(1, len(s) - 1):
            d = s[i + 1] - s[i - 1]; d /= np.linalg.norm(d)
            n = np.array([-d[1], d[0]])
            hl, hr = ray(s[i], n), ray(s[i], -n)
            sides["l"].append(hl); sides["r"].append(hr)
            if hl and hr and hl[0] + hr[0] < 30: widths.append(hl[0] + hr[0])
        fronts, jogs, open_n = [], [], 0
        for side in sides.values():
            runs, cur = [], None
            for h in side:
                if h is None or h[0] > 12:
                    open_n += 1
                    if cur: runs.append(cur); cur = None
                    continue
                if cur and cur["bid"] == h[1]: cur["n"] += 1; cur["t"].append(h[0])
                else:
                    if cur: runs.append(cur)
                    cur = {"bid": h[1], "n": 1, "t": [h[0]]}
            if cur: runs.append(cur)
            runs = [r for r in runs if r["n"] >= 2]
            fronts += [r["n"] for r in runs]
            off = [st.median(r["t"]) for r in runs]
            jogs += [abs(a - b) for a, b in zip(off[:-1], off[1:])]
        simp = dp(line, 0.8)
        segs = list(zip(simp[:-1], simp[1:]))
        ang = lambda u: math.degrees(math.atan2(u[1], u[0]))
        turns = [round((ang(d - c) - ang(b - a) + 540) % 360 - 180, 1) for (a, b), (c, d) in zip(segs[:-1], segs[1:])]
        report["streets"][key] = {
            "length_m": len(s) - 1,
            "width_facade_to_facade_p10_p50_p90": pct(widths),
            "width_min_max": [round(min(widths), 1), round(max(widths), 1)] if widths else None,
            "frontage_p10_p50_p90": pct(fronts),
            "setback_jog_between_neighbours_p50_p90": [round(float(x), 1) for x in np.percentile(jogs, [50, 90])] if jogs else None,
            "jogs_over_0_5m_share": round(sum(1 for j in jogs if j > 0.5) / max(1, len(jogs)), 2),
            "open_side_share": round(open_n / max(1, 2 * (len(s) - 2)), 2),
            "straight_runs_m": [round(float(np.linalg.norm(b - a)), 1) for a, b in segs],
            "bend_angles_deg": turns,
        }
    dims = []
    for bid, pts in buildings:
        c = pts.mean(axis=0)
        if not (box[0] < c[0] < box[2] and box[1] < c[1] < box[3]) or len(pts) < 4: continue
        p = pts[:-1] - pts[:-1].mean(axis=0)
        _, v = np.linalg.eigh(p.T @ p)
        ext = (p @ v).max(axis=0) - (p @ v).min(axis=0)
        dims.append((min(ext), max(ext)))
    if dims:
        dims = np.array(dims)
        report["footprints"] = {"count": len(dims), "short_side_p10_p50_p90": pct(list(dims[:, 0])),
                                "long_side_p10_p50_p90": pct(list(dims[:, 1]))}
    return report


# ---------------------------------------------------------------- plan

def plan(doc, frame, box, scale, out):
    from PIL import Image, ImageDraw, ImageFont
    W, H = int((box[2] - box[0]) * scale), int((box[3] - box[1]) * scale)
    img = Image.new("RGB", (W, H), (245, 243, 236)); dr = ImageDraw.Draw(img)
    px = lambda q: ((q[0] - box[0]) * scale, (box[3] - q[1]) * scale)
    try: font = ImageFont.truetype("arial.ttf", max(10, int(4 * scale)))
    except Exception: font = ImageFont.load_default()
    els = [e for e in doc["elements"] if "geometry" in e]
    for e in els:
        if "waterway" in e.get("tags", {}):
            dr.line([px(frame.xy(p)) for p in e["geometry"]], fill=(120, 170, 220), width=max(2, int(3 * scale)))
    for e in els:
        if "building" in e.get("tags", {}) and len(e["geometry"]) > 2:
            dr.polygon([px(frame.xy(p)) for p in e["geometry"]], fill=(196, 150, 120), outline=(90, 60, 45))
    labels = {}
    for e in els:
        t = e.get("tags", {})
        if "highway" in t:
            col = {"footway": (60, 140, 60), "steps": (200, 40, 40), "pedestrian": (40, 110, 160)}.get(t["highway"], (70, 70, 70))
            dr.line([px(frame.xy(p)) for p in e["geometry"]], fill=col, width=1)
            if t.get("name"): labels.setdefault(t["name"], px(frame.xy(e["geometry"][len(e["geometry"]) // 2])))
    for n, p in labels.items(): dr.text(p, n, fill=(20, 20, 120), font=font)
    dr.line([(20, H - 20), (20 + 20 * scale, H - 20)], fill=(0, 0, 0), width=3)
    dr.text((20, H - 40), "20 m", fill=(0, 0, 0), font=font)
    dr.text((W - 330, H - 20), ATTRIBUTION[:40], fill=(90, 90, 90), font=font)
    img.save(out)
    print(out, W, H)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch"); f.add_argument("--bbox", required=True); f.add_argument("--out", required=True)
    for name in ("measure", "plan"):
        p = sub.add_parser(name)
        p.add_argument("--osm", required=True); p.add_argument("--origin", required=True)
        p.add_argument("--box", required=True, help="x0,y0,x1,y1 metres around the origin"); p.add_argument("--out", required=True)
        if name == "measure": p.add_argument("--streets", required=True, help="name substrings separated by |")
        else: p.add_argument("--scale", type=float, default=4.0, help="pixels per metre")
    a = ap.parse_args()
    if a.cmd == "fetch":
        return fetch([float(v) for v in a.bbox.split(",")], a.out)
    doc = json.load(open(a.osm, encoding="utf-8"))
    lat0, lon0 = (float(v) for v in a.origin.split(","))
    box = [float(v) for v in a.box.split(",")]
    frame = Frame(lat0, lon0)
    if a.cmd == "measure":
        rep = measure(doc, frame, box, a.streets.split("|"))
        json.dump(rep, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print(json.dumps(rep, indent=1, ensure_ascii=False))
    else:
        plan(doc, frame, box, a.scale, a.out)


if __name__ == "__main__":
    main()

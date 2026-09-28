"""ENV factory catalogue: discovery, lineage and coverage checks (standard library only).

    python Tools/env_catalog.py search --demand shopfront_service_threshold
    python Tools/env_catalog.py search --query quay
    python Tools/env_catalog.py modules [--query balcony]
    python Tools/env_catalog.py lineage          # regenerate ENV records in Docs/asset_catalog/lineage.json
    python Tools/env_catalog.py check            # B0 demand coverage + library/lineage integrity
    python Tools/env_catalog.py inventory        # evidence inventory table

Inputs: Docs/asset_catalog/env_library.json (written by Unity "JuegoDef > ENV > 3 Build Library"),
Docs/asset_catalog/env_derive_manifest.json (written by Tools/blender/env_derive.py), the Unity grammar/spec JSON
and the PROD-ASSET-00 catalogue. The lineage command reads GUID references straight from the Unity text assets,
so a record always reflects what the committed prefab/material actually uses.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROJECT = REPO / "Unity" / "JuegoDef"
DERIVED = PROJECT / "Assets" / "JuegoDef" / "Derived" / "ENV"
GRAMMAR = PROJECT / "Assets" / "JuegoDef" / "Env" / "Grammar"
SPECS = PROJECT / "Assets" / "JuegoDef" / "Env" / "Specs"
CATALOG = REPO / "Docs" / "evidence" / "WP-PROD-ASSET-00" / "catalog.json"
LINEAGE = REPO / "Docs" / "asset_catalog" / "lineage.json"
LIBRARY = REPO / "Docs" / "asset_catalog" / "env_library.json"
MANIFEST = REPO / "Docs" / "asset_catalog" / "env_derive_manifest.json"
VENDOR = PROJECT / "Assets" / "ThirdParty" / "Quaternius"
GUID_RE = re.compile(r"guid: ([0-9a-f]{32})")
TEX_RE = re.compile(r"m_Texture: \{fileID: -?\d+, guid: ([0-9a-f]{32})")
SHADER_RE = re.compile(r"m_Shader: \{fileID: -?\d+, guid: ([0-9a-f]{32})")

# CITY-URBAN-00 ENV demand matrix rows (Docs/design/CITY_URBAN_00_HANDOFF.md) served by the factory.
DEMAND = {
    "mixed_commercial_facade": "ordinary mixed/commercial facades",
    "shopfront_service_threshold": "shopfront + distinct service threshold",
    "lodging_frontage": "lodging frontage / return-anchor language",
    "corners_terminations": "corners / terminations / junction-facing pieces",
    "street_kerb_pavement_drain": "street / kerb / pavement / drainage-compatible edge family",
    "stairs_ramps_retaining": "stairs / ramps / retaining family",
    "quay_public_edge_railings": "quay / public working-water edge + railings",
    "controlled_yard_boundary": "controlled work yard kept distinct from the public edge",
    "port_market_shop_street_props": "port / market / shop / street props",
    "closed_ordinary_frontage": "ordinary closed frontage",
    "shallow_interior_threshold": "shallow interior / threshold pieces",
    "signage_utilities_furniture": "signage mounting / utilities / street furniture",
    "damp_palette_families": "damp northern material/palette families",
}


# Kit materials are bound to their FBX models by Unity's name search at import time (no GUID in prefab or model
# .meta text), so each vendor material is attributed to one representative kit module observed to carry it
# (Unity inspection 2026-09-28, WP-PROD-ENV-01).
MATERIAL_REPRESENTATIVE = {
    "MI_Plaster": "Wall_Plaster_Straight", "MI_WoodTrim": "Window_Wide_Flat1", "MI_WoodTrim_Wear": "Door_4_Flat",
    "MI_RockTrim": "DoorFrame_Flat_Brick", "MI_UnevenBrick": "Wall_UnevenBrick_Straight", "MI_Brick": "Floor_Brick",
    "MI_RoundRocks": "Floor_RoundRocks", "MI_RoundTiles": "Roof_RoundTiles_6x8", "MI_FlatTiles": "Roof_FlatTiles_6x8",
    "MI_WindowGlass": "Window_Wide_Flat1", "MI_MetalOrnaments": "Prop_MetalFence_Simple",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return path.relative_to(PROJECT).as_posix()


def meta_guid(path: Path) -> str | None:
    meta = path.with_name(path.name + ".meta")
    if not meta.is_file():
        return None
    m = GUID_RE.search(meta.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else None


def refs(path: Path) -> set[str]:
    """GUIDs referenced by a Unity text asset (prefab/material) or by a model's .meta (material remaps)."""
    target = path.with_name(path.name + ".meta") if path.suffix.lower() == ".fbx" else path
    if not target.is_file():
        return set()
    text = target.read_text(encoding="utf-8", errors="replace")
    own = meta_guid(path)
    if path.suffix.lower() == ".mat":
        return set(TEX_RE.findall(text)) - {own}  # a shader is not a source asset
    return {g for g in GUID_RE.findall(text) if g != own} - set(SHADER_RE.findall(text))


class Resolver:
    """Maps any referenced GUID to PROD-ASSET-00 catalogue IDs (directly, through a derived file, or through the
    vendor material/texture it belongs to)."""

    def __init__(self):
        catalog = load(CATALOG)
        self.ids = {i["id"] for i in catalog["items"]}
        self.by_guid = {i["unityGuid"]: i["id"] for i in catalog["items"] if i.get("unityGuid")}
        self.by_name = {(i["pack"], i["name"]): i["id"] for i in catalog["items"]}
        self.derived = {}
        for f in DERIVED.rglob("*"):
            if f.is_file() and not f.name.endswith(".meta"):
                g = meta_guid(f)
                if g:
                    self.derived[g] = f
        # vendor Medieval materials/textures -> the catalogue prefabs that use them (representative = first id)
        self.vendor_users: dict[str, set[str]] = {}
        med = VENDOR / "MedievalVillage"
        mat_tex: dict[str, set[str]] = {}
        for mat in med.rglob("*.mat"):
            g = meta_guid(mat)
            if g:
                mat_tex[g] = set(TEX_RE.findall(mat.read_text(encoding="utf-8", errors="replace")))
        for mat in med.rglob("*.mat"):
            rep = MATERIAL_REPRESENTATIVE.get(mat.stem)
            g = meta_guid(mat)
            if not rep or not g:
                continue
            owner = self.by_name[("medieval", rep)]
            self.vendor_users.setdefault(g, set()).add(owner)
            for t in mat_tex.get(g, ()):
                self.vendor_users.setdefault(t, set()).add(owner)
        manifest = load(MANIFEST)
        def donor_id(d):
            for pack in ("medieval", "props", "nature"):
                if (pack, d) in self.by_name:
                    return self.by_name[(pack, d)]
            raise KeyError(f"derive manifest donor not in catalogue: {d}")
        self.mesh_donors = {name: [donor_id(d) for d in entry["donors"]] for name, entry in manifest.items()}
        self.recipes = {m["name"]: m for m in load(GRAMMAR / "materials.json")["materials"]}
        self.textures = {t["name"]: t for t in load(GRAMMAR / "materials.json")["textures"]}
        self.wrappers = {w["name"]: w for w in load(GRAMMAR / "modules.json")["wrappers"]}
        self.cache: dict[str, set[str]] = {}

    def of_guid(self, g: str, depth=0) -> set[str]:
        if g in self.by_guid:
            return {self.by_guid[g]}
        if g in self.derived:
            return self.of_file(self.derived[g], depth + 1)
        users = self.vendor_users.get(g)
        return {sorted(users)[0]} if users else set()

    def of_file(self, path: Path, depth=0) -> set[str]:
        key = rel(path)
        if key in self.cache or depth > 12:
            return self.cache.get(key, set())
        self.cache[key] = set()
        name = path.stem
        out: set[str] = set()
        if path.suffix.lower() == ".fbx":
            out |= set(self.mesh_donors.get(name, []))
        if path.suffix.lower() == ".png" and name in self.textures:
            src = self.textures[name]["source"]
            for tex in (VENDOR / "MedievalVillage").rglob(src + ".png"):
                g = meta_guid(tex)
                if g and g in self.vendor_users:
                    out.add(sorted(self.vendor_users[g])[0])
        if path.suffix.lower() == ".mat" and name in self.recipes and self.recipes[name].get("sources"):
            out |= set(self.recipes[name]["sources"])
        if path.suffix.lower() == ".prefab" and name in self.wrappers:
            # a wrapper is the wrapped model plus a collider and owned materials: its source is that model
            src = self.wrappers[name]["source"]
            out |= {i for (pack, n), i in self.by_name.items() if n == src}
            self.cache[key] = out
            return out
        for g in refs(path):
            out |= self.of_guid(g, depth)
        self.cache[key] = out
        return out


def method_for(path: Path, r: Resolver) -> tuple[str, str]:
    name, kind = path.stem, path.parent.name
    manifest = load(MANIFEST)
    if path.suffix.lower() == ".fbx":
        e = manifest.get(name, {})
        return e.get("class", "CREATE_DERIVED"), f"Blender recipe Tools/blender/env_derive.py::{name}: {e.get('method', '')}".strip()
    if kind == "Modules":
        if name in r.wrappers:
            return "ADAPTABLE", f"collider/material wrapper of {r.wrappers[name]['source']} (Env/Grammar/modules.json)"
        return manifest.get(name, {}).get("class", "CREATE_DERIVED"), f"module prefab of Meshes/{name}.fbx with collider policy (Env/Grammar/modules.json)"
    if kind == "Units":
        return "CREATE_DERIVED", "ENV library unit assembled by JuegoDef > ENV > 3 Build Library from Env/Specs/units.json"
    if kind == "Materials":
        return "ADAPTABLE", "palette/source material recipe in Env/Grammar/materials.json (JuegoDef > ENV > 1 Generate Materials)"
    if kind == "Textures":
        src = r.textures.get(name, {}).get("source", "?")
        return "ADAPTABLE", f"neutralised greyscale copy of vendor {src} (Env/Grammar/materials.json)"
    return "CREATE_DERIVED", "ENV factory output"


def cmd_lineage() -> int:
    r = Resolver()
    data = load(LINEAGE)
    keep = [a for a in data.get("assets", []) if not a.get("path", "").startswith("Assets/JuegoDef/Derived/ENV/")]
    records = []
    for f in sorted(DERIVED.rglob("*")):
        if not f.is_file() or f.name.endswith(".meta") or f.name.startswith("."):
            continue
        sources = sorted(r.of_file(f))
        cls, method = method_for(f, r)
        rec = {"id": f"env:{f.parent.name.lower()}:{f.stem}", "path": rel(f), "reuseClass": cls, "method": method}
        if sources:
            rec["sourceIds"] = sources
            if cls == "ORIGINAL":
                rec["reuseClass"] = "CREATE_DERIVED"  # new geometry, but carries kit materials/textures
        else:
            rec["origin"] = "ORIGINAL"
            rec["sourceIds"] = []
            rec["reuseClass"] = "ORIGINAL"
        records.append(rec)
    data["assets"] = keep + records
    LINEAGE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    counts: dict[str, int] = {}
    for rec in records:
        counts[rec["reuseClass"]] = counts.get(rec["reuseClass"], 0) + 1
    print(f"ENV_LINEAGE records={len(records)} classes={counts}")
    return 0


def modules() -> list[dict]:
    out = []
    for name, e in load(MANIFEST).items():
        out.append({"name": name, "class": e["class"], "donors": e["donors"], "doc": e["method"]})
    for w in load(GRAMMAR / "modules.json")["wrappers"]:
        out.append({"name": w["name"], "class": "ADAPTABLE", "donors": [w["source"]], "doc": "collider wrapper"})
    return out


def cmd_search(args) -> int:
    units = load(LIBRARY)["units"]
    q = (args.query or "").lower()
    hits = [u for u in units
            if (not args.demand or args.demand in u["demand"])
            and (not args.kind or u["kind"] == args.kind)
            and (not q or q in (u["id"] + " " + u["title"]).lower())]
    print(f"UNITS {len(hits)}")
    for u in hits:
        print(f"{u['id']} | {u['kind']} | {','.join(u['demand'])} | {u['prefab']}")
        print(f"    {u['title']} | size {u['size']} | preview {u['preview']}")
    return 0


def cmd_modules(args) -> int:
    q = (args.query or "").lower()
    ms = [m for m in modules() if not q or q in (m["name"] + " " + m["doc"]).lower()]
    print(f"MODULES {len(ms)} (plus every installed kit prefab by name, see PROD-ASSET-00 search)")
    for m in ms:
        print(f"{m['name']} | {m['class']} | donors={','.join(m['donors']) or '-'} | {m['doc'][:110]}")
    return 0


def cmd_check() -> int:
    problems = []
    lib = load(LIBRARY)["units"]
    spec_ids = [u["id"] for u in load(SPECS / "units.json")["units"]]
    if sorted(u["id"] for u in lib) != sorted(spec_ids):
        problems.append("env_library.json is stale versus units.json; run JuegoDef > ENV > 3 Build Library")
    for u in lib:
        for d in u["demand"]:
            if d not in DEMAND:
                problems.append(f"{u['id']}: unknown demand key {d}")
        if not (PROJECT / u["prefab"]).is_file():
            problems.append(f"{u['id']}: missing prefab {u['prefab']}")
        if not (REPO / u["preview"]).is_file():
            problems.append(f"{u['id']}: missing preview {u['preview']}")
    for d in DEMAND:
        if not any(d in u["demand"] for u in lib):
            problems.append(f"B0 demand row without a library unit: {d}")
    recorded = {a["path"] for a in load(LINEAGE).get("assets", [])}
    for f in DERIVED.rglob("*"):
        if f.is_file() and not f.name.endswith(".meta") and not f.name.startswith(".") and rel(f) not in recorded:
            problems.append(f"derived ENV file without lineage: {rel(f)}")
    manifest = load(MANIFEST)
    for name in manifest:
        if not (DERIVED / "Meshes" / f"{name}.fbx").is_file():
            problems.append(f"manifest entry without mesh: {name}")
    for fbx in (DERIVED / "Meshes").glob("*.fbx"):
        if fbx.stem not in manifest:
            problems.append(f"mesh without derive recipe: {fbx.name}")
    print(json.dumps({"units": len(lib), "demandRows": len(DEMAND), "problems": problems}, indent=2))
    return 1 if problems else 0


def cmd_inventory() -> int:
    """Writes Docs/evidence/WP-PROD-ENV-01/INVENTORY.md from the library index, derive manifest and lineage."""
    lin = {a["path"]: a for a in load(LINEAGE)["assets"]}
    lib = load(LIBRARY)["units"]
    lines = ["# WP-PROD-ENV-01 — factory output inventory", "",
             "Generated by `python Tools/env_catalog.py inventory` from `Docs/asset_catalog/env_library.json`, "
             "`env_derive_manifest.json` and `lineage.json`. Reuse classes follow the Visual Bible disposition order; "
             "`ORIGINAL` = juego-def-authored geometry/material with no vendor source.", "",
             f"## Production units ({len(lib)})", "",
             "| Unit | Kind | B0 demand rows | Size (m) | Modules (distinct / placed) | Reuse | Preview |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for u in lib:
        rec = lin.get(u["prefab"], {})
        mods = u["modules"]
        lines.append(f"| `{u['id']}` — {u['title']} | {u['kind']} | {', '.join(u['demand'])} | "
                     f"{' x '.join(str(x) for x in u['size'])} | {len(mods)} / {sum(mods.values())} | "
                     f"{rec.get('reuseClass', '?')} | [jpg](units/{Path(u['preview']).name}) |")
    manifest = load(MANIFEST)
    lines += ["", f"## Derived meshes / modules ({len(manifest)} Blender recipes)", "",
              "| Module | Class | Donor kit modules | Catalogue sources (lineage) | Method |", "| --- | --- | --- | --- | --- |"]
    for name, e in sorted(manifest.items()):
        rec = lin.get(f"Assets/JuegoDef/Derived/ENV/Meshes/{name}.fbx", {})
        lines.append(f"| `{name}` | {rec.get('reuseClass', e['class'])} | {', '.join(e['donors']) or '-'} | "
                     f"{', '.join(rec.get('sourceIds', [])) or 'ORIGINAL'} | {e['method'].splitlines()[0][:140]} |")
    wraps = load(GRAMMAR / "modules.json")["wrappers"]
    lines += ["", f"## Wrapped source props ({len(wraps)})", "",
              "Props/Nature models ship without collision and with machine-local materials; each wrapper adds a collider and owned `ENV_Src_*` materials.", "",
              "| Module | Source | Collider |", "| --- | --- | --- |"]
    for w in wraps:
        lines.append(f"| `{w['name']}` | {w['source']} | {w.get('collider', 'box')} |")
    counts: dict[str, int] = {}
    for a in lin.values():
        if a["path"].startswith("Assets/JuegoDef/Derived/ENV/"):
            counts[a["reuseClass"]] = counts.get(a["reuseClass"], 0) + 1
    lines += ["", "## Lineage totals", "", "| Reuse class | Derived ENV files |", "| --- | ---: |"]
    lines += [f"| {k} | {v} |" for k, v in sorted(counts.items())]
    out = REPO / "Docs" / "evidence" / "WP-PROD-ENV-01" / "INVENTORY.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"ENV_INVENTORY -> {out}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["search", "modules", "lineage", "check", "inventory"])
    p.add_argument("--demand", choices=sorted(DEMAND))
    p.add_argument("--kind")
    p.add_argument("--query")
    a = p.parse_args()
    if a.command == "search":
        return cmd_search(a)
    if a.command == "modules":
        return cmd_modules(a)
    if a.command == "lineage":
        return cmd_lineage()
    if a.command == "inventory":
        return cmd_inventory()
    return cmd_check()


if __name__ == "__main__":
    sys.exit(main())

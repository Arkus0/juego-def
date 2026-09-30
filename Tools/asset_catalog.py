"""B0-focused inventory and intake for the admitted Quaternius vault corpus.

Only metadata is committed. Source bytes stay in C:/Juego2-Assets or in ignored
Unity/Assets/ThirdParty/Quaternius copies. Python standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import uuid
import zipfile
from collections import Counter
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
PROJECT = REPO / "Unity" / "JuegoDef"
CATALOG = REPO / "Docs" / "evidence" / "WP-PROD-ASSET-00" / "catalog.json"
LINEAGE = REPO / "Docs" / "asset_catalog" / "lineage.json"
DERIVED = PROJECT / "Assets" / "JuegoDef" / "Derived"
VENDOR = "Assets/ThirdParty/Quaternius"
GUID_NAMESPACE = uuid.UUID("6e81ddc7-5c96-467a-b630-94431bcaf9af")

PACKS = {
    "medieval": {"root": "Medieval Village", "edition": "MegaKit Source / Unity URP", "license": "Medieval Village/License_Source.txt", "licenseKind": "CC0-1.0", "lanes": ["ENV", "PROP"]},
    "props": {"root": "Props (gratis)", "edition": "free", "license": "Props (gratis)/License_Standard.txt", "licenseKind": "CC0-1.0", "lanes": ["PROP", "ENV"]},
    "nature": {"root": "Nature", "edition": "standard", "license": "Nature/License_Standard.txt", "licenseKind": "CC0-1.0", "lanes": ["ENV", "PROP"]},
    "base": {"root": "Base Characters", "edition": "Source", "license": "Base Characters/License_Source.txt", "licenseKind": "CC0-1.0", "lanes": ["CHAR"]},
    "outfits": {"root": "Modular Character Outfits - Fantasy[Standard]", "edition": "Fantasy Standard/free subset", "license": "Modular Character Outfits - Fantasy[Standard]/License_Standard.txt", "licenseKind": "CC0-1.0", "lanes": ["CHAR"]},
    "ual1": {"root": "Animation", "edition": "UAL1", "license": "Animation/License.txt", "licenseKind": "CC0-1.0", "lanes": ["ANIM"]},
    "ual2": {"root": "Animation2", "edition": "UAL2", "license": "Animation2/License.txt", "licenseKind": "CC0-1.0", "lanes": ["ANIM"]},
}
PREVIEWS = {
    "medieval": "Medieval Village/Preview.jpg", "props": "Props (gratis)/Preview_1.jpg",
    "nature": "Nature/Preview_1.jpg", "base": "Base Characters/Preview.png",
    "outfits": "Modular Character Outfits - Fantasy[Standard]/Preview.jpg",
}
TARGETS = {
    "medieval": "MedievalVillage", "props": "Props", "nature": "Nature",
    "base": "BaseCharacters", "outfits": "Outfits", "ual1": "UAL1", "ual2": "UAL2",
}
INSTALL_GLOBS = {
    "props": ["Exports/FBX/*.fbx", "**/Textures/**/*"],
    "nature": ["FBX/*.fbx", "**/Textures/**/*"],
    "base": [
        "Base Characters/Exports/Unity/*.fbx",
        "Base Characters/Textures/**/*",
        "Hairstyles/Origin at 0/FBX (Unity)/*.fbx",
        "Hairstyles/**/Textures/**/*",
    ],
    "outfits": ["Exports/FBX (Unity)/**/*.fbx", "Textures/**/*"],
    "ual1": ["Unity/UAL1.fbx"],
    "ual2": ["Unity/UAL2.fbx"],
}

MEDIEVAL_ZIP = "Medieval Village/Engine Projects/Medieval Village MegaKit[Unity URP].zip"
MEDIEVAL_SHA256 = "b9d757dd2608a5cee4d9ee1e8183f6cb4cad9d27480841a905180def9c7d8b10"
MEDIEVAL_PREFIX = "Medieval Village MegaKit[Unity URP]/Quaternius/Assets/Quaternius/Medieval Village MegaKit/"
CLIP_RE = re.compile(rb"Armature\|([A-Za-z0-9_]+)\x00\x01AnimStack")
GUID_RE = re.compile(rb"(?m)^guid: ([0-9a-f]{32})\r?$")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def guid_for(path: str) -> str:
    return uuid.uuid5(GUID_NAMESPACE, path).hex


def meta_guid(data: bytes) -> str | None:
    match = GUID_RE.search(data)
    return match.group(1).decode("ascii") if match else None


def source_files_for_pack(vault: Path, pack: str) -> list[Path]:
    """Return exactly the non-Medieval source files copied by install, deterministically."""
    if pack == "medieval":
        raise ValueError("medieval intake identity is the pinned source archive")
    root = vault / PACKS[pack]["root"]
    seen: set[Path] = set()
    files: list[Path] = []
    for pattern in INSTALL_GLOBS[pack]:
        for source in sorted(root.glob(pattern)):
            if not source.is_file() or source in seen:
                continue
            seen.add(source)
            files.append(source)
    files.sort(key=lambda path: rel(path, root))
    return files


def manifest_from_rows(rows: list[tuple[str, str]]) -> str:
    """Hash path+content-hash rows so path, additions, removals and byte changes alter identity."""
    h = hashlib.sha256()
    for path, sha in sorted(rows):
        h.update(path.encode("utf-8"))
        h.update(b"\0")
        h.update(sha.encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def intake_identity(vault: Path, pack: str) -> dict:
    """Identity of every source byte install may copy for one pack."""
    if pack == "medieval":
        archive = vault / MEDIEVAL_ZIP
        if not archive.is_file():
            raise ValueError(f"Missing Medieval Village source archive: {archive}")
        archive_sha = digest(archive)
        if archive_sha != MEDIEVAL_SHA256:
            raise ValueError("Medieval Village source archive absent or hash mismatch")
        return {"kind": "archive-sha256", "sha256": archive_sha, "files": 1}

    root = vault / PACKS[pack]["root"]
    rows = [(rel(path, root), digest(path)) for path in source_files_for_pack(vault, pack)]
    if not rows:
        raise ValueError(f"No intake source files found for pack: {pack}")
    return {
        "kind": "path+content-sha256-v1",
        "sha256": manifest_from_rows(rows),
        "files": len(rows),
    }


def import_relative(pack: str, source: Path, root: Path) -> Path:
    if pack.startswith("ual"):
        return Path(source.name)
    return source.relative_to(root)


def expected_identity(catalog: dict, pack: str) -> dict:
    info = catalog.get("sourcePacks", {}).get(pack, {})
    identity = info.get("intakeIdentity")
    if not isinstance(identity, dict) or not identity.get("sha256") or not identity.get("files"):
        raise ValueError(
            f"Catalog has no complete intake identity for {pack}; run build against the admitted vault before install"
        )
    return identity


def assert_catalog_identity(vault: Path, pack: str, catalog: dict) -> dict:
    expected = expected_identity(catalog, pack)
    actual = intake_identity(vault, pack)
    if actual != expected:
        raise ValueError(
            f"Source intake identity changed for {pack}; run build, review the new snapshot, then retry install "
            f"(catalog={expected.get('sha256')} current={actual.get('sha256')})"
        )
    return actual


def classify(name: str, pack: str) -> tuple[str, list[str], list[str], list[str]]:
    low = name.lower()
    tags: set[str] = set()
    roles: set[str] = set()
    notes: list[str] = []
    reuse = "ADAPTABLE"
    if pack in {"medieval", "props", "nature"}:
        mapping = {
            "door": ("door", "commercial_frontage"),
            "window": ("window", "commercial_frontage"),
            "wall": ("wall", "commercial_frontage"),
            "corner": ("corner", "commercial_frontage"),
            "stair": ("stairs", "upper_port_loop"),
            "rail": ("railing", "upper_port_loop"),
            "fence": ("railing", "upper_port_loop"),
            "balcony": ("balcony", "commercial_frontage"),
            "floor": ("floor", "commercial_frontage"),
            "roof": ("roof", "commercial_frontage"),
            "overhang": ("awning", "commercial_frontage"),
            "arch": ("arch", "commercial_frontage"),
            "crate": ("crate", "market_port_props"),
            "barrel": ("barrel", "market_port_props"),
            "basket": ("basket", "market_port_props"),
            "bag": ("bag", "market_port_props"),
            "bench": ("bench", "street_props"),
            "table": ("table", "market_port_props"),
            "sign": ("sign_mount", "commercial_frontage"),
            "fish": ("fish", "market_port_props"),
            "rock": ("stone", "upper_port_loop"),
        }
        for token, (tag, role) in mapping.items():
            if token in low:
                tags.add(tag)
                roles.add(role)
        if "plaster" in low or "brick" in low:
            tags.add("masonry")
        if "wood" in low or "wagon" in low or "spike" in low:
            notes.append("Visual review: medieval/wood/fantasy cue may need adaptation or rejection.")
        if pack == "props" and not notes:
            reuse = "DIRECT"
        if pack == "nature":
            reuse = "DIRECT"
        if not roles:
            roles.add("supporting_environment" if pack != "props" else "supporting_prop")
    elif pack == "base":
        tags.update(["humanoid", "shared_rig"])
        roles.add("civilian_base")
        if "regular" in low:
            tags.add("adult")
            reuse = "ADAPTABLE"
        elif "teen" in low:
            tags.add("young")
            reuse = "ADAPTABLE"
        else:
            notes.append("Superhero proportions need visual review before civilian use.")
        if "female" in low:
            tags.add("female")
        elif "male" in low:
            tags.add("male")
        if "hair" in low or "brow" in low:
            roles.add("civilian_hair")
            reuse = "DIRECT"
    elif pack == "outfits":
        tags.update(["wardrobe", "shared_rig_candidate"])
        roles.add("civilian_wardrobe")
        reuse = "DONOR"
        if "peasant" in low:
            tags.update(["market", "shop", "resident"])
        if "ranger" in low:
            tags.update(["dock", "port", "workwear_candidate"])
            notes.append("Strip fantasy cues; role fit and rig/clipping require CHAR validation.")
        if "body" in low or "arms" in low or "legs" in low or "feet" in low:
            tags.add("modular_part")
    else:
        tags.add("humanoid_animation")
        if low.endswith("loop"):
            tags.add("loop")
        if any(x in low for x in ("walk", "jog", "sprint", "turn", "idle")):
            roles.add("locomotion_ambient")
        if any(x in low for x in ("talk", "counter", "yes", "no", "show", "surprise", "cry", "celebration")):
            roles.add("conversation_reaction")
        if any(x in low for x in ("carry", "pickup", "fish", "farm", "fixing", "drink", "interact", "mining", "chopping")):
            roles.add("market_port_work")
        if any(x in low for x in ("sitting", "sit", "look", "rail", "lean", "wait")):
            roles.add("ambient_social")
        if not roles:
            roles.add("other_animation")
        reuse = "DIRECT" if "other_animation" not in roles else "DONOR"
        if any(x in low for x in ("spell", "sword", "bow_", "zombie", "shield", "monster", "ninja")):
            reuse = "REJECT"
            notes.append("Out of B0 ordinary civilian scope.")
    return reuse, sorted(tags), sorted(roles), notes


def entry(pack: str, name: str, source: str, import_path: str, sha: str, *, guid: str | None = None,
          archive_entry: str | None = None, source_mesh: str | None = None) -> dict:
    reuse, tags, roles, notes = classify(name, pack)
    item = {
        "id": f"{pack}:{name.lower()}", "name": name, "pack": pack,
        "type": "animation" if pack.startswith("ual") else ("character" if pack in {"base", "outfits"} else "environment" if pack in {"medieval", "nature"} else "prop"),
        "lanes": PACKS[pack]["lanes"], "tags": tags, "b0Roles": roles, "reuse": reuse,
        "admission": "candidate", "sourcePath": source, "sourceSha256": sha,
        "licensePath": PACKS[pack]["license"], "importPath": import_path,
        "importNotes": [], "incompatibilities": notes, "derivedIds": [],
    }
    if pack in PREVIEWS:
        item["packPreviewPath"] = PREVIEWS[pack]
    if pack == "medieval":
        item["importNotes"] = ["Unity URP source-project prefab; preserve vendor GUID and review materials at use."]
    elif pack in {"base", "outfits"}:
        item["importNotes"] = ["Unity FBX export; CHAR lane must verify rig, clothing fit and materials."]
    elif pack in {"props", "nature"}:
        item["importNotes"] = ["FBX export with separate textures; inspect material assignment in Unity."]
    if guid:
        item["unityGuid"] = guid
    if archive_entry:
        item["archiveEntry"] = archive_entry
    if source_mesh:
        item["sourceMesh"] = source_mesh
    return item


def build(vault: Path) -> dict:
    for pack, info in PACKS.items():
        license_path = vault / info["license"]
        if not license_path.is_file() or "CC0" not in license_path.read_text(encoding="utf-8", errors="replace"):
            raise ValueError(f"Missing or unverified CC0 license: {license_path}")
    archive = vault / MEDIEVAL_ZIP
    if not archive.is_file() or digest(archive) != MEDIEVAL_SHA256:
        raise ValueError("Medieval Village source archive absent or hash mismatch")

    source_packs = {}
    for pack, info in PACKS.items():
        source_packs[pack] = {
            **info,
            "provider": "Quaternius",
            "version": "content-addressed source snapshot",
            "intakeIdentity": intake_identity(vault, pack),
        }

    items: list[dict] = []
    with zipfile.ZipFile(archive) as z:
        names = set(z.namelist())
        for path in sorted(names):
            if not path.startswith(MEDIEVAL_PREFIX + "Modules/Prefabs/") or not path.endswith(".prefab"):
                continue
            name = Path(path).stem
            vendor_rel = path[len(MEDIEVAL_PREFIX):]
            guid = meta_guid(z.read(path + ".meta")) if path + ".meta" in names else None
            mesh_rel = f"Modules/Source Models/{name}.fbx"
            source_mesh = mesh_rel if MEDIEVAL_PREFIX + mesh_rel in names else None
            items.append(entry("medieval", name, MEDIEVAL_ZIP,
                               f"{VENDOR}/MedievalVillage/{vendor_rel}",
                               hashlib.sha256(z.read(path)).hexdigest(), guid=guid,
                               archive_entry=vendor_rel, source_mesh=source_mesh))
    patterns = {
        "props": ["Exports/FBX/*.fbx"],
        "nature": ["FBX/*.fbx"],
        "base": ["Base Characters/Exports/Unity/*.fbx", "Hairstyles/Origin at 0/FBX (Unity)/*.fbx"],
        "outfits": ["Exports/FBX (Unity)/**/*.fbx"],
    }
    targets = {"props": "Props", "nature": "Nature", "base": "BaseCharacters", "outfits": "Outfits"}
    for pack, globs in patterns.items():
        root = vault / PACKS[pack]["root"]
        for pattern in globs:
            for path in sorted(root.glob(pattern)):
                source = rel(path, vault)
                unity = f"{VENDOR}/{targets[pack]}/{rel(path, root)}"
                items.append(entry(pack, path.stem, source, unity, digest(path), guid=guid_for(unity)))
    for pack, model in (("ual1", "Animation/Unity/UAL1.fbx"), ("ual2", "Animation2/Unity/UAL2.fbx")):
        path = vault / model
        data = path.read_bytes()
        source_hash = hashlib.sha256(data).hexdigest()
        clips = sorted(set(x.decode("ascii") for x in CLIP_RE.findall(data)))
        if len(clips) < 50:
            raise ValueError(f"FBX animation stack extraction failed: {model}")
        unity = f"{VENDOR}/{pack.upper()}/{Path(model).name}"
        for clip in clips:
            item = entry(pack, clip, model, unity, source_hash, guid=guid_for(unity))
            item["clipName"] = clip
            item["importNotes"] = ["Humanoid retarget, axis conversion and loop settings require ANIM lane validation."]
            items.append(item)
    ids = [item["id"] for item in items]
    if len(ids) != len(set(ids)):
        duplicates = [k for k, n in Counter(ids).items() if n > 1]
        raise ValueError(f"Duplicate IDs: {duplicates[:10]}")
    if LINEAGE.is_file():
        by_id = {item["id"]: item for item in items}
        for derived in json.loads(LINEAGE.read_text(encoding="utf-8")).get("assets", []):
            for source_id in derived.get("sourceIds", []):
                if source_id in by_id:
                    by_id[source_id]["derivedIds"].append(derived["id"])
    items.sort(key=lambda x: x["id"])
    return {
        "schemaVersion": 2,
        "vault": "C:/Juego2-Assets (override with --vault)",
        "sourcePacks": source_packs,
        "sourceArchiveSha256": MEDIEVAL_SHA256,
        "items": items,
    }


def write_catalog(vault: Path, output: Path) -> dict:
    catalog = build(vault)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "{",
        f'  "schemaVersion": {catalog["schemaVersion"]},',
        f'  "vault": {json.dumps(catalog["vault"], ensure_ascii=False)},',
        f'  "sourceArchiveSha256": {json.dumps(catalog["sourceArchiveSha256"])},',
        '  "sourcePacks": {',
    ]
    pack_rows = sorted(catalog["sourcePacks"].items())
    for index, (pack, info) in enumerate(pack_rows):
        comma = "," if index < len(pack_rows) - 1 else ""
        lines.append(f'    {json.dumps(pack)}: {json.dumps(info, ensure_ascii=False, sort_keys=True)}{comma}')
    lines.extend(["  },", '  "items": ['])
    for index, item in enumerate(catalog["items"]):
        comma = "," if index < len(catalog["items"]) - 1 else ""
        lines.append(f'    {json.dumps(item, ensure_ascii=False, sort_keys=True)}{comma}')
    lines.extend(["  ]", "}"])
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return catalog


def selected(item: dict, args: argparse.Namespace) -> bool:
    if item["reuse"] == "REJECT" and not args.include_rejected:
        return False
    if args.pack and item["pack"] != args.pack:
        return False
    if args.lane and args.lane not in item["lanes"]:
        return False
    if args.role and args.role not in item["b0Roles"]:
        return False
    if args.tag and args.tag not in item["tags"]:
        return False
    words = re.findall(r"[a-z0-9]+", (args.query or "").lower())
    haystack = " ".join((item["name"], item["type"], item["pack"], *item["tags"], *item["b0Roles"])).lower()
    return all(word in haystack for word in words)


def write_meta(path: Path, unity_path: str) -> None:
    path.with_name(path.name + ".meta").write_text(
        f"fileFormatVersion: 2\nguid: {guid_for(unity_path)}\n", encoding="utf-8")


def install(vault: Path, pack: str) -> int:
    target = PROJECT / VENDOR / TARGETS[pack]
    license_path = vault / PACKS[pack]["license"]
    if not license_path.is_file() or "CC0" not in license_path.read_text(encoding="utf-8", errors="replace"):
        raise ValueError(f"Missing or unverified CC0 license: {license_path}")
    if not CATALOG.is_file():
        raise ValueError(f"Missing committed catalog: {CATALOG}")
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    identity = assert_catalog_identity(vault, pack, catalog)

    receipt_path = target / ".juego-def-intake.json"
    if target.exists() and (not receipt_path.is_file() or json.loads(receipt_path.read_text(encoding="utf-8")).get("pack") != pack):
        raise ValueError(f"Existing folder has no matching intake receipt: {target}")
    target.mkdir(parents=True, exist_ok=True)
    count = 0
    added = 0
    local_upgrades = 0
    if pack == "medieval":
        with zipfile.ZipFile(vault / MEDIEVAL_ZIP) as z:
            for name in z.namelist():
                if not name.startswith(MEDIEVAL_PREFIX) or name.endswith("/"):
                    continue
                relative = name[len(MEDIEVAL_PREFIX):]
                out = target / relative
                out.parent.mkdir(parents=True, exist_ok=True)
                content = z.read(name)
                if out.exists():
                    if out.read_bytes() != content:
                        if out.suffix.lower() == ".mat":
                            local_upgrades += 1
                        else:
                            raise ValueError(f"Existing vendor file differs; refusing overwrite: {out}")
                else:
                    out.write_bytes(content)
                    added += 1
                count += 1
    else:
        root = vault / PACKS[pack]["root"]
        for source in source_files_for_pack(vault, pack):
            relative = import_relative(pack, source, root)
            out = target / relative
            out.parent.mkdir(parents=True, exist_ok=True)
            if out.exists():
                if digest(out) != digest(source):
                    raise ValueError(f"Existing vendor file differs; refusing overwrite: {out}")
            else:
                shutil.copy2(source, out)
                added += 1
            if not out.with_name(out.name + ".meta").exists():
                write_meta(out, f"{VENDOR}/{target.name}/{relative.as_posix()}")
            count += 1
    receipt = {
        "pack": pack,
        "files": count,
        "vaultRoot": PACKS[pack]["root"],
        "license": PACKS[pack]["license"],
        "intakeIdentity": identity,
        "localUnityMaterialUpgrades": local_upgrades,
    }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(
        f"INSTALLED {pack}: {count} source files ({added} new, {local_upgrades} local material upgrades preserved) "
        f"identity={identity['sha256']} -> {target}"
    )
    return count


def validate(vault: Path, catalog: dict) -> list[str]:
    problems: list[str] = []
    try:
        rebuilt = build(vault)
        if rebuilt != catalog:
            problems.append("catalog snapshot is stale; run build")
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        problems.append(f"cannot reconstruct source snapshot: {exc}")

    ids: set[str] = set()
    source_hashes: dict[str, str] = {}
    installed = {
        pack for pack in PACKS
        if (PROJECT / VENDOR / TARGETS[pack] / ".juego-def-intake.json").is_file()
    }
    for pack in PACKS:
        try:
            expected_identity(catalog, pack)
        except ValueError as exc:
            problems.append(str(exc))

    for item in catalog["items"]:
        if item["id"] in ids:
            problems.append(f"duplicate id: {item['id']}")
        ids.add(item["id"])
        source = vault / item["sourcePath"]
        if not source.is_file():
            problems.append(f"missing source: {item['id']}")
        elif item["pack"] != "medieval":
            key = item["sourcePath"]
            if key not in source_hashes:
                source_hashes[key] = digest(source)
            if source_hashes[key] != item["sourceSha256"]:
                problems.append(f"source changed: {item['id']}")
        if not (vault / item["licensePath"]).is_file():
            problems.append(f"missing license: {item['id']}")
        if item["pack"] == "medieval" and not item.get("unityGuid"):
            problems.append(f"missing native GUID: {item['id']}")
        if item["pack"] in installed:
            imported = PROJECT / item["importPath"]
            if not imported.is_file():
                problems.append(f"missing installed asset: {item['id']}")
            else:
                meta = imported.with_name(imported.name + ".meta")
                if not meta.is_file() or meta_guid(meta.read_bytes()) != item.get("unityGuid"):
                    problems.append(f"missing/changed Unity GUID: {item['id']}")

    if (vault / MEDIEVAL_ZIP).is_file() and digest(vault / MEDIEVAL_ZIP) != catalog.get("sourceArchiveSha256"):
        problems.append("Medieval Village archive identity changed")

    for pack in installed:
        target = PROJECT / VENDOR / TARGETS[pack]
        receipt_path = target / ".juego-def-intake.json"
        try:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            expected = expected_identity(catalog, pack)
            actual_source = intake_identity(vault, pack)
            if receipt.get("intakeIdentity") != expected:
                problems.append(f"stale intake receipt identity: {pack}")
            if actual_source != expected:
                problems.append(f"source intake identity changed: {pack}")
            if receipt.get("files") != expected.get("files") and pack != "medieval":
                problems.append(f"intake receipt file count differs from source manifest: {pack}")
            if pack != "medieval":
                root = vault / PACKS[pack]["root"]
                for source in source_files_for_pack(vault, pack):
                    relative = import_relative(pack, source, root)
                    imported = target / relative
                    if not imported.is_file():
                        problems.append(f"missing installed source byte: {pack}:{relative.as_posix()}")
                    elif digest(imported) != digest(source):
                        problems.append(f"installed source byte differs: {pack}:{relative.as_posix()}")
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            problems.append(f"invalid intake receipt for {pack}: {exc}")

    if LINEAGE.is_file():
        data = json.loads(LINEAGE.read_text(encoding="utf-8"))
        recorded: set[str] = set()
        for derived in data.get("assets", []):
            path = derived.get("path", "")
            if not derived.get("id"):
                problems.append(f"missing derived id: {path}")
            if not path.startswith("Assets/JuegoDef/Derived/") or not (PROJECT / path).is_file():
                problems.append(f"missing/invalid derived output: {path}")
            if derived.get("origin") == "ORIGINAL":
                # juego-def-authored geometry/material with no vendor source: allowed, but it must say how it
                # was made and may not also claim sources.
                if not derived.get("method") or derived.get("sourceIds"):
                    problems.append(f"invalid ORIGINAL lineage: {path}")
            elif not derived.get("sourceIds") or any(x not in ids for x in derived["sourceIds"]):
                problems.append(f"broken lineage: {path}")
            recorded.add(path)
        for file in DERIVED.rglob("*") if DERIVED.exists() else []:
            if file.is_file() and not file.name.endswith(".meta") and not file.name.startswith("."):
                unity_path = rel(file, PROJECT)
                if unity_path not in recorded:
                    problems.append(f"derived file without lineage: {unity_path}")
    else:
        problems.append("missing lineage registry")
    return problems


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["build", "search", "inspect", "validate", "install"])
    p.add_argument("--vault", type=Path, default=Path("C:/Juego2-Assets"))
    p.add_argument("--output", type=Path, default=CATALOG)
    p.add_argument("--pack", choices=PACKS)
    p.add_argument("--lane", choices=["ENV", "CHAR", "ANIM", "PROP", "UI"])
    p.add_argument("--role")
    p.add_argument("--tag")
    p.add_argument("--query")
    p.add_argument("--id")
    p.add_argument("--include-rejected", action="store_true")
    p.add_argument("--limit", type=int, default=20)
    args = p.parse_args()
    try:
        if args.command == "build":
            catalog = write_catalog(args.vault, args.output)
            print(f"BUILT {len(catalog['items'])} candidates -> {args.output}")
        elif args.command == "install":
            if not args.pack:
                p.error("install requires --pack")
            install(args.vault, args.pack)
        else:
            catalog = json.loads(args.output.read_text(encoding="utf-8"))
            if args.command == "validate":
                problems = validate(args.vault, catalog)
                print(json.dumps({"items": len(catalog["items"]), "problems": problems}, indent=2))
                return 1 if problems else 0
            if args.command == "inspect":
                if not args.id:
                    p.error("inspect requires --id")
                item = next((item for item in catalog["items"] if item["id"] == args.id), None)
                if item is None:
                    raise ValueError(f"Unknown asset ID: {args.id}")
                print(json.dumps(item, ensure_ascii=False, indent=2))
                return 0
            hits = [item for item in catalog["items"] if selected(item, args)]
            print(f"MATCHES {len(hits)}; showing {min(len(hits), args.limit)}")
            for item in hits[:args.limit]:
                print(f"{item['id']} | {item['reuse']} | {','.join(item['b0Roles'])} | {item['importPath']}")
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print(f"ASSET_CATALOG_ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

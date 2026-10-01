"""Bounded ENV01 freeze: copy the inspected scene and its existing generated assets.

Does not invoke the district builder or interpret a layout. Importer settings and
subasset IDs are preserved; new GUIDs isolate authored assets from legacy rebuilds.
"""
from pathlib import Path
import hashlib
import json
import re
import uuid

REPO = Path(__file__).resolve().parents[1]
PROJECT = REPO / "Unity/JuegoDef"
EVIDENCE = REPO / "Docs/evidence/WP-ENV01-AUTHORED-01"
SOURCE = "Assets/JuegoDef/Scenes/ENV/ENV01_Casco_District.unity"
TARGET = "Assets/JuegoDef/Scenes/ENV/ENV01_AUTHORED.unity"
REFERENCE = "Assets/JuegoDef/Scenes/ENV/ENV01_REFERENCE.unity"
PREFIX = "Assets/JuegoDef/Derived/ENV/"
SNAPSHOT = "Assets/JuegoDef/Authored/ENV01/"
GUID = re.compile(rb"\bguid: ([0-9a-f]{32})\b")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(path):
    data = path.read_bytes()
    if data.startswith(b"%YAML") or path.suffix == ".meta":
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def main():
    if (PROJECT / TARGET).exists():
        raise SystemExit("Authored scene already exists; refusing to overwrite manual work")
    deps = json.loads((EVIDENCE / "SOURCE_DEPENDENCIES.json").read_text())
    files = {p: SNAPSHOT + p[len(PREFIX):] for p in deps if p.startswith(PREFIX)}
    files[SOURCE] = TARGET
    remap = {}
    for src, dst in files.items():
        meta = (PROJECT / (src + ".meta")).read_bytes()
        old = GUID.search(meta).group(1)
        new = uuid.uuid5(uuid.NAMESPACE_URL, "juego-def:env01-authored:" + dst).hex.encode()
        remap[old] = new
    records = []
    for src, dst in sorted(files.items()):
        original = PROJECT / src
        dest = PROJECT / dst
        if dest.exists():
            raise SystemExit(f"Refusing existing snapshot asset: {dest}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = original.read_bytes()
        # Only serialized Unity text is rewritten; mesh/image binary data stays exact.
        if data.startswith(b"%YAML"):
            data = GUID.sub(lambda m: b"guid: " + remap.get(m.group(1), m.group(1)), data)
        dest.write_bytes(data)
        meta = (PROJECT / (src + ".meta")).read_bytes()
        (PROJECT / (dst + ".meta")).write_bytes(
            GUID.sub(lambda m: b"guid: " + remap.get(m.group(1), m.group(1)), meta))
        records.append({"source": src, "authored": dst, "source_sha256": sha(original),
                        "authored_sha256": sha(dest), "source_meta_sha256": sha(PROJECT / (src + ".meta")),
                        "authored_meta_sha256": sha(PROJECT / (dst + ".meta")),
                        "authored_canonical_sha256": canonical_sha(dest),
                        "authored_meta_canonical_sha256": canonical_sha(PROJECT / (dst + ".meta"))})
    # Reviewable pre-migration hierarchy; same frozen geometry assets, no regeneration.
    reference = PROJECT / REFERENCE
    if reference.exists():
        raise SystemExit("Reference already exists; refusing to overwrite it")
    reference.write_bytes((PROJECT / TARGET).read_bytes())
    reference_guid = uuid.uuid5(uuid.NAMESPACE_URL, "juego-def:env01-authored:" + REFERENCE).hex.encode()
    reference_meta = (PROJECT / (TARGET + ".meta")).read_bytes()
    authored_scene_guid = GUID.search(reference_meta).group(1)
    reference_meta = GUID.sub(lambda m: b"guid: " + reference_guid if m.group(1) == authored_scene_guid else m.group(0), reference_meta)
    (PROJECT / (REFERENCE + ".meta")).write_bytes(reference_meta)
    (EVIDENCE / "ASSET_SNAPSHOT.json").write_text(json.dumps(records, indent=2) + "\n")
    print(f"Copied {len(files)-1} generated assets + scene. Original unchanged.")


if __name__ == "__main__":
    main()

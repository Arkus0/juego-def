"""Restore the owner-licensed Game Creator 2 Core into the juego-def Unity project.

GC2 Core is an Asset Store package (per-seat EULA, not redistributable) and juego-def is a public repository, so its
bytes are never committed. This script copies it from the owner's local Asset Store download:

  python Tools/gc2-provision.py install [--package <Game Creator 2.unitypackage>]
  python Tools/gc2-provision.py status
  python Tools/gc2-provision.py remove

`install` refuses any package whose SHA-256/size differ from the admitted Core 2.19.61, extracts `Assets/**` only (the
vendor `Packages/manifest.json` is the author's own project manifest and is never applied; juego-def pins its packages
in its committed manifest) and writes a receipt. Nested example/installer `.unitypackage` files are copied as inert
files and are not installed.

Ported from Juego2 `scripts/h2f02-provision.py` (same admitted package), without the H2F define/lint machinery.
"""

import argparse
import hashlib
import json
import os
import shutil
import tarfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROJECT = REPO / "Unity" / "JuegoDef"
DEFAULT_PACKAGE = Path(os.environ.get("APPDATA", "")) / "Unity/Asset Store-5.x/Catsoft Works/Editor ExtensionsGame Toolkits/Game Creator 2.unitypackage"
GC2_SHA256 = "1e4f3ba0560eadb944b3cf3ca63f7095d95b47c55a94ee655f28a15952f3380b"
GC2_BYTES = 28236878
GC2_VERSION = "2.19.61"
GC2_ROOT = "Assets/Plugins/GameCreator"
RECEIPT = GC2_ROOT + "/.juego-def-provisioning.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_assets_only(package: Path) -> tuple[int, list[str]]:
    imported, excluded = 0, []
    with tarfile.open(package, "r:gz") as tar:
        members = {m.name: m for m in tar.getmembers()}
        for name, member in sorted(members.items()):
            if not name.endswith("/pathname"):
                continue
            guid = name.split("/")[0]
            path = tar.extractfile(member).read().decode("utf-8").splitlines()[0].strip()
            if not path.startswith(GC2_ROOT + "/") and path != GC2_ROOT:
                if path.startswith("Assets/"):
                    raise SystemExit(f"GC2_UNEXPECTED_PATH {path}")
                excluded.append(path)
                continue
            target = PROJECT / path
            asset, meta = members.get(f"{guid}/asset"), members.get(f"{guid}/asset.meta")
            if asset is not None:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(tar.extractfile(asset).read())
            else:
                target.mkdir(parents=True, exist_ok=True)
            if meta is not None:
                Path(str(target) + ".meta").write_bytes(tar.extractfile(meta).read())
            imported += 1
    return imported, excluded


def install(package: Path) -> None:
    if not package.is_file():
        raise SystemExit(f"GC2_PACKAGE_MISSING {package} (download Game Creator 2 from the Asset Store with the owner seat)")
    size, digest = package.stat().st_size, sha256(package)
    if (digest, size) != (GC2_SHA256, GC2_BYTES):
        raise SystemExit(f"GC2_PACKAGE_REFUSED sha256={digest} bytes={size} (expected Core {GC2_VERSION})")
    manifest = PROJECT / "Packages/manifest.json"
    before = sha256(manifest)
    imported, excluded = extract_assets_only(package)
    version = (PROJECT / GC2_ROOT / "Packages/Core/Editor/Version.txt").read_text(encoding="utf-8").strip()
    if version != GC2_VERSION:
        raise SystemExit(f"GC2_VERSION_MISMATCH {version}")
    if sha256(manifest) != before:
        raise SystemExit("GC2_MANIFEST_CHANGED")
    receipt = {"product": "Game Creator 2 Core", "version": version, "packageSha256": digest, "packageBytes": size,
               "route": "assets-only", "imported": imported, "excluded": excluded}
    (PROJECT / RECEIPT).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"GC2_INSTALLED version={version} imported={imported} excluded={excluded}")


def status() -> int:
    receipt = PROJECT / RECEIPT
    if not (PROJECT / GC2_ROOT).exists():
        print("GC2_ABSENT")
        return 3
    data = json.loads(receipt.read_text(encoding="utf-8")) if receipt.exists() else {}
    ok = data.get("packageSha256") == GC2_SHA256 and data.get("version") == GC2_VERSION
    print(f"GC2_{'INSTALLED' if ok else 'INVALID'} version={data.get('version')} sha256={data.get('packageSha256')}")
    return 0 if ok else 3


def remove() -> None:
    for p in [PROJECT / GC2_ROOT, PROJECT / (GC2_ROOT + ".meta")]:
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()
    print("GC2_REMOVED")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=["install", "status", "remove"])
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    args = parser.parse_args()
    if args.mode == "install":
        install(args.package)
        return 0
    if args.mode == "remove":
        remove()
        return 0
    return status()


if __name__ == "__main__":
    raise SystemExit(main())

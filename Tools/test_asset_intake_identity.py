"""Regression probe for WP-PROD-ASSET-00 intake source identity.

This uses a synthetic Props vault so it can run remotely without C:/Juego2-Assets.
It specifically guards the reviewer falsifier: changing a copied texture at the
same path must change the pack identity even though textures are not semantic
catalogue candidates.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import asset_catalog


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        vault = Path(tmp)
        root = vault / asset_catalog.PACKS["props"]["root"]
        fbx = root / "Exports" / "FBX" / "Bag.fbx"
        texture = root / "Textures" / "Bag.png"
        fbx.parent.mkdir(parents=True)
        texture.parent.mkdir(parents=True)
        fbx.write_bytes(b"fake-fbx-v1")
        texture.write_bytes(b"texture-v1")

        first = asset_catalog.intake_identity(vault, "props")
        second = asset_catalog.intake_identity(vault, "props")
        assert first == second, "unchanged source must have stable identity"
        assert first["files"] == 2, first

        texture.write_bytes(b"texture-v2")
        changed = asset_catalog.intake_identity(vault, "props")
        assert changed["files"] == 2, changed
        assert changed["sha256"] != first["sha256"], (
            "changing a copied texture at the same path must change intake identity"
        )

        extra = root / "Textures" / "Bag_Normal.png"
        extra.write_bytes(b"normal-v1")
        expanded = asset_catalog.intake_identity(vault, "props")
        assert expanded["files"] == 3, expanded
        assert expanded["sha256"] != changed["sha256"], (
            "adding another copied source file must change intake identity"
        )

    print("PASS: intake identity changes on texture mutation/addition and is stable otherwise")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

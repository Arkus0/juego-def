"""Bounded local completion for WP-PROD-ASSET-00 after the remote repair.

Runs the vault-independent regression probe, rebuilds the content-addressed
catalogue, refreshes receipts for all covered packs, validates the result and
writes VALIDATION.json. It does not commit, push, open Unity or modify the vault.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import asset_catalog
import test_asset_intake_identity


VALIDATION = (
    asset_catalog.REPO
    / "Docs"
    / "evidence"
    / "WP-PROD-ASSET-00"
    / "VALIDATION.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", type=Path, default=Path("C:/Juego2-Assets"))
    args = parser.parse_args()

    if test_asset_intake_identity.main() != 0:
        return 1

    catalog = asset_catalog.write_catalog(args.vault, asset_catalog.CATALOG)
    for pack in asset_catalog.PACKS:
        asset_catalog.install(args.vault, pack)

    problems = asset_catalog.validate(args.vault, catalog)
    report = {
        "schemaVersion": catalog["schemaVersion"],
        "items": len(catalog["items"]),
        "packIntakeIdentities": {
            pack: info["intakeIdentity"]
            for pack, info in sorted(catalog["sourcePacks"].items())
        },
        "problems": problems,
    }
    VALIDATION.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"WROTE {VALIDATION}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())

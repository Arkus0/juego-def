# Remote repair — intake source identity blocker

Date: 2026-09-28.

Reviewer #5338897627 rejected the previous frozen candidate because non-Medieval intake copied textures and other supporting bytes that were not part of the committed source identity. A same-path texture change could therefore change a clean clone's visual result without changing the catalogue snapshot.

## Repair applied remotely

`Tools/asset_catalog.py` now:

- defines the exact copied-source globs once and reuses them for install + provenance;
- computes a deterministic `intakeIdentity` for every pack;
- uses the pinned whole-archive SHA-256 for Medieval Village;
- uses SHA-256 over sorted `(relative path, content SHA-256)` rows for Props, Nature, Base Characters, Outfits and UAL;
- records that identity in schema-v2 `sourcePacks` metadata when `build` runs;
- refuses `install` when the current vault identity differs from the committed catalogue;
- stores the matched identity in `.juego-def-intake.json` receipts;
- makes `validate` compare catalogue identity, current vault identity and receipt identity;
- makes `validate` compare every copied non-Medieval source byte, including textures that are intentionally not semantic catalogue candidates.

`Tools/test_asset_intake_identity.py` is a vault-independent regression probe. Remote Worker execution passed:

```text
PASS: intake identity changes on texture mutation/addition and is stable otherwise
```

The probe specifically creates a synthetic Props FBX + texture pair, verifies stable identity with unchanged bytes, mutates the texture at the same path and requires the identity to change, then adds another texture and requires identity + file count to change.

Python syntax compilation of the repaired tool and the one-command refresh helper passed remotely.

## Main reconciliation

The repair branch was reconciled with current `main` after accepted `CITY-URBAN-00` / DocSync. No ASSET implementation file overlapped those main changes; the branch now consumes the current B0/CITY authority rather than the pre-CITY snapshot.

## Required bounded local vault refresh

The committed `catalog.json` still reflects schema v1 because the remote Worker cannot access `C:/Juego2-Assets`. This branch is therefore **not yet frozen for Reviewer**.

The local completion has been reduced to one command from repository root:

```powershell
python Tools/refresh_asset_intake_evidence.py
```

The helper does not commit, push, open Unity or modify the vault. It runs the regression probe, rebuilds the schema-v2 catalogue, refreshes all seven pack receipts, validates the complete intake and rewrites `Docs/evidence/WP-PROD-ASSET-00/VALIDATION.json` with the pack identities and final problem list.

Expected completion condition: catalogue remains 796 semantic candidates unless the actual vault changed, each `sourcePacks.*.intakeIdentity` is populated, all installed receipts carry the same identities, and final Python validation reports zero problems. If candidate count or source identities differ unexpectedly, stop and inspect the vault change instead of treating it as routine refresh.

After that bounded local run, commit the regenerated `catalog.json` plus refreshed `VALIDATION.json`, freeze the new exact `PRODUCT_SHA`, and request a fresh independent Reviewer.

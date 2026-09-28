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

## Local vault refresh completed

The local Worker ran the bounded refresh against `C:/Juego2-Assets` on 2026-09-28:

```powershell
python Tools/refresh_asset_intake_evidence.py
```

The regression probe passed. The schema-v2 catalogue contains the same 796 semantic candidates and populated identities for all seven packs. Intake found zero new source files; the Medieval archive identity remained pinned and 14 local Unity material upgrades were preserved. `validate` reported zero problems after comparing the catalogue, vault, installed receipts and copied source bytes. The resulting identities and problem list are recorded in [VALIDATION.json](VALIDATION.json).

The helper did not open Unity or modify the vault. The earlier Unity Editor validation remains recorded in [UNITY_VALIDATION.md](UNITY_VALIDATION.md). This local run closes the source-identity evidence gap and is ready for fresh independent review of the new frozen commit.

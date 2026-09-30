# WP-PROD-ENV-01 — dependency check

Date: 2026-09-28. Worker: Claude Code (Opus 5.5) with MCP for Unity + headless Blender 5.2.1. Baseline: `main` at `99302e6` (after `PROD-ASSET-00` PASS + DocSync).

## Direct accepted prerequisites

| Prerequisite | State on `main` | Consumed guarantee |
| --- | --- | --- |
| `WP-PROD-ASSET-00` | PASS + DocSync | Stable catalogue IDs (`catalog.json`), `install --pack` intake with pinned identities, owned-derivative convention `Assets/JuegoDef/Derived/<LANE>/` + `lineage.json`, `validate` and `Validate Asset Intake`. Vendor bytes stay ignored. |
| `WP-CITY-URBAN-00` | PASS / accepted | `CITY_URBAN_00_HANDOFF.md` ENV factory-demand matrix (12 `FACTORY_REQUIRED` rows, 1 `PROXY_ALLOWED_FOR_INTEGRATION`, 2 `DEFERRED_OUTSIDE_B0`) and B0 anchors/routes/access truth in `FIRST_KEEPER_BLOCK_B0.md`. |
| `BOOTSTRAP-UNITY-GC2` | PASS | Unity 6000.3.24f1 + URP 17.3 + GC2 Core player/camera for third-person checks; MCP operator path (`BOUNDED_OPERATOR`). |

## Guarantees/inputs consumed, not re-proved

- Medieval Village, Props and Nature are CC0, catalogued and installed through `python Tools/asset_catalog.py install --pack medieval|props|nature` (receipts match the committed identities). The earlier local provisioning copy from the archived ENV-01 attempt was replaced by the accepted intake; nothing from that attempt is committed.
- QuaterniusUnityUtils spike (ASSET-00): native Medieval prefabs already carry collision; the utility's collision maker is `REFERENCE_ONLY`.
- Known intake gap: vendor `MI_Plaster.mat` references one missing wear texture; ENV must use owned material variants instead of patching the vendor file.
- B0 demand rows and access rules are consumed as the product customer; ENV does not re-plan the block.

## What this WP newly owns

- The environment production path: semantic ENV catalogue, material/palette system, Blender donor/derived path, assembly grammar and templates, validators, operator recipe.
- The first juego-def-owned ENV module/unit library under `Assets/JuegoDef/Derived/ENV/` with lineage.
- `B0_COVERAGE.md`: which accepted ENV demand rows have ready units and which remain bounded gaps.

## Reopen conditions

- A catalogue/intake identity mismatch or missing native GUID would reopen ASSET-00 intake (not observed: `install` accepted all three ENV packs).
- A B0 demand that cannot be expressed as frontage/threshold/edge vocabulary without changing access or route truth would reopen CITY-URBAN-00 (none known).
- Owner rejection of the composed look would reopen the material/grammar decisions here, not CITY or ASSET.

## Knowledge carried from the archived ENV-01 attempt (not its bytes)

- Juego2 ART-01 read as an alpine village: detached houses, gables to the street, two floors. The target here is terraced port-town fabric: party walls, 3–4 storeys, low roofs parallel to the street, commercial ground floors, iron balconies/galleries, plaster in restrained colours.
- The kit is a 2 m bay × ~3 m storey grid; a small spec-driven assembler that only places vendor prefabs is the right size of tool. A builder growing into a framework is an alarm signal.
- Route probes in Play Mode catch collision defects that screenshots miss.

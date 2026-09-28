# WP-PROD-ENV-01 evidence — Environment Asset + Assembly Factory

Date: 2026-09-28. Worker: Claude Code (Opus 5.5) as Worker + Unity/asset operator (MCP for Unity 10.2.0, Unity 6000.3.24f1, headless Blender 5.2.1). Authoritative workflow: [`Docs/production/ENV_FACTORY.md`](../../production/ENV_FACTORY.md). This is Worker evidence; independent review is still required.

## Claim → evidence

| WP requirement | Evidence |
| --- | --- |
| 1. `ENV_FACTORY.md` | [`Docs/production/ENV_FACTORY.md`](../../production/ENV_FACTORY.md) |
| 2. `REUSE_DECISIONS.md` (bounded tests before custom tooling) | [REUSE_DECISIONS.md](REUSE_DECISIONS.md): Medieval kit, `osm_building_grammar` (run in Blender 5.2), QuaterniusUnityUtils, `game_export` (registered in Blender 5.2), Material Batch Tools, Auto/Geo-Buildings, Unity native import, Blender headless |
| 3. Lane semantic catalogue/tags on PROD-ASSET-00 | `Docs/asset_catalog/env_library.json` (units: demand rows, size, request, bill of modules), `env_derive_manifest.json` (derived modules: class, donors, method), `python Tools/env_catalog.py search/modules`; kit modules keep their PROD-ASSET-00 IDs |
| 4. Reusable owned prefab/module library | `Unity/JuegoDef/Assets/JuegoDef/Derived/ENV/`: 43 derived meshes, 65 module prefabs (43 derived + 22 collider/material wrappers of Props/Nature models), **19 production units** ([INVENTORY.md](INVENTORY.md), [unit previews](units/)) |
| 5. Material/palette adaptation system | `Env/Grammar/materials.json` + `palettes.json` → 39 owned materials + 4 neutral textures, 8 palettes, role-based slot remap (`JuegoDef > ENV > 1 Generate Materials`) |
| 6. Donor extraction / derived path | `Tools/blender/env_derive.py` (43 recipes, ~6 s); worked example below |
| 7. Assembly templates/rules | `FacadeGrammar` (frontage types, bay codes, rhythms, one-balcony rule), `BuildingAssembler` (layered assembly, party walls, quoins, verges), `EnvTemplates` (street ground, quay edge, yard boundary, stepped connector, interiors), `EnvStreet` (street specs) |
| 8. Cheap validation | `EnvValidator` → [VALIDATION.json](VALIDATION.json): **0 problems** over 19 units + 2 street scenes; **self-test 6/6 seeded defects detected**; `env_catalog.py check` and `asset_catalog.py validate` clean |
| 9. Non-trivial factory batch | 19 units across 13 demand rows (buildings of 5 frontage types, shop/lodging interiors, street/lane ground, stepped connector, public quay, controlled yard, market/port/furniture clusters, frontage vocabulary) + 2 materially different streets built from specs |
| 10. `B0_COVERAGE.md` | [B0_COVERAGE.md](B0_COVERAGE.md): every ENV demand row has a validated unit; bounded gaps listed |
| Captures / previews | [units/](units/) (19), [captures/](captures/) (streets A1–A6, B1–B3, derivation D1–D2, iteration I1–I4, Play Mode P1) |
| Validator results / route probes | [VALIDATION.json](VALIDATION.json), [ROUTE_PROBES.md](ROUTE_PROBES.md): street A **12/12**, street B **8/8**, 0 stalls, GC2 player |
| Dependency check | [DEPENDENCY_CHECK.md](DEPENDENCY_CHECK.md) |
| Lineage | `Docs/asset_catalog/lineage.json`: 170 ENV records (DONOR 22, CREATE_DERIVED 59, ADAPTABLE 51, ORIGINAL 38); PROD-ASSET-00 catalogue rebuilt so sources expose `derivedIds` |

## Two materially different streets from the same factory

| `ENV01_DemoA_Commercial_To_Quay` (kerbed, 42 × 8 m) | `ENV01_DemoB_Upper_Lane` (pedestrian, 28 × 6 m) |
| --- | --- |
| ![A1](captures/A1_street_from_west.jpg) | ![B1](captures/B1_lane_from_west.jpg) |
| ![A2](captures/A2_towards_quay.jpg) | ![B2](captures/B2_stepped_connector.jpg) |
| ![A4](captures/A4_shop_threshold.jpg) | ![B3](captures/B3_terrace_looking_back.jpg) |
| ![A6](captures/A6_yard_vs_public_edge.jpg) | ![A5](captures/A5_lodging_portal.jpg) |

Both are requested as data (`Env/Specs/streets/*.json`) from library unit IDs plus overrides; no scene-specific code or exact object paths. They are composition tests of the factory, **not** B0 keeper geometry (that is `WP-CITY-URBAN-01`). Play Mode through the GC2 camera: ![P1](captures/P1_play_mode_gc2_camera_lane_B.jpg)

## Worked donor → final example

![D1](captures/D1_donor_wall_to_clean_to_palette_and_shopfront.jpg)

Read right to left: kit `Wall_Plaster_Straight` (timber braces/post — alpine cue) → `ENV_Wall_Plaster_Clean` (`clean_plaster()`: loose `MI_WoodTrim` parts deleted except the floor-line band; the plaster plane is continuous behind) → same wall with the `cream_green` palette → kit `Wall_Plaster_Straight_Base` → `ENV_Wall_Plaster_Shopfront` (cleaned + 1.6 × 2.38 m boolean cut, hole-tolerant exact solver, stone reveals) → dressed with `ENV_Shopfront_Door_Open` (flush threshold, 2.22 m clear), fascia and awning, palette-remapped. Lineage record: `env:meshes:ENV_Wall_Plaster_Shopfront`, class `DONOR`, sources `medieval:wall_plaster_straight_base`, … (materials traced automatically).

![D2](captures/D2_donor_gable_and_stone_window.jpg)

Right to left: kit `Roof_Front_Brick6` (half-timbering + projecting purlins) → `ENV_Roof_Gable_6`; kit `Window_Wide_Flat_Rocks` (stone surround only — the empty building showed through) → with the derived `ENV_Window_Insert_Wide` sash measured on the donor wall opening.

## Iteration history (owner reviews during the session)

| I1 kit pieces as-is | I2 derived frontage | I3 after "ojo con tantas puertas arriba" | I4 after "compáralo con fotos reales… dejar respirar" |
| --- | --- | --- | --- |
| ![I1](captures/I1_first_row_kit_timber_brick_plaster.jpg) | ![I2](captures/I2_derived_frontage_before_owner_review.jpg) | ![I3](captures/I3_after_review_one_balcony_door.jpg) | ![I4](captures/I4_clean_walls_no_half_timbering.jpg) |

## Operator log — failures and corrections

| # | Failure | Diagnosis | Correction (kept in the factory) |
| --- | --- | --- | --- |
| 1 | No JuegoDef editor attached to MCP | only another project was open | launched the project editor; pinned instance `JuegoDef@9bfcb657` |
| 2 | Local Medieval copy from the archived attempt had a foreign receipt | old provisioning script | moved it aside, reinstalled via accepted `asset_catalog.py install` |
| 3 | Props/Nature 100× scale | intake minimal `.meta` ignores FBX file scale | `EnvImportRules` (useFileScale) |
| 4 | Every prop rendered white | textures imported as Cubemap; materials generated locally with random GUIDs | `EnvImportRules` 2D textures + owned `ENV_Src_*` materials in wrappers |
| 5 | Plaster palettes all brown | `M_Plaster` base texture non-modifiable + brick-reveal masks | owned plaster on `M_BaseWear` + neutral textures |
| 6 | Half-timbering and purlins everywhere | kit walls/gables carry timber parts | derived clean walls/gables; validator bans the originals |
| 7 | Derived pieces mirrored in Z | kit export = source rotated 180° | `U()` + `export()` rotation |
| 8 | Boolean cut kept cutter geometry | kit walls are open shells | exact solver, hole tolerant |
| 9 | Too many windows/doors upstairs | grammar gave every bay an opening/balcony | one-balcony rule; rhythms calibrated on real Cantabrian/Galician photos |
| 10 | Stone windows showed empty interiors | kit "Rocks" window is only a surround | derived glazed inserts |
| 11 | Shop door not walkable (4 separate causes) | leaf swing, sill, head height, floor slot | see [ROUTE_PROBES.md](ROUTE_PROBES.md); validator now checks with the real capsule |
| 12 | Beige shop glass | emission under project exposure (not reflections) | no emission on shop glass; streets bake a reflection probe |
| 13 | Lineage over-attributed a flat material to a kit door | shared shader GUID was treated as a source | lineage traces textures only; kit material → representative module table |
| 14 | MCP bridge dropped once during a long call + recompile | long synchronous call | split pipeline calls |

Counts: owner manual clicks **0**, exact-path hints **0**, owner interventions **2 visual reviews** (both folded into grammar rules). Escape hatches: `execute_code` for pipeline runs, runtime probes and captures.

## Repeatability boundary

Vendor bytes stay ignored; on a clean clone: intake (`install --pack medieval|props|nature`) → open Unity (import rules apply on first import) → `JuegoDef > ENV > 1…5`. Committed derived meshes carry their `.meta` material remaps to vendor GUIDs (deterministic from the admitted archive/intake). Re-running Blender recipes rewrites FBX bytes (timestamps) but not GUIDs or geometry semantics.

## CASCO district (owner request 2026-09-28: grow Demo C into a ~180 × 220 m "mini Potes" casco)

ENV-01 stays open until this district is built and judged (owner decision). Study, decisions and numbers:
[CASCO_REFERENCE_STUDY.md](CASCO_REFERENCE_STUDY.md); rules: [`ENV_COMPOSITION_RULES.md`](../../production/ENV_COMPOSITION_RULES.md).

| Milestone | Result | Evidence |
| --- | --- | --- |
| H1 skeleton | authored network over the measured Potes core (box A): 38 streets, 18 blocks, 311 plots from the real subdivision; grades **69/23/8 %** vs the reference's 21/24/55 % | [plan](reference/casco_district_skeleton.png), [box options](reference/casco_district_box_options.jpg) |
| H2 first build | `EnvDistrict` builds the whole district from the spec in ~4 s: heightfield ground, rows on the terrain with stone bases, garden walls, channelled river, bridges, stairs, plazas, player | [sheet](captures/district/H2_first_build_sheet.jpg), [top view](captures/district/H2_top_view.jpg) |
| H3 asset quality + lebaniego vocabulary | painted textures instead of flat colours; street pieces rebuilt to kit level; canecillo eaves, solanas, ashlar quoins on seen corners only, sandstone surrounds, casona shield; canto rodado with a central flag strip; far fewer downpipes | [asset lab](captures/district/H3_asset_lab_sheet.jpg), [district](captures/district/H3_district_potizado_sheet.jpg) |
| H4 composition | tower closing the spine, stone arch bridges, stair down to the river, plazuela fountain, huerta trees, valley backdrop with the sea to the north, route probe over the whole tour | [sheet](captures/district/H4_composition_sheet.jpg), [route](ROUTE_PROBES.md#casco-district) |

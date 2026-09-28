# Existing asset-pipeline research — production baseline

Status: **MIGRATED RESEARCH / BINDING INPUT TO FACTORY WPS**  
Date: 2026-09-28

## Purpose

Before juego-def writes custom graphical-production tooling, it must consume the strongest existing Quaternius/Blender/Unity pipeline research already discovered in Juego2.

The binding production rule is:

> **Do not invent a pipeline stage that a lawful existing tool/technique already solves adequately. Spike first, then reuse/adapt, and implement only missing glue.**

This document does not itself adopt or purchase any dependency. Exact version, compatibility and license/provenance must be checked at the moment of adoption.

## Source findings migrated from Juego2

The prior audit found that most hard production stages already have concrete precedent:

- Quaternius Universal Base Characters + Modular Character Outfits + Universal Animation Library form a shared humanoid ecosystem;
- reproducible Blender/Python pipelines exist for proportion editing, clothing construction/fitting, weight transfer and export;
- Quaternius-specific Unity utilities already automate UAL import settings and collision-prefab construction;
- Blender tooling exists for batch materials, building composition and Blender-to-Unity export/prefab workflows;
- public building-grammar projects already demonstrate semantic facade/window/door/shop/balcony/awning/roof/etc. vocabularies.

Therefore the factory WPs start from **reuse/adaptation**, not greenfield tooling.

## Candidate matrix

| Candidate | Lane | What it already demonstrates | Research disposition | Required action before equivalent custom tooling |
| --- | --- | --- | --- | --- |
| Quaternius Universal Base Characters | CHAR | shared Humanoid base, proportions, hair, rigged source, animation compatibility | USE when lawfully admitted | inspect actual owned/source corpus and make this the default baseline unless evidence rejects it |
| Quaternius Modular Character Outfits | CHAR | modular wardrobe on shared humanoid basis | USE / ADAPT / DONOR | test real civilian adaptation before building a custom wardrobe system |
| Quaternius Universal Animation Library | ANIM | shared rig, broad motion corpus, root/no-root variants | USE when admitted | inventory real owned corpus before sourcing/building another animation pipeline |
| Quaternius Medieval Village MegaKit Source | ENV | 300+ modular pieces, interiors, collisions, URP/source precedent | USE / ADAPT / DONOR | inspect as component library; do not reject due to medieval/timber label |
| Quaternius Downtown City MegaKit Source | ENV | modular urban/street pieces, fake interiors, wear/bevel/collision techniques | WATCH / future USE | evaluate only if owned or a real gap justifies acquisition |
| `ChilyerStudiosLLC/blender-character-pipeline` | CHAR | Quaternius base import, proportion edit, body-topology clothing, real-animation verification, scripted export | ADAPT / REFERENCE; MIT observed | bounded spike of its techniques before inventing an equivalent character transformation pipeline |
| Tinqs clothing pipeline | CHAR | staged `census -> prepare -> fit -> reduce -> bake -> skin -> export`, weight transfer, checkpoints | REFERENCE_ONLY; code license unresolved in prior audit | reuse architecture/ideas only until exact license verified; do not copy code blindly |
| Avelune | CHAR / ANIM | Quaternius character composition and shared animation-data architecture | REFERENCE / possible ADAPT; MIT observed | inspect architecture before duplicating character/animation packaging logic |
| `Animate-Rigged-Humanoid-No-Blender` | ANIM | programmatic Quaternius + UAL merge outside Blender | REFERENCE / WATCH | use as evidence/technique only; Three.js assumptions are not Unity authority |
| `firstkindgamer/QuaterniusUnityUtils` | ENV / ANIM | UAL import automation + Quaternius collision-prefab construction; Medieval Village support | **FIRST SPIKE**; Unlicense observed | test against current Unity 6000.3.24f1 before writing equivalent import/collision tooling |
| `codec-xyz/game_export` | ENV | Blender collections -> FBX/Unity prefab, material remap, colliders, instances | REFERENCE / SPIKE; MIT observed | compare on current Unity before writing exporter/prefab glue; avoid unsafe direct YAML assumptions |
| Auto-Building | ENV | custom modular collections, openings, facade/edge distribution, roofs, foundations, basic interiors | PAID SPIKE ONLY | only test/buy if repeated building work shows a real gap; prior audit noted Blender-version compatibility caveat |
| Geo-Buildings | ENV | Geometry Nodes building generator with custom assets/materials | ALTERNATIVE SPIKE | compare with Auto-Building only if procedural assistance is actually needed |
| `p-schulz/osm_building_grammar` | ENV | semantic building roles, deterministic style/config, metadata, instancing/batching | REFERENCE / ADAPT; Apache-2.0 observed | consume semantic-role model before inventing our own donor/facade taxonomy |
| Material Batch Tools (`mat_batch_tools`) | ENV | batch node/material normalization and bake/UV preparation | EXTERNAL TOOL SPIKE; GPL observed | test externally if material normalization becomes repetitive; do not vendor code by default |

## Mandatory candidate order by lane

### Shared substrate (`PROD-ASSET-00`)

Before creating broad custom indexing/import machinery:

1. inspect the actual owned Quaternius source corpus and its metadata/source projects;
2. test whether Unity/Editor indexing plus generated metadata is sufficient for semantic discovery;
3. spike `QuaterniusUnityUtils` for the exact import/collision jobs it claims to solve;
4. retain only missing common glue.

### Environment (`PROD-ENV-01`)

Before building custom environment generators:

1. inspect Medieval Village source modularity and any already-owned urban packs;
2. use `osm_building_grammar` as the first semantic-role/taxonomy reference;
3. test `QuaterniusUnityUtils` collision/import ideas where applicable;
4. inspect `game_export` techniques if Blender->Unity handoff becomes repetitive;
5. use material-batch tooling externally if normalization is materially repetitive;
6. only then, if real repeated-building work still hurts, benchmark Auto-Building vs Geo-Buildings;
7. write only the glue/templates/validators not adequately covered.

### Characters (`PROD-CHAR-01`)

Before building a custom civilian generator:

1. use Universal Base Characters as the shared-rig hypothesis;
2. test real Modular Outfits adaptation/donor combinations;
3. reproduce a bounded Chilyer-style workflow on our actual source;
4. consume Tinqs staged architecture as reference for fitting/skin/export checkpoints without copying unverified-license code;
5. inspect Avelune composition/shared-animation patterns;
6. automate only the repetitive steps still left.

### Animation (`PROD-ANIM-01`)

Before writing custom retarget/import tooling:

1. inventory the actual UAL/source corpus;
2. test `QuaterniusUnityUtils` import rules against current Unity;
3. validate shared-rig assumptions on accepted civilian bases;
4. inspect Avelune / no-Blender packaging references for data-sharing ideas;
5. build only the missing metadata/presets/validation/runtime glue.

## Required `REUSE_DECISIONS.md`

Each factory WP must retain a small `REUSE_DECISIONS.md` in its evidence folder with one row per materially relevant candidate:

- candidate + exact version/commit/page snapshot where practical;
- actual bounded task tested;
- license/provenance status;
- `USE`, `ADAPT`, `REFERENCE_ONLY`, `REJECT`, `NOT_MATERIAL`, `DEFER`;
- measured/observed reason;
- what custom glue remains necessary.

A candidate may legitimately be rejected. What is not allowed is silently reimplementing the same stage without looking.

## Purchase rule

No paid tool/pack is required merely because it appears here. Purchase is justified only when a bounded real task shows a material time or quality gain over owned/native/free alternatives.

## Source archive

This baseline was distilled from Juego2 research including:

- `Docs/discovery/QUATERNIUS_ADAPTATION_ECOSYSTEM_AUDIT.md`
- `Docs/discovery/QUATERNIUS_TOOLING_CATALOG.md`
- `Docs/discovery/QUATERNIUS_WP_IMPACT_MAP.md`

Those remain historical research evidence. This document is the self-contained execution baseline for juego-def.
# WP-PROD-CHAR-01 — Civilian Character + Wardrobe Factory

Status: **READY AFTER ASSET-00**  
Class: PRODUCTION FACTORY / CHARACTERS  
Depends on: `WP-PROD-ASSET-00` PASS  
Blocks: `WP-PROD-CHAR-02`, `WP-PROD-ANIM-02`

## Claim

juego-def has a repeatable civilian-character factory that can transform the admitted character/body/wardrobe corpus into coherent ordinary townspeople without bespoke manual repair for each NPC.

The factory must make **adding another ordinary civilian routine production work**. Hero/narrative characters may use bespoke treatment later.

## Required factory outputs

By PASS, retain:

1. `CHAR_FACTORY.md` — authoritative production workflow;
2. accepted base body/rig/avatar families;
3. machine-readable compatibility matrix for body/rig/wardrobe/accessory families actually used;
4. reusable wardrobe/material/palette variation mechanism;
5. prefab/variant creation template or small batch tool;
6. clipping/scale/material/avatar validation path;
7. Blender/source adaptation route for donor garments/meshes when useful;
8. semantic tags for civilian roles/silhouettes;
9. a non-trivial seed batch proving the factory.

## Minimum seed batch

Produce **6+ materially distinct civilian seed variants** through the same factory path. The goal is not the final population count; it is to prove the factory can generate distinct ordinary people without six unrelated one-off workflows.

Variants should exercise multiple combinations across:

- body/silhouette where supported;
- tops/bottoms/full outfits;
- hair/head/accessories;
- palette/material families;
- at least several different civilian role cues.

Do not satisfy the batch with recolours only.

## Compatibility + adaptation rules

The factory must know, for each admitted source family:

- rig/avatar compatibility;
- clothing/body assumptions;
- whether it is `DIRECT`, `ADAPTABLE`, `DONOR` or requires `CREATE_DERIVED`;
- safe Unity-side changes;
- changes requiring Blender/source editing;
- known clipping/weighting/scale failure patterns;
- animation compatibility expectations.

Fantasy/medieval source labels are not automatic rejection. Final civilian coherence governs acceptance.

## Civilian semantics

Support useful role tags that help batch generation/composition, for example:

- dock/warehouse worker;
- market/shop worker;
- service/office worker;
- older resident;
- younger resident;
- casual/nightlife visitor;
- neutral everyday pedestrian.

These are production roles, not narrative biographies.

## Tooling expectation

Use the simplest mix of:

- catalogue metadata;
- prefab variants/templates;
- material/palette presets;
- small Editor/batch scripts;
- MCP operator assembly;
- Blender derivation for incompatible/over-themed garments.

A large procedural character generator is not required. But repeated operations should not stay manual if a tiny tool/template can eliminate them.

## Validation baseline

For every generated civilian, cheaply check where relevant:

- valid rig/avatar;
- severe skinning/exploded mesh issue;
- body-through-clothing clipping in idle/basic locomotion poses;
- foot/ground/scale plausibility;
- URP/material correctness;
- missing references;
- duplicate/invalid generated identity/path;
- prefab reproducibility.

## Evidence

Retain under `Docs/evidence/WP-PROD-CHAR-01/`:

- factory workflow;
- compatibility matrix;
- seed batch inventory + lineage;
- third-person group captures;
- at least one bad/incompatible combination and factory response;
- retained tooling/templates that reduce repeated work;
- known source/wardrobe gaps.

## PASS

PASS when:

- 6+ distinct seed civilians are produced through one repeatable factory;
- compatibility/adaptation is encoded rather than remembered ad hoc;
- routine generation does not require unexplained manual mesh/rig repair;
- common bad combinations are detected/rejected cheaply;
- output prefabs are animation-ready and reproducible;
- creating the next ordinary civilian from covered source families is mostly selection/production, not pipeline R&D.

## FAIL

FAIL if six characters are unrelated one-offs, wardrobe compatibility remains tribal knowledge, fantasy/source identity dominates final civilians, most variants need bespoke repair, or tooling effort expands into an unnecessary universal character system.

## Handoff

`WP-PROD-CHAR-02` must prove the factory at population-batch scale and expose clone/coherence/performance problems before CITY integration.

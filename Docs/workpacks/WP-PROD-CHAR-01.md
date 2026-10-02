# WP-PROD-CHAR-01 — Civilian Character + Wardrobe Factory

Status: **READY AFTER ASSET-00**  
Class: PRODUCTION FACTORY / CHARACTERS  
Depends on: `WP-PROD-ASSET-00` PASS  
Blocks: `WP-PROD-CHAR-02`, `WP-PROD-ANIM-02`

## Claim

juego-def has a repeatable civilian-character factory that can transform the admitted character/body/wardrobe corpus into coherent ordinary townspeople without bespoke manual repair for each NPC.

The factory must make **adding another ordinary civilian routine production work**. Hero/narrative characters may use bespoke treatment later.

## Binding product demand

Consume [`../design/FIRST_KEEPER_BLOCK_B0.md`](../design/FIRST_KEEPER_BLOCK_B0.md). The seed batch must cover people useful to B0 rather than arbitrary showcase characters.

Priority role cues:

- market/shop worker;
- dock/port worker;
- older resident;
- younger/casual resident;
- ordinary service/office worker;
- neutral everyday pedestrian.

These are production roles, not narrative biographies.

## Binding research input — mandatory

Consume [`../research/EXISTING_ASSET_PIPELINE_RESEARCH.md`](../research/EXISTING_ASSET_PIPELINE_RESEARCH.md) before implementing a custom character/wardrobe generator.

Retain `Docs/evidence/WP-PROD-CHAR-01/REUSE_DECISIONS.md` covering at minimum:

1. Universal Base Characters as the shared-body/rig baseline hypothesis;
2. real Modular Character Outfits adaptation/donor tests;
3. a bounded reproduction of useful Chilyer `blender-character-pipeline` techniques on our actual source family;
4. Tinqs staged garment architecture as `REFERENCE_ONLY` unless exact code licensing is verified;
5. Avelune composition/shared-animation architecture as a reference before duplicating packaging logic;
6. only missing repetitive steps should become juego-def-specific tooling.

A candidate may be rejected; reinvention without evaluation is not acceptable.

## Required factory outputs

By PASS, retain:

1. `CHAR_FACTORY.md` — authoritative production workflow;
2. `REUSE_DECISIONS.md`;
3. accepted base body/rig/avatar families;
4. machine-readable compatibility matrix for body/rig/wardrobe/accessory families actually used;
5. reusable wardrobe/material/palette variation mechanism;
6. prefab/variant creation template or small batch tool;
7. clipping/scale/material/avatar validation path;
8. Blender/source adaptation route for donor garments/meshes when useful;
9. semantic tags for civilian roles/silhouettes;
10. a non-trivial seed batch proving the factory;
11. `B0_ROLE_COVERAGE.md` mapping B0 civilian needs to ready variants or gaps.

## Minimum seed batch

Produce **6+ materially distinct civilian seed variants** through the same factory path, deliberately covering several B0 roles. The goal is not the final population count; it is to prove the factory can generate distinct ordinary people without six unrelated one-off workflows.

Variants should exercise multiple combinations across body/silhouette where supported, tops/bottoms/full outfits, hair/head/accessories, palette/material families and role cues. Do not satisfy the batch with recolours only.

### Owner amendment — 2026-09-29: structural diversity at gameplay distance

Keep the existing rig and factory. Refine the same six role seeds; additional NPC count is not the objective. Prove people read as distinct at 10–20 metres, within one ordinary town and one PS2+/early-PS3-compatible stylized family. Colour changes do not count as material variants.

- Support at least 3–4 controlled body families covering short/tall, slim/medium/heavy and young/adult/older. Vary shoulders, torso, hips and leg length while preserving Humanoid retarget.
- Vary broad facial shape/age cues (jaw, nose, brows, cheekbones, hairline) without investing in higher-resolution face/texture detail. Use ordinary hair, greying and partial baldness.
- Distinguish roles through layered outfits, footwear and inexpensive functional accessories. Examples include jacket over T-shirt, shirt/jersey, work vest, light coat, hoodie, apron, glasses, bag, backpack, cap or watch. Each recipe must own the compatibility of its choices.
- Preserve the older resident's successful baldness/glasses/age read. Separate the red casual man structurally from the orange/navy port worker. Give the three women different body/clothing/role silhouettes; any market apron must read as a functional garment.
- Retain joint frontal, lateral and three-quarter gameplay-distance captures, including a reduced-size silhouette check. Prioritize silhouette, age and function over cosmetic recolour/detail.
- Run the same six through accepted ANIM-01 idle, walk and talking motions. Record clipping/deformation as recipe incompatibilities; fix the common recipe/family or reject the combination, never make unexplained per-NPC mesh/rig repairs.
- Owner follow-up: compare the current ENV-01 visual level before closing. Use its authored forms, functional construction and restrained material treatment as calibration; retain the structural priority and existing rig/pipeline.

## Compatibility + adaptation rules

### Owner amendment — 2026-10-01: naturalismo estilizado / ENV01 quality

The Owner accepted the full fifteen-person naturalism plan. Continue the existing CHAR candidate; preserve its rig, Humanoid/ANIM integration and IDs. Deliver materially authored heads, everyday hair, plausible anatomy, constructed garment patterns and individual restrained presentation. Parameter differences, recolours and accessory-only identity do not prove this amendment. Source topology may be replaced where it limits the result; authored reusable forms must survive the normal build. No additional population, schedules, narrative, facial rig or paid dependency is authorized.

Judge all fifteen in comparable bare-face and full-body views, at conversation distance and 10/20m, and in an isolated snapshot of the current effective ENV01 with its actual light, renderer and player camera. The ENV snapshot is calibration, not permission to edit ENV. Retain before/after, all-fifteen idle/walk/talk Play-Mode evidence, reconstruction identity and geometry/render observations. Update older six-person reports to the actual fifteen-person boundary. Subjective final acceptance remains with the Owner; Worker readiness is never independent PASS.

### Owner amendment — 2026-10-02: human anatomy and replacement of limiting source heads

The Owner rejects the revised Quaternius-derived heads as monsters and supplies a modern Yakuza screenshot and a Shenmue II group screenshot. The acceptance target is recognizably human anatomy, individual faces, natural eyes/lids/lips/nose/jaw, readable ordinary moods and coherent hair/skin, at ENV01's graphic density. Shenmue II is the practical detail reference; the modern screenshot is an anatomy reference, not an AAA fidelity mandate. Recolouring or further warping of the rejected head does not satisfy this request.

The Owner explicitly authorizes departure from Quaternius. Replace the head topology and its UV/material treatment where needed, using admitted lawful free human assets or authored equivalents. Keep the existing fifteen IDs, body/wardrobe improvements, admitted Humanoid skeleton and ANIM integration. Test a male and female pilot in Unity before applying the human head route to all fifteen. No new facial rig, population, gameplay authority or paid dependency. All earlier readiness/evidence remains superseded; the Owner retains final subjective acceptance.

### Owner amendment — 2026-10-02: character polish and living presentation

The Owner confirms that the anatomical replacement is the correct direction and singles out the veteran waiter as a useful face reference, while requiring a final Dreamcast/PS2+ finish at ENV01 quality. Use the waiter as the polish pilot, then apply shared corrections to the fifteen-person factory: darker integrated eyes, positioned lids/brows, visible facial volume under actual ENV light, restrained skin colour/roughness variation, a clean jaw/collar/bow-tie junction, deliberately constructed vest edges/folds and balanced head/shoulder proportions. Preserve character differences rather than cloning this face. Increasing geometric fidelity is not the primary remedy.

The Owner also explicitly requests irregular blinking, breathing, subtle head/eye attention and weight shifts. Bounded presentation behaviour and eyelid blend shapes are now authorized, using the existing Humanoid skeleton and animation authority. No new face-bone rig, player/gameplay authority, schedules or population. Observe the living pilot in Play Mode; frozen stills alone do not establish this added claim.

### Owner amendment — 2026-10-02: regional references, readable mood and clothing fit

The Owner rejects the current unsettling, neutral faces and visible clothing intersections. Continue the same fifteen-person candidate. Use real people photographed in Asturias and Cantabria as references for varied ordinary faces, expressions, hair and everyday clothing, with the readable character treatment of Shenmue. Reference photographs inform authored forms; they are not adopted textures, identities or biographies. Record source links and disposition.

Give each civilian a deliberate readable resting expression: relaxed/welcoming, happy or plainly grumpy as appropriate. A small mouth-corner adjustment and an empty numeric error list do not prove this. Women must have no moustache, including painted or shaded upper-lip marks that read as one. Rework common garment cuts, overlapping layers and skinning wherever clothing enters the body or another layer; inspect front, side and back in idle/walk/talk and actual ENV lighting. Previous readiness and captures are superseded until these corrections are observed and rebound. Keep the admitted skeleton and no new facial rig, population or paid dependency. Owner retains final art acceptance.

The factory must know, for each admitted source family, rig/avatar compatibility, clothing/body assumptions, reuse class (`DIRECT`, `ADAPTABLE`, `DONOR`, `CREATE_DERIVED`), safe Unity-side changes, Blender/source-edit needs, common clipping/weight/scale failures and animation compatibility expectations.

Fantasy/medieval source labels are not automatic rejection. Final civilian coherence governs acceptance.

## Tooling expectation

Use the simplest mix of existing/adapted pipeline techniques, catalogue metadata, prefab variants/templates, material/palette presets, small Editor/batch scripts, MCP operator assembly and Blender derivation where needed.

A large procedural character generator is not required. But repeated operations should not stay manual if a tiny tool/template can eliminate them.

## Validation baseline

For every generated civilian, cheaply check where relevant valid rig/avatar, severe skinning failure, body-through-clothing clipping in idle/basic locomotion poses, foot/ground/scale plausibility, URP/material correctness, missing references, duplicate/invalid generated identity/path and prefab reproducibility.

## Evidence

Retain under `Docs/evidence/WP-PROD-CHAR-01/`:

- `REUSE_DECISIONS.md`;
- `B0_ROLE_COVERAGE.md`;
- factory workflow;
- compatibility matrix;
- seed batch inventory + lineage;
- third-person group captures;
- at least one bad/incompatible combination and factory response;
- retained tooling/templates that reduce repeated work;
- known source/wardrobe gaps.

## PASS

PASS when:

- relevant existing character/wardrobe pipelines were tested or explicitly dispositioned before equivalent custom tooling was built;
- 6+ distinct seed civilians are produced through one repeatable factory;
- B0 civilian-role demand has meaningful coverage;
- compatibility/adaptation is encoded rather than remembered ad hoc;
- routine generation does not require unexplained manual mesh/rig repair;
- common bad combinations are detected/rejected cheaply;
- output prefabs are animation-ready and reproducible;
- creating the next ordinary civilian from covered source families is mostly selection/production, not pipeline R&D.

## FAIL

FAIL if six characters are unrelated one-offs, B0 roles are ignored, wardrobe compatibility remains tribal knowledge, audited reusable techniques were skipped in favor of unexplained custom tooling, fantasy/source identity dominates final civilians, most variants need bespoke repair, or tooling effort expands into an unnecessary universal character system.

## Handoff

`WP-PROD-CHAR-02` must prove the factory at population-batch scale and expose clone/coherence/performance problems before CITY integration.

# WP-PROD-ANIM-01 — Animation Intake + Retarget Factory

Status: **PASS / ACCEPTED 2026-09-28**  
Class: PRODUCTION FACTORY / ANIMATION ASSETS  
Depends on: `WP-PROD-ASSET-00` PASS  
Blocks: `WP-PROD-ANIM-02`

Accepted implementation: PR #9, reviewed `PRODUCT_SHA` `4750aa8ee7ab200143fc938230a4131b78e0ec1d`, merged as `2e81c9e31e1803656fd986aacc21b184a99d5d2d`.

## Claim

juego-def has a repeatable animation asset factory that can discover, classify, import, retarget, validate and admit useful motion clips in batches. Adding another compatible animation should be routine intake, not a new manual experiment.

## Binding product demand

Consume [`../design/FIRST_KEEPER_BLOCK_B0.md`](../design/FIRST_KEEPER_BLOCK_B0.md). Prioritize the motion vocabulary needed by B0 rather than maximizing raw clip count.

Priority families:

- idle/walk/turn and useful run/chase support;
- talk/listen/point/react;
- wait/look/lean/sit/stand;
- carry/handle/shop/market/port work gestures;
- door/inspect/use/pickup where available;
- surprise/recoil and other light reaction motions where available.

## Binding research input — mandatory

Consume [`../research/EXISTING_ASSET_PIPELINE_RESEARCH.md`](../research/EXISTING_ASSET_PIPELINE_RESEARCH.md) before implementing custom import/retarget tooling.

Retain `Docs/evidence/WP-PROD-ANIM-01/REUSE_DECISIONS.md` covering at minimum:

1. actual Universal Animation Library/source corpus and shared-rig assumptions;
2. `QuaterniusUnityUtils` import automation on current Unity 6000.3.24f1;
3. Avelune shared animation-data/composition architecture as a reference;
4. `Animate-Rigged-Humanoid-No-Blender` as packaging/automation evidence where useful;
5. only missing metadata/preset/validation/runtime glue should be custom-built.

A candidate may be rejected. Equivalent custom tooling may not be written merely because the prior research was not consulted.

## Factory scope

Cover at least these semantic animation families:

1. locomotion;
2. conversation/acting;
3. ambient/social;
4. work/activity;
5. object interaction;
6. reactions/action;
7. special/minigame/combat — index now, solve later only if immediately useful.

## Required factory outputs

By PASS, retain:

1. `ANIM_FACTORY.md` — authoritative intake/retarget workflow;
2. `REUSE_DECISIONS.md`;
3. machine-readable semantic animation catalogue built on `PROD-ASSET-00`;
4. import/retarget presets or small batch tooling for covered source families;
5. root-motion/in-place/loop conventions;
6. avatar/rig compatibility rules;
7. automated or cheap validation for common import/retarget failures;
8. preview/runtime inspection path on a real humanoid;
9. non-trivial admitted clip batch;
10. `B0_MOTION_COVERAGE.md` mapping first-block needs to admitted clips or explicit gaps.

## Minimum batch proof

Process and classify at least **25 clips** across multiple semantic families when the owned/source corpus permits. If fewer lawful relevant clips are actually available, record the real corpus limit rather than manufacturing filler.

At least **12 clips** should reach `ADMIT`/production-usable status across several families unless the source gap is explicitly demonstrated. Raw count alone is not PASS; B0 usefulness and correctness matter.

## Catalogue fields

For each candidate/admitted clip support where relevant: stable local ID/path, source/provenance, semantic role/tags, rig/avatar expectation, humanoid/generic status, root-motion vs in-place, loop/non-loop, import preset/family, quality/status (`ADMIT`, `ADAPT`, `REJECT`, `GAP`), known foot-slide/orientation/scale/hand-object issues and compatible civilian/body family.

## Batch tooling expectation

The operator should be able to request things such as:

- "admit conversation gestures for B0 shop/witness interactions";
- "find ambient motions for Mercado/Muelle civilians";
- "retarget and validate market/port work gestures";
- "find locomotion/reaction clips usable for the B0 follow/chase route";

without hand-configuring every clip independently.

Prefer existing/adapted import rules, presets and batch mechanisms before custom processors. Add Editor scripts or metadata-driven tooling only where repeated setup remains.

## Validation baseline

Cheaply detect or surface where practical invalid avatar/rig mapping, wrong orientation/scale, loop/root-motion mismatch, severe foot sliding or pose deformation, unusable clip boundaries, missing source/provenance and duplicate/ambiguous admitted entries.

At least one bad/incompatible clip must be diagnosed and repaired or rejected through the factory path.

## Evidence

Retain under `Docs/evidence/WP-PROD-ANIM-01/`:

- `REUSE_DECISIONS.md`;
- `B0_MOTION_COVERAGE.md`;
- factory workflow;
- processed/admitted batch inventory;
- import/retarget presets/tooling retained;
- representative runtime/preview captures or observations;
- bad-case diagnosis/outcome;
- explicit coverage gap matrix by gameplay family.

## PASS

PASS when:

- relevant existing animation/import pipeline candidates were tested or explicitly dispositioned before equivalent custom tooling was built;
- a meaningful batch is processed through one repeatable intake/retarget path;
- 12+ useful admitted clips exist across several families when corpus permits;
- B0 motion needs have useful coverage or explicit gaps;
- semantic catalogue and compatibility rules make discovery routine;
- common source-family imports no longer need manual setup per clip;
- broken clips are cheaply surfaced and not silently accepted;
- adding another animation from a covered source family is mainly batch production work.

## FAIL

FAIL if the output is only a prose/file list, B0 motion demand is ignored, every clip needs bespoke import setup, existing relevant import/retarget solutions were ignored, retargeting is assumed rather than proven, or the WP expands into building all future combat/cinematic animation systems.

## Handoff

`WP-PROD-ANIM-02` consumes this accepted factory plus the accepted civilian factory to prove reusable runtime vocabulary and batch use across multiple NPCs.

# WP-PROD-ANIM-01 — Animation Intake + Retarget Factory

Status: **READY AFTER ASSET-00**  
Class: PRODUCTION FACTORY / ANIMATION ASSETS  
Depends on: `WP-PROD-ASSET-00` PASS  
Blocks: `WP-PROD-ANIM-02`

## Claim

juego-def has a repeatable animation asset factory that can discover, classify, import, retarget, validate and admit useful motion clips in batches. Adding another compatible animation should be routine intake, not a new manual experiment.

## Factory scope

Cover at least these semantic animation families:

1. locomotion — idle/walk/turn/jog-run where useful;
2. conversation/acting — talk/listen/point/react/neutral gestures;
3. ambient/social — wait/look/sit/stand/casual social motions;
4. work/activity — carry/use/handle/shop/market/port-style gestures;
5. object interaction — door/pickup/inspect/use where available;
6. reactions/action — surprise/hit/recoil/fall where available;
7. special/minigame/combat — index now, solve later only if immediately useful.

## Required factory outputs

By PASS, retain:

1. `ANIM_FACTORY.md` — authoritative intake/retarget workflow;
2. machine-readable semantic animation catalogue built on `PROD-ASSET-00`;
3. import/retarget presets or small batch tooling for covered source families;
4. root-motion/in-place/loop conventions;
5. avatar/rig compatibility rules;
6. automated or cheap validation for common import/retarget failures;
7. preview/runtime inspection path on a real humanoid;
8. non-trivial admitted clip batch.

## Minimum batch proof

Process and classify at least **25 clips** across multiple semantic families when the owned/source corpus permits. If fewer lawful relevant clips are actually available, record the real corpus limit rather than manufacturing filler.

At least **12 clips** should reach `ADMIT`/production-usable status across several families unless the source gap is explicitly demonstrated.

Raw count alone is not PASS; semantic usefulness and correctness matter.

## Catalogue fields

For each candidate/admitted clip support where relevant:

- stable local ID/path;
- source/provenance;
- semantic role/tags;
- rig/avatar expectation;
- humanoid/generic status;
- root-motion vs in-place;
- loop/non-loop;
- import preset/family;
- quality/status: `ADMIT`, `ADAPT`, `REJECT`, `GAP`;
- known foot-slide/orientation/scale/hand-object issues;
- compatible civilian/body family.

## Batch tooling expectation

The operator should be able to request things such as:

- "admit useful conversation gestures from this source family";
- "find looping ambient motions compatible with our civilian rig";
- "retarget and validate work/activity clips";

without hand-configuring every clip independently.

Use import presets, Editor scripts, batch processors or metadata-driven tooling where they remove repeated setup.

## Validation baseline

Cheaply detect or surface where practical:

- invalid avatar/rig mapping;
- wrong orientation/scale;
- loop/root-motion mismatch;
- severe foot sliding or pose deformation;
- unusable clip boundaries;
- missing source/provenance;
- duplicate/ambiguous admitted entries.

At least one bad/incompatible clip must be diagnosed and repaired or rejected through the factory path.

## Evidence

Retain under `Docs/evidence/WP-PROD-ANIM-01/`:

- factory workflow;
- processed/admitted batch inventory;
- import/retarget presets/tooling retained;
- representative runtime/preview captures or observations;
- bad-case diagnosis/outcome;
- explicit coverage gap matrix by gameplay family.

## PASS

PASS when:

- a meaningful batch is processed through one repeatable intake/retarget path;
- 12+ useful admitted clips exist across several families when corpus permits;
- semantic catalogue and compatibility rules make discovery routine;
- common source-family imports no longer need manual setup per clip;
- broken clips are cheaply surfaced and not silently accepted;
- adding another animation from a covered source family is mainly batch production work.

## FAIL

FAIL if the output is only a prose/file list, every clip needs bespoke import setup, retargeting is assumed rather than proven, or the WP expands into building all future combat/cinematic animation systems.

## Handoff

`WP-PROD-ANIM-02` consumes this factory plus the accepted civilian factory to prove reusable runtime vocabulary and batch use across multiple NPCs.

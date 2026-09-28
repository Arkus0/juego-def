# WP-PROD-ANIM-01 — Animation Intake + Coverage Truth

Status: **READY AFTER M0**  
Class: PRODUCTION FACTORY / ANIMATION INTAKE  
Depends on: `WP-M0-00` PASS  
Blocks: `WP-PROD-ANIM-02`

## Claim

juego-def knows what animation coverage it actually has, which clips are production-usable, how they should be imported/retargeted, and which important gaps remain. Raw clip count is not treated as coverage.

## Binding inputs

- Quaternius Production Knowledge
- current Unity/GC2 character baseline
- Production Authoring Decision
- `WP-PROD-CHAR-01` may run in parallel; ANIM-01 must avoid freezing a body-specific convention that conflicts with the accepted character rig.

## Coverage taxonomy

Inventory and classify available animation sources into at least:

1. locomotion — idle, walk, turn, jog/run only where useful;
2. conversation/acting — talk, listen, point, react, neutral gestures;
3. ambient/social — wait, look around, sit/stand if available, casual social motions;
4. work/activity — carry/use/handle/work gestures relevant to shops/market/port;
5. object interaction — doors, pickup/inspect/use where available;
6. reactions/action — surprise, hit/recoil/fall or equivalents if already owned;
7. special/minigame/combat — record but do not solve unless immediately useful.

## Required output

Create `ANIMATION_COVERAGE.md` or equivalent with, for each admitted family/clip:

- source/provenance;
- rig/avatar expectation;
- humanoid/generic status;
- root-motion vs in-place intent;
- loop/non-loop intent;
- rough gameplay role;
- import/retarget settings that matter;
- quality/status: `ADMIT`, `ADAPT`, `REJECT`, `GAP`;
- known foot slide, pose, orientation, scale or hand/object issues.

Also retain a small Unity validation scene or prefab setup showing representative clips on a real accepted/near-accepted humanoid character.

## Required representative proof

Validate at least:

- one idle;
- one walk;
- one conversation gesture;
- one ambient/social motion;
- one work/object/reaction clip if available.

At least **one bad or incompatible clip/import** must be diagnosed and either repaired or explicitly rejected. This prevents silent acceptance of broken retargeting.

## Operator loop

`inspect animation corpus -> classify -> import/retarget representative clips -> play/preview/runtime inspect -> diagnose defects -> repair/reject -> record convention`

Use automated inspection/batch settings where useful, but visual motion judgment must occur on a real character.

## Evidence

Retain under `Docs/evidence/WP-PROD-ANIM-01/`:

- coverage matrix;
- representative clip/prefab paths;
- captures/video-equivalent frame series or runtime observations sufficient to judge representative motions;
- bad-import diagnosis and outcome;
- explicit gap list ranked by near-term gameplay importance.

## PASS

PASS when:

- animation sources are classified by gameplay role rather than raw count;
- representative locomotion + acting + ambient coverage works on a real humanoid;
- import/retarget conventions are explicit;
- one bad case is repaired/rejected transparently;
- near-term gaps are known;
- no major uncertainty remains about how clips enter the project.

## FAIL

FAIL if:

- the result is merely a file list;
- retargeting is assumed without runtime/preview proof;
- broken clips are hidden;
- the WP expands into building every future animation or full combat vocabulary.

## Non-goals

No final state machine, no complete combat set, no procedural animation framework, no final facial animation and no requirement to fill every gap in this WP.

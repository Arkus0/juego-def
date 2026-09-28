# WP-PROD-ANIM-02 — Runtime Animation Vocabulary + Batch Proof

Status: **READY AFTER ANIM-01 + CHAR-01**  
Class: PRODUCTION SCALE PROOF / RUNTIME ANIMATION  
Depends on: `WP-PROD-ANIM-01` PASS + `WP-PROD-CHAR-01` PASS  
Blocks: `WP-CITY-URBAN-01`

## Claim

The animation factory is not only an intake catalogue: admitted motions can be applied at runtime across many civilian prefabs through a small reusable vocabulary, without per-NPC Animator surgery.

## Required runtime vocabulary

Provide reusable mappings for at least:

- locomotion baseline inherited from GC2 character setup;
- neutral idle/ambient variation;
- conversation `talk/listen/gesture` presentation;
- one reaction family;
- one work/object/activity family where admitted coverage exists.

The mapping may use GC2 Instructions/Actions, Animator/StateMachine assets, small local adapters, or a combination. Choose the simplest reusable path.

## Batch proof

Use at least **6 different accepted civilian variants** from CHAR-01/CHAR-02 as available and exercise the shared vocabulary in one or more Play Mode fixtures.

Demonstrate:

1. all selected civilians can use shared idle/ambient behavior without per-character graph duplication;
2. at least 4 can perform conversation gestures/listen/talk transitions;
3. at least 3 can perform one reaction or work/activity motion;
4. changing an admitted clip or semantic mapping can update multiple NPCs without rewiring each prefab;
5. at least one retarget/runtime edge case is repaired/rejected transparently.

## Production interface

The desired factory interface is semantic, e.g.:

- `AMBIENT_IDLE`;
- `TALK_NEUTRAL`;
- `LISTEN_NEUTRAL`;
- `GESTURE_POINT`;
- `REACTION_SURPRISED`;
- `WORK_CARRY` / another admitted work role.

Exact implementation may differ, but downstream scene/NPC work should request a production role rather than know arbitrary clip paths.

## GC2 boundary

Prefer GC2-native animation/presentation surfaces when they simplify invocation. A tiny local adapter is acceptable where necessary. Do not introduce a second general gameplay framework.

## Validation

Cheaply surface:

- missing semantic mapping;
- invalid/unsupported avatar;
- missing Animator/runtime dependency;
- obvious transition lock/stuck pose;
- failed return to locomotion/idle;
- clip incompatible with one civilian family.

## Evidence

Retain under `Docs/evidence/WP-PROD-ANIM-02/`:

- semantic runtime vocabulary/mapping;
- fixture paths;
- batch proof on 6+ civilians;
- shared-update/replacement proof;
- edge-case record;
- known deferred gameplay-specific gaps.

## PASS

PASS when:

- shared vocabulary works across 6+ civilians without bespoke graph setup;
- ordinary conversation/ambient/reaction-or-work needs are reusable;
- semantic mapping hides raw clip-path plumbing from scene authors;
- replacing/extending an admitted motion is a factory operation rather than NPC-by-NPC surgery;
- no systemic transition/retarget blocker remains for ordinary NPC production;
- adding more ambient/conversation/work animation breadth is now mainly content production.

## FAIL

FAIL if each NPC needs bespoke Animator logic, semantic roles cannot be reused, runtime transitions are fragile, or the factory intake does not translate into scalable scene use.

## Non-goals

No combat animation graph, cinematic sequencer, facial animation lock, root-motion chase system or complete future activity library.

# WP-PROD-ANIM-02 — Runtime Animation Vocabulary

Status: **READY AFTER ANIM-01 + CHAR-01**  
Class: PRODUCTION FACTORY / RUNTIME ANIMATION  
Depends on: `WP-PROD-ANIM-01` PASS + `WP-PROD-CHAR-01` PASS  
Blocks: `WP-CITY-URBAN-01`

## Claim

The admitted animation corpus can be invoked reliably on real juego-def civilians through a small reusable GC2/Unity presentation vocabulary rather than bespoke wiring for every NPC and scene.

## Required runtime vocabulary

Provide reusable mappings for at least:

- locomotion baseline inherited from GC2 character setup;
- neutral idle/ambient variation;
- conversation `talk/listen/gesture` presentation;
- one reaction;
- one work/object/activity animation where admitted coverage exists.

The mapping may be GC2 instructions/actions, Animator/StateMachine setup, small local adapters, or a combination. Choose the simplest solution that remains understandable and reusable.

## Required proof

Use at least **two different accepted civilian variants** from CHAR-01.

Demonstrate in Play Mode:

1. both can use the shared runtime vocabulary without character-specific rewiring;
2. one NPC can transition from idle/ambient -> interaction/conversation gesture -> back to idle;
3. one additional action/reaction/work animation can be triggered intentionally;
4. a bad retarget/runtime edge case is either repaired or rejected, not hidden.

## GC2 boundary

Prefer native GC2 character/animation surfaces when they make the mapping simpler. Do not introduce a second generalized gameplay framework for animation.

A tiny local adapter is acceptable where GC2 does not cleanly expose a needed reusable call. Keep it narrow and replaceable.

## Operator loop

`inspect accepted characters/clips -> wire shared vocabulary -> Play Mode trigger -> observe transitions/console/pose -> correct -> repeat on second character`

## Evidence

Retain under `Docs/evidence/WP-PROD-ANIM-02/`:

- vocabulary/mapping description;
- paths to reusable assets/components/instructions;
- Play Mode proof on two civilian variants;
- bad-edge-case record;
- known gaps deferred to later gameplay-specific work.

## PASS

PASS when:

- the same small presentation vocabulary works on 2+ civilians;
- conversation gesture and return-to-idle are reusable;
- at least one extra activity/reaction works;
- no severe transition/retarget issue remains for these ordinary NPC uses;
- extending the vocabulary with another admitted clip does not require redesigning the system.

## FAIL

FAIL if every NPC needs bespoke Animator logic, accepted clips cannot be triggered reliably at runtime, or a large custom animation framework is built before a small shared vocabulary proves insufficient.

## Non-goals

No combat animation graph, cinematic sequencer, facial animation lock, root-motion chase system or complete activity library.

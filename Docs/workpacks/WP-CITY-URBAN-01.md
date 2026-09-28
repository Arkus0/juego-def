# WP-CITY-URBAN-01 — First Keeper Block from Production Factories

Status: **READY AFTER FACTORY BATCH PROOFS**  
Class: PRODUCT INTEGRATION / URBAN BLOCK  
Depends on: `WP-M0-00` PASS + `WP-PROD-ENV-02` PASS + `WP-PROD-CHAR-02` PASS + `WP-PROD-ANIM-02` PASS + `WP-PROD-UI-01` PASS  
Blocks: `WP-PROD-LOOK-GATE`

## Claim

juego-def can integrate the accepted graphical/content factories into one small keeper urban block that feels like the actual game. The block must be produced **from the factories**, not by bypassing them with one-off hand work.

M0 is required here only because it freezes the basic player/camera/interaction integration fixture before the keeper block consumes the graphical factories. It is not a prerequisite for building those factories.

## Recommended context

Default target: compact **Mercado–Muelle seam** or equivalent commercial-to-working-port transition supporting pedestrian exploration, service frontage, working-port cues, civilian variety and investigation interaction.

Exact geometry is a fresh juego-def design decision. Do not resurrect old Juego2 CITY node/edge contracts by default.

## Required block composition

At minimum:

1. one walkable route with a meaningful destination/turn/termination;
2. several coherent building/frontage outputs from ENV factory;
3. at least one enterable or deeply readable threshold/interior edge;
4. one strong port-town landmark/cue;
5. **8+** generated civilians present in the block;
6. several NPCs consuming shared ambient/conversation/work animation vocabulary;
7. one investigation-style dialogue using accepted Dialogue/UI factory;
8. one additional world interaction/examinable;
9. enough prop/signage/material/lighting treatment to judge the block as retained game content.

## Factory integrity rule

If integration exposes a systemic problem, repair/reopen the owning factory instead of hiding it locally:

- environment composition/kit issue -> ENV;
- character generation/clone/clipping issue -> CHAR;
- runtime animation/retarget issue -> ANIM;
- dialogue authoring/UI reuse issue -> DIALOGUE/UI.

Block-specific exceptions are allowed only when genuinely local and documented.

## Playability + product proof

Required:

- owner third-person walk-through;
- automated route/collision probe;
- NPC/world interaction in the actual block;
- no blocking runtime errors;
- gameplay captures from multiple relevant views;
- owner verdict that the block is worth **keeping and extending**, not discarding as a pipeline demo.

## Production evidence

Record which assets were generated/selected through each factory and whether integration required:

- exact-path owner hints;
- manual low-level fixes;
- new one-off tooling;
- factory extensions.

The desired result is that most work is selection/composition/content authoring, not foundational pipeline repair.

## PASS

PASS when:

- the block looks and plays like a credible early piece of the intended game;
- environment, civilian, animation and UI outputs all come through accepted factories;
- 8+ civilians coexist without obvious systemic clone/rig/material failures;
- investigation/world interactions work in Play Mode;
- route/collision validation passes or real defects are corrected;
- owner accepts the block as keeper content;
- no foundational factory blocker remains hidden behind block-specific fixes.

## FAIL

FAIL if the block only works by bypassing factories, still looks like dressed greybox, integration reveals unresolved systemic lane failures, or it becomes a one-off showcase that cannot seed the next district/content block.

## Non-goals

No full district, full living-world schedule system, final population count, combat or complete story slice.

# Roadmap jugable

Status: **BOOTSTRAP DONE / NEXT: M0 FIRST STREET** — authoring path `BOUNDED_OPERATOR` (MCP for Unity), owner-confirmed

## Immediate sequence

1. ~~**Knowledge migration**~~ — done (PR #1).
2. ~~**Production authoring decision**~~ — `BOUNDED_OPERATOR` (MCP for Unity) adopted by the owner on 2026-09-28 without waiting for Juego2 `WP-AI-UNITY-AUTHORING-00`; compared against Juego2's H0/H1 evidence. See [`PRODUCTION_AUTHORING_DECISION.md`](../architecture/PRODUCTION_AUTHORING_DECISION.md).
3. ~~**Bootstrap Unity + GC2 Core**~~ — done: Unity 6000.3.24f1 + URP 17.3 + GC2 Core 2.19.61, player/camera walking in Play Mode. See [`UNITY_PROJECT_SETUP.md`](../production/UNITY_PROJECT_SETUP.md) and [evidence](../evidence/BOOTSTRAP-UNITY-GC2/README.md).
4. **M0 — GC2 Walking Street** — player, camera, first street, one object/hotspot and one NPC interaction. **← next**
5. **Production lanes** — prove ENV / CHAR / ANIM / Dialogue-UI repeatability on the real port-town look.
6. **First Living Block** — routine-bearing small block with investigation value.
7. **Action/content** — chase, melee/confrontation, activities/jobs and 20–30 minute slice.
8. **Expansion** — additional neighbourhoods and population breadth.

The authoring benchmark is deliberately consumed **before** we invest heavily in a competing environment/character tooling architecture. A minimal bootstrap may happen earlier if useful; a large custom production framework should not.

## M0 and gameplay path

Each gameplay step produces a visible retained feature. Paid modules are acquired only if not already owned and only when the real feature justifies them.

| Step | Visible objective | Default tech | Keeper output | Observable PASS |
|---|---|---|---|---|
| Bootstrap Unity ✅ | Project opens, scene plays, real versions/pipeline recorded | Unity | minimal project | Open/Play without blocking errors. |
| GC2 Core ✅ | third-person player + camera | Core | player/camera | Walk, turn and follow in Play Mode. |
| First Street | short dense port-town street at human scale | chosen authoring path + Unity | retained street seed | Walkable/readable route with credible composition. |
| First Interaction | door/hotspot + examinable object | Core | interactions | Approach/activate with different visible results. |
| First NPC | recognizable person with brief response/gesture | Core | NPC interaction | Activate interaction in the same street. **Closes M0.** |
| Dialogue | ask about person/photo/place | Dialogue if justified; otherwise Core/local | contextual conversation | Known fact changes response. |
| First Investigation Loop | contrast testimony + physical clue | Core + chosen dialogue path | clue loop | Player reaches lead through world references, not mandatory waypoint chain. |
| Inventory / Quests | carry a needed object / represent a thread only when required | modules only if proven useful | persistent object/thread | Acquire/use/load state successfully. |
| Behavior | first useful schedule/routine | Behavior if justified + Unity navigation | routine with gameplay value | Return at another time and find a meaningful changed state/location. |
| First Living Block | street + commerce + a few coherent NPC routines | GC2 + production lanes | retained lived-in block | Morning/evening visit yields different opportunity/context. |
| Melee | brief sparring/fight with purpose | Melee if adopted | retained encounter | Start, play, finish, receive coherent consequence. |
| First Chase | suspect route through market/alley/port | Core/Behavior; Perception only if needed | retained chase | Can catch or lose suspect without dead-ending investigation. |
| 20–30 minute slice | investigation -> daily life -> chase/confrontation -> changed return | modules actually proven useful | complete slice | First-play timed run works end to end. |
| Expansion | additional neighbourhood/content | proven stack | incremental retained content | each increment adds a playable route/activity/person. |

## Production lock before broad expansion

The old Juego2 insight remains valuable: one attractive demo is not enough. Before scaling to many districts/NPCs, juego-def should pass the lightweight `PROD-LOOK-GATE` described in [`POST_FOUNDATION_PRODUCTION_WPS.md`](POST_FOUNDATION_PRODUCTION_WPS.md).

This gate asks whether we can repeatedly produce the game, not whether we reproduced old infrastructure.

## M0 — GC2 Walking Street

**Limit:** Unity opens; GC2 Core works; third-person player/camera; one short port-town street; one door/hotspot; one examinable object; one NPC; real GC2 interaction. Arkus absent. Dialogue/Inventory/Quests/Behavior/Melee/Perception are not M0 requirements.

**PASS:** the player can open the project, walk the street, approach an NPC/object and interact in Play Mode.

The street should already respect the migrated Visual Bible enough to avoid proving gameplay inside an obviously misleading cube test, but M0 does not require final art breadth.

## Tooling boundary

The pause on production is lifted by the authoring decision: M0 and the production lanes proceed with the MCP operator.

- **default:** operator + GC2 native + briefs/recipes + small validations;
- **still defer:** bespoke scenario generators, large character factories, H1-style lifecycle infrastructure, or other heavy tooling, until the operator's revisit trigger (after `PROD-ENV-01`) shows a concrete gap it cannot close.

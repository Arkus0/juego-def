# NPC depth tiers — juego-def planning rule

Status: **MIGRATED PRODUCT DIRECTION**

These are planning ranges for the eventual dense port-town product, not current performance gates or promises. Routine depth, visual uniqueness, narrative importance and persistent systemic depth are separate budgets.

| Tier | Typical final planning range | Gameplay obligation | Persistent/systemic cost |
| --- | ---: | --- | --- |
| **A — MAIN / SYSTEMIC** | ~10–15 named leads | Multi-state character, authored history, relevant relationships/knowledge/memory, readable routine and consequences across scenes/days | Stable individual identity and durable facts required by gameplay; save/revisit continuity |
| **B — INTERACTIVE / REACTIVE** | ~20–40 named/recurring characters | Shop, work, investigation, contextual dialogue and useful local routine; selective memories/relations only where later encounters need them | Persist only consequential individual facts; immediate behaviour/presentation may remain GC2/local |
| **C — POPULATION / AMBIENT** | remainder of an initial ~80–120 visible/recurring people | Believable occupancy, motion and immediate response using reusable variants; many may carry lightweight routines | No permanent bespoke biography by default; retain only identity/schedule anchor when continuity actually needs it |

## Routine depth is a separate axis

A daily routine is **not** Tier-A depth.

The product may eventually target roughly **60–100 routine-bearing NPCs across the whole town** while keeping only ~10–15 deeply systemic A actors. B/C actors may use reusable schedule templates such as:

`home -> job/POI -> meal/social/leisure -> home`

with day/time variation and bounded authored exceptions, without receiving bespoke memory graphs, relationships, quests or animation controllers.

The ~80–120 range includes A and B. These are different budgets:

- visible people at once;
- routine-bearing identities;
- visually unique variants/models;
- named recurring characters;
- deeply systemic actors;
- runtime-active GameObjects.

Do not conflate them.

## Active-area realization

Only the current neighbourhood/block and continuity seam needed by the player must pay full graphical/runtime realization cost: GameObjects, Animator, navigation, look-at, GC2 immediate behaviour and interaction.

Off-screen people may advance through a cheaper schedule/state representation once such continuity becomes a real implemented requirement. Exact off-screen architecture is deferred.

If the player follows a relevant actor through a visible seam, continuity should be preserved. Unloading an area must not erase a consequential authored outcome or make a recurring NPC become a different person.

## Promotion rule

Promote a B/C actor's **persistent depth** only when a concrete encounter/system needs individual continuity, memory, relationships, knowledge or cross-system consequences.

A Tier-A actor can still use GC2/local modules for immediate movement, dialogue or combat. The tier describes depth of **meaning**, not which Unity component moves the character.

## B0 implication

A representative keeper block should combine:

- at least one A-grade or future-A witness/lead where systemic depth is useful;
- several B-grade shop/work/investigation people;
- enough C-grade locals/pedestrians to read as inhabited.

Character factory output should therefore optimize reusable visual/routine variation for B/C scale while allowing selected promotion to A without rebuilding the whole character from scratch.

## Living World compatibility

This tiering composes with `Docs/research/living-world/LIVING_WORLD_KNOWLEDGE.md`:

- `PersistentActor` is a cost/meaning boundary, not a requirement that every named person use every PA system;
- `AmbientPopulation` does not automatically receive individual memory/belief/social-history state;
- routine-bearing is cheaper and more common than deep autonomous/social causality;
- store only deviations/consequences the player can meaningfully encounter again.

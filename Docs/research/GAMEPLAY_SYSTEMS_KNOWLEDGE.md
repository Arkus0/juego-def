# Gameplay systems knowledge migrated from Juego2

Status: **MIGRATED RESEARCH / FUTURE IMPLEMENTATION INPUT**

This document preserves high-value gameplay/system semantics that are independent of H0/H1. It is not a mandate to build infrastructure before a concrete gameplay WP needs it.

## 1. Object interaction — touchable world without universal simulation

Preserve three cost/meaning classes:

### WORLD PROP

Immediate local physical affordance: doors, shutters, chairs, drawers, switches, movable clutter, etc.

Unity/GC2 may own immediate interaction/animation/physics. Persistence is not required merely because the object can be touched.

### PORTABLE ITEM

An object the player can take/use/show/give/drop/transfer. Inventory 2 remains a candidate accelerator only when a real portable-item loop justifies it. A traditional RPG inventory UI is not required.

### CONSEQUENTIAL OBJECT

A particular instance/outcome the world must remember because later gameplay depends on it: murder evidence moved, unique key stolen, tool left elsewhere, package misdelivered, meaningful object broken/removed, etc.

The chosen gameplay/save owner must retain the durable semantic consequence. Plugin-private IDs must not become the only game meaning.

**Rule:** physical manipulability, portability and persistent systemic meaning are separate costs.

## 2. GameFlow is ownership before cinematics

Dialogue, cinematics, QTE-like sequences, combat and autonomous NPC behaviour compete for player/camera/actor control.

Preserve future invariants:

- one effective player-control owner at a time;
- one effective camera/director owner at a time;
- one actor should not simultaneously run incompatible schedule/autonomous/combat/cinematic control;
- transitions have acquire/enter, active state and release/exit or rollback;
- skip/cancel/failure/load/recovery cannot strand ownership;
- after directed control ends, Living World state is re-evaluated rather than blindly resuming stale execution;
- Timeline/Animator/Camera are presentation executors, not narrative/world-state authority.

Do not build a GameFlow framework until actual dialogue/chase/combat/cinematic integration makes this collision real.

## 3. Reusable explainable conditions

When multiple systems need the same semantic predicate, prefer one understandable condition vocabulary/adapter rather than private dialects per subsystem.

Useful future target:

```text
Evaluate(condition, read-only context) -> true/false/error
Explain(condition, read-only context) -> per-leaf trace + referenced state
Validate(condition) -> authoring diagnostics
```

Conditions read state; they do not become a second mutable truth store. An evaluated result is not automatically persisted as truth.

With GC2, prefer native Conditions where they remain clear and adequate. Introduce a local abstraction only when repeated cross-system semantics justify it.

## 4. Structured outcomes are integration seams

A meaningful action should expose enough structured outcome for legitimate downstream owners to react without reaching into each other's private state.

Examples:

- interaction moved/broke/transferred an object;
- activity completed/cancelled/won/lost;
- combat/QTE/cinematic caused an injury, escape, promise, access change or witnessed act;
- governance changed an institutional condition.

This is **not** a requirement for event sourcing everything. Keep outcomes as small as the actual cross-system seam.

Downstream systems should consume consequences through their own ownership rather than a sequence directly editing relationship/belief/memory fields ad hoc.

## 5. Persistent actor versus ambient population

Preserve the scale distinction from PA/Juego harvest:

- persistent actors earn stable identity and deeper continuity because gameplay needs it;
- ambient population supplies density/presence/cheap interaction and should not receive full social biography by default;
- promotion is explicit when a formerly ambient person becomes narratively/systemically important.

This prevents “100 visible NPCs” from accidentally becoming “100 full social simulations”.

## 6. Schedule is expectation, not screenplay

Schedules express time windows, activity intent and semantic destination/opportunity needs. Navigation owns route realization; activities own their internal execution; interruptions/events can override normal expectations.

Debug/authoring should be able to answer:

- what was this actor expected to do?
- what actually happened?
- why do they differ?

Crossing midnight, place capacity and interruption/recovery are real edge cases; exact path choreography is not schedule authority.

## 7. FULL / ABSTRACT continuity

Streaming/off-screen simulation may lower presentation fidelity and skip hidden microsteps. It may not silently change identity or meaningful causal state.

A committed goal, possession, important belief/relationship/memory state or consequential outcome must survive fidelity transitions without duplicate actors or magical reset.

Implement this only when off-screen persistence becomes a real current requirement; until then, keep the invariant as a design constraint rather than architecture.

## 8. Research/prior-art workflow

Before creating generic systems or tooling:

```text
concrete product question
 -> inspect existing candidate/prior art
 -> verify exact source/version/license if adoption is plausible
 -> extract mechanism/edge case/behavioural spec
 -> decide USE / ADAPT / BENCHMARK / REJECT / NOT_MATERIAL / DEFER
 -> encode value in the smallest juego-def contract/fixture/tool needed now
```

Prior art answers questions. It does not choose our architecture by prestige or feature count.

## 9. Fixture bank worth preserving

Future WPs should consider these failure shapes when relevant:

- player/camera/actor double authority during dialogue/cinematic/combat transitions;
- an actor “knows” debug/world truth they never acquired;
- a receiver's response is secretly chosen by the initiator;
- hidden rumour lineage leaks into actor corroboration;
- routine deviation rewrites the expected schedule to hide the discrepancy;
- local decisions scan all actors before narrowing candidates;
- repeated memories/events create unbounded biography/cascade growth;
- FULL↔ABSTRACT transition duplicates/erases meaningful state;
- a minigame has no relationship to ordinary town opportunity or aftermath;
- a player action uses quest-only flags while equivalent NPC action uses systemic state;
- policy directly sets citizen opinion/action rather than changing conditions;
- investigation UI reveals causal truth the player never legitimately obtained;
- a factory/batch pipeline works only because one hand-curated sample was special-cased.

## 10. Source provenance

Primary Juego2 sources retained as historical evidence/reference:

- `Docs/reference/JUEGO_KNOWLEDGE_LEDGER.md`
- `Docs/product/IMMERSIVE_OBJECT_INTERACTION_SCOPE.md`
- `Docs/research/living-world/results/PA-01.md` ... `PA-13.md`
- old Gameplay/GameFlow/Living World donor materials cited by that ledger

The old runtime/WorldState/DFU/Shenmue implementation wrappers do not travel.

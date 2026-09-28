# Game Creator 2 Hub reuse knowledge

Status: **MIGRATED DISCOVERY KNOWLEDGE / NO EXTENSION ADOPTED**  
Source snapshot: Juego2 audit observed 2026-09-28.

## Executive conclusion

The Game Creator Hub is useful as a **library of small reusable source extensions and authoring shortcuts**, not as a ready-made living-city framework.

The prior audit observed 643 distinct name/version cards, opened 77 relevant sources and classified the inspected set as 9 USE, 7 ADAPT, 37 WATCH, 9 IGNORE and 15 REJECT. Those labels are discovery input, not installation authority.

The practical rule for juego-def is:

> **GC2 native -> Hub candidate -> adapt source -> custom code**

for every feature that would otherwise trigger new glue/tooling.

## High-value Core findings

### Run Actions with Args

Adds reusable `Self` / `Target` context to Actions execution. Strong authoring value for shared interactions among witnesses, objects, NPCs and player. Re-check exact version/source before use.

### For Each in Radius

Useful authoring idea for spatial actions, but the audited implementation had fixed buffers/static collections and reentrancy concerns. **Adapt the idea**, do not blindly import it.

### Preload Scene / Activate Preloaded Scene

Potentially useful for controlled transitions, but the audited source used a single static async operation and is not a general multi-scene streaming solution.

### Wander Preferred Paths / Move to Random Marker

Useful bounded navigation helpers for readable routines. They are not schedules, memory or off-screen simulation.

## Dialogue finding

`Build Dialogue From Text` showed strong potential for turning indented text/options into Dialogue nodes, but the audited source depended on Dialogue plus an unresolved `Game.DialogueActors` namespace and used editor/reflection behavior. Treat the **workflow idea** as valuable; do not treat the specific extension as production-ready until dependencies, license and current-version behavior are resolved.

This is especially relevant because juego-def has a writer: fast text-to-dialogue authoring could materially reduce implementation friction once the dialogue runtime choice is made.

## Module-specific findings

- **Dialogue:** Hub adds useful authoring wrappers/import ideas, but product presentation remains the primary reason to adopt Dialogue.
- **Perception:** wrappers can help with bounded reactions; the module itself is more important than Hub glue.
- **Behavior:** Hub offered limited leverage; adopt Behavior only if real NPC routine/decision cases justify it.
- **Inventory:** merchant/bag events may save glue once Inventory is actually needed.
- **Quests:** lifecycle/task events may help once a real quest representation is justified.
- Third-party extensions do **not** justify bringing their dependencies in by themselves.

## Explicit non-solutions from the audit

The Hub did **not** provide a proven turnkey solution for:

- whole-town NPC schedules;
- off-screen simulation;
- persistent NPC identity/state across districts;
- robust crowd management;
- a complete Shenmue-like living world.

Do not mistake wrappers for architecture.

## Rejected patterns worth remembering

- Device-clock triggers (`DateTime.Now`) are not a game-world schedule system.
- Untested per-frame visibility/pooling scripts are not a persistence/residency solution.
- High tool count or a convenient title is not evidence of compatibility or quality.

## Adoption checklist

Before an extension becomes retained production input:

1. inspect exact current source/version;
2. verify license and dependencies;
3. compare against native GC2 solution;
4. run the real gameplay/authoring case in current Unity/GC2;
5. measure whether it actually reduces repeated work;
6. prefer copying/adapting a small lawful source idea over adopting a larger dependency when appropriate;
7. keep source ownership and upgrade/replacement path clear.

## Raw-source provenance

The full source audit remains archived in `Arkus0/Juego2`:

- `Docs/discovery/GC2_HUB_REUSE_AUDIT.md`
- `Docs/discovery/GC2_HUB_EXTENSION_CATALOG.csv`
- `Docs/discovery/GC2_HUB_COVERAGE_INVENTORY.csv`

juego-def intentionally migrates the **decision-useful knowledge**, not the old repository's governance or H1/H2F requirements. The raw catalog can be resnapshotted into this repo later if it becomes operationally useful.

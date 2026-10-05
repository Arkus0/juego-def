# WP-SEMANTIC-EDIT-HONDA-00 — local prop move

Status: **EXPERIMENT / NOT A FACTORY**
Base: `worker/env01-authored` @ `09f89c79`
Does not authorize rebuild, Director expansion, or any Juego2 import.

## Question

Can an editor operation move one prop in the authored ENV01 scene without changing any other object's hierarchy, source, or transform?

## Fixture

Scene: `Unity/JuegoDef/Assets/JuegoDef/Scenes/ENV/ENV01_AUTHORED.unity`
Edit mode only. Do not enter Play.
Universe: saved objects in that scene, excluding the resolved target.

## Operation

`Experiments/SemanticEditHonda01/operation.json`

1. Resolve exactly one object whose name contains `nameContains`.
2. Move it by `offset`.
3. Its renderer bounds must not intersect `passageAabb`.
4. Nothing else may change.

If zero or many objects match, FAIL. Do not guess.

## PASS

- target transform changed
- `passageClear` true
- `preservationHashBefore` == `preservationHashAfter`
- `unintendedChanges` == 0
- no new objects, no missing objects, no duplicate paths
- scene was not rebuilt

Screenshot is human evidence. It does not decide PASS.

## Out of scope

Openings, frontage, street width, NPCs, lighting, H1, DesignWorld.

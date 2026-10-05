# WP-SEMANTIC-EDIT-HONDA-01 — set back one entrance

Status: **EXPERIMENT / RUN ONLY AFTER HONDA-00 PASS**
Base: `experiment/semantic-edit-honda-01`
Does not authorize a street widen, a new opening, a district rebuild, or a Juego2 import.

## Question

After a prop move preserved the scene, can one entrance be set back without changing the locked bakery or any other saved object?

## Fixture

Same scene, Edit mode: `Assets/JuegoDef/Scenes/ENV/ENV01_AUTHORED.unity`.
Universe: saved scene objects except the resolved entrance.

## Operation

`Experiments/SemanticEditHonda02/operation.json`

1. Resolve exactly one entrance whose name contains `targetNameContains`.
2. Resolve exactly one locked bakery whose name contains `lockedNameContains`.
3. Refuse if the entrance is the bakery, or a child of it.
4. Move the entrance by `localOffset` in its local space. Default is a 0.4 m setback along -Z.
5. The bakery transform, source and hierarchy path must be unchanged. So must every other non-target object.

Zero or many matches: FAIL. Do not guess. Do not invent ENTRANCE_01 before the run. If the operator has to record a host facade to avoid touching the bakery, write that name in `notes.md` after the run. Do not add the field before it is needed.

## PASS

- Honda-00 result.json is PASS
- entrance transform changed
- locked bakery path still exists and its row is identical
- preservationHashBefore == preservationHashAfter
- unintendedChanges == 0
- no rebuild

Screenshot does not decide PASS.

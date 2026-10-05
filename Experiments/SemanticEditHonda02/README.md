# SemanticEditHonda02

Run this only after `Experiments/SemanticEditHonda01/result.json` says PASS and that scene save is the one you have open.

1. Edit mode. `ENV01_AUTHORED`.
2. Menu `JuegoDef/Semantic Edit Honda/02 Snapshot`.
3. If several doors match, set `targetNameContains` to the exact object that is the entrance you mean. It must not be the bakery and must not be parented under it.
4. Confirm `lockedNameContains` resolves one bakery. If the scene uses another name, change the token. Do not unlock it.
5. Menu `JuegoDef/Semantic Edit Honda/02 Apply`.
6. Read `result.json`. Save the scene only on PASS.

`localOffset` is in the entrance's local space. `[0, 0, -0.4]` pulls it 40 cm along its own -Z. Change it only if that axis pushes the door out of the facade instead of back into it. Record the final vector.

If you cannot name the entrance without also naming its facade or building, write that in `notes.md` after the attempt. Do not add those fields to the operation beforehand.

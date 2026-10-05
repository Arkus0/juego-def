# SemanticEditHonda01

One move. No rebuild.

1. Open `ENV01_AUTHORED` in Edit mode.
2. Menu `JuegoDef/Semantic Edit Honda/1 Snapshot`.
3. If `before.json` resolved a container that is not the one blocking the walk, set `nameContains` to that object's name and snapshot again.
4. Set `offset` and `passageAabb` in `operation.json`. The passage box is world space. The prop must end outside it.
5. Menu `JuegoDef/Semantic Edit Honda/2 Apply`.
6. Read `result.json`. Do not save the scene unless `result` is `PASS`.

The hash covers scene objects except the target: hierarchy path, prefab asset path, local position/rotation/scale. Player, rig, and Play Mode dirt are out because this runs in Edit mode on the saved scene.

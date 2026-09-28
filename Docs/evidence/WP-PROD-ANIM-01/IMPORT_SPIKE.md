# Existing importer spike

2026-09-28, isolated clean project on baseline main, Unity **6000.3.24f1**.

Restored UAL1, UAL2, Base Characters using ASSET-00 intake and GC2 using the existing provisioning script. Ran the already retained `JDAssetIntakeApplyUAL.Run` in batch mode before implementing animation preset glue.

Observed (Unity process exited 0; no C# compilation errors):

```text
JD_UAL_IMPORTED Assets/ThirdParty/Quaternius/UAL1/UAL1.fbx clips=120 loops=54
JD_UAL_IMPORTED Assets/ThirdParty/Quaternius/UAL2/UAL2.fbx clips=134 loops=47
```

The utility sets Humanoid import, baked axis conversion, `Rig/root` and loop flags by the `Loop` suffix. Its result compiles and imports in the required Unity version. It does not establish target-body compatibility, semantic admission, foot contact, or gameplay appropriateness.

Decision: reuse this utility, then add only policy corrections and validation. One semantic exception is already evident in the source inventory: UAL2 `Idle_No_Loop` is a head-shake/no gesture, not automatically a repeated idle simply because its name ends in `Loop`; its looping behavior must be evaluated explicitly. Root transform baking and regular body Humanoid setup are also outside the utility's current scope.

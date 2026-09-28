# Unity intake validation — 6000.3.24f1

The isolated worktree restored GC2 Core 2.19.61 locally, installed all seven catalogued Quaternius families, opened the real `Unity/JuegoDef` project in batch mode, and compiled the included Editor tools without C# errors. Vendor and licensed source bytes stayed ignored; the vault was untouched.

## Utility spike and retained import step

In a disposable Unity 6000.3.24f1 project, QuaterniusUnityUtils commit `62a4f8e790330e089488a6bd66df2734c28a8796`:

- created `Balcony_Cross_Straight_WithCollisions.prefab` with **one MeshCollider** from the matching vendor model/collision FBX pair;
- configured owner's UAL1 FBX as **Humanoid**, baked axis conversion, `Rig/root` motion node, **120 clips / 54 loops**.

After pinning that utility and its Unlicense in the project, `JDAssetIntakeApplyUAL.Run` applied the same import step to the real ignored intake copies:

```text
JD_UAL_IMPORTED Assets/ThirdParty/Quaternius/UAL1/UAL1.fbx clips=120 loops=54
JD_UAL_IMPORTED Assets/ThirdParty/Quaternius/UAL2/UAL2.fbx clips=134 loops=47
```

The wrapper does not reimplement Quaternius's importer; it selects both installed FBX files, calls it and forces reimport. ANIM-01 still owns visual retargeting/clip acceptance.

## Validator result

Run: Unity `-batchmode -nographics -quit -executeMethod JDAssetIntakeValidator.Run` on the real worktree after UAL import. Unity exited successfully, no C# compile errors.

```json
{
  "models": 840,
  "prefabs": 304,
  "problems": 1,
  "examples": [
    "unresolved GUID e3d3ccd904634374eb1eb4eda636d12d: Assets/ThirdParty/Quaternius/MedievalVillage/Materials/MI_Plaster.mat"
  ]
}
```

The single remaining issue is in the **source archive**: `MI_Plaster.mat` references GUID `e3d3ccd904634374eb1eb4eda636d12d` for a wear texture, but no file in the admitted Unity URP archive has that `.meta` GUID. The material makes that reference three times; the validator reports the distinct missing GUID once. It is not a missing intake copy. ENV should avoid that material or create an owned corrected derivative with lineage; do not patch the vendor archive/package in place.

The validator found no suspicious model import scale, invalid Humanoid avatar, missing prefab material/script or other unresolved serialized reference among the scanned batch. This is technical intake evidence, not a visual or animation quality verdict.

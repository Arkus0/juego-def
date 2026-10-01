# Animation intake and retarget factory

Scope: UAL1/UAL2 in-place FBX sources already admitted by ASSET-00. This factory admits **motions**, not final civilian art, NPC behavior, contact IK or minigame/combat systems. ANIM-02 consumes the shared motion library with CHAR-01's accepted civilian family.

## Operator workflow

From the checkout root, with Python 3.10+ and Unity 6000.3.24f1:

```powershell
python Tools/asset_catalog.py install --pack ual1
python Tools/asset_catalog.py install --pack ual2
python Tools/asset_catalog.py install --pack base
python Tools/gc2-provision.py install
python Tools/anim_catalog.py search --status ADMIT --family conversation_acting
python Tools/anim_catalog.py search --query muelle
python Tools/anim_catalog.py search --family work_activity
python Tools/anim_catalog.py prepare
```

Open this checkout's `Unity/JuegoDef` project. `Tools > JuegoDef > Animation > Run Batch in Play Mode` applies the existing Quaternius utility plus the small policy preset, imports each target Humanoid once, checks the full inventory and samples the selected batch on both regular bodies in Play Mode. It writes `Docs/evidence/WP-PROD-ANIM-01/runtime_report.json` and numbered contact sheets. Batch invocation uses `-batchmode -executeMethod JDAnimationFactory.Run` **without** `-quit` or `-nographics`: the callback exits after its Play Mode run and GPU captures. Retain the local log outside Git; the machine-readable report and curated captures are durable evidence.

Read each sheet's adjacent `.txt` row map. Columns are 10%, 45%, 80% of the source clip; blue is the regular male and orange the regular female, at source scale. `sequence-*.png` shows twelve chronological samples, left to right then top to bottom, covering the full clip. Captures render Unity's native `SkinnedMeshRenderer.BakeMesh` result after each Playable evaluation: this avoids Unity's GPU skinning cache repeating the first pose when many screenshots are taken within one Editor update. A repeated-frame guard rejects frozen representative sequences. Inspect motion over time using `Tools > JuegoDef > Animation > Motion Preview`, especially loop seams, contact placement and turns. Do not infer motion quality from `humanMotion=true` alone.

Record bounded visual decisions in `visual_review.json` against the runtime report SHA-256. `ADMIT` means the motion is usable within its recorded body/placement/consumer constraints. `ADAPT` retains an explicit contact, posture or integration task; `REJECT` is unusable as offered; `GAP` describes a missing capability rather than a pretend clip.

```powershell
python Tools/anim_catalog.py build
python Tools/anim_catalog.py validate
```

The build refuses stale policy, factory code, runtime or visual identities (including capture hashes), duplicate clips, missing retarget results and evidence-free admission. Validation also consumes ASSET-00's vault/receipt/source checks. Use `--vault` to relocate the source vault. Missing vendor bytes require the existing intake, never a different unrecorded download. `JDAnimationFactory.Verify` checks current Unity subclip identities, lengths, preset settings, importer metadata hashes and target Avatars against frozen evidence without changing the report; it is suitable for exact-candidate validation with `-batchmode -quit -executeMethod JDAnimationFactory.Verify`. Canonical LF attributes on ANIM metadata/evidence preserve content hashes across Windows clones.

## Adding the next normal clip

1. Search the semantic catalogue; use the stable ASSET-00 ID (`ual1:...` / `ual2:...`). Both FBXs contain many subclips; filename alone is not clip identity.
2. Add the desired existing source ID to `Docs/asset_catalog/anim_policy.json` with family, precise B0 tags and honest constraints. All covered UAL import/root/loop settings are applied by family, with no per-clip Inspector work. Preset repair starts from the current source's default takes and full boundaries, so newly added stacks are not silently lost behind old custom clip settings.
3. Prepare, run the same batch, inspect evidence, record the decision, build and validate. A changed report invalidates prior visual decisions until reconciled against the new output; do not manufacture an ADMIT by editing the catalogue directly.
4. A changed source FBX first goes through ASSET-00 snapshot/intake identity review. A new rig or source family requires a bounded compatibility spike. A new character proportion/outfit must pass the same sample checks before inheriting compatibility.

## Root, loop and rig conventions

- Only the pinned **in-place** `UAL1.fbx` and `UAL2.fbx` are covered. `_RM` variants present in the vault are not silently substituted or admitted.
- Humanoid imports use baked axis conversion, source frame boundaries and uncompressed animations. Root rotation, horizontal position and height are baked into the pose, preserving source orientation and position. The utility's explicit `Rig/root` motion node is cleared for this policy so it cannot override per-clip Humanoid root settings. The consumer owns movement and facing.
- Loop is explicit policy derived from the source naming convention. `Idle_No_Loop` is treated as a one-shot no/head-shake gesture by this factory. Source loop seams are measured just before the end of the clip without Unity loop-pose blending hiding discontinuities.
- Each body creates its **own** valid Humanoid Avatar. A shared naming convention is evidence to test, not permission to reuse a different body's Avatar. Required hips, head, hands, feet and lower-leg transforms plus a skinned renderer are checked.
- Validated target scope is regular male/female full bodies from the pinned CC0 corpus. Teen, superhero, partial-body, fantasy outfit or future CHAR derivatives do not automatically inherit ADMIT.
- Retarget measurement uses `AnimationClipPlayable`, `Animator.applyRootMotion=true` and foot/playable IK disabled so root baking and source problems remain visible. Foot travel and an approximate stance gait speed are reported; scene navigation must match the actual gait. The diagnostic estimate is not a shipped controller speed.

## Cheap rejection and review boundaries

The batch detects missing/ambiguous clips, source hash/GUID mismatch, wrong Humanoid/loop flags, short/empty boundaries, invalid/missing body Avatars/bones, non-finite/extreme skinned bounds, static motion, in-place drift, severe loop discontinuity and feet substantially below the test floor. Foot excursion, source-facing direction and gait speed are surfaced for review. Contact sheets and temporal preview are required for severe sliding, limb self-intersection, plausibility and object contact: numeric gates cannot establish subjective final quality.

The real source `A_TPose` is retained as a rejected reference-pose example. The factory also probes a missing-avatar target and contradictory loop settings through the same validators. These negatives demonstrate rejection rather than hiding broken inputs.

## Provenance and ownership

`Docs/asset_catalog/animations.json` joins ASSET-00 IDs, paths, source SHA-256 and license pointers to semantic family, tags, actual Unity local clip ID, preset, loop, status, restrictions and measured body compatibility. No duplicate source FBX is made and no source bytes are changed. The source copies and their import metadata remain local, restored by intake and presets. Any retained owned library asset is recorded in `Docs/asset_catalog/lineage.json`.

Reuse decisions, batch inputs/report, bad cases, visual observations and B0 gaps are retained under `Docs/evidence/WP-PROD-ANIM-01/`. Source documentation: Unity's [Humanoid retargeting](https://docs.unity3d.com/6000.3/Documentation/Manual/Retargeting.html) and [root-motion settings](https://docs.unity3d.com/6000.3/Documentation/Manual/RootMotion.html). No new paid or player-runtime dependency is adopted.

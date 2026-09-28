# ANIM-01 strict Worker pre-review

Role: Worker. This records readiness reasoning, **not independent PASS**. Baseline is `99302e624cd1962591b0186b21752fbb3db45dbd`; final exact candidate identity is in the PR. The WP's acceptance, forbidden expansion and handoff were re-read before freeze.

## Candidate and plausible falsifiers

| Could all supplied checks be green while the claim is false? | Inspection / disposition |
| --- | --- |
| Only file names/import flags, no real retarget | 45 selected source clips evaluated on **two distinct source-body Avatars** in Play Mode, with skinned mesh sampling and real native-rendered poses. 90 retarget evaluations, 6,728 pose samples. |
| Raw count padded with duplicate/reference/combat content | 254 indexed, but only **19 ADMIT**: 5 locomotion, 3 conversation, 4 ambient, 1 generic interaction and 6 reactions. Both T-poses rejected; UAL2 equivalent walk not admitted twice; combat/minigame content indexed only. |
| Runtime has moving bones but capture shows a cached pose | Found during inspection and repaired through native CPU skin snapshots. All eight temporal sequences and batch sheets inspected; temporal repeated-frame guard retained. |
| Shared rig assumed compatible with all civilians | Each regular male/female body builds its own valid Humanoid Avatar. Both were sampled. No claim about teen/superhero/final CHAR outfits; no final civilian-art acceptance. |
| Source/setting changes silently produce a different motion | ASSET-00 source/receipt validation, clip GUID/local ID, full source take boundaries, source/body hashes, actual importer metadata hashes, current clip lengths and factory/request/report/capture hashes. Canonical LF prevents clone-induced evidence drift. |
| Every next clip needs bespoke setup | Expanded 44→45 with `ual1:hit_stomach` by metadata only; all prior numeric measurements unchanged. Then reset all four imported FBX metadata files to deterministic GUID-only state and rebuilt: all IDs, measurements and capture bytes preserved. `REPEATABILITY.json` retains the comparison and a canonical baseline measurement digest. |
| Numeric checks certify object contact or ground traversal they never saw | Counter, chair, rail, pickup, carry, push, tool and consume motions remain `ADAPT`; door and specialist work gaps explicit. In-place locomotion is admitted as motion only, with consumer speed/navigation obligations. |
| Root flags hide drift or IK hides bad feet | Measured with root motion enabled and foot/playable IK disabled. Admitted clips had zero actor root translation/rotation drift; admitted looping pose endpoint error max ~0.00539 m. Foot travel/floor diagnostics retained. Full contact/foot-IK behavior in a moving gameplay actor is outside this claim. |
| Broken inputs admitted because they have valid duration/Avatar | Real T-pose rejected by reference semantics and measured zero motion; missing-avatar target and wrong-loop-policy probes also detected. |
| Admission report can lose a target, source identity or screenshot without failing | Eight regression probes run through the actual catalogue assembly path: stale policy, duplicate clips, wrong source hash, duplicate body, Edit Mode report, missing capture, changed capture hash and wrong body source. All passed. |
| Preview leaks or alters an author's scene | Native preview smoke renders the selected motion in a temporary preview scene and verifies that the original scene roots/dirty state are unchanged and the preview scene closes. |
| New generic importer or paid dependency silently adopted | Existing pinned Quaternius utility tested first and called for base settings. Unity Humanoid/PlayableGraph/BakeMesh reused. Avelune/no-Blender disposition retained. No new paid or runtime package; vendor source untouched. |

## Validation retained / reproduction

- `python Tools/asset_catalog.py validate`: 796 substrate candidates, no problems.
- `python Tools/anim_catalog.py validate`: 254 motions; 19 ADMIT / 233 ADAPT / 2 REJECT; five admitted families; no problems.
- `python Tools/test_anim_admission.py`: eight regression probes passed.
- Unity 6000.3.24f1 `JDAnimationFactory.Run`: completed Play Mode batch, 45 selected clips / two targets; three negative cases detected. Final C# compilation succeeded.
- `JDAnimationFactory.Verify`: current preset/boundaries/import hashes/clip identities and Avatars verified; preview smoke passed.
- `git diff --check`: checked before commit and again on the complete staged candidate. ANIM text hash bytes are checked against staged Git blobs so a fresh checkout preserves evidence identity.

The complete baseline-to-candidate file list, code, documentation and generated records were inspected. Generated JSON was checked as complete structured data against all ASSET-00 IDs, runtime records and visual decisions; images were inspected at actual third-person scale. No product/runtime systems, external dependency manifests, vendor bytes, unrelated workpacks or ENV work are part of this candidate.

After all bytes are committed, read the 40-character HEAD, run Python admission/substrate verification and native `Verify` on that exact candidate, and freeze only if clean. Any later commit invalidates that frozen identity. Independent Reviewer remains required before merge.

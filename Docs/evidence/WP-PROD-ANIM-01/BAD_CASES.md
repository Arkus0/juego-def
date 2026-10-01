# Bad cases and corrections

## Actual corpus: reference pose mistaken for a motion

`ual1:a_tpose` imports as a valid Humanoid clip, has duration and can be evaluated on both bodies. Those facts alone would pass a weak importer-only test. The factory rejects its reference semantics and independently measures zero useful bone displacement on both bodies (`static pose, no useful motion`). The capture shows the unchanged T-pose. Both libraries' reference poses remain `REJECT`, never counted as admitted vocabulary.

## Incompatible target and contradictory loop policy

The same target validator rejects an Animator without a valid Humanoid Avatar before retarget use. A second probe supplies the real looping idle with a contradictory one-shot policy; the clip validator surfaces `loop policy mismatch`. All three native negative cases report `detected: true` in `runtime_report.json`.

## Evidence capture failure found by Worker visual inspection

Early contact sheets repeated the first visible pose even though numerical bone samples changed. Advancing graph time alone did not cure it: Unity GPU skinning cached a pose while many captures ran inside the same Editor update. The final path evaluates native Humanoid motion in Play Mode, calls native `SkinnedMeshRenderer.BakeMesh` for that pose, renders transient mesh snapshots and removes them immediately. Twelve-frame representative sequences now show their changing poses; a guard rejects sequences with fewer than three distinct rendered frames. Early faulty sheets were replaced and are not admission evidence.

An earlier Editor search-index exception also interrupted a delayed callback. The batch now starts once through a guarded Editor update after entering Play Mode, and emits explicit start/completion markers. No incomplete report was used for admission.

## Semantic false friends

- `Turn90/180` on the admitted in-place source does not itself rotate the actor; `ADAPT` until consumer facing is synchronized.
- UAL2 `Walk_Fwd_Loop` reproduces the canonical UAL1 walk gait; it is indexed without counting it as another admitted motion.
- `Hit_Knockback` ends in a grounded fall. It is not admitted as a light B0 reaction.
- Source-valid counter/rail/sitting/pickup/carry motions are retained as `ADAPT` where contact with a real object is unproved.

## Evidence identity regressions

`Tools/test_anim_admission.py` probes policy drift, duplicate runtime clips, source-hash substitution, duplicate target-body substitution, Edit Mode masquerading as runtime evidence, missing screenshots, changed screenshot identity and body-source substitution. All must be rejected by the actual catalogue assembly path.

# ANIM-01 candidate evidence

This is Worker readiness evidence; it is **not an independent PASS**. The final exact `PRODUCT_SHA` is published in the candidate PR after all repository bytes are committed.

- [Dependency check](DEPENDENCY_CHECK.md): direct prerequisite and ownership boundary.
- [Reuse decisions](REUSE_DECISIONS.md) and [import spike](IMPORT_SPIKE.md): existing tools inspected/tested before missing glue.
- [Factory workflow](../../production/ANIM_FACTORY.md): provisioning, search, presets, batch execution, preview and next-clip path.
- `batch_request.json`: complete source inventory and selected retarget batch.
- `runtime_report.json`: 254 imported clips, 45 sampled clips on two real skinned humanoids in Unity 6000.3.24f1 Play Mode, 90 body/clip evaluations.
- `captures/batch-*.png` plus matching `.txt`: three poses per selected clip, row-to-ID mapping. `sequence-*.png`: twelve full-clip temporal samples for representative motions, left-to-right/top-to-bottom.
- `visual_review.json`: bounded Worker decisions tied to runtime report and screenshot hashes. [Semantic catalogue](../../asset_catalog/animations.json): 19 admitted motions plus adaptation/rejection metadata for every source candidate.
- [B0 coverage/gaps](B0_MOTION_COVERAGE.md), [bad cases](BAD_CASES.md), `REPEATABILITY.json`: demand fit, negative paths and 44→45 next-clip proof.
- [Worker pre-review](WORKER_PRE_REVIEW.md): complete candidate falsification and validation record.

The scene used for batch evidence is a disposable technical stage at third-person viewing scale. Blue/orange are inspection materials, not civilian art acceptance. Source bytes remain in the ignored, content-addressed ASSET-00 intake; there is no new derivative asset requiring lineage registration and no new external dependency.

# D0 REPAIR 1 — REBUILD made transactional (answer to independent FAIL)

- **Repaired candidate for**: the D0 frozen candidate `b3bb4665b1051f22d8aca956eb1729f6d1c1ce09`
  (PR #10, review **5366116751**, verdict **FAIL material**, inline anchor `EnvLayoutEditor.cs:1053`).
- **Reviewer's blocker (verified by re-reading the code before repairing)**: the regenerated spec
  became authority *before* all preconditions were checked and *before* the rebuild finished, and no
  cancel/exception path restored it. Repro: `SAVE TRACE → REBUILD → accept impact → dirty scene →
  Cancelar` left **new spec + old scene**; the same held for exceptions in `Begin`/`BuildRows`/
  `Finish`/AFFECTED and for a domain reload mid-rebuild (statics reset silently).
- **Repair scope**: the whole causal class, not the literal dialog. Everything lives in
  `EnvLayoutEditor.cs` (`LayoutRebuild`); the pipeline files (`EnvDistrict/EnvPolish/EnvPreview`) are
  untouched, and the OSM pinning question the reviewer flagged as still-suspicious is deliberately
  NOT touched here (fresh Reviewer of this SHA should attack it).

## What changed (contract of the repaired REBUILD)

1. **`TxGate` — every consent/environment precondition runs BEFORE the spec authority is touched**:
   Play Mode check for BOTH routes (was DISTRICT-only and post-write); the dirty-scene dialog moved
   before the promote; the AFFECTED route gains a preflight it never had (district scene open at
   `Assets/JuegoDef/Scenes/ENV/<id>.unity`, district root present — it edits the open scene in place).
   A "no" at any dialog leaves every byte untouched.
2. **`TxOpen` — promote happens inside a transaction**: snapshots of the previous spec AND the saved
   district scene go to `%LOCALAPPDATA%\JuegoDef\` (outside `Assets`, so nothing pollutes the repo —
   the old code wrote the spec `.bak` next to the authority file inside `Assets`). An EditorPrefs
   registry (`JuegoDef.ENV.Layout.RebuildTx.*`) marks the transaction in flight; unlike the statics,
   it survives domain reloads and editor restarts.
3. **`CommitTx` — at both success exits** (AFFECTED rows done / district `Finish`): marks committed
   first (a crash from then on must never roll a finished rebuild back), deletes the scene snapshot,
   keeps the spec snapshot for the operator.
4. **`Rollback` — on ANY cancel/exception after the promote**: restores the previous spec bytes
   (`File.Copy` back + reimport), restores the previous saved scene bytes, reloads the right scene in
   the editor (AFFECTED → district scene; DISTRICT → the scene it came from, falling back to the
   district scene / a new empty scene), and never saves the partial build (the only scene saves remain
   `EnvDistrict.Finish` / `SaveSceneIfDistrict` at the very end). If the compensation itself fails it
   says so loudly with the snapshot paths for a manual restore. The old `.bak`-with-no-reader is gone.
5. **`RecoverInterruptedTick` — crash/domain-reload recovery**: `[InitializeOnLoad]` on
   `LayoutRebuild`; on every domain load a per-editor-frame check rolls back a transaction left in
   flight without commit (compile or Play entered mid-rebuild, editor crash). Per-frame polling
   instead of a one-shot `delayCall` because the one-shot can fire while Play Mode is still tearing
   down and silently lose the trigger — found and fixed during this repair's own validation (the first
   implementation missed the recovery on the real Play-exit reload; re-tested below).
6. **`DebugFailAt {AfterPromote, MidChunk, MidRows}`** — operator/MCP evidence hook in the existing
   debug-hook style (`DebugSave`/`DebugRevert`): injects a failure after the promote to prove the
   rollback deterministically. Resets itself after firing.

Design choice (against the reviewer's "o mejor aún… staged" alternative): building from a staged
candidate without promoting would require pointing `EnvDistrict.Begin/BuildRows/Finish` at a
non-authority path (a pipeline change D0 declared forbidden) and would still need scene compensation
for the save inside `Finish`. Preconditions-first + guaranteed compensation keeps one build path and
makes every observable exit consistent.

## Evidence (2026-09-30, MCP-driven against the real CASCO, real node moves — no fixtures)

Baselines before every test (git-clean working tree): spec `942fb24f31026da7`,
scene-on-disk `2a386f8bb7929785`, trace `82d96b251dd0238a`. The scene file is git-ignored
(`.gitignore:46-47`) — it is a machine-local authority the transaction protects anyway.

| # | Test (exact reviewer repro first) | Receipts | Verdict |
| --- | --- | --- | --- |
| 1 | **Reviewer repro**: trace J_A moved (47,−69.8)→(50,−72) → REBUILD → impact dialog **REBUILD** clicked (real dialog, computer-driven) → dirty scene → **Cancelar** clicked | status `REBUILD cancelado: escena con cambios sin guardar`; `txOpen=false`; log shows NO `TX abierta` line (authority never touched); spec `942fb24f…` and scene `2a386f8b…` byte-identical; scene keeps its unsaved state | **PASS** |
| 2 | Same edit, `AutoConfirm`, `DebugFailAt=AfterPromote` (throw right after the spec was promoted) | `TX abierta` → `TX rollback (FALLO: JD_LAYOUT_DEBUG_FAIL AfterPromote)`; spec and scene byte-identical to baseline; `RebuildTx` keys cleared; snapshots present in `%LOCALAPPDATA%` (spec 746,891 B, scene 151,932,633 B) | **PASS** |
| 3 | `DebugFailAt=MidChunk` (failure after `Begin` discarded the old scene and the first 8-row chunk built) | `TX rollback (FALLO: JD_LAYOUT_DEBUG_FAIL MidChunk)`; spec/scene bytes identical to baseline; partial scene discarded, district scene reloaded (path + root + not dirty) | **PASS** |
| 4 | **Happy path** (no injection, real edit, full DISTRICT route) | `TX abierta` → `district completo (66 s)` → `TX commit`; promoted spec byte-equals the regenerated candidate (`f245c22078cc8878`); scene saved (`ac18ce2e7d4549f3` ≠ baseline, as expected); scene snapshot deleted on commit; reopen: root + **73,321** objects persisted | **PASS** |
| 5 | **Domain reload mid-rebuild**: Play entered at `RowsChunk` with the transaction open (statics reset, `phase=None`), Play exited → reload | automatic `TX rollback (rebuild interrumpido (domain reload / cierre del editor))` on the first editable frame — no manual invoke; spec/scene byte-identical; district scene restored and reopened | **PASS** |

Log tag for scripted re-verification: `JD_LAYOUT_REBUILD` (`TX abierta…`, `TX commit…`,
`TX rollback…`). Deterministic injection: `LayoutRebuild.DebugFailAt` + `AutoConfirm`.

## Not repaired here (on purpose)

- **OSM pinning by identity/hash** — still path + operator discipline (existence check only), exactly
  as in the failed candidate; the reviewer asked the fresh Reviewer of the repaired SHA to attack it.
- The AFFECTED route remains untriggered by any *real* edit this session (node moves correctly route
  to FULL because ground changes). It now has a preflight gate and shares the rollback machinery
  proven on the DISTRICT route; `MidRows` injection exists for the day a rows-only diff occurs.

## Environment / restore

Validation ran with the unrelated in-flight night-20260931 editor modifications still in the working
tree (see honest gap 3 in the README — unchanged situation, the consumed API surface is identical at
HEAD). After testing: trace + spec were reset to HEAD (`git checkout`), test snapshots/candidate
deleted from `%LOCALAPPDATA%`, and the local scene rebuilt from the restored HEAD spec through the
normal path (root + 72,552 objects; scenes are git-ignored). The district scene carried unrelated
unsaved in-memory changes from the night lane before validation started; they were preserved to
`%LOCALAPPDATA%\JuegoDef\D0_validation_dirty_scene_backup.unity` (saved-copy backup, differs from
disk) and NOT written back into the repo.

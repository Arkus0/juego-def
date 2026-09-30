# WP-PROD-ENV-DIRECTOR-00 — D0 vertical slice (move one thing correctly)

Status: **IMPLEMENTED + VERIFIED END-TO-END ON THE REAL CASCO** (2026-09-30, branch `worker/prod-env-01`)
Tool: `Unity/JuegoDef/Assets/JuegoDef/Editor/Env/EnvLayoutEditor.cs` — menu **JuegoDef > ENV > Layout Editor** (Editor-only)
Repair history: candidate `b3bb466` received an independent **FAIL** (PR #10 review 5366116751:
REBUILD was not transactional). Repaired and re-verified — see **`D0_REPAIR1.md`**. Repair-1
candidate `062e1e2` then received a second independent **FAIL** (PR #16 review 5366743166: the OSM
input was pinned only by path, so upstream drift could piggyback a rebuild). Repaired and
re-verified — see **`D0_REPAIR2.md`**.

## What D0 is (contract) and what shipped

```text
open CASCO -> select one trace node -> drag X/Z -> preview connected streets
-> SAVE -> regenerate authoritative district spec -> rebuild affected/full district
-> result survives reopen -> REVERT/Undo is safe
```

All steps verified on the real ENV01_Casco_District (~311 buildings), not a fixture. On top of the D0
minimum the slice already carries part of D1: street `via` points, plaza vertices AND plaza discs
(center + radius handle), landmarks and river points are selectable/draggable with the same
PositionHandle + explicit-Y + Unity Undo machinery; nodes have name labels; streets draw their width
envelope by role; dirty state + pre-save change list; `SAVE TRACE | REVERT | REBUILD | PLAY` toolbar.

## Architecture (deliberately small, no second authority)

- `TraceEditState` (hidden ScriptableObject) mirrors every editable point of
  `ENV01_Casco_District.trace.json`. All drags go through `Undo.RecordObject` on it → real Unity
  Undo/Redo; `Undo.undoRedoPerformed` re-derives the in-memory JSON from the mirror.
- Edits write ONLY the known coordinate paths back into the parsed `JObject` (nodes `[x,z,h]`,
  street `via`, plaza `poly`/`disc`, landmark `at`, river `pts`). Unknown fields are structurally
  unreachable, so they survive every round trip.
- Nothing is written to disk until **SAVE TRACE** (then a `.bak` of the previous file is kept).
- **REBUILD** reruns the existing pipeline — `python Tools/env_district_skeleton.py` (pinned OSM
  extract, see below) — to a candidate spec, diffs it against the current spec, shows the impact,
  and routes: *affected rows only* when the diff proves it safe (same row ids, ground/river/plazas/
  streets/route byte-identical, ≤6 rows, via `EnvPolish.RebuildRow`), otherwise *full district*
  through `EnvDistrict.Begin` + `BuildRows` chunked per editor frame + `Finish` (~73 s observed).
  The scene is saved by `Finish` exactly as menu 7 does.
- **REBUILD is transactional** (repair 1): every consent/environment precondition runs BEFORE the
  spec authority is touched; the previous spec AND the saved district scene are snapshotted to
  `%LOCALAPPDATA%\JuegoDef\`; and any cancel, exception or domain reload after the promote rolls both
  back — spec authority and scene can never disagree at any exit of the operation. See
  `D0_REPAIR1.md` for the contract and the byte-level receipts.

## Verified proofs (2026-09-30, MCP-driven against the real district)

| Proof | Result |
| --- | --- |
| Load: 103 editable points (35 nodes, 35 via, 23 plaza, 2 landmark, 8 river) | OK |
| Load/save with no edits | save blocked ("nothing to save"), file byte-untouched |
| Select J_A (47, −69.8, 0.7), move → (50, −72, 0.7) | mirror + JSON + change list update live; connected street guides redraw (screenshot `D0_scene_guides_JA_moved.png`) |
| Unity Undo → Redo | exact baseline restore / re-apply; dirty state follows |
| REVERT | in-memory discard only; trace file byte-identical afterwards |
| SAVE TRACE | `.bak` created, `.bak` == previous file bytes; exactly one JSON path changed (`nodes.J_A`); all 16 top-level keys + landmarks/route/zones/river byte-identical |
| Regenerate spec from saved trace | skeleton ran in-editor (73 s total rebuild); diff: `streets, river, stairs, garden, route, ground:{strip,lane,plaza,core,huerta,yard}` changed; 87 rows geometry + 40 rows re-rolled assignments → **FULL route** (correct: ground changed, partial unsafe) |
| Rebuild reflects the edit | rebuilt terrain height at the NEW node position (118, 166) = **0.70 m** = the node's authored height; rows 161 → 168 in spec and scene |
| Survives reopen | scene saved by `Finish`; reopened: root + 168 rows + 0.70 m still there |
| Undo/Revert cannot corrupt | trace never written except by SAVE; `.bak` byte-equality above |
| **REBUILD transaction (repair 1)** | reviewer repro (accept impact → dirty → Cancelar): spec+scene byte-untouched; failures injected after promote (`DebugFailAt`) and a Play-mode domain reload mid-rebuild: spec+scene rolled back byte-identical every time; happy path commits (`TX commit`) and survives reopen — full table in `D0_REPAIR1.md` |

## REBUILD safety model (why the impact dialog exists)

The district spec is not a pure function of the trace today: it carries accepted hand fixes
(e.g. `K15_1` east `tip_keep`, shortened `Obispo_Escalera` top) and was generated from an OSM
extract that is intentionally not in the repo. Regenerating therefore shows (and asks before
applying): (a) geometry spread, (b) stochastic re-rolls downstream of geometry changes
  (seed 1971 stream — observed 40–75 rows changing palette/seed for one node move), (c) OSM drift
  — now **gated upstream by the pinned source**: REBUILD hashes the extract and refuses to run
  unless it matches the adopted SHA-256, so drift can only enter through an explicit adoption
  (see the pinned-source section and `D0_REPAIR2.md`). The diff always reports these classes;
  REBUILD proceeds only after explicit confirmation (or `AutoConfirm` for operator runs).
  All consents happen BEFORE the spec is promoted; from the promote on, the operation is
  transactional — a failed or interrupted rebuild restores spec and scene to exactly the pre-rebuild
  bytes (`TX rollback`), a completed one commits (`TX commit`). The spec snapshot of the previous
  authority is kept at `%LOCALAPPDATA%\JuegoDef\<id>_spec.prev.json` after a commit.

## Pinned OSM extract (identity, not path — repair 2)

The OSM extract stays out of the repository (ODbL hygiene); what the repo carries is its **adopted
content identity**: `Assets/JuegoDef/Env/Specs/districts/<id>.osm.json`
(`{sha256, bytes, adoptedUtc, path}`). REBUILD hashes the configured extract (EditorPrefs path,
`elegir...` / `ruta por defecto` in the window footer) and **refuses to run** unless the bytes
match the adopted pin; the pin only ever changes through the explicit **«Adoptar OSM»** action
(old→new hash confirmation). Current adopted source: sha256
`d3e4220c819ee9f701a5f87dfb4fbde1c10414066743640da1867da172695a19` (210,703 B, Overpass base
2026-09-30, fetched with the documented `python Tools/env_morphology.py fetch --bbox
43.1521,-4.6244,43.1541,-4.6222`), at `%LOCALAPPDATA%\JuegoDef\ENV01_osm.json` on this machine.
Every run logs the verified hash; every promote receipt carries it. Adopting a genuinely different
extract re-rolls stochastic assignments in rows (shown in the impact dialog) — and the first pinned
rebuild exposed that the previous committed spec had been generated from an older extract: the spec
was re-baselined through the normal transactional path (see `D0_REPAIR2.md`, "Finding").

## Test artifacts / restore

The end-to-end test moved J_A, saved, rebuilt and then restored: trace + spec were reset to HEAD
(`git checkout`), test `.bak`s deleted, and the local generated scene rebuilt from the restored
HEAD spec through the normal path (`Begin/BuildRows/Finish`; scenes are git-ignored). The pinned
OSM extract and the EditorPrefs entry are kept — they are the working setup for real use.

## Not in D0 (remaining D1+, by contract)

Street width drag handles, landmark rotation, add/remove via/vertex, zones polygons, PLAY HERE
(positioned at selection), frame/top-view/bookmarks, Mode B/C (buildings/props), AI verbs (D3).
Known UX gaps flagged for D1: numeric Y editing exists only in the window inspector (no vertical
drag handle); plaza disc height is a guide value (trace discs carry no y).

## Worker pre-review (strict, before freeze)

- **Acceptance/DoD**: every D0 contract step executed on the real district, not a fixture (table above).
  Forbidden scope respected: no runtime editor, no second authority (the mirror is derived state and
  writes only known coordinate paths back into the parsed trace), no new framework, no pipeline change
  (REBUILD invokes the documented `env_district_skeleton.py` + `EnvDistrict.Begin/BuildRows/Finish`).
- **Baseline→candidate diff**: additions only — `Editor/Env/EnvLayoutEditor.cs` (+meta) and this
  evidence folder. No existing file modified.
- **Falsifiers checked**:
  - *Tool only works on a toy fixture* — no: 311-building district, 103 editable points, real spec/scene.
  - *Save corrupts unknown fields* — byte-compare proved only `nodes.J_A` changed, 16/16 keys intact.
  - *Undo/Revert leave half-written authority* — trace is written only by SAVE (guarded against
    external disk changes since load); REVERT is an in-memory reload, file untouched (byte-compared).
  - *Rebuild hides semantic drift* — the spec diff is computed, shown and confirmed before applying;
    the three drift classes (geometry spread, stochastic re-rolls from the seed-1971 stream, OSM
    drift) are all visible in the impact summary.
  - *Guides are a debug visualizer* — drag-editing drives the same mirror the JSON is written from.
- **Honest gaps (recorded, not hidden)**:
  1. The AFFECTED (rows-only) rebuild route was never triggered by a real edit in this session
     (node moves correctly routed to FULL because ground changed); it is built on the existing
     proven `EnvPolish.RebuildRow`, now gated by a preflight (district scene open + root present,
     checked before any authority write) and covered by the same transaction/rollback machinery the
     DISTRICT route proved — but it is still live-untested with a real rows-only diff.
  2. The PLAY toolbar button itself was not clicked via MCP; Play Mode entry/exit WAS exercised
     programmatically (`EditorApplication.isPlaying`) in the repair-1 reload test (D0_REPAIR1.md #5).
  3. Validation ran on the working tree while unrelated in-flight night-20260931 editor
     modifications existed (`EnvDistrict.cs` additive passes, `BuildingAssembler.cs`,
     `EnvInteriors.cs`); the API surface this tool consumes
     (`EnvDistrict.Begin/BuildRows/Finish/DistrictSpecs`, `EnvPolish.RebuildRow/
     FixBlockedOpenings/SeatOnGround/Auto`) is byte-verified identical at HEAD, so the candidate
     tree compiles and behaves the same at the tool boundary.
  4. The OSM extract **path** lives in EditorPrefs (machine-local convenience pointer) and the
     extract **bytes** stay out of the repo by policy — but their adopted **identity** is committed
     (`<id>.osm.json`). A fresh machine must run the documented fetch once and then adopt it
     explicitly if the bytes differ from the pin (REBUILD says so; it never adopts silently).
  5. First REBUILD after adopting a genuinely new OSM extract re-rolls stochastic assignments in
     rows (existing pipeline behaviour, seed 1971) — surfaced in the impact dialog, one-time per
     adoption, and now impossible to trigger by accident (refetch/overwrite alone is blocked).

## Candidate scope (frozen bytes)

Repair-2 candidate (over repair 1): `Unity/JuegoDef/Assets/JuegoDef/Editor/Env/EnvLayoutEditor.cs`
(+ `.meta`), the pinned-source sidecar `Assets/JuegoDef/Env/Specs/districts/
ENV01_Casco_District.osm.json` (+ `.meta`), the re-baselined district spec
`ENV01_Casco_District.json` (documented in `D0_REPAIR2.md`, "Finding"), and
`Docs/evidence/WP-PROD-ENV-DIRECTOR-00/` (this README + `D0_scene_guides_JA_moved.png` +
`D0_REPAIR1.md` + `D0_REPAIR2.md`). The working tree also carries unrelated uncommitted
night-20260931 work; it is NOT part of this candidate. PRODUCT_SHA is recorded in the freeze report
outside the repository bytes (any further commit would create a new candidate).

# WP-PROD-ENV-DIRECTOR-00 — D0 vertical slice (move one thing correctly)

Status: **IMPLEMENTED + VERIFIED END-TO-END ON THE REAL CASCO** (2026-09-30, branch `worker/prod-env-01`)
Tool: `Unity/JuegoDef/Assets/JuegoDef/Editor/Env/EnvLayoutEditor.cs` — menu **JuegoDef > ENV > Layout Editor** (Editor-only)

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

## REBUILD safety model (why the impact dialog exists)

The district spec is not a pure function of the trace today: it carries accepted hand fixes
(e.g. `K15_1` east `tip_keep`, shortened `Obispo_Escalera` top) and was generated from an OSM
extract that is intentionally not in the repo. Regenerating therefore shows (and asks before
applying): (a) geometry spread, (b) stochastic re-rolls downstream of geometry changes
(seed 1971 stream — observed 40–75 rows changing palette/seed for one node move), (c) OSM drift
(today's fetch has 2 plots more than the 2026-09-28 one). The diff always reports these classes;
REBUILD proceeds only after explicit confirmation (or `AutoConfirm` for operator runs).

## Pinned OSM extract (operator requirement)

`REBUILD` needs the OSM extract path (EditorPrefs `JuegoDef.ENV.Layout.ENV01_Casco_District.OsmPath`;
`elegir...` / `ruta por defecto` in the window footer). Current machine path:
`%LOCALAPPDATA%\JuegoDef\ENV01_osm.json` (Overpass base 2026-09-30, fetched with the documented
`python Tools/env_morphology.py fetch --bbox 43.1521,-4.6244,43.1541,-4.6222`). Reuse THE SAME file
for every rebuild; per-district determinism depends on it. First adoption after a new fetch will
re-roll stochastic assignments in rows (shown in the impact dialog).

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
     proven `EnvPolish.RebuildRow` but is live-untested.
  2. The PLAY button (Play Mode toggle) was not exercised via MCP.
  3. Validation ran on the working tree while unrelated in-flight night-20260931 editor
     modifications existed (`EnvDistrict.cs` additive passes, `BuildingAssembler.cs`,
     `EnvInteriors.cs`); the API surface this tool consumes
     (`EnvDistrict.Begin/BuildRows/Finish/DistrictSpecs`, `EnvPolish.RebuildRow/
     FixBlockedOpenings/SeatOnGround/Auto`) is byte-verified identical at HEAD, so the candidate
     tree compiles and behaves the same at the tool boundary.
  4. The OSM extract path lives in EditorPrefs (machine-local, outside candidate bytes); a fresh
     machine must run the documented fetch once (window footer → "ruta por defecto" prints it).
  5. First REBUILD after adopting a new OSM extract re-rolls stochastic assignments in rows
     (existing pipeline behaviour, seed 1971) — surfaced in the impact dialog, one-time per adoption.

## Candidate scope (frozen bytes)

Exactly: `Unity/JuegoDef/Assets/JuegoDef/Editor/Env/EnvLayoutEditor.cs` (+ `.meta`) and
`Docs/evidence/WP-PROD-ENV-DIRECTOR-00/` (this README + `D0_scene_guides_JA_moved.png`).
The working tree also carries unrelated uncommitted night-20260931 work; it is NOT part of this
candidate. PRODUCT_SHA is recorded in the freeze report outside the repository bytes (any further
commit would create a new candidate).

# D0 REPAIR 2 — OSM source pinned by content identity (answer to independent FAIL)

- **Repaired candidate for**: the D0 repair-1 candidate `062e1e2a64fe21041d1f0ed08ac4780a24b6e7af`
  (PR #16, review **5366743166**, verdict **FAIL material**, inline anchor `EnvLayoutEditor.cs`
  OSM row). The transactional REBUILD of repair 1 was re-tested by that review and accepted; it is
  NOT re-litigated here.
- **Reviewer's blocker**: the candidate persisted only an OSM **path** (EditorPrefs) — a refetch or
  overwrite at the same path changed the regeneration input without changing any pinned identity, so
  REBUILD could silently consume upstream OSM drift, and `SpecDiff` could not distinguish that from
  legitimate trace-edit spread. Prescription: per-district content identity (SHA-256), verified
  before every regeneration, blocked on mismatch, changed only by a distinct **adopt new OSM**
  action, adopted hash exposed in the rebuild/evidence log.
- **Repair scope**: the whole causal class (input identity, not the one filename). Everything lives
  in `EnvLayoutEditor.cs` (new `OsmPin` static + pin row/adoption UI in the window + hard gate in
  `LayoutRebuild.Start` + adopted-hash receipts). The transaction machinery of repair 1 is untouched
  except one receipt line after the promote (re-smoked below). The pipeline
  (`env_district_skeleton.py`, `EnvDistrict`, `EnvPolish`) is untouched.

## What changed (contract of the pinned source)

1. **The pin lives in repository bytes**, not EditorPrefs: `Assets/JuegoDef/Env/Specs/districts/
   <id>.osm.json` — `{sha256, bytes, adoptedUtc, path}` — committed next to the district spec, so
   the adopted identity is reviewable in the diff and survives machine changes. The raw OSM extract
   stays out of the repo (ODbL hygiene, unchanged policy); only its identity is committed. The
   EditorPrefs path remains what it always was: a convenience pointer to where the bytes live.
2. **Identity is content, not path**: same bytes at a new path = same source (allowed); different
   bytes at the same path = new source (blocked until adopted). Exactly the inverse of the failed
   candidate, where the path was the only identity.
3. **Adoption is the only way the pin changes** — window button **«Adoptar OSM»** with an explicit
   old→new hash confirmation dialog (operator/MCP runs may call `OsmPin.Adopt` directly; the
   receipt line is logged either way): `JD_LAYOUT_REBUILD osm-adopt district=… old=… new=<sha256>
   bytes=…`. A REBUILD never adopts a source by itself — not even the first one (fresh district =
   blocked until the operator adopts).
4. **Hard gate in `LayoutRebuild.Start`, before the python subprocess exists**: hashes the actual
   file bytes and compares with the pin. No pin → `Failed` with "OSM sin adoptar… Un REBUILD nunca
   adopta una fuente nueva por sí mismo". Mismatch → `Failed` with **both** hashes
   (`pineado <short> / actual <short>`) before anything regenerates — a fortiori before any
   promotion. The window's REBUILD button mirrors this (disabled + reason tooltip; cached UI hash
   is never trusted by the gate, which re-hashes).
5. **The adopted hash is in the evidence log**: every run logs
   `fuente OSM verificada contra el pin: sha256:<full> ✓ (<n> bytes)` and every promote logs
   `spec promovida — fuente OSM sha256:<full>`.
6. Residual (accepted, documented): the hash is verified at `Start`; the python subprocess reads
   the file moments later (single-operator editor tool — no second writer exists in the workflow).
   One-shot editor action, not a server.

## Evidence (2026-09-30, MCP-driven against the real CASCO — no fixtures)

Baselines before testing: OSM extract `%LOCALAPPDATA%\JuegoDef\ENV01_osm.json`
`d3e4220c819ee9f701a5f87dfb4fbde1c10414066743640da1867da172695a19` (210,703 B), spec at HEAD
`942fb24f31026da7…`, trace `82d96b251dd0238a…`, scene-on-disk `3c5c84da295d3cda…` (git-ignored).
OSM backed up before any mutation; restored afterwards (verified byte-identical).

| # | Reviewer falsifier | Receipts | Verdict |
| --- | --- | --- | --- |
| 0 | No pin → REBUILD must not bootstrap silently | `phase=Failed`, status `OSM sin adoptar: falta el pin Assets/…/ENV01_Casco_District.osm.json — usa «Adoptar OSM»… Un REBUILD nunca adopta una fuente nueva por sí mismo`; python never spawned (candidate file untouched) | **PASS** |
| 1 | Explicit adoption records the identity | `osm-adopt district=ENV01_Casco_District old=(none) new=d3e4220c819ee9f701a5f87dfb4fbde1c10414066743640da1867da172695a19 bytes=210703`; sidecar written next to the spec (+ `.meta` by Unity) | **PASS** |
| 2 | Same trace + same OSM hash reproduces deterministically | run 1 and run 2 both log `fuente OSM verificada contra el pin: sha256:d3e4220c… ✓ (210703 bytes)`; candidate `af5c7e0d286d4501…` **byte-identical across both runs**; run 2 ends `la spec ya refleja el trace — nada que reconstruir` (diff empty); promoted spec byte-equals candidate | **PASS** |
| 3 | Mutated bytes at the same path → REBUILD refuses **before promotion** | OSM mutated in place (one appended newline: 210,703→210,704 B, still valid JSON, semantically identical, sha `5ce5ede77e37f195…`); `phase=Failed`, status `OSM CAMBIÓ respecto al pin — REBUILD bloqueado antes de regenerar nada:\n pineado d3e4220c819ee9f7…\n actual 5ce5ede77e37f195…`; spec `af5c7e0d…` untouched; candidate file untouched **with pre-mutation mtime** — python never ran, so nothing was regenerated, let alone promoted | **PASS** |
| 4 | Explicit adoption makes the identity change visible, then permits regeneration | `osm-adopt district=… old=d3e4220c819ee9f7… new=5ce5ede77e37f195916901f27d6578fc7ac44b66c1c148d6d505682dc1a9ee1b bytes=210704`; REBUILD starts, log exposes the new hash; ends `la spec ya refleja el trace` (whitespace-only drift ⇒ zero silent consequences — the gate is identity-based, not semantics-based) | **PASS** |
| 5 | Reverse direction also caught | original bytes restored → REBUILD refuses again (`pineado 5ce5ede77e37f195… / actual d3e4220c819ee9f7…`) → re-adoption returns the pin to `d3e4220c…` (final committed sidecar) | **PASS** |
| 6 | Repair-1 transaction still intact (promote path gained a receipt line) | real edit `CP_N (−58,−2)→(−57.5,−1.5)` saved; impact `streets, river, garden, suelo:{strip,lane,plaza,core,yard,outer} + 6 filas geometría + 1 re-roll` → DISTRICT route; `TX abierta` → `spec promovida — fuente OSM sha256:d3e4220c…` → injected `DebugFailAt=AfterPromote` → `TX rollback (FALLO: JD_LAYOUT_DEBUG_FAIL AfterPromote): spec y escena quedan exactamente como antes del REBUILD`; spec `af5c7e0d…` and scene `24d3eed5…` byte-identical to pre-run; trace restored from `.bak` (`82d96b25…`) | **PASS** |

Log tag for scripted re-verification: `JD_LAYOUT_REBUILD` (unchanged), plus
`osm-adopt …` / `fuente OSM verificada contra el pin: sha256:… ✓` /
`spec promovida — fuente OSM sha256:…`. Console after the whole session: zero errors except the
two intentional `JD_LAYOUT_DEBUG_FAIL` injections.

## Finding surfaced by the first pinned run (real drift the review hypothesized)

Run #2's first rebuild did **not** produce an empty diff against the HEAD spec: impact
`stairs, garden, suelo:{lane,huerta,yard}` changed + 34 rows geometry + 41 rows re-rolled
assignments. With trace (`82d96b25…`, identical to the repair-1 receipts) and the committed python
tool unchanged, the only remaining variable is the OSM bytes: **the spec committed at `062e1e2`
was generated from an OSM extract that no longer exists at the documented path** (the D0 README
already recorded that the 2026-09-30 fetch "has 2 plots more than the 2026-09-28 one" — the file
at the path had been silently refetched since that spec was made). That is precisely the failure
mode of the FAIL review, live in the frozen candidate's machine state: before this repair, the
next REBUILD would have absorbed that drift invisibly.

Resolution (visible in this candidate's diff, for the Reviewer/Owner to judge): the pinned rebuild
re-baselined the spec through the normal transactional path to the now-adopted source —
`942fb24f… → af5c7e0d286d4501c62c66bfb9feabd926efc26d22a5453643172f9d4051f1b4`
(`TX commit`; previous authority snapshotted at `%LOCALAPPDATA%\JuegoDef\
ENV01_Casco_District_spec.prev.json` = the old `942fb24f…` bytes). The triple
(trace `82d96b25…` ↔ OSM pin `d3e4220c…` ↔ spec `af5c7e0d…`) is now self-consistent: a fresh
REBUILD at the frozen SHA deterministically yields the empty diff (table #2, run 2). The
alternative — keeping the old spec — would ship a repo whose spec contradicts its own pinned
input, so every future rebuild would re-apply a 34-row drift the operator never chose.

## Worker pre-review additions (repair 2)

- Gate placement: both refusals fire before the `Process` is created (no subprocess, no candidate
  write, no scene/spec touch) — verified by candidate-file mtime in table #3.
- The UI hash cache (`OsmShaNow`) is only used to render state and disable the button;
  `LayoutRebuild.Start` re-hashes the file itself, so a stale cache cannot admit a mismatch.
- Corrupt/unreadable sidecar → `PinnedSha=""` → treated as "not adopted" → REBUILD blocked (safe
  direction); re-adoption rewrites a valid sidecar.
- Forbidden scope respected: no new authority (the sidecar is an input-identity record next to the
  spec, not a second spec), no pipeline change, no runtime feature. The one product-byte change is
  the documented re-baseline above.

## Environment / restore

Validation ran on `worker/env-director-d0` with the unrelated in-flight night-20260931 editor
modifications in the working tree (unchanged situation since repair 1; consumed API surface
byte-identical at HEAD; none of it is committed here). After testing: OSM extract restored to the
original bytes and re-adopted (final pin = `d3e4220c…`), trace restored from `.bak`
(`82d96b25…`), spec/scene left at the committed re-baselined state (`af5c7e0d…` /
`24d3eed5…` machine-local), window clean (`dirty=false`, `phase=None`, `AutoConfirm=false`),
`DebugFailAt=None`. Backup of the original OSM kept at `.zcode/repair2-backup/` (untracked).

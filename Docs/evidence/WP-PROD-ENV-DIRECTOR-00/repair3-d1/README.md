# D0 repair 3 + D1 — Worker readiness

Scope: the preserved D0 and D1 releases in WP-PROD-ENV-DIRECTOR-00. Canonical PR #16 keeps the original D0/repair history; the review base is `246756c72d7181cd034c04c6b5cde163d076cb66`. The independent FAIL #5367807573 on `7cd575d040d9349410517186065405722568b6d0` prompted the causal repair. This is Worker evidence, not independent PASS or human visual acceptance.

## Product behavior

Open **JuegoDef → ENV → Director** with CASCO rebuilt. Select a street or controller in Scene View: the entire street, width envelope and its controlling nodes/vias are highlighted before dragging. Drag X/Z, use **Altura Y** for vertical movement, drag the street's side arrows for width, a plaza vertex for its contour, or a landmark's position/rotation handles. Selection and preview never regenerate or write the district every frame.

**SAVE** shows a human-readable impact summary, preserves a local previous save and writes the trace atomically. **REBUILD** consumes the saved authority through the existing complete factory. The UI distinguishes PREVIEW, GUARDADO and RECONSTRUIDO. **PLAY HERE** finds a nearby walkable clear capsule and positions the existing GC2 character in Play Mode without writing a spawn into the saved scene. Window and native Scene View overlay share these actions. Planta, Encuadrar and A pie use three persisted native view bookmarks. Normal editing needs no JSON, Inspector coordinates or asset paths; source setup/adoption remains under advanced configuration.

Undo/Redo change the preview buffer. Undo after SAVE does not silently roll back its saved baseline. REVERT while dirty drops the preview; REVERT while clean explicitly restores the previous local save and requests a new rebuild. External writes block SAVE and require reload. Saved source survives window/editor reopening; in-session previews also survive window/domain reload.

## Whole D0 repair

The pinned OSM extract is an input, not a replacement for authored town decisions. `ENV01_Casco_District.authoring.json` now preserves 346 plot choices across all 164 rows, four authored frontage subdivisions/source-depth policies, seven authored row ends, the Obispo stair extension and 216 garden choices. Provenance binds the incumbent base and original corrections. These are consumed at their actual generation stages: frontages before plotting, plot choices before footprints/ground, end/stair/garden corrections after generation. Authored parcel counts also own subdivision: when a bounded geometry edit crosses an OSM intersection threshold, their existing width proportions are fitted to the edited frontage (span ratio 0.75–1.25), preserving every building identity instead of rerolling two authored plots into three. Missing or semantically reidentified rows still fail closed; explicit disabled identities provide deliberate retirement. A new source adoption cannot silently erase them.

`generation.json` binds the current spec bytes. A future spec-only edit blocks REBUILD until its decisions are converted to reproducible upstream inputs. It does not silently bless a new baseline. This closes the class beyond the two reviewer examples.

Python reads per-run verified trace/authoring/OSM snapshots. OSM is copied with writes/replacement denied and checked against the content pin. Input/recipe changes are checked before promotion and commit. Rebuild also refuses Play Mode, compilation errors or source code that differs from the compiled recipe.

The durable journal is local to each Unity project under Library/ENVDirector. It snapshots spec, generation guard, saved district scene, local build receipt and every file beneath the generated ENV and rendering roots, including metadata and absence. Rollback verifies snapshots, restores bytes, deletes newly created files/directories and reloads the preceding saved scene. Interrupted operations recover after editor/domain restart; a failed recovery retains the journal for retry. Mesh updates preserve existing asset GUIDs. A missing/stale build receipt, different active scene, dirty scene or missing district root cannot turn an empty spec diff into a false successful rebuild.

## Retired partial optimization

The Worker attempted to falsify the old spec-diff-based partial route. An isolated end change and restoration completed, but comparison against a complete rebuild found differences in seven of 164 row digests (`partial-falsifier.json`; digest includes hierarchy, transforms, meshes, materials and component types). Global finishing/physics passes are not isolated by a small row diff. The current candidate therefore removes that route and always executes Begin → row chunks → Finish when a rebuild is needed. The preserved D0 contract permits affected/full rebuilding; no partial-equivalence or fast-build claim remains. Ground/finishing can block the editor for several seconds; the measured complete rebuild is around 48–54 seconds on this machine. D2–D6 expansion/catalogue/AI/fast build work is outside this release.

## Evidence

| Check | Result | Artifact |
| --- | --- | --- |
| Entire incumbent spec, repeat generation | All top-level fields equal; 164 rows, zero changed rows | incumbent-equality.json, Tools/test_env_director_inputs.py |
| Input checks | 9 Python checks pass, including height edit, unknown intent, missing identity/input, explicit retirement, non-finite data, a one-metre J_A reshape and byte-identical generation across different process hash seeds | python-checks.txt |
| Native editor behavior | 22 checks pass: byte no-op, unknown fields, backup, external writer, malformed sources, Undo/Redo, SAVE/REVERT, reopen, spec guard, material/batch diff and compiled recipe guard | editor-checks.json |
| Forced post-promotion/mid-build failure | 2,107 protected files restored; zero mismatches and extras | full-rollback.json, full-failure.log |
| Concurrent authored input | Failed before promotion; spec and scene unchanged | concurrent-input.json |
| OSM overwritten after snapshot | Build completed from verified snapshot; next rebuild blocked on changed content; spec/scene unchanged by refusal | osm-toctou-check.json |
| Missing build receipt with unchanged spec | Complete route selected, then injected AfterPromote rollback; no false no-op | missing-receipt.json |
| Wrong active scene with matching receipt | Complete route selected, then injected AfterPromote rollback; no false no-op | wrong-scene.json |
| Native Scene View gestures | Node X/Z moved 1.299 m; width 6.35 → 9.35 m and vertical control 2.15 → 3.383 m; preview only, Undo restored it | native-gesture.json, native-width.json, native-y.json |
| Real CASCO composed edit | SAVE + complete build after node X/Z/Y, via X/Z/Y, width, plaza vertex and Torre pose changes | trial-before.trace.json, trial-after.trace.json, landmark-pose.json |
| One-metre J_A reshape | Complete build; K10_1 retains both authored and physical buildings | reshape-result.json, reshape-full.log |
| Landmark materialization | Requested front-center within 0.000465 m, yaw error zero | landmark-pose.json |
| Actual native UI | Street/controller highlight, guides, owner actions, explicit state | director-window.png, director-scene-ui.png |
| Runtime PLAY HERE | Two selected areas; actual GC2 player at safe feet + collider half-height; scene file hash unchanged | play-*.json, director-play-node.png |
| Three native views | All persisted, source unchanged | bookmarks.json |
| Final state | Incumbent layout restored and rebuilt, preview clean, receipt matches, no pending transaction | final-ready.json, final-full.log |

The trial is Worker-operated, not a substituted claim of human preference. The landmark trial first encountered a foliage-obstructed inherited camera view; the node trial capture shows the actual unobstructed third-person runtime. This WP does not assert acceptance of ENV-01's overall art quality.

## Reproduce

Use the existing authorized GC2/Quaternius provisioning and Unity 6000.3.24f1. Choose the adopted OSM extract once in advanced configuration. Required content SHA-256 is `d3e4220c819ee9f701a5f87dfb4fbde1c10414066743640da1867da172695a19`; the operator cache used here is `%LOCALAPPDATA%/JuegoDef/ENV01_osm.json`. A different path with those bytes is equivalent; adoption of different bytes is deliberate and will still enforce authored identities.

From repo root run `python Tools/test_env_director_inputs.py --osm <extract> -v`. On the connected isolated editor run `unity command eval_file <absolute Tools/env_director_editor_checks.cs> --project-path <Unity/JuegoDef> --format json`. The installed CLI rejects the skill's caller/skill flags, so those unsupported flags were omitted. A CLI wrapper reporting success alone is insufficient: inspect compilationFailed and test results.

For the composed trial, run Tools/env_director_real_edit.cs only on a saved district in an isolated checkout. It uses the same owner edit/save services, retains before/after sources under Library/ENVDirector and starts the complete build. Native gesture evidence is separate from those method calls. Restore the before source with LayoutDocument.Save or the Director's backup REVERT and rebuild after the trial. The shipped trace contains the original layout, not the operator's composition experiment.

Editing retains the incumbent parcel identities. An expanded falsification trial initially found that a one-metre J_A move crossed a subdivision threshold. That class is repaired by the explicit parcel policy and checked in test_08 plus a complete Unity rebuild. Bounded geometry edits are supported while row identities survive. A topology-changing edit or a semantically reidentified row is refused rather than discarding its authored choices; explicit profile migration/retirement is outside the normal D1 gesture loop. There is no automatic town redesign or catalogue/ordinary prop manipulation claim.

## Strict Worker pre-review

Reviewed the entire base-to-candidate surface and the preserved D0/D1 acceptance/forbidden scope. Falsifiers included authored content hidden outside trace+OSM, correct hashes blessing a regressed spec, concurrent/changed inputs, uncompiled source, interrupted transactions, generated-asset corruption, absent receipts, partial/full composition, unknown/malformed source, saved-baseline Undo, landmark transform/ground mismatch and runtime spawn persistence. The partial-equivalence falsifier led to removing the optimization. Product-relevant native UI and third-person runtime were inspected.

No new generic editor framework, external asset/code dependency, paid service, autonomous layout or second scene authority was introduced. Factory inputs own the world; bookmarks only own view poses. Independent review must bind the exact frozen PR head. Later commits create a new candidate. No independent PASS or merge is issued here.

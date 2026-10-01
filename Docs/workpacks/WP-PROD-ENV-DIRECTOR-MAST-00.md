# WP-PROD-ENV-DIRECTOR-MAST-00 — MAST Backend Decision Spike

Status: **BLOCKED UNTIL DIRECTOR D1 PASS / THEN READY / MUST COMPLETE BEFORE D2 IMPLEMENTATION**  
Class: BOUNDED TECHNOLOGY / REUSE DECISION SPIKE  
Depends on: accepted **D0 + D1** milestones inside `WP-PROD-ENV-DIRECTOR-00`, on the exact post-D1 candidate/merged state used for the spike.  
Consumes: current ENV trace/build authority, admitted real project prefabs/catalogue, current Unity/GC2 project, and the Director Core/project-adapter boundary already established by D0/D1.  
Does not require: Director D2+, ENV02, CASCO-V2, CITY01, AI provider integration or new semantic building/programme commands.  
Blocks: **Director D2 implementation** only. It does not block CASCO-V2, ENV01 closure, CHAR, Dialogue, M0 or other independent production lanes.  
Decision output: one evidenced disposition for MAST — **USE / ADAPT / REJECT** — plus the resulting bounded D2/D5 handoff.

## Objective / claim

Determine, with a real isolated Unity proof rather than architectural optimism, whether **MAST can serve as a subordinate mechanical placement backend for ENV Director** and thereby replace material custom implementation planned for D2/D5 without weakening Director's authority, persistence, transactional safety, commercial separability or owner-facing semantics.

The spike is successful when it proves enough to make a rational adoption decision. It is **not** required to adopt MAST.

The intended separation under test is:

```text
OWNER / DIRECTOR SEMANTIC INTENT
        |
        v
Director Core + JuegoDefEnvAdapter
        |
        | generic placement/preview/occupancy command
        v
MAST adapter or selected MAST-derived mechanics
        |
        v
Unity scene preview/materialization
        |
        v
ACCEPT -> Director-owned neutral placement result
        |
        +--> existing placement-capable canonical class, only if D1 already has one
        |
        \--> isolated spike acceptance sink / replay fixture
              (generic catalogue-object persistence remains D2)
```

Binding rule:

> **MAST may execute mechanics; it may never become world authority.**

D0/D1 remain authoritative for the semantic identity, canonical layout/state, SAVE/REVERT/REBUILD and project-specific persistence they already own. This spike must not invent a new production placement schema to widen that authority. MAST scene objects, grid state, palettes, assemblies or editor state cannot become a second canonical representation of the world.

## Why this spike exists

The current Director contract already requires reuse before invention and names MAST as relevant prior art for:

- placement ghost;
- footprint/cell occupancy;
- invalidation after hierarchy/Undo/object changes;
- isolated thumbnails;
- modular scene tools;
- assembly creation.

D2 currently plans catalogue/direct manipulation/ghost/snap/placement, while D5 later plans smart repeated builders. Implementing those mechanics from scratch before checking whether MAST can supply them would violate the project's reuse-first rule and create avoidable sunk cost.

Conversely, installing MAST merely because the feature list looks similar would be equally weak. The decisive questions are whether its mechanics can be called and bounded cleanly inside **our** authority model, on **our** Unity version and real prefabs, with tolerable coupling and no second scene/world truth.

## Binding inputs and preflight

Before implementation, record:

1. exact accepted D1 SHA/status and the guarantees consumed from D0/D1;
2. exact juego-def Unity version and relevant package/assembly state;
3. exact MAST repository revision/tag/commit selected for the spike;
4. current license text and redistribution/code-reuse obligations at that exact revision;
5. installation/provisioning route used for the isolated spike;
6. real project prefab/assembly inputs selected for proof;
7. protected files/authority that the spike must not mutate.

Recheck MAST rather than relying on chat memory or old research. Inspect current source/API boundaries before writing glue.

Disposition existing MAST subsystems or patterns as:

- `USE` — can be consumed substantially as-is behind our boundary;
- `ADAPT` — useful mechanics/code exist but need bounded adaptation;
- `REFERENCE_ONLY` — useful design/pattern but unsuitable as code dependency;
- `REJECT` — unsuitable for Director;
- `NOT_MATERIAL` — irrelevant to D2/D5.

Do not infer whole-tool adoption from one useful subsystem.

## Isolation / safety

Run the spike on a dedicated branch and isolated Unity checkout/project state. Do not modify another Worker's active scene or uncommitted bytes.

The spike may add a temporary MAST package/vendor copy, adapter, tests, fixtures and evidence. It must not silently make MAST a permanent production dependency.

Until the final disposition is accepted:

- do not rewrite D2 around MAST;
- do not delete existing Director mechanisms;
- do not migrate canonical ENV data into MAST data structures;
- do not make MAST palette/grid/scene metadata required to rebuild the world;
- do not modify source/vendor prefabs destructively;
- do not purchase another dependency to make the spike pass.

If MAST cannot be installed or compiled reproducibly in the current project, record the exact blocker. Do not "fix" juego-def architecture merely to accommodate the tool.

## Required architecture boundary

Use the smallest adapter seam that can prove replaceability. Conceptually:

```text
Director Core
└── IPlacementBackend / equivalent narrow seam
      ├── NativeDirectorBackend   [existing/fallback concept]
      └── MastBackend             [spike]
```

Names are not binding. A generalized plugin framework is forbidden.

The seam should expose only operations materially required by the proof, such as:

```text
begin preview(candidate, pose, constraints)
update preview(pose)
query validity / occupancy
accept preview -> placement result
cancel preview
move / rotate / delete existing placement
optional create/place assembly
```

Do not force Director semantics into MAST types. Convert at the boundary.

The spike must be removable without breaking D0/D1. If temporary compile guards or a separate assembly are needed, keep them local and explicit.

## Mandatory real-project proof

Use **real admitted juego-def prefabs**, not only cubes or synthetic test objects. At least:

- one ordinary prop/small object;
- one architecture/module-sized object with a meaningful footprint;
- one multi-object composition for the assembly test if that feature is evaluated.

A synthetic primitive may be added as a diagnostic control but cannot satisfy the claim.

### P1 — Reproducible provisioning / compatibility gate

From the exact spike branch:

- provision or attempt to provision the pinned MAST revision reproducibly;
- open/compile under the project's real Unity version when provisioning reaches that stage;
- record any MAST-caused compile/provisioning blocker exactly;
- identify required editor assemblies/package boundaries to the extent inspection/execution reaches them;
- verify how removal/disable works when MAST was actually introduced into the isolated project.

Positive-path signal: another Worker can reproduce a clean MAST-enabled tool state from repository instructions + pinned dependency identity without manually reconstructing hidden local state.

A reproducible incompatibility or provisioning/compile failure may instead be a **decisive REJECT signal**. In that case, do not patch juego-def or overbuild compatibility shims merely to unlock later probes: preserve the failure evidence, mark causally unreachable downstream probes `N/A — REJECT gate at P1`, and continue only with the universal decision/evidence/handoff requirements.

### P2 — Programmatic placement path

Demonstrate that Director-side code can request placement of a real prefab at a specified pose **without requiring the owner to operate MAST's own UI as the source of intent**.

The proof must identify whether it uses:

- supported/public MAST API;
- stable internal API;
- copied/adapted MIT code;
- or a minimal wrapper around scene/editor primitives.

Record coupling honestly. Reflection/private-field driving or synthetic GUI automation is not a clean PASS unless explicitly classified as fragile and the final disposition accounts for it.

PASS signal: one Director-originated command produces the expected preview/materialization through the candidate backend.

### P3 — Preview + cancel is non-authoritative

Show:

1. begin placement preview;
2. move/update preview;
3. cancel;
4. canonical D0/D1 authority remains byte/state-equivalent to before;
5. no durable scene object, hidden MAST state or dirty production asset survives cancellation.

If MAST cannot supply preview directly but its mechanics can be safely adapted, demonstrate the adapted route and classify it `ADAPT`, not `USE`.

### P4 — Footprint / occupancy / placement validity

Using real project geometry:

- place or preview one valid item;
- attempt an intentionally conflicting overlap or invalid placement;
- obtain a deterministic validity/occupancy result useful to Director;
- alter/move/remove relevant scene geometry and show the constraint result updates rather than remaining stale.

Do not accept a rigid grid assumption that contradicts Director's semantic footprint/clearance model merely because MAST supports it. Record exactly which occupancy concepts are reusable and which must remain ours.

### P5 — ACCEPT -> Director-owned neutral result -> replay without MAST authority

This is the decisive **backend-suitability** proof. It must not create D2 product persistence merely to make the spike pass.

1. request a placement through the candidate backend;
2. preview it;
3. ACCEPT through Director and obtain a **Director-owned neutral placement result** containing only the minimum stable data needed to describe the accepted outcome (for example candidate identity + pose + bounded placement metadata), with no MAST editor/grid/palette state as authority;
4. prove that result can be serialized/deserialized or otherwise replayed deterministically without MAST-owned hidden state;
5. route the replay through **one of exactly two lawful sinks**:
   - an already-existing placement-capable canonical D0/D1 class, **only if accepted D1 genuinely already owns that exact class and operation**; or
   - an isolated test-only acceptance sink/fixture owned by this spike;
6. reconstruct/materialize from that Director-owned result and verify the same prefab identity/pose/relationship outcome.

Then exercise the corresponding reversible test path: remove/revert the accepted fixture/result, replay/rebuild the test sink as applicable, and verify state returns coherently.

**Forbidden for P5:** adding a new production catalogue-placement schema, production persistence path or generic object authority to D0/D1. Generic catalogue-object rebuild-safe persistence remains D2.

A scene object that survives only because Unity serialized it directly is **FAIL for this proof** unless direct scene serialization is already the declared authority for that exact pre-existing object class.

### P6 — Direct manipulation compatibility

On one real object materialized through the lawful P5 route (pre-existing canonical class or isolated spike fixture), prove whether move/rotate/delete can reuse MAST mechanics while Director remains responsible for semantic selection and the neutral result/commit boundary.

The owner-facing pick must resolve to Director's semantic identity, not force the owner to reason about MAST internals, child meshes or foreign IDs.

If MAST adds no value here, record `REFERENCE_ONLY`/`REJECT` for this capability rather than inventing glue solely to claim coverage.

### P7 — Assembly/composition probe

Evaluate MAST's assembly capability with one bounded multi-object composition of approximately 3–10 real pieces:

- create or capture one reusable composition;
- give it a stable juego-def-owned/admitted identity or a temporary spike identity;
- place a second instance/copy;
- verify no source/vendor prefab is destructively edited;
- identify what would be required to return an accepted assembly to Director's catalogue/lineage.

This proof may conclude that assembly creation is unsuitable. The spike still passes if the negative result is well evidenced and the final disposition reflects it.

Do not turn this into D4 Coherent Content Forge or a general prefab-generation system.

### P8 — Absence / fallback check

Disable/remove the MAST integration route and verify:

- D0/D1 still compile and operate;
- canonical ENV data is still sufficient;
- no production scene requires MAST-specific serialized state to reconstruct accepted D0/D1 work.

This can be demonstrated by a clean fallback branch/configuration rather than shipping two finished backends.

## Decision matrix

At the end, score **capability disposition**, not a vanity percentage.

At minimum assess:

| Capability | Evidence | Disposition | Glue required | Fragility / lock-in |
| --- | --- | --- | --- | --- |
| placement ray/surface resolution | | | | |
| ghost/preview | | | | |
| snap/grid assistance | | | | |
| footprint/occupancy | | | | |
| thumbnails if inspected | | | | |
| move/rotate/delete | | | | |
| repeated/line placement if inspected | | | | |
| assemblies | | | | |
| Undo/invalidation integration | | | | |
| headless/programmatic access | | | | |
| removal/fallback | | | | |

Then choose exactly one overall disposition:

### `USE`

Choose only if MAST can remain a clean subordinate backend with programmatic/editor API access, reproducible provisioning, acceptable Unity compatibility, reversible preview/accept flow and low enough coupling that adopting it materially reduces D2/D5 implementation.

Handoff: rewrite D2 around a thin MAST adapter and only implement missing semantic/persistence UX.

### `ADAPT`

Choose when selected MAST subsystems or MIT code materially reduce work but wholesale dependency would create unnecessary authority, API or packaging coupling.

Handoff: enumerate **exactly** which modules/patterns/code are adopted and which D2 mechanics remain native. Preserve required license notices/attribution.

### `REJECT`

Choose when real integration requires brittle UI driving/reflection, creates a second authority/state path, conflicts with Director semantics, is not reproducible/compatible, or costs at least as much glue as a bounded native implementation.

Handoff: D2 proceeds natively, carrying forward only lawful `REFERENCE_ONLY` lessons. Record the rejected approach so later Workers do not repeat the experiment without new evidence.

A negative answer is a valid PASS. "We installed it and it looked useful" is not.

## Forbidden scope

- Implementing D2, D3, D4, D5 or redesigning Director UX during the spike.
- Changing D0/D1 semantics merely to fit MAST.
- Letting MAST become canonical layout/world/scene authority.
- New universal placement framework, generalized backend marketplace or speculative abstraction hierarchy.
- AI integration; this WP tests mechanical authoring substrate only.
- CASCO semantic-building/programme authoring, automatic interiors or city generation.
- Replacing project catalogue/lineage with MAST palette/assembly metadata.
- Destructive changes inside third-party/vendor/source packages.
- Mass prefab conversion or project-wide scene migration.
- Paid dependency acquisition.
- Benchmarks based only on LOC count or subjective "feels faster" without functional proof.

## Evidence

Retain under `Docs/evidence/WP-PROD-ENV-DIRECTOR-MAST-00/`:

- dependency manifest: D1 SHA, Unity version, MAST exact revision/license/provisioning;
- source/API inspection notes with subsystem dispositions;
- provisioning/build/compile receipt, including exact negative compatibility evidence when that is the REJECT gate;
- clean removal/fallback receipt when MAST was introduced far enough for removal to be material;
- selected real prefab identities and why they are representative, where execution reached real-prefab probes;
- P2–P8 receipts for executed probes, and explicit `N/A — <causal REJECT reason>` entries for probes made unreachable by a decisive earlier falsifier;
- captures for preview/cancel, valid/invalid occupancy and accepted/replayed result where those probes are reached;
- neutral-result before/after/revert evidence for P5, including whether the lawful sink was a genuinely pre-existing D0/D1 canonical class or the isolated spike fixture;
- assembly probe evidence;
- capability decision matrix;
- concise custom-glue inventory, including fragile/internal API use;
- final `USE / ADAPT / REJECT` rationale;
- exact D2/D5 handoff: what is now reused, what still must be built, and what must not be duplicated;
- strict Worker pre-review over the complete candidate.

Evidence must distinguish MAST behavior from Director behavior. A green Director test that never exercises MAST cannot prove adoption value; a green MAST demo that bypasses D0/D1 cannot prove suitability.

## Acceptance / falsifiers

Acceptance is **decision-conditional**. A well-evidenced decisive falsifier may terminate the positive integration chain as `REJECT`; the Worker must not keep implementing around a rejected dependency merely to manufacture green P2–P8 evidence.

**PASS in every disposition (`USE` / `ADAPT` / `REJECT`) requires:**

- exact D1 baseline identity plus exact MAST revision/license/provisioning route inspected or attempted;
- evidence that the spike stayed isolated and did not change D0/D1 semantics or introduce production D2 persistence;
- complete capability matrix, including explicit `N/A — <causal reason>` for any probe made unreachable by a decisive REJECT gate;
- one explicit overall `USE / ADAPT / REJECT` disposition whose rationale matches the evidence;
- bounded D2/D5 handoff that states what may be reused, what remains native, and what must not be duplicated;
- frozen exact candidate SHA and fresh independent Reviewer with no surviving material falsifier.

**Additional PASS requirements for `USE` or `ADAPT` to the extent those capabilities are claimed:**

- clean isolated MAST-enabled project compile;
- real-project Director-originated programmatic placement proof;
- non-authoritative preview/cancel proof;
- P5 neutral ACCEPT result replayed without MAST authority, using only a genuinely pre-existing placement-capable D0/D1 class or the isolated spike fixture;
- reversible test path for the accepted neutral result;
- fallback/removal proof preserving D0/D1;
- occupancy/validity, direct-manipulation and assembly probes for each capability claimed as reusable/adaptable; unsupported capabilities may be `REFERENCE_ONLY` / `REJECT` with evidence rather than falsely implemented.

**Additional PASS requirements for `REJECT`:**

- at least one decisive, reproducible blocker or a documented accumulation of blockers sufficient to justify rejection (for example incompatible compile/provisioning, no usable programmatic path without brittle private/UI state, authority leakage, non-reproducible hidden state, or glue cost that defeats material reuse);
- every skipped downstream probe is marked `N/A` with the exact causal blocker, rather than silently omitted;
- D0/D1 baseline remains independently healthy and unchanged by the failed experiment;
- any MAST bytes/state actually introduced are removable without making accepted D0/D1 work depend on them.

A `REJECT` caused at P1/P2 is therefore a valid PASS for this **decision spike** even though later positive integration proofs are unreachable.

**FAIL** if any survives:

- placement works only by manually using MAST UI and cannot be subordinated to Director intent;
- any claimed accepted/replayed result depends on MAST scene/editor state rather than the Director-owned neutral result and its lawful sink;
- cancel leaves durable hidden/scene/canonical mutations;
- a claimed positive replay/rebuild loses or duplicates the accepted neutral placement result;
- occupancy cache is demonstrably stale in ordinary edit/Undo cases claimed as supported;
- integration requires brittle private API driving but is still labelled clean `USE`;
- D0/D1 stop compiling or functioning when MAST is absent;
- third-party/source assets are modified destructively;
- license/revision is unpinned or redistribution assumptions are guessed;
- spike expands into D2/D5 implementation;
- final recommendation is based on feature-list similarity instead of the real proofs.

Plausible Reviewer falsifiers:

- the claimed P5 replay/rebuild merely reloads a scene already serialized with the object instead of reconstructing from the Director-owned neutral result;
- preview cancel deletes the visible ghost but leaves a MAST grid/palette/object record that later rematerializes;
- test prefab has trivial bounds while architecture pieces fail occupancy;
- code path secretly calls MAST EditorWindow state and breaks when the window is closed;
- Undo restores Unity object state but not canonical ENV state, or vice versa;
- MAST removal succeeds only because the tested scene never referenced its components;
- assembly duplicates vendor references in a way that cannot pass project lineage/admission;
- `USE` is chosen even though almost all useful mechanics were reimplemented in glue.

Reviewer must derive additional falsifiers before relying on Worker evidence.

## Definition of Done / handoff

Complete implementation/evidence bytes; stop overlapping writers; commit; read exact 40-character `PRODUCT_SHA`; run the checks materially required by the chosen disposition (including explicit N/A reasons after a decisive REJECT gate); perform strict Worker pre-review; freeze; fresh Reviewer attempts falsification.

After PASS:

- if `USE`: amend D2/D5 to consume MAST only through the proven subordinate adapter boundary;
- if `ADAPT`: amend D2/D5 with the exact selected reused mechanics/code and preserved license obligations;
- if `REJECT`: leave D0/D1 unchanged and proceed with the smallest native D2 implementation informed by the evidence.

In all three outcomes, **D0/D1 are preserved**. D3 semantic map expansion remains Director-owned; this spike cannot transfer that authority to MAST.

# WP-CITY-URBAN-00 — strict Worker pre-review

Status: **CLEAN BEFORE FREEZE**  
Date: 2026-09-28

This is Worker readiness evidence, not an independent PASS.

## Complete candidate reviewed

Baseline-to-candidate scope at pre-review:

- `Docs/design/CITY_URBAN_00_HANDOFF.md` — new durable planning/factory handoff;
- `Docs/design/FIRST_KEEPER_BLOCK_B0.md` — corrected migration provenance and local reconciliation role;
- `Docs/evidence/WP-CITY-URBAN-00/DEPENDENCY_CHECK.md` — direct prerequisites/new guarantee/reopen boundary;
- `Docs/workpacks/WP-CITY-URBAN-00.md` — explicitly reuses accepted Juego2 PR #265 instead of repeating it.

No Unity scene, asset pipeline, gameplay code or H0/H1 architecture is introduced.

## Acceptance falsifiers attempted

### Could the five zones still be isolated themes?

No surviving falsifier found. The handoff has explicit direct relations and a later loop `CASCO -> MERCADO -> MUELLE -> TALLERES -> VIVIENDAS -> CASCO`, plus two distinct Mercado–Muelle relations. Cross-town routines need not funnel through Mercado.

### Could B0 still be a vague port street?

No. B0 retains named anchors `L/A/S/E/P/Q/O/V`, direct and alternate routes, two cycles, public/control truth, expansion seams, relative elevation roles and a place/programme table.

### Could the plan silently transplant old inland geometry?

No. Puente Viejo/Liébana geometry, IDs, masks and route costs remain explicitly historical/non-authoritative. The B0 coordinates already present in the migrated brief remain hypotheses only.

### Could historical Juego2 fiction override current juego-def product truth?

No. The handoff explicitly supersedes `Villa Bruma`, uses the current nightlife allocation (Casco primary; Talleres secondary/alternative), and leaves final naming open.

### Could ENV still have to guess what to manufacture?

No. The matrix identifies facade, threshold, lodging, corner, street/edge, elevation, quay, prop, closed-frontage, interior, signage and palette demands with explicit statuses and intent.

### Could CHAR/ANIM/DIALOGUE remain underspecified?

No. Required B0 civilian families, motion families and investigation/dialogue/UI needs are all explicitly classified. Later-district breadth, full combat and fully voiced/cinematic presentation are deliberately deferred.

### Could `COVERED` be mistaken for full ANIM-factory coverage?

No. The sole current `COVERED` animation row is bootstrap **player** locomotion and explicitly says it does not satisfy civilian ANIM factory coverage. Civilian motion remains `FACTORY_REQUIRED`.

### Could proxies become keeper acceptance by accident?

No. The handoff states proxies may support integration but never count as keeper coverage. Scenic blockers/continuation and generic mannequin placeholders are the only proxy-class examples.

### Could CITY steal factory implementation authority?

No. CITY defines product demand/status only. `PROD-ASSET/ENV/CHAR/ANIM/DIALOGUE/UI` still own discovery, manufacture, repeatability and implementation.

### Could the handoff freeze too much geometry before play evidence?

No. Exact shoreline, route curves, grades, width tuning, thresholds, facade inventory, landmarks and lighting remain deferred to factory/keeper realization. Only semantic topology, programme, access, seams and relative elevation concept are frozen.

## Required outputs check

| Requirement | Result |
| --- | --- |
| reconciled five-zone topology | present in `CITY_URBAN_00_HANDOFF.md` |
| B0 selected/bounded | retained as Mercado–Muelle with rationale |
| route/anchor/game-space summary | present, including direct + alternate + two cycles |
| place/programme importance + depth + access + availability | present |
| factory-demand matrix with allowed statuses | present for ENV/CHAR/ANIM/DIALOGUE-UI |
| unresolved questions deferred to realization/playtest | present |
| Juego2 PR #265 provenance + local divergences | present |
| no Unity scene required | respected |

## Worker conclusion

No causal blocker survives inside the WP boundary. Candidate is ready to be frozen for a fresh independent Reviewer. Worker does **not** issue the independent PASS.

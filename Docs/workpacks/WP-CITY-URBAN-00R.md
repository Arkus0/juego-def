# WP-CITY-URBAN-00R — Compact Semantic City Rebaseline

Status: **READY FOR IMPLEMENTATION / OWNER-DIRECTED REOPEN**
Class: PRODUCT DESIGN / CITY PROGRAMME AMENDMENT
Depends on: `WP-CITY-URBAN-00` PASS + current ENV01/CASCO evidence
Blocks: `WP-PROD-ENV-CASCO-V2-00`; constrains `WP-PROD-ENV-02` and later district breadth

## Why this reopen exists

The accepted CITY-URBAN-00 topology remains useful, but physical ENV01 evidence exposed a scale/granularity mismatch:

- five neighbourhood identities were being read too easily as five similarly large production districts;
- CASCO ENV01 is visually successful but physically oversized for the intended content density;
- its current parcel grain creates hundreds of narrow architectural units that work as streetscape but poorly as reusable gameplay interiors;
- large areas classified as yard/huerta or residual ground are not yet proven to justify their runtime/content cost;
- continuing breadth before resolving this would industrialize the wrong city scale.

This WP reopens only the affected product decisions. It does **not** invalidate the accepted five-zone semantic topology, B0 roles, port-town identity, compact-density principle, terrain/water decisions, or ENV01's proven visual language.

## Claim

juego-def has a revised city-scale contract for a **single compact, continuous port town** whose five named zones are overlapping functional identities rather than five equivalent maps, and whose urban fabric separates visual facade grain from semantic buildings and playable interiors.

The revised model makes every retained piece of urban ground deliberate, keeps the strongest ENV01 CASCO identity, and caps breadth strongly enough that buildings and blocks can be authored and reviewed with high per-place quality.

## Binding principles

### 1. Five identities, one town

Retain:

- `CASCO`
- `MERCADO`
- `MUELLE`
- `TALLERES`
- `VIVIENDAS`

They are **not** equal-size levels and need no hard borders.

Preferred spatial reading:

- CASCO blends into MERCADO;
- MERCADO descends/opens into MUELLE;
- MUELLE transitions into TALLERES;
- CASCO and MERCADO rise toward VIVIENDAS;
- direct/alternate cross-town relations from CITY-URBAN-00 remain semantically available.

Do not create five ENV01-sized districts.

### 2. Compactness is a production constraint

The city should be small enough that retained blocks, buildings, routes and thresholds can be reviewed individually and revisited in play.

Planning orientation until physical evidence refines it:

- roughly **90–130 semantic buildings across the whole town**;
- roughly **30–40 semantic buildings in CASCO**;
- CASCO should likely occupy about **15–25% of final urban playable surface**, not behave like one fifth of five equal megadistricts;
- current ENV01's 196x236 m box is reference material, not a required final extent;
- shrinking/compressing CASCO by roughly **30–45% effective surface** is allowed if identity and route quality improve.

These are guardrails, not count-chasing acceptance targets.

### 3. Three distinct spatial concepts

The following are separate authorities:

`FacadeCell != SemanticBuilding != InteriorProgramme`

#### FacadeCell
A visual frontage/body used to preserve historical grain, irregularity, roof steps, bays and apparent property rhythm.

Multiple FacadeCells may belong to one SemanticBuilding.

#### SemanticBuilding
The actual game/world property:

- stable identity;
- use/programme;
- entrances;
- public/semi-private/private/service truth;
- ownership/occupancy hooks;
- exterior storey expression;
- playable-floor policy;
- content relevance.

A SemanticBuilding may visually present several historical frontage bodies.

#### InteriorProgramme
The playable spatial programme, authored from use and gameplay needs rather than whatever cavity remains behind a facade.

Examples:

- shop + stockroom + office + service exit;
- bar + kitchen + store + upstairs dwelling;
- lodging + reception + common room + rooms + service circulation;
- dwelling + workshop + yard;
- civic/anchor building with multiple playable layers.

### 4. Every retained urban metre is deliberate

No space is retained merely because the generator left it there.

Every retained non-building area must be classifiable as a deliberate role such as:

- public street/lane/steps;
- plaza/widening;
- river/water edge;
- usable courtyard/patio;
- garden/huerta with explicit world/gameplay purpose;
- service/loading/work yard;
- terrace;
- access/egress;
- retaining/slope response;
- scenic/occlusion/landmark composition with a stated reason.

A `yard` or `huerta` label is **not** proof of value by itself.

Unjustified residual ground must be absorbed, compressed, repurposed or removed.

### 5. Meaning before universal enterability

The target is **not** 100% open doors.

Instead:

- 100% of SemanticBuildings have an explicit identity/use;
- accessible interiors exist for a reason;
- deep interiors are reserved for places that benefit from spatial gameplay/revisit;
- closed buildings may still matter through residents, schedules, signage, windows, exterior events or systemic identity;
- an interactable/openable door must not lead to filler;
- exterior storey count and playable storey count may differ.

### 6. Preserve ENV01's soul, not its current measurements

Keep unless evidence disproves them:

- main spine;
- river + bridge identity;
- principal plaza;
- strong elevation character;
- 2–3 best secondary streets;
- 1–2 useful descents;
- selected lanes/corners;
- landmark/framed-view logic;
- northern-Spain / mini-Potes architectural language;
- narrow visual facade rhythm.

Reopen freely:

- exact district boundary;
- weak peripheral branches;
- parcel count;
- building count;
- building footprint/depth;
- yard/huerta extent;
- residual gaps;
- frontage-to-building equivalence;
- which storeys are playable;
- local route distances where compression improves play.

## Required outputs

1. Revised `PORT_TOWN_WORLD_MODEL.md` wording that defines a compact substantial town rather than a large city-scale production target.
2. Revised roadmap/DAG preventing `ENV-02` from scaling the old district grammar before CASCO-V2 pilot evidence.
3. A CASCO reduction ledger identifying:
   - `PRESERVE`
   - `COMPRESS`
   - `REMOVE`
   - `REPURPOSE`
   for current route/area families.
4. A semantic-building target model with planning ranges rather than exact forced counts.
5. A pilot handoff to `WP-PROD-ENV-CASCO-V2-00`.
6. Explicit record of which accepted CITY-URBAN-00 truths remain untouched.

## PASS

PASS when:

- the five zones remain a coherent connected town but are no longer interpreted as five equivalent large maps;
- whole-town and CASCO scale are explicitly bounded enough to stop uncontrolled breadth;
- FacadeCell / SemanticBuilding / InteriorProgramme are separate concepts;
- every retained ground category requires a reason beyond generator provenance;
- ENV01's visual/topological strengths are preserved as reference rather than exact geometry;
- CASCO-V2 pilot can be executed without guessing whether it is allowed to merge, deepen, compress or remove current parcel fabric;
- ENV-02 cannot claim scale proof by producing more content with the superseded one-facade/one-building assumption.

## FAIL

FAIL if:

- the result merely renames current 311 plots as semantic buildings;
- five zones remain de facto five ENV01-scale maps;
- yard/huerta is automatically treated as useful because it is labelled;
- 100% enterability becomes a mandatory content burden;
- CASCO identity is discarded for a generic smaller town;
- exact target counts are optimized mechanically at the expense of visual/gameplay quality;
- the amendment silently reopens unrelated B0/port/topology decisions.

## Handoff

After PASS:

`CITY-URBAN-00R -> PROD-ENV-CASCO-V2-00 -> revised ENV scale proof -> CITY-URBAN-01`

ENV Director D0/D1/D4 may continue in parallel. Smart-builder operations derived from the pilot belong later; the product model must not be bent to fit current tooling.

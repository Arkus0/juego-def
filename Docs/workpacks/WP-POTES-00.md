# WP-POTES-00 — Potes 1:1 Exterior Core + Semantic Consolidation Lock

Status: **READY / RESEARCH + PRODUCT BOUNDARY / NO UNITY IMPLEMENTATION**
Class: PRODUCT MAP AUTHORITY / REFERENCE RECONSTRUCTION PREPARATION
Depends on: accepted ENV01 reference/research bytes + current juego-def asset/ENV substrate.
Blocks: any physical Potes-core reconstruction batch.
Supersedes for new CASCO physical direction: starting CASCO-V2 implementation before this WP fixes the real-reference boundary. It does not erase accepted CITY/ENV evidence or ENV01 factory work.

## Claim

juego-def can replace the current authored/procedural CASCO layout authority with an **externally reproducible 1:1 exterior reference of the already studied compact Potes core**, while consolidating its many real exterior cells into approximately **60 large semantic/gameplay buildings**. The historic core must remain roughly **40–60% of the final game's authored gameplay/activity weight**, leaving the rest of the game to a small number of more open expansion zones.

The WP does **not** build the casco in Unity.

It decides exactly **what Potes core is**, exactly **how it is measured and referenced**, how many buildings it contains, how it is divided into production sectors, and prepares a complete first-sector source pack so a visual Worker can spend its effort on faithful environment-art reproduction rather than factual research or urban design.

## Owner product decision — binding

The new posture is:

```text
REAL POTES EXTERIOR
    -> factual spatial/architectural authority
ENV01
    -> reusable visual/tooling vocabulary
Worker/Opus
    -> faithful reconstruction and visual craft
```

Not:

```text
ENV generator
    -> chooses city/building/window/door/prop layout
```

For the initial reconstruction, observable real-world facts decide:

- street alignment and length;
- building footprint and orientation;
- relative elevation/grade;
- party-wall/adjoining condition;
- facade width;
- storey count when recoverable;
- roof topology/orientation when recoverable;
- door/window/opening placement when observable;
- balconies/galleries/arcades and major facade attachments;
- walls, stairs, railings and parcel boundaries;
- structural vegetation and conspicuous public-space props;
- relationship between building, street, river, bridge, plaza and neighbour.

ENV01 may provide the reusable mesh/material/prefab pieces used to reproduce those facts. Its current 311 generated bodies are **not geometry authority**.

Interior programmes are not copied 1:1 unless independently known and later useful.

### Binding identity rule

**Real exterior cell != semantic/gameplay building.**

The starting ~145 real Potes footprints/cells may be consolidated into approximately **60 semantic buildings** when adjacent real cells can form one plausible gameplay property.

Consolidation may:
- union adjacent source cells behind the public-facing exterior;
- allow one gameplay interior/programme to occupy several apparent historic facades;
- remove internal party-wall authority where the wall is not externally observable and later interior design benefits;
- retain multiple roof/facade subcells under one gameplay-building root.

Consolidation may **not**:
- move the public street edge;
- invent a new public-facing footprint;
- erase observable facade divisions merely to simplify production;
- change visible window/door/roof placement from the reference baseline;
- turn the casco back into procedurally designed architecture.

The intended Unity/product model is therefore approximately:

```text
~145 real exterior source cells
        ↓ faithful public-facing reconstruction
~60 semantic/gameplay buildings
        ↓ interiors/programmes later
15–25 meaningfully enterable buildings
```

The exact cell-to-building mapping is an explicit deliverable of this WP.

## Critical scope rule — the core is dense; the rest of the map is open

The intended final-town composition is now:

| Zone | Semantic/gameplay buildings | Spatial character | Primary gameplay |
| --- | ---: | --- | --- |
| **Potes historic core** | **~60** | dense / vertical / urban | investigation, social play, politics, commerce, NPC routines, compact minigames |
| **Market / civic expansion** | **~10–20** | medium/open | events, crowds, commerce, social systems, medium encounters |
| **Residential expansion** | **~10–20** | open | home routines, personal substories, quieter traversal, local encounters |
| **Port + workshops / industrial expansion** | **~10–20** | very open | combat, workshops, large interiors, jobs, port activity, systemic spaces |

The final map therefore targets roughly **90–120 semantic/gameplay buildings**, not hundreds of independently authored properties.

The historic core should account for about **40–60% of gameplay/activity weight**, despite potentially occupying a smaller share of final traversable area. Later zones are intentionally more open and get more gameplay from exterior space per building.

### Hard production envelope for Potes core

Use the previously studied approximately **180 × 220 m** Potes reference area as the starting exterior authority. Do **not** automatically shrink it merely to reduce cadastral cells; its physical compactness is acceptable if the semantic consolidation works.

Targets:

- source exterior authority: approximately the existing **145 real Potes footprint/cells**, subject to source revalidation;
- semantic/gameplay building target: **55–65**, nominal target **60**;
- hard cap: **70 semantic buildings** without explicit Owner amendment;
- every semantic building must have an explicit gameplay identity/purpose class, even when closed to the player;
- later capacity target: approximately **15–25 enterable buildings** in the core, with roughly **4–8 deep/hero buildings**;
- no requirement that every semantic building have a deep interior;
- preserve at least **3 credible outward expansion interfaces** for market/civic, residential and port/workshop growth;
- do not enlarge the Potes reference area to solve gameplay-space needs that belong in the later open zones.

### What “every building contains something” means

Every semantic building must justify its existence through at least one durable game role, for example:

- enterable destination;
- named NPC home/workplace;
- shop/service;
- faction/institution;
- investigation clue location;
- recurring routine anchor;
- mission exterior/threshold;
- systemic prop/service location;
- landmark/navigation role;
- narrative/background identity that participates in world state.

A building may remain non-enterable while still having a real gameplay role. “Contains something” does **not** mean authoring 60 full interiors.

## Starting reference already available

Existing ENV01 research measured a Potes reference box approximately 180 × 220 m and recorded:

- 145 real reference footprints;
- ~2,187 m walkable network;
- 25 block faces;
- network relief around 34 m;
- main/secondary/lane widths and alignment irregularity;
- strong grade/stair character;
- Potes-derived references around Solana, Cimavilla, Cántabra, Doctor Encinas, Plaza Capitán Palacios / Torre del Infantado node and river relationships.

Relevant repository starting evidence includes at least:

- `Docs/evidence/WP-PROD-ENV-01/CASCO_REFERENCE_STUDY.md`;
- `Docs/evidence/WP-PROD-ENV-01/HANDOFF_CASCO_POTES.md`;
- `Docs/evidence/WP-PROD-ENV-01/reference/`;
- existing ENV01 captures and factory/catalogue documentation.

These are **starting research**, not sufficient by themselves for the new 1:1 claim. Re-fetch/re-pin authoritative external geometry and source identities as required.

## Exact source hierarchy

For facts used by production, record exact source, retrieval date/version where possible, license/usage constraints, confidence and whether the fact is MEASURED, DERIVED, VISUAL_ESTIMATE or UNKNOWN.

Prefer, in order appropriate to the fact:

1. official cadastral / INSPIRE building-parcel geometry where lawfully available;
2. IGN/CNIG official cartography and MDT/terrain for ground/elevation;
3. official Potes planning/maps and municipal material;
4. OpenStreetMap as reproducible geometry/topology cross-check and for facts not supplied by higher authority;
5. lawfully usable georeferenced/aerial reference;
6. street-level/photographic reference for facade openings and architectural appearance;
7. secondary sources only when primary/reference coverage is absent.

Street-level imagery may be used as **visual reference** without being redistributed. Do not commit third-party photographs unless their license permits repository redistribution. A source index may store URL, viewpoint, date/coverage notes and the factual observations derived from it.

If two sources materially disagree, record the discrepancy. Do not silently choose whichever is easier to build.

## Workstream A — freeze the Potes exterior core and consolidation hypothesis

Start from the known approximately 180 × 220 m reference box. Re-fetch/revalidate its authoritative geometry and determine whether the existing box remains the best compact exterior core.

Do **not** spend the WP searching for a much smaller arbitrary cut merely to hit 60. The 60 target applies to **semantic/gameplay buildings**, not source exterior cells.

The exterior core should preserve the coherent real sequence around the Torre/plaza/river node, commercial/social streets, distinctive lanes, Solana/Cimavilla-type vertical fabric, residential origins/destinations and outward seams.

### Required boundary alternatives

Produce only **bounded boundary checks**, not three unrelated landmark collages:

1. the existing ~180 × 220 m reference box;
2. a conservative trim if obvious low-value edge fabric can be removed without harming coherence;
3. a conservative extension only if needed to obtain a materially better outward seam.

For each report:

- polygon / dimensions / area;
- source exterior cell count;
- walkable network length;
- meaningful edge-to-edge walking distance;
- landmark/node coverage;
- expansion interfaces;
- what is gained/lost;
- expected reconstruction burden.

Owner chooses the exterior boundary.

### Semantic consolidation study

For the Owner-selected boundary, propose a complete mapping from source exterior cells to **55–65 semantic/gameplay buildings**.

Each proposed semantic building must:
- be one contiguous property/group;
- preserve the real public-facing shell;
- have a plausible unified gameplay identity;
- have enough useful area/shape to justify its role;
- avoid arbitrary cross-street or cross-courtyard unions;
- record all source cells it consumes.

Output the distribution:
- 1 source cell -> 1 semantic building;
- 2 source cells -> 1 semantic building;
- 3+ source cells -> 1 semantic building;
- resulting footprint/usable-envelope distribution;
- candidates for deep/hero, medium/partial and closed-but-purposeful roles.

The Owner must approve the consolidation logic before it becomes production authority.

## Workstream B — Source-cell ledger + Semantic Building Ledger

For every real exterior source cell inside the Owner-selected core assign a stable immutable ID:

`POT-C001`, `POT-C002`, ...

For every consolidated semantic/gameplay building assign:

`POT-B001`, `POT-B002`, ...

Each `POT-Bxxx` records the exact ordered set of `POT-Cxxx` cells it owns.

Do not use current ENV01 plot IDs as final Potes authority.

For each building retain, as recoverable:

- source cell footprint polygon(s) in real metric coordinates;
- semantic union polygon / envelope and constituent cell IDs;
- local-game coordinate transform;
- footprint area;
- oriented dimensions / frontage;
- ground/elevation relation;
- storey count / estimated height;
- roof type and ridge orientation;
- party-wall / detached / attached relationships;
- street-facing facade(s);
- door/opening locations and confidence;
- window axes/openings by visible floor and confidence;
- balconies/solanas/galleries/arcades;
- major annexes;
- parcel/patio/garden relationships;
- visible walls, gates, stairs and retaining elements;
- material/architectural observations;
- source references for each non-trivial observation;
- confidence state.

Allowed fact states:

- `MEASURED`
- `DERIVED`
- `VISUAL_ESTIMATE`
- `UNKNOWN`

Never upgrade an estimate to measured merely because it looks plausible.

### No invention rule

For the later visual Worker:

> uncertainty about **what exists** is not artistic freedom.

Unknown facade facts remain UNKNOWN until resolved or Owner explicitly authorizes a bounded approximation policy.

This WP must identify which buildings/facades are sufficiently documented for faithful production and which need more reference before reconstruction.

## Workstream C — street/public-space ledger

Assign stable IDs to:

- streets/lane segments;
- plaza/public-space polygons;
- bridges;
- river edges;
- steps/ramps;
- retaining walls;
- major public boundaries;
- meaningful structural vegetation.

Retain exact/derived geometry, surface/edge observations, level relationships and references.

The selected core must be independently reconstructible without reading the current ENV01 generated layout.

## Workstream D — ENV01 reuse map

ENV01 is a source kit, not a spatial template.

Produce a reuse inventory for the chosen core:

- `REUSE_EXACT` — current ENV component can represent the observed Potes feature with negligible change;
- `RECOMPOSE` — existing ENV pieces/materials can be recombined to reproduce the observed feature;
- `ADAPT` — bounded new variant/derivative required;
- `MISSING` — current kit does not cover the observed feature;
- `NOT_NEEDED`.

Do this by **families/components**, not by forcing each current ENV01 generated building to survive.

Expected reusable families include where valid: plaster/stone materials, joinery, windows/doors, balconies/solanas, roof pieces, street ground, walls/parapets, bridge/river vocabulary, vegetation and street-life props.

Do not preserve a generated ENV01 building because of sunk cost.

## Workstream E — production sectorization

Partition only the Owner-selected Potes core into **3–5 natural production sectors**, using semantic buildings as production ownership units while retaining source-cell geometry beneath them.

Sector boundaries should follow actual urban seams and should minimise visual seam risk.

For every sector report:

- exact building IDs;
- street/public-space IDs;
- boundary polygon;
- neighbouring sectors;
- cross-boundary sightlines;
- cross-boundary party-wall/roof dependencies;
- expected visual complexity;
- source-coverage completeness.

Do not use an arbitrary rectangular grid.

The sectors exist for production batching only. They do not create in-world districts.

## Workstream F — prepare Sector Pack 01 for a visual Worker

Choose the first production sector primarily for **method falsification**, not ease.

It should contain a representative mix where feasible:

- one important landmark/large building or strong node;
- ordinary attached historic buildings;
- at least one irregular footprint/alignment;
- street or plaza;
- meaningful elevation;
- enough windows/doors/roof relationships to test 1:1 facade reproduction;
- river/bridge/public edge if this can be included without making the first sector excessively large.

Within Sector 01 identify a **First Slice** of roughly **6–10 semantic buildings** (likely more real exterior cells/facades) for the first physical reconstruction WP.

The Sector Pack must leave the visual Worker with factual questions already answered.

Required pack:

- sector polygon + metric coordinate transform;
- source-cell ledger subset;
- semantic-building ledger subset and cell-to-building mapping;
- street/public-space ledger subset;
- source/reference index;
- per-building reference links/views;
- explicit facade/opening/roof observations;
- relevant ENV component shortlist;
- missing-asset list;
- cross-boundary context;
- fixed comparison viewpoints;
- list of UNKNOWN facts that block faithful reproduction;
- reconstruction tolerances;
- First Slice exact IDs.

The pack should be sufficient for a fresh Worker to act without private chat history.

## Exterior fidelity policy for later reconstruction

This WP defines the initial reconstruction standard consumed by later WPs.

### Geometry

- Preserve pinned source footprint/alignment unless the source itself is uncertain.
- Target positional/edge error <= **0.5 m** for ordinary visible exterior geometry where source precision supports it.
- Preserve real relative road/building relationships rather than snapping to ENV module widths.
- Do not split one real source cell into several gameplay properties merely because ENV modules are narrow.
- **Semantic consolidation of adjacent source cells is allowed and required**, but the visible public-facing shell of every source cell remains part of the 1:1 baseline.
- A semantic union may simplify hidden internal party walls/interior planning, not observable public geometry.
- A later gameplay-adaptation WP may deliberately change the replica after the baseline exists.

### Facades

Where photographs/reliable visual reference exist:

- reproduce observed opening count and approximate position;
- reproduce main door side/position;
- reproduce storey rhythm;
- reproduce major balconies/galleries/arcades;
- reproduce roof topology and orientation;
- reproduce major facade material divisions.

Do not use procedural facade randomness on a referenced facade.

### Props

The objective is not centimetre-perfect forensic reconstruction of every movable bin/chair/car.

Copy **structural / identity-bearing public-space features** and fixed facade attachments when recoverable. Movable transient clutter may later use ENV dressing, but the Worker must not let random dressing redefine routes, thresholds or the character of a documented reference view.

## Explicitly out of scope

This WP does NOT:

- build or edit the Potes scene in Unity;
- reconstruct buildings;
- author interiors;
- assign final missions;
- decide final NPC roster;
- generate procedural buildings;
- expand the city beyond the selected Potes core;
- choose later industrial/sports/large-combat chunks;
- delete or mutate ENV01;
- implement Director changes;
- claim the final town is Potes narratively.

The game remains fictional. Potes is initial exterior/spatial reference authority for the bounded historic core.

## Deliverables

Create under `Docs/evidence/WP-POTES-00/` at minimum:

- `DEPENDENCY_CHECK.md`
- `SOURCE_LOCK.md`
- `CORE_CANDIDATES.md`
- `CORE_SELECTED.md`
- `potes_core.geojson` or equivalent reproducible metric geometry
- `SOURCE_CELL_LEDGER.csv`
- `SOURCE_CELL_LEDGER.json`
- `SEMANTIC_BUILDING_LEDGER.csv`
- `SEMANTIC_BUILDING_LEDGER.json`
- `CELL_TO_BUILDING_MAP.json`
- `STREET_PUBLIC_SPACE_LEDGER.json`
- `ENV01_REUSE_MAP.md`
- `SECTOR_PLAN.md`
- `sector-01/SECTOR_PACK.md`
- `sector-01/REFERENCE_INDEX.md`
- `sector-01/FIRST_SLICE.md`
- machine-readable sector/building geometry used by the next Worker;
- map images sufficient for Owner review of the three candidate boundaries and final sectorization.

If lawful downloadable reference imagery is retained, include attribution/license. Otherwise retain links/viewpoint metadata, not copied bytes.

## Required Owner gates

There are exactly two subjective/product decisions before PASS:

1. **Core + Consolidation Gate** — Owner chooses the exterior boundary and approves the ~60-building semantic consolidation.
2. **Sectorization Gate** — Owner confirms the selected core and production-sector division are understandable and appropriately scoped.

Do not ask the Owner to decide building geometry that external evidence can resolve.

## Acceptance

PASS requires:

- exact external source identities and reproducible acquisition/derivation are recorded;
- selected exterior core is one coherent compact Potes area, nominally around the already studied ~180 × 220 m box;
- source exterior geometry remains 1:1 authority for streets, public-facing footprints, facades, roofs and structural public-space relationships;
- source cells are mapped into **55–65 semantic/gameplay buildings**, nominal target 60, and <=70 without explicit Owner amendment;
- every semantic building has an explicit durable gameplay-purpose class;
- no semantic consolidation erases or invents observable public-facing geometry merely for convenience;
- at least three credible outward interfaces remain for later market/civic, residential and port/workshop expansion;
- every source cell and every semantic building has a stable ID;
- all production-relevant facts carry source/confidence state;
- no unknown facade fact is silently invented;
- streets/public spaces/elevations are independently reconstructible;
- ENV01 reuse is mapped as kit/component reuse rather than layout authority;
- core is partitioned into 3–5 natural production sectors;
- Sector Pack 01 is sufficiently complete for a fresh visual Worker;
- First Slice contains 6–10 semantic buildings and representative environment complexity;
- Owner passes both gates;
- Worker strict pre-review finds no hidden expansion of the casco to solve gameplay needs that belong in later open zones.

## FAIL

FAIL if any survives:

- Worker treats ~145 real exterior cells as ~145 independent gameplay buildings;
- semantic building count exceeds 70 without explicit Owner amendment;
- Worker destroys 1:1 public-facing geometry simply to hit the semantic count;
- semantic unions are implausible, disconnected or cross public streets;
- core boundary is a disconnected highlight reel;
- core has no plausible later expansion interfaces;
- current ENV01 311 bodies remain spatial authority;
- procedural/random facade rules decide observable Potes openings;
- Worker invents missing facade facts without declaring approximation;
- source images/data cannot be traced;
- sector boundaries create untracked half-buildings/party-wall/roof seams;
- Sector Pack 01 still requires its visual Worker to research where buildings/windows/doors/roofs go;
- WP starts rebuilding Unity instead of finishing the reference/production contract.

## Definition of Done / handoff

Finish all evidence bytes, freeze exact `PRODUCT_SHA`, perform strict Worker pre-review and hand the exact SHA to a fresh independent Reviewer.

After PASS, the immediate successor is:

`WP-POTES-01 — Sector 01 First Slice Reconstruction`

It consumes the frozen Sector Pack 01 and reconstructs only its 6–10 semantic-building First Slice (including all constituent real exterior cells) in an isolated Unity authority/output using ENV components under the 1:1 fidelity rules.

Later WPs may complete Sector 01 and subsequent sectors, but **no later casco WP may enlarge the Potes core boundary without a separate Owner-approved map-scope amendment**.

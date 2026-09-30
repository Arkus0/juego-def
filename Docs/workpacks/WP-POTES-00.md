# WP-POTES-00 — Bounded 1:1 Potes Core Reference Lock

Status: **READY / RESEARCH + PRODUCT BOUNDARY / NO UNITY IMPLEMENTATION**
Class: PRODUCT MAP AUTHORITY / REFERENCE RECONSTRUCTION PREPARATION
Depends on: accepted ENV01 reference/research bytes + current juego-def asset/ENV substrate.
Blocks: any physical Potes-core reconstruction batch.
Supersedes for new CASCO physical direction: starting CASCO-V2 implementation before this WP fixes the real-reference boundary. It does not erase accepted CITY/ENV evidence or ENV01 factory work.

## Claim

juego-def can replace the current authored/procedural CASCO layout authority with a **bounded, externally reproducible 1:1 exterior reference of a deliberately selected part of real Potes**, while keeping the resulting historic core small enough to remain only **40–60% of the final game's authored experience** rather than becoming the whole map.

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

Interior programmes are not copied 1:1 unless independently known and later useful. Exterior historical cell != final gameplay programme.

## Critical scope rule — Potes is the core, not the whole game

The casco must be a great, dense place, but it must leave substantial production/gameplay space for later non-casco expansion.

Interpret **40–60% of the game** as authored gameplay/activity weight, not raw square metres.

The Potes core is expected to host a high share of:

- investigation;
- dialogue/social play;
- commerce;
- municipal/political activity;
- NPC crossing/routine encounters;
- compact minigames;
- small encounters;
- recurring hubs.

Later expansion is expected to carry a disproportionate share of:

- large combat spaces;
- industrial/workshop interiors;
- large sports/minigame spaces;
- broader parks/nature;
- large mission buildings unavailable inside the chosen core.

Therefore **do not select all historic Potes merely because data exist**.

### Hard production envelope for the selected Potes core

The Worker starts from the previously studied ~180 × 220 m Potes reference box with ~145 real footprints, but must select one **contiguous smaller gameplay core**.

Target envelope:

- **70–100 exterior building footprints**; prefer 75–95.
- **Hard cap: 110** exterior building footprints without an explicit Owner amendment.
- coherent walkable network target: roughly **0.9–1.5 km** inside the selected core;
- normal third-person traversal from one meaningful edge to the opposite meaningful edge should target roughly **2.5–4.5 minutes** before later expansion exists;
- retain enough large/medium footprints to support later core gameplay, but do not inflate the boundary merely to collect hero buildings;
- aim for later capacity of roughly **15–25 enterable core buildings**, of which approximately **4–7** could support deep/hero treatment. These are capacity targets, not interior commitments in this WP.

If no contiguous Potes subarea can satisfy the product claim within the hard cap, **FAIL / OWNER DECISION**. Do not silently expand to the whole historic core.

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

## Workstream A — choose the bounded Potes core

Start from the known reference box, but evaluate contiguous candidate boundaries against product utility.

The chosen core should strongly prefer keeping a coherent sequence including as much as feasible of:

- the Torre del Infantado / plaza / river node;
- at least one meaningful bridge crossing;
- a compact commercial/social street sequence;
- one distinctive lane/callejón sequence;
- a meaningful Solana/Cimavilla or equivalent vertical/irregular sequence;
- at least one breathing space/plaza;
- enough residential fabric that NPC routines can plausibly originate/terminate inside the core;
- at least two natural outward interfaces where later expansion can connect without demolishing the core.

Do **not** select streets independently to maximise landmarks. The result must be one contiguous place whose boundary follows defensible physical edges: river, major street, block edge, slope transition, parcel/back boundary or another visible urban seam.

### Boundary alternatives

Produce at least **three candidate bounded cores** from the same pinned data.

For each candidate report:

- polygon / bounding dimensions / area;
- exact building count;
- walkable network length;
- meaningful edge-to-edge walking distance;
- block/parcel count;
- landmark/node coverage;
- street hierarchy coverage;
- number of bridges/river interfaces;
- distribution of building footprints;
- number >100, >200 and >400 m²;
- obvious expansion interfaces;
- what important Potes character is lost by the cut;
- expected reconstruction burden.

Then recommend one candidate **without exceeding the hard cap**.

Owner final selection is required before the Worker freezes the Master Reference.

## Workstream B — Master Building Ledger

For every building inside the Owner-selected core assign a stable immutable ID:

`POT-B001`, `POT-B002`, ...

Do not use current ENV01 plot IDs as final Potes authority.

For each building retain, as recoverable:

- source footprint polygon in real metric coordinates;
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

Partition only the Owner-selected Potes core into **3–5 natural production sectors**.

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

Within Sector 01 identify a **First Slice** of roughly **8–15 buildings** for the first physical reconstruction WP.

The Sector Pack must leave the visual Worker with factual questions already answered.

Required pack:

- sector polygon + metric coordinate transform;
- building ledger subset;
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
- Do not split one real building into several gameplay properties merely because ENV modules are narrow.
- Do not merge real exterior buildings for convenience during reference reconstruction.
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
- `BUILDING_LEDGER.csv`
- `BUILDING_LEDGER.json`
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

1. **Core Boundary Gate** — Owner chooses one of the measured bounded candidates.
2. **Sectorization Gate** — Owner confirms the selected core and production-sector division are understandable and appropriately scoped.

Do not ask the Owner to decide building geometry that external evidence can resolve.

## Acceptance

PASS requires:

- exact external source identities and reproducible acquisition/derivation are recorded;
- selected core is one contiguous Potes subarea;
- selected core remains <=110 exterior buildings unless explicitly amended by Owner;
- selected core is demonstrably smaller than the prior 145-footprint study box;
- boundary preserves a recognisable, coherent Potes urban sequence rather than a landmark collage;
- at least two credible outward expansion interfaces remain;
- every selected building has a stable ID and footprint;
- all production-relevant facts carry source/confidence state;
- no unknown facade fact is silently invented;
- streets/public spaces/elevations are independently reconstructible;
- ENV01 reuse is mapped as kit/component reuse rather than layout authority;
- core is partitioned into 3–5 natural production sectors;
- Sector Pack 01 is sufficiently complete for a fresh visual Worker;
- First Slice contains 8–15 exact buildings and representative environment complexity;
- Owner passes both boundary and sectorization gates;
- Worker strict pre-review finds no hidden expansion toward “all Potes”.

## FAIL

FAIL if any survives:

- Worker chooses all/most of the 145-footprint reference simply because it already exists;
- selected core exceeds 110 buildings without explicit Owner amendment;
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

It consumes the frozen Sector Pack 01 and reconstructs only its 8–15 building First Slice in an isolated Unity authority/output using ENV components under the 1:1 fidelity rules.

Later WPs may complete Sector 01 and subsequent sectors, but **no later casco WP may enlarge the Potes core boundary without a separate Owner-approved map-scope amendment**.

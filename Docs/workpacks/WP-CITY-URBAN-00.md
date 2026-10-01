# WP-CITY-URBAN-00 — Port-town topology + first keeper-block brief

Status: **COMPLETE / ACCEPTED**  
Class: PRODUCT DESIGN / CITY PROGRAMME  
Depends on: current `GAME_VISION.md` + `PORT_TOWN_WORLD_MODEL.md` + `VISUAL_BIBLE.md`  
Blocks: `WP-PROD-ENV-01`; feeds `WP-CITY-URBAN-01`

Accepted candidate: `e77e4b300e16bb2b880f8ace86ef488903fde450`  
Canonical PR: `#6`  
Reviewer PASS: `#5338907941`  
Implementation merge: `2fdd75d6db10d71e5676c0b0d1c161d100e11c15`  
Owner acceptance: `2026-09-28`  
DocSync: `Docs/evidence/WP-CITY-URBAN-00/DOCSYNC.md`

Accepted bounded amendment (2026-09-30): [`WP-CITY-URBAN-00R`](WP-CITY-URBAN-00R.md) revises scale, semantic-building/programme ownership and residual-space policy. This accepted WP's five roles, U01–U07/U08 optional, B0 programme/loops/access and provenance remain valid; its acceptance is not revoked or reissued. New bounds are owned by the rebaseline after its independent acceptance.

## Claim

juego-def already inherits a **reviewed port-town topology and first-block design baseline** from the accepted Juego2 `WP-CITY-URBAN-00`. This local WP exists to reconcile that solved design with current juego-def product truth and turn it into a clean factory handoff; it is **not** a greenfield repetition of the old planning exercise.

This WP is planning/product work. It does not build the block and does not choose asset-pipeline implementation.

## Binding local inputs

- `Docs/design/GAME_VISION.md`
- `Docs/design/PORT_TOWN_WORLD_MODEL.md`
- `Docs/design/VISUAL_BIBLE.md`
- `Docs/design/CITY_PRODUCTION_KNOWLEDGE.md`
- `Docs/design/FIRST_KEEPER_BLOCK_B0.md`

These local documents govern juego-def.

## Inherited accepted evidence from Juego2

Historical source evidence is the accepted Juego2 **PR #265**, `WP-CITY-URBAN-00 — port-town neighbourhood and first-block brief`, reviewed on exact candidate `189f675a5bc16b99106a2848cd637761e46d2ef1` with independent **PASS**.

That accepted work already established, at planning fidelity:

- five connected production neighbourhoods;
- B0 Mercado–Muelle as the first keeper block;
- B0 lodging, market/activity, shop/witness, commercial, port threshold, overlook and upper-route roles;
- public/service/private truth;
- direct + alternate routes and genuine cycles;
- expansion seams;
- third-person route/readability questions to be proved physically later;
- the rule that provisional plan coordinates are not keeper geometry.

Later Juego2 product amendments superseded details such as the provisional town name and nightlife distribution. Those current product decisions are already distilled into juego-def local documents and win over the historical wording.

### Default inherited town topology

Treat this as the **starting semantic adjacency**, not measured geometry and not a frozen final street map:

| Relation | Role |
| --- | --- |
| `MERCADO <-> MUELLE` | primary public commercial-to-port connection |
| `MERCADO <-> MUELLE` | secondary/alternate pedestrian lookout-waterside relation |
| `MERCADO <-> CASCO` | uphill old-town connection |
| `MERCADO <-> VIVIENDAS` | main everyday residential connection |
| `CASCO <-> VIVIENDAS` | quieter upper/residential relation |
| `MUELLE <-> TALLERES` | working-waterfront relation with public edge distinct from controlled yards |
| `VIVIENDAS <-> TALLERES` | work-to-home connector preventing universal Mercado routing |
| `CASCO <-> MUELLE` | optional future direct descent candidate; not required for B0 |

This gives a later genuine loop through `CASCO–MERCADO–MUELLE–TALLERES–VIVIENDAS–CASCO` without forcing every cross-town routine through one hub.

Reopen or replace this topology only if current juego-def product truth or later physical/play evidence materially contradicts it.

## Required outputs

### 1. Reconciled five-zone topology

Confirm or minimally amend the inherited topology for the current product:

- CASCO;
- MERCADO;
- MUELLE;
- TALLERES;
- VIVIENDAS.

Record only changes that are actually needed. Do **not** redraw the whole town merely to reproduce accepted work.

The retained topology must still make clear:

- which zones directly touch;
- which connections are primary vs secondary/quiet/service;
- waterfront orientation and deeper working-port continuation;
- where elevation changes plausibly separate/relate zones;
- where cross-town routines can flow without every trip passing through one universal hub;
- at least two credible later expansion/continuation seams.

Do **not** freeze a full street map of all five zones before production evidence exists.

### 2. B0 first-block reconciliation

Treat `FIRST_KEEPER_BLOCK_B0.md` as a migrated accepted baseline rather than an unproven blank-slate hypothesis.

Default remains **Mercado–Muelle seam** because the accepted Juego2 planning already showed why it exercises commercial frontage, working-port identity, public/controlled thresholds, elevation, ordinary population, investigation and route loops in one bounded piece.

Only replace B0 if new local evidence materially dominates that accepted result. Record the reason rather than silently drifting during ENV/CITY-URBAN-01 execution.

### 3. Route + game-space brief

Confirm that B0 retains enough to constrain production:

- semantic anchors/destinations;
- direct route and at least one meaningful cycle/alternate path;
- primary/secondary/quiet/service route roles where applicable;
- width bands as hypotheses, not immutable engineering dimensions;
- landmark/reveal/orientation intent;
- controlled vs public access truth;
- expansion/scenic seams;
- a coherent local elevation concept and key vertical relationships;
- likely conversation/observation/follow/chase pockets without implementing those systems.

Do not spend this WP re-proving the accepted B01..B10 graph unless it is being changed.

### 4. Place/programme brief

Confirm the physical homes required by B0, including at minimum:

- lodging/return anchor;
- market/everyday activity space;
- ordinary shop/witness threshold;
- commercial frontage fabric;
- public port-facing lead/reveal;
- public waterfront/overlook distinct from controlled work space;
- ordinary closed/scenic frontage;
- at least one shallow useful interior/threshold;
- quiet or lower-intensity pocket/route for contrast.

For each important place, state:

- rough importance: anchor / supporting playable / ordinary fabric / scenic;
- spatial depth: scenic / shell / shallow / deep / hero-layered;
- public / semi-private / private / service access expectations;
- whether it must be open/playable now, later, or only readable.

Importance and spatial depth must remain independent.

### 5. Production-demand matrix

This is the main genuinely unfinished output of the local WP: publish the demand handed to factories and classify current coverage.

#### ENV

At minimum classify need for:

- ordinary mixed/commercial facades;
- shopfront/service thresholds;
- lodging frontage;
- corners/terminations;
- street/kerb/steps/ramp/retaining families;
- quay/public working-water edge + railings;
- port/market props;
- closed ordinary frontage;
- shallow interior pieces;
- signage mounting + material/palette families.

#### CHAR

At minimum identify required civilian role families for B0 such as shop/market worker, port worker, older resident, younger/casual resident and ordinary service/office civilian.

#### ANIM

Prioritize locomotion, conversation, ambient/social, work/handling, object-use and bounded chase/reaction support relevant to B0.

#### DIALOGUE/UI

Require questioning/context, changed-return response and readable street/threshold interaction presentation.

For every material demand, use status `COVERED`, `FACTORY_REQUIRED`, `PROXY_ALLOWED_FOR_INTEGRATION`, or `DEFERRED_OUTSIDE_B0`.

## CITY-07 knowledge carried forward

This WP consumes the reusable principles in `CITY_PRODUCTION_KNOWLEDGE.md`, not old inland geometry.

In particular:

- planning geometry is a constraint/brief, not literal keeper mesh;
- final realization should use third-person compression/expansion/reveal and landmark framing;
- building/street/threshold relationships must be layered and coherent;
- B0 uses one coherent local elevation frame;
- local geometric tuning is allowed when roles/routes/access truth remain intact;
- topology/programme changes are not local polish and must amend this brief.

## Evidence / deliverables

Retain at minimum:

- final/current `FIRST_KEEPER_BLOCK_B0.md`;
- one reconciled semantic five-zone topology table/diagram, allowed to be the inherited topology unchanged;
- B0 route/anchor/programme confirmation or explicit amendment;
- factory-demand matrix with coverage statuses;
- unresolved questions intentionally deferred to physical realization/playtest;
- short provenance note identifying Juego2 PR #265 as accepted source evidence and any local divergences from it.

No Unity scene is required for PASS.

## PASS

PASS when:

- accepted Juego2 CITY-URBAN-00 knowledge has been explicitly consumed rather than silently redone;
- the five zones form a plausible connected town rather than five isolated themes;
- B0 is clearly retained or explicitly replaced with evidence;
- B0 has loops/alternate movement and is not only a corridor;
- working-port, commercial, quiet/ordinary and access-control roles are spatially credible;
- ENV can read the brief and know which reusable asset/assembly families to manufacture;
- CHAR/ANIM/DIALOGUE can read their near-term role demand;
- every material factory demand has a coverage status;
- enough is specified to prevent ENV from manufacturing a generic fantasy/asset-pack town, but local keeper geometry remains free to improve through play;
- no old inland geometry or H0/H1 architecture has become authoritative again.

## FAIL

FAIL if:

- the Worker treats the accepted Juego2 CITY-URBAN-00 result as if it never existed and spends the WP redesigning the same topology without causal evidence;
- the output is only five zone names with no meaningful connections;
- B0 remains a vague “make a nice port street” instruction;
- every meaningful place/route is funnelled through one hub;
- the factory-demand matrix is missing, so ENV still has to guess what the city needs;
- the plan attempts to freeze the full final town before production/play evidence;
- old Puente Viejo/CITY IDs are copied as final geography by convenience;
- superseded `Villa Bruma` naming or old nightlife allocation is reintroduced as current truth.

## Handoff

After PASS:

- `PROD-ASSET-00 + CITY-URBAN-00 -> PROD-ENV-01`;
- CHAR/ANIM continue from ASSET-00 and consume B0 role priorities as demand, not hard dependencies;
- `CITY-URBAN-01` later realizes B0 using the accepted factories and may tune local geometry while preserving this WP's functional truth.

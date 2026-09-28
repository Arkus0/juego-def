# WP-CITY-URBAN-00 — Port-town topology + first keeper-block brief

Status: **READY / PARALLEL**  
Class: PRODUCT DESIGN / CITY PROGRAMME  
Depends on: current `GAME_VISION.md` + `PORT_TOWN_WORLD_MODEL.md` + `VISUAL_BIBLE.md`  
Blocks: `WP-PROD-ENV-01`; feeds `WP-CITY-URBAN-01`

## Claim

juego-def has enough accepted spatial/product definition to tell the environment factory **what it must be capable of manufacturing** and to later realize the first keeper block without inventing a different city inside Unity.

This WP is planning/product work. It does not build the block and does not choose asset-pipeline implementation.

## Binding inputs

- `Docs/design/GAME_VISION.md`
- `Docs/design/PORT_TOWN_WORLD_MODEL.md`
- `Docs/design/VISUAL_BIBLE.md`
- `Docs/design/CITY_PRODUCTION_KNOWLEDGE.md`
- existing `Docs/design/FIRST_KEEPER_BLOCK_B0.md` draft/baseline

## Required outputs

### 1. Five-zone town topology

Publish/retain a compact semantic topology showing how:

- CASCO;
- MERCADO;
- MUELLE;
- TALLERES;
- VIVIENDAS

relate spatially and functionally.

It must be enough to understand:

- which zones directly touch;
- which connections are primary vs secondary/quiet/service;
- waterfront orientation and deeper working-port continuation;
- where elevation changes plausibly separate/relate zones;
- where cross-town routines can flow without every trip passing through one universal hub;
- at least two credible later expansion/continuation seams.

Do **not** freeze a full street map of all five zones before production evidence exists.

### 2. B0 first-block decision

Validate and, where necessary, amend `FIRST_KEEPER_BLOCK_B0.md` as the actual first keeper-block brief.

Default remains **Mercado–Muelle seam** because it exercises commercial frontage, working-port identity, public/controlled thresholds, elevation, ordinary population, investigation and route loops in one bounded piece.

If another location materially dominates, record the reason and update the brief rather than silently drifting during ENV/CITY-URBAN-01 execution.

### 3. Route + game-space brief

B0 must define enough to constrain production:

- semantic anchors/destinations;
- direct route and at least one meaningful cycle/alternate path;
- primary/secondary/quiet/service route roles where applicable;
- width bands as hypotheses, not immutable engineering dimensions;
- landmark/reveal/orientation intent;
- controlled vs public access truth;
- expansion/scenic seams;
- a coherent local elevation concept and key vertical relationships;
- likely conversation/observation/follow/chase pockets without implementing those systems.

### 4. Place/programme brief

Define the physical homes required by B0, including at minimum:

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

Publish the demand handed to factories.

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

For every material demand, allow status `COVERED`, `FACTORY_REQUIRED`, `PROXY_ALLOWED_FOR_INTEGRATION`, or `DEFERRED_OUTSIDE_B0`.

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
- one semantic five-zone topology diagram/table;
- B0 route/anchor/programme summary;
- factory-demand matrix with coverage statuses;
- unresolved questions intentionally deferred to physical realization/playtest.

No Unity scene is required for PASS.

## PASS

PASS when:

- the five zones form a plausible connected town rather than five isolated themes;
- B0 is clearly selected and bounded as the first keeper production customer;
- B0 has loops/alternate movement and is not only a corridor;
- working-port, commercial, quiet/ordinary and access-control roles are spatially credible;
- ENV can read the brief and know which reusable asset/assembly families to manufacture;
- CHAR/ANIM/DIALOGUE can read their near-term role demand;
- enough is specified to prevent ENV from manufacturing a generic fantasy/asset-pack town, but local keeper geometry remains free to improve through play;
- no old inland geometry or H0/H1 architecture has become authoritative again.

## FAIL

FAIL if:

- the output is only five zone names with no meaningful connections;
- B0 remains a vague “make a nice port street” instruction;
- every meaningful place/route is funnelled through one hub;
- the factory-demand matrix is missing, so ENV still has to guess what the city needs;
- the plan attempts to freeze the full final town before production/play evidence;
- old Puente Viejo/CITY IDs are copied as final geography by convenience.

## Handoff

After PASS:

- `PROD-ASSET-00 + CITY-URBAN-00 -> PROD-ENV-01`;
- CHAR/ANIM continue from ASSET-00 and consume B0 role priorities as demand, not hard dependencies;
- `CITY-URBAN-01` later realizes B0 using the accepted factories and may tune local geometry while preserving this WP's functional truth.

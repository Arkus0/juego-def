# CITY-URBAN-00 — current topology + B0 factory handoff

Status: **WORKER CANDIDATE / PRODUCT HANDOFF**  
Date: 2026-09-28  
Source WP: `Docs/workpacks/WP-CITY-URBAN-00.md`

## Bounded scale amendment — accepted 2026-09-30

[`WP-CITY-URBAN-00R`](../workpacks/WP-CITY-URBAN-00R.md) reopens only scale, plot-to-building ownership, interior programme/floors and residual-space policy. The accepted binding amendment is [`COMPACT_SEMANTIC_CITY_REBASELINE.md`](COMPACT_SEMANTIC_CITY_REBASELINE.md). Five zones mean unequal functional identities in one compact continuous town. The tables/edges/B0 roles below remain preserved accepted intent; their lengths/footprints are budgeted during rebaseline, not multiplied into five ENV01-sized maps. Final exact geometry stays physical authoring.

The CASCO V2 block is a prior spatial experiment, not a replacement for B0 Mercado–Muelle. ENV01 factory/visual-reference closure remains independent. After CITY-00R acceptance, future ENV02/B0 production consumes `FacadeCell != SemanticBuilding != InteriorProgramme`, programme-first interiors and zero unintentional exterior space; shallow pieces remain useful for tasks that fit them.

## Decision

Retain the accepted Juego2 CITY-URBAN-00 product/design result and reconcile it to current juego-def truth.

**Selected first keeper block remains B0 Mercado–Muelle.** No current juego-def evidence materially dominates or invalidates that choice.

The historical Juego2 plan is reused as planning evidence, not as shipping geometry. Current juego-def authorities supersede the provisional `Villa Bruma` name, old nightlife allocation and old H0/H1/CITY governance.

## Five-zone semantic topology

The town is one socially connected place, not five isolated level themes.

| Zone | Current role | Direct semantic relations | Elevation / spatial character | B0 relation |
| --- | --- | --- | --- | --- |
| `MERCADO` | repeat-visit commercial/everyday core | MUELLE primary + alternate; CASCO uphill; VIVIENDAS everyday road | middle urban shelf; dense frontage and junctions | **active B0 core** |
| `MUELLE` | working port/lonja/warehouses with bounded social layer | MERCADO primary + alternate; TALLERES working waterfront; optional future CASCO descent | lower working-water edge; public quay distinct from controlled work | **bounded public B0 seam** |
| `CASCO` | dense old town, civic/family uses, primary nightlife pole | MERCADO; VIVIENDAS; optional future MUELLE descent | generally uphill/older fabric; tighter lanes and landmarks | future continuation only |
| `VIVIENDAS` | ordinary residential fabric and quieter night contrast | MERCADO; CASCO; TALLERES | upper/quieter fabric, everyday home-to-work movement | future continuation only |
| `TALLERES` | repairs/workshops/warehouses, secondary alternative nightlife | MUELLE; VIVIENDAS | work/service edge between waterfront and inland connector | future continuation only |

### Town edge ledger

| ID | Relation | Class / truth |
| --- | --- | --- |
| `U01` | MERCADO <-> MUELLE | primary public commercial-to-port route; future service-vehicle detail belongs to realization |
| `U02` | MERCADO <-> MUELLE | secondary pedestrian lookout/waterside route; no freight shortcut through stairs |
| `U03` | MERCADO <-> CASCO | public uphill old-town route |
| `U04` | MERCADO <-> VIVIENDAS | main ordinary residential connection |
| `U05` | CASCO <-> VIVIENDAS | quieter public upper/residential relation |
| `U06` | MUELLE <-> TALLERES | working-waterfront relation; public edge remains separate from controlled yards |
| `U07` | VIVIENDAS <-> TALLERES | public work-to-home connector; prevents universal Mercado routing |
| `U08` | CASCO <-> MUELLE | optional future direct descent candidate; not required for B0 or current redundancy claims |

The later town can form a genuine cross-town loop:

`CASCO -> MERCADO -> MUELLE -> TALLERES -> VIVIENDAS -> CASCO`.

This supports routines such as home in Viviendas -> work in Muelle/Talleres -> errands in Mercado -> nightlife/social visit in Casco -> home without forcing every movement through one universal hub.

## B0 decision and boundary

B0 remains the **Mercado–Muelle seam** because one bounded block exercises unusually high production value at once:

- ordinary commercial frontage;
- lodging/return anchor;
- market/everyday activity;
- shop + witness threshold;
- port reveal and working-water identity;
- public vs controlled access truth;
- local vertical transition;
- direct + alternate movement;
- observation/follow/chase-supporting loop;
- expansion seams that remain useful when the town grows.

B0 is not a miniature complete town and does not require Casco, Viviendas or Talleres to exist physically yet.

## B0 route + anchor summary

Retain the semantic anchors and starting-width hypotheses in `FIRST_KEEPER_BLOCK_B0.md`.

### Required route truth

- direct public route: `L -> A -> S -> E -> P`;
- quieter/upper alternate: `L -> V -> O -> E -> P`;
- commercial/upper cycle: `A -> S -> E -> O -> V -> A`;
- port/observation cycle: `E -> P -> Q -> O -> E`;
- no public route crosses water, controlled work yard or a private/service interior;
- shop service access never becomes a public shortcut.

### Local elevation concept

This WP freezes **relative spatial roles**, not exact Y coordinates:

1. `L/A/S/E` occupy one broadly coherent commercial/market datum with modest local grade allowed;
2. `P/Q` sit on the lower public working-water/quay datum;
3. `O/V` form an intermediate/upper return layer that creates overview and route choice;
4. `Q -> O` is the explicit vertical transition by stairs/ramp/retaining response;
5. future CASCO/VIVIENDAS continuation rises inland/uphill from the active block;
6. all final thresholds, grades, retaining edges and street levels must be resolved in one coherent local elevation frame during keeper realization.

This preserves useful verticality without pretending the planning diagram has already solved comfortable physical grades.

## B0 place/programme

Importance and spatial depth remain independent.

| Place / surface | Importance | Spatial depth | Access expectation | B0 availability |
| --- | --- | --- | --- | --- |
| `L` lodging / return anchor | anchor | shallow/common now; deeper private layers may grow later | public entry + semi-private/private lodging layers | readable/playable now at required public/common surface |
| `A` market court / activity | anchor | open public game-space | public; occupation must leave a clear route | playable now |
| `S` everyday shop + witness | anchor | shallow playable | public customer room + distinct service threshold | playable now |
| B01–B03 commercial rows | ordinary fabric | shell/frontage, selected shallow thresholds | public street; most interiors closed | readable now; selected openings playable |
| `E` commercial corner / port reveal | supporting playable | open game-space | public junction | playable now |
| `P` public port threshold | anchor/supporting | open public edge | public route beside but not through controlled work | playable now |
| `Q` quay overlook | supporting playable | open public game-space | public, rail/boundary to water | playable now |
| `O` raised observation landing | supporting playable | open public game-space | public | playable now |
| `V` quiet/stepped landing | supporting/ordinary contrast | open public game-space | public | playable now |
| controlled port work yard | supporting scenic/readable | shell/scenic for B0 | service/private/controlled | readable now; deeper access later |
| blocked future seams | scenic context | scenic/partial shell | not traversable until admitted | readable only |

## Factory-demand matrix

These statuses describe **current production coverage**, not design completeness. `PROD-ASSET-00` and the lane factories remain responsible for proving reusable manufacture. A proxy may support integration but never counts as keeper coverage.

### ENV

| Demand | Status | Production intent |
| --- | --- | --- |
| ordinary mixed/commercial facades | `FACTORY_REQUIRED` | repeated coherent frontage, not dressed boxes |
| shopfront + distinct service threshold | `FACTORY_REQUIRED` | readable public door/service truth at third-person distance |
| lodging frontage / return-anchor language | `FACTORY_REQUIRED` | ordinary believable lodging, not hero-only bespoke shell |
| corners / terminations / junction-facing pieces | `FACTORY_REQUIRED` | avoid kit seams and flat repeated frontage |
| street / kerb / pavement / drainage-compatible edge family | `FACTORY_REQUIRED` | coherent public surface and building-ground contact |
| stairs / ramps / retaining family | `FACTORY_REQUIRED` | support Q–O and upper-route elevation coherently |
| quay / public working-water edge + railings | `FACTORY_REQUIRED` | working port, not leisure marina; truthful water boundary |
| port / market / shop / street props | `FACTORY_REQUIRED` | activity/readability after structural composition works |
| ordinary closed frontage | `FACTORY_REQUIRED` | density without every door opening |
| shallow interior / threshold pieces | `FACTORY_REQUIRED` | shop/witness and selected useful thresholds; a piece is vocabulary, not the universal complete interior programme |
| signage mounting / utilities / street furniture | `FACTORY_REQUIRED` | late-1990s/early-2000s ordinary town identity |
| damp northern material/palette families | `FACTORY_REQUIRED` | coherent Atlantic identity across reused sources |
| blocked/scenic continuation for future seams | `PROXY_ALLOWED_FOR_INTEGRATION` | temporary honest blockers/continuation are allowed before keeper finalization; dressed greybox is not keeper output |
| deep Muelle industrial interior set beyond B0 | `DEFERRED_OUTSIDE_B0` | deeper port production belongs to later blocks |
| Casco/Viviendas/Talleres full building breadth | `DEFERRED_OUTSIDE_B0` | only seam readability is required now |

### CHAR

| Demand | Status | Production intent |
| --- | --- | --- |
| market/shop worker family | `FACTORY_REQUIRED` | ordinary repeatable civilian recipe |
| dock/port worker family | `FACTORY_REQUIRED` | readable work role without costume caricature |
| older resident family | `FACTORY_REQUIRED` | silhouette/age variety |
| younger/casual resident family | `FACTORY_REQUIRED` | ordinary population variety |
| service/office civilian family | `FACTORY_REQUIRED` | shop/office/port-admin support |
| generic integration mannequin / temporary placeholder | `PROXY_ALLOWED_FOR_INTEGRATION` | allowed for systems wiring only; not keeper population coverage |
| bespoke Casco nightlife cast and later-district population breadth | `DEFERRED_OUTSIDE_B0` | later content/factory expansion |

### ANIM

| Demand | Status | Production intent |
| --- | --- | --- |
| civilian idle / walk / turn | `FACTORY_REQUIRED` | shared ordinary locomotion vocabulary |
| talk / listen / point / react | `FACTORY_REQUIRED` | street/shop questioning and social read |
| wait / look / lean / sit / stand | `FACTORY_REQUIRED` | everyday life and observation pockets |
| carry / handle / shop / port-work gestures | `FACTORY_REQUIRED` | working-town activity vocabulary |
| inspect / use / pickup / door interactions where sources permit | `FACTORY_REQUIRED` | reusable world-interaction support |
| surprise / recoil / run / bounded chase-support motion | `FACTORY_REQUIRED` | supports future B0 follow/chase beat |
| bootstrap player locomotion | `COVERED` | existing GC2 player/camera bootstrap proves player movement only; it does **not** satisfy civilian ANIM factory coverage |
| full combat choreography | `DEFERRED_OUTSIDE_B0` | B0 needs space for confrontation, not combat-production completion |

### DIALOGUE / UI

| Demand | Status | Production intent |
| --- | --- | --- |
| shop/witness questioning flow | `FACTORY_REQUIRED` | investigation content authoring path |
| person/photo/place/object context | `FACTORY_REQUIRED` | natural clue questioning rather than waypoint chain |
| changed-return response | `FACTORY_REQUIRED` | revisit consequence in same spatial surface |
| readable interaction prompt at street/threshold scale | `FACTORY_REQUIRED` | composition first, UI second |
| no-voice dialogue presentation suitable for busy street/interior threshold | `FACTORY_REQUIRED` | reusable presentation baseline |
| fully voiced/cinematic dialogue pipeline | `DEFERRED_OUTSIDE_B0` | not required for first keeper production path |

## Expansion / continuation seams

Retain four B0 seams as semantic continuation, not currently traversable streets:

- `arrival_w` — arrival + ordinary commercial continuation;
- `casco_n` — uphill continuation toward Casco/civic/nightlife fabric;
- `homes_ne` — ordinary residential continuation toward Viviendas;
- `quay_e` — deeper working-waterfront continuation toward Muelle/Talleres.

At least `casco_n` and `quay_e` must remain credible enough that early keeper content can grow without demolition. All four should be visually honest about current traversability.

## Divergences from accepted Juego2 CITY-URBAN-00

| Historical detail | juego-def current truth |
| --- | --- |
| provisional `Villa Bruma` name | **superseded**; final proper name undecided |
| Talleres described as primary later-night social edge | **superseded**; Casco is nightlife-primary, Talleres secondary/alternative, Mercado ordinary evening life, Muelle night-work-led |
| CITY-00/01/02/03/05/06 owner addenda as formal keeper prerequisites | **not inherited as governance**; this WP owns current planning semantics and CITY-URBAN-01 reopens it only for material topology/programme/access changes |
| exact provisional B0 coordinates/plan box | retained only as starting hypotheses, never shipping geometry |
| old inland Puente Viejo/Liébana source geography | historical only; not current geography |
| H0/H1/H2F architecture/lifecycle | not inherited |

Everything else material to the B0 topology/programme remains consistent with current juego-def product truth.

## Questions intentionally deferred to physical realization / later production

- exact shoreline/quay outline and controlled-yard footprint;
- exact route curves, comfortable grades and stair/ramp engineering;
- exact width tuning after third-person camera/collision tests;
- precise landmark object(s) and port reveal composition;
- exact facade/prop inventory selected from the accepted factory corpus;
- exact shop/lodging internal dimensions beyond required access/depth truth;
- final lighting/weather tuning across day/evening/night;
- exact B0 civilian identities/count above the later CITY-URBAN-01 minimum;
- exact NPC schedules and off-screen state implementation;
- whether optional `U08` Casco–Muelle direct descent is ever needed;
- final town proper name.

These are not missing CITY-URBAN-00 truths. They require asset, keeper-space, runtime, content or owner evidence that does not yet exist.

## Handoff

`PROD-ENV-01` should read this document plus `FIRST_KEEPER_BLOCK_B0.md` as the current **what to manufacture** demand after `PROD-ASSET-00` establishes the real searchable source substrate.

CHAR/ANIM/DIALOGUE/UI may consume the role priorities immediately as product demand, while their own WPs remain authoritative for how the content is manufactured.

`CITY-URBAN-01` may tune local keeper geometry aggressively where useful, but must amend the current CITY handoff (including CITY-00R once accepted) if it needs a material change to route connectivity, access class, anchor programme, controlled-port boundary, expansion seam, major elevation concept or compact scale budget.

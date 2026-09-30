# B0 Mercado–Muelle — first keeper block production brief

Status: **CURRENT PRODUCT / PRODUCTION DEMAND BASELINE**  
Date: 2026-09-28

Compact-city amendment proposed 2026-09-30: [`COMPACT_SEMANTIC_CITY_REBASELINE.md`](COMPACT_SEMANTIC_CITY_REBASELINE.md), through `WP-CITY-URBAN-00R`. B0 remains Mercado–Muelle; its anchors, routes, access and port/elevation roles below are preserved. CASCO-V2 is a preceding programme/scale experiment, not B0 integration acceptance. Illustrative coordinates and frontage rows do not determine separate buildings or justify growing the city to fit the old diagram.

## Purpose

This document migrates the useful **what to build** knowledge from Juego2 CITY into juego-def without importing the old inland pilot, H1/H2F lifecycle or historical CITY governance.

It is the demand brief consumed by the graphical/content factories. The factories should industrialize the assets and vocabulary needed to realize this block and later related neighbourhood content.

## Source disposition

Distilled primarily from the **accepted Juego2 `WP-CITY-URBAN-00`** (`PR #265`, reviewed candidate `189f675a5bc16b99106a2848cd637761e46d2ef1`, independent reviewer PASS), plus reusable accepted CITY-00..07 planning/game-space knowledge and later product amendments.

That accepted WP already established the port-town neighbourhood transition and the B0 Mercado–Muelle first-block brief as coherent planning evidence. juego-def therefore **inherits the solved product/design knowledge**, but not Juego2's old causal-owner bureaucracy, H0/H1/H2F architecture or the requirement to preserve provisional coordinates as shipping geometry.

The executable `WP-CITY-URBAN-00` in juego-def is a **local reconciliation/production-handoff checkpoint**, not a greenfield attempt to invent the same town again. It may amend this brief only where current juego-def product truth, production evidence or factory demand requires it.

### Migrated as product truth / design input

- final setting: fictional northern-Spain working port town, late 1990s / early 2000s; compact playable scale under the current Owner direction;
- five production zones: MERCADO, MUELLE, CASCO, VIVIENDAS, TALLERES;
- first keeper urban block: **B0 Mercado–Muelle** unless new local evidence materially overturns it;
- compact density, recurring social routes, ordinary places and working waterfront;
- B0 functional programme and route/loop concept;
- public/service/private access distinction;
- expansion seams and apparent continuation;
- third-person game-space design principles described below.

### Historical / not migrated as authority

- inland Puente Viejo/Liébana geometry, IDs, crossings, route costs, river/arroyo masks or exact seed polygons;
- H1/H2F prerequisites;
- CITY-04 remeasurement bureaucracy tied to the historical greybox;
- old node/edge owners as governance mechanism;
- exact provisional B0 coordinates as immutable shipping coordinates;
- the provisional `Villa Bruma` name, which is superseded: the final town proper name remains undecided.

The B0 layout below is therefore a **production brief with measurable starting hypotheses**. `WP-CITY-URBAN-00` may reconcile it before ENV production; later keeper realization may tune local geometry while preserving the accepted roles, loops and access truth.

## B0 product role

B0 is an ordinary commercial block touching the public edge of the working port. It should already support the future investigation slice without implementing all gameplay systems yet.

It must provide spatial homes for:

1. **lodging / return anchor**;
2. **market court / small everyday activity**;
3. **everyday shop + witness threshold/interior**;
4. **commercial frontage run**;
5. **port-facing lead/reveal**;
6. **public port threshold** distinct from controlled work space;
7. **quay overlook / working-water observation**;
8. **raised observation/chase choice**;
9. **loop/return route** so the block is learned rather than consumed as a corridor;
10. future seams toward Casco, Viviendas, deeper Muelle/Talleres and arrival/ordinary commercial continuation.

B0 is not the whole town and does not require every future zone to be playable or resident.

## Spatial anchors

Use these semantic anchors. Coordinates are starting-layout hypotheses only.

| ID | Role | Approx starting frame `(u,v)` m |
| --- | --- | ---: |
| `L` | lodging door + changed-return anchor | `(30,105)` |
| `A` | market court / activity floor | `(75,100)` |
| `S` | everyday shop public door + witness threshold | `(115,105)` |
| `E` | east commercial corner + port reveal | `(160,100)` |
| `P` | public port-edge threshold, outside controlled yard | `(160,40)` |
| `Q` | rail-protected quay overlook | `(105,35)` |
| `O` | raised observation landing + chase/follow choice | `(105,65)` |
| `V` | stepped-lane / quieter landing | `(55,65)` |

The illustrative working-water edge lies south of the block. No route crosses water and no controlled work yard becomes a public shortcut.

## Route grammar

The block needs both a direct route and real cycles.

| Edge | Role | Starting clear-width target |
| --- | --- | ---: |
| `B01 L–A` | ordinary commercial approach | `5–7 m` |
| `B02 A–S` | commercial frontage / shop approach | `6–8 m` |
| `B03 S–E` | commercial frontage / port reveal build-up | `6–8 m` |
| `B04 E–P` | main public port approach | `5–7 m` |
| `B05 P–Q` | rail-protected waterfront walk | `3–5 m` |
| `B06 Q–O` | stepped/ramped ascent | `2–3 m` |
| `B07 O–E` | upper return lane | `3–4 m` |
| `B08 O–V` | upper parallel lane | `3–4 m` |
| `B09 V–A` | stepped market connector | `2–3 m` |
| `B10 L–V` | quieter second approach | `3–4 m` |

Desired cycles:

- `A–S–E–O–V–A` — commercial/upper loop;
- `E–P–Q–O–E` — port/observation loop;
- direct commercial-to-port route `L–A–S–E–P`;
- alternative quieter/upper approach `L–V–O–E–P`.

Exact curves, slopes, facade placement and junction shaping are resolved during keeper realization, not frozen by this document.

## Access + interior rules

- shop public room is a shallow useful interior/threshold; service access remains distinct;
- lodging may have deeper private/common layering later but must read as a believable return anchor;
- public port edge remains physically/readably separate from controlled yard/work areas;
- not every facade opens; every semantic building has identity/use, including closed fabric; several FacadeCells may belong to one mixed-use building;
- shallow shop/witness is a useful programme, not a fixed cubicle size: occupation, camera, access and service determine its dimensions; visual and playable floors may differ;
- every exterior gap/rear/setback has deliberate function or is absorbed/redesigned, under the compact-city amendment;
- an interior cannot be used to fake a public shortcut that does not exist in the street graph;
- thresholds must be spatially readable before interaction UI is invoked.

## Expansion seams

B0 should imply continuation without pretending future zones already exist.

- `arrival_w`: ordinary arrival/commercial continuation west of lodging/market;
- `casco_n`: uphill/old-town continuation toward CASCO;
- `homes_ne`: ordinary residential continuation toward VIVIENDAS;
- `quay_e`: deeper working waterfront toward MUELLE/TALLERES.

Use blocked/scenic continuation, rooflines, street alignment, sound/light/landmark cues and partial geometry honestly. Do not create invisible traversable streets.

## Game-space realization principles migrated from CITY

The keeper block must feel like an authored third-person level, not a planning diagram extruded into Unity.

### Composition

- deliberate compression -> expansion -> reveal rhythm;
- readable corners, destinations and route choices;
- framed views and landmark emphasis;
- occlusion used to stage discovery rather than hide navigation;
- nooks/threshold pockets where conversation, observation or waiting can occur;
- ordinary fabric between authored moments so the town is believable rather than theme-park dense.

### Verticality

- use one coherent local elevation frame;
- streets, thresholds, stairs/ramps, retaining edges and interior floors must relate intentionally;
- elevation change should produce route character and views, not arbitrary per-building Y offsets;
- player comfort and chase/follow readability matter alongside visual interest.

### Third-person usability

Design should spatially support:

- walking/exploration;
- stopping for conversation without blocking the route;
- following someone while retaining partial visual contact;
- searching/observing from alternate positions;
- a bounded chase choice around the `E–P–Q–O` cycle;
- future confrontation staging without requiring an arena-shaped plaza.

No gameplay system is required merely to prove those affordances.

### Route learning + orientation

- the player should learn the block through storefronts, water/work cues, elevation and landmarks;
- genuine cycles matter more than arbitrary shortcuts;
- dead ends/seams need a visual or experiential payoff;
- door/threshold readability should come from composition first and UI second;
- future measured player traversal time is different from planning-distance intuition.

## Factory demand map

### ENV factory must be able to produce

- ordinary mixed commercial facades;
- corners/terminations;
- shopfront + service threshold;
- lodging frontage/door language;
- stairs/ramps/retaining/railings;
- quay/public working-water edge;
- port/market props and signage mounting;
- closed ordinary frontage fabric;
- small shallow interior/threshold pieces;
- palette/material families supporting damp northern working-town identity.

### CHAR factory must cover at least

- market/shop worker;
- dock/port worker;
- older resident;
- younger/casual resident;
- ordinary service/office worker;
- nightlife-neutral everyday civilian silhouettes.

### ANIM factory should prioritize

- idle/walk/turn;
- talk/listen/point/react;
- wait/look/lean/sit/stand;
- carry/handle/work/shop/port gestures;
- inspect/use/pickup/door where source permits;
- surprise/recoil/run/chase-support motions where source permits.

### DIALOGUE/UI factory should support

- shop/witness questioning;
- person/photo/place/object context;
- changed return response;
- readable interaction prompts and no-voice presentation in a busy street/interior threshold.

## Keeper acceptance intent

The eventual `WP-CITY-URBAN-01` realization may tune the accepted starting layout, but must preserve the block's functional truth unless `CITY-URBAN-00` is explicitly amended:

- Mercado -> Muelle relationship reads clearly;
- direct and alternative routes exist;
- public/service/private boundaries remain truthful;
- lodging, market, shop/witness, port lead, overlook and observation/chase roles survive;
- the block supports revisits and future investigation/action content;
- expansion seams remain available;
- final result is worth keeping and extending as shipping city content.

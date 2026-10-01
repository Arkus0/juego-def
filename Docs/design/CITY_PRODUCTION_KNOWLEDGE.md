# CITY production knowledge — what the factories must serve

Status: **MIGRATED PRODUCT KNOWLEDGE / CURRENT juego-def INPUT**  
Date: 2026-09-28

## Purpose

Preserve the useful spatial/product knowledge from Juego2 CITY without importing its old inland geography, H0/H1 authority model or historical review bureaucracy.

The key separation for juego-def is:

- **CITY says what kind of place the game needs and how it should work spatially.**
- **ENV/CHAR/ANIM/UI factories say how to manufacture the reusable content that realizes it.**
- **CITY-URBAN-01 realizes the first keeper block and may tune local geometry through third-person iteration.**

The current first-block demand brief is [`FIRST_KEEPER_BLOCK_B0.md`](FIRST_KEEPER_BLOCK_B0.md).

Owner direction 2026-09-30 is one compact continuous city of five unequal functional identities. The accepted compact-city baseline [`COMPACT_SEMANTIC_CITY_REBASELINE.md`](COMPACT_SEMANTIC_CITY_REBASELINE.md) / `WP-CITY-URBAN-00R` owns the revised scale, semantic grammar and zero-residual-space rule. Existing CITY topology/B0 and ENV01 visual vocabulary remain useful; the CASCO pilot tests their physical composition before further scale.

## Knowledge retained from CITY-00..06

### Spatial constitution

Retain the underlying principles, not the old selected map:

- choose compact, distinctive neighbourhoods and meaningful connections before chasing acreage;
- loops and alternate routes are preferable to one hub-and-spokes graph;
- waterfront/port, commercial, residential, old-town and work/service areas need functional reasons to exist;
- preserve credible expansion seams so early keeper content remains usable as the town grows;
- playable fabric and scenic/backdrop continuation are distinct;
- at least some intentionally quiet fabric is necessary for contrast.

Old kilometre-square targets, inland river topology and exact route IDs are not inherited.

### Mobility and route grammar

The useful movement vocabulary is retained:

- primary routes;
- secondary/local routes;
- quiet routes;
- service/back routes;
- stairs/ramps/elevation transitions;
- meaningful junctions/chokepoints;
- alternate paths suitable for following, searching and time-sensitive movement.

Traversal should create route choice and place learning without becoming empty commute. Port/work routes must also make sense as ordinary logistics, not only as story corridors.

### Place importance and spatial depth are independent

Reuse the conceptual separation from CITY-02 without importing its old location matrix.

A place may be narratively/systemically important but physically shallow, or spatially deep but narratively ordinary. For planning, distinguish roughly:

- **importance:** anchor / supporting playable / ordinary fabric / scenic context;
- **spatial depth:** scenic only / shell-frontage / shallow playable / deep playable / hero layered.

Do not turn “living city” into every door open, every prop interactive or every visible NPC deeply persistent.

### Streets, parcels and building families

Reuse the CITY-05 production idea:

`module -> visual assembly / FacadeCell -> SemanticBuilding -> programme-designed place -> street segment`

**FacadeCell != SemanticBuilding != InteriorProgramme.** Several narrow visual bodies can share one larger coherent property/programme. Do not derive playable rooms or floors mechanically from the number of frontage bays/windows, and do not count visible cells as city properties. Closed buildings still have concrete use. Each exterior pocket requires physical intent/ownership/access evidence; decoration or a category alone cannot resolve it.

Near-term families should cover as demanded by the actual port town:

- ordinary mixed frontage;
- narrow/historic lane;
- market/plaza edge;
- port/work edge;
- service/back edge;
- residential street;
- workshop/warehouse fabric;
- stairs/retaining/elevation transitions;
- mixed-use house/shop;
- shop/service;
- bar/social venue;
- lodging/residential;
- workshop;
- warehouse/port building;
- selected civic/hero places.

These are semantic families for the ENV factory, not a requirement for unique bespoke buildings everywhere.

### Interiors and discovery

Retain selective **depth** rather than universal deep interiors (amended 2026-10-01: a majority — target 60 % — of semantic buildings is walkable, deep programmes stay ≤20 %; see [`CITY_MASTER_PLAN_V1.md`](CITY_MASTER_PLAN_V1.md)):

- public surface;
- semi-private/private layers;
- service/back-of-house routes;
- vertical spaces when useful;
- storage/rear court/basement only where useful;
- social/temporal discovery;
- authored, systemic or hybrid discovery where real gameplay later supports it.

Ordinary homes/workplaces remain valuable even without secrets. Important locations may support multiple truthful ways of learning/accessing them, but do not promise systemic routes before GC2/local gameplay actually exists.

## Knowledge retained from CITY-07 realization work

The old CITY-07 target was the inland Puente Viejo/Casco/Bar pilot, which is **not** migrated as geography. Its strongest game-space lessons are retained.

### Planning geometry is not keeper geometry

A validated route/brief constrains meaning, access and broad dimensions. It does not force final Unity geometry to be a literal extrusion of proxy boxes.

Keeper realization may tune local geometry to improve:

- coherent streets/kerbs/ground;
- thresholds and building-ground contacts;
- setbacks, retaining edges and stairs/ramps;
- compression -> expansion -> reveal rhythm;
- occlusion and framed views;
- landmark emphasis;
- conversation/observation pockets;
- route legibility at third-person scale.

A local adjustment that preserves the accepted route/programme is ordinary level-design iteration. A new connection, removed access role, new shortcut or changed programme belongs back in CITY planning.

### Layered building assembly

A keeper building should be understandable as a construction, not a decorated cuboid:

1. site/terrain datum;
2. footprint + principal access level;
3. base/plinth/foundation/retaining response;
4. massing/storey relationships;
5. facade/wall hosts + corners/terminations;
6. openings + doors/windows;
7. roof/eaves/termination + roof-wall meeting;
8. public/service/private thresholds;
9. building-ground/street connection;
10. dressing only after structure and transitions are coherent.

Useful relations include `HOSTS`, `FILLS`, `CAPS/MEETS`, `SUPPORTED_BY/ATTACHED_TO`, `TRANSITIONS_TO` and `CLEAR_OF`. These are design relations, not a demand for a new runtime schema.

### Layered street assembly

A keeper street should resolve:

1. terrain/support datum;
2. traversable surface;
3. width/grade/elevation intent;
4. kerb/pavement/drainage/readable edge where applicable;
5. retaining/building contacts;
6. threshold transitions;
7. collision/traversable-surface ownership;
8. props/vegetation after the surface system is coherent.

Do not hide overlapping proxy planes/cubes under materials and call them keeper streets.

### Shared elevation frame

Use one coherent local vertical frame per keeper block/connected area. Buildings may have convenient local origins, but public thresholds, street levels, steps/ramps and retaining responses must relate to the same authored game-space.

Avoid flattening/re-sloping public ground independently for every building just to make asset placement easy. Cross-sections/longitudinal profiles are useful wherever vertical relationships are hard to judge from plan view; they are not mandatory paperwork for every metre of street.

### Third-person oracle

Review from gameplay camera, not only top-down:

- massing/silhouette;
- facade/opening depth;
- roof-wall integration;
- ground/threshold contacts;
- corners/junctions/setbacks;
- coherent public surface;
- navigation/landmark readability;
- conversation/follow/search/chase affordances;
- ordinary fabric between authored beats.

## What is explicitly NOT migrated

- Puente Viejo, old river/ford/crossing geometry or inland seed IDs;
- exact old CITY node/edge matrices;
- H1/H2F prerequisites and Arkus authority contracts;
- historical differential-ledger/review bureaucracy;
- old measured Y values, route costs or seed polygons;
- requirement to preserve every old accepted CITY conclusion in juego-def;
- assumption that all future city topology is already decided.

## Current juego-def ownership

- `PORT_TOWN_WORLD_MODEL.md` owns current five-neighbourhood product roles.
- `WP-CITY-URBAN-00` owns the accepted topology/B0 handoff; `WP-CITY-URBAN-00R` makes the bounded scale/semantic-space amendment, without reopening unrelated accepted truths.
- `FIRST_KEEPER_BLOCK_B0.md` is the concrete first factory customer.
- `PROD-ENV-*` owns scalable environment manufacturing/assembly methods.
- `WP-CITY-URBAN-01` owns physical keeper realization of B0 using accepted factories.

The result should be a city that is **designed before it is mass-produced, but not over-specified before it is played**.

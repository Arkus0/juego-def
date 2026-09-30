# Port-town world model

Status: **CURRENT PRODUCT PLANNING MODEL — COMPACT CITY REBASELINE IN PROGRESS**  
Date: 2026-09-30 (compact semantic-city amendment; preserves accepted five-zone roles)

## Setting scale

The final setting is a **compact but substantial fictional port town in northern Spain**, with a late-1990s / early-2000s feel. It should read socially as a comarca hub rather than an anonymous major city: repeated faces, family/business connections, rumours, reputations and reasons to encounter the same people across days. Production should favor unusually high consequence per metre over geographical breadth.

The final proper name is **undecided**. Do not bake `Villa Bruma` or any other provisional name into keeper signage, assets or UI.

This document owns neighbourhood **roles**. `Docs/workpacks/WP-CITY-URBAN-00.md` owns the executable topology/first-block planning handoff; reusable migrated spatial knowledge lives in `CITY_PRODUCTION_KNOWLEDGE.md`.

## Five production neighbourhoods

These are production/world-organization **identities**, not five equal-size maps or hard municipal districts. They belong to one continuous compact town and may overlap perceptually at their seams:

- `CASCO` — dense old town; civic/family/day uses plus the **primary nightlife pole** in a bounded lower/central strip.
- `MERCADO` — main repeat-visit commercial/everyday zone; cafés, ordinary bars, restaurants and shopping.
- `MUELLE` — working port/lonja/warehouses/crews; night activity is driven first by work, shifts and a bounded port-social layer.
- `TALLERES` — repairs, workshops, warehouses and small industry; **secondary/alternative nightlife** such as worker bars, music/rehearsal, cheap late food and marginal hangouts.
- `VIVIENDAS` — lower-intensity residential fabric and quieter night contrast.

Nightlife is a **city layer**, not a sixth dedicated district. Casco is primary; Talleres secondary; Mercado has ordinary evening life; Muelle has night work; Viviendas quiets down.

### Compact semantic-city scale (owner amendment 2026-09-30)

Physical ENV01 evidence showed that visual parcel grain and gameplay building grain must be separated before city breadth continues.

Planning orientation, subject to the CASCO-V2 pilot:

- approximately **90–130 SemanticBuildings across the whole town**, not hundreds per zone;
- approximately **30–40 SemanticBuildings in CASCO**;
- five neighbourhood names remain five functional identities, but **must not become five ENV01-sized districts**;
- CASCO should plausibly occupy about **15–25% of final urban playable surface**, with uneven zone sizes and soft transitions;
- current ENV01's ~196x236 m extent is reference evidence, not a required final footprint;
- effective CASCO compression of roughly **30–45%** is allowed where it removes low-value breadth while preserving route identity, views and character.

The structural model is:

`FacadeCell != SemanticBuilding != InteriorProgramme`

Several apparent narrow historic frontage bodies may belong to one larger semantic/gameplay property. Every retained urban area must have a deliberate role; generator provenance such as `yard` or `huerta` does not by itself prove gameplay value.

### CASCO reference, terrain and water (owner decisions 2026-09-28, district approved 2026-09-29)

- **Real-town reference, fictional town.** The CASCO takes the historic core of a real Cantabrian town (Potes,
  Liébana) as its **morphology and look reference** ("mini Potes": lebaniego old-town architecture). The reference
  donates structure — street network, block and plot grain, node/plaza logic, slopes — and a regional look, studied
  from primary data (OSM, IGN MDT05). It never donates names, signage, named landmarks or geography: the setting stays
  this fictional port town and the old inland/Potes setting is **not** restored. Method and rules:
  [`../production/ENV_COMPOSITION_RULES.md`](../production/ENV_COMPOSITION_RULES.md); study and built district:
  [`../evidence/WP-PROD-ENV-01/CASCO_REFERENCE_STUDY.md`](../evidence/WP-PROD-ENV-01/CASCO_REFERENCE_STUDY.md).
- **Soul, not trace.** The playable CASCO keeps the spine, 2–3 characterful secondary streets, 1–2 descents to the
  water and a few corners; everything else is simplified for walking, NPC routes and legibility (plaza, bar, tower /
  town hall, way to the port).
- **The town rises from the port** towards Casco and Viviendas. Route grades by network length: about **70 %
  comfortable, 20 % perceptible, 10 % steep or stairs**; stairs are an accent. District terrain characters: Casco short
  slopes, stairs and small terraces; Mercado flatter with stepped plazas; Muelle almost flat with service ramps;
  Talleres gentle slopes and vehicle ramps; Viviendas hillside terraces and retaining walls.
- **A small/medium river**, partially channelled between stone walls, runs along one edge of the Casco (houses tight on
  the water, 1–2 small stone bridges, a plaza opening to it) and continues down to the port, where it opens or meets
  the sea. It is an edge, never a wide urban frontier. The built CASCO district leaves this riverside seam towards the
  port open (candidate for the optional Casco–Muelle descent `U08` of `CITY_URBAN_00_HANDOFF.md`).

## First keeper block authority

The concrete first-block demand baseline is [`FIRST_KEEPER_BLOCK_B0.md`](FIRST_KEEPER_BLOCK_B0.md), subject to validation/amendment by `WP-CITY-URBAN-00` before ENV production.

B0 is the Mercado–Muelle seam: lodging/return anchor, market/activity, everyday shop + witness threshold, commercial run, public port approach, quay overlook, upper/alternate route and truthful expansion seams. Graphical/content factories should prioritize this demand before generic breadth.

## Cross-town routine principle

People may live in Viviendas, work in Muelle or Talleres, shop/eat in Mercado, visit Casco at night and return home. Routine design should produce cross-town social reuse rather than five isolated populations.

`CITY-URBAN-00` must preserve this premise without forcing every trip through one universal hub.

## NPC depth and routine axes

Narrative depth and routine complexity are separate axes.

Planning orientation, not a shipping gate:

- roughly **80–120 visible person identities** at whole-town scale if production proves affordable;
- around **10–15 Tier A** important characters with the deepest story/state treatment;
- around **20–40 Tier B** recurring interactives;
- remaining population is lighter Tier C/background;
- a future target of roughly **60–100 routine-bearing people across the whole town** is acceptable only if authoring/QA cost proves manageable.

A routine-bearing NPC may have time/day → zone/POI/activity transitions without bespoke relationships, memory graphs or unique animations.

## Active-area scaling principle

Do not assume all planned NPCs must be graphically active at once. The active neighbourhood and necessary continuity seam own full Unity/GC2 realization: body, Animator, navigation, interaction and immediate reactions. Outside it, future implementation may use lighter schedule/state representation if real gameplay proves that necessary.

This is a scaling option, not authorization to rebuild H0/H1 or create a universal streaming framework. GC2/Unity is tried first; persistent cross-area state is added only when a concrete playable case requires it.

## First urban slice

Target future slice: **20–30 minutes of real first-play time**.

Working route:

1. leave lodging with a photograph/clue related to a murder;
2. question people in a commercial area;
3. learn a lead toward the port;
4. obtain access through a person, small job or another legible route;
5. spot/follow a suspect;
6. chase after being discovered;
7. confrontation or bounded fight;
8. gain a key/new lead;
9. return to a previous place and see a changed response;
10. open another thread.

A short everyday activity such as a bar game, arcade interaction, training or job can provide a reason to linger and may influence an encounter when authored.

## Spatial quality rules

- Compact density beats surface area.
- Streets and interiors should be learned through landmarks, storefronts, thresholds, stairs, alleys and activity.
- The player should repeatedly revisit places at different times and for different reasons.
- A district exists because it creates differentiated gameplay/social rhythm, not merely because the map needs more area.
- Meaningful loops/alternate routes beat a universal central connector.
- Quiet/ordinary fabric is necessary contrast, not wasted area.
- Public/service/private and scenic/playable distinctions must remain truthful.
- Keeper geometry should be deliberately composed for third-person route rhythm, threshold readability, orientation, sightlines and useful verticality; a planning diagram is not a level.

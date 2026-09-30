# Port-town world model

Status: **CURRENT PRODUCT PLANNING MODEL**  
Date: 2026-09-28 (compact-city Owner direction and architecture candidate: 2026-09-30)

## Setting scale

The final setting is a **compact, deliberately authored fictional port town in northern Spain**, with a late-1990s / early-2000s feel. Its social role as a town/comarca hub survives through repeated faces, family/business connections, rumours and reputations; that role does not require a large playable footprint.

The final proper name is **undecided**. Do not bake `Villa Bruma` or any other provisional name into keeper signage, assets or UI.

This document owns neighbourhood **roles**. `Docs/workpacks/WP-CITY-URBAN-00.md` owns the executable topology/first-block planning handoff; reusable migrated spatial knowledge lives in `CITY_PRODUCTION_KNOWLEDGE.md`.

## Five production neighbourhoods

These are five functional identities within **one continuous compact city**, with soft boundaries and very unequal sizes, not five equivalent maps or five repetitions of the ENV01 CASCO district:

- `CASCO` — dense old town; civic/family/day uses plus the **primary nightlife pole** in a bounded lower/central strip.
- `MERCADO` — main repeat-visit commercial/everyday zone; cafés, ordinary bars, restaurants and shopping.
- `MUELLE` — working port/lonja/warehouses/crews; night activity is driven first by work, shifts and a bounded port-social layer.
- `TALLERES` — repairs, workshops, warehouses and small industry; **secondary/alternative nightlife** such as worker bars, music/rehearsal, cheap late food and marginal hangouts.
- `VIVIENDAS` — lower-intensity residential fabric and quieter night contrast.

Nightlife is a **city layer**, not a sixth dedicated district. Casco is primary; Talleres secondary; Mercado has ordinary evening life; Muelle has night work; Viviendas quiets down.

### Compact semantic city amendment

Owner direction: **FacadeCell != SemanticBuilding != InteriorProgramme**. Several narrow historical facade bodies may belong to one larger functional building. Every semantic building has identity/use; selective accessible interiors exist for a reason, and a minority supports deeper programmes. Visual storeys and playable floors may differ. No space between/around buildings may remain a procedural leftover: it needs a defensible street, passage, court, garden, terrace, service, loading, river-edge, grade or setback function, or is absorbed/redesigned.

~90–130 semantic buildings town-wide and ~30–40 in CASCO, often 2–4 visual bodies per building, are **starting directions, without minimum quotas**. The proposed quantitative guardrails, counting rules, preserve/reopen ledger and dependency change live once in [`COMPACT_SEMANTIC_CITY_REBASELINE.md`](COMPACT_SEMANTIC_CITY_REBASELINE.md), awaiting independent acceptance through `WP-CITY-URBAN-00R`. No complete ENV01 conversion is authorized here.

CASCO preserves ENV01's lebaniego/Potes morphology and visual character as reference: irregular streets, regional materials, roof/eave rhythms, slopes/terraces, a small/medium channelled river at the edge, bridges and a descent toward the working port. The town rises from the port; ~70/20/10 comfortable/perceptible/strong-or-stairs by network length remains intent. The reference donates soul and structure, never town names or named landmarks. Its current evidence lives on the exact ENV01 branch reference identified in the rebaseline source note; that visual direction does not imply formal ENV01 PASS or final acceptance of its 311-plot scale.

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

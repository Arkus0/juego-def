# Roadmap jugable

Status: **BOOTSTRAP DONE / NEXT: PROD-ASSET-00 + CITY-URBAN-00** — authoring path `BOUNDED_OPERATOR` (MCP for Unity), owner-confirmed

## Immediate sequence

1. ~~**Knowledge migration**~~ — done.
2. ~~**Production authoring decision**~~ — `BOUNDED_OPERATOR` adopted.
3. ~~**Bootstrap Unity + GC2 Core**~~ — done: Unity 6000.3.24f1 + URP 17.3 + GC2 Core 2.19.61, player/camera working in Play Mode.
4. **Two parallel foundations for production:**
   - `PROD-ASSET-00` — existing-pipeline spikes + searchable catalogue, lineage, intake and validators;
   - `CITY-URBAN-00` — five-zone topology + final B0 Mercado–Muelle route/programme/elevation + factory-demand matrix.
   **← NEXT**
5. **M0 fixture + Dialogue in parallel** — small gameplay-integration fixture and dialogue-authoring factory; neither blocks asset/CITY research.
6. **Factories:** ENV starts after `ASSET-00 + CITY-URBAN-00`; CHAR/ANIM can start after ASSET-00 while consuming B0 role priorities.
7. **Factory scale proofs** — multi-scene ENV, civilian batch and animation runtime/batch; UI follows Dialogue.
8. **B0 Keeper Block (`CITY-URBAN-01`)** — physical third-person realization of the accepted city brief using the factories.
9. **Production Factory Gate (`PROD-LOOK-GATE`)** — fresh brief challenge proves content can now be produced without foundational pipeline work.
10. **Content production at scale** — routines, investigation, jobs/minigames, chase, melee/confrontation, 20–30 minute slice, then district/population breadth.

Executable contracts live in [`../workpacks/`](../workpacks/README.md).

## What vs how

The new production architecture has three distinct owners:

- [`WP-CITY-URBAN-00`](../workpacks/WP-CITY-URBAN-00.md) = **what city / what first block / what spatial roles are needed**;
- `PROD-ASSET/ENV/CHAR/ANIM/DIALOGUE/UI` = **how to manufacture those roles repeatedly**;
- [`WP-CITY-URBAN-01`](../workpacks/WP-CITY-URBAN-01.md) = **realize and tune the keeper block in actual third-person game space**.

The useful historical CITY knowledge is distilled in [`../design/CITY_PRODUCTION_KNOWLEDGE.md`](../design/CITY_PRODUCTION_KNOWLEDGE.md). The first concrete production brief is [`../design/FIRST_KEEPER_BLOCK_B0.md`](../design/FIRST_KEEPER_BLOCK_B0.md).

We preserve compact density, route logic, programme, access/threshold layers, reusable street/building families, selective interiors, coherent elevation and CITY-07 game-space principles. We do **not** restore the old Puente Viejo/inland topology, old IDs or H0/H1 governance.

## Why CITY-URBAN-00 exists before ENV

A factory without city demand tends to optimize whatever assets happen to be easiest to process. That is how we risk producing a technically good but visually/product-wrong generic kit.

CITY-URBAN-00 must give ENV a demand matrix for actual B0 needs: mixed commercial frontage, shop/service thresholds, lodging frontage, ordinary closed fabric, stairs/retaining/railings, working-water edge, port/market props, shallow interiors, access truth and local elevation relationships.

ENV then builds the smallest scalable factory that covers those demands and enough adjacent vocabulary for later blocks.

## Product/factory path

| Step | Objective | Output | PASS signal |
|---|---|---|---|
| Bootstrap Unity ✅ | Unity + GC2 operational | player/camera baseline | Play Mode + hand test work. |
| CITY-URBAN-00 | decide enough city/B0 product space to drive production | topology + B0 programme + demand matrix | ENV no longer has to guess what to manufacture. |
| PROD-ASSET-00 | make lawful source corpus searchable/reproducible | shared catalogue/intake/validators | routine source discovery no longer needs path archaeology. |
| M0 | validate camera/scale/reach/interaction | tiny gameplay fixture | walk + world/NPC interaction work. |
| ENV Factory | manufacture city architecture/urban vocabulary repeatedly | reusable kit + assembly grammar + validation | normal new ENV unit is production, not R&D. |
| CHAR Factory | manufacture ordinary civilians repeatedly | civilian/wardrobe factory | normal civilian is production, not bespoke repair. |
| ANIM Factory | batch discover/import/retarget/use motions | animation catalogue + runtime vocabulary | normal compatible motion is routine to admit/use. |
| Dialogue/UI Factory | author contextual investigation conversations repeatedly | authoring + no-voice presentation factory | new dialogue is content work, not scene plumbing. |
| Scale proofs | demonstrate volume and variation | ENV/CHAR/ANIM batches | no pipeline restart on later examples. |
| CITY-URBAN-01 | realize B0 as keeper game space | first retained city block | owner says keep and extend. |
| PROD-LOOK-GATE | fresh production challenge | production lock | new brief succeeds without foundational rework. |
| Content production | make the game | living block → slice → districts | breadth grows on proven factories/systems. |

## B0 target

B0 Mercado–Muelle is the first retained city customer: lodging/return anchor, market/activity, ordinary shop + witness threshold, commercial run, port reveal/public quay, raised observation/alternate route, genuine cycles and honest expansion seams.

Its starting dimensions/coordinates are hypotheses. `CITY-URBAN-01` may improve local keeper geometry while preserving programme, route connectivity, access truth and expansion intent.

## CITY-07 knowledge retained

Keeper realization is not a literal extrusion of a planning diagram. It must resolve:

- compression → expansion → reveal;
- landmark/framed-view orientation;
- conversation/observation pockets;
- layered building assembly rather than decorated cuboids;
- coherent street/ground/threshold construction;
- one shared local elevation frame;
- public/service/private and public-port/controlled-work boundaries;
- third-person support for walking, following, searching and bounded chase movement.

Local level-design iteration is encouraged. Material topology/programme changes go back to CITY-URBAN-00; ordinary local geometry corrections do not require historical CITY bureaucracy.

## Tooling rule

Existing pipeline research remains binding: [`../research/EXISTING_ASSET_PIPELINE_RESEARCH.md`](../research/EXISTING_ASSET_PIPELINE_RESEARCH.md).

Default production path is **existing/native solution → adapt → minimal missing glue**, using MCP/Unity and Blender where useful. No H1-style lifecycle infrastructure or giant universal generator is justified merely by elegance.

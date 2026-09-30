# Roadmap jugable

Status: **ANIM-01 DONE / CURRENT: ENV-01 + ENV-DIRECTOR-00 + CHAR-01** — human-directed ENV authoring is the next environment-production gate

## Immediate sequence

1. ~~**Knowledge migration**~~ — done.
2. ~~**Production authoring decision**~~ — `BOUNDED_OPERATOR` adopted.
3. ~~**Bootstrap Unity + GC2 Core**~~ — done: Unity 6000.3.24f1 + URP 17.3 + GC2 Core 2.19.61, player/camera working in Play Mode.
4. **Production foundations:**
   - ~~`PROD-ASSET-00`~~ — **done / accepted**: searchable catalogue, lineage, deterministic intake, validators and B0 coverage/gaps;
   - ~~`CITY-URBAN-00`~~ — **done / accepted**: five-zone topology + final B0 Mercado–Muelle route/programme/elevation + factory-demand matrix.
5. **M0 fixture + Dialogue in parallel** — small gameplay-integration fixture and dialogue-authoring factory; neither blocks the graphical factories.
6. **Factories + human authoring — CURRENT:** continue `ENV-01` and `CHAR-01`, and execute **`PROD-ENV-DIRECTOR-00` urgently**. Director gives the owner direct Scene View control of layout/buildings/details while AI/factory keep the repetitive production role. ~~`ANIM-01`~~ is **done / accepted**: 254 clips catalogued, 45 sampled on two Humanoid targets and 19 motions admitted across five families, with contact/navigation gaps kept explicit.
7. **Factory scale proofs** — `ENV-02` requires both ENV-01 and ENV-DIRECTOR-00; it must prove a fresh **human-directed -> AI/factory-produced -> validated -> human-corrected** composition. `CHAR-02` follows CHAR-01; `ANIM-02` consumes accepted ANIM-01 but waits for CHAR-01. UI follows Dialogue.
8. **B0 Keeper Block (`CITY-URBAN-01`)** — physical third-person realization of the accepted city brief using the factories.
9. **Production Factory Gate (`PROD-LOOK-GATE`)** — fresh brief challenge proves content can now be produced without foundational pipeline work.
10. **Content production at scale** — routines, investigation, jobs/minigames, chase, melee/confrontation, 20–30 minute slice, then district/population breadth.

Executable contracts live in [`../workpacks/`](../workpacks/README.md).

## What vs how

The new production architecture has three distinct owners:

- [`WP-CITY-URBAN-00`](../workpacks/WP-CITY-URBAN-00.md) = **what city / what first block / what spatial roles are needed**;
- `PROD-ASSET/ENV/CHAR/ANIM/DIALOGUE/UI` = **how to manufacture those roles repeatedly**;
- [`WP-PROD-ENV-DIRECTOR-00`](../workpacks/WP-PROD-ENV-DIRECTOR-00.md) = **how the owner directly authors high-value spatial/composition decisions without JSON/code/Inspector-coordinate work**;
- [`WP-CITY-URBAN-01`](../workpacks/WP-CITY-URBAN-01.md) = **realize and tune the keeper block in actual third-person game space**.

The useful historical CITY knowledge is distilled in [`../design/CITY_PRODUCTION_KNOWLEDGE.md`](../design/CITY_PRODUCTION_KNOWLEDGE.md). The first concrete production brief is [`../design/FIRST_KEEPER_BLOCK_B0.md`](../design/FIRST_KEEPER_BLOCK_B0.md).

We preserve compact density, route logic, programme, access/threshold layers, reusable street/building families, selective interiors, coherent elevation and CITY-07 game-space principles. We do **not** restore the old Puente Viejo/inland topology, old IDs or H0/H1 governance.

## Why CITY-URBAN-00 exists before ENV

A factory without city demand tends to optimize whatever assets happen to be easiest to process. That is how we risk producing a technically good but visually/product-wrong generic kit.

CITY-URBAN-00 now gives ENV a demand matrix for actual B0 needs: mixed commercial frontage, shop/service thresholds, lodging frontage, ordinary closed fabric, stairs/retaining/railings, working-water edge, port/market props, shallow interiors, access truth and local elevation relationships.

ENV now consumes that accepted demand together with the accepted ASSET substrate and builds the smallest scalable factory that covers those demands and enough adjacent vocabulary for later blocks.

## Product/factory path

| Step | Objective | Output | PASS signal |
|---|---|---|---|
| Bootstrap Unity ✅ | Unity + GC2 operational | player/camera baseline | Play Mode + hand test work. |
| CITY-URBAN-00 ✅ | decide enough city/B0 product space to drive production | topology + B0 programme + demand matrix | **PASS / accepted** — ENV no longer has to guess what to manufacture. |
| PROD-ASSET-00 ✅ | make lawful source corpus searchable/reproducible | shared catalogue/intake/validators | **PASS / accepted** — routine source discovery no longer needs path archaeology. |
| M0 | validate camera/scale/reach/interaction | tiny gameplay fixture | walk + world/NPC interaction work. |
| ENV Factory | manufacture city architecture/urban vocabulary repeatedly | reusable kit + assembly grammar + validation | normal new ENV unit is production, not R&D. |
| ENV Director | move the high-value spatial/composition decisions back to the owner through direct Unity manipulation | simple Scene View editor + safe upstream persistence + bounded AI actions | owner can move/reshape/place/rebuild/play without normal JSON/code/Inspector-coordinate work. |
| CHAR Factory | manufacture ordinary civilians repeatedly | civilian/wardrobe factory | normal civilian is production, not bespoke repair. |
| ANIM Factory ✅ | batch discover/import/retarget/use motions | animation catalogue + admitted motion library | **PASS / accepted** — normal compatible motion is routine to classify, retarget and admit; runtime multi-NPC use moves to ANIM-02. |
| Dialogue/UI Factory | author contextual investigation conversations repeatedly | authoring + no-voice presentation factory | new dialogue is content work, not scene plumbing. |
| Scale proofs | demonstrate volume and variation | ENV/CHAR/ANIM batches | no pipeline restart on later examples. |
| CITY-URBAN-01 | realize B0 as keeper game space | first retained city block | owner says keep and extend. |
| PROD-LOOK-GATE | fresh production challenge | production lock | new brief succeeds without foundational rework. |
| Content production | make the game | living block → slice → districts | breadth grows on proven factories/systems. |

## Human-directed ENV authoring

The current CASCO work demonstrates that technical validity and repeated agent polish do not guarantee human spatial coherence. From `PROD-ENV-DIRECTOR-00` onward, the production loop is:

```text
CITY / content brief
 -> owner direct blockout/composition in ENV Director
 -> lock important human decisions
 -> ENV factory + bounded AI/operator production
 -> validators / route checks
 -> owner third-person correction in ENV Director
 -> keeper candidate
```

The Director must be deliberately easy to use. Normal operations do not require hand-editing JSON, writing code or entering transform coordinates in the Inspector.

Delivery order is intentionally front-loaded:

1. **D0 vertical slice:** move one real trace node -> save -> rebuild -> undo/revert.
2. **D1 Layout MVP:** nodes/vias, street width, plaza vertices, landmarks, elevation, SAVE/REVERT/REBUILD/PLAY HERE.
3. **D2 Buildings + detail:** persistent move/rotate/duplicate/delete/lock and semantic replace.
4. **D3 Bounded AI actions:** VARIANT, REPLACE, EXPAND, GENERATE HERE, FILL AREA, MAKE ENTERABLE, POLISH SELECTED.
5. **D4 QA loop:** affected validation, targeted rebuild where safe, route/capture shortcuts and before/after.
6. **D5 production proof:** owner completes real keeper work faster and with less translation through an agent.

Do not wait for D3-D5 before shipping D1 to the owner. The entire point is to get human spatial judgment into the loop immediately.

AI remains a production multiplier, not autonomous spatial authority. Generated scenes stay rebuildable from upstream ENV authority; the Director must not become a second scene-state architecture.

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

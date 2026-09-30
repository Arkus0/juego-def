# Roadmap jugable

Status: **COMPACT SEMANTIC CITY REBASELINE CANDIDATE / BEFORE FURTHER ENV SCALE** — ENV01 closure, Director D0/D1 and other useful lane work remain independent

## Immediate sequence

1. ~~**Knowledge migration**~~ — done.
2. ~~**Production authoring decision**~~ — `BOUNDED_OPERATOR` adopted.
3. ~~**Bootstrap Unity + GC2 Core**~~ — done: Unity 6000.3.24f1 + URP 17.3 + GC2 Core 2.19.61, player/camera working in Play Mode.
4. **Production foundations:**
   - ~~`PROD-ASSET-00`~~ — **done / accepted**: searchable catalogue, lineage, deterministic intake, validators and B0 coverage/gaps;
   - ~~`CITY-URBAN-00`~~ — **done / accepted**: five-zone topology + final B0 Mercado–Muelle route/programme/elevation + factory-demand matrix.
5. **M0 fixture + Dialogue in parallel** — small gameplay-integration fixture and dialogue-authoring factory; neither blocks the graphical factories.
6. **Factories + human builder — CURRENT:** continue `ENV-01` and `CHAR-01`, and execute **`PROD-ENV-DIRECTOR-00` urgently**. D0/D1 stay focused on safe direct layout editing; later Director milestones add a thumbnail catalogue, game-like placement/manipulation, map expansion and a coherent-content forge that grows the catalogue by reusing/recombining/deriving before generating missing content. ~~`ANIM-01`~~ is **done / accepted**: 254 clips catalogued, 45 sampled on two Humanoid targets and 19 motions admitted across five families, with contact/navigation gaps kept explicit.
7. **Compact city correction before ENV scale:** independent acceptance of [`CITY-URBAN-00R`](../workpacks/WP-CITY-URBAN-00R.md) freezes scale, `FacadeCell != SemanticBuilding != InteriorProgramme` and deliberate exterior space; then [`PROD-ENV-CASCO-V2-00`](../workpacks/WP-PROD-ENV-CASCO-V2-00.md) tests one K2 block (23 current bodies → 4–7 semantic buildings) against an exact ENV01 reference. No full ENV01 conversion or speculative Director semantic tooling. The pilot does not require ENV01/Director PASS or later factory/integration proofs; it requires accepted rebaseline/bootstrap/ASSET and a reproducible pinned reference.
8. **Factory scale proofs** — `ENV-02` requires ENV01 + ENV-DIRECTOR-00 + CITY00R + pilot PASS; it retains **EDIT EXISTING**, **EXPAND MAP**, and **AI-SUPPLIED CONTENT** through the same factory/catalogue/QA path within the compact budget. `CHAR-02` follows CHAR-01; `ANIM-02` consumes accepted ANIM-01 but waits for CHAR-01. UI follows Dialogue.
9. **B0 Keeper Block (`CITY-URBAN-01`)** — Mercado–Muelle integration remains first keeper block, consuming rebaseline/pilot plus its existing factory/M0 prerequisites.
10. **Production Factory Gate (`PROD-LOOK-GATE`)** — fresh brief challenge proves content can now be produced without foundational pipeline work.
11. **Content production at scale** — routines, investigation, jobs/minigames, chase, melee/confrontation, the 20–30 minute slice and deliberate city breadth. Full CASCO reduction needs a later explicit brief based on pilot evidence; this proposal does not authorize it.

Executable contracts live in [`../workpacks/`](../workpacks/README.md).

## What vs how

The production responsibilities are:

- [`WP-CITY-URBAN-00`](../workpacks/WP-CITY-URBAN-00.md) = **what city / what first block / what spatial roles are needed**;
- [`WP-CITY-URBAN-00R`](../workpacks/WP-CITY-URBAN-00R.md) = **bounded scale/semantic-space amendment**; [`CASCO-V2-00`](../workpacks/WP-PROD-ENV-CASCO-V2-00.md) = **one physical falsification before scale**;
- `PROD-ASSET/ENV/CHAR/ANIM/DIALOGUE/UI` = **how to manufacture those roles repeatedly**;
- [`WP-PROD-ENV-DIRECTOR-00`](../workpacks/WP-PROD-ENV-DIRECTOR-00.md) = **how the owner visually builds, places, modifies and expands the world while AI/factory supply reusable pieces**;
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
| CITY-URBAN-00R | freeze compact scale, semantic buildings/programmes and deliberate space | bounded amendment; preserve five identities/B0 | architecture feasible and independently accepted; no Unity proof claimed. |
| PROD-ENV-CASCO-V2-00 | test larger semantic buildings in one existing CASCO block | isolated programme-first block + matched ENV01 comparison | radical playable utility AND retained character, proven with GC2/camera/concurrent NPC scale. |
| PROD-ASSET-00 ✅ | make lawful source corpus searchable/reproducible | shared catalogue/intake/validators | **PASS / accepted** — routine source discovery no longer needs path archaeology. |
| M0 | validate camera/scale/reach/interaction | tiny gameplay fixture | walk + world/NPC interaction work. |
| ENV Factory | manufacture city architecture/urban vocabulary repeatedly | reusable kit + assembly grammar + validation | normal new ENV unit is production, not R&D. |
| ENV Director | let the owner build/expand the world with game-like direct manipulation | layout tools + direct prop dragging + stretchable railing/wall chains + thumbnail catalogue + ghost placement/snap + persistent edits + AI-supplied pieces | owner can fix a misplaced barrel or extend an abrupt railing in seconds, then draw/place/move/expand/rebuild/play without JSON/code/Inspector/prefab-path archaeology. |
| CHAR Factory | manufacture ordinary civilians repeatedly | civilian/wardrobe factory | normal civilian is production, not bespoke repair. |
| ANIM Factory ✅ | batch discover/import/retarget/use motions | animation catalogue + admitted motion library | **PASS / accepted** — normal compatible motion is routine to classify, retarget and admit; runtime multi-NPC use moves to ANIM-02. |
| Dialogue/UI Factory | author contextual investigation conversations repeatedly | authoring + no-voice presentation factory | new dialogue is content work, not scene plumbing. |
| Scale proofs | demonstrate volume and variation | ENV/CHAR/ANIM batches | no pipeline restart on later examples. |
| CITY-URBAN-01 | realize B0 as keeper game space | first retained city block | owner says keep and extend. |
| PROD-LOOK-GATE | fresh production challenge | production lock | new brief succeeds without foundational rework. |
| Content production | make the game | living block → slice → districts | breadth grows on proven factories/systems. |

## Human-directed ENV authoring

The current CASCO work shows that technically valid agent generation is not enough. The production model is therefore a **human-operated visual world builder** backed by AI/factory automation:

```text
owner shapes layout
 -> owner chooses/places pieces from visual catalogue
 -> owner expands map where desired
 -> owner can AI-MODIFY a selected object/area using automatic scene context
 -> AI/operator manufactures missing requested pieces/structures
 -> new content returns to the same catalogue
 -> owner places/moves/locks
 -> deterministic rebuild + validators
 -> PLAY HERE
 -> owner corrects directly
```

The Director must be deliberately easy to use. Normal work must not require hand-editing JSON, writing code, typing transform coordinates, knowing prefab paths/GUIDs or translating every spatial decision into an agent prompt.

Delivery order:

1. **D0 — preserved vertical slice:** move one real trace node -> preview -> SAVE -> rebuild -> Undo/Revert. **Already-started D0 work remains valid.**
2. **D1 — preserved Layout MVP:** nodes/vias, street width, plaza vertices, landmarks, elevation, SAVE/REVERT/REBUILD/PLAY HERE.
3. **D2 — Visual Catalogue + Direct Manipulation:** thumbnails, drag/click placement, ghost/snap, plus **click a visible prop and drag it directly** and **drag endpoints of railings/walls to extend or shorten the semantic chain**; move/rotate/duplicate/delete/LOCK; rebuild-safe persistence.
4. **D3 — Map Expansion:** visually extend streets/spaces and place structures into new playable area without editing raw trace/spec data.
5. **D4 — Coherent Content Forge:** selection-context requests use an inspectable Project Style Profile and a binding REUSE → RECOMBINE → DERIVE → GENERATE MISSING CONTENT planner. AI MODIFY SELECTED remains transactional (PREVIEW / ACCEPT / TRY ANOTHER / DISCARD); new/materially-derived candidates pass an Admission Gate before lineage + thumbnail + catalogue admission. Free-form generation is last resort, not the default.
6. **D5 — Smart Builders/Brushes:** bounded wall/street/frontage/vegetation tools where they reduce repetitive clicks without taking composition authority.
7. **D6 — Fast QA/Play:** affected validation, local rebuild where safe, route/capture helpers and PLAY HERE.
8. **D7 — Owner Production Proof:** real keeper work proving edit-existing + map-expansion + AI-supplied-content flows.

D0/D1 are the foundation, not discarded prototypes. Do not pause or restart them because the later product target expanded.

### Prior-art posture

D2-D5 are not greenfield Unity-editor R&D. Their basic mechanics already have strong prior art:

- PrefabPalette: palette/placement-mode separation and thumbnail UX;
- Prefab Painter: minimal Scene View raycast + placement + Undo loop;
- MAST: ghost/occupancy, isolated thumbnails, modular tools and reusable assemblies;
- Prefabshop: pick-under-cursor, line tools and lasso/area interaction.

Director should reuse these **patterns** and compatible licensed code where lawful, while concentrating original engineering on juego-def's differentiators: semantic selection, rebuild-persistent upstream commits, semantic chains, locks/authority, bounded AI context and accepted AI output admission.

Do not adopt a third-party tool wholesale if it creates a second asset database, grid/world authority or scene-serialization path.


The core authority rule remains: **the owner decides where the world grows and what is kept; AI modifies/makes content only inside explicit human selection and intent.** Selecting something supplies context automatically; it does not grant authority over everything visible around it. Generated scenes remain rebuildable from upstream ENV authority; the Director must not become a second scene-state architecture.

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

Local level-design iteration is encouraged. Material topology/programme changes amend the current CITY handoff; scale/semantic-space changes consume CITY-00R once accepted. Ordinary local geometry corrections do not require historical CITY bureaucracy.

## Tooling rule

Existing pipeline research remains binding: [`../research/EXISTING_ASSET_PIPELINE_RESEARCH.md`](../research/EXISTING_ASSET_PIPELINE_RESEARCH.md).

Default production path is **existing/native solution → adapt → minimal missing glue**, using MCP/Unity and Blender where useful. No H1-style lifecycle infrastructure or giant universal generator is justified merely by elegance.

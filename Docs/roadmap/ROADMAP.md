# Roadmap jugable

Status: **BOOTSTRAP DONE / NEXT: PROD-ASSET-00** — authoring path `BOUNDED_OPERATOR` (MCP for Unity), owner-confirmed

## Immediate sequence

1. ~~**Knowledge migration**~~ — done.
2. ~~**Production authoring decision**~~ — `BOUNDED_OPERATOR` adopted; see `PRODUCTION_AUTHORING_DECISION.md`.
3. ~~**Bootstrap Unity + GC2 Core**~~ — done: Unity 6000.3.24f1 + URP 17.3 + GC2 Core 2.19.61, player/camera working in Play Mode.
4. **Shared graphical asset substrate (`PROD-ASSET-00`)** — research spikes + searchable catalogue, semantic discovery, lineage, intake conventions and validators, driven by the B0 Mercado–Muelle demand. **← NEXT**
5. **M0 fixture in parallel** — small retained player/camera/world/NPC interaction fixture; required before keeper integration, not before factory R&D.
6. **Graphical factories in parallel** — ENV / CHAR / ANIM build scalable production paths serving B0 first, not isolated examples.
7. **Factory scale proofs** — ENV multi-scene production, civilian batch, animation runtime/batch; Dialogue/UI authoring factory proceeds in parallel.
8. **B0 Keeper Block (`CITY-URBAN-01`)** — realize the migrated Mercado–Muelle first-block brief using the factories and CITY game-space design principles.
9. **Production Factory Gate (`PROD-LOOK-GATE`)** — fresh brief challenge proves new content can be produced without foundational pipeline work.
10. **Content production at scale** — routines, investigation, jobs/minigames, chase, melee/confrontation, 20–30 minute slice, then district/population breadth.

Executable contracts live in [`../workpacks/`](../workpacks/README.md). The roadmap states sequence; workpacks state PASS/FAIL.

## What vs how

- [`../design/FIRST_KEEPER_BLOCK_B0.md`](../design/FIRST_KEEPER_BLOCK_B0.md) is the migrated CITY answer to **what the first retained city content must contain**.
- `PROD-ASSET/ENV/CHAR/ANIM/DIALOGUE/UI` define **how to industrialize the assets/content needed to build it repeatedly**.
- `CITY-URBAN-01` integrates those factories back into the actual keeper B0 game space.

We migrate CITY product/game-space knowledge, not the old inland pilot or H1/H2F governance.

## Why factories come before breadth

The purpose of ENV/CHAR/ANIM/UI work is not merely to make one attractive sample. When the production gate passes, juego-def should be able to make the next normal building/street/civilian/animation/conversation primarily by using a known factory rather than inventing another pipeline.

A factory can be lightweight: metadata/catalogues, MCP/Unity recipes, Blender derivation, prefab/templates, small batch tooling and validators. We explicitly do **not** need H1-style infrastructure or giant procedural generators.

Existing pipeline research is binding input. See [`../research/EXISTING_ASSET_PIPELINE_RESEARCH.md`](../research/EXISTING_ASSET_PIPELINE_RESEARCH.md). Relevant candidates must be bounded-tested/dispositioned before equivalent custom tooling is written.

## Product/factory path

| Step | Visible/product objective | Default tech | Keeper/factory output | Observable PASS |
|---|---|---|---|---|
| Bootstrap Unity ✅ | Project opens, scene plays, real versions/pipeline recorded | Unity | minimal project | Open/Play without blocking errors. |
| GC2 Core ✅ | third-person player + camera | Core | player/camera | Walk, turn and follow in Play Mode. |
| Shared Asset Factory | B0-relevant source corpus becomes searchable/reproducible and existing pipeline candidates are evaluated | catalogue + bounded research spikes + small tooling | production substrate | ENV/CHAR/ANIM discover/intake assets without repeated path archaeology; B0 gaps visible. |
| M0 Gameplay Fixture | short route + object/hotspot + NPC interaction | operator + GC2 Core | retained scale/interaction fixture | Owner can walk/interact in Play Mode; may run in parallel. |
| Environment Factory | reusable architecture/urban asset + assembly system serving B0 | existing/adapted tooling + MCP/Unity + Blender where useful | reusable kit + tooling | Normal new environment units are routine to produce. |
| Character Factory | reusable civilian/wardrobe production serving B0 roles | existing/adapted Quaternius pipelines + prefab/batch tooling | civilian factory | Normal new civilian is routine to produce. |
| Animation Factory | semantic batch intake/retarget serving B0 motions | existing/adapted import rules + Unity/GC2 | animation factory | Normal compatible clip is routine to admit/use. |
| Dialogue/UI Factory | contextual conversations + reusable no-voice presentation | simplest justified GC2/local path | content/UI authoring factory | New normal dialogue is content work, not scene plumbing. |
| Factory Scale Proofs | demonstrate volume/repeatability | accepted factories | multi-scene/batch outputs | ENV/CHAR/ANIM scale without pipeline restart. |
| B0 Keeper Block | Mercado–Muelle lodging/market/shop/port/upper-loop game space | proven stack | first retained city block | Owner accepts it as keep-and-expand game content. |
| PROD-LOOK-GATE | fresh-production challenge | proven factories | production lock | New brief succeeds without foundational tooling changes. |
| First Investigation Loop | testimony + physical/context clue | GC2 + chosen dialogue path | clue loop | Player reaches a lead through world references. |
| Routines/Living Block | meaningful time/location changes | Behavior/local only if useful | living block | revisit produces changed opportunity/context. |
| Jobs/minigames | daily-life activity integrated in places/people | selected modules/local | retained activity | playable and contextually integrated. |
| First Chase | suspect route through real city content | proven gameplay stack | retained chase | can catch/lose without investigation dead-end. |
| Melee | brief purposeful confrontation | Melee if adopted | retained encounter | starts/plays/ends with consequence. |
| 20–30 minute slice | investigation -> daily life -> action -> changed return | proven stack | complete slice | first-play timed run works end to end. |
| Expansion | more districts/population/content | factories + proven systems | incremental content | each increment adds real playable density. |

## M0 fixture

M0 is deliberately small and parallel. It establishes the truthful gameplay camera/scale/interaction baseline used to validate factory output before B0 integration.

**PASS:** owner can walk the route, interact with object/world and interact with the NPC in Play Mode. Proxies must be explicit; M0 cannot pretend dressed cubes are final architecture.

## B0 city target

The first keeper block is the Mercado–Muelle seam defined in `FIRST_KEEPER_BLOCK_B0.md`: lodging/return, market/activity, everyday shop + witness threshold, commercial run, port reveal/public quay, upper observation/alternate route, honest expansion seams and genuine route cycles.

The useful CITY-07/CITY-09 lessons are retained as design criteria: route learning, compression/expansion/reveal, threshold readability, framed views, useful nooks, coherent elevation and third-person support for follow/search/chase. The old inland exact geometry and lifecycle gates are not.

## Production factory phase

Start now with:

1. `PROD-ASSET-00`, including reuse-first research spikes and B0 demand coverage;
2. M0 and Dialogue may proceed in parallel;
3. after ASSET-00, ENV/CHAR/ANIM factories run concurrently;
4. batch scale proofs;
5. B0 keeper realization;
6. fresh-production Gate.

See [`POST_FOUNDATION_PRODUCTION_WPS.md`](POST_FOUNDATION_PRODUCTION_WPS.md) for high-level rationale and [`../workpacks/README.md`](../workpacks/README.md) for executable DAG/contracts.

## Tooling boundary

- default: operator + GC2 native + source corpus + **existing/adapted pipelines first** + lightweight custom glue/validation;
- build small scripts/templates when they eliminate repeated work not already solved adequately;
- use Blender/derived assets where source components need real adaptation;
- still defer giant scenario generators, universal character generators, H1-style lifecycle infrastructure and tooling whose only justification is elegance rather than throughput/quality.

The operator decision is revisited with actual factory evidence after ENV batch proof, not by theoretical architecture comparison.

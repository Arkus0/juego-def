# Roadmap jugable

Status: **BOOTSTRAP DONE / NEXT: PROD-ASSET-00** — authoring path `BOUNDED_OPERATOR` (MCP for Unity), owner-confirmed

## Immediate sequence

1. ~~**Knowledge migration**~~ — done.
2. ~~**Production authoring decision**~~ — `BOUNDED_OPERATOR` adopted; see `PRODUCTION_AUTHORING_DECISION.md`.
3. ~~**Bootstrap Unity + GC2 Core**~~ — done: Unity 6000.3.24f1 + URP 17.3 + GC2 Core 2.19.61, player/camera working in Play Mode.
4. **Shared graphical asset substrate (`PROD-ASSET-00`)** — consume existing pipeline research first; searchable catalogue, semantic discovery, source/derived lineage, import/adaptation conventions and cheap validators. **← NEXT**
5. **M0 gameplay fixture — parallel** — short route + one world interaction + one NPC interaction; validates camera/scale/reach/GC2 integration but does not block factory R&D.
6. **Graphical factories in parallel after ASSET-00** — ENV / CHAR / ANIM build scalable production paths, explicitly reusing/adapting existing pipelines before custom tooling.
7. **Factory scale proofs** — ENV multi-scene production, civilian batch, animation runtime/batch. Dialogue/UI authoring factory can proceed in parallel from bootstrap.
8. **First Keeper Block (`CITY-URBAN-01`)** — integrate M0 interaction fixture + accepted factory outputs in actual game space.
9. **Production Factory Gate (`PROD-LOOK-GATE`)** — fresh brief challenge proves new content can be produced without foundational pipeline work.
10. **Content production at scale** — routines, investigation, jobs/minigames, chase, melee/confrontation, 20–30 minute slice, then district/population breadth.

Executable contracts live in [`../workpacks/`](../workpacks/README.md). The roadmap states sequence; workpacks state PASS/FAIL.

## Why factories come before breadth

The purpose of ENV/CHAR/ANIM/UI work is not merely to make one attractive sample. When the production gate passes, juego-def should be able to make the next normal building/street/civilian/animation/conversation primarily by using a known factory rather than inventing another pipeline.

A factory can be lightweight: metadata/catalogues, MCP/Unity recipes, Blender derivation, prefab/templates, small batch tooling and validators. We explicitly do **not** need H1-style infrastructure or giant procedural generators.

Existing pipeline research is binding input. See [`../research/EXISTING_ASSET_PIPELINE_RESEARCH.md`](../research/EXISTING_ASSET_PIPELINE_RESEARCH.md). Relevant candidates must be bounded-tested/dispositioned before equivalent custom tooling is written.

## Product/factory path

| Step | Visible objective | Default tech | Keeper output | Observable PASS |
|---|---|---|---|---|
| Bootstrap Unity ✅ | Project opens, scene plays, real versions/pipeline recorded | Unity | minimal project | Open/Play without blocking errors. |
| GC2 Core ✅ | third-person player + camera | Core | player/camera | Walk, turn and follow in Play Mode. |
| Shared Asset Factory | source corpus becomes searchable/reproducible and existing pipeline candidates are evaluated | catalogue + bounded research spikes + small tooling | production substrate | ENV/CHAR/ANIM can discover/intake assets without repeated manual path archaeology or blind reinvention. |
| M0 Gameplay Fixture | short route + object/hotspot + NPC interaction | operator + GC2 Core | retained scale/interaction fixture | Owner can walk/interact in Play Mode; may run in parallel. |
| Environment Factory | reusable architecture/urban asset + assembly system | existing/adapted tooling + MCP/Unity + Blender where useful | reusable kit + tooling | Normal new environment units are routine to produce. |
| Character Factory | reusable civilian/wardrobe production | existing/adapted Quaternius pipelines + prefab/batch tooling | civilian factory | Normal new civilian is routine to produce. |
| Animation Factory | semantic batch intake/retarget + runtime mapping | existing/adapted import rules + Unity/GC2 | animation factory | Normal compatible clip is routine to admit/use. |
| Dialogue/UI Factory | contextual conversations + reusable no-voice presentation | simplest justified GC2/local path | content/UI authoring factory | New normal dialogue is content work, not scene plumbing. |
| Factory Scale Proofs | demonstrate volume/repeatability | accepted factories | multi-scene/batch outputs | ENV/CHAR/ANIM scale without pipeline restart. |
| First Keeper Block | integrate factories into real urban content | proven stack | retained lived-in block seed | Owner accepts it as keep-and-expand game content. |
| PROD-LOOK-GATE | fresh-production challenge | proven factories | production lock | New brief succeeds without foundational tooling changes. |
| First Investigation Loop | testimony + physical/context clue | GC2 + chosen dialogue path | clue loop | Player reaches a lead through world references. |
| Routines/Living Block | meaningful time/location changes | Behavior/local only if useful | living block | revisit produces changed opportunity/context. |
| Jobs/minigames | daily-life activity integrated in places/people | selected modules/local | retained activity | playable and contextually integrated. |
| First Chase | suspect route through real city content | proven gameplay stack | retained chase | can catch/lose without investigation dead-end. |
| Melee | brief purposeful confrontation | Melee if adopted | retained encounter | starts/plays/ends with consequence. |
| 20–30 minute slice | investigation -> daily life -> action -> changed return | proven stack | complete slice | first-play timed run works end to end. |
| Expansion | more districts/population/content | factories + proven systems | incremental content | each increment adds real playable density. |

## M0 — why it still exists

M0 is deliberately tiny and **not** the gateway to factory development.

The bootstrap already proves player/camera. M0 adds only the smallest retained gameplay fixture needed to validate assets later at real third-person conditions: route width, camera framing, collision/reach and an NPC/world interaction.

It may run in parallel with `PROD-ASSET-00` and the early factory work. It must be ready before `CITY-URBAN-01`, when the first keeper block integrates all lanes.

## Production factory phase

Start now with:

1. `PROD-ASSET-00`, including reuse-first research spikes;
2. M0 and Dialogue may proceed in parallel;
3. after ASSET-00, ENV/CHAR/ANIM factories run concurrently;
4. batch scale proofs;
5. integrated keeper block;
6. fresh-production Gate.

See [`POST_FOUNDATION_PRODUCTION_WPS.md`](POST_FOUNDATION_PRODUCTION_WPS.md) for high-level rationale and [`../workpacks/README.md`](../workpacks/README.md) for executable DAG/contracts.

## Tooling boundary

- default: operator + GC2 native + source corpus + **existing/adapted pipelines first** + lightweight custom glue/validation;
- build small scripts/templates when they eliminate repeated work not already solved adequately;
- use Blender/derived assets where source components need real adaptation;
- still defer giant scenario generators, universal character generators, H1-style lifecycle infrastructure and tooling whose only justification is elegance rather than throughput/quality.

The operator decision is revisited with actual factory evidence after ENV batch proof, not by theoretical architecture comparison.

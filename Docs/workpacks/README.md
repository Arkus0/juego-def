# juego-def executable workpacks

Status: **ACTIVE / v1**  
Authority: `AGENTS.md` + `Docs/roadmap/ROADMAP.md` + `Docs/architecture/PRODUCTION_AUTHORING_DECISION.md`

## Purpose

This directory turns the roadmap into executable product/production contracts. The immediate objective is to build the **graphical/content factories** that let juego-def manufacture repeatedly and cheaply, while CITY provides concrete spatial/product demand.

The separation is deliberate:

- `CITY-URBAN-00` = **what town/block we need** — accepted;
- `PROD-ASSET-00` = **shared lawful production substrate** — accepted;
- `PROD-ENV/CHAR/ANIM/...` = **how we industrialize the content needed to build it**;
- `CITY-URBAN-01` = **physical keeper realization** of the first block with those factories.

The first concrete customer is [`../design/FIRST_KEEPER_BLOCK_B0.md`](../design/FIRST_KEEPER_BLOCK_B0.md), governed by [`../design/CITY_PRODUCTION_KNOWLEDGE.md`](../design/CITY_PRODUCTION_KNOWLEDGE.md).

## Factory exit principle

A production lane is not finished because it produced a nice sample. It finishes when:

- the real lawful source corpus is discoverable by worker/operator;
- existing public/commercial/native pipeline knowledge has been evaluated before equivalent custom tooling is written;
- intake/adaptation/derivation rules are repeatable;
- routine work is automated or templatized where that materially helps;
- common failures have cheap validators;
- a non-trivial batch has been produced through the same path;
- accepted CITY/B0 demand has usable coverage or explicit gaps;
- creating the next asset is primarily **production**, not new R&D or bespoke plumbing.

The factory may be scripts, Editor tools, Blender recipes, templates, metadata, prompts/briefs and validators. It does **not** need to be a huge custom framework.

## Execution rules

All workpack roles/hand-offs follow root [`../../AGENTS.md`](../../AGENTS.md) and the canonical skills under `.agents/skills/`.

1. **Product first.** Factory work exists to unlock B0 and later city content, not tooling for its own sake.
2. **CITY defines demand; factories define manufacture.** Do not let ENV invent the city or CITY invent asset tooling.
3. **GC2-first.** Use GC2 where it materially reduces gameplay/presentation work; do not duplicate it.
4. **Bounded operator by default.** Unity/MCP/asset operator performs the physical Editor loop where it adds value; Worker retains WP ownership and Reviewer remains independent.
5. **Human look authority.** Owner is final authority on keeper graphical output.
6. **No H0/H1 compatibility tax.** Old materialize/reconcile/gate machinery is not inherited.
7. **Reuse before invention is binding.** Consume [`../research/EXISTING_ASSET_PIPELINE_RESEARCH.md`](../research/EXISTING_ASSET_PIPELINE_RESEARCH.md); existing/adapted solution before equivalent custom tooling.
8. **CITY knowledge is selective.** Consume current port-town topology, B0 demand and reusable game-space principles; do not import the old inland pilot or historical CITY governance.
9. **No fake keeper art.** Proxies are explicit; dressed greybox cannot count as keeper production output.
10. **Source packages are inputs, not workspaces.** Derived output lives in juego-def-owned locations with lineage.
11. **Independent acceptance.** Worker pre-review is required readiness evidence but never substitutes for a fresh Reviewer PASS on the frozen candidate.

## M0

M0 is **not** the gateway to factory R&D. Bootstrap already proves Unity + GC2 player/camera.

M0 is only a small gameplay-integration fixture for player scale, camera, collision/reach and a world/NPC interaction. It runs in parallel and must pass before `CITY-URBAN-01`.

## DAG

```text
BOOTSTRAP-UNITY-GC2 (PASS)
      |
      +----> PROD-ASSET-00 (PASS) ----------+----> CHAR-01 -> CHAR-02 ----+
      |                                     +----> ANIM-01 -> ANIM-02 ----+
      |                                     |                              |
      +----> CITY-URBAN-00 (PASS) -----------+----> ENV-01  -> ENV-02 -----+
      |          what to build                                              |
      +----> M0-00 ---------------------------------------------------------+
      |                                                                     |
      +----> DIALOGUE-01 -> UI-01 ------------------------------------------+
                                                                            |
                                                                            v
                                                              CITY-URBAN-01 realize B0
                                                                            |
                                                                            v
                                                                   PROD-LOOK-GATE
                                                                            |
                                                                            v
                                                              CONTENT PRODUCTION AT SCALE
```

`CITY-URBAN-00` and `PROD-ASSET-00` are accepted. Product demand and shared production substrate are both available, so the three graphical lane factories are now dependency-valid.

## Workpacks

| WP | Outcome | Depends on |
| --- | --- | --- |
| `WP-CITY-URBAN-00` ✅ | Five-zone topology + accepted B0 programme/route/elevation + factory-demand matrix | **PASS / accepted** |
| `WP-PROD-ASSET-00` ✅ | Shared asset catalogue, research spikes, intake, lineage, discovery and validators | **PASS / accepted** |
| `WP-M0-00` | Small retained GC2 gameplay integration fixture | Bootstrap PASS; parallel |
| `WP-PROD-ENV-01` | Environment asset/assembly factory serving accepted CITY/B0 demand | ASSET-00 + CITY-URBAN-00 |
| `WP-PROD-ENV-02` | Multi-scene batch proof from ENV factory | ENV-01 |
| `WP-PROD-CHAR-01` | Civilian/wardrobe production factory serving B0 role priorities | ASSET-00 |
| `WP-PROD-CHAR-02` | Representative civilian batch from factory | CHAR-01 |
| `WP-PROD-ANIM-01` | Animation intake/retarget/coverage factory serving B0 motion priorities | ASSET-00 |
| `WP-PROD-ANIM-02` | Runtime animation vocabulary + batch proof | ANIM-01 + CHAR-01 |
| `WP-PROD-DIALOGUE-01` | Investigation dialogue authoring/runtime production path | Bootstrap PASS |
| `WP-PROD-UI-01` | Reusable no-voice dialogue/interaction presentation system | DIALOGUE-01 |
| `WP-CITY-URBAN-01` | Realize accepted B0 Mercado–Muelle from factories | CITY-URBAN-00 + M0 + ENV-02 + CHAR-02 + ANIM-02 + UI-01 |
| `WP-PROD-LOOK-GATE` | Prove factories ready for content-scale production | CITY-URBAN-01 |

## Immediate sequence

**Start `WP-PROD-ENV-01`, `WP-PROD-CHAR-01` and `WP-PROD-ANIM-01`.** Both shared foundations are now accepted.

M0 and Dialogue may continue independently. ENV consumes accepted ASSET + CITY demand; CHAR and ANIM consume the accepted ASSET substrate and B0 role priorities.

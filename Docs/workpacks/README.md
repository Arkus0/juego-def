# juego-def executable workpacks

Status: **ACTIVE / v1**  
Authority: `Docs/roadmap/ROADMAP.md` + `Docs/architecture/PRODUCTION_AUTHORING_DECISION.md`

## Purpose

This directory turns the roadmap into small executable contracts. The immediate objective is not merely to prove that one good scene/character/animation can be made: it is to build the **graphical production factories** that let juego-def manufacture content repeatedly and cheaply.

### Factory exit principle

A production lane is not finished because it produced a nice sample. It finishes when:

- the real lawful source corpus is discoverable by worker/operator;
- existing public/commercial/native pipeline knowledge has been evaluated before equivalent custom tooling is written;
- intake/adaptation/derivation rules are repeatable;
- routine work is automated or templatized where that materially helps;
- common failures have cheap validators;
- a non-trivial batch has been produced through the same path;
- creating the next asset is primarily **production**, not new R&D or bespoke plumbing.

The factory may be scripts, Editor tools, Blender recipes, templates, metadata, prompts/briefs and validators. It does **not** need to be a huge custom framework.

## Execution rules

1. **Product first.** Factory work exists to unlock content volume and quality, not tooling for its own sake.
2. **GC2-first.** Use GC2 where it materially reduces gameplay/presentation work; do not duplicate it.
3. **Bounded operator by default.** Claude Code + MCP for Unity performs the physical Editor loop where adopted: inspect -> act -> observe -> correct.
4. **Human look authority.** Owner is final authority on whether graphical output belongs in the game.
5. **No H0/H1 compatibility tax.** Old materialize/reconcile/gate machinery is not inherited.
6. **Evidence proportional to risk.** Keep batch output, runtime/capture evidence, validator results and meaningful intervention/failure notes.
7. **Reuse before invention is binding.** Consume [`../research/EXISTING_ASSET_PIPELINE_RESEARCH.md`](../research/EXISTING_ASSET_PIPELINE_RESEARCH.md). For art: `DIRECT -> ADAPTABLE -> DONOR -> CREATE_DERIVED`. A factory may reject an existing tool, but may not silently reimplement the same stage without a bounded evaluation.
8. **No fake keeper art.** Proxies are explicit; dressed greybox cannot count as keeper production output.
9. **Source packages are inputs, not workspaces.** Do not destructively mutate vendor/source packages; generated/derived outputs live in juego-def-owned locations with lineage.

## Why M0 still exists

M0 is **not** the gateway to factory R&D. The bootstrap already proves Unity + GC2 player/camera.

M0 is only a small gameplay-integration fixture: a walkable route, one world interaction and one NPC interaction at the real camera/player scale. It gives factories a stable in-game validation target and catches GC2/camera/reach/collision issues before the first keeper block.

Therefore M0 runs **in parallel** with the early factory work and must pass before `CITY-URBAN-01`, not before `PROD-ASSET-00`.

## DAG

```text
BOOTSTRAP-UNITY-GC2 (PASS)
      |                |                    |
      |                |                    +--> PROD-DIALOGUE-01 -> PROD-UI-01
      |                +--> WP-M0-00 (small integration fixture) ----------------+
      v                                                                        |
PROD-ASSET-00  shared catalogue/intake/reuse-spikes/lineage/validation          |
   |              |                 |                                          |
   v              v                 v                                          |
ENV-01          CHAR-01           ANIM-01                                      |
factory         factory           factory                                      |
   |              |                 |                                          |
   v              v                 v                                          |
ENV-02          CHAR-02           ANIM-02                                      |
   \              |                 /                                           |
    \             |                /                                            |
     +------------+---------------+---------------------------------------------+
                  |
                  v
            CITY-URBAN-01
                  |
                  v
            PROD-LOOK-GATE
                  |
                  v
         CONTENT PRODUCTION AT SCALE
```

## Workpacks

| WP | Factory/product outcome | Depends on |
| --- | --- | --- |
| `WP-PROD-ASSET-00` | Shared machine-readable asset catalogue, research spikes, intake, lineage, discovery and validators | Bootstrap PASS |
| `WP-M0-00` | Small retained GC2 gameplay integration fixture | Bootstrap PASS; parallel |
| `WP-PROD-ENV-01` | Environment asset/assembly factory | ASSET-00 |
| `WP-PROD-ENV-02` | Multi-scene batch proof from ENV factory | ENV-01 |
| `WP-PROD-CHAR-01` | Civilian/wardrobe production factory | ASSET-00 |
| `WP-PROD-CHAR-02` | Representative civilian batch from factory | CHAR-01 |
| `WP-PROD-ANIM-01` | Animation intake/retarget/coverage factory | ASSET-00 |
| `WP-PROD-ANIM-02` | Runtime animation vocabulary + batch proof | ANIM-01 + CHAR-01 |
| `WP-PROD-DIALOGUE-01` | Investigation dialogue authoring/runtime production path | Bootstrap PASS |
| `WP-PROD-UI-01` | Reusable no-voice dialogue/interaction presentation system | DIALOGUE-01 |
| `WP-CITY-URBAN-01` | First integrated keeper block produced from factories | M0 + ENV-02 + CHAR-02 + ANIM-02 + UI-01 |
| `WP-PROD-LOOK-GATE` | Prove factories are ready for content-scale production | CITY-URBAN-01 |

## Immediate sequence

**Start `WP-PROD-ASSET-00` now.**

In parallel, `WP-M0-00` may establish the tiny gameplay integration fixture and `WP-PROD-DIALOGUE-01` may start its authoring evaluation. Once ASSET-00 passes, ENV/CHAR/ANIM factories can run concurrently.

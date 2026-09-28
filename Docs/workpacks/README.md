# juego-def executable workpacks

Status: **ACTIVE / v1**  
Authority: `Docs/roadmap/ROADMAP.md` + `Docs/architecture/PRODUCTION_AUTHORING_DECISION.md`

## Purpose

This directory turns the roadmap into small executable contracts. The immediate objective after M0 is not merely to prove that one good scene/character/animation can be made: it is to build the **graphical production factories** that let juego-def manufacture content repeatedly and cheaply.

### Factory exit principle

A production lane is not finished because it produced a nice sample. It finishes when:

- the real lawful source corpus is discoverable by worker/operator;
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
7. **Reuse before invention.** `GC2/native -> known tooling -> adapt -> small custom`. For art: `DIRECT -> ADAPTABLE -> DONOR -> CREATE_DERIVED`.
8. **No fake keeper art.** Proxies are explicit; dressed greybox cannot count as keeper production output.
9. **Source packages are inputs, not workspaces.** Do not destructively mutate vendor/source packages; generated/derived outputs live in juego-def-owned locations with lineage.

## DAG

```text
BOOTSTRAP-UNITY-GC2 (PASS)
        |
        v
WP-M0-00  First Walking Street
        |
        +-----------------------> PROD-DIALOGUE-01 -> PROD-UI-01
        |
        v
PROD-ASSET-00  Shared catalogue/intake/lineage/validation substrate
   |              |                 |
   v              v                 v
ENV-01          CHAR-01           ANIM-01
Environment     Character         Animation
factory         factory           intake/retarget factory
   |              |                 |
   v              v                 v
ENV-02          CHAR-02           ANIM-02
batch scene     population batch  runtime/batch vocabulary
   \              |                 /
    \             |                /
     +------------+---------------+
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

`PROD-DIALOGUE-01/UI-01` can progress in parallel once M0 has a stable NPC interaction fixture. The graphical asset factories share `PROD-ASSET-00` so they do not each rediscover the same corpus/provenance/import problems.

## Workpacks

| WP | Factory/product outcome | Depends on |
| --- | --- | --- |
| `WP-M0-00` | First retained playable GC2 street | Bootstrap PASS |
| `WP-PROD-ASSET-00` | Shared machine-readable asset catalogue, intake, lineage, discovery and validators | M0 |
| `WP-PROD-ENV-01` | Environment asset/assembly factory | ASSET-00 |
| `WP-PROD-ENV-02` | Multi-scene batch proof from ENV factory | ENV-01 |
| `WP-PROD-CHAR-01` | Civilian/wardrobe production factory | ASSET-00 |
| `WP-PROD-CHAR-02` | Representative civilian batch from factory | CHAR-01 |
| `WP-PROD-ANIM-01` | Animation intake/retarget/coverage factory | ASSET-00 |
| `WP-PROD-ANIM-02` | Runtime animation vocabulary + batch proof | ANIM-01 + CHAR-01 |
| `WP-PROD-DIALOGUE-01` | Investigation dialogue authoring/runtime production path | M0 |
| `WP-PROD-UI-01` | Reusable no-voice dialogue/interaction presentation system | DIALOGUE-01 |
| `WP-CITY-URBAN-01` | First integrated keeper block produced from factories | ENV-02 + CHAR-02 + ANIM-02 + UI-01 |
| `WP-PROD-LOOK-GATE` | Prove factories are ready for content-scale production | CITY-URBAN-01 |

## Immediate sequence

**Execute `WP-M0-00` now.**

After M0: execute `WP-PROD-ASSET-00`. Dialogue may proceed in parallel. Once ASSET-00 passes, ENV/CHAR/ANIM factories can run concurrently.

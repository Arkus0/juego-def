# juego-def executable workpacks

Status: **ACTIVE / v1**  
Authority: `Docs/roadmap/ROADMAP.md` + `Docs/architecture/PRODUCTION_AUTHORING_DECISION.md`

## Purpose

This directory turns the product roadmap into small executable contracts. Workpacks are intentionally lighter than Juego2's infrastructure-heavy governance: each one exists to produce a visible keeper result, prove a reusable production recipe, or close a concrete product decision.

## Execution rules

1. **Product first.** A WP passes by producing/validating the stated game output, not by manufacturing infrastructure around it.
2. **GC2-first.** Use GC2 Core/modules where they materially reduce work; modules are not bought/adopted merely because a WP mentions them.
3. **Bounded operator by default.** Claude Code + MCP for Unity is the default physical Unity operator in the lanes listed by `PRODUCTION_AUTHORING_DECISION.md`. It must inspect -> act -> observe -> correct, not merely emit scripts.
4. **Human look authority.** The owner decides whether composition/feel is keeper-worthy. Automated evidence supports that decision but does not replace it.
5. **No H0/H1 compatibility tax.** H0/H1, materialize/reconcile and old H2F gates are not requirements.
6. **Evidence proportional to risk.** Keep captures, Play Mode proof, console/runtime observations and important intervention/failure notes. Do not create ceremony unrelated to a real risk.
7. **Reuse before invention.** Prefer GC2 native -> audited Hub/known tooling -> adaptation -> small local code. Prefer `DIRECT -> ADAPTABLE -> DONOR -> CREATE_DERIVED` for art reuse.
8. **No fake keeper art.** Primitive/proxy geometry is allowed only when clearly temporary. A WP that claims keeper environment output may not hide greybox behind pasted assets.

## DAG

```text
BOOTSTRAP-UNITY-GC2 (PASS)
        |
        v
WP-M0-00  First Walking Street
   |        |          |          |
   |        |          |          +--> PROD-DIALOGUE-01 --> PROD-UI-01
   |        |          +--> PROD-ANIM-01 --> PROD-ANIM-02
   |        +--> PROD-CHAR-01 --> PROD-CHAR-02
   +--> PROD-ENV-01

PROD-ENV-01 + PROD-CHAR-02 + PROD-ANIM-02 + PROD-UI-01
                         |
                         v
                   CITY-URBAN-01
                         |
                         v
                   PROD-LOOK-GATE
```

The production lanes should run in parallel once M0 provides a stable shared scene/baseline. `PROD-DIALOGUE-01` may begin earlier if the NPC fixture is already stable.

## Workpacks

| WP | Purpose | Depends on |
| --- | --- | --- |
| `WP-M0-00` | First retained GC2 walking street with interaction | Bootstrap PASS |
| `WP-PROD-ENV-01` | Keeper environment recipe + repeated-build proof | M0 |
| `WP-PROD-CHAR-01` | Ordinary character/wardrobe recipe | M0 |
| `WP-PROD-CHAR-02` | Representative population batch | CHAR-01 |
| `WP-PROD-ANIM-01` | Animation intake/coverage truth | M0 |
| `WP-PROD-ANIM-02` | Runtime animation vocabulary on real characters | ANIM-01 + CHAR-01 |
| `WP-PROD-DIALOGUE-01` | Choose real investigation dialogue authoring/presentation path | M0 |
| `WP-PROD-UI-01` | No-voice dialogue/UI presentation language | DIALOGUE-01 |
| `WP-CITY-URBAN-01` | First real keeper block | ENV-01 + CHAR-02 + ANIM-02 + UI-01 |
| `WP-PROD-LOOK-GATE` | Prove production repeatability before broad content | CITY-URBAN-01 |

## Immediate next WP

**Execute `WP-M0-00` now.**

Do not wait for every production lane to be specified further before starting M0; this v1 contract is intended to remove that ambiguity.

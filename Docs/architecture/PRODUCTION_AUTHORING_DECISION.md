# Production authoring decision

Status: **PENDING EXTERNAL BENCHMARK RESULT**  
Decision source: `Arkus0/Juego2` workpack `WP-AI-UNITY-AUTHORING-00`.

## Why this decision exists

juego-def should not inherit Juego2's H1 authoring/lifecycle architecture by default. At the same time, the current generation of Unity AI/MCP operators may be strong enough to become the primary physical authoring surface for environments, characters and animations.

The benchmark in Juego2 is therefore treated as a **decision input for juego-def**, not as an architectural dependency.

## Candidate future production path

If evidence supports it:

```text
product / CITY / ART brief
        -> AI Unity operator
        -> Unity + GC2 project
        -> Play Mode / captures / diagnostics
        -> operator correction
        -> human review
        -> retained content
```

GC2 remains the default gameplay framework. The operator is an Editor/content-production worker, not game-state authority.

## Evidence threshold for a strong migration decision

A strong positive result means more than “the MCP can create GameObjects”. The benchmark should demonstrate most of the following on real assets:

- autonomous project/asset inspection;
- useful asset discovery rather than receiving exact paths for every step;
- coherent third-person environment composition;
- prefab/material/hierarchy edits;
- Play Mode and console/runtime observation;
- screenshot/visual readback;
- at least one evidence-driven self-correction cycle;
- useful character-variant and/or animation-retarget work;
- low enough manual clicks/hints/rescue tooling to change production economics;
- repeatability under real product constraints;
- safe discard/recovery of the benchmark environment.

## Decision outcomes

### A. `PRIMARY_AUTHORING_PATH`

Use when the benchmark is clearly excellent and materially better than the current low-level/manual path.

Consequences:

- Unity + GC2 + winning operator becomes the production foundation.
- Environment/character/animation workpacks are rewritten around **brief -> operator -> validation**, not around building large bespoke factories first.
- juego-def does not import H1 lifecycle/materialize/reconcile obligations.
- Small utilities are built only where they measurably improve the operator or close a gap.

### B. `BOUNDED_OPERATOR`

Use when the operator is very useful only in named lanes, for example ENV + ANIM.

Consequences:

- those lanes consume it by default;
- other lanes use GC2/Unity/manual or specialized tooling;
- no general architecture is invented merely to make every task fit the MCP.

### C. `TOOL_SOURCE_ONLY`

Use when individual capabilities/ideas are useful but the full operator is fragile or too expensive.

Consequences:

- adopt/adapt only specific mechanisms;
- keep production direct and simple.

### D. `REJECT`

Use when evidence does not show material leverage.

Consequences:

- continue GC2-first with normal Unity authoring and the migrated Quaternius/tooling knowledge;
- no fallback to H1 merely because the MCP failed.

## H0/H1 rule

H0/H1 are **not** contingency defaults for juego-def. A future proposal to reuse a specific Arkus/H0 component must show a concrete product problem that GC2/local code cannot solve economically. H1 bridge/lifecycle machinery is not imported unless an independently demonstrated future need justifies a very small subset.

## Pause boundary

Until this decision is resolved, juego-def may continue documentation, product design, asset knowledge migration and low-risk repository setup, but should avoid heavy investment in a competing environment/character authoring framework.

A minimal Unity/GC2 bootstrap is still lawful if useful, but no large production tooling architecture should be frozen before the benchmark result is consumed.

# Production authoring decision

Status: **PROVISIONAL `BOUNDED_OPERATOR` — owner-delegated, 2026-09-28** (see [Provisional decision](#provisional-decision-2026-09-28))  
Original decision source: `Arkus0/Juego2` workpack `WP-AI-UNITY-AUTHORING-00` — now **confirming evidence**, not a blocker.

## Provisional decision (2026-09-28)

The owner chose not to wait for the Juego2 benchmark and delegated the choice. Decision:

**Claude Code + [MCP for Unity](https://github.com/CoplayDev/unity-mcp) (CoplayDev, MIT) is the default Editor operator for bounded lanes**, pinned in `Packages/manifest.json` as `com.coplaydev.unity-mcp` `v10.2.0` (editor-only; nothing ships in a player build).

| Lane | Default path |
|---|---|
| Scene assembly, hierarchy, placement, materials, lighting/volume settings | operator |
| GC2 wiring (Characters, Cameras/Shots, Triggers/Hotspots, Variables) | operator; GC2 `[SerializeReference]` polymorphic fields need `execute_code` (generic component tools cannot set managed references) |
| Play Mode observation: console, runtime state, screenshots, scripted motion checks | operator |
| Project-level plumbing that must be reproducible (package/render setup, import conventions) | one-shot batch editor scripts, not left in the repo unless reused |
| Mesh derivation from Quaternius (`DONOR` / `CREATE_DERIVED`) | Blender (Blender MCP available); not yet exercised |
| Final visual/composition judgment | **human review** — the operator reads screenshots but is not the authority on look |
| Real keyboard/mouse feel | human check (input injection is unreliable while the Editor is unfocused) |

Why this candidate:

- already configured on the owner's machine and used across versions (9.0.3 → 10.2.x); MIT, local, no cloud/account/credit burden;
- exposes the closed loop that matters: inspect → act (scene/prefab/material/components/menus) → Play → console/runtime/screenshots → correct;
- low lock-in: an Editor package plus normal Unity assets; removing it is one manifest line and leaves no hidden state;
- first real use (the Unity + GC2 bootstrap) is recorded in [`../evidence/BOOTSTRAP-UNITY-GC2/README.md`](../evidence/BOOTSTRAP-UNITY-GC2/README.md), including every failure and correction.

Not chosen as default: **Unity AI Assistant** (`com.unity.ai.assistant`) — requires a Unity AI subscription (this account reports `NoSubscription`), is prerelease, and ties the loop to Unity's own models. It may stay installed for the owner to try, but it is not a production dependency.

**Revisit trigger:** after `PROD-ENV-01` (first keeper-quality environment + repeated build). Downgrade to `TOOL_SOURCE_ONLY` if the operator still needs frequent manual rescue or produces compositions the owner repeatedly rejects; upgrade to `PRIMARY_AUTHORING_PATH` if repeated builds are materially cheaper than manual Unity work. The Juego2 benchmark (being executed separately) can confirm or overturn this with controlled evidence.

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

With the provisional decision, production lanes (M0, `PROD-ENV-01`, …) may start using the operator. The original caution still holds: do not build a large bespoke environment/character authoring framework while the operator is being proven; prefer briefs, recipes and small validations over new code.

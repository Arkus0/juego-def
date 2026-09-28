# WP-PROD-DIALOGUE-01 — Investigation Dialogue Runtime + Authoring Decision

Status: **READY AFTER M0**  
Class: PRODUCT TOOLING / DIALOGUE  
Depends on: `WP-M0-00` PASS  
Blocks: `WP-PROD-UI-01`

## Claim

juego-def has selected the simplest dialogue authoring/presentation path that materially supports an investigation game with contextual questions, without making a paid module or unnecessary framework a prerequisite.

## Candidates

Evaluate only candidates that are actually available and lawful, in this order of simplicity:

1. GC2 Core/local presentation;
2. GC2 Dialogue if owned/available and materially useful;
3. a small lawful authoring accelerator inspired by audited Hub text-to-dialogue ideas;
4. another tool/plugin only if it demonstrates a concrete material advantage.

Dialogue 2 remains optional. Alias remains research-only until exact evidence exists.

## Required decision fixture

Build one small retained investigation conversation with:

- one NPC;
- player can ask about at least **two contexts** among person/photo/place/object;
- one known/unknown fact or variable changes the NPC response;
- at least one player choice;
- at least one gesture/expression/presentation callback if the chosen path supports it economically;
- content can be edited without low-level scene surgery.

The fixture must be small enough that competing paths can be compared without building the real story system.

## Evaluate

Record for each serious candidate actually tested:

- setup friction;
- writer/content-editing friction;
- branching/context clarity;
- presentation quality;
- integration with GC2 Variables/Instructions/Conditions;
- debugging/inspection;
- persistence implications if any;
- replacement/uninstall cost;
- license/acquisition cost where relevant.

No false benchmark is required against unavailable paid packages.

## Required disposition

End with exactly one:

- `CORE_LOCAL`
- `GC2_DIALOGUE`
- `OTHER_ADOPTED`
- `DEFERRED` only if M0 can proceed but a real content blocker prevents a fair decision

The decision must state why the selected path is materially preferable for current production.

## Authoring requirement

A writer-facing or agent-facing content format should be understandable enough that dialogue text/choices can be changed without hand-editing arbitrary serialized Unity internals.

This does **not** require a custom dialogue DSL. If the chosen tool already provides a good authoring surface, use it.

## State boundary

NPC identity, clue facts and durable investigation meaning should remain understandable at juego-def/GC2 gameplay level. Avoid locking all canonical story meaning into opaque plugin-private IDs when a simple explicit variable/reference works.

## Evidence

Retain under `Docs/evidence/WP-PROD-DIALOGUE-01/`:

- selected disposition + rationale;
- fixture scene/content paths;
- Play Mode captures/proof of contextual response change;
- editing workflow note;
- any package/license/version record if a module/plugin is adopted;
- rejected/deferred candidate notes only where actually evaluated.

## PASS

PASS when:

- the fixture works end to end in Play Mode;
- response changes from actual context/state;
- content is reasonably editable;
- chosen path does not impose unjustified economic/architectural burden;
- downstream UI work has a concrete runtime surface to style.

## FAIL

FAIL if a module is adopted merely because the roadmap names it, context branching is faked, content editing requires fragile hidden surgery, or the WP expands into the full investigation narrative.

## Non-goals

No final story graph, no complete quest system, no voice acting, no localization pipeline lock and no requirement to solve every future narrative condition.

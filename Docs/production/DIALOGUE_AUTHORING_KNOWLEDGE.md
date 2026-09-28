# Dialogue authoring knowledge

Status: **MIGRATED STRATEGY / RUNTIME CHOICE PENDING REAL TEST**  
Date: 2026-09-28

## Core decision

Dialogue presentation/authoring must be chosen for **material production value**, not because a module exists or a roadmap names it.

The useful prior conclusion from Juego2 is:

- `ADOPTED` is valid only when an exact lawful Dialogue 2 version materially improves the real workflow/quality;
- `NOT_MATERIAL`, `REJECTED` and `DEFERRED_NOT_ACQUIRED` are equally legitimate outcomes;
- non-adoption routes dialogue through **GC2 Core/local presentation** without blocking the game.

juego-def intentionally drops the old H1 lifecycle burden. It preserves the product/economic decision rule.

## What Dialogue 2 would need to improve

Evaluate on a tiny investigation fixture, not marketing breadth:

- actor/speaker presentation;
- subtitle/dialogue UI skinning;
- choice presentation;
- no-voice pacing/typewriter or equivalent;
- expression/gesture/state callbacks;
- bounded camera/presentation hooks;
- authoring speed for branching/contextual investigation dialogue;
- replacement/uninstall simplicity.

A module is worth adopting when it produces a **material time saving or quality gain** over Core/local for the actual writer/gameplay workflow.

## No-voice baseline

Spoken voice acting is not a production requirement. The dialogue language should work with text, expression/gesture, camera/presentation and timing alone. Voice can be reconsidered later without making current content dependent on it.

## Hub authoring opportunity

The GC2 Hub audit found a high-potential **text-to-dialogue authoring idea** (`Build Dialogue From Text`): transforming indented text/options into Dialogue nodes could materially help a writer-heavy investigation game.

The audited extension itself was **not ready to adopt blindly** because it used editor/reflection behavior and depended on an unresolved `Game.DialogueActors` namespace. Preserve the workflow idea; re-test or reimplement a small lawful version only when the chosen dialogue runtime makes it useful.

## Alias

Prior project discussion identified **Alias** as potentially relevant authoring knowledge, but the current Juego2 repository does not contain enough canonical product evidence to assert its exact role, compatibility, license or adoption status here.

Therefore:

- `Alias = RESEARCH_PENDING`;
- do not install, purchase or make roadmap dependencies around it yet;
- when its source/documentation is available again, evaluate it against the same materiality test: does it materially improve the actual dialogue/content authoring workflow versus the chosen GC2/Core/local path?

This preserves the lead without inventing authority.

## Authority/state boundary

Even if a dialogue plugin is adopted, plugin-private IDs/variables should not accidentally become the only durable identity of NPCs, clues or world facts. Keep gameplay meaning understandable and replaceable at the juego-def layer.

This does **not** require importing Arkus/H0. It means avoiding unnecessary lock-in and duplicate ownership.

## Decision fixture

Before freezing the dialogue path, build one tiny real case:

1. NPC knows/does not know a fact;
2. player asks about person/photo/place;
3. response changes from context;
4. one choice exists;
5. one gesture/expression or presentation callback fires;
6. writer can edit the content without low-level scene surgery;
7. reload/reopen preserves the authored result.

Compare Core/local and any candidate module on authoring friction, presentation quality, debugging and replacement cost.

## Relationship to production roadmap

`PROD-DIALOGUE-01` owns the final disposition. `PROD-UI-01` consumes whichever runtime/presentation path wins. Neither may turn a paid module into an economic gate for the rest of production.

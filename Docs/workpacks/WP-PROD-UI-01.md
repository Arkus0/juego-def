# WP-PROD-UI-01 — Dialogue + Interaction UI Factory

Status: **READY AFTER DIALOGUE-01**  
Class: PRODUCTION FACTORY / UI PRESENTATION  
Depends on: `WP-PROD-DIALOGUE-01` PASS  
Blocks: `WP-CITY-URBAN-01`

## Claim

juego-def has a reusable no-voice presentation factory for investigation dialogue and nearby world interactions. New conversations/interactions can consume the same visual system without rebuilding UI per scene.

## Factory outputs

By PASS, retain:

- reusable speaker/name treatment;
- reusable dialogue text/subtitle component;
- reusable choice component;
- world interaction prompt/hotspot feedback pattern;
- typography/spacing/state tokens or equivalent reusable style source;
- pacing/reveal behavior if used;
- camera/acting coexistence conventions;
- prefab/style/template assets or equivalent;
- simple validation/checklist for overflow, missing speaker/style bindings and unreadable states.

Normal production assumption: **no spoken voice acting required**.

## Batch proof

Apply the UI factory to the 3+ conversations from `PROD-DIALOGUE-01` plus at least **2 different world-interaction prompts**.

Show:

1. NPC line;
2. player choice;
3. contextual response change;
4. gesture/acting beat or deliberate pause;
5. clean return to exploration;
6. multiple prompt types without custom rebuilding.

## Visual requirements

- readable at target gameplay resolution/window;
- belongs to the late-1990s/early-2000s PS2+ game rather than generic programmer UI;
- strong hierarchy without giant panels dominating exploration;
- works without voice acting;
- supports reasonable text-length variation;
- normal/selected/disabled states are coherent where applicable.

## Production loop

`apply reusable style/template -> Play Mode -> capture -> inspect readability/occlusion/overflow -> validate -> correct -> owner review`

## Evidence

Retain under `Docs/evidence/WP-PROD-UI-01/`:

- factory/style description;
- reusable asset/template paths;
- captures across 3+ conversations and 2+ world prompts;
- overflow/state validation notes;
- owner visual verdict;
- known polish items deferred.

## PASS

PASS when:

- one reusable presentation system serves the dialogue batch and multiple world prompts;
- UI/acting/camera coexist cleanly;
- new normal dialogue/prompt content does not require bespoke layout construction;
- owner accepts the visual language as keeper-capable;
- adding more dialogue/interactions is mainly content production and styling refinement.

## FAIL

FAIL if UI remains debug/programmer presentation, every conversation needs bespoke layout, voice is required for clarity, or reusable styles/templates cannot handle the existing batch.

## Non-goals

No full HUD, settings menus, inventory UI, accessibility suite, final localization pipeline or final branding lock.

# WP-PROD-UI-01 — No-Voice Dialogue + Interaction UI Language

Status: **READY AFTER DIALOGUE-01**  
Class: PRODUCTION FACTORY / UI PRESENTATION  
Depends on: `WP-PROD-DIALOGUE-01` PASS  
Blocks: `WP-CITY-URBAN-01`

## Claim

juego-def has a reusable, readable no-voice presentation language for investigation dialogue and nearby world interactions that fits the intended late-1990s/early-2000s, PS2+ visual identity without overwhelming third-person exploration.

## Binding inputs

- Visual Bible
- selected dialogue runtime from `WP-PROD-DIALOGUE-01`
- M0 interaction patterns
- accepted third-person camera baseline

## Required output

Create a retained UI/presentation pattern covering:

- speaker identity/name treatment;
- dialogue text/subtitle area;
- player choices;
- world interaction prompt/hotspot feedback;
- pacing/reveal behavior if used;
- gesture/acting timing coexistence;
- camera framing coexistence;
- readable normal/selected/disabled states where applicable.

Normal production assumption: **no spoken voice acting is required**.

## Required fixture

Use the investigation fixture from `PROD-DIALOGUE-01` and show:

1. NPC line;
2. player choice;
3. contextual response change;
4. one gesture/acting beat or deliberate visual pause;
5. return to exploration without UI residue or camera breakage;
6. one nearby world interaction prompt using the same visual language family.

## Visual requirements

- readable at the target gameplay resolution/window;
- strong hierarchy without giant HUD panels dominating the scene;
- compatible with damp/low-poly/PS2+ world rather than generic modern SaaS/game UI;
- no dependency on voice to communicate speaker/intent;
- typography and spacing consistent enough to reuse;
- supports future localization length variation without immediately collapsing.

Final brand polish is not required, but the pattern should be keeper-capable rather than programmer UI.

## Operator + human loop

`apply style -> Play Mode -> capture dialogue/choice/exploration transition -> inspect readability/occlusion -> correct -> owner visual review`

The owner is final authority on look/readability.

## Evidence

Retain under `Docs/evidence/WP-PROD-UI-01/`:

- style/presentation note;
- captures of line, choice, interaction prompt and return-to-play;
- relevant reusable prefab/style paths;
- owner verdict;
- known polish items deferred.

## PASS

PASS when:

- dialogue fixture is readable and coherent in Play Mode;
- choice/context state is visually clear;
- UI and acting/camera can coexist;
- interaction prompt belongs to the same presentation language;
- return to exploration is clean;
- pattern can be reused without rebuilding UI per conversation.

## FAIL

FAIL if the UI is only debug/programmer presentation, depends on voice to make sense, obscures gameplay excessively, or requires bespoke layout logic for the single fixture.

## Non-goals

No final full HUD, settings menus, inventory UI, accessibility suite, localization production pipeline or final branding lock.

# WP-PROD-CHAR-01 — Ordinary Character + Wardrobe Recipe

Status: **READY AFTER M0**  
Class: PRODUCTION FACTORY / CHARACTERS  
Depends on: `WP-M0-00` PASS  
Blocks: `WP-PROD-CHAR-02`, `WP-PROD-ANIM-02`

## Claim

juego-def has a repeatable, lawful recipe for producing visually coherent ordinary townspeople from the available Quaternius/shared character ecosystem without bespoke manual repair for every NPC.

This WP proves the **recipe and one representative set**, not population scale.

## Binding inputs

- Visual Bible
- Quaternius Production Knowledge
- retained M0 scale/camera baseline
- Production Authoring Decision

## Required outputs

1. `CHAR_RECIPE.md` describing the accepted base/rig/wardrobe path;
2. at least **4 materially distinct ordinary civilian variants** using the same recipe;
3. reusable Unity prefabs/variants or equivalent retained assets;
4. compatibility/provenance notes for every source family actually used;
5. visual/clipping/scale evidence in the real third-person camera.

The four variants are not a final population quota. They exist to prove that variation is systematic rather than four unrelated one-offs.

## Recipe must define

- accepted base body/rig/avatar family;
- clothing/wardrobe source families and compatibility rules;
- material/palette/accessory variation;
- hair/head/face options where available;
- scale/body-proportion bounds if safely adjustable;
- naming/prefab organization;
- collider/GC2 Character integration boundary;
- what changes are safe in Unity vs require Blender/source editing;
- clipping/skin-weight checks;
- fallback when a fantasy/medieval garment has useful donor geometry but unsuitable final styling;
- rejection rule for combinations that technically fit but look culturally/visually wrong.

## Visual target

Variants should read as ordinary inhabitants of the same northern Spanish port town, not fantasy adventurers, random asset-pack mannequins or costume-shop caricatures.

A source garment's original theme is not an automatic rejection. Adaptation is allowed when the final silhouette/material/details fit the product.

## Operator loop

`inspect available character/wardrobe corpus -> choose compatible bases -> assemble variants -> place in gameplay camera/lighting -> inspect clipping/scale -> correct -> owner review`

Use Blender/source tools only where they materially simplify adaptation. Do not build a generalized character generator unless the repeated work proves one is necessary.

## Required checks

For each accepted variant:

- rig/avatar valid;
- no severe skinning/exploded mesh issue;
- no obvious body-through-clothing clipping in idle + basic locomotion pose;
- feet/ground scale plausible;
- materials render correctly in current URP setup;
- prefab can be instantiated again without hidden hand setup;
- visual role is recorded in simple terms (age band / work-social role / silhouette) without overdesigning story.

## Evidence

Retain under `Docs/evidence/WP-PROD-CHAR-01/`:

- recipe;
- source/provenance notes;
- third-person captures of all accepted variants;
- at least one rejected/bad combination and why;
- operator intervention/failure notes;
- owner verdict on whether the group belongs to the intended game.

## PASS

PASS when:

- 4+ materially distinct civilian variants are retained;
- all share a repeatable base/wardrobe process;
- no variant requires unexplained bespoke repair;
- clipping/scale/rendering are acceptable for normal gameplay distance;
- owner accepts the group as a coherent starting civilian language;
- recipe is clear enough to generate more variants later.

## FAIL

FAIL if:

- success is four unrelated manually repaired characters;
- fantasy/source identity dominates the final civilians;
- clothing/rig compatibility is unresolved;
- variants only differ by trivial recolor;
- the solution depends on a large new character framework before proving simple prefab/recipe production.

## Non-goals

No hero/narrative character polish, facial dialogue system, final crowd count, full demographic plan or procedural population generator.

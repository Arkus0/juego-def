# Post-foundation production workpacks — factory phase

Status: **SUPERSEDED AS EXECUTION CONTRACT BY `Docs/workpacks/`**  
Purpose: retain the high-level production decomposition while the executable requirements live in one place.

## Current production strategy

juego-def does **not** jump straight into hand-producing lots of scenes/NPCs. It first builds the smallest effective graphical/content factories so that later breadth is cheap and repeatable.

The exit condition is not “we made one attractive example”. The exit condition is:

> creating the next normal asset/content item is mostly production work, not new pipeline R&D.

The factories may consist of metadata/catalogues, MCP/Unity workflows, adapted existing tools, Blender derivation recipes, prefab/templates, small Editor/batch tools, validators and semantic briefs. They should not become giant frameworks for their own sake.

## Reuse-first rule

The migrated pipeline research is now a binding input: [`../research/EXISTING_ASSET_PIPELINE_RESEARCH.md`](../research/EXISTING_ASSET_PIPELINE_RESEARCH.md).

Before writing equivalent custom tooling, the owning factory must bounded-test/disposition relevant existing techniques/tools such as Quaternius-native source workflows, `QuaterniusUnityUtils`, Chilyer/Tinqs/Avelune character techniques, `osm_building_grammar`, Blender->Unity export/material tooling and — only when a real gap exists — commercial building helpers.

The goal is **existing solution -> adapt -> minimal missing glue**, not invention-first.

## Executable sequence

Canonical contracts are under [`../workpacks/`](../workpacks/README.md):

1. `WP-PROD-ASSET-00` — start now from the accepted bootstrap: research spikes + shared asset catalogue, semantic discovery, lineage, intake conventions and cheap validation.
2. `WP-M0-00` — small gameplay integration fixture in parallel; not a gate on factory R&D.
3. Parallel graphical factories after ASSET-00:
   - `WP-PROD-ENV-01` — environment asset + assembly factory;
   - `WP-PROD-CHAR-01` — civilian/wardrobe factory;
   - `WP-PROD-ANIM-01` — animation intake + retarget factory.
4. Scale proofs:
   - `WP-PROD-ENV-02` — three materially distinct keeper environment compositions;
   - `WP-PROD-CHAR-02` — 12–20 civilian batch;
   - `WP-PROD-ANIM-02` — shared runtime animation vocabulary + batch use.
5. In parallel from bootstrap:
   - `WP-PROD-DIALOGUE-01` — repeatable investigation-dialogue authoring path;
   - `WP-PROD-UI-01` — reusable no-voice presentation factory.
6. `WP-CITY-URBAN-01` — first integrated keeper block, requiring M0 + accepted factory outputs.
7. `WP-PROD-LOOK-GATE` — fresh-production challenge proving the factories are ready for content at scale.

## Factory intent by lane

### ENV

Produce a searchable/reusable architectural and urban kit from real source material, including reuse of audited tooling/grammars, adaptation/donor/derived workflows, material variants, assembly grammar and validators. Then prove that the same factory can produce several different keeper spaces without restarting the pipeline.

### CHAR

Start from the shared Quaternius humanoid/wardrobe ecosystem and audited character/clothing pipeline techniques. Encode rig/body/wardrobe compatibility, palette/accessory variation, prefab generation and clipping/scale/material validation. Then prove batch production without clones or bespoke repairs.

### ANIM

Start from real UAL/shared-rig/import research. Index motion semantically, batch-import/retarget it, validate bad clips and expose a reusable runtime vocabulary so NPC production does not know raw clip plumbing.

### DIALOGUE/UI

Make contextual investigation conversations and their no-voice presentation repeatable content production rather than scene-specific Unity wiring.

## Production lock

`PROD-LOOK-GATE` is lightweight but strict about scalability. It includes a fresh brief challenge that must create new environment/civilians/animation breadth/dialogue using the accepted factories **without foundational tooling changes**.

After PASS, roadmap emphasis moves to content:

- routines/living block;
- investigation content;
- jobs/minigames;
- chase;
- melee/confrontation;
- 20–30 minute slice;
- district/population expansion.

## Anti-pattern

Do not recreate Juego2's infrastructure-heavy gates, but also do not mistake one polished demo for a production pipeline. The goal is a small-team asset/content factory that can feed the game repeatedly, while exploiting prior ecosystem research before writing our own machinery.

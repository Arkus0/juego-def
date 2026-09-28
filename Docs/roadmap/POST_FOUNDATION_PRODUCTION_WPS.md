# Post-foundation production workpacks — factory phase

Status: **SUPERSEDED AS EXECUTION CONTRACT BY `Docs/workpacks/`**  
Purpose: retain the high-level production decomposition while the executable requirements live in one place.

## Current production strategy

juego-def does **not** jump straight into hand-producing lots of scenes/NPCs. It first builds the smallest effective graphical/content factories so that later breadth is cheap and repeatable.

The factories have a concrete first customer: [`../design/FIRST_KEEPER_BLOCK_B0.md`](../design/FIRST_KEEPER_BLOCK_B0.md), the migrated CITY brief for B0 Mercado–Muelle. CITY supplies **what the first keeper block needs**; the production lanes build **how to manufacture it repeatedly**.

The exit condition is not “we made one attractive example”. The exit condition is:

> creating the next normal asset/content item is mostly production work, not new pipeline R&D.

The factories may consist of metadata/catalogues, MCP/Unity workflows, adapted existing tools, Blender derivation recipes, prefab/templates, small Editor/batch tools, validators and semantic briefs. They should not become giant frameworks for their own sake.

## Reuse-first rule

The migrated pipeline research is a binding input: [`../research/EXISTING_ASSET_PIPELINE_RESEARCH.md`](../research/EXISTING_ASSET_PIPELINE_RESEARCH.md).

Before writing equivalent custom tooling, the owning factory must bounded-test/disposition relevant existing techniques/tools. The goal is **existing solution -> adapt -> minimal missing glue**, not invention-first.

## Executable sequence

Canonical contracts are under [`../workpacks/`](../workpacks/README.md):

1. `WP-PROD-ASSET-00` — start now from the accepted bootstrap: research spikes + shared asset catalogue, semantic discovery, lineage, intake conventions, cheap validation and B0 coverage view.
2. `WP-M0-00` — small gameplay integration fixture in parallel; not a gate on factory R&D.
3. Parallel graphical factories after ASSET-00:
   - `WP-PROD-ENV-01` — environment asset + assembly factory serving B0 vocabulary first;
   - `WP-PROD-CHAR-01` — civilian/wardrobe factory serving B0 roles first;
   - `WP-PROD-ANIM-01` — animation intake + retarget factory serving B0 motion needs first.
4. Scale proofs: `ENV-02`, `CHAR-02`, `ANIM-02`.
5. In parallel from bootstrap: `PROD-DIALOGUE-01` and `PROD-UI-01`.
6. `WP-CITY-URBAN-01` — realize B0 Mercado–Muelle as the first integrated keeper block, requiring M0 + accepted factory outputs.
7. `WP-PROD-LOOK-GATE` — fresh-production challenge proving the factories are ready for content at scale.

## Factory intent by lane

### ENV

Produce a searchable/reusable architectural and urban kit from real source material. Its first demand is B0: mixed commercial frontage, shop/service thresholds, lodging entrance language, stairs/retaining/railings, public quay/working-water edge, market/port props, signage mounting and ordinary closed fabric.

### CHAR

Start from the shared Quaternius humanoid/wardrobe ecosystem and audited character/clothing pipeline techniques. First cover B0 roles such as shop/market worker, dock/port worker, residents and ordinary service people; then prove batch production without clones or bespoke repairs.

### ANIM

Start from real UAL/shared-rig/import research. Prioritize B0 locomotion, conversation, ambient, market/port work, interaction and follow/chase-support motions before unrelated breadth.

### DIALOGUE/UI

Make contextual investigation conversations and their no-voice presentation repeatable content production rather than scene-specific Unity wiring, using the B0 shop/witness and changed-return patterns as initial demand.

## CITY migration rule

Juego2 CITY is **not** copied wholesale.

Migrated:

- accepted B0 Mercado–Muelle product brief;
- direct/alternate routes and real loop intent;
- lodging/market/shop/port/overlook/observation roles;
- public/service/private truth;
- expansion seams;
- CITY-07/CITY-09 game-space lessons: route learning, compression/expansion/reveal, threshold readability, coherent elevation, framed views, nooks and third-person staging.

Not migrated:

- old inland Puente Viejo/Liébana geometry;
- H1/H2F prerequisites;
- CITY-04 historical remeasurement bureaucracy;
- old causal-owner governance as production architecture.

## Production lock

`PROD-LOOK-GATE` includes a fresh brief challenge that must create new environment/civilians/animation breadth/dialogue using the accepted factories **without foundational tooling changes**.

After PASS, roadmap emphasis moves to routines/living block, investigation content, jobs/minigames, chase, melee/confrontation, 20–30 minute slice and district/population expansion.

## Anti-pattern

Do not recreate Juego2's infrastructure-heavy gates, but also do not mistake one polished demo for a production pipeline. The goal is a small-team asset/content factory that can feed the game repeatedly and is grounded in a real city-content demand brief.

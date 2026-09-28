# WP-PROD-ASSET-00 — Shared Graphical Asset Factory Substrate

Status: **READY / START NOW**  
Class: PRODUCTION FACTORY / SHARED ASSET SUBSTRATE  
Depends on: Bootstrap Unity + GC2 Core PASS  
Blocks: `WP-PROD-ENV-01`, `WP-PROD-CHAR-01`, `WP-PROD-ANIM-01`

## Claim

juego-def has a shared, searchable and reproducible asset-production substrate so ENV/CHAR/ANIM workers can manufacture content from the real source corpus without rediscovering packages, paths, import rules, provenance or adaptation conventions for every asset.

This WP is deliberately **not** a giant asset-management platform and does not decide city topology. It creates the common machinery required to make the graphical lanes scalable while `WP-CITY-URBAN-00` runs in parallel to define accepted environment demand.

## Binding product demand

Consume the current [`../design/FIRST_KEEPER_BLOCK_B0.md`](../design/FIRST_KEEPER_BLOCK_B0.md) as provisional/current demand while `WP-CITY-URBAN-00` validates it.

The catalogue and first indexed/admitted corpus must be useful for B0 Mercado–Muelle, especially:

- commercial facades, corners, openings, thresholds and ordinary closed frontage;
- stairs/ramps/retaining/railings and waterfront/public-port pieces;
- market/port/shop/street props and signage mounting;
- civilian body/wardrobe families covering market/shop, dock/port, residents and ordinary service roles;
- locomotion, conversation, ambient and market/port work animations.

A technically elegant catalogue that does not expose candidates for near-term city demand is not sufficient. If `CITY-URBAN-00` materially amends B0, reconcile the coverage view rather than rebuilding the substrate.

## Binding research input — reuse before invention

Consume [`../research/EXISTING_ASSET_PIPELINE_RESEARCH.md`](../research/EXISTING_ASSET_PIPELINE_RESEARCH.md) before implementing equivalent custom tooling.

Mandatory first actions:

1. inspect the actual owned/admitted Quaternius source corpus and source projects;
2. identify which native/source metadata can be indexed rather than manually re-authored;
3. bounded-spike `QuaterniusUnityUtils` against current Unity 6000.3.24f1 for the import/collision jobs relevant to our corpus;
4. record `USE / ADAPT / REFERENCE_ONLY / REJECT / NOT_MATERIAL / DEFER` decisions;
5. implement only common glue still missing after those checks.

Retain `Docs/evidence/WP-PROD-ASSET-00/REUSE_DECISIONS.md`.

## Factory outputs

By PASS, the repo/project must contain:

1. a machine-readable **source/admitted asset catalogue** for the real lawful corpus used by juego-def;
2. stable tags/roles sufficient for AI/operator discovery;
3. source -> imported -> adapted/derived lineage/provenance;
4. deterministic folder/naming conventions for retained production assets;
5. repeatable import/adaptation entry points for the asset families actually used;
6. cheap preview/inspection capability so a worker can search candidates without manually opening hundreds of files;
7. lightweight validators for common broken states;
8. a defined place for generated/derived assets that does not mutate vendor/source packages in place;
9. a provisional/current coverage view against B0/CITY demand.

## Minimum catalogue fields

Use JSON/CSV/ScriptableObject/index or an equivalent machine-readable representation. For every admitted or candidate asset family, support where applicable:

- stable local ID/path;
- source pack/provider/version or acquisition identity;
- asset type/family;
- semantic tags/production roles;
- intended lane(s): ENV / CHAR / ANIM / PROP / UI;
- reuse class: `DIRECT`, `ADAPTABLE`, `DONOR`, `CREATE_DERIVED`, `REJECT`, `BLOCKED_EXTERNAL`;
- license/provenance pointer;
- import/rig/material notes;
- known incompatibilities;
- derived-output linkage.

The catalogue does not need to enumerate every irrelevant vendor file manually if indexing can derive entries automatically.

## Discovery requirement

The MCP/operator must be able to ask questions such as:

- "show me doors/windows suitable for B0 commercial frontage";
- "find stairs/railings/retaining pieces for the B0 upper/port loop";
- "find civilian-compatible clothing for market/shop/dock roles";
- "find humanoid talk/idle/work animations for B0";
- "find port/market props";

without receiving exact file paths from the owner for every candidate.

This can be achieved by generated inventories, metadata, thumbnails/previews, searchable docs/indexes or small Editor tooling. Choose the simplest reliable mechanism.

## Source preservation

- do not destructively edit vendor/source packages in place;
- derived/adapted production assets live in juego-def-owned locations;
- record enough lineage to reproduce or replace them;
- licensed/restricted bytes remain handled lawfully and need not be committed merely to satisfy this WP.

## Validation baseline

Provide lightweight checks where relevant for missing materials/textures, broken prefab references, obvious scale/import anomalies, humanoid/avatar invalidity, duplicate/missing source identifiers and derived assets with no lineage record.

Do not build a universal validator for hypothetical future asset types.

## Batch proof

Run the substrate over at least the source families immediately needed by current B0/CITY demand and the next lanes and show that it can discover/index a **non-trivial batch**, not just 5 hand-entered examples.

Minimum evidence should cover environment/building/prop material, character/wardrobe material and animation material with explicit B0-demand search examples.

## Evidence

Retain under `Docs/evidence/WP-PROD-ASSET-00/`:

- `REUSE_DECISIONS.md`;
- catalogue/index format and generated snapshot;
- source families covered;
- current B0/CITY demand coverage/gap list;
- import/derived folder conventions;
- example semantic searches used by the operator;
- validator output;
- known corpus gaps/external packages not currently available.

## PASS

PASS when:

- existing/native pipeline candidates were actually evaluated before equivalent custom code was written;
- ENV/CHAR/ANIM can consume the same asset substrate without independent rediscovery of source/provenance/path conventions;
- operator can discover useful B0-relevant candidates semantically from a non-trivial batch;
- derived assets have a reproducible owned destination + lineage;
- common bad-import/broken-reference conditions have a cheap detection path;
- current B0/CITY demand has an explicit coverage/gap view;
- adding another asset from an already-covered source family is routine production work.

ASSET-00 PASS does **not** authorize ENV-01 by itself: ENV also requires `WP-CITY-URBAN-00` PASS so the environment factory is driven by accepted city demand.

## FAIL

FAIL if the result is only a prose list, every later WP still needs exact owner-provided paths, B0/CITY demand remains invisible to the catalogue, vendor assets must be destructively edited, existing relevant pipelines were ignored and reimplemented without a bounded evaluation, or the WP expands into building a generic DAM system unrelated to near-term production.

## Handoff

On PASS:

- `PROD-CHAR-01` and `PROD-ANIM-01` may start, consuming B0 role priorities;
- `PROD-ENV-01` starts only when both `PROD-ASSET-00` and `WP-CITY-URBAN-00` are PASS.

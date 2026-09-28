# WP-PROD-ASSET-00 — Shared Graphical Asset Factory Substrate

Status: **READY AFTER M0**  
Class: PRODUCTION FACTORY / SHARED ASSET SUBSTRATE  
Depends on: `WP-M0-00` PASS  
Blocks: `WP-PROD-ENV-01`, `WP-PROD-CHAR-01`, `WP-PROD-ANIM-01`

## Claim

juego-def has a shared, searchable and reproducible asset-production substrate so ENV/CHAR/ANIM workers can manufacture content from the real source corpus without rediscovering packages, paths, import rules, provenance or adaptation conventions for every asset.

This WP is deliberately **not** a giant asset-management platform. It creates only the common machinery required to make the graphical lanes scalable.

## Factory outputs

By PASS, the repo/project must contain:

1. a machine-readable **source/admitted asset catalogue** for the real lawful corpus used by juego-def;
2. stable tags/roles sufficient for AI/operator discovery;
3. source -> imported -> adapted/derived lineage/provenance;
4. deterministic folder/naming conventions for retained production assets;
5. repeatable import/adaptation entry points for the asset families actually used;
6. cheap preview/inspection capability so a worker can search candidates without manually opening hundreds of files;
7. lightweight validators for common broken states;
8. a defined place for generated/derived assets that does not mutate vendor/source packages in place.

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

- "show me doors/windows suitable as donor components";
- "find civilian-compatible clothing pieces";
- "find humanoid talk/idle/work animations";
- "find port/market props";

without receiving exact file paths from the owner for every candidate.

This can be achieved by generated inventories, metadata, thumbnails/previews, searchable docs/indexes or small Editor tooling. Choose the simplest reliable mechanism.

## Source preservation

- do not destructively edit vendor/source packages in place;
- derived/adapted production assets live in juego-def-owned locations;
- record enough lineage to reproduce or replace them;
- licensed/restricted bytes remain handled lawfully and need not be committed merely to satisfy this WP.

## Validation baseline

Provide lightweight checks where relevant for:

- missing materials/textures;
- broken prefab references;
- obvious scale/import anomalies;
- humanoid/avatar invalidity;
- duplicate/missing source identifiers;
- derived asset with no lineage record.

Do not build a universal validator for hypothetical future asset types.

## Batch proof

Run the substrate over at least the source families immediately needed by the next lanes and show that it can discover/index a **non-trivial batch**, not just 5 hand-entered examples.

Minimum evidence should cover:

- environment/building/prop material;
- character/wardrobe material;
- animation material.

## Evidence

Retain under `Docs/evidence/WP-PROD-ASSET-00/`:

- catalogue/index format and generated snapshot;
- source families covered;
- import/derived folder conventions;
- example semantic searches used by the operator;
- validator output;
- known corpus gaps/external packages not currently available.

## PASS

PASS when:

- ENV/CHAR/ANIM can consume the same asset substrate without independent rediscovery of source/provenance/path conventions;
- operator can discover useful candidates semantically from a non-trivial batch;
- derived assets have a reproducible owned destination + lineage;
- common bad-import/broken-reference conditions have a cheap detection path;
- adding another asset from an already-covered source family is routine production work.

## FAIL

FAIL if the result is only a prose list, every later WP still needs exact owner-provided paths, vendor assets must be destructively edited, or the WP expands into building a generic DAM system unrelated to near-term production.

## Handoff

On PASS, start `PROD-ENV-01`, `PROD-CHAR-01` and `PROD-ANIM-01` in parallel. Their job is to turn this substrate into lane-specific **factories capable of batch production**.

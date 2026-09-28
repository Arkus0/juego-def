# WP-PROD-LOOK-GATE — Production Factory Lock

Status: **READY AFTER CITY-URBAN-01**  
Class: PRODUCT GATE / PRODUCTION READINESS  
Depends on: `WP-CITY-URBAN-01` PASS

## Claim

The graphical/content production stack is mature enough that juego-def can now shift from pipeline discovery to **content production at scale**.

This gate is deliberately not an infrastructure mega-gate. It asks one practical question:

> Can we now make more streets, buildings, civilians, animations and dialogue content mainly by using the factories, rather than inventing new production infrastructure each time?

## Required evidence set

Consume accepted evidence from:

- `PROD-ASSET-00`
- `PROD-ENV-01` + `PROD-ENV-02`
- `PROD-CHAR-01` + `PROD-CHAR-02`
- `PROD-ANIM-01` + `PROD-ANIM-02`
- `PROD-DIALOGUE-01`
- `PROD-UI-01`
- `CITY-URBAN-01`

## PASS dimensions

### Shared asset substrate

- source/admitted corpus is searchable and has lineage;
- operator can discover normal candidates semantically;
- adding an asset from a covered family does not require rediscovering import/provenance conventions.

### Environment factory

- reusable modular/derived kit exists;
- three materially different keeper compositions were produced through the same factory;
- route/collision validation works;
- next street/building composition is primarily art/content work rather than pipeline R&D.

### Character factory

- 12–20 coherent ordinary civilians exist through one factory;
- clone/clipping/rig/material failures are manageable through the factory;
- scaling toward many more civilians is mostly production volume.

### Animation factory

- meaningful batch intake/retarget works;
- semantic runtime vocabulary works across several civilians;
- adding more ordinary ambient/conversation/work motions is mostly content intake/mapping.

### Dialogue/UI factory

- multiple investigation conversations share one authoring path;
- reusable no-voice UI/presentation serves multiple conversations/prompts;
- adding more normal dialogue content does not require scene-specific plumbing.

### Integrated block

- owner accepts `CITY-URBAN-01` as keeper content;
- it uses factory outputs rather than bypassing them;
- remaining blockers are feature/content breadth, polish or truly new asset families.

## Scale-readiness challenge

Before PASS, perform one small **fresh-production challenge** from a new brief:

- one new environment micro-composition or frontage variation;
- 3 new/recombined civilian variants;
- 3 additional admitted/mapped animation clips or equivalent animation-breadth additions;
- one new contextual dialogue using existing UI.

The challenge must use the accepted factories without creating new foundational tooling. Small local fixes are allowed; systemic factory redesign means the gate is not ready.

## Authoring-path finalization

Consume the ENV-02 recommendation and choose one current default:

- `PRIMARY_AUTHORING_PATH`
- `BOUNDED_OPERATOR`
- `TOOL_SOURCE_ONLY`

Do not keep the status ambiguous after the factory evidence exists.

## PASS

PASS when:

- the fresh-production challenge succeeds without foundational rework;
- owner accepts visual/product quality of keeper outputs;
- no lane still depends on hidden bespoke per-asset setup;
- source/provenance/derived outputs remain reproducible enough for continued production;
- team can reasonably start producing district/NPC/activity/story breadth in parallel.

## FAIL

FAIL if normal new content still repeatedly requires:

- exact path spoon-feeding;
- bespoke import/rig/material surgery;
- new scene-specific framework code;
- hidden vendor-package mutation;
- major factory redesign;
- dressed-greybox acceptance merely to keep moving.

## After PASS

Move the roadmap emphasis from **factory construction** to **content production**:

- first living block/routines;
- investigation content;
- jobs/minigames;
- chase;
- melee/confrontation;
- 20–30 minute slice;
- additional neighbourhoods and larger population batches.

Factories continue to evolve only when genuinely new production families or recurring bottlenecks justify extension.

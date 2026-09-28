# Juego2 knowledge migration baseline

Status: **MIGRATION SNAPSHOT**  
Date: 2026-09-28

## Purpose

Preserve the product/production knowledge earned in `Arkus0/Juego2` while deliberately **not** inheriting its architecture by default.

juego-def is allowed to learn from Juego2. It is not required to remain compatible with H0, H1, old CITY contracts, H2F lifecycle, old gates or old execution policy.

## Migrated as current juego-def knowledge

### Product

- large fictional northern-Spain working port town;
- late-1990s / early-2000s feel;
- compact high-density neighbourhoods rather than a huge sparse map;
- investigation + everyday life + adventure loop;
- 20–30 minute future slice with clue/questions/port access/tailing/chase/confrontation/return consequence;
- five production neighbourhoods: Casco, Mercado, Muelle, Talleres, Viviendas;
- Casco nightlife-primary; Talleres nightlife-secondary; Muelle night-work-primary;
- final town proper name remains undecided;
- layered NPC depth, with routine complexity separate from narrative depth.

### Visual/ART

- stylized low-poly late-PS2/early-PS3 production language;
- damp Atlantic/northern light and working-port identity;
- final judgment at composed scene level, not per-asset geographic literalism;
- wood is allowed;
- medieval/fantasy-origin material may be adapted or harvested as donor components;
- explicit rejection of dressed-greybox keeper scenes;
- reuse order: `DIRECT -> ADAPTABLE -> DONOR -> CREATE_DERIVED -> REJECT/BLOCKED_EXTERNAL`;
- Quaternius is an editable parts ecosystem rather than only final prefabs.

### Quaternius/tooling

- shared character/wardrobe/animation ecosystem is a major production advantage;
- inspect existing public/commercial techniques before inventing pipelines;
- QuaterniusUnityUtils, character/clothing pipeline references, semantic building grammars and batch tooling are known candidates;
- exact source/version/license/provenance must be revalidated before actual adoption.

### GC2

- GC2-first gameplay architecture;
- buy/adopt modules only when real features justify them;
- Hub triage rule: `GC2 native -> Hub -> adapt source -> custom code`;
- useful Hub authoring ideas exist, especially reusable Actions arguments, spatial iteration/navigation helpers and dialogue import/authoring;
- Hub does not provide a proven whole living-city solution.

### Production

- environment, character, animation and dialogue/UI production should become repeatable before deep content breadth;
- repeated-build proof matters more than one attractive demo;
- factories may be recipes/briefs/validation rather than large bespoke frameworks;
- fresh-author/agent repeatability is a meaningful production test.

## Explicitly not inherited

- H0 harness as default game kernel;
- H1 canonical->Unity bridge/materialize/reconcile lifecycle;
- whole-world CAS/replay/snapshot architecture;
- old Potes/Liébana setting authority;
- old CITY node/edge matrices as mandatory geography;
- old H2F/H2 gates and workpack DAG as governance;
- requirement that future packages/assets prove compatibility with H1;
- assumption that Arkus owns persistence before GC2/local gameplay demonstrates a real gap.

## Pending external decision

`Juego2/WP-AI-UNITY-AUTHORING-00` is deliberately **not** copied as architecture. Its evidence will be consumed by `Docs/architecture/PRODUCTION_AUTHORING_DECISION.md`.

A top result may make an AI Unity operator the primary physical authoring path for ENV/CHAR/ANIM. A weak result does not invalidate this migration; juego-def remains GC2-first with direct Unity authoring.

## Source snapshot in Juego2

High-value source records at migration time include:

- `Docs/art/VISUAL_BIBLE.md`
- `Docs/product/ASSET_REUSE_VISUAL_DIRECTION_AMENDMENT.md`
- `Docs/product/PORT_TOWN_SCALE_AMENDMENT.md`
- `Docs/product/PORT_TOWN_IDENTITY_NIGHTLIFE_AMENDMENT.md`
- `Docs/product/SHENMUE_URBAN_SLICE_TARGET.md`
- `Docs/product/VISUAL_PRODUCTION_FACTORY_AMENDMENT.md`
- `Docs/discovery/QUATERNIUS_ADAPTATION_ECOSYSTEM_AUDIT.md`
- `Docs/discovery/QUATERNIUS_TOOLING_CATALOG.md`
- `Docs/discovery/QUATERNIUS_WP_IMPACT_MAP.md`
- `Docs/discovery/GC2_HUB_REUSE_AUDIT.md`
- `Docs/discovery/GC2_HUB_EXTENSION_CATALOG.csv`
- `Docs/discovery/GC2_HUB_COVERAGE_INVENTORY.csv`
- `Docs/workpacks/ART/WP-AI-UNITY-AUTHORING-00.md`

These remain historical/source evidence. The distilled juego-def documents govern this repository unless deliberately amended here.

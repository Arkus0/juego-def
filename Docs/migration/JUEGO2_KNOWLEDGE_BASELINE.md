# Juego2 knowledge migration baseline

Status: **MIGRATION SNAPSHOT**  
Date: 2026-09-28

## Purpose

Preserve the product/production knowledge earned in `Arkus0/Juego2` while deliberately **not** inheriting its architecture by default.

juego-def is allowed to learn from Juego2. It is not required to remain compatible with H0, H1, old CITY governance, H2F lifecycle, old gates or old execution policy.

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

### CITY / game-space

Migrated from accepted `CITY-URBAN-00` plus useful CITY-07/CITY-09 design lessons into `Docs/design/FIRST_KEEPER_BLOCK_B0.md`:

- first keeper block is B0 Mercado–Muelle;
- lodging/return, market/activity, shop+witness threshold, commercial run, port reveal/public quay, upper observation/alternate route and expansion seams;
- direct + alternate routes and genuine cycles;
- public/service/private and public-port/controlled-work access truth;
- compact third-person game-space composition: route learning, compression/expansion/reveal, threshold readability, framed views, useful nooks and coherent local elevation;
- spatial support for follow/search/chase/conversation without implementing those gameplay systems merely to prove geometry.

Not migrated as product authority: old inland Puente Viejo/Liébana exact geometry, crossings, masks, route costs, CITY-04 historical remeasurement machinery or H1/H2F prerequisites.

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
- exact source/version/license/provenance must be revalidated before actual adoption;
- the distilled execution baseline now lives in `Docs/research/EXISTING_ASSET_PIPELINE_RESEARCH.md`.

### GC2

- GC2-first gameplay architecture;
- buy/adopt modules only when real features justify them;
- Hub triage rule: `GC2 native -> Hub -> adapt source -> custom code`;
- useful Hub authoring ideas exist, especially reusable Actions arguments, spatial iteration/navigation helpers and dialogue import/authoring;
- Hub does not provide a proven whole living-city solution;
- Dialogue 2 is optional and materiality-driven; Core/local is a legitimate retained path;
- no-voice dialogue presentation is a valid production baseline;
- Alias remains `RESEARCH_PENDING` until exact documentation/source/compatibility/license evidence is available again.

### Production

- environment, character, animation and dialogue/UI production should become repeatable before deep content breadth;
- repeated-build proof matters more than one attractive demo;
- factories may be recipes/briefs/validation plus small tooling rather than large bespoke frameworks;
- fresh-author/agent repeatability is a meaningful production test;
- factory output is now driven by concrete B0 product demand rather than generic asset breadth.

## Explicitly not inherited

- H0 harness as default game kernel;
- H1 canonical->Unity bridge/materialize/reconcile lifecycle;
- whole-world CAS/replay/snapshot architecture;
- old Potes/Liébana setting authority;
- old inland CITY node/edge matrices as final geography;
- old CITY causal-owner bureaucracy as production architecture;
- old H2F/H2 gates and workpack DAG as governance;
- requirement that future packages/assets prove compatibility with H1;
- assumption that Arkus owns persistence before GC2/local gameplay demonstrates a real gap.

## Authoring decision

juego-def has adopted `BOUNDED_OPERATOR` for production authoring. Juego2 `WP-AI-UNITY-AUTHORING-00` remains useful confirming/overturning evidence, not an architectural blocker.

## Source snapshot in Juego2

High-value source records at migration time include:

- `Docs/art/VISUAL_BIBLE.md`
- `Docs/product/ASSET_REUSE_VISUAL_DIRECTION_AMENDMENT.md`
- `Docs/product/PORT_TOWN_SCALE_AMENDMENT.md`
- `Docs/product/PORT_TOWN_IDENTITY_NIGHTLIFE_AMENDMENT.md`
- `Docs/product/SHENMUE_URBAN_SLICE_TARGET.md`
- `Docs/product/VISUAL_PRODUCTION_FACTORY_AMENDMENT.md`
- `Docs/production/CITY_PORT_TOWN_TRANSITION.md`
- `Docs/workpacks/CITY/WP-CITY-URBAN-00.md`
- `Docs/workpacks/CITY/WP-CITY-07.md` (game-space lessons only)
- `Docs/workpacks/CITY/WP-CITY-09.md` (play-design lenses only)
- `Docs/discovery/QUATERNIUS_ADAPTATION_ECOSYSTEM_AUDIT.md`
- `Docs/discovery/QUATERNIUS_TOOLING_CATALOG.md`
- `Docs/discovery/QUATERNIUS_WP_IMPACT_MAP.md`
- `Docs/discovery/GC2_HUB_REUSE_AUDIT.md`
- `Docs/workpacks/GC2/WP-GC2-DIALOGUE-00.md`
- `Docs/workpacks/ART/WP-AI-UNITY-AUTHORING-00.md`

These remain historical/source evidence. The distilled juego-def documents govern this repository unless deliberately amended here.

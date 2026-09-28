# Juego2 knowledge migration baseline

Status: **MIGRATION SNAPSHOT — V2 COMPLETE**  
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

`Docs/design/NPC_DEPTH_TIERS.md` preserves the accepted planning distinction between ~10–15 deeply systemic A actors, ~20–40 named/reactive B actors and a broader ambient/population C layer within an initial ~80–120 visible/recurring town population. It also preserves the separate rough goal of ~60–100 routine-bearing identities without implying that all require Tier-A memory/relationship/agency cost.

### CITY / game-space

The source transition in **Juego2** `WP-CITY-URBAN-00` is `COMPLETE / ACCEPTED` (PR #265). Its useful result plus CITY-07/CITY-09 game-space lessons were migrated into juego-def, especially `Docs/design/FIRST_KEEPER_BLOCK_B0.md`:

- first keeper block is B0 Mercado–Muelle;
- lodging/return, market/activity, shop+witness threshold, commercial run, port reveal/public quay, upper observation/alternate route and expansion seams;
- direct + alternate routes and genuine cycles;
- public/service/private and public-port/controlled-work access truth;
- compact third-person game-space composition: route learning, compression/expansion/reveal, threshold readability, framed views, useful nooks and coherent local elevation;
- spatial support for follow/search/chase/conversation without implementing those gameplay systems merely to prove geometry.

**Important:** migration of that accepted source does not automatically PASS the separate executable `juego-def/WP-CITY-URBAN-00`. The local WP remains `READY / PARALLEL` and owns formal closure of the five-zone topology handoff, factory-demand coverage statuses and deferred-question list before `PROD-ENV-01` starts.

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
- distilled execution baseline lives in `Docs/research/EXISTING_ASSET_PIPELINE_RESEARCH.md`;
- detailed Juego2 audits remain indexed in `Docs/research/LEGACY_RESEARCH_SOURCE_INDEX.md` for escalation.

### GC2

- GC2-first gameplay architecture;
- buy/adopt modules only when real features justify them;
- Hub triage rule: `GC2 native -> Hub -> adapt source -> custom code`;
- useful Hub authoring ideas exist, especially reusable Actions arguments, spatial iteration/navigation helpers and dialogue import/authoring;
- Hub does not provide a proven whole living-city solution;
- Dialogue 2 is optional and materiality-driven; Core/local is a legitimate retained path;
- no-voice dialogue presentation is a valid production baseline;
- Alias remains `RESEARCH_PENDING` until exact documentation/source/compatibility/license evidence is available again;
- raw Hub coverage/catalog datasets remain explicitly indexed before fresh Hub discovery is repeated.

### Living World / PA

Accepted Juego2 PA-01..13 are distilled into `Docs/research/living-world/LIVING_WORLD_KNOWLEDGE.md` without their old H3/H4/H0 routing.

Preserved semantic spine includes:

- routine intent vs actual state;
- bounded actor-owned agency;
- directed typed relationships;
- truth vs actor belief/ignorance/deception;
- deliberate rumour/information transfer and provenance privacy;
- bounded selected memory and causal consequences;
- human-facing work/services/material dependencies without macroeconomy;
- minigames/activities integrated with ordinary town context and aftermath;
- player/NPC origin-neutral semantic world actions;
- bounded causal chains without hidden storyteller authority;
- investigation through legitimate traces/evidence rather than truth oracle;
- governance through explicit rule/opportunity changes, not mind control;
- simulation-control budgets that regulate execution without stealing semantics or preventing sustained transformation.

PA-14 is not migrated as the old H2-gated workpack. A future juego-def Living World integration proof will be derived only after real implementation exists.

### Gameplay-system lessons

`Docs/research/GAMEPLAY_SYSTEMS_KNOWLEDGE.md` preserves reusable non-H0/H1 findings:

- `WORLD PROP / PORTABLE ITEM / CONSEQUENTIAL OBJECT` interaction-cost separation;
- GameFlow as shared player/camera/actor ownership and safe transition/release;
- reusable explainable condition semantics when cross-system demand earns them;
- structured outcomes as narrow integration seams, not event-sourcing mandate;
- PersistentActor vs AmbientPopulation;
- schedule as expectation rather than waypoint screenplay;
- FULL/ABSTRACT continuity of meaningful causal state;
- prior-art workflow and recovered fixture/failure-case bank.

### Agent operations

The useful operating discipline has been migrated and simplified:

- root `AGENTS.md` defines Owner, Worker, Unity/Asset Operator, independent Reviewer and Repair Worker;
- `.agents/skills/**` provides implement/review/repair/plan/docsync/unity-operator flows;
- `.claude/skills/**` contains thin wrappers to the canonical skills;
- exact-SHA candidate identity, strict Worker pre-review and independent Reviewer falsification are retained;
- repair targets the causal blocker class;
- DocSync defaults to zero commit unless authoritative durable meaning changed;
- H1 execution, Automation V2, CTX capsules and old lifecycle ceremony are not inherited.

### Production

- environment, character, animation and dialogue/UI production should become repeatable before deep content breadth;
- repeated-build proof matters more than one attractive demo;
- factories may be recipes/briefs/validation plus small tooling rather than large bespoke frameworks;
- fresh-author/agent repeatability is a meaningful production test;
- factory output is driven by concrete B0 product demand rather than generic asset breadth;
- dependency/provenance rules are now local in `Docs/operations/DEPENDENCY_AND_PROVENANCE_POLICY.md`.

## Explicitly not inherited

- H0 harness as default game kernel;
- H1 canonical->Unity bridge/materialize/reconcile lifecycle;
- whole-world CAS/replay/snapshot architecture;
- old Potes/Liébana setting authority and its visual-reference index as current art direction;
- old inland CITY node/edge matrices as final geography;
- old CITY causal-owner bureaucracy as production architecture;
- old H2F/H2 gates and workpack DAG as governance;
- requirement that future packages/assets prove compatibility with H1;
- assumption that Arkus owns persistence before GC2/local gameplay demonstrates a real gap;
- Automation V2, CTX capsule/envelope machinery and old H1-specific local executor;
- old runtime/WorldState/DFU/Shenmue implementation wrappers from prior knowledge harvests.

## Authoring decision

juego-def has adopted `BOUNDED_OPERATOR` for production authoring. Juego2 `WP-AI-UNITY-AUTHORING-00` remains useful confirming/overturning evidence, not an architectural blocker.

## Source snapshot / escalation

High-value historical sources remain listed in `Docs/research/LEGACY_RESEARCH_SOURCE_INDEX.md`. Juego2 is the evidence archive, not a routine dependency.

A normal fresh Worker should use juego-def authorities. Reopen Juego2 only for a concrete omitted fixture/detail/provenance question or when a current adoption decision needs raw audit evidence.

## Final closure

`Docs/migration/JUEGO2_FINAL_MIGRATION_AUDIT.md` classifies the major Juego2 families as `MIGRATED / ABSORBED / REFERENCE_ONLY / DROP / FUTURE_ONLY`.

After that audit, a newly discovered useful Juego2 item is an exception and must justify its concrete value before migration. No old architecture comes with it automatically.

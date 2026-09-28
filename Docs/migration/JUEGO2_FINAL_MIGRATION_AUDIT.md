# Juego2 final migration audit

Status: **CLOSURE AUDIT**  
Date: 2026-09-28

## Goal

Make `juego-def` operationally independent of Juego2 for normal production while retaining Juego2 as a historical evidence/research archive.

Classification:

- `MIGRATED` — useful meaning now exists in juego-def and should be consumed here.
- `ABSORBED` — useful lesson is already represented by stronger/current juego-def docs or workpacks.
- `REFERENCE_ONLY` — source remains worth consulting for detail/fixtures/history but is not current authority.
- `DROP` — do not migrate; obsolete architecture/governance or negative value for current production.
- `FUTURE_ONLY` — not needed now; revisit only when a concrete product problem demands it.

## Family audit

| Juego2 family | Status | juego-def destination / rationale |
| --- | --- | --- |
| Product vision / port-city amendments | `MIGRATED` | `Docs/design/GAME_VISION.md`, `PORT_TOWN_WORLD_MODEL.md`, roadmap |
| NPC depth tiers / population-depth distinction | `MIGRATED` | `Docs/design/NPC_DEPTH_TIERS.md`; routine-bearing, visible, named and deeply systemic NPCs are separate budgets |
| Visual Bible / asset reuse direction | `MIGRATED` | `Docs/design/VISUAL_BIBLE.md`, production factory contracts |
| Old Potes visual-ref source index | `DROP` as current authority / `REFERENCE_ONLY` historical | setting is obsolete; useful generic/style observations are already absorbed by current Visual Bible/anti-greybox rules |
| CITY current port-city/B0 direction | `MIGRATED BASELINE / EXECUTION PENDING` | `CITY_PRODUCTION_KNOWLEDGE.md`, `FIRST_KEEPER_BLOCK_B0.md` and world model contain most of the answer; local `WP-CITY-URBAN-00` still must formally close topology + coverage-status matrix before PASS |
| Old inland/Potes CITY geometry/governance | `DROP` | obsolete geography and heavy causal-owner machinery |
| CITY grammar/interiors/location/mobility source corpus | `REFERENCE_ONLY` + `ABSORBED` | current CITY docs are authority; source index preserves deeper detail |
| Quaternius audits/tooling/reuse | `MIGRATED` | `QUATERNIUS_PRODUCTION_KNOWLEDGE.md`, `EXISTING_ASSET_PIPELINE_RESEARCH.md`, source index |
| GC2 Hub audit/conclusions | `MIGRATED` | `GC2_HUB_REUSE_KNOWLEDGE.md`, module acquisition policy, source index |
| GC2 raw Hub CSV catalog/inventory | `REFERENCE_ONLY` raw source | indexed explicitly; inspect before repeating Hub research; freshness revalidated at adoption |
| Dialogue 2 / dialogue authoring research | `MIGRATED` | `DIALOGUE_AUTHORING_KNOWLEDGE.md`, Dialogue factory WP |
| Alias | `FUTURE_ONLY` | `RESEARCH_PENDING`; insufficient canonical evidence for adoption |
| AI Unity authoring benchmark learning | `ABSORBED` | `BOUNDED_OPERATOR` decision + local `unity-operator` skill |
| H2 keeper-world/visual-production intent | `ABSORBED` | current factories + B0 + M0 + keeper/gate DAG preserve the useful claim; old inland/H1 execution mechanics are dropped |
| H2 semantic world-authoring planning inputs | `REFERENCE_ONLY` + `ABSORBED` | useful assembly/game-space ideas already live in CITY/ENV factory contracts; consult archive only for omitted detail |
| H2F toolchain/lifecycle | `DROP` as architecture | Unity/GC2 project exists independently; no H1 compatibility tax |
| H2F selected native-tool lessons | `ABSORBED` where still applicable | current Unity project/tooling state and production WPs own any retained package/tool decision |
| ART/ENV production intent | `MIGRATED` | ASSET/ENV factory WPs and pipeline research |
| CHAR production intent | `MIGRATED` | CHAR factory/batch WPs and existing-pipeline research |
| ANIM production intent | `MIGRATED` | ANIM factory/batch WPs and Quaternius/UAL research |
| UI production intent | `MIGRATED` | UI factory WP |
| PA-01..13 Living World research | `MIGRATED` | `Docs/research/living-world/LIVING_WORLD_KNOWLEDGE.md` |
| PA-14 old integration review | `DROP` as old gate / `FUTURE_ONLY` intent | future juego-def Living World integration proof derived when implementation exists |
| Immersive object interaction scope | `MIGRATED` | `GAMEPLAY_SYSTEMS_KNOWLEDGE.md` |
| GameFlow/condition/outcome/persistent-vs-ambient/schedule/full-abstract lessons | `MIGRATED` | `GAMEPLAY_SYSTEMS_KNOWLEDGE.md` |
| Old Juego knowledge ledger / fixture bank | `REFERENCE_ONLY` + `ABSORBED` | source index; strongest lessons distilled locally |
| Prior-art question bank | `REFERENCE_ONLY` | use as a question/failure-mode source before broad new research, not as product authority |
| GC2↔Arkus runtime-split/H1 ADRs | `DROP` as architecture / `ABSORBED` where useful | current `GC2_FIRST_ARCHITECTURE.md` governs; avoid duplicate authority, but no Arkus owner is assumed |
| H0 HK harness/runtime/CAS/snapshot/replay/MCP | `DROP` by default | no current product need justifies importing it; individual mechanism may return only via concrete WP evidence |
| H1 bridge/materialize/observe/reconcile | `DROP` | direct Unity + GC2 + bounded operator is current production path |
| CTX bootstrap/capsules/envelopes | `DROP` implementation | new repo is small; direct authoritative context is cheaper now |
| CTX principle of minimal starting context/escalation | `ABSORBED` | current lightweight skills read direct dependencies, not project history |
| DW design-world machinery | `DROP` implementation / `ABSORBED` research discipline | current docs/research index provide source-traceable knowledge without separate architecture |
| Dependency/IP policy | `MIGRATED` simplified | `Docs/operations/DEPENDENCY_AND_PROVENANCE_POLICY.md` |
| Worker/Reviewer/Repair role separation | `MIGRATED` simplified | `AGENTS.md`, `.agents/skills/**` |
| exact-SHA/freeze/pre-review discipline | `MIGRATED` simplified | `AGENTS.md` + implementation/review skills |
| Automation V2 / action-driven state machine | `DROP` | add CI only when concrete validation benefits justify it |
| Local WP autopilot + Telegram unattended flow | `FUTURE_ONLY` | potentially valuable once repeated WPs justify automation; do not import polling/quota/buttons/Automation-V2 complexity now |
| old local H1 executor skill | `DROP` | replaced by generic `unity-operator` bounded editor skill |
| DocSync zero-commit/bounded-delta lesson | `MIGRATED` | `.agents/skills/docsync-workpack` |
| old milestone planner process | `MIGRATED` simplified | `.agents/skills/plan-workpack` |
| `.claude` wrappers | `MIGRATED` as thin routing wrappers | no duplicate policy logic |
| Juego2 Unity project/generated bridge assets | `DROP` | juego-def owns its own Unity project/bootstrap |
| Juego2 code/tests/scripts tied to Arkus | `DROP` | no architecture-by-sunk-cost |
| SESSION_HANDOFF / accepted-state navigation caches | `DROP` implementation | live GitHub + current repo are small enough; no derived handoff database needed now |
| `Docs/history` chronology | `REFERENCE_ONLY` | old repo remains historical archive; no need to copy chronology |
| historical PR/evidence archive | `REFERENCE_ONLY` | remains in Juego2; use when provenance/reviewer history matters |
| production purchase history | `REFERENCE_ONLY` | ownership may be rechecked; old price/version/license is not current adoption evidence |

## CITY-URBAN-00 reconciliation

The **knowledge migration** performed today does not equal formal WP acceptance.

`FIRST_KEEPER_BLOCK_B0.md` and `PORT_TOWN_WORLD_MODEL.md` already carry most of the intended `CITY-URBAN-00` answer. The local WP remains `READY / PARALLEL` until its own execution closes the remaining explicit deliverables, especially:

- a five-zone topology/adjacency handoff with primary/secondary/service relationship clarity;
- systematic factory-demand statuses (`COVERED / FACTORY_REQUIRED / PROXY_ALLOWED_FOR_INTEGRATION / DEFERRED_OUTSIDE_B0`);
- a short unresolved-questions/deferred list.

Therefore normal production may start `PROD-ASSET-00` in parallel, but `PROD-ENV-01` still waits for formal `CITY-URBAN-00` PASS as already encoded by the local DAG.

## What normal production should read now

A fresh production Worker should normally remain inside juego-def:

1. `AGENTS.md`;
2. exact WP;
3. direct design/product authorities named by that WP;
4. applicable local production/research docs;
5. live GitHub state.

Opening Juego2 is an **escalation**, not a normal prerequisite.

## Allowed reasons to reopen Juego2 archive

- current distilled document explicitly points to a raw source/fixture needed for a decision;
- a reviewer needs exact historical provenance or a specific failure case;
- an external-tool/adoption question needs details from the raw Hub/Quaternius audit before fresh verification;
- a future Living World implementation needs a PA scenario/failure mode omitted from the distillation;
- a concrete problem appears that might justify recovering one isolated H0/H1 mechanism.

“Because it existed there” is not a sufficient reason.

## Migration completeness rule

After this audit, a newly discovered useful Juego2 item should be treated as an exception:

1. identify the concrete missing product/production value;
2. classify it `MIGRATE / ABSORB / REFERENCE_ONLY / DROP`;
3. migrate only the useful decision/invariant/fixture/mechanism;
4. do not reopen the old architecture around it.

## Next production action

This closure audit does not add a new foundation milestone. Once this PR is independently reviewed/accepted, resume the existing production DAG with:

- `WP-PROD-ASSET-00` — primary production-substrate work;
- `WP-CITY-URBAN-00` — short formal closure in parallel;
- `WP-M0-00` and Dialogue may also remain parallel as already defined.

`PROD-ENV-01` begins only after both ASSET-00 and CITY-URBAN-00 have passed.

# AGENTS.md — juego-def

Status: **CANONICAL OPERATING MODEL**

## Prime directive

`juego-def` is a production-first Unity + Game Creator 2 project. Agents exist to ship the game, not to preserve architecture or process for its own sake.

The default production loop is:

```text
accepted product/workpack brief
 -> Worker plans and implements
 -> Unity/asset operator performs bounded physical editor/tool work when useful
 -> Worker observes, corrects, validates and pre-reviews
 -> exact candidate SHA freezes
 -> fresh independent Reviewer attempts to falsify the claim
 -> PASS -> merge -> bounded DocSync
 -> FAIL -> fresh Repair Worker
```

H0/H1, Arkus canonical state, materialize/reconcile, Automation V2, CTX capsules and the old Juego2 milestone machinery are **not** inherited.

## Sources of truth

In order of authority for current work:

1. effective Unity/project bytes and reproducible evidence;
2. the exact current workpack under `Docs/workpacks/`;
3. current design/product authorities under `Docs/design/`, `Docs/architecture/` and `Docs/production/`;
4. current roadmap/dependency order under `Docs/roadmap/`;
5. research under `Docs/research/` as input, never automatic implementation authority;
6. live GitHub state for branch/PR/SHA/review/merge identity.

Private chat memory is never required to reconstruct an active candidate.

## Roles

### Owner

Owns product direction, major scope changes, purchases/licenses with material cost, final subjective visual acceptance and any decision that changes the game's identity.

### Worker

Owns one explicitly selected workpack from interpretation through implementation, evidence, correction and strict pre-review. The Worker may use Unity, MCP, Blender, scripts, GC2, external lawful tooling and delegated operators.

The Worker does **not** issue the independent PASS for its own candidate.

### Unity / Asset Operator

Executes bounded physical work for the Worker: inspect assets/scenes, act in Unity/Blender/tooling, enter Play Mode or previews, capture evidence, diagnose and correct within the declared task.

The operator may make ordinary implementation choices needed to complete the Worker's brief, but may not silently change product scope, adopt paid dependencies, redefine acceptance criteria or issue independent PASS.

### Reviewer

Fresh independent reasoning context. Reviews the frozen exact SHA. Must derive its own plausible falsifiers from the WP claim before relying on Worker conclusions or fixtures.

Reviewer outputs `PASS`, `FAIL`, or a narrow `PROTOCOL_FIX` when product/evidence identity is sound and only non-material metadata is wrong. Reviewer does not repair a material FAIL in the same role/context.

### Repair Worker

Fresh Worker after a material FAIL. Repairs the **causal blocker class**, not merely the literal example reported by Reviewer; revalidates affected surfaces, freezes a new SHA and hands to a fresh Reviewer.

## Shorthand routing

- `Worker <WP-ID>`: execute exactly that eligible workpack.
- `Reviewer <PR/WP>`: independently review the frozen candidate; do not edit implementation.
- `Repara <PR/WP>` / `Repair <WP-ID>`: fresh Repair Worker for the existing candidate/history.
- `Merge y docsync`: merge the exact reviewed SHA and reconcile only authoritative documentation whose meaning truly changed.

If an explicitly requested WP is blocked, report the concrete blocker rather than silently selecting another WP.

## Workpack discipline

A good `juego-def` workpack is small enough to execute/review independently and concrete enough that a fresh Worker can act without private chat context.

Before implementation, Worker records a short dependency check:

- direct accepted prerequisites;
- guarantees/inputs consumed from them;
- what this WP newly owns;
- what evidence would justify reopening an inherited assumption.

Do not reread or re-prove the entire project history without a concrete reason.

## Evidence and exact candidate identity

For any non-trivial implementation WP:

1. finish repository/evidence bytes;
2. stop overlapping writers;
3. read exact 40-character HEAD as `PRODUCT_SHA`;
4. run the validation materially required by the WP;
5. perform strict Worker pre-review over the complete candidate;
6. if clean, freeze the candidate for independent review;
7. any later Git commit creates a new candidate and invalidates the old frozen identity.

GitHub-side comments/PR wording that do not change repository bytes are non-material unless they make candidate/evidence identity ambiguous.

## Strict Worker pre-review

Before freeze, Worker attempts to disprove its own candidate. At minimum:

- re-read Acceptance, Forbidden scope and Definition of Done;
- inspect the complete baseline-to-candidate diff;
- verify evidence proves the actual claim rather than a convenient happy path;
- check likely failure modes, batch/scale where claimed, and missing/negative paths;
- verify selected external dependency/tool decisions match current provenance/license/product rules;
- for visual/Unity work, inspect the result at the product-relevant scale/view and in Play Mode when the claim depends on runtime behaviour.

A clean pre-review is readiness evidence, **not independent PASS**.

## Independent Reviewer rule

Before accepting Worker evidence as sufficient, Reviewer asks:

> How could every supplied fixture/check be green while the WP claim is still false?

Material dimensions include, when relevant:

- cardinality/batch scale;
- composition across systems;
- time/order and persistence;
- authority/duplicate ownership;
- provenance/dependency assumptions;
- absence/negative claims;
- visual quality from the actual third-person/product view;
- replaceability/repeatability for factory claims.

PASS requires no surviving material falsifier inside the WP boundary.

## Research/reuse rule

Before implementing generic pipeline/tooling from scratch, consume the applicable research index and disposition existing candidates as `USE / ADAPT / REFERENCE_ONLY / REJECT / NOT_MATERIAL / DEFER`.

External tools do not become dependencies merely because they appear in research. Exact version/license/provisioning are rechecked at adoption time.

## Production-authoring rule

Current authoring posture is bounded AI/operator use. Physical production should prefer:

```text
brief -> inspect -> act -> observe -> diagnose -> correct -> evidence
```

The operator is valuable when it reduces low-level manipulation and enables more/better iterations. Human/Owner judgment remains authoritative for subjective final visual/product calls.

## DocSync

Default after PASS/merge is **zero additional commit** unless accepted work changed the effective meaning of an authoritative durable document that future work consumes.

When a DocSync commit is required, make one bounded reconciliation. Do not recreate chronology across multiple summaries and do not rerun product/Unity tests for docs-only reconciliation.

## Product anti-goals

- no architecture preserved by sunk cost;
- no duplicate gameplay authority without demonstrated need;
- no greybox-plus-assets-pasted-on accepted as final environment production;
- no mass content before its lane has a repeatable factory/reuse path;
- no plugin/module purchase merely because the roadmap names it;
- no procedural soap-opera Living World detached from understandable play;
- no independent minigame universes disconnected from town consequences;
- no agent role allowed to silently broaden its own authority.

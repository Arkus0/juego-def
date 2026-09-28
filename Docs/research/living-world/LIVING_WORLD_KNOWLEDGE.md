# Living World knowledge — migrated PA corpus

Status: **MIGRATED PRODUCT/RESEARCH AUTHORITY / IMPLEMENTATION NOT IMPLIED**  
Source: `Arkus0/Juego2` accepted PA programme, PA-01..13.  
Migration date: 2026-09-28.

## Purpose

Preserve the useful semantic conclusions of Juego2's Living World research without importing H0/H1, the old H3/H4 roadmap, runtime schemas, scheduler architecture or old acceptance ceremony.

This document says **what the Living World should mean**. It does not require implementing all of it now. Future gameplay WPs consume only the sections relevant to their current product claim and must prove their own Unity/GC2 runtime behaviour.

## Acceptance/provenance reconciliation

Juego2's PA track README records PA-01..13 as accepted. PA-07..09 were accepted through batch `PA-B1`, PA-10..12 through `PA-B2`, and PA-13 through `PA-B3`. Some individual result files still carry their pre-batch `CANDIDATE / BATCH REVIEW PENDING` header; that historical header does not override the later accepted batch state.

PA-14 was an old integration review gated on the former H2 closure. It is **not migrated as an executable dependency**. juego-def will perform its own integration proof when Living World implementation becomes current.

## Product spine

The town is neither a living museum nor a procedural soap-opera machine. It is a **playable causal system**:

```text
ordinary life
 -> actors choose under their own information/reasons
 -> relationships/knowledge/resources/opportunities matter
 -> player and NPC actions perturb the same world
 -> consequences propagate through legitimate owners
 -> important consequences remain legible/reconstructible
 -> propagation/state/cost remain bounded
 -> sustained coherent causes may genuinely transform the town
```

Normality is an attractor under ordinary noise. It is not protected destiny. The simulation should recover from accidental churn while allowing sustained intentional player/world action to produce lasting constructive or destructive change.

## PA-01 — NPC Daily Life

**Core:** schedule is expected semantic intent, not a waypoint screenplay.

Preserve:

- expected routine and actual state are distinct;
- activity intent is distinct from destination/path/animation;
- compatible place/capacity/resource resolution is fallible;
- interruption releases/suspends transient execution and then re-evaluates current time/context;
- visible travel should remain coherent, but exact hidden path simulation is not required;
- off-screen fidelity may be cheaper while causal meaning survives re-entry;
- routine density does not itself create agency.

A durable town change may invalidate an old opportunity; schedule data must not reset the world to protect the original routine.

## PA-02 — NPC Agency & Autonomous Social Action

**Core:** agency is actor-owned choice under bounded authorized information/opportunity, not visible activity or hidden director assignment.

Preserve:

- actor-originated problem/goal/opportunity above routine;
- scope/bounded source before expensive candidate comparison — no global-population scan disguised as filtering;
- cheap eligibility before scoring/planning;
- commitment/inertia/cooldowns and bounded replanning to avoid thrash/spam;
- important decisions should be explainable from actor-accessible inputs;
- when a receiver genuinely has a choice, the receiver owns that response;
- PersistentActor-grade agency is distinct from ambient density;
- no universal Utility AI/GOAP/LLM architecture is implied;
- LLM language generation may phrase a decision but must not become hidden canonical decision/state authority.

## PA-03 — Social Graph That Changes Behaviour

**Core:** relationships are typed causal inputs to actor-owned decisions, not one friendship meter.

Minimum conceptual vocabulary:

- directed `trust`;
- directed `affinity`;
- directed `fear`;
- structural ties/endpoint roles such as household, employment or authority;
- identified obligations with source/lifecycle.

Direction matters: `A -> B` does not imply `B -> A`. Structural roles do not equal liking/trust/fear. A future display summary may be derived, but a universal `relationshipScore` must not replace the causal dimensions when those meanings matter.

Player↔NPC social state should use compatible semantics rather than a privileged player-only friendship universe.

## PA-04 — Knowledge, Belief, Ignorance & Deception

**Core authority invariant:**

```text
canonical world truth != actor-accessible belief
missing actor knowledge -> UNKNOWN
world truth changes -> no automatic actor learning
```

Preserve distinct layers:

- canonical world truth;
- actor-local epistemic state;
- actor-safe query surface;
- privileged debug/test comparison.

Legitimate acquisition may come from perception, accessed public source, communication, authored grant or bounded explicit inference. Public does not mean ambient omniscience. False/stale beliefs and deception must remain possible without corrupting canonical truth.

## PA-05 — Rumours & Information Flow

**Core:** a rumour/information hop is an explicit social action through a real opportunity/channel, not background synchronization.

Preserve:

```text
sender decides to communicate
 -> valid opportunity/channel
 -> sender -> receiver assertion + actor-visible context
 -> receiver interprets using receiver-accessible state
 -> receiver belief may change
 -> receiver later decides independently whether to retell
```

Crucial privacy boundary:

- engine/debug causal lineage may know root/parent/hops;
- actor-accessible provenance includes only what that actor legitimately learned;
- hidden engine lineage must not make the actor better at corroborating or judging a claim.

No automatic retransmission on belief change; social adjacency is not telepathy.

## PA-06 — Memory & Consequences

**Core:** memory is a bounded actor-accessible causal witness for later decisions, not a full life log and not a duplicate truth/belief/relationship store.

Preserve:

- only experiences the actor legitimately accessed are memory candidates;
- selection is causal in time — future fixture usefulness cannot retroactively decide what was remembered;
- salience uses declared dimensions such as stake, goal/role relevance, novelty and declared future consumer class;
- finite per-actor selected-memory surface independent of lifetime and number of distinct salient events;
- deterministic pressure policy: retire, demote, merge or summarize under budget;
- repeated ordinary experiences can compact into bounded summaries;
- an active consequence retains a bounded minimum reason witness somewhere under explicit ownership;
- forgetting memory, revising belief, repairing relationship and ending obligation are different operations;
- later action families may consume eligible memory as one input, but memory does not choose the action.

Reject unbounded biography/overflow and direct memory writes to current relationship/belief truth.

## PA-07 — Work, Businesses & Material Dependencies

**Core:** model human-facing service opportunity plus a deliberately tiny set of decision-relevant material dependencies, not a hidden economy simulator.

Useful service truth includes:

- opening/operating condition;
- relevant staffing;
- finite capacity when contention matters;
- named dependency/resource where shortage changes play;
- place/equipment/access condition;
- `AVAILABLE / DEGRADED / UNAVAILABLE`-type semantics with structured reason.

Work does not own schedules or actor decisions. It supplies material/service truth those owners encounter. Economic variables should exist only when they change visible opportunities, choices or consequences.

## PA-08 — Leisure, Social Activities & Minigames

**Core:** thin shared integration seam, not a universal minigame engine.

> The minigame owns play. The Living World owns context and aftermath.

An activity opportunity may expose place, availability, participant requirements, finite capacity, time cost, stake/material requirement and initiation mode. Actor choice remains actor-owned. Session-local scoring/rules stay local. Only a small structured outcome crosses back into normal town owners.

A Living World activity should be able to exist as ordinary town life where appropriate without player activation. A polished isolated score screen is not Living World integration.

## PA-09 — Player Causal Agency & Embodied Actions

**Core:** the player is a first-class initiator of semantic world actions, not a privileged writer of downstream state.

Origin-neutral rule:

> Equivalent accepted player/NPC world actions under equivalent capability/authority/context enter compatible causal owners.

Useful intervention families include bounded material/opportunity acts (give, take, deliver, occupy/release, enable/disable, help/repair), social/embodied acts (invite/refuse/accompany/follow, greet/show/offer, join/leave, assist/intervene) and activity participation.

Dialogue is one action family, not the universal adapter. We want a **few strong embodied verbs**, not “everything is interactive”.

## PA-10 — Autonomous Events & Causal Chains

**Core:** causal-chain coordination begins after a legitimate cause exists. It may group/limit propagation; it may not secretly write the story.

```text
legitimate cause
 -> bounded consequence opportunity
 -> relevant actor/domain owner encounters it
 -> actor chooses / owner applies legitimate delta
 -> next bounded consequence or stable state
 -> terminate/de-escalate/change equilibrium
```

Chain layer may own lineage/grouping, bounded relevance envelope, propagation/cooldown pressure, termination and explicit collision coordination. Actors still own meaningful actions/targets/responses; domain owners own their truth.

Reject the storyteller form where a manager first decides who argues/intervenes/apologises and assigns those decisions to actors afterward.

## PA-11 — Investigation, Legibility & Traces

**Core:** separate causal truth, evidence production, actor/player knowledge and player conclusion.

Important reconstructible events should have a viable **evidence ecology**, not one magic clue. Potential channels:

- first-hand witness/testimony;
- physical/material trace;
- documentary/institutional record where naturally produced;
- routine/absence/timing anomaly;
- social/information trace with legitimate provenance;
- persistent world consequence.

Two clues count as independent only when their causal/provenance bases are independently useful. Three people repeating the same rumour are not three independent sources.

Player evidence must never silently expose engine/debug causal lineage. A notebook may retain observations, but should not automatically solve the simulation.

## PA-12 — Governance as Intervention

**Core:** governance publishes explicit institutional condition changes into normal systems; it does not command private actor state.

High-leverage semantic families include:

- access/permission;
- time/service windows;
- capacity/allocation;
- service/resource support;
- public obligations/commitments;
- institutional sponsorship;
- bounded enforcement posture where later scope warrants it.

Macro↔micro target:

```text
municipal decision
 -> rules/resources/opportunities change
 -> actors independently respond
 -> player encounters consequences in third person
 -> player may locally help/resist/mediate/exploit
 -> later town state reflects both macro and micro causes
```

Do not implement ideology/mind-control mode flags that directly set citizen belief, loyalty or action.

## PA-13 — Simulation Control, Failure Modes & Budgets

**Core:** control is an execution envelope around semantic owners, not a hidden director and not a second copy of state.

It may regulate **how much, how often, in what order and at what fidelity** accepted capabilities execute. It may not redefine what their state means, manufacture decisions, erase legitimate causes or restore an approved equilibrium by fiat.

Tooling/runtime should be able to distinguish outcomes such as:

- executed;
- not eligible;
- deferred;
- cap hit;
- degraded fidelity;
- unrepresentable/rejected;
- terminated.

Preserve:

- bounded local discovery rather than global scans;
- explicit commitment/reconsideration envelopes;
- finite memory/trace/chain/activity pressure;
- FULL↔ABSTRACT continuity of identity and material causal state;
- reproducible/inspectable budget decisions;
- graceful overload by deferral/fidelity change rather than semantic corruption;
- ordinary/clumsy play should not naturally spiral into anarchy;
- sustained coherent causes must still be able to overcome stabilizers and materially transform the town.

Numeric CPU/save/NPC budgets remain empirical and must be established against representative content later.

## Cross-cutting amendments preserved

### Playable causal city

Living World exists to create playable opportunities, readable differences and third-person consequences. It must not become autonomous simulation watched from outside.

### Intentional transformation

Recovery/normality mechanisms regulate noise and propagation, not morality. Reversing a rule or repairing a condition is not a time machine: legitimate memories, debts, relationships, moved resources and prior consequences may remain.

### Emergent governance

The player should not select a labelled ideology/town archetype from a strategy screen. The town becomes different through explicit rules, allocations, opportunities and actions encountered in normal play.

## PersistentActor vs AmbientPopulation

Preserve this scale boundary across future implementation:

- **PersistentActor:** stable identity and continuity because later gameplay needs this person to remain individually meaningful; may acquire schedules, beliefs, relationships, memory, obligations and agency as demanded.
- **AmbientPopulation:** density/presence/cheap interaction; no individual persistent social biography by default.
- promotion to persistent is explicit when story/systemic continuity earns the cost.

Do not simulate every decorative citizen as a full social agent merely because they are visible.

## FULL vs ABSTRACT

Presentation fidelity may change off-screen. Meaningful causal category may not silently change.

If an actor has a committed goal, material possession, relationship/knowledge change or meaningful outcome, moving between FULL and ABSTRACT must not duplicate, erase or rewrite it. A significant abstract action should produce the same **kind of semantic outcome** as its visible equivalent even if animation/path microdetail is omitted.

## Deferred implementation decisions

This migration deliberately does **not** choose:

- Utility AI vs GOAP vs behavior trees vs rule systems;
- database/index/ECS/object representation;
- final save model;
- GC2 Behavior vs custom scheduling/agency split;
- numeric simulation budgets;
- exact off-screen tick cadence;
- dialogue/inventory/quest module ownership where product tests have not yet decided it.

When these become current, choose the cheapest implementation that preserves the semantic invariants actually needed by the playable slice.

## Source map

Canonical source results in `Arkus0/Juego2`:

- `Docs/research/living-world/results/PA-01.md` — Daily Life
- `.../PA-02.md` — Agency
- `.../PA-03.md` — Social Graph
- `.../PA-04.md` — Knowledge/Belief
- `.../PA-05.md` — Rumours/Information Flow
- `.../PA-06.md` — Memory/Consequences
- `.../PA-07.md` — Work/Businesses/Material Dependencies
- `.../PA-08.md` — Leisure/Social Activities/Minigames
- `.../PA-09.md` — Player Causal Agency
- `.../PA-10.md` — Autonomous Events/Causal Chains
- `.../PA-11.md` — Investigation/Legibility/Traces
- `.../PA-12.md` — Governance
- `.../PA-13.md` — Simulation Control/Budgets

Also preserve as research provenance:

- `LIVING_WORLD_CROSSCUTTING_AMENDMENT_01_PLAYABLE_CAUSAL_CITY.md`
- `LIVING_WORLD_CROSSCUTTING_AMENDMENT_02_INTENTIONAL_TRANSFORMATION.md`
- `PA-09_AMENDMENT_01_EMBODIED_ACTIONS.md`
- `PA-12_AMENDMENT_01_EMERGENT_GOVERNANCE.md`

Juego2 remains the historical evidence archive. This distilled document governs juego-def product semantics unless amended here.

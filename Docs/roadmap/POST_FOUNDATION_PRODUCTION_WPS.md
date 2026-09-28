# Post-foundation production workpacks — migrated draft

Status: **DRAFT / READY TO START WITH PROVISIONAL `BOUNDED_OPERATOR`** (see `PRODUCTION_AUTHORING_DECISION.md`)  
Purpose: preserve the useful post-H2F production decomposition from Juego2 without importing H1/H2F dependencies.

These are **product-production lanes**, not accepted executable contracts yet. Their final execution form depends on `Docs/architecture/PRODUCTION_AUTHORING_DECISION.md`.

## Principle

Before deep gameplay breadth, juego-def should prove that it can repeatedly produce:

- good streets/interiors;
- ordinary inhabitants;
- useful animation coverage;
- readable dialogue/UI presentation;
- an actual keeper urban block;

without returning to greybox-plus-assets improvisation or bespoke per-scene plumbing.

The difference from Juego2 is important: these factories must use the **simplest effective authoring path**. If the AI Unity operator proves strong, the factory is primarily a recipe/brief/validation system, not a new code framework.

## `PROD-ENV-01` — Environment recipe + repeated-build proof

Goal: produce a keeper-quality bounded street/interior composition and then a materially different second composition using the same recipe.

Inputs:

- Visual Bible;
- port-town world model;
- Quaternius production knowledge;
- real lawful source corpus;
- production-authoring decision.

Must prove:

- semantic component roles and dimensions where useful;
- `DIRECT / ADAPTABLE / DONOR / CREATE_DERIVED` reuse;
- credible joins, thresholds, ground contact and player scale;
- lighting/presentation fit;
- first-build vs repeated-build reduction in setup/manipulation;
- no primitive host geometry masquerading as keeper architecture.

If AI authoring wins, require the operator to inspect, build, observe and correct in Unity rather than merely emit scripts.

## `PROD-CHAR-01` — Character/wardrobe recipe

Goal: define a repeatable ordinary-population recipe from shared base/rig and modular/adapted wardrobe.

Must prove:

- lawful source/provenance;
- body/rig/wardrobe compatibility;
- civilian visual coherence;
- clipping/weight/scale checks;
- palette/accessory variation;
- reusable prefab/variant output;
- no requirement for bespoke tooling per NPC.

## `PROD-CHAR-02` — Representative population batch

Goal: produce a representative group of ordinary townspeople from `PROD-CHAR-01`, not unrelated one-offs.

Success is repeatable variation and useful town coverage, not a fixed raw character count. Important narrative characters may receive bespoke treatment later.

## `PROD-ANIM-01` — Animation intake/coverage truth

Goal: inventory and admit useful locomotion, conversation/acting, ambient/social, work/activity, object and reaction motions.

Record retarget/import conventions, root/in-place/loop intent, source/provenance and known gaps. Raw clip count is not a quality metric.

## `PROD-ANIM-02` — Runtime animation vocabulary

Goal: prove reusable GC2/Unity presentation mapping on real characters.

Must include real runtime validation and at least one bad import/retarget case that is repaired or rejected rather than silently accepted.

## `PROD-DIALOGUE-01` — Dialogue runtime/presentation decision

Goal: decide the actual dialogue authoring/presentation surface.

Default candidates:

- GC2 Dialogue if owned/justified;
- Core/local presentation if sufficient;
- audited Hub text-to-dialogue ideas as authoring accelerators where lawful/currently compatible.

Do not adopt a commercial module merely because the roadmap names it. The chosen path must materially improve the actual investigation/dialogue workflow.

## `PROD-UI-01` — No-voice dialogue/UI language

Goal: establish coherent typography, speaker treatment, choices, prompts, subtitles/dialogue pacing, acting/gesture timing and camera coexistence. Normal production assumption: **no spoken voice acting required**.

## `CITY-URBAN-01` — First real keeper block

Goal: realize the first dense port-town keeper block using the accepted environment recipe, not a historical/inland pilot.

Recommended first-block context: Mercado–Muelle seam or another similarly useful commercial-to-working-port transition. Exact geometry remains a fresh design decision in juego-def; do not copy Juego2's old node/edge contracts automatically.

## `PROD-LOOK-GATE` — Visual/content production lock

This is a lightweight product gate, not an infrastructure mega-gate.

PASS when:

- the actual port-town block looks like the intended game at third-person scale;
- environment roles are keeper-quality rather than dressed proxies;
- ordinary character variants are repeatable;
- useful animation coverage exists and can be extended;
- dialogue/UI presentation has a reusable pattern;
- a fresh brief can produce another bounded street + small population without inventing a new framework;
- remaining work is breadth/polish/content, not unresolved production architecture.

## After the production lock

Then accelerate gameplay/content:

- investigation conversations;
- persistent clues/objects only where needed;
- routines and living block;
- minigames/jobs;
- chase;
- melee/confrontation;
- 20–30 minute slice;
- additional neighbourhoods.

The production lanes should overlap where practical. Do not recreate Juego2's long serial gate chain.

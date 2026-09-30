# WP-PROD-ENV-DIRECTOR-00 — Human-Directed Environment Editor

Status: **READY NOW / URGENT PRODUCTION ENABLER**  
Class: HUMAN-IN-THE-LOOP AUTHORING TOOL / ENVIRONMENT  
Depends on: `BOOTSTRAP-UNITY-GC2` PASS + `WP-CITY-URBAN-00` PASS + an ENV district trace/build path on the execution branch  
Consumes when available: active `WP-PROD-ENV-01` trace/spec/build/polish/rebuild tooling  
Blocks: `WP-PROD-ENV-02`  
Feeds immediately: current ENV-01 human logic pass and all later keeper environment composition

## Claim

juego-def has a deliberately simple but powerful **Owner Director** inside Unity that lets the owner make the high-value human spatial and composition decisions directly, while the ENV factory and AI/operator perform the repetitive generation, adaptation, rebuilding and validation work.

For normal environment direction, the owner does **not** need to edit JSON, write code, use the Unity Inspector, understand internal object paths or ask an agent to translate every spatial intention into coordinates.

The production split becomes:

```text
OWNER DIRECTS
layout / spatial relationships / important placement / keep-change judgment
        |
        v
ENV DIRECTOR
direct manipulation + explicit semantic commands + safe upstream writes
        |
        v
ENV FACTORY / AI OPERATOR
generate / adapt / vary / expand / dress / rebuild / validate
        |
        v
OWNER REVIEWS IN THIRD PERSON
        |
        +--> accept
        +--> direct another change
```

This WP does not attempt to make the AI a better autonomous level designer. It changes the authoring interface so the human owns the decisions where current agents are weakest.

## Why this exists

ENV-01 has demonstrated a useful but important failure mode: a district can have structured planning data, deterministic generation, extensive semantic rules, route probes, validators, screenshots and repeated AI/operator correction while still containing choices that a human immediately reads as spatially or compositionally wrong.

The response is **not** another universal generator, a larger validation framework, or a different LLM.

The response is to preserve the existing factory and give the owner a very low-friction way to directly author the small number of decisions that dominate how a place reads.

## Authority split

Every editable environment decision belongs to one of three authority classes.

### 1. `HUMAN_DIRECTED`

The owner is authoritative for:

- macro street shape and important bends;
- plaza/space proportions;
- important width/elevation changes;
- bridges, stairs and major route transitions;
- landmark position and orientation;
- important building footprints/facings;
- framed views and visual closures;
- hero thresholds and key entrances;
- obvious public/service/private spatial truth;
- keep / move / remove / expand judgment on visible content.

AI may propose alternatives but may not silently rewrite these decisions.

### 2. `AI_ASSISTED`

The AI/operator may create or adapt within the owner's selected area/intent:

- ordinary building variants;
- facade variants;
- frontage treatment;
- shop/residential/service variants;
- secondary props and vegetation;
- shallow interiors;
- local dressing;
- material and weathering variants;
- repeated details;
- bounded geometry repair.

### 3. `PROCEDURAL`

Normal deterministic tooling remains authoritative for suitable mechanical work:

- material assignment;
- collision and clearance support;
- ground welding/fill;
- repeated facade assembly;
- weathering recipes;
- validation;
- catalogue/lineage;
- probes and evidence capture;
- other deterministic factory output.

The tool must make these boundaries visible enough that the owner is never surprised by an AI/global rewrite after making a local edit.

## Owner UX contract — non-negotiable

The Director is an **owner-facing production surface**, not an internal debug window.

For the normal workflow the owner must not need to:

- open or edit `*.trace.json`, generated specs or polish JSON manually;
- use the Inspector to type coordinates;
- know GameObject hierarchy paths;
- write C#/Python;
- invoke MCP commands manually;
- understand factory implementation classes;
- use a text diff to know what moved.

The owner should be able to perform the normal loop with:

- click to select;
- drag to move;
- rotate/scale handles when contextually valid;
- a small contextual action bar;
- visible labels/guides;
- `SAVE`, `REVERT`, `REBUILD`, `PLAY HERE`;
- safe AI actions on the current selection.

The editor may expose advanced details behind an explicit advanced foldout, but the default surface must remain simple.

## Interaction model

Use one Unity Editor window plus Scene View overlays. Prefer direct manipulation over forms.

### Mode A — LAYOUT

Editable visually:

- district nodes;
- street segments and `via` points;
- street width;
- plaza vertices;
- river/control points where supported safely;
- landmarks;
- zones/area polygons;
- authored elevation for selected layout points.

Expected interactions:

- click an element to select it;
- drag a handle to move;
- drag width handles to widen/narrow a street;
- drag a plaza/zone vertex;
- add/remove a `via` or polygon vertex through a contextual action;
- constrain movement to X/Z or Y when requested;
- show names and semantic role in the Scene View;
- show approximate street envelope/width, not only a centre line.

### Mode B — BUILDINGS

The owner can work with generated/assembled buildings as spatial objects without learning their implementation.

Minimum interactions:

- select building;
- move;
- rotate;
- duplicate when semantically safe;
- delete/remove from the authored result;
- change high-level role/type from a short list;
- mark `KEEP` / `LOCK`;
- request `VARIANT`, `REPLACE`, `EXPAND`, `MAKE ENTERABLE`.

A building edit must persist through rebuild by writing to the correct upstream source/override. Direct edits to generated scene objects that disappear on rebuild do not satisfy this WP.

### Mode C — DETAIL

For props, vegetation, signs, street furniture and similar local content:

- select / move / rotate / duplicate / remove;
- semantic replace from a filtered palette;
- `GENERATE HERE` or `FILL AREA` for a bounded selected area;
- `POLISH SELECTED` for a bounded object/group only.

The owner must be able to correct an obviously wrong prop in seconds without asking an agent to locate it by world coordinates.

## Contextual command bar

The default command vocabulary should remain small and stable.

### Always visible

- **SAVE**
- **REVERT**
- **REBUILD**
- **PLAY HERE**

### Selection-dependent

- **KEEP / LOCK**
- **DELETE**
- **DUPLICATE**
- **VARIANT**
- **REPLACE**
- **EXPAND**
- **GENERATE HERE**
- **FILL AREA**
- **MAKE ENTERABLE**
- **POLISH SELECTED**
- **VALIDATE SELECTED**

Commands that are not valid for the current selection should be disabled, not silently reinterpreted.

## AI/operator command semantics

This WP does **not** require embedding a paid LLM API into Unity.

The Director may invoke the existing external AI/operator workflow through the simplest robust mechanism available, or emit a structured request for the active operator. The important contract is the selection and authority boundary.

### `VARIANT`

Keep:

- footprint;
- placement;
- access role;
- important clearances;
- locked relationships.

Allow AI/factory variation of appropriate visual/content dimensions.

### `REPLACE`

Replace the selected object with another compatible semantic candidate while preserving the owner's placement intent as far as possible.

Show the proposed replacement before final acceptance when the change is material.

### `EXPAND`

On a building/space, request a bounded extension such as:

- additional floor;
- rear/side volume;
- shallow interior;
- yard/patio;
- small frontage extension.

Never infer a new district route or major programme change from `EXPAND`.

### `GENERATE HERE`

Generate content only inside the explicitly selected point/area/slot.

Examples:

- ordinary residential frontage;
- market props;
- port props;
- vegetation;
- wall/edge continuation;
- facade variant.

### `FILL AREA`

Populate a bounded selected polygon/area using an explicit semantic category and density. Preview before committing when the fill creates many objects.

### `MAKE ENTERABLE`

Create/adapt the minimum coherent threshold + shallow interior path for the selected building while respecting current access truth.

### `POLISH SELECTED`

Inspect and improve only the selected object/group for obvious local visual/semantic defects. It is not permission to restyle or rearrange the surrounding district.

## Canonical data / no duplicate authority

The Director is an interface over existing ENV authority, not a new scene-state architecture.

Default ownership:

- macro authored layout remains in the district `*.trace.json`;
- generated district spec remains generated;
- local building/object corrections continue through the established upstream spec/polish mechanism;
- generated Unity scene remains disposable/rebuildable;
- validation remains in the existing ENV validators/probes.

A small editor-only `*.director.json` is allowed only for information that has no existing authoritative home, such as:

- UI locks/pins;
- bookmarks;
- editor groups;
- owner view presets;
- non-product display preferences.

It may **not** become a second copy of layout/building truth.

Unknown fields in existing JSON must survive a Director load/save round trip.

## Safe editing transaction

Normal editing must behave transactionally.

Required:

1. load authoritative values into an editable in-memory model;
2. direct manipulation updates the preview immediately;
3. no full district rebuild while dragging;
4. changed elements are visually marked;
5. **SAVE** shows a compact human-readable change summary;
6. make an automatic backup before replacing an authoritative source file;
7. save through a deterministic serializer that preserves unsupported/unknown fields;
8. rebuild only affected scope when safe;
9. fall back to full district rebuild when dependency impact cannot be established confidently;
10. Unity Undo/Redo and Director `REVERT` must not corrupt upstream data.

No background agent may alter an owner-edited area between edit and save.

## Rebuild strategy

The user experience target is **local iteration**, not 30-second full rebuilds for every nudge.

Implement in this order:

1. immediate guide/ghost preview while dragging;
2. affected node/street/plaza visual preview;
3. targeted row/segment/building rebuild by reusing existing ENV primitives where safe;
4. full district rebuild fallback.

Do not create a second bespoke materialization system merely to achieve partial rebuild.

## Navigation / camera

The Director must reduce camera friction as well as data friction.

Required:

- frame selected;
- top/plan view;
- third-person approximate view at selection;
- save/recall a small number of bookmarks;
- **PLAY HERE** starts or positions the normal gameplay test near the selected location without requiring manual spawn-coordinate editing.

Useful if cheap:

- before/after camera bookmark;
- street forward/reverse quick views;
- toggle labels/guides to inspect the clean scene.

## Visual affordances

Use clear, low-clutter Scene View representation:

- node handle + label;
- coloured/outlined selection using Unity defaults/theme where practical;
- street centre line + width envelope;
- plaza/zone polygon fill/outline;
- landmark icon/label;
- lock marker;
- changed/unsaved marker;
- invalid/conflict marker.

Do not build a custom rendering framework. Unity Handles/Overlays/EditorWindow/Tool APIs are sufficient unless proved otherwise.

## Delivery roadmap

### D0 — 1-hour-shape spike: move one thing correctly

Prove the architecture with the smallest vertical slice:

```text
open CASCO
 -> select one trace node
 -> drag X/Z
 -> preview connected streets
 -> SAVE
 -> regenerate authoritative district spec
 -> rebuild affected/full district
 -> result survives reopen
 -> REVERT/Undo is safe
```

If this requires a new general authoring architecture, stop and simplify.

### D1 — LAYOUT MVP — **first usable owner release**

Must include:

- Director window + Scene View overlay;
- node selection/move;
- `via` point selection/move;
- street selection + width edit;
- plaza vertex move;
- landmark move/rotate;
- explicit Y edit/vertical handle;
- labels and width/polygon guides;
- dirty state;
- save summary;
- backup + SAVE + REVERT;
- REBUILD;
- PLAY HERE;
- Undo/Redo;
- real CASCO test.

This milestone is the urgent production unlock. Do not wait for AI buttons before giving it to the owner.

### D2 — BUILDINGS + DETAIL direct manipulation

Add:

- building select/move/rotate;
- persistent placement/role override;
- keep/lock;
- duplicate/delete;
- detail/prop selection and persistent move/remove/place;
- filtered semantic replace;
- box/multi-select where it materially speeds real work.

### D3 — AI-assisted selected operations

Add the bounded verbs:

- VARIANT;
- REPLACE;
- EXPAND;
- GENERATE HERE;
- FILL AREA;
- MAKE ENTERABLE;
- POLISH SELECTED.

Every request carries:

- exact selection identity;
- semantic role;
- locked constraints;
- spatial bounds;
- current before-state;
- allowed mutation scope.

Material AI output is previewed/accepted or at minimum clearly summarized before becoming authoritative.

### D4 — fast QA loop

Add/complete:

- validate selected/affected;
- targeted rebuild where reliable;
- route/clearance probe launch for affected area;
- third-person capture shortcuts;
- before/after comparison;
- conflict/highlight when a human edit violates a known hard constraint.

### D5 — usability + production proof

Run an owner trial on real keeper work, not a synthetic sandbox. Fix friction discovered by the trial. Freeze only when the Director is genuinely easier than asking an agent to perform each equivalent edit.

## Required owner trial

Without opening a JSON file, writing code or using the Inspector for coordinates, the owner must be able to complete all materially applicable steps on a real ENV district:

1. select a street node and move it;
2. move a street `via` point;
3. change a street width;
4. reshape a plaza;
5. move or rotate an important building/landmark;
6. move/remove/place a local prop;
7. lock one accepted element;
8. request at least one bounded AI-assisted action from D3;
9. SAVE and inspect a human-readable summary;
10. rebuild;
11. enter/play near the edited area;
12. validate the affected area;
13. Undo or REVERT one change safely;
14. close/reopen Unity and prove accepted edits persist.

The owner should complete the normal path using the Director controls and Scene View, not by being coached through internal implementation fields.

## Power-user features allowed after the basic UX works

Only after D1/D2 are genuinely usable:

- keyboard shortcuts;
- snap increments;
- copy/paste style/role;
- align/distribute;
- frontage-row move;
- constrained street offset;
- area density slider;
- layer visibility;
- semantic palette thumbnails;
- reusable selection sets;
- side-by-side reference image/bookmark;
- batch lock/unlock;
- change history panel.

Do not delay the owner-visible MVP for these.

## Evidence

Retain under `Docs/evidence/WP-PROD-ENV-DIRECTOR-00/` at minimum:

- short implementation/readme;
- screenshots or short capture sequence of D1 and final owner flow;
- round-trip proof for trace/spec data;
- backup/revert/undo proof;
- exact example of targeted vs full rebuild behavior;
- persistence proof after editor restart;
- AI scope proof showing an operation stayed inside its declared selection/bounds;
- owner trial checklist/result;
- known limitations that are real product constraints rather than hidden unfinished basics.

## Validation

At minimum test:

### Data safety

- load/save with no edits is semantically no-op;
- unknown JSON fields survive;
- backup created;
- malformed/unsupported source fails closed;
- Undo/Revert cannot leave half-written authority;
- generated scene can be rebuilt from repository authority.

### Selection safety

- selecting one node does not move neighbours except connected preview consequences;
- AI action scope is explicit;
- locked elements cannot be modified accidentally;
- hidden/unselected content is not silently rewritten by a local command.

### Scale

Test on the real ENV-01 CASCO-scale district rather than a ten-object fixture. Scene View guides must remain usable at the current district scale and dragging must not trigger full regeneration every frame.

### Product loop

- edit;
- save;
- rebuild;
- Play Mode;
- affected validation;
- owner visual judgment.

## PASS

PASS when all of the following are true:

- the owner can direct real environment composition in Unity without normal JSON/code/Inspector-coordinate work;
- D1 direct layout editing is reliable on the actual district;
- D2 lets the owner correct important building/detail placement with rebuild-persistent edits;
- D3 provides bounded AI generation/adaptation from explicit human selection rather than global autonomous composition;
- normal edits have visible preview, safe save/revert and no hidden second authority;
- affected rebuild/validation is fast enough for iterative direction, with full rebuild as safe fallback;
- Play Here closes the loop back to third-person judgment;
- the owner trial succeeds and the owner explicitly prefers the Director for these tasks over prompt-by-prompt spatial manipulation through an agent;
- no material ENV regression is hidden by the tool.

## FAIL

FAIL if any of the following survives:

- normal use still requires Inspector coordinate editing, JSON editing or code;
- the Director is mainly a debug visualizer rather than a manipulation tool;
- owner edits vanish on rebuild;
- generated Unity scene becomes the hidden authority;
- save can discard unknown source fields;
- AI commands may rewrite unselected/global content without an explicit scope change;
- every small move requires a full district rebuild;
- the implementation grows into a general-purpose Unity replacement/editor framework;
- the tool only works on a toy fixture and not the current real district;
- the owner finds it slower or more confusing than the current manual/agent path.

## Forbidden scope

Do not turn this WP into:

- a runtime player-facing level editor;
- a general-purpose replacement for Unity's editor;
- a new H0/H1 canonical-state/materialize architecture;
- a new procedural city generator;
- a full in-Unity LLM chat product;
- a mandatory paid AI service;
- a terrain/world-streaming rewrite;
- a new asset database;
- a new scene serialization authority;
- an excuse to redesign accepted CITY topology automatically.

## Relationship to ENV-01

This WP does **not retroactively invalidate or block acceptance of ENV-01**.

If implemented while ENV-01 is still active, it may be used to finish the human-logic pass and fix genuine layout/composition defects. Those fixes remain governed by ENV-01's contract and exact-SHA review discipline.

If execution requires code that currently exists only on the ENV-01 branch, the Worker must base the implementation on the appropriate current branch/candidate deliberately rather than duplicating the ENV factory on main.

## Handoff to ENV-02

`WP-PROD-ENV-02` is updated conceptually by this WP:

```text
fresh brief
 -> owner blockout / direct composition in ENV Director
 -> lock important human decisions
 -> ENV factory + AI/operator production
 -> validation
 -> owner third-person correction in ENV Director
 -> keeper candidate
```

At least one fresh ENV-02 composition must prove this loop end-to-end.

The desired production model is:

**human-directed space + AI-assisted production + deterministic factory + automated QA**.

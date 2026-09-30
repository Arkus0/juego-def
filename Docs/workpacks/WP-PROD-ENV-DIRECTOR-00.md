# WP-PROD-ENV-DIRECTOR-00 — Human-Directed Environment Editor

Status: **READY NOW / URGENT PRODUCTION ENABLER**  
Class: HUMAN-IN-THE-LOOP AUTHORING TOOL / ENVIRONMENT  
Depends on: `BOOTSTRAP-UNITY-GC2` PASS + `WP-CITY-URBAN-00` PASS + an ENV district trace/build path on the execution branch  
Consumes when available: active `WP-PROD-ENV-01` trace/spec/build/polish/rebuild tooling  
Blocks: `WP-PROD-ENV-02`  
Feeds immediately: current ENV-01 human logic pass and all later keeper environment composition

## Claim

juego-def has an owner-facing **ENV Director** inside Unity with the interaction simplicity of a building game and the production power of the existing ENV factory.

The owner can **build, reshape and expand the world visually** by selecting, dragging and placing catalogued pieces/structures, while AI/operator + factory manufacture or adapt the content requested by the owner.

For normal environment work, the owner does **not** need to edit JSON, write code, use Inspector coordinates, know prefab paths/GUIDs, navigate generated hierarchies or translate spatial intent into prompts.

The target production split is:

```text
OWNER BUILDS / DIRECTS
draw layout -> place pieces -> move/rotate/duplicate -> lock good results -> expand map
        |
        v
ENV DIRECTOR
visual catalogue + thumbnails + drag/drop + placement ghost + snap + safe persistence
        |
        +-------------------------+
        |                         |
        v                         v
ENV FACTORY                  AI / OPERATOR
repeatable assembly          make/adapt requested assets or structures
validation / lineage         within explicit human selection/bounds
        |                         |
        +------------+------------+
                     v
              OWNER PLACES / REVIEWS
                     |
                     v
              PLAY HERE + QA
```

The Director is therefore **not merely a visual editor for `trace.json`**. D0/D1 establish safe direct manipulation of canonical layout; subsequent milestones turn that foundation into a simple world-building surface for existing and AI-created environment content.

The AI is a production multiplier and asset/structure maker. It is not autonomous spatial authority.

## Why this exists

ENV-01 has demonstrated that structured planning, deterministic generation, semantic rules, route probes, validators, screenshots and repeated AI/operator correction can all be green while a human still sees spatial or composition choices that make little sense.

The answer is not another universal generator and not asking a stronger model to design the whole district.

The answer is to give the owner a low-friction visual construction surface:

- direct manipulation for layout and important relationships;
- a browsable **visual catalogue** for reusable pieces/structures;
- game-like placement and editing instead of prefab/path archaeology;
- map expansion controlled by the owner;
- AI generation/adaptation **on demand**, feeding new reusable content back into the catalogue;
- deterministic rebuild/validation underneath.

The Director should feel closer to a builder/editor from a game than to an internal Unity engineering tool.

### Compatibility guarantee for work already in progress

**D0 and D1 remain valid exactly as the foundation already defined.**

Any Worker already implementing D0/D1 should continue. This revision must not force a restart merely because later milestones became more ambitious.

Reopen D0/D1 only if implementation evidence shows they violate their existing safety/authority requirements.

## Implementation prior art — binding reuse posture

D2-D5 must begin from proven Unity editor patterns rather than re-inventing basic Scene View tooling.

The following prior art was inspected before this revision:

- **PrefabPalette** — visual prefab palette, stable thumbnail cache, surface interaction, single/line placement modes, Scene View overlays. Repository: `FrayedFunction/PrefabPalette`.
- **Prefab Painter** — minimal `SceneView.duringSceneGui -> GUIPointToWorldRay -> Physics.Raycast -> PrefabUtility.InstantiatePrefab -> Undo` placement/brush loop. Repository: `danielnagydeveloper/Prefab-Painter-Unity-Editor-Tool`.
- **MAST** — placement ghost, cell/footprint occupancy, lazy invalidation after hierarchy/Undo/object changes, isolated `PreviewRenderUtility` thumbnails, modular scene tools and assembly creation. Repository: `fertilesoilproductions/MAST`.
- **Prefabshop** — direct picking under cursor, Magic Wand-style related selection, line tool and polygon/lasso area interaction. Repository: `Raptorij/Prefabshop`.
- Commercial fence/wall builders and prefab/world brushes are **UX prior art only** for endpoint stretching, modular continuation and builder-style interaction.

### Licensing guardrail

The Worker must distinguish **pattern reuse** from **code reuse**:

- MAST and Prefab Painter are MIT at the inspected revisions; code reuse is allowed only with their license/copyright obligations preserved.
- PrefabPalette uses a non-resale license that forbids selling/distributing the tool or modified versions for a fee; **do not derive a commercial Director implementation from its code**. Use it as architecture/UX prior art only unless legal posture changes.
- No license was found in the inspected Prefabshop repository; treat its code as **reference-only** unless a compatible license is verified before reuse.
- Closed/commercial Asset Store tools are UX/behavior references only unless juego-def has a lawful local copy whose license explicitly permits the intended reuse.

If Director later becomes a sellable asset, it must remain possible to separate all third-party obligations cleanly.

### Optional geometry-editor integration — UModeler X first candidate

The owner already has **UModeler X** available in Unity. Director should exploit that capability when useful, but **must not depend on it**.

Current official product posture verified 2026-09-30:

- UModeler X is an **Editor-only** Unity tool;
- its current Unity Asset Store listing is an **Extension Asset** under the Standard Unity Asset Store EULA;
- the current publisher FAQ/listing allows commercial project use and states that generated/created assets may be used commercially;
- Director must therefore integrate with UModeler X as a separately installed optional tool, not redistribute its package/code as part of a future Director asset.

Binding architecture:

```text
ENV Director Core
├── semantic selection
├── placement / chains / map expansion
├── persistence / rebuild
├── AI context / preview / acceptance
└── GeometryEditAdapter interface
      ├── UModelerXAdapter   [optional, only when detected]
      ├── ProBuilderAdapter  [optional/future]
      └── NoGeometryEditor   [valid standalone state]
```

Requirements:

- Director core must compile and remain usable when UModeler X is not installed.
- Do not create an assembly-definition hard dependency on UModeler X unless it is isolated behind a separately compiled optional adapter.
- Prefer documented/public integration surfaces. Reflection or compile guards are acceptable only when bounded, version-checked and fail-closed.
- If the integration cannot be maintained safely against a UModeler X version, Director falls back to standalone behavior rather than breaking core authoring.
- A commercial Director package must not bundle or redistribute UModeler X binaries/source/package content unless separate redistribution permission exists.
- Geometry edited through UModeler X must be saved as juego-def-owned derived output with normal lineage; do not destructively edit vendor/source packages.
- UModeler X is not canonical scene/world authority. Director/ENV remains responsible for semantic identity, placement, locks, persistence, rebuild and catalogue admission.

Owner-facing behavior when the adapter is available may expose:

- `EDIT GEOMETRY`;
- `EDIT GEOMETRY WITH UMODELER X`;
- geometry refinement as one execution route for `AI MODIFY SELECTED` or `EXPAND`.

When the adapter is unavailable, those geometry-specific actions are hidden/disabled gracefully; all normal Director builder operations remain available.

This integration deliberately prevents Director from growing into a full DCC/modeler. Director owns **what semantic object is being edited and how the result re-enters ENV**; UModeler X may own the bounded mesh-editing session.


### Required implementation shape

Do **not** implement D2-D5 as one giant `EnvDirectorWindow.cs`.

Prefer a small owner-facing EditorWindow/Overlay plus native Unity tool surfaces and separable services:

```text
DirectorContext
├── SemanticSelectionResolver
├── PlacementSurfaceResolver
├── PreviewSession
├── AuthoringCommitService
├── CatalogService
├── ThumbnailService
├── Constraint/OccupancyService
└── SelectionContextBuilder

Editor tools / modes
├── LayoutTool
├── SelectMoveTool
├── PlaceTool
├── ChainTool
├── AreaTool
├── SmartBrushTool
└── AiModifyTool
```

Names may differ, but responsibilities must stay separable enough that adding a tool does not require growing a single Scene View switch or duplicating input/preview/commit code.

### Native interaction patterns to reuse

For supported scene content:

1. **Pick**
   - start with Unity Scene View picking/raycast APIs;
   - resolve picked child renderer/collider upward to the nearest meaningful authored semantic identity;
   - selecting a barrel mesh child should select the logical barrel, not an implementation fragment.

2. **Surface resolution**
   - resolve mouse position through scene raycast/surface hit first;
   - support a safe ground-plane/fallback where appropriate;
   - ground/surface drag is the default for ordinary props.

3. **Preview**
   - dragging/placing/stretching updates a non-authoritative ghost/guide immediately;
   - preview objects must be clearly temporary and removable without dirty durable state;
   - cancel leaves canonical authority unchanged.

4. **Undo**
   - use Unity Undo grouping for Editor-facing operations where possible;
   - the upstream authoring commit must remain reversible/transactional as already required by this WP.

5. **Thumbnails**
   - prefer isolated preview rendering similar to MAST's `PreviewRenderUtility` approach for stable catalogue thumbnails;
   - cache results and invalidate when source content materially changes;
   - do not instantiate thumbnail subjects into the user's production scene.

6. **Tool strategy**
   - placement, chain, area and AI tools share common selection/preview/commit services;
   - avoid duplicated mouse/raycast logic per tool.

7. **Constraint cache**
   - borrow MAST's idea of lazily invalidating occupancy/constraint data after hierarchy changes, Undo/Redo and object transform changes;
   - do **not** copy MAST's rigid grid as Director's product model;
   - Director constraints should operate on semantic footprints, clearances, locks and route/access rules.

### Semantic object contract

Every directly editable generated/placed object needs a resolvable semantic identity:

```text
visible renderer/collider
 -> generated GameObject
 -> semantic authored identity
 -> authoritative trace/spec/polish/catalogue source
```

The Director operates on that semantic object. Generated child-object structure is an implementation detail.

### Semantic chain contract

Stretchable railings/walls/fences/edges are one authored **semantic chain**, not N user-facing segments.

Minimum chain data should be equivalent to:

```text
chain id
start / end or ordered control points
module family
spacing / admissible module lengths
end-cap / terminal treatment
ground/terrain conformance rule
locks
authoritative source
```

Dragging an endpoint previews a new materialization. The factory chooses repeated modules, compatible short/end pieces and bounded adjustment; the owner never manually maintains hidden segment counts.

### Area/lasso contract

A bounded polygon/lasso is a reusable interaction primitive for:

- `FILL AREA`;
- multi-select;
- map-expansion bounds;
- `AI MODIFY SELECTED` authority;
- validation scope.

The area itself defines edit authority. A screenshot of surrounding content does not.

### AI output admission

When AI creates a useful multi-object result, prefer converting it into a reusable admitted assembly/prefab-like catalogue unit rather than leaving a one-off scene mutation:

```text
AI proposal
 -> preview
 -> ACCEPT
 -> validate/intake/lineage
 -> reusable assembly/catalogue identity
 -> isolated thumbnail
 -> AI Created
 -> owner can place it again
```

This mirrors the useful assembly workflow seen in MAST while preserving juego-def's own ENV authority and lineage.


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

The Director is an **owner-facing world-building surface**, not an internal debug window.

A person who can use a simple building/city game should be able to learn the normal workflow without understanding Unity internals.

For normal authoring the owner must not need to:

- open/edit `*.trace.json`, generated specs or polish JSON manually;
- type transform coordinates in the Inspector;
- know GameObject hierarchy paths;
- know prefab filenames, GUIDs or package folders;
- write C#/Python;
- invoke MCP commands manually;
- browse the Project window to find routine placeable content;
- understand factory implementation classes;
- use a text diff to know what changed.

The default interaction vocabulary is visual and small:

- **click** to select;
- **drag** to move/place;
- obvious rotate/width/height handles when relevant;
- thumbnails to choose placeable content;
- placement ghost before commit;
- green/valid vs conflict/invalid feedback;
- snap/alignment assistance;
- `SAVE`, `REVERT`, `REBUILD`, `PLAY HERE`;
- contextual actions such as `LOCK`, `VARIANT`, `REPLACE`, `EXPAND`, `CREATE WITH AI`.

Advanced implementation detail may exist behind an explicit advanced/debug surface but must not leak into the normal workflow.

## Interaction model

Use one Unity Editor window plus Scene View overlays/tools. Prefer direct manipulation, thumbnails and contextual actions over forms.

### Mode A — LAYOUT

This remains the D0/D1 foundation.

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
- add/remove a `via` or polygon vertex contextually;
- constrain movement to X/Z or Y when requested;
- show names and semantic role;
- show approximate street envelopes, not only centre lines.

### Mode B — BUILD / CATALOGUE

The owner browses existing ENV content visually instead of by internal prefab/path name.

The catalogue must provide, when relevant:

- thumbnail;
- human-readable display name;
- semantic category;
- useful tags/role;
- compatibility/placement hints;
- favourites;
- recent items;
- **AI Created** collection for newly manufactured content.

Minimum top-level categories should emerge from the real library rather than hardcoded asset paths, for example:

- Buildings / Houses;
- Shops / Frontages;
- Walls / Edges;
- Streets / Ground / Stairs;
- Vegetation;
- Street furniture / Props;
- Port / Market;
- Interiors / Thresholds;
- Landmarks / Specials.

The catalogue must reuse existing ENV/asset catalogues and lineage where possible; this WP does not authorize a second asset database.

### Placement contract

Placing an ordinary catalogue item should be:

```text
choose thumbnail
 -> drag/click into Scene View
 -> placement ghost follows cursor
 -> snap/alignment assistance
 -> valid/conflict feedback
 -> click to commit
 -> persistent upstream representation
```

Expected assistance:

- ground snap;
- reasonable orientation to street/edge when semantically applicable;
- optional grid/angle snap;
- collision/clearance preview where cheap;
- no silent movement of locked neighbours;
- no placement that exists only in the generated scene and disappears on rebuild.

### Mode C — SELECT / MODIFY

Selected placed structures/content expose simple contextual operations:

- move;
- rotate;
- duplicate;
- delete/remove;
- lock/keep;
- semantic role/type where appropriate;
- replace from compatible catalogue items;
- `VARIANT`;
- `EXPAND`;
- `MAKE ENTERABLE`;
- `POLISH SELECTED`.

A building or placed-structure edit must survive rebuild through the correct upstream trace/spec/polish/authoring mechanism.

### Mode D — EXPAND MAP

The owner can extend the current authored world rather than only polish an existing district.

Minimum expansion operations:

- extend an existing street;
- add a new street segment / bend / connection;
- add or reshape a plaza/space;
- place new buildings/structures along the expansion;
- continue a wall/edge;
- add a bounded new area/zone where the existing data model supports it;
- connect the expansion back to existing routes.

The Director must make expansion **human-authored**. It may assist with geometry and populate ordinary content, but it must not autonomously decide the direction/topology/programme of district growth.

### Mode E — DETAIL

For props, vegetation, signs, furniture and other local content:

- visual palette;
- place;
- move/rotate;
- duplicate/remove;
- semantic replace;
- bounded `FILL AREA`;
- bounded `POLISH SELECTED`.

A wrong local prop should be correctable in seconds.

### Direct pick contract — visible object means editable object

For ordinary visible environment content, the owner should not have to find the source entry first.

Canonical example:

```text
see a badly placed barrel
 -> click the barrel in Scene View
 -> Director resolves its authored identity/source
 -> drag it directly on the ground plane
 -> optional rotate/delete/duplicate
 -> SAVE
 -> rebuild
 -> barrel remains where the owner put it
```

This direct-pick path is mandatory for ordinary props and other supported placed content. Selection must prefer the meaningful authored object over incidental child renderers/colliders whenever that can be resolved safely.

The default drag should feel game-like:

- click visible object;
- drag along ground by default;
- obvious modifier/handle for vertical move;
- ground/surface snap;
- live ghost/preview;
- cancel without durable change.

Needing to search the hierarchy, select a hidden parent, enter coordinates, or identify a polish entry manually is a D2 failure.

### Stretchable linear structures — endpoint editing

Common modular chains must support **construction-game continuation** when their grammar allows it.

Target families include:

- railings / parapets;
- walls / retaining walls;
- fences / hedges;
- kerbs / simple edge strips;
- other repeated linear ENV structures admitted as stretchable.

Canonical example:

```text
see a railing that ends too early
 -> click the railing
 -> endpoint handles appear
 -> drag the end farther
 -> preview adds/removes/repeats compatible modules
 -> release to commit
 -> SAVE / rebuild
 -> continuous railing persists
```

The owner edits the **semantic chain**, not individual hidden 2 m segments. The Director/factory chooses the repeated module count, end treatment and final bounded adjustment underneath.

Where exact stretching would distort a rigid donor piece, the tool should repeat/trim/choose compatible modules rather than non-uniformly deform architecture unless that family explicitly supports deformation.

This endpoint interaction is a core builder capability, not deferred polish.

## Contextual command bar

Keep the default command vocabulary small and stable.

### Always visible

- **SAVE**
- **REVERT**
- **REBUILD**
- **PLAY HERE**

### Selection/context dependent

- **KEEP / LOCK**
- **DELETE**
- **DUPLICATE**
- **VARIANT**
- **REPLACE**
- **EXPAND**
- **EDIT GEOMETRY** *(only when a compatible optional geometry adapter is available)*
- **AI MODIFY SELECTED**
- **CREATE WITH AI**
- **GENERATE HERE**
- **FILL AREA**
- **MAKE ENTERABLE**
- **POLISH SELECTED**
- **VALIDATE SELECTED**

Commands that do not apply to the current selection are disabled rather than silently reinterpreted.

Routine placement from the catalogue should not require opening a modal form.

## AI/operator command semantics

This WP does **not** require embedding a paid LLM API into Unity.

The Director may invoke Codex/the existing external AI operator through the simplest robust integration, or emit a structured request consumed by that operator. What is binding is the **human selection, spatial bounds, contextual evidence and mutation authority**.

The intended UX is interactive: ordinary manipulation remains immediate; AI work runs as a separate request and must not freeze normal Scene View authoring while the proposal is being produced.

### `AI MODIFY SELECTED` — primary natural-language interaction

The owner selects one object, a semantic chain, or a bounded area in Scene View and writes a short natural-language request, for example:

- "continua esta barandilla hasta el muro y termina con un pilar";
- "convierte esta casa en una pension, manteniendo la planta baja";
- "cierra este hueco con una casa estrecha de tienda abajo y vivienda arriba";
- "haz que este rincon lea como entrada secundaria usada por vecinos".

The Director automatically builds a **selection context packet** so the owner does not have to explain coordinates, object paths or local scene structure.

At minimum the packet must include, where materially available:

- exact selected authored identity/identities;
- semantic role/type;
- current transform, footprint/bounds and relevant dimensions;
- authoritative upstream source/override controlling the selection;
- nearby objects/structures inside a bounded relevance radius;
- street/space/zone relationship;
- access/threshold information;
- ground/elevation/slope context;
- relevant collision/clearance facts;
- locked/immutable neighbours and relationships;
- applicable ENV grammar/catalogue candidates;
- explicit allowed mutation scope;
- the owner's natural-language request;
- visual context from a small standardized capture set when useful: gameplay/eye or oblique + top/plan, not an uncontrolled screenshot dump.

The packet must be compact and selection-driven. Do not send the whole district/repository merely because it is available.

The AI/operator may inspect further repository sources on demand, but the initial task boundary remains the selected object/area plus declared dependencies.

Expected loop:

```text
owner selects object / chain / area
 -> types request
 -> AI MODIFY SELECTED
 -> Director packages structure + semantics + locks + visual context
 -> Codex/operator proposes bounded change
 -> affected content rebuilds into a preview candidate
 -> [ PREVIEW ] [ ACCEPT ] [ TRY ANOTHER ] [ DISCARD ]
 -> ACCEPT writes through canonical ENV authority
 -> affected validation / PLAY HERE
```

**PREVIEW must not silently become authority.** ACCEPT is the normal commit point for a material AI proposal. DISCARD leaves canonical content unchanged. TRY ANOTHER creates another proposal from the same owner intent/selection unless the owner edits it.

The AI must not treat visible neighbouring content as editable merely because it appears in screenshots. Locks and explicit mutation scope take precedence.

### Geometry execution route for selected AI edits

For requests that genuinely require changing mesh topology/shape rather than rearranging catalogue modules, `AI MODIFY SELECTED` may choose an optional geometry-editor route:

```text
selected semantic object
 -> Director packages bounds / locks / authority / intent
 -> AI/operator proposes geometry change
 -> optional UModeler X adapter performs bounded derived-mesh edit
 -> Director preview candidate
 -> ACCEPT
 -> juego-def-owned derived asset + lineage
 -> canonical ENV reference updated
 -> affected rebuild / validation
```

This route is optional. AI modification must still support non-UModeler modular/assembly workflows, and lack of UModeler X must not make D4 fail.

### `CREATE WITH AI`

Create/adapt a reusable asset or bounded structure that the current catalogue does not provide satisfactorily.

The request should automatically include relevant context:

- requested semantic category;
- explicit owner text intent when supplied;
- target dimensions/slot/selected area when available;
- nearby locked relationships;
- existing visual/ENV grammar constraints;
- allowed mutation scope.

Expected completion path:

```text
owner requests piece/structure
 -> reuse/search existing content first
 -> AI/operator adapts/derives/creates only if needed
 -> ENV intake/material/collision/lineage/validation
 -> thumbnail/metadata generated
 -> result appears in catalogue / AI Created
 -> owner decides where/how often to place it
```

Creating a new piece is not permission to redesign surrounding layout.

### `VARIANT`

Keep footprint/placement/access/locks unless the owner explicitly allows otherwise. Vary appropriate visual/content dimensions and expose the result as a selectable/replaceable candidate.

### `REPLACE`

Replace the selected object with a compatible semantic candidate while preserving placement intent as far as possible. Material changes should preview before commit.

### `EXPAND`

For a selected building/structure, request a bounded structural extension such as:

- additional floor;
- rear/side volume;
- shallow interior;
- yard/patio;
- frontage extension.

For the map/layout, expansion remains owner-driven through Layout/Expand Map tools; `EXPAND` must not invent a new district topology.

### `GENERATE HERE`

Generate/adapt content only inside an explicitly selected point/slot/area. Nearby locked content is immutable.

### `FILL AREA`

Populate a bounded selected area using an explicit category and density. Preview before committing a material batch.

### `MAKE ENTERABLE`

Create/adapt the minimum coherent threshold + shallow interior path for the selected building while respecting access truth.

### `POLISH SELECTED`

Inspect/improve only the selected object/group for obvious local visual/semantic defects. It is not permission to restyle or rearrange the district.

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

### D0 — 1-hour-shape spike: move one thing correctly — **PRESERVED**

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

**This revision does not change D0 and does not invalidate an implementation already in progress.**

#### D0.1 — mandatory transactional REBUILD hotfix

Owner decision after the first real D0 trial: **do not throw away the vertical slice or block forward UX work on this defect**, but do not pretend the safety proof is closed either. D0 may be used as a provisional foundation while this hotfix is tracked explicitly.

The independent review of frozen D0 candidate `b3bb4665b1051f22d8aca956eb1729f6d1c1ce09` found that REBUILD can replace the authoritative generated district spec before all rebuild preconditions are known and before the scene rebuild succeeds. A later cancel/failure can therefore leave `trace/spec/scene` out of sync.

The hotfix must close the **whole transaction class**, not only the observed dirty-scene case:

- check all cancel-able preconditions before authoritative spec replacement;
- keep regenerated spec staged until the operation can safely commit, where practical;
- once authority changes, any cancel/exception/failure in AFFECTED or FULL rebuild must automatically restore the prior authoritative state;
- REVERT/Undo semantics must remain unambiguous after failed/cancelled rebuilds;
- retain evidence for at least one forced post-regeneration cancel/failure proving the prior coherent state is restored;
- fresh review must re-test rebuild input identity/determinism as part of the repaired safety proof.

This debt **does not count as D0 PASS**. Owner authorizes forward progress into D1 in parallel, but D0.1 must be closed before D1 is accepted as the first usable owner release and before Director persistence is relied on for production-scale editing.

### D1 — LAYOUT MVP — **PRESERVED / first usable owner release**

Must include:

- Director window + Scene View overlay;
- node selection/move;
- `via` point selection/move;
- street selection + width edit;
- selecting a street/segment must clearly highlight the whole affected piece and its controlling handles/nodes, so the owner knows what will move before dragging;
- plaza vertex move;
- landmark move/rotate;
- explicit Y edit/vertical handle;
- labels and width/polygon guides;
- dirty state with an explicit visual distinction between **preview / saved authority / rebuilt scene**;
- save summary;
- backup + SAVE + REVERT;
- REBUILD;
- PLAY HERE;
- Undo/Redo;
- real CASCO test.

This remains the urgent production unlock. Do not delay it for catalogue, AI or expansion features.

### D2 — VISUAL CATALOGUE + PLACE/MODIFY — **mandatory builder release**

Turn the Director from a layout tool into a simple visual world builder.

Must include:

- catalogue panel with thumbnails and human-readable categories;
- search/filter plus favourites and recent items if cheap;
- ordinary placeable ENV prefabs/structures surfaced without Project-browser path knowledge;
- drag/click placement into Scene View;
- placement ghost;
- ground snap;
- orientation/snap assistance where context supports it;
- obvious valid/conflict feedback;
- click/select ordinary visible placed content directly in Scene View, including props generated by ENV;
- drag selected props/objects along the ground without entering coordinates;
- move;
- rotate;
- duplicate;
- delete;
- KEEP/LOCK;
- select supported linear structures as semantic chains and drag endpoint handles to extend/shorten them;
- live preview of repeated modules while a chain endpoint moves;
- persistent rebuild-safe authoring;
- generated-scene-only edits rejected as incomplete.

D2 is not PASS if the owner still needs prefab filenames, GUIDs, hierarchy paths or Inspector transforms. It also does not PASS if a visibly misplaced ordinary prop (the reference case is a barrel) cannot simply be clicked and dragged to a better location, or if a supported modular railing/wall chain cannot be extended/shortened from an endpoint without manually placing each segment.

**D2 implementation proof must demonstrate the prior-art-derived primitives, not merely equivalent screenshots:**

- semantic pick from visible child -> logical authored object;
- shared surface resolver;
- non-authoritative placement/move ghost;
- native Undo integration;
- isolated/stable catalogue thumbnail generation;
- chain endpoint preview/commit;
- no duplicated Scene View input loop per tool.

### D3 — MAP EXPANSION

D3 builds on D2's direct object manipulation and stretchable-chain interaction. The same mental model should scale from "make this railing 4 m longer" to "continue this street / edge / block into new playable space".

Enable the owner to grow the authored world using the same simple interaction model.

Must prove on a real edge/extension:

- extend an existing street;
- create a new bounded street segment/bend/connection;
- add/reshape one public space or expansion area;
- place/arrange structures from the catalogue in the extension;
- connect the extension to existing playable space;
- save/rebuild/play the result;
- preserve existing locked layout/content.

No autonomous district growth is required or desired.

### D4 — AI ASSET / STRUCTURE FORGE

Make AI useful as a **supplier to the builder**.

Add bounded:

- **AI MODIFY SELECTED** with automatic structural + visual context packet;
- CREATE WITH AI;
- VARIANT;
- REPLACE;
- EXPAND;
- GENERATE HERE;
- MAKE ENTERABLE.

`AI MODIFY SELECTED` is the preferred path when the owner can point at the relevant world content and describe the desired result in natural language. It must support object, semantic-chain and bounded-area selections without requiring the owner to transcribe coordinates or hierarchy paths.

AI proposal generation should be non-blocking from the owner's point of view: the Director remains usable while a request is outstanding, and completed proposals return to an explicit review/accept surface.

At least one `AI MODIFY SELECTED` proof and at least one AI-created/adapted reusable piece/structure must be retained.

The selected-modification proof must show:

- object/area selected in Scene View;
- short owner request in natural language;
- automatically assembled context packet with locks/bounds;
- proposal produced without owner-provided coordinates/object paths;
- PREVIEW before authority;
- ACCEPT or DISCARD semantics;
- unrelated locked content unchanged.

The reusable piece/structure must:

- originate from an explicit owner request/selection;
- pass the normal ENV intake/lineage/validation path;
- receive a thumbnail/category;
- appear in the visual catalogue;
- be placeable/movable by the owner like ordinary content;
- survive rebuild;
- not rewrite unrelated layout/content.

### D5 — SMART BUILDERS / BRUSHES

Add high-leverage construction gestures only after D2-D4 work.

Candidate tools, implemented only where the existing grammar supports them cleanly:

- advanced wall/edge draw tool beyond the mandatory D2 endpoint-stretch interaction;
- advanced street continuation tool beyond D3's required map expansion;
- building-row/frontage tool;
- vegetation/prop brush;
- bounded area fill with category + simple density control.

Each tool must preview before material commit and remain editable after creation.

This milestone is about reducing repetitive clicks, not giving procedural tooling authority over composition.

D5 tools should reuse the common Area/Chain/Placement primitives established by D2-D3. Line/fill/lasso behavior has strong prior art; inventing a second independent brush/input framework is a FAIL unless a concrete limitation of the shared tool stack is demonstrated.

### D6 — FAST QA / PLAY LOOP

Complete the edit -> experience -> correct loop:

- validate selected/affected;
- targeted rebuild where reliable;
- route/clearance probe launch for affected area;
- third-person capture shortcuts;
- before/after comparison;
- conflict/highlight for known hard constraints;
- PLAY HERE from current/selected area.

### D7 — OWNER PRODUCTION PROOF

Run a real keeper production trial, not a synthetic sandbox.

The owner must use the Director to:

- modify existing composition;
- place content from the visual catalogue;
- expand playable map space;
- request at least one new AI-created/adapted piece;
- place and modify that piece;
- play/inspect;
- correct;
- validate;
- retain the result.

Freeze only when this is genuinely easier than prompt-by-prompt spatial manipulation or normal Unity prefab/path work.

## Required owner trial

Without opening JSON, writing code, using Inspector coordinates or searching prefab paths in the Project browser, the owner must be able to complete all materially applicable steps on a real ENV district:

1. move a real street node;
2. move a `via` point;
3. change a street width;
4. reshape a plaza;
5. click a visibly misplaced ordinary prop directly in Scene View and drag it to a sensible position without hierarchy/path lookup;
6. select a supported railing/wall chain and extend or shorten it by dragging an endpoint;
7. open the visual catalogue and identify useful pieces by thumbnail/category;
8. drag/place a structure or prefab;
9. move and rotate it;
10. duplicate one item and delete another;
11. lock an accepted element;
12. extend playable map/layout at a real boundary;
13. populate part of that expansion with catalogue content;
14. select an existing object/chain/area, describe a desired change in natural language and run AI MODIFY SELECTED without supplying coordinates or hierarchy paths;
15. inspect the returned bounded PREVIEW and either ACCEPT or DISCARD it;
16. request one bounded AI-created/adapted reusable asset or structure;
17. see that result enter the catalogue;
18. place or replace with the AI-created result;
19. SAVE and inspect a human-readable summary;
20. rebuild;
21. PLAY HERE in/near the edited or expanded area;
22. validate the affected area;
23. Undo or REVERT one change safely;
24. close/reopen Unity and prove accepted edits persist.

The owner should be able to discover this workflow from the Director UI itself with minimal instruction.

## Power-user features allowed after the basic UX works

Only after the core builder UX is genuinely usable:

- keyboard shortcuts;
- numeric snap increments;
- copy/paste style/role;
- align/distribute;
- frontage-row group move;
- constrained street offset;
- richer density controls;
- layer visibility presets;
- reusable selection sets;
- side-by-side reference image/bookmark;
- batch lock/unlock;
- change history panel;
- custom palette collections.

**Thumbnail catalogue, placement ghost, snap/basic alignment and direct place/move/rotate are not power-user extras; they are D2 requirements.**

## Evidence

Retain under `Docs/evidence/WP-PROD-ENV-DIRECTOR-00/` at minimum:

- short implementation/readme;
- D0/D1 evidence without rewriting/re-proving already accepted implementation unnecessarily;
- capture sequence of visual catalogue -> ghost placement -> commit -> move/rotate -> rebuild persistence;
- capture/evidence of real map expansion;
- round-trip proof for trace/spec/polish/other authority touched by the Director;
- backup/revert/undo proof;
- targeted vs full rebuild behavior;
- persistence proof after Editor restart;
- AI MODIFY SELECTED context-packet example with selection, owner request, locks/bounds and standardized captures;
- PREVIEW -> ACCEPT and PREVIEW -> DISCARD evidence;
- AI-created/adapted piece provenance + catalogue thumbnail + placement proof;
- AI scope proof that unrelated/locked content remained unchanged;
- prior-art implementation note: which mechanisms were reimplemented, which MIT code (if any) was reused with attribution, and which sources remained reference-only;
- owner production-trial checklist/result;
- known limitations that are real product constraints rather than hidden unfinished basics.

## Validation

At minimum test:

### Data safety

- load/save with no edits is semantically no-op;
- unknown fields survive supported round trips;
- backup created before authoritative replacement;
- malformed/unsupported source fails closed;
- Undo/Revert cannot leave half-written authority;
- generated scene remains rebuildable from repository authority.

### Optional-integration / commercial-separability safety

- Director core compiles and performs its normal D0-D7 responsibilities without UModeler X installed;
- optional geometry integration is isolated behind an adapter/boundary rather than leaked through core types;
- UModeler X package content is not redistributed by Director;
- geometry edits produce juego-def-owned derived outputs with lineage instead of mutating vendor packages;
- disabling an unavailable/incompatible geometry adapter fails gracefully and does not corrupt canonical ENV state.

### Architecture / prior-art safety

- no third-party code is copied from a source whose license does not permit the intended use;
- any reused MIT code retains required notices/attribution;
- normal tool modes share picking/surface/preview/commit primitives instead of duplicating them;
- thumbnail generation does not modify the production scene;
- semantic picking resolves meaningful authored units rather than exposing generated child hierarchy as the user model.

### Builder safety

- catalogue item maps to known/admitted source or generated content with lineage;
- ghost preview does not commit authority until placement;
- cancelling placement leaves no durable object;
- locked elements cannot be modified accidentally;
- local placement/edit does not silently rewrite unrelated content;
- placed/modified content survives rebuild.

### Expansion safety

- expansion remains connected to intended existing space;
- existing locked layout/content survives;
- saving expansion does not require hand-editing JSON;
- expansion can be rebuilt from canonical upstream data.

### AI scope safety

- AI request has explicit selection/bounds;
- context packet identifies immutable/locked neighbours separately from editable selection;
- standard visual captures do not implicitly broaden edit authority;
- owner is not required to provide coordinates, hierarchy paths or prefab IDs for a selected-scene request;
- PREVIEW does not mutate canonical authority before ACCEPT;
- DISCARD leaves canonical data unchanged;
- generated/adapted result records provenance/lineage;
- AI-created content is independently placeable from the catalogue;
- AI action does not gain implicit authority over district topology;
- the editor remains usable while an AI proposal request is outstanding.

### Scale

Test on the real ENV-01 CASCO-scale district, not only a toy fixture. Catalogue/selection/guides must remain usable at that scale; ordinary dragging/placement must not trigger full regeneration every frame.

### Product loop

- edit/build/expand;
- save;
- rebuild;
- Play Here;
- affected validation;
- owner visual judgment.

## PASS

PASS when all of the following are true:

- D0/D1 safe direct layout manipulation works on the real district;
- the owner can use normal Director workflows without JSON/code/Inspector-coordinate/prefab-path knowledge;
- D2 provides a genuinely visual thumbnail catalogue plus game-like place/move/rotate/duplicate/delete/lock;
- ordinary visible props can be clicked and ground-dragged directly, with the misplaced-barrel case proven end-to-end;
- supported modular railing/wall chains can be extended/shortened by dragging semantic endpoints, with module repetition/end treatment handled underneath;
- placed and modified structures survive rebuild through canonical upstream authority;
- D3 lets the owner expand real playable map space visually without autonomous topology invention;
- D4 proves AI MODIFY SELECTED with automatic structural/semantic/visual context, explicit PREVIEW/ACCEPT/DISCARD and no owner-supplied coordinates/paths, and lets AI/operator manufacture/adapt at least one reusable requested piece/structure that enters the catalogue and can then be placed by the owner;
- AI actions remain bounded by human selection/intent and do not silently rewrite locked/unselected content;
- D5, if implemented for PASS, reduces repetitive construction while leaving generated results editable;
- D6 closes the loop through PLAY HERE and affected QA;
- the real owner production trial succeeds;
- the owner explicitly prefers this path for routine environment building over prompt-by-prompt agent spatial manipulation and normal prefab/path archaeology;
- no material ENV regression is hidden by the tool.

## FAIL

FAIL if any of the following survives:

- normal use still requires Inspector transforms, JSON editing, code or prefab/path/GUID knowledge;
- the Director remains mainly a trace/debug visualizer instead of becoming a builder;
- catalogue items lack usable thumbnails/categories or still require Project-browser archaeology;
- a visible ordinary prop cannot be selected and dragged directly because the owner must find its hierarchy/source entry first;
- a supported railing/wall chain requires manually moving/placing individual segments instead of endpoint extension;
- placement is blind rather than ghosted/direct;
- owner edits/placements disappear on rebuild;
- generated Unity scene becomes hidden authority;
- map expansion still requires an agent to translate owner intent into coordinates;
- AI MODIFY SELECTED still requires the owner to transcribe coordinates, hierarchy paths or prefab IDs that the Director could derive from selection;
- AI proposal preview writes canonical state before explicit ACCEPT;
- AI-created content cannot flow back into the same reusable catalogue/placement path;
- AI commands can rewrite unselected/locked/global content without explicit scope;
- the tool becomes an autonomous city generator rather than a human construction surface;
- every small move/place requires a full district rebuild;
- implementation grows into a general-purpose Unity replacement/editor framework;
- the owner finds it slower or more confusing than the current path.

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

`WP-PROD-ENV-02` must now prove the complete builder model rather than only scene assembly:

```text
fresh brief
 -> owner draws/reshapes layout in ENV Director
 -> owner places existing catalogue pieces
 -> owner expands playable space
 -> AI/operator manufactures missing requested pieces/structures
 -> new pieces enter the same catalogue
 -> owner places/adjusts/locks
 -> factory rebuild + validators
 -> PLAY HERE
 -> owner corrects directly
 -> keeper candidate
```

ENV-02 must prove three materially different use cases:

1. **EDIT EXISTING** — materially improve an existing area through Director manipulation.
2. **EXPAND MAP** — extend a real boundary into new playable space through Director tools.
3. **AI-SUPPLIED CONTENT** — request at least one missing piece/structure from AI/operator, admit it through ENV, place it from the catalogue, and retain it.

The desired production model is:

**human-built/directed world + AI-made/adapted pieces + deterministic factory + automated QA**.

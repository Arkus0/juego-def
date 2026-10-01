# ENV factory — environment production workflow

Status: **CURRENT PRODUCTION PATH** (built by `WP-PROD-ENV-01`; scene-scale proof is `WP-PROD-ENV-02`)  
Operator posture: `BOUNDED_OPERATOR` (Claude Code + MCP for Unity; headless Blender for derivation). Owner remains the look authority.

## What it is

A small, data-driven path from **CITY demand** to **walkable street content**:

```text
CITY/B0 brief ─► request units by outcome (units.json / district trace)
      │                 │
      │   discover:  python Tools/env_catalog.py search|modules  +  python Tools/asset_catalog.py search
      ▼                 ▼
 vendor kit (installed, ignored) ─► Blender recipes (donor cleanup / new pieces on kit trim sheets)
      │                                   │  Tools/blender/env_derive.py  →  Derived/ENV/Meshes/*.fbx
      ▼                                   ▼
 Unity: 1 Generate Materials → 2 Build Modules → 3 Build Library → 7 Build District → 5 Validate
      │     palettes/textures      prefabs+colliders    units+previews    district scene     report
      │
      │  districts: real reference (OSM + IGN MDT05) ─► Tools/env_district.py measure
      │             authored trace (Env/Specs/districts/<id>.trace.json) ─► Tools/env_district_skeleton.py
      │             ─► district spec (blocks, rows, plots, terrain, ground meshes, river, stairs, route)
      │             ─► 7 Build District (EnvDistrict, chunked) ─► Play: route probe over the whole tour
      ▼
 python Tools/env_catalog.py lineage → check → inventory ;  python Tools/asset_catalog.py build → validate
      ▼
 Play Mode: JDRouteProbe route walk (GC2 player) + third-person captures → owner review
```

Not a city generator: buildings, streets and edges are assembled from a vocabulary; composition stays an authored act.

## ENV01 authored authority — accepted 2026-10-01

`WP-ENV01-AUTHORED-01` changes the authority model for the existing CASCO instance without deleting the reusable ENV factory. The current production level is now:

- `Assets/JuegoDef/Scenes/ENV/ENV01_AUTHORED.unity` — **authoritative persistent Unity scene**, committed through Git LFS;
- `Assets/JuegoDef/Authored/ENV01/` — frozen static snapshot of the generated ENV assets that the level owns;
- `ENV01_REFERENCE.unity` — comparison/reference copy of the pre-migration hierarchy;
- legacy trace/spec/builders — provenance and reusable factory inputs only; they **must not regenerate or replace ENV01_AUTHORED**.

For ENV01, ordinary spatial production is now direct Unity authoring: move/reorganize existing objects, consolidate buildings deliberately, improve facades/interiors/props and save the scene. The accepted migration proved persistence across scene reopen, domain reload, editor restart and Play Mode, while preserving the full renderer/collider/light population. Legacy rebuild entry points are guarded while the authored/reference scene is loaded.

This is an ENV01 authority decision, not a rejection of the ENV factory for new vocabulary or future districts. New reusable modules can still be produced through the factory and then deliberately admitted into an authored level.

## Where things live

| What | Path |
| --- | --- |
| Grammar data (palettes, material recipes, module policy, validator policy) | `Unity/JuegoDef/Assets/JuegoDef/Env/Grammar/*.json` |
| Unit library request | `Unity/JuegoDef/Assets/JuegoDef/Env/Specs/units.json` |
| Factory code (Editor only) | `Unity/JuegoDef/Assets/JuegoDef/Editor/Env/` (`EnvKit`, `FacadeGrammar`, `BuildingAssembler`, `EnvTemplates`, `EnvStreet` (facade-row rules), `EnvDistrict`, `EnvMaterials`, `EnvModules`, `EnvLibrary`, `EnvValidator`, `EnvClearance`, `EnvImportRules`, `EnvPreview`, `EnvLighting`) |
| Route probe (dev runtime) | `Unity/JuegoDef/Assets/JuegoDef/Runtime/Dev/JDRouteProbe.cs` |
| Blender derivation recipes | `Tools/blender/env_derive.py` (reads the vault `.blend`, never writes it) |
| Owned outputs (with lineage) | `Unity/JuegoDef/Assets/JuegoDef/Derived/ENV/{Meshes,Modules,Materials,Textures,Units}` |
| District scenes | `Unity/JuegoDef/Assets/JuegoDef/Scenes/ENV/`; **ENV01_AUTHORED is committed/LFS and authoritative**. Legacy generated scenes remain factory outputs only. |
| District specs (authored trace + generated spec) | `Unity/JuegoDef/Assets/JuegoDef/Env/Specs/districts/` |
| District tools | `Tools/env_morphology.py` (street study), `Tools/env_district.py` (district metrics, IGN DEM), `Tools/env_district_skeleton.py` (trace → spec), `Tools/env_textures.py` (painted tileable textures) |
| Composition rules | [`ENV_COMPOSITION_RULES.md`](ENV_COMPOSITION_RULES.md) |
| Searchable indexes | `Docs/asset_catalog/env_library.json`, `env_derive_manifest.json`, `lineage.json` |

## Run it (clean clone or after a change)

```powershell
python Tools/asset_catalog.py install --pack medieval   # plus props, nature (vault C:/Juego2-Assets)
blender -b --factory-startup --python Tools/blender/env_derive.py      # only if a recipe changed; add -- --only NAME
```

Generated textures (only when a generator changed; deterministic, one random stream per output):

```powershell
python Tools/env_textures.py --out Unity/JuegoDef/Assets/JuegoDef/Derived/ENV/Textures   # ground, canvas, weathering noise, stain atlas, water ripples
python Tools/env_masonry.py --out Unity/JuegoDef/Assets/JuegoDef/Derived/ENV/Textures   # 8 masonry/paving bonds, 4 m tiles (~5 min)
python Tools/env_signs.py                                                              # shop lettering, blade icons, notices, house numbers, painted adverts
```

Unity menu `JuegoDef > ENV`: **1 Generate Materials → 2 Build Modules → 8 Build Interior Rooms → 3 Build Library → 7 Build District → 5 Validate** (and **6 Validator Self-Test** after touching the validator). Then:

```powershell
python Tools/env_catalog.py lineage ; python Tools/env_catalog.py check ; python Tools/env_catalog.py inventory
python Tools/asset_catalog.py build ; python Tools/asset_catalog.py validate
```

Every step is idempotent (assets are updated in place, GUIDs kept). A module whose recipe/wrapper disappears is deleted by step 2, so no orphan lineage survives.

**A district** (the CASCO, ~180 × 220 m, 311 buildings):

```powershell
python Tools/env_morphology.py fetch --bbox <S,W,N,E> --out <scratch>/osm.json     # Overpass, ODbL
python Tools/env_district.py dem --bbox <S,W,N,E> --out <scratch>/mdt05.tif       # IGN MDT05, CC BY 4.0
python Tools/env_district.py measure --osm ... --dem ... --origin <lat,lon> --box <x0,y0,x1,y1> --out metrics.json --plan ref.png
python Tools/env_district_skeleton.py --trace Unity/JuegoDef/Assets/JuegoDef/Env/Specs/districts/<id>.trace.json --osm ... --out .../<id>.json --plan plan.png --metrics metrics.json
```

For a **new/legacy generated district**, `JuegoDef > ENV > 7 Build District` (or `EnvDistrict.Begin(id)`, `BuildRows(from, count)`…, `Finish()`) remains the factory path.

For the accepted CASCO instance **ENV01**, do not use that path to continue production. Open `ENV01_AUTHORED.unity` and edit the persistent scene directly. Its generated inputs are frozen provenance, not rebuild authority. The migration guards intentionally reject legacy Begin/BuildRows/Finish/RebuildRow/ApplyOps/NewStage/BuildRig paths while authored/reference is loaded. Review from product-relevant third-person views and use the accepted ENV01 evidence as the preservation baseline.

## Vocabulary

### Frontage types (`BuildingSpec.type`)

`mixed_commercial` (shops + portal ± service door), `lodging` (central arched portal, one balcony), `closed_residential` and `termination` (near-solid ground floor, portal, ≤1 window/garage shutter), `warehouse` (gates, high small windows, gable roof). Width in 2 m **bays**, depth 4/6/8 m (eaves roofs) or ≤12 m (gable roofs, span 4–8 m), floors 1–5, `seed` for deterministic variety, `palette` id.

### Bay codes (one character per 2 m bay; rows ground-first; empty rows are generated)

| Ground floor | | Upper floors | |
| --- | --- | --- | --- |
| `S` shop display window | `E`/`e` shop door closed/open (open = walkable) | `W` window + open shutters | `c` closed shutters |
| `R` shop bay behind roller shutter | `V` galvanised service door | `w` bare window | `T` small round-head window |
| `D`/`o` portal closed/open | `A`/`O` arched portal closed/open | `B` timber balcony / `I` iron balcony (glazed balcony door) | `L` glazed gallery (mirador) |
| `G` timber gate | `W` window, `P` plain wall | `P` plain wall | |

Grammar rules that encode owner reviews and real references (Castro Urdiales, Combarro):

- upper floors share **one rhythm of opening axes** with plain wall between them (≈1 axis per 3–4 m), never a window in every bay;
- **at most one balcony door per facade**, on the principal floor, on the most central axis; everything else is a window;
- galleries occupy one axis, floors 1–2; top floor of tall buildings takes smaller windows;
- plaster bays use the **derived clean walls** (kit half-timbering removed); rubble-stone bays get a derived glazed insert inside the kit stone surround.

### Palettes (`Env/Grammar/palettes.json`)

A palette names `facade`, `trim`, `joinery`, `roof`, `tiles`, `glass`. Vendor material slots are remapped by **module role** (`wall`, `joinery`, `shop`, `roof`, `stone`), so the same kit piece becomes cream/ochre/sage/blue-grey/rose/white render, painted green-blue/white/oxblood/blue joinery, terracotta/wet-brown/slate roofs. Add a palette = one JSON line; add a colour = one recipe in `materials.json`.

### Casco vocabulary (quality pass, owner 2026-09-28)

- `BuildingSpec.eave` resolves to **canecillos** (deep eave on carved rafter tails under the kit overhang) for casco
  palettes unless reformed; `solana` adds a timber gallery across the top floor (bay code **`N`** is its door; wing
  walls close the ends; no other balcony door on that facade); `surrounds` swaps rendered windows for the sandstone
  `ENV_Window_Wide_Ashlar` (no exterior shutters over stone); `escudo` hangs `ENV_Escudo` over the portal; `basement`
  gives a stone base down to the lowest ground (slopes, river walls).
- **Ashlar quoins** (`ENV_Quoin_Ashlar`) only where a corner is seen (exposed side at that storey, or a mitred tip);
  no pilaster on shared party lines.
- Downpipes are rare under canecillo eaves and absent on solana houses; when present they get `ENV_Downpipe_Head` and
  `ENV_Downpipe_Shoe`.
- Street pieces rebuilt to kit level: lathe-profiled iron (lamp post, bollard), slatted bin, meter cabinet, wrought-iron
  hanging sign, fascia, striped scalloped awning, terracotta pot, solid-crown `ENV_Tree_Plaza`, `ENV_Hill_Tree`,
  `ENV_Bridge_Arch`, `ENV_River_Stairs`, `ENV_Fountain_Trough`. Flat-colour ENV materials now carry painted textures
  (`Tools/env_textures.py`).

### Look pass after the owner audit of 2026-09-29 (45 points)

The district keeps its morphology; what each plot *is* is decided in the builder, not in the spec:

- **Character pass** (`EnvCharacter`): street personality by street id (commercial spine, bar streets, river edge,
  damp residential lanes, calle alta, huerta edge, plaza) → per building a **facade family** — `render` (all render,
  often no quoins, painted or low stone plinth), `zocalo` (render over a stone base 0.6–1.3 m), `stone_ground`,
  `stone`, `rehab` (fresh render, modern joinery), `modern` (clad ground floor, aluminium shopfront) — with render hue
  × condition (Nuevo / Pintado / Viejo / Gastado), masonry bond × tone, dressed stone, quoin style (ashlar / slim /
  painted / none), joinery and roof tiles, pitch, solana share and plant share. Weights are one table per street kind.
- **Weathered materials** (`JuegoDef/ENV/Weathered Lit`, material families in `materials.json`): macro tone and hue
  drift in world space, stone-scale tone, rising damp (object storey or river water line), rain streaks, moss,
  repair patches, flaking render; every family member has its own seed and jittered amounts. Masonry/paving
  textures from `env_masonry.py` repeat every 4 m.
- **Weathering by cause** (`FacadeGrammar.Weathering`, `ENV_Stain_Quad` + `JuegoDef/ENV/Stain`): splash and damp under
  each downpipe, streaks under sills, rust under iron balconies, run-off at seen corners, damp/algae bands at the
  foot, repair patches, soot over extractors; density follows the render's condition, none on a fresh front.
- **Contemporary layer** (`FacadeGrammar.Contemporary`): air conditioning, alarm boxes, intercoms, enamel house
  numbers, extractor vents, telecom boxes, gas risers — placed only where the wall has room and never on a
  downpipe line.
- **Ground-floor programme** (`EnvBusiness`, `Env/Grammar/businesses.json`): each commercial plot becomes a named
  fictional business (used once) or a garage / workshop / closed shop / ground-floor home, by street kind. It rewrites
  the ground bays (roller, gate, windows), picks the interior behind the glass, one fascia per shop run with its
  lettering, blade signs with trade icons, pharmacy cross, ATM, chalkboards, goods and barrels at the door, "SE
  ALQUILA" / "VADO PERMANENTE" notices, faded fascias of vanished shops. Lodging gets hostal plaques.
- **Glass**: every pane shows a fake interior (`JuegoDef/ENV/Interior Room`, rooms from menu 8, per-opening variants
  8b) with net curtains and roller blinds at different heights and a Fresnel reflection of the baked probe.
- **Plants**: rare, reasoned and varied (hydrangeas, ferns, geraniums, box balls, bay laurel in terracotta, glazed
  pots, old tins, stone troughs, timber boxes); stone benches by old doors on the damp lanes.
- **Ground**: paving by reason (`EnvDistrict.PaveOf`): flag strip only on the main spine, canto variants by street,
  setts on bridges, big flags on the plaza with a cobbled rim; overlays (`PavingOverlays`, laid 8 mm over the ground)
  for lane drainage channels, flag bands along facades and **repair strips** (`RepairStrips`: straight utility-trench
  strips in old setts or concrete, texture aligned to the strip); door steps and shop thresholds. The ground is welded
  (`GroundWeld`, 7.5 cm) so zone borders leave no hairline holes.
- **Plaza, river, edge**: fountain monument with candelabra, the singular tree, riverside walk, terraces; river water
  with depth, ripples, foam and reflection over a cobble bed with rocks, channel walls with water line, drains, ferns
  and ivy, stone bridge parapets and lamps; field walls, hedgerows and barns round the town.
- **Lighting** (`EnvLighting.BuildRig` → `JDLightingRig`, F9 in Play Mode): day / dusk / night presets drive sun,
  trilight ambient, linear fog that starts beyond the street, the Atlantic sky shader (horizon = fog colour, clouds),
  post-processing, lamp and lantern lights, interior brightness and a baked reflection probe per preset; SSAO sized
  for buildings.

### Micro-polish pass (walking the district, owner brief 2026-09-29)

After the look passes the district is inspected **by walking it**, unit by unit (`Docs/evidence/WP-PROD-ENV-01/micro-polish/UNITS.md`),
with a technical pass (P0 holes/clipping/floating, P1 camera and route, P2 architecture, P3 ground, P4 local composition,
P5 detail) and a **semantic** pass (does it make sense to a person: a board advertises what the shop behind it sells and
stands in front of it, furniture leaves the centreline clear, a strip does not end in a door).

- **Tools** (`Editor/Env/EnvWalk.cs`): `Street(id, folder, spacing, modes, w, h, holes)` walks a street both ways with the
  real GC2 third-person camera (`game`), `eye`, `diag`, `up` and the ground-facing `gnd` scan; `Building(path, folder)`
  views one building from the street; `Audit(street)` lists floating, sunk, overlapping and in-wall floor props;
  `GroundSeams()` and `WallGaps(row)` measure ground integrity; `holes: true` renders on a magenta background and
  `Tools/env_holes.py` counts hole pixels. Paths are relative to the Unity project folder (`Captures/` is git-ignored;
  curated shots are copied to `Docs/evidence/`).
- **Corrections survive a rebuild** (`EnvPolish`, `Env/Specs/districts/<id>.polish.json`): `plots` overrides any
  `BuildingSpec` field per building id, applied after the character pass; `ops` (`remove`, `move`, `place`, found by module
  name near a world point) run at the end of `EnvDistrict.Finish()`. Every entry names its unit, class (TECH/SEM) and why.
  `EnvPolish.RebuildRow(id)` rebuilds one row live in ~0.3 s exactly as a full build would (a dry run replays the stateful
  business pass first); a full rebuild takes ~30 s and is deterministic.
- **Generic fixes made by the first pass**: ground vertex weld and an earth underlay 10 cm below the ground, 10 cm footing
  under every facade, overlay winding (the overlays had never rendered), repair strips instead of relabelled triangles,
  chalkboard text by business type (`boardNotice`), and a route probe that follows the street vertices (`DensifyRoute`).
- **Semantic audit** (`Editor/Env/EnvSemantics.cs`, `Docs/evidence/WP-PROD-ENV-01/micro-polish/SEMANTICS.md`): doors onto the
  river / a drop / a parapet, windows onto walls, bare side walls, walls that are too long, twin fronts and props with no
  function, per inspection unit (`<id>.inspection.json`). Its fixes: `BuildingSpec.noEntrance` (river rows have no door),
  `BuildingSpec.raise` (a door buried by rising ground), bridge parapets kept off doors, side-wall windows, panelled garden walls,
  and `EnvPolish.FixBlockedOpenings`, a physical pass at the start of `Finish()` that rebuilds rows through `EnvPolish.Auto`
  (in-memory overrides on top of the polish file).

### Templates (`EnvTemplates`)

`StreetGround` (kerbed carriageway + pavements, or pedestrian single level with drainage channel), `QuayEdge` (public quay wall/coping/bollards/ladder/guard rail/water), `YardBoundary` (controlled work yard palisade + closed gate), `SteppedConnector` (1–3 m rise cut into a terrace with retaining walls and rails), `ShopInterior`, `LodgingVestibule`, `Cluster` (data list of props).

### Threshold interface

Every ground-floor door/gate carries an empty `THR_*` marker on its clear passage centre, forward = out to the street: `THR_Public_Shop`, `THR_Public_Portal` (walkable), `THR_*_Closed` (leaf shut), `THR_Service_Closed` (must never be a public shortcut). Routes, validators and later interaction/NPC work use these instead of guessing coordinates.

### District spec (`Env/Specs/districts/<id>.json`, generated from `<id>.trace.json`)

`streets` (centreline, width, role, heights), `blocks` with `rows` (one per block edge: frame, `ends`
open/hidden/tip_keep/tip_cede/concave, `plots` with width, depth, floors, palette, setback, level), `plazas`, `zones`
(huertas, yards), `ground` meshes per paving zone, `river` (channel, banks, parapets, stairs, bridge arches),
`fountains`, `garden`, `route` and `spawn`. `EnvDistrict` resolves each row with the facade-row rules (`EnvStreet`),
builds ground, stairs, bridges and dressing, the GC2 player and a disabled `RouteProbe`.

The four v1 street demos (A commercial-to-quay, B upper lane, C casco reference and its kit-palette control) and their
street-spec assembler and street-life pass were retired on 2026-09-29, when the owner kept the CASCO district as the
one ENV scene; their captures stay in the WP evidence and the code in git history (commit `c3d7796`).

## Routine recipes

- **New building variant:** add a `units.json` entry (`type`, `bays`, `floors`, `palette`, optional `rows`) → steps 3–5. No code.
- **New district:** measured reference → authored `Env/Specs/districts/<id>.trace.json` → `env_district_skeleton.py` → `EnvDistrict.Begin/BuildRows/Finish`, enable `RouteProbe`, Play, read `JD_ROUTE` lines.
- **New derived piece:** add a `@recipe` in `env_derive.py` (donor via `donor()`/`clean_*()` or new geometry on kit trim-sheet bands via `box(..., uv="band")`), run it, add a collider policy if not mesh, reference it from a bay code/template → steps 2–5 + lineage.
- **New source prop:** add a wrapper to `modules.json` (collider + owned `ENV_Src_*` material with declared `sources`) → steps 1–2.

## Validation (`JuegoDef > ENV > 5 Validate`, report `Docs/evidence/WP-PROD-ENV-01/VALIDATION.json`)

Units and district scenes are checked for: banned kit modules (medieval/alpine cues, `Env/Grammar/validation.json`); missing materials or machine-local vendor materials; Unity primitives or `Proxy`/`Greybox` objects; facade bays without collision; open thresholds blocked for the **real GC2 capsule** (radius 0.2 + skin 0.08, height 2.0; sills ≤ 0.1 m allowed) and closed/service thresholds that are actually open; buildings not sitting on the street surface; duplicated coplanar tiles. `6 Validator Self-Test` seeds one defect of each class and must report `missed=0`. Python `env_catalog.py check` covers B0 demand coverage, library/preview/prefab presence, recipe↔mesh parity and lineage completeness.

## Hard-won rules

- Kit walls are **open shells**: Blender booleans need the exact solver with *hole tolerant*.
- The kit's Blender → Unity orientation is a 180° turn about the vertical (`U()` + `export()` handle it).
- Kit materials bind to models by **name search at import**; derived FBX use Unity *Search-and-Remap by name*.
- Props/Nature intake needs `EnvImportRules` (file scale, 2D textures) and **owned** materials; Unity-generated vendor materials have machine-local GUIDs.
- `M_Plaster` cannot be recoloured (non-modifiable base texture, brick-reveal masks): owned plaster uses `M_BaseWear`.
- Emission on window glass reads as beige under the project volume; shop glass is dark, moderately smooth, and streets bake a reflection probe.
- Clear door height ≥ 2.22 m for the current GC2 capsule; no sills above 0.1 m; keep furniture out of the door lane.
- Trim-sheet bands: a tinted small-block band reads as **brick**; dressed stone uses one block per modelled piece on the
  smooth slab band.
- Anything cut out of a heightfield ground (stairs) uses flat caps: a square cap punched a hole in a junction and the
  route probe fell through it.
- Several editors named `JuegoDef` may be connected to the MCP (Codex worktrees): pin by hash and check
  `Application.dataPath` before mutating.
- Unity null: never `GetComponent<T>() ?? AddComponent<T>()` (the fake-null component is returned); test with `if (!c)`.
- The MCP `refresh_unity` compile request can return before the editor recompiles; check a new method by reflection
  (or `error CS` in `Editor.log`) before trusting a rebuild.
- The kit fern (`ENV_Plant_Fern`) is ~9 m wide: scale ≈ 0.07. The kit rock is 3 m: river rocks 0.2–0.5.
- Physics clearance spheres above the paving must start above the ground collider, or every candidate reads as blocked.
- Unity front faces are clockwise from the viewer: `Cross(b - a, c - a)` points **up** for a face seen from above. A swapped
  winding made every paving overlay invisible for a whole pass; check `up` vs `down` normals of any generated mesh.
- Judge ground and joints with a **magenta background** (`EnvWalk` `holes`): a hairline crack or a slit under a wall is
  invisible in a normal frame and shows as a bright line on foot. Ground zones must be welded.
- The spec's `basement` below 5 cm builds no base at all; every facade gets a 10 cm footing so a small dip never opens a slit.
- The route probe walks straight lines between waypoints: waypoints must include the street vertices or a bend is cut
  through the props on its inside.
- Unity CLI (`unity command eval_file --file x.cs`) picks the Editor by the **working directory**: run it from the project
  folder (another `JuegoDef` editor may be connected). Its reply is cut at 5 s of main-thread time but the work continues:
  write long results to a file and poll it. `eval` takes no `using` lines (fully qualify names).

## Current limits (see `Docs/evidence/WP-PROD-ENV-01/B0_COVERAGE.md`)

Six facade families over two wall geometries (render, masonry) — no post-1960 infill block building type; no hipped
roofs, dormers or roof terraces; no trapezoid corner buildings (corners are rectangles or chamfers). Lighting is
look-development, not the final day cycle. Remaining items are content breadth, not missing pipeline.

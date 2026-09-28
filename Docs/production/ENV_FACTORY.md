# ENV factory — environment production workflow

Status: **CURRENT PRODUCTION PATH** (built by `WP-PROD-ENV-01`; scene-scale proof is `WP-PROD-ENV-02`)  
Operator posture: `BOUNDED_OPERATOR` (Claude Code + MCP for Unity; headless Blender for derivation). Owner remains the look authority.

## What it is

A small, data-driven path from **CITY demand** to **walkable street content**:

```text
CITY/B0 brief ─► request units by outcome (units.json / street spec)
      │                 │
      │   discover:  python Tools/env_catalog.py search|modules  +  python Tools/asset_catalog.py search
      ▼                 ▼
 vendor kit (installed, ignored) ─► Blender recipes (donor cleanup / new pieces on kit trim sheets)
      │                                   │  Tools/blender/env_derive.py  →  Derived/ENV/Meshes/*.fbx
      ▼                                   ▼
 Unity: 1 Generate Materials → 2 Build Modules → 3 Build Library → 4 Build Street Demos → 5 Validate
      │     palettes/textures      prefabs+colliders    units+previews     scenes+probe        report
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

## Where things live

| What | Path |
| --- | --- |
| Grammar data (palettes, material recipes, module policy, validator policy) | `Unity/JuegoDef/Assets/JuegoDef/Env/Grammar/*.json` |
| Unit library request + street specs | `Unity/JuegoDef/Assets/JuegoDef/Env/Specs/units.json`, `Env/Specs/streets/*.json` |
| Factory code (Editor only) | `Unity/JuegoDef/Assets/JuegoDef/Editor/Env/` (`EnvKit`, `FacadeGrammar`, `BuildingAssembler`, `EnvTemplates`, `EnvStreet`, `EnvMaterials`, `EnvModules`, `EnvLibrary`, `EnvValidator`, `EnvImportRules`, `EnvPreview`) |
| Route probe (dev runtime) | `Unity/JuegoDef/Assets/JuegoDef/Runtime/Dev/JDRouteProbe.cs` |
| Blender derivation recipes | `Tools/blender/env_derive.py` (reads the vault `.blend`, never writes it) |
| Owned outputs (with lineage) | `Unity/JuegoDef/Assets/JuegoDef/Derived/ENV/{Meshes,Modules,Materials,Textures,Units}` |
| Demo/test street scenes | `Unity/JuegoDef/Assets/JuegoDef/Scenes/ENV/` |
| District specs (authored trace + generated spec) | `Unity/JuegoDef/Assets/JuegoDef/Env/Specs/districts/` |
| District tools | `Tools/env_morphology.py` (street study), `Tools/env_district.py` (district metrics, IGN DEM), `Tools/env_district_skeleton.py` (trace → spec), `Tools/env_textures.py` (painted tileable textures) |
| Composition rules | [`ENV_COMPOSITION_RULES.md`](ENV_COMPOSITION_RULES.md) |
| Searchable indexes | `Docs/asset_catalog/env_library.json`, `env_derive_manifest.json`, `lineage.json` |

## Run it (clean clone or after a change)

```powershell
python Tools/asset_catalog.py install --pack medieval   # plus props, nature (vault C:/Juego2-Assets)
blender -b --factory-startup --python Tools/blender/env_derive.py      # only if a recipe changed; add -- --only NAME
```

Unity menu `JuegoDef > ENV`: **1 Generate Materials → 2 Build Modules → 3 Build Library → 4 Build Street Demos → 5 Validate** (and **6 Validator Self-Test** after touching the validator). Then:

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

Then `JuegoDef > ENV > 7 Build District (CASCO)` (or `EnvDistrict.Begin(id)`, `BuildRows(from, count)`…, `Finish()`
from the operator). The generated scene (~95 MB) and its ground meshes are not committed; rebuild them from the spec.

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

### Templates (`EnvTemplates`)

`StreetGround` (kerbed carriageway + pavements, or pedestrian single level with drainage channel), `QuayEdge` (public quay wall/coping/bollards/ladder/guard rail/water), `YardBoundary` (controlled work yard palisade + closed gate), `SteppedConnector` (1–3 m rise cut into a terrace with retaining walls and rails), `ShopInterior`, `LodgingVestibule`, `Cluster` (data list of props).

### Threshold interface

Every ground-floor door/gate carries an empty `THR_*` marker on its clear passage centre, forward = out to the street: `THR_Public_Shop`, `THR_Public_Portal` (walkable), `THR_*_Closed` (leaf shut), `THR_Service_Closed` (must never be a public shortcut). Routes, validators and later interaction/NPC work use these instead of guessing coordinates.

### Street spec (`Env/Specs/streets/*.json`)

`length`, `width`, `ground` (`kerbed`/`pedestrian`), `rows.south|north` = ordered list of `{ "unit": "<library id>", ...overrides }` or `{ "gap": metres }`, `ends` (open/hidden), `templates` (`kind`/`unit` + `at` + `rotY` + `params`), `spawn`, `route`. The assembler resolves party walls (shared storeys build no side walls), one quoin column per shared edge, verges/gables only where the roof end is open, datum on the pavement, a baked reflection probe, the GC2 player and a disabled `RouteProbe`.

## Routine recipes

- **New building variant:** add a `units.json` entry (`type`, `bays`, `floors`, `palette`, optional `rows`) → steps 3–5. No code.
- **New street:** new spec in `Env/Specs/streets/` referencing library ids → step 4, enable `RouteProbe`, Play, read `JD_ROUTE` lines.
- **New derived piece:** add a `@recipe` in `env_derive.py` (donor via `donor()`/`clean_*()` or new geometry on kit trim-sheet bands via `box(..., uv="band")`), run it, add a collider policy if not mesh, reference it from a bay code/template → steps 2–5 + lineage.
- **New source prop:** add a wrapper to `modules.json` (collider + owned `ENV_Src_*` material with declared `sources`) → steps 1–2.

## Validation (`JuegoDef > ENV > 5 Validate`, report `Docs/evidence/WP-PROD-ENV-01/VALIDATION.json`)

Units and street scenes are checked for: banned kit modules (medieval/alpine cues, `Env/Grammar/validation.json`); missing materials or machine-local vendor materials; Unity primitives or `Proxy`/`Greybox` objects; facade bays without collision; open thresholds blocked for the **real GC2 capsule** (radius 0.2 + skin 0.08, height 2.0; sills ≤ 0.1 m allowed) and closed/service thresholds that are actually open; buildings not sitting on the street surface; duplicated coplanar tiles. `6 Validator Self-Test` seeds one defect of each class and must report `missed=0`. Python `env_catalog.py check` covers B0 demand coverage, library/preview/prefab presence, recipe↔mesh parity and lineage completeness.

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

## Current limits (see `Docs/evidence/WP-PROD-ENV-01/B0_COVERAGE.md`)

Two wall families only (render, rubble stone) — no post-1960 infill block; no hipped roofs or trapezoid corner
buildings (corners are rectangles with ashlar quoins or chamfers); lighting/sky/water are placeholders. Slopes,
stairs, terraces, river walls, bridges and districts are now covered (district builder). Remaining items are content
breadth, not missing pipeline.

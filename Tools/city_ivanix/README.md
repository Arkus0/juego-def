# city_ivanix — town on the Ivanix88 layout, ENV01 architecture

Pipeline that turns the observable urban composition of the *Medieval City Pack Demo* layout (Ivanix88; public
commercial-use permission, see `provenance/`) into a Cantabrian-Asturian port town built with our own ENV01 kit.

Rule: **Ivanix decides the urban composition · ENV01 decides the architecture · gameplay decides the interiors.**

## Steps

| Step | Tool | Output |
|---|---|---|
| 1. Trace the layout from the calibrated top capture (water, island, paving, yards, gardens, towers, wall, roofs) | `tools/trace_layout.py` | `reconstruction/layout_trace_v1.json` |
| 2. Street plan: streets, rings and squares authored over the layout's open corridors (level design decision) | `tools/street_plan.py` | `reconstruction/street_plan_v1.json` |
| 3. Seed v4: admitted footprints, programme (large interiors), parcel pass (frontage on streets, party walls, kit bays scaled to the plot, tapias), one way in per building, El Alto terraces, Torre, Finca, paseo maritimo on the XV wall, antepuerto and pier, bridges, south bank | `tools/city_seed_v4.py` (uses `open_space_streets.py`, `frontage_lines.py`) | `reconstruction/city_seed_v4.json` |
| 4. Props: the fountain first, market stalls, plaza, paseo, port, doorsteps, terraces, cars, containers, finca palms | `tools/city_props_v1.py` | `reconstruction/city_props_v1.json` |
| 5. Paving as laid by hand (12.5 cm class map: main-street flags through junctions, fans at mouths, plaza ring and bands, tree pits) | `tools/paving_map.py` | `City/Ground/CITY_PavingMap.png`, `reconstruction/paving_map_v1.json` |
| 6. Own props (Dreamcast+ style guide `Docs/design/CITY_STYLE_DCPLUS.md`): painted textures, then the Blender builds | `tools/{props,vehicle,ground}_textures.py`, `blender/build_{vehicles,street,nature}.py` | `City/Props/{Textures,Meshes}`, `City/Ground/TX_*` |
| 7. Unity (menu `JuegoDef/CITY/...`), in order: props library; seed scenes; dress (every prop an entity: `CityEntities`); shopfronts; DC export → `tools/dc_textures.py` → DC convert; paving; NavMesh probe; semantic + overlap audit | `Editor/City/{CityPropsLibrary,CityIvanixSeed,CityIvanixDress,CityShopfronts,CityDcPlus,CityPaving,CityIvanixNav,CityIvanixLint}.cs` | `Scenes/CITY_IVX/*`, `Docs/evidence/WP-CITY-IVX-00/{DRESS_ENTITIES,NAV_PROBE,LINT}.json` |

Steps 3–4 are deterministic: rerunning them reproduces the committed JSON byte for byte. The seeders are one-shot;
once the Owner accepts the layout the scenes become the authority and are edited by hand.

## Frozen (WP-CITY-IVX-HUMAN-01, 2026-10-03)

The `Scenes/CITY_IVX/*.unity` scenes and `CITY_IVX_NavMesh.asset` are versioned in git LFS and are the town's only
authority. The town is authored by hand from here on, one slice at a time (`Docs/workpacks/WP-CITY-IVX-HUMAN-01.md`).
`CityIvanixSeed.Seed`, `CityIvanixDress.Dress` and `CityShopfronts.Apply` refuse to run (`JD_CITY_IVX_FROZEN`), even
after the scenes are deleted; deleting a scene to reseed it is forbidden. The seed/props/signs JSON above is history,
not authority. Still usable as checks or look passes: `CityIvanixLint.Run`, `CityIvanixNav.BakeAndProbe`,
`CityEntities` (`Settle`, `Resolve`, `InsidePlan`), `CityDcPlus.Export/Convert`, `CityPaving.Apply`.

## Captures

The layout captures are **not** redistributed. Tools that draw over them (`trace_layout.py`, review images) read
`JD_IVX_REFS` (default `references/` next to `tools/`, git-ignored). Seeds and props need only the JSON here.

## Metrics (seed v4)

268 buildings, 60 % semantic buildings accessible, 0 footprint overlaps, neighbours on a street tramo differ by
4° (p50) / 14° (p90); NavMesh 18/18 anchor paths complete; semantic + overlap audit (`CityIvanixLint`) clean.

## Rules the pass enforces (owner walks 2026-10-02)

- one way in per building; consolidated programmes keep the door on their main cell;
- tapias only between two facades of the same tramo, with a yard behind; never across a stair, landing or gate;
- stairs need an open arrival above and a landing below; paseo furniture stays off landings;
- ground by meaning: granite flags (Calle Mayor, Muelle), setts (Plaza Mayor), river cobbles (streets), old cobbles
  (lanes, El Alto), grey setts (quay), earth (yards), meadow and huerta outside; no stray patches;
- building bases reach the lowest ground under the whole plan and sink 0.3 m;
- doorstep props stand clear of the real facade face (walls and rejas stand up to 0.85 m proud of the plot line);
- every object is an entity: seated on its own footprint, pushed out of what it touches (facades, railings, parapets,
  other objects, the solid plan of each building) by at most a short shift and on the same level, or not placed; a
  tree that does not fit is planted younger; boats are moored to the nearest bollards;
- paving changes run along hand-laid lines with a granite band at every joint; never on a straight bisector.

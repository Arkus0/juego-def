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
| 4. Props: market, plaza, paseo, port, doorsteps, terraces | `tools/city_props_v1.py` | `reconstruction/city_props_v1.json` |
| 5. Unity (editor menu `JuegoDef/CITY/...`): seed scenes, dress (light + props), afternoon look, NavMesh probe | `Editor/City/CityIvanix{Seed,Dress,Look,Nav}.cs` | `Scenes/CITY_IVX/*`, `Docs/evidence/WP-CITY-IVX-00/NAV_PROBE.json` |

Steps 3–4 are deterministic: rerunning them reproduces the committed JSON byte for byte. The seeders are one-shot;
once the Owner accepts the layout the scenes become the authority and are edited by hand.

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
- doorstep props stand clear of the real facade face (walls and rejas stand up to 0.85 m proud of the plot line).

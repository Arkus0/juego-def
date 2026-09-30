# STREET_A - Espina (east): micro-polish pass 1

Unit: `Espina_E`, main commercial street, 52 m along its centreline, 6.0-7.1 m between facades, 14 buildings
(rows `K4_0` right, `K7_6` left, `K7_7` east tip). The player spawns at its east end.
Owner brief (2026-09-29): walk it street by street, building by building; keep what works, correct what is wrong,
look at it from more angles before touching anything doubtful; then also judge **semantics** (an object can be well
built and still make no sense to a person).

## How it was walked

`EnvWalk` (Editor tool, `Unity/JuegoDef/Assets/JuegoDef/Editor/Env/EnvWalk.cs`), stations every 8 m, both directions:
the real GC2 third-person camera (pivot = capsule centre + 1 m lift, radius 3 m, shoulder 0.5 m, FOV 55, Player
mannequin as scale, camera pulled in against walls), eye level, 55 degree diagonals at each facade, raised views and a
ground-facing scan; then every building from the street (front, both obliques, looking up at the eaves, aerial, sides
and back where an end is exposed). Objective checks: `EnvWalk.Audit` (floating / sunk / overlapping / inside-wall
props), `GroundSeams`, `WallGaps`, hole pixels with a magenta background (`Tools/env_holes.py`), lateral clearance per
station (5.9-7.1 m facade to facade, comfortable for the third-person camera; nothing pinches).

## Findings and what was done

| # | Class | Finding | Action | Evidence |
|---|---|---|---|---|
| 1 | P0 | Hairline cracks in the ground (the sky shows through) along zone borders: zones are triangulated separately and met with vertices 2-6 cm apart; 3,575 of 19,995 ground triangles were collapsed slivers | `BuildGround` welds vertices closer than 7.5 cm in 3D (curb steps, >= 15 cm, are kept) and drops collapsed triangles | `weld_crack_before_after_magenta.jpg` |
| 2 | P0 | Slit at the foot of a wall (K7_6_2): the spec's `basement` is the measured ground drop, and below 5 cm no base is built; a 3 cm dip left a gap under the wall | every facade gets a 10 cm footing (`FootingMargin`) | `pairs_ground_holes_magenta.jpg` |
| 3 | P3 | "Repair patches" were relabelled ground triangles: grey wedges with no cobble detail and crooked edges | replaced by `RepairStrips`: straight utility-trench strips (old setts or concrete), texture aligned to the strip | `pairs_paving_patches.jpg`, `repair_strip_and_facade_flags.jpg` |
| 4 | P3 | **All four `PavingOverlays` meshes (setts channel in lanes, flag bands along facades, and the new strips) faced down and were culled: they had never rendered.** The owner-audit paving rule "the stone meets the house on a flag" existed on paper only | winding fixed in `OverlayMesh`; the bands and the lane channel are now visible | `repair_strip_and_facade_flags.jpg`, `walk_after_*` |
| 5 | SEM | The chalkboard of the bakery on the plaza corner (K9_0_2) stood wedged, edge-on, between two piers, half hidden | moved in front of the display window through the polish file | `sem_aframe_*` |
| 6 | SEM | **Every** business with a board got the restaurant "MENU DEL DIA" (bakeries, souvenir shops...) | boards follow the business (`boardNotice` in `businesses.json`: bars/cider houses "pinchos", cafes "menu", bakery "pan del dia", souvenirs "de la tierra"); two new notices | `sem_aframe_after.jpg` |
| 7 | P1 (probe) | The route probe stalled at Cimavilla_Baja: it walked a straight chord across a sharp bend where a stone bench (against the wall) and a chair sit on the inside. A person walks the centreline, which is clear (props 1.5 m from the vertex); the lane is passable | the probe now goes through the street vertices (`DensifyRoute`, 139 -> 158 waypoints) | `alley_b_cimavilla_bend.jpg` |
| - | - | Buildings: front, obliques and eaves of all 14 look coherent (facade families, corner quoins, canecillos, lit interiors); no floating or clipping | **kept as is** | `walk_*`, building sheets in `Captures/` |

Ruled out: the "floating boxwood" is planted in a glazed pot on the ground; the balcony planters "inside" the balcony iron are intended (the audit's false positives).

## Numbers

| Check | Before | After |
|---|---|---|
| Hole pixels (magenta), 55 ground-facing frames | 785 | **0** |
| Ground triangles / internal seams | 19,995 / 578 (1,771 m) | 16,420 / 474 (1,684 m); remaining ones are T-junctions that no longer show |
| Overlays visible | 0 of 4 | 4 of 4 (34 repair strips in the district) |
| Objects in the district root | 69,595 | 71,451 (footings, polish group) |
| `EnvValidator` | 0 problems | 0 problems (renderers 27,451 -> 28,580), self-test intact |
| Route probe (Play Mode, real GC2 player, x3 time) | 138/139 (1 stall, see #7) | **158/158, 0 stalls**, 918.9 m, console 0 errors / 0 warnings (final rebuild) |
| `EnvWalk.Audit("Espina_E")` | 12 findings (all false positives or already fixed) | 13 floor props, 0 findings |
| Full district rebuild | - | 29-33 s, deterministic (row fingerprints identical between a row rebuild and a full build) |

## Open (not fixed here, on purpose)

- **PERIM_A - the entrance looks onto a flat meadow.** Espina_E ends at the district edge on a featureless lawn with a few
  trees (`perim_a_spawn_views.jpg`): no closure for the view, and 10 m south of the spawn a **steep unwalled embankment**
  (the rear yard of `K4_0` is at y 2.0 and falls to 0.1-1.0 within a metre: a green pyramid). Needs a retaining wall or a
  softer slope and something that closes the view; it belongs to the perimeter unit, not to the street.
- Long plain plaster upper floors on `K4_0_2..4` (one window and a downpipe over ~25 m). Kept: the owner asked for fewer
  openings; a candidate for one or two quiet interventions (cable, sign, planter) after the owner's look.
- SEM checks still to do on this street with the shop fascias (which business is which) and the door thresholds.

## Repro

```text
EnvWalk.Street("Espina_E", "Captures/micro-polish/STREET_A_Espina_E/before", 8f, "game,eye,diag,up,gnd")
EnvWalk.Building("Rows/K4_0/K4_0_2", "<folder>")      EnvWalk.Audit("Espina_E")      EnvWalk.GroundSeams()
python Tools/env_sheet.py grid|pairs ...              python Tools/env_holes.py <folder>
```
Corrections that are not code live in `Env/Specs/districts/ENV01_Casco_District.polish.json` (see `EnvPolish`).

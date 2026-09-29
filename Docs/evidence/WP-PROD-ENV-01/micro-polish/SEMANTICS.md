# Semantic pass - does it make sense to a person?

Owner brief (2026-09-29): an object can be well built and still be illogical. What matters is not what a sign says but
**walls too long or that push into the street, doors that open onto the river or onto nothing, windows with no logical
place, and props with no human function.**

`EnvSemantics` (`Editor/Env/EnvSemantics.cs`) measures those on the built district and groups the findings by inspection unit
(`Env/Specs/districts/ENV01_Casco_District.inspection.json`). Run: `EnvSemantics.Run("Captures/micro-polish/semantic_audit.json")`
(4 s for the whole district). Final result: `SEM/semantic_audit_final.json`.

## What is measured

| Kind | Test |
| --- | --- |
| `DOOR_TO_RIVER`, `DOOR_TO_VOID`, `DOOR_DROP`, `DOOR_BLOCKED`, `DOOR_NOWHERE` | at every `THR_*` door: ground 0.7 and 1.5 m in front (river channel polygon, missing ground, height difference), a capsule at 1.3 m, and the distance from 2.6 m in front to the nearest street or plaza |
| `STREET_PINCH`, `STREET_SQUEEZED` | free width at chest height along every street against its nominal width, as runs |
| `WALL_LONG_RUN` | the longest garden-wall run with no gate, pier, change of height or masonry, on the built pieces |
| `BLANK_WALL`, `BLANK_UPPER_RUN` | frontage runs with no opening on any floor, or none above the ground floor (from the bay codes) |
| `WINDOW_ONTO_WALL`, `WINDOW_BURIED` | a side/back/front window with a solid within 1.3 m in front **and** in line of sight of a street; a ground-floor window below the pavement |
| `BARE_SIDE_WALL` | an exposed side wall at least two 2 m columns wide, seen from a street, with no opening anywhere on it |
| `TWIN_NEIGHBOURS`, `TWIN_REPEATED` | same bay pattern, wall and roof material next to each other, or three times in one unit |
| `PROP_ON_CENTRELINE`, `PROP_FACES_WALL`, `PROP_NO_ANCHOR` | a floor prop with no wall, door or plaza to belong to, on a street centreline, or a bench facing a wall |

## Result

| Kind | First run | Final |
| --- | --- | --- |
| Doors onto the river | 27 | 0 |
| Doors onto a void | 1 (a ray on a seam) | 0 |
| Doors buried 0.5-0.6 m by the paving | 2 | 0 |
| Doors blocked by a bridge parapet | 2 | 0 |
| Windows looking at a wall | 99 (most hidden between blocks) | 0 |
| Bare side walls | 52 | 0 |
| Long garden walls | 13 (10-37 m) | 0 runs over 10 m |
| Prop on a lane centreline | 1 | 0 |
| Door onto a lawn at the district edge (`DOOR_NOWHERE`) | 2 | 2, left to the perimeter unit |
| Narrowed streets, blank walls, twin fronts | 0 | 0 |
| **Total** | **204** | **2** |

## Causes and what changed (all in the factory or the polish file, so they survive a rebuild)

- **River houses had a door onto a 3 m drop** (all 27 houses of the river rows, type `closed_residential`, front to the water,
  entrance elsewhere): `BuildingSpec.noEntrance` for `river` rows turns door bays into (grilled) windows.
- **Bridge parapets ran up to the doors of the bridgehead houses** (a bar's glass door faced a stone parapet): `Bridge()` places no
  piece within reach of a door.
- **Doors buried by rising ground** (K11_0_1, K14_3_6: the plot floor is the lowest ground of its plot on an 8 % lane, the door is
  uphill): `BuildingSpec.raise` lifts the building to its door and grows its stone base; set in the polish file for these two.
- **Side walls were planes.** `SideCode` gave a window only to walls flagged `exposed`; a bend's concave corner had `party = 0` but
  `exposed = false` (four plain storeys onto the next street), and storeys above a lower neighbour were also plain. Now a side with no
  neighbour or storeys above one get the windows of an exposed end wall, and a **physical pass** (`EnvPolish.FixBlockedOpenings`, up to
  3 iterations, run at the start of `Finish`) gives windows to open plain walls and takes them from windows that look at another
  building within 1.3 m (walls 0.6 m apart between blocks). Footprints from the spec were tried first and dropped: rows overlap at
  bends and tips, so they gave false blocks.
- **Garden walls were one plane for 26-37 m.** `GardenWall` cuts long walls into panels of 6-9 m that alternate height and masonry
  (an older, lower or repaired stretch), each cut a huerta gate or a stone pier.
- **Ground cracks at entrances**: the wedge between the paving and the lawn beside the spawn door was 3 cm wide and 1.2 m long. The
  ground now has an earth underlay 10 cm below it (no collider, no shadow) so any crack reads as soil between stones.
- **Chair on the centreline** (Cimavilla_Baja bend): moved beside the bench (polish file).

## Judged and kept

- A pot, bucket or stool beside a **closed** door is life, not an obstruction (the audit ignores everyday props there).
- A door at the foot of a stair (a tread within 0.5 m of the sill) is a door on a landing.
- `DOOR_NOWHERE` x2 (`K2_13_0`, `K13_5_0`): houses at the district edge open onto a paved apron and then the lawn; they belong to the
  perimeter unit with the flat meadow and the unwalled embankment.

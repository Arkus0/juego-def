# Route probes — Play Mode walkability (GC2 player, real CharacterController)

Probe: `Assets/JuegoDef/Runtime/Dev/JDRouteProbe.cs` (dev-only, disabled `RouteProbe` object created by the street assembler). It drives the bootstrap GC2 `Player` (`CharacterController` radius 0.2, height 2.0, step 0.3) with `Motion.MoveToLocation`, logs `REACHED` / `STUCK` / `TIMEOUT` / `ABORTED` per waypoint with the colliders in front, and teleports past a failure so one defect cannot hide the rest. Unity 6000.3.24f1, `runInBackground = true`.

## Final runs (candidate geometry)

### `ENV01_DemoA_Commercial_To_Quay` — 12/12, 0 stalls

```text
JD_ROUTE START waypoints=12 at=(3,00,1,09,4,00)
JD_ROUTE wp=0 REACHED t=4,4s at=(19,59,1,09,4,00)      street
JD_ROUTE wp=1 REACHED t=5,1s at=(39,34,1,09,4,00)      street end
JD_ROUTE wp=2 REACHED t=1,8s at=(45,53,1,09,4,00)      onto the public quay
JD_ROUTE wp=3 REACHED t=1,2s at=(45,94,1,09,7,91)      along the guard rail
JD_ROUTE wp=4 REACHED t=4,2s at=(30,47,1,09,4,11)      back up the street
JD_ROUTE wp=5 REACHED t=1,8s at=(25,14,1,24,1,19)      kerb step onto the pavement (+0.15)
JD_ROUTE wp=6 REACHED t=1,8s at=(24,80,1,25,-0,90)     through the open shop door into the shop
JD_ROUTE wp=7 REACHED t=1,8s at=(24,80,1,24,0,49)      back out
JD_ROUTE wp=8 REACHED t=5,2s at=(5,18,1,24,0,99)       lodging portal
JD_ROUTE wp=9 REACHED t=1,2s at=(4,84,1,25,-2,62)      into the vestibule
JD_ROUTE wp=10 REACHED t=1,0s at=(4,81,1,24,0,52)      back out
JD_ROUTE wp=11 REACHED t=1,0s at=(3,32,1,09,3,38)      down to the carriageway
JD_ROUTE END reached=12/12 stalls=0 walked=101,8m time=30,7s
```

### `ENV01_DemoB_Upper_Lane` — 8/8, 0 stalls

```text
JD_ROUTE START waypoints=8 at=(2,00,1,09,3,00)
JD_ROUTE wp=0 REACHED t=3,2s at=(13,65,1,09,3,00)
JD_ROUTE wp=1 REACHED t=3,2s at=(25,51,1,09,3,00)
JD_ROUTE wp=2 REACHED t=1,4s at=(30,33,1,09,3,00)      landing at the foot of the stepped connector
JD_ROUTE wp=3 REACHED t=2,2s at=(37,90,4,06,3,00)      3 m climb
JD_ROUTE wp=4 REACHED t=0,8s at=(40,32,4,09,3,00)      upper terrace
JD_ROUTE wp=5 REACHED t=0,4s at=(39,25,4,09,3,00)
JD_ROUTE wp=6 REACHED t=2,5s at=(31,14,1,09,3,00)      back down
JD_ROUTE wp=7 REACHED t=7,4s at=(2,45,1,09,3,00)
JD_ROUTE END reached=8/8 stalls=0 walked=77,6m time=21,2s
```

## Defects the probe found (and where each was fixed)

| Run | Symptom | Cause | Fix (at the source, not in the scene) |
| --- | --- | --- | --- |
| 1 | Player spawned under the street | GC2 player pivot is ~1 m above its feet; spawn used ground height | `EnvStreet.BringPlayer` keeps the bootstrap offsets; probe resumes at target + 1.1 m |
| 2 | `STUCK` at the shop door; next waypoints falsely `REACHED` | open leaf swung **outwards**; waypoint on the counter; probe logged "finished short" as reached | leaf swing inverted in the Blender recipe; probe now reports `ABORTED` |
| 3 | `STUCK` at the door plane | furniture placed in the door lane; 8 cm frame sill | shop interior keeps produce away from the door axis; walkable door frames have no sill |
| 4 | `STUCK` at the door plane, nothing in front | transom at 2.02 m + 0.15 m datum vs capsule 2.0 m + 0.08 skin | walkable shop doors clear 2.22 m (`DOOR_CLEAR_H`); validator checks head height with the real capsule |
| 5 | `STUCK` leaving the shop, `blockers=none` | 0.3 m slot with no floor under the doorway (wall thickness between pavement and shop floor) | flush granite threshold slab in the shop door modules; interior floor reaches it |

The same capsule rules are now part of `EnvValidator` (open/closed thresholds) so the next building catches these without a Play run.

## CASCO district

Scene `ENV01_Casco_District` (built from `Env/Specs/districts/ENV01_Casco_District.json`), route = the authored node tour
in the trace (spine from the east, river plaza, stone bridge, north bank and El Sol, back over the bridge, Cántabra,
calle alta, Solana stairs up, Solana terrace, plazuela, San Pedro, mirador, Solana stairs down, central passage and
its stairs, spine crossing, Obispo stairs, east exit), sampled every ~6 m: 139 waypoints.

### Final run — 139/139, 0 stalls, 917 m

```text
JD_ROUTE START waypoints=139 at=(196,00,3,08,206,20)
JD_ROUTE wp=0 REACHED t=0,0s at=(196,00,3,08,206,20)
JD_ROUTE wp=1 REACHED t=1,8s at=(190,55,3,00,203,56)
JD_ROUTE wp=2 REACHED t=1,8s at=(184,89,2,91,200,82)
...
JD_ROUTE wp=137 REACHED t=1,8s at=(189,95,6,08,157,18)
JD_ROUTE wp=138 REACHED t=1,8s at=(195,45,6,08,160,65)
JD_ROUTE END reached=139/139 stalls=0 walked=916,8m time=261,7s
```

### Defects the probe found (first run) and fixes

| Symptom | Cause | Fix (at the source) |
| --- | --- | --- |
| `TIMEOUT`, player at y ≈ −1846 (wp 10, 70, 107, 108 and the Arco stairs) | the stair footprint cut out of the heightfield ground used a **square cap**, punching a hole into the junction at each end of every stair | `env_district_skeleton.py`: stair footprints use flat caps (exactly between the end nodes) |
| `STUCK` at the north bridgehead, `blockers=Cabeza_Puente/ENV_Bench_Street` | plaza dressing placed a bench on the walking line crossing a junction plaza | `EnvDistrict.DressPlaza` keeps trees, benches and the kiosk clear of every street lane crossing a plaza |

### Audit look pass (2026-09-29) — 139/139, 0 stalls, 917.5 m

Rebuilt with the look pass (facade families, businesses and their dressing, plants, door steps, plaza composition,
river life, street furniture). One stall on the run before the final one:

| Symptom | Cause | Fix (at the source) |
| --- | --- | --- |
| `STUCK wp=59 blockers=StreetFurniture/ENV_Recycling_Bins` (Plazuela Oeste) | recycling bins placed inside a small plaza on the lane that crosses it | `EnvDistrict.StreetFurniture` keeps bins off every street lane (width/2 + 1.6 m); no small plaza has room now, so none are placed |

```text
JD_ROUTE START waypoints=139 at=(196,00,3,08,206,20)
JD_ROUTE END reached=139/139 stalls=0 walked=917,5m time=263,0s
```

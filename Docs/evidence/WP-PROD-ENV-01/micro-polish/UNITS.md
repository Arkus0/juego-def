# ENV-01 CASCO - inspection units for the micro-polish pass

Generated from `Env/Specs/districts/ENV01_Casco_District.json` (38 street segments, 5 plazas, 2 bridges, 3 stairs, 164 rows, 311 buildings). A unit is walked end to end, in both directions, with the `EnvWalk` views before moving to the next; each pass has a technical part (P0-P5) and a semantic part (SEM: does it make sense to a person?). Status: `pending`, `pass 1 done` (walked, fixed, evidence here), `reviewed` (after the owner's look).

**Pass 2 (2026-09-29) closed every unit below** — see `pass2/PASS2.md` for the per-unit findings, the factory fixes and the false positives. Only the two PERIM units stay open (inherited from pass 1: the flat beige ground and the unwalled embankment behind K4_0 at the east entrance), plus the deferred route probe and the final HUMAN LOGIC WALK.

| ID | Unit | Role | Spec segments | Length m | Width m | Height change m | Buildings | Status | Notes |
|---|---|---|---|---:|---:|---:|---:|---|---|
| STREET_A | Espina (east) | main | Espina_E | 58 | 6.2 | -0.8 | 14 | pass 2: audit 0 findings | main commercial street; the player's entrance |
| STREET_B | Espina (plaza and node) | main | Espina_Plaza, Espina_Nodo | 61 | 6.5 | -0.8 | 6 | pass 2 done | terraces now only outside bars/cafés/sidrerías; 6 buildings inspected |
| STREET_C | Subida al puente | main | Subida_Puente | 24 | 6 | -0.2 | 4 | pass 2 done | chalkboard/barrel fix at the bridgehead |
| STREET_D | Cantabra | secondary | Cantabra | 58 | 4.5 | +0.6 | 16 | pass 2 done | chalkboard out of a terrace table |
| STREET_E | Calle Alta | secondary | Calle_Alta_O, Calle_Alta_C, Calle_Alta_C2, Calle_Alta_E, Calle_Alta_Salida | 159 | 4.4-4.6 | +1.3 | 38 | pass 2 done | stone bench removed from a portal doorway; K15_5_1 pinned to a taller (breaks the cloned ground floor) |
| STREET_F | Obispo | secondary | Obispo_Bajo, Obispo_Escalera | 57 | 3.2-4.2 | +3.8 | 12 | pass 2 done | |
| STREET_G | Ribera | secondary | Ribera | 80 | 4.4 | -3.6 | 18 | pass 2 done | east half opens onto the perimeter meadow (edge condition, accepted) |
| STREET_H | Capitan | secondary | Capitan, Capitan_Salida | 63 | 4.6 | -2.7 | 14 | pass 2 done | |
| STREET_I | San Pedro | secondary | San_Pedro, San_Pedro_Salida | 121 | 4.2 | +6.0 | 12 | pass 2 done | |
| ALLEY_A | Callejon Oeste | lane | Callejon_Oeste, Callejon_Oeste_Salida | 40 | 3.6 | +0.3 | 9 | pass 2 done |  |
| ALLEY_B | Cimavilla Baja | lane | Cimavilla_Baja | 24 | 3.8 | +2.7 | 7 | pass 1 + 2 verified | hero lane (everyday life) |
| ALLEY_C | Callejon del Arco | lane | Callejon_Arco, Arco_Escalera | 59 | 3-3.4 | +3.3 | 11 | pass 2 done | hero lane plus stairs |
| ALLEY_D | El Sol | lane | El_Sol | 46 | 3.8 | +0.0 | 9 | pass 2 done |  |
| ALLEY_E | Cervantes | lane | Cervantes | 51 | 4 | -2.4 | 9 | pass 2 done |  |
| ALLEY_F | Independencia | lane | Independencia | 46 | 4 | -2.3 | 8 | pass 2 done |  |
| ALLEY_G | La Solana | lane | Solana_Acceso, Solana_Escalera, Solana_Terraza, Solana_Bajada, Solana_Baja | 118 | 3-3.8 | +4.8 | 24 | pass 2 done | |
| ALLEY_H | Mirador | lane | Subida_Mirador, Ronda_Mirador | 83 | 3.6 | +0.2 | 17 | pass 2 done |  |
| ALLEY_I | Ronda de Huertas | lane | Ronda_Huertas | 116 | 3.8 | -3.4 | 14 | pass 2 done | rural edge |
| ALLEY_J | Llano | lane | Llano | 70 | 4 | -5.8 | 14 | pass 2 done |  |
| ALLEY_K | Fuente | lane | Fuente, Fuente_Baja | 62 | 3.4 | +3.3 | 15 | pass 2 done | hero lanes by the fountain |

Buildings on streets: 271. The rest (plaza and river rows, and the two bridge segments) are in the units below.

## Spaces that are not streets

| ID | Unit | Content | Status |
|---|---|---|---|
| PLAZA_A | Plaza_Rio | river plaza (main breathing space; tower, bar terrace, parapet over the water, stair down to the river) | pass 2 done |
| PLAZA_B | Plazuela_Fuente | calle alta widening with a fountain | pass 2 done |
| PLAZA_C | Mirador | upper mirador | pass 2 done |
| PLAZA_D | Cabeza_Puente | north bridgehead | pass 2 done |
| PLAZA_E | Plazuela_Oeste | small triangle at the west junction | pass 2 done |
| RIVER_A | River and channel | channel, channel walls (92 pieces), parapets, river stair, riverside walk, rocks, bed | pass 2 done |
| BRIDGE_A | Stone bridge | Puente_Piedra + arch (2 buildings on the bridge rows) | pass 2 done (walked both directions) |
| BRIDGE_B | Footbridge | Pasarela (2.6 m) | pass 2 done (walked both directions; sunk barrel lifted) |
| YARDS_A | Yards, orchards and orchard walls | 35 orchard walls + `yard`/`huerta` ground behind the rows | pass 2 done (square piers on every wall cut) |
| PERIM_A | East edge (the player's entrance) | flat meadow beside Espina_E; steep embankment without a wall behind K4_0 | **open findings** (inherited; see PASS2.md) |
| PERIM_B | South, west and north edge | outer ring, backdrop (1,023 trees), distant range | pass 2 done (backdrop reads well; PERIM_A items sit on the east edge) |

Check: 36 of 38 spec segments assigned to a street unit; the other two are the bridges.


## District-wide passes already applied to every unit

The semantic audit (`SEMANTICS.md`) ran over all units at once: 204 findings -> 2 (the two doors at the district edge belong to PERIM_A/B). Ground welding, the earth underlay, footing, overlays and repair strips (see `STREET_A_Espina_E.md`) are district-wide too. What is left per unit is the walk with the game camera, the building-by-building look for what a measurement cannot judge (proportion, repetition, local composition, props that need a decision) and the ground.

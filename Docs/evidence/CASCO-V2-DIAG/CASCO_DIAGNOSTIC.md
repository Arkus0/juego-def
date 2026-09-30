# CASCO_DIAGNOSTIC — diagnóstico mecánico del CASCO actual (ENV01)

**Qué es:** inventario geométrico verificable y reproducible del CASCO construido, como
input de datos para un futuro CASCO-V2. **Qué NO es:** no rediseña el urbanismo, no
elige agrupaciones, no decide usos, no crea interiores, no interpreta "mejor diseño".
Los "candidatos" de agrupación son filas de datos geométricos, nada más.

Generado por `Tools/casco_diagnostic.py` (read-only sobre el spec; nunca toca escena,
spec ni trace). Todo umbral es una heurística explícita y parametrizable del config;
ninguna es verdad de producto.

## 1. Inputs congelados (manifest completo en `casco_diagnostic.json.inputs`)

| input | SHA256 (primeros 16) |
|---|---|
| `ENV01_Casco_District.json` (spec autoritativo) | ver `inputs.spec.sha256` |
| `units.json` | ver `inputs.units.sha256` |
| `ENV01_Casco_District.polish.json` | ver `inputs.polish.sha256` |
| `Tools/casco_diagnostic.config.json` | ver `inputs.config.sha256` |
| escena commitada `ENV01_Casco_District.unity` (crosscheck) | `41e2cefdc4c3d0bb…` |

Base mecánica: `EnvDistrict.BuildRows` (colocación), `BuildingAssembler.Build`
(footprint, `Storey=3 m`), `EnvStreet.ResolveNeighbours` (party walls), `GardenWall`
(muros), `Tools/env_district_skeleton.py` (buffers de calle). Detalle de convenciones
en la cabecera del tool.

## 2. Verificación mecánica (Reviewer puede repetir cada número)

- **Checks del tool** (`checks` en el JSON): buildings 311 = `report.plots` ✓; walls
  35 = `report.walls` ✓; área rect == `w×depth` en los 311 ✓; pares consecutivos de
  fila se tocan (0 violaciones) ✓; suma de clases == 46.256,00 m² del dominio con
  error 0,0 m² ✓.
- **Cross-check contra la escena commitada** (`scene_crosscheck.json`): 27/27
  edificios muestreados (20 filas, 14 calles, incluye Torre-unit, casona landmark,
  los 3 plots con polish `raise`/`floors`, el más ancho y el más estrecho) reproducen
  posición local, escala, posición de frame, yaw de frame, linkage padre-hijo y las
  **4 esquinas del footprint** con delta máximo **0,497 mm**. La escena contiene
  exactamente 475 GameObjects con nombre K* = 164 frames + 311 edificios.
- **Determinismo**: dos ejecuciones producen los 4 archivos byte-idénticos
  (SHA256 en `REPRODUCE.md`).

## 3. Heurísticas explícitas (defaults del config; NO verdad de producto)

| parámetro | default | base |
|---|---|---|
| `min_interior_footprint_m2` | 24,0 | ≈2 bays × depth 6; no existe umbral autoritativo de interior jugable (ambigüedad A1) |
| `min_interior_frontage_m` | 4,0 | 2 bays del kit de 2 m |
| `narrow_plot_max_w_m` | 4,6 | ≈ bays ≤ 2 con escala ≤ 1,14 |
| `adjacency_tol_m` | 0,05 | precisión del generador |
| `absorb_buffer_m` | 1,5 | radio de absorción de residual por candidato |
| `back_clearance_m` | 1,6 | regla `blockBack` existente (1,6 m) |
| `candidate_sizes` | 2..6 | brief del Owner |
| `candidate_mode` | `same_row` | "frontage combinado" ⇒ un solo frente (ambigüedad A4) |
| prioridad de clasificación | building > wall > street > plaza > water > ground deliberado > residual | orden declarado |

## 4. Inventario global

164 filas (roles: lane 70, secondary 54, river 12, plaza 10, main 8, bridge 5,
steps 4, footbridge 1) · **311 edificios** + **35 muros de jardín** · 1 plot-unit
(Torre) · 2 landmarks · 6 casonas · **81 plots sin respaldo OSM real** (`real:false`,
creados por el generador) · 311/311 con portal asumido salvo filas río
(`noEntrance`, 27 en filas river según regla, ver `plots.csv`).

## 5. Distribuciones (311 edificios)

| métrica | min | p10 | p50 | p90 | max | media |
|---|---|---|---|---|---|---|
| frontage (m) | 1,85 | 3,91 | **6,76** | 10,13 | 16,41 | 7,03 |
| footprint (m²) | 9,04 | 23,53 | **47,49** | 78,26 | 109,55 | 48,50 |

- bays (2 m): 1→3, 2→67, 3→94, 4→90, 5→38, 6→15, 7→4
- depth: 4 m→35, 6 m→113, 8 m→163
- floors: 2→82, 3→162, 4→66, 6→1 (con unit/polish aplicados)
- distancia al edificio en frente (cruza calle): p50 **4,09 m**, p90 8,49 m, max 23,6 m
- distancia al vecino trasero (otra fila): 207/307 tocando o a <1 m (p50 = 0,0 m)

Celdas de fachada actuales del casco: **9.816** totales (3.190 de frente).

## 6. Superficie clasificada (dominio 196×236 = 46.256 m²)

| clase | m² | % |
|---|---|---|
| edificio | 14.253,8 | 30,8 % |
| calle (buffers del generador + puentes/escaleras) | 5.662,3 | 12,2 % |
| plaza | 1.521,1 | 3,3 % |
| agua (canal) | 1.094,6 | 2,4 % |
| ground deliberado (yard+huerta) | 21.327,6 | 46,1 % |
| muro ( strips 0,6 m) | 226,5 | 0,5 % |
| **residual (no clasificado)** | **2.170,1** | **4,7 %** |

Solapes crudos de interés (pre-prioridad): plaza∩calle 335,6 · edificio∩calle 129,7 ·
ground deliberado∩edificio 182,4 · calle∩agua 70,2 (pasos de puente) · edificio∩agua 16,1.
Referencia informativa: el estudio Potes marca 41 % de edificación en su box.

## 7. Hallazgos mecánicos (flags automáticos, dependen del config)

- **35 edificios** con footprint < 24 m² y **38** con frontage < 4,0 m
  (intersecan en parte; 3 edificios de 1 bay ≈ 1,85–2,2 m son el extremo).
- **69 edificios** "estrechos" (w ≤ 4,6 m) que aún superan algún mínimo.
- **26 edificios** con hueco trasero de 0,05–1,6 m (hendidura entre espaldas que no
  es calle ni patio; exactamente el rango que la regla `blockBack` prohíbe ventilar).
- **14 edificios** con edificio en frente a < 2 m (esquinas de manzana/envolventes).
- **23 filas con tramo sin construir** (sin plots ni filler): 165,7 m de frente total.
- **Residual**: 129 componentes > 0,05 m² (2.170 m²); 71 componentes ≥ 2 m²
  (2.125 m²); los 3 mayores son 571,9 / 230,4 / 97,8 m². 65 componentes (406 m²)
  son slivers pegados a líneas de fila (posible frente no construido, heurístico).

## 8. Candidatos de agrupación (SOLO DATOS)

Definición exacta: toda corrida contigua de 2–6 edificios en la misma fila, sin muro
ni hueco de x0 entre medios (contigüidad medida, no asumida: 0 violaciones).
**342 candidatos**: tamaño 2→166, 3→87, 4→51, 5→25, 6→13. 49 contienen algún
miembro flaggeado; 5 contienen landmark (Torre/casona); detalle completo en
`stats.json.candidates`.

Por candidato (columnas en `candidates.csv`): IDs, frontage combinado, depth
min/max, footprint sumado y de unión/hull, floors min/max, **celdas de fachada
preservables** (frentes + traseras + laterales que sobreviven: los internos al grupo
desaparecen; extremos según party real vía port de `Shared`/ends), celdas actuales,
accesos existentes (`entrances_assumed` deriva de `noEntrance` — ambigüedad A7;
interiores programados, chaflanes, units), residual absorbible ≤1,5 m,
conflictos: solape de la unión con calle/plaza/agua (138/0/23 candidatos con
>0,05 m²; máximos 14,2 y 8,9 m² — esquinas de manzana y filas río) y back_flag
(204 tocando, 47 con hueco <1,6 m, 91 despejados).

Ejemplos ilustrativos (las 3 corridas-6 con más frontage + la que contiene la
casona; **ejemplos de filas del CSV, no una selección ni una recomendación**):

| candidato | miembros | frontage | depth | footprint | celdas preserv. (de actuales) | accesos | residual absorbible | back |
|---|---|---|---|---|---|---|---|---|
| K15_12_02_6 | K15_12_2…7 | 54,7 m | 6–8 | 413,4 m² | 165 (de 218) | 6 | 66,8 m² | hueco<1,6 |
| K4_0_01_6 | K4_0_1…6 | 54,2 m | 8 | 433,8 m² | 198 (de 270) | 6 | 5,3 m² | tocando |
| K16_3_00_6 | K16_3_0…5 | 53,0 m | 4–6 | 285,4 m² | 134 (de 180) | 6 | 12,5 m² | tocando |
| K14_3_00_6 | K14_3_0…5 (incl. casona) | 44,0 m | 6–8 | 339,8 m² | 142 (de 226) | 6 | 19,0 m² | tocando |

## 9. Ambigüedades registradas (NO resueltas)

- **A1** No existe umbral autoritativo de "interior jugable"; los mínimos son
  heurísticas del config.
- **A2** Zonas ground `outer/strip/lane/core/plaza` se asumen pavimento bajo
  calle/plaza; sólo `yard/huerta` son "ground deliberado".
- **A3** `report.rows` = 161 vs 164 filas del array (el report cuenta filas
  construidas); aquí se cuenta el array.
- **A4** La contigüidad espalda-con-espalda se registra como vecino `back`, pero los
  candidatos son same-row por definición de "frontage combinado".
- **A5** Los 35 muros se inventarían (grosor aproximado 0,6 m) y se excluyen de
  candidatos.
- **A6** Los tramos sin construir se reportan como dato y caen en residual.
- **A7** `entrances_assumed` deriva de `noEntrance`; no se ejecuta el grammar para
  contar portales reales.

## 10. Cumplimiento de restricciones duras

No se movió ni modificó nada de ENV01: el tool sólo lee JSONs; el overlay
`EnvCascoDiag.cs` dibuja con Handles en SceneView (cero GameObjects, cero escrituras
de escena, cero saves) y su verificación es read-only. Escena/spec/trace quedan
byte-idénticos (verificable con `git status` y los SHA del §1). Ningún output decide
usos ni diseño; toda heurística está en el config versionado.

## 11. Archivos de este paquete

- `casco_diagnostic.json` — todo (plots, vecinos, candidatos, stats, checks,
  config embebida, manifest, polígonos para overlay).
- `plots.csv` / `candidates.csv` — tablas machine-readable.
- `stats.json` — stats + checks.
- `scene_crosscheck.json` — verificación contra la escena commitada.
- `REPRODUCE.md` / `RUNBOOK_OVERLAY.md` / `README.md`.

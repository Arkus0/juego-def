# PASS 2 — micro-pulido visual + semántico del CASCO (ENV-01), sesión del 2026-09-29

Segunda pasada del bucle OBSERVAR → ENTENDER → CORREGIR → VOLVER A MIRAR, unidad por unidad,
con cámara GC2 en tercera persona (radio 3 m, lift 1, hombro 0.5, FOV 55). Continúa la PASS 1
(`../UNITS.md`, `../STREET_A_Espina_E.md`, `../SEMANTICS.md`). Las hojas de contacto de esta
sesión están en las subcarpetas de `pass2/`; las capturas crudas (más de 700) siguen en
`Captures/micro-polish/` (gitignored). Las 8 hojas `defects/_sheet_*.jpg` y `SEM/` de la
sesión anterior son el ANTES de esta pasada.

## Fábrica (sobreviven al rebuild; commit de esta sesión)

| Fix | Dónde | Evidencia |
|---|---|---|
| Relleno de huecos entre manzanas `GroundGapFill` (de la sesión anterior, compilado y verificado hoy): malla de tierra `Underlay_GapFill` (19.487 verts) en los huecos de 1 m sin suelo; excluye cauce (+1,2 m), escaleras/puentes (+margen) y escaleras de río (+4 m); alturas relajadas desde el terreno vecino. `OpenAirHoles`: 43 celdas abiertas, 42 cubiertas; la restante (103.5, 205.5) está visualmente cubierta (falso positivo del chequeo por centroides de triángulo). 8 puntos SkyHoles mirados: sin cielo visible. | `EnvDistrict.GroundGapFill`, `EnvWalk.OpenAirHoles` | `gapfill/_sheet1..4.jpg` |
| Pilar de muro de huerta (v4): el corte usaba `ENV_Retaining_Wall_2x2` a escala x=0.22 (filo cruzado por su albardilla) y +0.25; ahora 0.6 m de frente, +0.45 sobre la albardilla: pilón cuadrado con su capitel. | `EnvDistrict.GardenWall` | `defects/_sheet_after.jpg` (v4_after) |
| Terraza de plaza (v5): las sombrillas miden 1,5 m de radio y estaban a 1,55 m de fachada; la copa entraba en el muro. Terraza completa a 2,05 m y radio de ocupación 1.6. | `EnvDistrict` (dressing de plazas) | `defects/_sheet_after.jpg` (v5_after) |
| Casa de río (v1): el zócalo (`Basement`) de las filas `river` se remapea al mismo tramo de mampostería de encauzamiento (`ENV_RiverWall_Canto/Mamposteria/Silleria` por el stretch de 22 m del muro) y las casas riberas garantizan sótano ≥ 0.45 m. La casa nace del muro, no de otra pared. Las juntas de sillar contra marcos quedan como limitación conocida. | `EnvDistrict.BuildRows` | `defects/_sheet_after.jpg` (v1_after + close) |
| FLAT_FACADE K6_10_1: balconera de hierro (`ENV_Balcony_Iron`) bajo la ventana oeste del piso alto. | `polish.json` op `place` | `defects/_sheet_v7balcony.jpg` (balcony_k6101) |
| STOREFRONT_GENERIC: K15_5_1 y K14_0_0 compartían planta baja D,P,R; K15_5_1 fijada a `taller` (portón de madera, F0 = D,P,G). | `polish.json` plot | `defects/_sheet_after.jpg` (sg_k1551_after) |
| Terrazas solo de hosteleros: `EnvBusiness.TypeByBuilding` registra el tipo de negocio por edificio; el dressing de plazas (10 filas plaza) ya no pone sombrilla+barriles delante de la farmacia, la zapatería o cualquier no-bar/café/sidrería. Tras el rebuild queda exactamente 1 sombrilla (el bar de K2_9_0, Bar Tito). | `EnvBusiness`, `EnvDistrict` | `streets/B_sh_terrace.jpg` |
| Compilación: `EnvWalk.OpenAirHoles` no compilaba (CS0136, `out var top` sombreaba el parámetro). Corregido a `hit`. | `EnvWalk.cs` | — |

## Ops de pulido aplicadas (todos en `ENV01_Casco_District.polish.json`, con unidad y porqué)

- ALLEY_B silla y STREET_B pizarra: ops de la PASS 1, reaplicadas por `Finish` tras cada rebuild (verificado).
- STREET_B: barril invisible dentro del stack de cajas del rincón de la miel, retirado.
- STREET_C (cabeza del puente): pizarra dentro del barril del bar → colocada a lo largo de la fachada, fuera del vano de la puerta (verificada con raycast: 0.14 m de la puerta era demasiado; posición final junto al barril, sin solape). `zooms/_board_final.jpg`.
- STREET_D (Cantabra): pizarra dentro de una mesa de terraza → deslizada junto al muro.
- STREET_E (Calle_Alta_O): banco de piedra DENTRO del portal reformado, a 0.5 m del umbral → retirado (el rincón conserva maceta, helecho y silla). `zooms/_portal_obl.jpg`.
- BRIDGE_B (pasarela): barril hundido 0.30 m en el pavimento del aterrizaje sur → levantado.

## Recorridos por unidad (cámara juego, A→B y B→A)

| Unidad | Estado | Hallazgos |
|---|---|---|
| STREET_B Espina plaza/nodo | **CERRADA** | 6 edificios inspeccionados (frontal, oblicuos, cubierta): sin P0/P1. Fix de terrazas hosteleras + barril. La cámara de edificio de K9_0_3 parece taparse con el muro K2_4: es el muro de ENFRENTE (falsa alarma). |
| STREET_C Subida al puente | **CERRADA** | Paseo fwd/rev limpio; pizarra/barril corregido; rocas a y≈-3.6 = lecho del río (intencional, `parent=Rocks`); árbol vs farola = solape de AABB (falso positivo). |
| STREET_D Cantabra | **CERRADA** | Calle de bares estrecha, creíble en ambos sentidos; flank liso de ~8 m lee como mediana (anotado, no tocado); clusters de mercado = falsos positivos del audit por AABB (barril+costal, maceta+jardinera, hortensias en jardinera). |
| STREET_E Calle Alta (5 seg) | **CERRADA** | Banco quitado del portal; resto de 42 hallazgos del audit = patrones ya conocidos (props apoyados en fachada, maceteros con planta, bicis apoyadas). El carril entre muros de contención y la salida al prado leen bien. |
| STREET_F Obispo + escalera | **CERRADA** | Pizarra/barril del Mesón La Torre: grupo apoyado, se acepta (a diferencia de la cabeza del puente, donde la pizarra estaba enterrada). Abrevadero sin suelo = bajo el vuelo del balcón (falso positivo). |
| STREET_G Ribera | **CERRADA** | Taburetes dentro de barriles = diseño barril-mesa; la mitad este abre al prado perimetral (borde, aceptado). |
| STREET_H Capitán + salida | **CERRADA** | Contenedores contra muro = falso positivo (cenital lo confirma); pizarra/barril del bar del río: grupo apoyado aceptado. |
| STREET_I San Pedro + salida | **CERRADA** | Contenedores OK; el carril entre muros de huerta con la torre al fondo es el mejor momento del distrito. |
| ALLEY_A–K | **CERRADAS** | 19 segmentos recorridos; bicicleta "NOGROUND" en el patio de la Fuente está asentada en el suelo de tierra del relleno (el patio no tiene colisionador: falso positivo); farol colgante del callejón, solanas de madera y fuentes: correctos. |
| PLAZA_A Plaza_Rio | **CERRADA** | Terraza solo del bar; parapeto sobre el agua, barca, escalera de río junto a la Farmacia. |
| PLAZA_B Plazuela_Fuente | **CERRADA** | Fuente de pared con árbol en el ensanche de Calle Alta (el centro del polígono del spec no es la fuente: está en (117.0, 118.0)). |
| PLAZA_C Mirador / PLAZA_D Cabeza_Puente / PLAZA_E Plazuela_Oeste | **CERRADAS** | Mirador con tarima de madera y banco; cabeza del puente correcta; la plazuela oeste es un triángulo mínimo de cruce (por diseño). |
| RIVER_A | **CERRADO** | Cauce, muros por tramos, escalera de río, barca y lecho rocoso leen bien desde los puentes y la plaza. |
| BRIDGE_A Puente_Piedra / BRIDGE_B Pasarela | **CERRADOS** | Recorridos completos con cámara juego: casas sobre el puente, pretiles fuera de las puertas, pasarela de tablas. Barril hundido corregido. |
| YARDS_A | **CERRADO** | Bancales arados, muros por paneles (con los pilones nuevos), caminos de losa. |
| PERIM_A / PERIM_B | **ABIERTAS (heredado)** | PERIM_A conserva su hallazgo abierto de la PASS 1 (llano beige tras la entrada este, talud sin muro tras K4_0); el anillo norte/sur/oeste y las huertas de borde leen bien. |

## Validación de esta sesión

- `EnvValidator.Validate`: **0 problemas** (escena: 372 umbrales, 0 walkable abiertos, 372 cerrados, 29.142 renderers).
- Auto-test del validador: **missed=0** (8/8 detectores).
- `WallGaps` de las **164 filas: 0 filas con hueco** muro-suelo.
- Sonda de ruta: **diferida** — arrancó (158 waypoints, alcanzó wp=13 sin atasco logueado) y el owner pidió dejarla para la siguiente sesión para retunear qué busca. No se registra resultado.
- HUMAN LOGIC WALK final: **pendiente** para la siguiente sesión (así lo pide el brief del owner).

## Limitaciones conocidas (documentadas, no tocadas)

1. Juntas de sillar que no alinean con los marcos de puerta (v1b, v6): requeriría alinear cursos por instancia en el módulo; impacto cosmético bajo a distancia de juego.
2. Persiana sobre puerta acristalada (v7, K14_3_6): lee como local cerrado (verosímil); el bloque superior de la jamba izquierda se lee ligeramente saliente — módulo, P4.
3. Flancos traseros casi ciegos con 1-2 ventanucos (v2/v3 y varios callejones): medianeras reales; se aceptan como lenguaje del casco salvo decisión del owner.
4. PERIM_A: llano beige y talud sin muro tras K4_0 (abierto desde la PASS 1).

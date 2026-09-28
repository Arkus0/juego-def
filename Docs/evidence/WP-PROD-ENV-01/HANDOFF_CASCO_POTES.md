# Handoff — Casco "mini Potes": de la Demo C a un distrito de ~180 × 220 m

Fecha: 2026-09-28. Sesión saliente: Worker WP-PROD-ENV-01 (Claude Code). Destino: nueva sesión.
Este documento sustituye al contexto del chat; léelo entero antes de tocar nada.

> **Estado 2026-09-29 (sesión siguiente):** encargo ejecutado hasta el hito 4. Las decisiones del owner (ENV-01 sigue
> abierto, caja A, río pequeño encajonado en el borde, 70/20/10, referencia como alma y no como calco, pasada de
> calidad de assets) y el resultado están en [CASCO_REFERENCE_STUDY.md](CASCO_REFERENCE_STUDY.md); las reglas en
> [`ENV_COMPOSITION_RULES.md`](../../production/ENV_COMPOSITION_RULES.md). Distrito: `Env/Specs/districts/ENV01_Casco_District*.json`,
> `JuegoDef > ENV > 7 Build District (CASCO)`; sonda 139/139; validación 0 problemas. Este documento queda como historia.

## 1. Encargo del owner para la nueva sesión

> "La demo C está genial pero hay que ahondar más en estilo visual Potes, aumentar el distrito hasta tamaño real
> (basándose en el casco histórico de Potes) a unos 180 m × 220 m. […] expandir la demo C y hacerlo más parecido
> al Potes real (e iterar una mejora de assets: están bien pero fallan aún; ya que los vamos a 'potizar', también
> se pueden mejorar)."

La Demo C es la escena `ENV01_CascoRef_Potes`, con trazado de Potes y paleta del casco. El owner la aprobó como dirección.

Objetivos:

1. **Distrito CASCO a tamaño real, unos 180 × 220 m**, con la morfología del casco histórico de Potes: red de calles, manzanas, plazas, pasos y remates de vista. Se amplía la Demo C; no se empieza de cero.
2. **Estilo visual Potes más profundo**: arquitectura lebaniega y materiales.
3. **Mejorar los assets mientras se "potizan"**: el owner los ve bien, pero todavía fallan.

## 2. Decisiones del owner vigentes (no reabrir)

| Fecha | Decisión |
| --- | --- |
| 2026-09-28 | Potes como **referencia morfológica fuerte** para el CASCO, estudiada con datos reales. Proceso: referencia → simplificación jugable → composición con nuestro kit → detalles e identidad propios. |
| 2026-09-28 | **"Mini Potes" también en la paleta, aunque el contrato diga otra cosa.** Esto contradice a sabiendas `Docs/design/PORT_TOWN_WORLD_MODEL.md` y `Docs/research/LEGACY_RESEARCH_SOURCE_INDEX.md`, que retiraron Potes como dirección de arte. Hay que registrarlo como decisión del owner y marcarlo para DocSync. |
| 2026-09-28 | **El puerto es otro distrito.** Esto es solo el casco. Tendrá una transición hacia el puerto más adelante; en la Demo C la marca una bajada que termina en un pretil. Ni muelle ni agua dentro del casco. |
| siempre | La ciudad sigue siendo un **puerto ficticio del norte de España**. Nada de nombres, rótulos ni hitos con nombre de Potes; nada de "Villa Bruma". Se usa estructura, no edificios concretos. |
| rondas 1–3 | Criterios visuales (memoria `feedback-env-visual-criteria`): pocas aberturas; como mucho **una puerta-balcón por fachada**; ventanas que **varían por planta** (p. ej. dos abajo y una arriba); **la puerta no siempre en el mismo lado**; **ninguna bajante o cable cruzando huecos**; historia/anomalías en un 10–20 %; vida (toldos, bicis, cajas, macetas, basura); jerarquía viaria; esquinas y finales compuestos; luz atlántica. |

El owner tiene la última palabra en lo visual. Hay que enseñarle capturas en cada hito.

## 3. Estado exacto de los bytes

- **Repo**: `C:\Juego Def` (`Arkus0/juego-def`).
- **Rama**: `worker/prod-env-01`.
  - `HEAD = c1bf286`: commit de control de la ronda 2, que por error se hizo sobre `main` local y ya está movido a esta rama.
  - El `main` local vuelve a apuntar a `origin/main`, que va 3 commits por delante de la base del WP (merge de ANIM-01). Antes del PR hay que mergear o rebasar desde `origin/main`.
- **Todo el trabajo de las rondas 3 y 4 está SIN COMMIT** en la working copy: unos 430 ficheros entre código, specs, derivados, escenas y evidencias.
  - Si la nueva sesión corre en otra worktree o en la nube, **no lo verá**.
  - Primer paso recomendado: commit de control en `worker/prod-env-01`.
- **Unity**:
  - Proyecto `Unity/JuegoDef`, Unity 6000.3.24f1, instancia MCP `JuegoDef@9bfcb657`.
  - Siempre `set_active_instance 9bfcb657`. Hay otros editores ("My project", el benchmark de Juego2) que no se tocan.
  - **Se quedó en Play Mode** con la escena DemoA abierta: hay que salir de Play Mode lo primero.
- **Blender**: 5.2.1 headless (`blender -b --factory-startup --python Tools/blender/env_derive.py -- [--only A,B]`).

## 4. Qué existe ya (para reutilizar)

### Fábrica ENV (Editor, `Unity/JuegoDef/Assets/JuegoDef/Editor/Env/`)

- **`EnvStreet`**, calles por spec. Tres formatos:
  - v1: una recta.
  - `segments`: tramos con `at`/`rotY`.
  - **`path`** (el de la Demo C): polilínea de ejes con un tramo por arista, cada uno con `width`, `shift`, `ground` y `rows`.

  Qué calcula `path` por sí solo:
  - **Ingletes en los quiebros.** En el lado interior, la punta de manzana (`tip_keep`/`tip_cede`: sin medianeras enfrentadas y un solo sillar). En el lado exterior, el rincón cóncavo (`concave`: sin sillares).
  - **Escalones de alineación** cuando cambia la anchura o hay desplazamiento de eje (extremos abiertos).
  - **Encaje de cada hilera** entre sus ingletes, escalando los edificios entre 0,88 y 1,14. Fuera de ese rango avisa con `ENV_ROW_FIT`.
  - **Solape de suelos**, con cada tramo 3 mm más bajo.
  - **Aviso `ENV_PATH_AXIS_SHIFT`** cada vez que el eje salta.

  Extras de las specs:
  - Plantillas relativas a un tramo (`{"segment": i, "at": [...]}`), también para `spawn` y `route`.
  - `extends` + `paletteMap` para variantes A/B.
  - Plantillas `cluster` con `parts`.
- **`FacadeGrammar` / `BuildingAssembler`**, fachadas.
  - Tipos de fachada: `mixed_commercial`, `closed_residential`, `lodging`, `warehouse`, `termination`, `landmark`.
  - Épocas: old / reformed / neglected.
  - `History`: parabólica, antena, contadores, cable, tendedero, macetas, enredaderas, bajante extra, ventana rara, repintado.
  - **Cadencia por planta** (`NextFloorAxes`): 55 % apiladas, 30 % una menos (dos abajo, una centrada arriba), 15 % desplazada.
  - **Portal a cualquier lado** (`Portal`).
  - **Regla de contraventanas** (`ResolveShutters`): abiertas miden ±1,24 m, así que en borde o junto a otro hueco pasan a cerradas o sin contraventana.
  - Chaflán a izquierda o derecha (`cornerEntrance`, `cornerSide`). Su puerta está **cerrada** porque aún no hay interior de esquina.
- **`EnvClearance`**: prueba exacta triángulo–caja.
  - Las bajantes y los cables solo se colocan donde caben: junto a la pilastra de esquina (x = 0,29) o en una junta libre.
  - El resto de añadidos (farol, parabólica, contadores, tendedero, macetas, enredadera) se colocan con `TryPlace`.
  - "Sillares fantasma" para medianeras cuya pilastra pertenece al vecino.
- **`EnvTemplates`**:
  - Perfiles de calle: `main`, `secondary`, `kerbed`, **`core`** (plataforma única: bandas de losa, adoquín y dos rigolas), `lane`, `pedestrian`, `plaza`, `port`.
  - Plantillas: `QuayEdge` v2 (params `water`, `lamps`), `Plaza` (`floor:false` para montarla sobre el suelo de un tramo), `SteppedConnector` (`landing`), interiores de tienda y pensión, `Cluster`.
- **`EnvLife`**: vida de calle según jerarquía. En `core`, papeleras contra fachada.
- **`EnvLighting`**: presets `atlantic_overcast` y `atlantic_dusk`.
- **`EnvValidator`**:
  - Checks: módulos vetados, materiales, primitivas, colisión de bahías, umbrales con la cápsula real, apoyo en la calle (impacto más bajo), medianeras abiertas, **`ENV_SERVICE_CLASH`** (bajantes y cables contra huecos), baldosas duplicadas.
  - Autotest con **8/8** defectos sembrados.

### Datos y specs

- **Paletas** del casco en `Env/Grammar/palettes.json`: `core_lime_chestnut`, `core_sandstone_chestnut`, `core_ochre_chestnut`, `core_lime_oxblood`, `core_cream_oxblood`.
- **Materiales nuevos**: `ENV_Joinery_Chestnut`, `ENV_Plaster_Lime`, `ENV_Plaster_Sandstone`, `ENV_Plaster_PaleOchre`.
- **Unidades nuevas** en `Env/Specs/units.json`:
  - `U20_Landmark_Tower_4x4`
  - `U21_Plaza_Node_16x12`
  - `U22_Quay_Composed_24m` (es del puerto; no va en el casco)
  - `U23_Core_House_Narrow_Stone`
  - `U24_Core_House_Stone_Solana`

  La librería queda en 24 unidades.
- **Specs de calle** (`Env/Specs/streets/`):
  - `ENV01_CascoRef_Potes.json`: la Demo C. Cinco tramos (M1, M2, plaza nodo, C1, C2), torre como remate de vista, casa del NE, plaza con vida, bajada con pretil y casa de fin de callejón.
  - `ENV01_CascoRef_Potes_KitPalette.json`: el control A/B, mismo trazado con la paleta antigua.
  - `ENV01_DemoA_Commercial_To_Quay` y `ENV01_DemoB_Upper_Lane`: líneas base "generadas desde cero".

### Referencia real y herramientas

- **`Tools/env_morphology.py`**: `fetch` usa Overpass con espejos (el principal suele estar saturado; `overpass.kumi.systems` funcionó). Los otros comandos son `measure` y `plan`.
- **OSM en bruto**: fuera del repo, en el scratchpad. Se vuelve a descargar con `fetch`.
- **`Docs/evidence/WP-PROD-ENV-01/reference/`**:
  - `casco_reference_metrics.json` (métricas medidas, con atribución ODbL);
  - `casco_reference_plan.jpg`;
  - `layout_metrics_generated_vs_reference.json`.
- **Capturas** en `Docs/evidence/WP-PROD-ENV-01/captures/R*`:
  - `R_sheet_generated_vs_reference.jpg` (A/B/C);
  - `R0_reference_node_vs_traced_skeleton.jpg`;
  - `R4c`–`R7c`: plaza y torre, callejón, esquina, bajada.

### Medidas de Potes (percentiles 10/50/90, OSM de 2026-07-24)

| Calle | Anchura entre fachadas | Frentes | Saltos entre vecinos | Tramos / quiebros |
| --- | --- | --- | --- | --- |
| Doctor Encinas (principal) | 5,6 / 6,5 m | 5 / 9 / 15 m | p50 0,3 m, >0,5 m en el 29 % | tramos de 50–70 m, quiebros de 5–10° |
| del Obispo | 4,1 / 6,4 m | 5 / 7 / 21 m | p50 1,1 m, 73 % | 14–29 m, 15–55° |
| Cántabra | 4,5 m | 5 / 8 / 10 m | 18 % | recta de 45 m tras un nudo desplazado |
| Cimavilla | 2,8 / 7,7 m | 4 / 9 / 15 m | p50 1,3 m, 75 % | 8–32 m, 7–41° |
| la Solana | 2,4 / 4,8 m | 2 / 6 / 14 m | 69 % | 5–28 m, hasta 128° |
| Plaza Capitán Palacios | 13–29 m | 4 / 6 / 10 m | — | plaza lineal junto al río |

Huellas de edificio: lado corto 6 / 9 / 16 m, lado largo 9 / 15 / 24 m. Son parcelas estrechas y profundas.

## 5. Resultados verificados y lo que falta verificar

- **Validación completa** (`5 Validate`): 0 problemas en 24 unidades + 4 escenas, autotest 8/8.
  - **Atención**: se pasó *antes* de tres cambios finales. Hay que repetirla.
    1. Puerta del chaflán cerrada.
    2. `shift -3.4` en C2 (corrige el salto de eje).
    3. Bahías de dos edificios del callejón.
- **Sonda de ruta de la Demo C**: **25/25, 0 atascos, 198 m**. Recorre tres umbrales abiertos, la bajada, el paso junto a la torre y los dos tramos de callejón. En la primera pasada detectó el salto de eje de C2, ya corregido.
- **Sonda de la Demo A** (fachadas nuevas): **11/12**. Aborta en el punto 3 porque un banco del mirador de `QuayEdge` v2 se interpone en el punto de ruta junto a la barandilla, en (46, 0, 8.5). Hay que mover ese punto de ruta o los bancos. Es escena del puerto, pero sigue siendo evidencia de ENV-01.
- **Sonda de la Demo B**: sin repetir con la gramática nueva.
- **Sin ejecutar** tras los cambios: `env_catalog.py lineage/check/inventory`, `asset_catalog.py build/validate` y el test de identidad de intake. El owner cortó justo ahí.

## 6. Pendiente de cierre de WP-PROD-ENV-01 (antes o en paralelo)

`WP-PROD-ENV-02` ("Environment Batch Production Proof": tres composiciones distintas, economía de lote) **depende de ENV-01 PASS**. El distrito de 180 × 220 m encaja como la composición "Casco" de ENV-02, o en un WP propio que el owner decida.

**Recomendación**: cerrar ENV-01 primero. Los pasos, con más detalle en la §9:

1. Commit de control.
2. Documentación:
   - `Docs/production/ENV_COMPOSITION_RULES.md` (reglas de composición extraídas de Potes, pedidas por el owner; hay borrador de contenido en la §7);
   - `Docs/evidence/WP-PROD-ENV-01/CASCO_REFERENCE_STUDY.md` (método, medidas, A/B y respuesta);
   - puesta al día de `ENV_FACTORY.md`, del `README.md` de evidencias, de `ROUTE_PROBES.md`, `REUSE_DECISIONS.md` (fila OSM/Overpass ODbL y decisiones del owner) y de `B0_COVERAGE.md` (gaps cerrados: vehículos, antenas/cables/señales, chaflán, rejillas/alcantarillas; siguen abiertos: bloque post-1960, calle en pendiente, calles con bordillo en curva, interior de esquina, tejado a cuatro aguas).
3. Validaciones.
4. Pre-review estricta, congelar el SHA y PR.

Así el distrito grande se construye sobre una fábrica revisada.

**Respuesta a la pregunta A/B del owner**: sí, mejora de forma material.
- **Aislado el trazado** (paleta antigua en los dos), pasamos de un pasillo recto de 42 × 8 m a cinco espacios:
  - con quiebros de 7–14° y un desplazamiento de eje;
  - con 12 de 14 pares de vecinos con salto de alineación, frente a 0/9;
  - con proporción altura/anchura de 0,7–2,5, frente a 1,1–1,5;
  - con tres remates de vista cerrados, frente a una vista que acaba en cielo.
- **La paleta Potes** suma coherencia, pero es secundaria.
- **La densidad** (28 edificios en 84 m de eje) también viene de la referencia: parcelas estrechas y profundas.

## 7. Reglas de composición extraídas (borrador para `ENV_COMPOSITION_RULES.md`)

1. **Calcar, no inventar.** Cada distrito parte de una zona real medida con `env_morphology.py`. De la referencia se toma estructura; nunca edificios, nombres ni hitos.
2. **Anchuras entre fachadas** (real → juego):
   - principal 5,5–6,5 → 6,0–6,5 m, en plataforma única;
   - secundaria 4,5 → 4,2–4,6;
   - calleja 2,4–4,8 → 3,4–4,0 si pasa de 8 m de largo, y 2,4–3,0 solo en pasos de 8 m o menos;
   - ensanches de 8–15 m cada 40–60 m;
   - nodo/plaza de 13–29 m → 10–14 m.
3. **Altura/anchura**: callejas 2–2,7; principal 1,5–2; plaza 0,7–1.
4. **Ningún tramo recto de más de unos 40 m** en el casco.
   - Principal: tramos de 12–22 m con quiebros de 5–15°.
   - Callejas: 8–15 m con quiebros de 10–20°.
   - **No combinar cambio de anchura y quiebro en la misma junta**: el inglete se desplaza Δoffset/sin θ. O se mantiene la anchura o se ajustan las bahías.
5. **Saltos de alineación**:
   - principal 0,3–0,8 m en el 30–40 % de los pares;
   - callejas 0,4–1,5 m en el 60–75 %;
   - también se permiten salientes (retranqueo negativo).
6. **Parcelas**: frente de 2–4 bahías encajado a la longitud real (así no salen múltiplos de 2 m), con una parcela ancha (10 m) cada 30–40 m. Fondo 8 donde lo permita la cubierta.
7. **Nodo**:
   - la principal desemboca en una plaza;
   - la continuación sale **más estrecha y con el eje desplazado 3–6 m**;
   - un **edificio singular sobresale sobre el eje** y remata la vista, con un paso de unos 3 m a su lado;
   - la esquina del nodo es un chaflán (bar) con fachada lateral abierta a la plaza.
8. **Cada quiebro y cada final de calle revela un cierre**: casa de remate, hito, o pretil/mirador donde el distrito continúa.
9. **Suelo**: el casco va en plataforma única, sin bordillos. Los bordillos son de los distritos modernos y del puerto.
10. **Paleta del casco**:
    - planta baja de piedra en ~70 %;
    - revoco cal/arenisca/ocre;
    - castaño y rojo sangre de toro;
    - teja árabe;
    - 10–20 % de anomalías (reformado en aluminio, abandono).
11. **Jugabilidad**: la cápsula GC2 necesita 2,4 m libres solo en pasos cortos. No se admite ningún estrechamiento de menos de 1,2 m entre bici, pilastra y bolardo. La sonda recorre todos los tramos y umbrales.
12. **A/B siempre** contra una línea base generada, con el mismo kit (variante con `paletteMap`).

## 8. Lecciones técnicas de esta sesión (evitan horas)

- **Exportación en Blender**: `tube()` deja el objeto en rotación QUATERNION y `export()` ponía `rotation_euler`, que se ignoraba. Ya se fuerza `rotation_mode = "XYZ"`. Afectaba a `ENV_Cable_Run_2m` (quedaba dentro del muro) y a `ENV_Mooring_Line` (iba hacia tierra).
- **Sillar de esquina**: el `Corner_ExteriorWide_Brick` es una **pilastra**. Ocupa x ∈ [-0,53; 0,22] y sobresale hasta z = 0,49. Nada de servicios encima: van a 0,29 del borde.
- **Contraventanas abiertas**: ocupan ±1,24 m e invaden la bahía vecina. Lo resuelve `ResolveShutters`.
- **Cambio de anchura en un quiebro**: desplaza el inglete 1,6 m (0,2 m de diferencia con 7°). Aviso `ENV_ROW_FIT`.
- **Desplazamiento de eje**: el `shift` va **en cada tramo**, no se hereda. El log `ENV_PATH_AXIS_SHIFT` lo delata.
- **Validación de apoyo**: lanzaba un rayo que impactaba en cajas o macetas. Ahora usa el impacto más bajo.
- **Cámara ortográfica** creada a mano con `cam.Render()`: no pinta los edificios (causa sin investigar). Para planos, perspectiva alta con niebla desactivada.
- **`execute_code`** (codedom, C# 6): escribe `UnityEngine.Object`, porque `Object` es ambiguo. Las capturas de `EnvPreview.Capture` usan rutas relativas al proyecto.
- **Diagrama referencia→esqueleto**: el script está en el scratchpad de la sesión saliente (`scratchpad/potes/diagram.py`), no en el repo. Si se necesita, conviene moverlo a `Tools/`.

## 9. Plan propuesto para la nueva sesión

0. **Higiene**:
   - salir de Play Mode;
   - commit de control en `worker/prod-env-01`;
   - `5 Validate` y `6 Self-Test`;
   - arreglar el punto 3 de ruta de la Demo A.

   Decide con el owner si se cierra ENV-01 antes (recomendado).
1. **Referencia 180 × 220 m**:
   - Descargar la zona del casco histórico. Caja orientativa en el marco local de la Demo C (origen 43.1542, -4.6237): x -60…120, y -230…-10, es decir, bbox S,W,N,E = `43.1521,-4.6244,43.1541,-4.6222`.
   - Ajústala con el owner sobre el plano: `python Tools/env_morphology.py plan …`. Debe cubrir Solana, Cimavilla, Llano, Cántabra, la plaza con la torre, Doctor Encinas y el primer tramo del Obispo.
   - Medir **todas** las calles y además, cosa nueva, **las manzanas**:
     - perímetro y fondo;
     - patios y huertas interiores;
     - nodos (cruces en T y en X) con anchuras;
     - plazas.

   Decisiones que hay que llevar al owner:
   - **Río.** El Quiviesa cruza el casco, con puentes y casas asomadas al agua. Recomendación: mantener un río o ría, porque estructura el casco y enlaza más tarde con el puerto.
   - **Pendientes.** La Solana sube. OSM no trae cotas; se pueden sacar del MDT del IGN (CC BY 4.0), comprobando licencia al adoptarlo. Opciones: casco plano con terrazas y escaleras (`SteppedConnector`), o módulo nuevo de calle en rampa, que es un gap de la fábrica.
2. **Capa de red urbana** en `EnvStreet`. Es el mayor gap técnico: hoy `path` es **una sola polilínea**. Un distrito necesita:
   - varias trayectorias con nodos compartidos;
   - resolución de cruces en T y en X, con edificios de esquina y chaflanes automáticos;
   - cierre de manzanas, con traseras y patios sin huecos;
   - cotas.

   Se puede generar la spec desde el grafo medido con una herramienta Python, y dejar la composición final (hitos, remates, vida) como acto de autor.
3. **"Potizar" y mejorar los assets.** Estilo lebaniego que hoy falta en el kit:
   - **solanas**: balcón corrido de madera bajo el alero, en la última planta, con una sola puerta;
   - **aleros profundos** con canecillos de madera;
   - **casonas** de sillería con portal de arco y escudo genérico;
   - **galerías de madera** con balaustres torneados;
   - **soportales** donde la referencia los tenga;
   - **cubiertas a cuatro aguas** de teja árabe, menos musgo verde;
   - **suelo** de canto rodado y losas;
   - **puente de piedra de arco**, si hay río.

   Fallos de asset vistos:
   - hay **demasiadas bajantes** en las casas lebaniegas, que desaguan por el alero; se leen como un bosque de postes. Bajar la probabilidad o el grosor;
   - las copas de árbol son tarjetas grandes;
   - la piedra del kit es muy "cartoon";
   - las pilastras de esquina son demasiado gruesas y se repiten en todas las medianeras.

   Hacer una pasada de fotos de referencia (Wikimedia Commons, comprobando licencia) y enseñar al owner una fila de laboratorio antes de aplicar en masa.
4. **Componer el distrito** con la red, la paleta y los assets nuevos. Después: sonda de ruta por todo el distrito, capturas desde la cámara en tercera persona y A/B contra la Demo C.

## 10. Prompt listo para pegar en la nueva sesión

```text
Continúa el casco "mini Potes" de juego-def. Lee primero
Docs/evidence/WP-PROD-ENV-01/HANDOFF_CASCO_POTES.md (estado, decisiones del owner, lecciones y plan) y la
memoria del proyecto. Rama worker/prod-env-01 (hay mucho trabajo sin commit: haz primero un commit de
control). Unity: set_active_instance 9bfcb657, sal de Play Mode si sigue activo.

Objetivo del owner: ampliar la Demo C (ENV01_CascoRef_Potes) hasta un distrito CASCO de ~180 x 220 m basado
en el casco histórico real de Potes (morfología medida con Tools/env_morphology.py: calles, manzanas, nodos,
plazas), ahondar en el estilo visual lebaniego (solanas, aleros con canecillos, casonas de sillería, galerías,
teja árabe, canto rodado) y mejorar los assets mientras se "potizan". El puerto es otro distrito (solo dejar
la transición). Ciudad ficticia: nada de nombres ni hitos de Potes. Antes de construir en grande, confirma
conmigo: cerrar ENV-01 primero o no, caja exacta de referencia, río sí/no, pendientes (terrazas o rampas).
Enséñame capturas en cada hito.
```

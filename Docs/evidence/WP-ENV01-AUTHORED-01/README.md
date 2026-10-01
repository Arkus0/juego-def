# ENV01 authored — entrega Worker

Estado: **READY FOR INDEPENDENT REVIEW**, no independent PASS ni merge.
Brief: [WP-ENV01-AUTHORED-01](../../workpacks/WP-ENV01-AUTHORED-01.md).

## Abrir y editar

Proyecto: `C:/Juego Def/Unity/JuegoDef`, Unity **6000.3.24f1**.

- Nivel: `Assets/JuegoDef/Scenes/ENV/ENV01_AUTHORED.unity`.
- Referencia versionada: `Assets/JuegoDef/Scenes/ENV/ENV01_REFERENCE.unity`, con la jerarquía anterior y los mismos assets congelados. No guardar cambios en ella para conservar la comparación. La original local `ENV01_Casco_District.unity` permanece intacta.
- Las dos escenas se distribuyen por Git LFS; en un checkout nuevo, `git lfs pull`. Mantienen los requisitos de provisioning existentes de Quaternius y GC2; no se redistribuyen los scripts privados de GC2.
- Seleccionar cualquier `BLDG_*` permite mover su conjunto y añadir, eliminar o reorganizar sus hijos normales. No pulsar Generate/Rebuild. La authored está guardada y queda abierta en Edit Mode.

## Inspección y cadena anterior

La original local tiene SHA-256 `41e2cefdc4c3d0bbce7d95e7cd269b5c0d81e9f38697decda7d3567d78aa54b8`.
Ya contenía **72.652 objetos persistentes**: no había meshes temporales ni generación de geometría en runtime.
Su fragilidad era la autoridad del builder y la distribución basada en regeneración: escena y meshes de distrito ignorados por Git, 29.087 instancias ambientales de prefabs generados y referencias a assets editables por las recetas.

| Superficie | Cadena de autoridad previa inspeccionada |
|---|---|
| Footprints, filas, calles, plazas, terreno, río y route | trace/OSM/DEM → `Tools/env_district_skeleton.py` → spec `ENV01_Casco_District.json` → `EnvDistrict.Begin / BuildRows / Finish` |
| Cuerpos, fachadas, cubiertas, interiores aparentes | spec/unidades → `BuildingAssembler`, `FacadeGrammar`, `EnvCharacter`, `EnvBusiness`, `EnvInteriors` → objetos y módulos |
| Props, vegetación, mobiliario, bordes | `EnvDistrict.Finish` y sus pases de dressing, furniture, backdrop, river promenade → instancias |
| Correcciones y sustitución de filas | polish JSON → `EnvPolish.ApplyOps / RebuildRow` → reemplazo de objetos/filas |
| Materiales, módulos y units | grammar → `EnvMaterials`, `EnvModules`, `EnvLibrary`; `EnvKit` coloca y remapea módulos; meshes/texturas/materiales en `Derived/ENV` |
| Colliders | prefabs/módulos y geometría del builder; 21.102 colliders efectivos en la escena |
| Iluminación | `EnvLighting.BuildRig` → luces, volume, `JDLightingRig`, cubemaps horneados |
| Navegación | no había NavMeshData ni NavMeshSurface/Agent en la original; se conserva la navegación física de GC2 sobre colliders, sin añadir un bake |
| Director local previo | `EnvLayoutEditor / LayoutRebuild`: trace → spec → filas o distrito; recuperación de transacciones en domain reload. Era un fichero local no versionado, no adoptado ni modificado en esta PR |

Los componentes efectivos de la escena se inspeccionaron, incluidos los prefabs y helpers: lighting rig, route probe inactivo, personaje/cámaras de GC2, PhysicsRaycaster, additional camera data y volume. No había un componente de generación espacial runtime. Véanse `SOURCE_INSPECTION.json`, `SOURCE_DEPENDENCIES.json`, `SOURCE_AUDIT.json` y los manifests de superficies completos.

## Autoridad nueva y protección

`ENV01_AUTHORED.unity` + sus assets estáticos de `Assets/JuegoDef/Authored/ENV01/` son la autoridad espacial. El trace/spec/polish legacy no reconstruye este nivel.

- Se copió el estado inspeccionado sin ejecutar un builder, con nuevos GUIDs para **780 assets** e importer settings/subasset IDs conservados. `ASSET_SNAPSHOT.json` retiene hashes y procedencia completa.
- Se desempaquetaron por API nativa las **29.087 instancias ambientales**. El cierre final de dependencias tiene **cero prefabs**, **cero `Derived/ENV`**, **cero specs/trace**. Los meshes/materiales importados existentes permanecen, con el mismo contenido.
- Se cambió el root y la organización; ningún objeto visual fue creado, eliminado, densificado o fusionado. Hay **49 objetos organizativos adicionales**, todos sin renderer/collider.
- `EnvAuthoredGuard` bloquea `Begin`, recuperación de estado/chunks/Finish, sustitución de filas, ApplyOps, NewStage y BuildRig antes de sus mutaciones mientras haya una authored/reference cargada, incluso con otra escena activa. El marcador pasivo sigue protegiendo una authored cuyo fichero se renombre.
- No se borran generadores. Sus flujos legacy siguen disponibles al cerrar authored/reference. Las herramientas normales de edición de Unity operan directamente sobre los objetos existentes.
- Los IDs se serializan una sola vez; conservan la clave de origen como procedencia. No se recalculan por nombre, posición ni índice de hijos. `JDSpatialIdentity` es sólo datos: no tiene Awake/OnEnable/Update ni reconstrucción.

## Inventario

| Elemento | Recuento |
|---|---:|
| Grupos de edificios del casco | 311, incluidos 2 landmark buildings |
| Cabañas del backdrop | 4, identificadas aparte como `STRUCT_Cabana_*` |
| Calles/tramos relevantes identificados | 38 |
| Espacios abiertos principales | 5 |
| Props aproximados, por nombre/raíz semántica | 782 |
| Raíces de vegetación fuera de edificios | 652 |
| Objetos authored totales | 72.701 |
| Renderers / colliders / luces | 29.176 / 21.102 / 93 |
| Identidades pasivas | 370 |

Jerarquía: **Buildings / Streets / OpenSpaces / Props / Vegetation / Landmarks / RiverWater / GameplayHelpers / MiscLegacy**. Decoración/fachadas de cada edificio permanecen dentro de su grupo para que se mueva como conjunto. Dos landmarks: `BLDG_K8_3_0` (Torre) y `BLDG_K14_3_0`.

**Pavimento compartido:** la original agrupa suelo por material, no un mesh por calle. Se conserva exactamente. Los 38 `STREET_*` identifican tramos y contienen sus aprons cuando había correspondencia explícita. Sus outlines son anotación legacy, no nueva autoridad geométrica; mover un anchor no traslada todo el pavimento compartido. No se partieron/reconstruyeron carreteras.

Inventario completo: `INVENTORY.json`; límites visuales observados: `BUILDING_ENVELOPES.json`.

## Candidatos futuros, sin consolidación

`CONSOLIDATION_CANDIDATES.json` contiene **342 propuestas solapadas** de 2–6 edificios procedentes del diagnóstico existente, ahora resueltas contra los 311 grupos reales y contrastadas con sus bounds visuales. Todas tienen una distancia XZ entre envelopes vecinos ≤1 m. El AABB es una heurística de proximidad, no prueba exacta de medianera, ownership ni selección de gameplay.

- `BLDG_K0_3_0 + BLDG_K0_3_1` → `GAME_CAND_K0_3_00_2` (Independencia).
- `BLDG_K0_6_0 + BLDG_K0_6_1` → `GAME_CAND_K0_6_00_2`.
- `BLDG_K1_3_3 + BLDG_K1_3_4` → `GAME_CAND_K1_3_03_2` (Capitan_Salida).

Nada se fusionó, clasificó como interior FULL/SHALLOW/DOOR-ONLY ni convirtió en edificio semántico.

## Evidencia y validación

Prueba obligatoria: `PROP_ManualPersistenceProbe`, tapa de registro secundaria, world X **+0,125 m**. Se guardó, reabrió escena, forzó domain reload, cerró Unity (PID 51204), inició otro proceso (PID 51000), entró/salió de Play Mode y observó el mismo transform en todos los pasos. Después se restauró el transform original y se reabrió el nivel. Recibos `MANUAL_EDIT.json`, `EDIT_*.json`, `RESTART_BEFORE.json`.

La equivalencia se comprueba sobre **toda** la población de renderers, colliders y luces: matrices mundiales a 1 mm, tipo/estado, mesh/material/subasset, sombras y formas de colisión. Los tres digests finales coinciden con source y reference. Los hashes reales de cada mesh/material/textura/importer congelado también coinciden con su snapshot; todos los bytes de la original y sus assets permanecen intactos. Las 49 adiciones organizativas no duplican geometría.

Capturas en `views/original`, `views/authored` y `views/runtime-third-person.png`: plaza/Torre, río y vista aérea, además de la tercera persona real en Play. Agua/cielo tienen animación de shader: las capturas separadas en el tiempo no se usan como igualdad literal de píxeles. Se inspeccionó su contenido visual, conservado.

También se compiló y probó Play con los **sources exactos del índice candidato**, excluyendo temporalmente las modificaciones locales anteriores de cuatro scripts y el Director local no versionado. Backups reversibles fuera del repositorio; después se restauraron todos esos bytes y GUIDs exactamente. `CANDIDATE_CLEAN_*.json`: cero errores/referencias faltantes, misma geometría y siete rutas de rebuild bloqueadas. El segundo Play conservó la población ambiental y no creó prefabs.

Reproducir: `python Tools/env01_authored_validate.py`; para un nuevo examen físico en Unity, `EnvAuthoredMigration.Audit("REVIEW_AUDIT")` sobre cada escena y comparar los campos con source/reference. `StartUnpack`/`Organize` son migración explícita de una copia previa, no pasos de apertura normal. No volver a ejecutar el snapshot sobre una authored existente: se niega a sobrescribirla.

`PORTABLE_CHECKOUT.json` verifica además una exportación real del índice Git: escenas completas recuperadas mediante LFS, conversión de finales de línea de Git y 45 checks correctos sin original ignorada ni ficheros locales no versionados. Los hashes canónicos de texto Unity normalizan exclusivamente CRLF/LF; los binarios se contrastan byte a byte. El check adicional de preservación raw de la original se ejecuta cuando esa original local existe.

## Límites y dependencias restantes

- Presentación existente: `JDLightingRig` conserva F9/presets, globals de shaders y lámparas; no modifica el layout. Shaders de agua/cielo/fake interiors siguen animando su presentación. RouteProbe queda inactivo.
- Quaternius importado, GC2, URP y shaders/versiones ya existentes siguen siendo requisitos de assets/runtime. No hay proceduralidad espacial necesaria para cargar authored.
- Reference comparte los assets congelados con authored. Una futura edición de un material/mesh compartido afectaría ambas vistas; la original local usa sus assets anteriores y se preservan los hashes. Comparar transforms/hierarchy no necesita regenerar nada.
- Legacy Director no se convierte en editor de objetos en este WP. Una transacción antigua podría todavía recuperar su propio spec/escena legacy; su registro estaba cerrado durante toda esta migración. No tiene referencias a la copia authored ni a sus assets.
- Al restaurar el Director local previo reaparecen sus dos warnings CS8632 de nullable context. El candidato sin ese fichero compila sin esos warnings; se ha preservado el trabajo ajeno.
- Duplicar manualmente un objeto copia su ID; asignar un nuevo ID cuando se crea una nueva entidad. La auditoría detecta duplicados y no mueve/borra objetos para corregirlos.
- No se rediseñó el casco ni hubo density/art/interior/road/optimization pass. La siguiente consolidación parte de esta escena Unity, nunca de regenerar el trace.

## Archivos y revisión

Lista completa: `CHANGED_FILES.txt`. Cambios: dos escenas LFS; snapshot de 780 assets y metas; identidad pasiva y tooling/guards acotados; dos llamadas del overlay previo reparadas por bloqueo de compilación; WP, recibos, inventario y validación. No se incluyen los cambios locales anteriores de BuildingAssembler/EnvDistrict/EnvInteriors/FacadeGrammar ni el Director local.

La PR se apoya en la baseline ENV actual `e3a012e4acf50b99413df16adfcd9444355cb691` (`worker/casco-diag-01`) para mostrar únicamente esta migración. La baseline ENV anterior no se reacepta ni mezcla con cambios de `main` en este WP. Un commit de producto; exact SHA en la PR/entrega. Véase `WORKER_PRE_REVIEW.md`. Siguiente gate: Reviewer fresco; sin merge por el Worker.

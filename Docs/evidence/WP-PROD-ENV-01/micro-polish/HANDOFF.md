# HANDOFF - micro-pulido del CASCO (ENV-01), sesion 2 del 2026-09-29

Lee primero: `AGENTS.md`, este fichero, `pass2/PASS2.md` (registro completo de la pasada 2),
`UNITS.md` (estados por unidad) y `Docs/production/ENV_FACTORY.md` (seccion "Micro-polish pass").
La pasada 1 vive en `UNITS.md` / `STREET_A_Espina_E.md` / `SEMANTICS.md` / `SEM/`.

## 1. Estado en una linea

Las **21 unidades de la pasada 2 estan CERRADAS** (calles, callejones, plazas, rio, puentes,
huertas); el arbol esta **commiteado y empujado a la PR #10**. Quedan abiertas: **PERIM_A**
(llano beige y talud sin muro tras la entrada este, heredado de la pasada 1), la **sonda de
ruta** (el owner quiere retunearla) y el **HUMAN LOGIC WALK final** del brief. Sin freeze ni
reviewer todavia: cuando la siguiente sesion cierre esas tres cosas, freeze SHA + Reviewer
independiente.

## 2. Proyecto, editor, escena

| | |
|---|---|
| Repo | `C:\Juego Def` (git), rama `worker/prod-env-01`, PR https://github.com/Arkus0/juego-def/pull/10 |
| Proyecto Unity | `C:\Juego Def\Unity\JuegoDef`, Unity 6000.3.24f1, escena `Assets/JuegoDef/Scenes/ENV/ENV01_Casco_District.unity` (generada, gitignored, ~30 s de rebuild) |
| MCP unityMCP | instancia **`JuegoDef@9bfcb657`** (puerto 6400; `set_active_instance 9bfcb657` tras cada domain reload — el registro de instancias del server MCP es inestable, si una llamada dice "not found", vuelve a fijar). La de Codex characters-01 es `2558158d`. |
| CLI | `C:\Users\Usuario\AppData\Local\Unity\bin\unity.exe` con cwd `C:\Juego Def\Unity\JuegoDef` (elige editor por cwd; el nuestro, puerto 7800). `eval_file --detach` + log a fichero para lotes. Requiere `com.unity.pipeline` en Packages/manifest.json — **sin commitear a proposito** (decision pendiente del owner, ver §6). |
| Trampa conocida | La copia de respaldo `C:\Juego Def-ENV01-local-20260928` (PID 25084) puede seguir abierta: NO es este proyecto, no la toques. |

## 3. Que cambio en esta sesion (fabrica; sobrevive al rebuild)

1. `EnvWalk.OpenAirHoles` compila ya (fix CS0136: `out var hit` en vez de `out var top`).
2. `GroundGapFill` verificado visualmente: 42/43 celdas cubiertas; la restante es falso positivo
   del chequeo por centroides; río/escaleras/puentes limpios; 8 puntos SkyHoles sin cielo visible.
3. Pilar de huerta cuadrado (antes cruz) en `EnvDistrict.GardenWall`.
4. Terrazas de plaza a 2.05 m de fachada (la copa de la sombrilla entraba en el muro) y solo
   para bar/cafe/sidreria (`EnvBusiness.TypeByBuilding` + `IsHospitality`): tras el rebuild
   queda exactamente 1 sombrilla (Bar Tito, K2_9_0).
5. Casas de río: zócalo remapeado al mismo tramo de `ENV_RiverWall_*` del encauzamiento y
   sótano mínimo 0.45 m (`EnvDistrict.BuildRows`).
6. `polish.json`: 8 ops (balconera K6_10_1; taller en K15_5_1; barril fuera en Espina_Nodo;
   2 pizarras recolocadas en STREET_C/D; banco fuera del portal en Calle_Alta_O; barril
   hundido levantado en la pasarela) + 1 plot (`K15_5_1 business=taller`).
   **Importante**: `EnvPolish.ApplyOps` no es idempotente para `move` (los `miss` tras un
   re-apply manual son esperados; tras un rebuild completo `Finish` las aplica desde cero).

## 4. Validacion de esta sesion

- `EnvValidator.Validate(false)` -> **0 problemas** (372 umbrales cerrados, 0 abiertos, 29.142 renderers).
- Self-test -> **missed=0** (8/8 detectores). OJO: `Validate` sobrescribe `VALIDATION.json` SIN la
  seccion `selfTest` (la escribe el item de menu "6 Validator Self-Test"); si el item falla en
  silencio (nos paso), restaura el bloque a mano — el de hoy esta commiteado.
- `WallGaps` de las 164 filas: **0 huecos** muro-suelo.
- Sonda de ruta: ARRANCADA (158 waypoints) y **diferida por el owner** en wp=13 sin atasco
  logueado; quiere afinar que buscar antes de fiarse del resultado. Pendiente de rerun.

## 5. Pendiente para la siguiente sesion (en orden)

1. **Sonda de ruta retuneada por el owner** + rerun (validador ya esta verde; la sonda es la
   prueba de navegacion del candidate).
2. **HUMAN LOGIC WALK final** del brief (seccion 26): una ultima vuelta completa buscando
   unicamente cosas sin sentido humano; corregir solo casos claros.
3. **PERIM_A**: decidir el llano beige tras la entrada este (prado con textura? talud con muro?)
   y el talud sin muro detras de K4_0. Es el unico hallazgo abierto heredado.
4. Revisar con el owner las **limitaciones documentadas** en `pass2/PASS2.md` (juntas de sillar
   vs marcos, persiana sobre cristal v7, flancos traseros ciegos): si insiste, son trabajo de
   modulo; si no, se cierran como lenguaje del casco.
5. Entonces: **pre-review estricta del Worker -> freeze del SHA exacto -> Reviewer independiente**
   para la PR #10 (el ciclo AGENTS.md sigue pendiente; nada de esto se ha revisado todavia).

## 6. Git (estado tras el push de esta sesion)

- Todo el trabajo de las sesiones 1+2 esta commiteado en la rama `worker/prod-env-01` y empujado
  (la PR #10 se actualiza sola). El commit mezcla a proposito las dos sesiones: venian revueltos
  en el working tree desde la sesion 1 (~370 ficheros) y separarlos con `git add -p` no aportaba
  nada revision-wise.
- **`Packages/manifest.json` + `packages-lock.json` siguen SIN commitear a proposito**: anaden
  `com.unity.pipeline 0.8.0-exp.1` (herramienta CLI del editor, no runtime). Decision pendiente
  del owner: si se queda, commitealos; si no, borra el paquete (`unity pipeline uninstall`) y
  la CLI dejara de funcionar en futuras sesiones.
- `Captures/`, `Temp/` y la escena generada siguen gitignored; lo curado vive en
  `Docs/evidence/WP-PROD-ENV-01/micro-polish/pass2/` (hojas de contacto de cada unidad).

## 7. Comandos utiles (igual que la sesion 1, resumen)

- Rebuild completo (~30 s): `JuegoDef.Env.EnvDistrict.Begin("ENV01_Casco_District"); BuildRows(0, int.MaxValue); Finish();`
- Paseo de calle: `EnvWalk.Street(id, "Captures/micro-polish/<u>", 6f, "game,up", 1280, 720, false)` + `EnvWalk.Audit(id, 9f)`.
- Look puntual: `EnvSemantics.Look(folder, name, at, dirOut, dist, fov)` (dos vistas _a/_b).
- Captura libre: `EnvPreview.Capture(path, eye, at, fov, w, h)`.
- Hojas de contacto: `python Tools/env_sheet.py grid <carpeta> <out.jpg> --cols 3 --width 640` (el `--match` es subcadena literal, sin `|`).
- Audit no es idempotente-agnostico: los solapes AABB de props contra muros/plantas son casi
  siempre falsos positivos; confirma con `Look` antes de tocar (lista de falsos positivos
  conocidos en `pass2/PASS2.md`).

## 8. Aviso de sesion

El dueno habla espanol y quiere respuestas decididas. La filosofia sigue siendo
OBSERVAR -> ENTENDER -> CORREGIR -> VOLVER A MIRAR, unidad por unidad, y
SI FUNCIONA -> CONSERVAR, SI ESTA MAL -> CORREGIR, SI ES DUDOSO -> mas angulos.

# WP-CITY-IVX-HUMAN-01 — La Plaza Mayor, hecha a mano: el pueblo deja de parecer generado

Status: **READY** (handoff 2026-10-03)
Class: PRODUCT / LEVEL DESIGN / UNITY
Track: pueblo sobre el trazado Ivanix88 (`Tools/city_ivanix`, escenas `Scenes/CITY_IVX/*`). No es el track Mapa F1 / B0
(`WP-CITY-SKELETON-00`, `WP-CITY-B0-01`); no se mezclan.
Worktree: `C:\Users\Usuario\juego-def-wt\city` · rama `worker/city-skeleton-00` (local, sin push).

## Veredicto del Owner que abre este WP (paseo, 2026-10-03)

> "He dado un paseo por el escenario y está fatal semánticamente. Y assets de bajo nivel fuera de Quaternius. Parecen
> low poly en vez de Dreamcast (y el nivel Dreamcast+ no se nota demasiado). El principal problema es que el escenario
> sigue siendo procedural y poco humano. Es la prioridad número uno. Piensa en que no eres Opus, eres un level designer
> de alto nivel, y si pierdes precisión por mayor creatividad, sentido y carisma, mejor."

Prioridades, en este orden: **1. humano / semántico** · 2. assets al nivel · 3. que el Dreamcast+ se note.

### Añadido del Owner (2026-10-03, durante el Paso 1)

Viendo una captura de Shenmue 2 junto a la Calle Mayor actual:

> "Creo el tema de la luz, y sobretodo, texturas con cada superficie pintada, es clave."
>
> "Es que es eso. Me da igual lo que haya que cambiar, me da igual la calidad, me da igual si tenemos que quitar assets
> quaternius o no, quiero que el juego parezca un spin off de shenmue 2. Como un DLC con el mismo estilo gráfico."

Consecuencia: el **look Shenmue 2** deja de ser la prioridad 3 y pasa a objetivo de primer orden, a la par de lo humano
(en Shenmue la densidad tiene sentido: cada objeto es de la tienda de al lado; ambas cosas son el mismo trabajo). La barra
de la sección 8 pasa a ser "parece Shenmue 2": luz horneada y textura pintada en cada superficie; Quaternius y el kit
dejan de ser obligatorios. Lectura del Worker, pendiente de confirmar en el checkpoint del brief: es el **estilo gráfico**
de Shenmue 2 sobre el mismo pueblo cantábrico de 1999–2003 (sin estética asiática ni marcas reales, sección 6).

---

## 0. Postura (léelo antes de tocar nada)

- **Eres el level designer del pueblo, no su generador.** Cada cosa que quede en la escena la has decidido tú, por un
  motivo que cabe en una frase. Si no sabes decir quién la puso ahí y por qué, no va.
- **Carisma por encima de exactitud.** Una decisión con intención y algo de imprecisión vale más que una regla
  correcta y anodina. Se puede (y se debe) ser específico, raro, local, con historia.
- **El generador está congelado.** No se arregla lo procedural con más reglas. Las herramientas existentes sirven para
  comprobar (colisiones, NavMesh), no para decidir.
- **Profundidad antes que extensión.** Un trozo de pueblo excelente vale más que todo el pueblo un poco mejor. Lo que
  veas fuera del corte se anota para después; no se toca.
- **Se juzga paseando**, con el Player y la cámara del juego. El Owner es el árbitro; las métricas sólo evitan errores
  físicos.

## 1. Diagnóstico: por qué sigue pareciendo procedural

1. **Todo se decidió por reglas a escala de ciudad a la vez** (268 edificios, ~317 objetos, 54 comercios). El resultado
   es una distribución estadística uniforme: farolas cada 22 m en el eje, contenedores cada 80 m, un 45 % de portales con
   "su" objeto al mismo lado y a la misma distancia, cada bar con dos juegos de terraza iguales. El ojo humano detecta el
   patrón aunque no sepa nombrarlo.
2. **El mapa de programas es incoherente** (visible en `reconstruction/city_seed_v4.json`, dentro del propio corte):
   - el Hotel ocupa tres edificios en tres calles distintas (`R0126` Levante Sur, `R0127` Solana, `R0128` Hospital);
   - el Mercado de Abastos, tres edificios en tres calles (`R0068` Finca, `R0083` Plaza, `R0111` Levante);
   - el Ayuntamiento, dos edificios, uno sin rótulo y en otra calle (`M0186_00` plaza, `M0184_00` Muelle);
   - "Farmacia **de la Plaza**" está a ~70 m de la plaza (`R0161_1`, Calle Mayor z≈−72);
   - "Bar El Puerto" (bar de misión `R0185`) no está en el puerto.
   Nombres y usos se repartieron por cupo, no por lugar.
3. **Edificios anónimos.** Las fachadas salen de la gramática ENV con elecciones aleatorias; el uso sólo se expresa con
   un rótulo pegado. Los edificios cívicos no son únicos; una tienda y una casa tienen la misma planta baja.
4. **Ningún lugar está compuesto para la cámara.** No hay remates de perspectiva pensados, ni jerarquía de alturas y
   ornamento, y la densidad es la misma en la calle principal que en un callejón.
5. **El trazado Ivanix (muralla, cubos, puertas) sigue leyéndose como villa medieval de fantasía** allí donde su uso de
   2000 (paseo marítimo, miradores, bar en un cubo, almacén en una torre) no se ve.
6. **Los assets propios (`CITY_*`) son de nivel low-poly**: siluetas de primitivas facetadas, color plano, textura sin
   detalle. El shader Dreamcast+ no compensa un objeto pobre.
7. **Cada corrección anterior fue una regla nueva** (resolver de entidades, lint, recortes…). Útil para lo físico, pero
   el Owner encuentra fallos semánticos nuevos en cada paseo: la vía generador + lint ha tocado techo para el sentido.

## 2. Decisión y alcance

- El pueblo pasa de **sembrado** a **authored**. Este WP hace el primer corte: **la Plaza Mayor y el arranque de la
  Calle Mayor**, el sitio que el jugador ve primero y que define el tono de todo lo demás.
- **Caja del corte** (coordenadas de mundo de las escenas CITY_IVX): `x ∈ [−45, 45]`, `z ∈ [−75, 35]`. Incluye la plaza
  (fuente en `(0, 10, 0)`), Iglesia `R0054` (≈17, 20), Casa Consistorial `M0186_00` (≈−18, 18), Mercado de Abastos
  `R0083` (≈33, 2), Calle Mayor hasta la bocacalle del abanico (≈−9, −61), Sidrería Casa Bustamante `R0152`, Bar La
  Ribera `R0117`, Hotel Miramar `R0126`, Hogar del Pensionista `R0171`, Farmacia `R0161_1`, Óptica `R0132_1`, Pescados
  Hnos. Ruiz `R0132_2`, Panadería La Espiga `R0058`, Sidrería La Pomarada `R0085`, Modas Carmen `R0086`.
- Fuera de alcance: el resto del pueblo (se anota en `Docs/evidence/WP-CITY-IVX-HUMAN-01/FUERA_DEL_CORTE.md`),
  interiores, sistemas de NPC/rutinas/combate, el track Mapa F1/B0, `ENV01_AUTHORED`, compras sin Owner.

## 3. Dependency check (AGENTS.md)

| | |
|---|---|
| Prerrequisitos | commits `effe9af` … `926aa49` + `bca8d27` (WIP sin verificar); pipeline `Tools/city_ivanix` (README); kit ENV; Quaternius `MedievalVillage`, `Nature`, `Props` provisionados en `Assets/ThirdParty/Quaternius`; Player GC2 en la escena base |
| Garantías que se consumen | trazado, calles, cotas y orientación de fachadas del pueblo Ivanix; luz atlántica (aceptada por el Owner); pavimento a pulso (`CityPaving`, shader DC Ground); sistema de rótulos pintados (`CityShopfronts`); comprobación física de entidades (`CityEntities`, `CityIvanixLint`); sonda NavMesh (`CityIvanixNav`, 18 anclas) |
| Lo que este WP posee | el estado authored del corte; el brief de lugar y los ledgers; la versión LFS de las escenas CITY_IVX; los assets que se sustituyan o mejoren para el corte |
| Reabrir si… | el paseo demuestra que el problema del corte es el trazado de calles y no su contenido → parar y preguntar al Owner antes de mover calles; un edificio héroe necesita un modelo que ni el kit ni Quaternius dan → decisión del Owner (crear o comprar) |

## 4. Trabajo, en orden

**Paso 0 — Toma de control técnica** (sección 9): terminar la cadena interrumpida, verificar los tres arreglos WIP,
versionar las escenas en LFS y **congelar**: desde ese commit nadie vuelve a sembrar ni a vestir CITY_IVX con los
seeders (borrar escenas para resembrar queda prohibido).

**Paso 1 — Paseo y diario.** Play Mode con el Player GC2. Recorre el corte entero dos veces (de día, sin prisa). Anota
cada parada donde algo chirría, con captura y clase: *no existiría · sitio equivocado · falta algo obvio · escala ·
época/estética · asset pobre*. Pide al Owner sus capturas del paseo si las tiene. Fija **8 puntos de vista** a altura
de jugador (cámara del juego: 3 m de distancia, FOV 55) y guárdalos en `VIEWS.json`; son los mismos para el antes y el
después.

**Paso 2 — Brief de lugar, en papel, antes de construir** (`Docs/design/city_ivx/PLAZA_MAYOR_BRIEF.md`, una página
+ una vista cenital anotada):
- la historia del sitio en cinco líneas (qué fue, qué es en 2000, qué día de la semana se ve);
- los habitantes: cada edificio con fachada al corte → quién vive o trabaja ahí, desde cuándo, cómo está (cuidado,
  cansado, cerrado), qué saca a la calle;
- usos por hora: mañana de mercadillo, mediodía de vermú, tarde de terrazas, noche vacía;
- las vistas: qué remata cada eje (torre, fachada pintada, árbol, un trozo de mar);
- recorridos: jugador, NPC, reparto; el hueco de la plaza que debe quedar libre (el mercadillo es de un día y tiene que
  poder retirarse: la plaza vacía también debe funcionar);
- la lista de viñetas (paso 6).

**Checkpoint del Owner (obligatorio):** al terminar el brief, parar y enviárselo al Owner con la vista anotada y el
diario del paseo. No se construye nada del corte hasta su visto bueno al brief.

**Paso 3 — Restar.** Quita todo lo que no tenga dueño ni motivo. Quitar cuenta como avance; una calle tranquila y
limpia es mejor que una llena de relleno.

**Paso 4 — Mapa de programas del corte.** Un programa = un edificio (o una fila contigua que se lea como uno), en el
sitio que su nombre promete. Resolver al menos los casos del diagnóstico: Hotel, Mercado de Abastos, Ayuntamiento,
"Farmacia de la Plaza". La planta baja expresa el uso (escaparate, portal de vecinos, garaje, persiana echada de un
local cerrado "Se traspasa"). Los nombres se reescriben si hace falta.

**Paso 5 — Los tres edificios héroe de la plaza** (Iglesia, Casa Consistorial, Mercado de Abastos): únicos, legibles
desde cualquier punto de la plaza, montados a mano con piezas del kit y de Quaternius. La Casa Consistorial con su
balcón, reloj o escudo, banderas y tablón de anuncios; el Mercado con su portalón y su muelle de carga a la calle de
atrás; la Iglesia con su atrio y sus escalones donde se sienta la gente.

**Paso 6 — Viñetas.** Entre 12 y 20 escenas pequeñas con historia, cada una con dueño, hora y motivo. Ejemplos del tono
que se busca (no una lista que haya que cumplir):
- *La esquina del bar*: tres mesas que no son iguales (una con dos cañas a medias y el periódico), la pizarra
  "Menú del día 1.200 pts", la caja de botellines vacíos junto a la puerta de servicio, un Vespino en el bordillo, el
  toldo medio recogido.
- *El portal de la señora del segundo*: felpudo, hortensias que se salen de la maceta, la bombona de butano esperando al
  butanero, la bici apoyada, ropa tendida arriba.
- *La descarga de la mañana*: furgoneta con el portón abierto frente al Mercado, carretilla, cajas apiladas, un charco.
- *Las fiestas*: banderines cruzando la Calle Mayor, el cartel de la verbena pegado en una pared, restos de confeti.
- *Lo cerrado*: un local con la persiana bajada y "Se traspasa", el fantasma de un rótulo antiguo en la fachada.
- *Lo civil*: placas con el nombre de la calle en las esquinas, paso de cebra y bolardos donde entra la Calle Mayor en
  la plaza, la cabina, el buzón, el quiosco de la ONCE, los contenedores metidos en un rincón y no en mitad de la acera.

**Paso 7 — Assets del corte al nivel** (sección 8): todo asset propio visible en el corte se sustituye por kit o
Quaternius, se rehace al nivel, o se quita.

**Paso 8 — Paseo del Owner e iteración.** Cada 3–4 viñetas, capturas al Owner. Al final, paseo del Owner con el Player
por la ruta acordada; se corrige y se repite hasta su PASS.

## 5. Definition of Done

| # | Criterio | Cómo se comprueba |
|---|---|---|
| D1 | Autoridad: escenas CITY_IVX en git LFS; el corte agrupado bajo `AUTHORED_PLAZA_MAYOR` (o equivalente) y ningún seeder vuelve a escribirlo | `.gitattributes`, commit, nota de guardia en el README del pipeline |
| D2 | Brief de lugar escrito y commiteado **antes** de construir | `Docs/design/city_ivx/PLAZA_MAYOR_BRIEF.md` con su vista anotada |
| D3 | Ledger de edificios: el 100 % de los edificios con fachada al corte tiene identidad (uso, dueño o nombre, estado), planta baja y puerta coherentes con el uso; los programas multi-edificio del diagnóstico están resueltos | `BUILDINGS.md` en la evidencia |
| D4 | Ledger de objetos: el 100 % de los objetos del corte pertenece a una viñeta con dueño y motivo; 12–20 viñetas; ninguna fila uniforme salvo mobiliario municipal (farolas, bolardos) | `VINETAS.md` en la evidencia |
| D5 | Vistas: los 8 puntos fijos con antes/después; cada vista principal tiene un remate legible; en ningún encuadre hay un objeto de color plano sin textura; ninguna variante de objeto se repite más de dos veces en un mismo encuadre (salvo mobiliario municipal) | capturas `views/before_*`, `views/after_*` |
| D6 | Assets: todo asset propio visible en el corte cumple la barra de la sección 8 o ha sido sustituido o quitado | capturas comparativas en `assets/` |
| D7 | Cordura física: 0 solapes en el corte (`CityIvanixLint` + comprobación `CityEntities`), nada flotando ni hundido, NavMesh 18/18 y cruces de la plaza a pie posibles, el hueco libre de la plaza respetado | `LINT.json`, `NAV_PROBE.json` |
| D8 | **Paseo del Owner PASS**: "nada que un humano no habría puesto; nada obvio que falte" en la ruta spawn → plaza → Calle Mayor → bocacalle | veredicto del Owner registrado |
| D9 | Disciplina AGENTS: commit por viñeta o paso, pre-review estricto, SHA congelado, Reviewer fresco | historial y `PRE_REVIEW.md` |

D8 es la puerta. D1–D7 sin D8 no es DONE; D8 sin D7 tampoco.

## 6. Lo que NO queremos

- Arreglar lo procedural con más procedural: reglas nuevas, pasadas globales, cuotas, "cada N metros", aleatoriedad
  como sustituto de decisión.
- Pasadas sobre todo el pueblo antes de que el corte esté excelente.
- Objetos sin dueño ni motivo, relleno para "dar densidad", decoración de museo.
- Estética de aldea medieval: barriles y cajas por todas partes, puestos medievales, antorchas, carros de madera.
- Assets propios de primitivas y color plano; objetos low-poly al lado de piezas de mejor nivel.
- Repetición visible: el mismo objeto, el mismo color, la misma distancia al portal.
- Simetrías y alineaciones de regla donde la vida real es irregular (y al revés: torcer lo que en la realidad está
  alineado, como una fila de farolas o un bordillo).
- Métricas como prueba de calidad: "lint limpio" no es "bien".
- Volver a sembrar o vestir CITY_IVX con los seeders tras el congelado.
- Estética asiática, marcas reales, luz andaluza.
- Tocar `ENV01_AUTHORED`, el trabajo DENSITY-01 del checkout principal o el track Mapa F1/B0.
- Inventar sistemas de juego o interiores dentro de este WP.
- Informes largos en lugar de capturas y paseo.

## 7. Buenas prácticas de level design para este trabajo

1. **Brief antes que geometría.** Cinco líneas de historia por lugar ahorran diez rondas de correcciones.
2. **Cámara del juego primero.** Se diseña para el encuadre de tercera persona (3 m, FOV 55, ojos a 1,7 m), no para la
   vista cenital. La cenital sirve para planificar, no para juzgar.
3. **Restar antes de sumar.**
4. **Remates y jerarquía.** Cada eje del corte termina en algo. Lo cívico manda (más alto, más ornamento, mejor
   pavimento, más luz), luego lo comercial, luego lo doméstico.
5. **Densidad con gradiente.** La vida se concentra en nodos: puertas de comercios con trabajo, esquinas, bordes de la
   plaza; las tiradas residenciales respiran.
6. **Viñetas, no objetos.** Grupos de 3–7 cosas que cuentan una escena, asimétricos, con una pieza dominante.
7. **"¿Cómo llegó esto aquí?"** Quién lo trajo, por dónde entra un vehículo, a qué hora se usa, qué desgaste deja
   (mancha de aceite donde aparca la furgoneta, baldosa gastada en la puerta del bar).
8. **Historia y desgaste.** Un revoco parchado, un escaparate de aluminio nuevo en una casa de piedra vieja, una
   ventana tapiada, el rótulo fantasma, una parabólica o un aire acondicionado puestos donde los pondría un instalador.
9. **Época, con moderación.** 1999–2003: pesetas en los precios, cabina, buzón amarillo, quiosco de la ONCE, butano,
   Vespinos, utilitarios genéricos, carteles de fiestas; nombres inventados, nada de marcas reales.
10. **Esquinas resueltas.** Las esquinas tienen usos fuertes (bar, farmacia, quiosco), placas con el nombre de la calle
    y su pequeño desorden.
11. **Presupuesto de repetición por encuadre** (D5).
12. **Bucle corto:** colocar → mirar con la cámara del juego → criticar como un forastero → corregir. Capturas al Owner
    cada 3–4 viñetas; commit por viñeta.
13. **Las herramientas asisten, no deciden.** Apoyar en el suelo, alinear a fachada, comprobar colisión
    (`CityEntities.Resolve`/`InsidePlan` como test), NavMesh. Nada de colocación aleatoria.
14. **Referencias reales.** Una o dos fotos por viñeta de pueblos cantábricos y asturianos de la época (Llanes,
    Ribadesella, Cudillero, Castro Urdiales, San Vicente de la Barquera, Comillas, Laredo, Santoña, Potes), usadas
    como alma y no como calco.

## 8. Barra de assets: "Dreamcast, no low-poly"

Low-poly es: siluetas facetadas de primitivas, color plano, superficies limpias y nuevas, ningún detalle impreso.
Dreamcast (Shenmue 2) es: siluetas suaves donde importan, **todo texturizado** con detalle pintado (suciedad, juntas,
etiquetas, letreros, desgaste, luz y oclusión horneadas), muchos objetos pequeños de calle con su textura impresa.

Un asset propio entra en el corte sólo si:
- puesto al lado de su equivalente Quaternius o del kit, a distancia de juego (3–6 m), **no se ve peor**; la prueba es
  una captura triple: referencia Shenmue 2 · Quaternius/kit · el nuestro;
- no se ve facetado en curvas a 3–6 m (coches y barcas con biseles y suavizado; del orden de 1,5–3 k triángulos en un
  coche);
- toda superficie tiene textura con detalle; el color plano sólo vale para cristal, goma o piezas metálicas pequeñas;
  densidad de textura ≥ ~200 px/m en objetos a menos de 5 m;
- si se repite, tiene 2–3 variantes de textura.

Si no se alcanza la barra pronto: **usar el asset de Quaternius o del kit, o no poner nada**. Un hueco es mejor que un
objeto pobre. Los `CITY_*` actuales (coches, furgoneta, barca, puestos, terraza, árboles, hortensias, butano, buzón,
máquina de chicles) son candidatos a sustituir o rehacer; los puestos de mercadillo y la barca son los mejor
encaminados. Herramientas: scripts de `Tools/city_ivanix/blender/`, Blender MCP, y `generate_model` de unityMCP sólo
tras comprobar licencia y procedencia (regla de investigación de AGENTS).

Para que el Dreamcast+ se note (prioridad 3, después del corte): más carga en la textura que en el shader —
escaparates con género visible, carteles y pegatinas, cajas de luz en bares y farmacia, suciedad de zócalo y bajantes,
charcos con brillo— antes que más efectos.

## 9. Estado técnico exacto (handoff)

**Rama y commits** (`worker/city-skeleton-00`, local, no hay push):
`effe9af` pipeline · `e500918` pulido tras paseos · `c6d60cd` look-dev Dreamcast+ y objetos como entidades ·
`926aa49` pavimento a pulso, fuente de vuelta · `bca8d27` **WIP sin verificar** (balcones de 1,64 m dentro de los
esquinales; barandilla del paseo recortada contra la sillería y con colliders; retirada de añadidos de fachada bajo
rótulos nuevos) · más el commit de este handoff.

**La cadena quedó interrumpida.** Las escenas en disco están resembradas, vestidas, con escaparates y con el manifiesto
DC exportado; **faltan** el repintado DC, la conversión, el pavimento, el NavMesh y el lint. Hasta completarlo, la
escena se ve con materiales URP sin estilo y sin NavMesh (el asset se borró al resembrar).

**Paso 0, en orden:**
1. Abrir Unity sobre el worktree (el editor no está abierto):
   `"C:\Program Files\Unity\Hub\Editor\6000.3.24f1\Editor\Unity.exe" -projectPath "C:\Users\Usuario\juego-def-wt\city\Unity\JuegoDef"`.
   En unityMCP, `set_active_instance` a la instancia `JuegoDef@…` de **este** worktree (la última fue `bcca777e`;
   puede cambiar; comprobar `Application.dataPath`). Hay otras instancias de Unity que comparten el MCP.
2. `python Tools/city_ivanix/tools/dc_textures.py` → `CityDcPlus.Convert()` → `CityPaving.Apply()` →
   `CityIvanixNav.BakeAndProbe(true)` → `CityIvanixLint.Run()`.
3. Verificar el WIP con las auditorías que lo motivaron: barandillas laterales de balcón contra esquinales (antes 50
   casos), piezas de barandilla del paseo contra sillería o papeleras (antes 71), añadidos de fachada bajo rótulos.
   Corregir si hace falta y commitear.
4. Versionar en LFS `Unity/JuegoDef/Assets/JuegoDef/Scenes/CITY_IVX/*.unity` y `CITY_IVX_NavMesh.asset`
   (`.gitattributes`, como `ENV01_AUTHORED.unity`) y commitear: **desde aquí, congelado**.
5. Antes de commitear, no arrastrar el ruido de reserialización de `Derived/ENV/*` y `Authored/ENV01/*` (materiales y
   `.meta` de rótulos que Unity reescribe): `git checkout --` sobre esas rutas, o dejarlas fuera del commit.

**Pipeline y herramientas** (orden completo en `Tools/city_ivanix/README.md`): `CityPropsLibrary.Build`,
`CityIvanixSeed.Seed`, `CityIvanixDress.Dress`, `CityShopfronts.Apply`, `CityDcPlus.Export/Convert`, `CityPaving.Apply`,
`CityIvanixNav.BakeAndProbe`, `CityIvanixLint.Run`; `CityEntities` (`Settle`, `Resolve`, `InsidePlan`, `Rope`) sirve
como comprobación al colocar a mano. Capturas: mover la `Main Camera` y `manage_camera screenshot` con
`camera="Main Camera"` y `output_folder="Captures"` (fuera del proyecto da error); copiar a la evidencia.

**Pendientes conocidos (no bloquean el corte, no olvidarlos):**
- `Rendering/JD_URP.asset`: sombras subidas a 4096 / 4 cascadas / 120 m para el pueblo; es **global** (afecta a
  ENV01). Antes de cualquier merge, mover a un perfil sólo para la ciudad.
- `Editor/Env/FacadeGrammar.cs` es código del kit compartido; el cambio de balcones afecta a cualquier reconstrucción
  ENV.
- Rótulos pintados con fuentes de `C:\Windows\Fonts`: sólo look-dev; cambiar a fuentes OFL antes de distribuir.
- `Scenes/CITY/*` (sin versionar) son las escenas del esqueleto del track Mapa F1; no son de este WP; no borrar.
- Las capturas de Ivanix88 (`references/`) no se redistribuyen.

**Trampas de herramientas ya pagadas:** `execute_code` compila C# 6 (CodeDom): sin funciones locales, usar `Func<>`;
borrar assets exige `safety_checks=false`. Tras cambios de código, `refresh_unity` con `mode=force`, `scope=all`,
`compile=request`, y volver a fijar la instancia si hubo recarga. En bash, los heredocs con comillas fallan: escribir
el parche a un `.py` del scratchpad y ejecutarlo. En Blender, bmesh crea la capa UV como `Float2`: pasar por
`uv_sanitize` antes de unir piezas. Los prefabs `CITY_*` tienen el frente en +Z local y el origen en el suelo. Al
remapear materiales de un FBX, crear primero los materiales y remapear sobre un importador recién leído.

## 10. Evidencia y cierre

`Docs/evidence/WP-CITY-IVX-HUMAN-01/`: `DIARIO_PASEO.md` (paso 1), `VIEWS.json` y `views/before_*`, `views/after_*`,
`BUILDINGS.md`, `VINETAS.md`, `assets/` (capturas triples), `FUERA_DEL_CORTE.md`, `LINT.json`, `NAV_PROBE.json`,
`PRE_REVIEW.md`, veredicto del Owner. Cierre según AGENTS: pre-review estricto, SHA congelado, Reviewer fresco.

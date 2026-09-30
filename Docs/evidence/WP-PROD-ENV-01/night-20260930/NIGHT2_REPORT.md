# INFORME NOCHE 2 — 2026-09-30 (censo real → auditor que aprende → fixes por clase → re-censo)

Para: owner (despertar). Orquestador: agente principal ZCode (ojo + mando). Jueces: 8 subagentes de visión + el orquestador (río completo). Estándar aplicado: **KEEPER = el paseo del owner**. La lección de Noche 1 (muestreo≠censo, prompt de confirmación, auditor sin categorías) aplicada de principio a fin.

## Resumen ejecutivo

**El distrito se censo COMPLETO por primera vez**: 356 capturas (38 calles × ambas direcciones a 17,5 m, ojo 1,7 m, 1920×1080; 5 plazas; ambas orillas del río; la escalera al agua), cada una juzgada con el prompt ABSOLUTO de caza. **2.898 defectos** (146🔴 / 1.541🟠 / 1.201🟡; 8,1/captura) frente a los "0 procesables" con que cerró la Noche 1 — esa brecha ERA la lección.

Después se arreglaron **cinco clases** con fix de generador (durable, determinista, validador 0, integridad OK) y el auditor aprendió 7 categorías nuevas con cobertura honesta medida contra el censo. Quedan dos clases grandes (SIN_TERMINAR 378, PUERTA_NEGRA 355 + TEX_WRONG 215) documentadas con evidencia para próximas noches — "mejor dejar un lote sin tocar que dejarlo regular".

## Commits de la noche (`worker/prod-env-01`)

| Commit | Contenido |
|---|---|
| `9473b19` | **B**: censo completo — ledger 356 imgs / 2.898 defectos + resumen por calle |
| `66491ae` | **C**: 7 categorías nuevas en EnvSemantics + cobertura regla-vs-ojo medida |
| `ce585e8` | **D7**: 6 ops de polish huérfanas fuera (missed=0 verificado) |
| `01a7155` | **D2**: río compone — rellano en la escalera al agua, pilares cierran la barandilla, línea de agua real |
| `1b9ae1d` | **D5a**: props con sentido — pase PropLogic + reglas calibradas (PROP_LOGIC 23→0) |
| `2a5d9a0` | **D5b**: línea de gemelos del mirador rota (deuda Noche 1; cornisas a 3 cm medidas) |
| `35b7159` | **D1a**: aprons en 16 finales de calle (5 Salidas + esquinas de hierba en cruces) |
| `b02ee13` | **D6**: SSAO a escala edificio (radio 0,55→1,4 m) — los edificios dejan de flotar |

Tag de seguridad: `checkpoint-noche2-pre-censo`. Backup de escena: `Captures/backups/ENV01_preNoche2_20260930.unity` (113 MB).

## Lote B — EL CENSO (el número que faltaba)

Método: `EnvWalk.Street(id, spacing 17.5, "eye", 1920×1080)` sobre las 38 calles + plazas (8 direcciones desde centro + 4 desde borde) + río (10 estaciones × 2 orillas × 2 miradas) + escalera (2 vistas). Juicio por `analyze_image` con prompt único de caza; exclusiones solo las documentadas (maniquí GC2, franja de losas de la espina). Jueces: 6 subagentes + 2 de rescate (rate-limit 429) + el orquestador como ojo en el río entero y las verificaciones de fix.

Distribución: RENDER 412 · SIN_TERMINAR 378 · PUERTA_NEGRA 355 · SUELO_SEAM 318 · VEG_CLIP 306 · PROP_LOGIC 298 · TEX_WRONG 215 · SUELO_DIRT 177 · ESTRUCTURA 164 · SUELO_PAVE_MISSING 146 · GEMELOS 128. Peores calles: Ronda_Huertas 116, Calle_Alta_E 110, Cantabra 91, Llano 91.

Ledger durable: `Docs/evidence/WP-PROD-ENV-01/night2-censo/ledger.json` + `RESUMEN.md`. Trabajos en `Captures/censo_noche2/` (git-ignored).

## Lote C — el auditor aprende (cobertura honesta)

7 reglas nuevas en `EnvSemantics.cs`: PAVE_MISSING, GROUND_DIRT_IN_STREET, TEX_WRONG_SURFACE, VEG_CLIP, SEAM_NO_KERB, PROP_LOGIC, WALL_PURPOSE. Cobertura medida contra el censo (cono 42°/34 m): **SEAM 67%, PROP_LOGIC 46%, VEG_CLIP 34%, WALL_PURPOSE 15%, PAVE 8%, DIRT 0%, TEX 0%.** Los ceros son hallazgos, no fallos de implementación: la "suciedad" que ve el ojo vive en las TEXTURAS de pavimento viejo (no en quads), y el "adoquín en muro" son UVs estirados (no material de suelo en vertical) — esas clases siguen siendo de ojo. Dos calibraciones honestas durante la noche: GROUND_DIRT disparaba 79× sobre bandas de humedad legítimas (medía transform.up, no la normal); el chequeo de props enterrados usaba cubos fallback de 0,5 m y "enterró" un banco al lado de una bici.

## Lotes D — fixes por clase (qué se arregló y cómo)

**D2 · río** (los "sin sentido" del paseo): rellano de losa al nivel del agua al pie de la escalera (la FEATURE ahora termina en plataforma de lavadero, no en escalones ahogados); pilar de piedra en cada extremo libre de la barandilla del muro (los "pasamanos muriendo en el agua"); banda de algas/línea de agua continua en TODOS los muros del canal (la junta agua-muro ya no es un corte seco). Verificado: fingerprints de filas idénticos, validador 0, ojos en 4 puntos antes/después.

**D5a · props**: pase `PropLogic` en el generador (asientos miran a lo que sirven; pizarra fuera del montón del barril; bici fuera del banco; pote fuera del abrevadero; silla encajada sin función se quita). PROP_LOGIC 23→0 mecánico, verificación de ojo en terrazas.

**D5b · gemelos del mirador** (deuda Noche 1): medidos — K14_1_0/K14_3_0/K14_3_1 con cornisas a 17,50/17,49/17,47 m en una banda de 8° desde el mirador. K14_1_0 gana una planta (19,86 m); la casona no se toca; el par interior ya difería en tejado y carpintería. El ojo confirma la línea rota.

**D1a · suelo**: aprons de 4,5 m en 16 finales de calle que caían en hierba (las 5 Salidas del auditor + 11 esquinas de cruces que su dedup plegaba), en el material propio de cada calle, en 3 tiras que siguen el terreno. PAVE_MISSING 5→3 (restantes = artefactos de muestreo más allá de la línea final). Nueva línea base de suelo: 27+ objetos mesh / 9 materiales (los aprons son adición, nada destruido).

**D6 · render (lo barato sin bake)**: SSAO radio 0,55→1,4 m, intensidad 1,8→1,5. El ojo: arranques asentados, gradientes en portales, sin lodo. Baked GI y presets de color: INTOCABLES (regla dura; solo esta palanca estaba autorizada).

**D7 · limpieza**: 6 ops huérfanas de polish.json eliminadas (ApplyOps missed=0).

## Lote E — re-censo (mismo método absoluto)

27 vistas re-juzgadas con el prompt de caza sobre todo lo tocado (río completo 18, mirador 1, terrazas 3, aprons 5):

| Punto | Antes | Después |
|---|---|---|
| **Escalera al agua** (2 vistas) | 19 | **4** |
| **Orilla oeste del río** (rio_00_L, donde pilar + algas) | 27 | **8** |
| Río resto (14 vistas) | ~129 | 126 (igual: RENDER/horizonte dominan) |
| Mirador skyline | 11 gemelos en el grupo | **0 tripletes de cornisa** (2 hallazgos leves) |
| Terrazas/props (3) | ~30 (sillas a muro, pizarras incrustadas) | 15 (quedan Y leves) |
| Aprons Salidas (5) | calle cortada en hierba | 19 leves (desgaste/AO, ya documentado) |

Nota honesta: con el prompt absoluto NUNCA llega a 0 — siempre queda RENDER/horizonte/tiling. La señal es por-clase y por-punto: ESTRUCTURA del río pasó de "pasamanos al agua/escalones ahogados/junta seca" a detalles menores (farolas en talud sin base Y, "canal corta muro" residual O en tramos donde la banda de algas se ve sutil a distancia). Verificación del orquestador a ojo del punto que el juez marcó peor ("mancha blanca flotante" en rio_00_R): el pilar se ve integrado, banda visible, sin mancha — ruido de juez, no regresión.

## QUÉ VERÁ EL OWNER AL CAMINAR (predicción honesta)

- **El río por fin compone**: la escalera baja a un lavadero de piedra (no se ahoga), la barandilla muere en pilares, el agua besa los muros con algas. Los "aros flotantes" de su paseo eran los remates del rail al aire: hoy tienen pilar.
- **Las salidas del pueblo** terminan en borde construido (adoquín que se estrecha), no en hierba a mitad de piedra.
- **Las terrazas** leen: sillas a su mesa, pizarras de pie junto a su puerta, nada incrustado.
- **Desde el mirador**, la línea triple de cornisas idénticas se rompió: hay un edificio claramente más alto.
- **Los arranques** de edificios tienen sombra de contacto: ya no "flotan" a media tarde.
- **Y seguirá viendo** (trabajo de próximas noches, no maquillaje de esta): puertas a negro sin profundidad (sin GI), fachadas lisas gigantes y remates planos contra el cielo (SIN_TERMINAR 378), transiciones de pavimento sin curso de borde en cruces (318), texturas estiradas (215), manchas de humedad ilógicas en texturas (177). El censo las tiene contadas, localizadas y clasificadas en el ledger.

## Decisiones tomadas por delegación (listadas para revisión)

1. La escalera al agua se ARREGLÓ (rellano + cierre), no se eliminó — era FEATURE diseñada que leía mal (indicación explícita del prompt).
2. Aprons en 16 extremos (no solo los 5 del auditor): el ojo del censo vio hierba en más esquinas de cruce que el dedup mecánico.
3. El edge-course de piedra en seams de 3 materiales quedó PENDIENTE con evidencia: el ojo juzgó las transiciones "reales pero sin terminar" y un flush edge-stone course es tratamiento de otra noche (son 103 seams; mejor 20 perfectas que 103 regulares).
4. D3 (sin terminar) y D4 (texturas) no se tocaron esta noche: son las clases más grandes y merecen noche propia con EnvInteriors y env_masonry. El ledger las tiene listas.
5. Paleta de K14_3_1 probada y REVERTIDA (la familia de fachada por calle de EnvCharacter manda sobre palette — override inerte, se quitó del polish.json).

## Pendientes del owner (listar, no decidir)

1. Paquete `com.unity.pipeline` 0.8.0-exp.1 (¿se queda?).
2. Las 3 limitaciones cosméticas del lenguaje del casco (persiana sobre cristal, juntas sillar/marcos, flancos ciegos traseros).
3. Baked GI / ciclo día-noche (fuera de alcance; medioamedio con SSAO mientras tanto).
4. PERIM_A y retune del route probe.
5. Revisor independiente + freeze SHA del AGENTS.md antes de merge (PR #10).
6. NUEVO de esta noche: decisión sobre edge-courses en seams (evidencia en d1_suelo) y el orden de D3 (puertas con profundidad) / D4 (UV estirados) para la Noche 3.

## Estado técnico al cierre

Escena `ENV01_Casco_District` guardada (isDirty=false), reconstruida completa 2 veces esta noche desde spec+polish+código (determinista: fingerprints K1_1/K8_3/K15_12 idénticos antes/después de cada cambio de generador). EnvValidator 0 problemas. Ground 27+/9 (aprons añadidos), PavingOverlays 4/3, Plazas 30/18. Editor `JuegoDef@9bfcb657` operativo. Todo pushed a `worker/prod-env-01` (PR #10).

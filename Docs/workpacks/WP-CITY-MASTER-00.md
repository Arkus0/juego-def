# WP-CITY-MASTER-00 — Plan maestro del Mapa F1 (escala Kamurocho) + enmiendas de escala e interiores

Status: **WORKER CANDIDATE / READY FOR INDEPENDENT REVIEW (docs only)**
Class: PRODUCT PLANNING / CITY MASTER PLAN / DOCS ONLY
Owner brief: 2026-10-01 — dirección de level design, world design y producción de entornos de la ciudad completa; decisiones D1–D6 registradas en [`CITY_MASTER_PLAN_V1.md`](../design/CITY_MASTER_PLAN_V1.md#1-decisiones-del-owner-registradas-2026-10-01).
Depends on: `WP-CITY-URBAN-00` PASS + `WP-CITY-URBAN-00R` PASS (presupuestos y gramática consumidos, no reabiertos salvo la enmienda de accesibilidad pedida por el Owner).
Blocks: `WP-CITY-SKELETON-00` (Fase 0) y `WP-CITY-B0-01` (Fase 1).
Supersedes: el papel de `WP-PROD-ENV-CASCO-V2-00` como primera falsificación física de CITY-00R (decisión D2) y la PR #22.

## Objetivo / claim

Entregar el primer entregable pedido por el Owner: diagnóstico del estado real, plano global a escala con relieve y masas, grafo de rutas y clases de acceso, distribución de las cinco identidades, inventario de edificios semánticos e interiores, anclas, espacios de actividad, loops, oportunidades, costuras de expansión, métricas iniciales, riesgos y plan por sectores con criterios de aceptación. Registrar las enmiendas del Owner: **Mapa F1 a escala Kamurocho con crecimiento reservado hasta escala Ijincho**, **mayoría de interiores accesibles (objetivo 60 %)** e **interconexión por capas tipo Sapienza**; reordenar la hoja de ruta: Fase 0 esqueleto global → Fase 1 B0 → sectores → integración.

Este WP prueba un plan coherente con los presupuestos aceptados y medible de forma reproducible. **No** prueba una ciudad jugable ni sustituye las mediciones en Unity: la escena authored de la Fase 0 pasa a ser la autoridad espacial.

## Dependency check

| Entrada | Consumo / garantía | Nuevo / razón para reabrir |
|---|---|---|
| CITY-00 PASS | U01–U07 (U08 opcional), cinco usos, B0 L/A/S/E/P/Q/O/V + B01–B10, ciclos, verdad de accesos y cotas relativas | posiciones concretas dentro de la ciudad compacta; ninguna adyacencia reabierta |
| CITY-00R PASS | gramática `FacadeCell ≠ SemanticBuilding ≠ InteriorProgramme`, 0 residuales, ≥2× entre identidades, vecinos ≤180 m, profundos ≤20 % | **enmienda Owner**: topes de Mapa F1 (≤150.000 m², red ≤3.600 m, ≤240 edificios con CASCO ≤50, extremo ≤900 m) y mayoría accesible (60 %); el esquema 300 × 200 se sustituye por el plano v1.2 |
| PR #25 ENV01_AUTHORED (cadena ENV, no main) | ENV01 authored, kit y herramientas como donantes | ENV01 deja de ser candidato a CASCO in situ (decisión D1) |
| Estado Unity (bfda1ad) | GC2 Core sólo, AI Navigation instalado sin uso, Player y cámara medidos | ninguna |

## Entregables

- [`Docs/design/CITY_MASTER_PLAN_V1.md`](../design/CITY_MASTER_PLAN_V1.md) — primer entregable completo.
- [`Docs/design/city/city_plan_v1.json`](../design/city/city_plan_v1.json) — registro de planeamiento v1.2 (zonas, nodos, red pública, capa de interconexión, puntos verticales, espacios abiertos, costuras, 200 edificios, oportunidades, espacios de actividad).
- `Tools/city_plan.py` — `metrics` (comprobaciones reproducibles) y `render` (planos a escala).
- `Docs/design/city/CITY_PLAN_V1_masas_relieve_red.png`, `CITY_PLAN_V1_interconexion.png`, `CITY_PLAN_V1_programa.png`.
- Enmienda de accesibilidad en `COMPACT_SEMANTIC_CITY_REBASELINE.md` + notas de vigencia en `PORT_TOWN_WORLD_MODEL.md`, `CITY_PRODUCTION_KNOWLEDGE.md`, `FIRST_KEEPER_BLOCK_B0.md`, `CITY_URBAN_00_HANDOFF.md`; estado de `WP-PROD-ENV-CASCO-V2-00` y `WP-CITY-URBAN-01`; `ROADMAP.md` y `Docs/workpacks/README.md`.
- `WP-CITY-SKELETON-00.md` y `WP-CITY-B0-01.md`.
- Evidencia: `Docs/evidence/WP-CITY-MASTER-00/` (métricas, pre-review).

## Aceptación

1. `python Tools/city_plan.py metrics` termina con `all_checks_pass: true` frente a los topes F1: envolvente ≤150.000 m², red pública (incluidos ejes exteriores PUB-H) ≤3.600 m, edificios ≤240 (CASCO ≤50), vecinos ≤180 m, extremo ≤900 m, mayor/menor ≥2, accesibles ≥60 % (>50 % duro), profundos ≤20 %, red conectada, IDs únicos, ≥3 capas extra por identidad y ganancia de alternativas en los pares clave.
2. Todo eje de servicio, condicionado o sin salida aparece declarado aparte; nada se esconde para cumplir la red.
3. B0 conserva anclas, aristas, ciclos y la ruta directa vs alternativa con experiencias distintas; U01–U07 presentes.
4. Los 200 edificios tienen identidad y uso (incluidos los 80 cerrados); los 15 grandes tienen programa con ocupación, estancias, accesos y oportunidad.
5. Oportunidades y actividades marcadas como **preparadas espacialmente**, nunca como gameplay implementado.
6. Costuras Y1–Y5 con corredor reservado y cierre honesto hacia la escala Ijincho; X1–X4 absorbidas por el anillo F1; ninguna calle invisible transitable.
7. Cada enlace de la capa de interconexión declara capa, acceso, condición y uso; ninguno es requisito de conectividad pública.
8. Las enmiendas (escala F1, accesibilidad, interconexión) y el reordenamiento de la hoja de ruta son explícitos y localizados; no se reabre nada más de CITY-00/00R.

## Forbidden scope

Implementación Unity, conversión de ENV01, cambios en la escena de ENV01 o en el trabajo DENSITY-01, Director/MAST, generadores automáticos de ciudad o interiores, compras, nombres keeper definitivos, cierre de PR ajenas sin OK del Owner.

## Definition of Done

Bytes de docs completos; `metrics` y `render` reproducibles; pre-review estricto del Worker sobre el diff completo; SHA congelado; Reviewer fresco. La revisión no rehace Unity ni pruebas de producto.

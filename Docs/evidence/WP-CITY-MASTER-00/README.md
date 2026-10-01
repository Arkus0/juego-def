# WP-CITY-MASTER-00 — evidencia

Status: **WORKER READY FOR INDEPENDENT REVIEW** (no es PASS independiente)
Date: 2026-10-01
Branch: `docs/city-master-plan-v1` desde `origin/main` `eacdd58`. Docs y herramienta de medición; sin bytes Unity.

## Dependency check

| Prerrequisito | Estado / SHA | Garantía consumida | Nuevo en este WP | Reabrir si |
|---|---|---|---|---|
| `WP-CITY-URBAN-00` | PASS (main) | U01–U07, B0 L/A/S/E/P/Q/O/V + B01–B10, ciclos, verdad de accesos, cotas relativas | posiciones dentro del Mapa F1 | una adyacencia resulta físicamente imposible en la escena |
| `WP-CITY-URBAN-00R` | PASS (PR #19, `8a37179`) | gramática de unidades, 0 residuales, ≥2× entre identidades, vecinos ≤180 m, profundos ≤20 % | enmienda Owner: topes F1 y accesibilidad 60 % | — (enmienda explícita del Owner) |
| PR #25 `ENV01_AUTHORED` | merged en `worker/casco-diag-01` (`bfa9da4`, DocSync `bfda1ad`), **no en main** | kit ENV y ENV01 como donante | ENV01 deja de ser candidato a CASCO in situ | — |
| Estado Unity en `bfda1ad` | inspección read-only | GC2 Core 2.19.61 únicamente; AI Navigation instalado sin uso; Player 2,0 × 0,2, 4 m/s, slope 45°, step 0,3; cámara 3 m FOV 55 | — | si la Fase 0 mide otra cosa |

Decisiones del Owner tomadas durante la planificación (2026-10-01): ENV01 donante en escena nueva; B0 absorbe el piloto CASCO-V2-00; los grandes adicionales; ciudad mayor con espacio para zonas futuras; interconexión tipo Sapienza; **Mapa F1 a escala Kamurocho con crecimiento hasta Ijincho**. Registradas en `CITY_MASTER_PLAN_V1.md §1`.

Reuse/research: consumido `Docs/research/EXISTING_ASSET_PIPELINE_RESEARCH.md` y `REUSE_DECISIONS.md` de ENV01; disposiciones en `CITY_MASTER_PLAN_V1.md §16`. Sin dependencias nuevas adoptadas en este WP (ProBuilder queda para la Fase 0, con verificación de versión/licencia).

## Reproducción

```text
python Tools/city_plan.py metrics --out Docs/evidence/WP-CITY-MASTER-00/METRICS.json   # exit 0 = todas las comprobaciones pasan
python Tools/city_plan.py render                                                        # 3 planos en Docs/design/city/
```

`METRICS.json` (versión 1.2): envolvente 121.568 m² · identidades CASCO 31.526 / VIVIENDAS 29.452 / MERCADO 24.620 / MUELLE 23.316 / TALLERES 12.654 (2,49×) · red pública 2.973 m, con ejes exteriores PUB-H 3.209 m · 57 ejes, 43 nodos, 15 ciclos, conectada · vecinos 97–176 m · extremo 759 m · 200 edificios (CASCO 45), 120 accesibles (60 %), 15 profundos (7,5 %) · 41 enlaces de capa (1.959 m caminables), 10 puntos verticales · 4–5 capas extra por identidad · `all_checks_pass: true`.

Fuentes de escala de referencia (sin cifras oficiales en m²): Ijincho ≈ 3× Kamurocho ([Gematsu](https://www.gematsu.com/2019/12/yakuza-like-a-dragon-details-the-areas-of-isezaki-ijincho), [PSU](https://www.psu.com/news/like-a-dragon-infinite-wealth-hawaii-map-is-3-times-as-big-as-yakuza-like-a-dragons-isezaki-ijincho/)); Kamurocho se cruza andando en ~9:20 y corriendo en ~2:36 ([How Big is the Map](https://howbigisthemap.com/yakuza-0-run-across-the-map-map-1/)). La estimación de 0,12–0,15 km² para Kamurocho es del Worker.

## Strict Worker pre-review

Intento de falsar el propio candidato:

1. **¿Se cumplen los topes escondiendo red?** No: los ejes exteriores públicos por horario (Callejón del Tinte, patio del instituto, grada del campo, senda de las rocas) se suman al tope (3.209 ≤ 3.600). Interiores, servicio, privados, controlados y PROG se declaran por capa en `METRICS.json`. El espigón se declara como espacio abierto sin salida.
2. **¿Un interior sostiene la conectividad pública?** No: la red pública es un solo componente sin enlaces de capa; los pares clave tienen ruta pública salvo muelle → varadero, que es deliberadamente laboral/controlado y así se declara.
3. **¿Se infla la accesibilidad?** El 60 % cuenta edificios únicos; las casas visitables son PRV por invitación y cuentan sólo si se construyen recorribles (criterio de los WPs de sector). Riesgo real: 120 interiores es el mayor coste; mitigado con kit de interiores probado en B0 antes de escalar. No se cuenta ninguna habitación simulada.
4. **¿La escala Kamurocho es tejido vacío?** Riesgo declarado (§14.2–3): ≈89.000 m² de suelo de manzana que la Fase 0 debe particionar con función. Se añadió actividad propia a cada parte del anillo (estación, cine-bingo, playa, campo, conservera, faro, ermita, instituto).
5. **¿B0 sigue siendo B0?** Anclas, B01–B10, ciclos A–S–E–O–V–A y E–P–Q–O–E, ruta directa (187 m) vs alternativa por terraza (184 m) con experiencias distintas, borde público P–Q separado del patio CTL y del muelle de armadores SRV, costuras arrival_w/casco_n/homes_ne/quay_e conectadas.
6. **¿Se reabre algo no pedido?** Sólo topes de escala, accesibilidad e interconexión (decisiones explícitas del Owner) y el estado del piloto CASCO-V2 (decisión D2). U01–U07, la gramática de unidades, 0 residuales, 70/20/10 como intención y GC2 se mantienen.
7. **¿Se tocó trabajo ajeno?** No: worktree propio desde `origin/main`; el checkout con DENSITY-01 sin commitear y `ENV01_AUTHORED` no se modifican. Las PR #23/#24 sólo se señalan; no se cierran.
8. **Enlaces y datos:** enlaces relativos de todos los documentos tocados verificados (0 rotos); IDs de edificio únicos; los planos se regeneran desde el JSON.

Límites conocidos: coordenadas, longitudes con factor de curvatura y curvas de nivel son de planeamiento; la Fase 0 re-mide todo desde la escena. Las capas de agua no caminables (lancha, traineras) y los accesos por horario/progreso son preparación espacial, no mecánicas.

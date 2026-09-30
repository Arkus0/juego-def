# INFORME DE NOCHE 1 — 2026-09-29 (semántica + anti-procedural, ENV01_Casco)

Para: owner (despertar 05:00). Orquestador: agente principal ZCode (ojo visual + mando). Operadores: 3 subagentes (1× Fase 2 Unity, 1× mapeo solo-lectura, 1× Fase 3 Unity). Estándar aplicado: **KEEPER + CERO REGRESIÓN** — lo que se queda es keeper o se revierte.

## Resumen ejecutivo

**Los dos objetivos de la noche están completos y verificados.** Semántica: 45 hallazgos → 0 procesables (los 3 restantes son legítimos, verificados a mano por el ojo). Anti-procedural: la monotonía sistémica rompida con variación determinista por seed. Pavimento intacto toda la noche, verificado independientemente al cierre. 23 capturas juzgadas visualmente por el ojo (20 ✅ / 1 retoque-hecho-y-reverificado / 2 falsos positivos de auditor confirmados / 1 deuda nueva: gemelos).

## Commits de la noche (branch `worker/prod-env-01`)

| Commit | Contenido |
|---|---|
| `e97332a` | f2 lote1: SeatOnGround (escalones crecen hasta pavimento, props se asientan) |
| `ea8e986` | f2 lote2: parapets de piedra cierran Plaza_Río + Mirador (25 piezas) |
| `2fe9d32` | f2 lote3: 6 finales de fila abiertos → `tip_keep` en spec |
| `f99db10` | f2 lote4: escalinata Obispo alargada hasta su umbral |
| `6b9f9ed` | f2 lote4b+5: Solana revertida (falso positivo); K6_11 ventanas en muro muerto |
| `8f52056` | f2 lote6: 2 portales muertos→ventana; puerta en muro de huerta K16_6 |
| `989d33e` | docs: informe de palancas Fase 3 (métrica, cotas, 8 quick-wins, regla RNG) |
| `91d122c` | f3 lote1: K6_11 alineado a línea de alféizar + banda de piedra cruzando costura |
| `deb43e4` | f3 lote2: **fix métrica RHYTHM_MONO_LINTELS** (los 22 eran bug: medía el muro) |
| `42d6f74` | f3 lote3: suites de ventana Hi/Lo (Blender headless; 440 Hi + 452 Lo; 5 dinteles) |
| `4824875` | f3 lote4: jitter rótulos, hierro balcón 3 colores, odd window 15%, fascia, toldos |
| `0e8ef29` | f3 lote5: persianas roller 3 posiciones (72/82/66) |
| `5165133` | f3 housekeeping (materiales regenerados + re-serialización, sin cambios de autor) |

Tag de seguridad: `checkpoint-night-pre-fase2` (pre-noche). Backups de escena: `Captures/backups/ENV01_preFase2_20260929.unity` y `ENV01_preFase3_20260929.unity` (118 MB cada uno).

## Fase 2 — Semántica (detalle)

- **Escalones flotantes ×4 + barril**: nuevo pase `SeatOnGround` enganchado a `Finish` — la granita crece hacia abajo hasta el pavimento en pendiente; los props se asientan en ambas direcciones. Ojo: bloques creíbles, sin floats.
- **Plazas abiertas ×2**: Plaza_Río (este+orilla) y Mirador cerrados con parapets de piedra de 2 m. Ojo: balaustradas creíbles, el mirador ahora lee como espacio público definido.
- **Volume-gaps ×6**: `ends: open → tip_keep` en spec + rebuild de fila. Quoin+inglete verificado en K13_5. El "edificio cortado por la mitad" de K1_5 ya no existe.
- **Escaleras**: Obispo extendida 1,1 m hasta su umbral (ojo: desemboca en la puerta). **Solana revertida** — falso positivo: su puerta abre al borde de la escalera-calle 0,2 m bajo el peldaño; el auditor ahora exige alineación vertical + línea de paso.
- **BLANK_WALL ×4**: veredictos del ojo — K6_11 DEFECTO (arreglado), K15_12_5+6 / K15_12_6+7 / K14_10_1 LEGÍTIMOS (medianeras creíbles, rotas visualmente por bajantes/zócalos/programas). No se tocan.
- **Sueltos**: 2 portales a la nada → ventanas (K2_13_0, K13_5_0); muro de huerta de 9,4 m → puerta timber en el spec; K6_10_1 ya tenía balcón (el auditor de relieve ahora ve las piezas de polish).

## Fase 3 — Anti-procedural (detalle)

- **Hallazgo crítico**: RHYTHM_MONO_LINTELS medía el tope del MURO (3,00 m), no el dintel — 22 falsos hallazgos. La varianza real ya existía (4 valores por familias de módulo). Métrica arreglada → 0.
- **Suites Hi/Lo** (el cambio gordo): módulos Blender con cabeza 2,41/2,21, cortados sobre muro limpio, una línea por edificio por hash dedicado (28% Hi / 25% Lo / 47% kit; `neglected` solo Lo). Persianas exteriores solo con cabeza kit; la roller cubre cualquier línea. En escena: 5 valores de dintel. **Determinismo probado** (fingerprint de fila idéntico tras rebuild).
- **Quick-wins** (todos con hash dedicado, RNG compartido intacto): rótulos ±0,10 m (111 alturas distintas), hierro de balcón Negro 40/Azul 31/Verde 11, ventana "odd" en 15% de edificios (14 colores de carpintería), fascias 0,9–1,1 (21 valores), toldos 6 canvases + jitter de escala, persianas roller en 3 bajadas.
- **Verificación del ojo en 8 vistas fijas antes/después**: espina este y comercios **MEJOR** (heterogeneidad natural, ventanas sin persiana leen como piedra/reformado, hierros sutiles); plaza del río, calle alta y callejón del arco **LIMPIOS**; K6_11 **REPARADO** (banda lee como curso de piedra natural, no parche).

## Cero regresión — verificación final independiente

- Ground **11 renderers / 9 materiales**, PavingOverlays **4/3**, Plazas **30/18** — idénticos al baseline, comprobado por el orquestador con consulta directa al editor tras el cierre (no solo reporte del operador).
- EnvValidator 0 (documentado en cada commit de rebuild). Auditoría final: 3 = solo los BLANK_WALL legítimos.
- Escena guardada (isDirty=false), editor re-pineado y verificado tras la caída de mitad de noche del operador.
- 1 falso positivo detectado y revertido por el propio operador (Solana) — el sistema keeper funcionó.

## Pendiente / decisiones del owner

1. **Anti-clonación (deuda nueva, preexistente)**: 3 edificios gemelos en fila (misma cornisa, ritmo 2-1-2, mismo estuco) visibles en el skyline desde el mirador. Confirmado preexistente (no regresión de la noche). El auditor tiene categoría TWIN; falta palanca de variación de cornisa/ritmo anti-colapso entre vecinos. **Recomendación: próxima noche empieza aquí** — cierra la última cara del "parece IA".
2. **Paquete `com.unity.pipeline` 0.8.0-exp.1**: sigue commiteado desde Fase 0; el handoff lo dejaba a decisión del owner.
3. **3 limitaciones cosméticas documentadas** (persiana sobre cristal, juntas sillar/marcos, flancos ciegos traseros): no tocadas.
4. **6 ops de polish huérfanas** (silla Cimavilla, 3 pizarras, barril, banco de noches previas): sus objetivos ya no existen tras el rebuild completo; auditor de props a 0, sin conflicto, pero conviene limpiarlas o re-apuntarlas.
5. **Técnicos menores**: `env_textures.py` no es byte-determinista entre entornos (10 texturas restauradas a las commiteadas); barra frontal de toldo a escala 0,95 queda en 1,94 m (pasa persona; la cota 2,15 era estimada); deriva spec↔escena (K2_9) cerrada por el rebuild completo — el spec es la verdad.
6. **Del handoff previo**: PERIM_A y retune del route probe siguen pendientes.
7. **Próximas noches (propuesta de roadmap)**: N2 anti-clonación → N3 Fase 4 diversión (route beats 20–40 m, sightlines, landmarks) → N4 ensanches de calle (anchos oficiales, per-street con commits) → N5 verificación + cierre + revisor independiente (AGENTS.md).

## Cómo reanudar (sesión siguiente)

Todo el estado está en `worker/prod-env-01` + este directorio. Capturas de juicio: `Captures/fase2/` y `Captures/fase3/` (antes/despues con 8 ojos fijos). Auditorías: `Captures/semantics/phase2_final4.json` y `phase3_lote5.json`. Backups de escena en `Captures/backups/`. La escena es gitignored y se regenera del spec; el estado duradero son specs + código + `polish.json`.

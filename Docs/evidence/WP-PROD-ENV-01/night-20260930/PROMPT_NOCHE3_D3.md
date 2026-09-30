# PROMPT — Noche 3: SIN_TERMINAR 378 (paste-ready)

> Pegar este bloque completo como primer mensaje de la sesión nueva.

---

Eres el orquestador nocturno de juego-def. El owner duerme; te deja el mando hasta las ~5am con informe detallado al despertar. Esto CONTINÚA la Noche 2 — mismo modelo de trabajo, mismas costumbres.

## Modelo de trabajo (innegociable — como Noches 1 y 2)

- **VISIÓN ANTES QUE CÓDIGO**: cada decisión de "qué está mal" y "está arreglado" nace de MIRAR IMÁGENES a pie de calle. Las reglas son el segundo par de ojos.
- **TÚ eres el ojo**: `Read` de la captura → URL CDN → `analyze_image`. Prompt ABSOLUTO para cazar ("cataloga TODO defecto sin piedad"), nunca de confirmación. Examina con tiempo.
- **Subagentes frescos y autocontenidos** para trabajo sin Unity (juicio de imágenes en JSONL por append, prompt VERBATIM idéntico). Solo UN agente toca el editor. Perfección por unidad antes que cobertura.
- **INFORMA CON CADA FASE** (el owner lee desde TG). Commit tras cada gran fase.
- **KEEPER = el paseo del owner**. Cero regresión: fix que no mejora claramente → revert.

## La lección de la Noche 2 — ya pagada, no la repitas

El censo completo existe: **356 capturas / 2.898 defectos** en `Docs/evidence/WP-PROD-ENV-01/night2-censo/ledger.json` (trabajos en `Captures/censo_noche2/`). NO re-censes lo ya censado: usa el ledger. Y la lección de toolchain cobrada tres veces: **`refresh_unity` vuelve ANTES de recompilar** — tras cada edit+refresh, `sleep ~22s` y verifica un MARCADOR de versión leído del console antes de confiar en cualquier invocación; la reflexión `GetMethod != null` NO basta. Ver `juegodef-unity-toolchain-traps` en la memoria o el informe de N2.

## Contexto

Repo `C:/Juego Def`, branch `worker/prod-env-01` (PR #10, pushed hasta `f249971`). Proyecto Unity `C:/Juego Def/Unity/JuegoDef` (6000.3.24f1, URP, GC2). Escena `ENV01_Casco_District.unity` GENERATED del spec, gitignored — cambios durables en spec (`Env/Specs/districts/ENV01_Casco_District.json`), `polish.json` y código (`Assets/JuegoDef/Editor/Env/`).

**LEE PRIMERO**: `Docs/evidence/WP-PROD-ENV-01/night-20260930/NIGHT2_REPORT.md` (qué se arregló y cómo), `night2-censo/ledger.json` (TU backlog), `Docs/production/ENV_COMPOSITION_RULES.md` (las look rules tras la auditoría de 45 puntos: "no kit formula on every house", familias por calle, weathering CON CAUSA), `ENV_FACTORY.md`, y el catálogo de palancas `night-20260929/PHASE3_VARIATION_LEVERS.md`.

## LA ANATOMÍA DEL ENEMIGO (del ledger, no de la intuición)

SIN_TERMINAR = 378 (1🔴/342🟠/35🟡). Se descompone:
1. **362 × "fachada/muro liso o plano"** — extensiones grandes de estuco/revoco SIN nada que las rompa (sin bajadas, sin líneas de pintura, sin reparaciones, sin capa contemporánea). Es el "fachadas gigantes lisas" del paseo del owner. OJO: el 90% son 🟠 — es la clase que hace que el pueblo lea "generado" en lugar de "vivido".
2. **9 × sin alero/cornisa contra el cielo** — edificios que acaban planos.
3. **1 🔴 en Ribera** — interior visible por un portal con paredes y suelo planos sin textura (caja sin terminar).
4. Resto: 1 caja que cierra calle, remates sueltos.

Peores calles: Ronda_Huertas 20, Calle_Alta_E 16, Cantabra 15, Llano 15, Ribera 15, San_Pedro+Salida 28, Capitan_Salida 12, Espina_E 12.

**Lo que ya existe y NO hay que inventar**: `FacadeGrammar.Weathering` (manchas CON CAUSA: Downpipe/Sill/Rust/Corner/Damp/Algae/Repair/Soot, densidad por condición), capa `Contemporary` (aires, alarmas, porteros, números, extractores, cables), `EnvCharacter` (familias por calle: render/zocalo/stone_ground/stone/rehab/modern), plintos por familia, quoins/surrounds, suites de ventana Hi/Lo y demás palancas de Fase 3. El problema NO es que falten piezas: es que en demasiadas fachadas NO SE COMBINAN (revoco limpio de 3 plantas seguidas).

## Reglas duras

- Editor MCP: SOLO `JuegoDef@9bfcb657` (`set_active_instance`; verificar `manage_scene get_active` tras cada reconexión; worktree characters-01 PROHIBIDO). Si el editor está cerrado: `"C:\Program Files\Unity\Hub\Editor\6000.3.24f1\Editor\Unity.exe" -projectPath "C:\Juego Def\Unity\JuegoDef"`; si se clava a ~57MB con log 0 bytes: matar, borrar `Temp/UnityLockfile`, relanzar.
- JAMÁS `EnvDistrict.RebuildGround`. NO tocar lighting/paquetes/presets (el brillo de interiores `interiorDim` es LIGHTING — intocable; la geometría/material del hueco sí es tuyo). No tocar `C:\Juego Def-ENV01-local-20260928`.
- `execute_code` no marca dirty: MarkSceneDirty+SaveScene tras cada mutación.
- **Regla de oro del RNG**: NUNCA dibujar del `rng` compartido (`BuildingAssembler.cs:117`) ni añadir/quitar llamadas `rng.Next*` existentes — sorteos nuevos con hash dedicado (`Hash01(x,z,const)` o `seed*primo+const`). Determinismo: `EnvPolish.Fingerprint` de 2-3 filas antes/después de CADA cambio de generador; si cambia el fingerprint sin querer, revert y repensar.
- `MeshObject` borra el asset por NOMBRE — nombres únicos siempre.
- Los 3 BLANK_WALL legítimos de Noche 1 (medianeras verificadas a ojo) NO se tocan. Y "liso" ≠ "mal": una casa reformada limpia es correcta — el defecto es la REPETICIÓN a lo largo de una calle. Juzga por tramo de calle, no por fachada aislada.
- Backup de escena a `Captures/backups/ENV01_preNoche3_<fecha>.unity` + tag antes de operar. Atascado 2 intentos → documentar y saltar.

## Misión (en orden)

**LOTE A — Arranque**: lecturas; pin del editor; verificar estado (integridad: Ground 27+/9 con aprons, PavingOverlays 4/3, Plazas 30/18); backup + tag.

**LOTE B — EL MAPA DEL LISO**: del ledger, extrae los 362 hallazgos a un working set (`Captures/n3_sinterminar/workset.json`) con calle, estación y gravedad. Muestrea CON TUS OJOS 12 fachadas representativas (las peores calles, 2 vistas c/u) y clasifica QUÉ falta en cada una: ¿bajante? ¿banda de humedad/reparación? ¿capa contemporánea? ¿zócalo? ¿surrounds? ¿2 tonos de pintura? ¿persianas/roller? Con eso escribe la RECETA por familia de calle (qué combinación, con qué densidad, respetando "no kit formula on every house" — el 10-20% de casas limpia es CORRECTO).

**LOTE C — EL GENERADOR VESTE LAS PAREDES**: implementa en `FacadeGrammar.Weathering`/`Contemporary`/`EnvCharacter` la palanca de "densidad de vida por fachada": una fachada de revoco con extensión de superficie lisa > X m² sin interacción acumula capas CON CAUSA hasta romper la lectura (hash dedicado por edificio+planta, NUNCA rng compartido). Palancas candidatas (elige con los ojos, no todas): línea de repintado a media altura (2 tonos del mismo render), tramo reparado con tono distinto, bajante donde el alero lo permita (no en solanas), ampliar Contemporary a fachadas residenciales (hoy parece denso solo en comerciales), cables/tendido telefónico en cornisa. Rebuild completo → fingerprints → validador → **re-censo con prompt absoluto de las 12 fachadas del Lote B + 20 estaciones al azar de las peores calles** → compara clase SIN_TERMINAR por estación contra el ledger. Commit.

**LOTE D — LOS EXTREMOS** (pequeño y quirúrgico): los 9 sin alero contra el cielo (¿`BuildingSpec.eave` sin resolver en esos edificios? ¿paleta reformada sin canecillos? — identifica los casos concretos desde el ledger, revisa el generador de aleros, fix determinista) y el 🔴 de Ribera (interior plano tras portal: la caja que se ve por la puerta — darle el interior falso de EnvInteriors o cegar con hoja). Commit.

**LOTE E — Cierre**: re-censo final del tramo trabajado, informe a `Docs/evidence/WP-PROD-ENV-01/night-20260931/` con antes/después por estación, QUÉ VERÁ EL OWNER AL CAMINAR, decisiones por delegación y el estado de las clases restantes (PUERTA_NEGRA 355 y TEX_WRONG 215 siguen en el ledger como candidatas a Noche 4; SUELO_SEAM 125 espera los edge-courses). Push.

Pendientes del owner (listar, no decidir): paquete com.unity.pipeline; 3 limitaciones cosméticas; baked GI; PERIM_A y route probe; revisor independiente; decidir N4 (PUERTA_NEGRA vs TEX_WRONG vs edge-courses).

Empieza por el Lote A e informa conforme avances.

# PROMPT — Noche 2 (paste-ready)

> Pegar este bloque completo como primer mensaje de la sesión nueva.

---

Eres el orquestador nocturno de juego-def. El owner duerme; te deja el mando hasta las ~5am con informe detallado al despertar. Esto CONTINÚA la Noche 1 — mismo modelo de trabajo, mismas costumbres.

## Modelo de trabajo (innegociable — es como trabajó la Noche 1)

- **VISIÓN ANTES QUE CÓDIGO**: cada decisión de "qué está mal" y "está arreglado" nace de MIRAR IMÁGENES a pie de calle ("esto no se arregla con código sino visualmente"). Las reglas y métricas son el segundo par de ojos, nunca el primero. Bucle ojo→regla: cuando el ojo caza una clase nueva de defecto, se convierte en categoría del auditor.
- **TÚ eres el ojo**: `Read` de la captura → URL CDN → `analyze_image`. Examina las imágenes con tiempo — es tu función principal, no un trámite.
- **Crea los subagentes que necesites** (frescos, no-fork, prompts autocontenidos; no tiene que ser el mismo). Solo UN agente toca el editor Unity a la vez; el paralelismo va en trabajo sin Unity. Perfección por unidad antes que cobertura: "lo que se haga que sea perfecto" — hay muchas noches, mejor dejar un lote sin tocar que dejarlo regular.
- **INFORMA CON CADA FASE**: el owner lee desde el bot de TG. Cada fase cierra con mensaje claro (qué se hizo, qué se encontró, qué sigue, dudas). Las dudas las resuelves tú con criterio (delegación explícita) y las listas en el informe.
- **Estándar KEEPER = el paseo del owner**: "pueblo creíble y terminado a pie de calle". Nunca "sin regresión respecto a ayer". Cero regresión: fix que no mejora claramente → revert. Commit tras cada gran fase.

## La lección de la Noche 1 — interiorízala

La Noche 1 arregló sus 45 hallazgos semánticos y declaró "keeper" — y el owner caminó y encontró fallos de todo tipo (8 capturas, 113 hallazgos). Causas: (1) se juzgaron 8 ojos fijos escénicos elegidos por el operador, no TODAS las calles (muestreo≠censo); (2) los prompts preguntaban "¿el fix lee bien?" — sesgo de confirmación: con el prompt duro "cataloga TODO defecto sin piedad" el mismo distrito da 9-19 defectos por captura; (3) el auditor no tenía categorías de suelo/textura/composición y la "integridad" (contar renderers) verifica que nada se destruyó, no que el contenido sea correcto.

## Contexto

Repo `C:/Juego Def`, branch `worker/prod-env-01` (PR #10, pushed hasta `54d719c`). Proyecto Unity `C:/Juego Def/Unity/JuegoDef` (6000.3.24f1, URP, GC2). Escena `Assets/JuegoDef/Scenes/ENV/ENV01_Casco_District.unity`: GENERADA del spec (~30s), gitignored — cambios durables en spec (`Assets/JuegoDef/Env/Specs/districts/ENV01_Casco_District.json`), `polish.json` y código (`Assets/JuegoDef/Editor/Env/`).

**LEE PRIMERO**: `Docs/evidence/WP-PROD-ENV-01/night-20260929/` (NIGHT_REPORT.md, HANDOFF_NIGHT2.md con el catálogo completo de defectos del paseo del owner, PHASE3_VARIATION_LEVERS.md con la regla de oro del RNG), `Docs/production/ENV_COMPOSITION_RULES.md`, `ENV_FACTORY.md`, `Docs/evidence/WP-PROD-ENV-01/CASCO_REFERENCE_STUDY.md`. Nota: la escalera-al-agua de la plaza del río es FEATURE diseñada que hoy lee mal — arreglar su lectura (rellano, cierre), no eliminarla.

## Reglas duras

- Editor MCP: SOLO `JuegoDef@9bfcb657` (`set_active_instance`; verificar `manage_scene get_active` tras cada reconexión; el worktree characters-01 está PROHIBIDO).
- Si el editor está cerrado: `"C:\Program Files\Unity\Hub\Editor\6000.3.24f1\Editor\Unity.exe" -projectPath "C:\Juego Def\Unity\JuegoDef"`. Si se clava a ~57MB con log 0 bytes hay `Temp/UnityLockfile` huérfano: matar proceso, borrar lock, relanzar.
- JAMÁS `EnvDistrict.RebuildGround`. No tocar lighting/paquetes. No tocar `C:\Juego Def-ENV01-local-20260928`.
- `execute_code` no marca dirty: MarkSceneDirty+SaveScene tras cada mutación. FixBlockedOpenings/SeatOnGround corren en Finish, no en RebuildRow.
- Si tocas generadores: RNG dedicado, nunca el compartido (`BuildingAssembler.cs:117`).
- Backup de escena a `Captures/backups/` antes de operar + tag git. Atascado 2 intentos → documentar y saltar.

## Misión (en orden)

**LOTE A — Arranque**: lecturas, pin del editor, verificar estado, backup, tag.

**LOTE B — CENSO REAL**: estaciones cada 15-20m en TODAS las calles (~38, ambas direcciones, ojo 1,7m, capturas ≥1920px), plazas y orilla del río incluidas. Juzga CADA captura con prompt absoluto de caza (ubicación y gravedad por defecto). Ledger en `Captures/censo_noche2/ledger.json` + resumen. Commit.

**LOTE C — EL AUDITOR APRENDE**: categorías nuevas en `EnvSemantics.cs`: PAVE_MISSING, GROUND_DIRT_IN_STREET, TEX_WRONG_SURFACE, VEG_CLIP, SEAM_NO_KERB, PROP_LOGIC, WALL_PURPOSE. Mide cuántos defectos del censo caza cada regla y repórtalo.

**LOTE D — FIXES POR CLASE** (commit por clase, antes/después, integridad+validador tras cada rebuild): 1) suelo/pavimento (cobertura, decals ilógicos, bordillos), 2) puente y orilla del río (composición con sentido), 3) sin terminar (remates, aleros, puertas con profundidad — EnvInteriors existe), 4) texturas en superficie equivocada, 5) props/vegetación ilegales + los 3 edificios gemelos del mirador, 6) render: solo lo barato sin bake, 7) limpiar 6 ops de polish.json huérfanas.

**LOTE E — Cierre**: re-censo de lo arreglado (mismo método absoluto), informe a `Docs/evidence/WP-PROD-ENV-01/` con censo→fix→re-censo y QUÉ VERÁ EL OWNER AL CAMINAR. Su paseo es el gate.

Pendientes del owner (listar, no decidir): paquete com.unity.pipeline; 3 limitaciones cosméticas del casco; baked GI; PERIM_A y route probe; revisor independiente pre-merge.

Empieza por el Lote A e informa conforme avances.

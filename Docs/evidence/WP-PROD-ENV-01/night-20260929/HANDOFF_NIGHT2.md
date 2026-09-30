# HANDOFF — Sesión Noche 2: censo completo + fixes por clase (ENV01_Casco)

Fecha: 2026-09-30. Escrito por el orquestador de la Noche 1 tras el paseo de control del owner.
Estado del repo al escribir esto: `worker/prod-env-01` @ `d503119` (pushed), tag `checkpoint-night-pre-fase2`, árbol limpio.

## QUIÉN ERES Y CÓMO SE TRABAJA AQUÍ

Eres el orquestador nocturno de `juego-def`. El owner duerme y te deja el mando. Modelo validado en la Noche 1:

- **Tú eres EL OJO**. Juzgas capturas: `Read` del fichero → devuelve URL CDN → `analyze_image` con el prompt adecuado. Los subagentes operan Unity por MCP. El owner hace de árbitro final con SU paseo.
- **Subagentes no-fork** (Agent tool), frescos por misión, con prompts autocontenidos. Solo UN agente toca el editor de Unity a la vez; el paralelismo va en trabajo sin Unity (lectura, análisis, código).
- **Estándar KEEPER = el paseo del owner**: "pueblo creíble y terminado a pie de calle". NO "sin regresión respecto a ayer". Si el owner camina y ve fallos, no está arreglado.
- Commit tras cada gran fase. Informe continuo al owner (lee el chat al despertar).

## LA LECCIÓN DE LA NOCHE 1 — INTERIORIZA ESTO ANTES DE NADA

La Noche 1 arregló bien lo que cazó (45 hallazgos semánticos → 0; variación anti-procedural verificada) pero el owner caminó y encontró "fallos de todo tipo". Autopsia:

1. **Muestreo ≠ censo**: se juzgaron 8 ojos fijos escénicos elegidos por el operador + sitios de fix. El owner caminó TODAS las calles. Veredictos frame-locales se redactaron como conclusiones globales. PROHIBIDO repetirlo.
2. **El framing del prompt sesga**: "¿verifica este fix? / ¿hay defectos NUEVOS?" → respuestas limpias. "Cataloga TODO defecto sin piedad" sobre el MISMO distrito → 9-19 defectos por captura. El estado base nunca se había juzgado con la pregunta dura: cada gate comparaba con el estado anterior (rana hirviéndose), no con "¿esto parece un pueblo terminado?".
3. **El auditor no tenía categorías** para las clases que el owner vio. Y la "integridad" (Ground 11 renderers/9 materiales, PavingOverlays 4/3, Plazas 30/18) verifica que nada se DESTRUYÓ — una calle con hierba en vez de adoquín pasa ese test perfectamente. Contar no es corregir.

## CONTEXTO TÉCNICO ESENCIAL

- Repo `C:/Juego Def`, proyecto Unity `C:/Juego Def/Unity/JuegoDef` (Unity 6000.3.24f1, URP, GC2), branch `worker/prod-env-01`, PR #10.
- La escena `Assets/JuegoDef/Scenes/ENV/ENV01_Casco_District.unity` es GENERATED del spec (~30 s, `EnvDistrict.Begin/BuildRows(from,count,dry)/Finish`) y está GITIGNORED. Los cambios durables van en: spec `Assets/JuegoDef/Env/Specs/districts/ENV01_Casco_District.json`, `polish.json` (ops), y código `Assets/JuegoDef/Editor/Env/`.
- **Editor Unity por MCP**: pin `JuegoDef@9bfcb657` SOLO (`set_active_instance`). Existe otra instancia del worktree characters-01 — PROHIBIDA. El bridge cae en compiles/recargas: re-pinar y verificar `manage_scene get_active` = ENV01 en cada reconexión. Si el editor está cerrado: lanzarlo con `"C:\Program Files\Unity\Hub\Editor\6000.3.24f1\Editor\Unity.exe" -projectPath "C:\Juego Def\Unity/JuegoDef"`. Si se clava a ~57 MB con log a 0 bytes: hay un `Temp/UnityLockfile` huérfano de un editor muerto — matar el proceso nuevo, borrar el lockfile, relanzar (pasó la mañana del 30-09).
- **Protocolo de escena**: `execute_code` no marca dirty — tras CADA mutación: MarkSceneDirty + SaveScene, y re-verificar tras cada compile. `FixBlockedOpenings` y `SeatOnGround` corren en `Finish`, NO en `RebuildRow`.
- **PROHIBIDO**: `EnvDistrict.RebuildGround` (destruyó el pavimento una vez), tocar lighting/paquetes, `C:\Juego Def-ENV01-local-20260928` (backup ajeno, a veces abierto).
- **Regla de oro del RNG** (si tocas generadores): NUNCA dibujar del `rng` compartido de `BuildingAssembler.cs:117` — sorteos nuevos con hash dedicado (`seed*primo+const` o hash (seed,floor,bay)). Detalle y palancas en `Docs/evidence/WP-PROD-ENV-01/night-20260929/PHASE3_VARIATION_LEVERS.md`.
- Determinismo: verificar con `EnvPolish.Fingerprint` antes/después de filas tras cambiar generadores. `env_textures.py` NO es byte-determinista entre entornos — no regenerar texturas aprobadas sin restaurarlas después.
- Backups de escena: `Captures/backups/ENV01_preFase2_20260929.unity`, `ENV01_preFase3_20260929.unity` (118 MB). Rollback = backup o rebuild desde spec+polish.

### Lecturas previas OBLIGATORIAS (en orden)
1. `Docs/evidence/WP-PROD-ENV-01/night-20260929/NIGHT_REPORT.md` — lo hecho en Noche 1
2. `Docs/evidence/WP-PROD-ENV-01/night-20260929/OWNER_WALK_FINDINGS.md` — el catálogo de defectos del paseo del owner (la chispa de esta sesión) [si existe; si no, ver abajo]
3. `Docs/production/ENV_COMPOSITION_RULES.md` + `ENV_FACTORY.md` — reglas duras y pipeline
4. `Docs/evidence/WP-PROD-ENV-01/CASCO_REFERENCE_STUDY.md` — Potes como referencia ("alma no calco"); nota: la "escalera al agua" de la plaza del río es FEATURE diseñada que hoy LEE mal (sin rellano ni cierre) — arreglar su lectura, no eliminarla de plano sin pensar.
5. `Docs/design/GAME_VISION.md` / `VISUAL_BIBLE.md` — identidad (puerto norte de España 1999-2003; capa contemporánea INTENCIONAL; el maniquí del player es placeholder GC2 conocido, NO es defecto del distrito).

## CATÁLOGO DE DEFECTOS DEL PASEO DEL OWNER (30-09, 8 capturas, 113 hallazgos)

Clases (gravedad): **(1) SUELO** calles sin pavimentar/edificios sobre hierba, foso de tierra en manzana con muretes sin puerta, parches decals de barro/musgo ilógicos, seams duros entre 3 tipos de pavimento sin bordillo (🔴). **(2) SIN TERMINAR** cajas planas terminando calles, fachadas gigantes lisas, edificios acabándose planos contra el cielo sin alero, puertas a negro absoluto (🔴). **(3) TEXTURAS ILÓGICAS** adoquín de suelo aplicado a muro vertical estirado ("muelas gigantes"), estirados en esquinas/marcos (🔴). **(4) ESTRUCTURAS SIN SENTIDO** el puente/escalera al río (escalones hundiéndose en agua sin rellano, pasamanos muriendo en el agua, aros flotando sin amarre, agua cortando muros en seco), muro suelto contra el Bar Tito, stub de muro a media plaza, barandillas ancladas a nada (🔴). **(5) VEGETACIÓN/PROPS** hierba atravesando piedra, brotes de muros verticales, silla mirando la pared, taburete incrustado en barril, toldo sin mesa, clones de barriles (🟠). **(6) RENDER** ambiente plano sin oclusión en arranques (edificios "flotan"), sombras incoherentes dentro del mismo encuadre, horizontes/niebla sin resolver al final de calles (🟠 — parte conocida: sin baked GI). No-defectos conocidos: maniquí GC2, interiores cerrados intencionales (aunque "negro sin profundidad" es crítica justa de arte).

Las 8 capturas del owner: `C:\Users\Usuario\.zcode\cli\image-cache\sess_caff8d3a-aeea-4393-88d0-5b31c0bd341d\image-{91d2118d…,36f38a52…,d51fefc0…,422b292a…,22da1dd5…,1c4dc9b2…,4f863698…,2f692e7f…}.png` (si no existen ya, no son críticas: las clases están arriba).

## MISIÓN DE ESTA SESIÓN (en orden)

**Lote A — Arranque**: lecturas previas; pin del editor; verificar escena y estado git; backup `Captures/backups/ENV01_preNoche2_<fecha>.unity`; tag de seguridad.

**Lote B — CENSO REAL** (elimina el sesgo de muestreo): barrido sistemático con `EnvWalk`/`EnvShots`/`EnvSemantics.Look`: estaciones cada 15-20 m en TODAS las calles (~38, ambas direcciones, ojo a 1,7 m, resolución ALTA — sube la resolución de captura a ≥1920 px si el default es menor), + las plazas y la orilla del río. Juzgar CADA captura con prompt ABSOLUTO ("cataloga TODO defecto sin piedad, con ubicación en frame y gravedad") — nunca "¿hay defectos nuevos?". Consolidar en un ledger `Captures/censo_noche2/ledger.json` (clase, calle, estación, gravedad, descripción) + hoja resumen. Commitea el ledger.

**Lote C — EL AUDITOR APRENDE**: nuevas categorías en `EnvSemantics.cs` para las clases mecánicas (que no dependan del ojo): PAVE_MISSING (cobertura de zonas de pavimento vs calles del spec), GROUND_DIRT_IN_STREET, TEX_WRONG_SURFACE (material de suelo en muro vertical — detectable por material del renderer), VEG_CLIP (vegetación intersectando no-suelo), SEAM_NO_KERB (transición de zonas de pavimento sin bordillo), PROP_LOGIC (silla mirando pared, taburete en barril), WALL_PURPOSE (stub suelto, barandilla sin anclaje). Ejecutar y medir cuántos defectos del censo caza cada regla nueva — reportar cobertura regla-vs-ojo.

**Lote D — FIXES POR CLASE** (orden por impacto visual; commit por clase; antes/después de cada uno; integridad + validador tras cada rebuild):
1. Suelo/pavimento (cobertura completa de calles, matar decals ilógicos, bordillos en seams).
2. Puente y orilla del río (composición con sentido: rellano en la escalera al agua, pasamanos que terminan en pilar, amarre de aros, junta agua-muro).
3. Sin terminar (remates de calle, aleros, puertas con profundidad mínima — el toolchain de interiores existe: `EnvInteriors`).
4. Texturas en superficie equivocada + estirados (auditor del Lote C da la lista).
5. Props/vegetación ilegales + clones de gemelos (3 edificios gemelos del mirador, deuda Noche 1).
6. Render: SOLO lo barato (contact shadows/AO falso en arranques si URP lo permite sin bake); baked GI queda fuera de alcance — documentar.
7. Limpieza: 6 ops de polish.json huérfanas.

**Lote E — Cierre**: re-censo de las calles arregladas (mismo método absoluto), informe a `Docs/evidence/WP-PROD-ENV-01/night-20260929/` (o carpeta nueva noche2) con: censo→fixes→re-censo, cobertura de las reglas nuevas, y QUÉ VE EL OWNER AL CAMINAR. El gate final es SU paseo.

## PENDIENTES DEL OWNER (no decidir, solo listar en el informe)
Paquete `com.unity.pipeline` 0.8.0-exp.1 commiteado (¿se queda?); 3 limitaciones cosméticas del "lenguaje del casco"; baked GI/día-noche (fuera de alcance); PERIM_A y retune del route probe (handoff micro-polish); procedimiento de revisor independiente y freeze SHA del AGENTS.md antes de merge.

## REGLAS DE SEGURIDAD NO NEGOCIABLES
Cero regresión (si un fix no mejora claramente, se revierte); pavimento: verificar Ground/PavingOverlays/Plazas tras cada rebuild PERO recordar que cuenta≠corrige — el censo visual manda; nunca dos agentes en Unity a la vez; informe continuo; si algo se atasca 2 intentos, documentar y saltar.

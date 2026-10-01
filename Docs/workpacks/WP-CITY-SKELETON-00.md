# WP-CITY-SKELETON-00 — Fase 0: esqueleto global del Mapa F1

Status: **READY AFTER WP-CITY-MASTER-00 (Worker may start in parallel; plan figures are re-measured here)**
Class: PRODUCT / CITY BLOCKOUT / UNITY
Depends on: `WP-CITY-MASTER-00` (plan v1.1), bootstrap Unity + GC2 PASS, ENV kit on the ENV chain (`worker/casco-diag-01` + PR #25).
Branch base: `origin/worker/casco-diag-01` + merge of `origin/main` (the ENV kit is not on `main`); PR base `worker/casco-diag-01`. Isolated worktree; never the shared checkout with uncommitted DENSITY-01 work.
Blocks: `WP-CITY-B0-01` and every sector WP.

## Objetivo / claim

El Mapa F1 completo (escala Kamurocho, núcleo + anillo) existe como **blockout recorrible y persistente** en escenas Unity authored: relieve y banquetas, dársena, río encajonado, red pública con escaleras y rampas reales, capa de interconexión (traseras, interiores atravesables como volúmenes con puertas, azoteas, cota de agua, huertas), masas por SemanticBuilding con puertas marcadas, volúmenes de los interiores grandes, espacios abiertos y costuras Y1–Y5. Los presupuestos y distancias se **re-miden desde la escena** y cumplen; el Player GC2 recorre todo; los agentes NPC navegan entre identidades.

Esto es **blockout validado**, no un sector terminado ni producción de entorno keeper.

## Dependency check (registrar antes de implementar)

Prerrequisitos y SHA; garantías consumidas (plan v1.1, Player/cámara GC2, `JDRouteProbe`, `JDSpatialIdentity`, `EnvAuthoredGuard`, kit ENV); lo que este WP posee (escenas CITY y su autoridad manual, exportación de métricas); evidencia que reabriría el plan (vecino >180 m, red >3.600 m, envolvente >150.000 m², extremo >900 m, imposibilidad física de una adyacencia, de una capa o de 70/20/10 razonable).

## Implementación permitida

- Escenas `Assets/JuegoDef/Scenes/CITY/`: `CITY_Base.unity` (suelos, agua, río, iluminación, `NavMeshSurface`, spawn del Player) + una escena por sector (`CITY_S1_B0`, `CITY_S2_MuelleMercado`, `CITY_S3_CascoBajo`, `CITY_S4_CascoAlto`, `CITY_S5_Viviendas`, `CITY_S6_Talleres`, `CITY_S7_Arrabal`, `CITY_S8_CostaEste`, `CITY_S9_Molinos`, `CITY_S10_Afueras`), cargadas juntas como multi-escena estándar; LFS para escenas grandes.
- Helper de editor **one-shot** que extruye el plan authored (no decide nada procedural): banquetas, cintas de calle con ancho y pendiente, escaleras reales (tabica ≤0,16 m, huella ≥0,30 m), rampas, muros de muelle y cauce, masas por SemanticBuilding, volúmenes de interiores grandes. Tras guardar, un guard (patrón `EnvAuthoredGuard`) impide re-sembrar sobre una escena authored; desde ahí toda edición es manual.
- ProBuilder (paquete oficial gratuito) si se adopta: registrar versión y licencia.
- Identidad pasiva con `JDSpatialIdentity` (Zone, StreetAxis con polilínea, LayerLink con capa y acceso, Building con huella y clase de acceso, OpenSpace, Seam, Opportunity) y exportador de editor → JSON que `Tools/city_plan.py` mide con las mismas reglas.
- NavMesh (`com.unity.ai.navigation`, ya instalado) y 3 agentes GC2 (Mannequin, driver NavMeshAgent, instrucciones nativas Move To / Wait) como **fixtures de validación**, no como sistema de rutinas.

## Forbidden scope

Arte keeper, interiores completos, conversión de ENV01, escritura en `ENV01_AUTHORED` o en el checkout con DENSITY-01, Director/MAST, generador de ciudad reutilizable, sistema de rutinas/horario, compras.

## Aceptación

1. Métricas **medidas desde la escena** dentro de los topes F1: envolvente ≤150.000 m²; red pública con ejes exteriores PUB-H ≤3.600 m (capas no públicas declaradas aparte); vecinos funcionales ≤180 m y extremo ≤900 m por camino NavMesh; mayor/menor identidad ≥2; 200 ±15 edificios (≤240; CASCO ≤50); ≥3 capas de interconexión por identidad; pendientes por longitud reportadas (intención 70/20/10).
2. Partición del suelo: 100 % del suelo de manzana etiquetado como edificio, patio, huerta, patio de trabajo, muelle o retranqueo con función y acceso; 0 residuales sin disposición (tolerancia ≤0,01 m² de redondeo).
3. `JDRouteProbe` recorre cada eje público en ambos sentidos con el Player GC2 real: 0 STUCK/TIMEOUT/ABORTED, sin caídas ni escapes.
4. NavMesh: camino válido entre todas las anclas y nodos públicos; agentes de r≈0,3 cruzan escaleras y callejas de 2,5 m.
5. Recorrido manual en tercera persona por cada costura entre identidades, por cada enlace caminable de la capa de interconexión y hasta el cierre de Y1–Y5; capturas fijas (Atalaya, revelación en E, plaza del mercado, Plaza Mayor, muelle, rampa de Talleres, terrazas, Plaza de la Estación, ermita, campo de fútbol, faro).
6. Negativos: agua, patio CTL, enlaces SRV/PRV/CTL/PROG cerrados en su estado por defecto y corredores Y1–Y5 no transitables más allá de su cierre; ningún interior ni capa es requisito de conectividad pública.
7. Persistencia: guardar, reabrir, domain reload y Play conservan una edición manual de prueba; el helper rechaza re-sembrar.
8. Profiler base (frame time y batches en 3 vistas representativas) registrado.

## Evidencia

`Docs/evidence/WP-CITY-SKELETON-00/`: dependency check, métricas exportadas, plano renderizado desde la escena, partición de suelo, receptores de ruta/NavMesh, capturas, persistencia, profiler, pre-review y handoff (qué cambió respecto al plan v1.1, qué se comprobó, qué falta, siguiente trabajo).

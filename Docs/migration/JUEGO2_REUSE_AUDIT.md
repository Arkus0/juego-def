# Auditoría de reutilización de Arkus0/Juego2

**Alcance:** ideas y evidencias inspeccionadas en Juego2 al fundar juego-def (2026-09-27). «Reutilizar directamente» autoriza una práctica pequeña tras comprobar que aplica; no implica importar código, contratos, assets ni requisitos. El setting anterior es un valle interior de Liébana; este juego tiene **puerto marítimo propio**, por lo que su biblia no es autoridad de ubicación.

| Clase | Concepto | Decisión para juego-def |
| --- | --- | --- |
| REUSE_DIRECTLY | Git/Unity: ignorar salidas generadas, conservar escenas, `ProjectSettings` y `.meta`, anotar versión real | Higiene básica al crear el nuevo proyecto, revisada contra su estructura efectiva. |
| REUSE_DIRECTLY | Comprar sólo ante una necesidad jugable | Regla de adquisición aplicada desde M0. GC2 Core figura comprado por el owner; verificar acceso. |
| REUSE_AS_KNOWLEDGE | ART: fachadas, huecos, umbrales, tejados, suelo y bordes deben tener uniones físicas creíbles | Componer la primera calle; evitar «cubo con ventana pegada», sin copiar el contrato extenso ART. |
| REUSE_AS_KNOWLEDGE | Escala peatonal, densidad, ritmo, legibilidad tercera persona y rutas aprendibles de CITY | Ajustar la primera calle jugando; ningún grafo/mapa CITY es obligatorio. |
| REUSE_AS_KNOWLEDGE | Pruebas H2F de URP, iluminación húmeda, materiales, NavMesh, avatar humanoide/cámara | Base de experimentos concretos; verificar en escena, versión, assets y GC2 nuevos antes de adoptar. |
| REUSE_AS_KNOWLEDGE | Quaternius como kit editable; adaptación de cubiertas, señalética, ropa, vegetación y puerto | Revisar catálogo, procedencia, términos y ajuste atlántico; acceso al vault previo no implica permiso de redistribución de otro paquete. |
| REUSE_AS_KNOWLEDGE | CI rápida y diagnóstico reproducible | Añadir sólo checks que eviten fallos reales en Unity; no copiar workflows largos por inercia. |
| REEVALUATE_LATER | Calendario global, hechos de investigación, creencias/mentiras duraderas, sucesos fuera de cámara | Intentar primero GC2 y probar límites; Arkus opcional sólo con caso fallido concreto. |
| REEVALUATE_LATER | Scripts/shaders/herramientas del spike H2F | Evaluar licencia, necesidad, portabilidad, materiales y propiedad. No copiar prototipos como foundation. |
| REEVALUATE_LATER | Assets de Juego2, derivados ART, paquetes Quaternius y animaciones | Auditar derechos, fuente, adecuación al puerto y coste de adaptación antes de incorporar archivos. |
| DO_NOT_PORT | Harness H0, bridge H1, autoridad canonical→Unity, CAS, MCP, replay/snapshot | Responden a otra arquitectura; M0 no los necesita. |
| DO_NOT_PORT | Workpacks, contratos, CITY completo, matrices/gates, freezes y cadenas de reviewer/DocSync | La nueva PR se evalúa por su juego y entregas observables, sin heredar burocracia. |
| DO_NOT_PORT | Setting de Potes/Liébana como geografía, prohibición del mar y sus restricciones visuales | Contradice la ciudad portuaria marítima de este proyecto. |
| DO_NOT_PORT | Simulación sistémica profunda de todos los NPC y ciudad planificada completa antes del slice | Usar NPC por capas y bloques incrementales. |

Fuentes revisadas: [setting anterior](https://github.com/Arkus0/Juego2/blob/main/Docs/art/SETTING.md), [biblia visual](https://github.com/Arkus0/Juego2/blob/main/Docs/art/VISUAL_BIBLE.md), [gramática ART](https://github.com/Arkus0/Juego2/blob/main/Docs/workpacks/ART/ART_ENVIRONMENT_ASSEMBLY_GRAMMAR.md), [realización CITY](https://github.com/Arkus0/Juego2/blob/main/Docs/workpacks/CITY/CITY_07_GAME_SPACE_REALIZATION_AMENDMENT.md), [pruebas H2F](https://github.com/Arkus0/Juego2/blob/main/Docs/evidence/WP-H2F-01/SPIKE_RESULTS.md) y [adquisición](https://github.com/Arkus0/Juego2/blob/main/Docs/evidence/WP-H2F-01/ACQUISITION_AND_POLICY.md). Estas referencias informan decisiones; no son dependencias ni contratos de juego-def.

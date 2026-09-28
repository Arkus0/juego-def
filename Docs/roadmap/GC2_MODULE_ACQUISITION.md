# Adquisición de Game Creator 2 por necesidad

**Regla económica:** no comprar/adoptar un módulo porque el roadmap lo nombre. Primero debe existir una feature real que demuestre un ahorro material de trabajo o una mejora importante de calidad. «Comprar» significa sólo si la licencia no es ya propiedad del owner; comprobar disponibilidad y compatibilidad en el equipo y versión Unity elegidos. No se compra ni instala nada en esta PR. GC2 Core fue adquirido previamente según el registro de Juego2; verificar acceso efectivo en este nuevo proyecto.

| Módulo | Cuándo evaluar/adquirir/activar | Feature que podría desbloquear | Prueba antes de conservarlo |
| --- | --- | --- | --- |
| Core | M0, tras bootstrap; verificar propiedad previa | Player, cámara, Triggers, Conditions, Instructions, Variables e interacción básica | Caminar por una calle, examinar objeto e interactuar con NPC. |
| Dialogue | Al construir preguntas/contexto reales; **evaluar primero frente a Core/local** | Presentación/authoring de preguntas, foto/persona/lugar y respuestas contextuales | Fixture real demuestra ahorro/calidad material; `NOT_MATERIAL`, `REJECTED` o `DEFERRED_NOT_ACQUIRED` son válidos. |
| Inventory | Sólo cuando una pista/llave/dinero deba recogerse, llevarse y usarse | Objetos y economía portátil | Un objeto pasa por adquisición, uso y recuperación tras carga. |
| Quests | Sólo si varios hilos no se manejan bien con Variables/Dialogue/local | Hilos persistentes, progreso y desbloqueos | Completar un hilo, recordar su estado tras cargar y abrir otro sin marcador obligatorio. |
| Behavior | Cuando un horario/ruta de NPC aporte jugabilidad real | Apertura de negocio, trayectos y rutinas | Volver en otro momento y hallar una rutina que cambie una pista/acceso. |
| Melee | Antes del primer sparring/pelea retenible | Entrenamiento, combate narrativo y callejero | Entrar, combatir, terminar y recibir reacción coherente. |
| Perception | Cuando guardias, pelea, sigilo o persecución necesiten sensores reales | Visión/oído/reacciones locales | Una detección y una evasión jugables; no comprar para una persecución dirigida que no lo necesite. |
| Stats / Shooter / Traversal / otros | Sólo si una feature concreta demuestra una carencia y compensa coste | A determinar | Comparación específica con Core/módulos/local antes de adopción. |

Inventory y Quests son decisiones independientes. Una fotografía puede empezar como utilería/contexto de Core y pasar a Inventory cuando haga falta llevarla persistentemente. Una persecución se prueba primero como ruta jugable dirigida; sólo necesita Perception si la detección sensorial forma parte del diseño probado.

Dialogue tiene su estrategia migrada en [`../production/DIALOGUE_AUTHORING_KNOWLEDGE.md`](../production/DIALOGUE_AUTHORING_KNOWLEDGE.md). La existencia de un módulo no certifica que una composición funcione: se demuestra en Play Mode y en el flujo real de autoría.

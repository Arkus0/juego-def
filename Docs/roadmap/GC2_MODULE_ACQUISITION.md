# Adquisición de Game Creator 2 por necesidad

**Regla económica:** no comprar el módulo siguiente hasta que el anterior haya producido una feature jugable que queremos conservar. «Comprar» en esta tabla significa sólo si la licencia no es ya propiedad del owner; comprobar disponibilidad y compatibilidad en el equipo y versión Unity elegidos. No se compra ni instala nada en esta PR. GC2 Core fue adquirido por el owner en Juego2 según [registro anterior](https://github.com/Arkus0/Juego2/blob/main/Docs/evidence/WP-H2F-01/ACQUISITION_AND_POLICY.md); verificar acceso efectivo en este nuevo proyecto.

| Módulo | Cuándo adquirir/activar | Feature que desbloquea | Prueba antes de considerar el siguiente |
| --- | --- | --- | --- |
| Core | M0, tras bootstrap; verificar propiedad previa | Player, cámara, Triggers, Conditions, Instructions, Variables e interacción básica | Caminar por una calle, examinar objeto e interactuar con NPC. |
| Dialogue | Al construir preguntas de investigación, tras M0 | Preguntar, ofrecer foto/objeto de contexto y variar respuestas | Una conversación produce una pista humana distinta según contexto. |
| Inventory | Sólo cuando una pista/llave/dinero deba recogerse, llevarse y usarse | Objetos y economía portátil | Un objeto pasa por adquisición, uso y recuperación tras carga. |
| Quests | Sólo si varios hilos de investigación no se manejan bien con variables/Dialogue | Hilos persistentes, progreso y desbloqueos | Completar un hilo, recordar su estado tras cargar y abrir otro sin marcador obligatorio. |
| Behavior | Cuando un horario/ruta de NPC aporte jugabilidad | Apertura de negocio, trayectos y rutinas | Volver en otro momento y hallar una rutina que cambie una pista/acceso. |
| Melee | Antes del primer sparring/pelea que se vaya a conservar | Entrenamiento, combate narrativo y callejero | Combate con inicio, final y reacción coherentes en una escena real. |
| Perception | Cuando guardias, pelea, sigilo o persecución necesiten detección sensorial real | Visión/oído/reacciones locales | Al menos una detección y una evasión jugables; no forzar su compra para una persecución dirigida. |
| Stats / Shooter / Traversal / otros | Sólo si una feature concreta demuestra una carencia y compensa coste | A determinar; ninguno es requisito de M0 ni del primer slice por defecto | Prueba mínima de la feature anterior y comparación específica con Core/módulos disponibles. |

Inventory y Quests son decisiones independientes: no comprar ambos por el mero nombre de la fase. Una fotografía puede comenzar como utilería/contexto en Core y pasar a Inventory cuando haga falta llevarla o usarla persistentemente. Una persecución se prueba primero como ruta jugable dirigida; sólo necesita Perception si la detección real es parte del diseño probado. Consultar la [lista oficial de módulos](https://docs.gamecreator.io/gamecreator/) y sus [requisitos de instalación](https://docs.gamecreator.io/gamecreator/getting-started/installation/) al activar cada uno. La existencia de un módulo no certifica que una composición específica funcione: se demuestra en Play Mode.

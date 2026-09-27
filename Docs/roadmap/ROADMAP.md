# Roadmap jugable

Cada fila propone una entrega pequeña con una prueba en Play Mode. «Compra» significa adquisición por el owner **si aún no posee el módulo**; poseerlo no demuestra instalación. La etapa siguiente sólo se activa cuando la etapa anterior deja una feature jugable que conservar. Se pueden reordenar módulos si una escena demuestra otra necesidad; no comprar por previsión. URP, materiales y activos se prueban al adoptar contenido, sin importar las decisiones técnicas de Juego2 como contrato.

| Paso | Objetivo visible | GC2 necesario | ¿Compra? | Keeper output | PASS observable |
| --- | --- | --- | --- | --- | --- |
| Bootstrap Unity | Proyecto abre, escena vacía reproduce y se guarda en git | Ninguno | No | Proyecto Unity mínimo, versión y pipeline anotados | Abrir y ejecutar la escena sin errores que impidan jugar. |
| GC2 Core | Jugador tercero y cámara controlables | Core | Core sólo si no pertenece ya al owner; [propiedad previa documentada](../migration/JUEGO2_REUSE_AUDIT.md) por verificar localmente | Player + cámara y escena de prueba | Caminar, girar y seguir al personaje en Play Mode. |
| First Street | Calle portuaria corta, transitada a escala humana | Core | No nueva | Tramo conservable de fachadas y suelo, aunque art provisional señalado | Recorrerlo con referencias espaciales legibles y sin bloqueos. |
| First Interaction | Puerta/hotspot y objeto examinable | Core | No nueva | Interacciones con GC2 | Acercarse, activar y ver un resultado distinto en cada uno. |
| First NPC | Habitante con posición, gesto o respuesta breve mediante Core | Core | No nueva | NPC reconocible con interacción simple | Activar la interacción del NPC en la calle. **Cierra M0.** |
| Dialogue | Preguntar a alguien por foto/persona y lugar | Dialogue | Sí, sólo antes de implementarlo si no está comprado | Primera conversación contextual | Dos preguntas dan información diferente según un hecho conocido. |
| First Investigation Loop | Contrastar dos testimonios con una prueba examinada | Core + Dialogue | No nueva | Pista que recontextualiza un sitio visitado | Jugador llega a la pista siguiendo referencias del mundo sin waypoint obligatorio. |
| Inventory / Quests | Portar una foto/llave/dinero; seguir un hilo si hace falta | Inventory; Quests **sólo si** variables Core resultan insuficientes | Cada módulo sólo al demostrar necesidad | Objeto persistente y, si procede, hilo de quest | Adquirir, usar y recuperar tras carga un objeto; estado del hilo persiste si Quests se adopta. |
| Behavior | Primer NPC abre, se mueve y cierra por horario | Behavior | Sí si no está comprado | Rutina que sirve una pista | Esperar o regresar y encontrarlo en otro sitio/estado sin teletransporte visible injustificado. |
| First Living Block | Calle, comercio y unos pocos NPC con tiempos coherentes | Core + Dialogue + Behavior; Inventory si se usó | No nueva | Bloque habitado retenible | Visitar mañana/tarde y descubrir una oportunidad diferente mediante una rutina. |
| Melee | Sparring breve con personaje y propósito | Melee | Sí si no está comprado | Encuentro y entrenamiento conservables | Entrar, combatir, terminar y recibir reacción narrativa en Play Mode. |
| First Chase | Sospechoso huye por mercado/callejón hacia puerto | Core + Behavior; Melee sólo si termina en combate; Perception sólo si detectar exige sensores | Perception **condicional**, no compra preventiva | Persecución jugable con salida al escapar/capturar | Jugador puede alcanzar o perder al sospechoso; ambos resultados conservan un camino de investigación. |
| First 20–30 minute Shenmue Slice | Investigar desde pensión a puerto y regresar con una pista nueva | Módulos realmente usados arriba | No nueva sin feature demostrada | Secuencia jugable de principio a fin con arte keeper creciente | Partida completa cronometrada 20–30 min, investigación comprensible, interacción, rutina, persecución, combate y retorno funcionan; anotar problemas reales. |
| Expansión | Nuevo bloque/distrito, actividades y NPC por capas | Según feature probada | Sólo ante necesidad demostrada | Contenido retenible incremental | Cada incremento produce una ruta, actividad o personaje que se juega de principio a fin. |

«Keeper» indica intención de reutilizar una escena/feature, no garantía de que todos los materiales provisionales sean finales. Una feature puede pasar su prueba y conservar límites documentados; una ausencia que impida vivir su criterio PASS no se declara aprobada.

## M0 — GC2 Walking Street

**Límite exacto:** Unity abre; GC2 Core instalado y operativo; jugador tercero con cámara; una calle portuaria mínima; una puerta o hotspot; un objeto examinable; un NPC; interacción real con GC2. **Arkus ausente.** Las 2–3 presencias simples del experimento Core son opcionales en M0: basta un NPC. Sin Dialogue, Inventory, Quests, Behavior, Melee o Perception requeridos. Si Core no ofrece una presentación conversacional suficiente, una respuesta breve mediante Instructions basta.

**PASS:** «El jugador puede abrir el proyecto, caminar por una pequeña calle, acercarse a un NPC/objeto e interactuar usando GC2». Demostrarlo con el proyecto abierto en editor, Play Mode y una breve captura o recorrido reproducible. La puerta/hotspot debe responder en la misma escena; no exigir su sistema completo. No reclamar este PASS hasta ejecutar la prueba.

**Siguiente tarea tras esta PR:** crear el proyecto Unity nuevo en `juego-def`, comprobar versión/pipeline y disponibilidad de la licencia de GC2 Core del owner; importar Core por la vía permitida por la licencia, sin distribuir el paquete comercial. Montar la escena mínima y ejecutar el PASS de M0. Si URP dificulta la prueba, documentar el hallazgo y elegir el pipeline por su resultado visible, sin hacer de la migración una infraestructura previa.

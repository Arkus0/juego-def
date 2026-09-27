# Arquitectura: GC2 primero

**Decisión fundacional.** Unity aloja el juego; Game Creator 2 (GC2) es el framework principal de gameplay. Se construye primero la experiencia jugable con Core y sus módulos cuando hagan falta. Arkus es opcional y no está presente en M0.

## Regla práctica del 80 %

Para cada feature, construir una prueba pequeña con GC2 y contenido real. Si GC2 satisface razonablemente al menos el 80 % de la experiencia y los cambios restantes caben en configuración, composición de Instructions/Conditions/Variables o un adaptador local pequeño, usar GC2. El porcentaje es una heurística de producto, no una métrica matemática ni un gate de cobertura: valorar lo que ve el jugador, tiempo de producción, estabilidad y mantenimiento. Registrar un problema reproducible antes de comprar otro paquete o programar un sistema propio.

## Propiedad por defecto

| Área | Propietario inicial | Condición de cambio |
| --- | --- | --- |
| Personaje jugador, locomoción, cámara, animación, gestures, LookAt/IK | GC2 Core y Unity | Ajuste local si un comportamiento visible lo necesita. |
| Hotspots, puertas, objetos examinables, eventos, Instructions, Conditions, Variables, States | GC2 Core | Componer primero; no inventar motor de interacción. |
| Conversaciones y presentación | GC2 Dialogue cuando empiece la investigación conversacional | Script local sólo para un caso demostrado fuera del módulo. |
| Objetos, dinero y comercio | GC2 Inventory cuando exista necesidad persistente | Un objeto de utilería o una foto presentada sin inventario formal pueden resolverse antes con Core. |
| Hilos y tareas convencionales | GC2 Quests cuando las variables de Core ya no sean suficientes | La interfaz debe favorecer pistas físicas, no marcadores permanentes. |
| Rutinas, navegación y conducta local | GC2 Behavior y navegación Unity cuando haya horarios reales | Primero rutinas pequeñas; población ambiental barata. |
| Combate, sparring, maestros | GC2 Melee cuando se conserve el primer encuentro | Mantener combate vinculado a personajes y lugares. |
| Detección, guardias, reacción a pelea, sigilo ligero | GC2 Perception cuando una escena lo exija | Persecuciones dirigidas pueden comenzar sin este módulo. |
| Trabajos, tiendas, minijuegos, persecuciones y secuencias dirigidas | Composición de GC2 + Unity | Extensiones pequeñas sólo frente a una carencia concreta. |

GC2 Core dispone de Character, Camera Controller, Triggers, Instructions y Variables; los módulos son extensiones separadas. Ver [documentación GC2](https://docs.gamecreator.io/gamecreator/), [instalación](https://docs.gamecreator.io/gamecreator/getting-started/installation/) y [módulos](https://docs.gamecreator.io/). La implementación y compatibilidad de cada versión se comprobarán en el proyecto nuevo; la tabla indica intención, no pruebas ya pasadas.

## Posible frontera causal de Arkus

Únicamente proponer Arkus tras demostrar una necesidad concreta como calendario global persistente, hechos canónicos de la investigación entre sistemas, creencias/mentiras duraderas, eventos relevantes fuera de cámara o consecuencias persistentes que atraviesan varias mecánicas. La propuesta debe contener una escena que falle con GC2, alternativas intentadas, coste de la solución y un contrato de datos mínimo. Si se aprueba, GC2 sigue siendo dueño de movimiento, presentación y gameplay local; la capa causal intercambia sólo hechos/órdenes definidos. Evitar dobles escritores del mismo hecho y probar guardado/carga en la feature afectada.

No trasladar de Juego2 por su mera existencia H0, H1, harness, CAS, MCP, replay/snapshot, autoridad canonical→Unity, modelos generales de agentes, workpacks o gates. Ninguna decisión de Juego2 obliga a este repositorio. No adoptar ECS, arquitectura distribuida ni implementaciones propias de quests, diálogo, behavior trees, combate o perception mientras GC2 dé una solución razonable.

## Criterio de ingeniería

**Gameplay > contenido > calidad visual > tooling > infraestructura.** Cada cambio debe crear o mejorar una feature jugable retenible. Una dependencia comercial se activa sólo ante la feature que la necesita; recursos de pago adicionales requieren decisión explícita del owner. Evitar bloquear una prueba jugable por una posibilidad remota; registrar los límites encontrados y resolverlos cuando afecten al juego.

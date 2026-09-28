# Arquitectura: GC2 primero

**Decisión fundacional.** Unity aloja el juego; Game Creator 2 (GC2) es el framework principal de gameplay. Se construye primero la experiencia jugable con Core y sus módulos cuando hagan falta. Arkus no es foundation y sólo puede reaparecer ante una necesidad causal concreta demostrada.

El **production-authoring path** se decide por separado en [`PRODUCTION_AUTHORING_DECISION.md`](PRODUCTION_AUTHORING_DECISION.md). Un operador AI/MCP directo sobre Unity puede convertirse en herramienta primaria de ENV/CHAR/ANIM sin cambiar que GC2 sea el framework principal de gameplay.

## Regla práctica del 80 %

Para cada feature, construir una prueba pequeña con GC2 y contenido real. Si GC2 satisface razonablemente al menos el 80 % de la experiencia y los cambios restantes caben en configuración, composición de Instructions/Conditions/Variables o un adaptador local pequeño, usar GC2. El porcentaje es una heurística de producto, no una métrica matemática ni un gate de cobertura: valorar lo que ve el jugador, tiempo de producción, estabilidad y mantenimiento.

Registrar un problema reproducible antes de comprar otro paquete o programar un sistema propio.

## Propiedad por defecto

| Área | Propietario inicial | Condición de cambio |
| --- | --- | --- |
| Personaje jugador, locomoción, cámara, gestures, LookAt/IK | GC2 Core + Unity | Ajuste local si una escena real lo necesita. |
| Hotspots, puertas, objetos examinables, eventos, Instructions, Conditions, Variables, States | GC2 Core | Componer primero; no inventar otro motor de interacción. |
| Conversaciones y presentación | GC2 Dialogue **si su prueba/adquisición resulta materialmente útil**; si no, Core/local | Elegir por el flujo real de investigación/autoría. |
| Objetos, dinero y comercio | GC2 Inventory cuando exista necesidad persistente | Utilería/foto simple puede comenzar con Core. |
| Hilos/tareas convencionales | GC2 Quests cuando Variables/Dialogue dejen de ser suficientes | Mantener la interfaz centrada en pistas, no marcadores permanentes. |
| Rutinas y conducta local | GC2 Behavior + navegación Unity cuando una escena real lo justifique | Primero horarios/rutas pequeños y observables. |
| Combate | GC2 Melee cuando exista un encuentro que conservar | Combate ligado a personajes/lugares/narrativa. |
| Detección/sigilo/reacción | GC2 Perception cuando una escena lo necesite | Persecuciones dirigidas pueden existir antes. |
| Trabajos, tiendas, minijuegos y persecuciones | composición GC2 + Unity | Extender sólo frente a una carencia concreta. |
| Authoring físico de ENV/CHAR/ANIM | **PENDING**: Unity directo/manual vs operador AI/MCP | Consumir `PRODUCTION_AUTHORING_DECISION`. |

## GC2 Hub precheck

Antes de escribir glue nuevo, usar esta secuencia:

`GC2 native -> Hub candidate -> adapt lawful source -> custom code`

El Hub contiene piezas útiles pero no es una living-city architecture. Ver `Docs/production/GC2_HUB_REUSE_KNOWLEDGE.md`.

## Posible frontera causal de Arkus

Únicamente proponer una pequeña pieza de Arkus/H0 tras demostrar una necesidad concreta: por ejemplo hechos persistentes de investigación entre sistemas, calendario global realmente necesario o consecuencias fuera de cámara que GC2/local no resuelva económicamente.

La propuesta debe incluir:

1. escena reproducible que falla;
2. alternativas GC2/local intentadas;
3. coste de no resolverlo;
4. contrato de datos mínimo;
5. ownership sin doble escritor;
6. guardado/carga del caso real.

No portar H0 completo para resolver una feature pequeña.

## H1 rule

**H1 no se hereda.** No existe obligación de materialize/observe/reconcile/rematerialize/clean-rebuild para nuevas features o paquetes de juego-def. Si en el futuro se quiere reutilizar una utilidad concreta de H1, debe justificarse por su valor aislado y no reintroducir la arquitectura como dependencia transversal.

## AI/MCP rule

No confundir el MCP de la antigua infraestructura Arkus con un operador de producción Unity.

- El primero no se importa.
- El segundo está pendiente de benchmark y puede convertirse en el authoring path principal o bounded si demuestra calidad, repetibilidad, observabilidad y ahorro material.

## Criterio de ingeniería

**Gameplay + contenido + calidad visual > tooling > infraestructura.**

El tooling merece existir cuando aumenta de forma demostrable la velocidad/calidad de producir el juego. Infraestructura que exige mantenimiento pero no mejora el producto visible debe congelarse o eliminarse.

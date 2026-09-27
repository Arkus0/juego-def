# juego-def

Un juego de aventura en tercera persona ambientado en una ciudad portuaria ficticia del norte de España, entre finales de los noventa y los primeros años dos mil. Aspiramos a la experiencia de vivir unos días en una ciudad densa mientras investigamos un asesinato: **vida cotidiana → investigación → aventura**. Shenmue II inspira la estructura y el ritmo; personajes, historia, nombres, escenarios y arte serán propios.

## Pilares

1. **Una ciudad que se aprende andando.** Comercios, bares, mercado, puerto y vecinos sirven de pistas y de orientación; calles e interiores compactos antes que superficie vacía.
2. **Investigar haciendo.** Preguntar, enseñar una foto, inspeccionar objetos, volver a distintas horas, seguir a alguien y ganarse acceso mediante trabajos o confianza.
3. **Vivir entre pistas.** Rutinas proporcionadas a cada NPC, pequeños trabajos, minijuegos y entrenamiento integrados en lugares y personas.
4. **Aventura con consecuencias.** Persecuciones jugables, peleas breves y escenas dirigidas cuando mejoren el ritmo de la historia.

La víctima tiene una relación personal con el protagonista. El primer tramo conduce desde una pensión y los comercios hacia el puerto. Los detalles del crimen y del reparto siguen abiertos.

## Tecnología y alcance

- **Unity**; evaluar URP como base de render en el bootstrap, según la escena y los materiales que realmente adoptemos.
- **Game Creator 2 Core** como base de personaje, cámara, movimiento, interacción, variables e instrucciones. Añadir módulos por necesidad demostrada y por fases.
- Arte PS2+ propio: atmósfera atlántica húmeda, piedra, hormigón, madera y puerto; Quaternius y recursos gratuitos sólo cuando su licencia, adecuación visual y compatibilidad estén comprobadas. Sin activos de pago nuevos por defecto.
- **Arkus no forma parte de M0.** Sólo considerar una pequeña capa causal si un problema concreto de persistencia global supera razonablemente lo que GC2 ofrece. Juego2 es una fuente de lecciones, no una dependencia de ejecución.

La meta de largo plazo, sujeta a pruebas de producción, es una ciudad de 4–5 distritos densos con 80–120 NPC visibles: alrededor de 10–15 protagonistas, 30–40 interactivos y el resto población ambiental. Estas cifras no son compromisos del vertical slice.

## Comenzar

El primer hito es **[M0 — GC2 Walking Street](Docs/roadmap/ROADMAP.md#m0--gc2-walking-street)**: abrir el proyecto, caminar por una calle portuaria mínima y usar GC2 para interactuar con un NPC y un objeto. Esta PR define el proyecto; **todavía no incluye un proyecto Unity jugable ni acredita M0**.

- [Visión del juego](Docs/design/GAME_VISION.md)
- [Arquitectura GC2-first](Docs/architecture/GC2_FIRST_ARCHITECTURE.md)
- [Roadmap y M0](Docs/roadmap/ROADMAP.md)
- [Adquisición de módulos](Docs/roadmap/GC2_MODULE_ACQUISITION.md)
- [Auditoría de reutilización de Juego2](Docs/migration/JUEGO2_REUSE_AUDIT.md)

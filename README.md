# juego-def

Un juego de aventura en tercera persona ambientado en una ciudad portuaria ficticia del norte de España, entre finales de los noventa y los primeros años dos mil. Aspiramos a la experiencia de vivir unos días en una ciudad densa mientras investigamos un asesinato: **vida cotidiana -> investigación -> aventura**. Shenmue II inspira la estructura y el ritmo; personajes, historia, nombres, escenarios y arte serán propios.

## Pilares

1. **Una ciudad que se aprende andando.** Comercios, bares, mercado, puerto y vecinos sirven de pistas y orientación; calles e interiores compactos antes que superficie vacía.
2. **Investigar haciendo.** Preguntar, enseñar una foto, inspeccionar objetos, volver a distintas horas, seguir a alguien y ganarse acceso mediante trabajos o confianza.
3. **Vivir entre pistas.** Rutinas proporcionadas a cada NPC, pequeños trabajos, minijuegos y entrenamiento integrados en lugares y personas.
4. **Aventura con consecuencias.** Persecuciones jugables, peleas breves y escenas dirigidas cuando mejoren el ritmo.

## Tecnología

- **Unity** como runtime/editor.
- **Game Creator 2 first** para gameplay: Core y módulos sólo cuando una feature real los justifique.
- **Production authoring:** `BOUNDED_OPERATOR` con MCP for Unity como superficie principal en las lanes donde aporta valor; reevaluación tras la primera factory ENV a escala.
- **H0/H1 no se heredan** como foundation. Una pieza causal de Arkus sólo puede reaparecer frente a un problema concreto que GC2/local no resuelva económicamente.

## Dirección visual y producción

Arte estilizado low-poly/PS2+: atmósfera atlántica húmeda, ciudad densa a escala peatonal, working port, composición fuerte y reutilización inteligente de assets. Quaternius se trata como ecosistema editable de prefabs/componentes/personajes/animaciones, no como una colección que deba usarse intacta.

No se acepta como objetivo visual final el patrón **greybox + assets pegados**. El criterio es el resultado compuesto visto en tercera persona.

## Estado actual

`juego-def` es el repo de producción GC2-first.

Ya contiene el conocimiento migrado de producto, Visual Bible, modelo urbano, Quaternius/tooling, GC2 Hub, dialogue authoring y el baseline de producción. Unity + URP + GC2 Core están levantados y el player/cámara funcionan en Play Mode.

La siguiente fase construye **factorías gráficas/contenido** para que el siguiente edificio, civil, animación o conversación sea producción y no nueva I+D. Las factorías consumen dos entradas vinculantes:

- [`Docs/design/FIRST_KEEPER_BLOCK_B0.md`](Docs/design/FIRST_KEEPER_BLOCK_B0.md): el **qué construir** migrado desde CITY — B0 Mercado–Muelle y sus reglas de game-space;
- [`Docs/research/EXISTING_ASSET_PIPELINE_RESEARCH.md`](Docs/research/EXISTING_ASSET_PIPELINE_RESEARCH.md): el **qué reutilizar/probar antes de inventar tooling propio**.

El siguiente workpack es `WP-PROD-ASSET-00`; M0 puede avanzar en paralelo como fixture jugable mínimo.

## Documentos clave

- [Visión del juego](Docs/design/GAME_VISION.md)
- [Visual Bible](Docs/design/VISUAL_BIBLE.md)
- [Modelo de ciudad portuaria](Docs/design/PORT_TOWN_WORLD_MODEL.md)
- [B0 Mercado–Muelle: first keeper block](Docs/design/FIRST_KEEPER_BLOCK_B0.md)
- [Arquitectura GC2-first](Docs/architecture/GC2_FIRST_ARCHITECTURE.md)
- [Production authoring decision](Docs/architecture/PRODUCTION_AUTHORING_DECISION.md)
- [Roadmap](Docs/roadmap/ROADMAP.md)
- [Executable workpacks](Docs/workpacks/README.md)
- [Existing asset-pipeline research](Docs/research/EXISTING_ASSET_PIPELINE_RESEARCH.md)
- [Adquisición de módulos](Docs/roadmap/GC2_MODULE_ACQUISITION.md)
- [Baseline de migración](Docs/migration/JUEGO2_KNOWLEDGE_BASELINE.md)
- [Quaternius production knowledge](Docs/production/QUATERNIUS_PRODUCTION_KNOWLEDGE.md)
- [GC2 Hub reuse knowledge](Docs/production/GC2_HUB_REUSE_KNOWLEDGE.md)
- [Dialogue authoring knowledge](Docs/production/DIALOGUE_AUTHORING_KNOWLEDGE.md)

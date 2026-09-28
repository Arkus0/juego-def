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
- **Production authoring pendiente de decisión:** Unity directo/manual vs operador AI/MCP principal o bounded, según el benchmark `WP-AI-UNITY-AUTHORING-00` que se está ejecutando en Juego2.
- **H0/H1 no se heredan** como foundation. Una pieza causal de Arkus sólo puede reaparecer frente a un problema concreto que GC2/local no resuelva económicamente.

## Dirección visual y producción

Arte estilizado low-poly/PS2+: atmósfera atlántica húmeda, ciudad densa a escala peatonal, working port, composición fuerte y reutilización inteligente de assets. Quaternius se trata como ecosistema editable de prefabs/componentes/personajes/animaciones, no como una colección que deba usarse intacta.

No se acepta como objetivo visual final el patrón **greybox + assets pegados**. El criterio es el resultado compuesto visto en tercera persona.

## Estado actual

`juego-def` está siendo preparado como **repo de producción limpio y landing zone del conocimiento útil de Juego2**.

Ya se migra aquí el conocimiento de producto, Visual Bible, modelo urbano, Quaternius/tooling, GC2 Hub y factories post-foundation. La inversión técnica pesada queda deliberadamente en pausa hasta consumir el resultado del benchmark de authoring AI.

El siguiente hito jugable sigue siendo **M0 — GC2 Walking Street**, pero no vamos a congelar antes un gran framework de escenarios/personajes que el operador ganador pueda volver innecesario.

## Documentos clave

- [Visión del juego](Docs/design/GAME_VISION.md)
- [Visual Bible](Docs/design/VISUAL_BIBLE.md)
- [Modelo de ciudad portuaria](Docs/design/PORT_TOWN_WORLD_MODEL.md)
- [Arquitectura GC2-first](Docs/architecture/GC2_FIRST_ARCHITECTURE.md)
- [Decisión pendiente de production authoring](Docs/architecture/PRODUCTION_AUTHORING_DECISION.md)
- [Roadmap](Docs/roadmap/ROADMAP.md)
- [Factories post-foundation](Docs/roadmap/POST_FOUNDATION_PRODUCTION_WPS.md)
- [Adquisición de módulos](Docs/roadmap/GC2_MODULE_ACQUISITION.md)
- [Auditoría de reutilización de Juego2](Docs/migration/JUEGO2_REUSE_AUDIT.md)
- [Baseline de conocimiento migrado](Docs/migration/JUEGO2_KNOWLEDGE_BASELINE.md)
- [Quaternius production knowledge](Docs/production/QUATERNIUS_PRODUCTION_KNOWLEDGE.md)
- [GC2 Hub reuse knowledge](Docs/production/GC2_HUB_REUSE_KNOWLEDGE.md)

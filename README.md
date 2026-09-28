# juego-def

Un juego de aventura en tercera persona ambientado en una ciudad portuaria ficticia del norte de España, entre finales de los noventa y los primeros años dos mil. Aspiramos a la experiencia de vivir unos días en una ciudad densa mientras investigamos un asesinato: **vida cotidiana -> investigación -> aventura**. Shenmue II inspira la estructura y el ritmo; personajes, historia, nombres, escenarios y arte serán propios.

## Pilares

1. **Una ciudad que se aprende andando.** Comercios, bares, mercado, puerto y vecinos sirven de pistas y orientación; calles e interiores compactos antes que superficie vacía.
2. **Investigar haciendo.** Preguntar, enseñar una foto, inspeccionar objetos, volver a distintas horas, seguir a alguien y ganarse acceso mediante trabajos o confianza.
3. **Vivir entre pistas.** Rutinas proporcionadas a cada NPC, pequeños trabajos, minijuegos y entrenamiento integrados en lugares y personas.
4. **Aventura con consecuencias.** Persecuciones jugables, peleas breves y escenas dirigidas cuando mejoren el ritmo.

## Tecnología

- **Unity 6000.3.24f1 + URP 17.3** como runtime/editor (proyecto en `Unity/JuegoDef`).
- **Game Creator 2 first** para gameplay: Core 2.19.61 y módulos sólo cuando una feature real los justifique.
- **Production authoring: Claude Code + MCP for Unity** como operador de editor (`BOUNDED_OPERATOR`, confirmado por el owner tras compararlo con H0/H1 de Juego2); el juicio visual final es humano. Unity AI Assistant descartado (requiere suscripción).
- **H0/H1 no se heredan** como foundation. Una pieza causal de Arkus sólo puede reaparecer frente a un problema concreto que GC2/local no resuelva económicamente.

### Abrir el proyecto

1. Instalar Unity **6000.3.24f1**.
2. Restaurar GC2 Core (licencia por puesto; **nunca se commitea**, el repo es público): `python Tools/gc2-provision.py install`.
3. Abrir `Unity/JuegoDef` y la escena `Assets/JuegoDef/Scenes/Bootstrap_GC2Core.unity`.

Detalles en [Unity project setup](Docs/production/UNITY_PROJECT_SETUP.md).

## Dirección visual y producción

Arte estilizado low-poly/PS2+: atmósfera atlántica húmeda, ciudad densa a escala peatonal, working port, composición fuerte y reutilización inteligente de assets. Quaternius se trata como ecosistema editable de prefabs/componentes/personajes/animaciones, no como una colección que deba usarse intacta.

No se acepta como objetivo visual final el patrón **greybox + assets pegados**. El criterio es el resultado compuesto visto en tercera persona.

## Estado actual

`juego-def` es el **repo de producción limpio** y la landing zone del conocimiento útil de Juego2 (producto, Visual Bible, modelo urbano, Quaternius/tooling, GC2 Hub, dialogue authoring y factories post-foundation).

**Bootstrap hecho:** proyecto Unity + URP + GC2 Core con player y cámara en tercera persona caminando en Play Mode, construido por el operador MCP ([evidencia](Docs/evidence/BOOTSTRAP-UNITY-GC2/README.md)).

El siguiente hito jugable es **M0 — GC2 Walking Street**. Seguimos sin congelar un gran framework de escenarios/personajes: primero se prueba hasta dónde llega el operador.

## Documentos clave

- [Visión del juego](Docs/design/GAME_VISION.md)
- [Visual Bible](Docs/design/VISUAL_BIBLE.md)
- [Modelo de ciudad portuaria](Docs/design/PORT_TOWN_WORLD_MODEL.md)
- [Arquitectura GC2-first](Docs/architecture/GC2_FIRST_ARCHITECTURE.md)
- [Decisión de production authoring](Docs/architecture/PRODUCTION_AUTHORING_DECISION.md)
- [Unity project setup](Docs/production/UNITY_PROJECT_SETUP.md)
- [Roadmap](Docs/roadmap/ROADMAP.md)
- [Factories post-foundation](Docs/roadmap/POST_FOUNDATION_PRODUCTION_WPS.md)
- [Adquisición de módulos](Docs/roadmap/GC2_MODULE_ACQUISITION.md)
- [Auditoría de reutilización de Juego2](Docs/migration/JUEGO2_REUSE_AUDIT.md)
- [Baseline de conocimiento migrado](Docs/migration/JUEGO2_KNOWLEDGE_BASELINE.md)
- [Quaternius production knowledge](Docs/production/QUATERNIUS_PRODUCTION_KNOWLEDGE.md)
- [GC2 Hub reuse knowledge](Docs/production/GC2_HUB_REUSE_KNOWLEDGE.md)
- [Dialogue authoring knowledge](Docs/production/DIALOGUE_AUTHORING_KNOWLEDGE.md)

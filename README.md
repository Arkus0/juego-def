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

## Living World

El conocimiento aceptado de PA-01..13 de Juego2 se ha migrado sin su arquitectura H3/H4/H0. La guía actual está en [`Docs/research/living-world/LIVING_WORLD_KNOWLEDGE.md`](Docs/research/living-world/LIVING_WORLD_KNOWLEDGE.md).

Principios centrales:

- rutina esperada != estado real;
- agencia = elección del actor bajo información/oportunidades legítimas y acotadas;
- relaciones, creencias, rumores y memoria tienen significados/owners distintos;
- minijuegos pertenecen a la vida de la ciudad y exponen aftermath estructurado;
- jugador y NPCs actúan sobre el mismo mundo causal;
- investigación obtiene evidencia legítima, no verdad omnisciente;
- gobernar cambia reglas/oportunidades, no la mente de los ciudadanos;
- control de simulación limita coste/propagación sin robar semántica ni impedir transformación deliberada.

La escala de NPCs separa explícitamente **profundidad sistémica, rutina, identidad visual y población visible**; ver [`Docs/design/NPC_DEPTH_TIERS.md`](Docs/design/NPC_DEPTH_TIERS.md).

## Operación con agentes

Root [`AGENTS.md`](AGENTS.md) define el modelo ligero de trabajo.

Roles principales: **Owner -> Worker -> Unity/Asset Operator -> independent Reviewer -> Repair Worker**.

Skills canónicas viven en `.agents/skills/`; `.claude/skills/` contiene wrappers finos. Conservamos exact-SHA, pre-review e independencia Worker/Reviewer, pero no Automation V2, CTX/H1 ni ceremonia heredada.

## Estado actual

`juego-def` es el repo de producción GC2-first.

Ya contiene el conocimiento migrado de producto, Visual Bible, CITY/B0, Quaternius/tooling, GC2 Hub, dialogue authoring, Living World/PA, gameplay-system lessons, NPC depth tiers y el operating model de agentes. Unity + URP + GC2 Core están levantados y el player/cámara funcionan en Play Mode.

La siguiente fase construye **factorías gráficas/contenido** para que el siguiente edificio, civil, animación o conversación sea producción y no nueva I+D. Las factorías consumen dos entradas vinculantes:

- [`Docs/design/FIRST_KEEPER_BLOCK_B0.md`](Docs/design/FIRST_KEEPER_BLOCK_B0.md): el **qué construir** migrado desde CITY — B0 Mercado–Muelle y sus reglas de game-space;
- [`Docs/research/EXISTING_ASSET_PIPELINE_RESEARCH.md`](Docs/research/EXISTING_ASSET_PIPELINE_RESEARCH.md): el **qué reutilizar/probar antes de inventar tooling propio**.

El siguiente workpack de producción sigue siendo `WP-PROD-ASSET-00`; M0 puede avanzar en paralelo como fixture jugable mínimo.

## Documentos clave

- [Visión del juego](Docs/design/GAME_VISION.md)
- [Visual Bible](Docs/design/VISUAL_BIBLE.md)
- [Modelo de ciudad portuaria](Docs/design/PORT_TOWN_WORLD_MODEL.md)
- [NPC depth tiers](Docs/design/NPC_DEPTH_TIERS.md)
- [B0 Mercado–Muelle: first keeper block](Docs/design/FIRST_KEEPER_BLOCK_B0.md)
- [Arquitectura GC2-first](Docs/architecture/GC2_FIRST_ARCHITECTURE.md)
- [Production authoring decision](Docs/architecture/PRODUCTION_AUTHORING_DECISION.md)
- [Roadmap](Docs/roadmap/ROADMAP.md)
- [Executable workpacks](Docs/workpacks/README.md)
- [Living World / PA knowledge](Docs/research/living-world/LIVING_WORLD_KNOWLEDGE.md)
- [Gameplay systems knowledge](Docs/research/GAMEPLAY_SYSTEMS_KNOWLEDGE.md)
- [Existing asset-pipeline research](Docs/research/EXISTING_ASSET_PIPELINE_RESEARCH.md)
- [Legacy research source index](Docs/research/LEGACY_RESEARCH_SOURCE_INDEX.md)
- [Dependency/provenance policy](Docs/operations/DEPENDENCY_AND_PROVENANCE_POLICY.md)
- [Agent roles and flow](Docs/operations/AGENT_ROLES_AND_FLOW.md)
- [Final Juego2 migration audit](Docs/migration/JUEGO2_FINAL_MIGRATION_AUDIT.md)
- [Adquisición de módulos](Docs/roadmap/GC2_MODULE_ACQUISITION.md)
- [Baseline de migración](Docs/migration/JUEGO2_KNOWLEDGE_BASELINE.md)
- [Quaternius production knowledge](Docs/production/QUATERNIUS_PRODUCTION_KNOWLEDGE.md)
- [Asset catalogue and intake](Docs/asset_catalog/README.md) · [PROD-ASSET-00 evidence](Docs/evidence/WP-PROD-ASSET-00/README.md)
- [GC2 Hub reuse knowledge](Docs/production/GC2_HUB_REUSE_KNOWLEDGE.md)
- [Dialogue authoring knowledge](Docs/production/DIALOGUE_AUTHORING_KNOWLEDGE.md)

# WP-PROD-ENV-01 — Environment Asset + Assembly Factory

Status: **READY AFTER ASSET-00 + CITY-URBAN-00**  
Class: PRODUCTION FACTORY / ENVIRONMENT  
Depends on: `WP-PROD-ASSET-00` PASS + `WP-CITY-URBAN-00` PASS  
Blocks: `WP-PROD-ENV-02`

## Claim

juego-def has a repeatable environment production factory that can turn the admitted source corpus into reusable, game-coherent architectural/urban assets and assemble them into streets/interiors without bespoke low-level work for every scene.

This WP does **not** pass because one street looks good. It passes when the machinery to make many streets/buildings/thresholds exists and a meaningful reusable asset batch has been produced through it.

The factory is demand-driven: `CITY-URBAN-00` defines **what spatial/product roles the town and B0 need**; this WP industrializes **how those roles are manufactured**.

## Binding inputs

- `Docs/design/VISUAL_BIBLE.md`
- `Docs/design/PORT_TOWN_WORLD_MODEL.md`
- [`../design/CITY_PRODUCTION_KNOWLEDGE.md`](../design/CITY_PRODUCTION_KNOWLEDGE.md)
- [`../design/FIRST_KEEPER_BLOCK_B0.md`](../design/FIRST_KEEPER_BLOCK_B0.md)
- accepted `WP-CITY-URBAN-00` topology/programme + production-demand matrix
- `Docs/production/QUATERNIUS_PRODUCTION_KNOWLEDGE.md`
- [`../research/EXISTING_ASSET_PIPELINE_RESEARCH.md`](../research/EXISTING_ASSET_PIPELINE_RESEARCH.md)
- `PROD-ASSET-00` catalogue/lineage conventions
- Production Authoring Decision (`BOUNDED_OPERATOR`)
- bootstrap/M0 gameplay-scale evidence where available

## B0/CITY demand — factory must serve the product

The first factory batch must deliberately cover the vocabulary demanded by accepted `CITY-URBAN-00` / B0 Mercado–Muelle, including meaningful coverage of:

- ordinary mixed commercial frontage;
- corners/terminations;
- everyday shop public threshold + separate service logic;
- lodging frontage/entrance language;
- closed ordinary frontage fabric;
- stairs/ramps/retaining/railings for upper/port loops;
- public quay/working-water edge distinct from controlled work yard;
- port/market/street props;
- signage mounting and material/palette variants;
- shallow interior/threshold kit;
- street/parcel/building families and access/elevation relationships explicitly demanded by CITY.

Factory work may discover better ways to realize those roles, but it may not drift into making an unrelated generic medieval/urban kit while the accepted city demand remains unsupported.

## Mandatory reuse-first spike

Before writing an environment generator/exporter/material pipeline from scratch, evaluate the relevant existing research on a bounded real task and record `Docs/evidence/WP-PROD-ENV-01/REUSE_DECISIONS.md`.

At minimum:

1. inspect Medieval Village Source modularity and any other already-owned relevant urban/environment packs as **component libraries**, not theme locks;
2. use `osm_building_grammar` as the first semantic-role/taxonomy reference before inventing facade/donor metadata;
3. consume the `QuaterniusUnityUtils` spike result for collision/import work;
4. inspect/test `codec-xyz/game_export` techniques if Blender -> Unity handoff is materially repetitive;
5. evaluate Material Batch Tools or equivalent external batch tooling if material normalization is materially repetitive;
6. only if repeated building assembly remains a real bottleneck, compare Auto-Building vs Geo-Buildings before building a large custom procedural solution;
7. retain only the missing juego-def glue/templates/validators.

A candidate may be rejected for compatibility, quality, license, cost or insufficient value. Silent reinvention is not allowed.

## Factory scope

The factory must cover the environment families needed for near-term city production:

- building shells/facades;
- doors/windows/thresholds;
- roof/trim/corner/join pieces;
- street/ground/curb/steps;
- shop/bar/service frontage/signage mounting;
- port/market/street props and furniture;
- materials/palette variants;
- small interior/threshold kit sufficient for enterable edges.

Not every family needs a custom generator. The factory is the **combined production path**: searchable source components + existing/adapted tooling + derivation + templates/prefabs + assembly rules + validators + operator recipe.

## Required factory outputs

By PASS, retain:

1. `ENV_FACTORY.md` — authoritative short workflow;
2. `REUSE_DECISIONS.md` — what existing pipelines/tools were used, adapted, rejected or deferred and why;
3. lane-specific semantic catalogue/tags built on `PROD-ASSET-00`;
4. reusable juego-def-owned prefab/module library;
5. material/palette adaptation system or repeatable batch recipe;
6. donor-component extraction / derived-asset path using Blender/source editing where needed;
7. assembly templates/rules for facades, corners, thresholds, ground contact and repeated frontage;
8. cheap validation for scale, missing refs/materials, obvious collision/threshold faults and illegal proxy-as-keeper states;
9. a non-trivial **factory output batch**;
10. a `B0_COVERAGE.md` mapping each accepted CITY/B0 required role to ready units or explicit gaps.

## Minimum batch proof

Produce at least **15 reusable environment production units** across multiple roles, with enough diversity that they can make genuinely different streets and with material coverage of accepted B0 demand.

A production unit may be a complete prefab or a reusable derived/module set, for example facade/building variants, corner/termination pieces, shopfront/door/window sets, roof/trim kits, port/market props, street/ground modules or small interior/threshold sets.

Do not satisfy the count with 15 trivial recolours or microscopic pieces that cannot materially vary scenes.

## Architecture adaptation requirement

The factory must demonstrate all relevant reuse classes on real candidates where available: `DIRECT`, `ADAPTABLE`, `DONOR`, `CREATE_DERIVED`.

Pack names like medieval/fantasy/timber are not automatic rejection. Final composed fit governs acceptance.

## Assembly grammar

Define enough semantic rules that a worker/operator can request outcomes rather than exact object paths, including frontage type/width bands, floor/height/silhouette guidance, corner/termination treatment, door/window rhythm, shop/service frontage roles, threshold/ground contact rules, material/palette families, clutter/signage density and landmark vs ordinary facade roles.

The grammar must also support the CITY game-space needs: compression/expansion/reveal, readable corners, coherent local elevation, public-vs-controlled waterfront edges, layered building/street assembly and ordinary closed fabric between authored moments.

This is not a procedural city generator. It is a vocabulary for repeatable assisted assembly.

## Operator/tooling loop

`CITY semantic brief -> product role -> catalogue search -> reuse/spike known tooling -> choose/reuse/adapt/derive -> prefab/module output -> validate -> gameplay-scale preview -> correct -> admit to factory library`

Use MCP in Unity for inspection/assembly/validation and Blender MCP/source tools for mesh derivation when materially useful. Small batch scripts/editor utilities are expected where they turn repeated manual work into routine production.

## Evidence

Retain under `Docs/evidence/WP-PROD-ENV-01/`:

- `REUSE_DECISIONS.md`;
- `B0_COVERAGE.md`;
- factory workflow;
- output inventory with lineage/reuse class;
- captures/previews of the batch;
- at least one donor/derived example from source to final output;
- validator results;
- tooling/scripts/templates retained because they materially reduce repeated work;
- known kit gaps still requiring future asset creation.

## PASS

PASS when:

- relevant existing environment pipeline/tool candidates were bounded-tested or explicitly dispositioned before equivalent custom tooling was built;
- 15+ meaningful reusable production units exist across several environment roles;
- accepted CITY/B0 environment roles have usable coverage or explicit bounded gaps;
- operator can discover and manufacture/adapt units without owner-provided exact paths for routine cases;
- derived assets have clean lineage and live outside vendor packages;
- common materials/scale/join/collision failure modes have a cheap validation path;
- assembly grammar/templates are sufficient to make materially different streets while preserving CITY access/elevation/threshold intent;
- adding another normal facade/shopfront/prop/module is now mainly production work rather than pipeline invention.

## FAIL

FAIL if the result is one beautiful hand-built scene instead of a factory, batch is mostly trivial variants, accepted CITY/B0 demand is ignored, every asset still needs bespoke import/material/mesh surgery, operator discovery depends on exact-path spoon-feeding, source packages are destructively modified, audited existing solutions were ignored and equivalent functionality rebuilt without evidence, or a huge city generator is built instead of modular production tooling.

## Handoff

`WP-PROD-ENV-02` consumes this factory and must prove **scene production at batch scale** with multiple distinct compositions, including at least one composition materially useful to B0. Only ENV-02 decides whether the current authoring operator should be upgraded to `PRIMARY_AUTHORING_PATH`.

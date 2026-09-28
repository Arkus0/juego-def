# WP-PROD-ENV-01 — Environment Asset + Assembly Factory

Status: **READY AFTER ASSET-00**  
Class: PRODUCTION FACTORY / ENVIRONMENT  
Depends on: `WP-PROD-ASSET-00` PASS  
Blocks: `WP-PROD-ENV-02`

## Claim

juego-def has a repeatable environment production factory that can turn the admitted source corpus into reusable, game-coherent architectural/urban assets and assemble them into streets/interiors without bespoke low-level work for every scene.

This WP does **not** pass because one street looks good. It passes when the machinery to make many streets/buildings/thresholds exists and a meaningful reusable asset batch has been produced through it.

## Binding inputs

- Visual Bible
- Port Town World Model
- Quaternius Production Knowledge
- `PROD-ASSET-00` catalogue/lineage conventions
- Production Authoring Decision (`BOUNDED_OPERATOR`)
- retained M0 scene as gameplay-scale reference

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

Not every family needs a custom generator. The factory is the **combined production path**: searchable source components + adaptation/derivation + templates/prefabs + assembly rules + validators + operator recipe.

## Required factory outputs

By PASS, retain:

1. `ENV_FACTORY.md` — authoritative short workflow;
2. lane-specific semantic catalogue/tags built on `PROD-ASSET-00`;
3. reusable juego-def-owned prefab/module library;
4. material/palette adaptation system or repeatable batch recipe;
5. donor-component extraction / derived-asset path using Blender/source editing where needed;
6. assembly templates/rules for facades, corners, thresholds, ground contact and repeated frontage;
7. cheap validation for scale, missing refs/materials, obvious collision/threshold faults and illegal proxy-as-keeper states;
8. a non-trivial **factory output batch**.

## Minimum batch proof

Produce at least **15 reusable environment production units** across multiple roles, with enough diversity that they can make genuinely different streets. A production unit may be a complete prefab or a reusable derived/module set, for example:

- facade/building variants;
- corner/termination pieces;
- shopfront/door/window sets;
- roof/trim kits;
- port/market props;
- street/ground modules;
- small interior/threshold sets.

Do not satisfy the count with 15 trivial recolours or microscopic pieces that cannot materially vary scenes.

## Architecture adaptation requirement

The factory must demonstrate all relevant reuse classes on real candidates where available:

- `DIRECT` — already fits;
- `ADAPTABLE` — material/detail/scale changes;
- `DONOR` — useful subcomponents extracted from unsuitable whole assets;
- `CREATE_DERIVED` — new juego-def-owned derivative where the source corpus cannot directly deliver the needed piece.

Pack names like medieval/fantasy/timber are not automatic rejection. Final composed fit governs acceptance.

## Assembly grammar

Define enough semantic rules that a worker/operator can request outcomes rather than exact object paths, including:

- frontage type/width bands;
- floor/height/silhouette guidance;
- corner/termination treatment;
- door/window rhythm;
- shop/service frontage roles;
- threshold/ground contact rules;
- material/palette families;
- clutter/signage density;
- landmark vs ordinary facade roles.

This is not a procedural city generator. It is a vocabulary for repeatable assisted assembly.

## Operator/tooling loop

`semantic brief -> catalogue search -> choose/reuse/adapt/derive -> prefab/module output -> validate -> gameplay-scale preview -> correct -> admit to factory library`

Use MCP in Unity for inspection/assembly/validation and Blender MCP/source tools for mesh derivation when materially useful. Small batch scripts/editor utilities are expected where they turn repeated manual work into routine production.

## Evidence

Retain under `Docs/evidence/WP-PROD-ENV-01/`:

- factory workflow;
- output inventory with lineage/reuse class;
- captures/previews of the batch;
- at least one donor/derived example from source to final output;
- validator results;
- tooling/scripts/templates retained because they materially reduce repeated work;
- known kit gaps still requiring future asset creation.

## PASS

PASS when:

- 15+ meaningful reusable production units exist across several environment roles;
- operator can discover and manufacture/adapt units without owner-provided exact paths for routine cases;
- derived assets have clean lineage and live outside vendor packages;
- common materials/scale/join/collision failure modes have a cheap validation path;
- assembly grammar/templates are sufficient to make materially different streets;
- adding another normal facade/shopfront/prop/module is now mainly production work rather than pipeline invention.

## FAIL

FAIL if:

- result is one beautiful hand-built scene instead of a factory;
- batch is mostly trivial variants;
- every asset still needs bespoke import/material/mesh surgery;
- operator discovery depends on exact path spoon-feeding;
- source packages are destructively modified;
- a huge city generator is built instead of modular production tooling.

## Handoff

`WP-PROD-ENV-02` consumes this factory and must prove **scene production at batch scale** with multiple distinct compositions. Only ENV-02 decides whether the current authoring operator should be upgraded to `PRIMARY_AUTHORING_PATH`.

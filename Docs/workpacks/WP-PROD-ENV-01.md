# WP-PROD-ENV-01 — Environment Recipe + Repeated-Build Proof

Status: **READY AFTER M0**  
Class: PRODUCTION FACTORY / ENVIRONMENT  
Depends on: `WP-M0-00` PASS  
Blocks: `WP-CITY-URBAN-01`; authoring-path revisit

## Claim

juego-def can repeatedly produce keeper-quality bounded streets/interiors in its intended northern port-town visual language using the simplest effective combination of Quaternius reuse, derived components, Unity, Blender where needed and the bounded MCP operator.

This WP is not complete after one attractive scene. It must prove a reusable recipe on **two materially different compositions**.

## Binding inputs

- Visual Bible
- Port Town World Model
- Quaternius Production Knowledge
- Production Authoring Decision (`BOUNDED_OPERATOR`)
- retained M0 scene as scale/gameplay reference

## Required outputs

1. `ENV_RECIPE.md` — concise production recipe that another worker/agent can follow;
2. first keeper-quality bounded environment composition;
3. second materially different composition produced with the same recipe;
4. admitted/rejected/proxy asset/component notes sufficient to explain what was reused and why;
5. runtime collision/walkability proof;
6. evidence sufficient to revisit `BOUNDED_OPERATOR` vs `PRIMARY_AUTHORING_PATH`.

The two outputs may be, for example:

- dense Casco/Mercado street + Muelle/working-port street;
- exterior street + small shop/bar threshold/interior;
- two different facade/street compositions with distinct topology and asset combinations.

They may **not** be trivial recolours/rearrangements of the same prefab row.

## Environment recipe must cover

- target pedestrian dimensions/ranges where useful;
- street width and building-height logic;
- facade rhythm and variation;
- corners/termination vistas/landmarks;
- entrances, thresholds and ground contact;
- wall/roof/facade joins;
- signage/props and clutter density;
- material/palette adaptation;
- lighting/atmosphere baseline;
- collision and traversal expectations;
- allowed proxy use;
- `DIRECT / ADAPTABLE / DONOR / CREATE_DERIVED` decision flow;
- when Blender derivation is cheaper/cleaner than forcing an unsuitable prefab;
- how the MCP operator discovers/selects assets without exact-path spoon-feeding where possible.

## Quaternius rule

Pack/theme labels are not visual vetoes. Medieval/fantasy/timber-origin assets may be adapted or mined as donor components if the composed result fits juego-def.

Before creating new geometry, inspect the lawful available corpus for:

- reusable full assets;
- separable facade/roof/window/door/trim pieces;
- props/vegetation/urban furniture;
- materials/textures/palettes;
- components worth deriving in Blender.

Do not force visibly wrong assets merely to maximize reuse.

## Operator loop

For each of the two compositions:

`brief -> autonomous asset/project inspection -> candidate assembly -> third-person capture -> Play Mode route -> diagnose -> correction pass(es) -> owner look review`

The operator should perform real Editor work, not only generate a one-shot scene-builder script. Procedural/batch code is allowed where it is the cheapest mechanism for repeated geometry, placement or validation.

## Mandatory automated route probe

Adapt the useful lesson from the prior prototype: run an automated character/controller traversal or equivalent route probe in Play Mode across the critical route.

It must detect/report obvious cases such as:

- blocked path/collision snag;
- impossible step/threshold;
- falling through/escaping geometry;
- route obstruction created by props;
- obviously invalid spawn/door approach.

This complements, not replaces, a human walk-through.

## Visual acceptance

Keeper environment output must be judged from third-person gameplay views, not isolated asset screenshots.

PASS requires the owner to accept that each composition:

- looks plausibly like the same game;
- is materially beyond dressed greybox;
- has coherent silhouette/rhythm/material use;
- feels intentionally composed rather than asset-store dumped;
- is pleasant/interesting to walk through at gameplay scale.

## Repeatability measurement

Record for build 1 and build 2:

- amount of owner manual rescue/clicking;
- exact-path hints needed;
- one-off scripts/utilities introduced;
- major failures/recovery;
- whether second build reused the recipe rather than rediscovering the process;
- qualitative reduction in setup/manipulation friction.

No need for false precision. The purpose is to decide whether production economics improved.

## Evidence

Retain under `Docs/evidence/WP-PROD-ENV-01/`:

- recipe;
- source/provenance/adaptation notes;
- captures from both scenes, including gameplay views;
- automated route-probe results;
- owner visual verdict;
- operator intervention/failure summary;
- list of remaining kit/look gaps;
- recommendation: keep `BOUNDED_OPERATOR`, upgrade to `PRIMARY_AUTHORING_PATH`, or downgrade.

## PASS

PASS when:

- two materially different keeper compositions exist;
- both survive Play Mode traversal and route probe;
- owner accepts both as representative of intended game quality/direction;
- recipe explains how to build a third without inventing a new framework;
- asset adaptation/derivation is lawful and documented enough to repeat;
- second build demonstrates meaningful reuse of the process;
- no major unresolved environment-production architecture problem remains for a bounded block.

## FAIL

FAIL if:

- only one good scene exists;
- second scene needs an unrelated bespoke workflow;
- compositions remain greybox + pasted assets;
- the operator requires persistent high manual rescue without an accepted mitigation;
- collision/playability is not validated;
- owner repeatedly rejects the composed look;
- work drifts into building a giant procedural city generator instead of proving a small production recipe.

## Handoff

On PASS:

- record the authoring-path revisit decision;
- feed the accepted recipe/assets into `WP-CITY-URBAN-01`;
- remaining environment work should primarily be breadth, art-direction refinement and new local needs rather than foundational pipeline invention.

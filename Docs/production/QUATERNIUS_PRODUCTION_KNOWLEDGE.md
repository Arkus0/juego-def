# Quaternius production knowledge

Status: **MIGRATED PRODUCTION KNOWLEDGE / NO TOOL ADOPTION IMPLIED**  
Date: 2026-09-28

## Executive conclusion

Do **not** begin by inventing a bespoke asset factory. Quaternius already has a reusable character/animation ecosystem, and public/commercial tooling demonstrates most of the hard production stages we expect to need. juego-def should first evaluate existing techniques in bounded real-content tests and implement only missing glue.

## Strong source-family findings

### Universal Base Characters

Useful because they provide a shared humanoid basis, reusable proportions, hairstyles and a rig designed for animation retargeting. This makes population variants materially more credible than unrelated bespoke NPC meshes.

### Modular Character Outfits

Treat as `ADAPTABLE` / `DONOR` input. Modular parts can be simplified, recolored, recombined and stripped of fantasy cues while keeping the shared humanoid basis.

### Universal Animation Library

High-value input for locomotion, ambient and acting coverage. Shared-rig compatibility and root/no-root variants support a reusable animation intake pipeline.

### Medieval Village MegaKit

Very high value as a **component library** because of modular walls, floors, roofs, openings, interiors and collision/source-project precedent. Source-pack genre is not final visual identity.

### Downtown City MegaKit

Potentially high-value urban breadth if lawfully owned/admitted later. Its modular streets/buildings and example shader/collision techniques are relevant, but this document does not authorize purchase.

## External technique/tool findings to preserve

| Tool/reference | Usefulness | Default stance |
|---|---|---|
| `ChilyerStudiosLLC/blender-character-pipeline` | proportion editing, body-topology clothing, real-animation validation, scripted export | HIGH-value reference/adapt |
| Tinqs clothing pipeline | staged `census -> prepare -> fit -> reduce -> bake -> skin -> export`, weight transfer and checkpoints | conceptual reference until code license is verified |
| Avelune | Quaternius character composition + shared animation data | high-value architecture reference |
| `QuaterniusUnityUtils` | UAL import automation and collision-prefab construction | spike before writing equivalent Unity tooling |
| `codec-xyz/game_export` | Blender collection -> FBX/Unity prefab, material remap, colliders | technique candidate; revalidate against current Unity serialization |
| Auto-Building | custom building-part collections, openings, facades, roofs, scatter | high-potential paid spike only if real task justifies it |
| Geo-Buildings | Geometry Nodes building generation with custom assets | cheaper alternative/watch candidate |
| `osm_building_grammar` | semantic roles for facade/window/door/shop/awning/balcony/shutter/chimney/gutter/etc. | strong reference for donor metadata/grammar |
| Material Batch Tools | repetitive Blender material/node normalization | external-tool candidate; license review before embedding anything |

## Production model

```text
LAWful SOURCE
   -> semantic catalog
   -> DIRECT / ADAPTABLE / DONOR / CREATE_DERIVED
   -> bounded adaptation
   -> assembly/composition
   -> third-person validation
   -> Unity/GC2 handoff
```

The semantic catalog should preserve at least role, dimensions, connection intent, material family and provenance. External tools may accelerate processing; they are not allowed to become visual/product authority.

## Environment recipe

For a representative source family:

1. select real donor components;
2. classify roles (`wall`, `opening`, `window`, `door`, `balcony`, `roof`, `trim`, `shopfront`, etc.);
3. produce a materially new facade/building/street composition;
4. normalize materials/palette and remove incompatible genre signals;
5. validate joins, ground contact and player-scale read;
6. test in Unity from third-person view;
7. repeat on a second brief without rebuilding the pipeline.

Success is not “generator ran”; success is **better/repeatable content with materially less repeated authoring**.

## Character recipe

1. shared base body/rig;
2. modular/adapted clothing and hair/accessories;
3. palette/material variants;
4. clipping/weight/scale validation;
5. real animation validation;
6. reusable prefab/variant output;
7. repeat without writing bespoke tooling for each person.

## Animation recipe

Prefer shared-skeleton/retarget reuse. Track clip function, root-motion/in-place/loop intent, import/rig settings and runtime presentation mapping. Validate technical import **and** visual result.

## License/provenance rule

Every actual asset/tool adoption must preserve exact source, acquisition evidence and license/version truth. Quaternius licensing has changed over time; never infer the license of an already acquired pack from the current website alone.

Do not redistribute source bytes merely because a tool or pack is usable in the game.

## Relationship to AI authoring

If the pending Unity AI/MCP authoring benchmark succeeds, these recipes become excellent operator briefs: the agent should discover source material, classify/adapt components, assemble, run Unity, inspect captures/errors and correct. If the benchmark fails, the same knowledge remains valid for manual or smaller-tool production.

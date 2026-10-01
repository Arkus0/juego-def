# WP-ENV01-AUTHORED-01 — ENV01 migration to Unity authored authority

Owner brief: 2026-10-01, current ENV01 → persistent, directly editable manual scene.

## Dependency check

- Consume the effective ENV01 scene and its existing meshes, prefabs, materials, colliders, lighting and gameplay helpers. Legacy ENV factory/diagnostic work is input, not newly accepted by this WP.
- Source: `Assets/JuegoDef/Scenes/ENV/ENV01_Casco_District.unity`, baseline repository `e3a012e4acf50b99413df16adfcd9444355cb691` plus inspected local scene/assets. The source scene is ignored by Git; record its full hash and asset lineage.
- Newly own: independent authored scene/assets, readable hierarchy, passive stable identities, inventory, consolidation candidates, regeneration exclusion and manual persistence evidence.
- Reopen an inherited assumption only if comparison reveals missing geometry/references or runtime/editor mutation of authored objects. Two inherited overlay API errors block Unity compilation; repair those calls only.

## Acceptance and Definition of Done

1. Preserve original scene bytes; create `ENV01_AUTHORED` without running a generator.
2. Retain effective world transforms, meshes/material content, colliders, lighting and gameplay references.
3. The copy is a normal Unity level, survives scene reopen, actual editor restart, domain reload and Play Mode without Generate/Rebuild.
4. Legacy automatic regeneration and mutable generated asset/prefab links cannot reauthorize the copy.
5. Distinguish Buildings, Streets, OpenSpaces, Props, Vegetation, Landmarks, RiverWater, GameplayHelpers and MiscLegacy.
6. Stable IDs on buildings, street references, principal open spaces and structural landmarks; identity must have no reconstruction behavior.
7. Inventory and future consolidation candidates refer to observed objects; no merges.
8. Save a controlled prop edit, verify it after restart/reload/Play and restore it after the test.
9. Check missing scripts/assets, renderer/collider equivalence, duplicate generation, original integrity and visual equivalence at street/product scale.
10. Limited commit/PR and strict Worker pre-review, frozen exact SHA for a fresh Reviewer. Worker does not issue independent PASS or merge.

## Forbidden scope

No redesign/layout edits, density additions, consolidation, facade/interior rebuild, new city generator, asset substitution, MAST, road reconstruction, general art/optimization pass, unnecessary legacy deletion or Director D0–D3 redevelopment.

## Reuse decisions

Consumed `Docs/research/EXISTING_ASSET_PIPELINE_RESEARCH.md` and ENV01 `REUSE_DECISIONS.md`.
USE existing Unity scene serialization, native prefab unpacking, existing materials/meshes/colliders and installed Git LFS. ADAPT existing fixed camera captures. REFERENCE_ONLY existing CASCO diagnostic candidate vocabulary. NOT_MATERIAL new Blender/exporter, Quaternius collision tooling, material normalization, Auto-Building, Geo-Buildings, MAST and new procedural grammars: this task freezes observed bytes and creates no new geometry. No purchase, new dependency or third-party code adoption.

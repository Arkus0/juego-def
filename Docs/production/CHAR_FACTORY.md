# Civilian character and wardrobe factory

CHAR-01 owns the fifteen existing civilians and the exact admitted outfit combinations in `char_compatibility.json`. The Owner's October 2 amendments replace rejected Quaternius heads with anatomical CC0 bundles and authorize bounded blink/gaze presentation. The admitted Quaternius body/donor families, 65-bone Humanoid skeleton and ANIM-01 sources remain. This is a Worker candidate; independent review and final Owner art acceptance are separate.

## Reconstructable inputs

- `char_recipes.json`: IDs, roles, body profile, anatomical head bundle, matched hairstyle, wardrobe, palette, mood and source idle.
- `char_body_profiles.json`: stature, mass, shoulders, hips, hands and posture inside the enforced source-relative human envelope. Superhero male is not admitted for civilians.
- `char_naturalism_forms.json`: authored face/mood and garment parameters. Legacy Quaternius head shaping supplies interface measurements; that head is removed from the final export.
- `Art/Characters/HumanHeads/source_manifest.json` and fifteen anatomical `.blend` bundles: heads, eyes, brows, lashes, everyday hair, source hashes and captured eyelid-closure vectors. A bundle couples sex and hairstyle.
- `Art/Characters/HumanSources/admission.json`: exact raw mesh/material/texture/eyelid-target subset, CC0 notices and derivation receipts. `makehuman:` catalogue IDs refer to these repository bytes.
- ASSET-00 catalogue and read-only vault: Quaternius bodies/donors. Chilyer's MIT `body_topo.py` is retained unchanged with its license.
- ANIM-01: accepted Humanoid import and UAL motions. `CharPosture` derives civilian hand/stance and per-person upper-body offsets; source root/foot/leg dynamics remain owned by ANIM.

[Reuse decisions](../evidence/WP-PROD-CHAR-01/REUSE_DECISIONS.md) record pins and licenses. MPFB 2.0.17 (`afb9f530a7c2741dedb8df0ebae2e0b183caec21`) is an external GPL authoring tool; its program code is not copied into Unity. Bundled admitted meshes/targets/textures and outputs are CC0. Regional photographs and the Owner's Shenmue/Yakuza examples are [references](../evidence/WP-PROD-CHAR-01/REGIONAL_ART_REFERENCE.md), never adopted photograph textures, likenesses or commercial meshes. No paid dependency or additional population is admitted.

## Normal production

Use Python with Pillow/NumPy, Blender 5.2.1 LTS and Unity 6000.3.24f1. Provision the existing admitted base/outfit/UAL packs and GC2 through their accepted routes. From the checkout root:

```powershell
python Tools/char_manifest.py
python Tools/char_textures.py
python Tools/char_skin.py
python Tools/char_stage.py
python Tools/char_human_textures.py --system-assets <unpacked-CC0-core> --mpfb-source <pinned-MPFB>
python Tools/char_audit.py lineage
python Tools/asset_catalog.py build
blender --background --factory-startup --python-exit-code 1 --python Tools/char_build.py
```

Normal assembly consumes retained anatomical bundles; it needs no MPFB in Unity. The texture step derives restrained albedos from admitted CC0 sources, darkens irises/limbal borders and preserves transparent cornea alpha. Own metallic-zero/smoothness controls and nondirectional geometry AO supply subtle skin variation. Eye materials use alpha clipping: opaque transparent-cornea faces produced the rejected white discs. AO/control maps import in linear space; albedos use sRGB.

`char_build.py` constructs weighted clothes, shapes the body/rig together, replaces the entire old head and joins the anatomical throat to the existing animated skeleton. Lower neck vertices inherit the complete supporting skin weights before covered skin is masked; disconnected visible head/hand remnants are not a valid support surface. Two anatomical lid shapes and four bounded eye shapes survive export; no face bones are added. One 65-bone rig, normalized weights and no animation clips are exported. Missing weights and incompatible donor rest poses fail.

Fifteen finished masters in `Art/Characters/Naturalism/` are inspectable generated outputs. Recipes, admitted bundles and common code own regeneration; editing an FBX/master alone is not a retained correction. `build_inventory.json` binds inputs, recipes, actual FBX hashes and semantic geometry, including complete blend-shape coordinates.

Stop this checkout's Unity Play Mode, refresh imports and wait for script compilation/domain reload. Use `Build seed prefabs` then `Create fit preview scene`, or `Tools/CharNaturalismRun.cs`. `CharFactory` rejects stale inputs/models, builds each Humanoid Avatar, assigns URP materials and configures `NpcPresentation`. Author Unity assets/importers/metadata through Editor APIs.

## Fit and construction

Explicit sewing-plane cuts interpolate source weights; deleting faces by centroids is insufficient. Tops retain source binding and ordinary ease. Thin double-sided cloth replaces coincident static inner shells. Fabric UVs use metre scale and shared restrained weave/smoothness.

Finish the supporting garment before adding another layer. Open coat/cardigan inner tees follow the finished outer surface, inset 12 mm with a 13 mm overlap. Hidden trouser waists retain a 20 mm overlap; skirt skin masks are bisected at their hem. Vests/backpack ribbons are cut from supporting cloth, with explicit openings and hidden inner-layer masks.

After head replacement, neck boundaries follow the actual throat. A continuous facing closes the shirt, with a limited sewing allowance that excludes arm/shoulder ray hits. Its hidden lower rows continue the measured retained throat section after the clavicle crop; measuring the discarded shoulder flare is forbidden. A turned collar replaces the old upright tube at the jaw. Hidden anatomical clavicle skin is cut below the shirt with a 20 mm overlap. Vest sewing lines are locally subdivided/rounded by at most 6 mm within the inner overlap, then rebound to the actual original weighted surface. Degenerate triangles are excluded from barycentric transfer. Continuous shared-corner edge bindings follow the resulting panel. Delantal/peto shoulder ribbons use the existing supporting-surface cut path, retaining its exact weights and participating in the final neckline fit.

Aprons/skirts are weighted surfaces, not collision cloth. Apron lower drape blends towards the thighs; ties/pockets follow their supporting surface. Footwear is shaped into ordinary shoes/boots. Caps fit the anatomical skull and trim hidden crown hair. Female facial hair is rejected, and female upper lips must also be inspected for misleading painted/shaded marks.

Outfit/palette rules, compatible body/sex, safe IDs, raw source hashes and proportions are executable. Component availability does not admit every combination. [Fit observations](../evidence/WP-PROD-CHAR-01/FIT_COMPATIBILITY.md) record causal failures and shared corrections.

## Living presentation

`NpcPresentation` adds irregular bilateral anatomical blinks, subtle head motion and bounded eye attention, with a stable private seed per recipe. The ordinary Animator owns idle breathing, weight shifts, gestures, locomotion and state selection. Presentation does not move the root or legs and restores its own head/morph contribution when disabled.

Attention consumes the existing GC2 `ShortcutPlayer.Instance`, using the player's Humanoid head or a floor-to-eye fallback. An optional explicit target supports previews. Range, frontal cone and angles are limited. No player, navigation, schedule, dialogue or movement authority is added.

`Tools/CharLivingRun.cs` checks all fifteen in Play Mode: complete asynchronous blinking, left/right attention, behind/far targets, no optional target, malformed timing, protected bones and disable restoration. It separately records uninterrupted waiter Animator/LateUpdate frames. Controlled `Sample` calls and actual live ticks are labelled separately. `CharEnvRun.Attention` exercises canonical GC2 attention in the actual isolated ENV fixture.

## New civilians and bundle authoring

Within covered combinations, select an admitted body/profile, head bundle with matched hairstyle, outfit and palette; supply a safe new ID and use the same assembly/fit gates. Reusing a head bundle under another ID is supported. New populations, unsupported combinations and arbitrary hairstyle swaps are not automatically admitted.

A new anatomical bundle uses the pinned external MPFB checkout and hash-bound MakeHuman core pack:

```powershell
blender --background --factory-startup --python-exit-code 1 --python Tools/char_human_sources.py -- --mpfb-source <pinned-checkout> --system-assets <unpacked-core>
```

The common author authors fictional head/mood parameters through public services, fits everyday hair, captures closure vectors and bakes nondirectional AO. Outside-UV AO background is white to prevent black mip fringes. Retain raw sources/notices and validate exact license/pin before adoption. Re-derive textures/receipts, lineage/catalogue, then the complete batch. New source production is inspectable authoring, not an unexplained export patch.

## Evidence and freeze

Inspect all fifteen clothed/bare-head portraits, three-quarter/profile views, full-body groups, and 10/20m colour/reduced silhouettes. Bare-head comparison hides hair, hats, glasses and male grooming, retaining anatomical brows/lids. Before portraits are preserved pre-naturalism WIP, never an accepted baseline.

Play Mode fit covers fifteen × Idle/Walk/Talking × four phases: 180 measured poses and 540 front/rear/side tiles. Dense safety samples 24 phases per motion and compares protected curves. Numeric checks cannot certify clipping, mood or final art quality. Correct the common rule or reject the combination; green bounds never waive a visible defect.

`CharEnvRun` runs only in the separate `ENV01Review` snapshot. Its disposable fixture uses actual ENV lighting, renderer, volumes and existing 55-degree player camera. Retain scene/overlay hashes and the complete snapshot locator; another host needs that exact snapshot to rerender. Original ENV bytes are not edited.

Regenerate into a scratch directory and compare semantic geometry, UVs, materials, weights, blend shapes and rest matrices. Exclude FBX timestamps and polygon enumeration/start corner, preserving winding. Unity rebuild must preserve serialized imports, GUIDs and references.

```powershell
blender --background --factory-startup --python-exit-code 1 --python Tools/char_build.py -- --output <scratch>
python Tools/char_audit.py repeat --other <scratch> --write
python Tools/char_audit.py negative --write
python Tools/asset_catalog.py validate
python Tools/char_evidence.py collect --audit <preserved-audit-root>
python Tools/char_audit.py verify
python Tools/char_evidence.py verify
```

Settle lineage/catalogue before the final build/captures: they are build inputs. Changed bound inputs invalidate evidence. Freeze after complete strict Worker pre-review at an exact 40-character SHA. Fresh independent Reviewer owns PASS/FAIL; Owner owns final visual acceptance. CHAR-01 does not certify population/FPS, player builds, arbitrary animation blending, running/sitting/contact, final navigation/dialogue integration or cloth simulation.

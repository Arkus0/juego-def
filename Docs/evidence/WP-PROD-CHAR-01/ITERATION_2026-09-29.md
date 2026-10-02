# CHAR iteration 2026-09-29 — human proportions, coherent wardrobes, northern skin, 15 people

Worker iteration on `codex/characters-01`, driven by three Owner remarks made while the batch was under review. **This is not a frozen candidate and not an independent PASS.** The formal six-person Play-Mode evidence in this folder (`fit_*.png`, `group_*.png`, `unity_runtime_validation.json`, `visual_review.json`, `repeatability.json`) describes the earlier six-recipe build and is **stale** for the current 15-recipe batch; regenerate it through the documented route before any freeze.

## Owner remarks and root causes

| Owner remark | Root cause (measured) | Correction |
|---|---|---|
| "Different, but monstrous: head and hips are not human." | Body profiles multiplied torso/hips/depth by 1.25–1.35 while the head stayed 1.0. Hip-joint width was +37 % over the source body on the market seed, +17–20 % on three others, shoulders up to +21 %; two of my own profiles pushed the nose +25 % and jaw +18 %. | Every profile re-authored inside human ranges (shoulders/hips about ±10 %, bounded belly/neck/stoop, no caricature faces). New `anthropometry` envelope in `char_compatibility.json`; `check_proportions` in `char_manifest.py` makes the Blender build fail outside it (hip/shoulder joint ratio vs the source body, head length, pelvis height). |
| "Clothes do not match: shoes do not go with trousers, which do not go with the shirt. Look at real northern people." | Slots were chosen independently; strong tiling normal maps made each garment look like a different material; several colours were saturated or pure black/white. | Reference pass (see `CHAR_COSTUME_RULES.md`); `outfitRules` (footwear by bottom, trainers only with casual tops, dark leather shoes) and a colour-discipline check per Visual Bible; fabric relief re-scaled and softened; per-role palettes. |
| "Why is everyone so tanned if this is Cantabria?" | The admitted `Light` skin atlas is itself a medium tan (median RGB 170,116,81); tints can only darken it, and the review sun was golden. | `Tools/char_skin.py` derives a pale-peach atlas from the same source atlas (shading preserved); six tones (pale, fair, olive, weathered, tan, brown) are per-person tints. Cast: 4 pale, 6 fair, 2 olive, 2 weathered, 1 tan. Review light made neutral-northern. |

## What was added to the factory (all through `Tools/char_build.py`)

- Bodies: Superhero Female (identical rest skeleton, direct donor use) and Superhero Male (donor footwear refit through its own bone weights, bounded 35 mm).
- Garments: shirt/collar, T-shirt, striped jersey (real material bands), waistcoat with clean V, bistro apron and bib apron as **measured wrap sheets** that follow the clothed cross-section and hang from the pelvis with continuous thigh weights, overalls (bib, crossed straps, buttons), long skirt, scarf, tie, bow tie.
- Head: hair variety (male: balding, buzzed, slick-back, side-parted; female: bob, buns, ponytails, long), beard/moustache/muttonchops, thick brows, work cap, beret, beanie, flat cap, fedora; hair under headwear is trimmed without detaching the ponytail.
- Body-mass detail: `belly`, `neckScale`, `stoop` in `char_shapes.py`, applied to meshes (and stoop to rest bones) consistently.
- Layer order fixed generally: tops now sit outside trouser waists (fixes dark crescents at the hem); export is triangulated so Unity no longer discards twisted quads (holes at coat hems).
- Materials: five fabric families with albedo + normal (Cloth, Knit, Canvas, Denim, Leather), skin normal, rubber boots, per-palette skin/eyes/hair/beard identities; Avatar description is regenerated on every prefab build (fixes stale "Rig Error" mis-match messages).
- Review tooling: `CharReview` (isolated preview scene, real ANIM-01 poses, street stage, silhouette mode, numeric pose sweep), `Tools/char_stage.py` fixture textures, `Tools/char_preview.py` (fast Blender preview).

## Cast (15) — see `B0_ROLE_COVERAGE.md`

Original six (re-proportioned): market-worker, dock-worker, older-resident, younger-resident, office-worker, everyday-pedestrian. New: waiter-veteran, fishmonger, mechanic, shopkeeper, elder-woman, student, local-fan, bruiser, eccentric.

## Checks run

- `python Tools/char_manifest.py`: 15 recipes valid (footwear/outfit/colour rules, proportion envelope inputs).
- `python Tools/char_audit.py negative --write`: 36 rejections including outfit, colour, body-family and synthetic non-human-proportion cases.
- `python Tools/char_audit.py lineage` + `python Tools/asset_catalog.py build/validate`: 0 problems, 169 derived CHAR records.
- Unity `CharReview.PoseSweep` (edit mode): 15 people x idle/walk/talking x 4 phases = 180 samples, 0 problems (valid Humanoid avatar, no missing bones/materials, plausible bounds/ground). `review_pose_sweep.json`.
- Visual rounds (about 40 captures across front/side/back/three-quarter, idle/walk/talking, 2.5 m faces to 14 m groups, silhouettes): `review_2026-09-29/`.

## Known limitations (honest list)

- Face geometry is still the shared Quaternius head; individuality comes from hair, facial hair, brows, skin tone, age cues, glasses and the bounded jaw/nose/cheek profile values. Reading faces beyond about 10 m is not claimed.
- Aprons and skirts are pelvis-hung sheets with capped thigh weights, not cloth simulation; extreme leg poses, sitting and running are not admitted.
- The overalls bib edge is slightly jagged in walking close-ups; the bistro apron leaves the outer thigh uncovered in a wide stance.
- Unity Play-Mode formal evidence, the ENV composite and the independent review are still to do; hair colour bands, eye colour and per-NPC posture life are minimal.
- The review street is a neutral stand-in (cobble, plaster, doors/windows for scale); it is not ENV and was not compared pixel-for-pixel with it.

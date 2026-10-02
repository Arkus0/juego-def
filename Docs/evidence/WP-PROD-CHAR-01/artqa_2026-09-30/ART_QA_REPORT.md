# CHAR art / visual QA pass — 2026-09-30

Worker pass on `codex/characters-01` (uncommitted, not frozen, not an independent PASS). Owner brief: inspect every NPC visually, fix in the
factory, re-inspect after each change, keep variety, raise coherence. All fixes are **factory rules** (recipe, family, profile or shared
code); no exported mesh was patched by hand.

## Method

- `CharReview` renders (Edit Mode, real ANIM-01 poses): front / three-quarter / side / back lineups, 5-person groups, 1.2-1.35 m
  conversation close-ups for all 15, walk phases, 10-20 m silhouette. Renders judged with SSAO off (asset read) — see *ENV SSAO* below.
- Blender probes measured the sources: Quaternius male = **8.1-8.6 heads tall**, male **hand = 1.0 head** (human ~0.8).
- Real-context check in the **ENV-01 CASCO** (`C:/Juego Def`, ENV editor): the 15 prefabs + dependencies were copied to a throw-away
  `Assets/_CharQA_tmp`, posed and baked as `DontSave` objects on `Espina_E` and `Espina_Plaza`, captured with ENV's own
  `EnvPreview.Capture` / `EnvWalk.GameCamera` (ENV lighting, grading, SSAO, GC2 player mannequin for scale), then deleted.
  The CASCO scene was never dirtied and the ENV worktree ended clean (`git status` empty).
- After every fix: rebuild (Blender 15 recipes ~16 s + `CharFactory.Build`) and re-render the affected views.

## Evidence (this folder)

| File | What |
|---|---|
| `ba_lineup_yaw0/-40/90/180.jpg` | Before (top) / after (bottom): front, 3/4, side, back, same pose/camera |
| `ba_group0/1/2_34.jpg` | Before/after 5-person groups, three-quarter |
| `before_faces_conversation.jpg`, `after_faces_conversation.jpg` | All 15 at 1.35 m |
| `before_street_recipe_poses_2026-09-29.jpg`, `after_street_recipe_poses.jpg` | Personality idles on the review street |
| `after_silhouette.jpg`, `after_walk_10/60.jpg` | Silhouette read, skirts/aprons in walk |
| `context_casco/final_*.jpg` | Real CASCO: game camera with player, eye level street, plaza, 4 conversation shots |
| `context_casco/before-fix_*.jpg` | CASCO defects that only showed in context (skin-like blouse, black straps, cap) |

## Findings and factory corrections (priority order)

| # | Seen | Root cause (measured) | Correction (where) |
|---|---|---|---|
| 1 | Everyone in a fighting stance: fists, feet wide, chest out | UAL clips hold `*.Stretched` -0.9 on every finger, `Upper Leg In-Out` +0.25, `UpperChest` -0.5 | `Editor/Char/CharPosture.cs`: derived civilian clips — relaxed hand table (picked from a rendered grid), leg spread x0.45, chest x0.55, forearm pronation -0.6 so opened hands face the thigh. Only held components change; gestures and walk dynamics survive. Controller + `CharReview` use them. |
| 2 | Pin heads on tall men, "inflated" bodies | Sources 8.1-8.6 heads tall; a head *ratio* made 1.9 m men worse | `char_shapes.solve_head`: absolute head height per family (`anthropometry.headHeight`, mild height term). Cast now 7.1-7.8 heads. Envelope `headsTall` 6.9-8.0. |
| 3 | Mitten hands | Male hand = 1.0 head | `bodies[].handScale` (male 0.92) scales hand mesh + finger bones about the wrist; envelope `handOverHead` 0.70-0.90 (cast 0.75-0.85). |
| 4 | Doorman from another game | Superhero-male sculpt (lats, gym arms) | Bruiser moved to `regular_male` with a deliberate broad profile (shoulders 1.10, neck 1.09, new `armGirth` 1.08). `superhero_male` marked `NOT_FOR_CIVILIANS`; manifest rejects it. |
| 5 | Dock worker boxy | Hi-vis vest pushed 6.5 cm; heavy profile | Vest 4.6 cm, armholes follow a curve (no shoulder cap spikes), tall_heavy shoulders 1.05. |
| 6 | Smudged chests, weave size differs per NPC | Garments inherited skin-atlas UVs | `fabric_uvs`: world-scale cylindrical UVs (torso/arms/legs); one tiles-per-metre and smoothness per fabric family (`CharFactory.TilesPerMetre/FabricSmoothness`); calmer Cloth/Knit tiles. |
| 7 | Every jacket/cardigan/coat a boxy kimono; trench = bathrobe | Outer offset 6.5 cm, bell sleeves, 1.18/1.30 skirt flare | Outer 4.4 cm, sleeves taper 14 % to the cuff, coat skirt 1.07/1.12. |
| 8 | Inner tees as cardboard tubes | Flat neck cut under the chin | `scoop_neck` per top type + `tuck_neck` (cloth edge onto the neck); skin kept under the scoop. |
| 9 | Beanie with jagged flaring rim; cap with ear spikes; caps in sweater knit | Crowns cut from head topology (ear tips); cap used the top material | `skull_dome`: fitted smooth crown + turned-up cuff; cap bill longer and curved; caps always get their own `cap` slot. |
| 10 | Waiter = tuxedo bib, bow tie = sunglasses, grey epaulettes | V from 1.22 at 0.62 slope; 5x4 cm plates; armhole trim | V from 1.31 at 0.46; flared bow on a pinched knot; tailored waistcoat has no armhole band. |
| 11 | Scarves as red planks | Flat strap tails | Wrapped neck scarf only (tidy edges). |
| 12 | Watch floating off the wrist | Hand-bound torus at a fixed point | Band + case fitted to the measured wrist, bound to the forearm. |
| 13 | Knee skirt notched by the stepping leg | Rigid pelvis weights | Continuous drape weights (no tear across the centre). |
| 14 | All women share heavy blue eyeshadow + gloss; all men the same stubble | Painted in the source atlas | `char_skin.face_variant`: deterministic chroma shift (not a flat patch) → `natural`, `mature`, `older` (soft creases), `clean` (no stubble). Recipe key `face`. |
| 15 | Same face geometry for everyone | Only ±6 % jaw/nose/cheek | Two bounded axes `faceWidth` (0.94-1.06) and `chin` (-0.35..+0.6); per profile. |
| 16 | Hair from the wrong person | Twin space buns on the elder woman; spiky undercut on the veteran waiter | Elder: grey bob. Waiter: combed grey side part. |
| 17 | Retiree/older woman lacked their shirt | — | Older resident: pale blue shirt collar under the cardigan (low, tight collar band). |
| 18 | Counter / phone / walk idles frozen without context read as wrestling | Work poses used as street idles | `pose` = standalone civilian idle; `workPose` keeps the counter idle for stall placement. Idle mix: 5 relaxed idle, 3 look-around, 2 talking, 2 folded arms, 1 phone, 2 walking. |
| 19 | *CASCO only:* cream blouse / white tee read as a bare torso in warm sun | Warm light, open outer layer, bust relief | Inner layers relaxed and bust relief flattened; manifest rules `skin_like` neck layer + light-warm inner under open outer → reject. Elder blouse cool grey, student heather tee, eccentric pale grey-green. |
| 20 | *CASCO only:* straps, bag straps and cap bills near black in sun | Strip winding faced the body; URP Lit does not flip back-face normals | `orient_outward` pass on every cloth/accessory piece before export. |

## Verification run

- `python Tools/char_manifest.py` → 15 valid. `python Tools/char_audit.py negative --write` → **43** rejections (7 new: pin head, one-head
  hands, superhero civilian, skin-like neck layer, light warm inner under open outer, unknown face, male grooming on a woman).
- `char_audit.py lineage` (194 records; posture clips and face variants registered) + `asset_catalog.py build/validate` → 0 problems.
- Unity `CharFactory.Build` (stale-input guard exercised and passed after rebuild), `CharReview.PoseSweep` → 180 samples, 0 problems.
- Build metrics (all 15): heads tall 7.07-7.80, hand/head 0.75-0.85, shoulder/hip ratios inside the existing envelope.

## Tiers (current visual readiness)

| Tier | NPCs | Why |
|---|---|---|
| **A** — can front a close conversation now (with the caveat below) | waiter-veteran, older-resident, eccentric, fishmonger, elder-woman | Distinct head read (hair/facial hair/glasses/age texture/shape), role-specific kit, clean at 1.3 m in the CASCO sun |
| **B** — recurring, holds a conversation reasonably | shopkeeper, market-worker, mechanic, bruiser, local-fan, dock-worker | Strong role silhouette; faces rely on hair/headwear more than on the face itself |
| **C** — population | student, office-worker, everyday-pedestrian, younger-resident | Good at 4-20 m; faces are the shared base with light variation |

Caveat for A: faces are still the shared Quaternius heads. Before a *named* narrative character is locked, give it a bespoke head
variant (sculpted shape keys or a derived head mesh) — that is hero work, deliberately outside this factory pass.

## Deliberately not touched

- Head topology, facial rig/blendshapes (sources have none): identity comes from the systems above; hero faces are separate work.
- Beard/hair "clump" style: it is the Quaternius hair language; changing only beards would break coherence with the hair.
- Cloth simulation: aprons and skirts are drape-weighted sheets; in the walk the bistro apron still swings between the legs.
- UAL walk style (slightly bouncy, high knee): ANIM lane; the posture filter only narrows it and relaxes hands/chest.
- Small leftovers seen at 1 m: dock-worker vest has two small points at the shoulder straps; the eccentric's scarf has a ragged lower
  edge; shop-coat has two small grey tabs beside the scarf; the dock cap dome shows a pole highlight. None reads at gameplay distance.
- Formal CHAR-01 Play-Mode evidence (`fit_*`, `group_*`, `char_audit verify`) is still stale for this batch; regenerate before a freeze.

## Cross-lane finding (ENV lighting, not changed)

ENV-01's SSAO (`JD_Renderer`: intensity 1.8, radius 0.55, falloff 70) puts visible grain on faces and shirts in shade at conversation
distance and blackens garment crevices (collars, neck of a shirt). See `context_casco/final_talk_waiter.jpg` (under an awning) vs
`final_talk_eccentric.jpg` (sun). Suggest ENV test radius ≤ 0.25 / higher sample count, or a conversation-camera override. This
checkout still carries the bootstrap SSAO (3.0 / 0.035), which produces a different smudge; `CharReview` now takes `ao: off|env|branch`.

## Rules for the next NPC batch (now encoded)

1. Heads are sized in metres (`anthropometry.headHeight`), never inherited from the source; build fails outside 6.9-8.0 heads.
2. Hands carry the family `handScale`; build fails outside 0.70-0.90 of the head.
3. No gym/superhero sculpt for civilians; mass comes from shoulders, torso, belly, `neckScale`, `armGirth`.
4. Civilians never play raw UAL clips: every idle/walk goes through `CharPosture`. Work idles (counter) are `workPose`, used in context.
5. Garments use world-scale fabric UVs; fabric (not slot) owns weave size and smoothness.
6. Layering offsets: top 3 cm, outer 4.4 cm with tapered sleeves, vests 4.6 cm with curved armholes; coats stay straight.
7. Necklines are scooped and tucked; collars are low, tight bands.
8. Headwear is fitted to the measured skull (domes/cuffs/bills), never cut from head topology.
9. Every cloth/strap piece is oriented outward before export (double-sided URP cloth is lit by its stored normal).
10. A neck layer must not read as skin; a light warm inner layer under an open jacket is rejected.
11. Pick `face` by age/role (women: natural/mature/older; men: clean/default/mature/older) and hair by age/role.
12. Review protocol before accepting a batch: 1.3 m conversation views for every NPC with AO off, then a CASCO context pass
    (sun + shade, game camera with the player) — several defects above only appeared in context.

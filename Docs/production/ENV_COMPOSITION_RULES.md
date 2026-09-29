# ENV composition rules — casco from a real reference

Status: **CURRENT** (WP-PROD-ENV-01, owner reviews 2026-09-28). Applies to CASCO composition; other districts reuse
the method with their own reference and terrain rules.
Evidence: [`../evidence/WP-PROD-ENV-01/CASCO_REFERENCE_STUDY.md`](../evidence/WP-PROD-ENV-01/CASCO_REFERENCE_STUDY.md).

## Method

1. **The reference is the soul, not a trace.** Every district starts from a real, measured zone
   (`Tools/env_morphology.py`, `Tools/env_district.py measure`): streets, widths, blocks, junctions, plazas, terrain.
   From it we keep structure — never buildings, names, signs or named landmarks. The playable network is then
   **authored** over the reference (`Env/Specs/districts/<id>.trace.json`): the spine, 2–3 secondary streets with
   personality, 1–2 strong descents to water, a few charming corners; the rest simplified (owner: "buen referente
   para el alma del casco; malo como calco literal").
2. **Legibility first.** A player must understand where the plaza, the bar, the tower/town hall and the way to the
   port are. Few streets, clear hierarchy, landmarks that close views.
3. **A/B always** against a generated baseline with the same kit when a rule is in doubt.

## Network and blocks

- **Widths between facades** (real → game): main 5.5–6.5 → 6.0–6.5 m on a shared surface; secondary 4.5 → 4.2–4.6;
  lanes 2.4–4.8 → 3.4–4.0 when longer than 8 m, 2.4–3.0 only in passes ≤ 8 m; widenings of 8–15 m every 40–60 m;
  node/plaza 13–29 → 10–14 m (the main river plaza may stay larger).
- **Height / width**: lanes 2–2.7; main street 1.5–2; plaza 0.7–1.
- **No straight run longer than ~40 m** in the casco. Main street: 12–22 m stretches with 5–15° bends; lanes 8–15 m
  with 10–20°. Never combine a width change and a bend at the same joint (the mitre moves Δoffset / sin θ).
- **Setback jogs** between neighbours: main 0.3–0.8 m in 30–40 % of pairs; lanes 0.4–1.5 m in 60–75 %; slight
  projections allowed. The skeleton takes them from the real plot subdivision.
- **Plots**: real frontages projected on each block edge, fitted to 2 m kit bays (row scale 0.88–1.14); a wide plot
  (≈10 m) every 30–40 m; depth 4/6/8 m, back-to-back rows meet but never cross.
- **Block corners**: acute tips (< 70°) become a short chamfer with a narrow "prow" plot; 70–100° corners get a corner
  building with an exposed side; obtuse bends mitre (one quoin); concave notches meet. A corner that lost its
  neighbour re-exposes its side (no open side walls, ever).
- **Nodes**: the main street reaches a plaza; the continuation leaves narrower with its axis shifted 3–6 m; a singular
  building stands proud on the axis and closes the view with a ~3 m pass beside it; a chamfered bar corner faces it.
- **Every bend and street end reveals a closure**: a house, a landmark, or a parapet/mirador where the town continues.

## Terrain (owner, 2026-09-28)

- The town **rises from the port** to Casco/Viviendas: sea below; balconies, miradores and streets crossing the slope.
- **Route grades by network length: 70 % comfortable (≤ 5 %), 20 % perceptible (5–10 %), 10 % strong (> 10 %) or
  stairs.** Stairs are an accent, never the norm; they must stay walkable for NPCs (risers ≤ 0.16 m).
- Casco: short slopes, stairs, small terraces; no big modern ramps. Mercado: flatter, stepped plazas. Muelle: almost
  flat at the water, real service ramps. Talleres: gentle slopes, wide vehicle ramps. Viviendas: hillside terraces,
  curved streets, retaining walls.
- Real relief is compressed and **redistributed** (the Potes core: 281–315 m, 55 % of its network steep) into a
  comfortable spine, a perceptible calle alta and short stair accents. Buildings stand on the terrain with a stone base
  down to the lowest ground around them.

## Water

Small/medium river, partially channelled between stone walls, integrated in the fabric and on an edge of the casco —
never a wide urban frontier. Casco on both banks for a short stretch, 1–2 small stone bridges, houses tight on the
water, a plaza opening to it behind a parapet, a stair down to the water. Downstream it runs to the port. Visual axis:
narrow street → stone bridge → houses over the channel → the sea hinted beyond.

## Casco look (lebaniego, owner photos)

- Ground: **canto rodado** with a **central strip of big flags**; flags in plazas; lanes darker and older.
- Walls: see the look rules below — families by street replace the old "rubble ground floor on ~70 %" rule; ashlar
  quoins only on seen corners of stone and old houses (never a pilaster on every party wall), slim or painted corners
  or none on rendered fronts; stone window surrounds on a share of fronts.
- Roofs: red Arab tile with little moss; **deep eaves on carved rafter tails (canecillos)**.
- **Solanas**: a timber gallery across the top floor of ~15 % of old houses (one door onto it, wing walls);
  casonas with arched portal, shield and solana.
- Life: striped awnings, wrought-iron hanging signs, terracotta pots, barrels at bars, benches and trees in plazas,
  fountain-trough in the plazuela, huertas behind stone walls with fruit trees. Few downpipes: deep eaves drip.
- 10–20 % anomalies: reformed aluminium, neglected fronts, a closed shop, a meter box, a clothesline.

## Look rules after the owner audit (2026-09-29, 45 points)

- **No kit formula on every house.** Facade families by street: all-render (most without quoins), render over a
  low stone base at varying heights, stone ground floor, all stone (old houses, casonas), rehabilitated, modern
  commercial ground floor. The stone base is never a continuous band down a street.
- **Materials age by building, not by kit tile**: each render/masonry material weathers with its own seed; masonry
  and paving repeat every 4 m; stone bonds (rubble, river stone, ashlar, slabs) and tones vary by building and wall.
- **Weathering has a cause**: damp and splash under downpipes, streaks under sills, rust under iron, run-off at
  seen corners, damp bands on the foot of walls in damp streets, repairs on old render; fresh fronts stay clean.
- **The present is visible**: aluminium/PVC joinery on reformed fronts, air conditioning, alarms, intercoms, house
  numbers, extractors, telecom boxes, gas risers, recycling bins, bike racks — sparse and placed where they fit.
- **Every commercial ground floor has a use** readable without its sign: named business (bar, café, sidrería,
  bakery, pharmacy, tobacconist, hardware, greengrocer, bank, hairdresser…), workshop, garage with its "vado",
  closed shop to let, or a ground floor turned home. One fascia per shop run; lettering, trade icons, notices are
  specific and few.
- **Glass is never a black plane**: a room behind, curtains and blinds at different heights, a restrained reflection.
- **Plants are rare and reasoned**: damp lanes and old doors keep more; species of the humid north in varied
  containers; stone benches where old neighbours sit.
- **Paving by reason**: the flag strip only on the main spine (the old cart track); finer canto on secondary streets,
  older canto and a setts drainage channel in lanes, setts on bridges, big flags on the plaza with a cobbled rim, flag
  bands along facades of the main streets, repair patches; door steps and thresholds meet the houses.
- **The plaza has a landmark and sub-spaces**: fountain with candelabra near the middle, the old plane tree with its
  ring bench, a riverside walk of trees and benches facing the water, terraces in front of the bars, planters at the
  edges — never trees on a grid.
- **The river is old infrastructure in constant rain**: water with depth over a cobble bed and rocks, foam at the
  walls, channel walls with water line, algae, drains, ferns and ivy; stone parapets and lamps on the bridge.
- **Light shows the work**: linear fog beyond the street, sky and fog from one preset, a lower warmer sun, darker
  ambient and building-scale ambient occlusion for contact shadow.

## Gameplay

The GC2 capsule needs 2.4 m clear only in short passes; no pinch under 1.2 m between bike, pier and bollard. The
route probe walks the whole authored tour (all streets, stairs, bridge) before a district is shown as done.

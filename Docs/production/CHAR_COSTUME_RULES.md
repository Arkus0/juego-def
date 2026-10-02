# Civilian costume + proportion rules (northern-Spain port town)

Status: Worker calibration, not Owner-accepted art direction. Purpose: stop outfits that "do not go together" and bodies that read as monsters.

## Why this exists

Owner review of the 15-person cast found (1) non-human proportions (head, hips) and (2) tops, trousers and shoes that did not belong to one person. Both were process failures: body profiles had drifted to +25–35 % on torso/hips while the head stayed constant, and each garment slot was chosen independently. This document is the checked rule set; `Tools/char_manifest.py` and `Tools/char_shapes.py` enforce the mechanical parts.

## Reference pass (2026-09-29)

Viewed (not copied, not stored in the repo) public photo search results for: street scenes in Aviles/Gijon, retirees with berets by the port, fish-market stalls in Aviles, fishing-port workers, waiters in black waistcoat and long white apron, overalled mechanics and older women in cardigan and mid-length skirt. Observed patterns, paraphrased:

| Group | What ordinary people actually wear |
|---|---|
| Market fish sellers | Jumper or polo under a **bright blue plastic/rubber apron**, sometimes white apron; **white rubber boots**; blue gloves; wool cap. |
| Fishing-port workers | Oilskin bib trousers/jackets in yellow or orange, green waders, dark rubber boots, wool hats. |
| Waiter (bar/sidreria) | White long-sleeve shirt, fitted **black waistcoat**, black bow tie, black trousers, long white waist apron, black leather shoes. Everything black or white. |
| Older men | Muted jacket or cardigan (navy, brown, grey), corduroy or wool trousers, flat cap/beret in dark wool, plain leather shoes; collared shirt. |
| Older women | Cardigan or quilted vest over blouse, mid-calf skirt or straight trousers, sensible dark flat shoes, grey set hair, bag on arm. |
| Workshop mechanics | Classic royal-blue **boiler suit**, plain tee or long-sleeve underneath, black safety boots. |
| General street | Dark jeans/chinos, navy/grey/green/burgundy knitwear, denim or waxed jackets, white trainers on the young; earth tones and navy dominate; saturated colour appears once per outfit. |

## Rules

The Owner's 2026-10-02 direction adds photographed Asturias/Cantabria people and a Shenmue treatment reference. Source links, observed details and per-person moods: [regional art reference](../evidence/WP-PROD-CHAR-01/REGIONAL_ART_REFERENCE.md). Every woman must have a clean upper lip, including the texture and scene shading. Resting mood and clothing fit must be observed in Unity; recipe validation alone is insufficient.

1. **One person, one wardrobe.** Top, trousers, shoes, outer layer and accessories are chosen together from the role row above; no slot is chosen independently.
2. **Footwear must fit the bottom** (`outfitRules.footwearByBottom`): work/overalls take work shoes or boots; skirts take ankle boots, flats or loafers; trainers only with casual tops. Rubber boots (`shoeFabric: rubber`) are allowed only for market/port roles.
3. **Shoes read as shoes**: leather footwear is dark (luma <= 0.34); white is reserved for trainers and market rubber boots.
4. **Colour**: at most one strongly saturated garment per person; the rest come from navy, charcoal, black, grey, cream, brown, olive or muted denim. Shirt and trousers never share the same mid-tone.
5. **Material family**: knit for jumpers/cardigans, cotton for shirts/tees, twill/canvas for work and coats, denim for jeans, smooth leather for shoes. Fabric relief is subtle and fine so garments read as one cloth family at 4–10 m.
6. **Silhouette carries role** (apron, waistcoat, boiler suit, jersey stripes, hat), never colour alone.
7. **Neck and inner layers never read as skin.** Warm light blouses/tees next to the face turned into a bare torso in the CASCO sun; the manifest rejects a skin-like neck layer and a light warm inner layer under an open jacket/coat (use cool tints or mid values).
8. **Hair belongs to the person.** Choose by age and role (no twin space buns on an elderly woman, no spiky undercut on a veteran waiter).
9. **Proportions stay human.** Every deviation from the source body is small; the factory rejects a build if any of these leave the envelope (`char_compatibility.json > anthropometry`): shoulder-joint width 0.90–1.12x the source body, hip-joint width 0.88–1.12x, head length 0.108–0.138 of stature, pelvis height 0.495–0.548 of stature. Current faces use the admitted anatomical bundles and deliberate age/mood parameters, hair, brows, grooming and restrained skin treatment. Scaling a rejected Quaternius nose/jaw into caricature is not an admitted facial route.

## Cast wardrobes (current)

| Recipe | Outfit |
|---|---|
| waiter-veteran | white shirt + collar, black waistcoat (V from mid-chest), bow tie, black trousers, long white bistro apron, black shoes; combed grey hair, moustache |
| fishmonger | heather-grey jumper, royal-blue rubber apron, dark work trousers, white rubber boots, navy wool beanie, beard |
| mechanic | royal-blue boiler suit, grey tee, faded-red cap, black boots |
| shopkeeper | pale blue-grey shop coat, black trousers, black flats, wine scarf, glasses |
| elder-woman | navy cardigan, cool pale-grey blouse, dark plum mid-calf skirt, dark ankle boots, glasses, handbag; short grey waves |
| student | faded denim jacket, heather-grey tee, dark indigo jeans, white canvas trainers, red backpack |
| local-fan | red/white striped football shirt, dark jeans, black trainers, muttonchops |
| bruiser | black jacket over dark tee, black trousers and boots, beard; broad Regular body (not the Superhero sculpt) |
| eccentric | cream straight coat, pale grey-green shirt, tobacco trousers, brown shoes and wide-brim hat, burgundy wrapped scarf, round glasses, moustache |
| older-resident | brown cardigan over a pale blue collared shirt, dark trousers, loafers, glasses, balding grey |
| market-worker, dock-worker, younger-resident, office-worker, everyday-pedestrian | original CHAR-01 seeds, re-proportioned to the human envelope |

# Visual Bible — juego-def

Status: **CURRENT PRODUCT ART DIRECTION**  
Date: 2026-09-28  
Origin: distilled from accepted Juego2 visual/product decisions; no Juego2 runtime architecture is inherited.

## 1. Style one-liner

A stylized low-poly **northern-Spain port town**: dense, damp, lived-in streets; old-town, market, working-port, workshop and residential layers; restrained materials and readable human-scale silhouettes; late-PS2 / early-PS3 production economy interpreted through modern Unity.

The target is **not photorealism** and not a literal geographical reconstruction asset by asset. The town should feel authored as one coherent Atlantic/northern-Spain world while reusing lawful source material aggressively and intelligently.

Shenmue/Yakuza-era references are about density, readability, lived-in composition and production economy, not copying protected content or literal rendering.

## 2. Positive language

- Flat or lightly graded albedo; restrained materials; shape/composition carries more detail than texture resolution.
- Chunky readable silhouettes at ordinary third-person distance.
- Damp Atlantic mood: overcast-friendly light, wet/dark surfaces, greens, localized warm interiors and nightlife.
- Stone, render/plaster, masonry, concrete and timber may coexist by street/building role.
- Wood is allowed in balconies, galleries, beams, shopfronts, workshops, port structures, interiors, stairs, porches and mixed assemblies.
- Dense frontage rhythm, corners, thresholds, alleys, shops, bars, workshops and work-port edges.
- Day/evening/night should materially change the social read without requiring a second art pipeline.
- Reused assets may remain intact, be adapted, or become donor components.

## 3. Rejection language

Avoid:

- photorealism or PBR micro-detail as a substitute for composition;
- generic sunny Mediterranean resort identity;
- final scenes dominated by obvious fantasy/alpine/medieval signals such as castles, town-wide thatch, exaggerated chalet massing or fantasy signage/weapons;
- blanket bans such as “wooden assets are forbidden” or “fantasy-labelled wardrobe is unusable”;
- leisure-marina identity replacing a working port;
- anonymous major-city/skyscraper language;
- visible primitive shells dressed with windows/roofs/props and presented as keeper architecture.

## 4. Palette and atmosphere

Useful family anchors, adjustable in the real Unity lighting baseline:

| Role | Reference |
|---|---|
| light stone / plaster | `#C9C3B6` |
| mid stone / masonry | `#A79F92` |
| shadowed stone | `#7E7568` |
| dark wet roof | `#4A3730` |
| timber | `#5C4433` |
| painted joinery green-blue | `#3E5A57` |
| damp green | `#4E7A43` |
| overcast sky range | `#B9C4C9` / `#93A3AC` |
| sea/port grey-green | `#3F5A5E` |
| warm interior/nightlife accent | `#E8B26A` |

Avoid pure black/white albedo and uncontrolled saturation. District identity may legitimately shift material balance and accent frequency.

## 5. Composition oracle

Human-scale third-person readability is the primary judge. Streets, thresholds, facade depth, roof/base junctions and ground contact must look intentional at player distance.

Final identity comes from the **composition** of:

- irregular massing and frontage rhythm;
- coherent material/palette treatment;
- damp northern light/weather;
- signage, shopfronts, utilities and street furniture;
- port/work/commercial ground detail;
- vegetation and terrain;
- selected hero landmarks and bespoke derivatives;
- character styling/activity context;
- day/evening/night presentation.

## 6. Reuse-first source policy

Use the maximum practical amount of lawful owned/admitted source material before seeking replacements.

Disposition order:

1. `DIRECT` — usable substantially as-is.
2. `ADAPTABLE` — keep as base after bounded material/mesh/part/composition treatment.
3. `DONOR` — whole source is unsuitable but useful walls, roofs, windows, doors, stairs, balconies, trim, props, clothing parts, etc. are recombined.
4. `CREATE_DERIVED` — build a reusable derivative from lawful source components when cheaper/better than preserving a whole source item.
5. `REJECT` — core silhouette/function/theme or adaptation cost remains incompatible.
6. `BLOCKED_EXTERNAL` — a material role remains uncovered after the previous routes have genuinely been tried.

Source pack labels are not visual oracles. A medieval/fantasy-origin piece may become valid after adaptation; a nominally modern asset may still fail scale or identity.

## 7. Quaternius interpretation

Quaternius is treated as an **editable upstream parts ecosystem**, not merely a collection of final prefabs. Universal Base Characters, Modular Character Outfits, Universal Animation Library, Medieval Village and other owned/admitted packs may contribute intact content, adapted content or donor components.

The final composed result, not the upstream pack label, decides visual fit.

## 8. Character/wardrobe rule

Ordinary population should come from reusable body/rig/wardrobe/material/accessory recipes. Fantasy-labelled clothing is not automatically rejected; useful tops, bottoms, footwear, bags, hats or coats may be simplified, recolored or recombined when the final civilian silhouette works. Armour, weapons and unmistakable fantasy ornament remain removal/rejection candidates.

## 9. Acquisition rule

Do not buy a new pack merely because current source material was filtered too strictly. External acquisition is justified only when a meaningful role remains blocked after `DIRECT`, `ADAPTABLE`, `DONOR` and reasonable derivative work, and when the expected quality/time gain materially exceeds the cost.

## 10. Final oracle

The decisive question is:

> **Does the composed third-person result read coherently as this game's northern-Spain port town?**

A scene may use a high proportion of reused assets and pass. A scene may use geographically plausible assets and still fail if it reads as dressed greybox, asset showroom or incoherent kitbash.

# WP-PROD-ENV-CASCO-V2-00 — Semantic Block Pilot

Status: **READY AFTER CITY-URBAN-00R**
Class: PRODUCT/ENV KEEPER PILOT
Depends on: `WP-CITY-URBAN-00R` PASS + current ENV01 reference candidate + Unity/GC2 bootstrap
Blocks: revised `WP-PROD-ENV-02` city-scale proof

## Claim

A representative piece of the current ENV01 CASCO can be rebuilt with **fewer, larger semantic buildings and fully deliberate ground** while preserving the visual character that makes ENV01 successful and materially improving third-person interior/gameplay usefulness.

This is a **pilot**, not a full CASCO rewrite.

## Starting evidence

Current ENV01 is retained as the visual/topological reference candidate.

Owner-supplied mechanical audit of the ENV01 source reports, at the audited candidate:

- domain about 196 x 236 m;
- 311 building plots;
- median frontage about 6.76 m;
- median footprint about 47.49 m2;
- 35 plots below a provisional 24 m2 footprint heuristic;
- 69 narrow plots under the audit's 4.6 m heuristic;
- about 30.8% building footprint;
- about 46.1% ground labelled yard/huerta;
- about 4.7% unclassified residual ground;
- hundreds of purely geometric same-row merge candidates.

These measurements are diagnostic inputs, **not product truth**. In particular, `yard/huerta` means classified by the current generator, not validated gameplay value.

## Pilot selection

Choose **one representative authored micro-area**, preferably equivalent to roughly 15–25 current plot units, containing enough complexity to test the new grammar.

The selected area should include several of:

- ordinary frontage;
- at least one narrow current plot;
- a corner or junction;
- a current yard/residual condition;
- useful elevation or rear condition;
- enough street identity that visual loss would be obvious.

Avoid choosing only the easiest straight row.

Freeze before/after viewpoints and route landmarks before physical modification.

## Target transformation

The pilot should normally reduce the chosen current parcel set to approximately **4–7 SemanticBuildings**, subject to spatial evidence.

The target is not count reduction by itself.

Each resulting SemanticBuilding must have:

- stable pilot ID;
- explicit use/programme;
- footprint justified by programme and street composition;
- one or more FacadeCells;
- entrance/access truth;
- exterior storeys;
- playable-storey policy;
- rear/yard/service relation;
- interior depth classification.

At least one building must preserve multiple apparent historical frontage bodies while acting as one semantic/gameplay property.

## Minimum programme coverage

The pilot must exercise at least:

1. one everyday commercial use;
2. one residential use;
3. one social/public-facing use such as bar/cafe/pension/common room or an equivalent justified use;
4. one multi-storey SemanticBuilding;
5. one rear/patio/service condition where the source morphology supports it.

One building may satisfy more than one role when architecturally plausible.

## Interior requirement

At least **three** resulting buildings must contain genuinely playable interiors deeper than the current threshold-box pattern.

At least one deep interior must support:

- third-person camera circulation;
- two NPC/player bodies passing or occupying the room without obvious collision absurdity;
- more than one functional zone/room;
- a legible entrance;
- a second spatial relationship such as stair, rear room, back door, patio, upper floor or service area.

Do not generate arbitrary room mazes to satisfy the test.

Programme drives volume:

`use/gameplay -> rooms/zones/circulation -> building volume -> FacadeCells`

not:

`existing narrow shell -> whatever rooms fit`.

## Ground-use requirement

Within the pilot boundary every retained square metre must be assigned deliberately.

Allowed outcomes include:

- building footprint;
- street/lane/steps;
- usable patio/courtyard;
- service/loading strip;
- garden/huerta with explicit resident/world/gameplay function;
- terrace;
- slope/retaining response;
- water edge;
- explicit scenic composition.

Tiny leftover slivers and accidental inaccessible gaps are FAIL unless they are eliminated or deliberately absorbed into a neighbouring role.

## Visual preservation gate

Before modification retain:

- top/plan capture;
- at least 3 street-level viewpoints;
- one approach/reveal view where available;
- route/landmark notes.

After modification reproduce the same views.

PASS requires the owner to recognize the pilot as the **same CASCO visual language and place family**, not a generic replacement.

Preserve where useful:

- apparent narrow facade rhythm;
- roof stepping;
- material variation;
- irregular historic bodies;
- street enclosure;
- framed views;
- landmark relationships.

Larger SemanticBuildings must not read automatically as monolithic modern blocks.

## Gameplay-scale validation

Run the current GC2/player path through the pilot.

At minimum validate:

- exterior walking route;
- threshold approach;
- interior camera clearance;
- door/corridor/stair usability where present;
- NPC/player occupancy scale;
- no accidental collision traps;
- no inaccessible residual wedges masquerading as useful space.

Automated probes may supplement but do not replace one human play/walk review.

## Non-goals

This WP does not:

- rebuild all CASCO;
- finalize whole-town building counts;
- require all buildings to be enterable;
- create a universal interior generator;
- redesign B0 Mercado-Muelle;
- require ENV Director smart-builders;
- require free-form AI generation;
- preserve every current ENV01 parcel or metre.

## Evidence

Retain under `Docs/evidence/WP-PROD-ENV-CASCO-V2-00/`:

- pilot boundary and source plot ledger;
- before/after plan;
- before/after matched viewpoints;
- SemanticBuilding ledger;
- FacadeCell-to-building mapping;
- InteriorProgramme summaries;
- ground-use ledger totaling the pilot boundary;
- GC2/play validation notes;
- defects/revisions;
- owner visual acceptance;
- exact authoritative spec/scene candidate SHA.

## PASS

PASS only when all are true:

- the pilot materially reduces semantic-building fragmentation;
- at least one multi-facade SemanticBuilding proves visual grain can survive consolidation;
- deep interiors are demonstrably more useful than current shallow threshold boxes;
- no unexplained residual ground remains inside the pilot boundary;
- third-person exterior/interior circulation works;
- the owner prefers the new block over the current ENV01 equivalent;
- matched viewpoints preserve CASCO identity;
- the technique is repeatable without bespoke one-off surgery for every building.

## FAIL

FAIL if:

- the result is merely current buildings scaled up;
- merged buildings become visually monolithic;
- interiors remain narrow boxes;
- residual/yards are relabelled rather than justified;
- the pilot only works by destroying street character;
- count targets are met while route/composition quality degrades;
- it requires a one-off scene hack that cannot seed the rest of CASCO.

## Handoff

On PASS, use the pilot evidence to define the full CASCO-V2 reconstruction grammar and only then extend Director smart builders with proven operations such as:

- merge/split SemanticBuilding;
- assign programme;
- set playable floors;
- edit footprint/depth;
- preserve/recompose FacadeCells;
- create courtyard/service access;
- validate interior/playability.

Do not build these operations speculatively before the pilot proves the underlying design.

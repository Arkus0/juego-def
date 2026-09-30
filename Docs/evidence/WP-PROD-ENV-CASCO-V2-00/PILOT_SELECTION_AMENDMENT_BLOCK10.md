# CASCO-V2 pilot-selection amendment — K2 -> Block 10 micro-area

Status: **PROPOSED / REVIEW REQUIRED**
Date: 2026-09-30
Scope: selection-only amendment to accepted `WP-PROD-ENV-CASCO-V2-00`
Accepted authority preserved: PR #19 / candidate `09f8b226f432ff8b1bec921ce2a33b88ce3820da`

## Intent

This amendment changes **only the physical pilot selection**.

It does not reopen or weaken any accepted CITY-00R or CASCO-V2 rule: reference freeze, protected legacy A/B, programme-first design, semantic-building limits, exterior-space accounting, runtime/GC2 proof, NPC/camera/access checks, utility thresholds, visual matched-view gate, anti-gaming, provenance, independent review and all forbidden scope remain binding exactly as accepted.

Original accepted pilot: **K2 / 23 existing assembled bodies**.

Proposed pilot: **bounded Block 10 micro-area / 22 existing assembled bodies**.

## Exact source

Recomputed directly from:

- `ENV_REF_SHA = 246756c72d7181cd034c04c6b5cde163d076cb66`
- `Unity/JuegoDef/Assets/JuegoDef/Env/Specs/districts/ENV01_Casco_District.json`
- Git blob SHA: `93e15adc4ceabb66674676b5330e2a52f0bdfe23`
- accepted evidence records the same spec content SHA256 as `942fb24f31026da77b9469aee0ad32db8632a2d49fa915bea74ce4c0ceeef9c9`.

No newer ENV01 bytes are used for this amendment.

## Proposed boundary

Select **all non-wall plots** from exactly these seven contiguous Block 10 rows:

- `K10_3` — Callejon_Arco — 5 bodies
- `K10_4` — Calle_Alta_C — 4
- `K10_5` — Calle_Alta_O — 4
- `K10_6` — Cimavilla_Baja — 2
- `K10_7` — Cimavilla_Baja — 1
- `K10_9` — Cantabra — 1
- `K10_10` — Cantabra — 5

Total: **22 source bodies**.

IDs are deterministic row/index IDs:

`K10_3_0..4`,
`K10_4_0..3`,
`K10_5_0..3`,
`K10_6_0..1`,
`K10_7_0`,
`K10_9_0`,
`K10_10_0..4`.

This is **not all of block==10**. The full Block 10 has 27 non-wall bodies and was correctly rejected by PR19 as exceeding the initial ~15–25 pilot range. The amendment deliberately defines a bounded coherent micro-area rather than relabelling the whole block.

The excluded northern/eastern spur rows (`K10_0`, `K10_1`, `K10_2`, `K10_11`) are excluded as complete rows, not cherry-picked individual easy plots. They extend into Espina_Nodo / the outer Cantabra-Arco continuation and are not needed to exercise the ordinary-block hypothesis.

## Exact mechanical measures

Computed from the exact spec above, using `w * depth` only as nominal source-body footprint (not usable interior area):

| Metric | Block 10 micro-area |
| --- | ---: |
| source bodies | 22 |
| summed frontage | 150.158 m |
| summed nominal footprint | 1,110.934 m² |
| frontage min / median / max | 2.571 / 6.089 / 13.694 m |
| footprint min / median / max | 15.426 / 47.429 / 109.552 m² |
| frontage < 4 m | 3 |
| frontage <= 4.6 m | 6 |
| nominal footprint < 24 m² | 4 |
| closed_residential / mixed_commercial | 14 / 8 |
| floors 2 / 3 / 4 | 2 / 13 / 7 |
| OSM-real false | 1 |

Street distribution:

- Cantabra: 6
- Callejon_Arco: 5
- Calle_Alta_C: 4
- Calle_Alta_O: 4
- Cimavilla_Baja: 3

Roles: 14 secondary + 8 lane.

## Why amend K2

The amendment is not because K2 is invalid. K2 remains a defensible pilot.

The question is which pilot better falsifies the **generalisable semantic-building grammar** before ENV02.

Exact-spec comparison:

| Property | Accepted K2 | Proposed Block 10 micro-area |
| --- | ---: | ---: |
| bodies | 23 | 22 |
| summed frontage | 157.343 m | 150.158 m |
| nominal footprint | 1,011.226 m² | 1,110.934 m² |
| median frontage | 6.783 m | 6.089 m |
| frontage <= 4.6 m | 5 | 6 |
| footprint < 24 m² | 4 | 4 |
| street/role character | 11 Ribera + 7 plaza + 5 river-role bodies | 5 ordinary streets; 14 secondary + 8 lane |

K2 is intentionally rich but unusually tied to **plaza + Ribera + river-edge** conditions: 12/23 source bodies are plaza/river-role fabric. That is valuable for a hero/special-edge test, but it can let a successful pilot depend on exceptional public/waterfront geometry.

Block 10 is a stronger first falsifier for the reusable grammar because it combines:

- five ordinary street fronts and several orientations;
- lane + secondary hierarchy;
- narrow and sub-24 m² source bodies at comparable pressure to K2;
- long same-block frontage chains plus rear/back-to-back relationships;
- commercial/residential mix without relying on plaza or river-edge special cases;
- enough complexity to expose whether FacadeCells can preserve historical grain while 22 source bodies become 4–7 real semantic properties.

If this ordinary fabric cannot be consolidated without destroying character, the whole-city semantic-building thesis is in trouble. If it works here, K2 remains a valuable later special-edge application rather than the sole first proof.

## Anti-gaming / boundary rule

The Worker may not shrink this selection further after seeing difficult plots.

The pilot boundary is all non-wall bodies from the seven rows above. Any later exclusion/addition requires a new explicit amendment with physical evidence.

The same accepted target remains: **4–7 semantic buildings**. Count is not sufficient for PASS.

## Viewpoint substitution

The accepted matched-view rigor is unchanged: >=8 A/B paired viewpoints, identical camera/render state, day+dusk/night at >=2 public stations, same third-person walkthrough and Owner + Reviewer character falsification.

Because K2-specific plaza/Ribera stations no longer cover the pilot, the Block 10 implementation must freeze before B changes:

- one Calle Alta approach in each direction;
- one Callejon Arco approach;
- one Cimavilla/Cantabra transition;
- two threshold/street gameplay views;
- one roof/oblique overview;
- one rear/court/back-to-back view;
- plus inherited ENV01 control shots where they materially show surrounding character.

Inherited shots that do not show the Block 10 micro-area remain controls only and cannot substitute for pilot coverage.

## Acceptance of this amendment

PASS for this amendment means only:

1. exact-source measures above are reproducible;
2. the seven-row selection is spatially coherent on reconstructed ENV01;
3. it remains within the accepted ~15–25 source-body pilot scale;
4. Reviewer agrees the ordinary-fabric rationale materially improves falsification value;
5. no other PR19 contract provision was weakened.

This amendment does **not** PASS CASCO-V2 implementation.

# CASCO-V2 pilot selection — Block 10 micro-area

Status: **PROPOSED PILOT BOUNDARY / ARCHITECT SELECTION**
Source: owner-supplied CASCO mechanical audit over `worker/prod-env-01@246756c`

## Decision

Use the central Block 10 micro-area spanning:

- `Callejon_Arco`
- `Calle_Alta_C`
- `Calle_Alta_O`
- `Cimavilla_Baja`
- `Cantabra`

as the first physical CASCO-V2 pilot.

This is deliberately **not** the easiest straight frontage. It contains multiple orientations, secondary + lane conditions, rear contacts, several very small/narrow plots and enough ordinary fabric that failure to preserve ENV01 character will be visible.

## Source plots

22 current plots:

`K10_3_0`, `K10_3_1`, `K10_3_2`, `K10_3_3`, `K10_3_4`,
`K10_4_0`, `K10_4_1`, `K10_4_2`, `K10_4_3`,
`K10_5_0`, `K10_5_1`, `K10_5_2`, `K10_5_3`,
`K10_6_0`, `K10_6_1`, `K10_7_0`, `K10_9_0`,
`K10_10_0`, `K10_10_1`, `K10_10_2`, `K10_10_3`, `K10_10_4`.

Mechanical audit summary for these source plots:

- 22 current plot-buildings;
- ~1,110.9 m2 summed current building footprint;
- ~150.2 m summed current frontage across the selected rows;
- 4 plots below the audit's provisional 24 m2 footprint threshold;
- 6 plots flagged narrow by the audit;
- footprint range ~15.4–109.6 m2; median ~47.4 m2.

These values are diagnostics, not acceptance targets.

## Why this area

The area is suitable because it forces the pilot to solve several real problems at once:

1. **narrow-building fragmentation** rather than only comfortable source plots;
2. **multiple street faces/orientations**, so SemanticBuildings cannot be faked as one straight mega-row;
3. **rear adjacency**, forcing deliberate decisions about depth, party walls, yards and service space;
4. **ordinary architecture**, so success cannot depend on bespoke hero-landmark treatment;
5. sufficient source fabric to target roughly **4–7 SemanticBuildings** while still preserving many FacadeCells.

## Binding preservation rule

Before changing geometry, freeze:

- one plan/top capture of this boundary;
- at least three street-level matched viewpoints;
- one movement path covering Calle Alta -> Callejon Arco/Cimavilla -> Cantabra where current connectivity permits;
- source plot-to-view ledger.

No source plot ID is sacred. The **street identity, enclosure, route legibility and facade rhythm** are the preservation target.

## First-pass programme hypothesis

The exact grouping is intentionally **not frozen before visual/GC2 iteration**, but the pilot should be capable of resolving approximately:

- 1 social/commercial building (bar/cafe/pension-like);
- 1 ordinary shop + rear/service component;
- 2–3 residential/mixed buildings;
- 1 larger multi-storey mixed property;
- optional sixth/seventh property only if needed to preserve corner/street rhythm.

Several current plots may become multiple FacadeCells of the same SemanticBuilding.

## Rejection conditions

Abandon this boundary and document why only if direct scene inspection shows that:

- the area is not actually a coherent walkable micro-area despite the source graph;
- required matched viewpoints cannot be captured;
- its geometry is dominated by a hidden special-case not visible in the audit;
- it cannot exercise at least three deep interior programmes without distorting streets.

Do not switch to an easier pilot merely because this area is harder to consolidate.

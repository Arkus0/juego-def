# WP-POTES-07 — Potes Core Integration + District Lock

Status: **BLOCKED UNTIL ALL REQUIRED POTES SECTORS PASS**  
Class: UNITY ENVIRONMENT / DISTRICT INTEGRATION  
Depends on: `WP-POTES-00` PASS + `WP-POTES-01/02/03/04` as applicable + `WP-POTES-05/06` when required by the accepted sector plan  
Outcome: **FIRST PHYSICAL DISTRICT LOCKED**

## Claim

All accepted Potes sectors form one continuous keeper-quality historic-core district that can be retained as the game's dense urban foundation and extended later through the preserved outward interfaces.

This WP integrates and validates; it does not enlarge or redesign the core.

## District scope

The final district must contain **exactly the real buildings and public-space authority accepted in POTES-00**, nominally ~55–65 buildings.

Resolve only cross-sector defects:

- duplicate/missing objects at seams;
- party-wall/roof discontinuities;
- terrain cracks;
- street/step/retaining discontinuities;
- river/bridge continuity;
- lighting/exposure discontinuities;
- collision/NavMesh/traversal discontinuities;
- obvious repeated dressing artifacts introduced independently by sector batches.

Do not change the accepted perimeter or reconstruct a new town-wide procedural pass.

## Continuous traversal proof

Using the real GC2 third-person player/camera, prove:

- complete intended public-route connectivity across the entire core;
- at least one full edge-to-edge traversal;
- all important loops implied by POTES-00 are continuous;
- every bridge/stair/grade intended as public path is traversable;
- no sector boundary is perceptible through broken geometry/collision/navigation;
- preserved outward expansion interfaces remain usable and visibly unfinished only in an intentional, production-safe way.

## Visual district proof

Capture:

- POTES-00 fixed reference viewpoints reproduced in the integrated district;
- representative street-level views across every sector;
- at least two long cross-sector sightlines;
- an aerial/diagnostic view proving perimeter and sector integration;
- day/lighting condition used as the canonical casco baseline.

Owner performs final **District Look Gate**.

## Identity and 1:1 audit

Reconcile the integrated Unity output against the POTES-00 ledgers:

- every accepted `POT-Bxxx` appears exactly once;
- no extra permanent building has appeared;
- street/public-space elements are complete;
- reference-driven facade facts remain intact after integration;
- any accepted approximation/UNKNOWN resolution is traceable.

## Runtime/production health

Run the relevant project validators and retain:

- missing reference/material checks;
- collision/route checks;
- NavMesh/navigation sanity if used by the current project;
- scene/rebuild determinism checks where the environment path supports them;
- basic profiler/scene-complexity snapshot sufficient to detect an obvious integration regression;
- no destructive changes to source/vendor packages.

This is not final platform optimization.

## Gameplay-content boundary

POTES-07 locks the **physical first district**, not 40–60% of finished game content.

At lock it should support later insertion of:

- ~20–30 functional/enterable destinations;
- ~5–8 deep/hero interiors;
- ordinary residential interiors via a future bounded system;
- NPC routines;
- dialogue/investigation;
- missions/substories;
- compact minigames.

Those systems/content remain separate work.

## Expansion contract

Preserve the POTES-00 outward seams for later:

- market/civic zone;
- residential zone;
- port/workshops/industrial zone;

as defined by the accepted reference/sector plan.

The next map expansion must attach through these interfaces rather than silently extending the historic core.

## Evidence

Retain under `Docs/evidence/WP-POTES-07/`:

- exact consumed sector SHAs;
- complete building/public-space reconciliation;
- seam defect/fix ledger;
- whole-core route proof;
- fixed-view and cross-sector captures;
- District Look Gate record;
- runtime/validator snapshot;
- outward-interface proof;
- strict Worker pre-review.

## Acceptance

PASS requires:

- all required sectors accepted and present;
- exact accepted core membership retained;
- whole core reads as one continuous place;
- no material seam defect survives;
- intended public routes/loops are traversable;
- reference identity remains recognisable from the accepted views;
- Owner accepts the integrated district visually;
- outward interfaces remain available;
- no hidden expansion beyond POTES-00 occurred.

## FAIL

FAIL if integration changes the real-town authority, hides sector problems with fake closure geometry, leaves broken loops/seams, introduces duplicate/missing buildings, or uses “district complete” to claim interiors/NPC/missions that were never built.

## Definition of Done

Freeze exact `PRODUCT_SHA`, perform strict Worker pre-review, then fresh independent Reviewer.

After PASS, the **Potes historic core is the first locked physical district of juego-def**. It is designed to host roughly **40–60% of final authored activity weight**, while later zones provide the remaining game space with lower building density and larger open/systemic areas.

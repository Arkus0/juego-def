# WP-PROD-CHAR-02 — Civilian Batch Production Proof

Status: **READY AFTER CHAR-01**  
Class: PRODUCTION SCALE PROOF / CHARACTERS  
Depends on: `WP-PROD-CHAR-01` PASS  
Blocks: `WP-CITY-URBAN-01`

## Claim

The civilian factory scales from a seed set to a useful population batch without collapsing into clones, bespoke repairs or manual bookkeeping. After PASS, producing dozens more ordinary NPC visuals should be content production, not character-pipeline R&D.

## Required output

Produce **12–20 ordinary civilian prefabs/variants** through the accepted factory.

The batch must demonstrate useful breadth across:

- silhouette/body presentation where supported;
- age presentation where available;
- work/social role cues;
- wardrobe combinations;
- palette/material variation;
- hair/head/accessories;
- several variants that are materially different rather than recolours.

## Batch-generation requirement

The worker/operator must be able to request a batch semantically (for example, "4 dock/market workers, 4 residents, 4 casual/service/nightlife civilians") and use the factory catalogue/compatibility rules to produce candidates without owner-provided exact asset paths for each NPC.

Manual visual selection/rejection is expected. Manual low-level setup for every prefab is not.

## Coherence + clone test

Place at least **8 generated civilians together in one gameplay-scale scene** and inspect:

- obvious clone repetition;
- palette clustering;
- repeated silhouette/outfit combinations;
- clipping/material failures exposed only in group use;
- scale consistency;
- render/performance red flags at first-block population scale.

The factory should support regenerating/recombining a rejected clone-like subset without redesign.

## Animation readiness

Every retained civilian must be compatible with the accepted/shared humanoid animation path or explicitly tagged with a known limitation. At least several must be consumed by `PROD-ANIM-02` without per-character rig surgery.

## Evidence

Retain under `Docs/evidence/WP-PROD-CHAR-02/`:

- batch inventory with prefab + source lineage;
- semantic request/input used to generate the batch;
- group captures of 8+ civilians;
- rejected/regenerated variants and reasons;
- repeated setup/intervention notes;
- simple first-block performance observation.

## PASS

PASS when:

- 12–20 usable civilians exist from the same factory;
- group reads as one town population rather than unrelated packs or obvious clones;
- batch generation does not require exact-path spoon-feeding or bespoke rig setup per NPC;
- rejected combinations can be replaced through the same workflow;
- no systemic clipping/rig/material blocker remains;
- owner accepts the batch as sufficient visual population language for `CITY-URBAN-01`;
- scaling later toward much larger population breadth is primarily a production-volume task.

## FAIL

FAIL if population breadth comes from unrelated pipelines, clones dominate, most characters need bespoke repair, group use reveals unresolved systemic failures, or adding the 13th/20th character still requires new foundational tooling.

## Non-goals

No final 100-NPC population, important named cast, facial animation lock, crowd simulation, schedules or narrative depth.

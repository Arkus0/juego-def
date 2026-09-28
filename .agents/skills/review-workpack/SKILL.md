---
name: review-workpack
description: Independently review one frozen juego-def candidate at exact SHA; derive falsifiers before trusting Worker evidence and issue PASS, FAIL or narrow PROTOCOL_FIX.
---

# review-workpack

Review one frozen candidate without editing implementation.

## Preconditions

- exact `PRODUCT_SHA` is identifiable;
- candidate is frozen;
- Reviewer is independent from Worker/Repair Worker;
- required evidence for the claim is available.

## Method

1. Read the exact WP plus directly binding authorities.
2. Build a claim ledger from Acceptance, DoD, Forbidden scope and any batch/repeatability/visual/runtime claims.
3. Before accepting Worker conclusions, derive at least one plausible falsifier for each material claim: how could supplied checks remain green while the claim is false?
4. Inspect complete candidate diff and exact-SHA evidence.
5. Challenge material dimensions relevant to the claim: scale/cardinality, composition, time/order/persistence, duplicate authority, provenance, negative/absence claims, visual quality at real camera/view, repeatability and clean reuse.
6. Run or request a targeted new probe only when it adds information; do not repeat deterministic proof for ceremony.
7. Issue:
   - `PASS` when no material falsifier survives inside scope;
   - `FAIL` for a causal product/evidence defect;
   - `PROTOCOL_FIX` only for non-material metadata while exact product/evidence identity remains trustworthy.

## Verdict quality

State the strongest independently constructed falsifier attempted and why it was closed, or use it as the blocker.

After FAIL, stop. A fresh Repair Worker owns implementation changes.

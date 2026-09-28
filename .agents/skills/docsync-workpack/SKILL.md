---
name: docsync-workpack
description: Reconcile authoritative documentation after an accepted juego-def change, defaulting to zero commits unless durable meaning actually changed.
---

# docsync-workpack

Post-PASS DocSync is a bounded delta, not another review.

## Flow

1. Confirm accepted PR, reviewed `PRODUCT_SHA` and merge state from live GitHub.
2. Ask whether the accepted transition changed the effective meaning of an authoritative document future work consumes.
3. If **no**, create no repository commit. Record/communicate next dependency-valid work and stop.
4. If **yes**, update only the minimum authoritative documents whose effective meaning changed.
5. Run only documentation validators relevant to the files edited.
6. Never rerun product/Unity evidence merely because docs changed.

Do not regenerate chronology, caches or summaries after every merge. Live GitHub and canonical current documents are enough.

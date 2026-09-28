---
name: repair-workpack
description: Repair one juego-def workpack after an independent material FAIL as a fresh Worker, preserving the canonical PR/history and causal scope.
---

# repair-workpack

Repair exactly the failed workpack/candidate.

## Flow

1. Reconstruct the canonical PR, reviewed SHA and latest independent verdict from live GitHub.
2. Classify the finding as material `FAIL` or narrow `PROTOCOL_FIX`.
3. For material FAIL, repair the **causal blocker class**, not merely the literal example reported.
4. Preserve accepted prior guarantees unless the repair contradicts them.
5. Re-run only validation/evidence materially affected by the repair plus the WP-level checks needed to show the whole claim still holds.
6. Finish repository/evidence bytes and select new exact HEAD as `PRODUCT_SHA`.
7. Perform complete strict Worker pre-review on the repaired candidate.
8. Freeze and STOP for a fresh independent Reviewer.

Do not turn a metadata-only correction into another product campaign when repository bytes and exact evidence identity are unchanged.

---
name: plan-workpack
description: Define or refine one juego-def workpack so a fresh Worker can execute it without private chat context; do not implement product code.
---

# plan-workpack

Plan one workpack or a small workpack boundary.

## Method

1. Read current roadmap, direct predecessor contracts and product/design authorities relevant to the proposed claim.
2. Define one concrete outcome and why it is needed now.
3. Split the claim if independent proof would otherwise be ambiguous or unnecessarily broad.
4. Encode explicit dependencies rather than relying on numbering.
5. Define:
   - Objective;
   - Inputs/binding authorities;
   - Allowed scope;
   - Forbidden scope;
   - Deliverables;
   - Acceptance;
   - required evidence/tests;
   - Definition of Done;
   - next work unlocked.
6. For production-factory WPs, require reuse research, repeatable tooling/recipe, validators and batch proof when the claim is mass-production readiness.
7. Do not freeze implementation details that depend on untested external tools or later product decisions; make those disposition points explicit.

A plan is good when another fresh Worker can execute it correctly without this chat.

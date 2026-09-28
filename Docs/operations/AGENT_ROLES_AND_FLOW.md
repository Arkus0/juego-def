# Agent roles and flow

Status: **CANONICAL / LIGHTWEIGHT**

## Purpose

Preserve the useful execution discipline from Juego2 without importing H0/H1, Automation V2 or lifecycle ceremony.

## Roles

| Role | Owns | Must not own |
| --- | --- | --- |
| Owner | product identity, major scope, material purchases, final subjective visual acceptance | routine WP implementation/review ceremony |
| Worker | exact WP interpretation, implementation, evidence, correction, pre-review and freeze | independent PASS of own candidate |
| Unity/Asset Operator | bounded editor/tool execution under Worker brief | product scope, paid adoption, acceptance criteria, independent PASS |
| Reviewer | independent falsification and exact-SHA PASS/FAIL | implementation repair in same role/context |
| Repair Worker | causal repair after FAIL, new evidence/freeze | reviewer independence |

## State flow

```text
PLANNED
 -> ACTIVE WORKER
 -> WORKER PRE-REVIEW CLEAN
 -> FROZEN @ exact PRODUCT_SHA
 -> INDEPENDENT REVIEW
    -> PASS -> MERGE -> bounded DocSync
    -> FAIL -> fresh REPAIR WORKER -> new PRODUCT_SHA -> new Reviewer
```

`PROTOCOL_FIX` is allowed only when exact product/evidence identity is already sound and the issue is non-material metadata.

## Delegated operator boundary

A Worker may hand an editor-heavy slice to an operator when this is faster or requires a specialized surface such as Unity/MCP/Blender. The brief should specify:

- repository/branch/current SHA;
- intended result;
- allowed mutation surfaces;
- mandatory inspect/Play/preview evidence;
- any forbidden dependency or product decisions;
- stop/escalation condition.

The Worker remains responsible for the final diff, interpretation and pre-review.

## Review principle

Reviewer independence is not just a fresh chat. It requires independent attack construction.

Before reading Worker conclusions as sufficient, Reviewer builds a claim ledger from the workpack and asks how the claim could still be false while all supplied checks are green. The strongest relevant surviving falsifier is the blocker; if none survives inside scope, PASS.

## Process budget

Use more rigor when the claim is foundational, irreversible, expensive to replace, or claims a production factory/batch property. Use less ceremony for tiny reversible content changes.

Exact-SHA identity and role independence remain cheap enough to keep almost always.

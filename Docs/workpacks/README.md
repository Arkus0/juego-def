# juego-def executable workpacks

Status: **ACTIVE / v1**  
Authority: `AGENTS.md` + `Docs/roadmap/ROADMAP.md` + `Docs/architecture/PRODUCTION_AUTHORING_DECISION.md`

## Purpose

This directory turns the roadmap into executable product/production contracts. The immediate objective is to build the **graphical/content factories** that let juego-def manufacture repeatedly and cheaply, while CITY provides concrete spatial/product demand.

The separation is deliberate:

- `CITY-URBAN-00` = **what town/block we need** — accepted;
- `CITY-URBAN-00R` = **compact semantic-city amendment** — accepted; then `PROD-ENV-CASCO-V2-00` proves one programme-designed block before ENV scale;
- `PROD-ASSET-00` = **shared lawful production substrate** — accepted;
- `PROD-ANIM-01` = **animation intake/retarget/admission factory** — accepted;
- `PROD-ENV/CHAR` = **remaining graphical factories**;
- `PROD-ENV-DIRECTOR-00` = **owner-facing visual world builder**: direct layout + thumbnail catalogue + simple placement/modification + map expansion, with AI supplying reusable pieces under human direction;
- `PROD-ANIM-02` = **runtime multi-NPC proof**, waiting on accepted CHAR output;
- `CITY-URBAN-01` = **physical keeper realization** of the first block with those factories.

The first concrete customer is [`../design/FIRST_KEEPER_BLOCK_B0.md`](../design/FIRST_KEEPER_BLOCK_B0.md), governed by [`../design/CITY_PRODUCTION_KNOWLEDGE.md`](../design/CITY_PRODUCTION_KNOWLEDGE.md).

## Factory exit principle

A production lane is not finished because it produced a nice sample. It finishes when:

- the real lawful source corpus is discoverable by worker/operator;
- existing public/commercial/native pipeline knowledge has been evaluated before equivalent custom tooling is written;
- intake/adaptation/derivation rules are repeatable;
- routine work is automated or templatized where that materially helps;
- common failures have cheap validators;
- a non-trivial batch has been produced through the same path;
- accepted CITY/B0 demand has usable coverage or explicit gaps;
- creating the next asset is primarily **production**, not new R&D or bespoke plumbing.

The factory may be scripts, Editor tools, Blender recipes, templates, metadata, prompts/briefs and validators. It does **not** need to be a huge custom framework.

## Execution rules

All workpack roles/hand-offs follow root [`../../AGENTS.md`](../../AGENTS.md) and the canonical skills under `.agents/skills/`.

1. **Product first.** Factory work exists to unlock B0 and later city content, not tooling for its own sake.
2. **CITY defines demand; factories define manufacture.** Do not let ENV invent the city or CITY invent asset tooling.
3. **GC2-first.** Use GC2 where it materially reduces gameplay/presentation work; do not duplicate it.
4. **Bounded operator by default.** Unity/MCP/asset operator performs the physical Editor loop where it adds value; Worker retains WP ownership and Reviewer remains independent.
5. **Human look authority.** Owner is final authority on keeper graphical output.
6. **No H0/H1 compatibility tax.** Old materialize/reconcile/gate machinery is not inherited.
7. **Reuse before invention is binding.** Consume [`../research/EXISTING_ASSET_PIPELINE_RESEARCH.md`](../research/EXISTING_ASSET_PIPELINE_RESEARCH.md); existing/adapted solution before equivalent custom tooling.
8. **CITY knowledge is selective.** Consume current port-town topology, B0 demand and reusable game-space principles; do not import the old inland pilot or historical CITY governance.
9. **No fake keeper art.** Proxies are explicit; dressed greybox cannot count as keeper production output.
10. **Source packages are inputs, not workspaces.** Derived output lives in juego-def-owned locations with lineage.
11. **Independent acceptance.** Worker pre-review is required readiness evidence but never substitutes for a fresh Reviewer PASS on the frozen candidate.

## M0

M0 is **not** the gateway to factory R&D. Bootstrap already proves Unity + GC2 player/camera.

M0 is only a small gameplay-integration fixture for player scale, camera, collision/reach and a world/NPC interaction. It runs in parallel and must pass before `CITY-URBAN-01`.

## DAG

```text
CITY-00 PASS + exact ENV01 reference -> CITY-00R -> CASCO-V2-00 pilot
Bootstrap PASS + ASSET-00 PASS + exact ENV01 reference -> pilot
ASSET-00 PASS + CITY-00 PASS -> ENV-01 (closure independent of pilot)
Bootstrap PASS + CITY-00 PASS + active ENV trace/build -> DIRECTOR-00
ENV-01 PASS + DIRECTOR-00 PASS + CITY-00R PASS + pilot PASS -> ENV-02

ASSET-00 PASS -> CHAR-01 -> CHAR-02
ASSET-00 PASS -> ANIM-01 PASS; ANIM-01 + CHAR-01 -> ANIM-02
Bootstrap PASS -> M0; Bootstrap PASS -> DIALOGUE-01 -> UI-01

CITY-00 + CITY-00R + pilot + ENV-02 + M0 + CHAR-02 + ANIM-02 + UI-01
 -> CITY-URBAN-01 (B0 Mercado–Muelle) -> LOOK-GATE -> bounded content scale

pilot -- evidence only --> later Director semantic capability disposition
```

`CITY-URBAN-00`, `CITY-URBAN-00R`, `PROD-ASSET-00` and `PROD-ANIM-01` are accepted. CASCO-V2 is the next physical pilot and is not yet implemented. Director retains its existing gate before ENV02; its D0/D1 and transactional repair can proceed in parallel, without semantic upgrades or a pilot dependency. The pilot uses bounded operator/native authoring and needs a reproducible ENV01 reference, not ENV01/Director PASS. See the [before/after DAG and preserve/reopen ledger](../design/COMPACT_SEMANTIC_CITY_REBASELINE.md). ANIM02 retains CHAR01 as prerequisite.

## Workpacks

| WP | Outcome | Depends on |
| --- | --- | --- |
| `WP-CITY-URBAN-00` ✅ | Five-zone topology + accepted B0 programme/route/elevation + factory-demand matrix | **PASS / accepted** |
| `WP-CITY-URBAN-00R` ✅ | Compact scale + separate cells/buildings/programmes + zero residual space | **PASS / accepted** |
| `WP-PROD-ENV-CASCO-V2-00` | One K2 semantic block pilot; radical utility with retained ENV01 character | CITY00R PASS + bootstrap/ASSET PASS + reproducible exact ENV01 reference |
| `WP-PROD-ASSET-00` ✅ | Shared asset catalogue, research spikes, intake, lineage, discovery and validators | **PASS / accepted** |
| `WP-M0-00` | Small retained GC2 gameplay integration fixture | Bootstrap PASS; parallel |
| `WP-PROD-ENV-01` | Environment asset/assembly factory serving accepted CITY/B0 demand | ASSET-00 + CITY-URBAN-00 |
| `WP-PROD-ENV-DIRECTOR-00` | Owner-facing visual world builder: layout + thumbnail catalogue + game-like placement + map expansion + AI-supplied reusable pieces | Bootstrap + CITY-URBAN-00 + ENV trace/build substrate; urgent parallel enabler |
| `WP-PROD-ENV-02` | Multi-scene batch proof using human-directed production within compact semantic-city rules | ENV01 + ENV-DIRECTOR00 + CITY00R + CASCO-V2 pilot |
| `WP-PROD-CHAR-01` | Civilian/wardrobe production factory serving B0 role priorities | ASSET-00 |
| `WP-PROD-CHAR-02` | Representative civilian batch from factory | CHAR-01 |
| `WP-PROD-ANIM-01` ✅ | Animation intake/retarget/coverage factory serving B0 motion priorities | **PASS / accepted** |
| `WP-PROD-ANIM-02` | Runtime animation vocabulary + batch proof | ANIM-01 ✅ + CHAR-01 |
| `WP-PROD-DIALOGUE-01` | Investigation dialogue authoring/runtime production path | Bootstrap PASS |
| `WP-PROD-UI-01` | Reusable no-voice dialogue/interaction presentation system | DIALOGUE-01 |
| `WP-CITY-URBAN-01` | Realize preserved B0 Mercado–Muelle within amended city grammar | CITY00 + CITY00R + CASCO-V2 pilot + M0 + ENV02 + CHAR02 + ANIM02 + UI01 |
| `WP-PROD-LOOK-GATE` | Prove factories ready for content-scale production | CITY-URBAN-01 |

## Immediate sequence

**Execute the one-block CASCO-V2 pilot before new ENV scale.** CITY-URBAN-00R is accepted; reference reconstruction is the pilot's first material gate. ENV01 closure, CHAR01 and useful Director work remain independent; ANIM01 is complete. This documentation candidate does not authorize Unity implementation or modification of the shared ENV01 checkout.

The first Director milestones remain deliberately small: D0/D1 direct Scene View layout manipulation with safe SAVE / REVERT / REBUILD / PLAY HERE. **Do not restart already-running D0/D1 work.** D2 then makes the tool a real builder with a thumbnail catalogue, semantic pick, ghost placement/snap, native Undo and direct manipulation; D3 adds map expansion; D4 adds the **Coherent Content Forge**: selection-context requests use a project Style Profile and prefer REUSE → RECOMBINE → DERIVE before generating missing content, with Admission Gate before reusable catalogue entry. D2-D5 must reuse proven Unity-editor patterns from inspected prior art rather than reinvent basic picking/placement/line/lasso/thumbnail mechanics, while respecting source licenses. UModeler X may be consumed through an **optional geometry-editor adapter** for advanced selected-object mesh edits, but Director must remain fully functional and commercially separable without it. ENV-02 waits for Director PASS. ANIM-02 must wait for CHAR-01 PASS so the runtime vocabulary is proved on accepted civilians rather than technical placeholder bodies. M0 and Dialogue may continue independently.

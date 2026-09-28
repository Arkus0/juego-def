# Auditoría de reutilización de Arkus0/Juego2

Status: **CURRENT MIGRATION POLICY**  
Updated: 2026-09-28

## Principle

juego-def inherits **knowledge and proven production lessons**, not Juego2's architecture by default.

The source project itself evolved on 2026-09-28 from the old inland/Potes-oriented product to the same large fictional northern-Spain port-town direction now retained here. Therefore the useful current visual/urban knowledge is migrated; obsolete inland authority and H0/H1 infrastructure are not.

See the detailed snapshot in [`JUEGO2_KNOWLEDGE_BASELINE.md`](JUEGO2_KNOWLEDGE_BASELINE.md).

| Class | Concept | Decision for juego-def |
|---|---|---|
| `REUSE_DIRECTLY` | Git/Unity hygiene: preserve scenes, `ProjectSettings`, `.meta`; ignore generated outputs; pin real versions | Apply when the new Unity project exists. |
| `REUSE_DIRECTLY` | Buy/adopt only for a demonstrated production or gameplay need | Foundation economic rule. |
| `REUSE_DIRECTLY` | GC2-first ownership | Core/modules own ordinary gameplay unless a real gap is shown. |
| `REUSE_AS_PRODUCT` | Current large port-town scale, five-zone model, nightlife distribution, unnamed town | Migrated into `PORT_TOWN_WORLD_MODEL.md`. |
| `REUSE_AS_PRODUCT` | 20–30 minute investigation/daily-life/adventure slice target | Migrated into current vision/world model. |
| `REUSE_AS_ART` | Current Visual Bible and reuse-first selection semantics | Migrated and made local in `Docs/design/VISUAL_BIBLE.md`. |
| `REUSE_AS_ART` | Avoid dressed greybox; require credible facade/threshold/ground/roof joins and third-person composition | Binding production quality principle. |
| `REUSE_AS_PRODUCTION` | Quaternius as editable source ecosystem; `DIRECT / ADAPTABLE / DONOR / CREATE_DERIVED` | Migrated into `Docs/production/QUATERNIUS_PRODUCTION_KNOWLEDGE.md`. |
| `REUSE_AS_PRODUCTION` | Existing Quaternius tooling/pipeline research before inventing new tools | Mandatory precheck for future ENV/CHAR/ANIM work. |
| `REUSE_AS_PRODUCTION` | GC2 Hub audit and `native -> Hub -> adapt -> custom` sequence | Migrated into `Docs/production/GC2_HUB_REUSE_KNOWLEDGE.md`. |
| `REUSE_AS_PRODUCTION` | ENV / CHAR / ANIM / UI production-lane decomposition and repeated-build proof | Migrated as drafts in `Docs/roadmap/POST_FOUNDATION_PRODUCTION_WPS.md`. |
| `ADOPTED` | AI Unity/MCP production operator | `BOUNDED_OPERATOR` (MCP for Unity), owner-confirmed 2026-09-28 after comparison with H0/H1 evidence; see `PRODUCTION_AUTHORING_DECISION.md`. Unity AI Assistant rejected. |
| `REEVALUATE_LATER` | Small Arkus/H0 component for durable cross-system facts | Only after a concrete GC2/local failure with a minimal proposed seam. |
| `REEVALUATE_LATER` | Useful scripts/shaders/helpers produced in Juego2 | Port only after current need, license/ownership, compatibility and simplicity review. |
| `DO_NOT_PORT` | H1 bridge, canonical->Unity materialize/observe/reconcile/rematerialize lifecycle | Another architecture; no default role here. |
| `DO_NOT_PORT` | H0 harness/CAS/replay/snapshot as project foundation | No default role here; a specific tiny component can be proposed later only on evidence. |
| `DO_NOT_PORT` | Old Potes/Liébana geography and inland pilot as final-setting authority | Historical experiment only. |
| `DO_NOT_PORT` | Old CITY exact node/edge matrices, H2F/H2 gate DAG, freezes and governance bureaucracy | Preserve lessons, not execution machinery. |
| `DO_NOT_PORT` | Deep simulation of every NPC before gameplay proves value | Layer NPC depth and scale incrementally. |

## Critical clarification about MCP

The original foundation draft grouped `MCP` with H0/H1 under `DO_NOT_PORT`. That is superseded.

- **Arkus/H1 MCP infrastructure** is not inherited.
- A **direct Unity production operator** is a separate product-authoring hypothesis and is actively pending benchmark evidence.

If that benchmark is excellent, juego-def may intentionally adopt the winning operator without importing H1.

## Source-of-truth rule

Juego2 remains a research/archive source. Once knowledge is distilled into juego-def, local documents govern this repository. Later changes in Juego2 do not silently mutate juego-def.

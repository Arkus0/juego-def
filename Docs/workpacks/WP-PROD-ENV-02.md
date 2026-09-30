# WP-PROD-ENV-02 — Environment Batch Production Proof

Status: **READY AFTER ENV-01 + ENV-DIRECTOR-00**  
Class: PRODUCTION SCALE PROOF / ENVIRONMENT  
Depends on: `WP-PROD-ENV-01` PASS + `WP-PROD-ENV-DIRECTOR-00` PASS  
Blocks: `WP-CITY-URBAN-01`; authoring-path revisit

## Claim

The ENV factory + ENV Director can now support **human-built environment production at scale**: the owner can edit existing space, expand the playable map and consume AI-made/adapted pieces through the same visual catalogue and rebuild/validation path, without falling back to prompt-by-prompt coordinate manipulation or Unity prefab/path archaeology.

## Required outputs

Produce **three materially different keeper proofs**, each exercising a distinct Director use case:

1. **EDIT EXISTING** — materially improve an existing bounded composition through direct manipulation, including (where present) a visible misplaced prop corrected by click+drag and a modular railing/wall/edge corrected by endpoint extension rather than segment-by-segment editing.
2. **EXPAND MAP** — extend a real boundary into new connected playable space using Director layout + catalogue placement.
3. **COHERENT CONTENT FORGE / AI-MODIFIED CONTENT** — use AI MODIFY SELECTED on an existing object/chain/area with automatic scene context and explicit preview/acceptance, then satisfy at least one missing-content request through the Director's coherent planner. The proof must evaluate REUSE → RECOMBINE → DERIVE → GENERATE in that order, use the active Project Style Profile, admit at least one new/materially-derived reusable result through the Admission Gate, expose it in the visual catalogue, reuse/place it and retain it.

The proofs may contribute to the same larger district if their boundaries/evidence remain independently reviewable. They must reuse the accepted ENV catalogue/modules/adaptation path/assembly grammar/validators rather than creating three bespoke pipelines.

## Required production loop

For each composition:

`brief -> owner shapes/extends layout in ENV Director -> owner places existing catalogue pieces -> lock important decisions -> owner may select object/chain/area + natural-language request -> Director packages bounded structural/visual context + Style Profile -> coherent planner tries REUSE / RECOMBINE / DERIVE before GENERATE -> explicit proposal preview/acceptance -> candidate passes Admission Gate -> admitted reusable content enters catalogue -> owner places/modifies -> rebuild -> Play Mode -> automated route/collision/affected QA -> owner correction in ENV Director -> gameplay captures -> owner review`

At least one proof must begin from a fresh brief and prove the complete builder loop without exact object/path/coordinate instructions from the owner. Spatial intent is expressed through Director manipulation/selection; AI receives bounded manufacturing/adaptation requests rather than authority to compose the district.

## Batch economics evidence

Record per composition:

- owner manual interactions in the Director and any rescue outside it;
- whether normal placement required Project-browser/prefab-path archaeology;
- exact path/coordinate hints given to agents;
- one-off scripts introduced;
- time/effort class qualitatively (`LOW`, `MEDIUM`, `HIGH`);
- major failures and whether the factory already had the mechanism to solve them;
- new asset classes that forced factory extension.

The third composition should not require rebuilding the pipeline.

## Human-direction proof

Across the three proofs, preserve a clear authority split:

- owner directly establishes/changes layout, placement and expansion decisions through `ENV Director`;
- existing content is chosen/placed through the visual catalogue;
- AI/operator modifies/generates content only inside declared human intent and selection scope;
- at least one selected-scene AI request derives local geometry/semantics/locks/views automatically rather than requiring owner-supplied coordinates/paths;
- material selected-scene AI output is previewed before canonical acceptance;
- AI-made reusable output returns to the catalogue rather than remaining a one-off hidden scene edit;
- missing-content requests prefer reuse/recombination/derivation over unconstrained new generation;
- admitted content is checked against an inspectable project-owned Style Profile and accepted by the owner before normal catalogue admission;
- factory/procedural systems perform repeatable mechanical work;
- owner can correct the result directly without reverting to JSON, Inspector-coordinate editing or prompt-by-prompt spatial translation.

The proofs must include at least one meaningful owner correction after AI/factory work and show that direct placement, map expansion and AI-supplied content all survive rebuild.

## Coherent-content proof

ENV-02 must prove that D4 grows a coherent reusable vocabulary rather than producing isolated AI assets.

Retain:

- the Project Style Profile used by the proof and where its rules/families came from;
- one request where suitable existing catalogue/family candidates are considered before generation;
- the planner disposition for `REUSE`, `RECOMBINE`, `DERIVE` and `GENERATE MISSING CONTENT`;
- at least one retained result produced by `RECOMBINE` or `DERIVE`;
- one candidate that passes the Admission Gate and becomes an admitted catalogue item;
- evidence that the admitted item is subsequently reused or placed again;
- owner visual verdict that the result belongs to the same project language as accepted neighbouring content;
- candidate lineage, semantic family and thumbnail;
- where a candidate is rejected or revised, retain the reason if useful.

Free-form generation of a complete building from scratch is **not** required. A proof that sensibly avoids generation because existing/derived vocabulary solves the request is stronger than gratuitous generation.

## Prior-art implementation proof

ENV-02 must prove that the Director's builder UX is built on reusable editor primitives rather than one-off scene hacks.

Retain evidence that:

- clicking a visible child renderer/collider resolves the correct semantic authored object;
- placement/movement uses a cancellable non-authoritative ghost/preview;
- catalogue thumbnails are generated without polluting the production scene;
- Undo/Revert operates across at least one placement/move and one chain edit;
- railing/wall extension edits the semantic chain and rematerializes modules rather than requiring manual segment management;
- area/lasso selection can bound at least one fill, validation or AI request;
- AI-created accepted multi-object content can become a reusable catalogue/assembly unit with lineage;
- no unlicensed/reference-only prior-art code was imported into production;
- optional third-party geometry integrations, if used, remain separable from Director core and do not become canonical ENV authority;
- juego-def project authority and AI-provider integrations remain behind explicit adapters rather than leaking through Director Core.

The evidence should identify any third-party MIT code actually reused and retain required notices.

## Portability + provider-neutrality proof

ENV-02 must retain a small architecture proof that Director is a reusable product layer rather than a juego-def-only editor.

The proof does **not** require packaging or publishing a separate Unity asset. It must show:

- Director Core code does not directly depend on CASCO IDs, juego-def repository paths or concrete trace/spec/polish types for normal selection/catalogue/preview/AI-context behavior;
- juego-def persistence, rebuild, lineage and validators are reached through a project/authoring adapter boundary;
- the AI request/proposal contract exists in a provider-neutral form before translation to the active provider/operator;
- disabling the configured AI provider leaves normal Director selection, placement, chains, map expansion, save/rebuild and validation functional;
- provider failure or malformed output leaves canonical ENV authority unchanged;
- adding a hypothetical second provider is structurally an adapter task rather than a rewrite of Director Core.

A second live AI provider is **not** required for PASS. The proof is architectural separability, not provider-count theatre.

## Optional geometry-tool proof

UModeler X is **not** a dependency of ENV-02 and its absence cannot cause FAIL.

If the Director UModeler X adapter is enabled during the proof, retain one bounded geometry-edit example showing:

- a semantic object is selected through Director rather than by raw mesh archaeology;
- UModeler X edits only a juego-def-owned derived copy / admitted target;
- the edit returns through Director/ENV with semantic identity, lineage and rebuild-safe reference intact;
- disabling the optional adapter does not break catalogue placement, direct manipulation, semantic chains, map expansion or AI modular/assembly workflows;
- no UModeler X package code/binaries are copied into juego-def-owned commercializable Director code.

A geometry-edit proof is useful evidence of extensibility, not a PASS requirement.

## Automated walkability proof

Each route must run the accepted automated traversal/collision probe plus one human walk-through. Detect/report obvious snags, threshold failures, prop blockage, invalid spawn/approach or geometry escapes.

## Visual acceptance

Owner must accept all three as:

- clearly beyond dressed greybox;
- belonging to the same game while having distinct local identity;
- intentionally composed at third-person scale;
- good enough to keep and improve, not discard as pipeline tests.

## PASS

PASS when:

- EDIT EXISTING, EXPAND MAP and AI-SUPPLIED CONTENT keeper proofs all exist;
- all were produced through the ENV factory + ENV Director path rather than bespoke scene-specific pipelines;
- catalogue placement works without routine prefab/path archaeology;
- direct Scene View correction of an existing visible prop is proven without hierarchy/path lookup;
- at least one supported modular linear structure is extended/shortened by endpoint manipulation with persistent rebuild-safe output;
- AI MODIFY SELECTED is proven with automatic bounded context + explicit PREVIEW/ACCEPT or DISCARD;
- coherent-content planning is proven, including REUSE → RECOMBINE → DERIVE → GENERATE ordering;
- at least one recombined/derived reusable result passes the Admission Gate and enters the same catalogue/placement path;
- the complete human-build -> AI-supply -> rebuild/validate -> human-correct loop is proven;
- semantic pick, ghost preview, native Undo, isolated thumbnails, semantic chain editing and bounded area selection are proven on real content;
- Director Core/project-adapter separation and provider-neutral AI request/proposal boundaries are evidenced without requiring a second live provider;
- route/collision validation passes or documented defects are repaired;
- later builds show materially lower rediscovery/setup friction than the first;
- owner accepts the environment quality/direction;
- remaining environment work is mostly breadth, new art needs and polish.

## Authoring-path decision

End with one recommendation:

- `UPGRADE_PRIMARY_AUTHORING_PATH` — operator + factory clearly supports routine environment production;
- `KEEP_BOUNDED_OPERATOR` — valuable but named manual/specialized steps remain;
- `DOWNGRADE_TOOL_SOURCE_ONLY` — operator still causes excessive rescue or rejected composition.

## FAIL

FAIL if any of the three required use cases is missing, factory/Director mechanisms are bypassed, ordinary placement still requires prefab/path archaeology, map expansion still requires prompt/coordinate translation, selected-scene AI still requires coordinate/path transcription, AI preview silently mutates canonical state, the coherent planner jumps to unconstrained generation while suitable admitted vocabulary exists, Style Profile is opaque/non-project-owned, generated/derived candidates bypass Admission Gate or owner acceptance, admitted pieces cannot re-enter/reuse the catalogue, AI actions overwrite locked/unselected human decisions, or each new area still triggers foundational pipeline invention.

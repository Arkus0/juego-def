# WP-PROD-ANIM-02 — Runtime Animation Vocabulary + Batch Proof

Status: **BLOCKED ON CHAR-01 / ANIM-01 ACCEPTED**  
Class: PRODUCTION SCALE PROOF / RUNTIME ANIMATION  
Depends on: `WP-PROD-ANIM-01` PASS + `WP-PROD-CHAR-01` PASS  
Blocks: `WP-CITY-URBAN-01`

ANIM-01 is accepted via PR #9. This WP must not begin its multi-NPC runtime proof until CHAR-01 provides the accepted civilian family.

## Claim

The animation factory is not only an intake catalogue: admitted motions can be applied at runtime across many civilian prefabs through a small reusable vocabulary, without per-NPC Animator surgery.

## Required runtime vocabulary

Provide reusable mappings for at least:

- locomotion baseline inherited from GC2 character setup;
- neutral idle/ambient variation;
- conversation `talk/listen/gesture` presentation;
- one reaction family;
- one work/object/activity family where admitted coverage exists.

## Batch proof

Use the accepted CHAR-01 civilian factory output and ANIM-01 admissions to prove the same runtime path on multiple materially different civilians. Do not hand-author a bespoke Animator Controller per NPC.

At minimum demonstrate:

1. several civilians can share the runtime vocabulary;
2. admitted motions resolve by semantic role rather than scene-specific clip wiring;
3. body/wardrobe incompatibility is surfaced rather than silently ignored;
4. locomotion/facing ownership is explicit;
5. contact-dependent motions remain bounded unless a real object/placement contract is supplied.

## Validation

Retain cheap checks for missing semantic mappings, missing clips, incompatible body admission, duplicate/ambiguous vocabulary keys and obvious runtime setup errors.

## Evidence

Retain under `Docs/evidence/WP-PROD-ANIM-02/`:

- runtime vocabulary/mapping definition;
- representative multi-NPC runtime captures/observations;
- batch inventory of civilians × motions actually exercised;
- incompatible/failure case;
- any bounded contact-placement convention introduced;
- Worker pre-review.

## PASS

PASS when the accepted animation factory can feed multiple accepted civilian prefabs through one reusable runtime vocabulary and adding another normal NPC does not require bespoke Animator surgery.

## FAIL

FAIL if ANIM-02 rebuilds the intake factory, silently broadens ANIM-01 admissions, hand-wires every NPC separately, assumes final civilian compatibility without CHAR evidence, or expands into a universal cinematic/combat system.

## Handoff

`WP-CITY-URBAN-01` consumes the proven runtime vocabulary while composing the first retained B0 block.

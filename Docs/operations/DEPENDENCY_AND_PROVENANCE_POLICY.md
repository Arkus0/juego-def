# Dependency and provenance policy

Status: **CANONICAL / LIGHTWEIGHT**

## Principle

Reuse aggressively when it saves material time or improves quality, but do not let an external package/tool become an accidental hidden authority or legal/provisioning trap.

## Before adoption

For any material third-party package, source tool, plugin or asset dependency that enters production rather than research:

- identify exact product/repository and exact version/commit where applicable;
- record license/ownership/provisioning status from an authoritative source;
- state what problem it solves better than the current GC2/native/local path;
- state replacement/removal boundary;
- run the smallest representative fixture proving the intended use;
- record known limitations and whether source modification is expected.

Research references and old Juego2 license observations are not current adoption approval.

## Cost rule

Do not purchase a package/module merely because a roadmap names it. Paid adoption requires a concrete feature/factory bottleneck and a material expected time/quality gain. Owner approval is required for a material new purchase.

## Provenance for assets and derived work

Maintain enough lineage to answer:

```text
what source did this come from?
what exact source/version/pack?
what transformation/adaptation was applied?
what license/ownership governs the source?
what output/prefab/asset does it produce?
```

Transforming an external source does not erase its provenance.

Use current production classifications where useful:

- `DIRECT`
- `ADAPTABLE`
- `DONOR_COMPONENTS`
- `CREATE_DERIVED`
- `REJECT/BLOCKED_EXTERNAL`

## Plugin/runtime ownership

GC2 and plugins may own execution where they are the chosen implementation. Avoid letting plugin-private IDs, save slots or opaque state become the only durable meaning for gameplay facts that must survive replacement or be understood across systems.

Do **not** create a duplicate custom authority merely as insurance. Add a local durable semantic layer only when a concrete product requirement proves it necessary.

## Vendor/source modification

Prefer adapters, templates/configuration and isolated source changes over scattered edits through vendor code. If modifying vendor/source packages is necessary, keep the delta discoverable and reproducible.

## Secrets and credentials

Never commit account passwords, access tokens, Unity credentials, asset-store credentials, 2FA codes or private keys. Authentication remains in the user's/tool's normal secure account store.

## Revalidation triggers

Recheck dependency facts when:

- adopting a previously research-only candidate;
- upgrading Unity/GC2/package major version;
- source/license materially changes;
- a dependency becomes unmaintained or incompatible;
- production starts depending on a feature that was not in the original representative fixture.

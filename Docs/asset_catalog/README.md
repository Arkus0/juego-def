# Asset substrate — operator entry point

This is the shared intake for `WP-PROD-ASSET-00`. The canonical workpack and B0 demand live in GitHub `main`; `catalog.json` is a reproducible snapshot of the owner's `C:/Juego2-Assets` vault, not a copy of asset bytes. Every entry is a **candidate**, even when its provisional reuse class is `DIRECT`. ENV/CHAR/ANIM still decide visual fit, scale and final admission on real output.

## Commands

From the repository root (Python 3.10+; standard library only):

```powershell
python Tools/asset_catalog.py build
python Tools/asset_catalog.py search --role commercial_frontage --query door --limit 10
python Tools/asset_catalog.py search --role upper_port_loop --query stair
python Tools/asset_catalog.py search --role civilian_wardrobe --tag dock
python Tools/asset_catalog.py search --role conversation_reaction --query talk
python Tools/asset_catalog.py search --role market_port_props
python Tools/asset_catalog.py validate
python Tools/asset_catalog.py install --pack medieval
python Tools/test_asset_intake_identity.py
```

Use `--vault <directory>` on another machine. The search reads the committed snapshot, so it does not need the vault mounted. Each hit gives a stable ID, B0 role, provisional reuse class and future Unity path. The JSON entry also has the source path relative to the vault, content digest, pack/license pointer, native Unity GUID where present and a pack preview image path where available. Search or inspect JSON first; then preview the pack image or the shortlisted source model in Unity. UAL entries are individual FBX animation stacks discovered from the source file, with clip names and tags; they do not have visual previews yet.

## Intake

- `build` records an `intakeIdentity` for every covered pack. For non-Medieval packs it hashes the ordered `(relative path, SHA-256)` manifest of **every file that install may copy**, including textures that are intentionally not standalone semantic catalogue candidates. Medieval uses the pinned source archive SHA-256, which content-addresses the whole extracted subtree.
- `install` refuses to ingest a pack if the current vault identity differs from the committed catalogue. This makes additions, removals and same-path byte changes explicit reviewable snapshot changes instead of silently changing a clean clone. The matching identity is written into `.juego-def-intake.json`.
- `install --pack medieval` extracts only the Medieval Village source-project subtree into ignored `Assets/ThirdParty/Quaternius/MedievalVillage/`, preserving its vendor `.meta` GUIDs, ready prefabs, collision models and materials. The exact source archive SHA-256 is pinned in the tool. Unity 6 locally resaves the 14 vendor `.mat` files on first import; a repeat intake preserves and reports those local upgrades while refusing other changed vendor files.
- `install --pack props|nature|base|outfits|ual1|ual2` copies the Unity FBX and texture representations into pack-specific ignored folders. It generates stable GUIDs for those source files because their vault exports have no Unity `.meta` files. Re-running intake on the same admitted identity is idempotent; a changed source identity requires `build` first.
- Install only the packs needed by the current worker. `python Tools/asset_catalog.py validate` checks snapshot freshness, pack intake identities, receipts, source identity, licenses, installed paths/GUIDs, every copied non-Medieval source byte (including textures), unique IDs and derived lineage. It does not pretend to prove Unity visual import quality.
- For UAL, the pinned [QuaterniusUnityUtils importer](https://github.com/firstkindgamer/QuaterniusUnityUtils) is included under `Assets/Plugins/QuaterniusUnityUtils/Editor/` with its Unlicense. Run `Tools/JuegoDef/Apply UAL Imports` in Unity, or batch `-executeMethod JDAssetIntakeApplyUAL.Run`, after installing UAL1/2. The small wrapper calls the existing utility and verifies Humanoid import; ANIM-01 must still validate retargeting and individual clips.
- The Medieval Village source project already includes collision prefabs. Its native prefabs are the first intake choice. The utility's collision maker works in Unity 6000.3.24f1 but writes to `Assets/Prefabs` and is only useful for models without an acceptable vendor prefab; move any retained derivative to the owned destination and record lineage.

The regression probe `python Tools/test_asset_intake_identity.py` uses a synthetic Props vault and proves three things without requiring the owner's vault: unchanged input has a stable identity, changing a copied texture at the same path changes the identity, and adding another copied texture changes both identity and file count.

## Owned derivatives

Place retained derived Unity assets under `Assets/JuegoDef/Derived/<ENV|CHAR|ANIM|PROP>/<stable-name>/`. Never edit ignored vendor source in place. Add a record to `Docs/asset_catalog/lineage.json` with `id`, `path` (Unity project relative, e.g. `Assets/JuegoDef/Derived/ENV/market-shopfront.prefab`), `sourceIds` (catalog IDs), `method`, and `notes`. Rebuild the catalogue after editing lineage to populate each source's `derivedIds`. The validator refuses an unrecorded derived file or a record whose source is absent.

Unity `Assets/ThirdParty/Quaternius/` is local intake state and is excluded from the public repository. This keeps source bytes and the generated snapshot separate while giving scene/prefab references deterministic GUIDs on another installation. The provisioning script records a content-addressed receipt inside each ignored pack folder.

## Scope and gaps

### Animation admission layer

`Docs/asset_catalog/animations.json` is the ANIM-01 semantic/admission layer over the unchanged source candidates. Use `python Tools/anim_catalog.py search --status ADMIT --family conversation_acting` or `--query muelle` for motion discovery. `ADMIT` is bounded to the measured body family and recorded constraints; contact-dependent or unreviewed clips remain `ADAPT`, and missing capabilities are explicit `GAP` entries. See [ANIM_FACTORY.md](../production/ANIM_FACTORY.md) for intake, native Unity presets, batch Play Mode retarget checks, preview and the next-clip workflow.

The catalogue intentionally indexes Unity prefabs and FBX exports as semantic candidates, not duplicate OBJ/glTF forms, all textures as standalone candidates, or irrelevant source-project editor files. **Not being a semantic candidate does not exclude a copied file from provenance:** all installed source bytes are covered by the pack intake identity. New assets from a covered family enter by re-running `build`; new families need a source/license row and a bounded semantic rule. See the WP evidence for B0 coverage and current missing waterfront, urban shopfront and civilian/work motion roles.

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
```

Use `--vault <directory>` on another machine. The search reads the committed snapshot, so it does not need the vault mounted. Each hit gives a stable ID, B0 role, provisional reuse class and future Unity path. The JSON entry also has the source path relative to the vault, content digest, pack/license pointer, native Unity GUID where present and a pack preview image path where available. Search or inspect JSON first; then preview the pack image or the shortlisted source model in Unity. UAL entries are individual FBX animation stacks discovered from the source file, with clip names and tags; they do not have visual previews yet.

## Intake

- `install --pack medieval` extracts only the Medieval Village source-project subtree into ignored `Assets/ThirdParty/Quaternius/MedievalVillage/`, preserving its vendor `.meta` GUIDs, ready prefabs, collision models and materials. The exact source archive SHA-256 is pinned in the tool. Unity 6 locally resaves the 14 vendor `.mat` files on first import; a repeat intake preserves and reports those local upgrades while refusing other changed vendor files.
- `install --pack props|nature|base|outfits|ual1|ual2` copies the Unity FBX and texture representations into pack-specific ignored folders. It generates stable GUIDs for those source files because their vault exports have no Unity `.meta` files. Re-running intake adds newly discovered source files and checks existing bytes; it refuses changed vendor files instead of overwriting them.
- Install only the packs needed by the current worker. `python Tools/asset_catalog.py validate` checks source identity, licenses, installed paths, unique IDs and derived lineage. It does not pretend to prove Unity visual import quality.
- For UAL, the pinned [QuaterniusUnityUtils importer](https://github.com/firstkindgamer/QuaterniusUnityUtils) is included under `Assets/Plugins/QuaterniusUnityUtils/Editor/` with its Unlicense. Run `Tools/JuegoDef/Apply UAL Imports` in Unity, or batch `-executeMethod JDAssetIntakeApplyUAL.Run`, after installing UAL1/2. The small wrapper calls the existing utility and verifies Humanoid import; ANIM-01 must still validate retargeting and individual clips.
- The Medieval Village source project already includes collision prefabs. Its native prefabs are the first intake choice. The utility's collision maker works in Unity 6000.3.24f1 but writes to `Assets/Prefabs` and is only useful for models without an acceptable vendor prefab; move any retained derivative to the owned destination and record lineage.

## Owned derivatives

Place retained derived Unity assets under `Assets/JuegoDef/Derived/<ENV|CHAR|ANIM|PROP>/<stable-name>/`. Never edit ignored vendor source in place. Add a record to `Docs/asset_catalog/lineage.json` with `id`, `path` (Unity project relative, e.g. `Assets/JuegoDef/Derived/ENV/market-shopfront.prefab`), `sourceIds` (catalog IDs), `method`, and `notes`. Rebuild the catalogue after editing lineage to populate each source's `derivedIds`. The validator refuses an unrecorded derived file or a record whose source is absent. Re-running `install` on an unchanged pack is idempotent (verified with Props: 111 files, 0 new).

Unity `Assets/ThirdParty/Quaternius/` is local intake state and is excluded from the public repository. This keeps source bytes and the generated snapshot separate while giving scene/prefab references deterministic GUIDs on another installation. The provisioning script records a receipt inside each ignored pack folder.

## Scope and gaps

The catalogue intentionally indexes Unity prefabs and FBX exports, not duplicate OBJ/glTF forms, all textures as standalone candidates, or irrelevant source-project editor files. New assets from a covered family enter by re-running `build`; new families need a source/license row and a bounded semantic rule. See the WP evidence for B0 coverage and current missing waterfront, urban shopfront and civilian/work motion roles.

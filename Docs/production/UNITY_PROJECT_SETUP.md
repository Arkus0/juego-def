# Unity project setup

Status: **BOOTSTRAPPED 2026-09-28** — evidence in [`../evidence/BOOTSTRAP-UNITY-GC2/README.md`](../evidence/BOOTSTRAP-UNITY-GC2/README.md).

## Pinned toolchain

| Item | Value | Notes |
|---|---|---|
| Unity | **6000.3.24f1** (revision `4e7b9b5b6244`) | same generation Juego2 validated; `ProjectSettings/ProjectVersion.txt` pins it |
| Project path | `Unity/JuegoDef` | repo root keeps `Docs/` and `Tools/` separate from the Unity project |
| Render pipeline | URP **17.3.0** | `Assets/JuegoDef/Rendering/JD_URP.asset` + `JD_Renderer.asset` (Forward, SSAO feature) |
| Game Creator 2 | Core **2.19.61** only | owner-licensed, never committed (see below) |
| Input | Input System **1.20.0**, *Active Input Handling = Input System Package* | GC2 Core uses only the Input System (no legacy `Input.*` calls) |
| Editor operator | MCP for Unity `com.coplaydev.unity-mcp` **v10.2.0** (git tag) | editor-only; see [`../architecture/PRODUCTION_AUTHORING_DECISION.md`](../architecture/PRODUCTION_AUTHORING_DECISION.md) |

Direct packages are pinned in `Packages/manifest.json`; the full resolution is committed in `packages-lock.json`. The GC2 vendor `Packages/manifest.json` inside the `.unitypackage` is the vendor's own project manifest and is **never applied**.

## Opening the project from a clean clone

1. Install Unity 6000.3.24f1 through Unity Hub.
2. Restore GC2 Core **before** opening the project (scenes reference GC2 scripts by GUID; without Core they show missing scripts and the project does not compile its GC2 content):
   ```
   python Tools/gc2-provision.py install
   ```
   It reads the owner's Asset Store download from `%APPDATA%/Unity/Asset Store-5.x/Catsoft Works/Editor ExtensionsGame Toolkits/Game Creator 2.unitypackage`, refuses anything that is not the admitted Core 2.19.61 (SHA-256 `1e4f3ba0…2f3380b`, 28,236,878 bytes), extracts `Assets/**` only into `Assets/Plugins/GameCreator/` and writes a receipt. `status` and `remove` are also available.
3. Open `Unity/JuegoDef` in Unity Hub. Packages resolve from the committed manifest/lock.
4. Open `Assets/JuegoDef/Scenes/Bootstrap_GC2Core.unity` and press Play: WASD moves the Player, the mouse orbits the GC2 third-person camera.

**Never commit GC2 bytes.** The repository is public and the Asset Store EULA is per seat and not redistributable. `.gitignore` covers `Assets/Plugins/GameCreator/`, its `.meta` and `Assets/Plugins.meta`. GC2 also generates its settings under that folder on first windowed open; they are regenerated and stay ignored.

## Project conventions

- Game content lives under `Assets/JuegoDef/` (`Scenes/`, `Materials/`, `Rendering/`, …). Third-party code stays in `Assets/Plugins/`.
- Commit scenes, prefabs, materials, `ProjectSettings/`, `Packages/manifest.json`, `packages-lock.json` and every `.meta`. `Library/`, `Temp/`, `Logs/`, `UserSettings/`, IDE files and operator `Captures/` are ignored.
- Colour space **Linear**; lights use linear intensity + colour temperature.
- URP pipeline: HDR on, MSAA 4x, depth texture on, opaque texture off, soft main-light shadows (70 m, 2 cascades), SSAO, legacy light probes (APV off). These are the Juego2-validated baseline values, not final look decisions.
- `PlayerSettings.runInBackground = true`. Besides being sensible for a windowed PC game, it is **required for operator Play Mode checks**: with it off, the Editor freezes the player loop whenever Unity is not the focused window (see evidence).
- Build Settings contain only `Bootstrap_GC2Core` until M0 adds the first street.

## Working with the MCP operator

- Several Unity Editors may be connected to the same MCP server (e.g. Juego2 benchmark worktrees). **Always select the instance first** (`set_active_instance JuegoDef@<hash>`) and never act on another project's instance.
- Screenshot `output_folder` must be inside the project: use `Captures/` (ignored) and copy curated images to `Docs/evidence/`.
- `execute_code` compiles with CodeDom (C# 6) by default: fully qualify `UnityEngine.Object`, `UnityEditor.SceneManagement.EditorSceneManager`, etc.
- GC2 `[SerializeReference]` fields (shot types, instructions, conditions, property getters) cannot be set with the generic component tools; use `execute_code` with `SerializedObject.managedReferenceValue` or GC2's public API.
- Package installs/removals trigger a domain reload; tool calls made meanwhile time out. Wait for the Editor status to report `ready`.
- MCP for Unity rewrites the MCP client configs it knows about on Editor start-up (`[StartupConfigRewrite]`). Expected behaviour of the package, but be aware it touches global client configuration.

## Optional packages currently installed by the owner

`com.unity.ai.assistant` 2.20.0-pre.1 and `com.unity.ai.inference` 2.6.1 were added to try Unity's own AI tools. Without a Unity AI subscription the Assistant logs `NoSubscription` errors from `generators.ai.unity.com` on every Play Mode entry, which is noise for console-based validation. Keep or remove them deliberately; they are not required by juego-def.

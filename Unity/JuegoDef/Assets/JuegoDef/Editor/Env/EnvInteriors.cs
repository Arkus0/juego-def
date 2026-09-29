using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace JuegoDef.Env
{
    /// <summary>
    /// Fake interiors (owner 2026-09-29: "usa los fake interiors"): builds a few small furnished rooms from the kit
    /// (Quaternius Props furniture, Medieval Village floors, owned plaster), lights them, captures each from its centre
    /// into a compressed cubemap and makes one JuegoDef/ENV/Interior Room material per room
    /// (Derived/ENV/Interiors). The district builder puts a card with one of these materials behind every window;
    /// the shader traces the view into the virtual room, so windows show depth and parallax, dim by day and lit in a
    /// share of homes, shops and bars at dusk and night. Menu: JuegoDef &gt; ENV &gt; 8 Build Interior Rooms.
    /// Room frame: floor y = 0, x across the window wall, the window wall at z = 0 and the room behind it (z &lt; 0).
    /// </summary>
    public static class EnvInteriors
    {
        public const string Folder = EnvKit.Derived + "/Interiors";
        public const int CubeSize = 256;

        public class Room
        {
            public string id;
            public Vector3 size;            // W, H, D
            public string walls, floor, dado;
            public Color light;
            public float lightIntensity = 2.2f;
            public bool shop;               // shopfront glazing (ground floor, no sill)
            public float litBias;           // bars stay lit at dusk and night
            public List<(string module, Vector3 at, float rot, float scale, string snap)> items = new List<(string, Vector3, float, float, string)>();
            public Room Add(string module, float x, float z, float rot = 0, float scale = 1, string snap = null, float y = 0)
            {
                items.Add((module, new Vector3(x, y, z), rot, scale, snap));
                return this;
            }
        }

        /// <summary>Homes are picked at random per window; shops and bars by the building's use.</summary>
        public static readonly Room[] Rooms =
        {
            new Room { id = "Sala", size = new Vector3(3.8f, 2.7f, 4.2f), walls = "ENV_Plaster_Cream", floor = "Floor_WoodDark", light = new Color(1f, 0.78f, 0.52f) }
                .Add("Bookcase_2", -0.7f, -4.2f, 0, 1, "back").Add("Cabinet", -1.9f, -2.6f, 90, 1, "left")
                .Add("Table_Large", 0.2f, -2.3f, 90, 0.8f).Add("Chair_1", -0.55f, -2.3f, 90).Add("Chair_1", 0.95f, -2.3f, -90)
                .Add("CandleStick_Triple", 0.2f, -2.3f, 0, 1, "on").Add("Book_Stack_1", 1.4f, -4.2f, 0, 1, "back")
                .Add("BookGroup_Medium_1", 1.5f, -3.4f, 0, 1, "right"),
            new Room { id = "Cocina", size = new Vector3(3.4f, 2.7f, 3.8f), walls = "ENV_Plaster_OffWhite", floor = "Floor_Brick", dado = "ENV_Stone_Sandstone", light = new Color(1f, 0.9f, 0.74f) }
                .Add("Workbench_Drawers", 0.3f, -3.8f, 0, 1, "back").Add("Shelf_Small_Bottles", 0.3f, -3.8f, 0, 1, "back", 1.55f)
                .Add("Pot_1", 0.0f, -3.5f, 0, 1, "on").Add("Shelf_Simple", -1.7f, -2.2f, 90, 1, "left", 1.4f)
                .Add("Table_Large", 0.3f, -1.9f, 0, 0.6f).Add("Stool", -0.5f, -1.9f).Add("Stool", 1.1f, -1.9f)
                .Add("Barrel_Apples", 1.35f, -3.4f, 20),
            new Room { id = "Dormitorio", size = new Vector3(3.6f, 2.7f, 4.0f), walls = "ENV_Plaster_Sage", floor = "Floor_WoodLight", light = new Color(1f, 0.72f, 0.45f), lightIntensity = 1.7f }
                .Add("Bed_Twin1", 0.2f, -4.0f, 0, 1, "back").Add("Nightstand_Shelf", -0.9f, -4.0f, 0, 1, "back")
                .Add("CandleStick", -0.9f, -3.8f, 0, 1, "on").Add("Chest_Wood", 0.2f, -2.2f, 0)
                .Add("Cabinet", 1.8f, -2.4f, -90, 1, "right"),
            new Room { id = "Bar", size = new Vector3(5.0f, 3.0f, 7.0f), walls = "ENV_Plaster_Ochre", floor = "Floor_RoundRocks", dado = "MI_WoodTrim", light = new Color(1f, 0.7f, 0.42f), lightIntensity = 2.8f, shop = true, litBias = 1f }
                .Add("Shelf_Small_Bottles", 2.5f, -3.0f, -90, 1.2f, "right", 1.5f).Add("Shelf_Small_Bottles", 2.5f, -4.8f, -90, 1.2f, "right", 1.5f)
                .Add("Barrel", -1.6f, -7.0f, 0, 1, "back").Add("Barrel", -0.6f, -7.0f, 0, 1, "back").Add("Barrel_Holder", 1.2f, -7.0f, 0, 1, "back")
                .Add("Table_Large", -1.2f, -3.0f, 0, 0.55f).Add("Stool", -1.9f, -3.0f).Add("Stool", -0.5f, -3.0f)
                .Add("Table_Large", -1.2f, -5.2f, 0, 0.55f).Add("Stool", -1.9f, -5.2f).Add("Mug", -1.2f, -5.2f, 0, 1, "on")
                .Add("Stool", 1.1f, -3.2f).Add("Stool", 1.1f, -4.4f).Add("Mug", -1.2f, -3.0f, 0, 1, "on"),
            new Room { id = "Tienda", size = new Vector3(5.0f, 3.0f, 6.0f), walls = "ENV_Plaster_OffWhite", floor = "Floor_UnevenBrick", light = new Color(1f, 0.93f, 0.82f), lightIntensity = 2.6f, shop = true }
                .Add("Shelf_Simple", -2.5f, -2.0f, 90, 1.2f, "left", 0.9f).Add("Shelf_Simple", -2.5f, -4.0f, 90, 1.2f, "left", 0.9f)
                .Add("Shelf_Simple", 0.0f, -6.0f, 0, 1.2f, "back", 1.0f).Add("FarmCrate_Apple", -1.9f, -2.0f, 90).Add("FarmCrate_Carrot", -1.9f, -3.0f, 90)
                .Add("FarmCrate_Apple", -1.9f, -4.0f, 90).Add("Barrel_Apples", -0.8f, -5.6f).Add("Crate_Wooden", 1.2f, -5.5f, 15)
                .Add("Workbench", 1.6f, -2.6f, -90, 1, "right").Add("Bag", 0.6f, -5.4f),
            // shop programmes (owner audit: "los locales comerciales son demasiado genéricos")
            new Room { id = "Farmacia", size = new Vector3(5.0f, 3.0f, 5.5f), walls = "ENV_Plaster_OffWhite", floor = "Floor_WoodLight", light = new Color(0.92f, 0.97f, 1f), lightIntensity = 3.0f, shop = true, litBias = 1f }
                .Add("Shelf_Small_Bottles", -2.5f, -1.8f, 90, 1.3f, "left", 1.2f).Add("Shelf_Small_Bottles", -2.5f, -3.4f, 90, 1.3f, "left", 1.2f)
                .Add("Shelf_Small_Bottles", 2.5f, -2.4f, -90, 1.3f, "right", 1.2f).Add("Shelf_Small_Bottles", -0.8f, -5.5f, 0, 1.3f, "back", 1.3f)
                .Add("Shelf_Small_Bottles", 0.9f, -5.5f, 0, 1.3f, "back", 1.3f).Add("Table_Large", 0.3f, -3.6f, 90, 0.7f).Add("SmallBottles_1", 0.3f, -3.6f, 0, 1, "on"),
            new Room { id = "Panaderia", size = new Vector3(5.0f, 3.0f, 5.0f), walls = "ENV_Plaster_Ochre", floor = "Floor_Brick", dado = "ENV_Stone_Sandstone", light = new Color(1f, 0.84f, 0.6f), lightIntensity = 2.8f, shop = true, litBias = 1f }
                .Add("Shelf_Simple", 0.0f, -5.0f, 0, 1.3f, "back", 1.0f).Add("Bag", -1.2f, -4.6f).Add("Bag", -0.7f, -4.7f, 30).Add("Barrel", 1.8f, -4.4f)
                .Add("Table_Large", 0.0f, -2.8f, 0, 0.8f).Add("Pot_1", -0.4f, -2.8f, 0, 1, "on").Add("Crate_Wooden", -1.9f, -2.2f, 20).Add("Mug", 0.5f, -2.8f, 0, 1, "on"),
            new Room { id = "Oficina", size = new Vector3(5.0f, 3.0f, 5.5f), walls = "ENV_Plaster_Cream", floor = "Floor_WoodLight", light = new Color(0.95f, 0.97f, 1f), lightIntensity = 2.7f, shop = true, litBias = 1f }
                .Add("Table_Large", -0.6f, -3.2f, 0, 0.7f).Add("Chair_1", -0.6f, -3.9f, 0).Add("Chair_1", -0.6f, -2.4f, 180).Add("BookGroup_Medium_2", -0.6f, -3.2f, 0, 1, "on")
                .Add("Cabinet", 2.2f, -4.4f, -90, 1, "right").Add("Bookcase_2", -1.4f, -5.5f, 0, 1, "back").Add("Bookcase_2", 0.4f, -5.5f, 0, 1, "back"),
            new Room { id = "Taller", size = new Vector3(5.0f, 3.2f, 7.0f), walls = "ENV_Plaster_Stained", floor = "Floor_UnevenBrick", light = new Color(1f, 0.86f, 0.66f), lightIntensity = 1.7f, shop = true }
                .Add("Workbench", -1.6f, -7.0f, 0, 1, "back").Add("Workbench_Drawers", 0.6f, -7.0f, 0, 1, "back").Add("Crate_Wooden", 2.0f, -5.8f, 10)
                .Add("Crate_Wooden", 2.0f, -5.8f, 35, 1, "on").Add("Barrel", -2.0f, -3.6f).Add("Chain_Coil", 1.2f, -3.2f).Add("Rope_2", -0.4f, -3.0f)
                .Add("Bucket_Metal", 1.8f, -2.4f).Add("Shelf_Simple", -2.5f, -5.0f, 90, 1.2f, "left", 1.1f),
            new Room { id = "Vacio", size = new Vector3(5.0f, 3.0f, 6.0f), walls = "ENV_Plaster_Stained", floor = "Floor_UnevenBrick", light = new Color(1f, 0.95f, 0.85f), lightIntensity = 0.8f, shop = true }
                .Add("Crate_Wooden", -1.6f, -5.2f, 12).Add("Crate_Wooden", 1.4f, -4.4f, -20).Add("FarmCrate_Empty", 0.2f, -5.6f, 5).Add("Bucket_Wooden_1", -0.4f, -3.0f),
        };

        /// <summary>Opening kinds: the glazing's extent in the module frame (y0, y1, half width) so blinds and
        /// curtains sit inside it. Homes get W (wide window), T (small round-head), D (balcony/gallery door);
        /// shops S (display) and E (door).</summary>
        public static readonly Dictionary<string, Vector4> Openings = new Dictionary<string, Vector4>
        {
            { "W", new Vector4(0.98f, 2.46f, 0.6f, 0) },
            { "D", new Vector4(0.05f, 2.28f, 0.5f, 0) },
            { "T", new Vector4(1.1f, 2.45f, 0.3f, 0) },
            { "S", new Vector4(0.66f, 2.28f, 0.7f, 0) },
            { "E", new Vector4(0.02f, 2.2f, 0.7f, 0) },
        };

        /// <summary>Per-kind material variants of every room (same cubemap): ENV_Interior_{room}_{kind}. Cheap: no
        /// capture, just material copies with their opening and their share of blinds and net curtains.</summary>
        [MenuItem("JuegoDef/ENV/8b Interior Variants")]
        public static void Variants()
        {
            foreach (var room in Rooms)
            {
                var basePath = $"{Folder}/ENV_Interior_{room.id}.mat";
                var baseMat = AssetDatabase.LoadAssetAtPath<Material>(basePath);
                if (!baseMat) throw new System.InvalidOperationException("ENV_INTERIOR_ROOM_NOT_BUILT " + room.id + " (run 8 Build Interior Rooms)");
                foreach (var kind in room.shop ? new[] { "S", "E" } : new[] { "W", "T", "D" })
                {
                    var path = $"{Folder}/ENV_Interior_{room.id}_{kind}.mat";
                    var m = AssetDatabase.LoadAssetAtPath<Material>(path);
                    if (!m) { m = new Material(baseMat); AssetDatabase.CreateAsset(m, path); }
                    else m.CopyPropertiesFromMaterial(baseMat);
                    m.SetVector("_Opening", Openings[kind]);
                    m.SetFloat("_Blinds", room.shop ? 0f : kind == "D" ? 0.25f : 0.45f);
                    m.SetFloat("_Curtains", room.shop ? 0f : kind == "T" ? 0.3f : 0.45f);
                    m.SetFloat("_Reflect", room.shop ? 0.08f : 0.12f);
                    m.enableInstancing = true;
                    EditorUtility.SetDirty(m);
                }
            }
            AssetDatabase.SaveAssets();
        }

        public static bool IsShopRoom(string id) => Rooms.Any(r => r.id == id && r.shop);

        [MenuItem("JuegoDef/ENV/8 Build Interior Rooms")]
        public static void BuildMenu() => BuildAll();

        /// <summary>Captures every room (or only the listed ids) and makes its material, then the per-opening variants.
        /// Opens temporary scenes: run it before building a district.</summary>
        public static void BuildAll(string only = null)
        {
            var want = string.IsNullOrEmpty(only) ? null : new HashSet<string>(only.Split(','));
            EnvKit.ClearCache();
            EnvKit.EnsureFolder(Folder);
            var shader = Shader.Find("JuegoDef/ENV/Interior Room");
            if (!shader) throw new System.InvalidOperationException("ENV_INTERIOR_SHADER_MISSING");
            foreach (var room in Rooms)
            {
                if (want != null && !want.Contains(room.id)) continue;
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                RenderSettings.ambientMode = AmbientMode.Flat;
                RenderSettings.ambientLight = new Color(0.32f, 0.3f, 0.28f);
                RenderSettings.fog = false;
                RenderSettings.skybox = null;
                var root = Build(room);
                var cube = new Cubemap(CubeSize, TextureFormat.RGBA32, true);
                var camGo = new GameObject("Capture");
                var cam = camGo.AddComponent<Camera>();
                cam.transform.position = new Vector3(0, room.size.y / 2f, -room.size.z / 2f);
                cam.nearClipPlane = 0.05f;
                cam.farClipPlane = 30f;
                cam.clearFlags = CameraClearFlags.SolidColor;
                cam.backgroundColor = Color.black;
                bool asyncWas = ShaderUtil.allowAsyncCompilation;
                ShaderUtil.allowAsyncCompilation = false;
                bool ok = cam.RenderToCubemap(cube);
                ShaderUtil.allowAsyncCompilation = asyncWas;
                if (!ok) throw new System.InvalidOperationException("ENV_INTERIOR_CAPTURE_FAILED " + room.id);
                cube.Apply(true);
                EditorUtility.CompressCubemapTexture(cube, TextureFormat.DXT1, UnityEditor.TextureCompressionQuality.Best);
                var cubePath = $"{Folder}/T_ENV_Room_{room.id}.asset";
                var old = AssetDatabase.LoadAssetAtPath<Cubemap>(cubePath);
                if (old) { EditorUtility.CopySerialized(cube, old); cube = old; }
                else AssetDatabase.CreateAsset(cube, cubePath);
                var matPath = $"{Folder}/ENV_Interior_{room.id}.mat";
                var mat = AssetDatabase.LoadAssetAtPath<Material>(matPath);
                if (!mat) { mat = new Material(shader); AssetDatabase.CreateAsset(mat, matPath); }
                mat.shader = shader;
                mat.SetTexture("_RoomCube", cube);
                mat.SetVector("_RoomSize", new Vector4(room.size.x, room.size.y, room.size.z, 0));
                mat.SetColor("_Tint", Color.white);
                mat.SetFloat("_LitBias", room.litBias);
                mat.enableInstancing = true;
                EditorUtility.SetDirty(mat);
                Debug.Log($"JD_ENV_INTERIOR {room.id} items={root.childCount} -> {cubePath}");
            }
            AssetDatabase.SaveAssets();
            Variants();
        }

        /// <summary>The furnished room in the open scene; returns its root.</summary>
        public static Transform Build(Room room)
        {
            var root = new GameObject("Room_" + room.id).transform;
            float w = room.size.x, h = room.size.y, d = room.size.z;
            var wall = TiledCopy(EnvKit.Mat(room.walls), 2.5f);
            Slab(root, "Back", new Vector3(0, h / 2, -d - 0.05f), new Vector3(w + 0.2f, h + 0.2f, 0.1f), wall);
            Slab(root, "Left", new Vector3(-w / 2 - 0.05f, h / 2, -d / 2), new Vector3(0.1f, h + 0.2f, d + 0.2f), wall);
            Slab(root, "Right", new Vector3(w / 2 + 0.05f, h / 2, -d / 2), new Vector3(0.1f, h + 0.2f, d + 0.2f), wall);
            Slab(root, "Front", new Vector3(0, h / 2, 0.05f), new Vector3(w + 0.2f, h + 0.2f, 0.1f), wall);
            Slab(root, "Ceiling", new Vector3(0, h + 0.05f, -d / 2), new Vector3(w + 0.2f, 0.1f, d + 0.2f), TiledCopy(EnvKit.Mat("ENV_Plaster_OffWhite"), 2.5f));
            if (room.dado != null)
            {
                // wainscot / tiled dado band on the three visible walls
                var dado = TiledCopy(EnvKit.Mat(room.dado), 1.5f);
                Slab(root, "DadoB", new Vector3(0, 0.55f, -d + 0.01f), new Vector3(w, 1.1f, 0.04f), dado);
                Slab(root, "DadoL", new Vector3(-w / 2 + 0.01f, 0.55f, -d / 2), new Vector3(0.04f, 1.1f, d), dado);
                Slab(root, "DadoR", new Vector3(w / 2 - 0.01f, 0.55f, -d / 2), new Vector3(0.04f, 1.1f, d), dado);
            }
            // ceiling beams: the lebaniego interior (timber ceilings)
            var beam = EnvKit.Mat("MI_WoodTrim");
            for (float x = -w / 2 + 0.9f; x < w / 2 - 0.3f; x += 1.2f)
                Slab(root, "Beam", new Vector3(x, h - 0.09f, -d / 2), new Vector3(0.16f, 0.18f, d), beam);
            // kit floor tiles over the whole room
            var floorGroup = EnvKit.Group(root, "Floor");
            var probe = EnvKit.Place(room.floor, floorGroup, Vector3.zero, 0);
            var fb = EnvPreview.BoundsOf(probe);
            Object.DestroyImmediate(probe);
            float tx = Mathf.Max(0.5f, fb.size.x), tz = Mathf.Max(0.5f, fb.size.z);
            for (float x = -w / 2; x < w / 2; x += tx)
                for (float z = -d; z < 0; z += tz)
                {
                    var t = EnvKit.Place(room.floor, floorGroup, Vector3.zero, 0);
                    var b = EnvPreview.BoundsOf(t);
                    t.transform.position += new Vector3(x - b.min.x, -b.max.y, z - b.min.z);
                }
            GameObject last = null;
            foreach (var it in room.items)
            {
                var go = EnvKit.Place(it.module, root, Vector3.zero, it.rot, Vector3.one * it.scale);
                EnvKit.Remap(go, go.GetComponentsInChildren<Renderer>(true).SelectMany(r => r.sharedMaterials).Where(m => m)
                    .Select(m => m.name).Distinct().Where(n => HasMat("ENV_Src_" + n)).ToDictionary(n => n, n => "ENV_Src_" + n));
                var b = EnvPreview.BoundsOf(go);
                var pos = new Vector3(it.at.x - b.center.x, it.at.y - b.min.y, it.at.z - b.center.z);
                if (it.snap == "back") pos.z = -d + 0.03f - b.min.z;
                if (it.snap == "left") pos.x = -w / 2 + 0.03f - b.min.x;
                if (it.snap == "right") pos.x = w / 2 - 0.03f - b.max.x;
                if (it.snap == "on" && last)
                {
                    var lb = EnvPreview.BoundsOf(last);
                    pos = new Vector3(it.at.x - b.center.x, lb.max.y - b.min.y, it.at.z - b.center.z);
                }
                go.transform.position += pos;
                if (it.snap != "on") last = go;
            }
            // lighting: a ceiling lamp over the middle of the room (bulb visible), a softer fill near the back
            AddLight(root, new Vector3(0, h - 0.35f, -d * 0.45f), room.light, room.lightIntensity, Mathf.Max(w, d) * 1.6f, true);
            AddLight(root, new Vector3(0, h * 0.6f, -d * 0.85f), room.light, room.lightIntensity * 0.45f, Mathf.Max(w, d), false);
            return root;
        }

        static bool HasMat(string name)
        {
            try { return EnvKit.Mat(name); }
            catch (System.ArgumentException) { return false; }
        }

        static Material TiledCopy(Material src, float metresPerTile)
        {
            var m = new Material(src);
            foreach (var prop in new[] { "_BaseMap", "_Base_Color_Texture", "_MainTex" })
                if (m.HasProperty(prop)) m.SetTextureScale(prop, Vector2.one * (4f / metresPerTile));
            return m;
        }

        static void Slab(Transform parent, string name, Vector3 centre, Vector3 size, Material mat)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = name;
            go.transform.SetParent(parent, false);
            go.transform.localPosition = centre;
            go.transform.localScale = size;
            go.GetComponent<Renderer>().sharedMaterial = mat;
        }

        static void AddLight(Transform parent, Vector3 at, Color c, float intensity, float range, bool bulb)
        {
            var go = new GameObject("Lamp");
            go.transform.SetParent(parent, false);
            go.transform.localPosition = at;
            var l = go.AddComponent<Light>();
            l.type = LightType.Point;
            l.color = c;
            l.intensity = intensity;
            l.range = range;
            if (!bulb) return;
            var b = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            b.transform.SetParent(go.transform, false);
            b.transform.localScale = Vector3.one * 0.18f;
            var m = new Material(Shader.Find("Universal Render Pipeline/Unlit"));
            m.SetColor("_BaseColor", Color.Lerp(c, Color.white, 0.6f));
            b.GetComponent<Renderer>().sharedMaterial = m;
        }
    }
}

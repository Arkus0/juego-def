using System.Collections.Generic;
using System.IO;
using JuegoDef.Env;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace JuegoDef.City
{
    /// <summary>
    /// Small verbs for placing things by hand in the authored slices of the town (WP-CITY-IVX-HUMAN-01). Each call is
    /// one decision of the level designer (what, where, whose); nothing here distributes, repeats or picks at random.
    /// Painted surfaces come from Tools/city_ivanix/tools/paint_plaza.py and render with the town's DC Plus shader;
    /// dirt decals with the ENV stain shader (2x multiply). Shops show their room lit by day (shop lights on), as in
    /// Shenmue, through the ENV fake-interior shader.
    /// </summary>
    public static class CityHand
    {
        public const string Root = "Assets/JuegoDef/City/Authored/PlazaMayor";
        const string TexDir = Root + "/Textures";
        const string MatDir = Root + "/Materials";
        const string MeshDir = Root + "/Meshes";
        const string DcDir = "Assets/JuegoDef/City/DCMaterials";

        // ------------------------------------------------------------------ materials

        /// <summary>A painted surface: DC Plus with the texture <paramref name="tex"/> (cut-out for decals with holes,
        /// two-sided for things seen from both faces: pennants, cards).</summary>
        public static Material Painted(string tex, bool cutout = false, bool twoSided = false, float gloss = 0f, string name = null)
        {
            EnvKit.EnsureFolder(MatDir);
            var t = Texture(tex, cutout);
            var path = $"{MatDir}/{name ?? tex}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (!m) { m = new Material(Shader.Find("JuegoDef/City/DC Plus")); AssetDatabase.CreateAsset(m, path); }
            m.SetTexture("_BaseMap", t);
            m.SetColor("_BaseColor", Color.white);
            m.SetColor("_ShadeColor", new Color(0.80f, 0.83f, 0.92f, 1f));
            m.SetFloat("_AmbientScale", 1.08f);
            m.SetFloat("_MipBias", 0f);
            m.SetFloat("_SpecAmount", gloss);
            m.SetFloat("_Gloss", gloss > 0.3f ? 96f : 24f);
            m.SetFloat("_Cull", twoSided ? 0 : 2);
            m.SetFloat("_AlphaClip", cutout ? 1 : 0);
            m.SetFloat("_Cutoff", 0.5f);
            if (cutout) { m.EnableKeyword("_ALPHATEST_ON"); m.renderQueue = (int)RenderQueue.AlphaTest; }
            else { m.DisableKeyword("_ALPHATEST_ON"); m.renderQueue = -1; }
            EditorUtility.SetDirty(m);
            return m;
        }

        /// <summary>A dirt decal (ENV stain, 2x multiply; texture painted around mid grey).</summary>
        public static Material Stain(string tex, float strength = 1f)
        {
            EnvKit.EnsureFolder(MatDir);
            var t = Texture(tex, true);
            var path = $"{MatDir}/{tex}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (!m) { m = new Material(Shader.Find("JuegoDef/ENV/Stain")); AssetDatabase.CreateAsset(m, path); }
            m.SetTexture("_BaseMap", t);
            m.SetFloat("_Strength", strength);
            EditorUtility.SetDirty(m);
            return m;
        }

        /// <summary>Flat colour, allowed only for glass, rubber and small metal parts (brief, section 0).</summary>
        public static Material Flat(string name, Color c, float gloss = 0f)
        {
            EnvKit.EnsureFolder(MatDir);
            var path = $"{MatDir}/{name}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (!m) { m = new Material(Shader.Find("JuegoDef/City/DC Plus")); AssetDatabase.CreateAsset(m, path); }
            m.SetColor("_BaseColor", c);
            m.SetFloat("_SpecAmount", gloss);
            m.SetFloat("_Gloss", 64f);
            EditorUtility.SetDirty(m);
            return m;
        }

        static Texture2D Texture(string tex, bool alpha)
        {
            var path = $"{TexDir}/{tex}.png";
            AssetDatabase.ImportAsset(path);
            var ti = AssetImporter.GetAtPath(path) as TextureImporter;
            if (ti == null) throw new FileNotFoundException("JD_CITY_HAND_NO_TEXTURE " + path + " (run paint_plaza.py)");
            bool dirty = false;
            if (ti.alphaIsTransparency != alpha) { ti.alphaIsTransparency = alpha; dirty = true; }
            if (ti.filterMode != FilterMode.Bilinear) { ti.filterMode = FilterMode.Bilinear; dirty = true; }
            if (ti.anisoLevel != 4) { ti.anisoLevel = 4; dirty = true; }
            if (ti.wrapMode != TextureWrapMode.Repeat) { ti.wrapMode = TextureWrapMode.Repeat; dirty = true; }
            if (ti.maxTextureSize != 1024) { ti.maxTextureSize = 1024; dirty = true; }
            if (dirty) ti.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        /// <summary>The room a shop shows behind its glass, lit by day: the ENV room material with the shop lights on.</summary>
        public static Material ShopRoom(string room, string kind, float brightness = 1.15f)
        {
            EnvKit.EnsureFolder(MatDir);
            var src = AssetDatabase.LoadAssetAtPath<Material>($"Assets/JuegoDef/Derived/ENV/Interiors/ENV_Interior_{room}_{kind}.mat");
            if (!src) throw new FileNotFoundException("JD_CITY_HAND_NO_ROOM " + room + "_" + kind);
            var path = $"{MatDir}/PM_Interior_{room}_{kind}_Dia.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (!m) { m = new Material(src); AssetDatabase.CreateAsset(m, path); }
            else m.CopyPropertiesFromMaterial(src);
            m.SetFloat("_Brightness", brightness);
            m.SetFloat("_Reflect", 0.06f);
            m.SetFloat("_Blinds", 0f);
            m.SetFloat("_Curtains", 0f);
            EditorUtility.SetDirty(m);
            return m;
        }

        /// <summary>Puts <paramref name="room"/> behind every shop glazing on the ground floor of a building side
        /// (displays get the _S framing, doors the _E one). Returns the number of panes changed.</summary>
        public static int SetShopRoom(Transform floor0, string room, float brightness = 1.15f)
        {
            var s = ShopRoom(room, "S", brightness);
            var e = ShopRoom(room, "E", brightness);
            int n = 0;
            foreach (var r in floor0.GetComponentsInChildren<Renderer>(true))
            {
                var mats = r.sharedMaterials;
                bool ch = false;
                for (int i = 0; i < mats.Length; i++)
                {
                    if (!mats[i] || !mats[i].shader.name.Contains("Interior")) continue;
                    mats[i] = r.name.Contains("Door") ? e : s;
                    ch = true; n++;
                }
                if (ch) r.sharedMaterials = mats;
            }
            return n;
        }

        // ------------------------------------------------------------------ geometry

        /// <summary>A unit quad facing +Z (its visible side looks out along the parent's +Z), centred, UV 0..1.</summary>
        public static Mesh QuadMesh()
        {
            EnvKit.EnsureFolder(MeshDir);
            var path = MeshDir + "/PM_Quad.asset";
            var mesh = AssetDatabase.LoadAssetAtPath<Mesh>(path);
            if (mesh) return mesh;
            mesh = new Mesh { name = "PM_Quad" };
            mesh.vertices = new[] { new Vector3(-0.5f, -0.5f, 0), new Vector3(0.5f, -0.5f, 0), new Vector3(0.5f, 0.5f, 0), new Vector3(-0.5f, 0.5f, 0) };
            mesh.uv = new[] { new Vector2(1, 0), new Vector2(0, 0), new Vector2(0, 1), new Vector2(1, 1) };
            mesh.triangles = new[] { 0, 1, 2, 0, 2, 3 };   // clockwise seen from +Z (Unity's front face)
            mesh.normals = new[] { Vector3.forward, Vector3.forward, Vector3.forward, Vector3.forward };
            mesh.tangents = new[] { new Vector4(-1, 0, 0, 1), new Vector4(-1, 0, 0, 1), new Vector4(-1, 0, 0, 1), new Vector4(-1, 0, 0, 1) };
            mesh.RecalculateBounds();
            AssetDatabase.CreateAsset(mesh, path);
            return mesh;
        }

        /// <summary>A painted card in the parent's frame: centre, Euler rotation, width x height (m). With
        /// <paramref name="flat"/> the card lies on the ground facing up (decals on the paving).</summary>
        public static GameObject Quad(Transform parent, string name, Vector3 localPos, Vector3 localEuler, Vector2 size, Material m)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.transform.localPosition = localPos;
            go.transform.localRotation = Quaternion.Euler(localEuler);
            go.transform.localScale = new Vector3(size.x, size.y, 1);
            go.AddComponent<MeshFilter>().sharedMesh = QuadMesh();
            var r = go.AddComponent<MeshRenderer>();
            r.sharedMaterial = m;
            r.shadowCastingMode = ShadowCastingMode.Off;
            return go;
        }

        /// <summary>A solid box (cube primitive) with a collider, in the parent's frame.</summary>
        public static GameObject Box(Transform parent, string name, Vector3 localPos, Vector3 localEuler, Vector3 size, Material m, bool collider = true)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = name;
            if (!collider) Object.DestroyImmediate(go.GetComponent<Collider>());
            go.transform.SetParent(parent, false);
            go.transform.localPosition = localPos;
            go.transform.localRotation = Quaternion.Euler(localEuler);
            go.transform.localScale = size;
            go.GetComponent<MeshRenderer>().sharedMaterial = m;
            return go;
        }

        /// <summary>A cylinder (bottle, glass, post) standing on <paramref name="localBase"/>.</summary>
        public static GameObject Cylinder(Transform parent, string name, Vector3 localBase, float diameter, float height, Material m)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            go.name = name;
            Object.DestroyImmediate(go.GetComponent<Collider>());
            go.transform.SetParent(parent, false);
            go.transform.localPosition = localBase + Vector3.up * height / 2f;
            go.transform.localScale = new Vector3(diameter, height / 2f, diameter);
            go.GetComponent<MeshRenderer>().sharedMaterial = m;
            return go;
        }

        /// <summary>A cord with hanging pennants (or any strip) between two world points, sagging as a catenary:
        /// the strip hangs <paramref name="drop"/> m below the cord; the texture repeats every <paramref name="uvMetres"/> m.</summary>
        public static GameObject Ribbon(Transform parent, string name, Vector3 a, Vector3 b, float sag, float drop, float uvMetres, Material m)
        {
            EnvKit.EnsureFolder(MeshDir);
            int n = Mathf.Max(8, Mathf.CeilToInt(Vector3.Distance(a, b) / 0.35f));
            var verts = new List<Vector3>(); var uvs = new List<Vector2>(); var tris = new List<int>();
            float len = 0; Vector3 prev = a;
            for (int i = 0; i <= n; i++)
            {
                float t = i / (float)n;
                var p = Vector3.Lerp(a, b, t) + Vector3.down * sag * 4f * t * (1 - t);
                len += Vector3.Distance(prev, p); prev = p;
                verts.Add(p); verts.Add(p + Vector3.down * drop);
                uvs.Add(new Vector2(len / uvMetres, 1)); uvs.Add(new Vector2(len / uvMetres, 0));
                if (i > 0) { int k = i * 2; tris.AddRange(new[] { k - 2, k, k - 1, k - 1, k, k + 1 }); }
            }
            var go = new GameObject(name);
            go.transform.SetParent(parent, true);
            go.transform.position = Vector3.zero;
            go.transform.rotation = Quaternion.identity;
            var local = new List<Vector3>();
            foreach (var v in verts) local.Add(go.transform.InverseTransformPoint(v));
            var mesh = new Mesh { name = "PM_" + name };
            mesh.SetVertices(local); mesh.SetUVs(0, uvs); mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals(); mesh.RecalculateBounds();
            var path = $"{MeshDir}/PM_{name}.asset";
            if (AssetDatabase.LoadAssetAtPath<Mesh>(path)) AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(mesh, path);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var r = go.AddComponent<MeshRenderer>();
            r.sharedMaterial = m;
            r.shadowCastingMode = ShadowCastingMode.TwoSided;
            return go;
        }

        /// <summary>A kit module placed at a world point (yaw in world degrees), seated on the ground, its vendor
        /// materials swapped for their DC Plus versions where the town already has them.</summary>
        public static GameObject Kit(string module, Transform parent, Vector3 worldPos, float yaw, Vector3? scale = null, bool settle = true)
        {
            var go = EnvKit.Place(module, parent, Vector3.zero, 0, scale);
            go.transform.position = worldPos;
            go.transform.rotation = Quaternion.Euler(0, yaw, 0);
            if (settle) CityEntities.Settle(go, c => c.name.StartsWith("TERRAIN"), false);
            ToDc(go);
            return go;
        }

        /// <summary>Swaps vendor materials for the town's DC Plus versions (City/DCMaterials/DC_*).</summary>
        public static int ToDc(GameObject go)
        {
            int n = 0;
            foreach (var r in go.GetComponentsInChildren<Renderer>(true))
            {
                var mats = r.sharedMaterials; bool ch = false;
                for (int i = 0; i < mats.Length; i++)
                {
                    if (!mats[i] || mats[i].name.StartsWith("DC_") || mats[i].name.StartsWith("PM_")) continue;
                    var dc = AssetDatabase.LoadAssetAtPath<Material>($"{DcDir}/DC_{mats[i].name}.mat");
                    if (dc) { mats[i] = dc; ch = true; n++; }
                }
                if (ch) r.sharedMaterials = mats;
            }
            return n;
        }

        // ------------------------------------------------------------------ scene

        /// <summary>The building whose id is <paramref name="id"/> (BLD_&lt;id&gt; [...]).</summary>
        public static Transform Building(string id)
        {
            foreach (Transform t in GameObject.Find("CITY_IVX_Buildings").transform)
                if (t.name.StartsWith("BLD_" + id + " ")) return t;
            throw new KeyNotFoundException("JD_CITY_HAND_NO_BUILDING " + id);
        }

        /// <summary>The authored group of a vignette: CITY_IVX_Props/AUTHORED_PLAZA_MAYOR/&lt;name&gt;.</summary>
        public static Transform Vignette(string name)
        {
            var props = GameObject.Find("CITY_IVX_Props").transform;
            return EnvKit.Group(EnvKit.Group(props, "AUTHORED_PLAZA_MAYOR"), name);
        }

        /// <summary>The authored layer of a building (BLD/AUTHORED): its painted skins and the shop's own things.</summary>
        public static Transform Authored(Transform bld) => EnvKit.Group(bld, "AUTHORED");
    }
}

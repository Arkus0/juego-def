using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace JuegoDef.City
{
    /// <summary>
    /// "Dreamcast+" conversion of the town (Docs/design/CITY_STYLE_DCPLUS.md). Two steps around a Python pass:
    ///   Export  - every material the city scenes use is mapped to its albedo / normal / tint; the textures go to a
    ///             manifest (Tools/city_ivanix/reconstruction/dc_manifest.json);
    ///   (python Tools/city_ivanix/tools/dc_textures.py repaints them: relief and cavities baked into the colour,
    ///    edge-preserving smoothing, 512 px, a touch more saturation)
    ///   Convert - a DC material per source material (shader JuegoDef/City/DC Plus) on the painted texture, swapped on
    ///             the city scenes; the city camera renders without SSAO and without vignette.
    /// Fake interiors, stains, water and sky keep their own shaders. ENV01 materials and scenes are not touched.
    /// </summary>
    public static class CityDcPlus
    {
        const string TexDir = "Assets/JuegoDef/City/DCTextures";
        const string MatDir = "Assets/JuegoDef/City/DCMaterials";
        static string Manifest => Path.GetFullPath(Path.Combine(Application.dataPath, "../../../Tools/city_ivanix/reconstruction/dc_manifest.json"));
        static readonly string[] Roots = { "CITY_IVX_Base", "CITY_IVX_Buildings", "CITY_IVX_Props" };

        class Src
        {
            public Texture albedo, normal, noise;
            public Color color = Color.white;
            public Vector4 st = new Vector4(1, 1, 0, 0);
            public float worldUV, macroScale = 0.06f, macroAmount, cutoff = 0.5f, cull = 2;
            public bool clip;
            public Color emission = Color.black;
            public Texture emissionMap;
            public string kind;
        }

        static IEnumerable<Material> CityMaterials()
        {
            var set = new HashSet<Material>();
            foreach (var rn in Roots)
            {
                var r = GameObject.Find(rn);
                if (!r) continue;
                foreach (var ren in r.GetComponentsInChildren<Renderer>(true))
                    foreach (var m in ren.sharedMaterials)
                        if (m) set.Add(m);
            }
            return set;
        }

        static Src Describe(Material m)
        {
            var sh = m.shader.name;
            Texture T(string p) => m.HasProperty(p) ? m.GetTexture(p) : null;
            Color C(string p) => m.HasProperty(p) ? m.GetColor(p) : Color.white;
            float F(string p, float d) => m.HasProperty(p) ? m.GetFloat(p) : d;
            var s = new Src();
            string n = m.name;
            if (sh == "JuegoDef/ENV/Weathered Lit")
            {
                s.albedo = T("_BaseMap"); s.normal = T("_BumpMap"); s.color = C("_BaseColor");
                s.st = m.GetVector("_BaseMap_ST"); s.worldUV = F("_WorldUV", 0); s.noise = T("_NoiseMap");
                s.macroScale = F("_MacroScale", 0.06f); s.macroAmount = Mathf.Max(F("_MacroAmount", 0), 0.06f); s.cull = F("_Cull", 2);
            }
            else if (sh == "Shader Graphs/M_BaseWear" || sh == "Shader Graphs/M_BaseMaterial")
            {
                s.albedo = T("_Base_Color_Texture"); s.normal = T("_Normal_Texture");
                s.color = m.HasProperty("_Color") ? C("_Color") : Color.white;
                s.st = m.HasProperty("_Base_Color_Texture_ST") ? m.GetVector("_Base_Color_Texture_ST") : new Vector4(1, 1, 0, 0);
            }
            else if (sh == "Shader Graphs/M_Leaves")
            {
                s.albedo = T("_Texture"); s.color = C("_Color"); s.clip = true; s.cull = 0;
            }
            else if (sh == "Universal Render Pipeline/Lit")
            {
                if (F("_Surface", 0) > 0.5f) return null;                    // transparent glass stays as it is
                s.albedo = T("_BaseMap"); s.normal = T("_BumpMap"); s.color = C("_BaseColor"); s.st = m.GetVector("_BaseMap_ST");
                s.clip = F("_AlphaClip", 0) > 0.5f; s.cutoff = F("_Cutoff", 0.5f); s.cull = F("_Cull", 2);
                if (m.IsKeywordEnabled("_EMISSION")) { s.emission = C("_EmissionColor"); s.emissionMap = T("_EmissionMap"); }
            }
            else return null;                                                // interiors, stains, water, sky
            s.kind = n.Contains("Sign") || n.Contains("Blade") || n.Contains("Notice") || n.Contains("_Num_") || n.Contains("Ghost") ? "sign"
                   : s.clip ? "foliage"
                   : n.Contains("Glass") ? "glass"
                   : n.Contains("Metal") || n.Contains("Iron") || n.Contains("Rail") || n.Contains("Paint_") ? "metal"
                   : n.Contains("Pave") || n.Contains("Ground") || n.Contains("Canto") || n.Contains("Setts") || n.Contains("Losa") || n.Contains("Adoquin") ? "ground"
                   : n.Contains("Roof") ? "roof"
                   : n.Contains("Joinery") || n.Contains("Wood") ? "wood"
                   : "wall";
            return s;
        }

        static string Abs(Texture t) => t ? Path.GetFullPath(AssetDatabase.GetAssetPath(t)) : null;
        static string DcPath(Texture t) => $"{TexDir}/{t.name}_dc.png";

        [MenuItem("JuegoDef/CITY/Dreamcast+: 1 export texture manifest")]
        public static string Export()
        {
            var items = new Dictionary<string, JObject>();
            int mats = 0;
            var dcShader = Shader.Find("JuegoDef/City/DC Plus");
            foreach (var m0 in CityMaterials())
            {
                var m = m0;
                // a DC material converted before its texture was painted: export its source material's texture
                if (m.shader == dcShader)
                {
                    var bm = m.GetTexture("_BaseMap");
                    if (!AssetDatabase.GetAssetPath(m).StartsWith(MatDir) || !bm || AssetDatabase.GetAssetPath(bm).StartsWith(TexDir)) continue;
                    var srcName = m.name.Substring(3);
                    m = AssetDatabase.FindAssets($"t:Material {srcName}").Select(g => AssetDatabase.LoadAssetAtPath<Material>(AssetDatabase.GUIDToAssetPath(g)))
                        .FirstOrDefault(x => x && x.name == srcName && x.shader != dcShader);
                    if (!m) continue;
                }
                var s = Describe(m);
                if (s == null || !s.albedo) continue;
                mats++;
                var key = AssetDatabase.GetAssetPath(s.albedo);
                if (items.ContainsKey(key)) continue;
                items[key] = new JObject
                {
                    ["albedo"] = Abs(s.albedo), ["normal"] = Abs(s.normal), ["kind"] = s.kind,
                    ["out"] = Path.GetFullPath(DcPath(s.albedo)), ["max"] = s.kind == "ground" ? 1024 : s.kind == "sign" ? 512 : 512,
                };
            }
            Directory.CreateDirectory(Path.GetDirectoryName(Manifest));
            File.WriteAllText(Manifest, new JObject { ["items"] = new JArray(items.Values) }.ToString());
            Directory.CreateDirectory(Path.GetFullPath(TexDir));
            return $"JD_DC_EXPORT materials={mats} textures={items.Count} -> {Manifest}";
        }

        [MenuItem("JuegoDef/CITY/Dreamcast+: 2 convert city materials")]
        public static string Convert()
        {
            AssetDatabase.Refresh();
            if (!AssetDatabase.IsValidFolder(MatDir)) { Directory.CreateDirectory(Path.GetFullPath(MatDir)); AssetDatabase.Refresh(); }
            var shader = Shader.Find("JuegoDef/City/DC Plus");
            var map = new Dictionary<Material, Material>();
            int made = 0, missingTex = 0;
            foreach (var m in CityMaterials())
            {
                if (m.shader == shader) continue;
                var s = Describe(m);
                if (s == null) continue;
                Texture2D tex = null;
                if (s.albedo)
                {
                    var p = DcPath(s.albedo);
                    var ti = AssetImporter.GetAtPath(p) as TextureImporter;
                    if (ti)
                    {
                        bool dirty = false;
                        int max = s.kind == "ground" ? 1024 : 512;
                        if (ti.maxTextureSize != max) { ti.maxTextureSize = max; dirty = true; }
                        if (ti.anisoLevel != 4) { ti.anisoLevel = 4; dirty = true; }
                        if (ti.filterMode != FilterMode.Bilinear) { ti.filterMode = FilterMode.Bilinear; dirty = true; }
                        if (ti.alphaIsTransparency != s.clip) { ti.alphaIsTransparency = s.clip; dirty = true; }
                        if (dirty) ti.SaveAndReimport();
                        tex = AssetDatabase.LoadAssetAtPath<Texture2D>(p);
                    }
                    if (!tex) { missingTex++; tex = s.albedo as Texture2D; }
                }
                var path = $"{MatDir}/DC_{m.name}.mat";
                var dc = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (!dc) { dc = new Material(shader); AssetDatabase.CreateAsset(dc, path); made++; }
                dc.shader = shader;
                dc.SetTexture("_BaseMap", tex);
                dc.SetVector("_BaseMap_ST", s.st);
                dc.SetColor("_BaseColor", s.color);
                dc.SetColor("_ShadeColor", new Color(0.80f, 0.83f, 0.92f, 1f));   // painted shade: cool, not grey
                dc.SetFloat("_AmbientScale", 1.08f);
                dc.SetFloat("_WorldUV", s.worldUV);
                if (s.noise) dc.SetTexture("_NoiseMap", s.noise);
                dc.SetFloat("_MacroScale", s.macroScale);
                dc.SetFloat("_MacroAmount", s.noise ? s.macroAmount : 0f);
                dc.SetFloat("_Cull", s.cull);
                dc.SetFloat("_Cutoff", s.cutoff);
                dc.SetFloat("_AlphaClip", s.clip ? 1 : 0);
                if (s.clip) dc.EnableKeyword("_ALPHATEST_ON"); else dc.DisableKeyword("_ALPHATEST_ON");
                dc.SetColor("_EmissionColor", s.emission);
                if (s.emissionMap) dc.SetTexture("_EmissionMap", s.emissionMap);
                // gloss only where a person would see a sheen
                float spec = s.kind == "glass" ? 0.55f : s.kind == "metal" ? 0.25f : s.kind == "ground" ? 0.10f : 0f;
                dc.SetFloat("_SpecAmount", spec);
                dc.SetFloat("_Gloss", s.kind == "glass" ? 96f : s.kind == "metal" ? 40f : 18f);
                dc.SetFloat("_MipBias", s.kind == "sign" ? 0f : 0.3f);
                if (s.clip) dc.renderQueue = (int)RenderQueue.AlphaTest;
                EditorUtility.SetDirty(dc);
                map[m] = dc;
            }
            // DC materials made before their painted texture existed now take it
            foreach (var m in CityMaterials().Where(x => x.shader == shader && AssetDatabase.GetAssetPath(x).StartsWith(MatDir)))
            {
                var bm = m.GetTexture("_BaseMap");
                if (!bm || AssetDatabase.GetAssetPath(bm).StartsWith(TexDir)) continue;
                var painted = AssetDatabase.LoadAssetAtPath<Texture2D>(DcPath(bm));
                if (painted) { m.SetTexture("_BaseMap", painted); EditorUtility.SetDirty(m); missingTex = Mathf.Max(0, missingTex - 1); }
            }
            int swapped = 0;
            foreach (var rn in Roots)
            {
                var r = GameObject.Find(rn);
                if (!r) continue;
                foreach (var ren in r.GetComponentsInChildren<Renderer>(true))
                {
                    var arr = ren.sharedMaterials;
                    bool ch = false;
                    for (int i = 0; i < arr.Length; i++)
                        if (arr[i] && map.TryGetValue(arr[i], out var d)) { arr[i] = d; ch = true; }
                    if (ch) { ren.sharedMaterials = arr; swapped++; }
                }
                EditorSceneManager.MarkSceneDirty(r.scene);
            }
            CameraAndPost();
            for (int i = 0; i < SceneManager.sceneCount; i++) EditorSceneManager.SaveScene(SceneManager.GetSceneAt(i));
            AssetDatabase.SaveAssets();
            return $"JD_DC_CONVERT materials={map.Count} (new {made}) renderers={swapped} missing_painted_textures={missingTex}";
        }

        /// <summary>The city camera renders with a renderer without SSAO (contact shading is painted in the textures)
        /// and the city volume drops the vignette.</summary>
        static void CameraAndPost()
        {
            var urp = GraphicsSettings.currentRenderPipeline as UniversalRenderPipelineAsset;
            const string cityRendererPath = "Assets/JuegoDef/City/JD_Renderer_City.asset";
            var cityRenderer = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(cityRendererPath);
            if (!cityRenderer)
            {
                AssetDatabase.CopyAsset("Assets/JuegoDef/Rendering/JD_Renderer.asset", cityRendererPath);
                cityRenderer = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(cityRendererPath);
            }
            foreach (var f in cityRenderer.rendererFeatures.Where(f => f && f.name == "SSAO")) f.SetActive(false);
            EditorUtility.SetDirty(cityRenderer);
            var so = new SerializedObject(urp);
            var list = so.FindProperty("m_RendererDataList");
            int index = -1;
            for (int i = 0; i < list.arraySize; i++) if (list.GetArrayElementAtIndex(i).objectReferenceValue == cityRenderer) index = i;
            if (index < 0)
            {
                list.InsertArrayElementAtIndex(list.arraySize);
                index = list.arraySize - 1;
                list.GetArrayElementAtIndex(index).objectReferenceValue = cityRenderer;
                so.ApplyModifiedPropertiesWithoutUndo();
                EditorUtility.SetDirty(urp);
            }
            var cam = GameObject.Find("Main Camera");
            if (cam)
            {
                var data = cam.GetComponent<UniversalAdditionalCameraData>();
                if (data) { data.SetRenderer(index); EditorUtility.SetDirty(data); }
            }
            var vol = Object.FindObjectsByType<Volume>(FindObjectsSortMode.None).FirstOrDefault(v => v.isGlobal && v.sharedProfile && v.sharedProfile.name.StartsWith("CITY_"));
            if (vol && vol.sharedProfile.TryGet<Vignette>(out var vig)) { vig.intensity.Override(0f); EditorUtility.SetDirty(vol.sharedProfile); }
        }
    }
}

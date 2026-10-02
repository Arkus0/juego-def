using System.Linq;
using JuegoDef.Env;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace JuegoDef.City
{
    /// <summary>
    /// The town's light (owner review 2026-10-02: "falta una hora clara, sombras legibles, contacto, haze controlado"):
    /// a late-September afternoon on the Cantabrian coast. The sea is north (the antepuerto), so the sun comes from the
    /// west-south-west, low (28 deg) and warm, raking the north-south Calle Mayor; a cool sky fills the shade; marine
    /// haze only beyond ~70 m; grading pushes cool shadows against warm highlights. City-owned assets: ENV01's presets
    /// are left untouched. Shadows: 4096 map, 4 cascades, 120 m.
    /// </summary>
    public static class CityIvanixLook
    {
        const string Folder = CityIvanixSeed.SceneDir + "/Lighting";

        [MenuItem("JuegoDef/CITY/Ivanix town: apply afternoon light")]
        static void Menu() => Debug.Log(Apply());

        public static string Apply()
        {
            var baseScene = SceneManager.GetSceneByPath(CityIvanixSeed.BaseScene);
            if (!baseScene.isLoaded) { CityIvanixSeed.Open(); baseScene = SceneManager.GetSceneByPath(CityIvanixSeed.BaseScene); }
            SceneManager.SetActiveScene(baseScene);
            if (!AssetDatabase.IsValidFolder(Folder)) AssetDatabase.CreateFolder(CityIvanixSeed.SceneDir, "Lighting");

            // sun: afternoon from WSW (azimuth ~250 deg), the light travels towards ENE
            var sun = baseScene.GetRootGameObjects().SelectMany(r => r.GetComponentsInChildren<Light>(true)).FirstOrDefault(l => l.type == LightType.Directional);
            if (!sun) { sun = new GameObject("Directional Light").AddComponent<Light>(); sun.type = LightType.Directional; }
            sun.transform.rotation = Quaternion.Euler(28f, 62f, 0f);
            sun.useColorTemperature = true;
            sun.colorTemperature = 4300f;
            sun.intensity = 2.6f;
            sun.shadows = LightShadows.Soft;
            sun.shadowStrength = 1.0f;
            sun.shadowBias = 0.03f;
            sun.shadowNormalBias = 0.25f;
            RenderSettings.sun = sun;

            // ambient: cool sky, neutral equator, warm low ground bounce; lower than ENV day so shade has body
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = EnvKit.Hex("#7A91B2");
            RenderSettings.ambientEquatorColor = EnvKit.Hex("#8C847A");
            RenderSettings.ambientGroundColor = EnvKit.Hex("#4A3E33");
            RenderSettings.reflectionIntensity = 0.75f;
            // marine haze: clear street, soft distance
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = EnvKit.Hex("#B4BEC4");
            RenderSettings.fogStartDistance = 70f;
            RenderSettings.fogEndDistance = 700f;
            RenderSettings.skybox = Sky();
            Shader.SetGlobalVector("_JD_SunDir", -sun.transform.forward);

            var vol = baseScene.GetRootGameObjects().SelectMany(r => r.GetComponentsInChildren<Volume>(true)).FirstOrDefault(v => v.isGlobal);
            if (!vol)
            {
                vol = new GameObject("GlobalVolume").AddComponent<Volume>();
                vol.isGlobal = true;
            }
            vol.sharedProfile = Profile();

            // shadows that read cornices, balconies and frames from the street
            var urp = GraphicsSettings.currentRenderPipeline as UniversalRenderPipelineAsset;
            if (urp)
            {
                urp.shadowDistance = 120f;
                urp.shadowCascadeCount = 4;
                urp.cascade4Split = new Vector3(0.05f, 0.14f, 0.38f);
                urp.mainLightShadowmapResolution = 4096;
                EditorUtility.SetDirty(urp);
            }
            int swapped = SurfaceVariants(baseScene);
            DynamicGI.UpdateEnvironment();
            EditorSceneManager.MarkSceneDirty(baseScene);
            EditorSceneManager.SaveScene(baseScene);
            AssetDatabase.SaveAssets();
            return $"JD_CITY_IVX_LOOK afternoon: sun 28/62 4300K, fog 70-700, shadows 4096x4 120m, surface variants on {swapped} renderers";
        }

        /// <summary>City-owned variants of the ground and stone materials (ENV01's kit stays as reviewed): the cobbles and
        /// flagstones slightly damp, as an Atlantic street usually is, so they catch the sky; masonry with deeper relief so
        /// stone separates from the matte lime render under raking light.</summary>
        static int SurfaceVariants(Scene scene)
        {
            Material Variant(Material src)
            {
                string tweak = src.name.StartsWith("ENV_Pave_Canto") || src.name.StartsWith("ENV_Ground_Canto") ? "Humedo"
                             : src.name.StartsWith("ENV_Pave_Losa") || src.name.StartsWith("ENV_Ground_Setts") ? "Humedo"
                             : src.name.StartsWith("ENV_Mason_") || src.name.StartsWith("ENV_RiverWall_") ? "Relieve" : null;
                if (tweak == null || src.shader.name != "JuegoDef/ENV/Weathered Lit") return null;
                var path = $"{Folder}/CITY_{src.name.Substring(4)}_{tweak}.mat";
                var m = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (!m) { m = new Material(src); AssetDatabase.CreateAsset(m, path); }
                m.CopyPropertiesFromMaterial(src);
                if (tweak == "Humedo") { m.SetFloat("_Roughness", src.name.Contains("Viejo") ? 0.8f : 0.74f); }
                else { m.SetFloat("_BumpScale", Mathf.Max(1.35f, src.GetFloat("_BumpScale") * 1.4f)); m.SetFloat("_Roughness", 0.92f); }
                EditorUtility.SetDirty(m);
                return m;
            }
            var cache = new System.Collections.Generic.Dictionary<Material, Material>();
            int n = 0;
            foreach (var root in scene.GetRootGameObjects())
            foreach (var r in root.GetComponentsInChildren<Renderer>(true))
            {
                var mats = r.sharedMaterials;
                bool changed = false;
                for (int i = 0; i < mats.Length; i++)
                {
                    var src = mats[i];
                    if (!src || src.name.StartsWith("CITY_")) continue;
                    if (!cache.TryGetValue(src, out var v)) cache[src] = v = Variant(src);
                    if (v) { mats[i] = v; changed = true; }
                }
                if (changed) { r.sharedMaterials = mats; n++; }
            }
            return n;
        }

        static Material Sky()
        {
            var path = $"{Folder}/CITY_IVX_Sky_Tarde.mat";
            var sh = Shader.Find("JuegoDef/ENV/Sky Atlantic");
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (!m) { m = new Material(sh); AssetDatabase.CreateAsset(m, path); }
            m.shader = sh;
            m.SetColor("_ZenithColor", EnvKit.Hex("#557DAA"));
            m.SetColor("_HorizonColor", EnvKit.Hex("#D2C7B4"));
            m.SetColor("_GroundColor", EnvKit.Hex("#4A3E33") * 1.6f);
            m.SetColor("_SunColor", EnvKit.Hex("#FFD3A0"));
            m.SetColor("_CloudLit", EnvKit.Hex("#FFF1DE"));
            m.SetColor("_CloudShade", EnvKit.Hex("#8C95A3"));
            m.SetFloat("_CloudCoverage", 0.4f);
            m.SetFloat("_Exposure", 1.0f);
            m.SetFloat("_SunGlow", 0.7f);
            m.SetTexture("_NoiseMap", EnvKit.Tex("T_ENV_Weather_Noise"));
            EditorUtility.SetDirty(m);
            return m;
        }

        static VolumeProfile Profile()
        {
            var path = $"{Folder}/CITY_IVX_Tarde_VolumeProfile.asset";
            var p = AssetDatabase.LoadAssetAtPath<VolumeProfile>(path);
            if (!p) { p = ScriptableObject.CreateInstance<VolumeProfile>(); AssetDatabase.CreateAsset(p, path); }
            T Get<T>() where T : VolumeComponent
            {
                if (!p.TryGet<T>(out var c)) { c = p.Add<T>(true); AssetDatabase.AddObjectToAsset(c, p); }
                c.active = true;
                return c;
            }
            Get<Tonemapping>().mode.Override(TonemappingMode.Neutral);
            var ca = Get<ColorAdjustments>();
            ca.postExposure.Override(0.1f);
            ca.contrast.Override(24f);
            ca.saturation.Override(8f);
            var wb = Get<WhiteBalance>();
            wb.temperature.Override(6f);
            wb.tint.Override(0f);
            var smh = Get<ShadowsMidtonesHighlights>();
            smh.shadows.Override(new Vector4(0.92f, 0.97f, 1.10f, -0.04f));
            smh.midtones.Override(new Vector4(1.0f, 1.0f, 1.0f, 0f));
            smh.highlights.Override(new Vector4(1.07f, 1.0f, 0.91f, 0f));
            var bloom = Get<Bloom>();
            bloom.threshold.Override(1.0f);
            bloom.intensity.Override(0.25f);
            Get<Vignette>().intensity.Override(0.2f);
            EditorUtility.SetDirty(p);
            return p;
        }
    }
}

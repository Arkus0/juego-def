using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace JuegoDef.Env
{
    /// <summary>
    /// Look-development lighting presets for ENV previews and street compositions. Not final game lighting (that is
    /// presentation work), but enough to judge material/palette choices under the damp Atlantic mood of the Visual
    /// Bible instead of Unity's neutral default: soft cool sun, trilight ambient, height-less exponential fog, an owned
    /// overcast procedural sky and a small colour grade. Assets live in Derived/ENV/Lighting.
    /// </summary>
    public static class EnvLighting
    {
        const string Folder = EnvKit.Derived + "/Lighting";

        public static void Apply(string preset = "atlantic_overcast")
        {
            EnvKit.EnsureFolder(Folder);
            var dusk = preset == "atlantic_dusk";
            var sunGo = GameObject.Find("Directional Light") ?? new GameObject("Directional Light", typeof(Light));
            var sun = sunGo.GetComponent<Light>();
            sun.type = LightType.Directional;
            sun.useColorTemperature = true;
            sun.colorTemperature = dusk ? 3600 : 7400;
            sun.intensity = dusk ? 0.55f : 1.05f;
            sun.shadows = LightShadows.Soft;
            sun.shadowStrength = dusk ? 0.55f : 0.72f;
            sunGo.transform.rotation = dusk ? Quaternion.Euler(9, 235, 0) : Quaternion.Euler(47, 160, 0);

            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = EnvKit.Hex(dusk ? "#5E6C85" : "#A9B6BD");
            RenderSettings.ambientEquatorColor = EnvKit.Hex(dusk ? "#6E5E58" : "#8F9A9B");
            RenderSettings.ambientGroundColor = EnvKit.Hex(dusk ? "#2E2A28" : "#5B5A55");
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Exponential;
            RenderSettings.fogColor = EnvKit.Hex(dusk ? "#6F7486" : "#B3BDC1");
            RenderSettings.fogDensity = dusk ? 0.018f : 0.011f;
            RenderSettings.skybox = Sky(dusk);
            DynamicGI.UpdateEnvironment();

            foreach (var v in Object.FindObjectsByType<Volume>(FindObjectsSortMode.None))
                if (v.isGlobal) Object.DestroyImmediate(v.gameObject);
            var vol = new GameObject("GlobalVolume").AddComponent<Volume>();
            vol.isGlobal = true;
            vol.sharedProfile = Profile(dusk);
        }

        static Material Sky(bool dusk)
        {
            var path = $"{Folder}/ENV_Sky_{(dusk ? "Dusk" : "Overcast")}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (!m)
            {
                m = new Material(Shader.Find("Skybox/Procedural"));
                AssetDatabase.CreateAsset(m, path);
            }
            m.SetFloat("_SunDisk", 1);
            m.SetFloat("_SunSize", dusk ? 0.05f : 0.02f);
            m.SetFloat("_AtmosphereThickness", dusk ? 1.6f : 0.55f);
            m.SetColor("_SkyTint", EnvKit.Hex(dusk ? "#7C7C9A" : "#A7B4BA"));
            m.SetColor("_GroundColor", EnvKit.Hex(dusk ? "#3A3634" : "#7A7C78"));
            m.SetFloat("_Exposure", dusk ? 0.9f : 1.15f);
            EditorUtility.SetDirty(m);
            return m;
        }

        static VolumeProfile Profile(bool dusk)
        {
            var path = $"{Folder}/ENV_{(dusk ? "Dusk" : "Overcast")}_VolumeProfile.asset";
            var p = AssetDatabase.LoadAssetAtPath<VolumeProfile>(path);
            if (!p)
            {
                p = ScriptableObject.CreateInstance<VolumeProfile>();
                AssetDatabase.CreateAsset(p, path);
            }
            T Get<T>() where T : VolumeComponent
            {
                if (!p.TryGet<T>(out var c)) { c = p.Add<T>(true); AssetDatabase.AddObjectToAsset(c, p); }
                c.active = true;
                return c;
            }
            var tone = Get<Tonemapping>();
            tone.mode.Override(TonemappingMode.Neutral);
            var ca = Get<ColorAdjustments>();
            ca.postExposure.Override(dusk ? 0.2f : 0.15f);
            ca.contrast.Override(dusk ? 14f : 10f);
            ca.saturation.Override(dusk ? -8f : -14f);
            var wb = Get<WhiteBalance>();
            wb.temperature.Override(dusk ? 6f : -9f);
            wb.tint.Override(dusk ? 0f : 3f);
            var smh = Get<ShadowsMidtonesHighlights>();
            smh.shadows.Override(dusk ? new Vector4(0.9f, 0.95f, 1.1f, 0f) : new Vector4(0.95f, 1.0f, 1.06f, 0f));
            var bloom = Get<Bloom>();
            bloom.threshold.Override(1.0f);
            bloom.intensity.Override(dusk ? 0.6f : 0.25f);
            var vig = Get<Vignette>();
            vig.intensity.Override(dusk ? 0.3f : 0.18f);
            EditorUtility.SetDirty(p);
            AssetDatabase.SaveAssets();
            return p;
        }
    }
}

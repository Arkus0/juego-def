using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace JuegoDef.Env
{
    /// <summary>
    /// Look-development lighting for ENV previews and districts. Not final game lighting (presentation owns that), but
    /// the Atlantic mood judged by the owner. One preset table drives everything so sky, fog and light agree (owner
    /// audit 2026-09-29: "el cielo azul intenso y la niebla gris no terminan de casar", "la niebla lava la imagen",
    /// "la iluminación es demasiado plana"): the sky horizon IS the fog colour, fog is linear and starts beyond the
    /// street so near buildings keep their colour, the sun is lower and warmer for modelling, ambient is darker so
    /// shadows separate planes, and SSAO gives contact shadow where walls meet ground, eaves and balconies.
    /// <see cref="BuildRig"/> puts a <see cref="JDLightingRig"/> (day / dusk / night, F9 in Play Mode) into a district.
    /// Assets live in Derived/ENV/Lighting.
    /// </summary>
    public static class EnvLighting
    {
        const string Folder = EnvKit.Derived + "/Lighting";

        class Look
        {
            public string name;
            public Vector3 sun;
            public float temp, intensity, shadow;
            public string ambSky, ambEq, ambGround, fog;
            public float fogStart, fogEnd, reflection;
            public string zenith, horizon, sunCol, cloudLit, cloudShade;
            public float cloudCover, exposure, sunGlow;
            public float postExposure, contrast, saturation, temperature, bloom, vignette;
            public Vector4 shadows, highlights;
            public bool lamps;
            public float interiorDim, interiorLit, interiorShare;
            public string interiorTint;
        }

        static readonly Look[] Looks =
        {
            new Look
            {
                name = "day", sun = new Vector3(38, 212, 0), temp = 5400, intensity = 1.85f, shadow = 0.88f,
                ambSky = "#8A98A6", ambEq = "#86857D", ambGround = "#4A4640", fog = "#BCC5CA", fogStart = 45, fogEnd = 750, reflection = 0.85f,
                zenith = "#6F8FAE", horizon = "#BCC5CA", sunCol = "#FFF0D6", cloudLit = "#F4F2EC", cloudShade = "#A3ABB5", cloudCover = 0.48f, exposure = 1.0f, sunGlow = 0.4f,
                postExposure = 0.05f, contrast = 16, saturation = -2, temperature = 2, bloom = 0.18f, vignette = 0.2f,
                shadows = new Vector4(0.96f, 0.99f, 1.06f, 0), highlights = new Vector4(1.03f, 1.0f, 0.96f, 0),
                interiorDim = 0.38f, interiorLit = 0.95f, interiorShare = 0.12f, interiorTint = "#FFFFFF",
            },
            new Look
            {
                name = "dusk", sun = new Vector3(7, 252, 0), temp = 3200, intensity = 1.05f, shadow = 0.8f,
                ambSky = "#4E5670", ambEq = "#6A5A55", ambGround = "#2A2624", fog = "#8E8390", fogStart = 30, fogEnd = 520, reflection = 0.7f,
                zenith = "#3C4E74", horizon = "#C79A84", sunCol = "#FFB27A", cloudLit = "#F2B08C", cloudShade = "#5E6078", cloudCover = 0.5f, exposure = 1.0f, sunGlow = 0.9f,
                postExposure = 0.25f, contrast = 14, saturation = 4, temperature = 8, bloom = 0.55f, vignette = 0.26f,
                shadows = new Vector4(0.92f, 0.95f, 1.1f, 0), highlights = new Vector4(1.05f, 0.99f, 0.93f, 0),
                lamps = true, interiorDim = 0.25f, interiorLit = 1.35f, interiorShare = 0.45f, interiorTint = "#FFE2BC",
            },
            new Look
            {
                name = "night", sun = new Vector3(42, 140, 0), temp = 9000, intensity = 0.16f, shadow = 0.6f,
                ambSky = "#1D2638", ambEq = "#1F2330", ambGround = "#0E0F12", fog = "#1E2533", fogStart = 25, fogEnd = 380, reflection = 0.5f,
                zenith = "#0C1424", horizon = "#28303F", sunCol = "#B8C8FF", cloudLit = "#3A4458", cloudShade = "#161C28", cloudCover = 0.42f, exposure = 1.0f, sunGlow = 0.15f,
                postExposure = 0.55f, contrast = 12, saturation = -6, temperature = -4, bloom = 0.8f, vignette = 0.3f,
                shadows = new Vector4(0.92f, 0.96f, 1.12f, 0), highlights = new Vector4(1.04f, 1.0f, 0.95f, 0),
                lamps = true, interiorDim = 0.1f, interiorLit = 1.25f, interiorShare = 0.3f, interiorTint = "#FFD9A8",
            },
        };

        /// <summary>Scene lighting from a preset (previews: "day"; the legacy "atlantic_overcast" maps to day).</summary>
        public static void Apply(string preset = "day")
        {
            EnvKit.EnsureFolder(Folder);
            var look = Looks.FirstOrDefault(l => l.name == preset) ?? Looks[0];
            var sun = Sun();
            ApplyLook(look, sun);
            foreach (var v in Object.FindObjectsByType<Volume>(FindObjectsSortMode.None))
                if (v.isGlobal) Object.DestroyImmediate(v.gameObject);
            var vol = new GameObject("GlobalVolume").AddComponent<Volume>();
            vol.isGlobal = true;
            vol.sharedProfile = Profile(look);
            Renderer();
        }

        static Light Sun()
        {
            var sunGo = GameObject.Find("Directional Light") ?? new GameObject("Directional Light", typeof(Light));
            var sun = sunGo.GetComponent<Light>();
            sun.type = LightType.Directional;
            sun.shadows = LightShadows.Soft;
            return sun;
        }

        static void ApplyLook(Look l, Light sun)
        {
            sun.transform.rotation = Quaternion.Euler(l.sun);
            sun.useColorTemperature = true;
            sun.colorTemperature = l.temp;
            sun.intensity = l.intensity;
            sun.shadowStrength = l.shadow;
            RenderSettings.sun = sun;
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = EnvKit.Hex(l.ambSky);
            RenderSettings.ambientEquatorColor = EnvKit.Hex(l.ambEq);
            RenderSettings.ambientGroundColor = EnvKit.Hex(l.ambGround);
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = EnvKit.Hex(l.fog);
            RenderSettings.fogStartDistance = l.fogStart;
            RenderSettings.fogEndDistance = l.fogEnd;
            RenderSettings.skybox = Sky(l);
            RenderSettings.reflectionIntensity = l.reflection;
            Shader.SetGlobalVector("_JD_SunDir", -sun.transform.forward);
            DynamicGI.UpdateEnvironment();
        }

        static Material Sky(Look l)
        {
            var path = $"{Folder}/ENV_Sky_{l.name}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            var sh = Shader.Find("JuegoDef/ENV/Sky Atlantic");
            if (!m)
            {
                m = new Material(sh);
                AssetDatabase.CreateAsset(m, path);
            }
            m.shader = sh;
            m.SetColor("_ZenithColor", EnvKit.Hex(l.zenith));
            m.SetColor("_HorizonColor", EnvKit.Hex(l.horizon));
            m.SetColor("_GroundColor", EnvKit.Hex(l.ambGround) * 1.6f);
            m.SetColor("_SunColor", EnvKit.Hex(l.sunCol));
            m.SetColor("_CloudLit", EnvKit.Hex(l.cloudLit));
            m.SetColor("_CloudShade", EnvKit.Hex(l.cloudShade));
            m.SetFloat("_CloudCoverage", l.cloudCover);
            m.SetFloat("_Exposure", l.exposure);
            m.SetFloat("_SunGlow", l.sunGlow);
            m.SetTexture("_NoiseMap", EnvKit.Tex("T_ENV_Weather_Noise"));
            EditorUtility.SetDirty(m);
            return m;
        }

        static VolumeProfile Profile(Look l)
        {
            var path = $"{Folder}/ENV_{l.name}_VolumeProfile.asset";
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
            Get<Tonemapping>().mode.Override(TonemappingMode.Neutral);
            var ca = Get<ColorAdjustments>();
            ca.postExposure.Override(l.postExposure);
            ca.contrast.Override(l.contrast);
            ca.saturation.Override(l.saturation);
            var wb = Get<WhiteBalance>();
            wb.temperature.Override(l.temperature);
            wb.tint.Override(0f);
            var smh = Get<ShadowsMidtonesHighlights>();
            smh.shadows.Override(l.shadows);
            smh.highlights.Override(l.highlights);
            var bloom = Get<Bloom>();
            bloom.threshold.Override(1.0f);
            bloom.intensity.Override(l.bloom);
            Get<Vignette>().intensity.Override(l.vignette);
            EditorUtility.SetDirty(p);
            AssetDatabase.SaveAssets();
            return p;
        }

        /// <summary>Renderer/pipeline settings the look depends on: SSAO sized for buildings (the old 3.5 cm radius gave
        /// no contact shadow at all), more shadow distance and a third cascade for street-level contact.</summary>
        public static void Renderer()
        {
            var urp = GraphicsSettings.currentRenderPipeline as UniversalRenderPipelineAsset;
            if (!urp) return;
            if (urp.shadowDistance < 90 || urp.shadowCascadeCount != 3)
            {
                urp.shadowDistance = 90;
                urp.shadowCascadeCount = 3;
                urp.cascade3Split = new Vector2(0.08f, 0.3f);
                EditorUtility.SetDirty(urp);
            }
            var data = AssetDatabase.LoadAssetAtPath<ScriptableRendererData>("Assets/JuegoDef/Rendering/JD_Renderer.asset");
            var ssao = data ? data.rendererFeatures.FirstOrDefault(f => f && f.name == "SSAO") : null;
            if (!ssao) return;
            var so = new SerializedObject(ssao);
            void F(string prop, float v) { var sp = so.FindProperty("m_Settings." + prop); if (sp != null) sp.floatValue = v; }
            void I(string prop, int v) { var sp = so.FindProperty("m_Settings." + prop); if (sp != null) sp.intValue = v; }
            F("Intensity", 1.6f);
            F("DirectLightingStrength", 0.35f);
            F("Radius", 0.55f);
            F("Falloff", 70f);
            I("Samples", 1);          // medium
            I("BlurQuality", 0);      // high
            I("NormalSamples", 1);
            so.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(data);
            AssetDatabase.SaveAssets();
        }

        /// <summary>Lighting rig for a built district: sun, volume, sky/fog presets, the street-lamp lights (from every
        /// lamp post and wall lantern placed), one baked reflection probe over the district, and the river water
        /// level for the weathering shader. Leaves the scene on the day preset.</summary>
        public static JDLightingRig BuildRig(Transform root, Bounds district, float waterLevel)
        {
            Apply("day");
            var sun = Sun();
            var vol = Object.FindObjectsByType<Volume>(FindObjectsSortMode.None).First(v => v.isGlobal);
            var rigGo = EnvKit.Group(root, "LightingRig").gameObject;
            var rig = rigGo.GetComponent<JDLightingRig>();
            if (!rig) rig = rigGo.AddComponent<JDLightingRig>();   // Unity null: no ?? on components
            rig.sun = sun;
            rig.volume = vol;
            rig.waterLevel = waterLevel;
            // lamps: a warm point light in every lamp glass; the glass swaps to its lit material at dusk and night
            var lampOff = EnvKit.Mat("ENV_Lamp_Glass");
            var lampOn = EnvKit.Mat("ENV_Lamp_Glass_Lit");
            var lamps = EnvKit.Group(rigGo.transform, "LampLights");
            for (int k = lamps.childCount - 1; k >= 0; k--) Object.DestroyImmediate(lamps.GetChild(k).gameObject);
            var glass = new List<Renderer>();
            foreach (var r in root.GetComponentsInChildren<Renderer>(true))
            {
                if (!r.sharedMaterials.Contains(lampOff)) continue;
                glass.Add(r);
                var l = new GameObject("Lamp").AddComponent<Light>();
                l.transform.SetParent(lamps, false);
                l.transform.position = r.bounds.center;
                l.type = LightType.Point;
                l.color = EnvKit.Hex("#FFC68A");
                l.intensity = 2.4f;
                l.range = 9f;
                l.shadows = LightShadows.None;
            }
            // wall lanterns (kit lantern, no separate glass): a warm light at the lantern body
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
            {
                if (!t.name.StartsWith("ENV_Prop_Lantern_Wall") || t.parent == null || t.parent.name.StartsWith("ENV_Prop_Lantern_Wall")) continue;
                var rs = t.GetComponentsInChildren<Renderer>();
                if (rs.Length == 0) continue;
                var l = new GameObject("Lantern").AddComponent<Light>();
                l.transform.SetParent(lamps, false);
                l.transform.position = rs[0].bounds.center + t.forward * 0.1f;
                l.type = LightType.Point;
                l.color = EnvKit.Hex("#FFB978");
                l.intensity = 1.6f;
                l.range = 7f;
                l.shadows = LightShadows.None;
            }
            rig.lampLights = lamps.gameObject;
            rig.lampGlass = glass.ToArray();
            rig.lampOff = lampOff;
            rig.lampOn = lampOn;
            // one baked probe for glass/water reflections of the town itself
            var pgo = EnvKit.Group(rigGo.transform, "ReflectionProbe").gameObject;
            var probe = pgo.GetComponent<ReflectionProbe>();
            if (!probe) probe = pgo.AddComponent<ReflectionProbe>();
            probe.transform.position = new Vector3(district.center.x, waterLevel + 8f, district.center.z);
            probe.size = new Vector3(district.size.x + 40, 90, district.size.z + 40);
            probe.mode = ReflectionProbeMode.Custom;
            probe.resolution = 256;
            probe.importance = 1;
            rig.probes = new[] { probe };
            rig.presets = Looks.Select(l => new JDLightingRig.Preset
            {
                name = l.name, sunEuler = l.sun, sunTemperature = l.temp, sunIntensity = l.intensity, shadowStrength = l.shadow,
                ambientSky = EnvKit.Hex(l.ambSky), ambientEquator = EnvKit.Hex(l.ambEq), ambientGround = EnvKit.Hex(l.ambGround),
                fogColor = EnvKit.Hex(l.fog), fogStart = l.fogStart, fogEnd = l.fogEnd, skybox = Sky(l), profile = Profile(l),
                reflectionIntensity = l.reflection, lamps = l.lamps, interiorDim = l.interiorDim, interiorLit = l.interiorLit,
                interiorLitShare = l.interiorShare, interiorTint = EnvKit.Hex(l.interiorTint),
            }).ToArray();
            // bake the probe per preset (the rig swaps the cubemap with the preset)
            EnvKit.EnsureFolder($"{EnvDistrictFolder(root)}");
            for (int k = 0; k < rig.presets.Length; k++)
            {
                rig.Apply(k);
                var path = $"{EnvDistrictFolder(root)}/Probe_{rig.presets[k].name}.exr";
                Lightmapping.BakeReflectionProbe(probe, path);
                AssetDatabase.ImportAsset(path);
                rig.presets[k].probeTextures = new[] { AssetDatabase.LoadAssetAtPath<Cubemap>(path) };
            }
            rig.Apply(0);
            EditorUtility.SetDirty(rig);
            return rig;
        }

        static string EnvDistrictFolder(Transform root) => $"{EnvKit.Derived}/District/{root.name}";
    }
}

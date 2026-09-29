using System;
using UnityEngine;
using UnityEngine.Rendering;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace JuegoDef.Env
{
    /// <summary>
    /// Time-of-day look development for a built ENV scene (day / dusk / night). A preset drives the sun (or moon),
    /// trilight ambient, fog, sky, the post-processing profile, environment reflections and the reflection probes baked
    /// for it, and the night layers the district builder placed: street-lamp lights, lit lamp glass, and how many of the
    /// fake interiors behind the windows are lit (shader globals read by JuegoDef/ENV/Interior Room). Built and filled
    /// by the editor (EnvLighting.BuildRig); F9 cycles presets in Play Mode. Not the final day cycle — presentation
    /// work will own that.
    /// </summary>
    [ExecuteAlways]
    public class JDLightingRig : MonoBehaviour
    {
        [Serializable]
        public class Preset
        {
            public string name;
            public Vector3 sunEuler;
            public float sunTemperature = 6500f;
            public float sunIntensity = 1f;
            public float shadowStrength = 0.8f;
            public Color ambientSky, ambientEquator, ambientGround;
            public Color fogColor;
            public float fogDensity = 0.01f;
            public Material skybox;
            public VolumeProfile profile;
            public float reflectionIntensity = 1f;
            public bool lamps;
            [Tooltip("Brightness of dark rooms / lit rooms, and the share of lit rooms (bars add their own bias).")]
            public float interiorDim = 0.3f, interiorLit = 0.3f, interiorLitShare = 1f;
            public Color interiorTint = Color.white;
            public Cubemap[] probeTextures;
        }

        public Light sun;
        public Volume volume;
        public Preset[] presets = new Preset[0];
        public int current;
        [Tooltip("Street-lamp point lights and lamp glass, active when the preset turns lamps on.")]
        public GameObject lampLights;
        public Renderer[] lampGlass = new Renderer[0];
        public Material lampOff, lampOn;
        public ReflectionProbe[] probes = new ReflectionProbe[0];

        static readonly int DimId = Shader.PropertyToID("_JD_InteriorDim");
        static readonly int LitId = Shader.PropertyToID("_JD_InteriorLit");
        static readonly int ShareId = Shader.PropertyToID("_JD_InteriorLitShare");
        static readonly int TintId = Shader.PropertyToID("_JD_InteriorTint");

        void OnEnable()
        {
            // shader globals are not saved with the scene: restore them on load (edit mode touches nothing else)
            if (Application.isPlaying) Apply(current);
            else if (presets != null && current < presets.Length) SetInteriorGlobals(presets[current]);
        }

        void Update()
        {
#if ENABLE_INPUT_SYSTEM
            if (Application.isPlaying && Keyboard.current != null && Keyboard.current.f9Key.wasPressedThisFrame && presets.Length > 0)
                Apply((current + 1) % presets.Length);
#endif
        }

        public int IndexOf(string presetName) => Array.FindIndex(presets, p => p.name == presetName);

        public void Apply(int index)
        {
            if (presets == null || presets.Length == 0) return;
            current = Mathf.Clamp(index, 0, presets.Length - 1);
            var p = presets[current];
            if (sun)
            {
                sun.transform.rotation = Quaternion.Euler(p.sunEuler);
                sun.useColorTemperature = true;
                sun.colorTemperature = p.sunTemperature;
                sun.intensity = p.sunIntensity;
                sun.shadowStrength = p.shadowStrength;
                RenderSettings.sun = sun;
            }
            RenderSettings.ambientMode = AmbientMode.Trilight;
            RenderSettings.ambientSkyColor = p.ambientSky;
            RenderSettings.ambientEquatorColor = p.ambientEquator;
            RenderSettings.ambientGroundColor = p.ambientGround;
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Exponential;
            RenderSettings.fogColor = p.fogColor;
            RenderSettings.fogDensity = p.fogDensity;
            if (p.skybox) RenderSettings.skybox = p.skybox;
            RenderSettings.reflectionIntensity = p.reflectionIntensity;
            if (volume && p.profile) volume.sharedProfile = p.profile;
            if (lampLights) lampLights.SetActive(p.lamps);
            var glass = p.lamps ? lampOn : lampOff;
            if (glass && lampOff && lampOn)
                foreach (var r in lampGlass)
                {
                    if (!r) continue;
                    var mats = r.sharedMaterials;
                    for (int k = 0; k < mats.Length; k++)
                        if (mats[k] == lampOff || mats[k] == lampOn) mats[k] = glass;
                    r.sharedMaterials = mats;
                }
            for (int k = 0; k < probes.Length; k++)
                if (probes[k] && p.probeTextures != null && k < p.probeTextures.Length && p.probeTextures[k])
                    probes[k].customBakedTexture = p.probeTextures[k];
            SetInteriorGlobals(p);
            DynamicGI.UpdateEnvironment();
        }

        static void SetInteriorGlobals(Preset p)
        {
            Shader.SetGlobalFloat(DimId, p.interiorDim);
            Shader.SetGlobalFloat(LitId, p.interiorLit);
            Shader.SetGlobalFloat(ShareId, p.interiorLitShare);
            Shader.SetGlobalColor(TintId, p.interiorTint);
        }
    }
}

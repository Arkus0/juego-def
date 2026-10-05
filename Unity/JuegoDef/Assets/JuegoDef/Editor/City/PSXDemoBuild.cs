using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace JuegoDef.City
{
    /// <summary>
    /// Builds the playable PS1 demo scene from the private CITY_B stack in one click (the CITY_B scenes are local-only,
    /// .git/info/exclude, so the demo scene itself is a local artifact; this builder is the committed, reproducible part).
    /// What it configures, all measured on 2026-10-05/06 (session PSX demo):
    ///   - CITY_B_PS1_DEMO.unity = copy of CITY_B_Base.unity (authority stays untouched);
    ///   - CityRetroScreen 480x360 point-filtered, no MSAA (crisp PS1 raster; the old VGA bilinear read as mush);
    ///   - LDR-safe light: sun 0.82 elev 24 az 238 warm amber, CityLook sunGain 1.0 / sky 0.98 / bounce 0.58,
    ///     Suelo _SunScale 0.72 — the plaza clipped to pure white with the old HDR-over-unity stack;
    ///   - RenderSettings fog off (the PSX materials carry their own per-material Atlantic haze);
    ///   - PSXDemoCamera on Main Camera (the GC2 shot solver ended up below the plaza floor) + GC2 shot machinery off;
    ///   - PSXDemoBootstrap (the town is Base + Buildings + Props additive layers; alone, Base is a ghost town);
    ///   - Player spawn at the plaza entrance, feet on the floor (pivot is the capsule CENTRE: floor + 0.98 m).
    /// Run "JuegoDef/CITY/PSX Demo: build demo scene", then Play. Walk test: PSXDemoWalkTest or the W key.
    /// </summary>
    public static class PSXDemoBuild
    {
        const string BaseScene = "Assets/JuegoDef/Scenes/CITY_B/CITY_B_Base.unity";
        const string DemoScene = "Assets/JuegoDef/Scenes/CITY_B/CITY_B_PS1_DEMO.unity";

        [MenuItem("JuegoDef/CITY/PSX Demo: build demo scene")]
        public static string Build()
        {
            var log = new StringBuilder();
            if (AssetDatabase.LoadAssetAtPath<SceneAsset>(BaseScene) == null)
                return "ERROR: " + BaseScene + " not found (open the city worktree project).";

            if (AssetDatabase.LoadAssetAtPath<SceneAsset>(DemoScene) == null)
            {
                AssetDatabase.CopyAsset(BaseScene, DemoScene);
                log.Append("scene copied; ");
            }

            var open = EditorSceneManager.OpenScene(DemoScene, OpenSceneMode.Single);
            // close any additive layers the tab had open; the bootstrap brings them in on Play
            for (int i = EditorSceneManager.sceneCount - 1; i >= 0; i--)
            {
                var s = EditorSceneManager.GetSceneAt(i);
                if (s.path != DemoScene) EditorSceneManager.CloseScene(s, true);
            }

            var camGo = GameObject.Find("Main Camera");
            var player = GameObject.Find("Player");

            // crisp raster
            var retro = camGo.GetComponent("CityRetroScreen");
            if (retro != null)
            {
                var so = new SerializedObject(retro);
                so.FindProperty("width").intValue = 480;
                so.FindProperty("height").intValue = 360;
                so.FindProperty("bilinear").boolValue = false;
                so.FindProperty("msaa").intValue = 1;
                so.ApplyModifiedProperties();
            }
            var comfort = camGo.GetComponent("JuegoDef.City.StyleB.CityComfort");
            if (comfort != null)
            {
                var so = new SerializedObject(comfort);
                so.FindProperty("msaa").intValue = 1;
                so.ApplyModifiedProperties();
            }

            // camera: custom third-person orbit; GC2 shot machinery off
            var shot = GameObject.Find("Camera Shot");
            if (shot != null) shot.SetActive(false);
            var gc2Motor = camGo.GetComponent("GameCreator.Runtime.Cameras.MainCamera");
            if (gc2Motor != null) ((Behaviour)gc2Motor).enabled = false;
            System.Type camType = null;
            foreach (var asm in System.AppDomain.CurrentDomain.GetAssemblies())
            {
                camType = asm.GetType("JuegoDef.City.PSXDemoCamera");
                if (camType != null) break;
            }
            var demoCam = camGo.GetComponent(camType) ?? camGo.AddComponent(camType);
            var soCam = new SerializedObject(demoCam);
            soCam.FindProperty("target").objectReferenceValue = player.transform;
            soCam.FindProperty("radius").floatValue = 3.6f;
            soCam.FindProperty("headHeight").floatValue = 1.6f;
            soCam.FindProperty("pitchDeg").floatValue = 12f;
            soCam.FindProperty("fov").floatValue = 60f;
            soCam.ApplyModifiedProperties();
            System.Type bootType = null;
            foreach (var asm in System.AppDomain.CurrentDomain.GetAssemblies())
            {
                bootType = asm.GetType("JuegoDef.City.PSXDemoBootstrap");
                if (bootType != null) break;
            }
            if (camGo.GetComponent(bootType) == null) camGo.AddComponent(bootType);

            // LDR-safe afternoon light
            var sun = RenderSettings.sun;
            sun.transform.rotation = Quaternion.Euler(24f, 238f, 0f);
            sun.intensity = 0.82f;
            sun.color = new Color(1f, 0.86f, 0.68f);
            EditorUtility.SetDirty(sun);
            RenderSettings.fog = false;
            var look = camGo.GetComponent("JuegoDef.City.StyleB.CityLook");
            if (look != null)
            {
                var soL = new SerializedObject(look);
                soL.FindProperty("sunGain").floatValue = 1.0f;
                soL.FindProperty("sky").colorValue = new Color(0.98f, 0.96f, 0.92f);
                soL.FindProperty("bounce").colorValue = new Color(0.58f, 0.53f, 0.47f);
                soL.ApplyModifiedProperties();
            }
            var suelo = AssetDatabase.LoadAssetAtPath<Material>("Assets/JuegoDef/City/StyleB/Materials/Suelo.mat");
            if (suelo != null) suelo.SetFloat("_SunScale", 0.72f);

            // spawn: plaza entrance V2, capsule-centre convention (feet + 0.98)
            if (Physics.Raycast(new Vector3(-2f, 60f, -22f), Vector3.down, out var hit, 120f, ~0, QueryTriggerInteraction.Ignore))
            {
                player.transform.position = new Vector3(-2f, hit.point.y + 0.98f, -22f);
                player.transform.rotation = Quaternion.Euler(0f, 20.7f, 0f);
            }

            EditorSceneManager.MarkSceneDirty(open);
            EditorSceneManager.SaveScene(open);
            AssetDatabase.SaveAssets();
            log.Append("saved " + DemoScene);
            return "JD_PSX_DEMO " + log;
        }
    }
}

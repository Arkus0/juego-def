using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.Playables;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace JuegoDef.Characters.Editor
{
    /// <summary>
    /// Fast visual review of civilian prefabs in an isolated preview scene (Edit Mode, real ANIM-01 poses).
    /// Nothing touches the open scene. Output goes to Unity/JuegoDef/Captures/char (git-ignored operator captures).
    /// </summary>
    public static class CharReview
    {
        [Serializable]
        public class Req
        {
            public string[] ids;
            public string pose = "idle";       // idle | walk | talk | rest
            public float phase = .25f;
            public float yaw = 0f;              // character facing (0 = toward +Z camera)
            public float camYaw = 0f;           // orbit of the camera around the lineup
            public float camDistance = 4.5f;
            public float camHeight = 1.35f;
            public float lookHeight = 1.0f;
            public float lookX = 0f;
            public float fov = 40f;
            public int width = 1600;
            public int height = 900;
            public float spacing = 1.1f;
            public float[] xs;                  // optional explicit x per id
            public float[] zs;                  // optional explicit z per id
            public float[] yaws;                // optional per-id yaw
            public string[] poses;              // optional per-id pose
            public float[] phases;              // optional per-id phase
            public string output = "lineup.png";
            public bool silhouette;
            public bool bareIdentity;          // hide head accessories for an intrinsic face/cranial-shape comparison
            public string prefabRoot;           // default CharFactory.Root/Prefabs
            // stage
            public float[] sky = new[] { .53f, .62f, .72f };
            public float[] ground = new[] { .46f, .43f, .38f };
            public float[] sun = new[] { 1f, .955f, .88f };
            public float sunIntensity = 1.9f;
            public float sunPitch = 42f;
            public float sunYaw = -38f;
            public float[] ambient = new[] { .58f, .60f, .62f };
            public string stage = "street";     // street | plain
            public bool grade = true;           // ENV-day-like grading (neutral tonemap, contrast, bloom, vignette)
            public bool useRecipePoses;         // pose/phase per recipe (civilian idles) instead of one pose for all
            public bool fog = false;
            public bool civil = true;           // CharPosture civilian filter (relaxed hands, hip-width stance); false = raw ANIM-01 source
            public string ao = "off";           // SSAO for the capture: off (judge the asset) | env (ENV-01 profile) | branch (this checkout's renderer)
        }

        // ENV-01 renderer SSAO (worker/prod-env-01 JD_Renderer.asset): what townspeople are actually lit with in the CASCO.
        static readonly KeyValuePair<string, float>[] EnvAO = { new KeyValuePair<string, float>("Intensity", 1.8f), new KeyValuePair<string, float>("DirectLightingStrength", .35f), new KeyValuePair<string, float>("Radius", .55f), new KeyValuePair<string, float>("Falloff", 70f) };
        static List<KeyValuePair<SerializedProperty, float>> ApplyAO(KeyValuePair<string, float>[] values)
        {
            var restore = new List<KeyValuePair<SerializedProperty, float>>();
            var rp = GraphicsSettings.currentRenderPipeline as UniversalRenderPipelineAsset;
            if (rp == null) return restore;
            var list = new SerializedObject(rp).FindProperty("m_RendererDataList");
            for (int i = 0; i < list.arraySize; i++)
            {
                var data = list.GetArrayElementAtIndex(i).objectReferenceValue as ScriptableRendererData;
                if (data == null) continue;
                foreach (var feature in data.rendererFeatures.Where(f => f != null && f.GetType().Name.Contains("ScreenSpaceAmbientOcclusion")))
                {
                    var so = new SerializedObject(feature);
                    foreach (var kv in values)
                    {
                        var prop = so.FindProperty("m_Settings." + kv.Key);
                        if (prop == null) continue;
                        restore.Add(new KeyValuePair<SerializedProperty, float>(prop, prop.floatValue));
                        prop.floatValue = kv.Value;
                    }
                    so.ApplyModifiedPropertiesWithoutUndo();
                }
            }
            return restore;
        }

        static string CaptureDir => Path.GetFullPath(Path.Combine(Application.dataPath, "../Captures/char"));
        static string ClipId(string pose) => pose.StartsWith(CharPosture.Prefix) ? pose.Substring(CharPosture.Prefix.Length) : pose.StartsWith("ual") ? pose : pose == "walk" ? "ual1:walk_loop" : pose == "talk" ? "ual1:idle_talking_loop" : "ual1:idle_loop";
        static Color C(float[] a) => new Color(a[0], a[1], a[2]);

        public static string Render(string json) => Render(JsonUtility.FromJson<Req>(json));

        public static string Render(Req req)
        {
            Directory.CreateDirectory(CaptureDir);
            var root = req.prefabRoot ?? (CharFactory.Root + "/Prefabs");
            var graphs = new List<PlayableGraph>();
            var scene = EditorSceneManager.NewPreviewScene();
            var oldAmbientMode = RenderSettings.ambientMode; var oldAmbient = RenderSettings.ambientLight; var oldSky = RenderSettings.ambientSkyColor; var oldEq = RenderSettings.ambientEquatorColor; var oldGr = RenderSettings.ambientGroundColor;
            bool oldFog = RenderSettings.fog; Color oldFogColor = RenderSettings.fogColor; FogMode oldFogMode = RenderSettings.fogMode; float oldFogStart = RenderSettings.fogStartDistance, oldFogEnd = RenderSettings.fogEndDistance;
            var toDestroy = new List<UnityEngine.Object>();
            bool oldAsyncShaders=ShaderUtil.allowAsyncCompilation;
            ShaderUtil.allowAsyncCompilation=false;
            var aoRestore = req.ao == "env" ? ApplyAO(EnvAO) : req.ao == "off" ? ApplyAO(new[] { new KeyValuePair<string, float>("Intensity", 0f) }) : new List<KeyValuePair<SerializedProperty, float>>();
            try
            {
                RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Trilight;
                RenderSettings.ambientSkyColor = new Color(.68f, .71f, .72f); RenderSettings.ambientEquatorColor = new Color(.64f, .62f, .59f); RenderSettings.ambientGroundColor = new Color(.40f, .37f, .33f);
                if (req.stage != "street") { RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat; RenderSettings.ambientLight = C(req.ambient); }
                if (req.fog && req.stage == "street") { RenderSettings.fog = true; RenderSettings.fogMode = FogMode.Linear; RenderSettings.fogColor = new Color(.72f, .77f, .79f); RenderSettings.fogStartDistance = 22f; RenderSettings.fogEndDistance = 120f; }
                if (req.stage == "street") BuildStreet(scene, toDestroy);
                else
                {
                    var ground = GameObject.CreatePrimitive(PrimitiveType.Plane); SceneManager.MoveGameObjectToScene(ground, scene);
                    ground.transform.localScale = new Vector3(8, 1, 8);
                    var gm = new Material(Shader.Find("Universal Render Pipeline/Lit")); gm.SetColor("_BaseColor", C(req.ground)); gm.SetFloat("_Smoothness", 0.05f); toDestroy.Add(gm);
                    ground.GetComponent<Renderer>().sharedMaterial = gm; toDestroy.Add(ground);
                }
                var lightGo = new GameObject("Sun"); SceneManager.MoveGameObjectToScene(lightGo, scene);
                var light = lightGo.AddComponent<Light>(); light.type = LightType.Directional; light.color = C(req.sun); light.intensity = req.sunIntensity; light.shadows = LightShadows.Soft;
                lightGo.transform.rotation = Quaternion.Euler(req.sunPitch, req.sunYaw, 0); toDestroy.Add(lightGo);

                int n = req.ids.Length;
                var clips = new Dictionary<string, AnimationClip>();
                AnimationClip Clip(string pose) { if (pose == "rest") return null; if (!clips.TryGetValue(pose, out var c)) clips[pose] = c = req.civil ? CharPosture.Load(ClipId(pose)) : JDAnimationFactory.Load(JDAnimationFactory.ReadRequest().clips.Single(k => k.id == ClipId(pose))); return c; }
                for (int i = 0; i < n; i++)
                {
                    var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(root + "/" + req.ids[i] + ".prefab");
                    if (prefab == null) throw new InvalidOperationException("Missing prefab " + req.ids[i]);
                    var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, scene);
                    if (req.bareIdentity)
                        foreach (var renderer in go.GetComponentsInChildren<SkinnedMeshRenderer>())
                            if (new[] { "Hair", "HumanHair", "HumanGroom_Facial_", "Facial_", "Glasses", "Hat_", "Cap_", "Work_cap", "Beanie", "Beret", "Flatcap", "Brows_thick" }.Any(prefix => renderer.name.StartsWith(prefix, StringComparison.Ordinal)))
                                renderer.enabled = false;
                    float x = req.xs != null && req.xs.Length == n ? req.xs[i] : (i - (n - 1) / 2f) * req.spacing;
                    float z = req.zs != null && req.zs.Length == n ? req.zs[i] : 0f;
                    float yaw = req.yaws != null && req.yaws.Length == n ? req.yaws[i] : req.yaw;
                    go.transform.SetPositionAndRotation(new Vector3(x, 0, z), Quaternion.Euler(0, yaw, 0));
                    toDestroy.Add(go);
                    var animator = go.GetComponent<Animator>();
                    var pose = req.poses != null && req.poses.Length == n ? req.poses[i] : req.pose;
                    if (req.useRecipePoses) { var rc = CharFactory.Read().recipes.FirstOrDefault(x => x.id == req.ids[i]); if (rc != null && !string.IsNullOrEmpty(rc.pose)) pose = rc.pose; }
                    var clip = Clip(pose);
                    var recipe=CharFactory.Read().recipes.FirstOrDefault(r=>r.id==req.ids[i]);
                    if(req.civil && recipe!=null && (pose=="idle"||pose=="walk"||pose=="talk"||req.useRecipePoses))
                        clip=CharPosture.LoadFor(recipe,pose=="walk"?"Walk":pose=="talk"?"Talking":"Idle");
                    if (clip != null && animator != null)
                    {
                        animator.Rebind();
                        animator.Update(0); // initialize Humanoid skin matrices after a model reimport
                        var g = JDAnimationFactory.Graph(animator, clip, out var playable);
                        float ph = req.phases != null && req.phases.Length == n ? req.phases[i] : req.useRecipePoses ? (.17f + .37f * i) % 1f : req.phase;
                        PlayableExtensions.SetTime(playable, ph * clip.length);
                        g.Evaluate(0);
                        graphs.Add(g);
                    }
                }
                var camGo = new GameObject("CharReview camera"); SceneManager.MoveGameObjectToScene(camGo, scene); toDestroy.Add(camGo);
                var cam = camGo.AddComponent<Camera>();
                cam.fieldOfView = req.fov; cam.nearClipPlane = .05f; cam.farClipPlane = 300;
                cam.clearFlags = CameraClearFlags.SolidColor; cam.backgroundColor = C(req.sky);
                cam.scene = scene;
                var camData = camGo.AddComponent<UniversalAdditionalCameraData>(); camData.renderPostProcessing = req.grade && !req.silhouette;
                if (req.grade && !req.silhouette) AddGrade(scene, toDestroy);
                if (req.silhouette)
                {
                    var sil = new Material(Shader.Find("Universal Render Pipeline/Unlit")); sil.SetColor("_BaseColor", Color.black); sil.SetFloat("_Cull", 0); toDestroy.Add(sil);
                    var white = new Material(Shader.Find("Universal Render Pipeline/Unlit")); white.SetColor("_BaseColor", Color.white); toDestroy.Add(white);
                    foreach (var top in scene.GetRootGameObjects())
                    {
                        bool person = top.GetComponent<Animator>() != null;
                        foreach (var r in top.GetComponentsInChildren<Renderer>()) r.sharedMaterials = r.sharedMaterials.Select(m => person ? sil : white).ToArray();
                    }
                    cam.backgroundColor = Color.white;
                }
                var look = new Vector3(req.lookX, req.lookHeight, 0);
                var offset = Quaternion.Euler(0, req.camYaw, 0) * new Vector3(0, 0, req.camDistance);
                cam.transform.position = look + new Vector3(offset.x, req.camHeight - req.lookHeight, offset.z);
                cam.transform.LookAt(look);
                // A fresh URP preview camera needs a first frame to settle
                // its render context after imports/domain reloads.
                var warm = Capture(cam, scene, req.width, req.height);
                UnityEngine.Object.DestroyImmediate(warm);
                var tex = Capture(cam, scene, req.width, req.height);
                var path = Path.Combine(CaptureDir, req.output);
                File.WriteAllBytes(path, tex.EncodeToPNG());
                UnityEngine.Object.DestroyImmediate(tex);
                return path;
            }
            finally
            {
                ShaderUtil.allowAsyncCompilation=oldAsyncShaders;
                foreach (var g in graphs) if (g.IsValid()) g.Destroy();
                foreach (var o in toDestroy) if (o != null) UnityEngine.Object.DestroyImmediate(o);
                EditorSceneManager.ClosePreviewScene(scene);
                foreach (var kv in aoRestore) { kv.Key.floatValue = kv.Value; kv.Key.serializedObject.ApplyModifiedPropertiesWithoutUndo(); }
                RenderSettings.ambientMode = oldAmbientMode; RenderSettings.ambientLight = oldAmbient; RenderSettings.ambientSkyColor = oldSky; RenderSettings.ambientEquatorColor = oldEq; RenderSettings.ambientGroundColor = oldGr;
                RenderSettings.fog = oldFog; RenderSettings.fogColor = oldFogColor; RenderSettings.fogMode = oldFogMode; RenderSettings.fogStartDistance = oldFogStart; RenderSettings.fogEndDistance = oldFogEnd;
            }
        }



        [Serializable] public class SweepSample { public string id, motion; public float phase, minY, height, width; public bool finite; }
        [Serializable] public class SweepReport { public string unity; public int variants; public List<string> problems = new List<string>(); public List<SweepSample> samples = new List<SweepSample>(); }

        /// <summary>Edit-Mode numeric pose sweep: every recipe through ANIM-01 idle/walk/talking at four phases. Not a substitute for looking.</summary>
        [MenuItem("Tools/JuegoDef/Characters/Review/Pose sweep (edit mode)")]
        public static void PoseSweepMenu() => Debug.Log(PoseSweep());

        public static string PoseSweep()
        {
            var recipes = CharFactory.Read().recipes;
            var report = new SweepReport { unity = Application.unityVersion, variants = recipes.Length };
            var scene = EditorSceneManager.NewPreviewScene();
            var request = JDAnimationFactory.ReadRequest();
            var clips = new[] { "ual1:idle_loop", "ual1:walk_loop", "ual1:idle_talking_loop" }.ToDictionary(id => id, id => JDAnimationFactory.Load(request.clips.Single(c => c.id == id)));
            try
            {
                foreach (var recipe in recipes)
                {
                    var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(CharFactory.Root + "/Prefabs/" + recipe.id + ".prefab");
                    if (prefab == null) { report.problems.Add(recipe.id + ": missing prefab"); continue; }
                    var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, scene);
                    var animator = go.GetComponent<Animator>();
                    if (animator == null || animator.avatar == null || !animator.avatar.isValid || !animator.avatar.isHuman) report.problems.Add(recipe.id + ": invalid Humanoid avatar");
                    foreach (var r in go.GetComponentsInChildren<SkinnedMeshRenderer>())
                    {
                        if (r.sharedMesh == null || r.bones.Any(b => b == null)) report.problems.Add(recipe.id + ": missing mesh/bone on " + r.name);
                        foreach (var m in r.sharedMaterials) if (!CharFactory.ValidMaterial(m)) report.problems.Add(recipe.id + ": invalid material on " + r.name);
                    }
                    foreach (var kv in clips)
                        foreach (float phase in new[] { 0f, .25f, .5f, .75f })
                        {
                            animator.Rebind();
                            var profiled=CharPosture.LoadFor(recipe,kv.Key=="ual1:idle_loop"?"Idle":kv.Key=="ual1:walk_loop"?"Walk":"Talking");
                            var g = JDAnimationFactory.Graph(animator, profiled, out var playable);
                            PlayableExtensions.SetTime(playable, phase * profiled.length); g.Evaluate(0);
                            Bounds b = default; bool first = true, finite = true;
                            foreach (var r in go.GetComponentsInChildren<SkinnedMeshRenderer>())
                            {
                                var mesh = new Mesh(); r.BakeMesh(mesh);
                                foreach (var v in mesh.vertices)
                                {
                                    var w = r.transform.TransformPoint(v);
                                    finite &= !(float.IsNaN(w.x) || float.IsInfinity(w.x) || float.IsNaN(w.y) || float.IsInfinity(w.y) || float.IsNaN(w.z) || float.IsInfinity(w.z));
                                    if (first) { b = new Bounds(w, Vector3.zero); first = false; } else b.Encapsulate(w);
                                }
                                UnityEngine.Object.DestroyImmediate(mesh);
                            }
                            g.Destroy();
                            var motion = kv.Key == "ual1:idle_loop" ? "Idle" : kv.Key == "ual1:walk_loop" ? "Walk" : "Talking";
                            report.samples.Add(new SweepSample { id = recipe.id, motion = motion, phase = phase, minY = b.min.y, height = b.size.y, width = b.size.x, finite = finite });
                            if (!finite || b.size.y < 1.35f || b.size.y > 2.15f || b.size.x > 1.3f || b.min.y < -.10f || b.min.y > .15f)
                                report.problems.Add(recipe.id + ": gross posed bounds/ground failure " + motion + "/" + phase + " (h=" + b.size.y.ToString("0.00") + ", w=" + b.size.x.ToString("0.00") + ", minY=" + b.min.y.ToString("0.00") + ")");
                        }
                    UnityEngine.Object.DestroyImmediate(go);
                }
            }
            finally { EditorSceneManager.ClosePreviewScene(scene); }
            var path = Path.Combine(CharFactory.Repo, "Docs/evidence/WP-PROD-CHAR-01/review_pose_sweep.json");
            File.WriteAllText(path, JsonUtility.ToJson(report, true));
            return "CHAR_POSE_SWEEP samples=" + report.samples.Count + " problems=" + report.problems.Count + (report.problems.Count > 0 ? "\n" + string.Join("\n", report.problems.Distinct()) : "");
        }

        static Texture2D StageTexture(string name, bool normal)
        {
            string path = "Assets/JuegoDef/Characters/Stage/" + name;
            var importer = AssetImporter.GetAtPath(path) as TextureImporter;
            if (importer == null) throw new InvalidOperationException("Missing stage texture " + path + " (run Tools/char_stage.py)");
            var want = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
            if (importer.textureType != want || importer.wrapMode != TextureWrapMode.Repeat) { importer.textureType = want; importer.wrapMode = TextureWrapMode.Repeat; importer.SaveAndReimport(); }
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }
        static Material Lit(Color c, float smooth, List<UnityEngine.Object> bag)
        {
            var m = new Material(Shader.Find("Universal Render Pipeline/Lit")); m.SetColor("_BaseColor", c); m.SetFloat("_Smoothness", smooth); bag.Add(m); return m;
        }
        static GameObject Box(Scene scene, string name, Vector3 pos, Vector3 size, Material m, List<UnityEngine.Object> bag)
        {
            var g = GameObject.CreatePrimitive(PrimitiveType.Cube); g.name = name; SceneManager.MoveGameObjectToScene(g, scene);
            g.transform.position = pos; g.transform.localScale = size; g.GetComponent<Renderer>().sharedMaterial = m;
            UnityEngine.Object.DestroyImmediate(g.GetComponent<Collider>()); bag.Add(g); return g;
        }
        /// <summary>Neutral human-scale frontage (plaster, base course, joinery, doors, windows) on muted cobble.</summary>
        static void BuildStreet(Scene scene, List<UnityEngine.Object> bag)
        {
            var cobble = Lit(Color.white, .10f, bag);
            cobble.SetTexture("_BaseMap", StageTexture("T_Stage_Cobble.png", false)); cobble.SetTextureScale("_BaseMap", new Vector2(64, 64));
            cobble.SetTexture("_BumpMap", StageTexture("T_Stage_Cobble_N.png", true)); cobble.SetTextureScale("_BumpMap", new Vector2(64, 64)); cobble.EnableKeyword("_NORMALMAP"); cobble.SetFloat("_BumpScale", .8f);
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane); SceneManager.MoveGameObjectToScene(ground, scene);
            ground.transform.position = new Vector3(0, 0, 8); ground.transform.localScale = new Vector3(8, 1, 8); ground.GetComponent<Renderer>().sharedMaterial = cobble; bag.Add(ground);
            var plaster = Lit(Color.white, .04f, bag);
            plaster.SetTexture("_BaseMap", StageTexture("T_Stage_Plaster.png", false)); plaster.SetTextureScale("_BaseMap", new Vector2(56, 14));
            var stone = Lit(new Color(.65f, .62f, .57f), .05f, bag);
            var joinery = Lit(new Color(.24f, .35f, .34f), .22f, bag);
            var timber = Lit(new Color(.36f, .27f, .20f), .12f, bag);
            var glass = Lit(new Color(.16f, .21f, .23f), .70f, bag);
            var kerb = Lit(new Color(.58f, .56f, .52f), .06f, bag);
            const float wallZ = -5.6f;
            Box(scene, "Frontage", new Vector3(0, 4.5f, wallZ), new Vector3(70, 9f, .5f), plaster, bag);
            Box(scene, "Base course", new Vector3(0, .55f, wallZ + .3f), new Vector3(70, 1.1f, .2f), stone, bag);
            Box(scene, "Kerb", new Vector3(0, .07f, wallZ + 1.4f), new Vector3(70, .14f, .9f), kerb, bag);
            for (int i = -10; i <= 10; i++)
            {
                float x = i * 3.4f;
                if (Mathf.Abs(i) % 3 == 2) // door
                {
                    Box(scene, "Door frame", new Vector3(x, 1.15f, wallZ + .3f), new Vector3(1.35f, 2.3f, .16f), joinery, bag);
                    Box(scene, "Door", new Vector3(x, 1.10f, wallZ + .4f), new Vector3(1.05f, 2.15f, .1f), timber, bag);
                    continue;
                }
                foreach (float y in new[] { 2.7f, 5.6f })
                {
                    Box(scene, "Window frame", new Vector3(x, y, wallZ + .3f), new Vector3(1.45f, 1.85f, .16f), joinery, bag);
                    Box(scene, "Glass", new Vector3(x, y, wallZ + .4f), new Vector3(1.15f, 1.55f, .08f), glass, bag);
                }
            }
        }
        static void AddGrade(Scene scene, List<UnityEngine.Object> bag)
        {
            var go = new GameObject("Grade"); SceneManager.MoveGameObjectToScene(go, scene); bag.Add(go);
            var profile = ScriptableObject.CreateInstance<VolumeProfile>(); bag.Add(profile);
            var tm = profile.Add<Tonemapping>(true); tm.mode.Override(TonemappingMode.Neutral);
            var ca = profile.Add<ColorAdjustments>(true); ca.postExposure.Override(.08f); ca.contrast.Override(19f); ca.saturation.Override(3f);
            var wb = profile.Add<WhiteBalance>(true); wb.temperature.Override(6f);
            var smh = profile.Add<ShadowsMidtonesHighlights>(true);
            smh.shadows.Override(new Vector4(.95f, .98f, 1.07f, 0)); smh.highlights.Override(new Vector4(1.04f, 1f, .94f, 0));
            smh.shadowsEnd.Override(.3f); smh.highlightsStart.Override(.55f);
            var bloom = profile.Add<Bloom>(true); bloom.intensity.Override(.2f); bloom.scatter.Override(.7f); bloom.threshold.Override(1f);
            var vg = profile.Add<Vignette>(true); vg.intensity.Override(.22f); vg.smoothness.Override(.2f);
            var vol = go.AddComponent<Volume>(); vol.isGlobal = true; vol.priority = 10; vol.sharedProfile = profile;
        }

        /// <summary>Bake native skinning into static snapshots (avoids GPU-skin caching in Edit Mode), then render.</summary>
        static Texture2D Capture(Camera camera, Scene scene, int width, int height)
        {
            var skins = scene.GetRootGameObjects().SelectMany(o => o.GetComponentsInChildren<SkinnedMeshRenderer>()).Where(s => s.enabled).ToArray();
            var snapshots = new List<GameObject>(); var meshes = new List<Mesh>();
            foreach (var skin in skins)
            {
                var mesh = new Mesh(); skin.BakeMesh(mesh); meshes.Add(mesh);
                var go = new GameObject("Pose capture"); SceneManager.MoveGameObjectToScene(go, scene);
                go.transform.SetPositionAndRotation(skin.transform.position, skin.transform.rotation);
                go.transform.localScale = skin.transform.lossyScale;
                go.AddComponent<MeshFilter>().sharedMesh = mesh;
                go.AddComponent<MeshRenderer>().sharedMaterials = skin.sharedMaterials;
                snapshots.Add(go); skin.enabled = false;
            }
            var rt = RenderTexture.GetTemporary(width, height, 24, RenderTextureFormat.ARGB32);
            var old = RenderTexture.active;
            camera.targetTexture = rt; camera.Render(); camera.Render();
            RenderTexture.active = rt;
            var image = new Texture2D(width, height, TextureFormat.RGB24, false);
            image.ReadPixels(new Rect(0, 0, width, height), 0, 0); image.Apply();
            camera.targetTexture = null; RenderTexture.active = old; RenderTexture.ReleaseTemporary(rt);
            foreach (var skin in skins) skin.enabled = true;
            foreach (var go in snapshots) UnityEngine.Object.DestroyImmediate(go);
            foreach (var mesh in meshes) UnityEngine.Object.DestroyImmediate(mesh);
            return image;
        }
    }
}

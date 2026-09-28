using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Animations;
using UnityEngine.Playables;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

/// <summary>Metadata and validation glue over QuaterniusUtils and native Humanoid retargeting.</summary>
public static class JDAnimationFactory
{
    [Serializable] public class ClipInput
    {
        public string id, path, name, sourceSha256, sourceGuid, family;
        public bool loop, sample, moving;
    }
    [Serializable] public class BodyInput { public string id, path, sourceSha256; }
    [Serializable] public class Request
    {
        public string policySha256;
        public BodyInput[] targets;
        public ClipInput[] clips;
    }
    [Serializable] public class BodyResult
    {
        public string id, avatarName, sourceSha256;
        public bool validAvatar;
        public float humanScale, bodyHeight, rootDrift, rootRotationDrift, loopPoseError, motionRange;
        public float footTravel, footFloorMinimum, estimatedGaitSpeed;
        public float maxMeshExtent, forwardDot;
        public int samples;
        public List<string> issues = new List<string>();
    }
    [Serializable] public class ClipResult
    {
        public string id, sourceSha256, localId;
        public bool humanMotion, loop, sampled;
        public float length, frameRate;
        public List<string> issues = new List<string>();
        public List<BodyResult> targets = new List<BodyResult>();
        public string[] captures;
    }
    [Serializable] public class NegativeCase { public string name, diagnosis; public bool detected; }
    [Serializable] public class ImportIdentity { public string path, metaSha256; }
    [Serializable] public class Report
    {
        public string unityVersion, requestSha256, factorySha256;
        public bool playMode;
        public List<ClipResult> clips = new List<ClipResult>();
        public List<NegativeCase> negativeCases = new List<NegativeCase>();
        public List<ImportIdentity> imports = new List<ImportIdentity>();
    }
    public static string Repo => Path.GetFullPath(Path.Combine(Application.dataPath, "../../.."));
    public static string Evidence => Path.Combine(Repo, "Docs/evidence/WP-PROD-ANIM-01");
    public static Request ReadRequest() => JsonUtility.FromJson<Request>(File.ReadAllText(Path.Combine(Evidence, "batch_request.json")));
    public static string Hash(string path)
    {
        using (var s = File.OpenRead(path)) using (var h = SHA256.Create())
            return BitConverter.ToString(h.ComputeHash(s)).Replace("-", "").ToLowerInvariant();
    }
    static string Clean(string name) => name.Substring(name.LastIndexOf('|') + 1);
    static bool MatchesPreset(ModelImporter importer, ClipInput[] inputs)
    {
        if(importer.animationType!=ModelImporterAnimationType.Human || !importer.bakeAxisConversion ||
            importer.motionNodeName!="" || importer.animationCompression!=ModelImporterAnimationCompression.Off) return false;
        var settings=importer.clipAnimations;
        var defaults=importer.defaultClipAnimations;
        return settings.Length==inputs.Length && settings.All(s=> {
            var c=inputs.SingleOrDefault(x=>x.name==Clean(s.name));
            var original=defaults.SingleOrDefault(x=>x.takeName==s.takeName);
            return c!=null && s.loopTime==c.loop && !s.loopPose && s.lockRootRotation &&
                s.keepOriginalOrientation && s.lockRootPositionXZ && s.keepOriginalPositionXZ &&
                s.lockRootHeightY && s.keepOriginalPositionY && original!=null &&
                s.firstFrame==original.firstFrame && s.lastFrame==original.lastFrame &&
                s.rotationOffset==0 && s.heightOffset==0 && s.cycleOffset==0 && !s.mirror &&
                !s.hasAdditiveReferencePose;
        });
    }
    public static AnimationClip Load(ClipInput c)
    {
        var matches = AssetDatabase.LoadAllAssetsAtPath(c.path).OfType<AnimationClip>()
            .Where(x => !x.name.StartsWith("__preview__") && Clean(x.name) == c.name).ToArray();
        if (matches.Length != 1) throw new InvalidOperationException("Missing/ambiguous clip " + c.id);
        return matches[0];
    }
    static void CheckSources(Request request)
    {
        foreach (var c in request.clips.GroupBy(c => c.path).Select(g => g.First()))
            if (Hash(c.path) != c.sourceSha256 || AssetDatabase.AssetPathToGUID(c.path) != c.sourceGuid)
                throw new InvalidOperationException("Source identity mismatch " + c.path);
        foreach (var b in request.targets)
            if (Hash(b.path) != b.sourceSha256) throw new InvalidOperationException("Body identity mismatch " + b.path);
        if (request.clips.Select(c => c.id).Distinct().Count() != request.clips.Length)
            throw new InvalidOperationException("Duplicate input id");
    }

    [MenuItem("Tools/JuegoDef/Animation/Apply Factory Presets")]
    public static void ApplyPresets()
    {
        var req = ReadRequest();
        CheckSources(req);
        foreach (var group in req.clips.GroupBy(c => c.path))
        {
            var importer = (ModelImporter)AssetImporter.GetAtPath(group.Key);
            if(MatchesPreset(importer,group.ToArray())) continue;
            // Reconstruct from current source takes, including newly added stacks and full boundaries.
            importer.clipAnimations=importer.defaultClipAnimations;
            // Reuse the pinned utility, combining its settings with policy before a single reimport.
            Selection.activeObject=AssetDatabase.LoadMainAssetAtPath(group.Key);
            QuaterniusUtils.ApplyLoopToEveryClip();
            var clips = importer.clipAnimations;
            foreach (var settings in clips)
            {
                var input = group.Single(c => c.name == Clean(settings.name));
                settings.loopTime = input.loop;
                settings.loopPose = false; // Preserve source motion; seams are measured, never hidden.
                settings.lockRootRotation = true;
                settings.keepOriginalOrientation = true;
                settings.lockRootPositionXZ = true;
                settings.keepOriginalPositionXZ = true;
                settings.lockRootHeightY = true;
                settings.keepOriginalPositionY = true;
            }
            importer.clipAnimations = clips;
            // Explicit motion-node extraction overrides per-clip root settings; use Humanoid body projection.
            importer.motionNodeName = "";
            importer.animationCompression = ModelImporterAnimationCompression.Off;
            importer.SaveAndReimport();
        }
        foreach (var body in req.targets)
        {
            var importer = (ModelImporter)AssetImporter.GetAtPath(body.path);
            if(importer.animationType==ModelImporterAnimationType.Human &&
                importer.avatarSetup==ModelImporterAvatarSetup.CreateFromThisModel && importer.bakeAxisConversion &&
                !importer.optimizeGameObjects && importer.materialImportMode==ModelImporterMaterialImportMode.None) continue;
            importer.animationType = ModelImporterAnimationType.Human;
            importer.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
            importer.bakeAxisConversion = true;
            importer.optimizeGameObjects = false;
            importer.materialImportMode = ModelImporterMaterialImportMode.None;
            importer.SaveAndReimport();
        }
        Debug.Log("JD_ANIM_PRESETS_APPLIED " + req.clips.Length);
    }

    [MenuItem("Tools/JuegoDef/Animation/Verify Frozen Evidence")]
    public static void Verify()
    {
        var req=ReadRequest(); CheckSources(req);
        var report=JsonUtility.FromJson<Report>(File.ReadAllText(Path.Combine(Evidence,"runtime_report.json")));
        if(!report.playMode || report.factorySha256!=Hash("Assets/JuegoDef/Editor/Animation/AnimationFactory.cs") ||
            report.requestSha256!=Hash(Path.Combine(Evidence,"batch_request.json"))) throw new InvalidOperationException("Stale runtime report");
        foreach(var group in req.clips.GroupBy(c=>c.path))
        {
            if(!MatchesPreset((ModelImporter)AssetImporter.GetAtPath(group.Key),group.ToArray()))
                throw new InvalidOperationException("Import preset drift: "+group.Key);
            var clips=AssetDatabase.LoadAllAssetsAtPath(group.Key).OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview__")).ToArray();
            foreach(var c in group)
            {
                var clip=clips.Single(x=>Clean(x.name)==c.name);
                AssetDatabase.TryGetGUIDAndLocalFileIdentifier(clip,out string guid,out long localId);
                var entry=report.clips.Single(x=>x.id==c.id);
                if(entry.localId!=localId.ToString() || entry.loop!=clip.isLooping || entry.humanMotion!=clip.humanMotion ||
                    entry.length!=clip.length || entry.frameRate!=clip.frameRate)
                    throw new InvalidOperationException("Clip identity drift: "+c.id);
            }
        }
        foreach(var identity in report.imports)
            if(Hash(identity.path+".meta")!=identity.metaSha256) throw new InvalidOperationException("Importer identity drift: "+identity.path);
        foreach(var b in req.targets)
        {
            var body=Body(b,Vector3.zero,Color.gray);
            var errors=CheckTarget(body.GetComponent<Animator>());
            DisposeBody(body);
            if(errors.Count>0) throw new InvalidOperationException(string.Join("; ",errors));
        }
        JDAnimationPreview.VerifyPreview();
        Debug.Log("JD_ANIM_VERIFY_OK clips="+req.clips.Length+" targets="+req.targets.Length);
    }

    static readonly HumanBodyBones[] ProbeBones = {
        HumanBodyBones.Hips, HumanBodyBones.Head, HumanBodyBones.LeftHand, HumanBodyBones.RightHand,
        HumanBodyBones.LeftFoot, HumanBodyBones.RightFoot, HumanBodyBones.LeftLowerLeg, HumanBodyBones.RightLowerLeg
    };
    public static List<string> CheckTarget(Animator a)
    {
        var issues = new List<string>();
        if (a == null || a.avatar == null || !a.avatar.isValid || !a.avatar.isHuman)
        { issues.Add("invalid humanoid avatar"); return issues; }
        foreach (var bone in ProbeBones)
            if (a.GetBoneTransform(bone) == null) issues.Add("missing required bone " + bone);
        if (a.GetComponentsInChildren<SkinnedMeshRenderer>().Length == 0) issues.Add("no skinned body");
        return issues;
    }
    static List<string> CheckClip(AnimationClip clip, ClipInput input)
    {
        var issues = new List<string>();
        if (!clip.humanMotion) issues.Add("clip is not Humanoid motion");
        if (clip.length < .1f || clip.frameRate < 1) issues.Add("unusable clip boundary");
        if (clip.isLooping != input.loop) issues.Add("loop policy mismatch");
        if (Clean(clip.name) == "A_TPose") issues.Add("reference pose is not production motion");
        return issues;
    }
    static Material MakeMaterial(Color color)
    {
        var mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
        mat.hideFlags=HideFlags.HideAndDontSave;
        mat.color = color;
        mat.SetFloat("_Smoothness", .15f);
        return mat;
    }
    public static GameObject Body(BodyInput input, Vector3 position, Color color, Scene scene=default)
    {
        var source = AssetDatabase.LoadAssetAtPath<GameObject>(input.path);
        if (!source) throw new InvalidOperationException("Missing body " + input.id);
        var go = Object.Instantiate(source);
        if(scene.IsValid()) SceneManager.MoveGameObjectToScene(go,scene);
        go.name = input.id;
        go.transform.position = position;
        var a = go.GetComponent<Animator>();
        if (!a) a = go.AddComponent<Animator>();
        a.avatar = AssetDatabase.LoadAllAssetsAtPath(input.path).OfType<Avatar>().Single();
        a.applyRootMotion = true; // Root-baking validation must not be masked by disabling root application.
        a.cullingMode = AnimatorCullingMode.AlwaysAnimate;
        var mat = MakeMaterial(color);
        foreach (var r in go.GetComponentsInChildren<Renderer>())
        {
            r.sharedMaterials = r.sharedMaterials.Select(_ => mat).ToArray();
            if (r is SkinnedMeshRenderer skinned) skinned.updateWhenOffscreen = true;
        }
        return go;
    }
    public static void DisposeBody(GameObject go)
    {
        foreach(var mat in go.GetComponentsInChildren<Renderer>().SelectMany(r=>r.sharedMaterials).Distinct())
            if(mat && mat.hideFlags==HideFlags.HideAndDontSave) Object.DestroyImmediate(mat);
        Object.DestroyImmediate(go);
    }
    public static Camera Stage(Scene scene=default)
    {
        var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        if(scene.IsValid()) SceneManager.MoveGameObjectToScene(ground,scene);
        ground.name = "Meter floor";
        ground.transform.localScale = new Vector3(2, 1, 2);
        ground.GetComponent<Renderer>().sharedMaterial = MakeMaterial(new Color(.18f,.22f,.26f));
        for (int i=-4; i<=4; i++)
        {
            var stripe = GameObject.CreatePrimitive(PrimitiveType.Cube);
            if(scene.IsValid()) SceneManager.MoveGameObjectToScene(stripe,scene);
            stripe.transform.position = new Vector3(i, .001f, 0);
            stripe.transform.localScale = new Vector3(.01f,.002f,8);
            stripe.GetComponent<Renderer>().sharedMaterial = MakeMaterial(new Color(.3f,.34f,.38f));
        }
        var light = new GameObject("Key light").AddComponent<Light>();
        if(scene.IsValid()) SceneManager.MoveGameObjectToScene(light.gameObject,scene);
        light.type = LightType.Directional;
        light.intensity = 2f;
        light.transform.rotation = Quaternion.Euler(40,-30,0);
        if(!scene.IsValid())
        {
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(.55f,.55f,.55f);
        }
        var camera = new GameObject("Animation inspection camera").AddComponent<Camera>();
        if(scene.IsValid()) { SceneManager.MoveGameObjectToScene(camera.gameObject,scene); camera.scene=scene; }
        camera.transform.position = new Vector3(3.3f,2.15f,5.5f);
        camera.transform.LookAt(new Vector3(0, .95f, 0));
        camera.fieldOfView = 35;
        camera.nearClipPlane = .05f;
        camera.farClipPlane = 100;
        camera.clearFlags = CameraClearFlags.SolidColor;
        camera.backgroundColor = new Color(.055f,.075f,.1f);
        return camera;
    }
    public static PlayableGraph Graph(Animator a, AnimationClip clip, out AnimationClipPlayable playable)
    {
        var graph = PlayableGraph.Create("ANIM factory: " + clip.name);
        graph.SetTimeUpdateMode(DirectorUpdateMode.Manual);
        playable = AnimationClipPlayable.Create(graph, clip);
        playable.SetApplyFootIK(false); // Expose source retarget problems instead of hiding them.
        playable.SetApplyPlayableIK(false);
        var output = AnimationPlayableOutput.Create(graph, "Humanoid", a);
        output.SetSourcePlayable(playable);
        graph.Play();
        graph.Evaluate(0);
        return graph;
    }
    static Vector3[] Positions(Animator animator) => ProbeBones.Select(b => animator.GetBoneTransform(b).position).ToArray();
    static float XZ(Vector3 v) => new Vector2(v.x, v.z).magnitude;
    static bool Finite(Vector3 v) => !(float.IsNaN(v.x) || float.IsNaN(v.y) || float.IsNaN(v.z) || float.IsInfinity(v.sqrMagnitude));

    static BodyResult Measure(BodyInput input, ClipInput c, AnimationClip clip)
    {
        var body = Body(input, Vector3.zero, Color.gray);
        var animator = body.GetComponent<Animator>();
        var result = new BodyResult { id=input.id, sourceSha256=Hash(input.path), avatarName=animator.avatar.name,
            validAvatar=animator.avatar.isValid && animator.avatar.isHuman, issues=CheckTarget(animator) };
        if (result.issues.Count > 0) { DisposeBody(body); return result; }
        result.humanScale = animator.humanScale;
        var bind = Positions(animator);
        result.bodyHeight = bind[1].y - Mathf.Min(bind[4].y, bind[5].y);
        var graph = Graph(animator, clip, out var playable);
        var mesh = new Mesh();
        try
        {
            playable.SetTime(0);
            graph.Evaluate(0);
            var initial = Positions(animator);
            // Bone local axes differ across valid Avatars. Use the anatomical right/up frame.
            var right = animator.GetBoneTransform(HumanBodyBones.RightUpperLeg).position - animator.GetBoneTransform(HumanBodyBones.LeftUpperLeg).position;
            var up = animator.GetBoneTransform(HumanBodyBones.Head).position - animator.GetBoneTransform(HumanBodyBones.Hips).position;
            result.forwardDot = Vector3.Dot(Vector3.Cross(right, up).normalized, Vector3.forward);
            var firstFeet = new[] { initial[4], initial[5] };
            var previous = initial;
            var stanceSpeeds = new List<float>();
            var count = Mathf.Max(60, Mathf.CeilToInt(clip.length * 30));
            var dt = Mathf.Max(0, clip.length - .001f) / count;
            result.footFloorMinimum = float.MaxValue;
            for (int f=0; f<=count; f++)
            {
                graph.Evaluate(f == 0 ? 0 : dt);
                var points = Positions(animator);
                if (points.Any(p => !Finite(p))) result.issues.Add("non-finite pose");
                result.rootDrift = Mathf.Max(result.rootDrift, body.transform.position.magnitude);
                result.rootRotationDrift = Mathf.Max(result.rootRotationDrift, Quaternion.Angle(body.transform.rotation,Quaternion.identity));
                for (int i=0; i<points.Length; i++)
                    result.motionRange = Mathf.Max(result.motionRange, Vector3.Distance(points[i], initial[i]));
                for (int foot=4; foot<=5; foot++)
                {
                    result.footTravel = Mathf.Max(result.footTravel, XZ(points[foot] - firstFeet[foot-4]));
                    result.footFloorMinimum = Mathf.Min(result.footFloorMinimum, points[foot].y);
                    if (f>0 && points[foot].y < initial[foot].y + .07f && points[foot].z < previous[foot].z)
                        stanceSpeeds.Add((previous[foot].z-points[foot].z)/dt);
                }
                if (f % 5 == 0)
                    foreach (var skin in body.GetComponentsInChildren<SkinnedMeshRenderer>())
                    {
                        skin.BakeMesh(mesh);
                        var extent = Vector3.Scale(mesh.bounds.size, skin.transform.lossyScale).magnitude;
                        result.maxMeshExtent = Mathf.Max(result.maxMeshExtent, extent);
                        if (!Finite(mesh.bounds.size) || extent > 5) result.issues.Add("severe deformed/scaled mesh");
                    }
                if (f==count)
                    result.loopPoseError = points.Select((p,i) => Vector3.Distance(p,initial[i])).Max();
                previous = points;
                result.samples++;
            }
            stanceSpeeds.Sort();
            result.estimatedGaitSpeed = stanceSpeeds.Count > 0 ? stanceSpeeds[stanceSpeeds.Count/2] : 0;
            if (result.bodyHeight < 1 || result.bodyHeight > 2.5f) result.issues.Add("wrong body scale/orientation");
            if (result.rootDrift > .03f) result.issues.Add("root-motion/in-place mismatch");
            if (result.rootRotationDrift > .5f) result.issues.Add("unexpected root rotation");
            if (result.motionRange < .001f) result.issues.Add("static pose, no useful motion");
            if (c.loop && result.loopPoseError > .12f) result.issues.Add("loop boundary discontinuity");
            if (result.footFloorMinimum < -.12f) result.issues.Add("foot below floor beyond tolerance");
            // Foot travel is surfaced for contact review; moving gaits require consumer translation.
            result.issues = result.issues.Distinct().ToList();
        }
        finally { graph.Destroy(); Object.DestroyImmediate(mesh); DisposeBody(body); }
        return result;
    }
    public static Texture2D Capture(Camera camera, int width=480, int height=360)
    {
        // GPU skinning can cache the first pose within an Editor update. Bake native skinning
        // after each graph evaluation so each recorded frame displays its actual measured pose.
        var skins=Object.FindObjectsByType<SkinnedMeshRenderer>(FindObjectsSortMode.None)
            .Where(s=>s.enabled && s.gameObject.scene==camera.gameObject.scene).ToArray();
        var snapshots=new List<GameObject>();
        var meshes=new List<Mesh>();
        foreach(var skin in skins)
        {
            var mesh=new Mesh(); skin.BakeMesh(mesh); meshes.Add(mesh);
            var go=new GameObject("Pose capture"); SceneManager.MoveGameObjectToScene(go,camera.gameObject.scene);
            go.transform.SetPositionAndRotation(skin.transform.position,skin.transform.rotation);
            go.transform.localScale=skin.transform.lossyScale;
            go.AddComponent<MeshFilter>().sharedMesh=mesh;
            go.AddComponent<MeshRenderer>().sharedMaterials=skin.sharedMaterials;
            snapshots.Add(go); skin.enabled=false;
        }
        var rt = RenderTexture.GetTemporary(width,height,24,RenderTextureFormat.ARGB32);
        var old = RenderTexture.active;
        camera.targetTexture = rt;
        camera.Render();
        RenderTexture.active = rt;
        var image = new Texture2D(width,height,TextureFormat.RGB24,false);
        image.ReadPixels(new Rect(0,0,width,height),0,0);
        image.Apply();
        camera.targetTexture = null;
        RenderTexture.active = old;
        RenderTexture.ReleaseTemporary(rt);
        foreach(var skin in skins) skin.enabled=true;
        foreach(var go in snapshots) Object.DestroyImmediate(go);
        foreach(var mesh in meshes) Object.DestroyImmediate(mesh);
        return image;
    }
    static void ContactSheets(Request request, List<ClipResult> selected)
    {
        Directory.CreateDirectory(Path.Combine(Evidence, "captures"));
        var camera = Stage();
        const int w=480, h=360, rows=6, cols=3;
        var warm = Capture(camera); Object.DestroyImmediate(warm);
        for (int start=0; start<selected.Count; start+=rows)
        {
            int actualRows=Mathf.Min(rows,selected.Count-start);
            var sheet = new Texture2D(w*cols,h*actualRows,TextureFormat.RGB24,false);
            var sheetName = "captures/batch-"+(start/rows+1).ToString("D2")+".png";
            var labels = new List<string>();
            for (int row=0; row<rows && start+row<selected.Count; row++)
            {
                var result = selected[start+row];
                var c = request.clips.Single(x=>x.id==result.id);
                var clip = Load(c);
                var bodies = request.targets.Select((t,i) => Body(t,new Vector3(i==0?-.6f:.6f,0,0),
                    i==0?new Color(.25f,.55f,.7f):new Color(.8f,.48f,.3f))).ToArray();
                var playables = new AnimationClipPlayable[bodies.Length];
                var graphs = bodies.Select((b,i)=>Graph(b.GetComponent<Animator>(),clip,out playables[i])).ToArray();
                float previousTime=0;
                for(int col=0; col<cols; col++)
                {
                    float targetTime=clip.length * new[]{.1f,.45f,.8f}[col];
                    for(int i=0;i<graphs.Length;i++) graphs[i].Evaluate(targetTime-previousTime);
                    previousTime=targetTime;
                    var shot=Capture(camera,w,h);
                    sheet.SetPixels(col*w,(actualRows-1-row)*h,w,h,shot.GetPixels());
                    Object.DestroyImmediate(shot);
                }
                foreach(var g in graphs) g.Destroy();
                foreach(var b in bodies) DisposeBody(b);
                labels.Add((row+1)+": "+c.id+" | 10%, 45%, 80%; male blue, female orange");
                result.captures=new[]{sheetName};
            }
            sheet.Apply();
            File.WriteAllBytes(Path.Combine(Evidence,sheetName),sheet.EncodeToPNG());
            File.WriteAllLines(Path.Combine(Evidence,sheetName.Replace(".png",".txt")),labels);
            Object.DestroyImmediate(sheet);
        }
        var temporalIds = new[]{"ual1:walk_loop","ual1:jog_fwd_loop","ual1:idle_talking_loop",
            "ual2:idle_foldarms_loop","ual1:interact","ual2:surprise","ual2:yes","ual1:turn90_l"};
        foreach(var id in temporalIds)
        {
            var c=request.clips.Single(x=>x.id==id);
            var clip=Load(c);
            var bodies=request.targets.Select((t,i)=>Body(t,new Vector3(i==0?-.6f:.6f,0,0),
                i==0?new Color(.25f,.55f,.7f):new Color(.8f,.48f,.3f))).ToArray();
            var graphs=bodies.Select(b=>Graph(b.GetComponent<Animator>(),clip,out _)).ToArray();
            var sheet=new Texture2D(4*360,3*270,TextureFormat.RGB24,false);
            var frameHashes=new List<string>();
            for(int frame=0;frame<12;frame++)
            {
                foreach(var graph in graphs) graph.Evaluate(frame==0?.001f:(clip.length-.002f)/11);
                var shot=Capture(camera,360,270);
                using(var hash=SHA256.Create()) frameHashes.Add(Convert.ToBase64String(hash.ComputeHash(shot.EncodeToPNG())));
                sheet.SetPixels((frame%4)*360,(2-frame/4)*270,360,270,shot.GetPixels());
                Object.DestroyImmediate(shot);
            }
            foreach(var graph in graphs) graph.Destroy();
            foreach(var body in bodies) DisposeBody(body);
            if(frameHashes.Distinct().Count()<3) throw new InvalidOperationException("Frozen temporal capture: "+id);
            sheet.Apply();
            var path="captures/sequence-"+id.Replace(':','-')+".png";
            File.WriteAllBytes(Path.Combine(Evidence,path),sheet.EncodeToPNG());
            var result=selected.Single(x=>x.id==id);
            result.captures=result.captures.Concat(new[]{path}).ToArray();
            Object.DestroyImmediate(sheet);
        }
    }
    [MenuItem("Tools/JuegoDef/Animation/Run Batch in Play Mode")]
    public static void Run()
    {
        if (EditorApplication.isPlaying) throw new InvalidOperationException("Run from Edit Mode");
        if (!Application.isBatchMode && !EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
        ApplyPresets();
        EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
        SessionState.SetBool("JDAnimFactoryPending",true);
        EditorApplication.EnterPlaymode();
    }
    [InitializeOnLoadMethod] static void Resume()
    {
        EditorApplication.update += () =>
        {
            // An unrelated Editor delayCall exception must not silently lose the batch callback.
            if(EditorApplication.isPlaying && !EditorApplication.isCompiling && SessionState.GetBool("JDAnimFactoryPending",false))
            {
                SessionState.SetBool("JDAnimFactoryPending",false);
                MeasureBatch();
            }
        };
    }
    static void MeasureBatch()
    {
        try
        {
            Debug.Log("JD_ANIM_RUNTIME_BEGIN");
            var req=ReadRequest(); CheckSources(req);
            var report=new Report { unityVersion=Application.unityVersion, playMode=Application.isPlaying,
                requestSha256=Hash(Path.Combine(Evidence,"batch_request.json")),
                factorySha256=Hash("Assets/JuegoDef/Editor/Animation/AnimationFactory.cs") };
            var loaded=req.clips.Select(c=>c.path).Distinct().ToDictionary(p=>p,p=>AssetDatabase.LoadAllAssetsAtPath(p)
                .OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__preview__")).ToDictionary(c=>Clean(c.name)));
            foreach(var path in req.clips.Select(c=>c.path).Concat(req.targets.Select(b=>b.path)).Distinct())
                report.imports.Add(new ImportIdentity{path=path,metaSha256=Hash(path+".meta")});
            foreach(var c in req.clips)
            {
                var clip=loaded[c.path][c.name];
                AssetDatabase.TryGetGUIDAndLocalFileIdentifier(clip,out string guid,out long localId);
                var r=new ClipResult { id=c.id,sourceSha256=c.sourceSha256,localId=localId.ToString(),
                    humanMotion=clip.humanMotion,loop=clip.isLooping,length=clip.length,frameRate=clip.frameRate,
                    issues=CheckClip(clip,c),sampled=c.sample,captures=Array.Empty<string>() };
                if(c.sample)
                    foreach(var target in req.targets) r.targets.Add(Measure(target,c,clip));
                report.clips.Add(r);
                if(c.sample) Debug.Log("JD_ANIM_MEASURED " + c.id);
            }
            var bad=new GameObject("incompatible target without avatar").AddComponent<Animator>();
            var diagnosis=CheckTarget(bad);
            report.negativeCases.Add(new NegativeCase{name="missing-avatar",detected=diagnosis.Contains("invalid humanoid avatar"),diagnosis=string.Join("; ",diagnosis)});
            Object.DestroyImmediate(bad.gameObject);
            var pose=report.clips.Single(c=>c.id=="ual1:a_tpose");
            report.negativeCases.Add(new NegativeCase{name="real-corpus-reference-pose",detected=pose.issues.Count>0 && pose.targets.All(t=>t.motionRange<.001f),diagnosis=string.Join("; ",pose.issues)});
            var idle=req.clips.Single(c=>c.id=="ual1:idle_loop");
            var wrongLoop=new ClipInput{loop=false};
            report.negativeCases.Add(new NegativeCase{name="wrong-loop-policy",detected=CheckClip(Load(idle),wrongLoop).Contains("loop policy mismatch"),diagnosis="The same clip is refused under a contradictory loop request."});
            ContactSheets(req,report.clips.Where(c=>c.sampled).ToList());
            File.WriteAllText(Path.Combine(Evidence,"runtime_report.json"),JsonUtility.ToJson(report,true)+"\n");
            Debug.Log("JD_ANIM_RUNTIME_REPORT clips="+report.clips.Count+" sampled="+report.clips.Count(c=>c.sampled)+" playMode="+report.playMode);
            if(Application.isBatchMode) EditorApplication.Exit(0); else EditorApplication.ExitPlaymode();
        }
        catch(Exception e) { Debug.LogException(e); if(Application.isBatchMode) EditorApplication.Exit(1); else EditorApplication.ExitPlaymode(); }
    }
}

using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using JuegoDef.Characters.Editor;

// Ephemeral Unity CLI entry points; this file deliberately lives outside Assets.
public static class CharNaturalismRun
{
    public static object Before() => Capture("before");
    public static object After() => Capture("after");
    public static object Baseline() => Capture("before", false, "Assets/JuegoDef/Derived/CHAR_BEFORE/Prefabs");
    public static object Pilot() => Capture("pilot", true);
    public static object FitPilot()
    {
        int count=0;
        foreach(var pose in new[]{"idle","walk","talk"})
        foreach(float yaw in new[]{0f,90f,180f})
        foreach(float phase in new[]{0f,.25f,.5f,.75f})
        {
            CharReview.Render(new CharReview.Req{ids=new[]{"dock-worker","student","waiter-veteran","mechanic"},
                pose=pose,phase=phase,yaw=yaw,camDistance=4.5f,camHeight=1.4f,lookHeight=1.2f,fov=36,
                width=2400,height=1100,spacing=.8f,ao="off",output="fitpilot_"+pose+"_"+yaw+"_"+phase+".png"});
            count++;
        }
        return new{count};
    }
    public static object Build() { CharPosture.BuildAll(); CharFactory.Build(); return "CHAR_NATURALISM_BUILT"; }
    public static object Preview() { CharFactory.Scene(); return "CHAR_PREVIEW_READY"; }
    public static object Validate() => CharReview.PoseSweep();
    public static object Runtime() { CharValidation.CaptureAll(); CharValidation.Groups(); return "CHAR_PLAY_AND_GROUPS_CAPTURED"; }
    public static object Rebuild() { CharValidation.Rebuild(); return "CHAR_REBUILD_VERIFIED"; }
    public static object Verify() { CharValidation.Verify(); return "CHAR_CURRENT_EVIDENCE_VERIFIED"; }
    public static object FinalEdit() { After(); Stats(); CharReview.PoseSweep(); CharFactory.Scene(); return "CHAR_FINAL_PORTRAITS_STATS_POSES_AND_SCENE_READY"; }
    public static object Stats()
    {
        var rows=CharFactory.Read().recipes.Select(r=>{
            var p=AssetDatabase.LoadAssetAtPath<GameObject>(CharFactory.Root+"/Prefabs/"+r.id+".prefab");
            var renderers=p.GetComponentsInChildren<SkinnedMeshRenderer>();
            return new {r.id,r.headForm,r.hairStyle,r.garmentPattern,skinnedRenderers=renderers.Length,
                vertices=renderers.Sum(s=>s.sharedMesh.vertexCount),triangles=renderers.Sum(s=>s.sharedMesh.triangles.Length/3),
                materialSlots=renderers.Sum(s=>s.sharedMaterials.Length),validAvatar=p.GetComponent<Animator>().avatar.isValid,
                missingBones=renderers.Sum(s=>s.bones.Count(b=>b==null))};
        }).ToArray();
        var text=Newtonsoft.Json.JsonConvert.SerializeObject(new {unity=Application.unityVersion,variants=rows.Length,
            note="Geometry/material observations; this is not an FPS or population-scale performance claim.",rows},Newtonsoft.Json.Formatting.Indented);
        File.WriteAllText(Path.Combine(CharValidation.Evidence,"naturalism_2026-10-01/GEOMETRY_OBSERVATIONS.json"),text);
        return text;
    }

    static object Capture(string prefix, bool pilot = false, string root = null)
    {
        var recipes = CharFactory.Read().recipes;
        string[] pilots = { "market-worker", "dock-worker", "older-resident", "elder-woman", "student", "waiter-veteran" };
        int count = 0;
        foreach (var r in recipes.Where(r => !pilot || pilots.Contains(r.id)))
        {
            foreach (float yaw in new[] { 0f, 45f, 90f })
            {
                CharReview.Render(new CharReview.Req { prefabRoot=root, ids = new[] { r.id }, pose = "civ:ual1:idle_loop", phase = .23f,
                    camDistance = 1.65f, camHeight = r.height - .14f, lookHeight = r.height - .17f, fov = 30,
                    width = 600, height = 700, ao = "off", yaw = yaw, bareIdentity = yaw != 0,
                    output = prefix + "_face_" + r.id + "_" + yaw.ToString("0") + ".png" });
                count++;
            }
            CharReview.Render(new CharReview.Req { prefabRoot=root, ids = new[] { r.id }, pose = "civ:ual1:idle_loop", phase = .23f,
                camDistance = 1.65f, camHeight = r.height - .14f, lookHeight = r.height - .17f, fov = 30,
                width = 600, height = 700, ao = "off", bareIdentity = true, output = prefix + "_bare_" + r.id + ".png" });
            count++;
        }
        if (!pilot)
            for (int j = 0; j < 3; j++)
                foreach (bool silhouette in new[] { false, true })
                {
                    CharReview.Render(new CharReview.Req { prefabRoot=root, ids = recipes.Skip(j * 5).Take(5).Select(r => r.id).ToArray(),
                        pose = "idle", useRecipePoses = !silhouette, stage = "street", camDistance = 6.2f,
                        camHeight = 1.6f, lookHeight = 1f, fov = 48, width = 1800, height = 1050, spacing = .9f,
                        ao = "off", silhouette = silhouette, output = prefix + "_group_" + j + (silhouette ? "_silhouette" : "") + ".png" });
                    count++;
                }
        return new { prefix, captures = count };
    }
}

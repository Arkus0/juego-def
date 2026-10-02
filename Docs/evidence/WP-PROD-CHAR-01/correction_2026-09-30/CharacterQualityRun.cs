using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using JuegoDef.Characters.Editor;
public static class CharacterQualityRun {
 public static object Captures(string phase) {
  var manifest=CharFactory.Read();
  foreach(var r in manifest.recipes) {
   float h=r.height;
   CharReview.Render(new CharReview.Req { ids=new[]{r.id},pose="civ:ual1:idle_loop",phase=.23f,stage="plain",camDistance=1.35f,camHeight=h-.14f,lookHeight=h-.17f,fov=28,width=560,height=650,ao="off",output=phase+"_face_"+r.id+".png" });
   CharReview.Render(new CharReview.Req { ids=new[]{r.id},pose="civ:ual1:idle_loop",phase=.23f,stage="plain",camDistance=1.35f,camHeight=h-.14f,lookHeight=h-.17f,fov=28,width=560,height=650,ao="off",bareIdentity=true,output=phase+"_bare_"+r.id+".png" });
  }
  var ids=manifest.recipes.Select(r=>r.id).ToArray();
  for(int j=0;j<3;j++) {
   var group=ids.Skip(j*5).Take(5).ToArray();
   CharReview.Render(new CharReview.Req{ids=group,pose="idle",useRecipePoses=true,stage="street",camDistance=6.2f,camHeight=1.6f,lookHeight=1.0f,width=1800,height=1050,spacing=.9f,fov=48,ao="off",output=phase+"_group_"+j+".png"});
   CharReview.Render(new CharReview.Req{ids=group,pose="idle",stage="plain",camDistance=6.2f,camHeight=1.6f,lookHeight=1.0f,width=1800,height=1050,spacing=.9f,fov=48,ao="off",silhouette=true,output=phase+"_silhouette_"+j+".png"});
  }
  return new {captures=36,phase};
 }
 public static object Build() { CharPosture.BuildAll();CharFactory.Build();return "CHAR_BUILD_DONE"; }
 public static object Validate() { return CharReview.PoseSweep(); }
 public static object Rebuild() { CharValidation.Rebuild();return "CHAR_REBUILD_IDENTICAL"; }
 public static object Runtime() { CharValidation.CaptureAll();CharValidation.Groups();return "CHAR_RUNTIME_AND_GROUPS_DONE"; }
 public static object Safety() {
  int protectedCurves=0, samples=0;var problems=new System.Collections.Generic.List<string>();
  var scene=UnityEditor.SceneManagement.EditorSceneManager.NewPreviewScene();
  try {
   foreach(var r in CharFactory.Read().recipes) {
    var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(CharFactory.Root+"/Prefabs/"+r.id+".prefab");
    var go=(GameObject)PrefabUtility.InstantiatePrefab(prefab,scene);var a=go.GetComponent<Animator>();
    if(a.avatar==null||!a.avatar.isValid||!a.avatar.isHuman)problems.Add(r.id+" avatar");
    foreach(var motion in new[]{"Idle","Walk","Talking"}) {
     var derived=CharPosture.LoadFor(r,motion);var source=CharPosture.Load(motion=="Idle"?r.pose:motion=="Walk"?"ual1:walk_loop":"ual1:idle_talking_loop");
     if(Mathf.Abs(derived.length-source.length)>1e-4f||derived.isLooping!=source.isLooping)problems.Add(r.id+" clip boundary "+motion);
     foreach(var b in AnimationUtility.GetCurveBindings(source).Where(b=>b.propertyName.StartsWith("Root")||b.propertyName.Contains("Leg")||b.propertyName.Contains("Foot"))) {
      var before=AnimationUtility.GetEditorCurve(source,b);var after=AnimationUtility.GetEditorCurve(derived,b);protectedCurves++;
      if(after==null){problems.Add(r.id+" missing protected curve "+b.propertyName);continue;}
      for(int i=0;i<64;i++)if(Mathf.Abs(before.Evaluate(source.length*i/63)-after.Evaluate(source.length*i/63))>1e-5f){problems.Add(r.id+" changed protected curve "+b.propertyName);break;}
     }
     for(int i=0;i<24;i++) {
      a.Rebind();var g=JDAnimationFactory.Graph(a,derived,out var playable);
      UnityEngine.Playables.PlayableExtensions.SetTime(playable,derived.length*i/24);g.Evaluate(0);
      try {
       Bounds bounds=default;bool first=true;bool finite=true;
       foreach(var skin in go.GetComponentsInChildren<SkinnedMeshRenderer>()) {
        if(skin.bones.Any(b=>b==null)||skin.sharedMaterials.Any(m=>m==null||m.shader==null||!m.shader.isSupported))problems.Add(r.id+" broken binding");
        var mesh=new Mesh();skin.BakeMesh(mesh);
        foreach(var vertex in mesh.vertices) {
         var v=skin.transform.TransformPoint(vertex);
         finite &= !(float.IsNaN(v.x)||float.IsNaN(v.y)||float.IsNaN(v.z)||float.IsInfinity(v.x)||float.IsInfinity(v.y)||float.IsInfinity(v.z));
         if(first){bounds=new Bounds(v,Vector3.zero);first=false;}else bounds.Encapsulate(v);
        }
        UnityEngine.Object.DestroyImmediate(mesh);
       }
       if(!finite||bounds.min.y<-.10f||bounds.min.y>.15f||bounds.size.y<1.35f||bounds.size.y>2.15f||bounds.size.x>1.3f)problems.Add(r.id+" posed bounds "+motion+"/"+i);
       samples++;
      } finally {g.Destroy();}
     }
    }
    UnityEngine.Object.DestroyImmediate(go);
   }
   var errors=ShaderUtil.GetShaderMessages(Shader.Find("JuegoDef/Characters/Skin")).Where(m=>m.severity.ToString()=="Error").ToArray();
   foreach(var e in errors)problems.Add("Skin shader: "+e.message);
  } finally {UnityEditor.SceneManagement.EditorSceneManager.ClosePreviewScene(scene);}
  var report=new SafetyReport{samples=samples,protectedCurves=protectedCurves,problems=problems.Distinct().ToArray(),unity=Application.unityVersion};
  File.WriteAllText("C:/Juego Def Auditorias/CHAR_2026-09-30/safety.json",JsonUtility.ToJson(report,true));
  if(report.problems.Length>0)throw new InvalidOperationException(string.Join("; ",report.problems));
  return report;
 }
 [Serializable] public class SafetyReport {public int samples,protectedCurves;public string unity;public string[] problems;}
 public static object Apron() {
  foreach(float phase in new[]{0f,.25f,.5f,.75f})
   CharReview.Render(new CharReview.Req{ids=new[]{"waiter-veteran","market-worker","fishmonger"},pose="walk",phase=phase,stage="plain",camDistance=4f,camHeight=1.4f,lookHeight=.95f,fov=44,width=1600,height=1050,spacing=.9f,ao="off",output="apron_"+phase.ToString("0.00",System.Globalization.CultureInfo.InvariantCulture)+".png"});
  return "CHAR_APRONS_CAPTURED";
 }
 public static object Preview() { CharFactory.Scene();return "CHAR_PREVIEW_DONE"; }
}


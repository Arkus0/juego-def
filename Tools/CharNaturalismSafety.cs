using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using JuegoDef.Characters.Editor;
public static class CharNaturalismSafety {
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
  File.WriteAllText(Path.Combine(CharValidation.Evidence,"naturalism_2026-10-01/SAFETY.json"),JsonUtility.ToJson(report,true));
  if(report.problems.Length>0)throw new InvalidOperationException(string.Join("; ",report.problems));
  return report;
 }
 [Serializable] public class SafetyReport {public int samples,protectedCurves;public string unity;public string[] problems;}
}

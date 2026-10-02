using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;
using UnityEngine.Rendering;
using UnityEngine.Playables;
using UnityEngine.Animations;
using System.Collections.Generic;
using JuegoDef.Characters.Editor;

// Run only in the isolated ENV01Review snapshot. Never saves the source scene.
public static class CharEnvRun
{
    static void Guard()
    {
        if(!Application.dataPath.Replace('\\','/').Contains("/CHAR_NATURALISM_2026-10-01/ENV01Review/"))
            throw new InvalidOperationException("ENV calibration requires the isolated review snapshot");
    }
    public static object Inspect()
    {
        Guard();
        if(!EditorApplication.isPlaying)EditorSceneManager.OpenScene("Assets/JuegoDef/Scenes/ENV/ENV01_AUTHORED.unity");
        var s=SceneManager.GetActiveScene();
        return Newtonsoft.Json.JsonConvert.SerializeObject(new {scene=s.path,play=EditorApplication.isPlaying,
            roots=s.GetRootGameObjects().Select(g=>new {g.name,p=V(g.transform.position),components=g.GetComponents<Component>().Where(c=>c!=null).Select(c=>c.GetType().FullName).ToArray()}).ToArray(),
            cameras=UnityEngine.Object.FindObjectsByType<Camera>(FindObjectsSortMode.None).Select(c=>new {c.name,c.fieldOfView,c.nearClipPlane,c.farClipPlane,p=V(c.transform.position),r=V(c.transform.eulerAngles)}).ToArray(),
            lights=UnityEngine.Object.FindObjectsByType<Light>(FindObjectsSortMode.None).Select(l=>new {l.name,l.type,color=new[]{l.color.r,l.color.g,l.color.b},l.intensity}).ToArray(),
            renderer=AssetDatabase.GetAssetPath(GraphicsSettings.currentRenderPipeline)});
    }
    static float[] V(Vector3 v)=>new[]{v.x,v.y,v.z};
    static readonly string[] Stations={"plaza","arco","workshop"};
    static readonly Vector3[] Feet={new Vector3(110,.2f,178),new Vector3(122,3.081623f,129.25f),new Vector3(55,5.595333f,84)};
    static readonly Vector3[] Eyes={new Vector3(113.012108f,2.61751938f,178.053772f),new Vector3(119.0292f,5.499142f,128.75f),new Vector3(57.9708061f,8.012853f,84.5f)};
    static readonly float[] Directions={-1,1,-1};
    public static object Refresh()
    {
        Guard();AssetDatabase.Refresh(ImportAssetOptions.ForceUpdate);return "ENV_CHAR_IMPORT_REFRESHED";
    }
    public static object Prepare()
    {
        Guard();if(EditorApplication.isPlaying)throw new InvalidOperationException("Stop Play before fixture creation");
        var s=EditorSceneManager.OpenScene("Assets/JuegoDef/Scenes/ENV/ENV01_AUTHORED.unity");
        var root=new GameObject("NPC_CALIBRATION_ONLY");
        var recipes=CharFactory.Read().recipes;Physics.SyncTransforms();
        for(int j=0;j<3;j++)
        {
            var group=new GameObject(Stations[j]);group.transform.parent=root.transform;
            var placed=new List<Vector3>();
            for(int i=0;i<5;i++)
            {
                var r=recipes[j*5+i];var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(CharFactory.Root+"/Prefabs/"+r.id+".prefab");
                var go=(GameObject)PrefabUtility.InstantiatePrefab(prefab,s);go.name=r.id;go.transform.parent=group.transform;
                var pos=Feet[j]+new Vector3(Directions[j]*1.2f,0,(i-2)*.75f);
                bool found=false;
                foreach(var dx in new[]{0f,-.4f,.4f,-.8f,.8f,-1.2f,1.2f})
                {
                    foreach(var dz in new[]{0f,-.3f,.3f,-.6f,.6f,-1f,1f})
                    {
                        var candidate=pos+new Vector3(dx,0,dz);
                        var hits=Physics.RaycastAll(candidate+Vector3.up*1.5f,Vector3.down,5).OrderBy(h=>h.distance);
                        foreach(var h in hits)
                        {
                            if(h.normal.y<.7f||Mathf.Abs(h.point.y-Feet[j].y)>.6f)continue;
                            candidate.y=h.point.y+.015f;
                            if(placed.Any(p=>Vector3.Distance(p,candidate)<.6f))continue;
                            if(Physics.CheckCapsule(candidate+Vector3.up*.28f,candidate+Vector3.up*(r.height-.22f),.21f,~0,QueryTriggerInteraction.Ignore))continue;
                            pos=candidate;found=true;break;
                        }
                        if(found)break;
                    }
                    if(found)break;
                }
                if(!found)throw new InvalidOperationException("No clear ENV paving found for "+r.id);
                placed.Add(pos);
                go.transform.SetPositionAndRotation(pos,Quaternion.LookRotation(new Vector3(-Directions[j],0,0)));
            }
        }
        Directory.CreateDirectory("Assets/JuegoDef/Scenes/CHAR");
        EditorSceneManager.SaveScene(s,"Assets/JuegoDef/Scenes/CHAR/ENV01CharacterReview.unity");
        return "ENV01_REVIEW_FIXTURE_READY_15";
    }
    public static object Capture()
    {
        Guard();if(!EditorApplication.isPlaying)throw new InvalidOperationException("ENV captures require Play Mode");
        var camera=Camera.main;if(camera==null)throw new InvalidOperationException("Missing actual ENV player camera");
        var graphs=new List<PlayableGraph>();var root=GameObject.Find("NPC_CALIBRATION_ONLY");
        var recipes=CharFactory.Read().recipes;var rows=new List<object>();
        var target=Path.Combine(CharFactory.Repo,"Captures/ENV01Characters");Directory.CreateDirectory(target);
        var originalPosition=camera.transform.position;var originalRotation=camera.transform.rotation;
        try
        {
            foreach(var r in recipes)
            {
                var go=GameObject.Find(r.id);var animator=go.GetComponent<Animator>();animator.Rebind();animator.Update(0);
                var graph=JDAnimationFactory.Graph(animator,CharPosture.LoadFor(r,"Idle"),out var playable);
                playable.SetTime(.23*CharPosture.LoadFor(r,"Idle").length);graph.Evaluate(0);graphs.Add(graph);
            }
            var player=UnityEngine.Object.FindObjectsByType<MonoBehaviour>(FindObjectsSortMode.None).FirstOrDefault(m=>m.GetType().FullName=="GameCreator.Runtime.Characters.Character" && m.name.ToLowerInvariant().Contains("player"));
            for(int j=0;j<3;j++)
            {
                if(player!=null)player.transform.position=Feet[j];
                camera.transform.position=Eyes[j];camera.transform.LookAt(Feet[j]+Vector3.up*1.25f+new Vector3(Directions[j],0,0));
                var file=Stations[j]+"_player_55fov.png";Save(camera,target,file,1920,1080);
                rows.Add(new {file,station=Stations[j],mode="actual ENV player camera; checkpoint boom",fov=camera.fieldOfView,position=V(camera.transform.position),rotation=V(camera.transform.eulerAngles),ids=recipes.Skip(j*5).Take(5).Select(r=>r.id).ToArray()});
                foreach(var r in recipes.Skip(j*5).Take(5))
                {
                    var go=GameObject.Find(r.id);var look=go.transform.position+Vector3.up*(r.height-.14f);
                    camera.transform.position=look+new Vector3(-Directions[j]*1.7f,.04f,0);camera.transform.LookAt(look);
                    file=Stations[j]+"_conversation_"+r.id+".png";Save(camera,target,file,900,1000);
                    rows.Add(new {file,station=Stations[j],mode="conversation; same camera and scene lighting",fov=camera.fieldOfView,position=V(camera.transform.position),rotation=V(camera.transform.eulerAngles),ids=new[]{r.id}});
                }
            }
            var text=Newtonsoft.Json.JsonConvert.SerializeObject(new {unity=Application.unityVersion,playMode=true,scene=SceneManager.GetActiveScene().path,renderer=AssetDatabase.GetAssetPath(GraphicsSettings.currentRenderPipeline),captures=rows},Newtonsoft.Json.Formatting.Indented);
            File.WriteAllText(Path.Combine(target,"ENV_CAPTURES.json"),text);return text;
        }
        finally {foreach(var g in graphs)if(g.IsValid())g.Destroy();camera.transform.SetPositionAndRotation(originalPosition,originalRotation);}
    }
    public static object Attention()
    {
        Guard();if(!EditorApplication.isPlaying)throw new InvalidOperationException("Attention needs actual ENV Play Mode");
        var player=GameCreator.Runtime.Common.ShortcutPlayer.Instance;
        if(player==null)throw new InvalidOperationException("Actual ENV canonical GC2 player is absent");
        var saved=player.transform.position;var rows=new List<object>();
        try
        {
            foreach(var recipe in CharFactory.Read().recipes)
            {
                var root=GameObject.Find(recipe.id);var presentation=root.GetComponent<JuegoDef.Characters.NpcPresentation>();
                if(presentation.attentionTarget!=null||!presentation.Ready)throw new InvalidOperationException("Not using canonical attention: "+recipe.id);
                player.transform.position=root.transform.position+root.transform.forward*2-root.transform.right*.8f;
                for(int j=0;j<120;j++)presentation.Sample(100+j/60f,1/60f);
                float left=presentation.GazeYaw;
                player.transform.position=root.transform.position+root.transform.forward*2+root.transform.right*.8f;
                for(int j=0;j<120;j++)presentation.Sample(103+j/60f,1/60f);
                float right=presentation.GazeYaw;
                if(left> -3||right<3)throw new InvalidOperationException("Canonical gaze direction: "+recipe.id);
                rows.Add(new {recipe.id,left,right,usesOptionalTarget=false});
            }
            var report=new {playMode=true,canonicalPlayer=player.name,variants=rows.Count,rows,
                note="The existing GC2 ShortcutPlayer authority; temporary Play Mode player placement is restored; no new player or movement authority."};
            var target=Path.Combine(CharFactory.Repo,"Captures/ENV01Characters");Directory.CreateDirectory(target);
            File.WriteAllText(Path.Combine(target,"ENV_ATTENTION.json"),Newtonsoft.Json.JsonConvert.SerializeObject(report,Newtonsoft.Json.Formatting.Indented));
            return report;
        }
        finally {player.transform.position=saved;}
    }
    static void Save(Camera camera,string target,string file,int width,int height)
    {
        var scene=SceneManager.GetActiveScene();
        var skins=scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<SkinnedMeshRenderer>()).Where(s=>s.enabled&&s.gameObject.activeInHierarchy).ToArray();
        var snapshots=new List<GameObject>();var meshes=new List<Mesh>();
        bool oldAsync=ShaderUtil.allowAsyncCompilation;ShaderUtil.allowAsyncCompilation=false;
        try
        {
            foreach(var skin in skins)
            {
                var mesh=new Mesh();skin.BakeMesh(mesh);meshes.Add(mesh);
                var go=new GameObject("Baked pose capture");go.transform.SetPositionAndRotation(skin.transform.position,skin.transform.rotation);go.transform.localScale=skin.transform.lossyScale;
                go.AddComponent<MeshFilter>().sharedMesh=mesh;go.AddComponent<MeshRenderer>().sharedMaterials=skin.sharedMaterials;snapshots.Add(go);skin.enabled=false;
            }
            var warm=JDAnimationFactory.Capture(camera,width,height);UnityEngine.Object.DestroyImmediate(warm);
            var image=JDAnimationFactory.Capture(camera,width,height);File.WriteAllBytes(Path.Combine(target,file),image.EncodeToPNG());UnityEngine.Object.DestroyImmediate(image);
        }
        finally {ShaderUtil.allowAsyncCompilation=oldAsync;foreach(var s in skins)s.enabled=true;foreach(var o in snapshots)UnityEngine.Object.DestroyImmediate(o);foreach(var m in meshes)UnityEngine.Object.DestroyImmediate(m);}
    }
}

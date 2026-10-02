using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEngine.Playables;
using UnityEngine.Animations;

namespace JuegoDef.Characters.Editor
{
    public static class CharValidation
    {
        [Serializable] public class Sample { public string id,motion;public float phase,minY,height,width;public int vertices;public bool finite; }
        [Serializable] public class Identity { public string path,sha256; }
        [Serializable] public class Report { public string unity; public bool playMode;public int variants;public List<string> problems=new List<string>(); public List<Sample> samples=new List<Sample>(); public List<Identity> inputs=new List<Identity>();public string[] motions; }
        public static string Evidence => Path.Combine(CharFactory.Repo,"Docs/evidence/WP-PROD-CHAR-01");
        static List<Identity> Inputs()
        {
            var repo=CharFactory.Repo;
            var files=new List<string>();
            foreach(var dir in new[]{CharFactory.Root,"Assets/JuegoDef/Editor/Char","Assets/JuegoDef/Characters","Assets/JuegoDef/Scenes/CHAR"})
                files.AddRange(Directory.GetFiles(dir,"*",SearchOption.AllDirectories).Select(Path.GetFullPath));
            files.AddRange(Directory.GetFiles(Path.Combine(repo,"Tools"),"char_*.py"));
            files.AddRange(Directory.GetFiles(Path.Combine(repo,"Tools"),"Char*.cs"));
            files.Add(Path.Combine(repo,"Tools/vendor/chilyer/body_topo.py"));
            files.Add(Path.Combine(repo,"Tools/vendor/chilyer/LICENSE"));
            files.AddRange(Directory.GetFiles(Path.Combine(repo,"Docs/asset_catalog"),"char_*.json"));
            foreach(var dir in new[]{"Art/Characters/HumanHeads","Art/Characters/HumanSources"})
                files.AddRange(Directory.GetFiles(Path.Combine(repo,dir),"*",SearchOption.AllDirectories));
            files.Add(Path.Combine(repo,"Tools/asset_catalog.py"));
            files.Add(Path.Combine(repo,"Docs/evidence/WP-PROD-ASSET-00/catalog.json"));
            files.Add(Path.Combine(repo,"Docs/evidence/WP-PROD-ANIM-01/batch_request.json"));
            files.Add(Path.Combine(Evidence,"build_inventory.json"));
            files.Add(Path.GetFullPath("Assets/JuegoDef/Editor/Animation/AnimationFactory.cs"));
            foreach(var path in new[]{"Packages/manifest.json","Packages/packages-lock.json","ProjectSettings/ProjectVersion.txt","ProjectSettings/GraphicsSettings.asset","ProjectSettings/QualitySettings.asset","ProjectSettings/ProjectSettings.asset"})
                files.Add(Path.GetFullPath(path));
            files.AddRange(Directory.GetFiles("Assets/JuegoDef/Rendering","*",SearchOption.AllDirectories).Select(Path.GetFullPath));
            foreach(var c in JDAnimationFactory.ReadRequest().clips.Where(c=>CharPosture.Has(c.id)))
            {files.Add(Path.GetFullPath(c.path));files.Add(Path.GetFullPath(c.path+".meta"));}
            foreach(var guid in AssetDatabase.FindAssets("t:Material",new[]{CharFactory.Root+"/Materials"}))
            {
                var mat=AssetDatabase.LoadAssetAtPath<Material>(AssetDatabase.GUIDToAssetPath(guid));
                var tex=mat.GetTexture("_BaseMap");
                if(tex==null&&(mat.name=="eyes"||mat.name.StartsWith("skin_")))throw new InvalidOperationException("Missing source texture "+mat.name);
                if(tex!=null){var path=AssetDatabase.GetAssetPath(tex);files.Add(Path.GetFullPath(path));files.Add(Path.GetFullPath(path+".meta"));}
                var normal=mat.GetTexture("_BumpMap");
                if(normal!=null){var path=AssetDatabase.GetAssetPath(normal);files.Add(Path.GetFullPath(path));files.Add(Path.GetFullPath(path+".meta"));}
            }
            return files.Distinct().OrderBy(p=>p,StringComparer.Ordinal).Select(p=>new Identity{path=Path.GetRelativePath(repo,p).Replace('\\','/'),sha256=JDAnimationFactory.Hash(p)}).ToList();
        }
        public static List<Identity> CurrentInputs()=>Inputs();
        [MenuItem("Tools/JuegoDef/Characters/Verify retained evidence identity")]
        public static void Verify()
        {
            var report=JsonUtility.FromJson<Report>(File.ReadAllText(Path.Combine(Evidence,"unity_runtime_validation.json")));
            var ids=CharFactory.Read().recipes.Select(r=>r.id).ToArray();
            if(!report.playMode||report.problems.Count!=0||report.variants!=ids.Length||report.samples.Count!=ids.Length*12)
                throw new InvalidOperationException("Incomplete or failing CHAR runtime evidence");
            foreach(var id in ids)foreach(var motion in new[]{"Idle","Walk","Talking"})foreach(float phase in new[]{0f,.25f,.5f,.75f})
                if(report.samples.Count(s=>s.id==id&&s.motion==motion&&s.phase==phase&&s.finite)!=1)throw new InvalidOperationException("Missing/duplicate CHAR pose");
            var current=Inputs();
            if(current.Count!=report.inputs.Count||current.Any(a=>!report.inputs.Any(b=>a.path==b.path&&a.sha256==b.sha256)))
                throw new InvalidOperationException("Stale CHAR runtime evidence: recapture after changing inputs");
            Debug.Log("CHAR_EVIDENCE_IDENTITY_VALID "+current.Count+" inputs");
        }
        [MenuItem("Tools/JuegoDef/Characters/Verify prefab rebuild")]
        public static void Rebuild()
        {
            if(EditorApplication.isPlaying)throw new InvalidOperationException("Stop Play Mode before rebuild check");
            var before=Inputs();CharFactory.Build();var after=Inputs();
            if(before.Count!=after.Count||after.Any(a=>!before.Any(b=>a.path==b.path&&a.sha256==b.sha256)))
                throw new InvalidOperationException("CHAR rebuild changed serialized inputs: "+string.Join(", ",after.Where(a=>!before.Any(b=>a.path==b.path&&a.sha256==b.sha256)).Select(a=>a.path)));
            File.WriteAllText(Path.Combine(Evidence,"unity_rebuild_validation.json"),JsonUtility.ToJson(new Report{unity=Application.unityVersion,variants=CharFactory.Read().recipes.Length,inputs=after},true));
            Debug.Log("CHAR_REBUILD_IDENTICAL "+after.Count+" inputs including prefab/model GUIDs and references");
        }

        [MenuItem("Tools/JuegoDef/Characters/Capture and validate runtime")]
        public static void CaptureAll() => Capture(false);
        public static void Quick() => Capture(true);
        static void Capture(bool quick)
        {
            if(!EditorApplication.isPlaying)throw new InvalidOperationException("Runtime fit validation requires Play Mode");
            var recipes=CharFactory.Read().recipes;
            var roots=recipes.Select(r=>GameObject.Find(r.id)).ToArray();
            if(roots.Any(x=>x==null))throw new InvalidOperationException("Load CivilianFitPreview and enter Play Mode");
            var camera=Camera.main;var oldPos=camera.transform.position;var oldRot=camera.transform.rotation;var oldFov=camera.fieldOfView;
            var activeGraph=default(PlayableGraph);
            var positions=roots.Select(r=>r.transform.position).ToArray();
            var rotations=roots.Select(r=>r.transform.rotation).ToArray();
            var report=new Report{unity=Application.unityVersion,playMode=true,variants=roots.Length,inputs=Inputs(),motions=new[]{"ual1:idle_loop","ual1:walk_loop","ual1:idle_talking_loop"}};
            var motions=quick?new[]{"Idle"}:new[]{"Idle","Walk","Talking"};
            var phases=quick?new[]{.25f}:new[]{0f,.25f,.5f,.75f};
            var views=quick?new[]{"front"}:new[]{"front","rear","side"};
            const int width=440,height=660;
            Directory.CreateDirectory(Evidence);
            try
            {
                foreach(var root in roots)root.SetActive(false);
                foreach(var motion in motions)foreach(var phase in phases)foreach(var view in views)
                {
                    var sheet=new Texture2D(width*roots.Length,height,TextureFormat.RGB24,false);
                    for(int index=0;index<roots.Length;index++)
                    {
                        var root=roots[index];root.SetActive(true);root.transform.position=Vector3.zero;root.transform.rotation=Quaternion.identity;
                        var animator=root.GetComponent<Animator>();animator.speed=0;animator.Rebind();
                        var motionId=motion=="Idle"?"ual1:idle_loop":motion=="Walk"?"ual1:walk_loop":"ual1:idle_talking_loop";
                        var input=JDAnimationFactory.ReadRequest().clips.Single(c=>c.id==motionId);
                        var clip=CharPosture.LoadFor(recipes[index],motion);
                        var graph=JDAnimationFactory.Graph(animator,clip,out var playable);
                        activeGraph=graph;
                        playable.SetTime(phase*clip.length);graph.Evaluate(0);
                        if(view=="front"&&phase==0)report.problems.AddRange(JDAnimationFactory.CheckTarget(animator).Select(p=>root.name+": "+p));
                        if(animator.avatar==null||!animator.avatar.isValid||!animator.isHuman)report.problems.Add(root.name+": invalid humanoid");
                        var renderers=root.GetComponentsInChildren<SkinnedMeshRenderer>();
                        if(renderers.Length==0)report.problems.Add(root.name+": no skin meshes");
                        Bounds bounds=new Bounds();bool first=true,finite=true;int vertices=0;
                        foreach(var renderer in renderers)
                        {
                            if(renderer.sharedMesh==null||renderer.bones.Any(b=>b==null))report.problems.Add(root.name+": missing mesh/bone");
                            foreach(var material in renderer.sharedMaterials)
                                if(!CharFactory.ValidMaterial(material))report.problems.Add(root.name+": invalid material");
                            var baked=new Mesh();renderer.BakeMesh(baked);
                            foreach(var v in baked.vertices)
                            {
                                var p=renderer.transform.TransformPoint(v);vertices++;
                                finite&=!(float.IsNaN(p.x)||float.IsInfinity(p.x)||float.IsNaN(p.y)||float.IsInfinity(p.y)||float.IsNaN(p.z)||float.IsInfinity(p.z));
                                if(first){bounds=new Bounds(p,Vector3.zero);first=false;}else bounds.Encapsulate(p);
                            }
                            UnityEngine.Object.DestroyImmediate(baked);
                        }
                        if(view=="front")
                        {
                            report.samples.Add(new Sample{id=root.name,motion=motion,phase=phase,minY=bounds.min.y,height=bounds.size.y,width=bounds.size.x,vertices=vertices,finite=finite});
                            if(!finite||bounds.size.y<1.4f||bounds.size.y>2.1f||bounds.size.x>1.3f||bounds.min.y<-.10f||bounds.min.y>.15f)
                                report.problems.Add(root.name+": gross posed bounds/ground failure "+motion+"/"+phase);
                        }
                        camera.transform.position=view=="front"?new Vector3(0,1.4f,3.1f):view=="rear"?new Vector3(0,1.4f,-3.1f):new Vector3(3.1f,1.4f,0);
                        camera.transform.LookAt(new Vector3(0,1.0f,0));camera.fieldOfView=42;
                        var tile=JDAnimationFactory.Capture(camera,width,height);sheet.SetPixels(index*width,0,width,height,tile.GetPixels());UnityEngine.Object.DestroyImmediate(tile);
                        graph.Destroy();
                        root.SetActive(false);
                    }
                    sheet.Apply();File.WriteAllBytes(Path.Combine(Evidence,(quick?"preview":"fit")+"_"+motion+"_"+phase.ToString("0.00",System.Globalization.CultureInfo.InvariantCulture)+"_"+view+".png"),sheet.EncodeToPNG());
                    UnityEngine.Object.DestroyImmediate(sheet);
                }
            }
            finally
            {
                if(activeGraph.IsValid())activeGraph.Destroy();
                for(int i=0;i<roots.Length;i++)
                {
                    roots[i].SetActive(true);roots[i].transform.position=positions[i];roots[i].transform.rotation=rotations[i];roots[i].GetComponent<Animator>().speed=1;
                }
                camera.transform.SetPositionAndRotation(oldPos,oldRot);camera.fieldOfView=oldFov;
            }
            if(!quick)File.WriteAllText(Path.Combine(Evidence,"unity_runtime_validation.json"),JsonUtility.ToJson(report,true));
            Debug.Log("CHAR_RUNTIME_VALIDATION samples="+report.samples.Count+" problems="+report.problems.Count);
            if(report.problems.Count>0)throw new InvalidOperationException(string.Join("\n",report.problems.Distinct()));
        }

        [MenuItem("Tools/JuegoDef/Characters/Capture gameplay distance groups")]
        public static void Groups()
        {
            if(!EditorApplication.isPlaying)throw new InvalidOperationException("Group captures require Play Mode");
            var recipes=CharFactory.Read().recipes;
            var roots=recipes.Select(r=>GameObject.Find(r.id)).ToArray();
            var active=roots.Select(r=>r.activeSelf).ToArray();
            var cam=Camera.main;var camPos=cam.transform.position;var camRot=cam.transform.rotation;var fov=cam.fieldOfView;
            var bg=cam.backgroundColor;var positions=roots.Select(r=>r.transform.position).ToArray();var rotations=roots.Select(r=>r.transform.rotation).ToArray();
            var graphs=new List<PlayableGraph>();
            var renderers=roots.SelectMany(r=>r.GetComponentsInChildren<Renderer>()).ToArray();
            var materials=renderers.Select(r=>r.sharedMaterials).ToArray();
            var silhouette=new Material(Shader.Find("Universal Render Pipeline/Unlit"));silhouette.SetColor("_BaseColor",Color.black);silhouette.SetFloat("_Cull",0);
            var ground=GameObject.Find("Fit review ground");
            try
            {
                for(int i=0;i<roots.Length;i++)
                {
                    roots[i].transform.position=new Vector3((i%5-2f)*1.15f,0,0);
                    var animator=roots[i].GetComponent<Animator>();animator.Rebind();
                    var clip=CharPosture.LoadFor(recipes[i],"Idle");
                    var graph=JDAnimationFactory.Graph(animator,clip,out var playable);playable.SetTime(.25*clip.length);graph.Evaluate(0);graphs.Add(graph);
                }
                foreach(float distance in new[]{10f,20f})foreach(float angle in new[]{0f,90f,45f})foreach(bool mono in new[]{false,true})
                {
                    for(int i=0;i<roots.Length;i++)roots[i].transform.rotation=Quaternion.Euler(0,angle,0);
                    cam.transform.position=new Vector3(0,1.7f,distance);cam.transform.LookAt(new Vector3(0,1,0));cam.fieldOfView=50;
                    cam.backgroundColor=mono?Color.white:bg;ground.SetActive(!mono);
                    for(int i=0;i<renderers.Length;i++)renderers[i].sharedMaterials=mono?materials[i].Select(m=>silhouette).ToArray():materials[i];
                    foreach(int width in new[]{1920,640})
                    {
                        int count=(roots.Length+4)/5, height=width*9/16;
                        var sheet=new Texture2D(width*count,height,TextureFormat.RGB24,false);
                        for(int batch=0;batch<count;batch++)
                        {
                            for(int i=0;i<roots.Length;i++)roots[i].SetActive(i/5==batch);
                            var image=JDAnimationFactory.Capture(cam,width,height);
                            sheet.SetPixels(batch*width,0,width,height,image.GetPixels());UnityEngine.Object.DestroyImmediate(image);
                        }
                        sheet.Apply();
                        File.WriteAllBytes(Path.Combine(Evidence,"group_"+distance+"m_"+angle+"deg_"+(mono?"silhouette":"color")+"_"+width+".png"),sheet.EncodeToPNG());
                        UnityEngine.Object.DestroyImmediate(sheet);
                    }
                }
            }
            finally
            {
                foreach(var graph in graphs)if(graph.IsValid())graph.Destroy();
                for(int i=0;i<roots.Length;i++){roots[i].SetActive(active[i]);roots[i].transform.SetPositionAndRotation(positions[i],rotations[i]);roots[i].GetComponent<Animator>().speed=1;}
                for(int i=0;i<renderers.Length;i++)renderers[i].sharedMaterials=materials[i];
                ground.SetActive(true);cam.transform.SetPositionAndRotation(camPos,camRot);cam.fieldOfView=fov;cam.backgroundColor=bg;
                UnityEngine.Object.DestroyImmediate(silhouette);
            }
            Debug.Log("CHAR_DISTANCE_GROUPS_COMPLETE");
        }
    }
}

using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEngine.Playables;
using JuegoDef.Characters;
using JuegoDef.Characters.Editor;

// Bounded Play Mode observations. Live never calls Sample: its frames observe
// the ordinary Animator + NpcPresentation.LateUpdate running between editor ticks.
public static class CharLivingRun
{
    static string Output => Path.Combine(CharValidation.Evidence,"naturalism_2026-10-01/living");
    static void Write(string file,object value) { Directory.CreateDirectory(Output);File.WriteAllText(Path.Combine(Output,file),Newtonsoft.Json.JsonConvert.SerializeObject(value,Newtonsoft.Json.Formatting.Indented)); }
    static void RequirePlay() { if(!EditorApplication.isPlaying)throw new InvalidOperationException("Living evidence requires Play Mode"); }
    static float AngleSpan(List<Quaternion> values) => values.Max(q=>Quaternion.Angle(values[0],q));
    static float Span(List<Vector3> values) => values.Max(v=>Vector3.Distance(values[0],v));
    static float[] V(Vector3 value)=>new[]{value.x,value.y,value.z};

    public static object Audit()
    {
        RequirePlay();var rows=new List<object>();var problems=new List<string>();
        var firstBlinks=new List<float>();
        foreach(var recipe in CharFactory.Read().recipes)
        {
            var root=UnityEngine.Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>(CharFactory.Root+"/Prefabs/"+recipe.id+".prefab"));
            root.name="Living observation: "+recipe.id;root.transform.SetPositionAndRotation(new Vector3(0,-10,0),Quaternion.identity);
            var target=new GameObject("Bounded attention observation");
            PlayableGraph graph=default;
            try
            {
                var animator=root.GetComponent<Animator>();animator.Rebind();animator.Update(0);animator.speed=0;
                var present=root.GetComponent<NpcPresentation>();
                if(!present.Ready) { problems.Add(recipe.id+" missing admitted lid/eye shapes");continue; }
                var head=animator.GetBoneTransform(HumanBodyBones.Head);
                var hips=animator.GetBoneTransform(HumanBodyBones.Hips);
                var chest=animator.GetBoneTransform(HumanBodyBones.Chest);
                var spine=animator.GetBoneTransform(HumanBodyBones.Spine);
                var clip=CharPosture.LoadFor(recipe,"Idle");
                graph=JDAnimationFactory.Graph(animator,clip,out var playable);
                var chestFrames=new List<Quaternion>();var spineFrames=new List<Quaternion>();var hipsFrames=new List<Vector3>();
                for(int j=0;j<48;j++)
                {
                    playable.SetTime(clip.length*j/48);graph.Evaluate(0);
                    chestFrames.Add(chest.rotation);spineFrames.Add(spine.rotation);hipsFrames.Add(hips.position);
                }
                playable.SetTime(0);graph.Evaluate(0);
                var protectedBones=new[]{HumanBodyBones.Hips,HumanBodyBones.LeftFoot,HumanBodyBones.RightFoot};
                var protectedMatrices=protectedBones.Select(b=>animator.GetBoneTransform(b).localToWorldMatrix).ToArray();
                target.transform.position=head.position+Vector3.forward*2;
                present.attentionTarget=target.transform;
                var events=new List<float>();bool closed=false;float peak=0,maxYaw=0,maxHead=0;
                for(int frame=0;frame<=2400;frame++)
                {
                    float t=frame/60f;present.Sample(t,1/60f);
                    bool now=present.BlinkLeftWeight>90;
                    if(now&&!closed)events.Add(t);closed=now;
                    peak=Mathf.Max(peak,present.BlinkLeftWeight);
                    maxYaw=Mathf.Max(maxYaw,Mathf.Abs(present.GazeYaw));maxHead=Mathf.Max(maxHead,Mathf.Abs(present.HeadYaw));
                }
                if(events.Count<5||peak<99)problems.Add(recipe.id+" no complete anatomical blink");
                var intervals=events.Skip(1).Select((t,i)=>t-events[i]).ToArray();
                if(intervals.Length>1&&intervals.Max()-intervals.Min()<.2f)problems.Add(recipe.id+" mechanical blink cadence");
                firstBlinks.Add(events.FirstOrDefault());
                target.transform.position=head.position+new Vector3(-.8f,.15f,2);
                for(int k=0;k<90;k++)present.Sample(41+k/60f,1/60f);
                float left=present.GazeYaw;
                target.transform.position=head.position+new Vector3(.8f,.15f,2);
                for(int k=0;k<90;k++)present.Sample(43+k/60f,1/60f);
                float right=present.GazeYaw;
                if(left> -3||right<3)problems.Add(recipe.id+" attention direction");
                target.transform.position=head.position-Vector3.forward*2;
                for(int k=0;k<150;k++)present.Sample(45+k/60f,1/60f);
                float behind=present.HeadYaw;
                if(Mathf.Abs(behind)>1)problems.Add(recipe.id+" turns to a target behind its body");
                target.transform.position=head.position+new Vector3(20,0,20);
                for(int k=0;k<150;k++)present.Sample(48+k/60f,1/60f);
                if(Mathf.Abs(present.HeadYaw)>1)problems.Add(recipe.id+" distant attention");
                present.attentionTarget=null;UnityEngine.Object.DestroyImmediate(target);target=null;
                present.Sample(52,1/60f);present.Sample(float.NaN,1/60f);present.Sample(53,float.PositiveInfinity);
                var input=typeof(NpcPresentation).GetField("inputHead",System.Reflection.BindingFlags.Instance|System.Reflection.BindingFlags.NonPublic);
                var baseRotation=(Quaternion)input.GetValue(present);
                present.enabled=false;
                if(Quaternion.Angle(head.rotation,baseRotation)>.01f)problems.Add(recipe.id+" additive head restore");
                foreach(var renderer in new[]{present.face,present.eyes})
                    for(int j=0;j<renderer.sharedMesh.blendShapeCount;j++)
                        if(Mathf.Abs(renderer.GetBlendShapeWeight(j))>.01f)problems.Add(recipe.id+" morph left active on disable");
                for(int j=0;j<protectedBones.Length;j++)
                    if(animator.GetBoneTransform(protectedBones[j]).localToWorldMatrix!=protectedMatrices[j])problems.Add(recipe.id+" presentation changes root/legs");
                rows.Add(new {recipe.id,seed=present.seed,blinkEvents=events,intervals,peak,left,right,behind,
                    eyeShapes=present.eyes.sharedMesh.blendShapeCount,lidShapes=present.face.sharedMesh.blendShapeCount,
                    idleDuration=clip.length,chestAngleSpan=AngleSpan(chestFrames),spineAngleSpan=AngleSpan(spineFrames),hipsPositionSpan=Span(hipsFrames)});
            }
            finally {if(graph.IsValid())graph.Destroy();if(target!=null)UnityEngine.Object.DestroyImmediate(target);UnityEngine.Object.DestroyImmediate(root);}
        }
        if(firstBlinks.Distinct().Count()<10)problems.Add("Batch blink phases are synchronized");
        var result=new {unity=Application.unityVersion,playMode=true,variants=rows.Count,rows,problems,inputs=CharValidation.CurrentInputs(),
            canonicalPlayerPresent=GameCreator.Runtime.Common.ShortcutPlayer.Instance!=null,
            note="Controlled calls to the same presentation update in Play Mode. Chest/hip observations measure the admitted Animator clip; live ticks are separately recorded."};
        Write("LIVING_AUDIT.json",result);
        if(problems.Count>0)throw new InvalidOperationException(string.Join("; ",problems));return result;
    }

    static GameObject[] roots;static bool[] active;static GameObject pilot,targetLive;
    static Camera camera;static Vector3 originalPilot,originalCamera;static Quaternion pilotRotation,cameraRotation;static float originalFov,start,last;
    static readonly List<object> liveFrames=new List<object>();static bool running;static int frame;static bool oldAsync;
    public static object StartLive()
    {
        RequirePlay();if(running)throw new InvalidOperationException("An observation is already running");
        roots=CharFactory.Read().recipes.Select(r=>GameObject.Find(r.id)).ToArray();active=roots.Select(r=>r.activeSelf).ToArray();
        pilot=roots.Single(r=>r.name=="waiter-veteran");camera=Camera.main;
        originalPilot=pilot.transform.position;pilotRotation=pilot.transform.rotation;
        originalCamera=camera.transform.position;cameraRotation=camera.transform.rotation;originalFov=camera.fieldOfView;
        foreach(var root in roots)root.SetActive(root==pilot);
        pilot.transform.SetPositionAndRotation(Vector3.zero,Quaternion.identity);
        var animator=pilot.GetComponent<Animator>();animator.speed=1;animator.Play("Idle",0,0);animator.Update(0);
        var present=pilot.GetComponent<NpcPresentation>();present.enabled=true;if(!present.Ready)throw new InvalidOperationException("Pilot morphs absent");
        targetLive=new GameObject("Live attention reference");present.attentionTarget=targetLive.transform;
        camera.transform.position=new Vector3(0,1.62f,1.55f);camera.transform.LookAt(new Vector3(0,1.59f,0));camera.fieldOfView=30;
        oldAsync=ShaderUtil.allowAsyncCompilation;ShaderUtil.allowAsyncCompilation=false;
        Directory.CreateDirectory(Path.Combine(Output,"frames"));
        foreach(var previous in Directory.GetFiles(Path.Combine(Output,"frames"),"frame_*.png"))File.Delete(previous);
        liveFrames.Clear();frame=0;start=Time.time;last=-1;running=true;
        EditorApplication.update+=Observe;
        return new {status="ordinary Play Mode observation running",seconds=8,rate=12};
    }
    static void Observe()
    {
        if(!running)return;
        try
        {
            if(!EditorApplication.isPlaying)throw new InvalidOperationException("Play stopped during observation");
            float time=Time.time-start;
            var animator=pilot.GetComponent<Animator>();var present=pilot.GetComponent<NpcPresentation>();
            var head=animator.GetBoneTransform(HumanBodyBones.Head);
            targetLive.transform.position=head.position+new Vector3(.8f*Mathf.Sin(time*.8f),.08f,2.2f);
            if(time-last<1/12f)return;last=time;
            string file="frame_"+frame.ToString("000")+".png";
            var image=JDAnimationFactory.Capture(camera,600,700);File.WriteAllBytes(Path.Combine(Output,"frames",file),image.EncodeToPNG());UnityEngine.Object.DestroyImmediate(image);
            liveFrames.Add(new {file,time,blinkLeft=present.BlinkLeftWeight,blinkRight=present.BlinkRightWeight,
                gazeYaw=present.GazeYaw,headYaw=present.HeadYaw,head=V(head.position),chest=V(animator.GetBoneTransform(HumanBodyBones.Chest).position),
                hips=V(animator.GetBoneTransform(HumanBodyBones.Hips).position)});frame++;
            if(time>=8)Finish(null);
        }
        catch(Exception error){Finish(error.ToString());}
    }
    static void Finish(string error)
    {
        running=false;EditorApplication.update-=Observe;
        pilot.GetComponent<NpcPresentation>().attentionTarget=null;
        UnityEngine.Object.DestroyImmediate(targetLive);pilot.transform.SetPositionAndRotation(originalPilot,pilotRotation);
        for(int i=0;i<roots.Length;i++)roots[i].SetActive(active[i]);
        camera.transform.SetPositionAndRotation(originalCamera,cameraRotation);camera.fieldOfView=originalFov;ShaderUtil.allowAsyncCompilation=oldAsync;
        Write("LIVING_LIVE.json",new {unity=Application.unityVersion,playMode=true,directSampleCalls=false,frames=liveFrames,error,inputs=CharValidation.CurrentInputs(),
            note="Uninterrupted ordinary Animator and LateUpdate ticks; a moving attention point exercises the same optional target input. Canonical GC2 player attention is checked in ENV separately."});
    }
    public static object Status()=>new {running,frames=frame};
}

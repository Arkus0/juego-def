using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Animations;
using UnityEngine.Playables;
using UnityEngine.SceneManagement;

/// <summary>Disposable native Humanoid preview; no scene/controller/gameplay ownership.</summary>
public sealed class JDAnimationPreview : EditorWindow
{
    JDAnimationFactory.Request request;
    JDAnimationFactory.ClipInput[] filtered = Array.Empty<JDAnimationFactory.ClipInput>();
    string query="", family="all";
    int selected;
    bool playing=true;
    float time;
    double last;
    Scene preview;
    Camera camera;
    GameObject[] bodies;
    PlayableGraph[] graphs;
    AnimationClip clip;
    RenderTexture texture;

    [MenuItem("Tools/JuegoDef/Animation/Motion Preview")]
    public static void Open() => GetWindow<JDAnimationPreview>("Motion Preview");
    public static void VerifyPreview()
    {
        var active=SceneManager.GetActiveScene();
        var roots=active.GetRootGameObjects();
        var dirty=active.isDirty;
        var window=CreateInstance<JDAnimationPreview>();
        try
        {
            window.query="ual1:walk_loop";window.Filter();window.Build();
            foreach(var graph in window.graphs) graph.Evaluate(.3f);
            var image=JDAnimationFactory.Capture(window.camera,960,640);
            Directory.CreateDirectory("Captures");
            File.WriteAllBytes("Captures/anim-preview-smoke.png",image.EncodeToPNG());
            DestroyImmediate(image);
            var temporary=window.preview;
            window.DisposePreview();
            if(temporary.IsValid() || active.isDirty!=dirty ||
                !roots.SequenceEqual(active.GetRootGameObjects())) throw new InvalidOperationException("Preview modified the active scene or leaked its temporary scene");
            Debug.Log("JD_ANIM_PREVIEW_OK");
        }
        finally { DestroyImmediate(window); }
    }
    void OnEnable()
    {
        request=JDAnimationFactory.ReadRequest();
        Filter();
        last=EditorApplication.timeSinceStartup;
        EditorApplication.update+=Tick;
    }
    void Filter()
    {
        filtered=request.clips.Where(c=>(family=="all" || c.family==family) &&
            (c.id+" "+c.family).IndexOf(query,StringComparison.OrdinalIgnoreCase)>=0).ToArray();
        selected=0; DisposePreview();
    }
    void Build()
    {
        DisposePreview();
        if(filtered.Length==0) return;
        preview=EditorSceneManager.NewPreviewScene();
        camera=JDAnimationFactory.Stage(preview);
        bodies=request.targets.Select((t,i)=>JDAnimationFactory.Body(t,new Vector3(i==0?-.6f:.6f,0,0),
            i==0?new Color(.25f,.55f,.7f):new Color(.8f,.48f,.3f),preview)).ToArray();
        clip=JDAnimationFactory.Load(filtered[selected]);
        graphs=bodies.Select(b=>JDAnimationFactory.Graph(b.GetComponent<Animator>(),clip,out _)).ToArray();
        texture=new RenderTexture(960,640,24);
        camera.targetTexture=texture;
        time=0;
    }
    void Tick()
    {
        double now=EditorApplication.timeSinceStartup;
        float dt=Mathf.Min((float)(now-last),.05f); last=now;
        if(!camera || graphs==null) return;
        if(playing)
        {
            if(time+dt>=clip.length && !clip.isLooping) { Build(); dt=0; }
            foreach(var graph in graphs) graph.Evaluate(dt);
            time+=dt;
        }
        camera.Render(); Repaint();
    }
    void OnGUI()
    {
        EditorGUILayout.HelpBox("Source motion preview on regular male/female bodies. Contact props and final civilian art are not supplied. Batch Play Mode evidence remains the admission authority.",MessageType.Info);
        var nextQuery=EditorGUILayout.TextField("Search ID",query);
        var families=new[]{"all"}.Concat(request.clips.Select(c=>c.family).Distinct()).ToArray();
        var nextFamily=families[EditorGUILayout.Popup("Family",Array.IndexOf(families,family),families)];
        if(nextQuery!=query || nextFamily!=family) { query=nextQuery;family=nextFamily;Filter(); }
        if(filtered.Length==0) { EditorGUILayout.LabelField("No clips");return; }
        int next=EditorGUILayout.Popup("Clip",selected,filtered.Select(c=>c.id).ToArray());
        if(next!=selected) { selected=next; Build(); }
        if(GUILayout.Button(camera?"Restart":"Load motion")) Build();
        playing=EditorGUILayout.Toggle("Play",playing);
        if(texture) GUI.DrawTexture(GUILayoutUtility.GetAspectRect(1.5f),texture,ScaleMode.ScaleToFit,false);
    }
    void DisposePreview()
    {
        if(graphs!=null) foreach(var graph in graphs) if(graph.IsValid()) graph.Destroy();
        graphs=null;camera=null;
        if(preview.IsValid())
        {
            foreach(var root in preview.GetRootGameObjects()) JDAnimationFactory.DisposeBody(root);
            EditorSceneManager.ClosePreviewScene(preview);
        }
        if(texture) { texture.Release(); DestroyImmediate(texture); }
        texture=null;
    }
    void OnDisable() { EditorApplication.update-=Tick; DisposePreview(); }
}

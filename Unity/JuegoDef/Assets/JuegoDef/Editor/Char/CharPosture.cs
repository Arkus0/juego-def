using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;

namespace JuegoDef.Characters.Editor
{
    /// <summary>
    /// Civilian posture filter over admitted ANIM-01 Humanoid clips (CHAR presentation layer, not new motion).
    /// The UAL sources are authored for an action hero: fists clenched at -0.9 on every finger, feet planted wide
    /// (Upper Leg In-Out about +0.25) and the upper chest pushed back. Frozen in a street lineup this reads as a
    /// permanent fighting stance. Derived clips copy the source and rewrite only the static component of named
    /// muscle curves, so gestures, weight shifts and walk dynamics survive. Source clips stay untouched.
    /// </summary>
    public static class CharPosture
    {
        public const string Folder = CharFactory.Root + "/Motion";
        public const string Prefix = "civ:";

        /// <summary>Per-clip filter. hands: open relaxed hands; stance: factor on the mean leg spread; chest: factor on the mean upper-chest lean;
        /// pronate: held forearm twist for hanging arms (an opened UAL fist otherwise shows the palm to the front).</summary>
        [Serializable] public class Rule { public string id; public bool hands = true; public float stance = .45f; public float chest = .55f; public float pronate = float.NaN; }

        static readonly Rule[] Rules =
        {
            new Rule { id = "ual1:idle_loop", pronate = -.6f },
            new Rule { id = "ual1:idle_lookaround_loop" },
            new Rule { id = "ual1:idle_tired_loop", pronate = -.6f },
            new Rule { id = "ual1:idle_talking_loop" },
            new Rule { id = "ual1:counter_idle_loop" },
            new Rule { id = "ual2:idle_foldarms_loop" },
            new Rule { id = "ual2:idle_talkingphone_loop", hands = false },   // one hand holds the phone
            new Rule { id = "ual1:walk_loop", stance = .85f, chest = .8f, pronate = -.5f },
            new Rule { id = "ual1:walk_formal_loop", stance = .85f, chest = .8f, pronate = -.5f },
        };

        // Relaxed, loosely curled resting hand (Humanoid muscle space, -1 curled .. +1 stretched), picked from a rendered grid:
        // the thumb rests along the index, distal joints curl a little more than proximal ones, pinky most.
        static readonly Dictionary<string, float> Hand = new Dictionary<string, float>
        {
            { "Thumb.1 Stretched", -.68f }, { "Thumb.Spread", -.24f }, { "Thumb.2 Stretched", -.08f }, { "Thumb.3 Stretched", -.20f },
            { "Index.1 Stretched", .02f }, { "Index.Spread", 0f }, { "Index.2 Stretched", -.23f }, { "Index.3 Stretched", -.19f },
            { "Middle.1 Stretched", -.06f }, { "Middle.Spread", 0f }, { "Middle.2 Stretched", -.31f }, { "Middle.3 Stretched", -.23f },
            { "Ring.1 Stretched", -.14f }, { "Ring.Spread", 0f }, { "Ring.2 Stretched", -.39f }, { "Ring.3 Stretched", -.27f },
            { "Little.1 Stretched", -.22f }, { "Little.Spread", 0f }, { "Little.2 Stretched", -.47f }, { "Little.3 Stretched", -.31f },
        };

        public static bool Has(string sourceId) => Rules.Any(r => r.id == sourceId);
        static string AssetPath(string sourceId) => Folder + "/civ_" + sourceId.Replace(':', '_') + ".anim";

        /// <summary>Resolve "civ:&lt;source id&gt;" (or a bare source id that has a rule) to the derived clip, rebuilding it when missing.</summary>
        public static AnimationClip Load(string id)
        {
            var source = id.StartsWith(Prefix) ? id.Substring(Prefix.Length) : id;
            var rule = Rules.FirstOrDefault(r => r.id == source);
            var request = JDAnimationFactory.ReadRequest();
            var input = request.clips.Single(c => c.id == source);
            if (rule == null) return JDAnimationFactory.Load(input);
            var clip = AssetDatabase.LoadAssetAtPath<AnimationClip>(AssetPath(source));
            return clip != null ? clip : Derive(rule, JDAnimationFactory.Load(input));
        }

        [MenuItem("Tools/JuegoDef/Characters/Build civilian posture clips")]
        public static void BuildAll()
        {
            var request = JDAnimationFactory.ReadRequest();
            foreach (var rule in Rules) Derive(rule, JDAnimationFactory.Load(request.clips.Single(c => c.id == rule.id)));
            foreach(var recipe in CharFactory.Read().recipes)
                foreach(var motion in new[]{"Idle","Walk","Talking"}) Profile(recipe,motion);
            AssetDatabase.SaveAssets();
            Debug.Log("CHAR_POSTURE_BUILT " + Rules.Length);
        }

        static string ProfilePath(CharFactory.Recipe r,string motion) => Folder+"/char_"+r.id+"_"+motion+".anim";
        public static AnimationClip LoadFor(CharFactory.Recipe r,string motion)
        {
            var clip=AssetDatabase.LoadAssetAtPath<AnimationClip>(ProfilePath(r,motion));
            return clip!=null?clip:Profile(r,motion);
        }
        public static RuntimeAnimatorController Controller(CharFactory.Recipe r,RuntimeAnimatorController shared)
        {
            string path=Folder+"/char_"+r.id+".overrideController";
            var controller=AssetDatabase.LoadAssetAtPath<AnimatorOverrideController>(path);
            if(controller==null){controller=new AnimatorOverrideController(shared);AssetDatabase.CreateAsset(controller,path);}
            else controller.runtimeAnimatorController=shared;
            controller[Load("ual1:idle_loop").name]=LoadFor(r,"Idle");
            controller[Load("ual1:walk_loop").name]=LoadFor(r,"Walk");
            controller[Load("ual1:idle_talking_loop").name]=LoadFor(r,"Talking");
            EditorUtility.SetDirty(controller);return controller;
        }
        static AnimationClip Profile(CharFactory.Recipe r,string motion)
        {
            string id=motion=="Idle"?(string.IsNullOrEmpty(r.pose)?"ual1:idle_loop":r.pose):motion=="Walk"?"ual1:walk_loop":"ual1:idle_talking_loop";
            var source=Load(id);var clip=new AnimationClip();EditorUtility.CopySerialized(source,clip);
            clip.name="char_"+r.id+"_"+motion;
            float influence=motion=="Idle"?1f:motion=="Walk"?.45f:.6f;
            var offsets=new Dictionary<string,float> {
                {"Spine Front-Back",r.slouch*influence}, {"Chest Front-Back",r.slouch*.4f*influence},
                {"Neck Nod Down-Up",r.slouch*.25f*influence}, {"Head Nod Down-Up",-r.slouch*.3f*influence},
                {"Spine Left-Right",r.stanceBias*influence}, {"Head Tilt Left-Right",-r.stanceBias*.5f*influence},
                {"Left Shoulder Down-Up",-r.stanceBias*.5f*influence}, {"Right Shoulder Down-Up",r.stanceBias*.5f*influence}
            };
            foreach(var kv in offsets)
            {
                var binding=EditorCurveBinding.FloatCurve("",typeof(Animator),kv.Key);
                var curve=AnimationUtility.GetEditorCurve(source,binding);
                AnimationUtility.SetEditorCurve(clip,binding,curve==null?AnimationCurve.Constant(0,source.length,kv.Value):Shift(curve,kv.Value));
            }
            string path=ProfilePath(r,motion);var old=AssetDatabase.LoadAssetAtPath<AnimationClip>(path);
            if(old==null)AssetDatabase.CreateAsset(clip,path);
            else {EditorUtility.CopySerialized(clip,old);UnityEngine.Object.DestroyImmediate(clip);clip=old;EditorUtility.SetDirty(clip);}
            return clip;
        }

        static float Mean(AnimationCurve curve, float length)
        {
            float sum = 0; const int n = 24;
            for (int i = 0; i < n; i++) sum += curve.Evaluate(length * i / n);
            return sum / n;
        }

        /// <summary>value' = value - mean + target: replaces only the held component of a curve.</summary>
        static AnimationCurve Shift(AnimationCurve curve, float delta)
        {
            var keys = curve.keys;
            for (int i = 0; i < keys.Length; i++) keys[i].value += delta;
            return new AnimationCurve(keys) { preWrapMode = curve.preWrapMode, postWrapMode = curve.postWrapMode };
        }

        static AnimationClip Derive(Rule rule, AnimationClip source)
        {
            if (!source.humanMotion) throw new InvalidOperationException("Civilian posture needs a Humanoid clip: " + rule.id);
            Directory.CreateDirectory(Path.GetFullPath(Path.Combine(Application.dataPath, "..", Folder)));
            var clip = new AnimationClip();
            EditorUtility.CopySerialized(source, clip);
            clip.name = "civ_" + source.name;
            foreach (var binding in AnimationUtility.GetCurveBindings(source))
            {
                var name = binding.propertyName;
                var curve = AnimationUtility.GetEditorCurve(source, binding);
                float mean = Mean(curve, source.length);
                AnimationCurve result = null;
                if (rule.hands && (name.StartsWith("LeftHand.") || name.StartsWith("RightHand.")))
                {
                    var muscle = name.Substring(name.IndexOf('.') + 1);
                    if (Hand.TryGetValue(muscle, out var target)) result = Shift(curve, target - mean);
                }
                else if (name == "Left Upper Leg In-Out" || name == "Right Upper Leg In-Out") result = Shift(curve, mean * (rule.stance - 1));
                else if (name == "UpperChest Front-Back" || name == "Chest Front-Back") result = Shift(curve, mean * (rule.chest - 1));
                else if (!float.IsNaN(rule.pronate) && (name == "Left Forearm Twist In-Out" || name == "Right Forearm Twist In-Out")) result = Shift(curve, rule.pronate - mean);
                else if ((rule.id=="ual1:idle_loop"||rule.id=="ual1:idle_tired_loop"||rule.id=="ual1:idle_lookaround_loop"||rule.id.Contains("walk")) &&
                    (name=="Left Shoulder Front-Back"||name=="Right Shoulder Front-Back")) result=Shift(curve,.30f-mean);
                else if ((rule.id=="ual1:idle_loop"||rule.id=="ual1:idle_tired_loop") &&
                    (name=="Left Arm Down-Up"||name=="Right Arm Down-Up")) result=Shift(curve,-.60f-mean);
                if (result != null) AnimationUtility.SetEditorCurve(clip, binding, result);
            }
            if (!float.IsNaN(rule.pronate))
                foreach (var muscle in new[] { "Left Forearm Twist In-Out", "Right Forearm Twist In-Out" })
                    if (!AnimationUtility.GetCurveBindings(source).Any(b => b.propertyName == muscle))
                        AnimationUtility.SetEditorCurve(clip, EditorCurveBinding.FloatCurve("", typeof(Animator), muscle), AnimationCurve.Constant(0, source.length, rule.pronate));
            var path = AssetPath(rule.id);
            var existing = AssetDatabase.LoadAssetAtPath<AnimationClip>(path);
            if (existing == null) AssetDatabase.CreateAsset(clip, path);
            else { EditorUtility.CopySerialized(clip, existing); UnityEngine.Object.DestroyImmediate(clip); clip = existing; EditorUtility.SetDirty(clip); }
            return clip;
        }
    }
}

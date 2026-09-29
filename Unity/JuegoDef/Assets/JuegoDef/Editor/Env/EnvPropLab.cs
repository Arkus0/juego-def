using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// Prop lab (owner cohesion pass, CUSTOM_PROPS_BEFORE_AFTER): every module alone under the same light, from the
    /// same three-quarter street view, on real paving, with the GC2 mannequin (1.8 m) beside free-standing pieces for
    /// scale and a rendered wall behind wall-mounted ones — so own pieces are judged at the framing of the Quaternius
    /// ones and before/after close-ups pair by name.
    /// Entries: <c>"ENV_Bench_Street"</c>, or <c>"ENV_AC_Unit:wall:1.6"</c> (wall mount, origin height on the wall).
    /// Operator: <c>EnvPropLab.Capture("ENV_Bench_Street,ENV_AC_Unit:wall:1.6", "../../Docs/.../props/after")</c>.
    /// </summary>
    public static class EnvPropLab
    {
        const string MannequinPath = "Assets/Plugins/GameCreator/Packages/Core/Runtime/Characters/Assets/3D/Mannequin.fbx";

        public static string Capture(string entries, string outFolder, int size = 720, string district = "Assets/JuegoDef/Scenes/ENV/ENV01_Casco_District.unity")
        {
            var done = new List<string>();
            foreach (var raw in entries.Split(','))
            {
                var e = raw.Trim();
                if (e.Length == 0) continue;
                var parts = e.Split(':');
                var name = parts[0];
                bool wall = parts.Length > 1 && parts[1] == "wall";
                float height = parts.Length > 2 ? float.Parse(parts[2], System.Globalization.CultureInfo.InvariantCulture) : 0f;

                var stage = EnvPreview.NewStage("PropLab", ground: false);
                Ground(stage);
                var go = EnvKit.Place(name, stage, new Vector3(0, height, 0), 0);
                if (!go) { done.Add(name + "(missing)"); continue; }
                var b = EnvPreview.BoundsOf(go);
                if (wall) Wall(stage, b);
                else if (b.size.y > 0.4f) Human(stage, new Vector3(b.min.x - 0.5f, 0, b.center.z - 0.25f));

                // frame the piece itself (close-up); the mannequin is only a scale cue at the edge of the frame
                float r = Mathf.Max(b.extents.magnitude, 0.3f);
                const float fov = 34f;
                float dist = r / Mathf.Sin(fov * 0.5f * Mathf.Deg2Rad) * 1.08f;
                // from the street side (+z), a little to the right and above
                var eye = b.center + new Vector3(Mathf.Sin(28f * Mathf.Deg2Rad), Mathf.Tan(12f * Mathf.Deg2Rad), Mathf.Cos(28f * Mathf.Deg2Rad)).normalized * dist;
                EnvPreview.Capture($"{outFolder}/{name}.jpg", eye, b.center, fov, size, size);
                done.Add(name);
            }
            if (!string.IsNullOrEmpty(district)) EditorSceneManager.OpenScene(district);
            return $"JD_PROPLAB {done.Count} -> {outFolder}: {string.Join(",", done)}";
        }

        /// <summary>A 30 m paving square in the plaza flags (world-scale UVs), so contact reads as in the street.</summary>
        static void Ground(Transform stage)
        {
            var g = GameObject.CreatePrimitive(PrimitiveType.Quad);
            g.name = "LabGround";
            g.transform.SetParent(stage, false);
            g.transform.localRotation = Quaternion.Euler(90, 0, 0);
            g.transform.localScale = new Vector3(30, 30, 1);
            var mf = g.GetComponent<MeshFilter>();
            var m = Object.Instantiate(mf.sharedMesh);
            var uv = m.uv;
            for (int i = 0; i < uv.Length; i++) uv[i] = uv[i] * 30f / 4f;   // the paving textures repeat every 4 m
            m.uv = uv;
            mf.sharedMesh = m;
            var mat = EnvKit.HasMat("ENV_Pave_Losa") ? EnvKit.Mat("ENV_Pave_Losa") : AssetDatabase.LoadAssetAtPath<Material>("Assets/JuegoDef/Materials/JD_Bootstrap_WetGround.mat");
            g.GetComponent<Renderer>().sharedMaterial = mat;
        }

        static void Wall(Transform stage, Bounds b)
        {
            var w = GameObject.CreatePrimitive(PrimitiveType.Cube);
            w.name = "LabWall";
            w.transform.SetParent(stage, false);
            float wd = Mathf.Max(3f, b.size.x + 2f);
            w.transform.localPosition = new Vector3(b.center.x, 2f, 0.092f - 0.1f);
            w.transform.localScale = new Vector3(wd, 4f, 0.2f);
            foreach (var n in new[] { "ENV_Render_Crema_Pintado", "ENV_Render_Arena_Pintado", "MI_Plaster" })
                if (EnvKit.HasMat(n)) { w.GetComponent<Renderer>().sharedMaterial = EnvKit.Mat(n); break; }
        }

        static void Human(Transform stage, Vector3 at)
        {
            var src = AssetDatabase.LoadAssetAtPath<GameObject>(MannequinPath);
            if (!src) return;
            var h = (GameObject)PrefabUtility.InstantiatePrefab(src, stage);
            var b = EnvPreview.BoundsOf(h);
            float k = b.size.y > 0.01f ? 1.8f / b.size.y : 1f;
            h.transform.localScale = Vector3.one * k;
            h.transform.localPosition = at;
            h.transform.localRotation = Quaternion.Euler(0, 160, 0);
        }
    }
}

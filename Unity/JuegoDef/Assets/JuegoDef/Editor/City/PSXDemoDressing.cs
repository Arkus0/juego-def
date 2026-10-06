using System.Collections.Generic;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace JuegoDef.City
{
    /// <summary>
    /// Dressing utilities for the PSX demo (2026-10-06, Owner request after the pensioners-in-the-bench fault):
    ///   - "colliders for benches and tables": every seating/table unit missing a collider (ENV_Bench_Street,
    ///     ENV_Bench_Stone, FUR_ chairs/tables, PRP_Velador) gets a BoxCollider sized to its render bounds, matching
    ///     the convention of the units that already carry one (the pack props and 26 of the 65 benches). Until this
    ///     pass the player walked through them.
    ///   - "settle selected by pelvis": seats the selected NPCs correctly on whatever is under them — reads the
    ///     Animator's pelvis bone, raycasts down (skipping the NPC's own colliders) and lowers/raises the transform
    ///     until the pelvis rests 3 cm over the hit surface. The town's NPCs have no physics (by design: they are
    ///     posed or NavMesh-driven), so contact-aware placement is the correct way to seat them.
    /// Both are re-runnable and only touch the units they report.
    /// </summary>
    public static class PSXDemoDressing
    {
        static bool IsSeating(string n)
        {
            return n.StartsWith("ENV_Bench_Street") || n.StartsWith("ENV_Bench_Stone")
                || (n.StartsWith("FUR_") && (n.Contains("Silla") || n.Contains("Mesa")))
                || n.StartsWith("PRP_Velador");
        }

        [MenuItem("JuegoDef/CITY/PSX Demo: colliders for benches and tables")]
        public static string AddSeatingColliders()
        {
            int added = 0;
            var touchedScenes = new HashSet<Scene>();
            foreach (var t in Object.FindObjectsOfType<Transform>(false))
            {
                var n = t.name;
                if (!IsSeating(n) || n.EndsWith("_COL")) continue;
                if (t.GetComponentsInChildren<Collider>(true).Length > 0) continue;
                var rends = t.GetComponentsInChildren<Renderer>();
                if (rends.Length == 0) continue;
                var b = rends[0].bounds;
                foreach (var r in rends) b.Encapsulate(r.bounds);

                // world bounds -> local AABB of the unit root
                var corners = new Vector3[8];
                int i = 0;
                for (float sx = -1f; sx <= 1f; sx += 2f)
                for (float sy = -1f; sy <= 1f; sy += 2f)
                for (float sz = -1f; sz <= 1f; sz += 2f)
                    corners[i++] = t.InverseTransformPoint(b.center + new Vector3(b.extents.x * sx, b.extents.y * sy, b.extents.z * sz));
                var min = corners[0]; var max = corners[0];
                for (int k = 1; k < 8; k++) { min = Vector3.Min(min, corners[k]); max = Vector3.Max(max, corners[k]); }

                var box = t.gameObject.AddComponent<BoxCollider>();
                box.center = (min + max) * 0.5f;
                box.size = max - min;
                EditorUtility.SetDirty(t.gameObject);
                added++;
                var s = t.gameObject.scene;
                touchedScenes.Add(s);
            }
            foreach (var s in touchedScenes)
            {
                EditorSceneManager.MarkSceneDirty(s);
                EditorSceneManager.SaveScene(s);
            }
            return "JD_PSX_DRESSING colliders added=" + added + " scenes=" + touchedScenes.Count;
        }

        [MenuItem("JuegoDef/CITY/PSX Demo: settle selected by pelvis")]
        public static string SettleSelectedByPelvis()
        {
            var log = new StringBuilder();
            int settled = 0;
            var touchedScenes = new HashSet<Scene>();
            foreach (var go in Selection.gameObjects)
            {
                var anim = go.GetComponentInChildren<Animator>();
                if (anim == null) { log.AppendLine(go.name + ": no Animator, skipped"); continue; }
                Transform pelvis = null;
                foreach (var t in anim.GetComponentsInChildren<Transform>())
                {
                    var bn = t.name.ToLower();
                    if (bn.Contains("pelvis") || bn.Contains("hips")) { pelvis = t; break; }
                    if (pelvis == null && bn.Contains("spine")) pelvis = t;
                }
                if (pelvis == null) { log.AppendLine(go.name + ": no pelvis bone, skipped"); continue; }
                float targetPelvisY = float.NaN;
                foreach (var hit in Physics.RaycastAll(pelvis.position + Vector3.up * 1.5f, Vector3.down, 8f, ~0, QueryTriggerInteraction.Ignore))
                {
                    if (hit.transform.IsChildOf(go.transform)) continue;
                    targetPelvisY = hit.point.y + 0.03f;
                    break;
                }
                if (float.IsNaN(targetPelvisY)) { log.AppendLine(go.name + ": no surface under pelvis, skipped"); continue; }
                float delta = targetPelvisY - pelvis.position.y;
                go.transform.position += Vector3.up * delta;
                EditorUtility.SetDirty(go);
                touchedScenes.Add(go.scene);
                settled++;
                log.AppendLine(go.name + ": settled, pivot " + delta.ToString("F3"));
            }
            foreach (var s in touchedScenes)
            {
                EditorSceneManager.MarkSceneDirty(s);
                EditorSceneManager.SaveScene(s);
            }
            return "JD_PSX_SETTLE settled=" + settled + "\n" + log;
        }
    }
}

using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json.Linq;
using Unity.AI.Navigation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.SceneManagement;

namespace JuegoDef.City
{
    /// <summary>
    /// Walkability check of the Ivanix-layout town: bakes one NavMesh over base + buildings + props (colliders; the
    /// buildings and props are obstacles) and computes paths between the town's anchors — plaza, the three gates and
    /// what lies beyond them (antepuerto pier, south and east bridges), the El Alto rings and the Torre esplanade, the
    /// Finca patio — writing the result as evidence. A partial or missing path is reported, never hidden.
    /// </summary>
    public static class CityIvanixNav
    {
        static readonly (string id, Vector3 p)[] Anchors =
        {
            ("spawn_pension", new Vector3(12f, 6f, 40f)),
            ("plaza", new Vector3(9f, 10f, 8f)),
            ("puerta_muelle_alta", new Vector3(5.2f, 6f, 51.5f)),
            ("antepuerto", new Vector3(5f, 2.6f, 72f)),
            ("muelle_madera", new Vector3(1f, 2.6f, 86.5f)),
            ("puerta_puente", new Vector3(5f, 4.5f, -122f)),
            ("puente_sur_orilla", new Vector3(5.1f, 3.6f, -157f)),
            ("puerta_este", new Vector3(76f, 5.5f, -39f)),
            ("puente_este_orilla", new Vector3(96f, 4.2f, -50.5f)),
            ("alto_anillo_bajo", new Vector3(-140f, 14f, -60f)),
            ("alto_anillo_alto", new Vector3(-116f, 17.5f, -12f)),
            ("alto_explanada_torre", new Vector3(-129f, 19f, -12f)),
            ("finca_patio", new Vector3(42.7f, 13f, 40.4f)),
            ("hotel", new Vector3(16f, 7f, -48f)),
            ("comandancia", new Vector3(24f, 5f, -100f)),
            ("cultura", new Vector3(-120f, 12f, 58f)),
            ("paseo_este", new Vector3(98.16f, 11.77f, 22.44f)),
            ("paseo_oeste", new Vector3(-200.22f, 16.4f, -20.48f)),
            ("orilla_sur_carretera", new Vector3(5f, 2.1f, -170f)),
        };

        [MenuItem("JuegoDef/CITY/Ivanix town: bake NavMesh + probe anchors")]
        static void Menu() => Debug.Log(BakeAndProbe(true));

        public static string BakeAndProbe(bool bake)
        {
            var baseScene = SceneManager.GetSceneByPath(CityIvanixSeed.BaseScene);
            if (!baseScene.isLoaded) { CityIvanixSeed.Open(); EditorSceneManager.OpenScene(CityIvanixDress.PropsScene, OpenSceneMode.Additive); baseScene = SceneManager.GetSceneByPath(CityIvanixSeed.BaseScene); }
            SceneManager.SetActiveScene(baseScene);
            var root = baseScene.GetRootGameObjects().First(g => g.name == "CITY_IVX_Base");
            var surface = root.GetComponentInChildren<NavMeshSurface>();
            var sw = System.Diagnostics.Stopwatch.StartNew();
            if (bake)
            {
                if (!surface)
                {
                    var nav = new GameObject("NAVMESH");
                    nav.transform.SetParent(root.transform);
                    surface = nav.AddComponent<NavMeshSurface>();
                }
                // only the public ground is walkable: buildings (roofs, eaves, balconies) and props are obstacles
                foreach (var sceneRoot in new[] { "CITY_IVX_Buildings", "CITY_IVX_Props" })
                {
                    var r = GameObject.Find(sceneRoot);
                    if (!r) continue;
                    var mod = r.GetComponent<NavMeshModifier>();
                    if (!mod) mod = r.AddComponent<NavMeshModifier>();   // Unity null: no ?? on components
                    mod.overrideArea = true;
                    mod.area = NavMesh.GetAreaFromName("Not Walkable");
                    mod.applyToChildren = true;
                    EditorSceneManager.MarkSceneDirty(r.scene);
                    EditorSceneManager.SaveScene(r.scene);
                }
                surface.collectObjects = CollectObjects.All;
                surface.useGeometry = NavMeshCollectGeometry.PhysicsColliders;
                surface.BuildNavMesh();
                var navPath = $"{CityIvanixSeed.SceneDir}/CITY_IVX_NavMesh.asset";
                AssetDatabase.DeleteAsset(navPath);
                AssetDatabase.CreateAsset(surface.navMeshData, navPath);
                surface.navMeshData = AssetDatabase.LoadAssetAtPath<NavMeshData>(navPath);
                EditorSceneManager.MarkSceneDirty(baseScene);
                EditorSceneManager.SaveScene(baseScene);
                AssetDatabase.SaveAssets();
            }
            float bakeS = (float)sw.Elapsed.TotalSeconds;

            var snapped = new Dictionary<string, Vector3?>();
            foreach (var (id, p) in Anchors)
                snapped[id] = NavMesh.SamplePosition(p, out var hit, 4f, NavMesh.AllAreas) ? hit.position : (Vector3?)null;
            var pairs = new JArray();
            var path = new NavMeshPath();
            int complete = 0, total = 0;
            var hub = "plaza";
            foreach (var (id, _) in Anchors)
            {
                if (id == hub) continue;
                total++;
                var a = snapped[hub]; var b = snapped[id];
                string status = "NO_SAMPLE"; float len = -1f;
                if (a.HasValue && b.HasValue && NavMesh.CalculatePath(a.Value, b.Value, NavMesh.AllAreas, path))
                {
                    status = path.status.ToString();
                    if (path.status == NavMeshPathStatus.PathComplete)
                    {
                        complete++;
                        len = 0f;
                        for (int k = 1; k < path.corners.Length; k++) len += Vector3.Distance(path.corners[k - 1], path.corners[k]);
                    }
                    else if (path.corners.Length > 0) len = -Vector3.Distance(path.corners.Last(), b.Value);   // gap to target
                }
                pairs.Add(new JObject { ["from"] = hub, ["to"] = id, ["status"] = status, ["length_m"] = Mathf.Round(len * 10f) / 10f,
                    ["snap"] = b.HasValue ? new JArray(R(b.Value.x), R(b.Value.y), R(b.Value.z)) : null });
            }
            var tri = NavMesh.CalculateTriangulation();
            var doc = new JObject
            {
                ["schema"] = "juego-def.city-ivx-nav/1",
                ["agent"] = NavMesh.GetSettingsNameFromID(surface.agentTypeID),
                ["bake_s"] = Mathf.Round(bakeS * 10f) / 10f,
                ["navmesh_triangles"] = tri.indices.Length / 3,
                ["complete"] = complete, ["total"] = total, ["paths"] = pairs,
            };
            var evDir = Path.GetFullPath(Path.Combine(Application.dataPath, "../../../Docs/evidence/WP-CITY-IVX-00"));
            Directory.CreateDirectory(evDir);
            File.WriteAllText(Path.Combine(evDir, "NAV_PROBE.json"), doc.ToString());
            return $"JD_CITY_IVX_NAV tris={tri.indices.Length / 3} bake={bakeS:0.0}s complete={complete}/{total} " +
                   string.Join(" ", pairs.Where(p => (string)p["status"] != "PathComplete").Select(p => $"{p["to"]}:{p["status"]}({p["length_m"]})"));
        }

        static float R(float v) => Mathf.Round(v * 100f) / 100f;
    }
}

using System.Collections.Generic;
using System.IO;
using System.Linq;
using JuegoDef.Env;
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
    /// Operator edits on the authored CITY scenes. Each operation adds or adjusts named objects only; nothing is wiped
    /// or regenerated, and every call is recorded in the evidence by the operator. Undo-able in the Editor.
    /// </summary>
    public static class CityAuthoring
    {
        static string PlanFile => Path.GetFullPath(Path.Combine(Application.dataPath, "../../../Docs/design/city/city_plan_v1.json"));
        const string NavAsset = "Assets/JuegoDef/Authored/CITY/Blockout/CITY_NavMesh.asset";

        /// <summary>Walkable junction pads at public nodes so street ribbons meet without wedge gaps.</summary>
        public static string AddJunctionPads()
        {
            var plan = JObject.Parse(File.ReadAllText(PlanFile));
            var width = new Dictionary<string, float>();
            foreach (JObject e in plan["edges"])
                foreach (var end in new[] { (string)e["a"], (string)e["b"] })
                    width[end] = Mathf.Max(width.TryGetValue(end, out var w) ? w : 0f, (float)e["width"]);
            var baseScene = SceneManager.GetSceneByPath(CityBlockoutSeed.BaseScene);
            var root = baseScene.GetRootGameObjects().First(g => g.name == "CITY_Base").transform;
            var group = root.Find("JUNCTIONS") ?? new GameObject("JUNCTIONS").transform;
            group.SetParent(root, false);
            var mat = AssetDatabase.LoadAssetAtPath<Material>("Assets/JuegoDef/Authored/CITY/Blockout/Materials/CITY_Street_Secondary.mat");
            int added = 0;
            foreach (var node in root.Find("NODES").GetComponentsInChildren<JDSpatialIdentity>())
            {
                if (!width.TryGetValue(node.stableId, out var w) || group.Find($"JUNCTION_{node.stableId}")) continue;
                float r = w / 2f + 1.2f;
                var c = node.transform.position + Vector3.up * 0.055f;
                var v = new List<Vector3> { c };
                var t = new List<int>();
                const int n = 20;
                for (int i = 0; i < n; i++)
                {
                    float a = -i * Mathf.PI * 2f / n;
                    v.Add(c + new Vector3(Mathf.Cos(a) * r, 0f, Mathf.Sin(a) * r));
                }
                for (int i = 0; i < n; i++) { t.Add(0); t.Add(1 + i); t.Add(1 + (i + 1) % n); }
                int rim = v.Count;
                for (int i = 0; i < n; i++) v.Add(v[1 + i] + Vector3.down * 0.5f);
                for (int i = 0; i < n; i++)
                {
                    int a0 = 1 + i, a1 = 1 + (i + 1) % n, b0 = rim + i, b1 = rim + (i + 1) % n;
                    t.Add(a0); t.Add(b0); t.Add(b1); t.Add(a0); t.Add(b1); t.Add(a1);
                }
                var mesh = new Mesh { name = $"JUNCTION_{node.stableId}" };
                mesh.SetVertices(v); mesh.SetTriangles(t, 0); mesh.RecalculateNormals(); mesh.RecalculateBounds();
                var go = new GameObject($"JUNCTION_{node.stableId}");
                Undo.RegisterCreatedObjectUndo(go, "City junction pad");
                go.transform.SetParent(group, false);
                go.AddComponent<MeshFilter>().sharedMesh = mesh;
                go.AddComponent<MeshRenderer>().sharedMaterial = mat;
                go.AddComponent<MeshCollider>().sharedMesh = mesh;
                go.isStatic = true;
                var id = go.AddComponent<JDSpatialIdentity>();
                id.stableId = $"JUNCTION_{node.stableId}"; id.kind = "Junction"; id.sourceId = node.stableId;
                added++;
            }
            EditorSceneManager.MarkSceneDirty(baseScene);
            return $"JD_CITY_JUNCTIONS added={added}";
        }

        /// <summary>Re-bakes the CITY NavMesh into its owned asset (all CITY scenes must be loaded).</summary>
        public static string RebakeNavMesh()
        {
            var surface = Object.FindFirstObjectByType<NavMeshSurface>();
            surface.BuildNavMesh();
            var data = surface.navMeshData;
            if (AssetDatabase.LoadAssetAtPath<NavMeshData>(NavAsset)) AssetDatabase.DeleteAsset(NavAsset);
            AssetDatabase.CreateAsset(data, NavAsset);
            surface.navMeshData = AssetDatabase.LoadAssetAtPath<NavMeshData>(NavAsset);
            EditorSceneManager.MarkSceneDirty(surface.gameObject.scene);
            EditorSceneManager.SaveOpenScenes();
            AssetDatabase.SaveAssets();
            return $"JD_CITY_NAVMESH tris={NavMesh.CalculateTriangulation().indices.Length / 3}";
        }

        /// <summary>
        /// Manual placement of a semantic building mass from the plan ledger (operator-chosen pose). Front edge centre
        /// at (x, z), facing yaw in degrees (door side), width along the frontage, depth behind it.
        /// </summary>
        public static string PlaceBuilding(string id, float x, float z, float floorY, float yawDeg, float width, float depth)
        {
            var plan = JObject.Parse(File.ReadAllText(PlanFile));
            var b = (JObject)plan["buildings"].First(t => (string)t["id"] == id);
            var sector = ((string)b["sector"]).Split('/')[0];
            var scene = SceneManager.GetSceneByPath(CityBlockoutSeed.SectorScenePath(sector));
            var root = scene.GetRootGameObjects().First(g => g.name.StartsWith($"CITY_{sector}_")).transform;
            if (root.GetComponentsInChildren<JDSpatialIdentity>().Any(i => i.stableId == id)) return $"JD_CITY_PLACE_SKIP {id} already placed";
            float height = (int)b["visualFloors"] * 3f;
            const float sink = 1.5f;
            var facing = Quaternion.Euler(0f, yawDeg, 0f) * Vector3.forward;       // from building towards street
            var back = -facing;
            var center = new Vector3(x, 0f, z) + back * depth / 2f;
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            Undo.RegisterCreatedObjectUndo(go, "City manual building");
            go.name = $"BLD_{id} {b["name"]}";
            SceneManager.MoveGameObjectToScene(go, scene);
            go.transform.SetParent(root, false);
            go.transform.position = new Vector3(center.x, floorY - sink + (height + sink) / 2f, center.z);
            go.transform.rotation = Quaternion.LookRotation(back, Vector3.up);
            go.transform.localScale = new Vector3(width, height + sink, depth);
            go.GetComponent<MeshRenderer>().sharedMaterial =
                AssetDatabase.LoadAssetAtPath<Material>($"Assets/JuegoDef/Authored/CITY/Blockout/Materials/CITY_Building_{b["scale"]}.mat");
            go.isStatic = true;
            var mod = go.AddComponent<NavMeshModifier>(); mod.overrideArea = true; mod.area = 1;
            var corners = new[] { new Vector3(-0.5f, 0, -0.5f), new Vector3(0.5f, 0, -0.5f), new Vector3(0.5f, 0, 0.5f), new Vector3(-0.5f, 0, 0.5f) };
            var ident = go.AddComponent<JDSpatialIdentity>();
            ident.stableId = id;
            ident.kind = $"SemanticBuilding:{b["scale"]}:{b["interior"]}:{b["zone"]}:{b["sector"]}";
            ident.sourceId = $"{b["name"]} | {b["access"]} | manual placement";
            ident.referenceOutline = corners.Select(c => { var w = go.transform.TransformPoint(c); return new Vector3(w.x, floorY, w.z); }).ToArray();
            var door = GameObject.CreatePrimitive(PrimitiveType.Cube);
            Object.DestroyImmediate(door.GetComponent<BoxCollider>());
            door.name = $"DOOR_{id}";
            SceneManager.MoveGameObjectToScene(door, scene);
            door.transform.position = new Vector3(x, floorY + 1.15f, z) + facing * 0.06f;
            door.transform.rotation = Quaternion.LookRotation(facing, Vector3.up);
            door.transform.localScale = new Vector3(1.2f, 2.3f, 0.12f);
            door.GetComponent<MeshRenderer>().sharedMaterial =
                AssetDatabase.LoadAssetAtPath<Material>("Assets/JuegoDef/Authored/CITY/Blockout/Materials/CITY_Door_Closed.mat");
            door.transform.SetParent(go.transform, true);
            EditorSceneManager.MarkSceneDirty(scene);
            return $"JD_CITY_PLACED {id} sector={sector}";
        }
    }
}

using System.Collections.Generic;
using System.IO;
using System.Linq;
using JuegoDef.Env;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.SceneManagement;

namespace JuegoDef.City
{
    /// <summary>
    /// Reads the authored CITY scenes (not the seed) and exports what Tools/city_blockout.py `measure` needs:
    /// every JDSpatialIdentity (zones, public axes, layer links, open spaces, seams, nodes, semantic buildings with
    /// their effective footprint) plus NavMesh path lengths between all public nodes. The scene is the authority.
    /// </summary>
    public static class CityMetricsExport
    {
        static string OutFile => Path.GetFullPath(Path.Combine(Application.dataPath, "../../../Docs/evidence/WP-CITY-SKELETON-00/SCENE_EXPORT.json"));

        [MenuItem("JuegoDef/CITY/Export scene metrics")]
        static void Menu() => Debug.Log(Export());

        public static string Export()
        {
            var items = new JArray();
            var nodes = new List<(string id, Vector3 p, string src)>();
            for (int s = 0; s < SceneManager.sceneCount; s++)
            {
                var scene = SceneManager.GetSceneAt(s);
                if (!scene.isLoaded || !scene.path.StartsWith(CityBlockoutSeed.SceneDir)) continue;
                foreach (var root in scene.GetRootGameObjects())
                foreach (var id in root.GetComponentsInChildren<JDSpatialIdentity>(true))
                {
                    var o = new JObject
                    {
                        ["id"] = id.stableId, ["kind"] = id.kind, ["source"] = id.sourceId, ["scene"] = scene.name,
                        ["object"] = id.name, ["active"] = id.gameObject.activeInHierarchy,
                    };
                    if (id.kind.StartsWith("SemanticBuilding"))
                    {
                        // effective footprint from the live transform (manual edits count), not the seed outline
                        var t = id.transform;
                        var c = new[] { new Vector3(-0.5f, -0.5f, -0.5f), new Vector3(0.5f, -0.5f, -0.5f), new Vector3(0.5f, -0.5f, 0.5f), new Vector3(-0.5f, -0.5f, 0.5f) };
                        o["footprint"] = new JArray(c.Select(v => { var w = t.TransformPoint(v); return new JArray(R(w.x), R(w.z)); }));
                        o["baseY"] = R(t.TransformPoint(new Vector3(0, -0.5f, 0)).y);
                        o["topY"] = R(t.TransformPoint(new Vector3(0, 0.5f, 0)).y);
                    }
                    else
                    {
                        o["outline"] = new JArray(id.referenceOutline.Select(v => new JArray(R(v.x), R(v.y), R(v.z))));
                        if (id.kind == "Node")
                        {
                            var p = id.transform.position;
                            o["position"] = new JArray(R(p.x), R(p.y), R(p.z));
                            nodes.Add((id.stableId, p, id.sourceId));
                        }
                    }
                    items.Add(o);
                }
            }

            // NavMesh shortest paths between every pair of nodes: public network only (area 3 = interconnection layer
            // excluded) and with every walkable exterior layer open
            var paths = PathPairs(nodes, NavMesh.AllAreas & ~(1 << 3), out var snapped);
            var pathsLayers = PathPairs(nodes, NavMesh.AllAreas, out _);
            var tri = NavMesh.CalculateTriangulation();
            var doc = new JObject
            {
                ["schema"] = "juego-def.city-scene-export/2",
                ["exportedAt"] = System.DateTime.UtcNow.ToString("o"),
                ["scenes"] = new JArray(Enumerable.Range(0, SceneManager.sceneCount).Select(SceneManager.GetSceneAt).Where(sc => sc.isLoaded).Select(sc => sc.path)),
                ["items"] = items,
                ["navmesh"] = new JObject { ["triangles"] = tri.indices.Length / 3, ["vertices"] = tri.vertices.Length },
                ["nodeSnapped"] = new JObject(snapped.Select(kv => new JProperty(kv.Key, kv.Value.HasValue))),
                ["navPaths"] = paths,
                ["navPathsWithLayers"] = pathsLayers,
            };
            Directory.CreateDirectory(Path.GetDirectoryName(OutFile));
            File.WriteAllText(OutFile, doc.ToString(Newtonsoft.Json.Formatting.None) + "\n");
            int complete = paths.Count(p => (string)p["status"] == "PathComplete");
            return $"JD_CITY_EXPORT items={items.Count} nodes={nodes.Count} publicPaths={complete}/{paths.Count} -> {OutFile}";
        }

        static JArray PathPairs(List<(string id, Vector3 p, string src)> nodes, int mask, out Dictionary<string, Vector3?> snapped)
        {
            var paths = new JArray();
            var path = new NavMeshPath();
            snapped = new Dictionary<string, Vector3?>();
            foreach (var n in nodes)
                snapped[n.id] = NavMesh.SamplePosition(n.p, out var hit, 3f, mask) ? hit.position : (Vector3?)null;
            for (int i = 0; i < nodes.Count; i++)
            for (int j = i + 1; j < nodes.Count; j++)
            {
                var a = snapped[nodes[i].id]; var b = snapped[nodes[j].id];
                float len = -1f; string status = "NO_SAMPLE";
                if (a.HasValue && b.HasValue && NavMesh.CalculatePath(a.Value, b.Value, mask, path))
                {
                    status = path.status.ToString();
                    if (path.status == NavMeshPathStatus.PathComplete)
                    {
                        len = 0f;
                        for (int k = 1; k < path.corners.Length; k++) len += Vector3.Distance(path.corners[k - 1], path.corners[k]);
                    }
                }
                paths.Add(new JObject { ["a"] = nodes[i].id, ["b"] = nodes[j].id, ["status"] = status, ["length"] = R(len) });
            }
            return paths;
        }

        static float R(float v) => Mathf.Round(v * 100f) / 100f;
    }
}

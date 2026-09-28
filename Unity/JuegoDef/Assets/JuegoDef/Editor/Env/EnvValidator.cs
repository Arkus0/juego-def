using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// Step 5 of the ENV factory: cheap validation of library units and street scenes. Catches the failure classes
    /// met while building this factory: blocked/short thresholds, service doors that open a shortcut, missing or
    /// machine-local vendor materials (white props), Unity primitives presented as architecture, banned kit pieces
    /// that carry medieval/alpine cues, floating/sunk units, facade bays without collision and duplicated
    /// coplanar tiles. Menu: JuegoDef > ENV > 5 Validate; batch: -executeMethod JuegoDef.Env.EnvValidator.RunBatch
    /// </summary>
    public static class EnvValidator
    {
        const string ReportPath = "../../Docs/evidence/WP-PROD-ENV-01/VALIDATION.json";

        [MenuItem("JuegoDef/ENV/5 Validate")]
        public static void Run() => Validate(true);

        public static void RunBatch()
        {
            int problems = Validate(false);
            EditorApplication.Exit(problems == 0 ? 0 : 1);
        }

        public static int Validate(bool log)
        {
            var policy = JObject.Parse(EnvKit.ReadText(EnvKit.Grammar + "/validation.json"));
            var report = new JObject { ["units"] = new JArray(), ["scenes"] = new JArray() };
            int total = 0;
            var units = JObject.Parse(EnvKit.ReadText(EnvKit.Specs + "/units.json"))["units"];
            foreach (JObject u in units)
            {
                var path = $"{EnvLibrary.UnitFolder}/{u["id"]}.prefab";
                EnvPreview.NewStage("Validate", ground: false);
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                var issues = new List<string>();
                if (!prefab) issues.Add("missing unit prefab " + path);
                else
                {
                    var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
                    Check(go, policy, issues, (string)u["kind"], null);
                }
                ((JArray)report["units"]).Add(new JObject { ["id"] = u["id"], ["issues"] = new JArray(issues) });
                total += issues.Count;
            }
            foreach (var guid in AssetDatabase.FindAssets("t:Scene", new[] { "Assets/JuegoDef/Scenes/ENV" }))
            {
                var scenePath = AssetDatabase.GUIDToAssetPath(guid);
                var scene = EditorSceneManager.OpenScene(scenePath);
                var issues = new List<string>();
                var stats = new JObject();
                foreach (var root in scene.GetRootGameObjects())
                    if (root.name.StartsWith("ENV01_") || root.GetComponentInChildren<JuegoDef.Dev.JDRouteProbe>(true))
                        Check(root, policy, issues, "scene", stats);
                ((JArray)report["scenes"]).Add(new JObject { ["scene"] = scenePath, ["stats"] = stats, ["issues"] = new JArray(issues) });
                total += issues.Count;
            }
            report["problems"] = total;
            File.WriteAllText(ReportPath, report.ToString(Formatting.Indented) + "\n");
            if (log) Debug.Log($"JD_ENV_VALIDATE problems={total} report={ReportPath}");
            return total;
        }

        static void Check(GameObject root, JObject policy, List<string> issues, string kind, JObject stats)
        {
            Physics.SyncTransforms();
            var banned = new HashSet<string>(policy["bannedModules"].Select(t => (string)t));
            var prefixes = policy["bannedPrefixes"].Select(t => (string)t).ToArray();
            int thresholds = 0, openOk = 0, closedOk = 0;

            // 1. module provenance: banned kit pieces, missing prefabs
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
            {
                if (PrefabUtility.IsPrefabAssetMissing(t.gameObject)) issues.Add("missing prefab asset under " + Path(t));
                if (!PrefabUtility.IsOutermostPrefabInstanceRoot(t.gameObject)) continue;
                var src = PrefabUtility.GetCorrespondingObjectFromSource(t.gameObject);
                if (!src) continue;
                var name = System.IO.Path.GetFileNameWithoutExtension(AssetDatabase.GetAssetPath(src));
                if (banned.Contains(name) || prefixes.Any(name.StartsWith)) issues.Add($"banned kit module {name} at {Path(t)}");
            }

            // 2. materials: none missing, none generated locally inside vendor intake folders (random GUIDs)
            foreach (var r in root.GetComponentsInChildren<Renderer>(true))
                foreach (var m in r.sharedMaterials)
                {
                    if (!m) { issues.Add("missing material on " + Path(r.transform)); continue; }
                    var mp = AssetDatabase.GetAssetPath(m);
                    if (mp.StartsWith("Assets/ThirdParty/Quaternius/Props/") || mp.StartsWith("Assets/ThirdParty/Quaternius/Nature/"))
                        issues.Add($"machine-local vendor material {m.name} on {Path(r.transform)}");
                }

            // 3. no Unity primitives presented as architecture
            foreach (var mf in root.GetComponentsInChildren<MeshFilter>(true))
                if (mf.sharedMesh && AssetDatabase.GetAssetPath(mf.sharedMesh).Contains("unity default resources"))
                    issues.Add("Unity primitive mesh used as content: " + Path(mf.transform));
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
                if (t.name.Contains("Proxy") || t.name.Contains("Greybox")) issues.Add("proxy/greybox object in keeper content: " + Path(t));

            // 4. facade bays carry collision
            foreach (var group in root.GetComponentsInChildren<Transform>(true).Where(t => t.name == "Front" || t.name.StartsWith("Side_")))
                foreach (Transform floor in group)
                    foreach (Transform slot in floor)
                        if (!slot.GetComponentInChildren<Collider>(true)) issues.Add("facade bay without collider: " + Path(slot));

            // 5. thresholds with the real player capsule
            var pl = policy["player"];
            float radius = (float)pl["radius"] + (float)pl["skin"], height = (float)pl["height"] + (float)pl["skin"], probe = (float)pl["probe"];
            foreach (var thr in root.GetComponentsInChildren<Transform>(true).Where(t => t.name.StartsWith("THR_")))
            {
                thresholds++;
                bool closed = thr.name.EndsWith("_Closed");
                var fwd = thr.forward;
                // feet lifted by the sill clearance (the controller steps small sills), head at the real height
                var feetY = thr.position.y + (float)pl["sillClearance"];
                var headY = thr.position.y + height;
                var start = thr.position + fwd * probe;
                var p1 = new Vector3(start.x, feetY + radius, start.z);
                var p2 = new Vector3(start.x, headY - radius, start.z);
                bool blocked = Physics.CapsuleCast(p1, p2, radius, -fwd, out var hit, probe * 2f, ~0, QueryTriggerInteraction.Ignore);
                if (closed && !blocked) issues.Add($"{thr.name} is not closed (walkable shortcut) at {Path(thr)}");
                else if (!closed && blocked) issues.Add($"{thr.name} blocked by {hit.collider.name} at {hit.point:F2} ({Path(thr)})");
                else if (closed) closedOk++;
                else openOk++;
            }

            // 6. grounded: buildings/clusters sit on their datum, nothing floats or sinks
            if (kind == "building" || kind == "cluster")
            {
                var b = EnvPreview.BoundsOf(root);
                if (Mathf.Abs(b.min.y - root.transform.position.y) > 0.3f) issues.Add($"unit bottom at {b.min.y:F2}, expected {root.transform.position.y:F2}");
            }
            if (kind == "scene")
                foreach (var bld in root.GetComponentsInChildren<Transform>(true).Where(t => t.parent && t.parent.name.StartsWith("Row_")))
                {
                    var origin = bld.position + bld.forward * 0.6f + bld.right * 0.5f + Vector3.up * 0.5f;
                    if (!Physics.Raycast(origin, Vector3.down, out var hit, 2f) || Mathf.Abs(hit.point.y - bld.position.y) > 0.06f)
                        issues.Add($"building {bld.name} threshold not on the street surface");
                }

            // 6b. party walls: a storey built without its side wall must be covered, front to back, by a neighbour's volume
            if (kind == "scene")
            {
                var buildings = root.GetComponentsInChildren<Transform>(true).Where(t => t.parent && t.parent.name.StartsWith("Row_")).ToList();
                var volumes = buildings.ToDictionary(b => b, b => EnvPreview.BoundsOf(b.gameObject));
                foreach (var bld in buildings)
                {
                    var back = bld.Find("Back");
                    var front = bld.Find("Front");
                    if (!back || !front || back.childCount == 0) continue;
                    float depth = -back.GetComponentsInChildren<Transform>().Min(t => bld.InverseTransformPoint(t.position).z);
                    float width = front.GetComponentsInChildren<Transform>().Max(t => bld.InverseTransformPoint(t.position).x) + 1f;
                    foreach (var side in new[] { "Side_L", "Side_R" })
                    {
                        var group = bld.Find(side);
                        if (!group) continue;
                        foreach (Transform floor in group)
                        {
                            if (floor.childCount > 0) continue;  // wall present
                            int f = int.Parse(floor.name.Substring(1));
                            float x = side == "Side_L" ? -0.5f : width + 0.5f;
                            foreach (var z in new[] { -1f, -depth + 0.8f })
                            {
                                var p = bld.TransformPoint(new Vector3(x, f * BuildingAssembler.Storey + 1.5f, z));
                                bool covered = buildings.Any(o => o != bld && volumes[o].Contains(p));
                                if (!covered) issues.Add($"open party wall: {bld.name} {side} storey {f} at local z {z:F1}");
                            }
                        }
                    }
                }
            }

            // 7. duplicated coplanar tiles (z-fighting)
            var seen = new HashSet<string>();
            foreach (var mf in root.GetComponentsInChildren<MeshFilter>(true).Where(m => m.sharedMesh && m.sharedMesh.name.StartsWith("Floor_")))
            {
                var key = $"{mf.sharedMesh.name}:{Mathf.Round(mf.transform.position.x * 20)}:{Mathf.Round(mf.transform.position.y * 20)}:{Mathf.Round(mf.transform.position.z * 20)}";
                if (!seen.Add(key)) issues.Add("duplicated coplanar tile " + Path(mf.transform));
            }

            if (stats != null)
            {
                stats["thresholds"] = thresholds;
                stats["openWalkable"] = openOk;
                stats["closedBlocked"] = closedOk;
                stats["renderers"] = root.GetComponentsInChildren<Renderer>(true).Length;
            }
            else if (thresholds > 0 && openOk + closedOk < thresholds) { /* issues already listed */ }
        }

        /// <summary>Negative fixture: seeds one defect per check class and asserts the validator reports each.
        /// Menu JuegoDef > ENV > 6 Validator Self-Test; result logged as JD_ENV_SELFTEST and written to the report.</summary>
        [MenuItem("JuegoDef/ENV/6 Validator Self-Test")]
        public static void SelfTest()
        {
            var policy = JObject.Parse(EnvKit.ReadText(EnvKit.Grammar + "/validation.json"));
            EnvPreview.NewStage("SelfTest", ground: false);
            var root = new GameObject("SelfTest");
            // floor under everything so thresholds are cast over a real surface
            EnvTemplates.Tiles(root.transform, "Floor_Brick", -4, 12, -4, 4, 0, null);
            // (a) banned kit module (timber-framed plaster wall)
            EnvKit.Place("Wall_Plaster_Straight", root.transform, new Vector3(-3, 0, 2), 0);
            // (b) Unity primitive presented as architecture
            var cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
            cube.transform.SetParent(root.transform, false);
            cube.transform.localPosition = new Vector3(9, 0.5f, 2);
            // (c) open public threshold blocked by a counter right behind the door
            var shop = new GameObject("Front").transform; shop.SetParent(root.transform, false);
            var f0 = new GameObject("F0").transform; f0.SetParent(shop, false);
            var slot = new GameObject("e_0").transform; slot.SetParent(f0, false); slot.localPosition = new Vector3(1, 0, 0);
            EnvKit.Place("ENV_Wall_Plaster_Shopfront", slot, Vector3.zero, 0);
            EnvKit.Place("ENV_Shopfront_Door_Open", slot, Vector3.zero, 0);
            new GameObject("THR_Public_Shop").transform.SetParent(slot, false);
            slot.Find("THR_Public_Shop").localPosition = new Vector3(-0.2f, 0, 0);
            EnvKit.Place("ENV_Counter_Shop", root.transform, new Vector3(0.8f, 0, -0.7f), 0);
            // (d) "closed" service threshold with nothing closing it (a shortcut)
            var bare = new GameObject("F0b").transform; bare.SetParent(shop, false);
            var vslot = new GameObject("V_0").transform; vslot.SetParent(bare, false); vslot.localPosition = new Vector3(5, 0, 0);
            EnvKit.Place("ENV_Wall_Plaster_Clean_Door", vslot, Vector3.zero, 0);
            new GameObject("THR_Service_Closed").transform.SetParent(vslot, false);
            // (e) machine-local vendor material (the "white props" class)
            var barrel = (GameObject)PrefabUtility.InstantiatePrefab(EnvKit.Module("Barrel"), root.transform);
            barrel.transform.localPosition = new Vector3(7, 0, -2);
            // (f) duplicated coplanar tile
            EnvKit.Place("Floor_Brick", root.transform, new Vector3(-3, 0, -3), 0);
            // (g) party wall hidden behind a shallower neighbour (hole at the rear)
            var row = new GameObject("Row_SelfTest").transform;
            row.SetParent(root.transform, false);
            row.localPosition = new Vector3(20, 0, 0);
            BuildingAssembler.Build(new BuildingSpec { id = "Shallow", type = "closed_residential", bays = 2, depth = 6, floors = 2, seed = 1, palette = "cream_green", dress = false, partyRight = 2 }, row);
            var deep = BuildingAssembler.Build(new BuildingSpec { id = "Deep", type = "closed_residential", bays = 2, depth = 8, floors = 2, seed = 2, palette = "cream_green", dress = false, partyLeft = 2 }, row);
            deep.transform.localPosition = new Vector3(4, 0, 0);
            Physics.SyncTransforms();

            var issues = new List<string>();
            Check(root, policy, issues, "scene", new JObject());
            var expect = new Dictionary<string, string>
            {
                { "banned module", "banned kit module Wall_Plaster_Straight" },
                { "primitive", "Unity primitive mesh" },
                { "blocked open threshold", "THR_Public_Shop blocked" },
                { "open service shortcut", "THR_Service_Closed is not closed" },
                { "machine-local material", "machine-local vendor material" },
                { "duplicated tile", "duplicated coplanar tile" },
                { "open party wall", "open party wall: Deep" },
            };
            var result = new JObject();
            int missed = 0;
            foreach (var kv in expect)
            {
                bool hit = issues.Any(i => i.Contains(kv.Value));
                result[kv.Key] = hit ? "DETECTED" : "MISSED";
                if (!hit) missed++;
            }
            var report = File.Exists(ReportPath) ? JObject.Parse(File.ReadAllText(ReportPath)) : new JObject();
            report["selfTest"] = new JObject { ["expected"] = result, ["missed"] = missed, ["issuesReported"] = new JArray(issues) };
            File.WriteAllText(ReportPath, report.ToString(Formatting.Indented) + "\n");
            Debug.Log($"JD_ENV_SELFTEST missed={missed} {result.ToString(Formatting.None)}");
        }

        static string Path(Transform t)
        {
            var parts = new List<string>();
            for (var x = t; x != null && parts.Count < 5; x = x.parent) parts.Add(x.name);
            parts.Reverse();
            return string.Join("/", parts);
        }
    }
}

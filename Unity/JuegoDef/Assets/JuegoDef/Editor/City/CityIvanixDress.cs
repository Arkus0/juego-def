using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using JuegoDef.Env;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace JuegoDef.City
{
    /// <summary>
    /// One-shot dressing of the Ivanix-layout town: the ENV01 day light on the base scene and the street props
    /// (Tools/city_ivanix/reconstruction/city_props_v1.json) in their own authored scene, CITY_IVX_Props.
    /// Each prop is dropped by a ray onto the ground (terrain, terraces, quay, finca); a prop whose ray lands on a
    /// building is skipped and counted. Then it is an entity (CityEntities): seated on its own footprint, pushed out
    /// of whatever it touches or not placed at all, and given a body. Refuses to re-dress once the props scene exists.
    /// </summary>
    public static class CityIvanixDress
    {
        public const string PropsScene = CityIvanixSeed.SceneDir + "/CITY_IVX_Props.unity";
        public static string DefaultProps => Path.GetFullPath(Path.Combine(Application.dataPath, "../../../Tools/city_ivanix/reconstruction/city_props_v1.json"));
        static readonly string[] GroundGroups = { "TERRAIN", "EL_ALTO_TERRACES", "BRIDGES_QUAY", "FINCA_DEL_CACIQUE", "PASEO_MURALLA" };

        [MenuItem("JuegoDef/CITY/Dress Ivanix town (light + props, one-shot)")]
        static void Menu() => Debug.Log(Dress(DefaultProps));

        public static string Dress(string propsPath)
        {
            CityIvanixSeed.RefuseIfFrozen("CityIvanixDress.Dress");
            if (File.Exists(PropsScene)) throw new InvalidOperationException("JD_CITY_IVX_ALREADY_DRESSED: the props scene is authored now.");
            CityIvanixSeed.Open();
            var baseScene = SceneManager.GetSceneByPath(CityIvanixSeed.BaseScene);
            SceneManager.SetActiveScene(baseScene);

            // light: the ENV01 Atlantic day (sun, sky, fog, ambient, post volume) on the base scene
            var oldSun = baseScene.GetRootGameObjects().SelectMany(r => r.GetComponentsInChildren<Light>(true)).FirstOrDefault(l => l.type == LightType.Directional);
            if (oldSun) oldSun.gameObject.name = "Directional Light";
            EnvLighting.Apply("day");                 // builds sun, global volume and sky the city look then retunes
            EditorSceneManager.MarkSceneDirty(baseScene);
            EditorSceneManager.SaveScene(baseScene);
            CityIvanixLook.Apply();

            var doc = JObject.Parse(File.ReadAllText(propsPath));
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive);
            EditorSceneManager.SaveScene(scene, PropsScene);
            var root = new GameObject("CITY_IVX_Props");
            SceneManager.MoveGameObjectToScene(root, scene);
            var id = root.AddComponent<JDSpatialIdentity>();
            id.stableId = "CITY_IVX_Props"; id.kind = "AuthoredScene"; id.sourceId = "Ivanix layout · ENV01 props v1"; id.referenceOutline = new Vector3[0];

            Physics.SyncTransforms();
            int placed = 0, onBuilding = 0, noGround = 0, missing = 0, shifted = 0, rejected = 0;
            var missingNames = new HashSet<string>();
            var rejectedBy = new Dictionary<string, int>();
            var rejectedAt = new JArray();
            var groups = new Dictionary<string, Transform>();
            Func<Collider, bool> isGround = c => IsGround(c.transform);
            Func<Collider, bool> isTerrain = c => Under(c.transform, "TERRAIN");
            var bScene = SceneManager.GetSceneByPath(CityIvanixSeed.BuildingsScene);
            CityEntities.IndexBuildings(bScene.IsValid() ? bScene.GetRootGameObjects().FirstOrDefault()?.transform : null);
            foreach (JObject it in doc["items"])
            {
                string m = (string)it["m"], g = (string)it["g"];
                if (!CityEntities.Exists(m)) { missing++; missingNames.Add(m); continue; }
                float x = (float)it["p"][0], z = (float)it["p"][1];
                float y;
                if (it["y"] != null) y = (float)it["y"];
                else
                {
                    // eaves, awnings and balconies overhang the street: take the highest ground hit, not the first hit
                    var hits = Physics.RaycastAll(new Vector3(x, 90f, z), Vector3.down, 200f).Where(h => h.collider.gameObject.scene != scene).ToArray();
                    var ground = hits.Where(h => IsGround(h.collider.transform)).OrderBy(h => h.distance).ToList();
                    if (ground.Count == 0) { if (hits.Length == 0) noGround++; else onBuilding++; continue; }
                    var top = ground[0];
                    // a building floor slab between the ray and the ground means the spot is inside a building
                    if (hits.Any(h => !IsGround(h.collider.transform) && h.point.y < top.point.y + 2.0f && h.point.y > top.point.y + 0.05f)) { onBuilding++; continue; }
                    y = top.point.y;
                }
                if (it["dy"] != null) y += (float)it["dy"];      // goods standing on a table
                if (!groups.TryGetValue(g, out var parent)) groups[g] = parent = EnvKit.Group(root.transform, g);
                var go = CityEntities.Place(m, parent, new Vector3(x, y, z), (float)it["r"], it["s"] != null ? Vector3.one * (float)it["s"] : (Vector3?)null);
                // every object is an entity: seated on its own footprint, pushed out of what it touches, or not placed
                if (it["fix"] == null && it["dy"] == null)
                {
                    if (it["y"] == null) CityEntities.Settle(go, isGround, it["tilt"] != null);
                    float maxShift = it["shift"] != null ? (float)it["shift"] : 0.8f;
                    // trees answer to buildings, walls and railings with their crown; small street things only to their trunk
                    var ignore = m.Contains("Tree") || m.Contains("Palmera") ? (Func<Collider, bool>)(c => isTerrain(c) || c.gameObject.scene == scene) : isTerrain;
                    bool fits = CityEntities.Resolve(go, ignore, maxShift, out var moved, out var blocker);
                    // a tree that does not fit is planted younger: a smaller crown before giving up the spot
                    for (int age = 0; !fits && (m.Contains("Tree") || m.Contains("Palmera")) && age < 2; age++)
                    {
                        go.transform.localScale *= 0.8f;
                        fits = CityEntities.Resolve(go, ignore, maxShift, out moved, out blocker);
                    }
                    if (!fits)
                    {
                        UnityEngine.Object.DestroyImmediate(go);
                        rejected++;
                        rejectedBy[g + ":" + m] = rejectedBy.TryGetValue(g + ":" + m, out var k) ? k + 1 : 1;
                        rejectedAt.Add(new JObject { ["m"] = m, ["g"] = g, ["p"] = new JArray(x, z), ["blocker"] = blocker });
                        continue;
                    }
                    if (fits && moved > 0.05f && it["y"] == null)
                    {
                        // pushed sideways: it must still stand on the same level (not over a step, a ramp or a drop)
                        var p0 = go.transform.position;
                        var gy = CityEntities.GroundY(p0.x, p0.z, y, isGround);
                        if (gy == null || Mathf.Abs(gy.Value - y) > 0.4f) { fits = false; blocker = "level"; }
                        else { go.transform.position = new Vector3(p0.x, gy.Value, p0.z); CityEntities.Settle(go, isGround, it["tilt"] != null); }
                    }
                    if (!fits)
                    {
                        UnityEngine.Object.DestroyImmediate(go);
                        rejected++;
                        rejectedBy[g + ":" + m] = rejectedBy.TryGetValue(g + ":" + m, out var k2) ? k2 + 1 : 1;
                        rejectedAt.Add(new JObject { ["m"] = m, ["g"] = g, ["p"] = new JArray(x, z), ["blocker"] = blocker });
                        continue;
                    }
                    if (moved > 0.05f) shifted++;
                }
                CityEntities.EnsureBody(go);
                foreach (var tr in go.GetComponentsInChildren<Transform>(true)) tr.gameObject.isStatic = true;
                Physics.SyncTransforms();
                placed++;
            }
            // boats are tied to the bollards: a bow line and a stern line to the nearest free bollard on the deck
            int lines = 0;
            if (groups.TryGetValue("PUERTO", out var port))
            {
                var bollards = port.Cast<Transform>().Where(t => t.name.StartsWith("ENV_Bollard")).ToList();
                var rope = AssetDatabase.LoadAssetAtPath<Material>("Assets/JuegoDef/City/Props/Materials/DC_Rope.mat");
                var ropes = EnvKit.Group(root.transform, "AMARRAS");
                var used = new HashSet<Transform>();
                foreach (var boat in port.Cast<Transform>().Where(t => t.name.StartsWith("CITY_Boat")).ToList())
                    foreach (var cleat in new[] { new Vector3(0f, 1.25f, 3.1f), new Vector3(0.95f, 1.12f, -2.4f) })
                    {
                        var a0 = boat.TransformPoint(cleat);
                        var b0 = bollards.Where(bl => !used.Contains(bl)).OrderBy(bl => (bl.position - a0).sqrMagnitude).FirstOrDefault();
                        // the stern line leaves from the quarter on the bollard's side, clear of the net drum
                        if (b0 != null && cleat.x != 0 && boat.InverseTransformPoint(b0.position).x < 0) a0 = boat.TransformPoint(new Vector3(-cleat.x, cleat.y, cleat.z));
                        if (b0 == null || (b0.position - a0).magnitude > 9f) continue;
                        used.Add(b0);
                        var top = b0.position + Vector3.up * 0.5f;
                        CityEntities.Rope(ropes, "CABO_" + boat.name, a0, top, 0.12f + 0.04f * (top - a0).magnitude, 0.018f, rope);
                        lines++;
                    }
            }
            File.WriteAllText(Path.GetFullPath(Path.Combine(Application.dataPath, "../../../Docs/evidence/WP-CITY-IVX-00/DRESS_ENTITIES.json")),
                new JObject { ["placed"] = placed, ["mooring_lines"] = lines, ["shifted"] = shifted, ["rejected"] = rejected, ["on_building"] = onBuilding, ["no_ground"] = noGround,
                              ["rejected_by"] = JObject.FromObject(rejectedBy), ["rejected_at"] = rejectedAt }.ToString());
            EditorSceneManager.SaveScene(scene, PropsScene);
            SceneManager.SetActiveScene(baseScene);
            return $"JD_CITY_IVX_DRESSED props={placed} lines={lines} shifted={shifted} rejected={rejected} on_building={onBuilding} no_ground={noGround} missing={missing} {string.Join(",", missingNames)} | {string.Join(" ", rejectedBy.Select(kv => kv.Key + "x" + kv.Value))}";
        }

        static bool Under(Transform t, string group)
        {
            for (var p = t; p != null; p = p.parent)
                if (p.name == group) return true;
            return false;
        }

        static bool IsGround(Transform t)
        {
            for (var p = t; p != null; p = p.parent)
                if (GroundGroups.Contains(p.name)) return true;
            return false;
        }
    }
}

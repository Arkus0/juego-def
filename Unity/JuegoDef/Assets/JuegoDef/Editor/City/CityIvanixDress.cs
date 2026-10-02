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
    /// building is skipped and counted. Refuses to re-dress once the props scene exists.
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
            int placed = 0, onBuilding = 0, noGround = 0, missing = 0;
            var missingNames = new HashSet<string>();
            var groups = new Dictionary<string, Transform>();
            foreach (JObject it in doc["items"])
            {
                string m = (string)it["m"], g = (string)it["g"];
                if (!EnvKit.HasModule(m)) { missing++; missingNames.Add(m); continue; }
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
                var go = EnvKit.Place(m, parent, new Vector3(x, y, z), (float)it["r"], it["s"] != null ? Vector3.one * (float)it["s"] : (Vector3?)null);
                go.isStatic = true;
                placed++;
            }
            EditorSceneManager.SaveScene(scene, PropsScene);
            SceneManager.SetActiveScene(baseScene);
            return $"JD_CITY_IVX_DRESSED props={placed} on_building={onBuilding} no_ground={noGround} missing={missing} {string.Join(",", missingNames)}";
        }

        static bool IsGround(Transform t)
        {
            for (var p = t; p != null; p = p.parent)
                if (GroundGroups.Contains(p.name)) return true;
            return false;
        }
    }
}

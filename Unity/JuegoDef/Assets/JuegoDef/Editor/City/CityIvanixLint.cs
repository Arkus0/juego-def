using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace JuegoDef.City
{
    /// <summary>
    /// Semantic and overlap audit of the Ivanix-layout town (owner walk 2026-10-02: "si algo no lo hubiese puesto un
    /// humano, o falta algo que habría puesto un humano, hay que arreglarlo"): every wall, tapia, railing, parapet,
    /// stair and prop is tested against the buildings' colliders (a garden wall through a house, a bench inside a
    /// facade); every tapia must touch a building at both ends (a free-standing wall in a square is wrong); every prop
    /// must stand on the ground it was meant for. Findings go to Docs/evidence/WP-CITY-IVX-00/LINT.json with positions.
    /// </summary>
    public static class CityIvanixLint
    {
        [MenuItem("JuegoDef/CITY/Ivanix town: semantic + overlap audit")]
        static void Menu() => Debug.Log(Run());

        public static string Run()
        {
            Physics.SyncTransforms();
            var buildingsRoot = GameObject.Find("CITY_IVX_Buildings");
            var baseRoot = GameObject.Find("CITY_IVX_Base");
            var propsRoot = GameObject.Find("CITY_IVX_Props");
            var buildingCols = new HashSet<Collider>(buildingsRoot.GetComponentsInChildren<Collider>(true));
            var findings = new JArray();
            var counts = new Dictionary<string, int>();
            void Add(string cat, Transform t, Vector3 p, string note)
            {
                counts[cat] = counts.TryGetValue(cat, out var c) ? c + 1 : 1;
                if (findings.Count < 400)
                    findings.Add(new JObject { ["cat"] = cat, ["obj"] = Path(t), ["pos"] = new JArray(R(p.x), R(p.y), R(p.z)), ["note"] = note });
            }
            Transform Bld(Collider c)
            {
                var t = c.transform;
                while (t.parent && t.parent.gameObject != buildingsRoot) t = t.parent;
                return t;
            }

            // 1) base structures that cut into a house
            foreach (var group in new[] { "TAPIAS", "PASEO_MURALLA", "EL_ALTO_TERRACES", "FINCA_DEL_CACIQUE", "BRIDGES_QUAY" })
            {
                var g = baseRoot.transform.Find(group);
                if (!g) continue;
                foreach (var bc in g.GetComponentsInChildren<BoxCollider>(true))
                {
                    var t = bc.transform;
                    var half = Vector3.Scale(bc.size, t.lossyScale) * 0.5f - Vector3.one * 0.08f;   // touching is fine, cutting in is not
                    if (group == "TAPIAS") half.z -= 0.35f;    // a garden wall meets the house corner at its ends: only its run counts
                    if (group == "PASEO_MURALLA" && bc.name == "MURO") half.x -= 0.5f;   // a house built against the wall is right; cutting into it is not
                    if (half.x <= 0 || half.y <= 0 || half.z <= 0) continue;
                    var hits = Physics.OverlapBox(t.TransformPoint(bc.center), half, t.rotation).Where(buildingCols.Contains).ToList();
                    if (hits.Count > 0) Add($"{group}_IN_BUILDING", t, t.position, Bld(hits[0]).name);
                }
            }
            // 2) free-standing tapias: both ends must meet a building
            var tapias = baseRoot.transform.Find("TAPIAS");
            if (tapias)
                foreach (Transform run in tapias)
                {
                    var walls = run.GetComponentsInChildren<BoxCollider>().Where(c => c.name == "MURO" || c.name == "PORTILLA").ToList();
                    if (walls.Count == 0) continue;
                    var first = walls.First().transform; var last = walls.Last().transform;
                    var e0 = first.position - first.forward * (first.lossyScale.z * 0.5f);
                    var e1 = last.position + last.forward * (last.lossyScale.z * 0.5f);
                    bool touch0 = Physics.OverlapSphere(e0, 0.9f).Any(buildingCols.Contains);
                    bool touch1 = Physics.OverlapSphere(e1, 0.9f).Any(buildingCols.Contains);
                    if (!touch0 || !touch1) Add("TAPIA_FREE_END", run, touch0 ? e1 : e0, touch0 || touch1 ? "one end loose" : "free-standing");
                }
            // 3) props inside houses or floating
            CityEntities.IndexBuildings(buildingsRoot ? buildingsRoot.transform : null);
            if (propsRoot)
                foreach (Transform group in propsRoot.transform)
                foreach (Transform prop in group)
                {
                    if (group.name == "AMARRAS") continue;          // mooring lines hang between a boat and a bollard
                    var rs = prop.GetComponentsInChildren<Renderer>();
                    if (rs.Length == 0) continue;
                    var b = rs[0].bounds; foreach (var r in rs) b.Encapsulate(r.bounds);
                    // the entity's own volume (trees: trunk and crown heart), the same definition the placement used
                    var lb = CityEntities.LocalBox(prop.gameObject);
                    var hits = Physics.OverlapBox(prop.TransformPoint(lb.center + Vector3.up * 0.11f), Vector3.Scale(lb.extents - new Vector3(0.03f, 0.11f, 0.03f), prop.lossyScale), prop.rotation).Where(buildingCols.Contains).ToList();
                    if (hits.Count > 0) Add("PROP_IN_BUILDING", prop, prop.position, $"{group.name}: {Bld(hits[0]).name}");
                    if (CityEntities.InsidePlan(prop.gameObject, out var host)) Add("PROP_IN_BUILDING_PLAN", prop, prop.position, $"{group.name}: {host}");
                    if (group.name != "PUERTO" && !Physics.Raycast(prop.position + Vector3.up * 0.3f, Vector3.down, 0.8f))
                        Add("PROP_FLOATING", prop, prop.position, group.name);
                }
            var doc = new JObject { ["schema"] = "juego-def.city-ivx-lint/1", ["counts"] = JObject.FromObject(counts), ["findings"] = findings };
            var evDir = System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath, "../../../Docs/evidence/WP-CITY-IVX-00"));
            Directory.CreateDirectory(evDir);
            File.WriteAllText(System.IO.Path.Combine(evDir, "LINT.json"), doc.ToString());
            return "JD_CITY_IVX_LINT " + (counts.Count == 0 ? "clean" : string.Join(" ", counts.Select(kv => $"{kv.Key}={kv.Value}")));
        }

        static string Path(Transform t)
        {
            var parts = new List<string>();
            for (var x = t; x != null && parts.Count < 4; x = x.parent) parts.Insert(0, x.name);
            return string.Join("/", parts);
        }

        static float R(float v) => Mathf.Round(v * 100f) / 100f;
    }
}

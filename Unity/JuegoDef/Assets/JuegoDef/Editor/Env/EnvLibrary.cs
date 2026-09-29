using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// Step 3 of the ENV factory: builds every unit in Env/Specs/units.json into Derived/ENV/Units/&lt;id&gt;.prefab,
    /// captures a street-level preview into the WP evidence and writes the searchable library index
    /// Docs/asset_catalog/env_library.json (demand rows, modules used, size, prefab, preview).
    /// </summary>
    public static class EnvLibrary
    {
        public const string UnitFolder = EnvKit.Derived + "/Units";
        const string EvidenceUnits = "../../Docs/evidence/WP-PROD-ENV-01/units";
        const string IndexPath = "../../Docs/asset_catalog/env_library.json";

        [MenuItem("JuegoDef/ENV/3 Build Library")]
        public static void BuildAll() => Build(null);

        public static void Build(ICollection<string> only)
        {
            EnvKit.ClearCache();
            BuildingAssembler.ReloadGrammar();
            EnvKit.EnsureFolder(UnitFolder);
            var spec = JObject.Parse(EnvKit.ReadText(EnvKit.Specs + "/units.json"));
            var index = new JArray();
            var old = File.Exists(IndexPath) ? JObject.Parse(File.ReadAllText(IndexPath)) : null;
            foreach (JObject u in spec["units"])
            {
                var id = (string)u["id"];
                if (only != null && !only.Contains(id))
                {
                    var kept = old?["units"]?.FirstOrDefault(e => (string)e["id"] == id);
                    if (kept != null) index.Add(kept);
                    continue;
                }
                var stage = EnvPreview.NewStage("Stage");
                var root = BuildUnit(u, stage);
                var prefabPath = $"{UnitFolder}/{id}.prefab";
                PrefabUtility.SaveAsPrefabAsset(root, prefabPath);
                var preview = $"{EvidenceUnits}/{id}.jpg";
                string kind = (string)u["kind"];
                EnvPreview.CaptureObject(root, preview, 28f, kind == "building" ? 10f : 32f);
                var b = EnvPreview.BoundsOf(root);
                index.Add(new JObject
                {
                    ["id"] = id,
                    ["title"] = u["title"],
                    ["kind"] = kind,
                    ["demand"] = u["demand"],
                    ["prefab"] = prefabPath,
                    ["preview"] = $"Docs/evidence/WP-PROD-ENV-01/units/{id}.jpg",
                    ["size"] = new JArray(Round(b.size.x), Round(b.size.y), Round(b.size.z)),
                    ["request"] = u["building"] ?? u["params"] ?? (JToken)"cluster",
                    ["modules"] = ModulesUsed(root),
                    ["notes"] = u["notes"],
                });
                Debug.Log($"JD_ENV_UNIT {id} size={b.size}");
            }
            if (only == null)
            {
                // a unit removed/renamed in units.json must not linger as a prefab, preview or lineage record
                var ids = new HashSet<string>(spec["units"].Select(u => (string)u["id"]));
                foreach (var guid in AssetDatabase.FindAssets("t:Prefab", new[] { UnitFolder }))
                {
                    var path = AssetDatabase.GUIDToAssetPath(guid);
                    if (!ids.Contains(Path.GetFileNameWithoutExtension(path))) AssetDatabase.DeleteAsset(path);
                }
                foreach (var file in Directory.GetFiles(EvidenceUnits, "*.jpg"))
                    if (!ids.Contains(Path.GetFileNameWithoutExtension(file))) File.Delete(file);
            }
            var outJson = new JObject { ["schemaVersion"] = 1, ["generator"] = "JuegoDef > ENV > 3 Build Library", ["units"] = index };
            File.WriteAllText(IndexPath, outJson.ToString(Formatting.Indented) + "\n");
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();
            Debug.Log($"JD_ENV_LIBRARY units={index.Count}");
        }

        static float Round(float v) => Mathf.Round(v * 100f) / 100f;

        public static GameObject BuildUnit(JObject u, Transform parent)
        {
            var id = (string)u["id"];
            var root = new GameObject(id);
            root.transform.SetParent(parent, false);
            var p = u["params"] as JObject;
            switch ((string)u["kind"])
            {
                case "building":
                    var bs = u["building"].ToObject<BuildingSpec>();
                    bs.id = "Building";
                    BuildingAssembler.Build(bs, root.transform);
                    break;
                case "street_ground":
                    EnvTemplates.StreetGround(root.transform, (float)p["length"], (float)p["width"], (string)p["style"] ?? "kerbed", (float?)p["pavement"] ?? -1f, (int?)p["seed"] ?? 1);
                    break;
                case "plaza":
                    EnvTemplates.Plaza(root.transform, (float)p["w"], (float)p["d"], (int?)p["trees"] ?? 2, (bool?)p["terrace"] ?? true, (int?)p["seed"] ?? 1, (bool?)p["floor"] ?? true);
                    break;
                case "stepped_connector":
                    EnvTemplates.SteppedConnector(root.transform, (int)p["height"], (int?)p["terraceBays"] ?? 2, (bool?)p["landing"] ?? true);
                    break;
                case "quay_edge":
                    EnvTemplates.QuayEdge(root.transform, (float)p["length"], (bool?)p["railing"] ?? false, (float?)p["depth"] ?? 6f,
                        (float?)p["overlookFrom"] ?? -1f, (float?)p["overlookTo"] ?? -1f, (float?)p["stepsAt"] ?? -1f, (float?)p["slipwayAt"] ?? -1f,
                        (int?)p["boats"] ?? 0, (int?)p["seed"] ?? 1, (bool?)p["water"] ?? true, (bool?)p["lamps"] ?? true);
                    break;
                case "yard_boundary":
                    EnvTemplates.YardBoundary(root.transform, (float)p["length"], (int?)p["gateAt"] ?? 1);
                    break;
                case "cluster":
                    EnvTemplates.Cluster(root.transform, "Cluster", u["parts"].Select(t =>
                        ((string)t[0], new Vector3((float)t[1], (float)t[2], (float)t[3]), (float)t[4])));
                    break;
                default:
                    throw new System.ArgumentException("ENV_UNKNOWN_UNIT_KIND " + u["kind"]);
            }
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
                if (!t.GetComponent<Light>()) GameObjectUtility.SetStaticEditorFlags(t.gameObject, EnvKit.StaticFlags);
            return root;
        }

        /// <summary>Source module names (outermost prefab instances) with use counts — the unit's bill of materials.</summary>
        public static JObject ModulesUsed(GameObject root)
        {
            var counts = new SortedDictionary<string, int>();
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
            {
                if (!PrefabUtility.IsOutermostPrefabInstanceRoot(t.gameObject)) continue;
                var src = PrefabUtility.GetCorrespondingObjectFromSource(t.gameObject);
                if (!src) continue;
                var name = Path.GetFileNameWithoutExtension(AssetDatabase.GetAssetPath(src));
                counts[name] = counts.TryGetValue(name, out var c) ? c + 1 : 1;
            }
            return JObject.FromObject(counts);
        }
    }
}

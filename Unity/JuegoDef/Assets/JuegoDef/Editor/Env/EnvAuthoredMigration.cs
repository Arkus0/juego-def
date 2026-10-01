using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

namespace JuegoDef.Env
{
    /// <summary>One bounded freeze of the inspected ENV01, never a city/layout generator.</summary>
    public static class EnvAuthoredMigration
    {
        public const string Source = "Assets/JuegoDef/Scenes/ENV/ENV01_Casco_District.unity";
        public const string Target = "Assets/JuegoDef/Scenes/ENV/ENV01_AUTHORED.unity";
        public const string Snapshot = "Assets/JuegoDef/Authored/ENV01/";
        public static string Evidence => Path.GetFullPath("../../Docs/evidence/WP-ENV01-AUTHORED-01");
        static Queue<GameObject> unpack;
        static int unpacked;

        static Transform[] All() => SceneManager.GetActiveScene().GetRootGameObjects()
            .SelectMany(g => g.GetComponentsInChildren<Transform>(true)).ToArray();
        static string N(float f) => f.ToString("0.000", CultureInfo.InvariantCulture);
        static string V(Vector3 v) => N(v.x) + "," + N(v.y) + "," + N(v.z);
        static string Matrix(Transform t) => string.Join(",", Enumerable.Range(0, 16).Select(i => N(t.localToWorldMatrix[i])));
        static string Asset(Object o)
        {
            if (!o) return "NULL";
            string guid; long local;
            AssetDatabase.TryGetGUIDAndLocalFileIdentifier(o, out guid, out local);
            string p = AssetDatabase.GetAssetPath(o);
            if (p.StartsWith(Snapshot, StringComparison.Ordinal)) p = EnvKit.Derived + "/" + p.Substring(Snapshot.Length);
            return p + "#" + local + ":" + o.name;
        }
        static string Digest(IEnumerable<string> lines)
        {
            using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(Encoding.UTF8.GetBytes(string.Join("\n", lines.OrderBy(x => x, StringComparer.Ordinal))))).Replace("-", "").ToLowerInvariant();
        }
        public static void Write(string name, JToken value)
        {
            Directory.CreateDirectory(Evidence);
            File.WriteAllText(Path.Combine(Evidence, name + ".json"), value.ToString(Newtonsoft.Json.Formatting.Indented) + "\n");
        }

        /// <summary>Compare the full renderer/collider/light population, not a few buildings.</summary>
        public static JObject Audit(string stage)
        {
            var all = All();
            var renderers = all.SelectMany(t => t.GetComponents<Renderer>()).ToArray();
            var colliders = all.SelectMany(t => t.GetComponents<Collider>()).ToArray();
            var lights = all.SelectMany(t => t.GetComponents<Light>()).ToArray();
            var renderLines = new List<string>();
            foreach (var r in renderers)
            {
                var filter = r.GetComponent<MeshFilter>();
                var skinned = r as SkinnedMeshRenderer;
                var mesh = filter ? filter.sharedMesh : skinned ? skinned.sharedMesh : null;
                renderLines.Add(Matrix(r.transform) + "|" + r.GetType().Name + "|" + r.enabled + "|" + r.gameObject.activeInHierarchy
                    + "|" + Asset(mesh) + "|" + string.Join(";", r.sharedMaterials.Select(Asset)) + "|" + r.shadowCastingMode + "|" + r.receiveShadows);
            }
            var colliderLines = new List<string>();
            foreach (var c in colliders)
            {
                string shape = "";
                if (c is BoxCollider b) shape = V(b.center) + "/" + V(b.size);
                else if (c is MeshCollider m) shape = Asset(m.sharedMesh) + "/" + m.convex + "/" + m.cookingOptions;
                else if (c is SphereCollider s) shape = V(s.center) + "/" + N(s.radius);
                else if (c is CapsuleCollider cap) shape = V(cap.center) + "/" + N(cap.radius) + "/" + N(cap.height) + "/" + cap.direction;
                colliderLines.Add(Matrix(c.transform) + "|" + c.GetType().Name + "|" + c.enabled + "|" + c.isTrigger + "|"
                    + c.gameObject.activeInHierarchy + "|" + shape + "|" + Asset(c.sharedMaterial));
            }
            var missing = new List<string>();
            foreach (var t in all)
            {
                int n = GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject);
                if (n > 0) missing.Add(t.name + ": missing scripts=" + n);
                foreach (var component in t.GetComponents<MonoBehaviour>().Where(c => c))
                {
                    var so = new SerializedObject(component);
                    var p = so.GetIterator();
                    while (p.Next(true))
                        if (p.propertyType == SerializedPropertyType.ObjectReference && p.objectReferenceValue == null && p.objectReferenceInstanceIDValue != 0)
                            missing.Add(t.name + ":" + component.GetType().Name + ":" + p.propertyPath);
                }
            }
            int missingMeshes = all.SelectMany(t => t.GetComponents<MeshFilter>()).Count(f => !f.sharedMesh);
            int missingMaterials = renderers.Sum(r => r.sharedMaterials.Count(m => !m));
            var identities = all.SelectMany(t => t.GetComponents<JDSpatialIdentity>()).ToArray();
            var duplicateIds = identities.GroupBy(i => i.stableId).Where(g => string.IsNullOrEmpty(g.Key) || g.Count() != 1).Select(g => g.Key).ToArray();
            var lightLines = lights.Select(l => Matrix(l.transform) + "|" + l.type + "|" + N(l.intensity) + "|" + N(l.range)
                + "|" + l.color + "|" + l.enabled + "|" + l.gameObject.activeInHierarchy);
            var result = new JObject
            {
                ["stage"] = stage, ["scene"] = SceneManager.GetActiveScene().path, ["objects"] = all.Length,
                ["renderers"] = renderers.Length, ["colliders"] = colliders.Length, ["lights"] = lights.Length,
                ["rendererDigest"] = Digest(renderLines), ["colliderDigest"] = Digest(colliderLines), ["lightDigest"] = Digest(lightLines),
                ["missingReferences"] = JArray.FromObject(missing), ["missingMeshes"] = missingMeshes, ["missingMaterials"] = missingMaterials,
                ["temporaryMeshes"] = all.SelectMany(t => t.GetComponents<MeshFilter>()).Count(f => f.sharedMesh && !EditorUtility.IsPersistent(f.sharedMesh)),
                ["duplicateIds"] = JArray.FromObject(duplicateIds),
                ["scripts"] = JArray.FromObject(all.SelectMany(t => t.GetComponents<MonoBehaviour>()).Where(c => c).GroupBy(c => c.GetType().FullName)
                    .Select(g => new { type = g.Key, count = g.Count() })),
                ["identities"] = identities.Length
            };
            Write(stage, result);
            // Full multisets retained so any digest mismatch can be diagnosed independently.
            if (stage == "SOURCE_AUDIT" || stage == "AUTHORED_BASELINE")
                Write(stage + "_SURFACES", new JObject { ["renderers"] = JArray.FromObject(renderLines.OrderBy(x => x, StringComparer.Ordinal)),
                    ["colliders"] = JArray.FromObject(colliderLines.OrderBy(x => x, StringComparer.Ordinal)) });
            return result;
        }

        public static string StartUnpack()
        {
            if (SceneManager.GetActiveScene().path != Target || EditorApplication.isPlaying)
                throw new InvalidOperationException("Open ENV01_AUTHORED in edit mode first");
            var root = SceneManager.GetActiveScene().GetRootGameObjects().First(g => g.name == "ENV01_Casco_District");
            unpack = new Queue<GameObject>(root.GetComponentsInChildren<Transform>(true)
                .Where(t => PrefabUtility.IsOutermostPrefabInstanceRoot(t.gameObject)).Select(t => t.gameObject));
            unpacked = 0;
            EditorApplication.update -= UnpackTick;
            EditorApplication.update += UnpackTick;
            return "Scheduled native unpack: " + unpack.Count;
        }
        static void UnpackTick()
        {
            try
            {
                for (int i = 0; i < 300 && unpack.Count > 0; i++)
                {
                    var go = unpack.Dequeue();
                    if (go && PrefabUtility.IsOutermostPrefabInstanceRoot(go))
                    { PrefabUtility.UnpackPrefabInstance(go, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction); unpacked++; }
                }
                Write("UNPACK_PROGRESS", new JObject { ["unpacked"] = unpacked, ["remaining"] = unpack.Count });
                if (unpack.Count == 0)
                {
                    EditorApplication.update -= UnpackTick;
                    EditorSceneManager.SaveScene(SceneManager.GetActiveScene());
                }
            }
            catch (Exception ex)
            {
                EditorApplication.update -= UnpackTick;
                Write("UNPACK_ERROR", new JObject { ["error"] = ex.ToString() });
                Debug.LogException(ex);
            }
        }
        static Transform Group(Transform parent, string name)
        {
            var go = new GameObject(name); go.transform.SetParent(parent, false); return go.transform;
        }
        static JDSpatialIdentity Id(Transform t, string id, string kind, string source)
        {
            var component = t.gameObject.AddComponent<JDSpatialIdentity>();
            component.stableId = id; component.kind = kind; component.sourceId = source;
            return component;
        }
        static void Move(Transform t, Transform parent)
        {
            if (!t) return;
            // Identity groups can keep the original local floats exactly, including large imported tree scales.
            var before = t.parent ? t.parent.localToWorldMatrix : Matrix4x4.identity;
            bool equal = Enumerable.Range(0, 16).All(i => before[i] == parent.localToWorldMatrix[i]);
            t.SetParent(parent, !equal);
        }
        static bool Plant(Transform t) => t.name.IndexOf("Tree", StringComparison.OrdinalIgnoreCase) >= 0
            || t.name.IndexOf("Shrub", StringComparison.OrdinalIgnoreCase) >= 0 || t.name.IndexOf("Plant_", StringComparison.OrdinalIgnoreCase) >= 0;

        public static string Organize()
        {
            if (SceneManager.GetActiveScene().path != Target) throw new InvalidOperationException("Authored scene only");
            var root = GameObject.Find("ENV01_Casco_District").transform;
            if (root.GetComponentsInChildren<Transform>(true).Any(t => PrefabUtility.IsPartOfPrefabInstance(t.gameObject)))
                throw new InvalidOperationException("Finish native unpack first");
            var legacy = root.Cast<Transform>().ToDictionary(t => t.name);
            root.name = "ENV01_AUTHORED"; Id(root, "ENV01_AUTHORED", "AuthoredScene", "ENV01_Casco_District");
            var buildings = Group(root, "Buildings"); var streets = Group(root, "Streets");
            var spaces = Group(root, "OpenSpaces"); var props = Group(root, "Props"); var plants = Group(root, "Vegetation");
            var landmarks = Group(root, "Landmarks"); var river = Group(root, "RiverWater");
            var gameplay = Group(root, "GameplayHelpers"); var misc = Group(root, "MiscLegacy");
            Move(legacy["Rows"], buildings);
            foreach (var row in legacy["Rows"].Cast<Transform>())
                foreach (var t in row.Cast<Transform>().Where(t => t.name != "Walls"))
                { string source = t.name; Id(t, "BLDG_" + source, "Building", source); t.name = "BLDG_" + source; }
            Move(legacy["Ground"], streets); Move(legacy["PavingOverlays"], streets); Move(legacy["Stairs"], streets);
            var spec = JObject.Parse(File.ReadAllText(EnvDistrict.DistrictSpecs + "/ENV01_Casco_District.json"));
            foreach (JObject st in (JArray)spec["streets"])
            {
                string source = (string)st["id"];
                var anchor = Group(streets, "STREET_" + source);
                var identity = Id(anchor, "STREET_" + source, "StreetReference", source);
                identity.referenceOutline = ((JArray)st["pts"]).Select(p => new Vector3((float)p[0], 0, (float)p[1])).ToArray();
                // Existing apron objects have an explicit street id; no shared road mesh is split or rebuilt.
                foreach (var apron in legacy["Ground"].Cast<Transform>().Where(t => t.name.StartsWith("Ground_Apron_" + source + "_", StringComparison.Ordinal)
                    && t.name.Substring(("Ground_Apron_" + source + "_").Length).All(c => char.IsDigit(c) || c == '_')).ToArray()) Move(apron, anchor);
            }
            Move(legacy["Plazas"], spaces);
            foreach (var plaza in legacy["Plazas"].Cast<Transform>())
            { string source = plaza.name; Id(plaza, "SPACE_" + source, "OpenSpace", source); plaza.name = "SPACE_" + source; }
            foreach (var key in new[] { "StreetFurniture", "HeroCables", "Polish" }) Move(legacy[key], props);
            Move(legacy["Dressing"], props); Move(legacy["River"], river); Move(legacy["RiverPromenade"], river);
            Id(legacy["River"], "WATER_River", "River", "River");
            Move(legacy["Backdrop"], misc);
            foreach (var key in new[] { "Dressing", "Backdrop" })
            {
                var collection = Group(plants, key);
                foreach (var t in legacy[key].Cast<Transform>().Where(Plant).ToArray()) Move(t, collection);
            }
            Move(legacy["RouteProbe"], gameplay); Move(legacy["LightingRig"], misc);
            AddStructuralIds();
            foreach (JObject row in (JArray)spec["rows"])
            {
                int k = 0;
                foreach (JObject plot in (JArray)row["plots"])
                {
                    string landmark = (string)plot["landmark"];
                    if (!string.IsNullOrEmpty(landmark))
                    {
                        string source = (string)row["id"] + "_" + k;
                        var t = root.GetComponentsInChildren<JDSpatialIdentity>(true).FirstOrDefault(i => i.sourceId == source);
                        if (t) { t.kind = "LandmarkBuilding"; Move(t.transform, landmarks); }
                    }
                    k++;
                }
            }
            foreach (var go in SceneManager.GetActiveScene().GetRootGameObjects().Where(g => g.transform != root).ToArray())
                Move(go.transform, go.GetComponent<Light>() || go.GetComponent<UnityEngine.Rendering.Volume>() ? misc : gameplay);
            EditorSceneManager.SaveScene(SceneManager.GetActiveScene());
            Inventory();
            return "Hierarchy and passive identities saved";
        }

        public static void AddStructuralIds()
        {
            var root = GameObject.Find("ENV01_AUTHORED").transform;
            var paths = new[] { "RiverWater/River/Puente_Piedra", "RiverWater/River/Pasarela", "RiverWater/River/ENV_River_Stairs",
                "Streets/Stairs/Obispo_Escalera", "Streets/Stairs/Arco_Escalera", "Streets/Stairs/Solana_Escalera",
                "MiscLegacy/Backdrop/Backdrop_Sea", "MiscLegacy/Backdrop/Backdrop_Hills", "MiscLegacy/Backdrop/Backdrop_Range",
                "MiscLegacy/Backdrop/Cabana_0", "MiscLegacy/Backdrop/Cabana_1", "MiscLegacy/Backdrop/Cabana_5", "MiscLegacy/Backdrop/Cabana_6" };
            foreach (var path in paths)
            {
                var t = root.Find(path);
                if (t && !t.GetComponent<JDSpatialIdentity>()) Id(t, "STRUCT_" + t.name, "Structure", t.name);
            }
        }

        public static JObject Inventory()
        {
            var root = GameObject.Find("ENV01_AUTHORED").transform;
            var identities = root.GetComponentsInChildren<JDSpatialIdentity>(true);
            var entries = identities.Select(i => new { id = i.stableId, kind = i.kind, source = i.sourceId,
                position = new[] { i.transform.position.x, i.transform.position.y, i.transform.position.z },
                objects = i.GetComponentsInChildren<Transform>(true).Length, renderers = i.GetComponentsInChildren<Renderer>(true).Length,
                colliders = i.GetComponentsInChildren<Collider>(true).Length }).ToArray();
            var transforms = root.GetComponentsInChildren<Transform>(true);
            var propNames = new[] { "Prop_", "Bench", "Bollard", "Bin_", "Cafe_", "Parasol", "Planter", "Pot_", "Lamp_Post", "AFrame", "Bicycle", "Bike_Rack", "Utility_", "Telecom_", "AC_Unit", "Sat_Dish", "Fountain" };
            var props = transforms.Where(t => propNames.Any(n => t.name.Contains(n))
                && (t.parent == null || !propNames.Any(n => t.parent.name.Contains(n)))).ToArray();
            var result = new JObject { ["scene"] = Target, ["entries"] = JArray.FromObject(entries),
                ["buildingGroups"] = identities.Count(i => i.kind == "Building" || i.kind == "LandmarkBuilding"),
                ["streets"] = identities.Count(i => i.kind == "StreetReference"), ["openSpaces"] = identities.Count(i => i.kind == "OpenSpace"),
                ["approximateProps"] = props.Length, ["vegetationRoots"] = root.Find("Vegetation").GetComponentsInChildren<Transform>(true).Count(t => Plant(t) && !Plant(t.parent)),
                ["environmentPrefabInstances"] = transforms.Count(t => PrefabUtility.IsPartOfPrefabInstance(t.gameObject)),
                ["groups"] = JArray.FromObject(root.Cast<Transform>().Select(t => new { name = t.name, objects = t.GetComponentsInChildren<Transform>(true).Length })) };
            Write("INVENTORY", result); return result;
        }

        public static string Capture(string name)
        {
            var folder = Path.Combine(Evidence, "views", name);
            EnvPreview.Capture(folder + "/street.jpg", new Vector3(104, 2.1f, 186), new Vector3(81, 8, 158), 60, 1280, 720);
            EnvPreview.Capture(folder + "/river.jpg", new Vector3(60.5f, 2, 182.5f), new Vector3(30, -1.5f, 162), 60, 1280, 720);
            EnvPreview.Capture(folder + "/aerial.jpg", new Vector3(95, 120, -60), new Vector3(95, 0, 130), 55, 1280, 720);
            return folder;
        }
    }
}

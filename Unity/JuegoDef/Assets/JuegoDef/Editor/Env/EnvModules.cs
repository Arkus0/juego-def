using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// Step 2 of the ENV factory. Turns every Blender-derived mesh in Derived/ENV/Meshes into a module prefab in
    /// Derived/ENV/Modules (materials bound by name with Unity's Search-and-Remap, collider by policy), and wraps
    /// the Props/Nature models listed in Env/Grammar/modules.json with colliders, because those packs ship no
    /// collision. After this step every module is addressable by name through <see cref="EnvKit.Module"/>.
    /// </summary>
    public static class EnvModules
    {
        public const string ModuleFolder = EnvKit.Derived + "/Modules";
        const string MeshFolder = EnvKit.Derived + "/Meshes";

        [MenuItem("JuegoDef/ENV/2 Build Modules")]
        public static void BuildMenu() => Build();

        /// <summary>Builds every module, or only the named ones (comma list; no orphan sweep then) after a recipe
        /// change, so one new piece does not re-import the whole library.</summary>
        public static void Build(string only = null)
        {
            var want = string.IsNullOrEmpty(only) ? null : new HashSet<string>(only.Split(','));
            EnvKit.EnsureFolder(ModuleFolder);
            var policy = JObject.Parse(EnvKit.ReadText(EnvKit.Grammar + "/modules.json"));
            var none = new HashSet<string>(policy["noCollider"].Select(t => (string)t));
            var boxes = new HashSet<string>(policy["boxCollider"].Select(t => (string)t));
            var trunks = new HashSet<string>((policy["trunkCollider"] ?? new JArray()).Select(t => (string)t));
            noShadow = new HashSet<string>((policy["noShadow"] ?? new JArray()).Select(t => (string)t));
            int derived = 0, wrapped = 0;
            var produced = new HashSet<string>();

            foreach (var guid in AssetDatabase.FindAssets("t:Model", new[] { MeshFolder }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var name = Path.GetFileNameWithoutExtension(path);
                if (want != null && !want.Contains(name)) { produced.Add(name); continue; }
                var importer = (ModelImporter)AssetImporter.GetAtPath(path);
                importer.SearchAndRemapMaterials(ModelImporterMaterialName.BasedOnMaterialName, ModelImporterMaterialSearch.Everywhere);
                importer.SaveAndReimport();
                var model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                foreach (var r in model.GetComponentsInChildren<Renderer>())
                    foreach (var m in r.sharedMaterials)
                        if (!m || AssetDatabase.GetAssetPath(m) == path)
                            throw new System.InvalidOperationException($"ENV_MODULE_UNBOUND_MATERIAL {name}: {(m ? m.name : "null")} has no project material of that name");
                SaveModule(name, model, none.Contains(name) ? "none" : boxes.Contains(name) ? "box" : trunks.Contains(name) ? "trunk" : "mesh");
                produced.Add(name);
                derived++;
            }

            foreach (JObject w in policy["wrappers"])
            {
                if (want != null && !want.Contains((string)w["name"])) { produced.Add((string)w["name"]); continue; }
                var source = EnvKit.Module((string)w["source"]);
                var remap = (w["remap"] as JObject)?.Properties().ToDictionary(pr => pr.Name, pr => (string)pr.Value);
                SaveModule((string)w["name"], source, (string)w["collider"] ?? "box", remap, w);
                produced.Add((string)w["name"]);
                wrapped++;
            }
            // a module whose recipe/wrapper was removed must not linger (it would keep an orphan lineage record)
            foreach (var guid in AssetDatabase.FindAssets("t:Prefab", new[] { ModuleFolder }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                if (!produced.Contains(Path.GetFileNameWithoutExtension(path))) AssetDatabase.DeleteAsset(path);
            }
            AssetDatabase.SaveAssets();
            EnvKit.ClearCache();
            Debug.Log($"JD_ENV_MODULES derived={derived} wrapped={wrapped}");
        }

        static HashSet<string> noShadow = new HashSet<string>();

        /// <summary>One wrapped model under the module root: optional holder transform from the wrapper entry
        /// (<c>pos</c> [x,y,z], <c>rotY</c>, <c>scale</c> number or [x,y,z]) so the vendor model keeps its own import
        /// rotation, then the vendor materials bound to owned ENV_Src_* copies and the entry's remap.</summary>
        static GameObject Part(Transform root, GameObject source, Dictionary<string, string> remap, JObject w)
        {
            var parent = root;
            if (w != null && (w["pos"] != null || w["rotY"] != null || w["scale"] != null))
            {
                parent = new GameObject(source.name + "_Place").transform;
                parent.SetParent(root, false);
                if (w["pos"] is JArray p) parent.localPosition = new Vector3((float)p[0], (float)p[1], (float)p[2]);
                if (w["rotY"] != null) parent.localRotation = Quaternion.Euler(0, (float)w["rotY"], 0);
                if (w["scale"] is JArray sc) parent.localScale = new Vector3((float)sc[0], (float)sc[1], (float)sc[2]);
                else if (w["scale"] != null) parent.localScale = Vector3.one * (float)w["scale"];
            }
            var inst = (GameObject)PrefabUtility.InstantiatePrefab(source, parent);
            inst.name = source.name;
            // Props/Nature materials are generated locally by Unity's model import (random GUID per machine):
            // bind every one of them to the owned ENV_Src_* material so the committed prefab never references them.
            var map = new Dictionary<string, string>();
            foreach (var r in inst.GetComponentsInChildren<Renderer>(true))
                foreach (var m in r.sharedMaterials)
                    if (m && AssetDatabase.GetAssetPath(m).StartsWith("Assets/ThirdParty/Quaternius/") && !AssetDatabase.GetAssetPath(m).Contains("/MedievalVillage/"))
                        map[m.name] = "ENV_Src_" + m.name;
            if (remap != null) foreach (var kv in remap) map[kv.Key] = kv.Value;
            EnvKit.Remap(inst, map);
            return inst;
        }

        static void SaveModule(string name, GameObject source, string collider, Dictionary<string, string> remap = null, JObject wrapper = null)
        {
            var root = new GameObject(name);
            var inst = Part(root.transform, source, remap, wrapper);
            // composite wrappers (cohesion pass): a vendor model plus other modules/models, each placed, scaled and
            // remapped — e.g. a Quaternius crown on an own stem, a Quaternius tree over an own ring bench
            if (wrapper?["parts"] is JArray extra)
                foreach (JObject pw in extra)
                    Part(root.transform, EnvKit.Module((string)pw["source"]),
                         (pw["remap"] as JObject)?.Properties().ToDictionary(pr => pr.Name, pr => (string)pr.Value), pw);
            // flush or tiny details: their shadow never resolves in the main-light cascade, so they skip the shadow pass
            if (noShadow.Contains(name))
                foreach (var r in root.GetComponentsInChildren<Renderer>(true))
                    r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            switch (collider)
            {
                case "none":
                    foreach (var c in root.GetComponentsInChildren<Collider>(true)) Object.DestroyImmediate(c);
                    break;
                case "mesh":
                    foreach (var mf in root.GetComponentsInChildren<MeshFilter>())
                        if (!mf.GetComponent<Collider>()) mf.gameObject.AddComponent<MeshCollider>().sharedMesh = mf.sharedMesh;
                    break;
                case "trunk":
                    var tb = EnvPreview.BoundsOf(inst);   // the trunk of the main model
                    var cap = root.AddComponent<CapsuleCollider>();
                    cap.radius = 0.25f;
                    cap.height = 3f;
                    cap.center = new Vector3(tb.center.x - root.transform.position.x, 1.5f, tb.center.z - root.transform.position.z);
                    break;
                case "box":
                    var b = EnvPreview.BoundsOf(root);
                    var bc = root.AddComponent<BoxCollider>();
                    bc.center = b.center - root.transform.position;
                    bc.size = b.size;
                    break;
            }
            var path = $"{ModuleFolder}/{name}.prefab";
            PrefabUtility.SaveAsPrefabAsset(root, path);
            Object.DestroyImmediate(root);
        }
    }
}

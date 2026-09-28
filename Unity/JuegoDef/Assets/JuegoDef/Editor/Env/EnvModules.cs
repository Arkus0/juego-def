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
        public static void Build()
        {
            EnvKit.EnsureFolder(ModuleFolder);
            var policy = JObject.Parse(EnvKit.ReadText(EnvKit.Grammar + "/modules.json"));
            var none = new HashSet<string>(policy["noCollider"].Select(t => (string)t));
            var boxes = new HashSet<string>(policy["boxCollider"].Select(t => (string)t));
            int derived = 0, wrapped = 0;
            var produced = new HashSet<string>();

            foreach (var guid in AssetDatabase.FindAssets("t:Model", new[] { MeshFolder }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var name = Path.GetFileNameWithoutExtension(path);
                var importer = (ModelImporter)AssetImporter.GetAtPath(path);
                importer.SearchAndRemapMaterials(ModelImporterMaterialName.BasedOnMaterialName, ModelImporterMaterialSearch.Everywhere);
                importer.SaveAndReimport();
                var model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                foreach (var r in model.GetComponentsInChildren<Renderer>())
                    foreach (var m in r.sharedMaterials)
                        if (!m || AssetDatabase.GetAssetPath(m) == path)
                            throw new System.InvalidOperationException($"ENV_MODULE_UNBOUND_MATERIAL {name}: {(m ? m.name : "null")} has no project material of that name");
                SaveModule(name, model, none.Contains(name) ? "none" : boxes.Contains(name) ? "box" : "mesh");
                produced.Add(name);
                derived++;
            }

            foreach (JObject w in policy["wrappers"])
            {
                var source = EnvKit.Module((string)w["source"]);
                var remap = (w["remap"] as JObject)?.Properties().ToDictionary(pr => pr.Name, pr => (string)pr.Value);
                SaveModule((string)w["name"], source, (string)w["collider"] ?? "box", remap);
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

        static void SaveModule(string name, GameObject source, string collider, Dictionary<string, string> remap = null)
        {
            var root = new GameObject(name);
            var inst = (GameObject)PrefabUtility.InstantiatePrefab(source, root.transform);
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
            switch (collider)
            {
                case "mesh":
                    foreach (var mf in inst.GetComponentsInChildren<MeshFilter>())
                        if (!mf.GetComponent<Collider>()) mf.gameObject.AddComponent<MeshCollider>().sharedMesh = mf.sharedMesh;
                    break;
                case "trunk":
                    var tb = EnvPreview.BoundsOf(inst);
                    var cap = root.AddComponent<CapsuleCollider>();
                    cap.radius = 0.25f;
                    cap.height = 3f;
                    cap.center = new Vector3(tb.center.x - root.transform.position.x, 1.5f, tb.center.z - root.transform.position.z);
                    break;
                case "box":
                    var b = EnvPreview.BoundsOf(inst);
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

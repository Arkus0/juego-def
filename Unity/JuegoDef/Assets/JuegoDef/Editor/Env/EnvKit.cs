using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// Name-based access to ENV source modules (installed Quaternius packs + juego-def derived modules) and
    /// materials. Operators ask for a module by its catalogue name ("Wall_Plaster_Straight", "ENV_Shopfront_Frame");
    /// they never need a folder path. Vendor assets are only instantiated/referenced, never edited.
    /// </summary>
    public static class EnvKit
    {
        public const string Derived = "Assets/JuegoDef/Derived/ENV";
        public const string Grammar = "Assets/JuegoDef/Env/Grammar";
        public const string Specs = "Assets/JuegoDef/Env/Specs";

        /// <summary>Static flags for built environment: everything but static batching. URP's GPU Resident Drawer draws
        /// static kit pieces instanced; static batching would instead copy every mesh into combined buffers at load
        /// (the CASCO district: 9 s first frame, 2 GB of graphics memory).</summary>
        public const StaticEditorFlags StaticFlags = (StaticEditorFlags)~0 & ~StaticEditorFlags.BatchingStatic;
        public static readonly string[] SourceRoots =
        {
            Derived + "/Modules",
            "Assets/ThirdParty/Quaternius/MedievalVillage",
            "Assets/ThirdParty/Quaternius/Props",
            "Assets/ThirdParty/Quaternius/Nature",
        };
        public static readonly string[] MaterialRoots =
        {
            Derived + "/Materials",
            Derived + "/Interiors",
            Derived + "/Signs",
            "Assets/ThirdParty/Quaternius/MedievalVillage/Materials",
            "Assets/ThirdParty/Quaternius/Props",
            "Assets/ThirdParty/Quaternius/Nature",
        };

        static readonly Dictionary<string, GameObject> Prefabs = new Dictionary<string, GameObject>();
        static readonly Dictionary<string, Material> Materials = new Dictionary<string, Material>();
        static readonly Dictionary<string, Texture2D> Textures = new Dictionary<string, Texture2D>();

        public static void ClearCache()
        {
            Prefabs.Clear();
            Materials.Clear();
            Textures.Clear();
        }

        /// <summary>Prefab (or model for FBX-only packs) by exact file name, searched in <see cref="SourceRoots"/> order.</summary>
        public static GameObject Module(string name)
        {
            if (Prefabs.TryGetValue(name, out var cached) && cached) return cached;
            foreach (var root in SourceRoots)
            {
                if (!AssetDatabase.IsValidFolder(root)) continue;
                foreach (var filter in new[] { " t:Prefab", " t:Model" })
                foreach (var guid in AssetDatabase.FindAssets(name + filter, new[] { root }))
                {
                    var path = AssetDatabase.GUIDToAssetPath(guid);
                    if (Path.GetFileNameWithoutExtension(path) != name) continue;
                    return Prefabs[name] = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                }
            }
            throw new ArgumentException("ENV_MODULE_MISSING " + name + " (install the pack or run the derive/module step)");
        }

        public static bool HasMat(string name)
        {
            try { return Mat(name) != null; }
            catch (ArgumentException) { return false; }
        }

        public static bool HasModule(string name)
        {
            try { return Module(name) != null; }
            catch (ArgumentException) { return false; }
        }

        public static Material Mat(string name)
        {
            if (Materials.TryGetValue(name, out var cached) && cached) return cached;
            foreach (var root in MaterialRoots)
            {
                if (!AssetDatabase.IsValidFolder(root)) continue;
                foreach (var guid in AssetDatabase.FindAssets(name + " t:Material", new[] { root }))
                {
                    var path = AssetDatabase.GUIDToAssetPath(guid);
                    if (Path.GetFileNameWithoutExtension(path) != name) continue;
                    return Materials[name] = AssetDatabase.LoadAssetAtPath<Material>(path);
                }
            }
            throw new ArgumentException("ENV_MATERIAL_MISSING " + name + " (run JuegoDef > ENV > 1 Generate Materials)");
        }

        public static Texture2D Tex(string name)
        {
            if (Textures.TryGetValue(name, out var cached) && cached) return cached;
            foreach (var root in new[] { Derived + "/Textures", Derived + "/Signs", "Assets/ThirdParty/Quaternius" })
            {
                if (!AssetDatabase.IsValidFolder(root)) continue;
                foreach (var guid in AssetDatabase.FindAssets(name + " t:Texture2D", new[] { root }))
                {
                    var path = AssetDatabase.GUIDToAssetPath(guid);
                    if (Path.GetFileNameWithoutExtension(path) != name) continue;
                    // skip Unreal-convention normal maps and Unity-extracted .fbm copies (random local GUIDs)
                    if (path.Contains("Unreal") || path.Contains(".fbm/")) continue;
                    return Textures[name] = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
                }
            }
            throw new ArgumentException("ENV_TEXTURE_MISSING " + name);
        }

        /// <summary>Instantiates a module as a prefab instance (keeps the link to the source prefab).</summary>
        public static GameObject Place(string name, Transform parent, Vector3 localPos, float rotY, Vector3? scale = null)
        {
            var go = (GameObject)PrefabUtility.InstantiatePrefab(Module(name), parent);
            go.transform.localPosition = localPos;
            go.transform.localRotation = Quaternion.Euler(0, rotY, 0);
            if (scale.HasValue) go.transform.localScale = scale.Value;
            return go;
        }

        /// <summary>Replaces materials by source-material name on every renderer below <paramref name="root"/>.
        /// The map values are ENV material names. Unmapped slots keep their vendor material.</summary>
        public static void Remap(GameObject root, IDictionary<string, string> map)
        {
            if (map == null || map.Count == 0) return;
            foreach (var r in root.GetComponentsInChildren<Renderer>(true))
            {
                var mats = r.sharedMaterials;
                bool changed = false;
                for (int i = 0; i < mats.Length; i++)
                {
                    if (!mats[i]) continue;
                    if (map.TryGetValue(mats[i].name, out var target) && !string.IsNullOrEmpty(target))
                    {
                        var m = Mat(target);
                        if (m != mats[i]) { mats[i] = m; changed = true; }
                    }
                }
                if (changed) r.sharedMaterials = mats;
            }
        }

        public static Transform Group(Transform parent, string name)
        {
            var existing = parent.Find(name);
            if (existing) return existing;
            var t = new GameObject(name).transform;
            t.SetParent(parent, false);
            return t;
        }

        public static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;
            var parent = Path.GetDirectoryName(path).Replace('\\', '/');
            EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, Path.GetFileName(path));
        }

        public static string ReadText(string assetPath) =>
            File.ReadAllText(Path.Combine(Directory.GetCurrentDirectory(), assetPath));

        public static Color Hex(string hex) =>
            ColorUtility.TryParseHtmlString(hex, out var c) ? c : throw new ArgumentException("bad colour " + hex);
    }
}

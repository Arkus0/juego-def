using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;

/// <summary>Small Editor-only intake check; run from menu or -executeMethod JDAssetIntakeValidator.Run.</summary>
public static class JDAssetIntakeValidator
{
    [Serializable]
    private sealed class Report
    {
        public int models;
        public int prefabs;
        public int problems;
        public string[] examples;
    }

    private static readonly Regex GuidPattern = new Regex(@"guid: ([0-9a-f]{32})", RegexOptions.Compiled);

    [MenuItem("Tools/JuegoDef/Validate Asset Intake")]
    public static void Run()
    {
        var issues = new List<string>();
        var report = new Report();
        var roots = new[] { "Assets/ThirdParty/Quaternius", "Assets/JuegoDef/Derived" };
        foreach (var root in roots)
        {
            if (!AssetDatabase.IsValidFolder(root)) continue;
            var absolute = Path.Combine(Directory.GetCurrentDirectory(), root.Replace('/', Path.DirectorySeparatorChar));
            foreach (var file in Directory.GetFiles(absolute, "*", SearchOption.AllDirectories))
            {
                if (file.EndsWith(".meta", StringComparison.OrdinalIgnoreCase)) continue;
                var path = "Assets" + file.Substring(Path.Combine(Directory.GetCurrentDirectory(), "Assets").Length).Replace('\\', '/');
                var extension = Path.GetExtension(path).ToLowerInvariant();
                if (extension == ".fbx")
                {
                    report.models++;
                    var importer = AssetImporter.GetAtPath(path) as ModelImporter;
                    if (importer == null)
                    {
                        issues.Add("missing model importer: " + path);
                        continue;
                    }
                    if (importer.globalScale < 0.01f || importer.globalScale > 100f)
                        issues.Add("suspicious model scale " + importer.globalScale + ": " + path);
                    if ((path.Contains("/UAL1/") || path.Contains("/UAL2/")) && importer.animationType != ModelImporterAnimationType.Human)
                        issues.Add("UAL model has not had Humanoid import applied: " + path);
                    if (importer.animationType == ModelImporterAnimationType.Human)
                    {
                        var avatar = AssetDatabase.LoadAllAssetsAtPath(path).OfType<Avatar>().FirstOrDefault();
                        if (avatar == null || !avatar.isValid || !avatar.isHuman)
                            issues.Add("invalid humanoid avatar: " + path);
                    }
                }
                if (extension == ".prefab")
                {
                    report.prefabs++;
                    var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                    if (prefab == null)
                    {
                        issues.Add("unloadable prefab: " + path);
                        continue;
                    }
                    foreach (var component in prefab.GetComponentsInChildren<Component>(true))
                        if (component == null) issues.Add("missing prefab script: " + path);
                    foreach (var renderer in prefab.GetComponentsInChildren<Renderer>(true))
                        if (renderer.sharedMaterials.Any(material => material == null))
                            issues.Add("missing prefab material: " + path);
                }
                if (extension == ".prefab" || extension == ".mat" || extension == ".asset")
                {
                    foreach (Match match in GuidPattern.Matches(File.ReadAllText(file)))
                    {
                        var guid = match.Groups[1].Value;
                        if (guid == "00000000000000000000000000000000") continue;
                        if (string.IsNullOrEmpty(AssetDatabase.GUIDToAssetPath(guid)))
                            issues.Add("unresolved GUID " + guid + ": " + path);
                    }
                }
            }
        }
        var distinct = issues.Distinct().ToArray();
        report.problems = distinct.Length;
        report.examples = distinct.Take(50).ToArray();
        Debug.Log("JD_ASSET_VALIDATION " + JsonUtility.ToJson(report));
    }
}

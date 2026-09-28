using System;
using System.Linq;
using UnityEditor;
using UnityEngine;

/// <summary>Batch entry point using the pinned Quaternius utility, not a second UAL importer.</summary>
public static class JDAssetIntakeApplyUAL
{
    [MenuItem("Tools/JuegoDef/Apply UAL Imports")]
    public static void Run()
    {
        foreach (var path in new[] {
            "Assets/ThirdParty/Quaternius/UAL1/UAL1.fbx",
            "Assets/ThirdParty/Quaternius/UAL2/UAL2.fbx"
        })
        {
            var asset = AssetDatabase.LoadMainAssetAtPath(path);
            if (asset == null)
            {
                Debug.LogWarning("JD_UAL_NOT_INSTALLED " + path);
                continue;
            }
            Selection.activeObject = asset;
            QuaterniusUtils.ApplyLoopToEveryClip();
            AssetDatabase.WriteImportSettingsIfDirty(path);
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceUpdate);
            var importer = AssetImporter.GetAtPath(path) as ModelImporter;
            if (importer == null || importer.animationType != ModelImporterAnimationType.Human)
                throw new InvalidOperationException("UAL importer did not apply Humanoid: " + path);
            Debug.Log("JD_UAL_IMPORTED " + path + " clips=" + importer.clipAnimations.Length +
                " loops=" + importer.clipAnimations.Count(clip => clip.loopTime));
        }
    }
}

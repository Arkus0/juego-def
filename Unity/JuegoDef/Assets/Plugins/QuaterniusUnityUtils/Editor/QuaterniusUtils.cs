using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;


public class QuaterniusUtils {

    public const bool CompressCollisionsIntoOneObject = true;
    #region Static Fields and Methods
    public static (string packName, string packCollisionNaming)[] quaterniusPacks = new (string packName, string packCollisionNaming)[] {
        ("FantasyProps", "Collision_"),
        ("Stylized_Nature", "UCX_")
    };
    public static string defaultCollisionNaming = "Collision_";

    [MenuItem("Tools/QuaterniusUtility/Apply Import Steps to Universal Animation Library")]
    public static void ApplyLoopToEveryClip() {
        var paths = Selection.GetFiltered<Object>(SelectionMode.Assets);
        if (paths.Length == 0) {
            Debug.LogWarning("No file selected.");
            return;
        }
        string path = AssetDatabase.GetAssetPath(paths[0]);

        if(string.IsNullOrEmpty(path)) {
            Debug.LogWarning("No file selected.");
            return;
        }


        ModelImporter importer = AssetImporter.GetAtPath(path) as ModelImporter;
        if(importer == null) {
            Debug.LogError("Selected file is not a valid model.");
            return;
        }
        importer.bakeAxisConversion = true;
        importer.animationType = ModelImporterAnimationType.Human;
        importer.motionNodeName = "Rig/root";

        var animationImported = importer.clipAnimations;
        if (animationImported.Length == 0) {
            animationImported = importer.defaultClipAnimations;
        }

        foreach(var clipAnimation in animationImported) {


            if(clipAnimation != null && clipAnimation.name.EndsWith("Loop")) {
                clipAnimation.loopTime = true;
            } else {
                clipAnimation.loopTime = false;
            }
        }
        importer.clipAnimations = animationImported;
        AssetDatabase.SaveAssetIfDirty(importer);
    }
    [MenuItem("Tools/QuaterniusUtility/Apply Collision Prefabs to Selected Quaternius Models")]
    public static void CombineCollisions()
    {
        Debug.Log("CombineCollisions called");
        //Get the selected object paths and their corresponding folder paths
        List<string> importedObjectPaths = Selection.GetFiltered<Object>(SelectionMode.Assets)
            .Select(obj => AssetDatabase.GetAssetPath(obj))
            .ToList();
        List<string> importedFolderPaths = importedObjectPaths
            .Select(path => Path.GetDirectoryName(path))
            .ToList();

        List<string> folderPaths = CheckObjectsForFolders(importedObjectPaths);
        // Sanitize the imported objects by removing non-GameObject entries
        RemoveNonGameObjects(importedObjectPaths, importedFolderPaths);
        if(folderPaths.Count > 0) {
            Debug.Log("Folder paths found: " + folderPaths.Count);
            AddFolderObjects(importedObjectPaths, importedFolderPaths, folderPaths);
        }
        if(importedObjectPaths.Count == 0) {
            Debug.LogWarning("No models selected.");
            return;
        }

        Dictionary<string, List<int>> folderToObjectPaths = SortModelPaths(importedObjectPaths, importedFolderPaths);

        QuaterniusUtils defaultCollision = new QuaterniusUtils();
        foreach (var kvp in folderToObjectPaths) {
            if(CheckFolderForPackName(kvp.Key, out int packNamingIndex))
            {
                QuaterniusUtils applyCollisionPrefabs = new QuaterniusUtils(packNamingIndex);
                applyCollisionPrefabs.ApplyCollisionPrefabsToAllImportedModels(importedObjectPaths, importedFolderPaths, kvp.Value);
            } else {
                defaultCollision.ApplyCollisionPrefabsToAllImportedModels(importedObjectPaths, importedFolderPaths, kvp.Value);
            }
        }
    }

    private static bool CheckFolderForPackName(string folderPath, out int packNamingIndex) {
        folderPath = folderPath.Replace(" ", "_");
        for (int i = 0; i < quaterniusPacks.Length; i++) {
            if (folderPath.Contains(quaterniusPacks[i].packName)) {
                packNamingIndex = i;
                return true;
            }
        }
        packNamingIndex = -1;
        return false;
    }

    private static List<string>CheckObjectsForFolders(List<string> objectPaths) {
        List<string> folderObjects = new List<string>();
        for(int i = 0; i < objectPaths.Count; i++) {
            if(AssetDatabase.IsValidFolder(objectPaths[i])) {
                // Check if the folder path exists
                folderObjects.Add(objectPaths[i]);
            }
        }
        return folderObjects;
    }
    private static void AddFolderObjects(List<string> objectPaths, List<string> folderPaths, List<string> folderObjectPaths) {


        for (int i = 0; i < folderObjectPaths.Count; i++) {
            string folderPath = folderObjectPaths[i];
            string folderCheckPath = Path.GetDirectoryName(folderPath) + Path.DirectorySeparatorChar + Path.GetFileName(folderPath);
            string[] originalGUIDs = AssetDatabase.FindAssets("t:GameObject", new[] { folderPath });
            // Debug.Log("Found " + originalGUIDs.Length + " objects in folder (before filtering): " + folderPath);
            string[] originalPaths = originalGUIDs.Select(AssetDatabase.GUIDToAssetPath).ToArray();
            // Debug.Log("Found " + originalPaths.Length + " objects in folder (after converting GUIDs to paths): " + folderPath);
            // Debug.Log($" original paths: {string.Join(", ", originalPaths)}\n original Directory: {Path.GetDirectoryName(originalPaths[0])}, folderPath: {folderPath}");

            string[] objectsInFolderPaths = originalPaths
            .Where(path => Path.GetDirectoryName(path).Equals(folderCheckPath))
            .ToArray();

            // Debug.Log("Found " + objectsInFolderPaths.Length + " objects in folder: " + folderPath);
            for (int j = 0; j < objectsInFolderPaths.Length; j++) {
                objectPaths.Add(objectsInFolderPaths[j]);
                folderPaths.Add(folderPath);
            }
        }
    }

    private static void RemoveNonGameObjects(List<string> objectPaths, List<string> folderPaths) {
        for (int i = objectPaths.Count - 1; i >= 0; i--) {
            if (!AssetDatabase.LoadAssetAtPath<GameObject>(objectPaths[i])) {
                objectPaths.RemoveAt(i);
                folderPaths.RemoveAt(i);
            }
        }
    }

    private static Dictionary<string, List<int>> SortModelPaths(List<string> objectPaths, List<string> folderPaths)
    {
        Dictionary<string, List<int>> folderToObjectPaths = new Dictionary<string, List<int>>();
        for (int i = 0; i < objectPaths.Count; i++)
        {
            string folder = folderPaths[i];
            if (!folderToObjectPaths.ContainsKey(folder))
            {
                folderToObjectPaths[folder] = new List<int>();
            }
            folderToObjectPaths[folder].Add(i);
        }
        return folderToObjectPaths;
    }

    #endregion
    private readonly string collisionPrefix;
    public QuaterniusUtils(int packNamingIndex = -1) {
        if (packNamingIndex >= 0 && packNamingIndex < quaterniusPacks.Length) {
            collisionPrefix = quaterniusPacks[packNamingIndex].packCollisionNaming;
        } else {
            collisionPrefix = defaultCollisionNaming;
        }
    }

    #pragma warning disable format
    //Disable warning because the const variable can be changed by the user in the editor.
    public void ApplyCollisionPrefabsToModel(GameObject modelInstance, GameObject collisionInstance)
    {
        if(!CompressCollisionsIntoOneObject) {
            MeshRenderer[] meshRenderers = collisionInstance.GetComponentsInChildren<MeshRenderer>();
            foreach (MeshRenderer renderer in meshRenderers)
            {

                if (renderer.gameObject.GetComponent<Collider>() != null)
                {
                    renderer.enabled = false;
                    continue;

                }
                renderer.gameObject.AddComponent<MeshCollider>();
                renderer.enabled = false;
            }

        } else {
            MeshFilter[] meshFilters = collisionInstance.GetComponentsInChildren<MeshFilter>();
            foreach (MeshFilter filter in meshFilters) {

                var meshCollider = collisionInstance.AddComponent<MeshCollider>();
                meshCollider.sharedMesh = filter.sharedMesh;
                meshCollider.convex = true;
                meshCollider.enabled = true;
                if(filter.gameObject != collisionInstance) {
                    GameObject.DestroyImmediate(filter.gameObject);
                }

            }
        }
        #pragma warning restore format
        collisionInstance.transform.parent = modelInstance.transform;
        collisionInstance.transform.SetLocalPositionAndRotation(Vector3.zero, Quaternion.identity);
        collisionInstance.transform.localScale = Vector3.one;


    }
    public void ApplyCollisionPrefabsToAllImportedModels(List<string> importedModelPaths, List<string> modelFolders, List<int> indices)
    {

        if(AssetDatabase.IsValidFolder("Assets/Prefabs") == false)
        {
            AssetDatabase.CreateFolder("Assets", "Prefabs");
        }

        for(int i = 0; i < indices.Count; i++)
        {
            string modelPath = importedModelPaths[indices[i]];
            string modelFolder = modelFolders[indices[i]];
            GameObject model = AssetDatabase.LoadAssetAtPath<GameObject>(modelPath);
            if (model != null)
            {
                GameObject modelInstance = Object.Instantiate(model);
                modelInstance.name = model.name;
                string prefabPath = Path.Join("Assets", "Prefabs", model.name + "_WithCollisions.prefab");

                string collisionpath = Path.Join(modelFolder, "Collisions", collisionPrefix + Path.GetFileName(modelPath));
                GameObject collisionPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(collisionpath);
                if (collisionPrefab == null)
                {
                    Debug.LogWarning("No collision prefab found for model: " + model.name + " at path: " + collisionpath + "\n"
                    + "Creating prefab without collisions.");
                    PrefabUtility.SaveAsPrefabAsset(modelInstance, prefabPath);
                    GameObject.DestroyImmediate(modelInstance);
                    continue;
                }
                GameObject collisionInstance = Object.Instantiate(collisionPrefab);


                // Apply collision prefabs to the model instance
                ApplyCollisionPrefabsToModel(modelInstance, collisionInstance);

                // Save the modified model instance as a new prefab

                PrefabUtility.SaveAsPrefabAsset(modelInstance, prefabPath);

                // Clean up the instantiated model instance
                Object.DestroyImmediate(modelInstance);

                Debug.Log("Processed model: " + model.name);
            }
            else
            {
                Debug.LogError("Failed to load model at path: " + modelPath);
            }
        }
    }
}

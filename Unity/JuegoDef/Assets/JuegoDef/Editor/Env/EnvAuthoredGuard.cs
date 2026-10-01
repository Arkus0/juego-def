using System;
using UnityEngine.SceneManagement;

namespace JuegoDef.Env
{
    /// <summary>Legacy rebuild tools have no authority while an authored level is loaded, even additively.</summary>
    public static class EnvAuthoredGuard
    {
        public static void RequireLegacyScene()
        {
            for (int i = 0; i < SceneManager.sceneCount; i++)
            {
                var scene = SceneManager.GetSceneAt(i);
                if (!scene.isLoaded) continue;
                bool authored = scene.name == "ENV01_AUTHORED" || scene.name == "ENV01_REFERENCE";
                foreach (var root in scene.GetRootGameObjects())
                {
                    var identity = root.GetComponent<JDSpatialIdentity>();
                    authored |= identity && identity.kind == "AuthoredScene";
                }
                if (authored) throw new InvalidOperationException(
                    "JD_AUTHORED_NO_REBUILD: close the authored scene before using legacy generation tools. " +
                    "The Unity scene owns its layout; rebuilding is never an authored editing operation.");
            }
        }
    }
}

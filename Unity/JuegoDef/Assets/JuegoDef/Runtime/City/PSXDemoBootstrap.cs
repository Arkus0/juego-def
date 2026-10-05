using System.Collections;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace JuegoDef.City
{
    /// <summary>
    /// The town is a multi-scene stack: CITY_B_PS1_DEMO (base: terrain, walls, light, player) +
    /// CITY_B_Buildings (269 facades) + CITY_B_Props (market, furniture, NPCs). Opening the demo scene alone shows an
    /// empty ghost town — the layer the Owner was looking at. This bootstrap loads the two content layers additively on
    /// Play so the demo is one double-click. Idempotent: skips scenes already open (editor additive setup).
    /// Editor play uses LoadSceneAsyncInPlayMode (build settings not required); a player build needs the three scenes
    /// added to Build Settings in this order.
    /// </summary>
    public class PSXDemoBootstrap : MonoBehaviour
    {
        public string buildingsScene = "CITY_B_Buildings";
        public string propsScene = "CITY_B_Props";

        void Start()
        {
            StartCoroutine(LoadStack());
        }

        IEnumerator LoadStack()
        {
            yield return LoadIfMissing(buildingsScene);
            yield return LoadIfMissing(propsScene);
        }

        IEnumerator LoadIfMissing(string sceneName)
        {
            for (int i = 0; i < SceneManager.sceneCount; i++)
                if (SceneManager.GetSceneAt(i).name == sceneName)
                    yield break;
            AsyncOperation op = null;
#if UNITY_EDITOR
            var path = "Assets/JuegoDef/Scenes/CITY_B/" + sceneName + ".unity";
            var p = UnityEditor.SceneManagement.EditorSceneManager.LoadSceneAsyncInPlayMode(
                path, new LoadSceneParameters(LoadSceneMode.Additive));
            op = p;
#else
            op = SceneManager.LoadSceneAsync(sceneName, LoadSceneMode.Additive);
#endif
            while (op != null && !op.isDone) yield return null;
        }
    }
}

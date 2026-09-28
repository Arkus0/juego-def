using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace JuegoDef.Env
{
    /// <summary>Preview stage + camera capture used by the operator loop (observe step) and for library evidence,
    /// lit with the ENV look-development preset so previews judge materials under the intended mood.</summary>
    public static class EnvPreview
    {
        public static Transform NewStage(string rootName = "Stage", bool ground = true)
        {
            EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
            Lighting();
            if (ground)
            {
                var g = GameObject.CreatePrimitive(PrimitiveType.Plane);
                g.name = "PreviewGround";
                g.transform.localScale = new Vector3(8, 1, 8);
                g.GetComponent<Renderer>().sharedMaterial = AssetDatabase.LoadAssetAtPath<Material>("Assets/JuegoDef/Materials/JD_Bootstrap_WetGround.mat");
            }
            return new GameObject(rootName).transform;
        }

        /// <summary>Look-development lighting (see <see cref="EnvLighting"/>): damp Atlantic overcast by default.</summary>
        public static void Lighting(string preset = "atlantic_overcast") => EnvLighting.Apply(preset);

        /// <summary>Renders <paramref name="camera"/> (or a temporary camera) to a PNG under the project folder.</summary>
        public static string Capture(string projectRelativePng, Vector3 position, Vector3 lookAt, float fov = 50, int width = 1600, int height = 900)
        {
            var go = new GameObject("PreviewCamera");
            var cam = go.AddComponent<Camera>();
            cam.transform.position = position;
            cam.transform.LookAt(lookAt);
            cam.fieldOfView = fov;
            cam.nearClipPlane = 0.05f;
            cam.farClipPlane = 600f;
            var data = go.AddComponent<UnityEngine.Rendering.Universal.UniversalAdditionalCameraData>();
            data.renderPostProcessing = true;
            data.antialiasing = UnityEngine.Rendering.Universal.AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            var rt = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            cam.targetTexture = rt;
            // freshly generated material variants would otherwise render invisible while shaders compile async
            bool asyncWas = ShaderUtil.allowAsyncCompilation;
            ShaderUtil.allowAsyncCompilation = false;
            cam.Render();
            ShaderUtil.allowAsyncCompilation = asyncWas;
            RenderTexture.active = rt;
            var tex = new Texture2D(width, height, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
            tex.Apply();
            RenderTexture.active = null;
            var full = Path.Combine(Directory.GetCurrentDirectory(), projectRelativePng);
            Directory.CreateDirectory(Path.GetDirectoryName(full));
            File.WriteAllBytes(full, full.EndsWith(".jpg") ? tex.EncodeToJPG(88) : tex.EncodeToPNG());
            cam.targetTexture = null;
            Object.DestroyImmediate(rt);
            Object.DestroyImmediate(tex);
            Object.DestroyImmediate(go);
            return full;
        }

        public static Bounds BoundsOf(GameObject go)
        {
            var rs = go.GetComponentsInChildren<Renderer>();
            if (rs.Length == 0) return new Bounds(go.transform.position, Vector3.zero);
            var b = rs[0].bounds;
            foreach (var r in rs) b.Encapsulate(r.bounds);
            return b;
        }

        /// <summary>Three-quarter street-level view of an object (street side = +z of its root).</summary>
        public static string CaptureObject(GameObject go, string png, float yaw = 25f, float pitch = 8f, float distanceScale = 1.0f)
        {
            // frame the built object, not the 20 m water tiles that come with quay templates
            var rs = go.GetComponentsInChildren<Renderer>().Where(x => !x.transform.parent || !x.transform.parent.name.Contains("Water")).ToArray();
            var b = rs.Length > 0 ? rs[0].bounds : new Bounds(go.transform.position, Vector3.one);
            foreach (var x in rs) b.Encapsulate(x.bounds);
            float r = Mathf.Max(b.extents.magnitude, 1.5f);
            var dir = go.transform.rotation * Quaternion.Euler(-pitch, yaw, 0) * Vector3.forward;
            var pos = b.center + dir * r * distanceScale * 1.9f;
            pos.y = Mathf.Max(pos.y, 1.6f);
            return Capture(png, pos, b.center, 45);
        }
    }
}

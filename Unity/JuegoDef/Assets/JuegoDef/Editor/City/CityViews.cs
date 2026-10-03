using System.IO;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace JuegoDef.City
{
    /// <summary>
    /// Fixed player-height views of an authored slice (WP-CITY-IVX-HUMAN-01, D5): the game framing as measured in Play
    /// Mode on the scene's GC2 shot (camera 3 m behind the Player, 2.0 m above the feet, 0.5 m over the right shoulder,
    /// level, FOV 55) rendered with the Main Camera's settings, with the Player standing at the spot so scale reads. The same VIEWS.json gives the before and the after.
    /// The Player is put back where it was; nothing else in the scene is touched.
    /// VIEWS.json: { "views": [ { "id", "feet": [x, y, z], "yaw", "pitch"?, "note" } ] } (y is re-seated on the ground).
    /// </summary>
    public static class CityViews
    {
        public static string Capture(string viewsJson, string outDir, string prefix, int width = 1600, int height = 900)
        {
            var doc = JObject.Parse(File.ReadAllText(viewsJson));
            Directory.CreateDirectory(outDir);
            var main = Camera.main;
            var player = GameObject.Find("Player");
            var go = EditorUtility.CreateGameObjectWithHideFlags("CITY_VIEWS_CAPTURE", HideFlags.HideAndDontSave, typeof(Camera));
            var cam = go.GetComponent<Camera>();
            cam.CopyFrom(main);
            cam.fieldOfView = 55f;
            var data = go.AddComponent<UniversalAdditionalCameraData>();
            var mainData = main.GetComponent<UniversalAdditionalCameraData>();
            data.renderPostProcessing = mainData == null || mainData.renderPostProcessing;
            data.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            data.antialiasingQuality = AntialiasingQuality.High;
            Vector3 playerPos = player ? player.transform.position : Vector3.zero;
            Quaternion playerRot = player ? player.transform.rotation : Quaternion.identity;
            var rt = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            var tex = new Texture2D(width, height, TextureFormat.RGB24, false);
            int n = 0;
            try
            {
                foreach (JObject v in (JArray)doc["views"])
                {
                    var f = (JArray)v["feet"];
                    var feet = new Vector3((float)f[0], (float)f[1], (float)f[2]);
                    // seat the feet on what is under them (ground, steps), never on a roof or awning above
                    if (Physics.Raycast(feet + Vector3.up * 1.2f, Vector3.down, out var hit, 4f)) feet = hit.point;
                    float yaw = (float)v["yaw"], pitch = v["pitch"] != null ? (float)v["pitch"] : 0f;
                    var fwd = Quaternion.Euler(0, yaw, 0) * Vector3.forward;
                    var right = Quaternion.Euler(0, yaw, 0) * Vector3.right;
                    if (player) { player.transform.position = feet + Vector3.up * 1.0f; player.transform.rotation = Quaternion.Euler(0, yaw, 0); }
                    go.transform.position = feet + Vector3.up * 2.0f - fwd * 3f + right * 0.5f;
                    go.transform.rotation = Quaternion.Euler(pitch, yaw, 0);
                    cam.targetTexture = rt;
                    cam.Render();
                    RenderTexture.active = rt;
                    tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
                    tex.Apply();
                    File.WriteAllBytes(Path.Combine(outDir, $"{prefix}{(string)v["id"]}.jpg"), tex.EncodeToJPG(92));
                    n++;
                }
            }
            finally
            {
                RenderTexture.active = null;
                cam.targetTexture = null;
                if (player) { player.transform.position = playerPos; player.transform.rotation = playerRot; }
                Object.DestroyImmediate(rt);
                Object.DestroyImmediate(tex);
                Object.DestroyImmediate(go);
            }
            return $"JD_CITY_VIEWS {prefix} views={n} -> {outDir}";
        }
    }
}

using System.IO;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace JuegoDef.City
{
    /// <summary>
    /// Fixed player-height views of an authored slice (WP-CITY-IVX-HUMAN-01, D5), rendered with the Main Camera's
    /// settings and the Player standing at the spot so scale reads. The same VIEWS.json gives the before and the after.
    /// <see cref="Capture"/> keeps the framing measured in Play Mode on the scene's GC2 shot when the slice began
    /// (camera 3 m behind the Player, 2.0 m above the feet, 0.5 m over the right shoulder, FOV 55): before/after stay
    /// comparable. <see cref="CaptureGame"/> uses the scene's current GC2 shot (radius, lift, shoulder) and, when the
    /// Main Camera carries <see cref="CityRetroScreen"/>, its 640x480 image shown at 2x: what the player sees.
    /// The Player is put back where it was; nothing else in the scene is touched.
    /// VIEWS.json: { "views": [ { "id", "feet": [x, y, z], "yaw", "pitch"?, "note" } ] } (y is re-seated on the ground).
    /// </summary>
    public static class CityViews
    {
        public static string Capture(string viewsJson, string outDir, string prefix, int width = 1600, int height = 900) =>
            Render(viewsJson, outDir, prefix, 3f, 2f, 0.5f, width, height, 1);

        public static string CaptureGame(string viewsJson, string outDir, string prefix)
        {
            float radius = 3f, lift = 1f, shoulder = 0.5f;
            var shot = GameObject.Find("Camera Shot");
            var comp = shot ? shot.GetComponent("ShotCamera") : null;
            if (comp)
            {
                var so = new SerializedObject(comp);
                radius = so.FindProperty("m_ShotType.m_ThirdPerson.m_Radius.m_Property.m_Value").floatValue;
                lift = so.FindProperty("m_ShotType.m_ThirdPerson.m_Lift.m_Property.m_Value").floatValue;
                shoulder = so.FindProperty("m_ShotType.m_ThirdPerson.m_Shoulder.m_Property.m_Value").floatValue;
            }
            var retro = Camera.main.GetComponent<CityRetroScreen>();
            int w = retro ? retro.width : 1600, h = retro ? retro.height : 900;
            // the GC2 pivot is the Player's centre, 1 m above the feet
            return Render(viewsJson, outDir, prefix, radius, 1f + lift, shoulder, w, h, retro ? 2 : 1);
        }

        static string Render(string viewsJson, string outDir, string prefix, float back, float up, float side, int width, int height, int upscale)
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
            bool retro = upscale > 1;
            data.antialiasing = retro ? AntialiasingMode.None : AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            data.antialiasingQuality = AntialiasingQuality.High;
            Vector3 playerPos = player ? player.transform.position : Vector3.zero;
            Quaternion playerRot = player ? player.transform.rotation : Quaternion.identity;
            var rt = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32) { antiAliasing = retro ? 1 : 4 };
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
                    go.transform.position = feet + Vector3.up * up - fwd * back + right * side;
                    go.transform.rotation = Quaternion.Euler(pitch, yaw, 0);
                    cam.targetTexture = rt;
                    cam.Render();
                    RenderTexture.active = rt;
                    tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
                    tex.Apply();
                    var file = Path.Combine(outDir, $"{prefix}{(string)v["id"]}.jpg");
                    if (retro)
                    {
                        // the VGA image on a monitor: bilinear 2x, as the player sees it
                        var big = RenderTexture.GetTemporary(width * upscale, height * upscale, 0, RenderTextureFormat.ARGB32);
                        tex.filterMode = FilterMode.Bilinear;
                        Graphics.Blit(tex, big);
                        RenderTexture.active = big;
                        var bigTex = new Texture2D(width * upscale, height * upscale, TextureFormat.RGB24, false);
                        bigTex.ReadPixels(new Rect(0, 0, width * upscale, height * upscale), 0, 0);
                        bigTex.Apply();
                        File.WriteAllBytes(file, bigTex.EncodeToJPG(92));
                        Object.DestroyImmediate(bigTex);
                        RenderTexture.ReleaseTemporary(big);
                    }
                    else File.WriteAllBytes(file, tex.EncodeToJPG(92));
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
            return $"JD_CITY_VIEWS {prefix} views={n} back={back} up={up} side={side} {width}x{height}x{upscale} -> {outDir}";
        }
    }
}

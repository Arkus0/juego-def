using UnityEngine;
using UnityEngine.UI;

namespace JuegoDef.City
{
    /// <summary>
    /// Dreamcast output for the town (Owner 2026-10-03: "como un DLC de Shenmue 2"): the game camera renders into a
    /// 640x480 texture that is shown full screen at 4:3, pillarboxed in black, filtered bilinear like a VGA signal on a
    /// monitor. Only the camera's image changes; the game runs at the screen's own resolution underneath.
    /// </summary>
    [RequireComponent(typeof(Camera))]
    public class CityRetroScreen : MonoBehaviour
    {
        public int width = 640;
        public int height = 480;
        public bool bilinear = true;

        Camera cam;
        RenderTexture rt;
        GameObject screen;

        void OnEnable()
        {
            cam = GetComponent<Camera>();
            rt = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32)
            {
                name = "CityRetroScreen",
                antiAliasing = 1,
                filterMode = bilinear ? FilterMode.Bilinear : FilterMode.Point,
            };
            rt.Create();
            cam.targetTexture = rt;

            screen = new GameObject("CITY_RETRO_SCREEN");
            screen.hideFlags = HideFlags.DontSave;
            var canvas = screen.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = -1000;                     // under any game UI
            var black = new GameObject("Bars").AddComponent<Image>();
            black.transform.SetParent(screen.transform, false);
            black.color = Color.black;
            Stretch(black.rectTransform);
            var img = new GameObject("Image").AddComponent<RawImage>();
            img.transform.SetParent(screen.transform, false);
            img.texture = rt;
            Stretch(img.rectTransform);
            var fit = img.gameObject.AddComponent<AspectRatioFitter>();
            fit.aspectMode = AspectRatioFitter.AspectMode.FitInParent;
            fit.aspectRatio = width / (float)height;
        }

        void OnDisable()
        {
            if (cam) cam.targetTexture = null;
            if (screen) Destroy(screen);
            if (rt) { rt.Release(); Destroy(rt); }
        }

        static void Stretch(RectTransform r)
        {
            r.anchorMin = Vector2.zero;
            r.anchorMax = Vector2.one;
            r.offsetMin = r.offsetMax = Vector2.zero;
        }
    }
}

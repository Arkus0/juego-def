using UnityEngine;
using UnityEngine.UI;

namespace JuegoDef.City
{
    /// <summary>
    /// Phase-1 image definition for the demo (2026-10-06, plan Docs/evidence/PSX-DEMO-01/PLAN_DEFINICION_PS1.md).
    /// Sits next to CityRetroScreen (Owner WIP, untouched) and re-layouts its RawImage: instead of stretching the
    /// 480x360 raster to the window, it displays it at the biggest INTEGER multiple that fits (×2 = 960x720) and
    /// letterboxes the rest, so every game pixel lands on whole screen pixels — the difference between "chunky" and
    /// "blurry" on a modern monitor. Adds an optional lattice (F10) aligned one line per game pixel and F11 toggles
    /// back to the stretched fit. Edit mode does nothing: CityRetroScreen builds its canvas at Play.
    /// </summary>
    [DefaultExecutionOrder(300)]
    public class PSXDemoScreen : MonoBehaviour
    {
        public bool integerScale = true;
        [Range(0f, 0.6f)] public float latticeAlpha = 0.22f;

        RawImage image;
        AspectRatioFitter fitter;
        RawImage lattice;
        int lastW, lastH;
        Texture2D latticeTex;

        void Start() { Invoke(nameof(Attach), 0.05f); }

        void Attach()
        {
            var screen = transform.Find("CITY_RETRO_SCREEN");
            if (screen == null) return;
            var img = screen.Find("Image");
            if (img == null) return;
            image = img.GetComponent<RawImage>();
            fitter = img.GetComponent<AspectRatioFitter>();
            Layout();
        }

        void Update()
        {
            var k = UnityEngine.InputSystem.Keyboard.current;
            if (k != null)
            {
                if (k.f10Key.wasPressedThisFrame) { latticeAlpha = latticeAlpha > 0f ? 0f : 0.22f; RefreshLattice(); }
                if (k.f11Key.wasPressedThisFrame) { integerScale = !integerScale; Layout(); }
            }
            if (Screen.width != lastW || Screen.height != lastH) Layout();
        }

        void Layout()
        {
            if (image == null) { Attach(); if (image == null) return; }
            lastW = Screen.width; lastH = Screen.height;
            var rt = image.rectTransform;
            var screen = GetComponent<CityRetroScreen>();
            int w = screen ? screen.width : 480, h = screen ? screen.height : 360;
            if (integerScale)
            {
                int scale = Mathf.Max(1, Mathf.Min(Screen.width / w, Screen.height / h));
                fitter.enabled = false;
                rt.anchorMin = rt.anchorMax = new Vector2(0.5f, 0.5f);
                rt.pivot = new Vector2(0.5f, 0.5f);
                rt.sizeDelta = new Vector2(w * scale, h * scale);
                BuildLattice(w, h);
                if (lattice != null)
                {
                    lattice.rectTransform.sizeDelta = rt.sizeDelta;
                    lattice.uvRect = new Rect(0f, 0f, w, h);
                    lattice.enabled = latticeAlpha > 0f;
                }
            }
            else
            {
                fitter.enabled = true;
                if (lattice != null) lattice.enabled = false;
            }
        }

        void BuildLattice(int w, int h)
        {
            if (latticeTex == null)
            {
                latticeTex = new Texture2D(2, 2, TextureFormat.RGBA32, false) { wrapMode = TextureWrapMode.Repeat, filterMode = FilterMode.Point };
                latticeTex.SetPixels(new[] { new Color(0f, 0f, 0f, 1f), new Color(0, 0, 0, 0), new Color(0, 0, 0, 0), new Color(0, 0, 0, 0) });
                latticeTex.Apply(false, true);
            }
            var screen = transform.Find("CITY_RETRO_SCREEN");
            if (screen == null) return;
            var img = screen.Find("Image");
            if (img == null) return;
            if (lattice == null)
            {
                var go = new GameObject("PSX_Lattice", typeof(RawImage));
                go.transform.SetParent(img.parent, false);
                go.transform.SetSiblingIndex(img.GetSiblingIndex() + 1);
                lattice = go.GetComponent<RawImage>();
                lattice.raycastTarget = false;
            }
            lattice.texture = latticeTex;
            lattice.color = new Color(0f, 0f, 0f, latticeAlpha);
            lattice.rectTransform.anchorMin = image.rectTransform.anchorMin;
            lattice.rectTransform.anchorMax = image.rectTransform.anchorMax;
            lattice.rectTransform.pivot = image.rectTransform.pivot;
        }

        void RefreshLattice() { if (lattice != null) { lattice.color = new Color(0f, 0f, 0f, latticeAlpha); lattice.enabled = latticeAlpha > 0f; } }
    }
}

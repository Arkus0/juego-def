using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace JuegoDef.City
{
    /// <summary>
    /// The town's surfaces in the Shenmue 2 manner (Owner 2026-10-03: the textures were failure number one; "copiarlo,
    /// no imitarlo, no adaptarlo"). The DC Plus materials of the kit keep their meshes and their colour family but
    /// take the Dreamcast-sized photographed surfaces of Tools/city_ivanix/tools/shenmue_kit.py, chosen by the texture
    /// they used (the stylised kit sheets): render, ashlar, rubble, roof tile, the three trim sheets, river cobbles.
    /// Renders run in world space (a facade is one surface, not a stack of 2 m tiles) and take a saturated Cantabrian
    /// palette; the macro tone noise and the gloss go (both read as modern). Re-runnable; the ground classes are set by
    /// CityPaving with the same textures. Spec: Docs/design/city_ivx/SHENMUE_TEXTURE_SPEC.md.
    /// </summary>
    public static class CityShenmueKit
    {
        const string Kit = "Assets/JuegoDef/City/ShenmueKit/Textures";
        const string DcDir = "Assets/JuegoDef/City/DCMaterials";

        /// <summary>Old texture (by name prefix) -> kit texture and how its tiling changes (kit textures are 2 m photos;
        /// the stylised sheets were mapped at other scales).</summary>
        static readonly (string from, string to, float stScale, bool worldUV)[] ByTexture =
        {
            ("T_ENV_Plaster_Neutral", "SK_Revoco", 1f, true),
            ("T_ENV_Stone_Ashlar_BaseColor", "SK_Silleria", 2f, false),
            ("T_ENV_Stone_Rubble_BaseColor", "SK_Mamposteria", 2f, false),
            ("T_UnevenBrick_BaseColor", "SK_Mamposteria", 1f / 1.35f, false),
            ("T_ENV_RoundTiles_Neutral", "SK_Teja", 1.5f, false),
            ("T_ENV_Trim_Painted", "SK_Atlas_Moldura", 1f, false),
            ("T_WoodTrim_BaseColor", "SK_Atlas_Carpinteria", 1f, false),
            ("T_RockTrim_BaseColor", "SK_Atlas_PiedraLabrada", 1f, false),
            ("T_ENV_RoundRocks_Neutral", "SK_Canto_Rodado", 1f, false),
        };

        /// <summary>The render colours of the Cantabrian casco, pushed to Shenmue's saturation (photographed paint, not
        /// pastel wash): lime white, bone, cream, sand, ochre, toasted, salmon, indiano blue, verdigris, grey.</summary>
        static readonly Dictionary<string, string> RenderColour = new Dictionary<string, string>
        {
            { "Cal", "#F6F2E8" }, { "Hueso", "#F4E6C4" }, { "Crema", "#F6DC9C" }, { "Arena", "#E8C68A" }, { "Ocre", "#EDB45A" },
            { "Tostado", "#E0A06A" }, { "Salmon", "#F0A486" }, { "Anil", "#86A8DA" }, { "Verdin", "#A6CC98" }, { "Gris", "#D2D2CC" },
        };

        [MenuItem("JuegoDef/CITY/Shenmue kit: surfaces")]
        static void Menu() => Debug.Log(Apply());

        public static string Apply()
        {
            AssetDatabase.Refresh();
            var tex = new Dictionary<string, Texture2D>();
            Texture2D T(string n)
            {
                if (tex.TryGetValue(n, out var t)) return t;
                var p = $"{Kit}/{n}.png";
                var ti = AssetImporter.GetAtPath(p) as TextureImporter;
                if (ti == null) throw new FileNotFoundException("JD_SHENMUE_KIT_NO_TEXTURE " + p + " (run shenmue_kit.py)");
                if (ti.maxTextureSize != 1024 || ti.filterMode != FilterMode.Bilinear || ti.anisoLevel != 2 || ti.mipmapEnabled != true)
                {
                    ti.maxTextureSize = 1024; ti.filterMode = FilterMode.Bilinear; ti.anisoLevel = 2; ti.mipmapEnabled = true;
                    ti.SaveAndReimport();
                }
                return tex[n] = AssetDatabase.LoadAssetAtPath<Texture2D>(p);
            }

            int changed = 0, renders = 0;
            var counts = new Dictionary<string, int>();
            foreach (var guid in AssetDatabase.FindAssets("t:Material", new[] { DcDir, "Assets/JuegoDef/City/Authored" }))
            {
                var m = AssetDatabase.LoadAssetAtPath<Material>(AssetDatabase.GUIDToAssetPath(guid));
                if (!m || !m.HasProperty("_BaseMap")) continue;
                // Dreamcast light response: faces turned from the sun fall into a cool shade but keep their colour
                // (vertex-lit look; cast shadows are kept soft by CityIvanixLook)
                if (m.HasProperty("_Wrap")) { m.SetFloat("_Wrap", 0.25f); m.SetColor("_ShadeColor", new Color(0.70f, 0.75f, 0.90f, 1f)); EditorUtility.SetDirty(m); }
                var cur = m.GetTexture("_BaseMap");
                if (!cur) continue;
                // the source sheet: the current texture's name, or the one recorded when the kit was first applied
                var src = EditorPrefsKey(m);
                string from = EditorPrefs.GetString(src, cur.name);
                var rule = ByTexture.FirstOrDefault(r => from.StartsWith(r.from));
                if (rule.from == null) continue;
                if (!EditorPrefs.HasKey(src)) EditorPrefs.SetString(src, cur.name);
                var oldSt = EditorPrefs.HasKey(src + "_ST") ? Parse(EditorPrefs.GetString(src + "_ST")) : m.GetVector("_BaseMap_ST");
                if (!EditorPrefs.HasKey(src + "_ST")) EditorPrefs.SetString(src + "_ST", $"{oldSt.x};{oldSt.y};{oldSt.z};{oldSt.w}");

                string to = rule.to;
                if (to == "SK_Revoco")
                {
                    // DC_ENV_Render_<Colour>_<Age>[_G]: old and worn render shows its stones
                    var parts = m.name.Split('_');
                    string colour = parts.Length > 3 ? parts[3] : "";
                    string age = parts.Length > 4 ? parts[4] : "Nuevo";
                    if (age == "Viejo" || age == "Gastado") to = "SK_Revoco_Viejo";
                    if (m.name.StartsWith("DC_ENV_Render_") && RenderColour.TryGetValue(colour, out var hex))
                    {
                        float k = age == "Viejo" ? 0.95f : age == "Gastado" ? 0.9f : 1f;
                        m.SetColor("_BaseColor", EnvKit_Hex(hex) * new Color(k, k, k, 1));
                        renders++;
                    }
                    else if (m.name.StartsWith("DC_ENV_Paint_Plinth_"))
                        m.SetColor("_BaseColor", Saturate(m.GetColor("_BaseColor"), 1.5f));
                }
                else if (m.name.StartsWith("DC_ENV_Joinery_"))
                    m.SetColor("_BaseColor", Saturate(m.GetColor("_BaseColor"), 1.35f));

                m.SetTexture("_BaseMap", T(to));
                m.SetVector("_BaseMap_ST", rule.worldUV ? new Vector4(1, 1, 0, 0) : new Vector4(oldSt.x * rule.stScale, oldSt.y * rule.stScale, oldSt.z, oldSt.w));
                m.SetFloat("_WorldUV", rule.worldUV ? 1 : 0);
                m.SetFloat("_MacroAmount", 0f);
                m.SetFloat("_SpecAmount", 0f);
                m.SetFloat("_MipBias", 0f);
                EditorUtility.SetDirty(m);
                changed++;
                counts[to] = counts.TryGetValue(to, out var c) ? c + 1 : 1;
            }
            AssetDatabase.SaveAssets();
            return $"JD_SHENMUE_KIT materials={changed} renders_recoloured={renders} " + string.Join(" ", counts.Select(kv => $"{kv.Key}={kv.Value}"));
        }

        static string EditorPrefsKey(Material m) => "JD_SHENMUE_KIT_SRC_" + AssetDatabase.AssetPathToGUID(AssetDatabase.GetAssetPath(m));

        static Vector4 Parse(string s)
        {
            var p = s.Split(';').Select(float.Parse).ToArray();
            return new Vector4(p[0], p[1], p[2], p[3]);
        }

        static Color EnvKit_Hex(string hex) => ColorUtility.TryParseHtmlString(hex, out var c) ? c : Color.white;

        static Color Saturate(Color c, float k)
        {
            Color.RGBToHSV(c, out var h, out var s, out var v);
            var o = Color.HSVToRGB(h, Mathf.Clamp01(s * k), v);
            o.a = c.a;
            return o;
        }
    }
}

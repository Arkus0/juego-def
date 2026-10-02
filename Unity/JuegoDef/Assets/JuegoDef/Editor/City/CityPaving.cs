using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace JuegoDef.City
{
    /// <summary>
    /// The town's paving as one surface (shader JuegoDef/City/DC Ground) over the seed's terrain: the class map from
    /// Tools/city_ivanix/tools/paving_map.py decides which paving goes where at 12.5 cm, read with a hand-laid wander and
    /// a granite band at every joint. Each class keeps the painted texture, tiling and tint of the DC material its
    /// terrain pieces had; the fan of setts and the granite bands take the setts' and the flags' textures.
    /// Run after the DC conversion. Re-runnable: the material is refreshed and the terrain renderers re-pointed.
    /// </summary>
    public static class CityPaving
    {
        const string Dir = "Assets/JuegoDef/City/Ground";
        const string MapPath = Dir + "/CITY_PavingMap.png";
        const string MatPath = Dir + "/CITY_Ground_DC.mat";
        static string Meta => Path.GetFullPath(Path.Combine(Application.dataPath, "../../../Tools/city_ivanix/reconstruction/paving_map_v1.json"));
        static readonly string[] Names = { "CANTO", "CANTO_VIEJO", "HUERTA", "SUELO", "ROCA", "PRADO", "LOSA", "ADOQUIN", "MUELLE", "PATIO", "CAMINO" };

        [MenuItem("JuegoDef/CITY/Dreamcast+: 5 paving (hand-laid ground)")]
        static void Menu() => Debug.Log(Apply());

        public static string Apply()
        {
            AssetDatabase.Refresh();
            var ti = (TextureImporter)AssetImporter.GetAtPath(MapPath);
            ti.textureType = TextureImporterType.SingleChannel;
            ti.sRGBTexture = false;
            ti.mipmapEnabled = false;
            ti.filterMode = FilterMode.Point;
            ti.wrapMode = TextureWrapMode.Clamp;
            ti.npotScale = TextureImporterNPOTScale.None;
            ti.maxTextureSize = 8192;
            ti.textureCompression = TextureImporterCompression.Uncompressed;
            var ps = ti.GetDefaultPlatformTextureSettings();
            ps.format = TextureImporterFormat.R8; ps.textureCompression = TextureImporterCompression.Uncompressed; ps.maxTextureSize = 8192;
            ti.SetPlatformTextureSettings(ps);
            ti.SaveAndReimport();
            var map = AssetDatabase.LoadAssetAtPath<Texture2D>(MapPath);
            var meta = JObject.Parse(File.ReadAllText(Meta));

            var terrain = GameObject.Find("CITY_IVX_Base/TERRAIN");
            if (!terrain) return "JD_CITY_PAVING no terrain";
            var shader = Shader.Find("JuegoDef/City/DC Ground");
            var mat = AssetDatabase.LoadAssetAtPath<Material>(MatPath);
            if (!mat) { mat = new Material(shader); AssetDatabase.CreateAsset(mat, MatPath); }
            mat.shader = shader;
            mat.SetTexture("_ClassMap", map);
            mat.SetVector("_MapOrigin", new Vector4((float)meta["origin"][0], (float)meta["origin"][1], (float)meta["texel"], 0));
            mat.SetVector("_MapSize", new Vector4((float)meta["size"][0], (float)meta["size"][1], 0, 0));

            // each class's look: the DC material its terrain pieces carry now (or carried, if already on the ground shader)
            var looks = new Dictionary<int, Material>();
            var renderers = terrain.GetComponentsInChildren<MeshRenderer>(true).Where(r => r.name.StartsWith("TERRAIN_") && !r.name.Contains("ESCOLLERA")).ToList();
            foreach (var r in renderers)
            {
                int c = ClassOf(r.name);
                if (c < 0 || looks.ContainsKey(c)) continue;
                var m = r.sharedMaterial;
                if (m && m.shader == shader) m = AssetDatabase.LoadAssetAtPath<Material>(EditorPrefs.GetString($"JD_CITY_PAVING_SRC_{c}", ""));
                if (m) { looks[c] = m; EditorPrefs.SetString($"JD_CITY_PAVING_SRC_{c}", AssetDatabase.GetAssetPath(m)); }
            }
            Texture noise = null;
            for (int c = 0; c < 11; c++)
            {
                if (!looks.TryGetValue(c, out var m)) m = looks.TryGetValue(0, out var m0) ? m0 : null;
                if (!m) continue;
                Slot(mat, c, m, Vector2.one, Color.white);
                if (!noise && m.HasProperty("_NoiseMap")) noise = m.GetTexture("_NoiseMap");
            }
            // the fan of setts (one tile 1.2 m) and the dressed granite of bands, kerbs and rims (one tile 2 m), painted
            // for the paving (Tools/city_ivanix/tools/ground_textures.py)
            Painted(mat, 11, Dir + "/TX_Ground_Abanico.png", 2f / 1.8f, new Color(0.95f, 0.94f, 0.92f));     // setts a touch large: the fan reads at play distance
            Painted(mat, 12, Dir + "/TX_Ground_Granito.png", 1f, new Color(0.8f, 0.8f, 0.79f));
            if (noise) mat.SetTexture("_NoiseMap", noise);
            EditorUtility.SetDirty(mat);

            int swapped = 0;
            foreach (var r in renderers)
            {
                int c = ClassOf(r.name);
                if (c < 0 || c == 3) continue;                    // under the houses: never seen, keep it simple
                r.sharedMaterial = mat;
                swapped++;
            }
            EditorSceneManager.MarkSceneDirty(terrain.scene);
            EditorSceneManager.SaveScene(terrain.scene);
            AssetDatabase.SaveAssets();
            return $"JD_CITY_PAVING map={map.width}x{map.height} classes={looks.Count} renderers={swapped}";
        }

        static int ClassOf(string name)
        {
            // TERRAIN_<CLASS>_<cx>_<cz>; CANTO_VIEJO contains an underscore
            var body = name.Substring("TERRAIN_".Length);
            for (int c = Names.Length - 1; c >= 0; c--)
                if (body.StartsWith(Names[c] + "_")) return c;
            return -1;
        }

        static void Painted(Material mat, int c, string path, float st, Color tint)
        {
            var ti = (TextureImporter)AssetImporter.GetAtPath(path);
            if (ti && (ti.maxTextureSize != 1024 || ti.anisoLevel != 4)) { ti.maxTextureSize = 1024; ti.anisoLevel = 4; ti.SaveAndReimport(); }
            mat.SetTexture($"_T{c}", AssetDatabase.LoadAssetAtPath<Texture2D>(path));
            mat.SetVector($"_ST{c}", new Vector4(st, st, 0, 0));
            mat.SetColor($"_C{c}", tint);
        }

        static void Slot(Material mat, int c, Material src, Vector2 scale, Color tint)
        {
            var tex = src.HasProperty("_BaseMap") ? src.GetTexture("_BaseMap") : null;
            var st = src.HasProperty("_BaseMap_ST") ? src.GetVector("_BaseMap_ST") : new Vector4(1, 1, 0, 0);
            var col = src.HasProperty("_BaseColor") ? src.GetColor("_BaseColor") : Color.white;
            mat.SetTexture($"_T{c}", tex);
            mat.SetVector($"_ST{c}", new Vector4(st.x * scale.x, st.y * scale.y, st.z, st.w));
            mat.SetColor($"_C{c}", col * tint);
        }
    }
}

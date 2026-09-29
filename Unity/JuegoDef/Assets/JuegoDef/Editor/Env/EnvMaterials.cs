using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace JuegoDef.Env
{
    /// <summary>
    /// Step 1 of the ENV factory: builds the owned palette materials and the few derived textures they need from
    /// <c>Env/Grammar/materials.json</c>. Re-running is idempotent (assets are updated in place, GUIDs kept).
    /// Derived textures are neutralised copies of vendor base-colour textures so tints can reach light/grey
    /// colours that a plain multiply over the warm vendor texture cannot.
    /// </summary>
    public static class EnvMaterials
    {
        const string TexFolder = EnvKit.Derived + "/Textures";
        const string MatFolder = EnvKit.Derived + "/Materials";

        [MenuItem("JuegoDef/ENV/1 Generate Materials")]
        public static void Generate()
        {
            var recipe = JObject.Parse(EnvKit.ReadText(EnvKit.Grammar + "/materials.json"));
            EnvKit.EnsureFolder(TexFolder);
            EnvKit.EnsureFolder(MatFolder);
            int textures = 0, materials = 0;
            foreach (JObject t in recipe["textures"])
            {
                DeriveTexture((string)t["name"], (string)t["source"], (float)t["target"], (float)t["contrast"], (int?)t["size"] ?? 1024);
                textures++;
            }
            AssetDatabase.Refresh();
            EnvKit.ClearCache();
            foreach (JObject m in recipe["materials"])
            {
                BuildMaterial(m);
                materials++;
            }
            AssetDatabase.SaveAssets();
            EnvKit.ClearCache();
            Debug.Log($"JD_ENV_MATERIALS textures={textures} materials={materials}");
        }

        static void DeriveTexture(string name, string source, float target, float contrast, int size)
        {
            var src = EnvKit.Tex(source);
            var srcPath = AssetDatabase.GetAssetPath(src);
            var tex = new Texture2D(2, 2, TextureFormat.RGBA32, false, false);
            tex.LoadImage(File.ReadAllBytes(Path.Combine(Directory.GetCurrentDirectory(), srcPath)));
            var px = tex.GetPixels32();
            double mean = 0;
            for (int i = 0; i < px.Length; i++) mean += Lum(px[i]);
            mean /= px.Length;
            for (int i = 0; i < px.Length; i++)
            {
                float v = Mathf.Clamp01(target * (1f + contrast * ((float)(Lum(px[i]) / mean) - 1f)));
                byte b = (byte)Mathf.RoundToInt(v * 255f);
                px[i] = new Color32(b, b, b, 255);
            }
            tex.SetPixels32(px);
            tex.Apply();
            if (size < tex.width)
            {
                // Stylised flat-albedo walls/roofs do not need the vendor 2K: keep the repository light.
                var small = new Texture2D(size, size, TextureFormat.RGBA32, false, false);
                var sp = new Color[size * size];
                for (int y = 0; y < size; y++)
                for (int x = 0; x < size; x++)
                    sp[y * size + x] = tex.GetPixelBilinear((x + 0.5f) / size, (y + 0.5f) / size);
                small.SetPixels(sp);
                Object.DestroyImmediate(tex);
                tex = small;
            }
            var outPath = $"{TexFolder}/{name}.png";
            File.WriteAllBytes(Path.Combine(Directory.GetCurrentDirectory(), outPath), tex.EncodeToPNG());
            Object.DestroyImmediate(tex);
            AssetDatabase.ImportAsset(outPath);
            var importer = (TextureImporter)AssetImporter.GetAtPath(outPath);
            importer.sRGBTexture = true;
            importer.maxTextureSize = size;
            importer.mipmapEnabled = true;
            importer.SaveAndReimport();
        }

        static double Lum(Color32 c) => 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b;

        static void BuildMaterial(JObject r)
        {
            var name = (string)r["name"];
            var copy = new List<Material>();
            if (r["copy"] is JArray sources)
                foreach (var s in sources) copy.Add(EnvKit.Mat((string)s));
            var shader = r["shader"] != null ? Shader.Find((string)r["shader"]) : copy[0].shader;
            if (!shader) throw new System.ArgumentException("ENV shader missing for " + name);

            // Always rebuild in memory and copy over the existing asset: keeps the GUID, drops stale properties.
            var path = $"{MatFolder}/{name}.mat";
            var existing = AssetDatabase.LoadAssetAtPath<Material>(path);
            var mat = new Material(shader) { name = name };

            // Copy only properties the shader declares: vendor MI_Plaster carries stale entries pointing at a
            // texture that is not in the archive, and they must not travel into owned materials.
            foreach (var src in copy) CopyDeclared(src, mat);
            if (r["textures"] is JObject texs)
                foreach (var kv in texs) mat.SetTexture(kv.Key, EnvKit.Tex((string)kv.Value));
            if (r["colors"] is JObject cols)
                foreach (var kv in cols)
                {
                    var c = EnvKit.Hex((string)kv.Value);
                    mat.SetColor(kv.Key, c);
                    if (kv.Key == "_BaseColor" && mat.HasProperty("_Color")) mat.SetColor("_Color", c);
                }
            if (r["floats"] is JObject floats)
                foreach (var kv in floats) mat.SetFloat(kv.Key, (float)kv.Value);
            if (r["emission"] is JArray em)
            {
                // HDR emission: hex colour times intensity (night lamps and lit windows drive the bloom)
                var e = EnvKit.Hex((string)em[0]) * (float)em[1];
                e.a = 1f;
                mat.SetColor("_EmissionColor", e);
                mat.EnableKeyword("_EMISSION");
            }
            if (r["keywords"] is JArray keywords)
                foreach (var k in keywords) mat.EnableKeyword((string)k);
            if (mat.IsKeywordEnabled("_EMISSION")) mat.globalIlluminationFlags = MaterialGlobalIlluminationFlags.RealtimeEmissive;
            if (copy.Count > 0) mat.renderQueue = copy[0].renderQueue;
            if (r["queue"] != null) mat.renderQueue = (int)r["queue"];
            mat.enableInstancing = true;

            if (!existing) AssetDatabase.CreateAsset(mat, path);
            else
            {
                EditorUtility.CopySerialized(mat, existing);
                existing.name = name;
                EditorUtility.SetDirty(existing);
                Object.DestroyImmediate(mat);
            }
        }

        static void CopyDeclared(Material src, Material dst)
        {
            var s = src.shader;
            for (int i = 0; i < s.GetPropertyCount(); i++)
            {
                var prop = s.GetPropertyName(i);
                if (!dst.HasProperty(prop)) continue;
                switch (s.GetPropertyType(i))
                {
                    case ShaderPropertyType.Texture:
                        dst.SetTexture(prop, src.GetTexture(prop));
                        dst.SetTextureScale(prop, src.GetTextureScale(prop));
                        dst.SetTextureOffset(prop, src.GetTextureOffset(prop));
                        break;
                    case ShaderPropertyType.Color: dst.SetColor(prop, src.GetColor(prop)); break;
                    case ShaderPropertyType.Vector: dst.SetVector(prop, src.GetVector(prop)); break;
                    case ShaderPropertyType.Int: dst.SetInteger(prop, src.GetInteger(prop)); break;
                    default: dst.SetFloat(prop, src.GetFloat(prop)); break;
                }
            }
            foreach (var kw in src.shaderKeywords) dst.EnableKeyword(kw);
        }
    }
}

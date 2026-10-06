using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace JuegoDef.City
{
    /// <summary>
    /// Polish pass for the PSX demo's materials (2026-10-06). Two fixes, both raster-level, nothing semantic:
    ///   1. every PSX-family material's vertex-snap reference (_Resolution) moves from the 384x288 default to the
    ///      demo's 480x360 raster, so the PS1 vertex wobble lands exactly on the displayed pixel grid;
    ///   2. every texture used by the PSX-family materials is forced to Point filtering — a few (NPC_NoGlasses, some
    ///      imports) still came in Bilinear and read as smudges against the point-filtered town.
    /// Re-runnable; reports what it touched. Does not touch gameplay, placement or the licensed source art.
    /// </summary>
    public static class PSXDemoPolish
    {
        static readonly string[] ShaderFragments = { "JuegoDef/City/PSX Atlantic", "JuegoDef/City/PSX Ground", "JuegoDef/City/PSX Contact", "JuegoDef/City/PSX Decal", "JuegoDef/City/PSX Sky" };
        static readonly string[] TextureSlots = { "_BaseMap", "_ClassMap", "_NoiseMap", "_T0", "_T1", "_T2", "_T3", "_T4", "_T5", "_T6", "_T7", "_T8", "_T9", "_T10", "_T11", "_T12", "_EmissionMap" };

        [MenuItem("JuegoDef/CITY/PSX Demo: polish materials")]
        public static string Run()
        {
            int matsFixed = 0, texsFixed = 0;
            var touchedTextures = new HashSet<Object>();
            var all = AssetDatabase.FindAssets("t:Material", new[] { "Assets/JuegoDef" });
            foreach (var guid in all)
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (mat == null || mat.shader == null) continue;
                var shaderName = mat.shader.name;
                bool psx = false;
                foreach (var f in ShaderFragments) if (shaderName.Contains(f)) { psx = true; break; }
                if (!psx) continue;

                if (mat.HasProperty("_Resolution"))
                {
                    var res = mat.GetVector("_Resolution");
                    if ((int)res.x != 480 || (int)res.y != 360)
                    {
                        mat.SetVector("_Resolution", new Vector4(480f, 360f, 0f, 0f));
                        EditorUtility.SetDirty(mat);
                        matsFixed++;
                    }
                }

                if (mat.HasProperty("_MipBias") && mat.GetFloat("_MipBias") > 0.1f)
                {
                    mat.SetFloat("_MipBias", 0.1f);
                    EditorUtility.SetDirty(mat);
                    matsFixed++;
                }

                foreach (var slot in TextureSlots)
                {
                    if (!mat.HasProperty(slot)) continue;
                    var tex = mat.GetTexture(slot);
                    if (tex == null || !touchedTextures.Add(tex)) continue;
                    if (tex.filterMode != FilterMode.Point)
                    {
                        tex.filterMode = FilterMode.Point;
                        EditorUtility.SetDirty(tex);
                        texsFixed++;
                    }
                }
            }
            AssetDatabase.SaveAssets();
            return "JD_PSX_POLISH materials(_Resolution->480x360)=" + matsFixed + " textures(->Point)=" + texsFixed;
        }
    }
}

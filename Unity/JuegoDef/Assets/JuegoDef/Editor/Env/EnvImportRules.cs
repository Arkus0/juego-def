using UnityEditor;

namespace JuegoDef.Env
{
    /// <summary>
    /// Import rules that make ENV/PROP sources usable without per-asset surgery.
    /// <list type="bullet">
    /// <item>Quaternius Props/Nature FBX exports are authored in centimetres (file scale 0.01). The intake writes
    /// minimal .meta files, so Unity would ignore the file scale and import them 100x too large.</item>
    /// <item>juego-def derived ENV meshes (Blender exports) use metres, no import cameras/lights, and keep their
    /// Blender material names so the module step can bind them to kit/palette materials with Unity's own
    /// Search-and-Remap (by material name).</item>
    /// </list>
    /// </summary>
    public class EnvImportRules : AssetPostprocessor
    {
        const string Props = "Assets/ThirdParty/Quaternius/Props/";
        const string Nature = "Assets/ThirdParty/Quaternius/Nature/";
        public const string DerivedMeshes = EnvKit.Derived + "/Meshes/";

        /// <summary>The intake's minimal .meta files leave Props/Nature textures on importer defaults, which Unity
        /// resolved to Cubemap shape — every prop rendered white. Force 2D textures with the right colour space.</summary>
        void OnPreprocessTexture()
        {
            if (assetPath.StartsWith(EnvKit.Derived + "/Signs/"))
            {
                // lettering must not bleed across the panel edges
                ((TextureImporter)assetImporter).wrapMode = UnityEngine.TextureWrapMode.Clamp;
                return;
            }
            if (assetPath.StartsWith(EnvKit.Derived + "/Textures/"))
            {
                // generated data textures (weathering noise, water normals) are linear; generated normal maps are normals
                var name = System.IO.Path.GetFileNameWithoutExtension(assetPath);
                var ti = (TextureImporter)assetImporter;
                if (name.Contains("_Noise") || name.EndsWith("_Roughness")) ti.sRGBTexture = false;
                // the weathering shader thresholds the noise (flaking edges, moss, streaks): block compression turned
                // those edges into scattered 4x4 dots on the renders; the stain atlas alpha likewise (cohesion pass)
                if (name.Contains("_Noise")) ti.textureCompression = TextureImporterCompression.Uncompressed;
                if (name == "T_ENV_Stains") ti.textureCompression = TextureImporterCompression.CompressedHQ;
                if (name.EndsWith("_Normal")) ti.textureType = TextureImporterType.NormalMap;
                return;
            }
            if (!assetPath.StartsWith(Props) && !assetPath.StartsWith(Nature)) return;
            var importer = (TextureImporter)assetImporter;
            var file = System.IO.Path.GetFileNameWithoutExtension(assetPath);
            importer.textureShape = TextureImporterShape.Texture2D;
            // a normal map ends in "_Normal"; "Bark_NormalTree" / "Leaves_NormalTree_C" are colour maps of the "normal
            // tree" (they imported as normal maps before: purple-red trunks, red crowns)
            bool normal = file.EndsWith("_Normal");
            importer.textureType = normal ? TextureImporterType.NormalMap : TextureImporterType.Default;
            importer.sRGBTexture = !normal && !file.Contains("ORM") && !file.Contains("Roughness");
            bool foliage = file.Contains("Leaf") || file.Contains("Leaves") || file.Contains("Grass") || file.Contains("Flowers");
            importer.alphaIsTransparency = foliage;
            importer.mipmapEnabled = true;
            // alpha-tested foliage vanishes at distance unless mips keep their alpha coverage
            importer.mipMapsPreserveCoverage = foliage;
            importer.alphaTestReferenceValue = 0.45f;
        }

        void OnPreprocessModel()
        {
            var importer = (ModelImporter)assetImporter;
            if (assetPath.StartsWith(Props) || assetPath.StartsWith(Nature))
            {
                importer.useFileScale = true;
                importer.globalScale = 1f;
                importer.bakeAxisConversion = false;
            }
            else if (assetPath.StartsWith(DerivedMeshes))
            {
                importer.useFileScale = true;
                importer.globalScale = 1f;
                importer.bakeAxisConversion = true;
                importer.importCameras = false;
                importer.importLights = false;
                importer.importAnimation = false;
                importer.animationType = ModelImporterAnimationType.None;
                importer.addCollider = false;
                importer.isReadable = true;
            }
        }
    }
}

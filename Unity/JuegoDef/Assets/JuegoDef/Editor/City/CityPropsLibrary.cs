using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace JuegoDef.City
{
    /// <summary>
    /// The town's own props (Tools/city_ivanix/blender/*.py) as prefabs on Dreamcast+ materials: every FBX material
    /// slot is remapped to a DC Plus material by name (TX_* slots use the painted texture of the same name; role slots
    /// such as Paint, Glass or Plastic use a period colour, and their painted map TXR_&lt;role&gt;.png when there is one;
    /// the body paint map is greyscale and the colour tints it), colliders sized to the piece, and the variants a street of
    /// 2000 shows (car colours with their own plates, vans with their trade lettering, boat bands with their names).
    /// Prefabs: Assets/JuegoDef/City/Props/Prefabs/CITY_*.prefab.
    /// </summary>
    public static class CityPropsLibrary
    {
        const string MeshDir = "Assets/JuegoDef/City/Props/Meshes";
        const string TexDir = "Assets/JuegoDef/City/Props/Textures";
        const string MatDir = "Assets/JuegoDef/City/Props/Materials";
        const string PrefabDir = "Assets/JuegoDef/City/Props/Prefabs";

        static readonly Dictionary<string, (Color c, float spec)> Roles = new Dictionary<string, (Color, float)>
        {
            { "Paint", (new Color(0.62f, 0.10f, 0.08f), 0.35f) }, { "Glass", (new Color(0.08f, 0.11f, 0.14f), 0.7f) },
            { "Plastic", (new Color(0.12f, 0.12f, 0.13f), 0.1f) }, { "Rubber", (new Color(0.05f, 0.05f, 0.055f), 0f) },
            { "Hub", (new Color(0.66f, 0.68f, 0.7f), 0.4f) }, { "LightFront", (new Color(0.95f, 0.94f, 0.88f), 0.5f) },
            { "LightRear", (new Color(0.78f, 0.08f, 0.06f), 0.4f) }, { "Plate", (new Color(0.96f, 0.96f, 0.94f), 0.1f) },
            { "Chrome", (new Color(0.78f, 0.79f, 0.81f), 0.6f) },
            { "HullWhite", (new Color(0.93f, 0.92f, 0.88f), 0.15f) }, { "HullBand", (new Color(0.12f, 0.28f, 0.6f), 0.15f) },
            { "Antifouling", (new Color(0.55f, 0.12f, 0.08f), 0.05f) }, { "DeckWood", (new Color(0.55f, 0.40f, 0.25f), 0f) },
            { "CabinWhite", (new Color(0.94f, 0.93f, 0.9f), 0.1f) }, { "Mast", (new Color(0.25f, 0.22f, 0.2f), 0f) },
            { "Metal", (new Color(0.62f, 0.64f, 0.66f), 0.4f) }, { "TableWood", (new Color(0.62f, 0.48f, 0.32f), 0f) },
            { "PlasticWhite", (new Color(0.95f, 0.95f, 0.93f), 0.15f) }, { "Alu", (new Color(0.78f, 0.79f, 0.8f), 0.45f) },
            { "ParasolCanvas", (new Color(0.92f, 0.89f, 0.8f), 0f) }, { "Butane", (new Color(0.95f, 0.42f, 0.08f), 0.3f) },
            { "Correos", (new Color(0.98f, 0.78f, 0.05f), 0.25f) }, { "CorreosBlue", (new Color(0.08f, 0.2f, 0.5f), 0.1f) },
            { "Gumball", (new Color(0.1f, 0.55f, 0.25f), 0.3f) }, { "GumGlass", (new Color(0.75f, 0.82f, 0.86f), 0.6f) },
            { "Crate", (new Color(0.66f, 0.5f, 0.32f), 0f) },
            { "BootTop", (new Color(0.1f, 0.1f, 0.11f), 0.2f) }, { "CapRail", (new Color(0.42f, 0.3f, 0.2f), 0.15f) },
            { "BulwarkIn", (new Color(0.86f, 0.85f, 0.8f), 0.05f) }, { "Strake", (new Color(0.2f, 0.19f, 0.18f), 0.1f) },
            { "Salvavidas", (new Color(0.95f, 0.38f, 0.08f), 0.2f) }, { "NetGreen", (new Color(0.2f, 0.36f, 0.28f), 0f) },
            { "Rope", (new Color(0.72f, 0.62f, 0.42f), 0f) }, { "Grille", (new Color(0.1f, 0.1f, 0.11f), 0.2f) },
            { "Ropa", (new Color(0.16f, 0.22f, 0.42f), 0f) }, { "Ropa_A", (new Color(0.16f, 0.22f, 0.42f), 0f) }, { "Ropa_B", (new Color(0.62f, 0.14f, 0.12f), 0f) },
            { "Ropa_C", (new Color(0.86f, 0.82f, 0.72f), 0f) }, { "Ropa_D", (new Color(0.22f, 0.4f, 0.26f), 0f) },
            { "Queso", (new Color(0.92f, 0.84f, 0.58f), 0.05f) }, { "Miel", (new Color(0.78f, 0.46f, 0.08f), 0.5f) }, { "TapaMiel", (new Color(0.86f, 0.72f, 0.2f), 0.3f) },
            { "Botella", (new Color(0.42f, 0.52f, 0.36f), 0.6f) }, { "Corcho", (new Color(0.6f, 0.45f, 0.3f), 0f) }, { "Carton", (new Color(0.7f, 0.56f, 0.38f), 0f) },
        };
        static readonly (string name, Color c)[] CarColours =
        {
            ("Rojo", new Color(0.62f, 0.10f, 0.08f)), ("Blanco", new Color(0.92f, 0.92f, 0.9f)), ("Azul", new Color(0.12f, 0.24f, 0.48f)),
            ("Verde", new Color(0.18f, 0.36f, 0.24f)), ("Plata", new Color(0.7f, 0.72f, 0.74f)), ("Beige", new Color(0.78f, 0.70f, 0.55f)),
        };
        static readonly (string name, Color c)[] BandColours =
        {
            ("Azul", new Color(0.12f, 0.28f, 0.6f)), ("Rojo", new Color(0.62f, 0.12f, 0.1f)), ("Verde", new Color(0.12f, 0.42f, 0.24f)),
        };

        [MenuItem("JuegoDef/CITY/Dreamcast+: 4 build props library")]
        static void Menu() => Debug.Log(Build());

        public static string Build()
        {
            foreach (var d in new[] { MatDir, PrefabDir }) if (!AssetDatabase.IsValidFolder(d)) { Directory.CreateDirectory(Path.GetFullPath(d)); }
            AssetDatabase.Refresh();
            var shader = Shader.Find("JuegoDef/City/DC Plus");
            int prefabs = 0;
            foreach (var path in Directory.GetFiles(MeshDir, "*.fbx").Select(p => p.Replace('\\', '/')))
            {
                var mi = (ModelImporter)AssetImporter.GetAtPath(path);
                mi.materialImportMode = ModelImporterMaterialImportMode.ImportViaMaterialDescription;
                mi.importNormals = ModelImporterNormals.Import;
                mi.globalScale = 1f;
                // remap every slot to a DC material
                // the FBX's own slots plus the ones already remapped on an earlier build (those are refreshed too)
                var names = AssetDatabase.LoadAllAssetsAtPath(path).OfType<Material>().Select(m => m.name)
                    .Concat(mi.GetExternalObjectMap().Keys.Where(k => k.type == typeof(Material)).Select(k => k.name)).Distinct().ToList();
                // materials first (painting a new texture reimports it, which would drop remaps added to a stale importer),
                // then every remap on a fresh importer
                var dc = names.ToDictionary(n => n, n => DcMaterial(n, shader));
                mi = (ModelImporter)AssetImporter.GetAtPath(path);
                foreach (var n in names) mi.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material), n), dc[n]);
                mi.SaveAndReimport();
                var model = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                string baseName = Path.GetFileNameWithoutExtension(path);
                if (baseName == "CITY_Car_Hatch" || baseName == "CITY_Van")
                    for (int i = 0; i < CarColours.Length; i++)
                    {
                        var (cn, c) = CarColours[i];
                        // each colour its own number plate; each van its trade on the side
                        var plate = DcMaterial($"Plate_{(i + (baseName == "CITY_Van" ? 3 : 0)) % 6}", shader);
                        if (baseName == "CITY_Van") SavePrefab(model, $"{baseName}_{cn}", ("Paint", Variant("Paint", cn, c, shader)), ("Plate", plate), ("TX_VanDecal_0", DcMaterial($"TX_VanDecal_{i % 3}", shader)));
                        else SavePrefab(model, $"{baseName}_{cn}", ("Paint", Variant("Paint", cn, c, shader)), ("Plate", plate));
                        prefabs++;
                    }
                else if (baseName == "CITY_Boat_Lancha")
                    for (int i = 0; i < BandColours.Length; i++)
                    {
                        var (bn, c) = BandColours[i];
                        // each boat its own band colour and its own name on the bows
                        SavePrefab(model, $"{baseName}_{bn}", ("HullBand", Variant("HullBand", bn, c, shader)), ("TX_BoatName_0", DcMaterial($"TX_BoatName_{i + 1}", shader)));
                        prefabs++;
                    }
                else { SavePrefab(model, baseName); prefabs++; }
            }
            AssetDatabase.SaveAssets();
            return $"JD_CITY_PROPS_LIBRARY prefabs={prefabs}";
        }

        static Material DcMaterial(string name, Shader shader)
        {
            var path = $"{MatDir}/DC_{name}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (!m) { m = new Material(shader); AssetDatabase.CreateAsset(m, path); }
            m.shader = shader;
            m.SetColor("_ShadeColor", new Color(0.80f, 0.83f, 0.92f));
            m.SetFloat("_AmbientScale", 1.08f);
            if (name.StartsWith("TX_"))
            {
                var tp = $"{TexDir}/{name}.png";
                var ti = AssetImporter.GetAtPath(tp) as TextureImporter;
                bool cards = name.Contains("Leaves") || name.Contains("Frond") || name.Contains("Hortensia") || name.Contains("BoatName") || name.Contains("Decal") || name == "TX_Ropa";
                if (ti && (ti.alphaIsTransparency != cards || ti.maxTextureSize != 512))
                {
                    ti.alphaIsTransparency = cards; ti.maxTextureSize = 512; ti.mipmapEnabled = true;
                    if (cards) ti.mipMapsPreserveCoverage = true;
                    ti.SaveAndReimport();
                }
                m.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>(tp));
                m.SetColor("_BaseColor", Color.white);
                if (cards)
                {
                    m.SetFloat("_AlphaClip", 1); m.EnableKeyword("_ALPHATEST_ON"); m.SetFloat("_Cutoff", 0.45f); m.SetFloat("_Cull", 0);
                    m.renderQueue = 2450;
                    m.SetFloat("_Wrap", 0.6f);
                }
                else { m.SetFloat("_AlphaClip", 0); m.DisableKeyword("_ALPHATEST_ON"); m.SetFloat("_Cull", name.Contains("Lona") || name.Contains("Ropa") ? 0 : 2); }   // canvas is seen from under
            }
            else
            {
                // a role: its period colour, and its painted map when there is one (Plate_3 falls back to Plate's colour)
                string role = name.Split('_')[0];
                var (c, spec) = Roles.TryGetValue(name, out var r) ? r : Roles.TryGetValue(role, out r) ? r : (new Color(0.5f, 0.5f, 0.5f), 0f);
                var tex = RoleTexture(name) ?? RoleTexture(role);
                m.SetTexture("_BaseMap", tex ? tex : Texture2D.whiteTexture);
                m.SetColor("_BaseColor", tex && role != "Paint" ? Color.white : c);
                m.SetFloat("_SpecAmount", spec);
                m.SetFloat("_Gloss", spec > 0.5f ? 96f : 40f);
            }
            EditorUtility.SetDirty(m);
            return m;
        }

        static Texture2D RoleTexture(string name)
        {
            var tp = $"{TexDir}/TXR_{name}.png";
            var ti = AssetImporter.GetAtPath(tp) as TextureImporter;
            if (!ti) return null;
            if (ti.maxTextureSize != 512 || ti.wrapMode != TextureWrapMode.Clamp)
            {
                ti.maxTextureSize = 512; ti.mipmapEnabled = true; ti.wrapMode = TextureWrapMode.Clamp; ti.anisoLevel = 2;
                ti.SaveAndReimport();
            }
            return AssetDatabase.LoadAssetAtPath<Texture2D>(tp);
        }

        static Material Variant(string role, string variant, Color c, Shader shader)
        {
            var path = $"{MatDir}/DC_{role}_{variant}.mat";
            var src = DcMaterial(role, shader);
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (!m) { m = new Material(src); AssetDatabase.CreateAsset(m, path); }
            else m.CopyPropertiesFromMaterial(src);
            // the painted body map averages ~0.8: lift the paint so the colour reads as the colour
            m.SetColor("_BaseColor", role == "Paint" ? new Color(Mathf.Min(1, c.r * 1.18f), Mathf.Min(1, c.g * 1.18f), Mathf.Min(1, c.b * 1.18f)) : c);
            EditorUtility.SetDirty(m);
            return m;
        }

        static void SavePrefab(GameObject model, string name, params (string slot, Material mat)[] swaps)
        {
            var inst = (GameObject)PrefabUtility.InstantiatePrefab(model);
            inst.name = name;
            foreach (var swap in swaps)
                foreach (var r in inst.GetComponentsInChildren<Renderer>())
                {
                    var arr = r.sharedMaterials;
                    for (int i = 0; i < arr.Length; i++) if (arr[i] && arr[i].name == $"DC_{swap.slot}") arr[i] = swap.mat;
                    r.sharedMaterials = arr;
                }
            // one collider for the whole piece; trees and palms only round the trunk
            var rs = inst.GetComponentsInChildren<Renderer>();
            var b = rs[0].bounds; foreach (var r in rs) b.Encapsulate(r.bounds);
            if (name.StartsWith("CITY_Tree"))
            {
                var cc = inst.AddComponent<CapsuleCollider>();
                cc.radius = 0.28f; cc.height = 3f; cc.center = new Vector3(0, 1.5f, 0);
            }
            else if (!name.StartsWith("CITY_Hortensia"))
            {
                var bc = inst.AddComponent<BoxCollider>();
                bc.center = inst.transform.InverseTransformPoint(b.center);
                bc.size = b.size;
            }
            foreach (var t in inst.GetComponentsInChildren<Transform>()) t.gameObject.isStatic = true;
            PrefabUtility.SaveAsPrefabAsset(inst, $"{PrefabDir}/{name}.prefab");
            Object.DestroyImmediate(inst);
        }
    }
}

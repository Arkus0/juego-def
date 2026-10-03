using System.Collections.Generic;
using System.IO;
using System.Linq;
using JuegoDef.Env;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace JuegoDef.City
{
    /// <summary>
    /// Shopfronts with personality (Docs/design/CITY_STYLE_DCPLUS.md; Shenmue: "rótulos a escala, género en la puerta").
    /// Every business of the seed gets, as entities that belong to something:
    ///   fascia  - one painted board across the shop's own bays (replacing the kit's per-bay boards) above the door;
    ///   blade   - a projecting sign on an iron arm at a pier of the facade free of balconies and windows;
    ///   awning  - the shop's striped canvas, under its fascia (only where the shop would have one);
    ///   goods   - what the shop puts out, beside the door, on the side away from it, only where the street keeps a
    ///             1.6 m way past it.
    /// Nothing is placed where it would touch a building, a prop or another entity (physics check first).
    /// </summary>
    public static class CityShopfronts
    {
        static string SignsJson => Path.GetFullPath(Path.Combine(Application.dataPath, "../../../Tools/city_ivanix/reconstruction/city_signs.json"));
        const string MatDir = "Assets/JuegoDef/City/DCMaterials";

        [MenuItem("JuegoDef/CITY/Dreamcast+: 3 shopfronts (signs, awnings, goods)")]
        static void Menu() => Debug.Log(Apply());

        public static string Apply()
        {
            var doc = JObject.Parse(File.ReadAllText(SignsJson));
            var root = GameObject.Find("CITY_IVX_Buildings");
            CityEntities.IndexBuildings(root.transform);
            var shader = Shader.Find("JuegoDef/City/DC Plus");
            var iron = EnvKit.Mat("ENV_Metal_Iron");
            var dark = EnvKit.Mat("ENV_Joinery_Walnut");
            var groupRoot = root.transform.Find("SHOPFRONTS");
            if (groupRoot) Object.DestroyImmediate(groupRoot.gameObject);
            groupRoot = new GameObject("SHOPFRONTS").transform;
            groupRoot.SetParent(root.transform, false);
            Physics.SyncTransforms();
            int fascias = 0, blades = 0, awnings = 0, goods = 0, skipped = 0;
            var byId = root.transform.Cast<Transform>().Where(t => t.name.StartsWith("BLD_")).ToDictionary(t => t.name.Substring(4).Split(' ')[0], t => t);

            foreach (var kv in doc)
            {
                if (!byId.TryGetValue(kv.Key, out var bld)) { skipped++; continue; }
                var rec = (JObject)kv.Value;
                string cat = (string)rec["category"];
                var g = new GameObject($"SHOP_{kv.Key} {rec["name"]}").transform;
                g.SetParent(groupRoot, false);
                var ident = g.gameObject.AddComponent<JDSpatialIdentity>();
                ident.stableId = "SHOP_" + kv.Key; ident.kind = "Shopfront:" + cat; ident.sourceId = (string)rec["name"]; ident.referenceOutline = new Vector3[0];

                var n = bld.forward;
                var right = bld.right;
                float floorY = bld.position.y;
                var own = new HashSet<Collider>(bld.GetComponentsInChildren<Collider>());
                // the shop's extent: the kit's own fascias (or the shopfront modules) on the ground floor
                var marks = bld.GetComponentsInChildren<Transform>(true).Where(t => t.name.StartsWith("ENV_Shop_Fascia") || t.name.StartsWith("ENV_Awning") || t.name.StartsWith("ENV_Fascia_Lamp")).ToList();
                var shopMods = bld.GetComponentsInChildren<Transform>(true).Where(t => t.name.StartsWith("ENV_Wall_") && t.name.Contains("Shopfront") || t.name.StartsWith("ENV_Shopfront_Door")).ToList();
                var refs = marks.Where(t => t.name.StartsWith("ENV_Shop_Fascia")).Select(t => t.position).Concat(shopMods.Select(t => t.position)).ToList();
                float wTotal = bld.lossyScale.x * BaysOf(bld) * 2f;
                float u0 = 0.4f, u1 = wTotal - 0.4f;
                if (refs.Count > 0)
                {
                    var us = refs.Select(p => Vector3.Dot(p - bld.position, right)).ToList();
                    u0 = Mathf.Max(0.3f, us.Min() - 0.3f);
                    u1 = Mathf.Min(wTotal - 0.3f, us.Max() + 2f * bld.lossyScale.x + 0.3f);
                }
                if (u1 - u0 < 1.6f) { u0 = Mathf.Max(0.3f, (wTotal - 2.4f) / 2f); u1 = Mathf.Min(wTotal - 0.3f, u0 + 2.4f); }
                foreach (var m in marks.Where(m => !marks.Contains(m.parent)).ToList()) if (m) Object.DestroyImmediate(m.gameObject);
                // the kit's small sign panels on the shop's ground floor give way to the shop's own painted sign
                foreach (var sp in bld.GetComponentsInChildren<Transform>(true).Where(t => t.name.StartsWith("ENV_Sign_Panel") && !(t.parent && t.parent.name.StartsWith("ENV_Sign_Panel"))).ToList())
                {
                    float h = sp.position.y - floorY, u = Vector3.Dot(sp.position - bld.position, right);
                    if (h > 1.5f && h < 4.6f && u > u0 - 0.6f && u < u1 + 0.6f) Object.DestroyImmediate(sp.gameObject);
                }
                Physics.SyncTransforms();

                // the facade's face, found from the street
                float FaceAt(float u, float y)
                {
                    var o = bld.position + right * u + Vector3.up * y + n * 3f;
                    var hits = Physics.RaycastAll(o, -n, 3.5f).Where(h => own.Contains(h.collider)).OrderBy(h => h.distance).ToList();
                    return hits.Count > 0 ? 3f - hits[0].distance : 0.45f;
                }
                // fascia over the shop's bays, just under the first floor
                float fw = Mathf.Min(u1 - u0, 9f), fh = cat == "hotel" || cat == "ayuntamiento" || cat == "cuartel" ? 0.62f : 0.66f;
                float um = (u0 + u1) / 2f;
                float face = Mathf.Max(FaceAt(um, 2.7f), FaceAt(u0 + 0.3f, 2.7f), FaceAt(u1 - 0.3f, 2.7f));
                var fc = bld.position + right * um + Vector3.up * (2.36f + fh / 2f) + n * (face + 0.05f);
                var fasciaMat = SignMat((string)rec["fascia"], shader, kv.Key + "_fascia", cat == "caja" || cat == "farmacia" ? 0.6f : 0.35f);
                Board(g, "ROTULO", fc, n, right, fw, fh, fasciaMat, dark);
                fascias++;

                // awning under the fascia
                if (rec["awning"] != null)
                {
                    var am = SignMat((string)rec["awning"], shader, kv.Key + "_awning", 0f, true);
                    float aw = fw * 0.92f, ad = 1.0f;
                    var top = bld.position + right * um + Vector3.up * 2.33f + n * (face + 0.04f);
                    var tilt = Quaternion.LookRotation(n) * Quaternion.Euler(22f, 0, 0);
                    var mid = top + (tilt * Vector3.forward) * (ad / 2f);
                    if (!Blocked(mid, new Vector3(aw / 2f, 0.1f, ad / 2f), tilt, own))
                    {
                        Slab(g, "TOLDO", mid, tilt, new Vector3(aw, 0.03f, ad), am);
                        var front = top + (tilt * Vector3.forward) * ad;
                        Slab(g, "TOLDO_FALDON", front + Vector3.down * 0.12f, Quaternion.LookRotation(n), new Vector3(aw, 0.24f, 0.02f), am);
                        awnings++;
                    }
                }

                // blade sign on an iron arm at a pier free of balconies
                if (rec["blade"] != null)
                {
                    var bm = SignMat((string)rec["blade"], shader, kv.Key + "_blade", cat == "farmacia" ? 0.9f : 0.3f);
                    bool cross = cat == "farmacia";
                    float bw = cross ? 0.7f : 0.78f, bh = cross ? 0.7f : 0.52f;
                    foreach (float u in new[] { 0.45f, wTotal - 0.45f })
                    {
                        float bf = FaceAt(u, 3.4f);
                        var arm0 = bld.position + right * u + Vector3.up * 3.55f + n * bf;
                        var plate = arm0 + n * (0.18f + bw / 2f) + Vector3.down * (0.04f + bh / 2f);
                        var rotPlate = Quaternion.LookRotation(right, Vector3.up);       // seen by people walking along the street
                        if (Blocked(plate, new Vector3(0.05f, bh / 2f + 0.05f, bw / 2f + 0.05f), rotPlate, own)) continue;
                        Slab(g, "BANDEROLA_BRAZO", arm0 + n * (0.5f * (bw + 0.3f)), Quaternion.LookRotation(n), new Vector3(0.035f, 0.035f, bw + 0.3f), iron);
                        Board(g, "BANDEROLA", plate, right, n, bw, bh, bm, dark, twoSided: true);
                        blades++;
                        break;
                    }
                }

                // what the shop puts out, beside the door, never in the way
                // the shop's sign, blade and awning come first: wall-mounted additions of the house that they would cover
                // or cut through (air conditioners, boxes, plaques, dishes, lanterns) are taken down
                Physics.SyncTransforms();
                foreach (var el in g.GetComponentsInChildren<Renderer>().Where(r => r.name.StartsWith("ROTULO") || r.name.StartsWith("BANDEROLA") || r.name.StartsWith("TOLDO")).ToList())
                {
                    var eb = el.bounds; eb.Expand(0.06f);
                    foreach (var other in bld.GetComponentsInChildren<Renderer>(true).Where(r => r && WallAddition(r.transform) && r.bounds.Intersects(eb)).ToList())
                    {
                        var top = other.transform;
                        while (top.parent != null && top.parent != bld && WallAddition(top.parent)) top = top.parent;
                        if (top) Object.DestroyImmediate(top.gameObject);
                    }
                }
                string kind = (string)rec["goods"];
                if (kind != null && Goods(g, bld, own, kind, u0, u1, face, ref goods)) { }
            }
            EditorSceneManager.MarkSceneDirty(root.scene);
            EditorSceneManager.SaveScene(root.scene);
            AssetDatabase.SaveAssets();
            return $"JD_CITY_SHOPFRONTS fascias={fascias} blades={blades} awnings={awnings} goods={goods} skipped={skipped}";
        }

        static bool WallAddition(Transform t)
        {
            var n = t.name;
            return n.StartsWith("ENV_AC_Unit") || n.StartsWith("ENV_Telecom_Box") || n.StartsWith("ENV_Alarm_Box") || n.StartsWith("ENV_Satellite")
                || n.StartsWith("ENV_Extractor_Vent") || n.StartsWith("ENV_Sign_Panel") || n.StartsWith("ENV_Plaque") || n.StartsWith("ENV_Wall_Lantern")
                || n.StartsWith("ENV_Gas_Pipe") || n.StartsWith("Prop_Vine");
        }

        static int BaysOf(Transform bld)
        {
            // "BLD_<id> [..|..|type|BxD|Fp]": bays from the name
            var parts = bld.name.Split('|');
            var bd = parts.FirstOrDefault(p => p.Contains("x") && char.IsDigit(p[0]));
            return bd != null && int.TryParse(bd.Split('x')[0], out var b) ? b : 3;
        }

        static bool Blocked(Vector3 c, Vector3 half, Quaternion r, HashSet<Collider> ignore)
        {
            return Physics.OverlapBox(c, half, r).Any(col => !col.name.StartsWith("TERRAIN") && (ignore == null || !ignore.Contains(col)) || ignore != null && ignore.Contains(col) && OverlapsHard(col));
        }

        // within the building's own colliders only real volumes (balconies, rejas, shutters, lamps) block a sign
        static bool OverlapsHard(Collider col)
        {
            var n = col.name;
            return n.Contains("Balcony") || n.Contains("Reja") || n.Contains("Shutter") || n.Contains("Lamp") || n.Contains("Lantern") || n.Contains("Gallery") || n.Contains("Sign");
        }

        static Material SignMat(string texPath, Shader shader, string key, float emission, bool twoSided = false)
        {
            var ti = AssetImporter.GetAtPath(texPath) as TextureImporter;
            if (ti && (ti.maxTextureSize != 1024 || ti.anisoLevel != 4)) { ti.maxTextureSize = 1024; ti.anisoLevel = 4; ti.SaveAndReimport(); }
            var tex = AssetDatabase.LoadAssetAtPath<Texture2D>(texPath);
            var path = $"{MatDir}/SIGN_{key}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (!m) { m = new Material(shader); AssetDatabase.CreateAsset(m, path); }
            m.SetTexture("_BaseMap", tex);
            m.SetFloat("_MipBias", 0f);
            m.SetFloat("_SpecAmount", 0.08f);
            m.SetFloat("_Cull", twoSided ? 0 : 2);
            m.SetTexture("_EmissionMap", tex);
            m.SetColor("_EmissionColor", Color.white * emission * 0.0f);   // lit at dusk by the rig; daylight look first
            EditorUtility.SetDirty(m);
            return m;
        }

        static void Board(Transform g, string name, Vector3 c, Vector3 normal, Vector3 along, float w, float h, Material face, Material frame, bool twoSided = false)
        {
            var q = GameObject.CreatePrimitive(PrimitiveType.Quad);
            q.name = name;
            q.transform.SetParent(g, false);
            q.transform.SetPositionAndRotation(c, Quaternion.LookRotation(-normal, Vector3.up));
            q.transform.localScale = new Vector3(w, h, 1);
            Object.DestroyImmediate(q.GetComponent<Collider>());
            q.GetComponent<MeshRenderer>().sharedMaterial = face;
            q.isStatic = true;
            if (twoSided)
            {
                var b = Object.Instantiate(q, g);
                b.name = name + "_DORSO";
                b.transform.SetPositionAndRotation(c - normal * 0.02f, Quaternion.LookRotation(normal, Vector3.up));
            }
            // the board's thickness and frame behind the painted face
            Slab(g, name + "_MARCO", c - normal * (twoSided ? 0.01f : 0.035f), Quaternion.LookRotation(normal, Vector3.up), new Vector3(w + 0.06f, h + 0.06f, twoSided ? 0.012f : 0.06f), frame);
        }

        static GameObject Slab(Transform g, string name, Vector3 c, Quaternion r, Vector3 size, Material m)
        {
            var b = GameObject.CreatePrimitive(PrimitiveType.Cube);
            b.name = name;
            b.transform.SetParent(g, false);
            b.transform.SetPositionAndRotation(c, r);
            b.transform.localScale = size;
            b.GetComponent<MeshRenderer>().sharedMaterial = m;
            b.isStatic = true;
            return b;
        }

        /// <summary>Goods outside the shop, as one entity: placed on the side of the shop away from its door, only
        /// where 1.6 m of street stays free in front of them.</summary>
        static bool Goods(Transform g, Transform bld, HashSet<Collider> own, string kind, float u0, float u1, float face, ref int count)
        {
            var n = bld.forward; var right = bld.right;
            var door = bld.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name.StartsWith("ENV_Shopfront_Door"));
            float ud = door ? Vector3.Dot(door.position - bld.position, right) : (u0 + u1) / 2f;
            var items = new List<(string m, Vector3 off, float rot, float dy)>();
            float depth, half = 0.75f;
            switch (kind)
            {
                case "fruta":
                    items.Add(("ENV_Pallet", new Vector3(0, 0, 0), 0, 0));
                    items.Add(("ENV_Prop_FarmCrate_Apple", new Vector3(-0.3f, 0, 0.1f), 0, 0.14f));
                    items.Add(("ENV_Prop_FarmCrate_Carrot", new Vector3(0.32f, 0, -0.1f), 0, 0.14f));
                    depth = 0.9f; break;
                case "pescado":
                    items.Add(("ENV_Pallet", new Vector3(0, 0, 0), 0, 0));
                    items.Add(("ENV_Crate_Fish", new Vector3(-0.3f, 0, 0.15f), 0, 0.14f));
                    items.Add(("ENV_Crate_Fish", new Vector3(0.32f, 0, -0.1f), 8, 0.14f));
                    depth = 0.9f; break;
                case "cajas":
                    items.Add(("ENV_Prop_Crate_Wooden", new Vector3(0, 0, 0), 4, 0));
                    items.Add(("ENV_Box_Cardboard", new Vector3(0.7f, 0, 0.05f), -10, 0));
                    depth = 0.95f; break;
                case "barriles":
                    items.Add(("ENV_Prop_Barrel", new Vector3(-0.35f, 0, 0), 0, 0));
                    items.Add(("ENV_Prop_Barrel", new Vector3(0.4f, 0, 0.05f), 30, 0));
                    depth = 0.7f; break;
                case "ferreteria":
                    items.Add(("ENV_Prop_Bucket", new Vector3(-0.3f, 0, 0), 0, 0));
                    items.Add(("ENV_Prop_Bucket", new Vector3(0.1f, 0, 0.1f), 0, 0));
                    items.Add(("ENV_AFrame_Board", new Vector3(0.7f, 0, 0.1f), 0, 0));
                    depth = 0.7f; break;
                case "terraza":    // the bar's own terrace set: table, four chairs and the parasol through the table
                    items.Add(("CITY_Terrace_Set", Vector3.zero, 0, 0));
                    depth = 2.2f; half = 1.1f; break;
                case "prensa":     // the newsagent's board and the gumball machine every child stopped at
                    items.Add(("ENV_AFrame_Board", new Vector3(-0.25f, 0, 0), 0, 0));
                    items.Add(("CITY_Gumball", new Vector3(0.45f, 0, -0.05f), 0, 0));
                    depth = 0.6f; break;
                default:   // caballete, pan: a sandwich board by the door
                    items.Add(("ENV_AFrame_Board", Vector3.zero, 0, 0));
                    depth = 0.6f; break;
            }
            // side away from the door, within the shop's own front
            float edge = half + 0.15f;
            foreach (float u in new[] { ud < (u0 + u1) / 2f ? u1 - edge : u0 + edge, ud < (u0 + u1) / 2f ? u0 + edge : u1 - edge })
            {
                if (Mathf.Abs(u - ud) < half + 0.55f) continue;           // never in front of the door
                var c = bld.position + right * u + n * (face + 0.35f + depth / 2f);
                var hit = Physics.Raycast(c + Vector3.up * 2f, Vector3.down, out var gh, 4f) ? gh.point.y : bld.position.y;
                c.y = hit;
                // 1.6 m of street must stay free beyond the goods
                var way = c + n * (depth / 2f + 0.8f) + Vector3.up * 1f;
                if (Physics.CheckBox(way, new Vector3(0.6f, 0.8f, 0.8f), bld.rotation)) continue;
                var eg = new GameObject("GENERO_" + kind).transform;
                eg.SetParent(g, false);
                eg.SetPositionAndRotation(c, bld.rotation);
                foreach (var (m, off, rot, dy) in items)
                {
                    if (!CityEntities.Exists(m)) continue;
                    CityEntities.Place(m, eg, off + Vector3.up * dy, rot);
                }
                // the goods are one entity: out of the facade, its rejas and sills, the lamp posts and the neighbours' goods
                if (!CityEntities.Resolve(eg.gameObject, c2 => c2.name.StartsWith("TERRAIN"), 0.5f, out _)) { Object.DestroyImmediate(eg.gameObject); continue; }
                foreach (var tr in eg.GetComponentsInChildren<Transform>(true)) tr.gameObject.isStatic = true;
                Physics.SyncTransforms();
                count++;
                return true;
            }
            return false;
        }
    }
}

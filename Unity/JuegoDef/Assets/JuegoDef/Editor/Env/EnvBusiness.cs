using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// Ground-floor programme of commercial plots (owner audit 2026-09-29, points 8/10/35/44): every mixed_commercial
    /// plot becomes a specific business — bar, café, sidrería, bakery, pharmacy, tobacconist, hardware, greengrocer,
    /// bank, hairdresser, workshop, garage, a closed shop to let, or a ground floor turned into a home — drawn by the
    /// street's personality from Env/Grammar/businesses.json. A named business is used once per district. The
    /// business decides the ground-floor bays (roller door, gate, windows), the interior behind the glass, the
    /// fascia lettering (Tools/env_signs.py textures), a hanging or light-box sign, a chalkboard, goods at the door,
    /// the ATM, the "vado" plate, the "SE ALQUILA" notice. Sign materials are made on demand in Derived/ENV/Signs.
    /// </summary>
    public static class EnvBusiness
    {
        const string SignFolder = EnvKit.Derived + "/Signs";
        static JObject spec;
        static JObject Spec => spec ??= JObject.Parse(EnvKit.ReadText(EnvKit.Grammar + "/businesses.json"));
        static readonly HashSet<string> Used = new HashSet<string>();
        // business type per built building id ("K9_0_2" -> "farmacia"): the plaza dressing only sets a bar terrace
        // in front of a drinking/eating place, never a pharmacy or a shoe shop
        public static readonly Dictionary<string, string> TypeByBuilding = new Dictionary<string, string>();

        public static void Reset()
        {
            spec = null;
            Used.Clear();
            TypeByBuilding.Clear();
        }

        /// <summary>True when the building's ground floor is a bar, café or sidrería — the businesses that own a terrace.</summary>
        public static bool IsHospitality(string buildingId)
        {
            string t;
            return TypeByBuilding.TryGetValue(buildingId, out t) && (t == "bar" || t == "cafe" || t == "sidreria");
        }

        static JObject Business(string id) => Spec["businesses"].Cast<JObject>().FirstOrDefault(b => (string)b["id"] == id);
        public static string TypeOf(BuildingSpec s)
        {
            if (string.IsNullOrEmpty(s.business)) return "";
            var b = Business(s.business);
            return b != null ? (string)b["type"] : s.business;
        }
        static JObject TypeSpec(string type) => Spec["types"][type] as JObject;

        public static string RoomFor(BuildingSpec s)
        {
            var t = TypeOf(s);
            if (t == "") return "Tienda";
            return (string)TypeSpec(t)?["room"] ?? "Tienda";
        }

        /// <summary>Draws the business of a commercial plot by street kind; generic types (garage, closed, home)
        /// repeat, named ones do not.</summary>
        public static void Assign(BuildingSpec bs, string kind)
        {
            if (bs.type != "mixed_commercial") return;
            var rng = new System.Random(bs.seed * 3571 + 11);
            var weights = (JObject)(Spec["kinds"][kind] ?? Spec["kinds"]["residencial"]);
            for (int attempt = 0; attempt < 6; attempt++)
            {
                int total = weights.Properties().Sum(p => (int)p.Value), r = rng.Next(total);
                string type = null;
                foreach (var p in weights.Properties())
                {
                    if (r < (int)p.Value) { type = p.Name; break; }
                    r -= (int)p.Value;
                }
                var named = Spec["businesses"].Cast<JObject>().Where(b => (string)b["type"] == type && !Used.Contains((string)b["id"])).ToList();
                if (named.Count > 0)
                {
                    var b = named[rng.Next(named.Count)];
                    Used.Add((string)b["id"]);
                    bs.business = (string)b["id"];
                    TypeByBuilding[bs.id] = type;
                    return;
                }
                if (type == "garaje" || type == "cerrado" || type == "vivienda" || type == "taller")
                {
                    bs.business = type;
                    TypeByBuilding[bs.id] = type;
                    return;
                }
            }
            bs.business = "cerrado";
            TypeByBuilding[bs.id] = "cerrado";
        }

        public static void AssignLodging(BuildingSpec bs)
        {
            var named = Spec["businesses"].Cast<JObject>().Where(b => (string)b["type"] == "hostal" && !Used.Contains((string)b["id"])).ToList();
            if (named.Count == 0) return;
            var b = named[new System.Random(bs.seed * 17 + 5).Next(named.Count)];
            Used.Add((string)b["id"]);
            bs.business = (string)b["id"];
            TypeByBuilding[bs.id] = "hostal";
        }

        /// <summary>Ground-floor bay codes the business needs: a garage gets a roller door, a workshop a timber gate,
        /// a ground floor turned into a home gets windows and a portal instead of shop glass.</summary>
        public static string[] RewriteGround(BuildingSpec s, string[] rows)
        {
            var t = TypeOf(s);
            if (t == "" || rows == null || rows.Length == 0) return rows;
            var g = rows[0].ToCharArray();
            var shop = Enumerable.Range(0, g.Length).Where(i => "SEeR".IndexOf(g[i]) >= 0).ToList();
            if (shop.Count == 0) return rows;
            var door = (string)TypeSpec(t)?["door"];
            if (door == "roller")
            {
                // one wide garage door (the middle shop bay), the rest closed wall
                int k = shop[shop.Count / 2];
                foreach (var i in shop) g[i] = i == k ? 'R' : 'P';
            }
            else if (door == "gate")
            {
                int k = shop[0];
                foreach (var i in shop) g[i] = i == k ? 'G' : g[i] == 'E' || g[i] == 'e' ? 'E' : g[i];
            }
            else if (door == "portal")
            {
                // a shop turned into a home: its door becomes the portal, one old display bay a window, the rest wall
                int door0 = shop.FirstOrDefault(i => g[i] == 'E' || g[i] == 'e');
                if (!shop.Any(i => g[i] == 'E' || g[i] == 'e')) door0 = shop[0];
                int win = shop.Where(i => i != door0).OrderBy(i => Mathf.Abs(i - door0)).DefaultIfEmpty(-1).First();
                foreach (var i in shop) g[i] = i == door0 ? 'D' : i == win && shop.Count >= 3 ? 'W' : 'P';
            }
            else
            {
                // one shop = its door and at most two display windows beside it (owner: "otra vez locos con tantas
                // puertas y ventanas"); the other bays of the frontage are wall. Closed shops keep a lowered shutter.
                var doorBay = shop.Where(i => g[i] == 'E' || g[i] == 'e').DefaultIfEmpty(shop[shop.Count / 2]).First();
                if (g[doorBay] != 'E' && g[doorBay] != 'e') g[doorBay] = 'E';
                var keep = shop.Where(i => i != doorBay).OrderBy(i => Mathf.Abs(i - doorBay)).Take(t == "cerrado" ? 1 : 2).ToList();
                foreach (var i in shop)
                {
                    if (i == doorBay) { if (t == "cerrado") g[i] = 'E'; continue; }
                    if (!keep.Contains(i)) g[i] = 'P';
                    else if (t == "cerrado") g[i] = 'R';
                    else if (g[i] == 'R') g[i] = 'S';
                }
            }
            var o = (string[])rows.Clone();
            o[0] = new string(g);
            return o;
        }

        // ------------------------------------------------------------------ materials

        static Material Lit(string name, string texture, Color colour, float smooth, Color? emission = null)
        {
            EnvKit.EnsureFolder(SignFolder);
            var path = $"{SignFolder}/{name}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (!m) { m = new Material(Shader.Find("Universal Render Pipeline/Lit")); AssetDatabase.CreateAsset(m, path); }
            if (texture != null) m.SetTexture("_BaseMap", EnvKit.Tex(texture));
            m.SetColor("_BaseColor", colour);
            m.SetFloat("_Smoothness", smooth);
            m.SetFloat("_Metallic", 0);
            if (emission.HasValue)
            {
                m.SetColor("_EmissionColor", emission.Value);
                m.SetTexture("_EmissionMap", texture != null ? EnvKit.Tex(texture) : null);
                m.EnableKeyword("_EMISSION");
                m.globalIlluminationFlags = MaterialGlobalIlluminationFlags.RealtimeEmissive;
            }
            m.enableInstancing = true;
            EditorUtility.SetDirty(m);
            return m;
        }

        static readonly Dictionary<string, string> Made = new Dictionary<string, string>();

        public static string SignMat(string id, bool faded = false)
        {
            var key = (faded ? "ENV_SignOld_" : "ENV_Sign_") + id;
            if (Made.ContainsKey(key) && EnvKit.HasMat(key)) return key;
            var b = Business(id);
            string style = (string)b?["style"] ?? "painted";
            float smooth = style == "enamel" ? 0.6f : style == "gilded" ? 0.5f : style == "modern" ? 0.35f : 0.15f;
            // light boxes glow a little even by day (modern shops); painted boards never do
            Color? glow = style == "modern" && !faded ? Color.white * 0.35f : (Color?)null;
            Lit(key, "T_ENV_Sign_" + id, faded ? new Color(0.72f, 0.7f, 0.66f) : Color.white, faded ? 0.05f : smooth, glow);
            Made[key] = key;
            return key;
        }

        public static string BoardMat(string id)
        {
            var key = "ENV_SignBg_" + id;
            if (Made.ContainsKey(key) && EnvKit.HasMat(key)) return key;
            var b = Business(id);
            Lit(key, null, EnvKit.Hex((string)b["bg"]), 0.2f);
            Made[key] = key;
            return key;
        }

        public static string TextureMat(string key, string texture, float smooth = 0.2f, Color? glow = null)
        {
            if (Made.ContainsKey(key) && EnvKit.HasMat(key)) return key;
            Lit(key, texture, Color.white, smooth, glow);
            Made[key] = key;
            return key;
        }

        // ------------------------------------------------------------------ dressing

        /// <summary>Business dressing on a built building (local frame: street face z = 0 facing +z, ground floor
        /// y = 0). <paramref name="tryPlace"/> places only where the facade has room (EnvClearance).</summary>
        public static void Dress(BuildingSpec s, Transform root, string[] rows, System.Random rng, Dictionary<string, string> joinMap,
                                 System.Func<string, Transform, Vector3, float, Vector3?, GameObject> tryPlace,
                                 System.Func<string, Transform, Vector3, float, Vector3?, GameObject> place)
        {
            var t = TypeOf(s);
            if (t == "" || t == "vivienda") return;
            var ts = TypeSpec(t);
            var named = Business(s.business);
            var g = EnvKit.Group(root, "Dressing");
            if (t == "hostal")
            {
                int portal = rows[0].IndexOfAny(new[] { 'A', 'O', 'D', 'o' });
                if (portal < 0) return;
                float px = 1 + 2 * portal;
                var plaque = tryPlace("ENV_Sign_Panel", g, new Vector3(px, 2.62f, WallFace + 0.016f), 0, new Vector3(1.5f, 0.3f, 1));
                if (plaque) EnvKit.Remap(plaque, new Dictionary<string, string> { { "ENV_Sign_Board", SignMat(s.business) } });
                var br = tryPlace("ENV_Sign_Bracket", g, new Vector3(px + (portal == 0 ? 1.15f : -1.15f), 0.35f, 0), 0, null);
                if (br) EnvKit.Remap(br, With(joinMap, "ENV_Sign_Face", TextureMat("ENV_Blade_" + s.business, "T_ENV_Blade_" + s.business, 0.2f)));
                return;
            }
            var shop = Enumerable.Range(0, s.bays).Where(i => "SEeR".IndexOf(rows[0][i]) >= 0).ToList();
            var doorBays = Enumerable.Range(0, s.bays).Where(i => rows[0][i] == 'E' || rows[0][i] == 'e').ToList();
            // runs of consecutive shop bays carry one fascia each; the lettering goes on the longest run
            var runs = new List<(int a, int b)>();
            foreach (var i in shop)
                if (runs.Count > 0 && runs[runs.Count - 1].b == i - 1) runs[runs.Count - 1] = (runs[runs.Count - 1].a, i);
                else runs.Add((i, i));
            bool modern = s.family == "modern" || (string)named?["style"] == "modern";
            var main = runs.OrderByDescending(r => r.b - r.a).FirstOrDefault();
            foreach (var run in runs)
            {
                float x0 = 2 * run.a + (run.a == 0 ? 0.2f : 0.05f), x1 = 2 * run.b + 2 - (run.b == s.bays - 1 ? 0.2f : 0.05f);
                float cx = (x0 + x1) / 2, w = x1 - x0;
                bool lettering = named != null && run.Equals(main);
                if (!modern)
                {
                    // timber fascia board spanning the run (one board, not one per 2 m bay)
                    var f = place("ENV_Shop_Fascia", g, new Vector3(cx, 0, 0), 0, new Vector3(w / 1.94f, 1, 1));
                    EnvKit.Remap(f, joinMap);
                    if (named != null) EnvKit.Remap(f, new Dictionary<string, string> { { "ENV_Sign_Board", BoardMat(s.business) } });
                    if (lettering)
                    {
                        float sw = Mathf.Min(w - 0.25f, 0.34f * 5f);
                        var p = EnvKit.Place("ENV_Sign_Panel", g, new Vector3(cx, 2.675f, 0.143f), 0, new Vector3(sw, 0.34f, 1));
                        EnvKit.Remap(p, new Dictionary<string, string> { { "ENV_Sign_Board", SignMat(s.business, t == "cerrado") } });
                    }
                }
                else if (lettering)
                {
                    // light box / vinyl lettering straight on the wall over the opening
                    float sw = Mathf.Min(w - 0.1f, 0.44f * 5f);
                    var p = place("ENV_Sign_Panel", g, new Vector3(cx, 2.68f, WallFace + 0.016f), 0, new Vector3(sw, 0.44f, 1));
                    EnvKit.Remap(p, new Dictionary<string, string> { { "ENV_Sign_Board", SignMat(s.business) }, { "MI_WoodTrim", "ENV_Metal_Galvanised" } });
                }
                // awning over part of the run, by type
                float awn = (float?)ts?["awning"] ?? 0f;
                bool awning = !string.IsNullOrEmpty(s.awning) || rng.NextDouble() < awn;
                // or a pair of gooseneck lamps lighting the fascia (cohesion pass: shops need exterior light and a
                // silhouette that tells one shop from the next at 10-20 m)
                if (!awning && lettering && !modern && rng.NextDouble() < 0.6)
                    foreach (var sx in new[] { -1f, 1f })
                        tryPlace("ENV_Fascia_Lamp", g, new Vector3(cx + sx * Mathf.Min(w * 0.3f, 0.95f), 3.0f, 0), 0, null);
                if (awning)
                {
                    string canvas = string.IsNullOrEmpty(s.awning) ? new[] { "ENV_Canvas_Green", "ENV_Canvas_Red", "ENV_Canvas_Cream" }[rng.Next(3)] : s.awning;
                    for (int i = run.a; i <= run.b; i++)
                        if (rows[0][i] != 'R')
                            EnvKit.Remap(place("ENV_Awning", g, new Vector3(1 + 2 * i, 0, 0), 0, null), new Dictionary<string, string> { { "ENV_Canvas_Green", canvas } });
                }
            }
            if (named == null && t == "cerrado" && shop.Count > 0 && rng.NextDouble() < 0.5)
            {
                // a vanished business's faded fascia over the closed shop
                var ghost = Spec["businesses"].Cast<JObject>().ElementAt(rng.Next(Spec["businesses"].Count()));
                var run = main;
                float cx = run.a + run.b + 1;
                var p = EnvKit.Place("ENV_Sign_Panel", g, new Vector3(cx, 2.675f, 0.143f), 0, new Vector3(Mathf.Min(2 * (run.b - run.a + 1) - 0.4f, 1.6f), 0.3f, 1));
                EnvKit.Remap(p, new Dictionary<string, string> { { "ENV_Sign_Board", SignMat((string)ghost["id"], true) } });
            }
            // hanging sign on a wrought-iron bracket with the trade icon (painted / gilded shops)
            if (named?["icon"] != null && rng.NextDouble() < ((float?)ts?["bracket"] ?? 0f) && shop.Count > 0)
            {
                // above the fascia, at a bay joint of the shop or at its outer edge, wherever the facade has room
                var xs = new List<float> { 2 * shop[0] + 0.12f, 2 * shop[shop.Count - 1] + 1.88f };
                for (int i = 1; i < shop.Count; i++) xs.Add(2 * shop[i]);
                foreach (var bx in xs)
                {
                    var br = tryPlace("ENV_Sign_Bracket", g, new Vector3(bx, 0.62f, 0), 0, null);
                    if (!br) continue;
                    EnvKit.Remap(br, With(joinMap, "ENV_Sign_Face", TextureMat("ENV_Blade_" + s.business, "T_ENV_Blade_" + s.business, 0.2f)));
                    break;
                }
            }
            // pharmacy: green cross light box
            if ((bool?)ts?["cross"] == true)
            {
                float bx = shop.Count > 0 ? 2 * shop[shop.Count - 1] + 1.9f : 1f;
                var c = tryPlace("ENV_Blade_Sign", g, new Vector3(Mathf.Min(bx, s.bays * 2 - 0.4f), 0.2f, 0), 0, null);
                if (c) EnvKit.Remap(c, new Dictionary<string, string> { { "ENV_Sign_Board", TextureMat("ENV_Cross_Pharmacy", "T_ENV_Cross_Pharmacy", 0.5f, new Color(0.35f, 1.4f, 0.55f)) } });
            }
            // bank: cash machine on a plain ground bay beside the door
            if ((bool?)ts?["atm"] == true)
            {
                var plain = Enumerable.Range(0, s.bays).Where(i => rows[0][i] == 'P' || rows[0][i] == 'S').ToList();
                foreach (var i in plain)
                    if (tryPlace("ENV_ATM", g, new Vector3(1 + 2 * i + (rows[0][i] == 'S' ? 0.0f : 0f), 0, rows[0][i] == 'S' ? 0.0f : 0f), 0, null)) break;
            }
            // chalkboard on the pavement at the door
            if (doorBays.Count > 0 && rng.NextDouble() < ((float?)ts?["board"] ?? 0f))
            {
                float bx = 1 + 2 * doorBays[0] + (rng.NextDouble() < 0.5 ? -1.1f : 1.1f);
                var a = EnvKit.Place("ENV_AFrame_Board", g, new Vector3(bx, 0, 0.75f), rng.Next(-20, 20));
                // what the board says follows what the business sells (a bakery does not chalk up a "menú del día")
                string bn = (string)ts?["boardNotice"] ?? "menu";
                EnvKit.Remap(a, new Dictionary<string, string> { { "ENV_Sign_Board", TextureMat("ENV_Notice_" + bn, "T_ENV_Notice_" + bn, 0.1f) } });
            }
            // opening-hours vinyl on the shop door glass
            if (doorBays.Count > 0 && (bool?)ts?["lit"] == true && t != "cerrado")
            {
                var v = EnvKit.Place("ENV_Sign_Panel", g, new Vector3(1 + 2 * doorBays[0] + 0.25f, 1.45f, 0.035f), 0, new Vector3(0.3f, 0.15f, 0.2f));
                EnvKit.Remap(v, new Dictionary<string, string> { { "ENV_Sign_Board", TextureMat("ENV_Notice_horario", "T_ENV_Notice_horario", 0.5f) }, { "MI_WoodTrim", "ENV_Paint_White" } });
            }
            // closed: a notice in the window; garage: the municipal "vado" plate
            if (t == "cerrado" && shop.Count > 0)
            {
                var notices = new[] { "se_alquila", "se_vende", "jubilacion", "traspaso" };
                var n = notices[rng.Next(notices.Length)];
                int i = shop[rng.Next(shop.Count)];
                var v = EnvKit.Place("ENV_Sign_Panel", g, new Vector3(1 + 2 * i, 1.45f, 0.03f), 0, new Vector3(0.62f, 0.31f, 0.2f));
                EnvKit.Remap(v, new Dictionary<string, string> { { "ENV_Sign_Board", TextureMat("ENV_Notice_" + n, "T_ENV_Notice_" + n, 0.1f) }, { "MI_WoodTrim", "ENV_Paint_White" } });
            }
            if (t == "garaje")
            {
                int i = Enumerable.Range(0, s.bays).FirstOrDefault(k => rows[0][k] == 'R');
                var v = tryPlace("ENV_Sign_Panel", g, new Vector3(1 + 2 * i + 1.05f, 2.25f, WallFace + 0.016f), 0, new Vector3(0.44f, 0.22f, 1));
                if (v) EnvKit.Remap(v, new Dictionary<string, string> { { "ENV_Sign_Board", TextureMat("ENV_Notice_vado", "T_ENV_Notice_vado", 0.4f) }, { "MI_WoodTrim", "ENV_Metal_Galvanised" } });
            }
            // bars on the street: a barrel as a table and two stools against the front, beside the door
            var terrace = (string)ts?["terrace"];
            if (terrace != null && doorBays.Count > 0)
            {
                float bx = 1 + 2 * doorBays[0] + (rng.NextDouble() < 0.5 ? -1.25f : 1.25f);
                var b = tryPlace(terrace == "cafe" ? "ENV_Cafe_Table" : "ENV_Prop_Barrel", g, new Vector3(bx, 0, 0.62f), rng.Next(360), null);
                if (b)
                    foreach (var dx in new[] { -0.62f, 0.62f })
                        tryPlace(terrace == "cafe" ? "ENV_Cafe_Chair" : "ENV_Prop_Stool", g, new Vector3(bx + dx, 0, 0.7f), rng.Next(360), null);
            }
            // goods at the door
            var goods = (string)ts?["goods"];
            if (goods != null && doorBays.Count > 0)
            {
                float gx = 1 + 2 * doorBays[0] + (rng.NextDouble() < 0.5 ? -1.2f : 1.2f);
                switch (goods)
                {
                    case "fruta":
                        EnvKit.Place("ENV_Prop_FarmCrate_Apple", g, new Vector3(gx, 0, 0.45f), 0);
                        EnvKit.Place("ENV_Prop_FarmCrate_Carrot", g, new Vector3(gx + 0.55f, 0, 0.45f), 0);
                        EnvKit.Place("ENV_Prop_FarmCrate_Apple", g, new Vector3(gx + 0.25f, 0.33f, 0.45f), 8);
                        break;
                    case "ferreteria":
                        EnvKit.Place("ENV_Prop_Bucket", g, new Vector3(gx, 0, 0.4f), 0);
                        EnvKit.Place("ENV_Prop_Bucket_Wood", g, new Vector3(gx + 0.4f, 0, 0.35f), 30);
                        EnvKit.Place("ENV_Prop_Rope_Coil", g, new Vector3(gx - 0.35f, 0, 0.4f), 0);
                        break;
                    case "ultramarinos":
                        EnvKit.Place("ENV_Prop_Barrel_Apples", g, new Vector3(gx, 0, 0.45f), 0);
                        EnvKit.Place("ENV_Prop_Bag", g, new Vector3(gx + 0.5f, 0, 0.4f), 20);
                        break;
                    case "recuerdos":
                        EnvKit.Place("ENV_Prop_Barrel", g, new Vector3(gx, 0, 0.45f), 0);
                        EnvKit.Place("ENV_Prop_Crate_Wooden", g, new Vector3(gx + 0.55f, 0, 0.4f), 12);
                        break;
                }
            }
        }

        const float WallFace = 0.092f;

        static Dictionary<string, string> With(Dictionary<string, string> map, string k, string v)
        {
            var c = new Dictionary<string, string>(map) { [k] = v };
            return c;
        }
    }
}

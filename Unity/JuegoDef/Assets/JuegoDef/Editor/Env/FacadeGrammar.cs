using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>One module placed inside a 2 m bay slot (slot frame: wall centred on x = 0, street side +z).</summary>
    public struct EnvPart
    {
        public string module, role;   // role: wall | joinery | stone | mat:&lt;material&gt;
        public Vector3 offset, scale;
        public float rotY;
        public EnvPart(string module, string role, Vector3 offset = default, float rotY = 0, Vector3? scale = null)
        { this.module = module; this.role = role; this.offset = offset; this.rotY = rotY; this.scale = scale ?? Vector3.one; }
    }

    /// <summary>
    /// The facade vocabulary. Bay codes (one char per 2 m bay):
    /// ground floor — S shop display window, E shop entrance (e = open, walkable), R shop bay closed by roller
    /// shutter, D portal (o = open), A arched portal (O = open), V service door, G timber gate, W window, P plain; upper floors — W window + open shutters,
    /// c closed shutters, w bare window, B timber balcony, I iron balcony (both with a glazed balcony door; the
    /// grammar places at most one per facade), L gallery (glazed mirador), T small round-head window, P plain.
    /// Rows the spec leaves empty are generated per frontage type with vertically aligned bay columns.
    /// </summary>
    public static class FacadeGrammar
    {
        public static readonly string[] Types = { "mixed_commercial", "closed_residential", "lodging", "warehouse", "termination" };
        static readonly string[] PortalDoors = { "Door_1_Flat", "Door_6_Flat", "Door_2_Flat", "Door_5_Flat" }; // not the lattice/heavy-studded kit doors

        static readonly Dictionary<string, string> CleanPlaster = new Dictionary<string, string>
        {
            { "Window_Wide_Flat", "ENV_Wall_Plaster_Clean_Window" },
            { "Window_Thin_Round", "ENV_Wall_Plaster_Clean_Thin" },
            { "Door_Flat", "ENV_Wall_Plaster_Clean_Door" },
            { "Door_Round", "ENV_Wall_Plaster_Clean_DoorRound" },
        };

        public static string DefaultGround(string type) => type == "mixed_commercial" || type == "lodging" ? "plaster" : "stone";

        public static char BackCode(int floor, int bay, System.Random rng) => floor > 0 && bay % 2 == 1 ? 'w' : 'P';

        public static string[] Rows(BuildingSpec s, System.Random rng)
        {
            var rows = new string[s.floors];
            var generated = Generate(s, rng);
            for (int f = 0; f < s.floors; f++)
            {
                string given = s.rows != null && f < s.rows.Length ? (s.rows[f] ?? "").Replace(" ", "") : "";
                rows[f] = given.Length == 0 ? generated[f] : given.PadRight(s.bays, 'P').Substring(0, s.bays);
            }
            return rows;
        }

        /// <summary>Upper-floor opening axes per frontage width, weighted. Calibrated against real Cantabrian and
        /// Galician port fabric (Castro Urdiales harbour front, Combarro): roughly one opening axis per 3-4 m and a
        /// lot of plain wall, never a window in every 2 m bay (owner reviews 2026-09-28: "ojo con tanta ventana",
        /// "dejar respirar un poco").</summary>
        static readonly Dictionary<int, (string axes, int weight)[]> Rhythms = new Dictionary<int, (string, int)[]>
        {
            { 1, new[] { ("W", 1) } },
            { 2, new[] { ("WP", 4), ("PW", 4), ("WW", 1) } },
            { 3, new[] { ("WPW", 3), ("PWP", 3), ("WPP", 1), ("PPW", 1) } },
            { 4, new[] { ("WPPW", 4), ("PWPW", 2), ("WPWP", 2), ("PWWP", 1) } },
            { 5, new[] { ("WPWPW", 2), ("PWPWP", 3), ("WPPPW", 2) } },
            { 6, new[] { ("PWPPWP", 3), ("WPPWPP", 2), ("PPWPWP", 2) } },
        };

        static string Rhythm(int n, System.Random rng)
        {
            if (Rhythms.TryGetValue(n, out var options))
            {
                int total = options.Sum(o => o.weight), pick = rng.Next(total);
                foreach (var o in options)
                {
                    if (pick < o.weight) return o.axes;
                    pick -= o.weight;
                }
            }
            var c = new char[n];
            for (int i = 0; i < n; i++) c[i] = i % 3 == 1 ? 'W' : 'P';
            return new string(c);
        }

        static string[] Generate(BuildingSpec s, System.Random rng)
        {
            int n = s.bays;
            var rows = new char[s.floors][];
            for (int f = 0; f < s.floors; f++) rows[f] = Enumerable.Repeat('P', n).ToArray();
            int portal = (s.seed & 1) == 0 ? 0 : n - 1;
            double balconyChance = 0, galleryChance = 0;
            switch (s.type)
            {
                case "mixed_commercial":
                {
                    for (int i = 0; i < n; i++) rows[0][i] = 'S';
                    rows[0][portal] = 'D';
                    var shop = Enumerable.Range(0, n).Where(i => i != portal).ToList();
                    if (n >= 4 && rng.NextDouble() < 0.6) { rows[0][n - 1 - portal] = 'V'; shop.Remove(n - 1 - portal); }
                    if (shop.Count > 0) rows[0][shop[shop.Count / 2]] = 'E';
                    if (shop.Count >= 3 && rng.NextDouble() < 0.4) rows[0][shop[0] == shop[shop.Count / 2] ? shop[1] : shop[0]] = 'R';
                    balconyChance = 0.7; galleryChance = 0.35;
                    break;
                }
                case "lodging":
                {
                    rows[0][n / 2] = 'A';
                    if (n >= 4) { rows[0][0] = 'W'; rows[0][n - 1] = 'W'; }
                    balconyChance = 1.0;
                    break;
                }
                case "closed_residential":
                case "termination":
                {
                    rows[0][portal] = 'D';
                    if (n >= 3 && rng.NextDouble() < 0.6) rows[0][n / 2] = 'W';
                    if (n >= 3 && rng.NextDouble() < 0.4) rows[0][n - 1 - portal] = 'R';
                    balconyChance = s.type == "termination" ? 0.3 : 0.5; galleryChance = 0.3;
                    break;
                }
                case "warehouse":
                {
                    int g0 = Math.Max(0, n / 2 - 1);
                    rows[0][g0] = 'G';
                    if (n >= 4) rows[0][g0 + 1] = 'G';
                    if (n >= 5) rows[0][0] = 'V';
                    for (int f = 1; f < s.floors; f++)
                        for (int i = 0; i < n; i++) rows[f][i] = i % 2 == 0 ? 'T' : 'P';
                    return rows.Select(r => new string(r)).ToArray();
                }
                default: throw new ArgumentException("ENV_UNKNOWN_FRONTAGE_TYPE " + s.type);
            }

            // Upper floors: one rhythm shared by all floors so openings stack in vertical axes.
            var axes = Rhythm(n, rng);
            var windowCols = Enumerable.Range(0, n).Where(i => axes[i] == 'W').ToList();
            int gallery = s.floors > 1 && windowCols.Count >= 2 && rng.NextDouble() < galleryChance ? windowCols[rng.Next(windowCols.Count)] : -1;
            // At most ONE balcony door (glazed balconera) per facade, on the principal floor, on the most central axis.
            int balcony = -1;
            if (s.floors > 1 && rng.NextDouble() < balconyChance)
                balcony = windowCols.Where(i => i != gallery).OrderBy(i => Math.Abs(i - (n - 1) / 2.0)).DefaultIfEmpty(-1).First();
            char balconyCode = rng.NextDouble() < 0.65 ? 'I' : 'B';
            for (int f = 1; f < s.floors; f++)
                for (int i = 0; i < n; i++)
                {
                    if (axes[i] != 'W') continue;
                    char c;
                    if (i == gallery && f <= 2) c = 'L';
                    else if (i == balcony && f == 1) c = balconyCode;
                    else if (f == s.floors - 1 && s.floors >= 4) c = 'w';
                    else
                    {
                        double r = rng.NextDouble();
                        c = r < 0.7 ? 'W' : r < 0.85 ? 'c' : 'w';
                    }
                    rows[f][i] = c;
                }
            return rows.Select(r => new string(r)).ToArray();
        }

        /// <summary>Modules for one bay slot.</summary>
        public static List<EnvPart> Recipe(BuildingSpec s, string fam, char code, int floor, System.Random rng)
        {
            bool stone = fam == "stone";
            string F = stone ? "UnevenBrick" : "Plaster";
            var parts = new List<EnvPart>();
            // Plaster bays use the derived clean walls (kit half-timbering removed); stone bays use the kit walls.
            void Wall(string variant) => parts.Add(new EnvPart(stone ? $"Wall_UnevenBrick_{variant}" : CleanPlaster[variant], "wall"));
            void Join(string module, Vector3 at = default, float rot = 0) => parts.Add(new EnvPart(module, "joinery", at, rot));
            void Stone(string module, Vector3 at = default) => parts.Add(new EnvPart(module, "stone", at));
            string door = string.IsNullOrEmpty(s.door) ? PortalDoors[Math.Abs(s.seed) % PortalDoors.Length] : s.door;
            // stone bays: the kit "Rocks" window is only a stone surround, the glazed sash is a derived insert
            void WideWindow()
            {
                if (stone) { Stone("Window_Wide_Flat_Rocks"); Join("ENV_Window_Insert_Wide"); }
                else Join("Window_Wide_Flat1");
            }

            switch (code)
            {
                case 'P':
                    parts.Add(new EnvPart(stone ? "Wall_UnevenBrick_Straight" : floor == 0 ? "ENV_Wall_Plaster_Clean_Base" : "ENV_Wall_Plaster_Clean", "wall"));
                    break;
                case 'W':
                    Wall("Window_Wide_Flat");
                    WideWindow();
                    if (floor > 0) Join("WindowShutters_Wide_Flat_Open");
                    break;
                case 'w':
                    Wall("Window_Wide_Flat");
                    WideWindow();
                    break;
                case 'c':
                    Wall("Window_Wide_Flat");
                    WideWindow();
                    Join("WindowShutters_Wide_Flat_Closed");
                    break;
                case 'T':
                    Wall("Window_Thin_Round");
                    if (stone) { Stone("Window_Thin_Round_Rocks"); Join("ENV_Window_Insert_Thin"); }
                    else Join("Window_Thin_Round1");
                    break;
                case 'D':
                    Wall("Door_Flat");
                    Stone("DoorFrame_Flat_Brick");
                    Join(door, new Vector3(0.5f, 0, 0));
                    break;
                case 'A':
                    Wall("Door_Round");
                    Stone("DoorFrame_Round_Brick");
                    Join(door.Replace("_Flat", "_Round"), new Vector3(0.5f, 0, 0));
                    break;
                case 'V':
                    Wall("Door_Flat");
                    Join("ENV_Door_Service");
                    break;
                case 'S':
                    parts.Add(new EnvPart($"ENV_Wall_{F}_Shopfront", "wall"));
                    parts.Add(new EnvPart("ENV_Shopfront_Frame", "shop"));
                    break;
                case 'E':
                    parts.Add(new EnvPart($"ENV_Wall_{F}_Shopfront", "wall"));
                    parts.Add(new EnvPart("ENV_Shopfront_Door", "shop"));
                    break;
                case 'e':
                    parts.Add(new EnvPart($"ENV_Wall_{F}_Shopfront", "wall"));
                    parts.Add(new EnvPart("ENV_Shopfront_Door_Open", "shop"));
                    break;
                case 'O':
                    Wall("Door_Round");
                    Stone("DoorFrame_Round_Brick");
                    Join(door.Replace("_Flat", "_Round"), new Vector3(0.5f, 0, 0), -80);
                    break;
                case 'o':
                    Wall("Door_Flat");
                    Stone("DoorFrame_Flat_Brick");
                    Join(door, new Vector3(0.5f, 0, 0), -80);
                    break;
                case 'R':
                    parts.Add(new EnvPart($"ENV_Wall_{F}_Shopfront", "wall"));
                    parts.Add(new EnvPart("ENV_Shutter_Roller", "stone"));
                    break;
                case 'G':
                    parts.Add(new EnvPart($"ENV_Wall_{F}_Shopfront", "wall"));
                    Join("ENV_Gate_Timber");
                    break;
                case 'B':
                    Wall("Door_Flat");
                    Join("DoorFrame_Flat_WoodDark");
                    Join("ENV_Door_Balcony");
                    Join("Balcony_Simple_Straight");
                    Join("Floor_WoodDark_Half3", new Vector3(0, 0, 1f));
                    break;
                case 'I':
                    Wall("Door_Flat");
                    Join("DoorFrame_Flat_WoodDark");
                    Join("ENV_Door_Balcony");
                    Stone("ENV_Balcony_Iron");
                    break;
                case 'L':
                    parts.Add(new EnvPart($"ENV_Wall_{F}_Shopfront", "wall"));
                    Join("ENV_Gallery_Bay");
                    break;
                default:
                    throw new ArgumentException($"ENV_UNKNOWN_BAY_CODE '{code}' in {s.id}");
            }
            return parts;
        }

        /// <summary>Street dressing that belongs to the building: shop fascias/awnings, lodging sign, wall lamps,
        /// rain-water pipes at the party lines. Structure first, dressing after (CITY layered assembly rule).</summary>
        public static void Dress(BuildingSpec s, Transform root, string[] rows, System.Random rng, Dictionary<string, string> joinMap)
        {
            var dress = EnvKit.Group(root, "Dressing");
            float top = s.floors * BuildingAssembler.Storey;
            int width = s.bays * 2;
            for (int i = 0; i < s.bays; i++)
            {
                char g = rows[0][i];
                var x = 1 + 2 * i;
                if (g == 'S' || g == 'R' || g == 'E' || g == 'e')
                {
                    var fascia = EnvKit.Place("ENV_Shop_Fascia", dress, new Vector3(x, 0, 0), 0);
                    EnvKit.Remap(fascia, joinMap);
                    if (!string.IsNullOrEmpty(s.awning) && (g == 'S' || g == 'E' || g == 'e'))
                        EnvKit.Remap(EnvKit.Place("ENV_Awning", dress, new Vector3(x, 0, 0), 0), new Dictionary<string, string> { { "ENV_Canvas_Green", s.awning } });
                }
                if ((g == 'A' || g == 'D' || g == 'O' || g == 'o') && (s.type == "lodging" || s.sign == "bracket"))
                    EnvKit.Remap(EnvKit.Place("ENV_Sign_Bracket", dress, new Vector3(x - 1f, 0, 0), 0), joinMap);
            }
            // street lighting: wall lanterns on roughly one building in three, not on every facade
            if (s.type != "warehouse" && s.bays >= 3 && (s.type == "lodging" || rng.NextDouble() < 0.35))
                EnvKit.Place("ENV_Prop_Lantern_Wall", dress, new Vector3(rng.NextDouble() < 0.5 ? 2f : width - 2f, 3.3f, 0.1f), 0, new Vector3(0.75f, 0.75f, 0.75f));
            // rain-water downpipes on the street face at both party lines
            // just inside the corner quoins (which project ~0.5 m along the facade)
            EnvKit.Place("ENV_Downpipe", dress, new Vector3(0.6f, 0, 0.16f), 0, new Vector3(1, top / 3f, 1));
            if (s.bays >= 3) EnvKit.Place("ENV_Downpipe", dress, new Vector3(width - 0.6f, 0, 0.16f), 0, new Vector3(1, top / 3f, 1));
        }
    }
}

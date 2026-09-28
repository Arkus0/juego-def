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
    /// c closed shutters, w bare window, X boarded-up window, B timber balcony, I iron balcony (both with a glazed
    /// balcony door; the grammar places at most one per facade), L gallery (glazed mirador), T small round-head
    /// window, P plain. Era (old / reformed / neglected) swaps shutters for roller blinds, portal doors, joinery
    /// colours and render; History adds the later additions.
    /// Rows the spec leaves empty are generated per frontage type with vertically aligned bay columns.
    /// </summary>
    public static class FacadeGrammar
    {
        public static readonly string[] Types = { "mixed_commercial", "closed_residential", "lodging", "warehouse", "termination", "landmark" };
        static readonly string[] PortalDoors = { "Door_1_Flat", "Door_6_Flat", "Door_2_Flat", "Door_5_Flat" }; // not the lattice/heavy-studded kit doors

        static readonly Dictionary<string, string> CleanPlaster = new Dictionary<string, string>
        {
            { "Window_Wide_Flat", "ENV_Wall_Plaster_Clean_Window" },
            { "Window_Thin_Round", "ENV_Wall_Plaster_Clean_Thin" },
            { "Door_Flat", "ENV_Wall_Plaster_Clean_Door" },
            { "Door_Round", "ENV_Wall_Plaster_Clean_DoorRound" },
        };

        public static string DefaultGround(string type) => type == "mixed_commercial" || type == "lodging" ? "plaster" : "stone";

        static readonly string[] Repaints = { "ENV_Plaster_Ochre", "ENV_Plaster_Sage", "ENV_Plaster_OffWhite", "ENV_Plaster_BlueGrey", "ENV_Plaster_Rose" };

        /// <summary>Accumulated history of a building: old (original joinery, shutters, galleries), reformed (1970s-90s:
        /// bronze/silver aluminium, roller blinds, new portal, fresh render) or neglected (stained render, closed or boarded
        /// windows, closed shops, vines). Seeded unless the spec fixes it.</summary>
        public static string ResolveEra(BuildingSpec s, System.Random rng)
        {
            if (!string.IsNullOrEmpty(s.era)) return s.era;
            if (s.type == "landmark" || s.type == "warehouse") return "old";
            double r = rng.NextDouble();
            return r < 0.5 ? "old" : r < 0.8 ? "reformed" : "neglected";
        }

        public static string[] ApplyEra(BuildingSpec s, string[] rows, System.Random rng)
        {
            var o = rows.Select(r => r.ToCharArray()).ToArray();
            for (int f = 0; f < o.Length; f++)
                for (int i = 0; i < o[f].Length; i++)
                {
                    char c = o[f][i];
                    if (s.era == "reformed" && c == 'B') o[f][i] = 'I';
                    if (s.era == "neglected")
                    {
                        if (f > 0 && c == 'W') o[f][i] = rng.NextDouble() < 0.2 ? 'X' : (rng.NextDouble() < 0.65 ? 'c' : 'W');
                        if (f == 0 && string.IsNullOrEmpty(s.interior) && (c == 'S' || c == 'E') && rng.NextDouble() < 0.5) o[f][i] = 'R';
                    }
                }
            return o.Select(r => new string(r)).ToArray();
        }

        public static void EraMaterials(BuildingSpec s, Dictionary<string, string> wallMap, Dictionary<string, string> joinMap, System.Random rng)
        {
            if (s.era == "reformed")
            {
                if (rng.NextDouble() < 0.6) wallMap["MI_Plaster"] = "ENV_Plaster_Reformed";
                var alu = rng.NextDouble() < 0.55 ? "ENV_Joinery_Bronze" : "ENV_Joinery_Silver";
                joinMap["MI_WoodTrim"] = alu;
                joinMap["MI_WoodTrim_Wear"] = alu;
            }
            else if (s.era == "neglected")
            {
                wallMap["MI_Plaster"] = rng.NextDouble() < 0.7 ? "ENV_Plaster_Stained" : "ENV_Plaster_Weathered";
                wallMap["MI_WoodTrim"] = "ENV_Trim_Dark";
                wallMap["MI_WoodTrim_Wear"] = "ENV_Trim_Dark";
            }
        }

        /// <summary>Plinth pieces (x, width) for a ground-floor bay: full run on solid/window bays, stubs on the piers
        /// beside door (kit opening ±0.65 m) and shop/gate (±0.8 m) openings.</summary>
        public static IEnumerable<(float x, float w)> PlinthRuns(char code)
        {
            switch (code)
            {
                case 'P': case 'W': case 'w': case 'c': case 'T': case 'X':
                    yield return (0f, 2f); break;
                case 'D': case 'o': case 'A': case 'O': case 'V':
                    yield return (-0.825f, 0.35f); yield return (0.825f, 0.35f); break;
                case 'S': case 'E': case 'e': case 'R': case 'G':
                    yield return (-0.9f, 0.2f); yield return (0.9f, 0.2f); break;
            }
        }

        /// <summary>The 10–20 % of "this should not be here, but it has been for forty years": later additions and
        /// odd replacements drawn per building (deterministic by seed).</summary>
        public class History
        {
            public (int f, int i) oddWindow = (-1, -1);
            public string groundRepaint;
            public int dishFloor = -1, dishBay;
            public bool aerial, cable, pots, vines;
            public int meterBay = -1, clothesFloor = -1, clothesBay;
            public float extraPipeX = -1;
            public static readonly History None = new History();

            public static History Draw(BuildingSpec s, string[] rows, System.Random rng)
            {
                var h = new History();
                if (s.type == "landmark") return h;
                bool home = s.type == "closed_residential" || s.type == "termination";
                var windows = new List<(int, int)>();
                for (int f = 1; f < rows.Length; f++)
                    for (int i = 0; i < rows[f].Length; i++)
                        if ("Wwc".IndexOf(rows[f][i]) >= 0) windows.Add((f, i));
                if (windows.Count > 0 && s.era != "reformed" && rng.NextDouble() < 0.18) h.oddWindow = windows[rng.Next(windows.Count)];
                if (s.type != "warehouse" && (string.IsNullOrEmpty(s.ground) ? DefaultGround(s.type) : s.ground) == "plaster" && rng.NextDouble() < 0.2)
                    h.groundRepaint = Repaints[rng.Next(Repaints.Length)];
                if (s.floors > 1 && rng.NextDouble() < 0.25) { h.dishFloor = s.floors - 1; h.dishBay = rng.Next(s.bays); }
                h.aerial = s.roof == "eaves" && rng.NextDouble() < 0.35;
                var solid = Enumerable.Range(0, s.bays).Where(i => rows[0][i] == 'P').ToList();
                if (solid.Count > 0 && rng.NextDouble() < 0.15) h.meterBay = solid[rng.Next(solid.Count)];  // meters: occasional, not on every house
                h.cable = s.type != "warehouse" && rng.NextDouble() < 0.3;
                if (windows.Count > 0 && rng.NextDouble() < (home ? 0.4 : s.type == "mixed_commercial" ? 0.15 : 0.0))
                {
                    var w = windows[rng.Next(windows.Count)];
                    h.clothesFloor = w.Item1; h.clothesBay = w.Item2;
                }
                h.pots = rng.NextDouble() < 0.45;
                h.vines = rng.NextDouble() < (s.era == "neglected" ? 0.6 : s.era == "old" ? 0.15 : 0.0);
                if (s.bays >= 3 && rng.NextDouble() < 0.2) h.extraPipeX = 2 * (1 + rng.Next(s.bays - 1));
                return h;
            }
        }

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
            int portal = Portal(s.type, n, rng);
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
                    var others = Enumerable.Range(0, n).Where(i => i != portal).ToList();
                    if (others.Count >= 2 && rng.NextDouble() < 0.6) rows[0][others[rng.Next(others.Count)]] = 'W';
                    if (n >= 3 && rng.NextDouble() < 0.4)
                    {
                        var far = others.Where(i => rows[0][i] == 'P').OrderByDescending(i => Math.Abs(i - portal)).ToList();
                        if (far.Count > 0) rows[0][far[0]] = 'R';
                    }
                    balconyChance = s.type == "termination" ? 0.3 : 0.5; galleryChance = 0.3;
                    break;
                }
                case "landmark":
                {
                    // stone tower (belfry / singular building) closing a view: solid shaft, small openings, open belfry
                    rows[0][0] = 'A';
                    for (int f = 1; f < s.floors; f++)
                        for (int i = 0; i < n; i++) rows[f][i] = f == s.floors - 1 ? 'T' : ((f + i) % 2 == 0 ? 'T' : 'P');
                    return rows.Select(r => new string(r)).ToArray();
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

            // Upper floors: the principal floor takes a weighted rhythm; each floor above keeps the axes of the one
            // below (stacked), thins them out (two windows below, one above) or moves one, as vernacular fabric does.
            // Owner review 2026-09-28: "dos ventanas en una planta y una en la superior".
            var floorAxes = new string[s.floors];
            if (s.floors > 1) floorAxes[1] = Rhythm(n, rng);
            for (int f = 2; f < s.floors; f++) floorAxes[f] = NextFloorAxes(floorAxes[f - 1], rng);
            var axes = s.floors > 1 ? floorAxes[1] : new string('P', n);
            var windowCols = Enumerable.Range(0, n).Where(i => axes[i] == 'W').ToList();
            int gallery = s.floors > 1 && windowCols.Count >= 2 && rng.NextDouble() < galleryChance ? windowCols[rng.Next(windowCols.Count)] : -1;
            // At most ONE balcony door (glazed balconera) per facade, on the principal floor, on the most central axis.
            int balcony = -1;
            if (s.floors > 1 && rng.NextDouble() < balconyChance)
                balcony = windowCols.Where(i => i != gallery).OrderBy(i => Math.Abs(i - (n - 1) / 2.0)).DefaultIfEmpty(-1).First();
            char balconyCode = rng.NextDouble() < 0.65 ? 'I' : 'B';
            // Solana: the top floor opens onto the gallery through ONE door; it is the facade's only balcony door
            if (s.solana && s.floors > 1)
            {
                balcony = -1;
                if (s.floors - 1 <= 2) gallery = -1;
            }
            for (int f = 1; f < s.floors; f++)
                for (int i = 0; i < n; i++)
                {
                    if (s.solana && f == s.floors - 1) continue;
                    bool galleryHere = i == gallery && f <= 2 && (f == 1 || floorAxes[f][i] == 'W');
                    if (floorAxes[f][i] != 'W' && !galleryHere) continue;
                    char c;
                    if (galleryHere) c = 'L';
                    else if (i == balcony && f == 1) c = balconyCode;
                    else if (f == s.floors - 1 && s.floors >= 3 && s.type != "mixed_commercial" && rng.NextDouble() < 0.25) c = 'T';  // attic
                    else if (f == s.floors - 1 && s.floors >= 4) c = 'w';
                    else
                    {
                        double r = rng.NextDouble();
                        c = r < 0.7 ? 'W' : r < 0.85 ? 'c' : 'w';
                    }
                    rows[f][i] = c;
                }
            if (s.solana && s.floors > 1)
            {
                int top = s.floors - 1;
                var ax = floorAxes[top];
                var cols = Enumerable.Range(0, n).Where(i => ax[i] == 'W').ToList();
                int door = cols.Count > 0 ? cols.OrderBy(i => Math.Abs(i - (n - 1) / 2.0)).First() : n / 2;
                for (int i = 0; i < n; i++) rows[top][i] = i == door ? 'N' : (ax[i] == 'W' ? 'w' : 'P');
            }
            return rows.Select(r => new string(r)).ToArray();
        }

        /// <summary>Portal (street door) bay: either end or an inner bay, drawn per building so doors along a street do
        /// not all fall on the same side (owner review 2026-09-28).</summary>
        static int Portal(string type, int n, System.Random rng)
        {
            if (n <= 2) return rng.NextDouble() < 0.5 ? 0 : n - 1;
            var options = new List<(int bay, int w)> { (0, 3), (n - 1, 3) };
            for (int i = 1; i < n - 1; i++)
                options.Add((i, type == "mixed_commercial" ? 1 : (n % 2 == 1 && i == n / 2 ? 3 : 2)));
            int pick = rng.Next(options.Sum(o => o.w));
            foreach (var o in options)
            {
                if (pick < o.w) return o.bay;
                pick -= o.w;
            }
            return 0;
        }

        /// <summary>Axes of the floor above: 55 % stacked, 30 % one fewer (the survivor moves to the centre when a
        /// pair thins to one on an odd frontage), 15 % one axis moved to a free neighbouring bay.</summary>
        static string NextFloorAxes(string below, System.Random rng)
        {
            var a = below.ToCharArray();
            int n = a.Length;
            var cols = Enumerable.Range(0, n).Where(i => a[i] == 'W').ToList();
            double r = rng.NextDouble();
            if (r < 0.55 || cols.Count == 0) return below;
            if (r < 0.85)
            {
                if (cols.Count < 2) return below;
                if (cols.Count == 2 && n % 2 == 1)
                {
                    var single = new string('P', n).ToCharArray();
                    single[n / 2] = 'W';
                    return new string(single);
                }
                a[rng.NextDouble() < 0.5 ? cols.First() : cols.Last()] = 'P';  // drop an outer axis
                return new string(a);
            }
            bool Free(int i) => i >= 0 && i < n && a[i] == 'P' && (i == 0 || a[i - 1] != 'W') && (i == n - 1 || a[i + 1] != 'W');
            foreach (var c in cols.OrderBy(_ => rng.Next()).ToList())
                foreach (var d in rng.NextDouble() < 0.5 ? new[] { -1, 1 } : new[] { 1, -1 })
                {
                    a[c] = 'P';
                    if (Free(c + d)) { a[c + d] = 'W'; return new string(a); }
                    a[c] = 'W';
                }
            return below;
        }

        /// <summary>Open shutters fold 0.24 m past their 2 m bay: an open-shuttered window needs free wall on both
        /// sides. At a building edge (quoins, neighbour) or beside another window, balcony or gallery it keeps its
        /// shutters closed or has none. Reformed facades use roller blinds and are left alone.</summary>
        public static string[] ResolveShutters(BuildingSpec s, string[] rows, System.Random rng)
        {
            if (rows == null || s.era == "reformed") return rows;
            var o = rows.Select(r => (r ?? "").ToCharArray()).ToArray();
            for (int f = 1; f < o.Length; f++)
                for (int i = 0; i < o[f].Length; i++)
                {
                    if (o[f][i] != 'W') continue;
                    int n = o[f].Length;
                    bool edge = i == 0 || i == n - 1;
                    bool crowded = (i > 0 && "WBILN".IndexOf(o[f][i - 1]) >= 0) || (i < n - 1 && "WBILN".IndexOf(o[f][i + 1]) >= 0);
                    // ashlar-framed windows carry interior shutters: no exterior leaves over the stone
                    if (edge || crowded || s.surrounds) o[f][i] = s.surrounds ? 'w' : rng.NextDouble() < 0.4 ? 'c' : 'w';
                }
            return o.Select(r => new string(r)).ToArray();
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
                else if (s.surrounds) parts.Add(new EnvPart("ENV_Window_Wide_Ashlar", "stone"));  // casco: sandstone surround + sash
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
                    if (floor > 0) { if (s.era == "reformed") Stone("ENV_Window_Blind"); else Join("WindowShutters_Wide_Flat_Open"); }
                    break;
                case 'X':
                    Wall("Window_Wide_Flat");
                    WideWindow();
                    Stone("ENV_Window_Boarded");
                    break;
                case 'w':
                    Wall("Window_Wide_Flat");
                    WideWindow();
                    break;
                case 'c':
                    Wall("Window_Wide_Flat");
                    WideWindow();
                    if (s.era == "reformed") Stone("ENV_Window_Blind"); else Join("WindowShutters_Wide_Flat_Closed");
                    break;
                case 'T':
                    Wall("Window_Thin_Round");
                    if (stone) { Stone("Window_Thin_Round_Rocks"); Join("ENV_Window_Insert_Thin"); }
                    else Join("Window_Thin_Round1");
                    break;
                case 'D':
                    Wall("Door_Flat");
                    Stone("DoorFrame_Flat_Brick");
                    if (s.era == "reformed") parts.Add(new EnvPart("ENV_Door_Portal_Reformed", "stone"));
                    else Join(door, new Vector3(0.5f, 0, 0));
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
                case 'N':
                    // door onto the solana (the gallery itself is placed by the assembler across the top floor)
                    Wall("Door_Flat");
                    Join("DoorFrame_Flat_WoodDark");
                    Join("ENV_Door_Balcony");
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

        /// <summary>Street dressing that belongs to the building: shop fascias/awnings, lodging sign, then the services
        /// — rain-water pipes, wall lantern — and the building's history (dish, aerial, meters, service cable,
        /// clothesline, doorstep pots, vines, an awkward extra downpipe). Every service is tested against the facade's
        /// real geometry (EnvClearance) and only goes where a real one would fit: never across a window, door,
        /// shutter, balcony, fascia or sign (owner review 2026-09-28).</summary>
        public static void Dress(BuildingSpec s, Transform root, string[] rows, System.Random rng, Dictionary<string, string> joinMap, History h)
        {
            var dress = EnvKit.Group(root, "Dressing");
            float top = s.floors * BuildingAssembler.Storey;
            int width = s.bays * 2;
            var doors = new List<float>();
            for (int i = 0; i < s.bays; i++)
            {
                if (s.cornerEntrance && i == (s.cornerSide == "left" ? 0 : s.bays - 1)) continue;  // the chamfer carries its own fascia
                char g = rows[0][i];
                var x = 1 + 2 * i;
                if (g == 'S' || g == 'R' || g == 'E' || g == 'e')
                {
                    // edge bays stop the fascia/awning 0.36 m short of the party line: the quoin pilaster (0.22 m on
                    // our side) and the downpipe beside it
                    float inset = i == 0 ? 0.155f : i == s.bays - 1 ? -0.155f : 0f;
                    var k = inset != 0 ? new Vector3(0.837f, 1, 1) : Vector3.one;
                    var fascia = EnvKit.Place("ENV_Shop_Fascia", dress, new Vector3(x + inset, 0, 0), 0, k);
                    EnvKit.Remap(fascia, joinMap);
                    if (!string.IsNullOrEmpty(s.awning) && (g == 'S' || g == 'E' || g == 'e'))
                        EnvKit.Remap(EnvKit.Place("ENV_Awning", dress, new Vector3(x + inset, 0, 0), 0, k), new Dictionary<string, string> { { "ENV_Canvas_Green", s.awning } });
                }
                if ((g == 'A' || g == 'D' || g == 'O' || g == 'o') && (s.type == "lodging" || s.sign == "bracket"))
                    EnvKit.Remap(EnvKit.Place("ENV_Sign_Bracket", dress, new Vector3(x - 1f, 0, 0), 0), joinMap);
                if (g == 'A' || g == 'D' || g == 'O' || g == 'o') doors.Add(x);
            }

            var field = EnvClearance.Field.Of(root, new[] { root });
            var ghosts = GhostQuoins(s, root, field);
            var hist = EnvKit.Group(root, "History");
            var pipes = new List<float>();

            GameObject Pipe(Transform parent, IEnumerable<float> xs, float height)
            {
                foreach (var x in xs)
                {
                    if (x < 0.05f || x > width - 0.05f || pipes.Any(p => Mathf.Abs(p - x) < 1f)) continue;
                    foreach (var zc in new[] { 0.16f, 0.21f, 0.26f, 0.31f })
                    {
                        var (core, sweep) = EnvClearance.PipeBoxes(x, zc, 0.45f, height - 0.05f);
                        if (field.Hit(sweep, it => !EnvClearance.IsStandOff(it.module)) != null) break;  // an opening/joinery in the column
                        if (field.Hit(core) != null) continue;                                          // quoin: longer brackets
                        var go = EnvKit.Place(EnvClearance.Pipe, parent, new Vector3(x, 0, zc), 0, new Vector3(1, height / 3f, 1));
                        field.Add(go);
                        EnvKit.Place("ENV_Downpipe_Head", parent, new Vector3(x, height, zc), 0);
                        EnvKit.Place("ENV_Downpipe_Shoe", parent, new Vector3(x, 0, zc), 0);
                        pipes.Add(x);
                        return go;
                    }
                }
                return null;
            }

            GameObject TryPlace(string module, Transform parent, Vector3 pos, float rot, Vector3? scale = null, Func<EnvClearance.Item, bool> consider = null)
            {
                var go = EnvKit.Place(module, parent, pos, rot, scale);
                var b = EnvClearance.BoundsIn(root, go);
                b.Expand(-0.02f);
                if (field.Hit(b, it => !it.module.StartsWith("ENV_Plinth") && (consider == null || consider(it))) != null)
                {
                    UnityEngine.Object.DestroyImmediate(go);
                    return null;
                }
                field.Add(go);
                return go;
            }

            // rain-water downpipes: one per party line (the right one only where no neighbour brings its own), beside
            // the quoin pilaster if free, else at the nearest free bay joint
            // Lebaniego deep eaves drip onto the street, so most casco houses have none (owner: "demasiadas bajantes,
            // se leen como un bosque de postes")
            if (s.type != "landmark" && !s.solana && (s.eave != "canecillos" || rng.NextDouble() < 0.25))
            {
                var inner = Enumerable.Range(1, Math.Max(0, s.bays - 1)).Select(k => 2f * k).ToList();
                Pipe(dress, new[] { 0.29f, 0.56f }.Concat(inner.Where(x => x <= width / 2f)), top);
                if (s.bays >= 3 && s.partyRight == 0)
                    Pipe(dress, new[] { width - 0.29f, width - 0.56f }.Concat(inner.Where(x => x > width / 2f).OrderByDescending(x => x)), top);
            }
            // street lighting: wall lanterns on roughly one building in three, not on every facade
            if (s.type != "warehouse" && s.type != "landmark" && s.bays >= 3 && s.era != "neglected" && (s.type == "lodging" || rng.NextDouble() < 0.35))
            {
                var xs = new List<float> { 2f, width - 2f };
                if (rng.NextDouble() < 0.5) xs.Reverse();
                foreach (var x in xs.Concat(Enumerable.Range(2, Math.Max(0, s.bays - 3)).Select(k => 2f * k)))
                    if (TryPlace("ENV_Prop_Lantern_Wall", dress, new Vector3(x, 3.3f, 0.1f), 0, new Vector3(0.75f, 0.75f, 0.75f))) break;
            }
            // doorstep pots: kept clear of pipes and meters, may stand in front of the door jambs
            if (h.pots)
                foreach (var x in doors)
                    foreach (var sx in new[] { -0.95f, 0.95f })
                        if (TryPlace("ENV_Planter_Pot", dress, new Vector3(x + sx, 0, 0.38f), 0, new Vector3(0.8f, 0.8f, 0.8f), it => EnvClearance.IsService(it.module) || it.module == "ENV_Utility_Box" || it.module.StartsWith("Corner_")))
                            field.Add(EnvKit.Place("ENV_Plant_Small", dress, new Vector3(x + sx, 0.34f, 0.38f), rng.Next(360), new Vector3(0.6f, 0.6f, 0.6f)));

            if (h.dishFloor > 0)
                foreach (var b in new[] { h.dishBay }.Concat(Enumerable.Range(0, s.bays).Where(i => i != h.dishBay)))
                    if (TryPlace("ENV_Sat_Dish", hist, new Vector3(1 + 2 * b + 0.65f, h.dishFloor * BuildingAssembler.Storey + 1.9f, 0), 0)) break;
            if (h.aerial)
                EnvKit.Place("ENV_TV_Aerial", hist, new Vector3(width * 0.3f, top + 1.7f, -s.depth / 2f), rng.Next(360));
            if (h.meterBay >= 0)
                TryPlace("ENV_Utility_Box", hist, new Vector3(1 + 2 * h.meterBay + 0.45f, 0, 0), 0);
            if (h.cable)
            {
                // service cable stapled under the first-floor line: the longest free run of at least two bays
                // (it passes behind downpipes; stops at quoins, balconies, galleries and signs)
                const float y = 2.97f;
                var free = Enumerable.Range(0, s.bays).Select(i =>
                    field.Hit(EnvClearance.Box(2 * i + 0.01f, 2 * i + 1.99f, y - 0.035f, y + 0.005f, 0.1f, 0.13f), it => it.module != EnvClearance.Pipe) == null).ToArray();
                int best = -1, bestLen = 0;
                for (int i = 0; i < s.bays;)
                {
                    if (!free[i]) { i++; continue; }
                    int j = i;
                    while (j < s.bays && free[j]) j++;
                    if (j - i > bestLen) { bestLen = j - i; best = i; }
                    i = j;
                }
                if (bestLen >= 2)
                    for (int i = best; i < best + bestLen; i++)
                        field.Add(EnvKit.Place(EnvClearance.Cable, hist, new Vector3(1 + 2 * i, y, 0), 0));
            }
            if (h.clothesFloor > 0)
                TryPlace("ENV_Clothesline", hist, new Vector3(1 + 2 * h.clothesBay, h.clothesFloor * BuildingAssembler.Storey + 0.88f, 0), 0);
            if (h.extraPipeX > 0)
                Pipe(hist, Enumerable.Range(1, Math.Max(0, s.bays - 1)).Select(k => 2f * k).OrderBy(x => Mathf.Abs(x - h.extraPipeX)),
                     Mathf.Max(1, s.floors - 1) * BuildingAssembler.Storey);
            if (h.vines)
            {
                var solid = Enumerable.Range(0, s.bays).Where(i => rows[0][i] == 'P' || (rows.Length > 1 && rows[1][i] == 'P')).ToList();
                foreach (var b in solid.OrderBy(_ => rng.Next()).ToList())
                    if (TryPlace("Prop_Vine" + (1 + rng.Next(3)), hist, new Vector3(1 + 2 * b, 2.9f + (rows.Length > 1 && rows[1][b] == 'P' ? 3f : 0f), 0.12f), 0,
                                 consider: it => EnvClearance.IsService(it.module) || it.go.transform.parent == dress || it.go.transform.parent == hist)) break;
            }
            for (int i = 0; i < s.bays && s.floors > 1; i++)
                if ((rows[1][i] == 'I' || rows[1][i] == 'B') && h.pots)
                    foreach (var sx in new[] { -0.55f, 0.55f })
                    {
                        EnvKit.Place("ENV_Planter_Pot", hist, new Vector3(1 + 2 * i + sx, BuildingAssembler.Storey, 0.42f), 0, new Vector3(0.6f, 0.6f, 0.6f));
                        EnvKit.Place("ENV_Plant_Bush_Flowers", hist, new Vector3(1 + 2 * i + sx, BuildingAssembler.Storey + 0.26f, 0.42f), rng.Next(360), new Vector3(0.3f, 0.3f, 0.3f));
                    }
            foreach (var g in ghosts) UnityEngine.Object.DestroyImmediate(g);
        }

        /// <summary>Temporary copies of the neighbour's quoin column on a shared edge the neighbour owns (the street
        /// assembler turns ours off there), so services on our side of the party line clear it too.</summary>
        static List<GameObject> GhostQuoins(BuildingSpec s, Transform root, EnvClearance.Field field)
        {
            // shared party lines carry no pilaster on either side any more (ashlar quoins only on seen corners), so
            // there is nothing of the neighbour's to keep services clear of
            return new List<GameObject> { EnvKit.Group(root, "_GhostQuoins").gameObject };
        }
    }
}

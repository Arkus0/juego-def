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
                        if (f == 0 && string.IsNullOrEmpty(s.interior) && string.IsNullOrEmpty(s.business) && (c == 'S' || c == 'E') && rng.NextDouble() < 0.5) o[f][i] = 'R';
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
                h.cable = s.type != "warehouse" && rng.NextDouble() < 0.3 + 0.35 * s.hero;
                if (windows.Count > 0 && rng.NextDouble() < (home ? 0.4 + 0.35 * s.hero : s.type == "mixed_commercial" ? 0.15 + 0.2 * s.hero : 0.0))
                {
                    var w = windows[rng.Next(windows.Count)];
                    h.clothesFloor = w.Item1; h.clothesBay = w.Item2;
                }
                h.pots = rng.NextDouble() < 0.45 + 0.4 * s.hero;
                h.vines = rng.NextDouble() < (s.era == "neglected" ? 0.6 : s.era == "old" ? 0.15 + 0.35 * s.hero : 0.1 * s.hero);
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
            // owner audit 2026-09-29 ("otra vez locos con tantas puertas y ventanas"): sparser again — about one
            // opening axis per 4-6 m of front, walls read as walls
            { 1, new[] { ("W", 1) } },
            { 2, new[] { ("WP", 4), ("PW", 4) } },
            { 3, new[] { ("PWP", 5), ("WPW", 1), ("WPP", 2), ("PPW", 2) } },
            { 4, new[] { ("WPPW", 3), ("PWPP", 2), ("PPWP", 2), ("PWPW", 1) } },
            { 5, new[] { ("PWPWP", 3), ("PPWPP", 2), ("WPPPW", 2) } },
            { 6, new[] { ("PWPPWP", 3), ("PPWPPP", 1), ("PPPWPP", 1), ("WPPPPW", 1) } },
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
                    // the house portal, one shop (door + at most two display windows beside it), maybe a service door;
                    // the rest of the ground floor is wall (owner: "otra vez locos con tantas puertas y ventanas")
                    rows[0][portal] = 'D';
                    var shop = Enumerable.Range(0, n).Where(i => i != portal).ToList();
                    if (n >= 5 && rng.NextDouble() < 0.4) { rows[0][n - 1 - portal] = 'V'; shop.Remove(n - 1 - portal); }
                    if (shop.Count > 0)
                    {
                        int door = shop[shop.Count / 2];
                        rows[0][door] = 'E';
                        foreach (var i in shop.Where(i => i != door).OrderBy(i => Math.Abs(i - door)).Take(rng.NextDouble() < 0.5 ? 1 : 2))
                            rows[0][i] = 'S';
                    }
                    balconyChance = 0.45; galleryChance = 0.18;
                    break;
                }
                case "lodging":
                {
                    rows[0][n / 2] = 'A';
                    if (n >= 4) rows[0][rng.NextDouble() < 0.5 ? 0 : n - 1] = 'W';
                    balconyChance = 1.0;
                    break;
                }
                case "closed_residential":
                case "termination":
                {
                    rows[0][portal] = 'D';
                    // near-solid ground floors: the portal and at most ONE more opening — a small window or a garage
                    var others = Enumerable.Range(0, n).Where(i => i != portal).ToList();
                    double extra = rng.NextDouble();
                    if (others.Count >= 2 && extra < 0.35) rows[0][others[rng.Next(others.Count)]] = 'W';
                    else if (n >= 3 && extra < 0.55)
                    {
                        var far = others.OrderByDescending(i => Math.Abs(i - portal)).ToList();
                        rows[0][far[0]] = 'R';
                    }
                    balconyChance = s.type == "termination" ? 0.2 : 0.32; galleryChance = 0.15;
                    break;
                }
                case "landmark":
                {
                    // stone tower (belfry / singular building) closing a view: solid shaft, small openings, open belfry
                    rows[0][0] = 'A';
                    for (int f = 1; f < s.floors; f++)
                        for (int i = 0; i < n; i++) rows[f][i] = f == s.floors - 1 ? 'T' : f == s.floors - 2 ? 'P' : ((f + i) % 2 == 0 ? 'T' : 'P');  // clock storey plain
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

        /// <summary>Iron box grilles on the ground-floor windows of some houses (all of that house's ground windows or
        /// none): the cheapest strong variation of ground floors, and what a street-level window looks like here.</summary>
        static bool Reja(BuildingSpec s)
        {
            if (s.type == "landmark" || s.family == "modern" || s.family == "rehab" || !EnvKit.HasModule("ENV_Window_Reja")) return false;
            uint h = (uint)(s.seed * 2654435761u) >> 7;
            return h % 100 < (s.family == "stone" || s.family == "stone_ground" ? 45 : 32);
        }

        /// <summary>Head line of a building's wide windows (phase 3 anti-procedural): 0 = the kit cut (head 2.52),
        /// +1 = Hi (2.41), -1 = Lo (2.21). ONE line per building — a second would break the structural read of the
        /// facade. Drawn from a dedicated hash of the seed (never the shared <paramref name="rng"/> consumed in order
        /// by Rows/Era/Shutters/History/Dress: inserting draws there would shift every later choice of the district).
        /// Exterior shutters are kit-height, so a building off the kit line keeps its windows bare; roller blinds hang
        /// from above the head and cover any line. Neglected houses get at most Lo: their boarded planks reach 2.27.</summary>
        public static int HeadLine(BuildingSpec s)
        {
            if (s.surrounds) return 0;                          // ashlar surrounds carry their own head
            uint h = (uint)s.seed * 2654435761u >> 11;
            int v = (int)(h % 100);
            if (s.era == "neglected") return v < 25 ? -1 : 0;
            return v < 28 ? 1 : v < 53 ? -1 : 0;
        }

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
            // the wide-window wall of the building's head line (kit cut, Hi 2.41 or Lo 2.21); stone bays keep the kit wall
            int hl = HeadLine(s);
            string WindowWall() => hl > 0 ? "ENV_Wall_Plaster_Clean_Window_Hi" : hl < 0 ? "ENV_Wall_Plaster_Clean_Window_Lo" : CleanPlaster["Window_Wide_Flat"];
            void WindowWallPart() { if (stone) Wall("Window_Wide_Flat"); else parts.Add(new EnvPart(WindowWall(), "wall")); }
            // stone bays: the kit "Rocks" window is only a stone surround, the glazed sash is a derived insert
            void WideWindow()
            {
                if (stone) { Stone("Window_Wide_Flat_Rocks"); Join("ENV_Window_Insert_Wide"); }
                else if (s.surrounds) parts.Add(new EnvPart("ENV_Window_Wide_Ashlar", "stone"));  // casco: sandstone surround + sash
                else if (hl > 0) Join("ENV_Window_Insert_Wide_Hi");
                else if (hl < 0) Join("ENV_Window_Insert_Wide_Lo");
                else Join("Window_Wide_Flat1");
            }

            switch (code)
            {
                case 'P':
                    parts.Add(new EnvPart(stone ? "Wall_UnevenBrick_Straight" : floor == 0 ? "ENV_Wall_Plaster_Clean_Base" : "ENV_Wall_Plaster_Clean", "wall"));
                    break;
                case 'W':
                    WindowWallPart();
                    WideWindow();
                    if (floor > 0) { if (s.era == "reformed") Stone("ENV_Window_Blind"); else if (hl == 0) Join("WindowShutters_Wide_Flat_Open"); }
                    else if (Reja(s)) parts.Add(new EnvPart("ENV_Window_Reja", "prop"));
                    break;
                case 'X':
                    WindowWallPart();
                    WideWindow();
                    Stone("ENV_Window_Boarded");
                    break;
                case 'w':
                    WindowWallPart();
                    WideWindow();
                    if (floor == 0 && Reja(s)) parts.Add(new EnvPart("ENV_Window_Reja", "prop"));
                    break;
                case 'c':
                    WindowWallPart();
                    WideWindow();
                    if (s.era == "reformed") Stone("ENV_Window_Blind"); else if (hl == 0) Join("WindowShutters_Wide_Flat_Closed");
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
            bool district = !string.IsNullOrEmpty(s.family);
            bool programme = !string.IsNullOrEmpty(s.business);
            for (int i = 0; i < s.bays; i++)
            {
                if (s.cornerEntrance && i == (s.cornerSide == "left" ? 0 : s.bays - 1)) continue;  // the chamfer carries its own fascia
                char g = rows[0][i];
                var x = 1 + 2 * i;
                if (g == 'A' || g == 'D' || g == 'O' || g == 'o') doors.Add(x);
                if (programme) continue;   // the business dresses its own front (EnvBusiness)
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
                if ((g == 'A' || g == 'D' || g == 'O' || g == 'o') && !district && (s.type == "lodging" || s.sign == "bracket"))
                    EnvKit.Remap(EnvKit.Place("ENV_Sign_Bracket", dress, new Vector3(x - 1f, 0, 0), 0), joinMap);
            }

            var field = EnvClearance.Field.Of(root, new[] { root });
            var ghosts = GhostQuoins(s, root, field);
            var hist = EnvKit.Group(root, "History");
            var weather = EnvKit.Group(root, "Weathering");
            var pipes = new List<float>();
            string cond = Condition(s);
            bool old = cond == "Viejo" || cond == "Gastado";

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
                        // the splash at the foot and the damp run along the pipe (owner: "humedad bajo bajantes")
                        if (district && (old || rng.NextDouble() < 0.5))
                            Stain("Downpipe", weather, new Vector3(x, 0, 0), new Vector3(0.8f + 0.5f * (float)rng.NextDouble(), 1.2f + 1.4f * (float)rng.NextDouble(), 1));
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

            if (programme)
                EnvBusiness.Dress(s, root, rows, rng, joinMap,
                    (m, par, pos, rot, sc) => TryPlace(m, par, pos, rot, sc),
                    (m, par, pos, rot, sc) => { var go = EnvKit.Place(m, par, pos, rot, sc); field.Add(go); return go; });
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
            if (s.type != "warehouse" && s.type != "landmark" && s.bays >= (s.hero > 0 ? 2 : 3) && s.era != "neglected" && (s.type == "lodging" || rng.NextDouble() < 0.35 + 0.35 * s.hero))
            {
                var xs = new List<float> { 2f, width - 2f };
                if (rng.NextDouble() < 0.5) xs.Reverse();
                foreach (var x in xs.Concat(Enumerable.Range(2, Math.Max(0, s.bays - 3)).Select(k => 2f * k)))
                    if (TryPlace("ENV_Prop_Lantern_Wall", dress, new Vector3(x, 3.3f, 0.1f), 0, new Vector3(0.75f, 0.75f, 0.75f))) break;
            }
            if (district)
            {
                Plants(s, root, rows, rng, doors, field, hist, TryPlace);
                DoorCanopies(s, rows, rng, doors, dress, TryPlace);
            }
            // doorstep pots: kept clear of pipes and meters, may stand in front of the door jambs
            else if (h.pots)
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
            for (int i = 0; i < s.bays && s.floors > 1 && !district; i++)
                if ((rows[1][i] == 'I' || rows[1][i] == 'B') && h.pots)
                    foreach (var sx in new[] { -0.55f, 0.55f })
                    {
                        EnvKit.Place("ENV_Planter_Pot", hist, new Vector3(1 + 2 * i + sx, BuildingAssembler.Storey, 0.42f), 0, new Vector3(0.6f, 0.6f, 0.6f));
                        EnvKit.Place("ENV_Plant_Bush_Flowers", hist, new Vector3(1 + 2 * i + sx, BuildingAssembler.Storey + 0.26f, 0.42f), rng.Next(360), new Vector3(0.3f, 0.3f, 0.3f));
                    }
            if (district)
            {
                // wall-mounted additions keep clear of every downpipe line and its brackets (the validator's pipe box)
                GameObject WallPlace(string m, Transform par, Vector3 pos, float rot, Vector3? sc, Func<EnvClearance.Item, bool> consider)
                {
                    float half = m == "ENV_AC_Unit" ? 0.42f : m == "ENV_Telecom_Box" || m == "ENV_Gas_Pipe" ? 0.22f : m == "ENV_Alarm_Box" || m == "ENV_Extractor_Vent" ? 0.15f : 0.1f;
                    if (pipes.Any(px => Mathf.Abs(px - pos.x) < half + 0.12f)) return null;
                    return TryPlace(m, par, pos, rot, sc, consider);
                }
                Contemporary(s, root, rows, rng, doors, hist, weather, WallPlace, old);
                Weathering(s, root, rows, rng, cond, weather, field);
                Thresholds(s, root, rows, rng, dress);
                GhostAdvert(s, root, rows, rng, weather);
            }
            foreach (var g in ghosts) UnityEngine.Object.DestroyImmediate(g);
        }

        /// <summary>Building-ground contact (owner point 15): a worn granite step under every portal (flush with the
        /// floor, so it shows as a step wherever the street falls away), a flush stone slab at shop doors, and on
        /// the damp residential lanes an old stone bench (poyo) by some doors — where the old neighbours sit.</summary>
        static void Thresholds(BuildingSpec s, Transform root, string[] rows, System.Random rng, Transform dress)
        {
            for (int i = 0; i < s.bays; i++)
            {
                char c = rows[0][i];
                float x = 1 + 2 * i;
                if ("DAoO".IndexOf(c) >= 0)
                    EnvKit.Remap(EnvKit.Place("ENV_Door_Step", dress, new Vector3(x, -0.14f, WallFaceZ), 0, new Vector3(1.0f, 1f, 0.9f)),
                                 new Dictionary<string, string> { { "MI_RockTrim", string.IsNullOrEmpty(s.dressed) ? "ENV_Dressed_Gris" : s.dressed } });
                else if (c == 'E' || c == 'e')
                    EnvKit.Remap(EnvKit.Place("ENV_Threshold_Slab", dress, new Vector3(x - 0.1f, -0.012f, WallFaceZ), 0),
                                 new Dictionary<string, string> { { "MI_RockTrim", "ENV_Dressed_Gris" } });
            }
        }

        const float WallFaceZ = 0.092f;

        /// <summary>A faded painted advertisement on the blind upper side wall of a taller corner house (owner points
        /// 21 and 44: blank walls, "carteles viejos", stories on the walls). Only on the rear bay of a deep side wall,
        /// clear of its small windows.</summary>
        static void GhostAdvert(BuildingSpec s, Transform root, string[] rows, System.Random rng, Transform weather)
        {
            if (s.floors < 3 || s.depth < 6 || rng.NextDouble() > 0.22) return;
            bool left = s.exposeLeft && (!s.exposeRight || rng.NextDouble() < 0.5);
            if (!left && !s.exposeRight) return;
            var ghosts = new[] { "ghost_anis", "ghost_chocolates", "ghost_abonos", "ghost_hotel" };
            var id = ghosts[rng.Next(ghosts.Length)];
            float z = -s.depth + 1.3f, y = 1 * BuildingAssembler.Storey + 0.5f;
            float x = left ? -0.1f : s.bays * 2 + 0.1f;
            var p = EnvKit.Place("ENV_Sign_Panel", weather, new Vector3(x, y + 1.0f, z), left ? 270 : 90, new Vector3(1.9f, 1.2f, 0.1f));
            EnvKit.Remap(p, new Dictionary<string, string> { { "ENV_Sign_Board", EnvBusiness.TextureMat("ENV_Ghost_" + id, "T_ENV_Ghost_" + id, 0.02f) }, { "MI_WoodTrim", s.render ?? "ENV_Plaster_Lime" } });
        }

        /// <summary>Render condition of a family building (Nuevo / Pintado / Viejo / Gastado), "" otherwise.</summary>
        public static string Condition(BuildingSpec s)
        {
            if (string.IsNullOrEmpty(s.render)) return "";
            var parts = s.render.Split('_');
            return parts.Length >= 4 ? parts[3] : "";
        }

        static GameObject Stain(string cell, Transform parent, Vector3 pos, Vector3 scale)
        {
            var go = EnvKit.Place("ENV_Stain_Quad", parent, pos, 0, scale);
            EnvKit.Remap(go, new Dictionary<string, string> { { "ENV_Stain_Downpipe", "ENV_Stain_" + cell } });
            return go;
        }

        /// <summary>Where water, iron and time mark a facade (owner audit 2026-09-29: "humedad bajo bajantes,
        /// reparaciones, desgaste de zócalos, manchas en esquinas"): streaks under sills, rust under iron balconies,
        /// run-off at exposed corners, a damp band on ground floors of damp streets, algae on river stone, repair
        /// patches on old render. Density follows the render's condition; nothing on a freshly painted front.</summary>
        static void Weathering(BuildingSpec s, Transform root, string[] rows, System.Random rng, string cond, Transform weather, EnvClearance.Field field)
        {
            if (cond == "Nuevo") return;
            float age = cond == "Gastado" ? 1f : cond == "Viejo" ? 0.6f : 0.25f;
            int width = s.bays * 2;
            for (int f = 1; f < rows.Length; f++)
                for (int i = 0; i < s.bays; i++)
                {
                    char c = rows[f][i];
                    float x = 1 + 2 * i, y = f * BuildingAssembler.Storey;
                    if ("Wwc".IndexOf(c) >= 0 && rng.NextDouble() < 0.4f * age)
                        Stain("Sill", weather, new Vector3(x + (float)(rng.NextDouble() - 0.5) * 0.2f, y + 0.95f - 1.3f, 0), new Vector3(1.1f, 1.3f, 1));
                    if ((c == 'I' || c == 'B') && rng.NextDouble() < 0.7f * age + 0.2f)
                        Stain(c == 'I' ? "Rust" : "Sill", weather, new Vector3(x, y - 1.2f, 0), new Vector3(1.5f, 1.25f, 1));
                }
            // corner run-off where the front corner is seen
            if (s.exposeLeft && rng.NextDouble() < 0.4f + 0.4f * age)
                Stain("Corner", weather, new Vector3(0.3f, 0.2f, 0), new Vector3(0.6f, s.floors * BuildingAssembler.Storey * (0.5f + 0.4f * (float)rng.NextDouble()), 1));
            if (s.exposeRight && rng.NextDouble() < 0.4f + 0.4f * age)
                Stain("Corner", weather, new Vector3(width - 0.3f, 0.2f, 0), new Vector3(-0.6f, s.floors * BuildingAssembler.Storey * (0.5f + 0.4f * (float)rng.NextDouble()), 1));
            // damp band / algae along the foot of solid ground-floor bays
            for (int i = 0; i < s.bays; i++)
            {
                char c = rows[0][i];
                if ("PWwT".IndexOf(c) < 0) continue;
                if (rng.NextDouble() < 0.35f * age + (s.basement > 0.5f ? 0.2f : 0f))
                    Stain(s.ground == "stone" && rng.NextDouble() < 0.5 ? "Algae" : "Damp", weather, new Vector3(1 + 2 * i, 0.02f, 0), new Vector3(2.05f, 0.8f + 0.7f * (float)rng.NextDouble(), 1));
            }
            // repair patches on old render, only where the wall is plain
            if (s.upper != "stone")
            {
                int n = rng.NextDouble() < 0.6f * age ? 1 + rng.Next(3) : 0;
                for (int k = 0; k < n; k++)
                {
                    int f = rng.Next(rows.Length), i = rng.Next(s.bays);
                    if (rows[f][i] != 'P') continue;
                    float w = 0.5f + 0.9f * (float)rng.NextDouble(), h = 0.4f + 0.7f * (float)rng.NextDouble();
                    var pos = new Vector3(1 + 2 * i + (float)(rng.NextDouble() - 0.5) * 0.6f, f * BuildingAssembler.Storey + 0.3f + 1.8f * (float)rng.NextDouble(), 0);
                    if (field.Hit(EnvClearance.Box(pos.x - w / 2, pos.x + w / 2, pos.y, pos.y + h, 0.05f, 0.2f), it => !it.module.StartsWith("ENV_Plinth")) == null)
                        Stain("Repair", weather, pos, new Vector3(w, h, 1));
                }
            }
        }

        /// <summary>The 21st century on an old front (owner: "falta arquitectura contemporánea"): split air-conditioning
        /// units, an alarm box over a shop, intercom and house number at the portal, extractor vents, a telecom box, a
        /// gas riser. All placed only where the facade has room; rarer on old untouched houses.</summary>
        static void Contemporary(BuildingSpec s, Transform root, string[] rows, System.Random rng, List<float> doors, Transform hist, Transform weather,
                                 System.Func<string, Transform, Vector3, float, Vector3?, System.Func<EnvClearance.Item, bool>, GameObject> tryPlace, bool old)
        {
            if (s.type == "landmark") return;
            bool recent = s.era == "reformed";
            // house number and intercom by every portal
            foreach (var x in doors)
            {
                int num = 1 + (int)(((uint)(s.seed * 2654435761u) >> 8) % 40);
                var plate = tryPlace("ENV_Sign_Panel", hist, new Vector3(x + 0.78f, 2.2f, 0.108f), 0, new Vector3(0.17f, 0.13f, 0.4f), null);
                if (plate) EnvKit.Remap(plate, new Dictionary<string, string> { { "ENV_Sign_Board", NumberMat(num, s.seed) }, { "MI_WoodTrim", "ENV_Paint_White" } });
                if (recent || rng.NextDouble() < 0.55)
                    foreach (var dx in rng.NextDouble() < 0.5 ? new[] { -0.95f, 0.95f } : new[] { 0.95f, -0.95f })
                        if (tryPlace("ENV_Intercom", hist, new Vector3(x + dx, 0, 0), 0, null, null)) break;
            }
            // air conditioning: on plain bays of upper floors, likelier on reformed houses and shops
            int ac = recent ? rng.Next(0, 3) : rng.NextDouble() < 0.18 ? 1 : 0;
            for (int k = 0; k < ac; k++)
            {
                int f = 1 + rng.Next(Mathf.Max(1, rows.Length - 1));
                if (f >= rows.Length) continue;
                var plain = Enumerable.Range(0, s.bays).Where(i => rows[f][i] == 'P').ToList();
                if (plain.Count == 0) continue;
                int b = plain[rng.Next(plain.Count)];
                tryPlace("ENV_AC_Unit", hist, new Vector3(1 + 2 * b, f * BuildingAssembler.Storey + 0.35f, 0), 0, null, null);
            }
            if (s.type == "mixed_commercial" && EnvBusiness.TypeOf(s) != "cerrado" && EnvBusiness.TypeOf(s) != "vivienda" && rng.NextDouble() < 0.55)
                foreach (var x in new[] { 1f, s.bays * 2 - 1f })
                    if (tryPlace("ENV_Alarm_Box", hist, new Vector3(x, 3.25f, 0), 0, null, null)) break;
            if (rng.NextDouble() < (recent ? 0.35 : 0.18))
            {
                var plain = Enumerable.Range(0, s.bays).Where(i => rows[0][i] == 'P' || (rows.Length > 1 && rows[1][i] == 'P')).ToList();
                if (plain.Count > 0)
                {
                    int b = plain[rng.Next(plain.Count)];
                    int f = rows[0][b] == 'P' ? 0 : 1;
                    var v = tryPlace("ENV_Extractor_Vent", hist, new Vector3(1 + 2 * b + 0.5f, f * BuildingAssembler.Storey + 2.2f, 0), 0, null, null);
                    if (v && (old || rng.NextDouble() < 0.4)) Stain("Soot", weather, new Vector3(1 + 2 * b + 0.5f, f * BuildingAssembler.Storey + 2.3f, 0), new Vector3(0.6f, 0.9f, 1));
                }
            }
            if (rng.NextDouble() < 0.2)
            {
                var plain = Enumerable.Range(0, s.bays).Where(i => rows[0][i] == 'P').ToList();
                if (plain.Count > 0) tryPlace("ENV_Telecom_Box", hist, new Vector3(1 + 2 * plain[rng.Next(plain.Count)] - 0.4f, 1.1f, 0), 0, null, null);
            }
            if (s.floors >= 2 && rng.NextDouble() < 0.12)
            {
                var cols = Enumerable.Range(0, s.bays).Where(i => rows.All(r => r[i] == 'P')).ToList();
                if (cols.Count > 0) tryPlace("ENV_Gas_Pipe", hist, new Vector3(1 + 2 * cols[rng.Next(cols.Count)] + 0.3f, 0, 0), 0, null, null);
            }
        }

        static string NumberMat(int n, int seed)
        {
            // 12 enamel number plates (Tools/env_signs.py); the house gets the nearest one
            var have = new[] { 2, 3, 5, 7, 8, 11, 12, 14, 17, 19, 21, 26 };
            int k = have.OrderBy(v => Mathf.Abs(v - n)).First();
            return EnvBusiness.TextureMat($"ENV_Num_{k}", $"T_ENV_Num_{k}", 0.5f);
        }

        /// <summary>Doorstep and balcony plants (owner audit: "las macetas delatan el procedural dressing"): far
        /// rarer, chosen by street (damp lanes and huerta edges keep more), mixed species of the humid north —
        /// hydrangeas, ferns, geraniums, box balls, a bay laurel — in different containers (terracotta, glazed, an
        /// old tin, a stone trough, a timber box), and never the same pair beside every door.</summary>
        static void Plants(BuildingSpec s, Transform root, string[] rows, System.Random rng, List<float> doors, EnvClearance.Field field, Transform hist,
                           System.Func<string, Transform, Vector3, float, Vector3?, System.Func<EnvClearance.Item, bool>, GameObject> tryPlace)
        {
            var dress = EnvKit.Group(root, "Dressing");
            float share = s.plantShare;
            System.Func<EnvClearance.Item, bool> soft = it => EnvClearance.IsService(it.module) || it.module == "ENV_Utility_Box" || it.module.StartsWith("Corner_") || it.module == "ENV_Intercom";
            (string pot, string plant, float py, float ps)[] doorsets =
            {
                ("ENV_Planter_Pot", "ENV_Plant_Hydrangea", 0.36f, 0.7f),
                ("ENV_Pot_Glazed", "ENV_Plant_Boxwood", 0.34f, 1.0f),
                ("ENV_Trough_Stone", "ENV_Plant_Hydrangea", 0.36f, 0.75f),
                ("ENV_Planter_Pot", "ENV_Plant_Fern", 0.36f, 0.075f),   // the kit fern is ~9 m wide
                ("ENV_Pot_Tin", "ENV_Plant_Geranium", 0.29f, 1.0f),
                ("ENV_Pot_Glazed", "ENV_Plant_Laurel", 0.33f, 1.0f),
                ("ENV_Planter_Box", "ENV_Plant_Geranium", 0.2f, 0.9f),
            };
            string[] flowers = { "ENV_Src_Flowers_Blue", "ENV_Src_Flowers", "ENV_Src_Flowers_White" };   // hydrangea heads (Quaternius flower atlas, tinted)
            string[] glazes = { "ENV_Ceramic_Blue", "ENV_Ceramic_Green", "ENV_Ceramic_Ochre" };
            foreach (var x in doors)
            {
                if (rng.NextDouble() > share) continue;
                var set = doorsets[rng.Next(doorsets.Length)];
                int count = set.pot == "ENV_Trough_Stone" || set.pot == "ENV_Planter_Box" || rng.NextDouble() < 0.6 ? 1 : 2;
                var sides = rng.NextDouble() < 0.5 ? new[] { -1.0f, 1.0f } : new[] { 1.0f, -1.0f };
                for (int k = 0; k < count; k++)
                {
                    float sx = sides[k] * (set.pot == "ENV_Trough_Stone" ? 1.3f : 0.98f);
                    var pos = new Vector3(x + sx, 0, set.pot == "ENV_Trough_Stone" ? 0.42f : 0.36f);
                    var pot = tryPlace(set.pot, dress, pos, rng.Next(-15, 15), null, soft);
                    if (!pot) continue;
                    if (set.pot == "ENV_Pot_Glazed") EnvKit.Remap(pot, new Dictionary<string, string> { { "ENV_Ceramic_Blue", glazes[rng.Next(glazes.Length)] } });
                    var pl = EnvKit.Place(set.plant, dress, pos + new Vector3(0, set.py, 0), rng.Next(360), Vector3.one * set.ps * (0.85f + 0.3f * (float)rng.NextDouble()));
                    EnvKit.Remap(pl, new Dictionary<string, string> { { "ENV_Src_Flowers_Blue", flowers[rng.Next(flowers.Length)] } });
                    // the leaves must not grow through a downpipe or a meter box either
                    var pb = EnvClearance.BoundsIn(root, pl);
                    pb.Expand(-0.02f);
                    if (field.Hit(pb, it => EnvClearance.IsService(it.module) || it.module == "ENV_Utility_Box") != null)
                    {
                        field.Remove(pot);
                        UnityEngine.Object.DestroyImmediate(pl);
                        UnityEngine.Object.DestroyImmediate(pot);
                        continue;
                    }
                    field.Add(pl);
                }
            }
            // an old stone bench by the door, a chair brought out (residential lanes: the plant share is high there)
            if (share >= 0.3f && doors.Count > 0 && rng.NextDouble() < 0.18 + 0.3 * s.hero)
            {
                float x = doors[rng.Next(doors.Count)] + (rng.NextDouble() < 0.5 ? -1.6f : 1.6f);
                if (tryPlace("ENV_Bench_Stone", dress, new Vector3(x, 0, 0.35f), 0, new Vector3(0.7f, 1, 0.8f), soft) && rng.NextDouble() < 0.5)
                    tryPlace("ENV_Prop_Chair", dress, new Vector3(x + (rng.NextDouble() < 0.5 ? 1.1f : -1.1f), 0, 0.6f), rng.Next(150, 210), null, soft);
            }
            // a bicycle left against the wall beside a door (residential lanes), parallel to the facade
            if (share >= 0.3f && doors.Count > 0 && rng.NextDouble() < 0.08 + 0.12 * s.hero)
            {
                float x = doors[rng.Next(doors.Count)] + (rng.NextDouble() < 0.5 ? -1.55f : 1.55f);
                var bike = tryPlace("ENV_Bicycle", dress, new Vector3(x, 0, 0.36f), rng.NextDouble() < 0.5 ? 90 : 270, null, soft);
                if (bike) EnvKit.Remap(bike, new Dictionary<string, string> { { "ENV_Paint_Red", new[] { "ENV_Paint_Red", "ENV_PropMat_Azul", "ENV_PropMat_Verde", "ENV_PropMat_Negro" }[rng.Next(4)] } });
            }
            // balconies: geraniums in a box or a couple of pots on some iron/timber balconies
            for (int f = 1; f < rows.Length; f++)
                for (int i = 0; i < s.bays; i++)
                {
                    if ((rows[f][i] != 'I' && rows[f][i] != 'B') || rng.NextDouble() > share * 1.2f) continue;
                    float y = f * BuildingAssembler.Storey;
                    if (rng.NextDouble() < 0.5)
                    {
                        EnvKit.Place("ENV_Planter_Box", hist, new Vector3(1 + 2 * i, y, 0.5f), 0, new Vector3(0.9f, 1, 0.8f));
                        EnvKit.Place("ENV_Plant_Geranium", hist, new Vector3(1 + 2 * i - 0.2f, y + 0.18f, 0.5f), rng.Next(360), Vector3.one * 0.8f);
                        EnvKit.Place("ENV_Plant_Geranium", hist, new Vector3(1 + 2 * i + 0.22f, y + 0.18f, 0.5f), rng.Next(360), Vector3.one * 0.75f);
                    }
                    else
                    {
                        float sx = rng.NextDouble() < 0.5 ? -0.55f : 0.55f;
                        EnvKit.Place("ENV_Planter_Pot", hist, new Vector3(1 + 2 * i + sx, y, 0.42f), 0, Vector3.one * 0.6f);
                        EnvKit.Remap(EnvKit.Place(rng.NextDouble() < 0.5 ? "ENV_Plant_Geranium" : "ENV_Plant_Hydrangea", hist, new Vector3(1 + 2 * i + sx, y + 0.23f, 0.42f), rng.Next(360), Vector3.one * 0.45f),
                                     new Dictionary<string, string> { { "ENV_Src_Flowers_Blue", flowers[rng.Next(flowers.Length)] } });
                    }
                }
        }

        /// <summary>Tejaroz over some old house doors (owner: doors and windows "les falta personalidad", not more of
        /// them): only plain portals of old houses, never shops, reformed fronts or stone-surround doors; refused where
        /// a balcony, sign, lantern or anything else of the facade is in the way. More often on the hero lanes.</summary>
        static void DoorCanopies(BuildingSpec s, string[] rows, System.Random rng, List<float> doors, Transform dress,
                                 System.Func<string, Transform, Vector3, float, Vector3?, System.Func<EnvClearance.Item, bool>, GameObject> tryPlace)
        {
            if (s.type == "mixed_commercial" || s.type == "landmark" || s.type == "warehouse" || s.era == "reformed" || s.family == "modern" || s.family == "rehab") return;
            foreach (var x in doors)
            {
                int bay = Mathf.RoundToInt((x - 1) / 2f);
                if (bay < 0 || bay >= rows[0].Length || "ADO".IndexOf(rows[0][bay]) < 0) continue;
                if (rng.NextDouble() > 0.1 + 0.35 * s.hero) continue;
                tryPlace("ENV_Door_Canopy", dress, new Vector3(x, 0, 0), 0, null, it => !it.module.Contains("Door"));
            }
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

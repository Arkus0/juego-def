using System.Collections.Generic;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// Assembly templates for the non-building parts of a street (CITY layered street assembly: datum ->
    /// traversable surface -> kerb/drain edge -> retaining/threshold contact -> dressing). Each template builds under
    /// a parent in its local frame; the street assembler and the unit library both call them, so a template fix
    /// improves every street. Frames: x runs along the street/edge, +z is "towards the street/water", y up.
    /// </summary>
    public static class EnvTemplates
    {
        static readonly Dictionary<string, string> WetCobble = new Dictionary<string, string> { { "MI_RoundRocks", "ENV_Ground_Setts_Old" } };
        public const float PavementTop = 0.15f;

        /// <summary>Street hierarchy profiles: surface materials, kerbs and default pavement width. Main and secondary
        /// streets are kerbed (pavement datum +0.15); the historic core is a shared surface (flag strips along the
        /// facades, setts between, granite channels, one level); lanes, plazas and port aprons are single-level.</summary>
        public static readonly Dictionary<string, (bool kerbed, string road, string pave, float pavement)> Profiles =
            new Dictionary<string, (bool, string, string, float)>
            {
                { "main", (true, "ENV_Ground_Setts_Grey", "ENV_Ground_Flag_Light", 1.8f) },
                { "secondary", (true, "ENV_Ground_Setts_Warm", "ENV_Ground_Flag_Warm", 1.2f) },
                { "kerbed", (true, "ENV_Ground_Setts_Warm", "ENV_Ground_Flag_Warm", 1.5f) },
                { "core", (false, "ENV_Ground_Setts_Warm", "ENV_Ground_Flag_Light", 0.9f) },  // shared surface, historic core
                { "lane", (false, "ENV_Ground_Setts_Old", null, 0f) },
                { "pedestrian", (false, "ENV_Ground_Setts_Old", null, 0f) },
                { "plaza", (false, "ENV_Ground_Flag_Warm", null, 0f) },
                { "port", (false, "ENV_Ground_Concrete", null, 0f) },
            };

        public static bool IsKerbed(string style) => Profiles.TryGetValue(style ?? "kerbed", out var p) && p.kerbed;

        static void Surface(Transform root, string material, float x0, float x1, float z0, float z1, float y, System.Random rng, float patchChance)
        {
            // setts on the kit cobble tile, flags on the kit flagstone tile, concrete on the kit brick tile (UVs only)
            string tile = material.Contains("Setts") || material.Contains("Patch") ? "Floor_RoundRocks" : material.Contains("Flag") ? "Floor_UnevenBrick" : "Floor_Brick";
            string slot = tile == "Floor_RoundRocks" ? "MI_RoundRocks" : tile == "Floor_UnevenBrick" ? "MI_UnevenBrick" : "MI_Brick";
            for (float x = x0; x < x1 - 0.01f; x += 2f)
            {
                float sx = Mathf.Min(2f, x1 - x);
                for (float z = z0; z < z1 - 0.01f; z += 2f)
                {
                    float sz = Mathf.Min(2f, z1 - z);
                    var m = patchChance > 0 && rng.NextDouble() < patchChance ? "ENV_Ground_Patch" : material;
                    var go = EnvKit.Place(m == "ENV_Ground_Patch" ? "Floor_RoundRocks" : tile, root, new Vector3(x + sx / 2f, y, z + sz / 2f), 0, new Vector3(sx / 2f, 1, sz / 2f));
                    EnvKit.Remap(go, new Dictionary<string, string> { { m == "ENV_Ground_Patch" ? "MI_RoundRocks" : slot, m } });
                }
            }
        }

        /// <summary>Street floor between two facade lines z = 0 and z = width, by hierarchy profile (main, secondary,
        /// lane, plaza, port): surface materials, granite kerbs on kerbed streets, central channel on lanes, and the
        /// small irregularities that stop it reading as a render: repair patches, drain grates, manholes, puddles and
        /// weeds at wall bases (deterministic by seed).</summary>
        public static Transform StreetGround(Transform parent, float length, float width, string style = "kerbed", float pavement = -1f, int seed = 1)
        {
            var root = EnvKit.Group(parent, "StreetGround");
            if (!Profiles.TryGetValue(style, out var prof)) throw new System.ArgumentException("ENV_UNKNOWN_STREET_STYLE " + style);
            var rng = new System.Random(seed * 131 + (int)(length * 10));
            int nx = Mathf.CeilToInt(length / 2f);
            if (!prof.kerbed)
            {
                float fp = prof.pave != null ? (pavement > 0 ? pavement : prof.pavement) : 0f;
                if (fp > 0)
                {
                    // shared surface ("plataforma única"): flag strips along both facades, setts between, two channels
                    Surface(root, prof.road, 0, length, fp, width - fp, 0, rng, 0.06f);
                    Surface(root, prof.pave, 0, length, 0, fp, 0, rng, 0f);
                    Surface(root, prof.pave, 0, length, width - fp, width, 0, rng, 0f);
                    for (int i = 0; i < nx; i++)
                        foreach (var z in new[] { fp, width - fp })
                            EnvKit.Place("ENV_Gutter_Channel_2m", root, new Vector3(1 + 2 * i, 0.001f, z), 0);
                    bool side = true;
                    for (float x = 3f; x < length - 1; x += 9f, side = !side)
                        EnvKit.Place("ENV_Drain_Grate", root, new Vector3(x, 0.005f, side ? fp : width - fp), 90);
                }
                else
                    Surface(root, prof.road, 0, length, 0, width, 0, rng, style == "plaza" ? 0f : 0.08f);
                if (style == "lane" || style == "pedestrian")
                {
                    for (int i = 0; i < nx; i++) EnvKit.Place("ENV_Gutter_Channel_2m", root, new Vector3(1 + 2 * i, 0.001f, width / 2f), 0);
                    for (float x = 4f; x < length - 1; x += 8f) EnvKit.Place("ENV_Drain_Grate", root, new Vector3(x, 0.005f, width / 2f), 90);
                    for (float x = 1f; x < length; x += 2.5f)
                        foreach (var z in new[] { 0.18f, width - 0.18f })
                            if (rng.NextDouble() < 0.35) EnvKit.Place(rng.NextDouble() < 0.7 ? "ENV_Weeds_Grass" : "ENV_Weeds_Tall", root, new Vector3(x + (float)rng.NextDouble(), 0, z), rng.Next(360), Vector3.one * 0.55f);
                }
                if (style != "plaza")
                    for (float x = 3f + (float)rng.NextDouble() * 4f; x < length - 1; x += 7f + (float)rng.NextDouble() * 5f)
                        EnvKit.Place(rng.NextDouble() < 0.5 ? "ENV_Puddle_A" : "ENV_Puddle_B", root, new Vector3(x, 0, width / 2f + (float)(rng.NextDouble() - 0.5) * 1.2f), rng.Next(360));
                return root;
            }
            float p = pavement > 0 ? pavement : prof.pavement;
            Surface(root, prof.road, 0, length, p, width - p, 0, rng, 0.12f);
            Surface(root, prof.pave, 0, length, 0, p, PavementTop, rng, 0f);
            Surface(root, prof.pave, 0, length, width - p, width, PavementTop, rng, 0f);
            for (int i = 0; i < nx; i++)
            {
                EnvKit.Place("ENV_Kerb_2m", root, new Vector3(1 + 2 * i, 0, p - 0.14f), 0);
                EnvKit.Place("ENV_Kerb_2m", root, new Vector3(1 + 2 * i, 0, width - p + 0.14f), 180);
            }
            bool south = true;
            for (float x = 3f; x < length - 1; x += 8f, south = !south)
                EnvKit.Place("ENV_Drain_Grate", root, new Vector3(x, 0.004f, south ? p + 0.22f : width - p - 0.22f), 0);
            for (float x = 6f + (float)rng.NextDouble() * 4f; x < length - 2; x += 12f + (float)rng.NextDouble() * 6f)
                EnvKit.Place("ENV_Manhole", root, new Vector3(x, 0, p + (width - 2 * p) * (0.3f + 0.4f * (float)rng.NextDouble())), 0);
            for (float x = 4f + (float)rng.NextDouble() * 3f; x < length - 1; x += 8f + (float)rng.NextDouble() * 6f)
                EnvKit.Place(rng.NextDouble() < 0.5 ? "ENV_Puddle_A" : "ENV_Puddle_B", root, new Vector3(x, 0, rng.NextDouble() < 0.5 ? p + 0.8f : width - p - 0.8f), rng.Next(360));
            return root;
        }

        /// <summary>Covers an x/z rectangle with 2 m kit floor tiles; the last row/column is scaled, never overlapped
        /// (overlapping coplanar tiles z-fight).</summary>
        public static void Tiles(Transform parent, string tile, float x0, float x1, float z0, float z1, float y, Dictionary<string, string> remap)
        {
            for (float x = x0; x < x1 - 0.01f; x += 2f)
            {
                float sx = Mathf.Min(2f, x1 - x);
                for (float z = z0; z < z1 - 0.01f; z += 2f)
                {
                    float sz = Mathf.Min(2f, z1 - z);
                    var go = EnvKit.Place(tile, parent, new Vector3(x + sx / 2f, y, z + sz / 2f), 0, new Vector3(sx / 2f, 1, sz / 2f));
                    EnvKit.Remap(go, remap);
                }
            }
        }

        /// <summary>Public working-water edge composed as a place, not a stopped street: rubble quay wall and granite
        /// coping at y = 0, a paved apron behind (z &lt; 0), and along the edge a sequence of treatments —
        /// an overlook section (stone upstand + rail, benches facing the water, lamps, lifebuoy) and working sections
        /// (open edge, mooring bollards, moored boats with lines, nets, fish crates), with stone steps down to the
        /// water and an optional slipway. Water 1.4 m below the coping.</summary>
        public static Transform QuayEdge(Transform parent, float length, bool railing, float quayDepth = 6f,
                                         float overlookFrom = -1, float overlookTo = -1, float stepsAt = -1, float slipwayAt = -1,
                                         int boats = 0, int seed = 1, bool water = true, bool lamps = true)
        {
            var root = EnvKit.Group(parent, "QuayEdge");
            var rng = new System.Random(seed * 71 + 5);
            int n = Mathf.CeilToInt(length / 4f);
            float len = n * 4f;
            if (railing && overlookFrom < 0) { overlookFrom = 0; overlookTo = len; }
            bool Overlook(float x) => x >= overlookFrom && x <= overlookTo;
            bool Gap(float x) => (stepsAt >= 0 && x > stepsAt - 0.2f && x < stepsAt + 3.2f) || (slipwayAt >= 0 && Mathf.Abs(x - slipwayAt) < 2.4f);
            for (int i = 0; i < n; i++)
                if (slipwayAt < 0 || Mathf.Abs(2 + 4 * i - slipwayAt) > 1.9f) EnvKit.Place("ENV_Quay_Wall_4m", root, new Vector3(2 + 4 * i, 0, 0), 0);
            // apron: flags on the overlook, concrete on the working quay
            var rngS = new System.Random(seed);
            for (float x = 0; x < len; x += 2f)
                Surface(root, Overlook(x + 1) ? "ENV_Ground_Flag_Light" : "ENV_Ground_Concrete", x, x + 2, -quayDepth, -0.25f, 0f, rngS, 0f);
            if (stepsAt >= 0) EnvKit.Place("ENV_Quay_Steps", root, new Vector3(stepsAt, 0, 0), 0);
            if (slipwayAt >= 0) EnvKit.Place("ENV_Slipway", root, new Vector3(slipwayAt, 0, -0.2f), 0);
            var bollards = new List<float>();
            for (float x = 1f; x < len; x += 2f)
            {
                if (Gap(x)) continue;
                if (Overlook(x)) EnvKit.Place("ENV_Parapet_Rail_2m", root, new Vector3(x, 0, -0.45f), 0);
                else if (Mathf.Repeat(x - 3f, 6f) < 0.1f) { EnvKit.Place("ENV_Bollard_Mooring", root, new Vector3(x, 0, -0.4f), 0); bollards.Add(x); }
            }
            if (overlookTo > overlookFrom)
            {
                for (float x = overlookFrom + 2.5f; x < overlookTo - 1.5f; x += 6f)
                    if (!Gap(x)) EnvKit.Place("ENV_Bench_Street", root, new Vector3(x, 0, -1.5f), 0);
                EnvKit.Place("ENV_Lifebuoy_Post", root, new Vector3(Mathf.Clamp(overlookTo - 0.6f, 0, len), 0, -1.1f), 0);
            }
            for (float x = 5f; x < len && lamps; x += 12f)
                EnvKit.Place("ENV_Lamp_Post", root, new Vector3(x, 0, -quayDepth + 0.8f), 0);
            if (!Gap(6f)) EnvKit.Place("ENV_Quay_Ladder", root, new Vector3(Mathf.Min(6f, len - 1), 0, 0), 0);
            // moored boats with lines to the nearest bollards, buoys, working clutter
            var hulls = new[] { "ENV_Paint_Blue", "ENV_Paint_Red", "ENV_Paint_Green", "ENV_Paint_White" };
            for (int b = 0; b < boats && b < bollards.Count; b++)
            {
                float bx = bollards[b] + 2.8f;
                var boat = EnvKit.Place("ENV_Boat_Small", root, new Vector3(bx, -1.45f, 1.9f), 90 + (rng.NextDouble() < 0.5 ? 0 : 180));
                EnvKit.Remap(boat, new Dictionary<string, string> { { "ENV_Paint_Blue", hulls[rng.Next(hulls.Length)] } });
                Line(root, new Vector3(bollards[b], 0.62f, -0.4f), new Vector3(bx - 2.3f, -0.6f, 1.6f));
                Line(root, new Vector3(bollards[b], 0.62f, -0.4f), new Vector3(bx + 2.2f, -0.6f, 1.5f));
            }
            for (int k = 0; k < 3; k++)
                EnvKit.Place("ENV_Buoy", root, new Vector3((float)rng.NextDouble() * len, -1.4f, 5f + (float)rng.NextDouble() * 8f), 0);
            float work = overlookTo > 0 && overlookTo < len - 4 ? overlookTo + 3f : 2f;
            if (work < len - 2)
            {
                EnvKit.Place("ENV_Net_Pile", root, new Vector3(work, 0, -2.2f), rng.Next(360));
                EnvKit.Place("ENV_Crate_Fish", root, new Vector3(work + 1.6f, 0, -1.6f), 10);
                EnvKit.Place("ENV_Crate_Fish", root, new Vector3(work + 1.7f, 0.22f, -1.62f), -6);
                EnvKit.Place("ENV_Prop_Rope_Coil", root, new Vector3(work - 1.2f, 0, -1.2f), 0);
            }
            if (water)
            {
                // one plane reaching 20 m past both ends, so chained quays can leave theirs off (no coplanar overlap)
                var plane = EnvKit.Place("ENV_Water_Plane_20m", root, new Vector3(len / 2f, -1.4f, 10f), 0, new Vector3((len + 40f) / 20f, 1, 1));
                plane.name = "PortWater";
            }
            return root;
        }

        /// <summary>Straight rope between two points (unit rope module stretched along +z).</summary>
        public static void Line(Transform parent, Vector3 a, Vector3 b)
        {
            var go = EnvKit.Place("ENV_Mooring_Line", parent, a, 0);
            go.transform.localRotation = Quaternion.LookRotation(b - a, Vector3.up);
            go.transform.localScale = new Vector3(1, 1, (b - a).magnitude);
        }

        /// <summary>Small square (plaza/placita) that gives a corner or a widening a reason to exist: warm flags,
        /// trees in iron pits, benches facing in, a lamp, a bar terrace on one side, bollards on the open edges.</summary>
        public static Transform Plaza(Transform parent, float w, float d, int trees = 2, bool terrace = true, int seed = 1, bool floor = true)
        {
            var root = EnvKit.Group(parent, "Plaza");
            var rng = new System.Random(seed * 17 + 3);
            if (floor) Surface(root, "ENV_Ground_Flag_Warm", 0, w, 0, d, 0.02f, rng, 0f);
            var spots = new List<Vector3> { new Vector3(w * 0.3f, 0, d * 0.35f), new Vector3(w * 0.72f, 0, d * 0.62f), new Vector3(w * 0.25f, 0, d * 0.75f) };
            string[] kinds = { "ENV_Tree_Common_A", "ENV_Tree_Common_C", "ENV_Tree_Common_B" };
            for (int i = 0; i < trees && i < spots.Count; i++)
            {
                EnvKit.Place("ENV_Tree_Pit", root, spots[i] + Vector3.up * 0.02f, 0);
                EnvKit.Place(kinds[i], root, spots[i], rng.Next(360), Vector3.one * (0.8f + 0.2f * (float)rng.NextDouble()));
                EnvKit.Place("ENV_Bench_Street", root, spots[i] + new Vector3(0, 0, -1.4f), 0);
            }
            EnvKit.Place("ENV_Lamp_Post", root, new Vector3(w - 1f, 0, 1f), -90);
            if (terrace)
            {
                var t = new Vector3(w * 0.62f, 0, d * 0.25f);
                EnvKit.Place("ENV_Parasol", root, t + new Vector3(0, 0, 0), 0);
                EnvKit.Place("ENV_Cafe_Table", root, t, 0);
                EnvKit.Place("ENV_Cafe_Chair", root, t + new Vector3(0, 0, -0.62f), 0);
                EnvKit.Place("ENV_Cafe_Chair", root, t + new Vector3(0.6f, 0, 0.1f), 250);
                EnvKit.Place("ENV_Cafe_Table", root, t + new Vector3(1.9f, 0, 0.4f), 0);
                EnvKit.Place("ENV_Cafe_Chair", root, t + new Vector3(1.9f, 0, -0.25f), 10);
                EnvKit.Place("ENV_Cafe_Chair", root, t + new Vector3(2.5f, 0, 0.5f), 260);
            }
            EnvKit.Place("ENV_Planter_Pot", root, new Vector3(0.6f, 0, d - 0.6f), 0);
            EnvKit.Place("ENV_Plant_Bush_Flowers", root, new Vector3(0.6f, 0.4f, d - 0.6f), 0, Vector3.one * 0.45f);
            EnvKit.Place("ENV_Bin_Street", root, new Vector3(w * 0.5f, 0, d - 0.5f), 180);
            return root;
        }

        /// <summary>Controlled work-yard boundary: galvanised palisade on a plinth with one sliding gate leaf parked
        /// in front of the fence line. Readably "you can see in, you cannot walk in".</summary>
        public static Transform YardBoundary(Transform parent, float length, int gateAt = 1)
        {
            var root = EnvKit.Group(parent, "YardBoundary");
            int n = Mathf.CeilToInt(length / 2f);
            for (int i = 0; i < n; i++)
            {
                if (i == gateAt) continue;
                EnvKit.Place("ENV_Fence_Yard_2m", root, new Vector3(1 + 2 * i, 0, 0), 0);
            }
            if (gateAt >= 0 && gateAt < n)
            {
                var gate = EnvKit.Place("ENV_Fence_Yard_2m", root, new Vector3(1 + 2 * gateAt, 0, 0.0f), 0);
                gate.name = "YardGate_Closed";
            }
            return root;
        }

        /// <summary>Stepped public connector rising <paramref name="height"/> m (1..3) from a lower datum (y = 0,
        /// z &gt; 1) to an upper terrace (y = height). The 2 m kit stair flights (1 m rise each, ascending towards -z)
        /// are cut into the terrace: rubble retaining walls line both sides and the terrace front (face at z = 1),
        /// guard rails run along every drop edge. Upper route continues at z &lt; 1 - 2*height.</summary>
        public static Transform SteppedConnector(Transform parent, int height, int terraceBays = 2, bool landing = true)
        {
            var root = EnvKit.Group(parent, "SteppedConnector");
            height = Mathf.Clamp(height, 1, 3);
            string wall = "ENV_Retaining_Wall_2x" + height;
            for (int k = 0; k < height; k++)
            {
                float zc = -2f * k;
                EnvKit.Place("Stairs_Exterior_Straight", root, new Vector3(0, k, zc), 0);
                EnvKit.Place(wall, root, new Vector3(-1f, height, zc), 90);   // faces +x, into the stair
                EnvKit.Place(wall, root, new Vector3(1f, height, zc), -90);   // faces -x
                EnvKit.Place("ENV_Railing_Quay_2m", root, new Vector3(-1.45f, height, zc), 90);
                EnvKit.Place("ENV_Railing_Quay_2m", root, new Vector3(1.45f, height, zc), 90);
            }
            float head = 1f - 2f * height;           // z where the last flight arrives on the terrace
            float xw = 1f + terraceBays * 2f;        // terrace half width
            for (int b = 0; b < terraceBays; b++)
                for (int side = -1; side <= 1; side += 2)
                {
                    float x = side * (2f + 2f * b);
                    EnvKit.Place(wall, root, new Vector3(x, height, 1f), 0);
                    EnvKit.Place("ENV_Railing_Quay_2m", root, new Vector3(x, height, 0.7f), 0);
                }
            // terrace floor (kept clear of the copings to avoid coplanar faces), lower landing in front
            Tiles(root, "Floor_UnevenBrick", -xw, xw, head - 4f, head, height, null);
            Tiles(root, "Floor_UnevenBrick", -xw, -1.95f, head, 0.1f, height, null);
            Tiles(root, "Floor_UnevenBrick", 1.95f, xw, head, 0.1f, height, null);
            if (landing) Tiles(root, "Floor_RoundRocks", -xw, xw, 1.1f, 5f, 0, WetCobble);
            return root;
        }

        /// <summary>Shallow shop interior behind a ground-floor frontage (building frame: street face z = 0, depth
        /// to -depthUsed): tiled floor, ceiling, back partition with a closed service door, counter, shelving and a
        /// warm interior light. The building's own walls provide the side faces.</summary>
        public static Transform ShopInterior(Transform parent, int bays, float doorX, float depthUsed = 4f)
        {
            var root = EnvKit.Group(parent, "Interior");
            float w = bays * 2f;
            Tiles(root, "Floor_Brick", 0.3f, w - 0.3f, -depthUsed, -0.4f, 0.01f, null);
            for (int i = 0; i < bays; i++)
            {
                var ceil = EnvKit.Place("Floor_WoodDark", root, new Vector3(1 + 2 * i, 2.95f, -depthUsed / 2f), 0, new Vector3(1, 1, depthUsed / 2f));
                ceil.transform.localRotation = Quaternion.Euler(180, 0, 0);
                string wall = i == bays - 1 ? "ENV_Wall_Plaster_Clean_Door" : "ENV_Wall_Plaster_Clean";
                var back = EnvKit.Place(wall, root, new Vector3(1 + 2 * i, 0, -depthUsed), 180);
                EnvKit.Remap(back, new Dictionary<string, string> { { "MI_Plaster", "ENV_Plaster_OffWhite" }, { "MI_WoodTrim", "ENV_Trim_White" } });
                if (i == bays - 1)
                {
                    EnvKit.Place("ENV_Door_Service", root, new Vector3(1 + 2 * i, 0, -depthUsed), 180);
                    var thr = new GameObject("THR_Service_Closed").transform;  // back-of-house: must stay shut
                    thr.SetParent(root, false);
                    thr.localPosition = new Vector3(1 + 2 * i, 0, -depthUsed);
                    thr.localRotation = Quaternion.Euler(0, 180, 0);
                }
            }
            EnvKit.Place("ENV_Counter_Shop", root, new Vector3(w * 0.5f, 0, -depthUsed + 1.6f), 0);
            EnvKit.Place("ENV_Prop_Shelf_Bottles", root, new Vector3(0.7f, 0, -depthUsed * 0.55f), 90);
            EnvKit.Place("ENV_Prop_Shelf_Simple", root, new Vector3(w - 0.7f, 0, -depthUsed * 0.55f), 270);
            // produce display on the side away from the public door: keep a clear 1.2 m lane door -> counter
            float side = doorX < w / 2f ? w - 1.1f : 1.1f;
            EnvKit.Place("ENV_Prop_FarmCrate_Apple", root, new Vector3(side, 0, -0.9f), 10);
            EnvKit.Place("ENV_Prop_FarmCrate_Carrot", root, new Vector3(side + (doorX < w / 2f ? -0.9f : 0.9f), 0, -0.9f), -8);
            var lightGo = new GameObject("InteriorLight");
            lightGo.transform.SetParent(root, false);
            lightGo.transform.localPosition = new Vector3(w / 2f, 2.6f, -depthUsed / 2f);
            var l = lightGo.AddComponent<Light>();
            l.type = LightType.Point;
            l.color = EnvKit.Hex("#E8B26A");
            l.intensity = 2.2f;
            l.range = 6f;
            l.shadows = LightShadows.None;
            return root;
        }

        /// <summary>Common lodging vestibule behind the portal bay, open to the next bay where the kit interior stair
        /// rises towards the back (to the rooms): flagged floor, ceiling over the entrance, side partitions to the
        /// building's back wall, a small reception counter and a warm light. Needs bays &gt;= portal + 2.</summary>
        public static Transform LodgingVestibule(Transform parent, int bay, int buildingBays, int depth)
        {
            if (bay + 1 >= buildingBays) throw new System.ArgumentException("lodging vestibule needs a bay right of the portal for the stair");
            var root = EnvKit.Group(parent, "Interior");
            float x = 1 + 2 * bay;
            float back = -depth + 0.32f;   // inner face of the building back wall
            var white = new Dictionary<string, string> { { "MI_Plaster", "ENV_Plaster_OffWhite" }, { "MI_WoodTrim", "ENV_Trim_White" } };
            Tiles(root, "Floor_Brick", x - 1f, x + 3f, back, -0.3f, 0.01f, null);
            var ceil = EnvKit.Place("Floor_WoodDark", root, new Vector3(x, 2.95f, back / 2f), 0, new Vector3(1, 1, -back / 2f));
            ceil.transform.localRotation = Quaternion.Euler(180, 0, 0);
            for (int j = 0; j < depth / 2; j++)
            {
                EnvKit.Remap(EnvKit.Place("ENV_Wall_Plaster_Clean", root, new Vector3(x - 1f, 0, -1 - 2 * j), 90), white);
                EnvKit.Remap(EnvKit.Place("ENV_Wall_Plaster_Clean", root, new Vector3(x + 3f, 0, -1 - 2 * j), 270), white);
            }
            EnvKit.Place("Stair_Interior_Solid", root, new Vector3(x + 2f, 0, back + 4.4f), 0);
            var counter = EnvKit.Place("ENV_Counter_Shop", root, new Vector3(x - 0.3f, 0, back + 1.2f), 0, new Vector3(0.6f, 1f, 1f));
            counter.name = "ReceptionCounter";
            EnvKit.Place("ENV_Plant_Small", root, new Vector3(x - 0.6f, 0, -0.8f), 0);
            var lightGo = new GameObject("InteriorLight");
            lightGo.transform.SetParent(root, false);
            lightGo.transform.localPosition = new Vector3(x + 0.5f, 2.6f, back / 2f);
            var l = lightGo.AddComponent<Light>();
            l.type = LightType.Point;
            l.color = EnvKit.Hex("#E8B26A");
            l.intensity = 2f;
            l.range = 6f;
            l.shadows = LightShadows.None;
            return root;
        }

        /// <summary>Places a list of (module, x, y, z, rotY) entries — small authored clusters (market stall, port
        /// props, furniture) described as data in units.json.</summary>
        public static Transform Cluster(Transform parent, string name, IEnumerable<(string module, Vector3 pos, float rot)> parts)
        {
            var root = EnvKit.Group(parent, name);
            foreach (var p in parts) EnvKit.Place(p.module, root, p.pos, p.rot);
            return root;
        }
    }
}

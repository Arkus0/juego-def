using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// One terraced port-town building described by outcome, not by object paths. Width is counted in 2 m kit
    /// bays; the grammar fills any row the spec leaves empty. See Docs/production/ENV_FACTORY.md for the codes.
    /// </summary>
    [Serializable]
    public class BuildingSpec
    {
        public string id = "Building";
        public string type = "mixed_commercial"; // mixed_commercial | closed_residential | lodging | warehouse | termination | landmark
        public int bays = 4;                     // 2 m bays along the frontage
        public int depth = 6;                    // 4 | 6 | 8 (kit roof modules)
        public int floors = 3;
        public int seed = 1;
        public string palette = "cream_green";
        public string ground = "";               // stone | plaster ("" = type default)
        public string upper = "plaster";         // plaster | stone
        public string[] rows;                    // codes per floor, ground first; missing/"" rows come from the grammar
        public string[] left, right;             // codes per floor for the side walls (depth/2 slots)
        public bool exposeLeft, exposeRight;     // side seen from the street (end of terrace / corner)
        public int partyLeft, partyRight;        // storeys hidden by a touching neighbour on that side (set by the street assembler)
        public bool quoinsLeft = true, quoinsRight = true; // one quoin column per shared edge: the street assembler turns one off
        public string roof = "eaves";            // eaves (ridge parallel to street) | gable (gable to street) | tower | none
        public float pitch = 0.45f;              // vertical scale of kit roofs (kit ~50 deg -> ~30 deg)
        public bool chimney = true;
        public string door = "";                 // portal door module override
        public string sign = "";                 // fascia | bracket | "" (grammar)
        public string awning = "";               // canvas material for shop awnings ("" = none)
        public bool dress = true;                // add building dressing (fascias, lamps, downpipes, history)
        public string interior = "";             // "" | shop (shallow shop room behind the ground floor) | lodging (vestibule behind the portal)
        public string era = "";                  // "" (seeded) | old | reformed | neglected — accumulated history of the building
        public bool history = true;              // allow the 10-20 % of later additions (dish, meters, cables, clothes, odd window)
        public bool cornerEntrance;              // chamfered ground-floor entrance at a front corner (needs that side exposed)
        public string cornerSide = "right";      // right | left: which front corner is chamfered
        public float basement;                   // m of stone base below the ground floor (sloping ground, river walls)
    }

    public static class BuildingAssembler
    {
        public const float Storey = 3f;
        static JObject palettes;

        /// <summary>Ground-floor bay codes that are thresholds, with the x of their clear passage in the slot
        /// (open leaves occupy the hinge side).</summary>
        public static readonly Dictionary<char, (string name, float x)> Thresholds = new Dictionary<char, (string, float)>
        {
            { 'e', ("THR_Public_Shop", -0.2f) }, { 'E', ("THR_Public_Shop_Closed", -0.2f) },
            { 'O', ("THR_Public_Portal", -0.2f) }, { 'o', ("THR_Public_Portal", -0.2f) },
            { 'D', ("THR_Public_Portal_Closed", 0f) }, { 'A', ("THR_Public_Portal_Closed", 0f) },
            { 'V', ("THR_Service_Closed", 0f) }, { 'G', ("THR_Gate_Closed", 0f) },
        };

        public static void ReloadGrammar() => palettes = null;

        static JObject Palettes => palettes ??= JObject.Parse(EnvKit.ReadText(EnvKit.Grammar + "/palettes.json"));

        public static Dictionary<string, string> RoleMap(string paletteId, string role)
        {
            var pal = Palettes["palettes"].FirstOrDefault(p => (string)p["id"] == paletteId) as JObject
                      ?? throw new ArgumentException("ENV_PALETTE_MISSING " + paletteId);
            var map = new Dictionary<string, string>();
            if (Palettes["roleRemaps"][role] is JObject remap)
                foreach (var kv in remap)
                    if (pal[(string)kv.Value] != null) map[kv.Key] = (string)pal[(string)kv.Value];
            return map;
        }

        public static string PaletteValue(string paletteId, string key)
        {
            var pal = Palettes["palettes"].First(p => (string)p["id"] == paletteId);
            return (string)pal[key];
        }

        /// <summary>Builds the building under <paramref name="parent"/>. Local frame: street face on z = 0 facing +z,
        /// footprint x in [0, 2*bays], z in [-depth, 0], ground floor at y = 0.</summary>
        public static GameObject Build(BuildingSpec s, Transform parent)
        {
            // Kit roof sizes: eaves roofs are 2 m modular sections for depth 4/6/8; gable roofs need a span (width) of
            // 4/6/8 m and a ridge length (depth + 2) of at most 14 m; the tower roof covers a 4 x 4 m plan.
            if (s.roof == "eaves" && s.depth != 4 && s.depth != 6 && s.depth != 8) throw new ArgumentException(s.id + ": eaves roof needs depth 4, 6 or 8");
            if (s.roof == "gable" && (s.bays < 2 || s.bays > 4 || s.depth % 2 != 0 || s.depth < 2 || s.depth > 12)) throw new ArgumentException(s.id + ": gable roof needs 2-4 bays and an even depth <= 12");
            if (s.roof == "tower" && (s.bays != 2 || s.depth != 4)) throw new ArgumentException(s.id + ": tower roof needs a 2-bay x 4 m plan");
            if (s.depth % 2 != 0) throw new ArgumentException(s.id + ": depth must be even (2 m side bays)");
            if (s.bays < 1 || s.floors < 1) throw new ArgumentException(s.id + ": bays/floors must be positive");
            bool cl = s.cornerSide == "left";
            if (s.cornerEntrance && ((cl ? !s.exposeLeft : !s.exposeRight) || s.bays < 2)) throw new ArgumentException(s.id + ": cornerEntrance needs the chamfered side exposed and >= 2 bays");
            var rng = new System.Random(s.seed * 7919 + s.id.GetHashCode());
            var rows = FacadeGrammar.Rows(s, rng);
            s.era = FacadeGrammar.ResolveEra(s, rng);
            rows = FacadeGrammar.ApplyEra(s, rows, rng);
            rows = FacadeGrammar.ResolveShutters(s, rows, rng);
            var history = s.dress && s.history ? FacadeGrammar.History.Draw(s, rows, rng) : FacadeGrammar.History.None;
            int width = s.bays * 2, nz = s.depth / 2;
            string[] SideRows(string[] given, bool exposed) => Enumerable.Range(0, s.floors)
                .Select(f => new string(Enumerable.Range(0, nz).Select(j => SideCode(given, exposed, f, j, nz, rng)).ToArray())).ToArray();
            var leftRows = FacadeGrammar.ResolveShutters(s, SideRows(s.left, s.exposeLeft), rng);
            var rightRows = FacadeGrammar.ResolveShutters(s, SideRows(s.right, s.exposeRight), rng);
            var root = new GameObject(s.id).transform;
            root.SetParent(parent, false);
            var wallMap = RoleMap(s.palette, "wall");
            var joinMap = RoleMap(s.palette, "joinery");
            var roofMap = RoleMap(s.palette, "roof");
            FacadeGrammar.EraMaterials(s, wallMap, joinMap, rng);
            var groundWallMap = history.groundRepaint != null ? With(wallMap, "MI_Plaster", history.groundRepaint) : wallMap;
            string groundFam = string.IsNullOrEmpty(s.ground) ? FacadeGrammar.DefaultGround(s.type) : s.ground;

            for (int f = 0; f < s.floors; f++)
            {
                float y = f * Storey;
                string fam = f == 0 ? groundFam : s.upper;
                var wm = f == 0 ? groundWallMap : wallMap;
                var front = EnvKit.Group(EnvKit.Group(root, "Front"), "F" + f);
                for (int i = 0; i < s.bays; i++)
                {
                    if (f == 0 && s.cornerEntrance && i == (cl ? 0 : s.bays - 1)) continue;
                    var jm = history.oddWindow == (f, i) ? With(joinMap, "MI_WoodTrim", "ENV_Joinery_Silver", "MI_WoodTrim_Wear", "ENV_Joinery_Silver") : joinMap;
                    Slot(s, front, fam, rows[f][i], f, new Vector3(1 + 2 * i, y, 0), 0, rng, wm, jm, plinth: true);
                }
                var back = EnvKit.Group(EnvKit.Group(root, "Back"), "F" + f);
                for (int i = 0; i < s.bays; i++)
                    Slot(s, back, fam, FacadeGrammar.BackCode(f, i, rng), f, new Vector3(width - 1 - 2 * i, y, -s.depth), 180, rng, wm, joinMap, plinth: false);
                var left = EnvKit.Group(EnvKit.Group(root, "Side_L"), "F" + f);
                var right = EnvKit.Group(EnvKit.Group(root, "Side_R"), "F" + f);
                // Party walls: storeys covered by a neighbour get no side wall (no hidden double walls, no z-fighting).
                for (int j = 0; j < nz; j++)
                {
                    if (f >= s.partyLeft && !(f == 0 && s.cornerEntrance && cl && j == nz - 1))
                        Slot(s, left, fam, leftRows[f][j], f, new Vector3(0, y, -s.depth + 1 + 2 * j), 270, rng, wm, joinMap, plinth: s.exposeLeft);
                    if (f >= s.partyRight && !(f == 0 && s.cornerEntrance && !cl && j == 0))
                        Slot(s, right, fam, rightRows[f][j], f, new Vector3(width, y, -1 - 2 * j), 90, rng, wm, joinMap, plinth: s.exposeRight);
                }
                var corners = EnvKit.Group(EnvKit.Group(root, "Corners"), "F" + f);
                string corner = "Corner_ExteriorWide_Brick";
                bool qL = s.quoinsLeft || f >= s.partyLeft, qR = s.quoinsRight || f >= s.partyRight;
                foreach (var c in new[] { new Vector3(0, y, 0), new Vector3(width, y, 0), new Vector3(width, y, -s.depth), new Vector3(0, y, -s.depth) })
                {
                    if (f == 0 && s.cornerEntrance && (cl ? c.x < 0.5f : c.x > 0.5f) && c.z > -0.5f) continue;  // the column replaces it
                    if (c.x < 0.5f ? qL : qR)
                        EnvKit.Place(corner, corners, c, CornerRot(c, width, s.depth));
                }
            }
            if (s.cornerEntrance) CornerEntrance(s, root, groundWallMap, joinMap);

            if (s.interior == "shop")
            {
                int door = rows[0].IndexOfAny(new[] { 'e', 'E' });
                if (door < 0) throw new ArgumentException(s.id + ": shop interior needs a shop entrance bay (e/E)");
                EnvTemplates.ShopInterior(root, s.bays, 1 + 2 * door + Thresholds['e'].x);
            }
            else if (s.interior == "lodging")
            {
                int portal = rows[0].IndexOfAny(new[] { 'O', 'o', 'A', 'D' });
                if (portal < 0) throw new ArgumentException(s.id + ": lodging interior needs a portal bay (O/o/A/D)");
                EnvTemplates.LodgingVestibule(root, portal, s.bays, s.depth);
            }
            if (s.basement > 0.05f) Basement(s, root, wallMap);
            BuildRoof(s, root, roofMap, wallMap);
            if (s.dress) FacadeGrammar.Dress(s, root, rows, rng, joinMap, history);
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
                if (!t.GetComponent<Light>()) GameObjectUtility.SetStaticEditorFlags(t.gameObject, (StaticEditorFlags)~0);
            return root.gameObject;
        }

        /// <summary>Chamfered ground-floor corner (bar/shop entrance under the corner): the last front bay and the first
        /// right-side bay give way to a 45-degree shop door wall, a cast-iron column carries the corner above, and a
        /// soffit closes the recess.</summary>
        static void CornerEntrance(BuildingSpec s, Transform root, Dictionary<string, string> wallMap, Dictionary<string, string> joinMap)
        {
            float w = s.bays * 2;
            bool left = s.cornerSide == "left";
            var g = EnvKit.Group(root, "CornerEntrance");
            var slot = new GameObject("e_chamfer").transform;
            slot.SetParent(g, false);
            slot.localPosition = left ? new Vector3(1, 0, -1) : new Vector3(w - 1, 0, -1);
            slot.localRotation = Quaternion.Euler(0, left ? -45 : 45, 0);
            var k = new Vector3(1.414f, 1, 1);
            EnvKit.Remap(EnvKit.Place("ENV_Wall_Plaster_Shopfront", slot, Vector3.zero, 0, k), wallMap);
            // the chamfer has no room of its own yet (shop interiors sit behind a front bay): its door stays shut, so the
            // threshold is a closed one and nobody walks into the void behind it
            EnvKit.Remap(EnvKit.Place("ENV_Shopfront_Door", slot, Vector3.zero, 0, k), With(joinMap, "MI_WindowGlass", "ENV_Glass_Shop"));
            EnvKit.Remap(EnvKit.Place("ENV_Shop_Fascia", slot, Vector3.zero, 0, k), joinMap);
            var thr = new GameObject("THR_Public_Shop_Closed").transform;
            thr.SetParent(slot, false);
            thr.localPosition = new Vector3(-0.28f, 0, 0);
            EnvKit.Place("ENV_Corner_Column", g, left ? new Vector3(0.1f, 0, -0.1f) : new Vector3(w - 0.1f, 0, -0.1f), 0);
            var soffit = EnvKit.Place("Floor_WoodDark", g, left ? new Vector3(1, 2.97f, -1) : new Vector3(w - 1, 2.97f, -1), 0);
            soffit.transform.localRotation = Quaternion.Euler(180, 0, 0);
            EnvKit.Remap(soffit, new Dictionary<string, string> { { "MI_WoodTrim", "ENV_Trim_Stone" } });
        }

        /// <summary>Stone base below the ground floor, down to the lowest ground around the building (a sloping
        /// street, a terraced yard, a river wall): rubble retaining-wall pieces on every face, coping at floor level.</summary>
        static void Basement(BuildingSpec s, Transform root, Dictionary<string, string> wallMap)
        {
            var g = EnvKit.Group(root, "Basement");
            int width = s.bays * 2;
            var k = new Vector3(1, s.basement / 2f, 1);
            void Piece(Vector3 at, float rot) => EnvKit.Remap(EnvKit.Place("ENV_Retaining_Wall_2x2", g, at, rot, k), wallMap);
            for (int i = 0; i < s.bays; i++)
            {
                Piece(new Vector3(1 + 2 * i, 0, 0), 0);
                Piece(new Vector3(width - 1 - 2 * i, 0, -s.depth), 180);
            }
            for (int j = 0; j < s.depth / 2; j++)
            {
                Piece(new Vector3(0, 0, -s.depth + 1 + 2 * j), 270);
                Piece(new Vector3(width, 0, -1 - 2 * j), 90);
            }
        }

        static float CornerRot(Vector3 c, int width, int depth)
        {
            bool l = c.x < 0.5f, front = c.z > -0.5f;
            if (front) return l ? 270 : 0;
            return l ? 180 : 90;
        }

        static char SideCode(string[] rows, bool exposed, int floor, int slot, int count, System.Random rng)
        {
            if (rows != null && floor < rows.Length && !string.IsNullOrEmpty(rows[floor]))
            {
                var r = rows[floor].Replace(" ", "");
                if (slot < r.Length) return r[slot];
            }
            if (!exposed) return 'P';
            // exposed end wall: sparse small windows on upper floors, blank on the ground floor
            if (floor == 0) return 'P';
            return slot == count / 2 ? 'T' : 'P';
        }

        static void Slot(BuildingSpec s, Transform parent, string fam, char code, int floor, Vector3 pos, float rot,
                         System.Random rng, Dictionary<string, string> wallMap, Dictionary<string, string> joinMap, bool plinth)
        {
            var side = Quaternion.Euler(0, rot, 0);
            var slot = new GameObject($"{code}_{parent.childCount}").transform;
            slot.SetParent(parent, false);
            slot.localPosition = pos;
            slot.localRotation = side;
            foreach (var p in FacadeGrammar.Recipe(s, fam, code, floor, rng))
            {
                var go = EnvKit.Place(p.module, slot, p.offset, p.rotY, p.scale);
                if (p.role == "wall") EnvKit.Remap(go, floor > 0 ? With(wallMap, "MI_Brick", wallMap.TryGetValue("MI_Plaster", out var fac) ? fac : null) : wallMap);
                else if (p.role == "joinery") EnvKit.Remap(go, joinMap);
                else if (p.role == "shop") EnvKit.Remap(go, With(joinMap, "MI_WindowGlass", "ENV_Glass_Shop"));
                else if (p.role.StartsWith("mat:")) EnvKit.Remap(go, AllTo(go, p.role.Substring(4)));
            }
            // Building-ground junction: a continuous ashlar plinth on rendered ground floors (stubs beside openings).
            if (floor == 0 && plinth && fam != "stone")
                foreach (var (x, wdt) in FacadeGrammar.PlinthRuns(code))
                    EnvKit.Place(wdt >= 1.9f ? "ENV_Plinth_2m" : "ENV_Plinth_Pier", slot, new Vector3(x, 0, 0), 0,
                                 wdt >= 1.9f ? (Vector3?)null : new Vector3(wdt / 0.2f, 1, 1));
            if (floor == 0 && Thresholds.TryGetValue(code, out var thr))
            {
                // Threshold interface for routes, validators and later interaction/NPC work: an empty marker on the
                // clear passage centre, forward = out to the street. "_Closed" = the leaf is shut in the geometry.
                var m = new GameObject(thr.name).transform;
                m.SetParent(slot, false);
                m.localPosition = new Vector3(thr.x, 0, 0);
            }
        }

        /// <summary>Returns a copy of <paramref name="map"/> with extra slot bindings (key, value, key, value...).</summary>
        public static Dictionary<string, string> With(Dictionary<string, string> map, params string[] kv)
        {
            var copy = new Dictionary<string, string>(map);
            for (int i = 0; i + 1 < kv.Length; i += 2)
                if (!string.IsNullOrEmpty(kv[i + 1])) copy[kv[i]] = kv[i + 1];
            return copy;
        }

        static Dictionary<string, string> AllTo(GameObject go, string material)
        {
            var map = new Dictionary<string, string>();
            foreach (var r in go.GetComponentsInChildren<Renderer>(true))
                foreach (var m in r.sharedMaterials) if (m) map[m.name] = material;
            return map;
        }

        static void BuildRoof(BuildingSpec s, Transform root, Dictionary<string, string> roofMap, Dictionary<string, string> wallMap)
        {
            if (s.roof == "none") return;
            var roof = EnvKit.Group(root, "Roof");
            float top = s.floors * Storey;
            int width = s.bays * 2;
            string tiles = PaletteValue(s.palette, "tiles") ?? "RoundTiles";
            var k = new Vector3(1, s.pitch, 1);
            if (s.roof == "tower")
            {
                // landmark tower: the kit pyramid roof with finial, not flattened
                EnvKit.Remap(EnvKit.Place($"Roof_Tower_{tiles}", roof, new Vector3(width / 2f, top, -s.depth / 2f), 0), roofMap);
                return;
            }
            if (s.roof == "gable")
            {
                // ridge runs front-to-back; gable ends face the street and the back
                var body = EnvKit.Place($"Roof_{tiles}_{width}x{s.depth + 2}", roof, new Vector3(width / 2f, top, -s.depth / 2f), 0, k);
                EnvKit.Remap(body, roofMap);
                var gf = EnvKit.Group(roof, "Gable_Front");
                EnvKit.Remap(EnvKit.Place("ENV_Roof_Gable_" + width, gf, new Vector3(width / 2f, top, 0), 0, k), wallMap);
                EnvKit.Remap(EnvKit.Place("ENV_Roof_Gable_" + width, EnvKit.Group(roof, "Gable_Back"), new Vector3(width / 2f, top, -s.depth), 180, k), wallMap);
            }
            else
            {
                // ridge parallel to the street, built from 2 m modular sections so party sides need no verge
                var body = EnvKit.Group(roof, "Body");
                for (int i = 0; i < s.bays; i++)
                {
                    // a verge where the roof end is open to the sky: end of terrace, or a lower neighbour
                    bool openL = s.exposeLeft || s.partyLeft < s.floors, openR = s.exposeRight || s.partyRight < s.floors;
                    string piece = "Mid";
                    if (i == 0 && openL) piece = "R";
                    if (i == s.bays - 1 && openR) piece = s.bays == 1 && openL ? "Mid" : "L";
                    var go = EnvKit.Place($"Roof_Modular_{tiles}_{s.depth}_{piece}", body, new Vector3(1 + 2 * i, top, -s.depth / 2f), 90, k);
                    EnvKit.Remap(go, roofMap);
                }
                if (s.partyLeft < s.floors)
                    EnvKit.Remap(EnvKit.Place("ENV_Roof_Gable_" + s.depth, EnvKit.Group(roof, "Gable_L"), new Vector3(0, top, -s.depth / 2f), 270, k), wallMap);
                if (s.partyRight < s.floors)
                    EnvKit.Remap(EnvKit.Place("ENV_Roof_Gable_" + s.depth, EnvKit.Group(roof, "Gable_R"), new Vector3(width, top, -s.depth / 2f), 90, k), wallMap);
            }
            if (s.chimney)
                EnvKit.Remap(EnvKit.Place("Prop_Chimney2", roof, new Vector3(width * 0.7f, top, -s.depth * 0.62f), 0), wallMap);
        }
    }
}

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using JuegoDef.Env;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace JuegoDef.City
{
    /// <summary>
    /// One-shot seeder for the town built on the Ivanix88 layout (author permission, Owner 2026-10-02):
    /// Ivanix decides urban composition, ENV01 decides architecture, gameplay decides interiors.
    /// Reads the seed produced by Tools/city_ivanix (layout trace -> authored street plan -> parcel pass, see its README)
    /// and writes two persistent authored scenes: CITY_IVX_Base (terrain by ground class, the XV-century wall as paseo
    /// maritimo, gates, bridges, antepuerto and pier, El Alto terraces, Finca, tapias, player) and CITY_IVX_Buildings
    /// (one ENV01 building per parcel, its facade on its street, one way in). Refuses to re-seed.
    /// </summary>
    public static class CityIvanixSeed
    {
        public const string SceneDir = "Assets/JuegoDef/Scenes/CITY_IVX";
        public const string BaseScene = SceneDir + "/CITY_IVX_Base.unity";
        public const string BuildingsScene = SceneDir + "/CITY_IVX_Buildings.unity";
        public static string DefaultSeed => Path.GetFullPath(Path.Combine(Application.dataPath, "../../../Tools/city_ivanix/reconstruction/city_seed_v4.json"));

        /// <summary>From WP-CITY-IVX-HUMAN-01 the CITY_IVX scenes are authored by hand and versioned in LFS: the tools that
        /// write town content (seed, dress, shopfronts) refuse to run, even after the scenes are deleted. Tools that only
        /// check or re-light (lint, NavMesh probe, DC convert, paving map) stay usable.</summary>
        public static readonly bool Frozen = true;

        public static void RefuseIfFrozen(string tool)
        {
            if (Frozen) throw new InvalidOperationException($"JD_CITY_IVX_FROZEN: {tool} would rewrite the hand-authored town (WP-CITY-IVX-HUMAN-01); edit the scenes by hand.");
        }

        static readonly string[] Palettes = { "core_lime_chestnut", "core_sandstone_chestnut", "core_ochre_chestnut", "core_lime_oxblood", "core_cream_oxblood" };
        static readonly Dictionary<string, string> KindStreet = new Dictionary<string, string>
        {
            { "comercial", "Espina_E" }, { "ribera", "Ribera" }, { "alta", "Calle_Alta_O" }, { "huertas", "Ronda_Huertas" },
        };

        [MenuItem("JuegoDef/CITY/Seed Ivanix town (one-shot)")]
        static void Menu() => Debug.Log(Seed(DefaultSeed));

        public static string Seed(string seedPath)
        {
            RefuseIfFrozen("CityIvanixSeed.Seed");
            if (File.Exists(BaseScene)) throw new InvalidOperationException("JD_CITY_IVX_ALREADY_SEEDED: the authored scenes own the town now.");
            var doc = JObject.Parse(File.ReadAllText(seedPath));
            Directory.CreateDirectory(SceneDir);

            var baseScene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = new GameObject("CITY_IVX_Base");
            Identity(root, "CITY_IVX_Base", "AuthoredScene", "Ivanix layout · ENV01 architecture · base");
            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional; sun.intensity = 1.2f; sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(42f, 60f, 0f);
            sun.transform.SetParent(root.transform);

            BuildTerrain((JObject)doc["terrain"], Group(root, "TERRAIN"));
            BuildWater(Group(root, "WATER"));
            if (doc["paseo"] is JObject paseo)
                BuildPaseo(paseo, (JArray)doc["towers"], doc["spurs"] as JArray ?? new JArray(), doc["antepuerto"] as JArray, Group(root, "PASEO_MURALLA"));
            else
                BuildRiverWall((JObject)doc["river_wall"], (JArray)doc["gates"], (JArray)doc["towers"], doc["spurs"] as JArray ?? new JArray(), Group(root, "RIVER_WALL"));
            var quay = Group(root, "BRIDGES_QUAY");
            BuildBridges((JArray)doc["bridges"], (JArray)doc["gates"], quay);
            if (doc["stairs_extra"] is JArray sx) BuildStairsExtra(sx, quay);
            if (doc["pier"] is JObject pier) BuildPier(pier, Group(quay.gameObject, "MUELLE_MADERA"));
            if (doc["terraces"] is JArray terr) BuildTerraces(terr, Group(root, "EL_ALTO_TERRACES"));
            if (doc["finca"] is JObject finca) BuildFinca(finca, Group(root, "FINCA_DEL_CACIQUE"));
            if (doc["tapias"] is JArray tapias) BuildTapias(tapias, Group(root, "TAPIAS"));
            TrimRailings(root.transform);
            var spawn = (JArray)doc["spawn"];
            EnvStreet.BringPlayer(new JObject { ["_spawnWorld"] = new JArray((float)spawn[0], (float)spawn[1] + 0.05f, (float)spawn[2]) });
            EditorSceneManager.SaveScene(baseScene, BaseScene);

            var bScene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive);
            EditorSceneManager.SaveScene(bScene, BuildingsScene);
            var broot = new GameObject("CITY_IVX_Buildings");
            SceneManager.MoveGameObjectToScene(broot, bScene);
            Identity(broot, "CITY_IVX_Buildings", "AuthoredScene", "Ivanix layout · ENV01 buildings");
            int ok = 0, fallback = 0, failed = 0;
            string prevHue = "";
            var errors = new List<string>();
            foreach (JObject b in doc["buildings"])
            {
                try
                {
                    var go = BuildOne(b, broot.transform, ref prevHue, out bool usedFallback);
                    if (usedFallback) fallback++;
                    ok++;
                }
                catch (Exception e) { failed++; if (errors.Count < 12) errors.Add($"{b["id"]}: {e.Message}"); }
            }
            EditorSceneManager.SaveScene(bScene, BuildingsScene);
            SceneManager.SetActiveScene(baseScene);
            EditorSceneManager.SaveScene(baseScene, BaseScene);
            return $"JD_CITY_IVX_SEEDED buildings={ok} fallback={fallback} failed={failed} {string.Join(" | ", errors)}";
        }

        [MenuItem("JuegoDef/CITY/Open Ivanix town")]
        public static void Open()
        {
            EditorSceneManager.OpenScene(BaseScene, OpenSceneMode.Single);
            EditorSceneManager.OpenScene(BuildingsScene, OpenSceneMode.Additive);
        }

        // ---------------------------------------------------------------- buildings

        static GameObject BuildOne(JObject b, Transform parent, ref string prevHue, out bool usedFallback)
        {
            usedFallback = false;
            var sp = (JObject)b["spec"];
            var kind = (string)b["kind"];
            int seed = (int)sp["seed"];
            var bs = new BuildingSpec
            {
                id = (string)sp["id"], type = (string)sp["type"], bays = (int)sp["bays"], depth = (int)sp["depth"],
                floors = (int)sp["floors"], roof = (string)sp["roof"], seed = seed, basement = (float)sp["basement"],
                palette = Palettes[seed % Palettes.Length], exposeLeft = true, exposeRight = true,
            };
            if (bs.roof == "eaves" && bs.bays > 9) bs.bays = 9;
            var row = KindStreet.TryGetValue(kind, out var street) ? new JObject { ["street"] = street } : new JObject();
            var plot = new JObject();
            if ((bool?)sp["casona"] == true) plot["casona"] = true;
            EnvCharacter.Apply(bs, plot, row, ref prevHue);
            // a town around 2000 has repainted most fronts: Nuevo 30 / Pintado 35 / Viejo 25 / Gastado 10 (ENV01's casco
            // is 30/0/52/18 by design); new fronts carry no stains, repainted ones few (owner review: "manchas grises")
            if (!string.IsNullOrEmpty(bs.render) && bs.render.StartsWith("ENV_Render_"))
            {
                var parts = bs.render.Split('_');
                if (parts.Length >= 4)
                {
                    var crng = new System.Random(seed * 31 + 7);
                    double a = crng.NextDouble();
                    string cond = a < 0.30 ? "Nuevo" : a < 0.65 ? "Pintado" : a < 0.90 ? "Viejo" : "Gastado";
                    bs.render = $"ENV_Render_{parts[2]}_{cond}";
                    bs.renderGround = bs.render + "_G";
                    bs.era = cond == "Gastado" ? "neglected" : cond == "Viejo" ? "old" : crng.NextDouble() < 0.6 ? "reformed" : "old";
                }
            }
            if ((bool?)sp["stone"] == true)
            {
                // casa-torre / palace wing: dressed sandstone ashlar, aged tiles, walnut joinery
                bs.family = "stone"; bs.ground = "stone"; bs.upper = "stone"; bs.era = "old"; bs.quoins = "ashlar";
                bs.stone = bs.stoneGround = "ENV_Mason_Silleria_Arenisca"; bs.dressed = "ENV_Dressed_Arenisca";
                bs.render = bs.renderGround = "ENV_Render_Arena_Viejo"; bs.roofMat = "ENV_Roof_TileAged"; bs.joinery = "ENV_Joinery_Walnut";
            }
            if (sp["escudo"] != null) bs.escudo = (bool)sp["escudo"];
            if (sp["solana"] != null) bs.solana = (bool)sp["solana"];
            if (sp["chimney"] != null) bs.chimney = (bool)sp["chimney"];
            if (sp["history"] != null) bs.history = (bool)sp["history"];
            if (sp["rows"] is JArray rows) bs.rows = rows.Select(r => (string)r).ToArray();
            if (sp["left"] is JArray left) bs.left = left.Select(r => (string)r).ToArray();
            if (sp["right"] is JArray right) bs.right = right.Select(r => (string)r).ToArray();
            // one way in per building (owner 2026-10-02): the grammar's rows, drawn with the assembler's own generator so
            // nothing else on the facade changes, keep a single entrance; cells of a consolidated building without the
            // main entrance, and houses whose front has no reachable ground, keep none
            bool door = (bool?)b["door"] ?? true;
            var rows0 = FacadeGrammar.Rows(bs, new System.Random(bs.seed * 7919 + bs.id.GetHashCode()));
            rows0[0] = SingleEntrance(rows0[0], bs.type, door);
            bs.rows = rows0;
            GameObject go;
            try { go = BuildingAssembler.Build(bs, parent); }
            catch (ArgumentException)
            {
                usedFallback = true;
                bs.roof = "eaves"; bs.depth = Mathf.Clamp(bs.depth, 4, 8) / 2 * 2; if (bs.depth == 2) bs.depth = 4;
                go = BuildingAssembler.Build(bs, parent);
            }
            var mid = (JArray)b["frontage_mid"];
            var n = new Vector3((float)b["facing"][0], 0f, (float)b["facing"][1]).normalized;
            var xdir = new Vector3(n.z, 0f, -n.x);
            // the plot's real width and depth: kit bays and depths scaled to the parcel (seed v4, 0.8-1.25)
            float sx = sp["sx"] != null ? (float)sp["sx"] : 1f, sz = sp["sz"] != null ? (float)sp["sz"] : 1f;
            float width = bs.bays * 2f * sx, depthM = bs.depth * sz;
            var origin = new Vector3((float)mid[0], (float)mid[1], (float)mid[2]) - xdir * width / 2f;
            go.transform.SetPositionAndRotation(origin, Quaternion.LookRotation(n, Vector3.up));
            go.transform.localScale = new Vector3(sx, 1f, sz);
            string sem = (string)b["semantic_id"] ?? bs.id, semName = (string)b["semantic_name"] ?? "";
            go.name = $"BLD_{bs.id} [{(sem.StartsWith("P_") ? sem + "|" : "")}{b["class"]}|{kind}|{bs.type}|{bs.bays}x{bs.depth}|{bs.floors}p]";
            Identity(go, bs.id, $"FacadeCell:{b["class"]}:{kind}:{bs.type}",
                $"semantic {sem}{(semName.Length > 0 ? " (" + semName + ")" : "")} · trace {b["trace_area_m2"]} m2 · roof seen {b["roof_seen"]}",
                new[] { origin, origin + xdir * width, origin + xdir * width - n * depthM, origin - n * depthM });
            return go;
        }

        /// <summary>Ground-floor row with at most one entrance: the shop door for shops, one gate for warehouses, the
        /// portal for houses and lodgings. Other doors become shop windows (shops) or windows.</summary>
        public static string SingleEntrance(string ground, string type, bool door)
        {
            const string Doors = "DAOoEeVGR";
            var c = ground.ToCharArray();
            int keep = -1;
            if (door)
            {
                string pref = type == "mixed_commercial" ? "eE" : type == "warehouse" ? "G" : type == "lodging" ? "AO" : "DAOo";
                for (int i = 0; i < c.Length && keep < 0; i++) if (pref.IndexOf(c[i]) >= 0) keep = i;
                for (int i = 0; i < c.Length && keep < 0; i++) if (Doors.IndexOf(c[i]) >= 0 && c[i] != 'R') keep = i;
                if (keep < 0) { keep = c.Length / 2; c[keep] = type == "mixed_commercial" ? 'E' : type == "warehouse" ? 'G' : 'D'; }
            }
            for (int i = 0; i < c.Length; i++)
                if (i != keep && Doors.IndexOf(c[i]) >= 0)
                    c[i] = type == "mixed_commercial" && c[i] != 'R' ? 'S' : 'W';
            return new string(c);
        }

        // ---------------------------------------------------------------- terrain / water / wall / bridges

        static void BuildTerrain(JObject t, Transform parent)
        {
            float ox = (float)t["origin"][0], oz = (float)t["origin"][1], cell = (float)t["cell"];
            var h = new Dictionary<long, (float y, int cls)>();
            foreach (JArray c in t["cells"]) h[Key((int)c[0], (int)c[1])] = ((float)c[2], (int)c[3]);
            // corners average only the neighbours on the same level, so terrace steps stay vertical (retaining walls)
            float Corner(int ci, int cj, float self)
            {
                float sum = 0; int n = 0;
                for (int di = -1; di <= 0; di++)
                for (int dj = -1; dj <= 0; dj++)
                    if (h.TryGetValue(Key(ci + di, cj + dj), out var v) && Mathf.Abs(v.y - self) < 0.6f) { sum += v.y; n++; }
                return n > 0 ? sum / n : self;
            }

            // shoreline: the land outline follows the trace, not the 1 m grid. Boundary corners (land on one side, water
            // on the other) are relaxed along the outline; the bank drops to the water as a sloped rock revetment.
            var edges = new List<(long a, long b, Vector2 outN)>();
            foreach (var kv in h)
            {
                int i = (int)(kv.Key >> 32), j = (int)(kv.Key & 0xffffffff);
                if (!h.ContainsKey(Key(i, j - 1))) edges.Add((Key(i + 1, j), Key(i, j), new Vector2(0, -1)));
                if (!h.ContainsKey(Key(i + 1, j))) edges.Add((Key(i + 1, j + 1), Key(i + 1, j), new Vector2(1, 0)));
                if (!h.ContainsKey(Key(i, j + 1))) edges.Add((Key(i, j + 1), Key(i + 1, j + 1), new Vector2(0, 1)));
                if (!h.ContainsKey(Key(i - 1, j))) edges.Add((Key(i, j), Key(i, j + 1), new Vector2(-1, 0)));
            }
            var nbr = new Dictionary<long, List<long>>();
            var outN = new Dictionary<long, Vector2>();
            foreach (var e in edges)
            {
                if (!nbr.TryGetValue(e.a, out var la)) nbr[e.a] = la = new List<long>();
                if (!nbr.TryGetValue(e.b, out var lb)) nbr[e.b] = lb = new List<long>();
                la.Add(e.b); lb.Add(e.a);
                outN[e.a] = (outN.TryGetValue(e.a, out var na) ? na : Vector2.zero) + e.outN;
                outN[e.b] = (outN.TryGetValue(e.b, out var nb) ? nb : Vector2.zero) + e.outN;
            }
            Vector2 Grid(long k) => new Vector2(ox + (int)(k >> 32) * cell, oz + (int)(k & 0xffffffff) * cell);
            var xz = nbr.Keys.ToDictionary(k => k, Grid);
            for (int it = 0; it < 6; it++)
            {
                var nxt = new Dictionary<long, Vector2>(xz);
                foreach (var kv in nbr)
                    if (kv.Value.Count == 2) nxt[kv.Key] = 0.5f * xz[kv.Key] + 0.25f * (xz[kv.Value[0]] + xz[kv.Value[1]]);
                xz = nxt;
            }

            // ground by meaning (seed v4 classes): streets, lanes, huertas, under buildings, shore rock, meadow, the Calle
            // Mayor's granite flags, the Plaza Mayor's setts, the quay, yards behind the tapias, the roads outside
            string[] mats = { "ENV_Pave_Canto", "ENV_Pave_Canto_Viejo", "ENV_Ground_Grass", "ENV_Ground_Canto_Old", "ENV_RiverWall_Canto", "ENV_Ground_Grass",
                              "ENV_Pave_Losa", "ENV_Pave_Adoquin", "ENV_Ground_Setts_Grey", "ENV_Ground_Earth", "ENV_Ground_Setts_Old" };
            string[] names = { "CANTO", "CANTO_VIEJO", "HUERTA", "SUELO", "ROCA", "PRADO", "LOSA", "ADOQUIN", "MUELLE", "PATIO", "CAMINO" };
            const int Chunk = 64;
            var builders = new Dictionary<(int cls, int cx, int cz), MB>();
            var shore = new MB();
            foreach (var kv in h)
            {
                int i = (int)(kv.Key >> 32), j = (int)(kv.Key & 0xffffffff);
                var key = (kv.Value.cls, i / Chunk, j / Chunk);
                if (!builders.TryGetValue(key, out var mb)) builders[key] = mb = new MB();
                float self = kv.Value.y;
                Vector3 V(int ci, int cj)
                {
                    var k = Key(ci, cj);
                    var p2 = xz.TryGetValue(k, out var q) ? q : new Vector2(ox + ci * cell, oz + cj * cell);
                    return new Vector3(p2.x, Corner(ci, cj, self), p2.y);
                }
                Vector3 a = V(i, j), b = V(i + 1, j), c = V(i + 1, j + 1), d = V(i, j + 1);
                mb.Quad(a, d, c, b, true);
                // internal drops (terraces, quays) keep a vertical face of the cell's own surface
                float Drop(int ni, int nj) => h.TryGetValue(Key(ni, nj), out var nv) ? (self - nv.y > 0.6f ? nv.y - 0.2f : float.NaN) : float.NaN;
                float s0 = Drop(i, j - 1), s1 = Drop(i + 1, j), s2 = Drop(i, j + 1), s3 = Drop(i - 1, j);
                if (!float.IsNaN(s0)) mb.Skirt(b, a, s0);
                if (!float.IsNaN(s1)) mb.Skirt(c, b, s1);
                if (!float.IsNaN(s2)) mb.Skirt(d, c, s2);
                if (!float.IsNaN(s3)) mb.Skirt(a, d, s3);
                // to the water: a rock revetment sloping 1.4 m out and down below the surface
                Vector3 Toe(int ci, int cj, Vector3 top)
                {
                    var n2 = outN.TryGetValue(Key(ci, cj), out var nn) && nn.sqrMagnitude > 1e-4f ? nn.normalized : Vector2.zero;
                    return new Vector3(top.x + n2.x * 1.4f, -1.4f, top.z + n2.y * 1.4f);
                }
                void Bank(Vector3 p0, int i0, int j0, Vector3 p1, int i1, int j1) => shore.QuadUV(p0, Toe(i0, j0, p0), Toe(i1, j1, p1), p1);
                if (!h.ContainsKey(Key(i, j - 1))) Bank(b, i + 1, j, a, i, j);
                if (!h.ContainsKey(Key(i + 1, j))) Bank(c, i + 1, j + 1, b, i + 1, j);
                if (!h.ContainsKey(Key(i, j + 1))) Bank(d, i, j + 1, c, i + 1, j + 1);
                if (!h.ContainsKey(Key(i - 1, j))) Bank(a, i, j, d, i, j + 1);
            }
            foreach (var kv in builders)
                MeshObject($"TERRAIN_{names[kv.Key.cls]}_{kv.Key.cx}_{kv.Key.cz}", parent, kv.Value.ToMesh(), EnvKit.Mat(mats[kv.Key.cls]), true);
            MeshObject("TERRAIN_ORILLA_ESCOLLERA", parent, shore.ToMesh(), EnvKit.Mat("ENV_RiverWall_Canto"), true);
        }

        static void BuildWater(Transform parent)
        {
            var mb = new MB();
            mb.Quad(new Vector3(-400, 0, -400), new Vector3(-400, 0, 400), new Vector3(500, 0, 400), new Vector3(500, 0, -400), true);
            MeshObject("RIVER_WATER", parent, mb.ToMesh(), EnvKit.Mat("ENV_River_Water"), false);
            var bed = GameObject.CreatePrimitive(PrimitiveType.Cube);
            bed.name = "RIVERBED_SAFETY (collider only)";
            bed.transform.SetParent(parent, false);
            bed.transform.position = new Vector3(50, -2.2f, 0);
            bed.transform.localScale = new Vector3(900, 0.4f, 800);
            UnityEngine.Object.DestroyImmediate(bed.GetComponent<MeshRenderer>());
        }

        static void BuildRiverWall(JObject w, JArray gates, JArray towers, JArray spurs, Transform parent)
        {
            var pts = ((JArray)w["points"]).Select(p => new Vector3((float)p[0], (float)p[1], (float)p[2])).ToList();
            float thick = (float)w["thickness"], parapet = (float)w["parapet"], baseY = (float)w["base_y"];
            var gatePos = gates.Select(g => new Vector3((float)g["pos"][0], 0, (float)g["pos"][2])).ToList();
            var stone = EnvKit.Mat("ENV_RiverWall_Silleria");
            var cap = EnvKit.Mat("ENV_Mason_Silleria_Arenisca");
            var lines = new List<(List<Vector3> pts, bool closed, string name)> { (pts, true, "MALECON") };
            foreach (JObject sp in spurs)
                lines.Add((((JArray)sp["points"]).Select(p => new Vector3((float)p[0], (float)p[1], (float)p[2])).ToList(), false, "ANTEPUERTO"));
            foreach (var line in lines)
            for (int i = 0; i < (line.closed ? line.pts.Count : line.pts.Count - 1); i++)
            {
                var a = line.pts[i]; var b = line.pts[(i + 1) % line.pts.Count];
                var mid = (a + b) / 2f;
                if (gatePos.Any(g => Vector2.Distance(new Vector2(g.x, g.z), new Vector2(mid.x, mid.z)) < 5.5f)) continue;   // gate opening
                var dir = new Vector3(b.x - a.x, 0, b.z - a.z);
                float len = dir.magnitude;
                if (len < 0.05f) continue;
                float top = Mathf.Max(a.y, b.y) + parapet;
                var seg = GameObject.CreatePrimitive(PrimitiveType.Cube);
                seg.name = $"{line.name}_{i:000}";
                seg.transform.SetParent(parent, false);
                seg.transform.position = new Vector3(mid.x, (top + baseY) / 2f, mid.z);
                seg.transform.rotation = Quaternion.LookRotation(dir / len, Vector3.up);
                seg.transform.localScale = new Vector3(thick, top - baseY, len + 0.3f);
                seg.GetComponent<MeshRenderer>().sharedMaterial = stone;
                seg.isStatic = true;
                var coping = GameObject.CreatePrimitive(PrimitiveType.Cube);
                coping.name = "PRETIL";
                UnityEngine.Object.DestroyImmediate(coping.GetComponent<BoxCollider>());
                coping.transform.SetParent(seg.transform, false);
                coping.transform.localPosition = new Vector3(0, 0.5f, 0);
                coping.transform.localScale = new Vector3(1.12f, 0.12f / (top - baseY), 1.0f);
                coping.GetComponent<MeshRenderer>().sharedMaterial = cap;
            }
            foreach (JObject t in towers)
            {
                var p = (JArray)t["pos"];
                float top = (float)t["top"] + 1.1f;
                var c = Cylinder();
                c.name = $"CUBO_{t["role"]}";
                c.transform.SetParent(parent, false);
                c.transform.position = new Vector3((float)p[0], (top + baseY) / 2f, (float)p[1]);
                c.transform.localScale = new Vector3(6.6f, (top - baseY) / 2f, 6.6f);
                c.GetComponent<MeshRenderer>().sharedMaterial = stone;
                c.isStatic = true;
            }
        }

        static void BuildBridges(JArray bridges, JArray gates, Transform parent)
        {
            var deck = EnvKit.Mat("ENV_Ground_Setts_Old");
            var wall = EnvKit.Mat("ENV_Mason_Silleria_Gris");
            foreach (JObject b in bridges)
            {
                var f = new Vector3((float)b["from"][0], (float)b["from"][1], (float)b["from"][2]);
                var t = new Vector3((float)b["to"][0], (float)b["to"][1], (float)b["to"][2]);
                float w = (float)b["width"];
                var dir = t - f;
                var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
                go.name = $"{b["id"]}";
                go.transform.SetParent(parent, false);
                go.transform.position = (f + t) / 2f + Vector3.down * 0.4f;
                go.transform.rotation = Quaternion.LookRotation(dir.normalized, Vector3.up);
                go.transform.localScale = new Vector3(w, 0.8f, dir.magnitude);
                go.GetComponent<MeshRenderer>().sharedMaterial = deck;
                if ((string)b["id"] != "muelle_norte")
                    foreach (int side in new[] { -1, 1 })
                    {
                        var par = GameObject.CreatePrimitive(PrimitiveType.Cube);
                        par.name = "PRETIL";
                        par.transform.SetParent(go.transform, false);
                        par.transform.localPosition = new Vector3(side * 0.5f, 1.1f, 0);
                        par.transform.localScale = new Vector3(0.35f / w, 1.4f / 0.8f, 1f);
                        par.GetComponent<MeshRenderer>().sharedMaterial = wall;
                    }
            }
        }

        /// <summary>The XV-century wall adapted as a paseo maritimo: the wall body carries a flagstone deck that rises and
        /// falls with the town, a stone parapet on the sea side and the quay railing on the town side, cubos turned into
        /// round lookouts flush with the deck, the antepuerto arms as two short paseos, and stairs against the inner face
        /// (the railing opens at each landing). The deck ends at every gate with a cross railing.</summary>
        static void BuildPaseo(JObject paseo, JArray towers, JArray spurs, JArray ante, Transform parent)
        {
            var body = EnvKit.Mat("ENV_RiverWall_Silleria");
            var deckMat = EnvKit.Mat("ENV_Pave_Losa_Viejo");
            var stepMat = EnvKit.Mat("ENV_Mason_Silleria_Gris");
            var cheek = EnvKit.Mat("ENV_Mason_Silleria_Arenisca");
            float half = (float)paseo["half_width"], baseY = (float)paseo["base_y"];
            Identity(parent.gameObject, "PASEO_MURALLA", "PublicSpace:paseo", "muralla del s. XV adaptada como paseo marítimo");
            var pts = ((JArray)paseo["points"]).Select(p => (pos: new Vector3((float)p[0], (float)p[3], (float)p[2]), gap: (bool)p[4], abut: p.Count() > 5 && (bool)p[5])).ToList();
            // the quay railing's own painted iron, built continuous along each run (no 2 m modules overlapping at joints)
            var railProto = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/JuegoDef/Derived/ENV/Modules/ENV_Railing_Quay_2m.prefab");
            var iron = railProto ? railProto.GetComponentInChildren<Renderer>().sharedMaterial : EnvKit.Mat("ENV_Metal_Iron");
            var coping = EnvKit.Mat("ENV_Mason_Silleria_Gris");
            var landings = ((JArray)paseo["stairs"]).Select(s => new Vector3((float)s["landing"][0], 0, (float)s["landing"][2])).ToList();
            // ring orientation: the town is on the left of the walking direction when the ring runs counter-clockwise
            float area = 0;
            for (int i = 0; i < pts.Count; i++) { var a = pts[i].pos; var b = pts[(i + 1) % pts.Count].pos; area += a.x * b.z - b.x * a.z; }
            float leftIsTown = area > 0 ? 1f : -1f;

            var towerXZ = towers.Select(t0 => new Vector2((float)t0["pos"][0], (float)t0["pos"][1])).ToList();
            void Rail(Transform g, Vector3 a, Vector3 b, bool startPost, bool endPost)
            {
                // two painted iron rails (hand rail at 1.0 m, mid rail at 0.5 m) and a post at the start of each 2 m bay
                var d = b - a;
                float L = d.magnitude;
                if (L < 0.05f) return;
                var r = Quaternion.LookRotation(d / L);
                // every bar and post has a body: what stands on the paseo keeps clear of all of the railing, not just its top
                foreach (float h in new[] { 1.0f, 0.5f })
                    Box("BARANDILLA", g, (a + b) / 2f + Vector3.up * h, r, new Vector3(0.05f, h > 0.9f ? 0.06f : 0.04f, L + 0.03f), iron, true);
                if (startPost) Box("POSTE", g, a + Vector3.up * 0.51f, Quaternion.LookRotation(new Vector3(d.x, 0, d.z).normalized), new Vector3(0.06f, 1.02f, 0.06f), iron, true);
                if (endPost) Box("POSTE", g, b + Vector3.up * 0.51f, Quaternion.LookRotation(new Vector3(d.x, 0, d.z).normalized), new Vector3(0.06f, 1.02f, 0.06f), iron, true);
            }

            void Run(List<(Vector3 pos, bool gap, bool abut)> line, bool closed, string name, Func<Vector3, Vector3, Vector3> inward)
            {
                var g = new GameObject(name).transform;
                g.SetParent(parent, false);
                int n = closed ? line.Count : line.Count - 1;
                bool railOpen = false;
                for (int i = 0; i < n; i++)
                {
                    var A = line[i]; var B = line[(i + 1) % line.Count];
                    if (A.gap || B.gap)
                    {
                        // the deck ends at the gate: a cross railing on the last segment before the opening
                        if (A.gap != B.gap)
                        {
                            var end = A.gap ? B.pos : A.pos;
                            var other = A.gap ? A.pos : B.pos;
                            var d0 = new Vector3(other.x - end.x, 0, other.z - end.z).normalized;
                            var side = new Vector3(-d0.z, 0, d0.x);
                            Rail(g, end + d0 * 0.1f - side * (half - 0.1f), end + d0 * 0.1f + side * (half - 0.1f), true, true);
                        }
                        railOpen = false;
                        continue;
                    }
                    var a3 = A.pos; var b3 = B.pos;
                    var flat = new Vector3(b3.x - a3.x, 0, b3.z - a3.z);
                    float len = flat.magnitude;
                    if (len < 0.05f) continue;
                    var t = flat / len;
                    var inn = inward(a3, t);
                    var mid = (a3 + b3) / 2f;
                    var dir3 = (b3 - a3).normalized;
                    var pitch = Quaternion.LookRotation(dir3);
                    float low = Mathf.Min(a3.y, b3.y);
                    float len3 = (b3 - a3).magnitude;
                    Box("MURO", g, new Vector3(mid.x, (low - 0.3f + baseY) / 2f, mid.z), Quaternion.LookRotation(t), new Vector3(half * 2f, low - 0.3f - baseY, len + 0.08f), body, true);
                    Box("ADARVE", g, mid - Vector3.up * 0.15f, pitch, new Vector3(half * 2f, 0.3f, len3 + 0.06f), deckMat, true);
                    // sea parapet: continuous ashlar with a coping; at a cubo it opens onto the lookout
                    if (!towerXZ.Any(tp => Vector2.Distance(tp, new Vector2(mid.x, mid.z)) < 3.6f))
                    {
                        Box("PARAPETO", g, mid - inn * (half - 0.25f) + Vector3.up * 0.45f, pitch, new Vector3(0.5f, 0.9f, len3 + 0.02f), cheek, true);
                        Box("ALBARDILLA", g, mid - inn * (half - 0.25f) + Vector3.up * 0.94f, pitch, new Vector3(0.62f, 0.08f, len3 + 0.02f), coping, false);
                    }
                    // town-side railing, continuous; none where a house stands against the wall or the stairs open
                    var ra = a3 + inn * (half - 0.08f);
                    var rb = b3 + inn * (half - 0.08f);
                    bool stairs = landings.Any(l => Vector2.Distance(new Vector2(l.x, l.z), new Vector2((ra.x + rb.x) / 2, (ra.z + rb.z) / 2)) < 1.9f);
                    bool house = A.abut || B.abut;
                    if (stairs || house)
                    {
                        if (railOpen) Box("POSTE", g, ra + Vector3.up * 0.51f, Quaternion.LookRotation(t), new Vector3(0.06f, 1.02f, 0.06f), iron, false);
                        railOpen = false;
                        continue;
                    }
                    Rail(g, ra, rb, true, false);
                    railOpen = true;
                }
            }

            Run(pts, true, "PASEO_ANILLO", (p, t) => new Vector3(-t.z, 0, t.x) * leftIsTown);
            Vector3 anteC = Vector3.zero;
            if (ante != null) { foreach (JArray q in ante) anteC += new Vector3((float)q[0], 0, (float)q[1]); anteC /= ante.Count; }
            int k = 0;
            foreach (JObject sp in spurs)
            {
                var sPts = (JArray)sp["points"]; var tops = (JArray)sp["tops"];
                var line = sPts.Select((p, i) => (pos: new Vector3((float)p[0], (float)tops[i], (float)p[2]), gap: false, abut: false)).ToList();
                // the forecourt side is the "town" side of an arm: railing there, stone parapet towards the sea
                Run(line, false, $"PASEO_ESPIGON_{k++}", (p, t) => { var l = new Vector3(-t.z, 0, t.x); return Vector3.Dot(anteC - p, l) > 0 ? l : -l; });
            }

            // cubos: round lookouts flush with the deck, parapet ring towards the sea
            foreach (JObject tw in towers)
            {
                var p = new Vector3((float)tw["pos"][0], 0, (float)tw["pos"][1]);
                float top = (float)tw["top"];
                var cg = new GameObject($"CUBO_MIRADOR_{tw["role"]}").transform;
                cg.SetParent(parent, false);
                Identity(cg.gameObject, cg.name, "PublicSpace:mirador", "cubo de la muralla convertido en mirador");
                var c = Cylinder();
                c.name = "CUBO";
                c.transform.SetParent(cg, false);
                c.transform.position = new Vector3(p.x, (top - 0.3f + baseY) / 2f, p.z);
                c.transform.localScale = new Vector3(6.6f, (top - 0.3f - baseY) / 2f, 6.6f);
                c.GetComponent<MeshRenderer>().sharedMaterial = body;
                c.isStatic = true;
                var disk = Cylinder();
                disk.name = "SUELO_MIRADOR";
                disk.transform.SetParent(cg, false);
                disk.transform.position = new Vector3(p.x, top - 0.15f, p.z);
                disk.transform.localScale = new Vector3(6.7f, 0.15f, 6.7f);
                disk.GetComponent<MeshRenderer>().sharedMaterial = deckMat;
                disk.isStatic = true;
                // nearest deck point gives the side the walk arrives from: no parapet there
                var near = pts.OrderBy(q => (new Vector2(q.pos.x, q.pos.z) - new Vector2(p.x, p.z)).sqrMagnitude).First().pos;
                var toTown = new Vector3(near.x - p.x, 0, near.z - p.z);
                int ni = pts.FindIndex(q => q.pos == near);
                var tt = new Vector3(pts[(ni + 1) % pts.Count].pos.x - near.x, 0, pts[(ni + 1) % pts.Count].pos.z - near.z).normalized;
                var townDir = new Vector3(-tt.z, 0, tt.x) * leftIsTown;
                for (int s = 0; s < 12; s++)
                {
                    float ang = s * 30f * Mathf.Deg2Rad;
                    var dirOut = new Vector3(Mathf.Cos(ang), 0, Mathf.Sin(ang));
                    if (Vector3.Dot(dirOut, -townDir) * 3.05f < half + 0.25f) continue;   // only the bulge beyond the deck's sea edge
                    var tang = Vector3.Cross(Vector3.up, dirOut);
                    float chord = 2f * 3.05f * Mathf.Sin(15f * Mathf.Deg2Rad) + 0.04f;
                    Box("PARAPETO_CUBO", cg, new Vector3(p.x, top + 0.45f, p.z) + dirOut * 3.05f, Quaternion.LookRotation(tang), new Vector3(0.5f, 0.9f, chord), cheek, true);
                    Box("ALBARDILLA", cg, new Vector3(p.x, top + 0.94f, p.z) + dirOut * 3.05f, Quaternion.LookRotation(tang), new Vector3(0.62f, 0.08f, chord), coping, false);
                }
            }

            // stairs up from the inner streets: a landing beside the deck and the flight down along the wall
            int si = 0;
            foreach (JObject st in paseo["stairs"])
            {
                var landing = new Vector3((float)st["landing"][0], (float)st["landing"][1], (float)st["landing"][2]);
                var dir = new Vector3((float)st["dir"][0], 0, (float)st["dir"][1]).normalized;
                float lowY = (float)st["low"];
                Box($"RELLANO_{si}", parent, new Vector3(landing.x, (landing.y + lowY - 0.4f) / 2f, landing.z), Quaternion.LookRotation(dir),
                    new Vector3(2.3f, landing.y - (lowY - 0.4f), 1.4f), stepMat, true);
                Stairs($"ESCALERA_PASEO_{si++}", parent, new Vector3((float)st["top"][0], (float)st["top"][1], (float)st["top"][2]), dir, (float)st["width"], lowY, stepMat, cheek);
            }
        }

        /// <summary>Garden walls closing the street edge between facades (yards, corrals, huertas behind): mamposteria
        /// 2 m high with a sandstone coping, following the ground, with a timber gate in the longer runs.</summary>
        static void BuildTapias(JArray tapias, Transform parent)
        {
            var wall = EnvKit.Mat("ENV_Mason_Mamposteria_Arenisca");
            var cap = EnvKit.Mat("ENV_Mason_Silleria_Arenisca");
            var wood = EnvKit.Mat("ENV_Joinery_Chestnut");
            const float H = 2.0f, Th = 0.45f;
            int k = 0;
            foreach (JObject t in tapias)
            {
                var pts = ((JArray)t["pts"]).Select(q => new Vector3((float)q[0], (float)q[1], (float)q[2])).ToList();
                var g = new GameObject($"TAPIA_{k++:000}").transform;
                g.SetParent(parent, false);
                Identity(g.gameObject, g.name, "Boundary:tapia", "tapia de patio/huerta en la línea de calle");
                bool gate = (bool?)t["gate"] == true;
                int gi = pts.Count / 2;
                for (int i = 0; i + 1 < pts.Count; i++)
                {
                    var a = pts[i]; var b = pts[i + 1];
                    var d = new Vector3(b.x - a.x, 0, b.z - a.z);
                    float len = d.magnitude;
                    if (len < 0.05f) continue;
                    var rot = Quaternion.LookRotation(d / len);
                    var mid = (a + b) / 2f;
                    float y0 = Mathf.Min(a.y, b.y) - 0.3f;
                    if (gate && i == gi)
                    {
                        // portilla: a plank gate between two stone posts
                        Box("PORTILLA", g, new Vector3(mid.x, y0 + 0.3f + 0.95f, mid.z), rot, new Vector3(0.07f, 1.9f, len - 0.1f), wood, true);
                        Box("DINTEL", g, new Vector3(mid.x, y0 + H + 0.35f, mid.z), rot, new Vector3(Th + 0.1f, 0.12f, len + 0.3f), cap, false);
                        continue;
                    }
                    float top = Mathf.Max(a.y, b.y) + H;
                    Box("MURO", g, new Vector3(mid.x, (y0 + top) / 2f, mid.z), rot, new Vector3(Th, top - y0, len + 0.04f), wall, true);
                    Box("ALBARDILLA", g, new Vector3(mid.x, top + 0.05f, mid.z), rot, new Vector3(Th + 0.1f, 0.1f, len + 0.04f), cap, false);
                }
            }
        }

        /// <summary>Stairs listed in the seed outside the terraces (the port gate down to the quay).</summary>
        static void BuildStairsExtra(JArray stairs, Transform parent)
        {
            var step = EnvKit.Mat("ENV_Mason_Silleria_Gris");
            var cheek = EnvKit.Mat("ENV_Mason_Silleria_Arenisca");
            foreach (JObject st in stairs)
                Stairs((string)st["id"], parent, new Vector3((float)st["top"][0], (float)st["top"][1], (float)st["top"][2]),
                    new Vector3((float)st["dir"][0], 0, (float)st["dir"][1]), (float)st["width"], (float)st["low"], step, cheek);
        }

        /// <summary>The timber pier at the end of the antepuerto: plank decks on posts standing in the water.</summary>
        static void BuildPier(JObject pier, Transform parent)
        {
            var plank = EnvKit.Mat("ENV_Joinery_Chestnut");
            var post = EnvKit.Mat("ENV_Joinery_Walnut");
            float y = (float)pier["y"], bottom = (float)pier["post_bottom"];
            Identity(parent.gameObject, "MUELLE_MADERA", "Quay", "muelle de madera en U del antepuerto");
            int k = 0;
            foreach (JArray d in pier["decks"])
            {
                float x0 = (float)d[0], z0 = (float)d[1], x1 = (float)d[2], z1 = (float)d[3];
                Box($"TABLERO_{k++}", parent, new Vector3((x0 + x1) / 2f, y - 0.15f, (z0 + z1) / 2f), Quaternion.identity, new Vector3(x1 - x0, 0.3f, z1 - z0), plank, true);
                for (float x = x0 + 0.3f; x <= x1 - 0.2f; x += 2.5f)
                for (float z = z0 + 0.3f; z <= z1 - 0.2f; z += 2.5f)
                {
                    bool edge = x < x0 + 0.5f || x > x1 - 2.6f || z < z0 + 0.5f || z > z1 - 2.6f;
                    if (!edge) continue;
                    Box("PILOTE", parent, new Vector3(x, (y - 0.3f + bottom) / 2f, z), Quaternion.identity, new Vector3(0.32f, y - 0.3f - bottom, 0.32f), post, false);
                }
            }
        }

        // ---------------------------------------------------------------- El Alto / Finca

        /// <summary>Retaining walls (mamposteria with a sandstone coping and parapet) on the free arcs of each terrace
        /// ring, and escalinatas (risers &lt;= 0.15 m, 0.32 m treads) going down from the upper level to the lower one.</summary>
        static void BuildTerraces(JArray terraces, Transform parent)
        {
            var wallMat = EnvKit.Mat("ENV_Mason_Mamposteria_Arenisca");
            var capMat = EnvKit.Mat("ENV_Mason_Silleria_Arenisca");
            var stepMat = EnvKit.Mat("ENV_Mason_Silleria_Gris");
            int t = 0;
            foreach (JObject ring in terraces)
            {
                var g = new GameObject($"TERRACE_{t++}_R{(float)ring["radius"]:0.#}").transform;
                g.SetParent(parent, false);
                Identity(g.gameObject, g.name, "Terrace", $"El Alto ring r={(float)ring["radius"]} {(float)ring["low"]}->{(float)ring["high"]} m");
                var c = new Vector3((float)ring["center"][0], 0, (float)ring["center"][1]);
                float low = (float)ring["low"], high = (float)ring["high"];
                const float Thick = 1.1f, Parapet = 0.95f;
                int k = 0;
                foreach (JArray seg in ring["walls"])
                {
                    var pts = seg.Select(p => new Vector3((float)p[0], 0, (float)p[1])).ToList();
                    for (int i = 0; i + 1 < pts.Count; i++)
                    {
                        var a = pts[i]; var b = pts[i + 1];
                        var mid = (a + b) / 2f;
                        var dir = b - a; float len = dir.magnitude;
                        if (len < 0.05f) continue;
                        var outward = (mid - c).normalized;
                        var center = mid + outward * (Thick / 2f - 0.2f);
                        Box($"MURO_{k++:000}", g, new Vector3(center.x, (low - 0.6f + high + Parapet) / 2f, center.z), Quaternion.LookRotation(dir / len),
                            new Vector3(Thick, high + Parapet - (low - 0.6f), len + 0.12f), wallMat, true);
                        Box("ALBARDILLA", g, new Vector3(center.x, high + Parapet + 0.06f, center.z), Quaternion.LookRotation(dir / len),
                            new Vector3(Thick + 0.12f, 0.12f, len + 0.12f), capMat, false);
                    }
                }
                int s = 0;
                foreach (JObject st in ring["stairs"])
                    Stairs($"ESCALINATA_{s++}", g, new Vector3((float)st["top"][0], (float)st["top"][1], (float)st["top"][2]),
                        new Vector3((float)st["dir"][0], 0, (float)st["dir"][1]), (float)st["width"], (float)st["low"], stepMat, capMat);
            }
        }

        static void Stairs(string name, Transform parent, Vector3 top, Vector3 dir, float width, float low, Material step, Material cheek)
        {
            var g = new GameObject(name).transform;
            g.SetParent(parent, false);
            Identity(g.gameObject, name, "Stairs", $"{top.y:0.0}->{low:0.0} m");
            dir = dir.normalized;
            float drop = top.y - low;
            int n = Mathf.CeilToInt(drop / 0.15f);
            float rise = drop / n;
            var rot = Quaternion.LookRotation(dir);
            for (int i = 0; i < n - 1; i++)
            {
                float y = top.y - (i + 1) * rise;
                var p = top + dir * ((i + 0.5f) * 0.32f);
                Box($"PELDANO_{i:00}", g, new Vector3(p.x, (y + low - 0.4f) / 2f, p.z), rot, new Vector3(width, y - (low - 0.4f), 0.34f), step, true);
            }
            float run = (n - 1) * 0.32f;
            var side = Vector3.Cross(Vector3.up, dir);
            float pitch = Mathf.Atan2(drop, run) * Mathf.Rad2Deg, slope = Mathf.Sqrt(run * run + drop * drop);
            foreach (int sgn in new[] { -1, 1 })
            {
                // sloped stone balustrade following the flight on each side
                var a = top + side * sgn * (width / 2f + 0.18f) + dir * (run / 2f);
                Box("PRETIL_ESCALERA", g, new Vector3(a.x, (top.y + low) / 2f + 0.45f, a.z), rot * Quaternion.Euler(pitch, 0, 0), new Vector3(0.36f, 0.9f, slope), cheek, true);
            }
        }

        /// <summary>The Finca del Cacique: walled casona compound with three ways in — the main gate on the street side,
        /// a collapsed stretch of the back wall, and the orujo cellar hatch outside the side wall facing the river wall.</summary>
        static void BuildFinca(JObject f, Transform parent)
        {
            var wallMat = EnvKit.Mat("ENV_Mason_Mamposteria_Gris");
            var capMat = EnvKit.Mat("ENV_Mason_Silleria_Gris");
            var wood = EnvKit.Mat("ENV_Joinery_Walnut");
            float y = (float)f["y"], h = (float)f["wall_height"], th = (float)f["wall_thickness"];
            Identity(parent.gameObject, "P_FINCA", "SemanticBuilding:QUEST:finca", "Finca del Cacique: portón, muro derrumbado, bodegas de orujo");
            var rng = new System.Random(1999);
            var fincaC = Vector3.zero;
            foreach (JArray tp in f["towers"]) fincaC += new Vector3((float)tp[0], 0, (float)tp[1]);
            fincaC /= ((JArray)f["towers"]).Count;
            foreach (JObject e in f["edges"])
            {
                var a = new Vector3((float)e["a"][0], 0, (float)e["a"][1]);
                var b = new Vector3((float)e["b"][0], 0, (float)e["b"][1]);
                var dir = (b - a); float len = dir.magnitude; dir /= len;
                var rot = Quaternion.LookRotation(dir);
                string role = (string)e["role"];
                void Wall(float from, float to, float height, string nm)
                {
                    if (to - from < 0.1f) return;
                    var m = a + dir * ((from + to) / 2f);
                    Box(nm, parent, new Vector3(m.x, y - 1.2f + (height + 1.2f) / 2f, m.z), rot, new Vector3(th, height + 1.2f, to - from), wallMat, true);
                    Box("ALBARDILLA", parent, new Vector3(m.x, y + height + 0.05f, m.z), rot, new Vector3(th + 0.1f, 0.1f, to - from), capMat, false);
                }
                float c0 = 1.7f, c1 = len - 1.7f;     // clear of the corner cubos
                if (role == "porton")
                {
                    float w = (float)f["porton_width"], m0 = len / 2f - w / 2f, m1 = len / 2f + w / 2f;
                    Wall(c0, m0 - 0.45f, h, "MURO_FINCA");
                    Wall(m1 + 0.45f, c1, h, "MURO_FINCA");
                    // portalada montañesa: ashlar jambs rising above the wall, a lintel with a cornice, the family's
                    // escudo on a small pediment, two plank leaves standing open into the patio
                    var ashlar = EnvKit.Mat("ENV_Mason_Silleria_Arenisca");
                    var outN = Vector3.Cross(Vector3.up, dir);
                    var gm = a + dir * (len / 2f);
                    if (Vector3.Dot(outN, gm - fincaC) < 0) outN = -outN;
                    foreach (float u in new[] { m0 - 0.5f, m1 + 0.5f })
                    {
                        var p = a + dir * u;
                        Box("JAMBA_PORTALADA", parent, new Vector3(p.x, y - 1.0f + (h + 2.0f) / 2f, p.z), rot, new Vector3(1.1f, h + 2.0f, 1.0f), ashlar, true);
                        Box("PINACULO", parent, new Vector3(p.x, y + h + 1.25f, p.z), rot, new Vector3(0.5f, 0.5f, 0.5f), ashlar, false);
                    }
                    var arch = Box("DINTEL_PORTALADA", parent, new Vector3(gm.x, y + h + 0.3f, gm.z), rot, new Vector3(1.0f, 0.6f, w + 2.2f), ashlar, true);
                    Box("CORNISA", parent, new Vector3(gm.x, y + h + 0.66f, gm.z), rot, new Vector3(1.25f, 0.12f, w + 2.5f), capMat, false);
                    Box("FRONTON", parent, new Vector3(gm.x, y + h + 1.3f, gm.z), rot, new Vector3(0.7f, 1.2f, 1.9f), ashlar, false);
                    var esc = EnvKit.Place("ENV_Escudo", parent, new Vector3(gm.x, y + h + 1.25f, gm.z) + outN * 0.36f, 0, Vector3.one * 1.4f);
                    esc.transform.rotation = Quaternion.LookRotation(outN);
                    foreach (int sgn in new[] { -1, 1 })
                    {
                        // each leaf hinged at its jamb, swung 80 degrees into the patio
                        var hinge = gm + dir * (sgn * w / 2f) - outN * 0.1f;
                        var leafDir = (-dir * sgn * Mathf.Cos(80f * Mathf.Deg2Rad) - outN * Mathf.Sin(80f * Mathf.Deg2Rad)).normalized;
                        var leafC = hinge + leafDir * (w / 4f);
                        Box("HOJA_PORTALADA (abierta)", parent, leafC + Vector3.up * (y + 1.35f), Quaternion.LookRotation(leafDir), new Vector3(0.1f, 2.7f, w / 2f - 0.05f), wood, true);
                    }
                    Identity(arch, "FINCA_PORTALADA", "Access:PUB-H", "portalada con escudo: portón principal (abierto de día)");
                }
                else if (role == "derrumbe")
                {
                    float w = (float)f["derrumbe_width"], m0 = len * 0.55f - w / 2f, m1 = m0 + w;
                    Wall(c0, m0, h, "MURO_FINCA");
                    Wall(m1, c1, h, "MURO_FINCA");
                    for (float u = m0; u < m1 - 0.2f; u += 0.75f)
                        Wall(u, u + 0.75f, 0.5f + (float)rng.NextDouble() * 0.9f, "MURO_DERRUMBADO");
                    var n = Vector3.Cross(Vector3.up, dir);
                    for (int i = 0; i < 9; i++)
                    {
                        var p = a + dir * (m0 + (float)rng.NextDouble() * w) + n * (((float)rng.NextDouble() - 0.5f) * 3.2f);
                        float sz = 0.35f + (float)rng.NextDouble() * 0.45f;
                        Box("CASCOTE", parent, new Vector3(p.x, y + sz * 0.3f, p.z), Quaternion.Euler((float)rng.NextDouble() * 40, (float)rng.NextDouble() * 360, (float)rng.NextDouble() * 40),
                            Vector3.one * sz, wallMat, false);
                    }
                    var mark = new GameObject("DERRUMBE_ACCESS");
                    mark.transform.SetParent(parent, false);
                    mark.transform.SetPositionAndRotation(a + dir * ((m0 + m1) / 2f) + Vector3.up * y, rot);
                    Identity(mark, "FINCA_DERRUMBE", "Access:PRV-furtivo", "muro derrumbado trasero: entrada furtiva saltando cascotes");
                }
                else Wall(c0, c1, h, "MURO_FINCA");
            }
            foreach (JArray tp in f["towers"])
            {
                // the cerca's corners: square ashlar pillars with a capping stone, not round towers
                var cp = new Vector3((float)tp[0], 0, (float)tp[1]);
                var toC = fincaC - cp;
                var r0 = Quaternion.LookRotation(toC.normalized);
                Box("PILAR_ESQUINA", parent, new Vector3(cp.x, y - 1.0f + (h + 1.5f) / 2f, cp.z) + toC.normalized * 0.2f, r0, new Vector3(1.2f, h + 1.5f, 1.2f), EnvKit.Mat("ENV_Mason_Silleria_Arenisca"), true);
                Box("REMATE", parent, new Vector3(cp.x, y + h + 0.6f, cp.z) + toC.normalized * 0.2f, r0, new Vector3(1.4f, 0.2f, 1.4f), capMat, false);
            }
            // orujo cellars: a stone hatch with a timber trapdoor against the side wall, outside the compound
            var bd = (JObject)f["bodega"];
            var bp = new Vector3((float)bd["pos"][0], (float)bd["y"], (float)bd["pos"][1]);
            var bn = new Vector3((float)bd["facing"][0], 0, (float)bd["facing"][1]).normalized;
            var hatch = Box("BODEGA_ORUJO_BROCAL", parent, bp + Vector3.up * 0.35f, Quaternion.LookRotation(bn), new Vector3(2.2f, 0.7f, 1.8f), capMat, true);
            Box("BODEGA_ORUJO_TRAMPILLA", parent, bp + Vector3.up * 0.74f, Quaternion.LookRotation(bn) * Quaternion.Euler(-12f, 0, 0), new Vector3(1.7f, 0.08f, 1.4f), wood, false);
            Identity(hatch, "FINCA_BODEGA", "Access:PROG", "acceso furtivo por las bodegas de orujo (cerrado hasta misión)");
        }

        /// <summary>Cylinder primitive with a mesh collider: the primitive's capsule collider would put an invisible dome
        /// of the cylinder's radius on top of every cubo and lookout floor.</summary>
        static GameObject Cylinder()
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            UnityEngine.Object.DestroyImmediate(go.GetComponent<Collider>());
            go.AddComponent<MeshCollider>().sharedMesh = go.GetComponent<MeshFilter>().sharedMesh;
            return go;
        }

        static GameObject Box(string name, Transform parent, Vector3 pos, Quaternion rot, Vector3 size, Material mat, bool collider)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = name;
            go.transform.SetParent(parent, false);
            go.transform.SetPositionAndRotation(pos, rot);
            go.transform.localScale = size;
            if (!collider) UnityEngine.Object.DestroyImmediate(go.GetComponent<BoxCollider>());
            if (mat) go.GetComponent<MeshRenderer>().sharedMaterial = mat;
            go.isStatic = true;
            return go;
        }

        /// <summary>The railings as a smith fits them: a bar that runs into masonry (a cubo, its lookout floor, a stair's
        /// pretil, the adarve, a parapet) stops at the stone face and is fixed there; a post standing in masonry goes.
        /// Owner walk 2026-10-02: "sigue habiendo colisiones ... la barandilla de la foto".</summary>
        static int TrimRailings(Transform root)
        {
            Physics.SyncTransforms();
            int cut = 0;
            bool Masonry(Collider c) => c.name != "BARANDILLA" && c.name != "POSTE" && !c.name.StartsWith("TERRAIN") && !c.name.StartsWith("RIVERBED");
            foreach (var post in root.GetComponentsInChildren<Transform>(true).Where(t => t.name == "POSTE").ToList())
            {
                var half = post.lossyScale * 0.5f - new Vector3(0.01f, 0.06f, 0.01f);
                if (Physics.OverlapBox(post.position, half, post.rotation).Any(Masonry)) { UnityEngine.Object.DestroyImmediate(post.gameObject); cut++; }
            }
            foreach (var bar in root.GetComponentsInChildren<Transform>(true).Where(t => t.name == "BARANDILLA").ToList())
            {
                float L = bar.lossyScale.z;
                var half = new Vector3(bar.lossyScale.x * 0.5f - 0.005f, bar.lossyScale.y * 0.5f - 0.005f, 0.025f);
                int n = Mathf.Max(2, Mathf.CeilToInt(L / 0.05f));
                var free = new bool[n];
                bool any = false;
                for (int k = 0; k < n; k++)
                {
                    float t = -L / 2f + (k + 0.5f) * L / n;
                    free[k] = !Physics.OverlapBox(bar.position + bar.forward * t, half, bar.rotation).Any(Masonry);
                    any |= !free[k];
                }
                if (!any) continue;
                var mat = bar.GetComponent<MeshRenderer>().sharedMaterial;
                // the free runs of the bar become bars of their own, ending at the stone faces
                for (int k = 0; k < n;)
                {
                    if (!free[k]) { k++; continue; }
                    int k0 = k;
                    while (k < n && free[k]) k++;
                    float t0 = -L / 2f + k0 * L / n, t1 = -L / 2f + k * L / n;
                    if (t1 - t0 < 0.15f) continue;
                    var piece = Box("BARANDILLA", bar.parent, bar.position + bar.forward * ((t0 + t1) / 2f), bar.rotation,
                                    new Vector3(bar.lossyScale.x, bar.lossyScale.y, t1 - t0), mat, true);
                }
                UnityEngine.Object.DestroyImmediate(bar.gameObject);
                cut++;
            }
            Physics.SyncTransforms();
            return cut;
        }

        // ---------------------------------------------------------------- helpers

        static long Key(int i, int j) => ((long)i << 32) | (uint)j;

        static Transform Group(GameObject root, string name)
        {
            var g = new GameObject(name);
            g.transform.SetParent(root.transform, false);
            return g.transform;
        }

        static GameObject MeshObject(string name, Transform parent, Mesh mesh, Material mat, bool collider)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            mesh.name = name;
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var mr = go.AddComponent<MeshRenderer>();
            if (mat) mr.sharedMaterial = mat;
            if (collider) go.AddComponent<MeshCollider>().sharedMesh = mesh;
            go.isStatic = true;
            return go;
        }

        static void Identity(GameObject go, string id, string kind, string source, Vector3[] outline = null)
        {
            var c = go.GetComponent<JDSpatialIdentity>() ?? go.AddComponent<JDSpatialIdentity>();
            c.stableId = id; c.kind = kind; c.sourceId = source; c.referenceOutline = outline ?? new Vector3[0];
        }

        sealed class MB
        {
            readonly List<Vector3> v = new List<Vector3>();
            readonly List<Vector2> uv = new List<Vector2>();
            readonly List<int> t = new List<int>();

            public void Quad(Vector3 a, Vector3 b, Vector3 c, Vector3 d, bool worldUv)
            {
                int i = v.Count;
                v.Add(a); v.Add(b); v.Add(c); v.Add(d);
                foreach (var p in new[] { a, b, c, d }) uv.Add(worldUv ? new Vector2(p.x, p.z) * 0.25f : Vector2.zero);
                t.Add(i); t.Add(i + 1); t.Add(i + 2); t.Add(i); t.Add(i + 2); t.Add(i + 3);
            }

            public void QuadUV(Vector3 a, Vector3 b, Vector3 c, Vector3 d)
            {
                // a = top start, b = toe start, c = toe end, d = top end
                int i = v.Count;
                v.Add(a); v.Add(b); v.Add(c); v.Add(d);
                float u0 = (a.x + a.z) * 0.25f, u1 = (d.x + d.z) * 0.25f, dv = Vector3.Distance(a, b) * 0.25f;
                uv.Add(new Vector2(u0, 0)); uv.Add(new Vector2(u0, -dv)); uv.Add(new Vector2(u1, -dv)); uv.Add(new Vector2(u1, 0));
                t.Add(i); t.Add(i + 1); t.Add(i + 2); t.Add(i); t.Add(i + 2); t.Add(i + 3);
            }

            public void Skirt(Vector3 a, Vector3 b, float bottom)
            {
                int i = v.Count;
                var a2 = new Vector3(a.x, bottom, a.z); var b2 = new Vector3(b.x, bottom, b.z);
                v.Add(a); v.Add(a2); v.Add(b2); v.Add(b);
                float len = Vector3.Distance(a, b);
                uv.Add(new Vector2(0, a.y) * 0.25f); uv.Add(new Vector2(0, bottom) * 0.25f); uv.Add(new Vector2(len, bottom) * 0.25f); uv.Add(new Vector2(len, b.y) * 0.25f);
                t.Add(i); t.Add(i + 1); t.Add(i + 2); t.Add(i); t.Add(i + 2); t.Add(i + 3);
            }

            public Mesh ToMesh()
            {
                var m = new Mesh { indexFormat = v.Count > 65000 ? IndexFormat.UInt32 : IndexFormat.UInt16 };
                m.SetVertices(v); m.SetUVs(0, uv); m.SetTriangles(t, 0);
                m.RecalculateNormals(); m.RecalculateBounds();
                return m;
            }
        }
    }
}

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using JuegoDef.Env;
using Newtonsoft.Json.Linq;
using Unity.AI.Navigation;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace JuegoDef.City
{
    /// <summary>
    /// WP-CITY-SKELETON-00 one-shot helper: materialises the Mapa F1 blockout seed
    /// (Docs/evidence/WP-CITY-SKELETON-00/city_blockout_seed.json) into persistent authored scenes:
    /// CITY_Base (terrain, water, public network, layer links, open spaces, edge guards, nodes, NavMesh, GC2 player)
    /// plus one scene per sector holding its semantic-building masses and door markers.
    /// It makes no layout decisions of its own and refuses to run once CITY_Base exists: from then on the scenes are
    /// edited by hand and are the spatial authority (see CityAuthoredGuard).
    /// </summary>
    public static class CityBlockoutSeed
    {
        public const string SceneDir = "Assets/JuegoDef/Scenes/CITY";
        public const string BaseScene = SceneDir + "/CITY_Base.unity";
        const string OwnedDir = "Assets/JuegoDef/Authored/CITY/Blockout";
        static readonly (string id, string name)[] Sectors =
        {
            ("S1", "B0"), ("S2", "MuelleMercado"), ("S3", "CascoBajo"), ("S4", "CascoAlto"), ("S5", "Viviendas"),
            ("S6", "Talleres"), ("S7", "Arrabal"), ("S8", "CostaEste"), ("S9", "Molinos"), ("S10", "Afueras"),
        };

        public static string SectorScenePath(string id) =>
            $"{SceneDir}/CITY_{id}_{Sectors.First(s => s.id == id).name}.unity";

        public static IEnumerable<string> AllScenePaths() => new[] { BaseScene }.Concat(Sectors.Select(s => SectorScenePath(s.id)));

        static string SeedFile => Path.GetFullPath(Path.Combine(Application.dataPath, "../../../Docs/evidence/WP-CITY-SKELETON-00/city_blockout_seed.json"));

        [MenuItem("JuegoDef/CITY/Seed Mapa F1 blockout (one-shot)")]
        static void Menu() => Debug.Log(Seed());

        public static string Seed()
        {
            if (AssetDatabase.LoadAssetAtPath<SceneAsset>(BaseScene) != null || File.Exists(BaseScene))
                throw new InvalidOperationException("JD_CITY_ALREADY_SEEDED: the authored CITY scenes own the layout; the seed is one-shot.");
            var doc = JObject.Parse(File.ReadAllText(SeedFile));
            Directory.CreateDirectory(SceneDir);
            Directory.CreateDirectory(OwnedDir);
            var m = new Mats();

            var baseScene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = new GameObject("CITY_Base");
            Identity(root, "CITY_Base", "AuthoredScene", "Mapa F1 blockout — base (WP-CITY-SKELETON-00)");
            var sun = new GameObject("Sun").AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.intensity = 1.25f;
            sun.shadows = LightShadows.Soft;
            sun.transform.rotation = Quaternion.Euler(48f, -35f, 0f);
            sun.transform.SetParent(root.transform);

            var terrain = Group(root, "TERRAIN");
            BuildTerrain((JObject)doc["terrain"], terrain, m);
            var water = Group(root, "WATER");
            BuildWater(doc, water, m);
            var guards = Group(root, "EDGE_GUARDS");
            BuildGuards((JArray)doc["guards"], guards, m);
            var zones = Group(root, "ZONES");
            foreach (JObject z in doc["zones"])
            {
                int k = 0;
                foreach (JArray poly in z["polygons"])
                {
                    var go = new GameObject($"ZONE_{z["id"]}_{k++}");
                    go.transform.SetParent(zones, false);
                    Identity(go, $"ZONE_{z["id"]}", "Zone", (string)z["id"],
                        poly.Select(p => new Vector3((float)p[0], 0f, (float)p[1])).ToArray());
                }
            }
            var streets = Group(root, "PUBLIC_NETWORK");
            foreach (JObject s in doc["streets"]) BuildStreet(s, streets, m);
            var opens = Group(root, "OPEN_SPACES");
            foreach (JObject o in doc["openSpaces"]) BuildOpenSpace(o, opens, m);
            var links = Group(root, "LAYER_LINKS");
            foreach (JObject k in doc["layerLinks"]) BuildLink(k, links, m);
            var seams = Group(root, "SEAMS");
            foreach (JObject s in doc["seams"]) BuildSeam(s, seams, m);
            var nodes = Group(root, "NODES");
            foreach (JObject n in doc["nodes"])
            {
                var go = new GameObject($"NODE_{n["id"]}");
                go.transform.SetParent(nodes, false);
                go.transform.position = new Vector3((float)n["x"], (float)n["y"], (float)n["z"]);
                Identity(go, (string)n["id"], "Node", $"{n["zone"]}|{n["role"]}|anchor={n["anchorOf"]}");
            }
            var spawn = (JArray)doc["spawn"];
            EnvStreet.BringPlayer(new JObject { ["_spawnWorld"] = new JArray((float)spawn[0], (float)spawn[1] + 0.06f, (float)spawn[2]) });
            EditorSceneManager.SaveScene(baseScene, BaseScene);

            // sector scenes: semantic-building masses + doors
            var sectorScenes = new Dictionary<string, Scene>();
            var sectorRoots = new Dictionary<string, Transform>();
            foreach (var (id, name) in Sectors)
            {
                var sc = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive);
                var r = new GameObject($"CITY_{id}_{name}");
                SceneManager.MoveGameObjectToScene(r, sc);
                Identity(r, $"CITY_{id}", "AuthoredScene", $"Mapa F1 blockout — sector {id} {name}");
                EditorSceneManager.SaveScene(sc, SectorScenePath(id));
                sectorScenes[id] = sc;
                sectorRoots[id] = r.transform;
            }
            int placed = 0;
            foreach (JObject b in doc["buildings"])
            {
                var sector = ((string)b["sector"]).Split('/')[0];
                var go = BuildBuilding(b, m);
                SceneManager.MoveGameObjectToScene(go, sectorScenes[sector]);
                go.transform.SetParent(sectorRoots[sector], true);
                placed++;
            }
            foreach (var (id, _) in Sectors) EditorSceneManager.SaveScene(sectorScenes[id], SectorScenePath(id));

            // NavMesh over every loaded scene (buildings are obstacles), saved next to the base scene
            SceneManager.SetActiveScene(baseScene);
            var nav = new GameObject("NAVMESH");
            nav.transform.SetParent(root.transform);
            var surface = nav.AddComponent<NavMeshSurface>();
            surface.collectObjects = CollectObjects.All;
            surface.useGeometry = NavMeshCollectGeometry.PhysicsColliders;
            surface.BuildNavMesh();
            var navPath = $"{OwnedDir}/CITY_NavMesh.asset";
            AssetDatabase.CreateAsset(surface.navMeshData, navPath);
            surface.navMeshData = AssetDatabase.LoadAssetAtPath<NavMeshData>(navPath);
            EditorSceneManager.MarkSceneDirty(baseScene);
            EditorSceneManager.SaveScene(baseScene, BaseScene);
            AssetDatabase.SaveAssets();
            var tri = NavMesh.CalculateTriangulation();
            return $"JD_CITY_SEEDED scenes={1 + Sectors.Length} buildings={placed} streets={doc["streets"].Count()} links={doc["layerLinks"].Count()} navmesh_tris={tri.indices.Length / 3}";
        }

        [MenuItem("JuegoDef/CITY/Open Mapa F1 (base + all sectors)")]
        public static void OpenAll()
        {
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            EditorSceneManager.OpenScene(BaseScene, OpenSceneMode.Single);
            foreach (var (id, _) in Sectors) EditorSceneManager.OpenScene(SectorScenePath(id), OpenSceneMode.Additive);
            SceneManager.SetActiveScene(SceneManager.GetSceneByPath(BaseScene));
        }

        // ---------------------------------------------------------------- terrain / water / guards

        static void BuildTerrain(JObject t, Transform parent, Mats m)
        {
            float ox = (float)t["origin"][0], oz = (float)t["origin"][1], cell = (float)t["cell"];
            var h = new Dictionary<long, (float y, int zone)>();
            foreach (JArray c in t["cells"]) h[Key((int)c[0], (int)c[1])] = ((float)c[2], (int)c[3]);
            float Corner(int ci, int cj)
            {
                float sum = 0; int n = 0;
                for (int di = -1; di <= 0; di++)
                for (int dj = -1; dj <= 0; dj++)
                    if (h.TryGetValue(Key(ci + di, cj + dj), out var v)) { sum += v.y; n++; }
                return n > 0 ? sum / n : 0f;
            }
            const int Chunk = 48;
            var builders = new Dictionary<(int zone, int cx, int cz), MeshBuilder>();
            foreach (var kv in h)
            {
                int i = (int)(kv.Key >> 32), j = (int)(kv.Key & 0xffffffff);
                var key = (kv.Value.zone, i / Chunk, j / Chunk);
                if (!builders.TryGetValue(key, out var mb)) builders[key] = mb = new MeshBuilder();
                Vector3 V(int ci, int cj) => new Vector3(ox + ci * cell, Corner(ci, cj), oz + cj * cell);
                var a = V(i, j); var b = V(i + 1, j); var c = V(i + 1, j + 1); var d = V(i, j + 1);
                mb.Quad(a, d, c, b);
                // skirts on sides without a neighbouring land cell (water, river, envelope edge)
                if (!h.ContainsKey(Key(i, j - 1))) mb.Skirt(b, a, -2.0f);
                if (!h.ContainsKey(Key(i + 1, j))) mb.Skirt(c, b, -2.0f);
                if (!h.ContainsKey(Key(i, j + 1))) mb.Skirt(d, c, -2.0f);
                if (!h.ContainsKey(Key(i - 1, j))) mb.Skirt(a, d, -2.0f);
            }
            string[] zoneNames = { "CASCO", "MERCADO", "MUELLE", "TALLERES", "VIVIENDAS" };
            foreach (var kv in builders)
                MeshObject($"TERRAIN_{zoneNames[kv.Key.zone]}_{kv.Key.cx}_{kv.Key.cz}", parent, kv.Value.ToMesh(), m.Zone[kv.Key.zone], true);
        }

        static long Key(int i, int j) => ((long)i << 32) | (uint)j;

        static void BuildWater(JObject doc, Transform parent, Mats m)
        {
            var hp = (JArray)doc["harbour"]["polygon"];
            var mb = new MeshBuilder();
            mb.Quad(P(hp[0], 0f), P(hp[3], 0f), P(hp[2], 0f), P(hp[1], 0f));
            MeshObject("HARBOUR_WATER", parent, mb.ToMesh(), m.Water, false);
            var bed = GameObject.CreatePrimitive(PrimitiveType.Cube);
            bed.name = "HARBOUR_SEABED_SAFETY (collider only)";
            bed.transform.SetParent(parent, false);
            bed.transform.position = new Vector3(140f, -2.2f, -40f);
            bed.transform.localScale = new Vector3(600f, 0.4f, 90f);
            UnityEngine.Object.DestroyImmediate(bed.GetComponent<MeshRenderer>());
            var strip = (JArray)doc["riverStrip"];
            var rb = new MeshBuilder();
            for (int i = 0; i + 1 < strip.Count; i++)
            {
                var w0 = V3((JArray)strip[i][0]); var e0 = V3((JArray)strip[i][1]);
                var w1 = V3((JArray)strip[i + 1][0]); var e1 = V3((JArray)strip[i + 1][1]);
                rb.Quad(w0, w1, e1, e0);
            }
            MeshObject("RIVER_WATER", parent, rb.ToMesh(), m.Water, false);
        }

        static void BuildGuards(JArray guards, Transform parent, Mats m)
        {
            var col = new MeshBuilder();
            var curb = new MeshBuilder();
            foreach (JArray g in guards)
                for (int i = 0; i + 1 < g.Count; i++)
                {
                    var a = V3((JArray)g[i]); var b = V3((JArray)g[i + 1]);
                    col.Wall(a + Vector3.down * 0.6f, b + Vector3.down * 0.6f, 1.8f);
                    curb.Wall(a, b, 0.45f);
                }
            var c = MeshObject("EDGE_GUARD_COLLIDERS (no renderer)", parent, col.ToMesh(), null, true);
            UnityEngine.Object.DestroyImmediate(c.GetComponent<MeshRenderer>());
            MeshObject("EDGE_CURBS", parent, curb.ToMesh(), m.Curb, false);
        }

        // ---------------------------------------------------------------- network

        static void BuildStreet(JObject s, Transform parent, Mats m)
        {
            var pts = ((JArray)s["points"]).Select(p => V3((JArray)p)).ToList();
            var cls = (string)s["class"];
            int risers = (int)s["risers"];
            var mesh = cls == "stair" && risers > 0 ? Ribbon(pts, (float)s["width"], 0.05f, risers) : Ribbon(pts, (float)s["width"], 0.05f, 0);
            var mat = cls switch
            {
                "stair" => m.Stair, "commercial" => m.Commercial, "main" => m.Main, "quay" => m.Quay,
                "bridge" => m.Bridge, "passage" => m.Passage, _ => m.Secondary,
            };
            var go = MeshObject($"ST_{s["id"]} {s["name"]}", parent, mesh, mat, true);
            Identity(go, (string)s["id"], $"StreetAxis:{cls}:{s["access"]}", (string)s["name"], pts.ToArray());
        }

        static void BuildOpenSpace(JObject o, Transform parent, Mats m)
        {
            float y = (float)o["y"] + 0.06f;
            var poly = ((JArray)o["polygon"]).Select(p => new Vector3((float)p[0], y, (float)p[1])).ToArray();
            var mb = new MeshBuilder();
            mb.Quad(poly[0], poly[3], poly[2], poly[1]);
            mb.Skirt(poly[1], poly[0], y - 0.6f); mb.Skirt(poly[2], poly[1], y - 0.6f);
            mb.Skirt(poly[3], poly[2], y - 0.6f); mb.Skirt(poly[0], poly[3], y - 0.6f);
            var go = MeshObject($"OS_{o["id"]} {o["name"]}", parent, mb.ToMesh(), m.Plaza, true);
            Identity(go, (string)o["id"], $"OpenSpace:{o["access"]}", (string)o["name"], poly);
        }

        static void BuildLink(JObject k, Transform parent, Mats m)
        {
            var pts = ((JArray)k["points"]).Select(p => V3((JArray)p)).ToList();
            var layer = (string)k["layer"];
            bool walkable = (bool)k["walkable"];
            bool exterior = walkable && (layer == "service" || layer == "garden" || layer == "openspace" || layer == "water");
            float width = exterior ? Mathf.Max((float)k["width"], 1.2f) : 0.25f;
            var mesh = Ribbon(Resample(pts, 2f), width, exterior ? 0.07f : 3.2f, 0);
            var go = MeshObject($"LINK_{k["id"]} [{layer}|{k["access"]}] {k["name"]}", parent, mesh, m.Layer(layer), exterior);
            Identity(go, (string)k["id"], $"LayerLink:{layer}:{k["access"]}:{(walkable ? "walk" : "nowalk")}:{(exterior ? "exterior" : "pending-sector")}",
                $"{k["name"]} | {k["condition"]}", pts.ToArray());
        }

        static void BuildSeam(JObject s, Transform parent, Mats m)
        {
            var pts = ((JArray)s["points"]).Select(p => V3((JArray)p)).ToList();
            var go = MeshObject($"SEAM_{s["id"]} → {s["future"]}", parent, Ribbon(Resample(pts, 3f), (float)s["corridorWidth"], 0.04f, 0), m.Seam, false);
            Identity(go, (string)s["id"], "Seam:reserved-corridor", $"{s["future"]} | cierre: {s["closure"]}", pts.ToArray());
        }

        // ---------------------------------------------------------------- buildings

        static GameObject BuildBuilding(JObject b, Mats m)
        {
            var fp = ((JArray)b["footprint"]).Select(p => new Vector3((float)p[0], 0f, (float)p[1])).ToArray();
            float floorY = (float)b["floorY"], height = (float)b["height"];
            var front = fp[1] - fp[0];
            var depthDir = fp[3] - fp[0];
            var center = (fp[0] + fp[1] + fp[2] + fp[3]) / 4f;
            const float sink = 1.5f;
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = $"BLD_{b["id"]} {b["name"]}";
            go.transform.position = new Vector3(center.x, floorY - sink + (height + sink) / 2f, center.z);
            go.transform.rotation = Quaternion.LookRotation(depthDir.normalized, Vector3.up);
            go.transform.localScale = new Vector3(front.magnitude, height + sink, depthDir.magnitude);
            go.GetComponent<MeshRenderer>().sharedMaterial = m.Building((string)b["scale"]);
            go.isStatic = true;
            Identity(go, (string)b["id"], $"SemanticBuilding:{b["scale"]}:{b["interior"]}:{b["zone"]}:{b["sector"]}",
                $"{b["name"]} | {b["access"]}", fp.Select(p => new Vector3(p.x, floorY, p.z)).ToArray());
            var door = GameObject.CreatePrimitive(PrimitiveType.Cube);
            door.name = $"DOOR_{b["id"]}";
            UnityEngine.Object.DestroyImmediate(door.GetComponent<BoxCollider>());
            var dp = V3((JArray)b["door"]);
            var facing = new Vector3((float)b["doorFacing"][0], 0f, (float)b["doorFacing"][1]);
            door.transform.position = dp + Vector3.up * 1.15f + facing * 0.06f;
            door.transform.rotation = Quaternion.LookRotation(facing, Vector3.up);
            door.transform.localScale = new Vector3(b["interior"].ToString() == "LARGE" ? 2.0f : 1.2f, 2.3f, 0.12f);
            door.GetComponent<MeshRenderer>().sharedMaterial = b["interior"].ToString() == "CLOSED" ? m.DoorClosed : m.Door;
            door.transform.SetParent(go.transform, true);
            return go;
        }

        // ---------------------------------------------------------------- mesh helpers

        static Mesh Ribbon(List<Vector3> pts, float width, float lift, int risers)
        {
            var sampled = Resample(pts, 0.5f);
            var cum = new List<float> { 0f };
            for (int i = 1; i < sampled.Count; i++) cum.Add(cum[i - 1] + Flat(sampled[i] - sampled[i - 1]));
            float total = Mathf.Max(cum[cum.Count - 1], 0.01f);
            float ya = sampled[0].y, yb = sampled[sampled.Count - 1].y;
            int treads = risers > 0 ? risers + 1 : 0;
            float Y(int i)
            {
                if (treads == 0) return sampled[i].y + lift;
                int k = Mathf.Min(treads - 1, Mathf.FloorToInt(cum[i] / total * treads));
                return ya + (yb - ya) * k / (treads - 1) + lift;
            }
            var mb = new MeshBuilder();
            float half = width / 2f;
            Vector3 Side(int i)
            {
                var a = sampled[Mathf.Max(0, i - 1)]; var b = sampled[Mathf.Min(sampled.Count - 1, i + 1)];
                var t = new Vector3(b.x - a.x, 0f, b.z - a.z).normalized;
                return new Vector3(-t.z, 0f, t.x);
            }
            for (int i = 0; i + 1 < sampled.Count; i++)
            {
                var s0 = Side(i); var s1 = Side(i + 1);
                float y0 = Y(i), y1 = treads > 0 ? y0 : Y(i + 1);
                var p0 = new Vector3(sampled[i].x, y0, sampled[i].z);
                var p1 = new Vector3(sampled[i + 1].x, y1, sampled[i + 1].z);
                var l0 = p0 + s0 * half; var r0 = p0 - s0 * half; var l1 = p1 + s1 * half; var r1 = p1 - s1 * half;
                mb.Quad(r0, l0, l1, r1);
                mb.Skirt(l0, l1, Mathf.Min(y0, y1) - 0.5f);
                mb.Skirt(r1, r0, Mathf.Min(y0, y1) - 0.5f);
                if (treads > 0 && i + 2 < sampled.Count)
                {
                    float yn = Y(i + 1);
                    if (Mathf.Abs(yn - y0) > 0.001f)
                    {
                        var lo = Mathf.Min(yn, y0); var hi = Mathf.Max(yn, y0);
                        var a = new Vector3(l1.x, lo, l1.z); var b = new Vector3(r1.x, lo, r1.z);
                        mb.Quad(a, new Vector3(a.x, hi, a.z), new Vector3(b.x, hi, b.z), b);
                        mb.Quad(b, new Vector3(b.x, hi, b.z), new Vector3(a.x, hi, a.z), a);
                    }
                }
            }
            return mb.ToMesh();
        }

        static List<Vector3> Resample(List<Vector3> pts, float step)
        {
            var outp = new List<Vector3> { pts[0] };
            for (int i = 0; i + 1 < pts.Count; i++)
            {
                float d = Flat(pts[i + 1] - pts[i]);
                int n = Mathf.Max(1, Mathf.CeilToInt(d / step));
                for (int k = 1; k <= n; k++) outp.Add(Vector3.Lerp(pts[i], pts[i + 1], k / (float)n));
            }
            return outp;
        }

        static float Flat(Vector3 v) => new Vector2(v.x, v.z).magnitude;
        static Vector3 V3(JArray a) => new Vector3((float)a[0], (float)a[1], (float)a[2]);
        static Vector3 P(JToken xz, float y) => new Vector3((float)xz[0], y, (float)xz[1]);

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
            var c = go.AddComponent<JDSpatialIdentity>();
            c.stableId = id;
            c.kind = kind;
            c.sourceId = source;
            c.referenceOutline = outline ?? new Vector3[0];
        }

        sealed class MeshBuilder
        {
            readonly List<Vector3> v = new List<Vector3>();
            readonly List<int> t = new List<int>();

            public void Quad(Vector3 a, Vector3 b, Vector3 c, Vector3 d)
            {
                int i = v.Count;
                v.Add(a); v.Add(b); v.Add(c); v.Add(d);
                t.Add(i); t.Add(i + 1); t.Add(i + 2); t.Add(i); t.Add(i + 2); t.Add(i + 3);
            }

            public void Skirt(Vector3 a, Vector3 b, float bottom)
            {
                Quad(a, new Vector3(a.x, bottom, a.z), new Vector3(b.x, bottom, b.z), b);
            }

            public void Wall(Vector3 a, Vector3 b, float height)
            {
                var a2 = a + Vector3.up * height; var b2 = b + Vector3.up * height;
                Quad(a, a2, b2, b);
                Quad(b, b2, a2, a);
            }

            public Mesh ToMesh()
            {
                var mesh = new Mesh { indexFormat = v.Count > 65000 ? IndexFormat.UInt32 : IndexFormat.UInt16 };
                mesh.SetVertices(v);
                mesh.SetTriangles(t, 0);
                mesh.RecalculateNormals();
                mesh.RecalculateBounds();
                return mesh;
            }
        }

        sealed class Mats
        {
            public readonly Material[] Zone;
            public readonly Material Water, Curb, Stair, Commercial, Main, Secondary, Quay, Bridge, Passage, Plaza, Seam, Door, DoorClosed;
            readonly Dictionary<string, Material> layers = new Dictionary<string, Material>();
            readonly Dictionary<string, Material> buildings = new Dictionary<string, Material>();

            public Mats()
            {
                Zone = new[]
                {
                    Make("Zone_CASCO", "#C9AE92"), Make("Zone_MERCADO", "#D9C9A0"), Make("Zone_MUELLE", "#B8C2C4"),
                    Make("Zone_TALLERES", "#B5AEA2"), Make("Zone_VIVIENDAS", "#B9C7A0"),
                };
                Water = Make("Water", "#3F5A5E");
                Curb = Make("Curb", "#7E7568");
                Stair = Make("Street_Stair", "#B5504A");
                Commercial = Make("Street_Commercial", "#9C6A4E");
                Main = Make("Street_Main", "#6E6A66");
                Secondary = Make("Street_Secondary", "#8C8780");
                Quay = Make("Street_Quay", "#5E7480");
                Bridge = Make("Street_Bridge", "#5A5550");
                Passage = Make("Street_Passage", "#7A4E8C");
                Plaza = Make("OpenSpace", "#C8CFA8");
                Seam = Make("Seam", "#C040A0");
                Door = Make("Door_Accessible", "#F2C230");
                DoorClosed = Make("Door_Closed", "#4A3730");
                layers["service"] = Make("Layer_service", "#B07820");
                layers["interior"] = Make("Layer_interior", "#962896");
                layers["upper"] = Make("Layer_upper", "#DC5A14");
                layers["water"] = Make("Layer_water", "#146EBE");
                layers["garden"] = Make("Layer_garden", "#288C3C");
                layers["openspace"] = Make("Layer_openspace", "#5A96C8");
                buildings["G"] = Make("Building_G", "#962020");
                buildings["M"] = Make("Building_M", "#BE6E28");
                buildings["P"] = Make("Building_P", "#3C6E3C");
                buildings["C"] = Make("Building_C", "#6E6964");
            }

            public Material Layer(string l) => layers.TryGetValue(l, out var mat) ? mat : layers["service"];
            public Material Building(string s) => buildings[s];

            static Material Make(string name, string hex)
            {
                var path = $"{OwnedDir}/Materials/CITY_{name}.mat";
                var existing = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (existing) return existing;
                Directory.CreateDirectory($"{OwnedDir}/Materials");
                var mat = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                ColorUtility.TryParseHtmlString(hex, out var c);
                mat.SetColor("_BaseColor", c);
                mat.SetFloat("_Smoothness", 0.15f);
                AssetDatabase.CreateAsset(mat, path);
                return mat;
            }
        }
    }
}

using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// Step 4 of the ENV factory: assembles a street from a data spec (Env/Specs/streets/*.json). A street is an
    /// axis along +x with a floor style, two building rows that reference library units by id (with overrides:
    /// palette, seed, floors, rows...) and placed templates (quay edge, stepped connector, clusters...). The
    /// assembler resolves party walls between neighbours, one quoin column per shared edge and exposed ends, so
    /// the operator asks for outcomes ("a lodging, then a narrow closed house, a 2 m alley...") not object paths.
    /// </summary>
    public static class EnvStreet
    {
        public const string StreetSpecs = EnvKit.Specs + "/streets";
        static Dictionary<string, string> paletteMap;

        internal class Placed
        {
            public BuildingSpec spec;
            public float x0, width, setback, scale = 1f;
            public float y;          // ground-floor level (districts on sloping ground; 0 on flat streets)
            public bool north;
        }

        [MenuItem("JuegoDef/ENV/4 Build Street Demos")]
        public static void BuildDemos()
        {
            foreach (var guid in AssetDatabase.FindAssets("t:TextAsset", new[] { StreetSpecs }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                if (path.EndsWith(".json")) BuildScene(path);
            }
        }

        /// <summary>Builds the street into a new scene with the project lighting and the bootstrap GC2 player, then
        /// saves it as Scenes/ENV/&lt;id&gt;.unity.</summary>
        public static string BuildScene(string specPath)
        {
            var spec = JObject.Parse(EnvKit.ReadText(specPath));
            if (spec["extends"] != null)
            {
                // variant of another street: same layout, top-level keys replaced (id, paletteMap, brief...)
                var baseSpec = JObject.Parse(EnvKit.ReadText($"{StreetSpecs}/{spec["extends"]}.json"));
                foreach (var kv in spec)
                    if (kv.Key != "extends") baseSpec[kv.Key] = kv.Value.DeepClone();
                spec = baseSpec;
            }
            var id = (string)spec["id"];
            var stage = EnvPreview.NewStage(id, ground: false);
            Object.DestroyImmediate(stage.gameObject);
            var root = Build(spec, null);
            BringPlayer(spec);
            EnvKit.EnsureFolder("Assets/JuegoDef/Scenes/ENV");
            var scenePath = $"Assets/JuegoDef/Scenes/ENV/{id}.unity";
            EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(), scenePath);
            // Glass and wet stone need the street itself in their reflections; without a probe they mirror the
            // default sky's brown lower hemisphere. One small baked probe per street is enough at this stage.
            var probeGo = new GameObject("StreetReflectionProbe");
            var rp = probeGo.AddComponent<ReflectionProbe>();
            var bounds = EnvPreview.BoundsOf(root);
            probeGo.transform.position = new Vector3(bounds.center.x, 2f, bounds.center.z);
            rp.size = new Vector3(bounds.size.x + 10f, 20f, bounds.size.z + 10f);
            rp.mode = UnityEngine.Rendering.ReflectionProbeMode.Custom;
            rp.resolution = 128;
            rp.boxProjection = true;
            var cubePath = $"Assets/JuegoDef/Scenes/ENV/{id}_Reflection.exr";
            if (Lightmapping.BakeReflectionProbe(rp, cubePath))
            {
                AssetDatabase.ImportAsset(cubePath);
                rp.customBakedTexture = AssetDatabase.LoadAssetAtPath<Cubemap>(cubePath);
            }
            EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(), scenePath);
            Debug.Log($"JD_ENV_STREET {id} -> {scenePath} objects={root.GetComponentsInChildren<Transform>().Length}");
            return scenePath;
        }

        public static GameObject Build(JObject spec, Transform parent)
        {
            EnvKit.ClearCache();
            BuildingAssembler.ReloadGrammar();
            var units = JObject.Parse(EnvKit.ReadText(EnvKit.Specs + "/units.json"))["units"].ToDictionary(u => (string)u["id"], u => (JObject)u);
            var root = new GameObject((string)spec["id"]).transform;
            root.SetParent(parent, false);
            // A/B variants: swap palette families without touching the layout
            paletteMap = spec["paletteMap"] is JObject pm ? pm.Properties().ToDictionary(pr => pr.Name, pr => (string)pr.Value) : null;

            // A street is one straight segment (v1 spec), a list of placed segments, or a path (centreline traced
            // from a reference, segments mitred automatically); bends, widenings and corners are composed between segments.
            var frames = new List<Transform>();
            if (spec["path"] is JArray)
                frames = BuildPath(spec, root, units);
            else if (spec["segments"] is JArray segments)
                foreach (JObject seg in segments)
                {
                    var holder = new GameObject((string)seg["id"] ?? "Segment").transform;
                    holder.SetParent(root, false);
                    holder.localPosition = seg["at"] is JArray at ? V(at) : Vector3.zero;
                    holder.localRotation = Quaternion.Euler(0, (float?)seg["rotY"] ?? 0, 0);
                    BuildSegment(seg, holder, units);
                    frames.Add(holder);
                }
            else
                BuildSegment(spec, root, units);

            if (spec["templates"] is JArray templates)
            {
                var troot = EnvKit.Group(root, "Templates");
                foreach (JObject t in templates)
                {
                    var holder = new GameObject((string)t["name"] ?? (string)t["kind"]).transform;
                    holder.SetParent(troot, false);
                    if (t["segment"] != null)
                    {
                        // placed in a segment frame: x along the segment, z from its south facade line
                        var f = frames[(int)t["segment"]];
                        holder.position = f.TransformPoint(V((JArray)t["at"]));
                        holder.rotation = f.rotation * Quaternion.Euler(0, (float?)t["rotY"] ?? 0, 0);
                    }
                    else
                    {
                        holder.localPosition = V((JArray)t["at"]);
                        holder.localRotation = Quaternion.Euler(0, (float?)t["rotY"] ?? 0, 0);
                    }
                    JObject unit;
                    if (t["unit"] != null)
                    {
                        unit = (JObject)units[(string)t["unit"]].DeepClone();
                        if (t["overrides"] is JObject ov && unit["building"] is JObject b)
                            foreach (var kv in ov) b[kv.Key] = kv.Value.DeepClone();
                        if (unit["building"] is JObject bb && paletteMap != null && paletteMap.TryGetValue((string)bb["palette"] ?? "", out var mapped))
                            bb["palette"] = mapped;
                    }
                    else unit = new JObject { ["id"] = (string)t["kind"], ["kind"] = t["kind"], ["params"] = t["params"], ["parts"] = t["parts"] };
                    EnvLibrary.BuildUnit(unit, holder);
                }
            }

            if (spec["route"] is JArray route)
            {
                var probe = new GameObject("RouteProbe");
                probe.transform.SetParent(root, false);
                probe.SetActive(false);
                var comp = probe.AddComponent<JuegoDef.Dev.JDRouteProbe>();
                comp.waypoints = route.Select(w => root.TransformPoint(At(w, root, frames))).ToArray();
            }
            if (spec["spawn"] != null)
            {
                var sp = root.TransformPoint(At(spec["spawn"], root, frames));
                spec["_spawnWorld"] = new JArray(sp.x, sp.y, sp.z);
            }
            return root.gameObject;
        }

        /// <summary>One straight segment: hierarchy ground, two facade rows with party walls/quoins/setbacks, life pass.</summary>
        static void BuildSegment(JObject spec, Transform root, Dictionary<string, JObject> units)
        {
            float length = (float)spec["length"], width = (float)spec["width"];
            string ground = (string)spec["ground"] ?? "kerbed";
            int seed = (int?)spec["seed"] ?? 1;
            bool kerbed = EnvTemplates.IsKerbed(ground);
            float pavement = (float?)spec["pavement"] ?? EnvTemplates.Profiles[ground].pavement;
            float datum = kerbed ? EnvTemplates.PavementTop : 0f;
            float g0 = (float?)spec["groundFrom"] ?? 0f, g1 = (float?)spec["groundTo"] ?? length;
            var floor = new GameObject("Floor").transform;
            floor.SetParent(root, false);
            floor.localPosition = new Vector3(g0, (float?)spec["groundY"] ?? 0f, 0);
            float floorW = width - ((float?)spec["quayDepth"] ?? 0f);  // a quay apron takes the water side of a plaza
            EnvTemplates.StreetGround(floor, g1 - g0, floorW, ground, pavement, seed);

            var built = new List<GameObject>();
            foreach (var side in new[] { "south", "north" })
            {
                var row = spec["rows"]?[side] as JArray;
                if (row == null) continue;
                float x = (float?)spec["rowStart"]?[side] ?? 0f;
                // fitted rows (path streets): buildings scale so the row exactly fills its mitred length
                float scale = 1f;
                if (spec["fit"]?[side] is JArray fit && (bool?)spec["fitRows"] != false)
                {
                    x = (float)fit[0];
                    float gaps = row.Cast<JObject>().Where(it => it["gap"] != null).Sum(it => (float)it["gap"]);
                    float natural = row.Cast<JObject>().Where(it => it["gap"] == null).Sum(it => Resolve(it, units).bays * 2f);
                    if (natural > 0) scale = ((float)fit[1] - (float)fit[0] - gaps) / natural;
                    if (scale < 0.88f || scale > 1.14f)
                        Debug.LogWarning($"ENV_ROW_FIT {root.name}/{side}: scale {scale:F2} outside 0.88-1.14 (row {natural + gaps:F1} m for {(float)fit[1] - (float)fit[0]:F1} m)");
                }
                var rowPlaced = new List<Placed>();
                foreach (JObject item in row)
                {
                    if (item["gap"] != null) { x += (float)item["gap"]; rowPlaced.Add(null); continue; }
                    var bs = Resolve(item, units);
                    var p = new Placed { spec = bs, x0 = x, width = bs.bays * 2 * scale, scale = scale, north = side == "north", setback = (float?)item["setback"] ?? 0f };
                    rowPlaced.Add(p);
                    x += p.width;
                }
                ResolveNeighbours(rowPlaced, spec["ends"]?[side] as JObject);
                var rowRoot = EnvKit.Group(root, "Row_" + side);
                foreach (var p in rowPlaced.Where(p => p != null))
                {
                    var go = BuildingAssembler.Build(p.spec, rowRoot);
                    go.transform.localPosition = p.north ? new Vector3(p.x0 + p.width, datum, width + p.setback) : new Vector3(p.x0, datum, -p.setback);
                    go.transform.localRotation = Quaternion.Euler(0, p.north ? 180 : 0, 0);
                    if (Mathf.Abs(p.scale - 1f) > 0.001f) go.transform.localScale = new Vector3(p.scale, 1, 1);
                    built.Add(go);
                    if (p.setback > 0.01f)
                    {
                        // the forecourt of a set-back building is paved like its footway
                        var mat = kerbed ? EnvTemplates.Profiles[ground].pave : EnvTemplates.Profiles[ground].road;
                        var yard = new GameObject("Setback_" + p.spec.id).transform;
                        yard.SetParent(root, false);
                        yard.localPosition = new Vector3(p.x0, 0, p.north ? width : -p.setback);
                        EnvTemplates.Tiles(yard, mat.Contains("Flag") ? "Floor_UnevenBrick" : "Floor_RoundRocks", 0, p.width, 0, p.setback, datum,
                            new Dictionary<string, string> { { mat.Contains("Flag") ? "MI_UnevenBrick" : "MI_RoundRocks", mat } });
                    }
                }
            }
            if ((bool?)spec["life"] ?? true)
                EnvLife.DressSegment(root, ground, length, width, pavement, datum, built, seed, (bool?)spec["vehicles"] ?? true);
        }

        /// <summary>Path street: a layout traced from a real reference and simplified for play. A centreline of points
        /// ("path", [x, z] pairs) with one segment per edge; each segment has its own width, lateral shift (axis
        /// changes), hierarchy profile and rows. The assembler computes every segment frame and, at each joint, the
        /// mitre of each facade line: on the inner side of a bend rows stop at the block tip (one quoin, no side walls
        /// facing each other), on the outer side they run into the concave corner (no quoins); a width change or an
        /// axis shift steps the building line (exposed return). Each row is then fitted between its mitres by scaling
        /// its buildings (plots are not multiples of 2 m in a real town), and floors overlap at the joints, each
        /// later segment a few millimetres lower so the overlap never z-fights.</summary>
        static List<Transform> BuildPath(JObject spec, Transform root, Dictionary<string, JObject> units)
        {
            var pts = ((JArray)spec["path"]).Select(p => new Vector2((float)p[0], (float)p[1])).ToList();
            var segs = ((JArray)spec["segments"]).Cast<JObject>().ToList();
            if (segs.Count != pts.Count - 1) throw new System.ArgumentException("ENV_PATH_SEGMENTS_MISMATCH " + spec["id"]);
            int n = segs.Count;
            var d = new Vector2[n]; var nl = new Vector2[n]; var o = new Vector2[n];
            var len = new float[n]; var wid = new float[n];
            for (int i = 0; i < n; i++)
            {
                var e = pts[i + 1] - pts[i];
                len[i] = e.magnitude; d[i] = e / len[i];
                nl[i] = new Vector2(-d[i].y, d[i].x);                       // left normal = the segment's north side
                wid[i] = (float)segs[i]["width"];
                o[i] = pts[i] + nl[i] * (((float?)segs[i]["shift"] ?? 0f) - wid[i] / 2f);
                // an axis shift is a composed event (the street carries on beside a landmark); report every one so a
                // forgotten "shift" on a later segment cannot silently offset the street
                float jump = ((float?)segs[i]["shift"] ?? 0f) - (i > 0 ? (float?)segs[i - 1]["shift"] ?? 0f : 0f);
                if (i > 0 && Mathf.Abs(jump) > 0.5f) Debug.Log($"ENV_PATH_AXIS_SHIFT {spec["id"]} {segs[i]["id"]}: centreline moves {jump:F1} m");
            }
            var rowFrom = new float[n, 2]; var rowTo = new float[n, 2];
            var endKind = new string[n, 2, 2];                             // [segment, side 0 south / 1 north, 0 west / 1 east]
            var ext = new float[n, 2];                                     // floor overlap before / after
            for (int i = 0; i < n; i++)
                for (int s = 0; s < 2; s++) { rowFrom[i, s] = 0; rowTo[i, s] = len[i]; endKind[i, s, 0] = endKind[i, s, 1] = "open"; }
            for (int k = 1; k < n; k++)
            {
                float turn = Vector2.SignedAngle(d[k - 1], d[k]);          // + = left (towards the north side)
                float overlap = Mathf.Max(wid[k - 1], wid[k]) / 2f * Mathf.Tan(Mathf.Abs(turn) * Mathf.Deg2Rad / 2f) + 0.6f;
                ext[k - 1, 1] = overlap; ext[k, 0] = overlap;
                for (int s = 0; s < 2; s++)
                {
                    var a = o[k - 1] + nl[k - 1] * (s == 1 ? wid[k - 1] : 0f);
                    var b = o[k] + nl[k] * (s == 1 ? wid[k] : 0f);
                    float den = d[k - 1].x * d[k].y - d[k - 1].y * d[k].x;
                    bool mitred = false;
                    if (Mathf.Abs(turn) > 0.5f && Mathf.Abs(den) > 1e-4f)
                    {
                        var ab = b - a;
                        float ta = (ab.x * d[k].y - ab.y * d[k].x) / den, tb = (ab.x * d[k - 1].y - ab.y * d[k - 1].x) / den;
                        if (Mathf.Abs(ta - len[k - 1]) < 4f && Mathf.Abs(tb) < 4f)
                        {
                            rowTo[k - 1, s] = ta; rowFrom[k, s] = tb; mitred = true;
                            bool inner = (turn > 0) == (s == 1);
                            endKind[k - 1, s, 1] = inner ? "tip_keep" : "concave";
                            endKind[k, s, 0] = inner ? "tip_cede" : "concave";
                        }
                    }
                    if (!mitred) { endKind[k - 1, s, 1] = "open"; endKind[k, s, 0] = "open"; }  // stepped building line
                }
            }
            var frames = new List<Transform>();
            for (int i = 0; i < n; i++)
            {
                var seg = (JObject)segs[i].DeepClone();
                var holder = new GameObject((string)seg["id"] ?? "Segment_" + i).transform;
                holder.SetParent(root, false);
                holder.localPosition = new Vector3(o[i].x, 0, o[i].y);
                holder.localRotation = Quaternion.Euler(0, Mathf.Atan2(-d[i].y, d[i].x) * Mathf.Rad2Deg, 0);
                seg["length"] = len[i];
                if (seg["seed"] == null) seg["seed"] = i + 1;
                var ends = new JObject();
                var fit = new JObject();
                foreach (var (side, s) in new[] { ("south", 0), ("north", 1) })
                {
                    // the north row runs east-to-west in the building frame, so its west/east ends swap nothing here:
                    // ends are always in segment x (west = small x)
                    ends[side] = new JObject { ["west"] = seg["ends"]?[side]?["west"] ?? endKind[i, s, 0], ["east"] = seg["ends"]?[side]?["east"] ?? endKind[i, s, 1] };
                    fit[side] = new JArray((float?)seg["rowFrom"]?[side] ?? rowFrom[i, s], (float?)seg["rowTo"]?[side] ?? rowTo[i, s]);
                }
                seg["ends"] = ends;
                seg["fit"] = fit;
                seg["groundFrom"] = -ext[i, 0];
                seg["groundTo"] = len[i] + ext[i, 1];
                seg["groundY"] = -0.003f * i;
                BuildSegment(seg, holder, units);
                frames.Add(holder);
            }
            return frames;
        }

        /// <summary>A point in the street: [x, y, z] in street space, or {"segment": i, "at": [x, y, z]} in a path
        /// segment's frame (x along the segment, z = 0 on its south facade line).</summary>
        static Vector3 At(JToken t, Transform root, List<Transform> frames)
        {
            if (t is JObject jo && jo["segment"] != null)
                return root.InverseTransformPoint(frames[(int)jo["segment"]].TransformPoint(V((JArray)jo["at"])));
            return V((JArray)t);
        }

        static Vector3 V(JArray a) => new Vector3((float)a[0], (float)a[1], (float)a[2]);

        static BuildingSpec Resolve(JObject item, Dictionary<string, JObject> units)
        {
            JObject b;
            if (item["unit"] != null)
            {
                var uid = (string)item["unit"];
                if (!units.TryGetValue(uid, out var unit) || (string)unit["kind"] != "building")
                    throw new System.ArgumentException("ENV_STREET_UNKNOWN_BUILDING_UNIT " + uid);
                b = (JObject)unit["building"].DeepClone();
            }
            else b = new JObject();
            foreach (var kv in item)
                if (kv.Key != "unit") b[kv.Key] = kv.Value.DeepClone();
            var spec = b.ToObject<BuildingSpec>();
            spec.id = (string)item["name"] ?? ((string)item["unit"] ?? spec.type) + "_" + spec.seed;
            if (paletteMap != null && paletteMap.TryGetValue(spec.palette ?? "", out var mapped)) spec.palette = mapped;
            return spec;
        }

        /// <summary>West/east neighbours along the row (null entries are gaps/alleys). Shared storeys hide both side
        /// walls when the neighbour is at least as deep; the taller (or western, on a tie) building keeps the quoins of
        /// the shared edge; open ends expose.</summary>
        internal static void ResolveNeighbours(List<Placed> row, JObject ends)
        {
            // row ends: open (exposed, quoins) | hidden (a neighbour beyond the spec) | tip_keep / tip_cede (convex block
            // tip at a bend: no side walls, one quoin) | concave (outer corner of a bend: side wall to the back notch, no quoins)
            string westKind = (string)ends?["west"] ?? "open", eastKind = (string)ends?["east"] ?? "open";
            bool westOpen = westKind == "open", eastOpen = eastKind == "open";
            for (int i = 0; i < row.Count; i++)
            {
                var p = row[i];
                if (p == null) continue;
                var west = i > 0 ? row[i - 1] : null;
                var east = i < row.Count - 1 ? row[i + 1] : null;
                // a neighbour only covers our side wall if it is at least as deep and on the same building line
                // (else the rear part, or the step of a setback, would be a hole)
                bool Covers(Placed o) => o.spec.depth >= p.spec.depth && Mathf.Abs(o.setback - p.setback) < 0.01f;
                // storeys of p (from the ground floor up) that lie entirely within the neighbour's height, so a
                // neighbour one step up or down a sloping street never leaves a sliver of missing side wall
                int Shared(Placed o)
                {
                    if (!Covers(o)) return 0;
                    float bottom = o.y - o.spec.basement - 0.05f, top = o.y + o.spec.floors * BuildingAssembler.Storey + 0.05f;
                    int n = 0;
                    for (int f = 0; f < p.spec.floors; f++)
                    {
                        if (p.y + f * BuildingAssembler.Storey < bottom || p.y + (f + 1) * BuildingAssembler.Storey > top) break;
                        n++;
                    }
                    return n;
                }
                int westParty = west != null ? Shared(west) : (i == 0 && !westOpen ? p.spec.floors : 0);
                int eastParty = east != null ? Shared(east) : (i == row.Count - 1 && !eastOpen ? p.spec.floors : 0);
                bool westExposed = west == null && (i > 0 || westOpen);
                bool eastExposed = east == null && (i < row.Count - 1 || eastOpen);
                bool westQuoins = west == null || p.spec.floors > west.spec.floors || westParty == 0;
                bool eastQuoins = east == null || p.spec.floors >= east.spec.floors || eastParty == 0;
                bool westTip = false, eastTip = false;
                if (i == 0 && west == null && westKind != "open" && westKind != "hidden")
                {
                    westParty = westKind.StartsWith("tip") ? p.spec.floors : 0;
                    westQuoins = westKind == "tip_keep";
                    westTip = westQuoins;
                }
                if (i == row.Count - 1 && east == null && eastKind != "open" && eastKind != "hidden")
                {
                    eastParty = eastKind.StartsWith("tip") ? p.spec.floors : 0;
                    eastQuoins = eastKind == "tip_keep";
                    eastTip = eastQuoins;
                }
                // building local left = west for the south row, east for the north row (rotated 180)
                if (!p.north)
                {
                    p.spec.partyLeft = westParty; p.spec.partyRight = eastParty;
                    p.spec.exposeLeft |= westExposed; p.spec.exposeRight |= eastExposed;
                    p.spec.quoinsLeft = westQuoins; p.spec.quoinsRight = eastQuoins;
                    p.spec.tipLeft = westTip; p.spec.tipRight = eastTip;
                }
                else
                {
                    p.spec.partyLeft = eastParty; p.spec.partyRight = westParty;
                    p.spec.exposeLeft |= eastExposed; p.spec.exposeRight |= westExposed;
                    p.spec.quoinsLeft = eastQuoins; p.spec.quoinsRight = westQuoins;
                    p.spec.tipLeft = eastTip; p.spec.tipRight = westTip;
                }
            }
        }

        /// <summary>Copies the bootstrap GC2 player, camera and camera shot into the street scene at the spec's spawn.</summary>
        internal static void BringPlayer(JObject spec)
        {
            var active = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            var boot = EditorSceneManager.OpenScene("Assets/JuegoDef/Scenes/Bootstrap_GC2Core.unity", OpenSceneMode.Additive);
            var spawn = spec["_spawnWorld"] is JArray a ? V(a) : new Vector3(2, 0.2f, 4);
            foreach (var go in boot.GetRootGameObjects())
            {
                if (go.name != "Player" && go.name != "Main Camera" && go.name != "Camera Shot") continue;
                UnityEngine.SceneManagement.SceneManager.MoveGameObjectToScene(go, active);
                go.transform.position += spawn;  // keeps the bootstrap offsets (player pivot 1 m above its ground)
            }
            var oldCam = active.GetRootGameObjects().FirstOrDefault(g => g.name == "Main Camera" && !g.GetComponents<MonoBehaviour>().Any(m => m && m.GetType().Namespace != null && m.GetType().Namespace.StartsWith("GameCreator")));
            if (oldCam) Object.DestroyImmediate(oldCam);
            EditorSceneManager.CloseScene(boot, true);
        }
    }
}

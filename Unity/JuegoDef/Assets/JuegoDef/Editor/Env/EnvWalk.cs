using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// Micro-polish inspection walk (owner brief 2026-09-29: "recorrer todo el distrito en 3D ... calle por calle"). For one
    /// street of the district spec it stands at stations along the centreline and captures, in BOTH directions:
    /// <c>game</c> (the real GC2 third-person camera: pivot 1 m up, radius 3 m, shoulder 0.5 m, FOV 55, the Player
    /// mannequin as scale reference, camera pulled in when a wall is in the way), <c>eye</c> (1.7 m, looking ahead),
    /// <c>diagL/diagR</c> (eye level, 55 degrees off the axis at each facade) and <c>up</c> (6 m up, roofs and joints);
    /// plus lateral clearance per station (facade to facade at chest height) so a narrow street is judged by data.
    /// Operator: <c>EnvWalk.Street("Espina_E", "Captures/micro-polish/STREET_A_Espina_E/before")</c> (paths are relative
    /// to the Unity project folder; Captures/ is git-ignored, curated shots are copied to Docs/evidence/).
    /// The Player is moved only for the capture and always restored.
    /// </summary>
    public static class EnvWalk
    {
        // The Player root sits at the capsule centre (mannequin local y = -1), so the GC2 pivot (Player + Lift) is feet + 2 m.
        public const float PlayerCentre = 1.0f, GamePivotLift = 1.0f, GameRadius = 3.0f, GameShoulder = 0.5f, GameFov = 55f, GamePitch = 8f;

        static JObject Spec => JObject.Parse(EnvKit.ReadText($"{EnvDistrict.DistrictSpecs}/ENV01_Casco_District.json"));

        static readonly Vector2[] SeamOffsets =
        {
            Vector2.zero, new Vector2(0.003f, 0), new Vector2(-0.003f, 0), new Vector2(0, 0.003f), new Vector2(0, -0.003f),
            new Vector2(0.02f, 0), new Vector2(-0.02f, 0), new Vector2(0, 0.02f), new Vector2(0, -0.02f),
            new Vector2(0.045f, 0), new Vector2(-0.045f, 0), new Vector2(0, 0.045f), new Vector2(0, -0.045f),
        };

        /// <summary>Height of the walkable surface at (x, z); a ray that lands exactly on a seam between two ground meshes can
        /// slip through, so it retries a few millimetres either side before giving up.</summary>
        public static float Ground(float x, float z, float fallback = 0f)
        {
            foreach (var o in SeamOffsets)
            {
                var hits = Physics.RaycastAll(new Vector3(x + o.x, 80, z + o.y), Vector3.down, 200)
                    .Where(h => (h.collider is MeshCollider && h.collider.name.StartsWith("Ground_")) || h.collider.name.Contains("_Deck") || h.collider.name.Contains("_Treads"))
                    .OrderBy(h => h.distance).ToList();
                if (hits.Count > 0) return hits[0].point.y;
            }
            return fallback;
        }

        public struct Station { public Vector3 pos; public Vector3 dir; public float t; }

        public static List<Station> Stations(string street, float spacing)
        {
            var s = ((JArray)Spec["streets"]).Cast<JObject>().First(x => (string)x["id"] == street);
            float total = 0;
            var pts = ((JArray)s["pts"]).Select(c => new Vector3((float)c[0], (float)c[2], (float)c[1])).ToList();
            for (int i = 0; i + 1 < pts.Count; i++) total += Vector3.Distance(pts[i], pts[i + 1]);
            int n = Mathf.Max(2, Mathf.CeilToInt(total / spacing) + 1);
            var list = new List<Station>();
            for (int i = 0; i < n; i++)
            {
                float t = n == 1 ? 0 : (float)i / (n - 1);
                float t0 = Mathf.Clamp01(t - 0.02f), t1 = Mathf.Clamp01(t + 0.02f);
                var p = EnvDistrict.StreetPoint(street, t);
                var d = EnvDistrict.StreetPoint(street, t1) - EnvDistrict.StreetPoint(street, t0);
                d.y = 0;
                p.y = Ground(p.x, p.z, p.y);
                list.Add(new Station { pos = p, dir = d.normalized, t = t });
            }
            return list;
        }

        /// <summary>Camera as the GC2 third-person shot places it for a player standing at <paramref name="feet"/> facing <paramref name="fwd"/>.</summary>
        public static (Vector3 eye, Vector3 at) GameCamera(Vector3 feet, Vector3 fwd, float pitch = GamePitch)
        {
            var right = Vector3.Cross(Vector3.up, fwd).normalized;
            var pivot = feet + Vector3.up * (PlayerCentre + GamePivotLift) + right * GameShoulder;
            var rot = Quaternion.LookRotation(fwd, Vector3.up) * Quaternion.Euler(pitch, 0, 0);
            var want = pivot + rot * Vector3.back * GameRadius;
            // avoid clipping: pull the camera in along the boom when a collider is in the way
            var boom = want - pivot;
            var eye = want;
            var player = GameObject.Find("Player");
            var hits = Physics.SphereCastAll(pivot, 0.25f, boom.normalized, boom.magnitude)
                .Where(h => !h.collider.isTrigger && (player == null || !h.collider.transform.IsChildOf(player.transform)))
                .OrderBy(h => h.distance).ToList();
            if (hits.Count > 0 && hits[0].distance > 0.05f) eye = pivot + boom.normalized * hits[0].distance;
            return (eye, pivot + rot * Vector3.forward * 4f);
        }

        /// <summary>Distance from the centreline to the first solid on each side at chest height (m); 99 when open.</summary>
        public static (float left, float right) Clearance(Vector3 p, Vector3 dir)
        {
            var origin = p + Vector3.up * 1.4f;
            var left = Vector3.Cross(Vector3.up, dir).normalized * -1f;
            var right = -left;
            float Probe(Vector3 d)
            {
                var hits = Physics.RaycastAll(origin, d, 30f).Where(h => !h.collider.isTrigger && !h.collider.name.StartsWith("Ground_") && !h.collider.name.Contains("Player")).OrderBy(h => h.distance).ToList();
                return hits.Count > 0 ? hits[0].distance : 99f;
            }
            return (Probe(left), Probe(right));
        }

        public static string Street(string street, string outFolder, float spacing = 6f, string modes = "game,eye,diag,up", int width = 1280, int height = 720, bool holes = false)
        {
            // holes: magenta background so any gap in the geometry (cracks, wall/ground joints) shows as magenta; Tools/env_holes.py counts it
            Color? bg = holes ? new Color(1f, 0f, 1f) : (Color?)null;
            Physics.SyncTransforms();
            var want = new HashSet<string>(modes.Split(','));
            var st = Stations(street, spacing);
            var player = GameObject.Find("Player");
            var savedPos = player != null ? player.transform.position : Vector3.zero;
            var savedRot = player != null ? player.transform.rotation : Quaternion.identity;
            var report = new StringBuilder();
            report.AppendLine("idx,t,x,y,z,slopePct,clearL,clearR,width");
            int shots = 0;
            try
            {
                for (int dirSign = 1; dirSign >= -1; dirSign -= 2)
                {
                    string tag = dirSign > 0 ? "fwd" : "rev";
                    for (int k = 0; k < st.Count; k++)
                    {
                        int i = dirSign > 0 ? k : st.Count - 1 - k;
                        var s = st[i];
                        var fwd = s.dir * dirSign;
                        string id = $"{i:00}";
                        if (want.Contains("game") && player != null)
                        {
                            player.transform.SetPositionAndRotation(s.pos + Vector3.up * PlayerCentre, Quaternion.LookRotation(fwd));
                            Physics.SyncTransforms();
                            var (eye, at) = GameCamera(s.pos, fwd);
                            EnvPreview.Capture($"{outFolder}/{street}_game_{tag}_{id}.jpg", eye, at, GameFov, width, height, bg);
                            shots++;
                        }
                        if (player != null) player.transform.position = savedPos + Vector3.down * 200f;   // out of every view but the game shots
                        if (want.Contains("eye"))
                        {
                            EnvPreview.Capture($"{outFolder}/{street}_eye_{tag}_{id}.jpg", s.pos + Vector3.up * 1.7f, s.pos + fwd * 12f + Vector3.up * 2.2f, 60f, width, height, bg);
                            shots++;
                        }
                        if (want.Contains("up"))
                        {
                            EnvPreview.Capture($"{outFolder}/{street}_up_{tag}_{id}.jpg", s.pos + Vector3.up * 6.5f - fwd * 2f, s.pos + fwd * 10f + Vector3.up * 3f, 60f, width, height, bg);
                            shots++;
                        }
                        if (dirSign > 0 && want.Contains("gnd"))
                        {
                            // the ground and the foot of both facades at 2-8 m: where cracks and wall/ground joints are seen at pixel scale
                            foreach (float yaw in new[] { -70f, -35f, 0f, 35f, 70f })
                            {
                                var dirH = Quaternion.AngleAxis(yaw, Vector3.up) * fwd;
                                var eyeP = s.pos + Vector3.up * 1.7f;
                                var atP = eyeP + dirH * Mathf.Cos(38f * Mathf.Deg2Rad) * 8f + Vector3.down * Mathf.Sin(38f * Mathf.Deg2Rad) * 8f;
                                EnvPreview.Capture($"{outFolder}/{street}_gnd_{id}_{(int)yaw:+00;-00;00}.jpg", eyeP, atP, 60f, width, height, bg);
                                shots++;
                            }
                        }
                        if (dirSign > 0 && want.Contains("diag"))
                        {
                            var left = Vector3.Cross(Vector3.up, fwd).normalized * -1f;
                            foreach (var (nm, side) in new[] { ("diagL", -1f), ("diagR", 1f) })
                            {
                                var look = Quaternion.AngleAxis(side * 55f, Vector3.up) * fwd;
                                EnvPreview.Capture($"{outFolder}/{street}_{nm}_{id}.jpg", s.pos + Vector3.up * 1.7f, s.pos + look * 8f + Vector3.up * 3.2f, 62f, width, height, bg);
                                shots++;
                            }
                        }
                    }
                }
                var sb = report;
                for (int i = 0; i < st.Count; i++)
                {
                    var s = st[i];
                    var (l, r) = Clearance(s.pos, s.dir);
                    float slope = i + 1 < st.Count ? (st[i + 1].pos.y - s.pos.y) / Mathf.Max(0.01f, Vector2.Distance(new Vector2(s.pos.x, s.pos.z), new Vector2(st[i + 1].pos.x, st[i + 1].pos.z))) * 100f : 0f;
                    sb.AppendLine(System.FormattableString.Invariant($"{i:00},{s.t:0.00},{s.pos.x:0.0},{s.pos.y:0.00},{s.pos.z:0.0},{slope:0.0},{l:0.0},{r:0.0},{(l + r):0.0}"));
                }
                Directory.CreateDirectory(Path.Combine(Directory.GetCurrentDirectory(), outFolder));
                File.WriteAllText(Path.Combine(Directory.GetCurrentDirectory(), $"{outFolder}/{street}_stations.csv"), report.ToString());
            }
            finally
            {
                if (player != null) player.transform.SetPositionAndRotation(savedPos, savedRot);
            }
            return $"JD_WALK {street}: {st.Count} stations, {shots} shots -> {outFolder}\n{report}";
        }

        static readonly System.Text.RegularExpressions.Regex FloorProp = new System.Text.RegularExpressions.Regex(
            "^(ENV_(Bench_Stone|Bicycle|Bike_Rack|Bollard_Street|Cafe_Chair|Cafe_Table|Parasol|Lamp_Post|Planter_Box|Planter_Pot|Pot_Glazed|Pot_Tin|" +
            "Prop_Barrel|Prop_Barrel_Apples|Prop_Bucket|Prop_Bucket_Wood|Prop_Chair|Prop_Crate_Wooden|Prop_Stool|Prop_Bag|Recycling_Bins|Trough_Stone|" +
            "Tree_Plaza|Tree_Plaza_B|Tree_Plaza_C|Tree_Singular|Shrub_Garden|Plant_\\w+|Sign_NoEntry|AFrame_Board|Rock_\\w|Weeds_Grass|Gate_Timber))$");

        /// <summary>P0 audit of the floor-standing props within <paramref name="radius"/> m of a street: floating,
        /// sunk, overlapping each other, or inside a building's colliders. Returns one line per finding.</summary>
        public static string Audit(string street, float radius = 9f)
        {
            Physics.SyncTransforms();
            var root = GameObject.Find("ENV01_Casco_District").transform;
            var line = Stations(street, 2f).Select(s => s.pos).ToList();
            float DistToStreet(Vector3 p) => line.Min(q => Vector2.Distance(new Vector2(p.x, p.z), new Vector2(q.x, q.z)));
            var props = new List<(Transform t, Bounds b)>();
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
            {
                if (!FloorProp.IsMatch(t.name) || !t.gameObject.activeInHierarchy) continue;
                if (t.parent != null && FloorProp.IsMatch(t.parent.name)) continue;
                if (DistToStreet(t.position) > radius) continue;
                var rs = t.GetComponentsInChildren<Renderer>();
                if (rs.Length == 0) continue;
                var b = rs[0].bounds; foreach (var r in rs) b.Encapsulate(r.bounds);
                props.Add((t, b));
            }
            var sb = new StringBuilder();
            int flag = 0;
            foreach (var (t, b) in props)
            {
                float g = Ground(b.center.x, b.center.z, float.NaN);
                if (float.IsNaN(g)) { sb.AppendLine($"NOGROUND {t.name} {t.position:0.0}"); flag++; continue; }
                float gap = b.min.y - g;
                bool plant = t.name.StartsWith("ENV_Plant") || t.name.StartsWith("ENV_Shrub") || t.name.StartsWith("ENV_Tree") || t.name.StartsWith("ENV_Weeds") || t.name.StartsWith("ENV_Rock");
                if (gap > 0.12f)
                {
                    var hit = Physics.RaycastAll(new Vector3(b.center.x, b.min.y + 0.05f, b.center.z), Vector3.down, gap + 0.3f)
                        .Where(h => !h.collider.name.StartsWith("Ground_") && !h.collider.transform.IsChildOf(t)).OrderBy(h => h.distance).FirstOrDefault();
                    // a plant stands in a pot or planter (a prop of the list whose box holds its foot), not on the ground
                    var foot = new Vector3(b.center.x, b.min.y + 0.03f, b.center.z);
                    bool potted = plant && props.Any(o => o.t != t && (o.t.name.StartsWith("ENV_Planter") || o.t.name.StartsWith("ENV_Pot_")) && o.b.Contains(foot));
                    if (hit.collider == null && !potted) { sb.AppendLine($"FLOAT {t.name} {t.position:0.0} gap={gap:0.00} parent={t.parent?.name}"); flag++; }
                }
                else if (gap < (plant ? -0.35f : -0.2f)) { sb.AppendLine($"SUNK {t.name} {t.position:0.0} gap={gap:0.00} parent={t.parent?.name}"); flag++; }
                var solids = Physics.OverlapBox(b.center, b.extents * 0.55f)
                    .Where(c => !c.isTrigger && !c.transform.IsChildOf(t) && !c.name.StartsWith("Ground_") && c.transform.IsChildOf(root.Find("Rows") ?? root)).ToArray();
                // pots and planters sit in a balcony's iron, and the plant stands in its pot or planter: holders, not walls
                bool Holder(Collider c)
                {
                    for (var p = c.transform; p != null && p != root; p = p.parent)
                        if (p.name.StartsWith("ENV_Balcony") || p.name.StartsWith("ENV_Planter") || p.name.StartsWith("ENV_Pot_")) return true;
                    return false;
                }
                if (solids.Length > 0 && !solids.All(Holder))
                { sb.AppendLine($"INWALL {t.name} {t.position:0.0} in {solids[0].transform.parent?.name}/{solids[0].name}"); flag++; }
            }
            for (int i = 0; i < props.Count; i++)
                for (int j = i + 1; j < props.Count; j++)
                {
                    if (props[j].t.IsChildOf(props[i].t) || props[i].t.IsChildOf(props[j].t)) continue;
                    var a = props[i].b; var c = props[j].b;
                    if (!a.Intersects(c)) continue;
                    float dx = Mathf.Min(a.max.x, c.max.x) - Mathf.Max(a.min.x, c.min.x), dy = Mathf.Min(a.max.y, c.max.y) - Mathf.Max(a.min.y, c.min.y), dz = Mathf.Min(a.max.z, c.max.z) - Mathf.Max(a.min.z, c.min.z);
                    float vol = dx * dy * dz, small = Mathf.Min(a.size.x * a.size.y * a.size.z, c.size.x * c.size.y * c.size.z);
                    // a plant in its pot or planter overlaps it by design
                    bool IsHolder(string n) => n.StartsWith("ENV_Planter") || n.StartsWith("ENV_Pot_");
                    bool IsPlant(string n) => n.StartsWith("ENV_Plant_") || n.StartsWith("ENV_Shrub");
                    bool plantInPot = (IsPlant(props[i].t.name) && IsHolder(props[j].t.name)) || (IsPlant(props[j].t.name) && IsHolder(props[i].t.name));
                    if (small > 1e-4f && vol / small > 0.3f && !plantInPot) { sb.AppendLine($"OVERLAP {props[i].t.name} + {props[j].t.name} at {a.center:0.0} share={vol / small:0.00}"); flag++; }
                }
            return $"JD_AUDIT {street} r={radius}: {props.Count} floor props, {flag} findings\n{sb}";
        }

        /// <summary>Holes seen from every street: from a station of each street every <paramref name="step"/> m, rays in 24 directions
        /// at three angles below the horizon. Below the horizon a ray that meets nothing within 80 m is a hole in the ground (sky can
        /// not be below the horizon); rays that would land in the river channel are ignored. Findings are grouped in 2 m cells.</summary>
        public static string SkyHoles(float step = 3f, string outCsv = null)
        {
            Physics.SyncTransforms();
            var spec = Spec;
            var channel = ((JArray)spec["river"]["channel"]).Select(q => new Vector2((float)q[0], (float)q[1])).ToList();
            bool InChannel(Vector2 p)
            {
                bool c = false;
                for (int i = 0, j = channel.Count - 1; i < channel.Count; j = i++)
                    if ((channel[i].y > p.y) != (channel[j].y > p.y) && p.x < (channel[j].x - channel[i].x) * (p.y - channel[i].y) / (channel[j].y - channel[i].y) + channel[i].x) c = !c;
                return c;
            }
            var found = new Dictionary<(int, int), (Vector3 pos, string street, int rays)>();
            int rays = 0;
            foreach (JObject s in (JArray)spec["streets"])
            {
                string id = (string)s["id"];
                foreach (var st in Stations(id, step))
                {
                    var eye = st.pos + Vector3.up * 1.7f;
                    for (int a = 0; a < 24; a++)
                        foreach (float pitch in new[] { 6f, 16f, 35f })   // Unity: a positive x rotation looks DOWN
                        {
                            var d = Quaternion.Euler(pitch, a * 15f, 0) * Vector3.forward;
                            rays++;
                            if (Physics.Raycast(eye, d, out var _, 80f, ~0, QueryTriggerInteraction.Ignore)) continue;
                            // where the ray would reach the ground level of the station; only inside the district counts
                            float t = 1.7f / Mathf.Max(0.05f, -d.y);
                            var p = eye + d * Mathf.Min(t, 80f);
                            if (p.x < 3f || p.z < 3f || p.x > 193f || p.z > 233f) continue;
                            if (InChannel(new Vector2(p.x, p.z))) continue;
                            var key = ((int)Mathf.Floor(p.x / 2f), (int)Mathf.Floor(p.z / 2f));
                            found[key] = found.TryGetValue(key, out var e) ? (e.pos, e.street, e.rays + 1) : (p, id, 1);
                        }
                }
            }
            var sb = new StringBuilder();
            sb.AppendLine($"JD_SKYHOLES {rays} rays, {found.Count} 2 m cells with no ground");
            foreach (var kv in found.OrderByDescending(k => k.Value.rays).Take(40))
                sb.AppendLine(System.FormattableString.Invariant($"  {kv.Value.street} at ({kv.Value.pos.x:0.0}, {kv.Value.pos.y:0.0}, {kv.Value.pos.z:0.0}) seen by {kv.Value.rays} rays"));
            if (outCsv != null)
            {
                Directory.CreateDirectory(Path.GetDirectoryName(Path.Combine(Directory.GetCurrentDirectory(), outCsv)));
                File.WriteAllLines(Path.Combine(Directory.GetCurrentDirectory(), outCsv), found.Select(kv => System.FormattableString.Invariant($"{kv.Value.street},{kv.Value.pos.x:0.0},{kv.Value.pos.y:0.0},{kv.Value.pos.z:0.0},{kv.Value.rays}")));
            }
            return sb.ToString();
        }

        /// <summary>Open-air holes, independent of any camera: every 1 m cell of the district with open sky above it and no walkable
        /// ground under it (river channel, stairs and decks excluded). Connected cells are reported as clusters; a cluster is
        /// "filled" when the earth gap-fill mesh covers its cells.</summary>
        public static string OpenAirHoles(int top = 25)
        {
            Physics.SyncTransforms();
            var spec = Spec;
            var root = GameObject.Find("ENV01_Casco_District").transform;
            var channel = ((JArray)spec["river"]["channel"]).Select(q => new Vector2((float)q[0], (float)q[1])).ToList();
            bool InPoly(List<Vector2> poly, Vector2 p)
            {
                bool c = false;
                for (int i = 0, j = poly.Count - 1; i < poly.Count; j = i++)
                    if ((poly[i].y > p.y) != (poly[j].y > p.y) && p.x < (poly[j].x - poly[i].x) * (p.y - poly[i].y) / (poly[j].y - poly[i].y) + poly[i].x) c = !c;
                return c;
            }
            const int X0 = 3, Z0 = 3, X1 = 193, Z1 = 233;
            int W = X1 - X0 + 1;
            var hole = new bool[W * (Z1 - Z0 + 1)];
            for (int z = Z0; z <= Z1; z++)
                for (int x = X0; x <= X1; x++)
                {
                    var p = new Vector2(x + 0.5f, z + 0.5f);
                    if (InPoly(channel, p)) continue;
                    // one ray from above: the first thing it meets decides. Ground (or a deck/stair): fine. A roof, a wall top, a
                    // prop or a tree crown: the cell is covered or inside a footprint. Nothing at all: open sky over no ground.
                    if (Physics.Raycast(new Vector3(p.x, 60f, p.y), Vector3.down, out var hit, 120f, ~0, QueryTriggerInteraction.Ignore)) continue;
                    if (!float.IsNaN(Ground(p.x, p.y, float.NaN))) continue;   // a ray lost on a seam
                    hole[(z - Z0) * W + (x - X0)] = true;
                }
            // fill coverage from the gap-fill mesh
            var covered = new HashSet<int>();
            var fill = root.Find("Ground/Underlay_GapFill");
            if (fill != null)
            {
                var m = fill.GetComponent<MeshFilter>().sharedMesh; var v = m.vertices; var t = m.triangles;
                for (int i = 0; i < t.Length; i += 3)
                {
                    var c = (v[t[i]] + v[t[i + 1]] + v[t[i + 2]]) / 3f;
                    covered.Add(Mathf.FloorToInt(c.z - Z0) * W + Mathf.FloorToInt(c.x - X0));
                }
            }
            var seen = new bool[hole.Length]; var sb = new StringBuilder(); var clusters = new List<(int n, int filled, Vector3 c)>();
            for (int i = 0; i < hole.Length; i++)
            {
                if (!hole[i] || seen[i]) continue;
                var q = new Queue<int>(); q.Enqueue(i); seen[i] = true; int n = 0, filled = 0; double sx = 0, sz = 0;
                while (q.Count > 0)
                {
                    int k = q.Dequeue(); n++; int x = k % W, z = k / W; sx += x + X0 + 0.5; sz += z + Z0 + 0.5;
                    if (covered.Contains(k)) filled++;
                    foreach (var (dx, dz) in new[] { (1, 0), (-1, 0), (0, 1), (0, -1) })
                    {
                        int xx = x + dx, zz = z + dz; if (xx < 0 || zz < 0 || xx >= W || zz > Z1 - Z0) continue;
                        int kk = zz * W + xx; if (hole[kk] && !seen[kk]) { seen[kk] = true; q.Enqueue(kk); }
                    }
                }
                var cx = (float)(sx / n); var cz = (float)(sz / n);
                clusters.Add((n, filled, new Vector3(cx, Ground(cx, cz, 0f), cz)));
            }
            int cells = clusters.Sum(c => c.n), fcells = clusters.Sum(c => c.filled);
            sb.AppendLine($"JD_OPENAIR {cells} open-air 1 m cells with no ground in {clusters.Count} clusters; {fcells} covered by the gap fill");
            foreach (var c in clusters.OrderByDescending(c => c.n - c.filled).Take(top))
                sb.AppendLine(System.FormattableString.Invariant($"  {c.n} cells ({c.filled} filled) around ({c.c.x:0.0}, {c.c.z:0.0})"));
            return sb.ToString();
        }

        /// <summary>Gap between each facade's street face and the first ground under it, every 20 cm along the frontage (m).
        /// A gap of even a few millimetres shows as a hairline of sky at the foot of the wall from a low angle.</summary>
        public static string WallGaps(string rowId, float minGap = 0.008f)
        {
            Physics.SyncTransforms();
            var row = GameObject.Find("ENV01_Casco_District").transform.Find("Rows/" + rowId);
            var sb = new StringBuilder();
            int pts = 0, bad = 0;
            foreach (Transform b in row)
            {
                if (b.name == "Walls") continue;
                float x0 = float.MaxValue, x1 = float.MinValue;
                foreach (var r in b.GetComponentsInChildren<Renderer>())
                {
                    var lb = r.localBounds;
                    for (int i = 0; i < 8; i++)
                    {
                        var l = b.InverseTransformPoint(r.transform.TransformPoint(lb.center + Vector3.Scale(lb.extents, new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1))));
                        x0 = Mathf.Min(x0, l.x); x1 = Mathf.Max(x1, l.x);
                    }
                }
                var run = new List<float>(); float worst = 0;
                for (float x = x0 + 0.2f; x < x1 - 0.2f; x += 0.2f)
                {
                    pts++;
                    var p = b.TransformPoint(new Vector3(x, 0, 0));
                    var f = b.forward; f.y = 0; f.Normalize();
                    float gap = -1;
                    for (float d = -0.05f; d <= 0.4f; d += 0.004f)
                        if (!float.IsNaN(Ground(p.x + f.x * d, p.z + f.z * d, float.NaN))) { gap = d; break; }
                    if (gap > minGap) { bad++; run.Add(x); worst = Mathf.Max(worst, gap); }
                }
                if (run.Count > 0) sb.AppendLine($"  {b.name}: {run.Count} pts with gap>{minGap * 1000:0} mm, worst {worst * 1000:0} mm, x {run.Min():0.0}..{run.Max():0.0} (world {b.TransformPoint(new Vector3(run.Min(), 0, 0)):0.0})");
            }
            return $"JD_WALLGAPS {rowId}: {pts} pts, {bad} gaps\n{sb}";
        }

        struct Edge { public int n; public float dy; public Vector3 a, b; public string mat; }

        static long WeldKey(Vector3 p) => ((long)Mathf.Round(p.x * 200f) << 32) ^ (long)Mathf.Round(p.z * 200f);   // 5 mm weld in plan

        /// <summary>Ground mesh integrity: edges used by one triangle only (open borders / T-junctions) and shared edges whose
        /// heights disagree. Both leave hairline holes through which the sky shows. Lists the longest open edges near
        /// <paramref name="near"/> (radius <paramref name="radius"/>) when given.</summary>
        public static string GroundSeams(Vector3? near = null, float radius = 12f, int top = 12)
        {
            var g = GameObject.Find("ENV01_Casco_District").transform.Find("Ground");
            var edges = new Dictionary<(long, long), Edge>();
            int tris = 0;
            foreach (Transform c in g)
            {
                var mf = c.GetComponent<MeshFilter>(); if (mf == null || c.name.StartsWith("Underlay")) continue;
                var v = mf.sharedMesh.vertices; var t = mf.sharedMesh.triangles;
                for (int i = 0; i < t.Length; i += 3)
                {
                    tris++;
                    for (int e = 0; e < 3; e++)
                    {
                        var p = c.TransformPoint(v[t[i + e]]); var q = c.TransformPoint(v[t[i + (e + 1) % 3]]);
                        long kp = WeldKey(p), kq = WeldKey(q);
                        var k = kp < kq ? (kp, kq) : (kq, kp);
                        var a = kp < kq ? p : q; var b = kp < kq ? q : p;
                        if (edges.TryGetValue(k, out var cur)) { cur.dy = Mathf.Max(cur.dy, Mathf.Abs(a.y - cur.a.y), Mathf.Abs(b.y - cur.b.y)); cur.n++; edges[k] = cur; }
                        else edges[k] = new Edge { n = 1, a = a, b = b, mat = c.name };
                    }
                }
            }
            int boundary = 0, inner = 0, mism = 0; float bLen = 0, innerLen = 0, mLen = 0, maxDy = 0;
            var worst = new List<(float len, Edge e)>();
            foreach (var kv in edges)
            {
                var e = kv.Value; float len = Vector2.Distance(new Vector2(e.a.x, e.a.z), new Vector2(e.b.x, e.b.z));
                if (e.n == 1)
                {
                    boundary++; bLen += len;
                    var mid = (e.a + e.b) / 2f;
                    if (!(mid.x < 3 || mid.z < 3 || mid.x > 193 || mid.z > 233)) { inner++; innerLen += len; }
                    if (near.HasValue && Vector2.Distance(new Vector2(mid.x, mid.z), new Vector2(near.Value.x, near.Value.z)) < radius) worst.Add((len, e));
                }
                else if (e.n == 2 && e.dy > 0.004f) { mism++; mLen += len; maxDy = Mathf.Max(maxDy, e.dy); }
            }
            // an open edge with ground on BOTH sides (2 cm either way) is an internal seam (T-junction): a hairline hole risk;
            // ground on one side only is a real border (under a house, the district edge)
            bool GroundAt(float x, float z) => Physics.RaycastAll(new Vector3(x, 80, z), Vector3.down, 200).Any(h => h.collider.name.StartsWith("Ground_"));
            int seams = 0; float seamLen = 0; var seamList = new List<(float len, Edge e)>();
            foreach (var kv in edges)
            {
                var e = kv.Value; if (e.n != 1) continue;
                var d = new Vector2(e.b.x - e.a.x, e.b.z - e.a.z); float len = d.magnitude; if (len < 1e-3f) continue;
                var nrm = new Vector2(-d.y, d.x) / len; var mid = (e.a + e.b) / 2f;
                bool s1 = GroundAt(mid.x + nrm.x * 0.02f, mid.z + nrm.y * 0.02f), s2 = GroundAt(mid.x - nrm.x * 0.02f, mid.z - nrm.y * 0.02f);
                if (s1 && s2) { seams++; seamLen += len; if (near.HasValue && Vector2.Distance(new Vector2(mid.x, mid.z), new Vector2(near.Value.x, near.Value.z)) < radius) seamList.Add((len, e)); }
            }
            var sb = new StringBuilder();
            sb.AppendLine($"JD_SEAMS tris={tris} edges={edges.Count} | open edges={boundary} ({bLen:0} m), not near outer border={inner} ({innerLen:0} m) | INTERNAL seams (ground on both sides)={seams} ({seamLen:0} m) | height mismatch>4mm={mism}");
            foreach (var w in seamList.OrderByDescending(x => x.len).Take(top))
                sb.AppendLine($"  seam {w.e.mat} len={w.len:0.00} from {w.e.a:0.00} to {w.e.b:0.00}");
            return sb.ToString();
        }

        /// <summary>Pulls <paramref name="eye"/> back toward <paramref name="target"/> when a solid other than
        /// <paramref name="own"/> is in the way (the opposite facade of a 6 m street), like the game camera's clipping avoidance.</summary>
        /// <summary>Same clipping avoidance for an ad-hoc view of a world point (no building of its own).</summary>
        public static Vector3 ClearEye(Vector3 target, Vector3 eye)
        {
            var dir = eye - target;
            var hits = Physics.RaycastAll(target, dir.normalized, dir.magnitude)
                .Where(h => !h.collider.isTrigger && !h.collider.name.StartsWith("Ground_")).OrderBy(h => h.distance).ToList();
            return hits.Count > 0 ? target + dir.normalized * Mathf.Max(0.6f, hits[0].distance - 0.35f) : eye;
        }

        static Vector3 Clear(Vector3 target, Vector3 eye, Transform own)
        {
            var dir = eye - target;
            var hits = Physics.RaycastAll(target, dir.normalized, dir.magnitude)
                .Where(h => !h.collider.isTrigger && !h.collider.transform.IsChildOf(own) && !h.collider.name.StartsWith("Ground_"))
                .OrderBy(h => h.distance).ToList();
            return hits.Count > 0 ? target + dir.normalized * Mathf.Max(0.6f, hits[0].distance - 0.35f) : eye;
        }

        /// <summary>One building (path under the district root, e.g. "Rows/K3_2/K3_2_0"). Views are taken from the street
        /// side in the building frame (street face on local z = 0 facing +z): <c>front</c>, oblique <c>obL/obR</c>,
        /// <c>up</c> (walker looking at the eaves), <c>roof</c> (aerial), plus <c>sideL/sideR/back</c> when asked.</summary>
        public static string Building(string path, string outFolder, string views = "front,obL,obR,up,roof", int width = 1280, int height = 720)
        {
            Physics.SyncTransforms();
            var root = GameObject.Find("ENV01_Casco_District").transform;
            var b = root.Find(path);
            if (b == null) return "JD_WALK no building " + path;
            // extent in the building's own frame (x along the frontage, y up, z from the street face into the plot)
            var lo = new Vector3(float.MaxValue, float.MaxValue, float.MaxValue); var hi = -lo;
            foreach (var r in b.GetComponentsInChildren<Renderer>())
                for (int i = 0; i < 8; i++)
                {
                    var lb = r.localBounds;   // the renderer's own box, not the world AABB (inflated on a building turned 154 degrees)
                    var wc = r.transform.TransformPoint(lb.center + Vector3.Scale(lb.extents, new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1)));
                    var l = b.InverseTransformPoint(wc);
                    lo = Vector3.Min(lo, l); hi = Vector3.Max(hi, l);
                }
            float W = hi.x - lo.x, H = hi.y - lo.y, xc = (lo.x + hi.x) / 2f;
            Vector3 P(float x, float y, float z) => b.TransformPoint(new Vector3(x, y, z));
            var want = new HashSet<string>(views.Split(','));
            string n = path.Replace('/', '_');
            int shots = 0;
            void Shot(string name, Vector3 target, Vector3 eye, float fov)
            {
                if (!want.Contains(name)) return;
                EnvPreview.Capture($"{outFolder}/{n}_{name}.jpg", Clear(target, eye, b), target, fov, width, height);
                shots++;
            }
            var mid = P(xc, 0.4f * H, 0);
            Shot("front", mid, P(xc, 1.7f, 9f), 78f);
            Shot("obL", P(xc + 0.15f * W, 0.4f * H, 0), P(xc - 0.8f * W - 1f, 1.7f, 4f), 70f);
            Shot("obR", P(xc - 0.15f * W, 0.4f * H, 0), P(xc + 0.8f * W + 1f, 1.7f, 4f), 70f);
            Shot("up", P(xc, 0.85f * H, 0), P(xc, 1.7f, 4.5f), 72f);
            Shot("roof", P(xc, H, -0.4f * Mathf.Abs(lo.z)), P(xc, H + 6f, 8f), 60f);
            Shot("sideL", P(lo.x, 0.4f * H, -0.3f * Mathf.Abs(lo.z)), P(lo.x - 7f, 1.7f, 0.5f), 70f);
            Shot("sideR", P(hi.x, 0.4f * H, -0.3f * Mathf.Abs(lo.z)), P(hi.x + 7f, 1.7f, 0.5f), 70f);
            Shot("back", P(xc, 0.4f * H, lo.z), P(xc, 1.7f, lo.z - 8f), 78f);
            return $"JD_WALK {path}: W={W:0.0} H={H:0.0} D={-lo.z:0.0} {shots} views";
        }
    }
}

using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// Semantic audit of the built district (owner brief 2026-09-29: an object can be well built and still make no sense to a
    /// person). What is measured, not what a sign says: doors that open onto the river, a void, a drop or a wall; walls and
    /// facades that squeeze the street; long runs of blank wall; windows that look onto a wall; bare side walls seen from the
    /// street; identical neighbours; props with no human function (no wall, door or plaza to belong to, or on the centreline).
    /// Findings are grouped by inspection unit (Env/Specs/districts/&lt;id&gt;.inspection.json).
    /// Operator: <c>EnvSemantics.Run("Captures/micro-polish/semantic_audit.json")</c>.
    /// </summary>
    public static class EnvSemantics
    {
        public class Finding
        {
            public string kind, unit, street, where, detail;
            public float x, y, z;
        }

        static JObject spec;
        static List<(string id, float w, List<Vector2> pts)> streets;
        static List<List<Vector2>> plazas;
        static List<Vector2> channel;
        static Dictionary<string, string> segUnit, rowStreet, rowRole;
        static JObject inspection;
        static Transform root, rows;

        static void Load()
        {
            spec = JObject.Parse(EnvKit.ReadText($"{EnvDistrict.DistrictSpecs}/ENV01_Casco_District.json"));
            inspection = JObject.Parse(EnvKit.ReadText($"{EnvDistrict.DistrictSpecs}/ENV01_Casco_District.inspection.json"));
            streets = ((JArray)spec["streets"]).Cast<JObject>().Select(s => ((string)s["id"], (float)s["width"], ((JArray)s["pts"]).Select(q => new Vector2((float)q[0], (float)q[1])).ToList())).ToList();
            plazas = ((JArray)spec["plazas"]).Cast<JObject>().Select(p => ((JArray)p["poly"]).Select(q => new Vector2((float)q[0], (float)q[1])).ToList()).ToList();
            channel = ((JArray)spec["river"]["channel"]).Select(q => new Vector2((float)q[0], (float)q[1])).ToList();
            segUnit = new Dictionary<string, string>();
            foreach (JObject u in (JArray)inspection["units"])
                foreach (var s in (JArray)u["segments"]) segUnit[(string)s] = (string)u["id"];
            rowStreet = new Dictionary<string, string>(); rowRole = new Dictionary<string, string>();
            foreach (JObject r in (JArray)spec["rows"]) { rowStreet[(string)r["id"]] = (string)r["street"]; rowRole[(string)r["id"]] = (string)r["role"]; }
            root = GameObject.Find("ENV01_Casco_District").transform;
            rows = root.Find("Rows");
            Physics.SyncTransforms();
        }

        static string UnitOfRow(string rowId)
        {
            if (rowStreet.TryGetValue(rowId, out var st) && !string.IsNullOrEmpty(st) && segUnit.TryGetValue(st, out var u)) return u;
            return rowRole.TryGetValue(rowId, out var role) && inspection["rowRoleUnits"][role] != null ? (string)inspection["rowRoleUnits"][role] : "OTHER";
        }

        static string UnitOfStreet(string id) => segUnit.TryGetValue(id, out var u) ? u : "OTHER";

        static float DistToPolyline(List<Vector2> pts, Vector2 p)
        {
            float best = float.MaxValue;
            for (int i = 0; i + 1 < pts.Count; i++)
            {
                var a = pts[i]; var ab = pts[i + 1] - a;
                float t = ab.sqrMagnitude > 0 ? Mathf.Clamp01(Vector2.Dot(p - a, ab) / ab.sqrMagnitude) : 0;
                best = Mathf.Min(best, (a + ab * t - p).magnitude);
            }
            return best;
        }

        static float DistToPolygonEdge(List<Vector2> poly, Vector2 p)
        {
            var closed = new List<Vector2>(poly) { poly[0] };
            return DistToPolyline(closed, p);
        }

        static bool Inside(List<Vector2> poly, Vector2 p)
        {
            bool c = false;
            for (int i = 0, j = poly.Count - 1; i < poly.Count; j = i++)
                if ((poly[i].y > p.y) != (poly[j].y > p.y) && p.x < (poly[j].x - poly[i].x) * (p.y - poly[i].y) / (poly[j].y - poly[i].y) + poly[i].x) c = !c;
            return c;
        }

        /// <summary>Gap from a plan point to the nearest walkable public space: metres beyond the edge of a street or plaza (negative inside).</summary>
        static float PublicGap(Vector2 p, out string street)
        {
            street = null;
            float best = float.MaxValue;
            foreach (var s in streets)
            {
                float g = DistToPolyline(s.pts, p) - s.w / 2f;
                if (g < best) { best = g; street = s.id; }
            }
            foreach (var pl in plazas)
                if (Inside(pl, p)) { best = Mathf.Min(best, -1f); }
            return best;
        }

        /// <summary>Is this collider part of a floor prop of everyday life (stool, pot, bucket, chair...)?</summary>
        static bool IsLifeProp(Transform t)
        {
            for (var c = t; c != null && c != root; c = c.parent)
                if (PropKind.ContainsKey(c.name)) return true;
            return false;
        }

        static Transform BuildingOf(Transform t)
        {
            for (var c = t; c != null; c = c.parent)
                if (c.parent != null && c.parent.parent == rows) return c;
            return null;
        }

        static string Path(Transform t)
        {
            var parts = new List<string>();
            for (var c = t; c != null && c != root; c = c.parent) parts.Add(c.name);
            parts.Reverse();
            return string.Join("/", parts);
        }

        static Finding F(string kind, string unit, string street, Vector3 p, string where, string detail) =>
            new Finding { kind = kind, unit = unit, street = street, x = p.x, y = p.y, z = p.z, where = where, detail = detail };

        // ------------------------------------------------------------------ doors

        /// <summary>Every door and gate: what is in front of it must be somewhere a person can step to.</summary>
        public static List<Finding> Doors()
        {
            var list = new List<Finding>();
            foreach (var t in rows.GetComponentsInChildren<Transform>(true))
            {
                if (!t.name.StartsWith("THR_")) continue;
                var b = BuildingOf(t); if (b == null) continue;
                string unit = UnitOfRow(b.parent.name);
                var p = t.position; var f = t.forward; f.y = 0; f.Normalize();
                Vector3 Q(float d) => p + f * d;
                float gy(float d) => EnvWalk.Ground(Q(d).x, Q(d).z, float.NaN);
                var g07 = gy(0.7f); var g15 = gy(1.5f);
                var where = Path(t);
                var q3 = Q(2.6f);
                if (float.IsNaN(g07) || float.IsNaN(g15))
                {
                    bool water = Inside(channel, new Vector2(Q(1.5f).x, Q(1.5f).z)) || DistToPolygonEdge(channel, new Vector2(Q(1.2f).x, Q(1.2f).z)) < 1.6f;
                    list.Add(F(water ? "DOOR_TO_RIVER" : "DOOR_TO_VOID", unit, null, p, where, $"no ground 0.7 m / 1.5 m in front ({(float.IsNaN(g07) ? "none" : g07.ToString("0.00"))} / {(float.IsNaN(g15) ? "none" : g15.ToString("0.00"))})"));
                    continue;
                }
                if (Mathf.Abs(g15 - p.y) > 0.5f || Mathf.Abs(g07 - p.y) > 0.45f)
                    list.Add(F("DOOR_DROP", unit, null, p, where, $"ground {g07 - p.y:+0.00;-0.00} m at 0.7 m and {g15 - p.y:+0.00;-0.00} m at 1.5 m from the door sill"));
                var dressing = b.Find("Dressing");
                // a door at the foot of a stair (a tread within half a metre of the sill) is a door on a landing, not a blocked one
                float g13 = gy(1.3f);
                bool stairOk = !float.IsNaN(g13) && g13 - p.y <= 0.5f;
                var capsule = Physics.OverlapCapsule(Q(1.3f) + Vector3.up * 0.35f, Q(1.3f) + Vector3.up * 1.7f, 0.28f)
                    .Where(c => !c.isTrigger && !c.name.StartsWith("Ground_") && !(c.transform.IsChildOf(b) && !(dressing != null && c.transform.IsChildOf(dressing)))
                                && !(stairOk && (c.name.EndsWith("_Treads") || c.name.EndsWith("_Risers")))
                                && !(t.name.EndsWith("_Closed") && IsLifeProp(c.transform)))   // a pot or a stool by a closed door is life
                    .ToArray();
                if (capsule.Length > 0 && !t.name.EndsWith("_Closed")) list.Add(F("DOOR_BLOCKED", unit, null, p, where, "in front of the door: " + string.Join(", ", capsule.Select(c => c.transform.name).Distinct().Take(3))));
                else if (capsule.Length > 0) list.Add(F("DOOR_BLOCKED_CLOSED", unit, null, p, where, "in front of a closed door: " + string.Join(", ", capsule.Select(c => c.transform.name).Distinct().Take(3))));
                float gap = PublicGap(new Vector2(q3.x, q3.z), out var street);
                if (gap > 1.2f)
                {
                    var hit = Physics.RaycastAll(new Vector3(Q(1.5f).x, 80, Q(1.5f).z), Vector3.down, 200).Where(h => h.collider.name.StartsWith("Ground_")).OrderBy(h => h.distance).FirstOrDefault();
                    string mat = hit.collider != null ? hit.collider.name : "?";
                    bool yard = mat.Contains("Earth") || mat.Contains("Grass");
                    if (!(yard && (t.name.Contains("Gate") || t.name.Contains("Service"))))
                        list.Add(F("DOOR_NOWHERE", unit, street, p, where, $"2.6 m in front is {gap:0.0} m beyond the nearest street/plaza ({street}); ground {mat}"));
                }
            }
            return list;
        }

        // ------------------------------------------------------------------ streets

        static (float dist, Collider col) Probe(Vector3 o, Vector3 d)
        {
            var hit = Physics.RaycastAll(o, d, 30f).Where(h => !h.collider.isTrigger && !h.collider.name.StartsWith("Ground_") && !h.collider.name.Contains("Player")).OrderBy(h => h.distance).FirstOrDefault();
            return hit.collider == null ? (99f, null) : (hit.distance, hit.collider);
        }

        /// <summary>Free width along every street at chest height against the nominal facade-to-facade width: walls, projecting
        /// facades and props that squeeze the way. Reported as runs.</summary>
        public static List<Finding> Narrowings(float step = 1.5f)
        {
            var list = new List<Finding>();
            foreach (var s in streets)
            {
                var stations = EnvWalk.Stations(s.id, step);
                var run = new List<(Vector3 p, float w, string culprit)>();
                void Flush()
                {
                    if (run.Count == 0) return;
                    var worst = run.OrderBy(r => r.w).First();
                    float len = run.Count * step;
                    if (len >= 1.5f || worst.w < 1.4f)
                        list.Add(F(worst.w < 1.4f ? "STREET_PINCH" : "STREET_SQUEEZED", UnitOfStreet(s.id), s.id, worst.p, worst.culprit, $"free width {worst.w:0.0} m over {len:0.0} m (nominal {s.w:0.0} m)"));
                    run.Clear();
                }
                foreach (var st in stations)
                {
                    var o = st.pos + Vector3.up * 1.4f;
                    var left = -Vector3.Cross(Vector3.up, st.dir).normalized; var right = -left;
                    var (dl, cl) = Probe(o, left); var (dr, cr) = Probe(o, right);
                    float w = dl + dr;
                    bool open = dl > 9f || dr > 9f;   // junction, plaza or end of the street
                    if (!open && (w < s.w - 1.3f || w < 2.3f))
                    {
                        var c = (dl <= dr ? cl : cr);
                        run.Add((st.pos, w, c != null ? Path(c.transform) : "?"));
                    }
                    else Flush();
                }
                Flush();
            }
            return list;
        }

        /// <summary>Garden walls: the longest run with no break (a gate, a pier, a change of height or masonry), measured on the
        /// built pieces, and tall walls closing a street.</summary>
        public static List<Finding> Walls()
        {
            var list = new List<Finding>();
            foreach (Transform row in rows)
            {
                var g = row.Find("Walls"); if (g == null) continue;
                var pieces = new List<(float x, float h, string mat, bool cut)>();
                foreach (Transform t in g)
                {
                    if (t.name == "ENV_Gate_Timber") { pieces.Add((row.InverseTransformPoint(t.position).x, 0, "gate", true)); continue; }
                    if (t.name != "ENV_Retaining_Wall_2x2") continue;
                    if (t.localScale.x < 0.4f) { pieces.Add((row.InverseTransformPoint(t.position).x, 0, "pier", true)); continue; }
                    var r = t.GetComponentInChildren<Renderer>();
                    pieces.Add((row.InverseTransformPoint(t.position).x, t.localScale.y, r != null && r.sharedMaterial != null ? r.sharedMaterial.name : "?", false));
                }
                var walls = pieces.Where(p => !p.cut).OrderBy(p => p.x).ToList();
                if (walls.Count == 0) continue;
                var cuts = pieces.Where(p => p.cut).Select(p => p.x).ToList();
                int start = 0;
                for (int i = 1; i <= walls.Count; i++)
                {
                    bool brk = i == walls.Count || walls[i].x - walls[i - 1].x > 2.4f || Mathf.Abs(walls[i].h - walls[i - 1].h) > 0.25f || walls[i].mat != walls[i - 1].mat
                               || cuts.Any(c => c > walls[i - 1].x && c < walls[i].x + 0.01f);
                    if (!brk) continue;
                    float len = walls[i - 1].x - walls[start].x + 2f;
                    if (len >= 10f)
                    {
                        var mid = row.TransformPoint(new Vector3((walls[start].x + walls[i - 1].x) / 2f, 0, 0));
                        mid.y = EnvWalk.Ground(mid.x, mid.z, mid.y);
                        list.Add(F("WALL_LONG_RUN", UnitOfRow(row.name), rowStreet.TryGetValue(row.name, out var s) ? s : null, mid, row.name, $"{len:0.0} m of garden wall in one height and one masonry, with no gate or pier"));
                    }
                    start = i;
                }
            }
            return list;
        }

        // ------------------------------------------------------------------ facades

        static readonly string WindowCodes = "WwTcBILN";

        static IEnumerable<Transform> Bays(Transform b, string section)
        {
            var sec = b.Find(section); if (sec == null) yield break;
            foreach (Transform f in sec) foreach (Transform m in f) yield return m;
        }

        /// <summary>Runs of frontage with no opening on any floor (or none above the ground floor) along a row.</summary>
        public static List<Finding> Blanks()
        {
            var list = new List<Finding>();
            foreach (Transform row in rows)
            {
                var cols = new List<(float x, bool blankAll, bool blankUpper, Transform b, Vector3 pos)>();
                foreach (Transform b in row)
                {
                    if (b.name == "Walls") continue;
                    var front = b.Find("Front"); if (front == null) continue;
                    var byBay = new Dictionary<int, List<(int floor, char code, Vector3 pos)>>();
                    int fl = 0;
                    foreach (Transform f in front)
                    {
                        foreach (Transform m in f)
                        {
                            int us = m.name.IndexOf('_'); if (us < 1 || !int.TryParse(m.name.Substring(us + 1), out int bay)) continue;
                            if (!byBay.ContainsKey(bay)) byBay[bay] = new List<(int, char, Vector3)>();
                            byBay[bay].Add((fl, m.name[0], m.position));
                        }
                        fl++;
                    }
                    foreach (var kv in byBay)
                    {
                        bool all = kv.Value.All(e => e.code == 'P'), upper = kv.Value.Where(e => e.floor >= 1).All(e => e.code == 'P');
                        var pos = kv.Value[0].pos;
                        cols.Add((row.InverseTransformPoint(pos).x, all, upper, b, pos));
                    }
                }
                foreach (var kind in new[] { "all", "upper" })
                {
                    var sorted = cols.OrderBy(c => c.x).ToList();
                    var run = new List<(float x, bool blankAll, bool blankUpper, Transform b, Vector3 pos)>();
                    void Flush()
                    {
                        if (run.Count > 0)
                        {
                            float len = run[run.Count - 1].x - run[0].x + 2f;
                            float min = kind == "all" ? 8f : 12f;
                            if (len >= min)
                            {
                                var mid = run[run.Count / 2].pos;
                                list.Add(F(kind == "all" ? "BLANK_WALL" : "BLANK_UPPER_RUN", UnitOfRow(row.name), rowStreet.TryGetValue(row.name, out var s) ? s : null, mid, row.name + ": " + string.Join(",", run.Select(r => r.b.name).Distinct()), $"{len:0.0} m of frontage with {(kind == "all" ? "no opening on any floor" : "no opening above the ground floor")}"));
                            }
                        }
                        run.Clear();
                    }
                    foreach (var c in sorted)
                    {
                        bool blank = kind == "all" ? c.blankAll : c.blankUpper;
                        if (!blank) { Flush(); continue; }
                        if (run.Count > 0 && c.x - run[run.Count - 1].x > 2.7f) Flush();
                        run.Add(c);
                    }
                    Flush();
                }
            }
            return list;
        }

        /// <summary>Windows that look onto a wall, and ground-floor windows buried by the pavement.</summary>
        public static List<Finding> Windows()
        {
            var list = new List<Finding>();
            foreach (Transform row in rows)
                foreach (Transform b in row)
                {
                    if (b.name == "Walls") continue;
                    string unit = UnitOfRow(row.name);
                    foreach (var section in new[] { "Front", "Side_L", "Side_R", "Back" })
                    {
                        var sec = b.Find(section); if (sec == null) continue;
                        int floor = 0;
                        foreach (Transform f in sec)
                        {
                            foreach (Transform m in f)
                            {
                                if (!WindowCodes.Contains(m.name[0])) continue;
                                var o = m.position + Vector3.up * 1.5f + m.forward * 0.08f;
                                var hit = Physics.RaycastAll(o, m.forward, 1.3f).Where(h => !h.collider.isTrigger && !h.collider.name.StartsWith("Ground_") && !h.collider.transform.IsChildOf(b)).OrderBy(h => h.distance).FirstOrDefault();
                                // only what a person can see: a back window 0.6 m from the next house's back wall, hidden between
                                // the blocks, is absurd but nobody looks at it
                                if (hit.collider != null && VisibleFromPublic(m.position + Vector3.up * 1.5f + m.forward * 0.4f, b))
                                    list.Add(F("WINDOW_ONTO_WALL", unit, null, m.position, Path(m), $"{section} window looks onto {Path(hit.collider.transform)} at {hit.distance:0.00} m"));
                                if (floor == 0 && section == "Front" && (m.name[0] == 'W' || m.name[0] == 'w'))
                                {
                                    float g = EnvWalk.Ground(m.position.x + m.forward.x * 0.6f, m.position.z + m.forward.z * 0.6f, float.NaN);
                                    if (!float.IsNaN(g) && g > m.position.y + 0.6f) list.Add(F("WINDOW_BURIED", unit, null, m.position, Path(m), $"pavement {g - m.position.y:0.00} m above the sill line"));
                                }
                            }
                            floor++;
                        }
                    }
                }
            return list;
        }

        /// <summary>Exposed side walls with no opening at all, seen from a street.</summary>
        public static List<Finding> BareSides()
        {
            var list = new List<Finding>();
            foreach (Transform row in rows)
                foreach (Transform b in row)
                {
                    if (b.name == "Walls") continue;
                    foreach (var section in new[] { "Side_L", "Side_R" })
                    {
                        var mods = Bays(b, section).ToList();
                        int visible = 0, openings = mods.Count(m => m.name[0] != 'P'); Vector3 mid = Vector3.zero;   // openings anywhere on the wall
                        var slots = new HashSet<string>();   // distinct 2 m columns seen: a 2 m strip beside a neighbour is not a wall
                        foreach (var m in mods)
                        {
                            var c = m.position + Vector3.up * 1.5f;
                            if (Physics.Raycast(c + m.forward * 0.1f, m.forward, 3f)) continue;   // a neighbour stands there
                            var target = c + m.forward * 0.4f;
                            var near = streets.OrderBy(s => DistToPolyline(s.pts, new Vector2(target.x, target.z))).First();
                            var nearestPoint = NearestPoint(near.pts, new Vector2(target.x, target.z));
                            var eye = new Vector3(nearestPoint.x, EnvWalk.Ground(nearestPoint.x, nearestPoint.y, target.y) + 1.7f, nearestPoint.y);
                            if ((eye - target).magnitude > 45f) continue;
                            if (Physics.Linecast(eye, target, out var h) && !h.collider.transform.IsChildOf(b)) continue;
                            visible++; mid = target; slots.Add(m.name.Substring(m.name.IndexOf('_') + 1));
                        }
                        if (visible >= 3 && slots.Count >= 2 && openings == 0)
                            list.Add(F("BARE_SIDE_WALL", UnitOfRow(row.name), null, mid, Path(b) + "/" + section, $"{visible * 6} m2 of exposed side wall seen from the street, no opening"));
                    }
                }
            return list;
        }

        /// <summary>Is <paramref name="target"/> in line of sight of a person standing on the nearest street, within 45 m?</summary>
        static bool VisibleFromPublic(Vector3 target, Transform own)
        {
            var near = streets.OrderBy(s => DistToPolyline(s.pts, new Vector2(target.x, target.z))).First();
            var np = NearestPoint(near.pts, new Vector2(target.x, target.z));
            var eye = new Vector3(np.x, EnvWalk.Ground(np.x, np.y, target.y) + 1.7f, np.y);
            if ((eye - target).magnitude > 45f) return false;
            return !(Physics.Linecast(eye, target, out var h) && !h.collider.transform.IsChildOf(own));
        }

        static Vector2 NearestPoint(List<Vector2> pts, Vector2 p)
        {
            float best = float.MaxValue; var bp = pts[0];
            for (int i = 0; i + 1 < pts.Count; i++)
            {
                var a = pts[i]; var ab = pts[i + 1] - a;
                float t = ab.sqrMagnitude > 0 ? Mathf.Clamp01(Vector2.Dot(p - a, ab) / ab.sqrMagnitude) : 0;
                var q = a + ab * t;
                if ((q - p).magnitude < best) { best = (q - p).magnitude; bp = q; }
            }
            return bp;
        }

        /// <summary>Facades with no relief at all (nothing stands out more than 30 cm: no balcony, awning, sign, canopy, open
        /// shutter), and runs of three or more identical windows on one floor.</summary>
        public static List<Finding> Facades()
        {
            var list = new List<Finding>();
            foreach (Transform row in rows)
                foreach (Transform b in row)
                {
                    if (b.name == "Walls") continue;
                    var front = b.Find("Front"); if (front == null) continue;
                    // relief: the furthest a front-side renderer stands out of the street face (local z), balconies and awnings included
                    float relief = 0;
                    foreach (var sec in new[] { front, b.Find("Dressing") })
                    {
                        if (sec == null) continue;
                        foreach (var r in sec.GetComponentsInChildren<Renderer>())
                        {
                            var lb = r.localBounds;
                            for (int i = 0; i < 8; i++)
                            {
                                var l = b.InverseTransformPoint(r.transform.TransformPoint(lb.center + Vector3.Scale(lb.extents, new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1))));
                                relief = Mathf.Max(relief, l.z);
                            }
                        }
                    }
                    if (relief < 0.3f) list.Add(F("FLAT_FACADE", UnitOfRow(row.name), null, b.position, Path(b), $"nothing stands out more than {relief * 100:0} cm from the front: no balcony, awning, sign or canopy"));
                    int fl = 0;
                    foreach (Transform f in front)
                    {
                        var codes = new string(f.Cast<Transform>().Select(m => m.name[0]).ToArray());
                        for (int i = 0; i + 2 < codes.Length; i++)
                            if ("WwTc".IndexOf(codes[i]) >= 0 && codes[i] == codes[i + 1] && codes[i] == codes[i + 2])
                            {
                                list.Add(F("WINDOW_RUN", UnitOfRow(row.name), null, f.GetChild(i).position, Path(b) + "/F" + fl, $"three identical windows in a row on floor {fl}: {codes}"));
                                break;
                            }
                        fl++;
                    }
                }
            return list;
        }

        /// <summary>Neighbouring roofs that overlap in plan by more than 60 cm (they should butt at the party line).</summary>
        public static List<Finding> Roofs()
        {
            var list = new List<Finding>();
            foreach (Transform row in rows)
            {
                (float min, float max, Transform b)? prev = null;
                foreach (Transform b in row)
                {
                    if (b.name == "Walls") { prev = null; continue; }
                    var roof = b.Find("Roof"); if (roof == null) continue;
                    float min = float.MaxValue, max = float.MinValue;
                    foreach (var r in roof.GetComponentsInChildren<Renderer>())
                    {
                        var lb = r.localBounds;
                        for (int i = 0; i < 8; i++)
                        {
                            var l = row.InverseTransformPoint(r.transform.TransformPoint(lb.center + Vector3.Scale(lb.extents, new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1))));
                            min = Mathf.Min(min, l.x); max = Mathf.Max(max, l.x);
                        }
                    }
                    if (prev.HasValue && prev.Value.max - min > 0.6f)
                        list.Add(F("ROOF_OVERLAP", UnitOfRow(row.name), null, b.position + Vector3.up * 10f, prev.Value.b.name + "+" + b.name, $"roofs overlap by {prev.Value.max - min:0.00} m in plan"));
                    prev = (min, max, b);
                }
            }
            return list;
        }

        /// <summary>One ground-floor pattern for most of the shops of a unit.</summary>
        public static List<Finding> Storefronts()
        {
            var list = new List<Finding>();
            var byUnit = new Dictionary<string, List<(string pat, Transform b)>>();
            foreach (Transform row in rows)
                foreach (Transform b in row)
                {
                    if (b.name == "Walls") continue;
                    var f0 = b.Find("Front/F0"); if (f0 == null) continue;
                    var codes = new string(f0.Cast<Transform>().Select(m => m.name[0]).ToArray());
                    if (codes.IndexOf('S') < 0 && codes.IndexOf('e') < 0 && codes.IndexOf('E') < 0 && codes.IndexOf('R') < 0) continue;   // not a shop
                    string unit = UnitOfRow(row.name);
                    if (!byUnit.ContainsKey(unit)) byUnit[unit] = new List<(string, Transform)>();
                    byUnit[unit].Add((codes, b));
                }
            foreach (var u in byUnit.Where(e => e.Value.Count >= 4))
            {
                var top = u.Value.GroupBy(v => v.pat).OrderByDescending(g => g.Count()).First();
                if (top.Count() * 2 >= u.Value.Count)
                    list.Add(F("STOREFRONT_GENERIC", u.Key, null, top.First().b.position, string.Join(",", top.Select(v => v.b.name)), $"{top.Count()} of {u.Value.Count} shops share the ground floor {top.Key}"));
            }
            return list;
        }

        static string WallMaterial(Transform module)
        {
            var r = module.GetComponentsInChildren<Renderer>().FirstOrDefault(x => x.sharedMaterial != null && x.sharedMaterial.name.StartsWith("ENV_"));
            return r == null ? null : r.sharedMaterial.name.Replace("_G", "");
        }

        /// <summary>A building whose exposed side wall is a different render or masonry from its own front at the same height:
        /// the material changes at a corner with no reason (no quoin, no plinth line).</summary>
        public static List<Finding> Materials()
        {
            var list = new List<Finding>();
            foreach (Transform row in rows)
                foreach (Transform b in row)
                {
                    if (b.name == "Walls") continue;
                    var front = b.Find("Front"); if (front == null) continue;
                    var frontMat = new Dictionary<int, string>(); int fl = 0;
                    foreach (Transform f in front)
                    {
                        var p = f.Cast<Transform>().FirstOrDefault(m => m.name[0] == 'P');
                        if (p != null) frontMat[fl] = WallMaterial(p);
                        fl++;
                    }
                    foreach (var section in new[] { "Side_L", "Side_R" })
                    {
                        var sec = b.Find(section); if (sec == null) continue;
                        fl = 0;
                        foreach (Transform f in sec)
                        {
                            var p = f.Cast<Transform>().FirstOrDefault(m => m.name[0] == 'P');
                            if (p != null && frontMat.TryGetValue(fl, out var fm) && fm != null)
                            {
                                var sm = WallMaterial(p);
                                bool exposed = !Physics.Raycast(p.position + Vector3.up * 1.5f + p.forward * 0.1f, p.forward, 3f);
                                if (sm != null && sm != fm && exposed && VisibleFromPublic(p.position + Vector3.up * 1.5f + p.forward * 0.4f, b))
                                    list.Add(F("MATERIAL_SEAM", UnitOfRow(row.name), null, p.position, Path(b) + "/" + section + "/F" + fl, $"front {fm} but side {sm} at storey {fl}"));
                            }
                            fl++;
                        }
                    }
                }
            return list;
        }

        /// <summary>The same front (bay codes, wall and roof material) next to each other, or three times on one street.</summary>
        public static List<Finding> Twins()
        {
            var list = new List<Finding>();
            var byUnit = new Dictionary<string, Dictionary<string, List<Transform>>>();
            foreach (Transform row in rows)
            {
                string prev = null; Transform prevB = null;
                foreach (Transform b in row)
                {
                    if (b.name == "Walls") { prev = null; continue; }
                    var front = b.Find("Front"); if (front == null) continue;
                    var sb = new StringBuilder();
                    foreach (Transform f in front) { sb.Append('|'); foreach (Transform m in f) sb.Append(m.name[0]); }
                    var wall = front.GetComponentsInChildren<Renderer>().FirstOrDefault(r => r.transform.parent != null && r.transform.parent.name.StartsWith("P_"));
                    var roof = b.Find("Roof")?.GetComponentInChildren<Renderer>();
                    sb.Append('#').Append(wall != null ? wall.sharedMaterial.name : "-").Append('#').Append(roof != null ? roof.sharedMaterial.name : "-");
                    string sig = sb.ToString();
                    if (sig == prev) list.Add(F("TWIN_NEIGHBOURS", UnitOfRow(row.name), null, b.position, $"{prevB.name}+{b.name}", "same bay pattern, wall and roof material: " + sig));
                    prev = sig; prevB = b;
                    string unit = UnitOfRow(row.name);
                    if (!byUnit.ContainsKey(unit)) byUnit[unit] = new Dictionary<string, List<Transform>>();
                    if (!byUnit[unit].ContainsKey(sig)) byUnit[unit][sig] = new List<Transform>();
                    byUnit[unit][sig].Add(b);
                }
            }
            foreach (var u in byUnit)
                foreach (var kv in u.Value.Where(e => e.Value.Count >= 3))
                    list.Add(F("TWIN_REPEATED", u.Key, null, kv.Value[0].position, string.Join(",", kv.Value.Select(x => x.name)), $"{kv.Value.Count}x the same front in one unit: " + kv.Key));
            return list;
        }

        // ------------------------------------------------------------------ props

        static readonly Dictionary<string, string> PropKind = new Dictionary<string, string>
        {
            { "ENV_Bench_Stone", "bench" }, { "ENV_Prop_Chair", "seat" }, { "ENV_Prop_Stool", "seat" }, { "ENV_Cafe_Chair", "cafe" }, { "ENV_Cafe_Table", "cafe" }, { "ENV_Parasol", "cafe" },
            { "ENV_Prop_Barrel", "goods" }, { "ENV_Prop_Barrel_Apples", "goods" }, { "ENV_Prop_Crate_Wooden", "goods" }, { "ENV_Prop_Bucket", "goods" }, { "ENV_Prop_Bucket_Wood", "goods" }, { "ENV_Prop_Bag", "goods" },
            { "ENV_Pot_Glazed", "pot" }, { "ENV_Pot_Tin", "pot" }, { "ENV_Planter_Pot", "pot" }, { "ENV_Planter_Box", "pot" }, { "ENV_Trough_Stone", "pot" },
            { "ENV_Bicycle", "bike" }, { "ENV_Bike_Rack", "bike" }, { "ENV_AFrame_Board", "board" }, { "ENV_Recycling_Bins", "service" },
        };

        /// <summary>Floor props with no human function: nothing to belong to (no wall, door or plaza near), facing a wall, or on the centreline.</summary>
        public static List<Finding> Props()
        {
            var list = new List<Finding>();
            var doors = rows.GetComponentsInChildren<Transform>(true).Where(t => t.name.StartsWith("THR_")).Select(t => t.position).ToList();
            bool IsStructure(Collider c) => !c.isTrigger && !c.name.StartsWith("Ground_") && (c.transform.IsChildOf(rows) && !Path(c.transform).Contains("/Dressing/") && !Path(c.transform).Contains("/History/") || Path(c.transform).StartsWith("River") || Path(c.transform).Contains("Parapet"));
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
            {
                if (!PropKind.TryGetValue(t.name, out var kind) || !t.gameObject.activeInHierarchy) continue;
                if (t.parent != null && PropKind.ContainsKey(t.parent.name)) continue;
                var p = t.position;
                var b = BuildingOf(t);
                string unit = b != null ? UnitOfRow(b.parent.name) : "PLAZAS";
                float gap = PublicGap(new Vector2(p.x, p.z), out var street);
                bool inPlaza = plazas.Any(pl => Inside(pl, new Vector2(p.x, p.z))) || Path(t).StartsWith("Plazas") || Path(t).StartsWith("RiverPromenade");
                if (inPlaza) unit = "PLAZAS";
                // nearest structure in 8 directions at 0.8 m, and whether one stands right in front of the prop
                float wall = 99f, front = 99f; string wallName = null;
                for (int i = 0; i < 8; i++)
                {
                    var d = Quaternion.Euler(0, i * 45f, 0) * Vector3.forward;
                    var hit = Physics.RaycastAll(p + Vector3.up * 0.8f, d, 3f).Where(h => IsStructure(h.collider) && !h.collider.transform.IsChildOf(t)).OrderBy(h => h.distance).FirstOrDefault();
                    if (hit.collider != null && hit.distance < wall) { wall = hit.distance; wallName = Path(hit.collider.transform); }
                }
                var fh = Physics.RaycastAll(p + Vector3.up * 0.8f, t.forward, 1.2f).Where(h => IsStructure(h.collider)).OrderBy(h => h.distance).FirstOrDefault();
                if (fh.collider != null) front = fh.distance;
                float door = doors.Count > 0 ? doors.Min(q => Vector3.Distance(q, p)) : 99f;
                float centre = streets.Min(s => DistToPolyline(s.pts, new Vector2(p.x, p.z)));
                var sw = streets.OrderBy(s => DistToPolyline(s.pts, new Vector2(p.x, p.z))).First().w;
                string where = Path(t);
                if (!inPlaza && kind != "cafe" && centre < 0.55f && sw < 6.6f)
                    list.Add(F("PROP_ON_CENTRELINE", unit, street, p, where, $"{t.name} {centre:0.00} m from the centreline of a {sw:0.0} m street"));
                switch (kind)
                {
                    case "bench":
                        if (front < 0.9f) list.Add(F("PROP_FACES_WALL", unit, street, p, where, $"bench faces a wall {front:0.00} m away"));
                        else if (wall > 1.2f && !inPlaza) list.Add(F("PROP_NO_ANCHOR", unit, street, p, where, $"bench in the open ({wall:0.0} m from any wall, {door:0.0} m from a door)"));
                        break;
                    case "seat":
                        if (wall > 1.4f && door > 3.5f && !inPlaza) list.Add(F("PROP_NO_ANCHOR", unit, street, p, where, $"{t.name}: no wall within {wall:0.0} m nor door within {door:0.0} m"));
                        break;
                    case "goods":
                        if (door > 4.5f && wall > 1.2f && !inPlaza) list.Add(F("PROP_NO_ANCHOR", unit, street, p, where, $"{t.name}: goods {door:0.0} m from a door and {wall:0.0} m from a wall"));
                        break;
                    case "pot":
                        if (door > 3.2f && wall > 1.0f && !inPlaza) list.Add(F("PROP_NO_ANCHOR", unit, street, p, where, $"{t.name}: {door:0.0} m from a door, {wall:0.0} m from a wall"));
                        break;
                    case "bike":
                        if (wall > 1.2f && !inPlaza) list.Add(F("PROP_NO_ANCHOR", unit, street, p, where, $"{t.name} {wall:0.0} m from any wall"));
                        break;
                    case "board":
                        if (door > 3.5f) list.Add(F("PROP_NO_ANCHOR", unit, street, p, where, $"chalkboard {door:0.0} m from the nearest door"));
                        break;
                }
            }
            return list;
        }

        // ------------------------------------------------------------------ views

        /// <summary>Two views of a finding position: from the front at 1.7 m (or from where the opening looks out, if given a
        /// direction) and a wider one from above the street, so a doubtful finding is judged by eye before it is fixed.</summary>
        public static string Look(string outFolder, string name, Vector3 at, Vector3 dirOut, float dist = 4.5f, float fov = 60f)
        {
            var pl = GameObject.Find("Player"); var saved = pl != null ? pl.transform.position : Vector3.zero;
            if (pl != null) pl.transform.position = new Vector3(0, -300, 0);
            Physics.SyncTransforms();
            dirOut.y = 0; dirOut.Normalize();
            var target = at + Vector3.up * 1.3f;
            var eye1 = EnvWalk.ClearEye(target, at + dirOut * dist + Vector3.up * 1.7f);
            EnvPreview.Capture($"{outFolder}/{name}_a.jpg", eye1, target, fov, 1100, 620);
            var eye2 = EnvWalk.ClearEye(target, at + dirOut * dist * 1.8f + Vector3.up * 4.5f);
            EnvPreview.Capture($"{outFolder}/{name}_b.jpg", eye2, target, fov, 1100, 620);
            if (pl != null) pl.transform.position = saved;
            return "ok";
        }

        // ------------------------------------------------------------------ run

        public static string Run(string outJson, string kinds = "doors,narrow,walls,blanks,windows,sides,materials,twins,props,facades,roofs,shops")
        {
            Load();
            var want = new HashSet<string>(kinds.Split(','));
            var all = new List<Finding>();
            var log = new StringBuilder();
            void Do(string name, System.Func<List<Finding>> f)
            {
                if (!want.Contains(name)) return;
                var l = f();
                all.AddRange(l);
                log.AppendLine($"{name}: {l.Count}");
            }
            Do("doors", Doors); Do("narrow", () => Narrowings()); Do("walls", Walls); Do("blanks", Blanks);
            Do("windows", Windows); Do("sides", BareSides); Do("materials", Materials); Do("twins", Twins); Do("props", Props);
            Do("facades", Facades); Do("roofs", Roofs); Do("shops", Storefronts);
            var full = System.IO.Path.Combine(Directory.GetCurrentDirectory(), outJson);
            Directory.CreateDirectory(System.IO.Path.GetDirectoryName(full));
            File.WriteAllText(full, JsonConvert.SerializeObject(all.Select(f => new { f.kind, f.unit, f.street, f.where, f.detail, x = System.Math.Round(f.x, 2), y = System.Math.Round(f.y, 2), z = System.Math.Round(f.z, 2) }), Formatting.Indented));
            var byKind = all.GroupBy(f => f.kind).OrderByDescending(g => g.Count());
            log.AppendLine("by kind: " + string.Join(", ", byKind.Select(g => g.Key + " " + g.Count())));
            var byUnit = all.GroupBy(f => f.unit).OrderBy(g => g.Key);
            log.AppendLine("by unit: " + string.Join(", ", byUnit.Select(g => g.Key + " " + g.Count())));
            return $"JD_SEMANTICS {all.Count} findings -> {outJson}\n{log}";
        }
    }
}

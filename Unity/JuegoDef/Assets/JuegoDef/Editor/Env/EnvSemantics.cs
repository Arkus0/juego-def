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
    /// Phase 1 (owner addenda 2026-09-29): missing volumes between neighbours and at open terrace ends; stairs and door steps
    /// without logic; garden walls with nothing to retain, ending in the air or sealing public space; monotone rhythm per unit
    /// (bay widths, lintel lines, ground patterns, fuzzy silhouettes); flat painted windows and glass with no room behind it;
    /// doors opening onto a falling street with no landing; floating props; unreachable gallery passages; plaza edges with no
    /// closure and twin-plaza massing.
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
        static Dictionary<string, (string west, string east)> rowEnds;   // authored closure (open/hidden/tip/concave) per row end
        static Dictionary<string, Vector2> rowDir;                       // spec dir (west -> east) per row, plan
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
            rowEnds = new Dictionary<string, (string, string)>(); rowDir = new Dictionary<string, Vector2>();
            foreach (JObject r in (JArray)spec["rows"])
            {
                rowStreet[(string)r["id"]] = (string)r["street"]; rowRole[(string)r["id"]] = (string)r["role"];
                rowEnds[(string)r["id"]] = ((string)r["ends"]["west"], (string)r["ends"]["east"]);
                rowDir[(string)r["id"]] = new Vector2((float)r["dir"][0], (float)r["dir"][1]);
            }
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
                    if (len >= 8f)
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
                            float min = kind == "all" ? 6f : 12f;
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
            if (module == null) return null;
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

        // ------------------------------------------------------------------ volume

        /// <summary>Which side section of a building faces the lower / higher local x of its row (Side_L is the west
        /// end for south rows and the east end for north rows, so it is decided geometrically, per building).</summary>
        static (string low, string high) SideOrder(Transform b, Transform row)
        {
            var l = b.Find("Side_L"); var r = b.Find("Side_R");
            if (l == null || r == null) return ("Side_L", "Side_R");
            return row.InverseTransformPoint(l.position).x <= row.InverseTransformPoint(r.position).x ? ("Side_L", "Side_R") : ("Side_R", "Side_L");
        }

        /// <summary>Missing volumes in a row: a gap between neighbours faced by a party wall (a side with no opening),
        /// and terrace ends the spec left "open" whose blank side stands visible to the street — half a building
        /// missing, the seam the eye reads as "something should be here".</summary>
        public static List<Finding> VolumeGaps()
        {
            var list = new List<Finding>();
            foreach (Transform row in rows)
            {
                var boxes = new List<(float x0, float x1, Transform b)>();
                foreach (Transform b in row)
                {
                    if (b.name == "Walls") continue;
                    float x0 = float.MaxValue, x1 = float.MinValue;
                    foreach (var r in b.GetComponentsInChildren<Renderer>())
                    {
                        var wb = r.bounds;
                        x0 = Mathf.Min(x0, row.InverseTransformPoint(wb.min).x, row.InverseTransformPoint(new Vector3(wb.max.x, wb.min.y, wb.min.z)).x);
                        x1 = Mathf.Max(x1, row.InverseTransformPoint(wb.max).x, row.InverseTransformPoint(new Vector3(wb.min.x, wb.min.y, wb.max.z)).x);
                    }
                    if (x1 > x0) boxes.Add((x0, x1, b));
                }
                boxes.Sort((p, q) => p.x0.CompareTo(q.x0));
                int Openings(Transform b, string side) { var sec = b.Find(side); return sec == null ? -1 : Bays(b, side).Count(m => m.name[0] != 'P'); }
                for (int i = 1; i < boxes.Count; i++)
                {
                    float gap = boxes[i].x0 - boxes[i - 1].x1;
                    if (gap < 1.2f) continue;
                    var orderA = SideOrder(boxes[i - 1].b, row); var orderB = SideOrder(boxes[i].b, row);
                    int innerA = Openings(boxes[i - 1].b, orderA.high); int innerB = Openings(boxes[i].b, orderB.low);
                    if (innerA != 0 && innerB != 0) continue;   // both facing sides are living walls: a side alley, not a missing house
                    var mid = row.TransformPoint(new Vector3((boxes[i - 1].x1 + boxes[i].x0) / 2f, 0, 0));
                    mid.y = EnvWalk.Ground(mid.x, mid.z, mid.y);
                    float pub = PublicGap(new Vector2(mid.x, mid.z), out var street);
                    if (pub > 3f && !VisibleFromPublic(mid + Vector3.up * 2.2f, row)) continue;   // nobody can see it
                    list.Add(F("VOLUME_GAP_ROW", UnitOfRow(row.name), rowStreet.TryGetValue(row.name, out var s) ? s : null, mid,
                        row.name + ": " + boxes[i - 1].b.name + "+" + boxes[i].b.name,
                        $"{gap:0.0} m gap between neighbours; facing side of {boxes[i - 1].b.name} {(innerA == 0 ? "has no opening (party wall)" : "has windows")}, of {boxes[i].b.name} {(innerB == 0 ? "has no opening (party wall)" : "has windows")}; {pub:0.0} m from public space"));
                }
                if (boxes.Count > 0 && rowEnds.TryGetValue(row.name, out var ends))
                {
                    bool eastIsPlus = true;
                    if (rowDir.TryGetValue(row.name, out var d)) { var right = row.right; eastIsPlus = Vector2.Dot(new Vector2(right.x, right.z), d) >= 0; }
                    void End((float x0, float x1, Transform b) box, string kind, string endName)
                    {
                        if (kind != "open") return;                       // a closure was authored (tip / concave / hidden)
                        var order = SideOrder(box.b, row);
                        string side = endName == "west" ? order.low : order.high;   // the side section facing that end of the row
                        if (Openings(box.b, side) != 0) return;          // the end wall has windows: it is a front, not a seam
                        var sec = box.b.Find(side); if (sec == null) return;
                        var p = sec.position; p.y = EnvWalk.Ground(p.x, p.z, p.y);
                        var dir = sec.forward; dir.y = 0; dir.Normalize();
                        if (Physics.Raycast(p + Vector3.up * 1.5f + dir * 0.3f, dir, 2.5f)) return;   // something stands beside it
                        if (!VisibleFromPublic(p + Vector3.up * 2.5f, box.b)) return;
                        list.Add(F("VOLUME_GAP_END", UnitOfRow(row.name), rowStreet.TryGetValue(row.name, out var s2) ? s2 : null, p,
                            row.name + ": " + box.b.name + "/" + side,
                            $"row end '{endName}' left open: the blank side of {box.b.name} faces public space with nothing behind it"));
                    }
                    End(boxes[0], eastIsPlus ? ends.west : ends.east, "west");
                    End(boxes[boxes.Count - 1], eastIsPlus ? ends.east : ends.west, "east");
                }
            }
            return list;
        }

        // ------------------------------------------------------------------ stairs

        /// <summary>Stairs and door steps that make no sense to a person: an escalinata that stops short of its door or
        /// runs past its opening, whose landing is narrower than the door, that disembarks on a way with no room, or
        /// that climbs to nothing; and door steps floating over the terrain, buried by it, or serving no door.</summary>
        public static List<Finding> StairLogic()
        {
            var list = new List<Finding>();
            var doors = rows.GetComponentsInChildren<Transform>(true).Where(t => t.name.StartsWith("THR_")).Select(t => t.position).ToList();
            foreach (JObject s in (JArray)spec["stairs"])
            {
                string id = (string)s["id"];
                var pts = ((JArray)s["pts"]).Select(c => new Vector3((float)c[0], (float)c[2], (float)c[1])).ToList();
                float w = (float)s["width"];
                var a = pts[0]; var b = pts[pts.Count - 1];
                if (a.y > b.y) (a, b) = (b, a);
                var dv = b - a; dv.y = 0; float len = dv.magnitude; dv /= len;
                string unit = UnitOfStreet(id);
                if (w < 1.2f) list.Add(F("STAIR_NARROW_LANDING", unit, id, a, "Stairs/" + id, $"landing {w:0.0} m wide, narrower than the door it serves"));
                (float dist, Vector3 p)? door = null;
                foreach (var q in doors)
                {
                    float dd = Vector2.Distance(new Vector2(q.x, q.z), new Vector2(b.x, b.z));
                    if (dd < 6f && (door == null || dd < door.Value.dist)) door = (dd, q);
                }
                if (door != null)
                {
                    var q = door.Value.p;
                    float t = Vector2.Dot(new Vector2(q.x - a.x, q.z - a.z), new Vector2(dv.x, dv.z));
                    float lat = Mathf.Abs((q.x - a.x) * dv.z - (q.z - a.z) * dv.x);
                    if (lat < w / 2f + 0.45f)
                    {
                        float past = len - t;    // > 0: the door stands beyond the top tread; < 0: the stair runs past the door line
                        if (past > 1.2f) list.Add(F("STAIR_SHORT_OF_DOOR", unit, id, b, "Stairs/" + id, $"top tread {past:0.0} m before the door it serves (door {door.Value.dist:0.0} m from the top end)"));
                        if (past < -0.35f) list.Add(F("STAIR_PAST_DOOR", unit, id, b, "Stairs/" + id, $"stair runs {-past:0.00} m past the door line: the first tread is inside its opening"));
                    }
                }
                var n = new Vector3(-dv.z, 0, dv.x);
                var (dl, _) = Probe(a + Vector3.up * 1.4f, -n); var (dr, _) = Probe(a + Vector3.up * 1.4f, n);
                if (dl < 9f && dr < 9f && dl + dr < 2.5f)
                    list.Add(F("STAIR_LANDS_NARROW", unit, id, a, "Stairs/" + id, $"disembarks with {dl + dr:0.0} m free across the way (needs 2.5 m)"));
                bool doorNear = doors.Any(q => Vector2.Distance(new Vector2(q.x, q.z), new Vector2(b.x, b.z)) < 6f);
                float pubTop = PublicGap(new Vector2(b.x, b.z), out _);
                if (!doorNear && pubTop > 4f && PublicGap(new Vector2(a.x, a.z), out _) > 4f)
                    list.Add(F("STAIR_TO_NOTHING", unit, id, b, "Stairs/" + id, $"no door within 6 m of the top and {pubTop:0.0} m from any street or plaza: climbs to nothing"));
            }
            foreach (var t in rows.GetComponentsInChildren<Transform>(true))
            {
                if (t.name != "ENV_Door_Step") continue;
                if (t.parent != null && t.parent.name == "ENV_Door_Step") continue;   // the step nests a mesh child of its own name
                var b = BuildingOf(t); if (b == null) continue;
                var rs = t.GetComponentsInChildren<Renderer>(); if (rs.Length == 0) continue;
                var bb = rs[0].bounds; foreach (var r in rs) bb.Encapsulate(r.bounds);
                var p = t.position; string unit = UnitOfRow(b.parent.name);
                float g = EnvWalk.Ground(p.x, p.z, float.NaN);
                if (!VisibleFromPublic(p + Vector3.up * 0.2f, b)) continue;
                if (float.IsNaN(g)) list.Add(F("STEP_FLOATS", unit, null, p, Path(t), "no ground under the door step"));
                else if (bb.min.y - g > 0.18f) list.Add(F("STEP_FLOATS", unit, null, p, Path(t), $"step floats {bb.min.y - g:0.00} m over the ground"));
                else if (g - bb.max.y > 0.08f) list.Add(F("STEP_BURIED", unit, null, p, Path(t), $"ground {g - bb.max.y:0.00} m above the step: invisible"));
                if (!doors.Any(q => Vector2.Distance(new Vector2(q.x, q.z), new Vector2(p.x, p.z)) < 1.4f))
                    list.Add(F("STEP_ORPHAN", unit, null, p, Path(t), "no door within 1.4 m of the step"));
            }
            return list;
        }

        // ------------------------------------------------------------------ walls

        /// <summary>Garden and retaining walls with no reason to be: holding back no level change at all, ending in the
        /// air with no pier, gate, corner or building to anchor them, floating over the terrain, or sealing a long
        /// stretch of public space with no access through. Covers the row Walls groups and the backdrop hillside runs.</summary>
        public static List<Finding> WallSense()
        {
            var list = new List<Finding>();
            var doors = rows.GetComponentsInChildren<Transform>(true).Where(t => t.name.StartsWith("THR_")).Select(t => t.position).ToList();
            // one wall piece in world terms: cut = a gate or pier breaks the run there
            void Audit(List<(Vector3 p, float y0, float y1, bool cut, string path)> pieces, string unit, string tag)
            {
                if (pieces.Count < 2) return;
                var used = new bool[pieces.Count];
                int Chain(int seed, List<int> run)
                {
                    used[seed] = true; run.Add(seed);
                    int last = seed;
                    while (true)
                    {
                        int best = -1; float bd = 2.7f;
                        for (int j = 0; j < pieces.Count; j++)
                        {
                            if (used[j]) continue;
                            float d = Vector3.Distance(pieces[j].p, pieces[last].p);
                            if (d < bd) { bd = d; best = j; }
                        }
                        if (best < 0) break;
                        used[best] = true; run.Add(best); last = best;
                    }
                    return run.Count;
                }
                var runs = new List<List<int>>();
                for (int i = 0; i < pieces.Count; i++) if (!used[i]) runs.Add(new List<int>(Chain(i, new List<int>())));
                foreach (var run in runs.OrderByDescending(r => r.Count))
                {
                    if (run.Count < 2) continue;
                    var ps = run.Select(i => pieces[i]).ToList();
                    float len = 2f; for (int i = 1; i < ps.Count; i++) len += Vector3.Distance(ps[i - 1].p, ps[i].p);
                    var first = ps[0]; var last = ps[ps.Count - 1];
                    var mid = (first.p + last.p) / 2f;
                    var dir = last.p - first.p; dir.y = 0; float l2 = dir.magnitude; if (l2 < 0.5f) continue; dir /= l2;
                    var nrm = new Vector3(-dir.z, 0, dir.x);
                    bool gate = ps.Any(p => p.cut);
                    bool doorNear = doors.Any(q => ps.Any(p => Vector2.Distance(new Vector2(q.x, q.z), new Vector2(p.p.x, p.p.z)) < 3.5f));
                    float pub = PublicGap(new Vector2(mid.x, mid.z), out var street);
                    mid.y = EnvWalk.Ground(mid.x, mid.z, mid.y);
                    // retaining nothing: flat ground on both sides along the whole run, no gate, no door, and near public space
                    if (len >= 6f && !gate && !doorNear && pub < 4f)
                    {
                        bool retains = false;
                        for (int k = 1; k <= 3 && !retains; k++)
                        {
                            var q = first.p + (last.p - first.p) * (k / 4f);
                            var gl = EnvWalk.Ground(q.x + nrm.x * 0.6f, q.z + nrm.z * 0.6f, float.NaN);
                            var gr = EnvWalk.Ground(q.x - nrm.x * 0.6f, q.z - nrm.z * 0.6f, float.NaN);
                            if (float.IsNaN(gl) || float.IsNaN(gr) || Mathf.Abs(gl - gr) > 0.22f) retains = true;
                        }
                        if (!retains)
                            list.Add(F("WALL_RETAINS_NOTHING", unit, street, mid, tag + " run " + ps[0].path, $"{len:0.0} m of wall on flat ground (level change under 0.22 m on both sides), no gate, no door: holds back nothing"));
                    }
                    // dead frontage: a long wall along public space with no access through anywhere
                    if (len >= 14f && !gate && !doorNear && pub < 2.5f)
                        list.Add(F("WALL_NO_ACCESS", unit, street, mid, tag + " run " + ps[0].path, $"{len:0.0} m along public space with no gate, door or gap"));
                    // floating: base clearly above the ground under it
                    int floats = 0; float worst = 0;
                    foreach (var p in ps)
                    {
                        float g = EnvWalk.Ground(p.p.x, p.p.z, float.NaN);
                        float gap = float.IsNaN(g) ? 1f : p.y0 - g;
                        if (gap > 0.3f) { floats++; worst = Mathf.Max(worst, gap); }
                    }
                    if (floats >= 2 && pub < 8f)
                        list.Add(F("WALL_FLOATS", unit, street, mid, tag + " run " + ps[0].path, $"{floats} of {ps.Count} pieces float over the terrain (worst {worst:0.00} m)"));
                    // ends in the air: no anchor at the free ends of the run
                    void EndTip((Vector3 p, float y0, float y1, bool cut, string path) piece, Vector3 outDir)
                    {
                        var e = piece.p + outDir * 1.1f;
                        if (Physics.OverlapSphere(e, 2.5f).Any(c => !c.isTrigger && c.transform.IsChildOf(rows) && !c.name.StartsWith("Ground_"))) return;   // a building takes it
                        if (pieces.Any(p => p.cut && Vector3.Distance(p.p, piece.p) < 2.3f)) return;                                                        // dies on its own gate or pier
                        var beyond = piece.p + outDir * 2.6f;
                        float g1 = EnvWalk.Ground(piece.p.x, piece.p.z, float.NaN), g2 = EnvWalk.Ground(beyond.x, beyond.z, float.NaN);
                        if (!float.IsNaN(g1) && !float.IsNaN(g2) && Mathf.Abs(g2 - g1) > 0.5f) return;                                                      // dies into a real level change
                        if (!VisibleFromPublic(piece.p + Vector3.up * 1.2f, null)) return;
                        list.Add(F("WALL_ENDS_AIR", unit, street, piece.p, tag + " " + piece.path, $"wall run ends in the air: no building, gate, corner or level change within 2.5 m"));
                    }
                    if (len >= 4f) { EndTip(first, -dir); EndTip(last, dir); }
                }
            }
            foreach (Transform row in rows)
            {
                var g = row.Find("Walls"); if (g == null) continue;
                var pieces = new List<(Vector3, float, float, bool, string)>();
                foreach (Transform t in g)
                {
                    if (t.name == "ENV_Gate_Timber") { pieces.Add((t.position, 0, 0, true, Path(t))); continue; }
                    if (t.name.StartsWith("ENV_Retaining_Wall"))
                    {
                        var r = t.GetComponentInChildren<Renderer>();
                        if (t.localScale.x < 0.4f) { pieces.Add((t.position, 0, 0, true, Path(t))); continue; }   // pier
                        if (r != null) pieces.Add((t.position, r.bounds.min.y, r.bounds.max.y, false, Path(t)));
                    }
                }
                Audit(pieces, UnitOfRow(row.name), row.name);
            }
            var bd = root.Find("Backdrop");
            if (bd != null)
            {
                var pieces = new List<(Vector3, float, float, bool, string)>();
                foreach (Transform t in bd)
                    if (t.name.StartsWith("ENV_Retaining_Wall"))
                    {
                        var r = t.GetComponentInChildren<Renderer>();
                        if (r != null) pieces.Add((t.position, r.bounds.min.y, r.bounds.max.y, false, Path(t)));
                    }
                Audit(pieces.OrderByDescending(p => Vector2.Distance(new Vector2(p.Item1.x, p.Item1.z), new Vector2(96, 116))).ToList(), "BACKDROP", "Backdrop");
            }
            return list;
        }

        // ------------------------------------------------------------------ rhythm

        /// <summary>Rhythm per unit: frontage widths with no variance, one lintel line for every upper window, one
        /// ground-floor pattern for most fronts, and the same fuzzy silhouette (bay count + floors + wall and roof
        /// material, not the exact fronts) stamped across the unit.</summary>
        public static List<Finding> Rhythm()
        {
            var list = new List<Finding>();
            var per = new Dictionary<string, List<(Transform b, string row, int bays, int floors, string f0, string wall, string roof)>>();
            var lintels = new Dictionary<string, HashSet<float>>();
            var lintelN = new Dictionary<string, int>();
            foreach (Transform row in rows)
                foreach (Transform b in row)
                {
                    if (b.name == "Walls") continue;
                    var front = b.Find("Front"); var f0 = front?.Find("F0"); if (front == null || f0 == null) continue;
                    string unit = UnitOfRow(row.name);
                    int bays = f0.childCount, floors = front.childCount;
                    var f0codes = new string(f0.Cast<Transform>().OrderBy(m => int.TryParse(m.name.Substring(m.name.IndexOf('_') + 1), out var bi) ? bi : 99).Select(m => m.name[0]).ToArray());
                    var wall = WallMaterial(f0.Cast<Transform>().FirstOrDefault(m => m.name[0] == 'P')) ?? "-";
                    var roofR = b.Find("Roof")?.GetComponentInChildren<Renderer>();
                    var roof = roofR != null && roofR.sharedMaterial != null ? roofR.sharedMaterial.name.Replace("_G", "") : "-";
                    if (!per.ContainsKey(unit)) per[unit] = new List<(Transform, string, int, int, string, string, string)>();
                    per[unit].Add((b, row.name, bays, floors, f0codes, wall, roof));
                    int fl = 0;
                    foreach (Transform f in front)
                    {
                        if (fl >= 1)
                            foreach (Transform m in f)
                                if ("WwTc".IndexOf(m.name[0]) >= 0)
                                {
                                    var rs = m.GetComponentsInChildren<Renderer>(); if (rs.Length == 0) continue;
                                    float top = float.MinValue; foreach (var r in rs) top = Mathf.Max(top, r.bounds.max.y);
                                    float floorLine = b.TransformPoint(new Vector3(0, (fl + 1) * BuildingAssembler.Storey, 0)).y;
                                    if (!lintels.ContainsKey(unit)) { lintels[unit] = new HashSet<float>(); lintelN[unit] = 0; }
                                    lintels[unit].Add(Mathf.Round((top - floorLine) * 10f) / 10f);
                                    lintelN[unit]++;
                                }
                        fl++;
                    }
                }
            foreach (var u in per.Where(e => e.Value.Count >= 6))
            {
                var bs = u.Value;
                var widths = bs.Select(x => x.bays * 2f).ToList();
                float mean = widths.Average();
                float sd = Mathf.Sqrt(widths.Sum(x => (x - mean) * (x - mean)) / widths.Count);
                if (sd < 0.75f)
                    list.Add(F("RHYTHM_MONO_WIDTHS", u.Key, null, bs[bs.Count / 2].b.position, string.Join(",", bs.Select(x => x.row + "/" + x.b.name).Take(6)),
                        $"{bs.Count} fronts with a frontage stdev of {sd:0.00} m (mean {mean:0.0} m): the same bay width all along"));
                var top = bs.GroupBy(x => x.f0).OrderByDescending(g => g.Count()).First();
                if (top.Count() * 1f / bs.Count >= 0.55f && top.Count() >= 5)
                    list.Add(F("RHYTHM_MONO_GROUND", u.Key, null, top.First().b.position, string.Join(",", top.Select(x => x.row + "/" + x.b.name).Take(6)),
                        $"{top.Count()} of {bs.Count} fronts share the ground-floor pattern {top.Key}"));
                var sil = bs.GroupBy(x => (x.bays, x.floors, x.wall, x.roof)).OrderByDescending(g => g.Count()).First();
                if (sil.Count() * 1f / bs.Count >= 0.4f && sil.Count() >= 5)
                    list.Add(F("RHYTHM_MONO_SILHOUETTE", u.Key, null, sil.First().b.position, string.Join(",", sil.Select(x => x.row + "/" + x.b.name).Take(6)),
                        $"{sil.Count()} of {bs.Count} fronts share one silhouette: {sil.Key.bays} bays x {sil.Key.floors} floors, {sil.Key.wall}, roof {sil.Key.roof}"));
            }
            foreach (var kv in lintels.Where(e => lintelN[e.Key] >= 8 && e.Value.Count <= 2))
                list.Add(F("RHYTHM_MONO_LINTELS", kv.Key, null, per[kv.Key][0].b.position, per[kv.Key].Count + " fronts",
                    $"every upper window cuts its lintel at the same {string.Join(" / ", kv.Value.Select(v => v.ToString("0.0")))} m below the floor line ({lintelN[kv.Key]} windows)"));
            return list;
        }

        // ------------------------------------------------------------------ glass

        /// <summary>Windows that cheat the eye: flat painted rectangles with no reveal depth (the kit window is a
        /// recessed box), and glazing with no room behind it — no interior material, the glass shows the void.</summary>
        public static List<Finding> WindowDepth()
        {
            var list = new List<Finding>();
            var fake = new Dictionary<Transform, int>();
            var voids = new Dictionary<Transform, int>();
            foreach (Transform row in rows)
                foreach (Transform b in row)
                {
                    if (b.name == "Walls") continue;
                    foreach (var section in new[] { "Front", "Side_L", "Side_R", "Back" })
                    {
                        var sec = b.Find(section); if (sec == null) continue;
                        foreach (Transform f in sec)
                            foreach (Transform m in f)
                            {
                                if (!WindowCodes.Contains(m.name[0])) continue;
                                var rs = m.GetComponentsInChildren<Renderer>(); if (rs.Length == 0) continue;
                                float minF = float.MaxValue, maxF = float.MinValue; bool glass = false, room = false;
                                foreach (var r in rs)
                                    foreach (var mat in r.sharedMaterials)
                                    {
                                        if (mat == null) continue;
                                        if (mat.name.StartsWith("ENV_Interior_")) room = true;
                                        if (mat.name.Contains("Glass")) glass = true;
                                    }
                                foreach (var r in rs)
                                {
                                    var wb = r.bounds;
                                    foreach (var corner in new[] { wb.min, wb.max, new Vector3(wb.min.x, wb.min.y, wb.max.z), new Vector3(wb.max.x, wb.min.y, wb.min.z) })
                                    {
                                        float d = Vector3.Dot(corner - m.position, m.forward);
                                        minF = Mathf.Min(minF, d); maxF = Mathf.Max(maxF, d);
                                    }
                                }
                                if (maxF - minF < 0.09f) { fake[b] = fake.TryGetValue(b, out var c) ? c + 1 : 1; continue; }
                                if (glass && !room) voids[b] = voids.TryGetValue(b, out var c2) ? c2 + 1 : 1;
                            }
                    }
                }
            foreach (var kv in fake.Where(e => VisibleFromPublic(e.Key.position + Vector3.up * 4f, e.Key)))
                list.Add(F("WINDOW_FAKE", UnitOfRow(kv.Key.parent.name), null, kv.Key.position, Path(kv.Key), $"{kv.Value} windows are flat planes with no reveal depth (the kit window is a recessed box)"));
            foreach (var kv in voids.Where(e => VisibleFromPublic(e.Key.position + Vector3.up * 4f, e.Key)))
                list.Add(F("WINDOW_INTO_VOID", UnitOfRow(kv.Key.parent.name), null, kv.Key.position, Path(kv.Key), $"{kv.Value} glazed windows show no room behind: plain glass, the void shows through"));
            return list;
        }

        // ------------------------------------------------------------------ thresholds and props

        /// <summary>Doors that open straight onto a falling street: the ground drops across the threshold (no flat
        /// landing) or falls away just past the sill, and no step or tread covers it.</summary>
        public static List<Finding> Landings()
        {
            var list = new List<Finding>();
            foreach (var t in rows.GetComponentsInChildren<Transform>(true))
            {
                if (!t.name.StartsWith("THR_")) continue;
                var b = BuildingOf(t); if (b == null) continue;
                var p = t.position; var f = t.forward; f.y = 0; f.Normalize();
                var rgt = new Vector3(f.z, 0, -f.x);
                float G(float lat, float d) => EnvWalk.Ground(p.x + f.x * d + rgt.x * lat, p.z + f.z * d + rgt.z * lat, float.NaN);
                bool step = Physics.OverlapSphere(p + f * 0.5f, 1.2f).Any(c => !c.isTrigger && (c.name == "ENV_Door_Step" || c.name.EndsWith("_Treads")));
                if (step) continue;   // a worn step or tread is the landing
                var g0 = G(0, 0.6f); var gl = G(-0.55f, 0.6f); var gr = G(0.55f, 0.6f);
                var vals = new[] { g0, gl, gr }.Where(g => !float.IsNaN(g)).ToList();
                if (vals.Count >= 2 && vals.Max() - vals.Min() > 0.28f && VisibleFromPublic(p + Vector3.up * 1.2f, b))
                    list.Add(F("DOOR_NO_LANDING", UnitOfRow(b.parent.name), null, p, Path(t), $"the street falls {vals.Max() - vals.Min():0.00} m across the threshold (0.6 m out): the door opens onto the slope, no landing"));
                var g1 = G(0, 0.1f); var g9 = G(0, 0.9f);
                if (!float.IsNaN(g1) && !float.IsNaN(g9) && Mathf.Abs(g1 - p.y) < 0.2f && g9 < p.y - 0.45f && VisibleFromPublic(p + Vector3.up * 1.2f, b))
                    list.Add(F("DOOR_NO_LANDING", UnitOfRow(b.parent.name), null, p, Path(t), $"level at the sill but the ground drops {p.y - g9:0.00} m by 0.9 m out: the street falls away right past the threshold"));
            }
            return list;
        }

        /// <summary>Props with no ground to stand on: floating above the terrain, or perched on a near-vertical face of
        /// a sloping street with no ledge under them.</summary>
        public static List<Finding> FloatingProps()
        {
            var list = new List<Finding>();
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
            {
                if (!PropKind.TryGetValue(t.name, out var kind) || !t.gameObject.activeInHierarchy) continue;
                if (t.parent != null && PropKind.ContainsKey(t.parent.name)) continue;
                var p = t.position;
                if (PublicGap(new Vector2(p.x, p.z), out var street) > 8f) continue;
                var rs = t.GetComponentsInChildren<Renderer>(); if (rs.Length == 0) continue;
                var bb = rs[0].bounds; foreach (var r in rs) bb.Encapsulate(r.bounds);
                var b = BuildingOf(t);
                string unit = b != null ? UnitOfRow(b.parent.name) : "PLAZAS";
                var hits = Physics.RaycastAll(new Vector3(p.x, bb.max.y + 0.3f, p.z), Vector3.down, 8f)
                    .Where(h => !h.collider.isTrigger && !h.collider.transform.IsChildOf(t)).OrderBy(h => h.distance).ToArray();
                // effective support: the nearest surface under it (a step, a sill, a wall the prop stands on), but seam-safe
                // for the pavement itself — a single ray falls through a seam between ground meshes onto whatever lies below
                float g = EnvWalk.Ground(bb.center.x, bb.center.z, float.NaN);
                float top = hits.Length > 0 ? hits[0].point.y : float.NaN;
                float support = float.IsNaN(g) ? top : float.IsNaN(top) ? g : Mathf.Max(g, top);
                if (float.IsNaN(support)) { list.Add(F("PROP_FLOAT", unit, street, p, Path(t), $"{t.name}: no ground within 8 m below it")); continue; }
                float gap = bb.min.y - support;
                if (gap > 0.2f) list.Add(F("PROP_FLOAT", unit, street, p, Path(t), $"{t.name} floats {gap:0.00} m above the ground"));
                else if (hits.Length > 0 && Vector3.Angle(hits[0].normal, Vector3.up) > 32f)
                    list.Add(F("PROP_FLOAT", unit, street, p, Path(t), $"{t.name} perched on a {Vector3.Angle(hits[0].normal, Vector3.up):0}° slope with no ledge"));
            }
            return list;
        }

        /// <summary>Gallery bays and bridging pieces with no way up: a passage above head height whose floor aligns
        /// with no door threshold, with nothing supporting its ends.</summary>
        public static List<Finding> Passages()
        {
            var list = new List<Finding>();
            var doors = rows.GetComponentsInChildren<Transform>(true).Where(t => t.name.StartsWith("THR_")).Select(t => t.position).ToList();
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
            {
                if (t.name != "ENV_Gallery_Bay" || !t.gameObject.activeInHierarchy) continue;
                var rs = t.GetComponentsInChildren<Renderer>(); if (rs.Length == 0) continue;
                var bb = rs[0].bounds; foreach (var r in rs) bb.Encapsulate(r.bounds);
                var c = bb.center;
                float g = EnvWalk.Ground(c.x, c.z, float.NaN);
                if (float.IsNaN(g)) continue;
                float h = bb.min.y - g;
                if (h < 1.9f) continue;   // reachable from the ground below
                if (doors.Any(q => Mathf.Abs(q.y - bb.min.y) < 1.4f && Vector2.Distance(new Vector2(q.x, q.z), new Vector2(c.x, c.z)) < 6f)) continue;   // a door opens at its floor
                var ends = new[] { bb.min + Vector3.right * 0.2f, bb.max - Vector3.right * 0.2f };
                bool supported = false;
                foreach (var e in ends)
                    if (Physics.OverlapSphere(new Vector3(e.x, bb.min.y - 0.6f, e.z), 0.8f).Any(col => !col.isTrigger && !col.transform.IsChildOf(t)))
                        supported = true;
                if (supported) continue;
                var b = BuildingOf(t);
                if (!VisibleFromPublic(c, b)) continue;
                list.Add(F("PASSAGE_FLOAT", b != null ? UnitOfRow(b.parent.name) : "OTHER", null, c, Path(t),
                    $"gallery floor {h:0.0} m above the ground, no door at its level within 6 m, nothing under its ends"));
            }
            return list;
        }

        /// <summary>Notices (se vende, se alquila...) stamped twice at the same height on one front: the eye reads the
        /// duplication before it reads the sign.</summary>
        public static List<Finding> SignDuplicates()
        {
            var list = new List<Finding>();
            var signs = new List<(Vector3 p, string mat, Transform t)>();
            foreach (var t in rows.GetComponentsInChildren<Transform>(true))
                if (t.name == "ENV_Sign_Panel" && t.gameObject.activeInHierarchy)
                {
                    var r = t.GetComponentInChildren<Renderer>();
                    var mat = r != null && r.sharedMaterial != null ? r.sharedMaterial.name : "?";
                    if (!mat.Contains("Notice")) continue;
                    signs.Add((t.position, mat, t));
                }
            for (int i = 0; i < signs.Count; i++)
                for (int j = i + 1; j < signs.Count; j++)
                    if (signs[i].mat == signs[j].mat
                        && Mathf.Abs(signs[i].p.y - signs[j].p.y) < 0.15f
                        && Vector2.Distance(new Vector2(signs[i].p.x, signs[i].p.z), new Vector2(signs[j].p.x, signs[j].p.z)) < 3.5f)
                    {
                        var b = BuildingOf(signs[i].t);
                        list.Add(F("SIGN_FLOAT", b != null ? UnitOfRow(b.parent.name) : "OTHER", null, (signs[i].p + signs[j].p) / 2f,
                            Path(signs[i].t) + " + " + Path(signs[j].t), $"two '{signs[i].mat}' notices at the same height within 3.5 m"));
                    }
            return list;
        }

        // ------------------------------------------------------------------ plazas

        /// <summary>Plaza borders: pavement that ends with no building or wall to close it (it drains onto the
        /// hillside instead of onto a facade), and twin plazas ringed by the same massing.</summary>
        public static List<Finding> PlazaEdges()
        {
            var list = new List<Finding>();
            var sigs = new List<(Vector2 c, int floors, string wall, string roof, int n)>();
            foreach (var pl in plazas)
            {
                var cx = pl.Average(p => p.x); var cz = pl.Average(p => p.y);
                float open = 0; Vector3 worst = Vector3.zero; float worstOpen = 0;
                var closed = new List<Vector2>(pl) { pl[0] };
                for (int i = 0; i + 1 < closed.Count; i++)
                {
                    var a = closed[i]; var b2 = closed[i + 1];
                    var seg = b2 - a; float l = seg.magnitude; if (l < 0.01f) continue;
                    var nrm = new Vector2(-seg.y, seg.x) / l;
                    if (nrm.x * (a.x - cx) + nrm.y * (a.y - cz) < 0) nrm = -nrm;   // outward
                    for (float t = 1.5f; t < l; t += 3f)
                    {
                        var q = a + seg * (t / l);
                        var probe = new Vector3(q.x + nrm.x * 4f, 1.5f, q.y + nrm.y * 4f);
                        if (Inside(channel, new Vector2(probe.x, probe.z))) continue;          // opens onto the river by design
                        if (PublicGap(new Vector2(probe.x, probe.z), out _) < 2.5f) continue;  // a street continues there
                        bool hit = Physics.RaycastAll(new Vector3(q.x + nrm.x * 1.2f, 1.5f, q.y + nrm.y * 1.2f), new Vector3(nrm.x, 0, nrm.y), 5f)
                            .Any(h => !h.collider.isTrigger && h.collider.transform.IsChildOf(rows));
                        if (!hit)
                        {
                            open += 3f;
                            if (open > worstOpen) { worstOpen = open; worst = new Vector3(q.x, EnvWalk.Ground(q.x, q.y, 0), q.y); }
                        }
                        else worstOpen = Mathf.Max(0f, worstOpen - 0f);
                    }
                }
                if (open >= 8f)
                    list.Add(F("PLAZA_NOT_CLOSED", "PLAZAS", null, worst, "plaza near (" + cx.ToString("0") + "," + cz.ToString("0") + ")",
                        $"{open:0} m of plaza edge with no building or wall within 5 m outside: the pavement ends and the space drains away"));
                // massing signature: the fronts that stand within 15 m of the polygon
                var bs = new List<(int floors, string wall, string roof)>();
                foreach (Transform row in rows)
                    foreach (Transform bld in row)
                    {
                        if (bld.name == "Walls") continue;
                        var q = new Vector2(bld.position.x, bld.position.z);
                        if (DistToPolygonEdge(pl, q) < 15f && !Inside(pl, q))
                        {
                            var front = bld.Find("Front"); if (front == null) continue;
                            var wallR = WallMaterial(front.Find("F0")?.Cast<Transform>().FirstOrDefault(m => m.name[0] == 'P')) ?? "-";
                            var roofR = bld.Find("Roof")?.GetComponentInChildren<Renderer>();
                            bs.Add((front.childCount, wallR, roofR != null && roofR.sharedMaterial != null ? roofR.sharedMaterial.name.Replace("_G", "") : "-"));
                        }
                    }
                if (bs.Count >= 5)
                {
                    var dom = bs.GroupBy(x => x).OrderByDescending(g => g.Count()).First();
                    sigs.Add((new Vector2(cx, cz), dom.Key.floors, dom.Key.wall, dom.Key.roof, dom.Count()));
                }
            }
            for (int i = 0; i < sigs.Count; i++)
                for (int j = i + 1; j < sigs.Count; j++)
                    if (sigs[i].floors == sigs[j].floors && sigs[i].wall == sigs[j].wall && sigs[i].roof == sigs[j].roof && sigs[i].n >= 5 && sigs[j].n >= 5)
                        list.Add(F("PLAZA_TWIN_ROWS", "PLAZAS", null, new Vector3(sigs[i].c.x, 0, sigs[i].c.y), "plazas " + sigs[i].c + " + " + sigs[j].c,
                            $"two plazas ringed by the same massing: {sigs[i].floors} floors, {sigs[i].wall}, roof {sigs[i].roof} ({sigs[i].n} and {sigs[j].n} fronts)"));
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

        public static string Run(string outJson, string kinds = "doors,narrow,walls,blanks,windows,sides,materials,twins,props,facades,roofs,shops,volume,stairs,wallsense,rhythm,windowdepth,landings,floaters,passages,plazas,signs")
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
            Do("volume", VolumeGaps); Do("stairs", StairLogic); Do("wallsense", WallSense); Do("rhythm", Rhythm);
            Do("windowdepth", WindowDepth); Do("landings", Landings); Do("floaters", FloatingProps); Do("passages", Passages); Do("plazas", PlazaEdges); Do("signs", SignDuplicates);
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

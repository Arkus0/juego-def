using System.Collections.Generic;
using System.Linq;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// Hand-authored micro-polish of the district (owner brief 2026-09-29: "SI FUNCIONA -> CONSERVAR, SI ESTA MAL ->
    /// CORREGIR", street by street). The district scene is generated, so every local correction lives in one committed
    /// data file, <c>Env/Specs/districts/&lt;id&gt;.polish.json</c>, and survives a rebuild:
    /// <list type="bullet">
    /// <item><c>plots</c>: per-building <see cref="BuildingSpec"/> field overrides keyed by building id
    /// (<c>"K4_0_2": { "family": "zocalo", "quoins": "none" }</c>), applied after the character pass.</item>
    /// <item><c>ops</c>: object-level corrections on the built district (<c>remove</c>, <c>move</c>, <c>place</c>), found by
    /// module name near a world point, applied at the end of <see cref="EnvDistrict.Finish"/>.</item>
    /// </list>
    /// Every entry carries <c>unit</c> (inspection unit, e.g. STREET_A) and <c>why</c> (the observed problem), so the
    /// file reads as the log of the pass. <see cref="RebuildRow"/> rebuilds one row live for the observe step.
    /// </summary>
    public static class EnvPolish
    {
        static string DocPath => $"{EnvDistrict.DistrictSpecs}/ENV01_Casco_District.polish.json";
        static JObject doc;

        public static void Reload() => doc = null;

        static JObject Doc
        {
            get
            {
                if (doc != null) return doc;
                doc = System.IO.File.Exists(DocPath) ? JObject.Parse(EnvKit.ReadText(DocPath)) : new JObject();
                return doc;
            }
        }

        /// <summary>Overrides computed during the build itself (physical checks after the rows exist), by building id; cleared by
        /// <see cref="EnvDistrict.Begin"/>. They apply on top of the file, so a second build of the row sees them.</summary>
        public static readonly Dictionary<string, JObject> Auto = new Dictionary<string, JObject>();

        /// <summary>Per-building overrides (any <see cref="BuildingSpec"/> field), by building id ("K4_0_2").</summary>
        public static void ApplyPlot(BuildingSpec bs)
        {
            if (Doc["plots"] is JObject plots && plots[bs.id] is JObject o)
            {
                var fields = (JObject)o.DeepClone();
                fields.Remove("unit"); fields.Remove("why"); fields.Remove("class");
                JsonConvert.PopulateObject(fields.ToString(), bs);
            }
            if (Auto.TryGetValue(bs.id, out var a)) JsonConvert.PopulateObject(a.ToString(), bs);
        }

        /// <summary>Physical check after all rows are built: a side or back wall whose windows look at another building within
        /// 1.3 m (walls 0.15-1.2 m apart the spec footprints do not show) is rebuilt without windows on that wall. Returns a summary.</summary>
        public static string FixBlockedOpenings(Transform root)
        {
            // a rebuilt wall can move its neighbour's face (a window recess becomes a plain face 1 cm from the next building),
            // so the check repeats until nothing is left, at most three times
            var log = new StringBuilder();
            var openDone = new HashSet<string>();   // a wall gets the windows of an open wall once, never again (no add / remove ping-pong)
            for (int iter = 0; iter < 3; iter++)
            {
                var (buildings, rowsN) = FixBlockedOnce(root, openDone);
                log.Append($"[{iter}: {buildings} buildings, {rowsN} rows] ");
                if (buildings == 0) break;
            }
            return "JD_POLISH auto (windows that look at another building within 1.3 m): " + log;
        }

        static (int buildings, int rows) FixBlockedOnce(Transform root, HashSet<string> openDone)
        {
            var rowsT = root.Find("Rows");
            var todo = new Dictionary<string, JObject>(); var rowsToRebuild = new HashSet<string>();
            Physics.SyncTransforms();
            foreach (Transform row in rowsT)
                foreach (Transform b in row)
                {
                    if (b.name == "Walls") continue;
                    foreach (var (section, field, blockField) in new[] { ("Side_L", "left", ""), ("Side_R", "right", ""), ("Back", "", "blockBack") })
                    {
                        var sec = b.Find(section); if (sec == null) continue;
                        bool any = false;
                        var codes = new List<string>();   // per floor, slot by slot, with the blocked windows turned into plain wall
                        foreach (Transform f in sec)
                        {
                            var sb = new System.Text.StringBuilder();
                            foreach (Transform m in f)
                            {
                                char c = m.name[0];
                                if ("WwTcBILN".IndexOf(c) >= 0 &&
                                    Physics.RaycastAll(m.position + Vector3.up * 1.5f + m.forward * 0.08f, m.forward, 1.3f).Any(h => !h.collider.isTrigger && !h.collider.name.StartsWith("Ground_") && !h.collider.transform.IsChildOf(b)))
                                { c = 'P'; any = true; }
                                sb.Append(c);
                            }
                            codes.Add(sb.ToString());
                        }
                        // the reverse case: a side wall with air in front of it and no opening at all. The spec calls a block tip "hidden by
                        // its neighbour", but where the neighbour does not cover it the wall stands open to a meadow as four plain storeys;
                        // it gets the windows of an exposed end wall (small window mid-depth on upper floors, staggered plain windows).
                        if (!any && field != "" && openDone.Add(b.name + "/" + section))
                        {
                            int mods = 0, open = 0; bool hasOpening = false;
                            foreach (Transform f in sec)
                                foreach (Transform m in f)
                                {
                                    mods++;
                                    if (m.name[0] != 'P') hasOpening = true;
                                    if (!Physics.Raycast(m.position + Vector3.up * 1.5f + m.forward * 0.1f, m.forward, 3f)) open++;
                                }
                            if (mods > 0 && !hasOpening && open >= 2)
                            {
                                codes.Clear();
                                int fi = 0;
                                foreach (Transform f in sec)
                                {
                                    var sb = new System.Text.StringBuilder();
                                    int count = f.childCount;
                                    for (int slot = 0; slot < count; slot++)
                                    {
                                        char c = 'P';
                                        if (fi > 0 && count >= 2)
                                        {
                                            if (slot == count / 2) c = 'T';
                                            else if (count >= 3 && slot > 0 && ((fi + slot) & 1) == 0 && new System.Random(b.name.GetHashCode() * 31 + fi * 7 + slot).NextDouble() < 0.6) c = 'w';
                                        }
                                        sb.Append(c);
                                    }
                                    codes.Add(sb.ToString());
                                    fi++;
                                }
                                any = true;
                            }
                        }
                        if (!any) continue;
                        if (!todo.TryGetValue(b.name, out var j)) todo[b.name] = j = new JObject();
                        if (blockField != "") j[blockField] = true;   // a back wall is not seen: all of it goes plain
                        else j[field] = new JArray(codes);            // a side wall keeps its other windows
                        rowsToRebuild.Add(row.name);
                    }
                }
            foreach (var kv in todo)
            {
                if (!Auto.TryGetValue(kv.Key, out var existing)) Auto[kv.Key] = kv.Value;
                else foreach (var p in kv.Value.Properties()) existing[p.Name] = p.Value;
            }
            foreach (var r in rowsToRebuild) RebuildRow(r);
            return (todo.Count, rowsToRebuild.Count);
        }

        /// <summary>Physical check after the rows stand at their final plot positions (assembly happens at the row origin
        /// and the building is moved afterwards, so no build-time query sees the real ground): the worn granite step under
        /// a portal grows down to the pavement where the street fell away on a slope — its top stays flush with the floor,
        /// so it still reads as the building's own step, not a loose slab — and street props placed at floor level (barrel
        /// tables, crates, buckets) drop onto the pavement when the building sits over falling ground. Stacked props follow
        /// the prop that carries them. Idempotent; run again by <see cref="EnvDistrict.Finish"/> and after row rebuilds.</summary>
        public static string SeatOnGround(Transform root)
        {
            Physics.SyncTransforms();
            int steps = 0, props = 0;
            var rowsT = root.Find("Rows");
            foreach (var t in rowsT.GetComponentsInChildren<Transform>(true))
            {
                if (t.name != "ENV_Door_Step" || (t.parent != null && t.parent.name == "ENV_Door_Step")) continue;
                var rs = t.GetComponentsInChildren<Renderer>(); if (rs.Length == 0) continue;
                var bb = rs[0].bounds; foreach (var r in rs) bb.Encapsulate(r.bounds);
                var fwd = t.forward; fwd.y = 0; fwd.Normalize();
                var p = t.position;
                float g1 = EnvWalk.Ground(p.x, p.z, float.NaN), g2 = EnvWalk.Ground(p.x + fwd.x * 0.35f, p.z + fwd.z * 0.35f, float.NaN);
                float g = float.IsNaN(g1) ? g2 : float.IsNaN(g2) ? g1 : Mathf.Min(g1, g2);
                if (float.IsNaN(g) || bb.min.y - g <= 0.06f) continue;
                float grow = bb.min.y - g + 0.03f;                       // reach 3 cm into the ground
                float k = (bb.size.y + grow) / bb.size.y;
                float hAbove = bb.max.y - p.y;                           // keep the top where it is
                var sc = t.localScale;
                t.localScale = new Vector3(sc.x, sc.y * k, sc.z);
                var lp = t.localPosition;
                lp.y -= (k - 1f) * hAbove / Mathf.Max(t.parent != null ? t.parent.lossyScale.y : 1f, 0.0001f);
                t.localPosition = lp;
                steps++;
            }
            // street props by dressing group: each floating ground prop drops by its own gap; a stacked prop follows
            var propNames = new HashSet<string> { "ENV_Prop_Barrel", "ENV_Prop_Barrel_Apples", "ENV_Prop_Stool", "ENV_Cafe_Chair", "ENV_Cafe_Table",
                "ENV_Prop_FarmCrate_Apple", "ENV_Prop_FarmCrate_Carrot", "ENV_Prop_FarmCrate_Empty", "ENV_Prop_Bucket", "ENV_Prop_Bucket_Wood",
                "ENV_Prop_Rope_Coil", "ENV_Prop_Bag", "ENV_Prop_Crate_Wooden" };
            foreach (Transform row in rowsT)
                foreach (Transform b in row)
                {
                    if (b.name == "Walls") continue;
                    var dress = b.Find("Dressing"); if (dress == null) continue;
                    var items = new List<(Transform t, Bounds bb, float drop)>();
                    foreach (Transform c in dress)
                        if (propNames.Contains(c.name) && c.gameObject.activeInHierarchy && (c.parent == null || c.parent.name != c.name))
                        {
                            var rs = c.GetComponentsInChildren<Renderer>(); if (rs.Length == 0) continue;
                            var bb = rs[0].bounds; foreach (var r in rs) bb.Encapsulate(r.bounds);
                            items.Add((c, bb, 0f));
                        }
                    if (items.Count == 0) continue;
                    var byBase = items.OrderBy(i => i.bb.min.y).ToList();
                    for (int i = 0; i < byBase.Count; i++)
                    {
                        var it = byBase[i];
                        // a prop standing on another prop of the same group follows its carrier, whatever it does
                        int carrier = -1;
                        for (int j = 0; j < i; j++)
                        {
                            var other = byBase[j].bb;
                            if (Mathf.Abs(other.max.y - it.bb.min.y) < 0.12f && other.min.x < it.bb.max.x - 0.08f && other.max.x > it.bb.min.x + 0.08f
                                && other.min.z < it.bb.max.z - 0.08f && other.max.z > it.bb.min.z + 0.08f) { carrier = j; break; }
                        }
                        if (carrier >= 0) { byBase[i] = (it.t, it.bb, byBase[carrier].drop); continue; }
                        float g = EnvWalk.Ground(it.bb.center.x, it.bb.center.z, float.NaN);
                        float gap = float.IsNaN(g) ? 0f : it.bb.min.y - g;
                        byBase[i] = (it.t, it.bb, Mathf.Abs(gap) > 0.06f ? gap - Mathf.Sign(gap) * 0.01f : 0f);   // seat up or down
                    }
                    foreach (var it in byBase)
                        if (Mathf.Abs(it.drop) > 0.001f)
                        {
                            it.t.position += Vector3.down * it.drop;
                            props++;
                        }
                }
            Physics.SyncTransforms();
            return $"JD_POLISH seat on ground: {steps} door steps grown down to the street, {props} street props dropped onto it";
        }

        /// <summary>Rebuilds one row exactly as a full build would (stateful passes replayed in a dry run first) and swaps it in.</summary>
        public static string RebuildRow(string rowId)
        {
            Reload();
            var spec = JObject.Parse(EnvKit.ReadText($"{EnvDistrict.DistrictSpecs}/ENV01_Casco_District.json"));
            var rows = (JArray)spec["rows"];
            int idx = rows.Cast<JObject>().Select((r, i) => ((string)r["id"], i)).First(t => t.Item1 == rowId).i;
            var root = GameObject.Find("ENV01_Casco_District").transform;
            EnvBusiness.Reset();
            EnvDistrict.BuildRows(0, idx, dry: true);
            var old = root.Find("Rows/" + rowId);
            if (old != null) Object.DestroyImmediate(old.gameObject);
            var msg = EnvDistrict.BuildRows(idx, 1);
            Physics.SyncTransforms();
            return msg;
        }

        /// <summary>Stable digest of a row (hierarchy, meshes, materials, rounded transforms) to prove a rebuild is identical.</summary>
        public static string Fingerprint(string rowId)
        {
            var t = GameObject.Find("ENV01_Casco_District").transform.Find("Rows/" + rowId);
            var sb = new StringBuilder();
            int n = 0;
            foreach (var tr in t.GetComponentsInChildren<Transform>(true).OrderBy(x => Path(x, t), System.StringComparer.Ordinal))
            {
                var mf = tr.GetComponent<MeshFilter>();
                var mr = tr.GetComponent<Renderer>();
                sb.Append(Path(tr, t)).Append('|').Append(mf != null && mf.sharedMesh != null ? mf.sharedMesh.name : "").Append('|')
                  .Append(mr != null ? string.Join(",", mr.sharedMaterials.Select(m => m != null ? m.name : "null")) : "").Append('|')
                  .Append(tr.position.x.ToString("0.00")).Append(',').Append(tr.position.y.ToString("0.00")).Append(',').Append(tr.position.z.ToString("0.00")).Append('|')
                  .Append(tr.lossyScale.x.ToString("0.00")).Append('\n');
                n++;
            }
            using (var md5 = System.Security.Cryptography.MD5.Create())
                return $"{rowId} objects={n} md5=" + System.BitConverter.ToString(md5.ComputeHash(Encoding.UTF8.GetBytes(sb.ToString()))).Replace("-", "").Substring(0, 12);
        }

        static string Path(Transform t, Transform root)
        {
            var parts = new List<string>();
            for (var c = t; c != null && c != root; c = c.parent) parts.Add(c.name);
            parts.Reverse();
            return string.Join("/", parts);
        }

        static Vector3 V3(JToken a) => new Vector3((float)a[0], (float)a[1], (float)a[2]);

        /// <summary>Object-level corrections on the built district; the "Polish" group (placed objects) is recreated each run.</summary>
        public static string ApplyOps(Transform root)
        {
            Reload();
            var old = root.Find("Polish");
            if (old != null) Object.DestroyImmediate(old.gameObject);
            if (!(Doc["ops"] is JArray ops) || ops.Count == 0) return "JD_POLISH no ops";
            var group = EnvKit.Group(root, "Polish");
            Physics.SyncTransforms();
            var all = root.GetComponentsInChildren<Transform>(true).Where(t => t != root && !t.IsChildOf(group)).ToArray();
            int removed = 0, moved = 0, placed = 0, missed = 0;
            var log = new StringBuilder();
            foreach (JObject op in ops)
            {
                string kind = (string)op["op"];
                if (kind == "place")
                {
                    var at = op["at"];
                    float x = (float)at[0], z = (float)at[at.Count() - 1];
                    float y = at.Count() >= 3 ? (float)at[1] : EnvWalk.Ground(x, z);
                    var sub = string.IsNullOrEmpty((string)op["unit"]) ? group : EnvKit.Group(group, (string)op["unit"]);
                    var go = EnvKit.Place((string)op["module"], sub, new Vector3(x, y, z), (float?)op["yaw"] ?? 0f, op["scale"] != null ? Vector3.one * (float)op["scale"] : (Vector3?)null);
                    if (go != null) placed++; else missed++;
                    continue;
                }
                string name = (string)op["name"];
                var near = V3(op["near"]);
                float r = (float?)op["r"] ?? 0.5f;
                var hits = all.Where(t => t != null && t.name == name && (t.position - near).magnitude <= r).ToList();
                hits = hits.Where(h => !hits.Any(o2 => o2 != h && h.IsChildOf(o2))).ToList();   // outermost matches only
                if (hits.Count == 0) { missed++; log.AppendLine($"  miss {kind} {name} near {near}"); continue; }
                foreach (var h in hits)
                {
                    if (kind == "remove") { Object.DestroyImmediate(h.gameObject); removed++; }
                    else if (kind == "move")
                    {
                        Vector3 to;
                        if (op["to"] == null) to = h.position + V3(op["by"]);
                        else if (op["to"].Count() == 2) to = new Vector3((float)op["to"][0], EnvWalk.Ground((float)op["to"][0], (float)op["to"][1]), (float)op["to"][1]);
                        else to = V3(op["to"]);
                        h.position = to;
                        if (op["yaw"] != null) h.rotation = Quaternion.Euler(0, (float)op["yaw"], 0);
                        if (op["scale"] != null) h.localScale = Vector3.one * (float)op["scale"];
                        moved++;
                    }
                }
            }
            Physics.SyncTransforms();
            return $"JD_POLISH ops={ops.Count} removed={removed} moved={moved} placed={placed} missed={missed}\n{log}";
        }
    }
}

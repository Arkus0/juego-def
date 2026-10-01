using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace JuegoDef.Env
{
    // Only the JSON buffer participates in Undo. The saved baseline belongs to the session,
    // so Undo after SAVE can never accidentally restore an obsolete saved baseline.
    public class TraceEditState : ScriptableObject
    {
        public string json;
        public static TraceEditState FromDoc(JObject doc)
        {
            var state = CreateInstance<TraceEditState>();
            state.hideFlags = HideFlags.HideAndDontSave;
            state.json = doc.ToString(Formatting.None);
            return state;
        }
    }

    public enum PtKind { Node, StreetVia, PlazaVertex, PlazaDisc, PlazaDiscRadius, Landmark, River, Street }

    public class EditPt
    {
        public PtKind kind;
        public string owner, label;
        public int index;
        public Vector3 world;
        public float radius, yaw;
        public string Key => $"{kind}:{owner}:{index}";
    }

    public static class LayoutDocument
    {
        public static string TracePath(string id) => $"{EnvDistrict.DistrictSpecs}/{id}.trace.json";
        public static string SpecPath(string id) => $"{EnvDistrict.DistrictSpecs}/{id}.json";
        public static JObject Item(JObject d, string collection, string id) =>
            (d[collection] as JArray)?.OfType<JObject>().FirstOrDefault(x => (string)x["id"] == id);
        public static Vector3 Offset(JObject d) => new Vector3((float)d["unityOffset"][0], 0, (float)d["unityOffset"][1]);
        public static float Width(JObject d, JObject street) => (float?)(street["width"] ?? d["roles"]?[(string)street["role"]]?["width"]) ?? 0;
        static float Y(JArray a, float fallback = 0) => a.Count > 2 ? (float)a[2] : fallback;

        public static List<Vector3> StreetPoints(JObject d, JObject s)
        {
            var raw = new List<JArray> { (JArray)d["nodes"][(string)s["from"]] };
            if (s["via"] is JArray via) raw.AddRange(via.Cast<JArray>());
            raw.Add((JArray)d["nodes"][(string)s["to"]]);
            var cumulative = new float[raw.Count];
            for (int i = 1; i < raw.Count; ++i)
                cumulative[i] = cumulative[i - 1] + Vector2.Distance(new Vector2((float)raw[i - 1][0], (float)raw[i - 1][1]), new Vector2((float)raw[i][0], (float)raw[i][1]));
            var off = Offset(d);
            return raw.Select((a, i) => new Vector3((float)a[0], Y(a, Mathf.Lerp(Y(raw[0]), Y(raw[^1]), cumulative[i] / Mathf.Max(.001f, cumulative[^1]))), (float)a[1]) + off).ToList();
        }

        // Resolve legacy plot anchoring from the generated spec, rather than displaying a
        // misleading target marker disconnected from the visible landmark.
        public static (Vector3 at, float yaw) Landmark(JObject d, JObject lm, JObject spec)
        {
            var a = (JArray)lm["at"];
            if ((string)lm["placement"] == "direct") return (new Vector3((float)a[0], Y(a), (float)a[1]) + Offset(d), (float?)lm["yaw"] ?? 0);
            if (spec?["rows"] is JArray rows)
                foreach (var row in rows.OfType<JObject>())
                    foreach (var plot in ((JArray)row["plots"]).OfType<JObject>())
                        if ((string)plot["landmark"] == (string)lm["id"])
                        {
                            float yaw = Mathf.Atan2(-(float)row["dir"][1], (float)row["dir"][0]) * Mathf.Rad2Deg;
                            var at = new Vector3((float)row["origin"][0], 0, (float)row["origin"][1]) + Quaternion.Euler(0, yaw, 0) * new Vector3((float)plot["x0"] + (float)plot["w"] / 2, (float)plot["y"], -(float?)plot["setback"] ?? 0);
                            return (at, yaw);
                        }
            return (new Vector3((float)a[0], Y(a), (float)a[1]) + Offset(d), 0);
        }

        public static List<EditPt> Points(JObject d, JObject spec)
        {
            var result = new List<EditPt>();
            var off = Offset(d);
            foreach (var n in ((JObject)d["nodes"]).Properties())
            {
                var a = (JArray)n.Value;
                result.Add(new EditPt { kind = PtKind.Node, owner = n.Name, label = n.Name, world = new Vector3((float)a[0], Y(a), (float)a[1]) + off });
            }
            foreach (var s in ((JArray)d["streets"]).OfType<JObject>())
            {
                var pts = StreetPoints(d, s);
                string id = (string)s["id"];
                result.Add(new EditPt { kind = PtKind.Street, owner = id, label = (string)s["name"] ?? id, world = (pts.First() + pts.Last()) / 2 });
                if (s["via"] is JArray via)
                    for (int i = 0; i < via.Count; ++i) result.Add(new EditPt { kind = PtKind.StreetVia, owner = id, index = i, label = $"{id} · curva {i + 1}", world = pts[i + 1] });
            }
            foreach (var p in ((JArray)d["plazas"]).OfType<JObject>())
            {
                string id = (string)p["id"];
                float y = (float?)p["y"] ?? 0;
                if (p["poly"] is JArray poly)
                    for (int i = 0; i < poly.Count; ++i) result.Add(new EditPt { kind = PtKind.PlazaVertex, owner = id, index = i, label = $"{id} · vértice {i + 1}", world = new Vector3((float)poly[i][0], y, (float)poly[i][1]) + off });
                if (p["disc"] is JArray disc)
                {
                    var centre = new Vector3((float)disc[0], y, (float)disc[1]) + off;
                    result.Add(new EditPt { kind = PtKind.PlazaDisc, owner = id, label = id, world = centre, radius = (float)disc[2] });
                    result.Add(new EditPt { kind = PtKind.PlazaDiscRadius, owner = id, label = $"{id} · radio", world = centre + Vector3.right * (float)disc[2], radius = (float)disc[2] });
                }
            }
            foreach (var lm in (d["landmarks"] as JArray ?? new JArray()).OfType<JObject>())
            {
                var (at, yaw) = Landmark(d, lm, spec);
                result.Add(new EditPt { kind = PtKind.Landmark, owner = (string)lm["id"], label = $"Landmark {(string)lm["id"]}", world = at, yaw = yaw });
            }
            if (d["river"]?["pts"] is JArray river)
                for (int i = 0; i < river.Count; ++i) result.Add(new EditPt { kind = PtKind.River, owner = "river", index = i, label = $"Río · punto {i + 1}", world = new Vector3((float)river[i][0], (float?)d["river"]["water"] ?? 0, (float)river[i][1]) + off });
            return result;
        }

        public static void Move(JObject d, EditPt p, Vector3 world, bool height)
        {
            var local = world - Offset(d);
            JArray a = null;
            switch (p.kind)
            {
                case PtKind.Node: a = (JArray)d["nodes"][p.owner]; break;
                case PtKind.StreetVia: a = (JArray)Item(d, "streets", p.owner)["via"][p.index]; break;
                case PtKind.PlazaVertex: a = (JArray)Item(d, "plazas", p.owner)["poly"][p.index]; break;
                case PtKind.PlazaDisc: a = (JArray)Item(d, "plazas", p.owner)["disc"]; break;
                case PtKind.Landmark:
                    var lm = Item(d, "landmarks", p.owner);
                    a = (JArray)lm["at"];
                    if (lm["anchorAt"] == null) lm["anchorAt"] = new JArray((float)a[0], (float)a[1]);
                    lm["placement"] = "direct";
                    lm["yaw"] = p.yaw;
                    height = true;
                    break;
                case PtKind.River: a = (JArray)d["river"]["pts"][p.index]; break;
                case PtKind.PlazaDiscRadius:
                    var disc = (JArray)Item(d, "plazas", p.owner)["disc"];
                    disc[2] = Mathf.Max(.5f, Vector2.Distance(new Vector2(local.x, local.z), new Vector2((float)disc[0], (float)disc[1])));
                    return;
            }
            if (a == null) return;
            a[0] = local.x; a[1] = local.z;
            if (height && (p.kind == PtKind.Node || p.kind == PtKind.StreetVia || p.kind == PtKind.Landmark))
            { if (a.Count < 3) a.Add(world.y); else a[2] = world.y; }
            if (height && (p.kind == PtKind.PlazaVertex || p.kind == PtKind.PlazaDisc)) Item(d, "plazas", p.owner)["y"] = world.y;
        }

        public static List<string> Changes(JObject baseline, JObject doc)
        {
            var result = new List<string>();
            foreach (var n in ((JObject)doc["nodes"]).Properties())
                if (!JToken.DeepEquals(baseline["nodes"]?[n.Name], n.Value)) result.Add($"Nodo {n.Name}: posición/altura");
            foreach (var c in new[] { "streets", "plazas", "landmarks" })
                foreach (var item in (doc[c] as JArray ?? new JArray()).OfType<JObject>())
                {
                    string id = (string)item["id"];
                    var old = Item(baseline, c, id);
                    if (JToken.DeepEquals(old, item)) continue;
                    var fields = item.Properties().Select(x => x.Name).Union(old?.Properties().Select(x => x.Name) ?? Array.Empty<string>())
                        .Where(k => k != "anchorAt" && k != "placement" && !JToken.DeepEquals(old?[k], item[k])).Select(k => k == "width" ? "anchura" : k == "via" ? "curvas/altura" : k == "yaw" ? "giro" : k == "at" ? "posición/altura" : k == "poly" ? "contorno" : k == "y" ? "altura" : k);
                    result.Add($"{id}: {string.Join(", ", fields)}");
                }
            if (!JToken.DeepEquals(baseline["river"], doc["river"])) result.Add("Río: puntos de control");
            return result;
        }

        static void Coordinate(JToken token, int minimum, string label)
        {
            if (token is not JArray a || a.Count < minimum || a.Any(v => v.Type != JTokenType.Integer && v.Type != JTokenType.Float || !double.IsFinite((double)v)))
                throw new InvalidDataException($"{label}: coordenadas inválidas");
        }
        static void Polygon(JArray poly)
        {
            var pts = poly.Select(p => new Vector2((float)p[0], (float)p[1])).ToList();
            if (pts.Count > 3 && pts[0] == pts[pts.Count - 1]) pts.RemoveAt(pts.Count - 1);
            float area = 0;
            float Cross(Vector2 a, Vector2 b) => a.x*b.y-a.y*b.x;
            for (int i=0;i<pts.Count;i++)
            {
                var a=pts[i]; var b=pts[(i+1)%pts.Count]; area += Cross(a,b);
                if ((a-b).sqrMagnitude < .0001f) throw new InvalidDataException("Polígono con vértices repetidos");
                for (int j=i+2;j<pts.Count;j++)
                {
                    if (i==0 && j==pts.Count-1) continue;
                    var c=pts[j]; var e=pts[(j+1)%pts.Count]; float den=Cross(b-a,e-c);
                    if (Mathf.Abs(den)<.00001f) continue;
                    float t=Cross(c-a,e-c)/den, u=Cross(c-a,b-a)/den;
                    if (t>=0 && t<=1 && u>=0 && u<=1) throw new InvalidDataException("El contorno de plaza se cruza");
                }
            }
            if (Mathf.Abs(area)<.01f) throw new InvalidDataException("Plaza sin superficie");
        }
        public static void Validate(JObject d)
        {
            Coordinate(d["unityOffset"], 2, "Origen");
            if (d["nodes"] is not JObject nodes || d["streets"] is not JArray streets || d["plazas"] is not JArray) throw new InvalidDataException("Faltan nodos, calles o plazas");
            if (d["landmarks"] != null && d["landmarks"] is not JArray) throw new InvalidDataException("Colección de landmarks no soportada");
            foreach (var n in nodes.Properties()) Coordinate(n.Value, 3, n.Name);
            foreach (var collection in new[] { "streets", "plazas", "landmarks" })
            {
                var ids = new HashSet<string>();
                foreach (var entry in d[collection] as JArray ?? new JArray())
                {
                    if (entry is not JObject item) throw new InvalidDataException("Elemento no soportado en " + collection);
                    if (string.IsNullOrEmpty((string)item["id"]) || !ids.Add((string)item["id"])) throw new InvalidDataException($"{collection}: identidad ausente/duplicada");
                }
            }
            foreach (var s in streets.OfType<JObject>())
            {
                if (nodes[(string)s["from"] ?? ""] == null || nodes[(string)s["to"] ?? ""] == null) throw new InvalidDataException($"{s["id"]}: extremo desconocido");
                if (!float.IsFinite(Width(d, s)) || Width(d, s) < .5f) throw new InvalidDataException($"{s["id"]}: anchura inválida");
                if (s["via"] != null && s["via"] is not JArray) throw new InvalidDataException("Curvas no soportadas");
                foreach (var a in s["via"] as JArray ?? new JArray()) Coordinate(a, 2, "Curva");
                var pts = StreetPoints(d, s);
                for (int i = 1; i < pts.Count; ++i) if ((new Vector2(pts[i].x - pts[i - 1].x, pts[i].z - pts[i - 1].z)).sqrMagnitude < .0001f) throw new InvalidDataException($"{s["id"]}: tramo de longitud cero");
            }
            foreach (var p in ((JArray)d["plazas"]).OfType<JObject>())
            {
                if (p["disc"] is JArray disc) { Coordinate(disc, 3, "Plaza"); if ((float)disc[2] < .5f) throw new InvalidDataException("Radio inválido"); }
                else if (p["poly"] is JArray poly && poly.Count >= 3) { foreach (var a in poly) Coordinate(a, 2, "Vértice"); Polygon(poly); }
                else throw new InvalidDataException($"{p["id"]}: polígono no soportado");
                if (p["y"] != null && !float.IsFinite((float)p["y"])) throw new InvalidDataException("Altura inválida");
            }
            foreach (var lm in (d["landmarks"] as JArray ?? new JArray()).OfType<JObject>())
            {
                if (lm["anchorAt"] != null) Coordinate(lm["anchorAt"],2,"Anclaje de landmark");
                if ((string)lm["placement"] == "direct" && (lm["at"] as JArray)?.Count != 3) throw new InvalidDataException("Posición de landmark no soportada");
                Coordinate(lm["at"], (string)lm["placement"] == "direct" ? 3 : 2, "Landmark");
                if (lm["placement"] != null && (string)lm["placement"] != "direct") throw new InvalidDataException("Modo de landmark no soportado");
                if (lm["yaw"] != null && !float.IsFinite((float)lm["yaw"])) throw new InvalidDataException("Giro inválido");
            }
            if (d["river"] is JObject river)
            {
                if (river["pts"] is not JArray pts || pts.Count<2) throw new InvalidDataException("Río sin puntos soportados");
                foreach(var p in pts) Coordinate(p,2,"Río");
                if (!float.IsFinite((float)river["water"]) || !float.IsFinite((float)river["width"]) || (float)river["width"]<=0) throw new InvalidDataException("Río inválido");
            }
        }

        public static bool Save(string path, string loaded, JObject doc)
        {
            Validate(doc);
            if (File.ReadAllText(path) != loaded) throw new IOException("El distrito cambió fuera del Director. Recarga antes de guardar.");
            var before = JObject.Parse(loaded);
            if (JToken.DeepEquals(before, doc)) return false;
            var temp = path + ".director.tmp";
            try
            {
                File.WriteAllText(temp, doc.ToString(Formatting.Indented).Replace("\r\n", "\n") + "\n", new UTF8Encoding(false));
                File.Replace(temp, path, path + ".bak");
            }
            finally { if (File.Exists(temp)) File.Delete(temp); }
            return true;
        }
    }
}

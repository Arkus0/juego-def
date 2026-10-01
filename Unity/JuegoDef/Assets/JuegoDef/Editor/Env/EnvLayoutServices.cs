using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using GameCreator.Runtime.Characters;

namespace JuegoDef.Env
{
    public static class LayoutBookmarks
    {
        static string PathOf(string id) => $"{EnvDistrict.DistrictSpecs}/{id}.director.json";
        static JObject Read(string id) => File.Exists(PathOf(id)) ? JObject.Parse(File.ReadAllText(PathOf(id))) : new JObject();
        public static bool Exists(string id, int slot) => Read(id)["bookmarks"]?[slot.ToString()] != null;
        public static void Save(string id, int slot)
        {
            var sv = SceneView.lastActiveSceneView;
            if (!sv) return;
            var d = Read(id);
            if (d["bookmarks"] is not JObject) d["bookmarks"] = new JObject();
            d["bookmarks"][slot.ToString()] = new JObject { ["pivot"] = new JArray(sv.pivot.x, sv.pivot.y, sv.pivot.z), ["rotation"] = new JArray(sv.rotation.x, sv.rotation.y, sv.rotation.z, sv.rotation.w), ["size"] = sv.size, ["orthographic"] = sv.orthographic, ["fog"] = sv.sceneViewState.showFog };
            File.WriteAllText(PathOf(id), d.ToString());
            AssetDatabase.ImportAsset(PathOf(id));
        }
        public static void Recall(string id, int slot)
        {
            var sv = SceneView.lastActiveSceneView;
            var b = Read(id)["bookmarks"]?[slot.ToString()];
            if (!sv || b == null) return;
            var a = b["pivot"]; var q = b["rotation"];
            sv.sceneViewState.showFog = (bool?)b["fog"] ?? true;
            sv.LookAt(new Vector3((float)a[0], (float)a[1], (float)a[2]), new Quaternion((float)q[0], (float)q[1], (float)q[2], (float)q[3]), (float)b["size"], (bool)b["orthographic"]);
        }
    }

    public static class LayoutPlacement
    {
        public static Vector3 Anchor(JObject row, JObject plot)
        {
            if (plot["directPlacement"] is JObject direct) { var a = direct["at"]; return new Vector3((float)a[0], (float)a[1], (float)a[2]); }
            return new Vector3((float)row["origin"][0], 0, (float)row["origin"][1]) + Quaternion.Euler(0, Yaw(row, plot), 0) * new Vector3((float)plot["x0"] + (float)plot["w"] / 2, (float)plot["y"], -((float?)plot["setback"] ?? 0));
        }
        public static float Yaw(JObject row, JObject plot) => (float?)plot["directPlacement"]?["yaw"] ?? Mathf.Atan2(-(float)row["dir"][1], (float)row["dir"][0]) * Mathf.Rad2Deg;
        public static Vector3[] Footprint(JObject row, JObject plot)
        {
            var at = Anchor(row, plot); var rot = Quaternion.Euler(0, Yaw(row, plot), 0);
            float w = (float)plot["w"], depth = (float?)plot["depth"] ?? 6;
            return new[] { new Vector3(-w / 2, 0, 0), new Vector3(w / 2, 0, 0), new Vector3(w / 2, 0, -depth), new Vector3(-w / 2, 0, -depth) }.Select(x => at + rot * x).ToArray();
        }
        static float Cross(Vector2 a, Vector2 b) => a.x * b.y - a.y * b.x;
        static Vector2 V(Vector3 p) => new Vector2(p.x, p.z);
        static bool Overlap(Vector3[] a, Vector3[] b)
        {
            foreach (var polygon in new[] { a, b })
                for (int i = 0; i < polygon.Length; ++i)
                {
                    var e = V(polygon[(i + 1) % polygon.Length] - polygon[i]); var axis = new Vector2(-e.y, e.x).normalized;
                    float amin = a.Min(p => Vector2.Dot(V(p), axis)), amax = a.Max(p => Vector2.Dot(V(p), axis));
                    float bmin = b.Min(p => Vector2.Dot(V(p), axis)), bmax = b.Max(p => Vector2.Dot(V(p), axis));
                    if (amax <= bmin + .02f || bmax <= amin + .02f) return false;
                }
            return true;
        }
        static bool Inside(Vector2 p, JArray poly)
        {
            bool hit = false;
            for (int i = 0, j = poly.Count - 1; i < poly.Count; j = i++)
            {
                var a = new Vector2((float)poly[i][0], (float)poly[i][1]); var b = new Vector2((float)poly[j][0], (float)poly[j][1]);
                if ((a.y > p.y) != (b.y > p.y) && p.x < (b.x - a.x) * (p.y - a.y) / (b.y - a.y) + a.x) hit = !hit;
            }
            return hit;
        }
        // SAT is for building rectangles. A river polygon can be concave and can
        // cross the footprint without containing any of its corners.
        static bool CrossesChannel(Vector3[] footprint, JArray channel)
        {
            if (footprint.Any(p => Inside(V(p), channel))) return true;
            var fp = new JArray(footprint.Select(p => new JArray(p.x, p.z)));
            if (channel.Any(p => Inside(new Vector2((float)p[0], (float)p[1]), fp))) return true;
            for(int i=0;i<footprint.Length;i++) for(int j=0;j<channel.Count;j++)
            {
                var a=V(footprint[i]);var b=V(footprint[(i+1)%footprint.Length]);
                var c=new Vector2((float)channel[j][0],(float)channel[j][1]);
                var d=new Vector2((float)channel[(j+1)%channel.Count][0],(float)channel[(j+1)%channel.Count][1]);
                float den=Cross(b-a,d-c);
                if(Mathf.Abs(den)<.00001f) continue;
                float t=Cross(c-a,d-c)/den,u=Cross(c-a,b-a)/den;
                if(t>=0 && t<=1 && u>=0 && u<=1) return true;
            }
            return false;
        }
        static float SegmentDistance(Vector2 p, Vector2 a, Vector2 b) => Vector2.Distance(p, a + (b - a) * Mathf.Clamp01(Vector2.Dot(p - a, b - a) / Mathf.Max(.0001f, (b - a).sqrMagnitude)));
        public static JObject PreviewSpec(JObject doc, JObject spec)
        {
            var s = (JObject)spec.DeepClone();
            foreach (var lm in (doc["landmarks"] as JArray ?? new JArray()).OfType<JObject>().Where(x => (string)x["placement"] == "direct"))
                foreach (var row in ((JArray)s["rows"]).OfType<JObject>())
                    foreach (var plot in ((JArray)row["plots"]).OfType<JObject>().Where(x => (string)x["landmark"] == (string)lm["id"]))
                        plot["directPlacement"] = new JObject { ["at"] = new JArray((float)lm["at"][0] + (float)doc["unityOffset"][0], (float)lm["at"][2], (float)lm["at"][1] + (float)doc["unityOffset"][1]), ["yaw"] = (float)lm["yaw"] };
            return s;
        }
        public static string Validate(JObject spec)
        {
            var all = ((JArray)spec["rows"]).OfType<JObject>().SelectMany(r => ((JArray)r["plots"]).OfType<JObject>().Where(p => (bool?)p["wall"] != true).Select(p => (row: r, plot: p))).ToList();
            foreach (var item in all.Where(x => x.plot["directPlacement"] != null))
            {
                string id = (string)item.plot["landmark"];
                var footprint = Footprint(item.row, item.plot);
                foreach (var other in all.Where(x => !ReferenceEquals(x.plot, item.plot)))
                    if (Overlap(footprint, Footprint(other.row, other.plot))) return $"{id}: solape con un edificio vecino";
                var bounds = (JArray)spec["district"];
                if (footprint.Any(p => p.x < (float)bounds[0][0] || p.z < (float)bounds[0][1] || p.x > (float)bounds[1][0] || p.z > (float)bounds[1][1])) return $"{id}: fuera del distrito";
                if (spec["river"]?["channel"] is JArray channel && CrossesChannel(footprint, channel)) return $"{id}: invade el cauce";
                var front = Anchor(item.row, item.plot) + Quaternion.Euler(0, Yaw(item.row, item.plot), 0) * Vector3.forward * .6f;
                bool access = (spec["plazas"] as JArray ?? new JArray()).OfType<JObject>().Any(p => Inside(V(front), (JArray)p["poly"]));
                foreach (var st in ((JArray)spec["streets"]).OfType<JObject>())
                {
                    var pts = (JArray)st["pts"];
                    for (int i = 1; i < pts.Count; ++i)
                        if (SegmentDistance(V(front), new Vector2((float)pts[i - 1][0], (float)pts[i - 1][1]), new Vector2((float)pts[i][0], (float)pts[i][1])) <= (float)st["width"] / 2 + .8f) access = true;
                }
                if (!access) return $"{id}: la fachada queda sin acceso a calle/plaza";
                foreach (var other in all.Where(x => !ReferenceEquals(x.plot, item.plot)))
                {
                    var entrance = new[] { front + new Vector3(-.25f, 0, -.25f), front + new Vector3(.25f, 0, -.25f), front + new Vector3(.25f, 0, .25f), front + new Vector3(-.25f, 0, .25f) };
                    if (Overlap(entrance, Footprint(other.row, other.plot))) return $"{id}: acceso bloqueado";
                }
            }
            return "";
        }
        public static void ApplyAll(Transform root, JObject spec)
        {
            foreach(var row in ((JArray)spec["rows"]).OfType<JObject>())
            {
                var plots=(JArray)row["plots"];
                for(int i=0;i<plots.Count;i++) if(plots[i]["directPlacement"] is JObject)
                {
                    var go=root.Find($"Rows/{row["id"]}/{row["id"]}_{i}");
                    if(!go) throw new InvalidOperationException("Landmark no materializado: " + plots[i]["landmark"]);
                    Apply(go.gameObject,(JObject)plots[i],(float)plots[i]["w"]);
                }
            }
        }
        // Shared by FULL and EnvPolish.RebuildRow through EnvDistrict.BuildRows.
        public static void Apply(GameObject go, JObject plot, float scaledWidth)
        {
            if (plot["directPlacement"] is not JObject direct) return;
            var a = direct["at"];
            var rot = Quaternion.Euler(0, (float)direct["yaw"], 0);
            go.transform.SetPositionAndRotation(new Vector3((float)a[0], (float)a[1], (float)a[2]) - rot * Vector3.right * (scaledWidth / 2), rot);
        }
    }

    [InitializeOnLoad]
    public static class LayoutPlayHere
    {
        static string Key => "JuegoDef.Director.PlayHere." + LayoutReceipt.WorkspaceKey;
        public static Vector3 Target { get; private set; }
        public static string Message { get; private set; } = "";
        static double deadline;
        static LayoutPlayHere() { EditorApplication.playModeStateChanged += Changed; }
        public static bool Resolve(Vector3 selected, out Vector3 feet)
        {
            Physics.SyncTransforms();
            var player = GameObject.Find("Player");
            var cc = player ? player.GetComponent<CharacterController>() : null;
            float radius = cc ? cc.radius : .3f, height = cc ? cc.height : 2f;
            for (int ring = 0; ring <= 12; ++ring)
                for (int i = 0; i < (ring == 0 ? 1 : 16); ++i)
                {
                    float angle = i * Mathf.PI / 8;
                    var p = selected + new Vector3(Mathf.Cos(angle), 0, Mathf.Sin(angle)) * (ring * .5f);
                    var hits = Physics.RaycastAll(new Vector3(p.x, 100, p.z), Vector3.down, 200, ~0, QueryTriggerInteraction.Ignore)
                        .Where(h => (h.collider.name.StartsWith("Ground_") || h.collider.name.Contains("_Deck") || h.collider.name.Contains("_Treads"))).OrderBy(h => Mathf.Abs(h.point.y - selected.y));
                    foreach (var h in hits)
                    {
                        if (h.normal.y < .65f) continue;
                        var a = h.point + Vector3.up * (radius + .06f); var b = h.point + Vector3.up * (height - radius + .06f);
                        if (Physics.OverlapCapsule(a, b, radius, ~0, QueryTriggerInteraction.Ignore).Any(c => player == null || !c.transform.IsChildOf(player.transform))) continue;
                        feet = h.point + Vector3.up * .06f; return true;
                    }
                }
            feet = default; return false;
        }
        public static bool Start(string id, Vector3 at, float yaw, bool confirm)
        {
            if (LayoutRebuild.phase != LayoutRebuild.Phase.None) { Message = "Termina o cancela la reconstrucción antes de jugar"; return false; }
            if (!EditorApplication.isPlaying && SceneManager.GetActiveScene().path != LayoutReceipt.ScenePath(id))
            {
                if (!File.Exists(LayoutReceipt.ScenePath(id)) || !EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) { Message = "Abre/reconstruye el distrito antes de jugar"; return false; }
                EditorSceneManager.OpenScene(LayoutReceipt.ScenePath(id));
            }
            if (!Resolve(at, out var feet)) { Message = "No hay un punto transitable y libre a menos de 6 m de la selección"; return false; }
            Target = feet;
            if (confirm && !EditorUtility.DisplayDialog("PLAY HERE", "El marcador azul es el punto seguro de inicio. Se probará la escena de la última reconstrucción.", "JUGAR", "Cancelar")) return false;
            SessionState.SetString(Key, new JObject { ["feet"] = new JArray(feet.x, feet.y, feet.z), ["yaw"] = yaw }.ToString());
            if (EditorApplication.isPlaying) BeginPosition(); else EditorApplication.isPlaying = true;
            Message = "Iniciando prueba junto a la selección"; return true;
        }
        static void Changed(PlayModeStateChange change)
        {
            if (change == PlayModeStateChange.EnteredPlayMode) BeginPosition();
            if (change == PlayModeStateChange.ExitingPlayMode) { SessionState.EraseString(Key); EditorApplication.update -= Position; }
        }
        static void BeginPosition() { deadline = EditorApplication.timeSinceStartup + 10; EditorApplication.update -= Position; EditorApplication.update += Position; }
        static void Position()
        {
            var json = SessionState.GetString(Key, "");
            if (json == "") { EditorApplication.update -= Position; return; }
            var player = GameObject.Find("Player"); var c = player ? player.GetComponent<Character>() : null;
            if (c && c.Driver != null)
            {
                var d = JObject.Parse(json); var p = d["feet"];
                c.Driver.SetPosition(new Vector3((float)p[0], (float)p[1], (float)p[2]), true);
                c.Driver.SetRotation(Quaternion.Euler(0, (float)d["yaw"], 0));
                SessionState.EraseString(Key); EditorApplication.update -= Position;
                Message = "PLAY HERE · jugador colocado"; Debug.Log("JD_DIRECTOR_PLAY " + json);
            }
            else if (EditorApplication.timeSinceStartup > deadline) { Message = "El jugador GC2 no está disponible"; SessionState.EraseString(Key); EditorApplication.update -= Position; Debug.LogWarning(Message); }
        }
    }
}

using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// Facade clearance: exact triangle-vs-box tests of later additions (rain-water pipes, service cables, dishes,
    /// meters, lanterns, clotheslines, vines) against the openings, joinery, quoins and projecting dressing of a
    /// facade, in the building frame. The assembler places services only where a real one would fit; the validator
    /// re-checks every pipe and cable of a scene against its building and row neighbours (ENV_SERVICE_CLASH).
    /// Owner review 2026-09-28: "tuberías que atraviesan ventanas, fachadas y puertas".
    /// </summary>
    public static class EnvClearance
    {
        public const string Pipe = "ENV_Downpipe", Cable = "ENV_Cable_Run_2m";
        public const float WallFace = 0.1f;   // just in front of the kit wall street face (z = 0.092)
        public const float PipeR = 0.045f;    // ENV_Downpipe tube radius

        static readonly string[] Passive = { "ENV_Wall_", "Wall_", "THR_" };
        // pieces a pipe may stand in front of (it takes a longer bracket) rather than being refused by
        // pieces a service may stand off in front of: corner quoins/pilasters, plinths, and the pipe's own hopper head/shoe
        static readonly string[] StandOff = { "Corner_", "ENV_Quoin_", "ENV_Plinth", "ENV_Downpipe_" };

        public static bool IsService(string module) => module == Pipe || module == Cable;
        public static bool IsStandOff(string module) => StandOff.Any(module.StartsWith);

        /// <summary>Module instances that make up a facade: front slots, quoins, dressing, history, corner entrance.</summary>
        public static IEnumerable<GameObject> FacadeModules(Transform building)
        {
            foreach (var group in new[] { "Front", "Corners" })
            {
                var g = building.Find(group);
                if (!g) continue;
                foreach (Transform floor in g)
                    foreach (Transform child in floor)
                        if (group == "Corners") yield return child.gameObject;
                        else foreach (Transform m in child) yield return m.gameObject;
            }
            foreach (var group in new[] { "Dressing", "History" })
            {
                var g = building.Find(group);
                if (g) foreach (Transform m in g) yield return m.gameObject;
            }
            var ce = building.Find("CornerEntrance");
            if (ce)
                foreach (Transform m in ce)
                    if (m.name == "e_chamfer") { foreach (Transform k in m) yield return k.gameObject; }
                    else yield return m.gameObject;
        }

        public static string ModuleName(GameObject go)
        {
            var n = go.name;
            int cut = n.IndexOf(" (");
            return cut > 0 ? n.Substring(0, cut) : n;
        }

        static readonly Dictionary<Mesh, (Vector3[] v, int[] t)> meshCache = new Dictionary<Mesh, (Vector3[], int[])>();

        public static void ClearCache() => meshCache.Clear();

        /// <summary>Bounds of a module's renderers in the frame of <paramref name="frame"/>.</summary>
        public static Bounds BoundsIn(Transform frame, GameObject go)
        {
            bool any = false;
            var b = new Bounds();
            foreach (var r in go.GetComponentsInChildren<Renderer>(true))
            {
                var lb = r.localBounds;
                var m = frame.worldToLocalMatrix * r.transform.localToWorldMatrix;
                for (int i = 0; i < 8; i++)
                {
                    var c = new Vector3((i & 1) == 0 ? lb.min.x : lb.max.x, (i & 2) == 0 ? lb.min.y : lb.max.y, (i & 4) == 0 ? lb.min.z : lb.max.z);
                    var p = m.MultiplyPoint3x4(c);
                    if (!any) { b = new Bounds(p, Vector3.zero); any = true; }
                    else b.Encapsulate(p);
                }
            }
            return b;
        }

        public class Item
        {
            public GameObject go;
            public string module;
            public Bounds bounds;
            public Vector3[] tris;   // world triangles expressed in the field frame, 3 per triangle
        }

        /// <summary>Obstacles of one or more facades, expressed in one building frame.</summary>
        public class Field
        {
            public readonly Transform frame;
            public readonly List<Item> items = new List<Item>();

            public Field(Transform frame) { this.frame = frame; }

            public static Field Of(Transform frame, IEnumerable<Transform> buildings)
            {
                var f = new Field(frame);
                foreach (var b in buildings)
                    foreach (var go in FacadeModules(b))
                        f.Add(go);
                return f;
            }

            public void Add(GameObject go)
            {
                var module = ModuleName(go);
                if (Passive.Any(module.StartsWith)) return;
                var tris = new List<Vector3>();
                foreach (var mf in go.GetComponentsInChildren<MeshFilter>(true))
                {
                    var mesh = mf.sharedMesh;
                    if (!mesh) continue;
                    if (!meshCache.TryGetValue(mesh, out var data)) meshCache[mesh] = data = (mesh.vertices, mesh.triangles);
                    var m = frame.worldToLocalMatrix * mf.transform.localToWorldMatrix;
                    foreach (var i in data.t) tris.Add(m.MultiplyPoint3x4(data.v[i]));
                }
                if (tris.Count == 0) return;
                items.Add(new Item { go = go, module = module, bounds = BoundsIn(frame, go), tris = tris.ToArray() });
            }

            public void Remove(GameObject go) => items.RemoveAll(i => i.go == go);

            /// <summary>First item whose triangles enter <paramref name="box"/>, or null.</summary>
            public Item Hit(Bounds box, System.Func<Item, bool> consider = null)
            {
                foreach (var it in items)
                {
                    if (!it.bounds.Intersects(box)) continue;
                    if (consider != null && !consider(it)) continue;
                    var t = it.tris;
                    for (int k = 0; k + 2 < t.Length; k += 3)
                        if (TriBox(box.center, box.extents, t[k], t[k + 1], t[k + 2])) return it;
                }
                return null;
            }
        }

        public static Bounds Box(float x0, float x1, float y0, float y1, float z0, float z1) =>
            new Bounds(new Vector3((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), new Vector3(x1 - x0, y1 - y0, z1 - z0));

        /// <summary>Tube of a downpipe standing at (x, zc) from y0 to y1, and the column between it and the wall.</summary>
        public static (Bounds core, Bounds sweep) PipeBoxes(float x, float zc, float y0, float y1, float shrink = 0f)
        {
            float r = PipeR - shrink;
            return (Box(x - r, x + r, y0, y1, zc - r, zc + r), Box(x - r, x + r, y0, y1, WallFace, zc + r));
        }

        /// <summary>The volume a placed pipe or cable really occupies (tube only; clips and shoe excluded), with the
        /// wall-side sweep for pipes. Frame: the building.</summary>
        public static (Bounds core, Bounds? sweep) ServiceBoxes(Transform frame, GameObject go, float shrink)
        {
            var p = frame.InverseTransformPoint(go.transform.position);
            var module = ModuleName(go);
            if (module == Pipe)
            {
                float h = 3f * go.transform.lossyScale.y / frame.lossyScale.y;
                var (core, sweep) = PipeBoxes(p.x, p.z, p.y + 0.45f, p.y + h - 0.05f, shrink);  // from above the plinth
                return (core, sweep);
            }
            // cable: tube along x at local y 0..-0.03, z 0.11 (see env_derive.py cable_run)
            return (Box(p.x - 0.99f, p.x + 0.99f, p.y - 0.035f + shrink, p.y + 0.005f - shrink, p.z + 0.1f + shrink, p.z + 0.12f - shrink), null);
        }

        // ------------------------------------------------------------ triangle / AABB overlap (separating axes)

        public static bool TriBox(Vector3 c, Vector3 h, Vector3 a, Vector3 b, Vector3 d)
        {
            Vector3 v0 = a - c, v1 = b - c, v2 = d - c;
            // box face normals
            if (Mathf.Max(v0.x, Mathf.Max(v1.x, v2.x)) < -h.x || Mathf.Min(v0.x, Mathf.Min(v1.x, v2.x)) > h.x) return false;
            if (Mathf.Max(v0.y, Mathf.Max(v1.y, v2.y)) < -h.y || Mathf.Min(v0.y, Mathf.Min(v1.y, v2.y)) > h.y) return false;
            if (Mathf.Max(v0.z, Mathf.Max(v1.z, v2.z)) < -h.z || Mathf.Min(v0.z, Mathf.Min(v1.z, v2.z)) > h.z) return false;
            Vector3 e0 = v1 - v0, e1 = v2 - v1, e2 = v0 - v2;
            // triangle normal
            var n = Vector3.Cross(e0, e1);
            float rn = h.x * Mathf.Abs(n.x) + h.y * Mathf.Abs(n.y) + h.z * Mathf.Abs(n.z);
            if (Mathf.Abs(Vector3.Dot(n, v0)) > rn) return false;
            // 9 edge cross axes
            foreach (var e in new[] { e0, e1, e2 })
            {
                if (!AxisOverlap(new Vector3(0, -e.z, e.y), v0, v1, v2, h)) return false;
                if (!AxisOverlap(new Vector3(e.z, 0, -e.x), v0, v1, v2, h)) return false;
                if (!AxisOverlap(new Vector3(-e.y, e.x, 0), v0, v1, v2, h)) return false;
            }
            return true;
        }

        static bool AxisOverlap(Vector3 axis, Vector3 v0, Vector3 v1, Vector3 v2, Vector3 h)
        {
            if (axis.sqrMagnitude < 1e-12f) return true;
            float p0 = Vector3.Dot(axis, v0), p1 = Vector3.Dot(axis, v1), p2 = Vector3.Dot(axis, v2);
            float r = h.x * Mathf.Abs(axis.x) + h.y * Mathf.Abs(axis.y) + h.z * Mathf.Abs(axis.z);
            return !(Mathf.Min(p0, Mathf.Min(p1, p2)) > r || Mathf.Max(p0, Mathf.Max(p1, p2)) < -r);
        }
    }
}

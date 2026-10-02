using System;
using System.Collections.Generic;
using System.Linq;
using JuegoDef.Env;
using UnityEditor;
using UnityEngine;

namespace JuegoDef.City
{
    /// <summary>
    /// Street objects as entities: each one is placed with its real volume, seated on the ground under its own
    /// footprint, and checked against everything already standing (facades, railings, parapets, tapias, other
    /// objects). An entity that touches something is pushed out along the penetration (at most a short way, so it
    /// stays where its placement rule meant it); one that still does not fit is not placed. Once placed it carries a
    /// collider, so later entities and the player treat it as a thing in the world too.
    /// The town's own props are CITY_* prefabs (front = local +Z, origin on the ground); everything else is an ENV module.
    /// </summary>
    public static class CityEntities
    {
        public const string PrefabDir = "Assets/JuegoDef/City/Props/Prefabs";
        static readonly Dictionary<string, GameObject> Prefabs = new Dictionary<string, GameObject>();

        public static bool Exists(string name) => name.StartsWith("CITY_") ? Prefab(name) != null : EnvKit.HasModule(name);

        static GameObject Prefab(string name)
        {
            if (!Prefabs.TryGetValue(name, out var p) || !p) Prefabs[name] = p = AssetDatabase.LoadAssetAtPath<GameObject>($"{PrefabDir}/{name}.prefab");
            return p;
        }

        public static GameObject Place(string name, Transform parent, Vector3 localPos, float rotY, Vector3? scale = null)
        {
            if (!name.StartsWith("CITY_")) return EnvKit.Place(name, parent, localPos, rotY, scale);
            var go = (GameObject)PrefabUtility.InstantiatePrefab(Prefab(name), parent);
            go.transform.localPosition = localPos;
            go.transform.localRotation = Quaternion.Euler(0, rotY, 0);
            if (scale.HasValue) go.transform.localScale = scale.Value;
            return go;
        }

        static bool IsTree(string n) => n.Contains("Tree") || n.Contains("Palmera");

        /// <summary>The entity's footprint box in its own local frame (renderer meshes, not colliders). Trees count
        /// their trunk and the heart of the crown: a crown may brush a cornice, its heart may not enter a house.</summary>
        public static Bounds LocalBox(GameObject go)
        {
            var root = go.transform;
            bool first = true;
            var b = new Bounds();
            foreach (var mf in go.GetComponentsInChildren<MeshFilter>())
            {
                if (!mf.sharedMesh) continue;
                var mb = mf.sharedMesh.bounds;
                for (int i = 0; i < 8; i++)
                {
                    var c = mb.center + Vector3.Scale(mb.extents, new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1));
                    var p = root.InverseTransformPoint(mf.transform.TransformPoint(c));
                    if (first) { b = new Bounds(p, Vector3.zero); first = false; } else b.Encapsulate(p);
                }
            }
            if (IsTree(go.name)) b = new Bounds(new Vector3(b.center.x, b.center.y, b.center.z), new Vector3(b.size.x * 0.75f, b.size.y, b.size.z * 0.75f));
            return b;
        }

        // the solid plan of every building (its basement, plot line to back wall): a shell of facade colliders is
        // hollow to the physics queries, the plan is not
        static List<(Transform t, Vector2 min, Vector2 max)> cores = new List<(Transform, Vector2, Vector2)>();

        public static int IndexBuildings(Transform buildingsRoot)
        {
            cores.Clear();
            if (!buildingsRoot) return 0;
            foreach (Transform b in buildingsRoot)
            {
                if (!b.name.StartsWith("BLD_")) continue;
                var basement = b.Find("Basement");
                var src = basement ? basement.gameObject : b.gameObject;
                bool first = true;
                var lb = new Bounds();
                foreach (var mf in src.GetComponentsInChildren<MeshFilter>())
                {
                    if (!mf.sharedMesh) continue;
                    var mb = mf.sharedMesh.bounds;
                    for (int i = 0; i < 8; i++)
                    {
                        var c = mb.center + Vector3.Scale(mb.extents, new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1));
                        var p = b.InverseTransformPoint(mf.transform.TransformPoint(c));
                        if (first) { lb = new Bounds(p, Vector3.zero); first = false; } else lb.Encapsulate(p);
                    }
                }
                if (first) continue;
                cores.Add((b, new Vector2(lb.min.x + 0.1f, lb.min.z + 0.1f), new Vector2(lb.max.x - 0.1f, Mathf.Min(lb.max.z - 0.1f, 0f))));
            }
            return cores.Count;
        }

        /// <summary>Horizontal push that takes the footprint out of every building plan it enters (zero if none).</summary>
        static Vector3 CorePush(Transform t, Bounds lb)
        {
            var push = Vector3.zero;
            var pos = t.position;
            var corners = new[] { new Vector3(lb.min.x, 0, lb.min.z), new Vector3(lb.max.x, 0, lb.min.z), new Vector3(lb.min.x, 0, lb.max.z), new Vector3(lb.max.x, 0, lb.max.z), new Vector3(lb.center.x, 0, lb.center.z) };
            foreach (var (b, mn, mx) in cores)
            {
                if ((b.position - pos).sqrMagnitude > 2500f) continue;
                Vector2 cmin = new Vector2(float.MaxValue, float.MaxValue), cmax = new Vector2(float.MinValue, float.MinValue);
                foreach (var c in corners)
                {
                    var l = b.InverseTransformPoint(t.TransformPoint(c + Vector3.up * 0.3f));
                    cmin = Vector2.Min(cmin, new Vector2(l.x, l.z)); cmax = Vector2.Max(cmax, new Vector2(l.x, l.z));
                }
                if (cmax.x <= mn.x || cmin.x >= mx.x || cmax.y <= mn.y || cmin.y >= mx.y) continue;
                // the shortest way out of the plan, in the building's own frame
                float left = cmax.x - mn.x, right = mx.x - cmin.x, back = cmax.y - mn.y, front = mx.y - cmin.y;
                float m = Mathf.Min(Mathf.Min(left, right), Mathf.Min(back, front));
                var lp = m == left ? new Vector3(-left, 0, 0) : m == right ? new Vector3(right, 0, 0) : m == back ? new Vector3(0, 0, -back) : new Vector3(0, 0, front);
                var w = b.TransformVector(lp);
                push += new Vector3(w.x, 0, w.z) * 1.05f + new Vector3(w.x, 0, w.z).normalized * 0.03f;
            }
            return push;
        }

        /// <summary>Ground height under (x, z): the ground hit closest to <paramref name="refY"/>.</summary>
        public static float? GroundY(float x, float z, float refY, Func<Collider, bool> isGround)
        {
            var hits = Physics.RaycastAll(new Vector3(x, refY + 6f, z), Vector3.down, 30f).Where(h => isGround(h.collider)).ToList();
            if (hits.Count == 0) return null;
            return hits.OrderBy(h => Mathf.Abs(h.point.y - refY)).First().point.y;
        }

        /// <summary>Seats the entity on the ground under its footprint. Vehicles follow the slope (four wheels on the
        /// ground); stalls, terraces and benches drop to the lowest corner so no leg floats.</summary>
        public static void Settle(GameObject go, Func<Collider, bool> isGround, bool tilt)
        {
            if (IsTree(go.name)) return;                         // a trunk stands on one point
            var t = go.transform;
            var lb = LocalBox(go);
            float hx = lb.extents.x * 0.8f, hz = lb.extents.z * 0.8f;
            if (Mathf.Max(hx, hz) < 0.6f) return;               // small things: the centre ray is enough
            float y0 = t.position.y;
            var sc = t.lossyScale;
            hx *= sc.x; hz *= sc.z;
            Vector3 W(float lx, float lz) => t.position + Quaternion.Euler(0, t.eulerAngles.y, 0) * new Vector3(lb.center.x * sc.x + lx, 0, lb.center.z * sc.z + lz);
            var pts = new[] { W(-hx, hz), W(hx, hz), W(-hx, -hz), W(hx, -hz) };
            var ys = pts.Select(p => GroundY(p.x, p.z, y0, isGround) ?? y0).ToArray();
            if (tilt)
            {
                var P = pts.Select((p, i) => new Vector3(p.x, ys[i], p.z)).ToArray();
                var fwd = ((P[0] + P[1]) - (P[2] + P[3])).normalized;
                var right = ((P[1] + P[3]) - (P[0] + P[2])).normalized;
                var up = Vector3.Cross(fwd, right).normalized;
                t.rotation = Quaternion.LookRotation(fwd, up);
                t.position = new Vector3(t.position.x, ys.Average(), t.position.z);
            }
            else t.position = new Vector3(t.position.x, Mathf.Min(y0, ys.Min()), t.position.z);
        }

        /// <summary>Pushes the entity out of whatever it touches (buildings, railings, parapets, tapias, other
        /// entities), up to <paramref name="maxShift"/> metres sideways. Returns false if it still does not fit.</summary>
        public static bool Resolve(GameObject go, Func<Collider, bool> isTerrain, float maxShift, out float shifted) =>
            Resolve(go, isTerrain, maxShift, out shifted, out _);

        public static bool Resolve(GameObject go, Func<Collider, bool> isTerrain, float maxShift, out float shifted, out string blocker)
        {
            shifted = 0f;
            blocker = null;
            var t = go.transform;
            var own = new HashSet<Collider>(go.GetComponentsInChildren<Collider>(true));
            var lb = LocalBox(go);
            // the box starts 0.22 m above the base: the floor it stands on and a kerb or slope under a leg do not count
            const float lift = 0.22f;
            var ws = Vector3.Scale(lb.size, t.lossyScale);
            var size = new Vector3(Mathf.Max(0.05f, ws.x - 0.06f), Mathf.Max(0.05f, ws.y - lift), Mathf.Max(0.05f, ws.z - 0.06f));
            var probe = new GameObject("__probe") { hideFlags = HideFlags.HideAndDontSave };
            var box = probe.AddComponent<BoxCollider>();
            box.size = size;
            var start = t.position;
            try
            {
                for (int it = 0; it < 6; it++)
                {
                    var centre = t.TransformPoint(new Vector3(lb.center.x, lb.min.y, lb.center.z)) + t.up * (lift + size.y / 2f);
                    probe.transform.SetPositionAndRotation(centre, t.rotation);
                    Physics.SyncTransforms();
                    var push = Vector3.zero;
                    int touching = 0;
                    foreach (var c in Physics.OverlapBox(centre, size / 2f, t.rotation, ~0, QueryTriggerInteraction.Ignore))
                    {
                        if (c == box || own.Contains(c) || isTerrain(c)) continue;
                        if (!Physics.ComputePenetration(box, centre, t.rotation, c, c.transform.position, c.transform.rotation, out var dir, out var dist)) continue;
                        var h = new Vector3(dir.x, 0, dir.z);
                        if (h.sqrMagnitude < 0.04f) continue;            // only something above or below: an eave, a floor
                        touching++;
                        blocker = Owner(c.transform);
                        push += h.normalized * (dist / h.magnitude + 0.02f);
                    }
                    var core = CorePush(t, lb);
                    if (core.sqrMagnitude > 1e-6f) { touching++; push += core; blocker = "plan"; }
                    if (touching == 0) { shifted = Vector3.Distance(new Vector3(start.x, 0, start.z), new Vector3(t.position.x, 0, t.position.z)); return true; }
                    t.position += push;
                    if (Vector3.Distance(new Vector3(start.x, 0, start.z), new Vector3(t.position.x, 0, t.position.z)) > maxShift) break;
                }
                t.position = start;
                return false;
            }
            finally { UnityEngine.Object.DestroyImmediate(probe); }
        }

        static string Owner(Transform t)
        {
            for (var p = t; p != null; p = p.parent)
                if (p.name.StartsWith("BLD_") || p.parent == null || p.parent.parent == null) return p.name.Split(' ')[0] + "/" + t.name;
            return t.name;
        }

        /// <summary>True if the entity's footprint enters a building's plan (inside a hollow shell counts).</summary>
        public static bool InsidePlan(GameObject go, out string host)
        {
            host = null;
            var t = go.transform;
            var lb = LocalBox(go);
            var shrunk = new Bounds(lb.center, new Vector3(Mathf.Max(0.02f, lb.size.x - 0.1f), lb.size.y, Mathf.Max(0.02f, lb.size.z - 0.1f)));
            foreach (var (b, mn, mx) in cores)
            {
                if ((b.position - t.position).sqrMagnitude > 2500f) continue;
                foreach (var c in new[] { new Vector3(shrunk.min.x, 0, shrunk.min.z), new Vector3(shrunk.max.x, 0, shrunk.min.z), new Vector3(shrunk.min.x, 0, shrunk.max.z), new Vector3(shrunk.max.x, 0, shrunk.max.z), new Vector3(shrunk.center.x, 0, shrunk.center.z) })
                {
                    var l = b.InverseTransformPoint(t.TransformPoint(c));
                    if (l.x > mn.x && l.x < mx.x && l.z > mn.y && l.z < mx.y) { host = b.name; return true; }
                }
            }
            return false;
        }

        /// <summary>A rope between two points hanging in a shallow curve: one small tube mesh (no collider).</summary>
        public static GameObject Rope(Transform parent, string name, Vector3 a, Vector3 b, float sag, float radius, Material m)
        {
            const int seg = 10, sides = 4;
            var verts = new List<Vector3>(); var tris = new List<int>();
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.transform.position = a;
            Vector3 P(float t) => Vector3.Lerp(a, b, t) + Vector3.down * (4f * sag * t * (1 - t)) - a;
            for (int i = 0; i <= seg; i++)
            {
                float t = i / (float)seg;
                var dir = (P(Mathf.Min(1, t + 0.01f)) - P(Mathf.Max(0, t - 0.01f))).normalized;
                var side = Vector3.Cross(dir, Vector3.up).normalized; if (side.sqrMagnitude < 1e-4f) side = Vector3.right;
                var up = Vector3.Cross(side, dir);
                for (int k = 0; k < sides; k++)
                {
                    float ang = k * Mathf.PI * 2f / sides;
                    verts.Add(P(t) + (side * Mathf.Cos(ang) + up * Mathf.Sin(ang)) * radius);
                }
            }
            for (int i = 0; i < seg; i++)
                for (int k = 0; k < sides; k++)
                {
                    int a0 = i * sides + k, a1 = i * sides + (k + 1) % sides, b0 = a0 + sides, b1 = a1 + sides;
                    tris.AddRange(new[] { a0, b0, a1, a1, b0, b1 });
                }
            var mesh = new Mesh { name = name };
            mesh.SetVertices(verts); mesh.SetTriangles(tris, 0); mesh.RecalculateNormals(); mesh.RecalculateBounds();
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var mr = go.AddComponent<MeshRenderer>(); mr.sharedMaterial = m;
            mr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            go.isStatic = true;
            return go;
        }

        /// <summary>Gives a placed entity a body if it has none: small things a box, tall ones (trees, posts) their trunk.</summary>
        public static void EnsureBody(GameObject go)
        {
            if (go.GetComponentsInChildren<Collider>(true).Length > 0) return;
            var lb = LocalBox(go);
            if (lb.size.y <= 2.2f)
            {
                var bc = go.AddComponent<BoxCollider>();
                bc.center = lb.center; bc.size = Vector3.Scale(lb.size, new Vector3(0.8f, 1f, 0.8f));
            }
            else
            {
                var cc = go.AddComponent<CapsuleCollider>();
                cc.radius = 0.28f; cc.height = 3f; cc.center = new Vector3(lb.center.x, 1.5f, lb.center.z);
            }
        }
    }
}

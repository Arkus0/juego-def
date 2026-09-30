using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// Read-only Scene-view overlay of the CASCO mechanical diagnostic
    /// (Tools/casco_diagnostic.py -> Docs/evidence/CASCO-V2-DIAG/casco_diagnostic.json).
    /// Draws plot footprints by heuristic class, grouping candidates, residual gaps and
    /// the deliberate urban space (streets, plazas, water, yards) on top of the built
    /// district. Strictly non-destructive: it creates no GameObjects, writes nothing to
    /// the scene and saves nothing — only Handles drawing and a console verification of
    /// five sampled buildings against the diagnostic's expected transforms. Thresholds
    /// displayed in the window come from the JSON's config block (heuristics, never
    /// product truth; changing them means re-running the tool with a new config).
    /// </summary>
    public class EnvCascoDiag : EditorWindow
    {
        const string MenuPath = "JuegoDef/ENV/Casco Diagnostic Overlay";
        const string DefaultJson = "Docs/evidence/CASCO-V2-DIAG/casco_diagnostic.json";

        // ---------------------------------------------------------------- data

        class Plot
        {
            public string id, kind;
            public float w, depth, floors, y;
            public bool small, minFront, narrow;
            public Vector3[] rect;      // world XZ corners at y (not lifted)
        }

        class Cand
        {
            public string id;
            public int size, nSmall;
            public float frontage;
            public Vector3[] hull;      // world XZ corners at 0
            public Vector3 labelAt;
        }

        class Poly
        {
            public float area;
            public Vector3[] pts;       // world XZ at probed ground height
            public bool convex;
        }

        List<Plot> _plots = new List<Plot>();
        List<Cand> _cands = new List<Cand>();
        List<Poly> _residual = new List<Poly>();
        List<Poly> _deliberate = new List<Poly>();
        List<Poly> _water = new List<Poly>();
        List<(Vector3[] pts, float width)> _streets = new List<(Vector3[], float)>();
        List<(Vector3[] pts, string id)> _plazas = new List<(Vector3[], string)>();
        string _thresholds = "";
        string _source = "";

        // ---------------------------------------------------------------- ui state

        string _jsonPath = DefaultJson;
        bool _layerPlots = true, _layerCands = true, _layerResidual = true, _layerDeliberate = true;
        bool _onlyDeficientCands = true, _labels = true;
        int _candMin = 2, _candMax = 6;
        float _alpha = 0.28f;

        [MenuItem(MenuPath)]
        public static void Open()
        {
            var w = GetWindow<EnvCascoDiag>("CASCO Diag");
            w.minSize = new Vector2(340, 420);
            w.Load();
        }

        void OnEnable() { SceneView.duringSceneGui += OnSceneGUI; }
        void OnDisable() { SceneView.duringSceneGui -= OnSceneGUI; }

        // ---------------------------------------------------------------- load

        void Load()
        {
            _plots.Clear(); _cands.Clear(); _residual.Clear();
            _deliberate.Clear(); _water.Clear(); _streets.Clear(); _plazas.Clear();
            var abs = Path.Combine(Directory.GetCurrentDirectory(), _jsonPath);
            if (!File.Exists(abs)) { _source = "not found: " + _jsonPath; return; }
            var root = JObject.Parse(File.ReadAllText(abs));
            _source = _jsonPath;

            foreach (var p in (JArray)root["plots"])
            {
                var rect = PtsWithY((JArray)p["rect_xz"], OptFloat(p["y"]) + 0.25f);
                if (rect == null) continue;
                _plots.Add(new Plot
                {
                    id = (string)p["id"],
                    kind = (string)p["kind"],
                    w = OptFloat(p["w"]),
                    depth = OptFloat(p["depth"]),
                    floors = OptFloat(p["floors"]),
                    y = OptFloat(p["y"]),
                    small = OptBool(p["flag_small_footprint"]),
                    minFront = OptBool(p["flag_below_min_frontage"]),
                    narrow = OptBool(p["flag_narrow"]),
                    rect = rect,
                });
            }

            foreach (var c in (JArray)root["candidates"])
            {
                var hull = PtsWithY((JArray)c["hull_xz"], 0f);
                if (hull == null) continue;
                float y = 0f;
                var members = (JArray)c["member_ids"];
                var labelPlot = _plots.FirstOrDefault(q => q.id == (string)members[0]);
                if (labelPlot != null) y = labelPlot.y + 3.2f + 0.5f * (float)c["size"];
                _cands.Add(new Cand
                {
                    id = (string)c["id"],
                    size = (int)c["size"],
                    nSmall = (int)c["n_small_members"],
                    frontage = OptFloat(c["frontage_combined_m"]),
                    hull = hull.Select(v => new Vector3(v.x, y, v.z)).ToArray(),
                    labelAt = new Vector3(hull.Average(v => v.x), y, hull.Average(v => v.z)),
                });
            }

            var ov = (JObject)root["debug_overlay"];
            float waterY = OptFloat(ov["water_y"], -3f) + 0.06f;
            _water = LoadPolys((JArray)ov["water_poly"], waterY);
            _residual = LoadPolys((JArray)ov["residual_polys"], float.NaN);
            _deliberate = LoadPolys((JArray)ov["deliberate_polys"], float.NaN);
            foreach (var s in (JArray)ov["street_ribbons"])
            {
                var pts = ((JArray)s["pts"]).Select(q => new Vector3((float)q[0], (float)q[2] + 0.07f, (float)q[1])).ToArray();
                if (pts.Length >= 2) _streets.Add((pts, (float)s["width"]));
            }
            foreach (var p in (JArray)ov["plazas"])
            {
                var pts = PtsWithY((JArray)p["poly"], OptFloat(p["y"]) + 0.07f);
                if (pts != null) _plazas.Add((pts, (string)p["id"]));
            }

            var h = (JObject)root["config_used"]["heuristics"];
            _thresholds = string.Format(
                "heuristics (from JSON, read-only):\n  min_interior_footprint = {0} m2\n" +
                "  min_interior_frontage = {1} m\n  narrow_plot_max_w = {2} m\n" +
                "  absorb_buffer = {3} m\n  candidate sizes = {4}..{5}",
                h["min_interior_footprint_m2"], h["min_interior_frontage_m"],
                h["narrow_plot_max_w_m"], h["absorb_buffer_m"],
                ((JArray)h["candidate_sizes"]).Min(), ((JArray)h["candidate_sizes"]).Max());
            Repaint();
            Debug.Log($"JD_CASCO_DIAG loaded {_plots.Count} plots, {_cands.Count} candidates, " +
                      $"{_residual.Count} residual polys from {_jsonPath}");
        }

        static float OptFloat(JToken t, float d = 0f) => t == null ? d : (float)t;
        static bool OptBool(JToken t) => t != null && (bool)t;

        static Vector3[] PtsWithY(JArray arr, float y)
        {
            if (arr == null || arr.Count < 3) return null;
            var pts = new List<Vector3>();
            foreach (var q in arr) pts.Add(new Vector3((float)q[0], y, (float)q[1]));
            if (pts[0] == pts[pts.Count - 1]) pts.RemoveAt(pts.Count - 1);
            return pts.ToArray();
        }

        static readonly Dictionary<Vector3, float> _groundCache = new Dictionary<Vector3, float>();

        static float GroundY(float x, float z)
        {
            var k = new Vector3(Mathf.Round(x * 4f) / 4f, 0, Mathf.Round(z * 4f) / 4f);
            if (_groundCache.TryGetValue(k, out float y)) return y;
            var hit = Physics.RaycastAll(new Ray(new Vector3(k.x, 60f, k.z), Vector3.down), 80f);
            y = 0.25f;
            float best = float.PositiveInfinity;
            foreach (var h in hit)
                if (h.distance < best && !h.collider.isTrigger) { best = h.distance; y = h.point.y + 0.25f; }
            _groundCache[k] = y;
            return y;
        }

        List<Poly> LoadPolys(JArray arr, float fixedY)
        {
            var list = new List<Poly>();
            if (arr == null) return list;
            foreach (var e in arr)
            {
                JArray coords = e is JObject o && o["coords"] != null ? (JArray)o["coords"] : e as JArray;
                if (coords == null || coords.Count < 3) continue;
                var pts = new Vector3[coords.Count];
                float cx = 0f, cz = 0f;
                for (int i = 0; i < coords.Count; i++)
                {
                    float x = (float)coords[i][0], z = (float)coords[i][1];
                    pts[i] = new Vector3(x, 0f, z);
                    cx += x; cz += z;
                }
                // one ground probe per polygon (per-vertex probing would cast thousands of
                // raycasts against the district colliders on every load)
                float y = float.IsNaN(fixedY) ? GroundY(cx / pts.Length, cz / pts.Length) : fixedY;
                for (int i = 0; i < pts.Length; i++) pts[i].y = y;
                list.Add(new Poly { area = e is JObject o2 && o2["area_m2"] != null ? (float)o2["area_m2"] : 0f,
                                    pts = pts, convex = IsConvex(pts) });
            }
            return list;
        }

        static bool IsConvex(Vector3[] p)
        {
            int n = p.Length;
            if (n < 4) return true;
            bool pos = false, neg = false;
            for (int i = 0; i < n; i++)
            {
                var a = p[i]; var b = p[(i + 1) % n]; var c = p[(i + 2) % n];
                float cross = (b.x - a.x) * (c.z - b.z) - (b.z - a.z) * (c.x - b.x);
                if (cross > 1e-4f) pos = true; else if (cross < -1e-4f) neg = true;
                if (pos && neg) return false;
            }
            return true;
        }

        // ---------------------------------------------------------------- draw

        void OnSceneGUI(SceneView sv)
        {
            if (_plots.Count == 0) return;
            var cam = sv.camera;

            if (_layerDeliberate)
            {
                var cyan = new Color(0.2f, 0.8f, 0.9f, _alpha * 0.45f);
                foreach (var (pts, width) in _streets) DrawRibbon(pts, width, cyan);
                foreach (var (pts, _) in _plazas) FillConvex(pts, cyan);
                foreach (var w in _water) FillConvex(w.pts, new Color(0.2f, 0.5f, 0.95f, _alpha * 0.45f));
                foreach (var d in _deliberate) FillConvex(d.pts, cyan);
            }

            if (_layerResidual)
            {
                var yellow = new Color(0.95f, 0.9f, 0.2f, _alpha);
                foreach (var r in _residual)
                {
                    FillConvex(r.pts, yellow);
                    Handles.color = new Color(0.9f, 0.8f, 0.1f, 0.9f);
                    Handles.DrawAAPolyLine(2f, CloseLoop(r.pts));
                }
            }

            if (_layerPlots)
            {
                var green = new Color(0.3f, 0.85f, 0.4f, _alpha);
                var amber = new Color(0.95f, 0.6f, 0.1f, _alpha);
                var red = new Color(1f, 0.25f, 0.2f, _alpha + 0.1f);
                foreach (var p in _plots)
                {
                    if (p.kind != "building")
                    {
                        Handles.color = new Color(0.7f, 0.7f, 0.7f, 0.8f);
                        Handles.DrawAAPolyLine(2f, CloseLoop(p.rect));
                        continue;
                    }
                    FillConvex(p.rect, p.small || p.minFront ? red : p.narrow ? amber : green);
                    if (_labels && cam != null &&
                        Vector3.Distance(cam.transform.position, p.rect[0]) < 70f)
                        Handles.Label(p.rect[0] + Vector3.up * 2.6f,
                            $"{p.id}\n{p.w:0.0}x{p.depth:0.0}m");
                }
            }

            if (_layerCands)
            {
                var blue = new Color(0.25f, 0.55f, 1f, 0.95f);
                foreach (var c in _cands)
                {
                    if (c.size < _candMin || c.size > _candMax) continue;
                    if (_onlyDeficientCands && c.nSmall == 0) continue;
                    Handles.color = blue;
                    Handles.DrawAAPolyLine(3.5f, CloseLoop(c.hull));
                    if (_labels && cam != null &&
                        Vector3.Distance(cam.transform.position, c.labelAt) < 110f)
                        Handles.Label(c.labelAt, $"{c.id}  {c.size}p  {c.frontage:0.0}m");
                }
            }
        }

        static Vector3[] CloseLoop(Vector3[] pts)
        {
            var closed = new Vector3[pts.Length + 1];
            pts.CopyTo(closed, 0);
            closed[pts.Length] = pts[0];
            return closed;
        }

        static void FillConvex(Vector3[] pts, Color c)
        {
            Handles.color = c;
            Handles.DrawAAConvexPolygon(pts);
        }

        static void DrawRibbon(Vector3[] pts, float width, Color c)
        {
            if (pts.Length < 2) return;
            var left = new List<Vector3>(); var right = new List<Vector3>();
            for (int i = 0; i < pts.Length; i++)
            {
                var dir = (pts[Mathf.Max(0, i - 1)] - pts[Mathf.Min(pts.Length - 1, i + 1)]).normalized;
                var n = new Vector3(-dir.z, 0, dir.x) * (width * 0.5f);
                left.Add(pts[i] + n); right.Add(pts[i] - n);
            }
            var poly = left.Concat(right.Reverse()).ToArray();
            if (IsConvex(poly)) { FillConvex(poly, c); return; }
            Handles.color = c; Handles.color = new Color(c.r, c.g, c.b, 0.9f);
            Handles.DrawAAPolyLine(2f, CloseLoop(poly));
        }

        // ---------------------------------------------------------------- window

        void OnGUI()
        {
            EditorGUILayout.HelpBox(
                "Read-only overlay of the CASCO diagnostic. Creates no GameObjects, " +
                "modifies nothing, saves nothing. Candidates are geometric data only — " +
                "no grouping has been chosen.", MessageType.Info);
            EditorGUILayout.BeginHorizontal();
            _jsonPath = EditorGUILayout.TextField(_jsonPath);
            if (GUILayout.Button("Load", GUILayout.Width(60))) Load();
            EditorGUILayout.EndHorizontal();
            EditorGUILayout.LabelField("source", _source);
            EditorGUILayout.Space();

            _layerPlots = EditorGUILayout.Toggle("Plots (red=below min / amber=narrow / green=above min)", _layerPlots);
            _layerCands = EditorGUILayout.Toggle("Grouping candidates", _layerCands);
            _layerResidual = EditorGUILayout.Toggle("Residual gaps", _layerResidual);
            _layerDeliberate = EditorGUILayout.Toggle("Deliberate urban space", _layerDeliberate);
            _labels = EditorGUILayout.Toggle("Labels", _labels);
            _alpha = EditorGUILayout.Slider("Fill alpha", _alpha, 0.05f, 0.6f);
            EditorGUILayout.MinMaxSlider("Candidate size", ref _candMin, ref _candMax, 2, 6);
            _onlyDeficientCands = EditorGUILayout.Toggle(
                "Only candidates with red (below-minimum) members", _onlyDeficientCands);

            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Legend");
            EditorGUILayout.LabelField("  ■ red", "below current minimum heuristic (NOT 'unreasonable' — no authoritative threshold exists)");
            EditorGUILayout.LabelField("  ■ amber", $"narrow (<= {NarrowLimit()} m) but above minimum");
            EditorGUILayout.LabelField("  ■ green", "above_current_minimum_heuristic (not 'reasonable' — provisional thresholds only)");
            EditorGUILayout.LabelField("  ■ yellow", "residual / unclassified");
            EditorGUILayout.LabelField("  ■ cyan", "deliberate per GENERATOR tags (street, plaza, water, yard) — not validated for V2");
            EditorGUILayout.LabelField("  □ blue", "2-6 plot grouping candidate (data only)");
            EditorGUILayout.HelpBox(_thresholds, MessageType.None);

            EditorGUILayout.Space();
            if (GUILayout.Button("Verify 5 sampled buildings (console, read-only)"))
                VerifySamples();
        }

        string NarrowLimit()
        {
            var h = _thresholds;
            int i = h.IndexOf("narrow_plot_max_w = ") + 20;
            return i > 20 ? h.Substring(i, Mathf.Min(4, h.Length - i)).Trim() : "?";
        }

        /// <summary>Console re-check of five buildings against the diagnostic's expected
        /// local transforms (the full 27-sample proof lives in scene_crosscheck.json).</summary>
        static void VerifySamples()
        {
            var abs = Path.Combine(Directory.GetCurrentDirectory(), DefaultJson);
            if (!File.Exists(abs)) { Debug.LogWarning("JD_CASCO_DIAG " + abs + " missing"); return; }
            var root = JObject.Parse(File.ReadAllText(abs));
            var rows = (JArray)root["plots"];
            var ids = new[] { "K8_3_0", "K14_3_0", "K14_1_0", "K11_0_1", "K14_3_6" };
            int ok = 0;
            foreach (var id in ids)
            {
                var p = rows.FirstOrDefault(q => (string)q["id"] == id);
                if (p == null) { Debug.Log($"JD_CASCO_DIAG {id}: not in diagnostic"); continue; }
                var go = GameObject.Find((string)p["id"]);
                if (go == null) { Debug.Log($"JD_CASCO_DIAG {id}: NOT FOUND in scene"); continue; }
                var exp = new Vector3((float)p["x0"], (float)p["y"], -(float)p["setback"]);
                var d = (go.transform.localPosition - exp).magnitude;
                bool pass = d <= 0.002f;
                if (pass) ok++;
                Debug.Log($"JD_CASCO_DIAG {id}: {(pass ? "OK" : "FAIL")} |expected {exp}|scene {go.transform.localPosition}|delta {d * 1000f:0.0} mm");
            }
            Debug.Log($"JD_CASCO_DIAG verify {ok}/{ids.Length} ok (tolerance 2 mm)");
        }
    }
}

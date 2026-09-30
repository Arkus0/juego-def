using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEditor;
using Debug = UnityEngine.Debug;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// Visual layout editor for an authored district trace (owner brief 2026-09-30: "quiero utilizar esto yo mismo
    /// como level designer visual"). Draws the trace (nodes, streets with their width, plazas, landmarks, river) in the
    /// Scene View and edits it in place: nodes drag on X/Z with a PositionHandle and an explicit height field, street
    /// via points, plaza vertices/discs, landmarks and river points drag too. Edits live in memory only — nothing
    /// dirties disk until SAVE TRACE writes the trace file (a .bak copy of the previous state first) and shows
    /// exactly which elements changed; REVERT drops them. REBUILD reruns the existing pipeline (Tools/env_district_skeleton.py
    /// with the pinned OSM extract -> district spec -> EnvDistrict): it diffs the regenerated spec against the current
    /// one, shows the impact, and rebuilds only the affected rows when that is provably safe (same row ids,
    /// ground/river/plazas/streets intact) or the whole district otherwise. REBUILD is transactional: all consents run
    /// before the spec is promoted, spec+scene are snapshotted, and any cancel/exception/reload rolls them back.
    /// Menu: JuegoDef &gt; ENV &gt; Layout Editor.
    /// Undo/Redo is real Unity Undo on a hidden ScriptableObject mirror of the editable points.
    /// </summary>
    public class EnvLayoutEditor : EditorWindow
    {
        const string MenuPath = "JuegoDef/ENV/Layout Editor";

        [MenuItem(MenuPath)]
        public static void Open() => GetWindow<EnvLayoutEditor>("ENV Layout Editor");

        // ---------------------------------------------------------------- state

        TraceEditState state;                    // the undo-able mirror of every editable point
        JObject doc, pristine;                   // live document and its last saved/loaded copy
        string tracePath = "", loadedText = "";  // file content as loaded, to detect external edits before overwriting
        string[] traceChoices = new string[0];
        int traceChoice;
        string districtId = "ENV01_Casco_District";
        readonly Dictionary<string, EditPt> nodeIndex = new Dictionary<string, EditPt>();
        int selected = -1;
        Vector2 scroll, changedScroll;
        string search = "";
        bool streetLabels;

        string SpecPath => $"{EnvDistrict.DistrictSpecs}/{districtId}.json";
        string TracePath => $"{EnvDistrict.DistrictSpecs}/{districtId}.trace.json";
        string OsmPrefsKey => $"JuegoDef.ENV.Layout.{districtId}.OsmPath";
        string OsmPath => EditorPrefs.GetString(OsmPrefsKey, "");
        string RepoRoot => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", ".."));

        public bool Dirty
        {
            get
            {
                if (state == null) return false;
                foreach (var p in state.pts)
                    if (p.Changed) return true;
                return false;
            }
        }

        void OnEnable()
        {
            Undo.undoRedoPerformed += OnUndoRedo;
            SceneView.duringSceneGui -= OnSceneGUI;
            SceneView.duringSceneGui += OnSceneGUI;
            ReloadTraceList();
            LoadTrace();
        }

        void OnDisable()
        {
            Undo.undoRedoPerformed -= OnUndoRedo;
            SceneView.duringSceneGui -= OnSceneGUI;
        }

        void OnUndoRedo()
        {
            if (state == null) return;
            state.ApplyToDoc(doc);
            RebuildNodeIndex();
            Repaint();
            SceneView.RepaintAll();
        }

        void ReloadTraceList()
        {
            traceChoices = Directory.Exists(EnvDistrict.DistrictSpecs)
                ? Directory.GetFiles(EnvDistrict.DistrictSpecs, "*.trace.json").Select(Path.GetFileName).OrderBy(n => n).ToArray()
                : new string[0];
            traceChoice = System.Math.Max(0, System.Array.IndexOf(traceChoices, districtId + ".trace.json"));
            if (traceChoices.Length > 0)
                districtId = traceChoices[traceChoice].Replace(".trace.json", "");
        }

        // ---------------------------------------------------------------- load / save / revert

        void LoadTrace()
        {
            tracePath = TracePath;
            if (!File.Exists(tracePath))
            {
                doc = pristine = null;
                state = null;
                return;
            }
            doc = JObject.Parse(EnvKit.ReadText(tracePath));
            loadedText = File.ReadAllText(tracePath);
            pristine = (JObject)doc.DeepClone();
            selected = -1;
            state = TraceEditState.FromDoc(doc);
            state.ApplyToDoc(doc);
            RebuildNodeIndex();
            Repaint();
            SceneView.RepaintAll();
        }

        void RebuildNodeIndex()
        {
            nodeIndex.Clear();
            if (state == null) return;
            foreach (var p in state.pts)
                if ((PtKind)p.kind == PtKind.Node)
                    nodeIndex[p.owner] = p;
        }

        /// <summary>Writes the edited document over the trace file, keeping a .bak of the previous state and every
        /// unknown JSON field untouched (only the known coordinate paths are ever written).</summary>
        void SaveTrace()
        {
            var changed = ChangedList().ToList();
            if (changed.Count == 0) return;
            if (!EditorUtility.DisplayDialog("Guardar trace",
                    $"Guardar {changed.Count} elemento(s) cambiado(s) en\n{tracePath}?\n\n(copia .bak del estado anterior)", "SAVE TRACE", "Cancelar"))
                return;
            if (File.Exists(tracePath) && File.ReadAllText(tracePath) != loadedText &&
                !EditorUtility.DisplayDialog("trace.json cambió en disco",
                    "El fichero cambió fuera del Layout Editor desde que se cargó (git, otro editor...).\n¿Sobrescribirlo con tu versión editada?", "Sobrescribir", "Cancelar"))
                return;
            if (File.Exists(tracePath))
                File.Copy(tracePath, tracePath + ".bak", true);
            File.WriteAllText(tracePath, doc.ToString(Formatting.Indented), new UTF8Encoding(false));
            loadedText = File.ReadAllText(tracePath);
            pristine = (JObject)doc.DeepClone();
            foreach (var p in state.pts) p.TakeBaseline();
            AssetDatabase.ImportAsset(tracePath);
            Debug.Log($"JD_LAYOUT_TRACE saved {changed.Count} element(s) -> {tracePath} (.bak kept)");
            Repaint();
        }

        void RevertTrace()
        {
            if (!Dirty || EditorUtility.DisplayDialog("Revertir", "Descartar TODOS los cambios sin guardar del trace?", "REVERT", "Cancelar"))
                LoadTrace();
        }

        /// <summary>Changed elements as readable lines "label: (x, z) -> (x, z)" for the pre-save review.</summary>
        public List<string> ChangedList()
        {
            var list = new List<string>();
            if (state == null || pristine == null) return list;
            foreach (var p in state.pts)
                if (p.Changed) list.Add(p.DiffLine());
            return list;
        }

        // ---------------------------------------------------------------- GUI (window)

        void OnGUI()
        {
            if (traceChoices.Length == 0) { EditorGUILayout.HelpBox("No hay *.trace.json en " + EnvDistrict.DistrictSpecs, MessageType.Warning); return; }

            EditorGUILayout.BeginHorizontal();
            var choice = EditorGUILayout.Popup("distrito", traceChoice, traceChoices);
            if (choice != traceChoice && !Dirty)
            {
                traceChoice = choice;
                districtId = traceChoices[choice].Replace(".trace.json", "");
                LoadTrace();
            }
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.LabelField(new GUIContent(tracePath.Replace('\\', '/')), EditorStyles.miniLabel);
            DrawToolbar();

            if (doc == null) { EditorGUILayout.HelpBox("No se pudo cargar " + tracePath, MessageType.Error); return; }
            if (LayoutRebuild.phase != LayoutRebuild.Phase.None) DrawRebuildStatus();
            else if (Dirty) DrawChangedList();

            DrawSelectionInspector();
            DrawElementList();
            DrawOsmRow();
        }

        /// <summary>Rebuild progress, log tail and reset when the pipeline failed.</summary>
        void DrawRebuildStatus()
        {
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField(LayoutRebuild.phase == LayoutRebuild.Phase.Failed ? "REBUILD — FALLO" : "REBUILD", EditorStyles.boldLabel);
            var rect = EditorGUILayout.GetControlRect(GUILayout.Height(18));
            EditorGUI.ProgressBar(rect, LayoutRebuild.progress, LayoutRebuild.status.Split('\n')[0]);
            if (LayoutRebuild.log.Count > 0)
            {
                EditorGUILayout.Space(2);
                var tail = string.Join("\n", LayoutRebuild.log.Skip(Mathf.Max(0, LayoutRebuild.log.Count - 5)));
                EditorGUILayout.LabelField(tail, EditorStyles.miniLabel);
            }
            if (GUILayout.Button("cerrar", EditorStyles.miniButton, GUILayout.Width(50)))
                LayoutRebuild.phase = LayoutRebuild.Phase.None;
            EditorGUILayout.EndVertical();
        }

        /// <summary>The pinned OSM extract the skeleton needs (real plot subdivision); it stays out of the repo, so the
        /// editor remembers the path. The documented fetch step creates it: python Tools/env_morphology.py fetch.</summary>
        void DrawOsmRow()
        {
            EditorGUILayout.BeginHorizontal();
            var ok = File.Exists(OsmPath);
            EditorGUILayout.LabelField(new GUIContent($"OSM {(ok ? "✓" : "✗ falta")}: {OsmPath}", "Extracto de OpenStreetMap que alimenta el skeleton"), EditorStyles.miniLabel);
            if (GUILayout.Button("elegir...", EditorStyles.miniButton, GUILayout.Width(58)))
            {
                var picked = EditorUtility.OpenFilePanel("Extracto OSM del CASCO (osm.json)", "", "json");
                if (picked != "") EditorPrefs.SetString(OsmPrefsKey, picked);
                Repaint();
            }
            if (GUILayout.Button("ruta por defecto", EditorStyles.miniButton, GUILayout.Width(100)))
            {
                var def = Path.Combine(System.Environment.GetFolderPath(System.Environment.SpecialFolder.LocalApplicationData), "JuegoDef", districtId + "_osm.json");
                EditorPrefs.SetString(OsmPrefsKey, def);
                if (!File.Exists(def))
                    EditorUtility.DisplayDialog("Extracto OSM", $"No existe {def}.\n\nCréalo con el paso documentado del pipeline:\n\npython Tools/env_morphology.py fetch --bbox 43.1521,-4.6244,43.1541,-4.6222 --out \"{def}\"", "OK");
                Repaint();
            }
            EditorGUILayout.EndHorizontal();
        }

        void DrawToolbar()
        {
            EditorGUILayout.BeginHorizontal(EditorStyles.helpBox);
            GUI.backgroundColor = Dirty ? new Color(0.55f, 1f, 0.55f) : Color.white;
            using (new EditorGUI.DisabledScope(!Dirty || LayoutRebuild.phase != LayoutRebuild.Phase.None))
                if (GUILayout.Button(new GUIContent("SAVE TRACE", "Escribe el trace.json (con .bak previo)"), GUILayout.Height(30), GUILayout.MinWidth(92)))
                    SaveTrace();
            GUI.backgroundColor = Dirty ? new Color(1f, 0.62f, 0.62f) : Color.white;
            using (new EditorGUI.DisabledScope(!Dirty))
                if (GUILayout.Button(new GUIContent("REVERT", "Descarta los cambios sin guardar"), GUILayout.Height(30), GUILayout.MinWidth(70)))
                    RevertTrace();
            bool rebuilding = LayoutRebuild.phase != LayoutRebuild.Phase.None;
            GUI.backgroundColor = new Color(1f, 0.78f, 0.45f);
            using (new EditorGUI.DisabledScope(Dirty || rebuilding || EditorApplication.isPlaying || OsmPath == "" || !File.Exists(OsmPath)))
                if (GUILayout.Button(new GUIContent(rebuilding ? "REBUILD..." : "REBUILD",
                        Dirty ? "Guarda el trace antes de reconstruir"
                        : rebuilding ? "Reconstrucción en curso"
                        : OsmPath == "" || !File.Exists(OsmPath) ? "Configura el extracto OSM (más abajo)"
                        : "Regenera la spec con el pipeline y reconstruye el distrito"), GUILayout.Height(30), GUILayout.MinWidth(84)))
                    LayoutRebuild.Start(districtId, Application.dataPath);
            GUI.backgroundColor = new Color(0.6f, 0.8f, 1f);
            if (GUILayout.Button(EditorApplication.isPlaying ? new GUIContent("STOP", "Sale de Play Mode") : new GUIContent("PLAY", "Entra en Play Mode"), GUILayout.Height(30), GUILayout.MinWidth(60)))
                EditorApplication.isPlaying = !EditorApplication.isPlaying;
            GUI.backgroundColor = Color.white;
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.BeginHorizontal();
            streetLabels = GUILayout.Toggle(streetLabels, "nombres de calles", EditorStyles.miniButton, GUILayout.Width(120));
            GUILayout.Label(Dirty ? $"● {ChangedList().Count} cambio(s) SIN GUARDAR" : "sin cambios", Dirty ? EditorStyles.boldLabel : EditorStyles.miniLabel);
            GUILayout.FlexibleSpace();
            EditorGUILayout.EndHorizontal();
        }

        void DrawChangedList()
        {
            var changed = ChangedList();
            changedScroll = EditorGUILayout.BeginScrollView(changedScroll, GUILayout.MaxHeight(96));
            foreach (var line in changed)
                EditorGUILayout.LabelField(line, EditorStyles.miniLabel);
            EditorGUILayout.EndScrollView();
        }

        void DrawSelectionInspector()
        {
            var p = SelectedPt;
            if (p == null) { EditorGUILayout.HelpBox("Click en un punto de la Scene View (o en la lista) para seleccionar y arrastrar. Y editable aquí.", MessageType.Info); return; }

            EditorGUILayout.LabelField(p.label, EditorStyles.boldLabel);
            EditorGUILayout.BeginHorizontal();
            EditorGUI.BeginChangeCheck();
            Undo.RecordObject(state, "Edit " + p.label);
            var x = EditorGUILayout.FloatField("x (este)", p.x);
            var z = EditorGUILayout.FloatField("z (norte)", p.z);
            if (EditorGUI.EndChangeCheck()) { p.x = x; p.z = z; AfterEdit(p); }

            if ((PtKind)p.kind == PtKind.PlazaDiscRadius)
            {
                EditorGUI.BeginChangeCheck();
                Undo.RecordObject(state, "Edit " + p.label);
                var r = EditorGUILayout.FloatField("radio (m)", p.radius);
                if (EditorGUI.EndChangeCheck()) { p.radius = Mathf.Max(0.5f, r); AfterEdit(p); }
            }
            else if ((PtKind)p.kind == PtKind.Node || (p.hasH && (PtKind)p.kind == PtKind.StreetVia))
            {
                EditorGUI.BeginChangeCheck();
                Undo.RecordObject(state, "Edit " + p.label);
                var h = EditorGUILayout.FloatField("altura Y (m)", p.h);
                if (EditorGUI.EndChangeCheck()) { p.h = h; AfterEdit(p); }
            }
            else if ((PtKind)p.kind == PtKind.StreetVia)
            {
                if (GUILayout.Button(new GUIContent("fijar altura", "Convierte el punto en [x, z, h] con altura fija"), EditorStyles.miniButton, GUILayout.Width(78)))
                {
                    Undo.RecordObject(state, "Set via height " + p.label);
                    p.hasH = true;
                    AfterEdit(p);
                }
                GUILayout.Label("(se interpola)", EditorStyles.miniLabel);
            }
            EditorGUILayout.EndHorizontal();
            EditorGUILayout.Space(2);
        }

        void AfterEdit(EditPt p)
        {
            state.ApplyToDoc(doc);
            EditorUtility.SetDirty(state);
            Repaint();
            SceneView.RepaintAll();
        }

        EditPt SelectedPt => state != null && selected >= 0 && selected < state.pts.Count ? state.pts[selected] : null;

        void Select(EditPt p, bool frame = false)
        {
            selected = state.pts.IndexOf(p);
            Repaint();
            if (frame && SceneView.lastActiveSceneView != null)
            {
                var w = WorldOf(p);
                SceneView.lastActiveSceneView.pivot = w;
                SceneView.lastActiveSceneView.size = Mathf.Max(12f, p.radius * 3f);
                SceneView.lastActiveSceneView.Repaint();
            }
        }

        void DrawElementList()
        {
            search = EditorGUILayout.TextField("buscar", search);
            scroll = EditorGUILayout.BeginScrollView(scroll);
            DrawGroup("nodes", PtKind.Node, p => true);
            DrawGroup("calles (vía)", PtKind.StreetVia, p => true);
            DrawGroup("plazas", PtKind.PlazaVertex, p => true);
            DrawGroup("plazas (discos)", PtKind.PlazaDisc, p => true);
            DrawGroup("landmarks", PtKind.Landmark, p => true);
            DrawGroup("río", PtKind.River, p => true);
            EditorGUILayout.EndScrollView();
        }

        void DrawGroup(string title, PtKind kind, System.Func<EditPt, bool> filter)
        {
            var matches = state.pts.Where(p => (PtKind)p.kind == kind && Matches(p)).ToList();
            if (matches.Count == 0) return;
            EditorGUILayout.LabelField($"{title} ({matches.Count})", EditorStyles.boldLabel);
            foreach (var p in matches)
            {
                var style = state.pts.IndexOf(p) == selected ? EditorStyles.whiteLargeLabel : EditorStyles.miniLabel;
                var mark = p.Changed ? "* " : "";
                EditorGUILayout.BeginHorizontal();
                if (GUILayout.Button(mark + p.label, style))
                    Select(p, frame: true);
                if ((PtKind)p.kind == PtKind.Node && GUILayout.Button("ir", EditorStyles.miniButton, GUILayout.Width(30)))
                    Select(p, frame: true);
                EditorGUILayout.EndHorizontal();
            }
        }

        bool Matches(EditPt p) => string.IsNullOrEmpty(search) || p.label.IndexOf(search, System.StringComparison.OrdinalIgnoreCase) >= 0;

        // ---------------------------------------------------------------- scene view

        Vector3 WorldOf(EditPt p)
        {
            float ox = doc?["unityOffset"]?[0]?.Value<float>() ?? 68f;
            float oy = doc?["unityOffset"]?[1]?.Value<float>() ?? 238f;
            float h = (PtKind)p.kind switch
            {
                PtKind.Node => p.h,
                PtKind.StreetVia => p.h,
                PtKind.PlazaVertex => PlazaY(p.owner),
                PtKind.PlazaDisc => PlazaY(p.owner),
                PtKind.PlazaDiscRadius => PlazaY(p.owner),
                PtKind.Landmark => 1.2f,
                PtKind.River => (doc?["river"]?["water"]?.Value<float>() ?? -3f) + 0.05f,
                _ => 0f
            };
            return new Vector3(p.x + ox, h, p.z + oy);
        }

        readonly Dictionary<string, float> plazaYCache = new Dictionary<string, float>();
        float PlazaY(string plazaId)
        {
            if (plazaYCache.TryGetValue(plazaId, out var y)) return y;
            y = 0.3f;
            var pz = ((JArray)doc["plazas"]).Cast<JObject>().FirstOrDefault(q => (string)q["id"] == plazaId);
            if (pz != null && pz["y"] != null) y = (float)pz["y"];
            plazaYCache[plazaId] = y;
            return y;
        }

        static readonly Dictionary<string, Color> RoleColor = new Dictionary<string, Color>
        {
            { "main", new Color(1f, 0.78f, 0.25f) }, { "secondary", new Color(0.45f, 0.78f, 1f) },
            { "lane", new Color(0.55f, 0.9f, 0.55f) }, { "steps", new Color(1f, 0.5f, 0.5f) },
            { "bridge", new Color(0.5f, 0.6f, 1f) }, { "footbridge", new Color(0.7f, 0.85f, 1f) },
        };

        void OnSceneGUI(SceneView sv)
        {
            if (doc == null || state == null || EditorApplication.isPlaying) return;
            plazaYCache.Clear();
            bool editing = LayoutRebuild.phase == LayoutRebuild.Phase.None;
            var sel = SelectedPt;
            var touchedStreets = TouchedStreetIds(sel);

            DrawRiver();
            foreach (var st in ((JArray)doc["streets"]).Cast<JObject>())
                DrawStreet(st, touchedStreets.Contains((string)st["id"]));
            foreach (var pz in ((JArray)doc["plazas"]).Cast<JObject>())
                DrawPlaza(pz, sel != null && sel.owner == (string)pz["id"] && ((PtKind)sel.kind == PtKind.PlazaVertex || (PtKind)sel.kind == PtKind.PlazaDisc || (PtKind)sel.kind == PtKind.PlazaDiscRadius));
            DrawLandmarks();

            // pickers (click to select), then the PositionHandle of the selection so it wins focus
            if (editing)
                foreach (var p in state.pts)
                    DrawPicker(p);

            if (editing && sel != null)
            {
                EditorGUI.BeginChangeCheck();
                Undo.RecordObject(state, "Move " + sel.label);
                var np = Handles.PositionHandle(WorldOf(sel), Quaternion.identity);
                if (EditorGUI.EndChangeCheck())
                {
                    float ox = (float)doc["unityOffset"][0], oy = (float)doc["unityOffset"][1];
                    if ((PtKind)sel.kind == PtKind.PlazaDiscRadius)
                        sel.radius = Mathf.Max(0.5f, Vector2.Distance(new Vector2(np.x - ox, np.z - oy), new Vector2(sel.x, sel.z)));
                    else
                    {
                        sel.x = np.x - ox;
                        sel.z = np.z - oy;
                        if ((PtKind)sel.kind == PtKind.Node || (PtKind)sel.kind == PtKind.StreetVia || (PtKind)sel.kind == PtKind.Landmark) sel.h = np.y;
                    }
                    AfterEdit(sel);
                }
                DrawSelectionLabel(sel);
            }
        }

        HashSet<string> TouchedStreetIds(EditPt sel)
        {
            var set = new HashSet<string>();
            if (sel == null) return set;
            switch ((PtKind)sel.kind)
            {
                case PtKind.Node:
                    foreach (var st in ((JArray)doc["streets"]).Cast<JObject>())
                        if ((string)st["from"] == sel.owner || (string)st["to"] == sel.owner) set.Add((string)st["id"]);
                    break;
                case PtKind.StreetVia: set.Add(sel.owner); break;
            }
            return set;
        }

        void DrawPicker(EditPt p)
        {
            var w = WorldOf(p);
            float size = Mathf.Max(0.55f, HandleUtility.GetHandleSize(w) * 0.06f);
            float pick = HandleUtility.GetHandleSize(w) * 0.16f;
            var kind = (PtKind)p.kind;
            Handles.CapFunction cap;
            if (kind == PtKind.Node) cap = Handles.DotHandleCap;
            else if (kind == PtKind.Landmark) cap = Handles.SphereHandleCap;
            else if (kind == PtKind.PlazaDiscRadius) cap = Handles.CubeHandleCap;
            else cap = Handles.CircleHandleCap;
            Color c = kind switch
            {
                PtKind.Node => new Color(1f, 0.9f, 0.4f),
                PtKind.Landmark => new Color(0.9f, 0.5f, 1f),
                PtKind.River => new Color(0.4f, 0.7f, 1f),
                PtKind.PlazaDiscRadius => new Color(1f, 0.6f, 0.3f),
                _ => new Color(0.6f, 1f, 0.8f),
            };
            var prev = Handles.color;
            Handles.color = c;
            if (Handles.Button(w, Quaternion.identity, size, pick, cap))
                Select(p);
            Handles.color = prev;
        }

        void DrawSelectionLabel(EditPt sel)
        {
            var w = WorldOf(sel);
            var style = new GUIStyle(EditorStyles.boldLabel) { normal = { textColor = Color.white }, fontSize = 12 };
            Handles.Label(w + Vector3.up * 0.6f, $"▼ {sel.label}" + (sel.Changed ? "  *" : ""), style);
        }

        void DrawStreet(JObject st, bool highlight)
        {
            string role = (string)st["role"];
            var col = RoleColor.GetValueOrDefault(role, Color.gray);
            float width = st["width"] != null ? (float)st["width"] : (float)doc["roles"][role]["width"];
            var pts = StreetWorldPts(st);
            if (pts.Count < 2) return;

            var prev = Handles.color;
            var fill = col; fill.a = highlight ? 0.34f : 0.14f;
            Handles.color = fill;
            var (left, right) = OffsetStrip(pts, width / 2f);
            for (int i = 0; i + 1 < pts.Count; i++)
                Handles.DrawAAConvexPolygon(left[i], left[i + 1], right[i + 1], right[i]);
            Handles.color = col;
            Handles.DrawAAPolyLine(highlight ? 3.5f : 2f, pts.ToArray());

            if (streetLabels || highlight)
            {
                var style = new GUIStyle(EditorStyles.miniLabel) { normal = { textColor = col } };
                Handles.Label(pts[pts.Count / 2] + Vector3.up * 0.4f, $"{(string)st["id"]}  {width:0.#}m", style);
            }
            Handles.color = prev;
        }

        /// <summary>World polyline of a street: from node -> via points -> to node, heights interpolated by arc length
        /// where a via point carries no explicit height (the skeleton's rule).</summary>
        List<Vector3> StreetWorldPts(JObject st)
        {
            var list = new List<Vector3>();
            if (!nodeIndex.TryGetValue((string)st["from"], out var a) || !nodeIndex.TryGetValue((string)st["to"], out var b)) return list;
            var raw = new List<(float x, float z, float? h)> { (a.x, a.z, a.h) };
            if (st["via"] is JArray via)
                for (int i = 0; i < via.Count; i++)
                {
                    var v = (JArray)via[i];
                    raw.Add(((float)v[0], (float)v[1], v.Count >= 3 ? (float)v[2] : (float?)null));
                }
            raw.Add((b.x, b.z, b.h));

            // arc length parameter for the height interpolation
            var acc = new float[raw.Count];
            for (int i = 1; i < raw.Count; i++)
                acc[i] = acc[i - 1] + Vector2.Distance(new Vector2(raw[i - 1].x, raw[i - 1].z), new Vector2(raw[i].x, raw[i].z));
            float ox = (float)doc["unityOffset"][0], oy = (float)doc["unityOffset"][1];
            for (int i = 0; i < raw.Count; i++)
            {
                float h = raw[i].h ?? Mathf.Lerp(raw[0].h ?? 0f, raw[^1].h ?? 0f, acc[i] / Mathf.Max(acc[^1], 0.01f));
                list.Add(new Vector3(raw[i].x + ox, h, raw[i].z + oy));
            }
            return list;
        }

        static (Vector3[] left, Vector3[] right) OffsetStrip(List<Vector3> pts, float half)
        {
            var left = new Vector3[pts.Count];
            var right = new Vector3[pts.Count];
            for (int i = 0; i < pts.Count; i++)
            {
                var a = pts[Mathf.Max(i - 1, 0)];
                var b = pts[Mathf.Min(i + 1, pts.Count - 1)];
                var d = (b - a); d.y = 0;
                if (d.sqrMagnitude < 1e-6f) d = Vector3.forward;
                var n = new Vector3(-d.z, 0f, d.x).normalized * half;
                left[i] = pts[i] + n;
                right[i] = pts[i] - n;
            }
            return (left, right);
        }

        void DrawPlaza(JObject pz, bool highlight)
        {
            float ox = (float)doc["unityOffset"][0], oy = (float)doc["unityOffset"][1];
            float y = pz["y"] != null ? (float)pz["y"] : 0.3f;
            var prev = Handles.color;
            var col = highlight ? new Color(1f, 0.85f, 0.35f) : new Color(1f, 0.85f, 0.35f);
            if (pz["poly"] is JArray poly)
            {
                var pts = poly.Select(q => new Vector3((float)q[0] + ox, y, (float)q[1] + oy)).ToArray();
                Handles.color = col;
                var closed = pts.Concat(new[] { pts[0] }).ToArray();
                Handles.DrawAAPolyLine(highlight ? 3.5f : 2f, closed);
                if (IsConvex(poly) || highlight)
                {
                    var fill = col; fill.a = highlight ? 0.2f : 0.09f;
                    Handles.color = fill;
                    Handles.DrawAAConvexPolygon(pts);
                }
                var style = new GUIStyle(EditorStyles.miniLabel) { normal = { textColor = col } };
                Handles.Label(Avg(pts) + Vector3.up * 0.3f, (string)pz["id"], style);
            }
            else if (pz["disc"] is JArray disc)
            {
                var c = new Vector3((float)disc[0] + ox, y, (float)disc[1] + oy);
                float r = (float)disc[2];
                Handles.color = col;
                Handles.DrawWireDisc(c, Vector3.up, r);
                Handles.DrawAAPolyLine(2f, c, c + Vector3.right * r);
                var style = new GUIStyle(EditorStyles.miniLabel) { normal = { textColor = col } };
                Handles.Label(c + new Vector3(0, 0.3f, -r - 0.6f), (string)pz["id"], style);
            }
            Handles.color = prev;
        }

        static bool IsConvex(JArray poly)
        {
            int n = poly.Count;
            if (n < 4) return true;
            bool? sign = null;
            for (int i = 0; i < n; i++)
            {
                var a = poly[i]; var b = poly[(i + 1) % n]; var c = poly[(i + 2) % n];
                float cross = ((float)b[0] - (float)a[0]) * ((float)c[1] - (float)b[1]) - ((float)b[1] - (float)a[1]) * ((float)c[0] - (float)b[0]);
                if (Mathf.Abs(cross) < 1e-6f) continue;
                if (sign == null) sign = cross > 0;
                else if (sign != cross > 0) return false;
            }
            return true;
        }

        static Vector3 Avg(Vector3[] pts)
        {
            var acc = Vector3.zero;
            foreach (var p in pts) acc += p;
            return acc / pts.Length;
        }

        void DrawLandmarks()
        {
            float ox = (float)doc["unityOffset"][0], oy = (float)doc["unityOffset"][1];
            var prev = Handles.color;
            var col = new Color(0.9f, 0.5f, 1f);
            Handles.color = col;
            foreach (var lm in ((JArray)doc["landmarks"]).Cast<JObject>())
            {
                var at = (JArray)lm["at"];
                var c = new Vector3((float)at[0] + ox, 1.2f, (float)at[1] + oy);
                float s = HandleUtility.GetHandleSize(c) * 0.22f;
                Handles.DrawAAPolyLine(2.5f, c + new Vector3(-s, 0, -s), c + new Vector3(s, 0, s));
                Handles.DrawAAPolyLine(2.5f, c + new Vector3(-s, 0, s), c + new Vector3(s, 0, -s));
                Handles.DrawAAPolyLine(2f, c + new Vector3(0, 0, -s * 1.6f), c + new Vector3(0, 0, s * 1.6f));
                Handles.DrawAAPolyLine(2f, c + new Vector3(-s * 1.6f, 0, 0), c + new Vector3(s * 1.6f, 0, 0));
                var style = new GUIStyle(EditorStyles.miniLabel) { normal = { textColor = col } };
                Handles.Label(c + Vector3.up * 0.5f, $"◆ {(string)lm["id"]}", style);
            }
            Handles.color = prev;
        }

        void DrawRiver()
        {
            var rv = doc["river"] as JObject;
            if (rv?["pts"] is not JArray pts) return;
            float ox = (float)doc["unityOffset"][0], oy = (float)doc["unityOffset"][1];
            float water = (float)rv["water"];
            float width = (float)rv["width"];
            var centre = pts.Select(q => new Vector3((float)q[0] + ox, water + 0.05f, (float)q[1] + oy)).ToList();
            var prev = Handles.color;
            var col = new Color(0.35f, 0.65f, 1f);
            var (left, right) = OffsetStrip(centre, width / 2f);
            var fill = col; fill.a = 0.16f;
            Handles.color = fill;
            for (int i = 0; i + 1 < centre.Count; i++)
                Handles.DrawAAConvexPolygon(left[i], left[i + 1], right[i + 1], right[i]);
            Handles.color = col;
            Handles.DrawAAPolyLine(2.5f, centre.ToArray());
            var style = new GUIStyle(EditorStyles.miniLabel) { normal = { textColor = col } };
            Handles.Label(centre[centre.Count / 2] + Vector3.up * 0.3f, (string)rv["name"] ?? "río", style);
            Handles.color = prev;
        }

        // ---------------------------------------------------------------- test hooks (operator/MCP)

        /// <summary>Selects a point by label substring (operator hook; used by MCP smoke tests).</summary>
        public bool DebugSelect(string label)
        {
            var p = state.pts.FirstOrDefault(q => q.label.IndexOf(label, System.StringComparison.OrdinalIgnoreCase) >= 0);
            if (p == null) return false;
            Select(p);
            return true;
        }

        /// <summary>Moves the selection through the exact same code path as the PositionHandle (operator hook).</summary>
        public string DebugMove(float dx, float dz, float? dy = null)
        {
            var p = SelectedPt;
            if (p == null) return "no selection";
            Undo.RecordObject(state, "Move " + p.label);
            p.x += dx; p.z += dz;
            if (dy.HasValue && ((PtKind)p.kind == PtKind.Node || (PtKind)p.kind == PtKind.StreetVia)) p.h += dy.Value;
            if ((PtKind)p.kind == PtKind.PlazaDiscRadius) p.radius = Mathf.Max(0.5f, p.radius + dx);
            AfterEdit(p);
            return p.DiffLine();
        }

        /// <summary>Saves without the confirmation dialog (operator/MCP runs; the dialog stays for the manual button).</summary>
        public string DebugSave()
        {
            var changed = ChangedList();
            if (changed.Count == 0) return "nothing to save";
            if (File.Exists(tracePath))
                File.Copy(tracePath, tracePath + ".bak", true);
            File.WriteAllText(tracePath, doc.ToString(Formatting.Indented), new UTF8Encoding(false));
            loadedText = File.ReadAllText(tracePath);
            pristine = (JObject)doc.DeepClone();
            foreach (var p in state.pts) p.TakeBaseline();
            AssetDatabase.ImportAsset(tracePath);
            Debug.Log($"JD_LAYOUT_TRACE saved {changed.Count} element(s) -> {tracePath} (.bak kept)");
            return "saved " + changed.Count + ": " + string.Join(" | ", changed);
        }

        public int DebugPointCount => state != null ? state.pts.Count : -1;

        /// <summary>Same reload path as REVERT without its dialog (operator/MCP runs).</summary>
        public void DebugRevert() => LoadTrace();

        public string DebugSelectionInfo()
        {
            var p = SelectedPt;
            return p == null ? "no selection" : $"{p.label} ({p.x:0.###}, {p.z:0.###}, {p.h:0.###})";
        }
    }

    // -------------------------------------------------------------------- mirror + document model

    public enum PtKind { Node, StreetVia, PlazaVertex, PlazaDisc, PlazaDiscRadius, Landmark, River }

    /// <summary>One draggable point of the trace, in trace coordinates (x east, z north, h up metres). The baseline
    /// fields remember the loaded/saved value so the changed-element list is exact.</summary>
    [System.Serializable]
    public class EditPt
    {
        public int kind;
        public string owner;
        public int index;
        public string label;
        public float x, z, h;
        public float radius;
        public bool hasH;
        public float bx, bz, bh, bradius;      // baseline (as loaded / as saved)
        public bool bHasH;

        public bool Changed => !Mathf.Approximately(x, bx) || !Mathf.Approximately(z, bz) || !Mathf.Approximately(h, bh)
            || !Mathf.Approximately(radius, bradius) || hasH != bHasH;

        public string DiffLine() =>
            $"{label}: ({bx:0.##}, {bz:0.##}{(bHasH ? $", {bh:0.##}" : "")}) -> ({x:0.##}, {z:0.##}{(hasH ? $", {h:0.##}" : "")}){(Mathf.Approximately(radius, bradius) ? "" : $" r={bradius:0.##}->{radius:0.##}")}";

        public void TakeBaseline()
        {
            bx = x; bz = z; bh = h; bradius = radius; bHasH = hasH;
        }
    }

    /// <summary>Hidden ScriptableObject holding the editable points so Unity Undo records real, revertible states.
    /// The trace JObject is re-derived from this mirror on every edit and on every undo/redo; only the known
    /// coordinate paths are written, so unknown JSON fields survive untouched.</summary>
    public class TraceEditState : ScriptableObject
    {
        public List<EditPt> pts = new List<EditPt>();

        public static TraceEditState FromDoc(JObject doc)
        {
            var st = CreateInstance<TraceEditState>();
            st.hideFlags = HideFlags.HideAndDontSave;

            foreach (var kv in (JObject)doc["nodes"])
            {
                var a = (JArray)kv.Value;
                st.pts.Add(new EditPt { kind = (int)PtKind.Node, owner = kv.Key, index = 0, label = kv.Key,
                    x = (float)a[0], z = (float)a[1], h = a.Count >= 3 ? (float)a[2] : 0f, hasH = true });
            }
            foreach (var s in ((JArray)doc["streets"]).Cast<JObject>())
                if (s["via"] is JArray via)
                    for (int i = 0; i < via.Count; i++)
                    {
                        var v = (JArray)via[i];
                        st.pts.Add(new EditPt { kind = (int)PtKind.StreetVia, owner = (string)s["id"], index = i,
                            label = $"{(string)s["id"]} · vía {i + 1}",
                            x = (float)v[0], z = (float)v[1], h = v.Count >= 3 ? (float)v[2] : 0f, hasH = v.Count >= 3 });
                    }
            foreach (var pz in ((JArray)doc["plazas"]).Cast<JObject>())
            {
                if (pz["poly"] is JArray poly)
                    for (int i = 0; i < poly.Count; i++)
                    {
                        var v = (JArray)poly[i];
                        st.pts.Add(new EditPt { kind = (int)PtKind.PlazaVertex, owner = (string)pz["id"], index = i,
                            label = $"{(string)pz["id"]} · vértice {i + 1}", x = (float)v[0], z = (float)v[1] });
                    }
                if (pz["disc"] is JArray disc)
                {
                    st.pts.Add(new EditPt { kind = (int)PtKind.PlazaDisc, owner = (string)pz["id"], index = 0,
                        label = $"{(string)pz["id"]} · centro", x = (float)disc[0], z = (float)disc[1] });
                    st.pts.Add(new EditPt { kind = (int)PtKind.PlazaDiscRadius, owner = (string)pz["id"], index = 0,
                        label = $"{(string)pz["id"]} · radio", x = (float)disc[0] + (float)disc[2], z = (float)disc[1], radius = (float)disc[2] });
                }
            }
            foreach (var lm in ((JArray)doc["landmarks"]).Cast<JObject>())
            {
                var at = (JArray)lm["at"];
                st.pts.Add(new EditPt { kind = (int)PtKind.Landmark, owner = (string)lm["id"], index = 0,
                    label = $"landmark {(string)lm["id"]}", x = (float)at[0], z = (float)at[1] });
            }
            if (doc["river"]?["pts"] is JArray river)
                for (int i = 0; i < river.Count; i++)
                {
                    var v = (JArray)river[i];
                    st.pts.Add(new EditPt { kind = (int)PtKind.River, owner = "river", index = i,
                        label = $"río · punto {i + 1}", x = (float)v[0], z = (float)v[1] });
                }

            foreach (var p in st.pts) p.TakeBaseline();
            return st;
        }

        /// <summary>Writes every point back into its known path of the document (in place; unknown fields untouched).</summary>
        public void ApplyToDoc(JObject doc)
        {
            foreach (var p in pts)
            {
                switch ((PtKind)p.kind)
                {
                    case PtKind.Node:
                        if (doc["nodes"][p.owner] is JArray n) { n[0] = p.x; n[1] = p.z; n[2] = p.h; }
                        break;
                    case PtKind.StreetVia:
                        foreach (var s in ((JArray)doc["streets"]).Cast<JObject>())
                            if ((string)s["id"] == p.owner && s["via"] is JArray via && p.index < via.Count)
                            {
                                var v = (JArray)via[p.index];
                                v[0] = p.x; v[1] = p.z;
                                if (p.hasH) { if (v.Count < 3) v.Add(p.h); else v[2] = p.h; }
                                else while (v.Count > 2) v.RemoveAt(v.Count - 1);
                            }
                        break;
                    case PtKind.PlazaVertex:
                        foreach (var pz in ((JArray)doc["plazas"]).Cast<JObject>())
                            if ((string)pz["id"] == p.owner && pz["poly"] is JArray poly && p.index < poly.Count)
                            {
                                var v = (JArray)poly[p.index];
                                v[0] = p.x; v[1] = p.z;
                            }
                        break;
                    case PtKind.PlazaDisc:
                    case PtKind.PlazaDiscRadius:
                        foreach (var pz in ((JArray)doc["plazas"]).Cast<JObject>())
                            if ((string)pz["id"] == p.owner && pz["disc"] is JArray disc)
                            {
                                if ((PtKind)p.kind == PtKind.PlazaDisc) { disc[0] = p.x; disc[1] = p.z; }
                                else disc[2] = p.radius;
                            }
                        break;
                    case PtKind.Landmark:
                        foreach (var lm in ((JArray)doc["landmarks"]).Cast<JObject>())
                            if ((string)lm["id"] == p.owner && lm["at"] is JArray at)
                            { at[0] = p.x; at[1] = p.z; }
                        break;
                    case PtKind.River:
                        if (doc["river"]?["pts"] is JArray river && p.index < river.Count)
                        {
                            var v = (JArray)river[p.index];
                            v[0] = p.x; v[1] = p.z;
                        }
                        break;
                }
            }
        }
    }

    // -------------------------------------------------------------------- rebuild pipeline

    /// <summary>Frame-driven runner for REBUILD: regenerates the district spec with the existing skeleton tool, diffs
    /// it against the current one, and either rebuilds just the affected rows (only when the diff proves that safe) or
    /// the whole district through EnvDistrict.Begin/BuildRows/Finish, chunked so the Editor never locks up.
    /// The promote of the regenerated spec is transactional: every consent/environment precondition runs BEFORE the
    /// spec authority is touched, the previous spec AND the saved district scene are snapshotted outside Assets, and
    /// any cancel, exception or domain reload after the promote rolls both authorities back — spec and scene can never
    /// be left disagreeing at any exit of the operation.</summary>
    [UnityEditor.InitializeOnLoad]
    public static class LayoutRebuild
    {
        public enum Phase { None, Regen, Confirm, Rows, BeginPhase, RowsChunk, FinishPhase, Done, Failed }

        /// <summary>Operator/MCP evidence hook: injects a failure at this point of the next rebuild (after the spec was
        /// promoted) to prove the transaction rolls spec and scene back. Resets itself after firing.</summary>
        public enum DebugFailPoint { None, AfterPromote, MidChunk, MidRows }
        public static DebugFailPoint DebugFailAt = DebugFailPoint.None;

        public static Phase phase = Phase.None;
        public static string status = "";
        public static float progress;
        public static readonly List<string> log = new List<string>();
        /// <summary>Operator/MCP runs set this to skip the impact confirmation dialog (the summary is still logged).</summary>
        public static bool AutoConfirm = false;

        // EditorPrefs registry of the open promote transaction: unlike the statics below it survives domain reloads
        // (script compile, Play) and editor restarts, so an interrupted rebuild can always be rolled back on next load.
        const string TxKey = "JuegoDef.ENV.Layout.RebuildTx";
        static bool txOpen;                // spec promoted, transaction not yet committed/rolled back

        static LayoutRebuild()
        {
            EditorApplication.update += RecoverInterruptedTick;
        }

        static string districtId, projectRoot, repoRoot, traceAbs, specAbs, candidatePath;
        static Process proc;
        static readonly StringBuilder stdout = new StringBuilder(), stderr = new StringBuilder();
        static JObject currentSpec, candidateSpec;
        static SpecDiff diff;
        static string[] affectedRows = new string[0];
        static int rowCursor, chunkCursor;
        static double startedAt;

        public static void Start(string id, string dataPath)
        {
            if (phase != Phase.None) return;
            districtId = id;
            projectRoot = Path.GetFullPath(Path.Combine(dataPath, ".."));
            repoRoot = Path.GetFullPath(Path.Combine(projectRoot, "..", ".."));
            traceAbs = Path.Combine(projectRoot, EnvDistrict.DistrictSpecs.Replace('/', Path.DirectorySeparatorChar), id + ".trace.json");
            specAbs = Path.Combine(projectRoot, EnvDistrict.DistrictSpecs.Replace('/', Path.DirectorySeparatorChar), id + ".json");
            var osm = EditorPrefs.GetString($"JuegoDef.ENV.Layout.{id}.OsmPath", "");
            if (osm == "" || !File.Exists(osm))
            {
                phase = Phase.Failed;
                Status("falta el extracto OSM — elígeló con «elegir...» en la ventana");
                return;
            }
            candidatePath = Path.Combine(System.Environment.GetFolderPath(System.Environment.SpecialFolder.LocalApplicationData),
                "JuegoDef", id + "_spec_candidate.json");
            Directory.CreateDirectory(Path.GetDirectoryName(candidatePath));
            log.Clear();
            Status($"regenerando spec: python Tools/env_district_skeleton.py --trace {id}.trace.json");
            phase = Phase.Regen;
            progress = 0.02f;
            startedAt = EditorApplication.timeSinceStartup;

            var psi = new ProcessStartInfo
            {
                FileName = "python",
                WorkingDirectory = repoRoot,
                Arguments = $"Tools/env_district_skeleton.py --trace \"{traceAbs}\" --osm \"{osm}\" --out \"{candidatePath}\"",
                UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true, CreateNoWindow = true,
            };
            stdout.Clear(); stderr.Clear();
            proc = Process.Start(psi);
            proc.OutputDataReceived += (_, e) => { if (e.Data != null) lock (stdout) stdout.AppendLine(e.Data); };
            proc.ErrorDataReceived += (_, e) => { if (e.Data != null) lock (stderr) stderr.AppendLine(e.Data); };
            proc.BeginOutputReadLine();
            proc.BeginErrorReadLine();
            EditorApplication.update -= Tick;
            EditorApplication.update += Tick;
        }

        public static void Cancel(string why)
        {
            if (txOpen) { Rollback("cancelado: " + why); return; }
            if (proc is { HasExited: false }) { try { proc.Kill(); } catch { } }
            phase = Phase.None;
            Status("REBUILD cancelado: " + why);
            EditorApplication.update -= Tick;
        }

        // ---------------------------------------------------------------- transaction

        /// <summary>Every consent/environment precondition runs BEFORE the spec authority is touched: Play Mode for
        /// both routes, the AFFECTED route additionally needs the district scene open with its root present (it edits
        /// the open scene in place), and a dirty scene always needs an explicit continue because the rollback restores
        /// the scene from disk. A "no" here leaves every repository byte untouched.</summary>
        static bool TxGate(bool rowsOnly)
        {
            if (EditorApplication.isPlaying) { Cancel("no se reconstruye en Play Mode"); return false; }
            var scene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            if (rowsOnly && !scene.path.EndsWith($"{districtId}.unity"))
            { Cancel($"la ruta AFFECTED necesita abierta la escena {districtId}.unity (activa: {(scene.path == "" ? "(sin guardar)" : scene.path)})"); return false; }
            if (rowsOnly && GameObject.Find(districtId) == null)
            { Cancel($"la escena abierta no contiene el root {districtId} — abre la escena del distrito o fuerza la ruta DISTRICT"); return false; }
            if (scene.isDirty)
            {
                var body = rowsOnly
                    ? "El rebuild sustituye filas de la escena abierta; si el rebuild falla, la transacción recarga la escena desde disco y estos cambios sin guardar se pierden."
                    : "El rebuild abre una escena nueva y guarda el distrito; la escena abierta tiene cambios sin guardar y se descartarán.";
                if (!EditorUtility.DisplayDialog("Escena sin guardar",
                        body + "\n\nREBUILD es transaccional: si algo falla, spec y escena se restauran al estado anterior.", "Continuar", "Cancelar"))
                { Cancel("escena con cambios sin guardar"); return false; }
            }
            return true;
        }

        /// <summary>Opens the promote transaction: snapshots of the previous spec and of the saved district scene go to
        /// %LOCALAPPDATA%\JuegoDef (outside Assets, so nothing pollutes the project), then the EditorPrefs registry
        /// marks the transaction in flight. The caller promotes the spec only after this returns.</summary>
        static void TxOpen(bool rowsOnly)
        {
            var dir = Path.Combine(System.Environment.GetFolderPath(System.Environment.SpecialFolder.LocalApplicationData), "JuegoDef");
            Directory.CreateDirectory(dir);
            var specBak = Path.Combine(dir, districtId + "_spec.prev.json");
            var sceneBak = Path.Combine(dir, districtId + "_scene.prev.unity");
            var sceneAbs = Path.Combine(projectRoot, "Assets", "JuegoDef", "Scenes", "ENV", districtId + ".unity");
            File.Copy(specAbs, specBak, true);
            var hadScene = File.Exists(sceneAbs);
            if (hadScene) File.Copy(sceneAbs, sceneBak, true);
            EditorPrefs.SetString(TxKey + ".DistrictId", districtId);
            EditorPrefs.SetString(TxKey + ".SpecBak", specBak);
            EditorPrefs.SetString(TxKey + ".SceneBak", hadScene ? sceneBak : "");
            EditorPrefs.SetString(TxKey + ".PrevScene", UnityEngine.SceneManagement.SceneManager.GetActiveScene().path);
            EditorPrefs.SetInt(TxKey + ".Route", rowsOnly ? 0 : 1);
            EditorPrefs.SetBool(TxKey + ".Committed", false);
            EditorPrefs.SetBool(TxKey + ".InFlight", true);
            txOpen = true;
            Status($"TX abierta: snapshots de spec{(hadScene ? " y escena" : "")} previas en {dir} — rollback automático ante cualquier fallo");
        }

        /// <summary>Commits the transaction at a success exit: marks committed first (a crash from here on must never
        /// roll a finished rebuild back), drops the scene snapshot, keeps the spec snapshot for the operator.</summary>
        static void CommitTx()
        {
            if (!txOpen) return;
            txOpen = false;
            EditorPrefs.SetBool(TxKey + ".Committed", true);
            var sceneBak = EditorPrefs.GetString(TxKey + ".SceneBak", "");
            var specBak = EditorPrefs.GetString(TxKey + ".SpecBak", "");
            if (sceneBak != "") { try { if (File.Exists(sceneBak)) File.Delete(sceneBak); } catch { } }
            EditorPrefs.DeleteKey(TxKey + ".InFlight");
            Status($"TX commit: spec aplicada y escena guardada (snapshot de la spec anterior en {specBak})");
            ClearTxKeys();
        }

        /// <summary>Compensates an unfinished transaction: restores the previous spec bytes and the previous saved
        /// district scene, then reloads the right scene in the editor, so spec authority and scene can never disagree.
        /// All inputs come from the EditorPrefs registry, so this works identically after a domain reload or restart;
        /// if the compensation itself fails it says so loudly with the snapshot paths for a manual restore.</summary>
        static void Rollback(string why)
        {
            txOpen = false;
            if (proc is { HasExited: false }) { try { proc.Kill(); } catch { } }
            var id = EditorPrefs.GetString(TxKey + ".DistrictId", districtId);
            var specBak = EditorPrefs.GetString(TxKey + ".SpecBak", "");
            var sceneBak = EditorPrefs.GetString(TxKey + ".SceneBak", "");
            var prevScene = EditorPrefs.GetString(TxKey + ".PrevScene", "");
            bool rowsRoute = EditorPrefs.GetInt(TxKey + ".Route", 1) == 0;
            var proj = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            var specAbsR = Path.Combine(proj, EnvDistrict.DistrictSpecs.Replace('/', Path.DirectorySeparatorChar), id + ".json");
            var sceneRel = $"Assets/JuegoDef/Scenes/ENV/{id}.unity";
            var sceneAbsR = Path.Combine(proj, sceneRel.Replace('/', Path.DirectorySeparatorChar));
            var problems = new List<string>();
            try
            {
                if (specBak != "" && File.Exists(specBak)) { File.Copy(specBak, specAbsR, true); AssetDatabase.ImportAsset($"{EnvDistrict.DistrictSpecs}/{id}.json"); }
                else problems.Add($"snapshot de spec no encontrado: {specBak}");
            }
            catch (System.Exception ex) { problems.Add("restaurar spec: " + ex.Message); }
            try { if (sceneBak != "" && File.Exists(sceneBak)) File.Copy(sceneBak, sceneAbsR, true); }
            catch (System.Exception ex) { problems.Add("restaurar escena: " + ex.Message); }
            if (!EditorApplication.isPlaying)
            {
                try
                {
                    string open = null;   // AFFECTED returns to the district scene; DISTRICT prefers the scene it came from
                    if (rowsRoute && File.Exists(sceneAbsR)) open = sceneRel;
                    else if (prevScene != "" && File.Exists(Path.Combine(proj, prevScene.Replace('/', Path.DirectorySeparatorChar)))) open = prevScene;
                    else if (File.Exists(sceneAbsR)) open = sceneRel;
                    if (open != null) UnityEditor.SceneManagement.EditorSceneManager.OpenScene(open, UnityEditor.SceneManagement.OpenSceneMode.Single);
                    else UnityEditor.SceneManagement.EditorSceneManager.NewScene(UnityEditor.SceneManagement.NewSceneSetup.DefaultGameObjects, UnityEditor.SceneManagement.NewSceneMode.Single);
                }
                catch (System.Exception ex) { problems.Add("recargar escena: " + ex.Message); }
            }
            ClearTxKeys();
            if (problems.Count > 0)
                Status($"TX ROLLBACK INCOMPLETO ({why}). Restaurar a mano:\n  spec   {specAbsR}  <=  {specBak}\n  escena {sceneAbsR}  <=  {sceneBak}\n" + string.Join("\n", problems));
            else
                Status($"TX rollback ({why}): spec y escena quedan exactamente como antes del REBUILD");
            Finish(Phase.Failed);
        }

        static void ClearTxKeys()
        {
            EditorPrefs.DeleteKey(TxKey + ".InFlight");
            EditorPrefs.DeleteKey(TxKey + ".Committed");
            EditorPrefs.DeleteKey(TxKey + ".DistrictId");
            EditorPrefs.DeleteKey(TxKey + ".SpecBak");
            EditorPrefs.DeleteKey(TxKey + ".SceneBak");
            EditorPrefs.DeleteKey(TxKey + ".PrevScene");
            EditorPrefs.DeleteKey(TxKey + ".Route");
        }

        /// <summary>Runs on every domain reload (via [InitializeOnLoad]) and checks once per editor frame: a
        /// transaction left in flight (compile/Play entered mid-rebuild, editor crash) that never committed is rolled
        /// back on the first frame that can. Per-frame polling instead of a one-shot delayCall because the latter can
        /// fire while Play Mode is still tearing down, which would silently lose the recovery trigger.</summary>
        static void RecoverInterruptedTick()
        {
            if (!EditorPrefs.GetBool(TxKey + ".InFlight", false)) { EditorApplication.update -= RecoverInterruptedTick; return; }
            if (EditorPrefs.GetBool(TxKey + ".Committed", false)) { ClearTxKeys(); EditorApplication.update -= RecoverInterruptedTick; return; }
            if (EditorApplication.isPlaying || EditorApplication.isCompiling || EditorApplication.isUpdating) return;
            EditorApplication.update -= RecoverInterruptedTick;
            Rollback("rebuild interrumpido (domain reload / cierre del editor)");
        }

        static void Status(string s)
        {
            status = s;
            log.Add(s);
            Debug.Log("JD_LAYOUT_REBUILD " + s);
        }

        static void Tick()
        {
            try
            {
                switch (phase)
                {
                    case Phase.Regen:
                        progress = Mathf.Min(0.25f, 0.02f + (float)((EditorApplication.timeSinceStartup - startedAt) / 60.0));
                        if (proc == null || proc.HasExited)
                        {
                            if (proc == null || proc.ExitCode != 0)
                            {
                                Status($"FALLO regenerando spec (exit {proc?.ExitCode}):\n{stderr}");
                                Finish(Phase.Failed);
                            }
                            else OnRegenDone();
                        }
                        else if (EditorApplication.timeSinceStartup - startedAt > 240) Cancel("timeout del skeleton (>4 min)");
                        break;
                    case Phase.Confirm: break;   // waiting for the dialog answer (dialog opened on regen done)
                    case Phase.Rows:
                        if (rowCursor < affectedRows.Length)
                        {
                            var rid = affectedRows[rowCursor++];
                            EnvPolish.RebuildRow(rid);
                            if (DebugFailAt == DebugFailPoint.MidRows) { DebugFailAt = DebugFailPoint.None; throw new System.InvalidOperationException("JD_LAYOUT_DEBUG_FAIL MidRows"); }
                            progress = 0.2f + 0.7f * rowCursor / affectedRows.Length;
                            Status($"fila {rid} reconstruida ({rowCursor}/{affectedRows.Length})");
                        }
                        else
                        {
                            var root = GameObject.Find(districtId)?.transform;
                            Debug.Log(EnvPolish.FixBlockedOpenings(root));
                            Debug.Log(EnvPolish.SeatOnGround(root));
                            SaveSceneIfDistrict();
                            CommitTx();
                            Status($"JD_LAYOUT_REBUILD affected: {affectedRows.Length} fila(s) reconstruidas desde la spec nueva");
                            Finish(Phase.Done);
                        }
                        break;
                    case Phase.BeginPhase:
                        Debug.Log(EnvDistrict.Begin(districtId));
                        chunkCursor = 0;
                        phase = Phase.RowsChunk;
                        break;
                    case Phase.RowsChunk:
                    {
                        var rows = (JArray)currentSpec["rows"];
                        Debug.Log(EnvDistrict.BuildRows(chunkCursor, 8));
                        chunkCursor += 8;
                        if (DebugFailAt == DebugFailPoint.MidChunk) { DebugFailAt = DebugFailPoint.None; throw new System.InvalidOperationException("JD_LAYOUT_DEBUG_FAIL MidChunk"); }
                        progress = 0.3f + 0.6f * Mathf.Min(1f, (float)chunkCursor / rows.Count);
                        if (chunkCursor >= rows.Count) phase = Phase.FinishPhase;
                        break;
                    }
                    case Phase.FinishPhase:
                        Debug.Log(EnvDistrict.Finish());
                        progress = 1f;
                        CommitTx();
                        Status($"JD_LAYOUT_REBUILD district completo ({(int)(EditorApplication.timeSinceStartup - startedAt)} s)");
                        Finish(Phase.Done);
                        break;
                }
            }
            catch (System.Exception ex)
            {
                Debug.LogException(ex);
                if (txOpen) Rollback("FALLO: " + ex.Message);
                else { Status("FALLO: " + ex.Message + "\n" + ex.StackTrace); Finish(Phase.Failed); }
            }
        }

        /// <summary>Compares the regenerated spec with the current one and routes: affected rows only when nothing but
        /// some rows changed (same ids, ground/river/plazas/streets/route byte-identical, at most 6 rows); otherwise
        /// the whole district. The impact summary and every other precondition are confirmed in dialogs BEFORE the
        /// spec is applied; from the apply on, the operation is transactional (see TxOpen/Rollback).</summary>
        static void OnRegenDone()
        {
            candidateSpec = JObject.Parse(File.ReadAllText(candidatePath));
            currentSpec = File.Exists(specAbs) ? JObject.Parse(EnvKit.ReadText($"{EnvDistrict.DistrictSpecs}/{districtId}.json")) : new JObject();
            diff = SpecDiff.Compute(currentSpec, candidateSpec);
            progress = 0.3f;

            if (diff.Empty)
            {
                Status("la spec ya refleja el trace — nada que reconstruir");
                Finish(Phase.Done);
                return;
            }
            string route = diff.RowsOnly ? $"AFFECTED ({diff.rowIdsChanged.Count} fila(s))" : "DISTRICT COMPLETO (~30 s)";
            Status($"impacto: {diff.Summary()}\nruta: {route}");

            bool proceed = AutoConfirm;
            if (!proceed)
                proceed = EditorUtility.DisplayDialog("REBUILD — impacto de la regeneración",
                    $"El pipeline regeneró la spec desde el trace guardado.\n\n{diff.Summary()}\n\nRuta: {route}\n\n¿Aplicar la spec nueva y reconstruir?\n(transaccional: si algo falla, spec y escena se restauran)", "REBUILD", "Cancelar");
            if (!proceed)
            {
                Cancel("cancelado en el diálogo de impacto");
                return;
            }

            // Transaction gate: every precondition and consent runs BEFORE the spec authority is touched, so a "no"
            // leaves every byte as it was (the reviewer repro SAVE->REBUILD->accept->dirty->Cancel ends here, clean).
            if (!TxGate(diff.RowsOnly)) return;

            TxOpen(diff.RowsOnly);
            File.Copy(candidatePath, specAbs, true);
            AssetDatabase.ImportAsset($"{EnvDistrict.DistrictSpecs}/{districtId}.json");
            currentSpec = candidateSpec;
            if (DebugFailAt == DebugFailPoint.AfterPromote) { DebugFailAt = DebugFailPoint.None; throw new System.InvalidOperationException("JD_LAYOUT_DEBUG_FAIL AfterPromote"); }

            if (diff.RowsOnly)
            {
                affectedRows = diff.rowIdsChanged.ToArray();
                rowCursor = 0;
                phase = Phase.Rows;
            }
            else phase = Phase.BeginPhase;
        }

        static void SaveSceneIfDistrict()
        {
            var scene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            if (scene.path.EndsWith($"{districtId}.unity"))
                UnityEditor.SceneManagement.EditorSceneManager.SaveScene(scene);
        }

        static void Finish(Phase end)
        {
            phase = end == Phase.Done ? Phase.None : end;
            if (end == Phase.Done) phase = Phase.None;
            progress = end == Phase.Done ? 1f : 0f;
            EditorApplication.update -= Tick;
            SceneView.RepaintAll();
        }

        public class SpecDiff
        {
            public List<string> otherChanged = new List<string>();   // geometry collections other than rows
            public List<string> rowIdsChanged = new List<string>();
            public int rowsAssignOnly, rowsGeometry, rowsAdded, rowsRemoved;
            static readonly string[] AssignFields =
                { "palette", "seed", "ground", "upper", "solana", "surrounds", "gate", "escudo", "basement", "awning", "tall", "thin", "wall" };

            public bool Empty => otherChanged.Count == 0 && rowIdsChanged.Count == 0 && rowsAdded == 0 && rowsRemoved == 0;
            public bool RowsOnly => otherChanged.Count == 0 && rowsAdded == 0 && rowsRemoved == 0 && rowIdsChanged.Count > 0 && rowIdsChanged.Count <= 6;

            public string Summary()
            {
                var sb = new StringBuilder();
                sb.Append(otherChanged.Count > 0 ? "suelo/calles/plazas/río/etc.: CAMBIAN (" + string.Join(", ", otherChanged) + ")" : "suelo/calles/plazas/río/etc.: intactos");
                sb.Append($"\nfilas: {rowsGeometry} cambian geometría · {rowsAssignOnly} re-tiran asignación (paleta/seed...)");
                if (rowsAdded + rowsRemoved > 0) sb.Append($"\nfilas añadidas/eliminadas: +{rowsAdded}/-{rowsRemoved}");
                return sb.ToString();
            }

            public static SpecDiff Compute(JObject cur, JObject newSpec)
            {
                var d = new SpecDiff();
                foreach (var key in new[] { "streets", "plazas", "river", "bridges", "stairs", "riverStairs", "bridgeArches", "fountains", "garden", "route", "ground", "district" })
                {
                    var a = cur[key]; var b = newSpec[key];
                    if (a == null && b == null) continue;
                    if (JToken.DeepEquals(a, b)) continue;
                    if (key == "ground" && a is JObject ga && b is JObject gb)
                    {
                        var zones = ga.Properties().Select(p => p.Name).Union(gb.Properties().Select(p => p.Name))
                            .Where(z => !JToken.DeepEquals(ga[z], gb[z])).Select(z => "suelo:" + z).ToList();
                        d.otherChanged.AddRange(zones);
                    }
                    else if (a is JArray aa && b is JArray ab && aa.Count > 0 && aa[0] is JObject && ((JObject)aa[0])["id"] != null)
                        d.otherChanged.Add(key);
                    else
                        d.otherChanged.Add(key);
                }

                var ra = ((JArray?)cur["rows"])?.Cast<JObject>().ToDictionary(r => (string)r["id"]) ?? new Dictionary<string, JObject>();
                var rb = ((JArray?)newSpec["rows"])?.Cast<JObject>().ToDictionary(r => (string)r["id"]) ?? new Dictionary<string, JObject>();
                d.rowsAdded = rb.Keys.Except(ra.Keys).Count();
                d.rowsRemoved = ra.Keys.Except(rb.Keys).Count();
                foreach (var rid in ra.Keys.Intersect(rb.Keys))
                {
                    if (JToken.DeepEquals(ra[rid], rb[rid])) continue;
                    d.rowIdsChanged.Add(rid);
                    if (RowAssignOnly(ra[rid], rb[rid])) d.rowsAssignOnly++; else d.rowsGeometry++;
                }
                return d;
            }

            /// <summary>True when every changed field of the row is a stochastic assignment (palette/seed/finish picks
            /// re-rolled downstream of a geometry change), not geometry itself.</summary>
            static bool RowAssignOnly(JObject a, JObject b)
            {
                var names = a.Properties().Select(p => p.Name).Union(b.Properties().Select(p => p.Name));
                foreach (var name in names)
                {
                    if (JToken.DeepEquals(a[name], b[name])) continue;
                    if (name != "plots") { if (!AssignFields.Contains(name)) return false; continue; }
                    var pa = a["plots"] as JArray; var pb = b["plots"] as JArray;
                    if (pa == null || pb == null || pa.Count != pb.Count) return false;
                    for (int i = 0; i < pa.Count; i++)
                    {
                        var p1 = (JObject)pa[i]; var p2 = (JObject)pb[i];
                        var fields = p1.Properties().Select(q => q.Name).Union(p2.Properties().Select(q => q.Name));
                        foreach (var f in fields)
                            if (!JToken.DeepEquals(p1[f], p2[f]) && !AssignFields.Contains(f))
                                return false;
                    }
                }
                return true;
            }
        }
    }
}

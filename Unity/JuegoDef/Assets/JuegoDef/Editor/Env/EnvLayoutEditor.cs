using System;
using System.IO;
using System.Linq;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace JuegoDef.Env
{
    public class EnvLayoutEditor : EditorWindow
    {
        public static EnvLayoutEditor Active { get; private set; }
        public const string District = "ENV01_Casco_District";
        [SerializeField] TraceEditState state;
        [SerializeField] string loaded, selectedKey;
        JObject doc, spec;
        public JObject Doc => doc;
        public JObject Spec => spec;
        public EditPt[] Points { get; private set; } = Array.Empty<EditPt>();
        public EditPt Selected => Points.FirstOrDefault(p => p.Key == selectedKey);
        public bool Dirty => doc != null && !JToken.DeepEquals(JObject.Parse(loaded), doc);
        public bool CanEdit => doc != null && LayoutRebuild.phase == LayoutRebuild.Phase.None && !EnvRebuildTransaction.Pending && !EditorApplication.isPlayingOrWillChangePlaymode && !EditorApplication.isCompiling && !EditorApplication.isUpdating && !EditorUtility.scriptCompilationFailed;
        public bool Guides = true, Height;
        string message = "", error = "";
        bool advanced;
        Vector2 scroll;
        double refreshed;
        long specStamp;
        string SessionKey => "JuegoDef.Director.Preview." + LayoutReceipt.WorkspaceKey;

        [MenuItem("JuegoDef/ENV/Director")]
        [MenuItem("JuegoDef/ENV/Layout Editor")]
        public static void Open() => GetWindow<EnvLayoutEditor>("ENV Director");
        void OnEnable()
        {
            Active = this; minSize = new Vector2(300, 410);
            Undo.undoRedoPerformed += UndoChanged;
            SceneView.duringSceneGui += SceneGUI;
            EditorApplication.update += UpdateStatus;
            try
            {
                if (state && !string.IsNullOrEmpty(loaded)) Refresh();
                else
                {
                    var saved = SessionState.GetString(SessionKey, "");
                    if (saved != "") { var session = JObject.Parse(saved); loaded = (string)session["loaded"]; state = TraceEditState.FromDoc((JObject)session["preview"]); selectedKey = (string)session["selection"]; Refresh(); }
                    else Load();
                }
            }
            catch (Exception ex) { error = ex.Message; }
        }
        void OnDisable()
        {
            Persist(); Undo.undoRedoPerformed -= UndoChanged; SceneView.duringSceneGui -= SceneGUI; EditorApplication.update -= UpdateStatus;
            if (Active == this) Active = null;
        }
        void Persist()
        {
            if (doc != null) SessionState.SetString(SessionKey, new JObject { ["loaded"] = loaded, ["preview"] = doc, ["selection"] = selectedKey }.ToString(Formatting.None));
        }
        void UpdateStatus()
        {
            if (EditorApplication.timeSinceStartup - refreshed < .5) return;
            refreshed = EditorApplication.timeSinceStartup;
            if (doc != null && (LayoutRebuild.phase == LayoutRebuild.Phase.None || LayoutRebuild.phase == LayoutRebuild.Phase.Failed))
                try { if (File.GetLastWriteTimeUtc(LayoutDocument.SpecPath(District)).Ticks != specStamp) Refresh(); } catch (Exception ex) { error = ex.Message; }
            Repaint();
        }
        void UndoChanged() { try { Refresh(); message = "Undo/Redo aplicado al preview. SAVE conserva la decisión."; } catch (Exception ex) { error = ex.Message; } }
        public void Load()
        {
            loaded = File.ReadAllText(LayoutDocument.TracePath(District));
            var source = JObject.Parse(loaded); LayoutDocument.Validate(source);
            if (!state) state = TraceEditState.FromDoc(source); else state.json = source.ToString(Formatting.None);
            Refresh(); error = ""; message = "Distrito cargado";
        }
        void Refresh()
        {
            doc = JObject.Parse(state.json);
            error = "";
            try { LayoutDocument.Validate(doc); } catch (Exception ex) { error = ex.Message; }
            spec = JObject.Parse(File.ReadAllText(LayoutDocument.SpecPath(District)));
            specStamp = File.GetLastWriteTimeUtc(LayoutDocument.SpecPath(District)).Ticks;
            Points = LayoutDocument.Points(doc, spec).ToArray();
            var preview = LayoutPlacement.PreviewSpec(doc, spec);
            if (error == "") error = LayoutPlacement.Validate(preview);
            Persist(); Repaint(); SceneView.RepaintAll();
        }
        public void Select(EditPt p) { selectedKey = p?.Key; Repaint(); SceneView.RepaintAll(); }
        public void Edit(string label, Action<JObject> change)
        {
            if (!CanEdit) return;
            var next = (JObject)doc.DeepClone(); change(next);
            if (JToken.DeepEquals(doc, next)) return;
            Undo.RecordObject(state, label); state.json = next.ToString(Formatting.None); EditorUtility.SetDirty(state); Refresh();
        }
        public bool Save(bool confirm = true)
        {
            if (!CanEdit) return false;
            try
            {
                LayoutDocument.Validate(doc);
                var conflict = LayoutPlacement.Validate(LayoutPlacement.PreviewSpec(doc, spec));
                if (conflict != "") throw new InvalidDataException(conflict);
                var changes = LayoutDocument.Changes(JObject.Parse(loaded), doc);
                if (!Dirty) { message = "Sin cambios · SAVE no modifica la autoridad"; return true; }
                var summary = string.Join("\n", changes.Select(x => "• " + x));
                if (confirm && !EditorUtility.DisplayDialog("SAVE · decisiones del distrito", summary + "\n\nSe conservará una copia anterior. La escena quedará pendiente de REBUILD.", "GUARDAR", "Cancelar")) return false;
                LayoutDocument.Save(LayoutDocument.TracePath(District), loaded, doc);
                loaded = File.ReadAllText(LayoutDocument.TracePath(District)); AssetDatabase.ImportAsset(LayoutDocument.TracePath(District));
                LayoutReceipt.Invalidate(); message = "Guardado:\n" + summary; Persist(); return true;
            }
            catch (Exception ex) { error = ex.Message; return false; }
        }
        public void Revert(bool confirm = true)
        {
            if (!CanEdit) return;
            if (Dirty)
            {
                Edit("Revertir preview", d => { d.RemoveAll(); foreach (var p in JObject.Parse(loaded).Properties()) d[p.Name] = p.Value.DeepClone(); });
                message = "Preview descartado · se conserva lo guardado"; return;
            }
            var path = LayoutDocument.TracePath(District);
            if (!File.Exists(path + ".bak")) { message = "No hay un guardado anterior"; return; }
            try
            {
                var before = JObject.Parse(File.ReadAllText(path + ".bak")); LayoutDocument.Validate(before);
                if (confirm && !EditorUtility.DisplayDialog("REVERT · último guardado", "Recuperar el layout anterior guardado. Después será necesario REBUILD.\n\n" + string.Join("\n", LayoutDocument.Changes(doc, before)), "RECUPERAR", "Cancelar")) return;
                LayoutDocument.Save(path, loaded, before); loaded = File.ReadAllText(path);
                Undo.RecordObject(state, "Recuperar guardado anterior"); state.json = before.ToString(Formatting.None);
                AssetDatabase.ImportAsset(path); Refresh(); LayoutReceipt.Invalidate(); message = "Guardado anterior recuperado · REBUILD pendiente";
            }
            catch (Exception ex) { error = ex.Message; }
        }
        public void Rebuild()
        {
            if (!CanEdit || Dirty || error != "") return;
            LayoutRebuild.ForceFull = false; LayoutRebuild.Start(District, Application.dataPath);
        }
        public void PlayHere()
        {
            if (Selected == null || LayoutRebuild.phase != LayoutRebuild.Phase.None) return;
            if ((Dirty || !LayoutReceipt.Matches(District)) && !EditorUtility.DisplayDialog("PLAY HERE · preview pendiente", "Se probará la última escena reconstruida. Hay decisiones pendientes de REBUILD.", "PROBAR ESCENA", "Cancelar")) return;
            LayoutPlayHere.Start(District, Selected.world, Selected.yaw, true);
        }
        public void View(int slot, bool recall = true)
        {
            if (recall && LayoutBookmarks.Exists(District, slot)) { LayoutBookmarks.Recall(District, slot); return; }
            var sv = SceneView.lastActiveSceneView ?? GetWindow<SceneView>();
            var at = Selected?.world ?? new Vector3(100, 2, 140);
            sv.sceneViewState.showFog = slot == 2;
            if (slot == 0) sv.LookAt(new Vector3(100, 2, 140), Quaternion.Euler(90, 0, 0), 130, true);
            else if (slot == 1)
            {
                var bounds = new Bounds(at, Vector3.one * 10);
                foreach (var st in EnvDirectorScene.Affected(this)) foreach (var p in LayoutDocument.StreetPoints(doc, st)) bounds.Encapsulate(p);
                sv.LookAt(bounds.center, Quaternion.Euler(55, -25, 0), Mathf.Max(12, bounds.extents.magnitude), false);
            }
            else sv.LookAt(at + Vector3.up * 1.7f, Quaternion.Euler(12, Selected?.yaw ?? 0, 0), 5, false);
        }
        static string OwnerBuildStatus()
        {
            if (EnvRebuildTransaction.Pending && LayoutRebuild.phase==LayoutRebuild.Phase.Failed) return "Recuperación pendiente. Usa RECUPERAR ESTADO ANTERIOR antes de continuar.";
            switch(LayoutRebuild.phase)
            {
                case LayoutRebuild.Phase.Regen: return "Preparando el distrito con las decisiones guardadas…";
                case LayoutRebuild.Phase.Confirm: return "Confirma el impacto de los cambios.";
                case LayoutRebuild.Phase.BeginPhase: return "Preparando suelo y calles…";
                case LayoutRebuild.Phase.RowsChunk: return "Construyendo los edificios…";
                case LayoutRebuild.Phase.FinishPhase: return "Aplicando acabado y guardando la escena…";
            }
            var detail=LayoutRebuild.status;
            if(detail.Contains("ENV_AUTHORING_CONFLICT") || detail.Contains("ENV_AUTHORING_MISSING")) return "El cambio altera la identidad de parcelas existentes. Reduce el desplazamiento o REVERT; rediseñar esas parcelas requiere migrar sus autorías.";
            if(detail.Contains("OSM")) return "La fuente OSM falta o no coincide con la adoptada. Revisa Configuración avanzada.";
            if(detail.Contains("Input cambió") || detail.Contains("receta cambió")) return "Las decisiones cambiaron durante REBUILD. Revisa el estado guardado y repite.";
            if(detail.Contains("compilación")) return "Unity debe terminar una compilación correcta antes de reconstruir.";
            if(detail.Contains("cambios no registrados")) return "Hay correcciones del distrito sin registrar. Se han conservado; intégralas en los inputs de generación antes de REBUILD.";
            if(new[]{"solape","cauce","acceso","fuera del distrito"}.Any(detail.Contains)) return detail.Split('\n')[0].Replace("FALLO: ","");
            return "La reconstrucción se ha interrumpido. El estado anterior se conserva; puedes corregir el cambio o REVERT.";
        }
        void OnGUI()
        {
            using(var viewport = new EditorGUILayout.ScrollViewScope(scroll))
            {
            scroll = viewport.scrollPosition;
            EditorGUILayout.Space(8); EditorGUILayout.LabelField("ENV DIRECTOR", EditorStyles.boldLabel);
            EditorGUILayout.LabelField("CASCO · Layout", EditorStyles.miniLabel);
            EditorGUILayout.HelpBox("1  Selecciona en la escena\n2  Arrastra posición, anchura o giro\n3  SAVE → REBUILD → PLAY HERE", MessageType.None);
            if (doc == null) { EditorGUILayout.HelpBox(error, MessageType.Error); if (GUILayout.Button("CARGAR CASCO")) Load(); return; }
            EditorGUILayout.HelpBox(LayoutReceipt.State(District, Dirty), Dirty ? MessageType.Warning : MessageType.Info);
            DrawCompact();
            using (new EditorGUILayout.HorizontalScope())
            {
                Guides = GUILayout.Toggle(Guides, "Guías", "Button");
                Height = GUILayout.Toggle(Height, "Altura Y", "Button");
                if (GUILayout.Button("Undo")) Undo.PerformUndo(); if (GUILayout.Button("Redo")) Undo.PerformRedo();
            }
            EditorGUILayout.Space(7);
            EditorGUILayout.LabelField(Selected?.label ?? "Selecciona una calle, punto, plaza o hito", EditorStyles.boldLabel);
            EditorGUILayout.LabelField(Selected?.kind == PtKind.Street ? "Toda la calle y sus controles están resaltados." : "Arrastra el control. Altura Y usa el eje vertical.", EditorStyles.wordWrappedMiniLabel);
            using (new EditorGUILayout.HorizontalScope())
            { if (GUILayout.Button("Planta")) View(0); if (GUILayout.Button("Encuadrar")) View(1); if (GUILayout.Button("A pie")) View(2); }
            using (new EditorGUILayout.HorizontalScope())
            { for (int i = 0; i < 3; ++i) { int slot = i; if (GUILayout.Button("Guardar vista " + (i + 1), EditorStyles.miniButton)) LayoutBookmarks.Save(District, slot); } }
            if (error != "") EditorGUILayout.HelpBox(error, MessageType.Error);
            if (message != "") EditorGUILayout.HelpBox(message, MessageType.None);
            if (LayoutPlayHere.Message != "") EditorGUILayout.LabelField(LayoutPlayHere.Message, EditorStyles.wordWrappedMiniLabel);
            if (LayoutRebuild.phase != LayoutRebuild.Phase.None)
            {
                EditorGUI.ProgressBar(GUILayoutUtility.GetRect(1, 22), LayoutRebuild.progress, LayoutRebuild.phase.ToString());
                EditorGUILayout.HelpBox(OwnerBuildStatus(), LayoutRebuild.phase == LayoutRebuild.Phase.Failed ? MessageType.Error : MessageType.Info);
                if (EnvRebuildTransaction.Pending && GUILayout.Button("RECUPERAR ESTADO ANTERIOR")) LayoutRebuild.RetryRecovery();
                else if (GUILayout.Button(LayoutRebuild.phase == LayoutRebuild.Phase.Failed ? "VOLVER A EDITAR" : "CANCELAR REBUILD")) LayoutRebuild.Cancel("solicitado por el usuario");
            }
            advanced = EditorGUILayout.Foldout(advanced, "Configuración avanzada", true);
            if (advanced) Advanced();
            }
        }
        public void DrawCompact()
        {
            using (new EditorGUILayout.HorizontalScope())
            {
                using (new EditorGUI.DisabledScope(!CanEdit || !Dirty || error != "")) if (GUILayout.Button("SAVE", GUILayout.Height(28))) Save();
                using (new EditorGUI.DisabledScope(!CanEdit)) if (GUILayout.Button("REVERT", GUILayout.Height(28))) Revert();
                using (new EditorGUI.DisabledScope(!CanEdit || Dirty || error != "")) if (GUILayout.Button("REBUILD", GUILayout.Height(28))) Rebuild();
            }
            using (new EditorGUI.DisabledScope(Selected == null || LayoutRebuild.phase != LayoutRebuild.Phase.None)) if (GUILayout.Button("PLAY HERE · selección", GUILayout.Height(26))) PlayHere();
        }
        void Advanced()
        {
            var key = $"JuegoDef.ENV.Layout.{District}.OsmPath"; var path = EditorPrefs.GetString(key, "");
            EditorGUILayout.LabelField("Fuente OSM", EditorStyles.miniLabel);
            if(LayoutRebuild.phase==LayoutRebuild.Phase.Failed) EditorGUILayout.HelpBox(LayoutRebuild.status,MessageType.None);
            if (GUILayout.Button("Elegir extracto…")) { var p = EditorUtility.OpenFilePanel("Extracto OSM", "", "json"); if (p != "") EditorPrefs.SetString(key, p); }
            EditorGUILayout.LabelField(path, EditorStyles.wordWrappedMiniLabel);
            using (new EditorGUI.DisabledScope(!CanEdit || !File.Exists(path)))
                if (GUILayout.Button("Adoptar fuente OSM"))
                {
                    string sha = OsmPin.Sha256File(path);
                    if (EditorUtility.DisplayDialog("Cambio deliberado de fuente", "La adopción cambia un input de generación. Las correcciones aceptadas seguirán siendo inputs explícitos.\n\n" + OsmPin.Short(OsmPin.PinnedSha(District)) + " → " + OsmPin.Short(sha), "ADOPTAR", "Cancelar")) { OsmPin.Adopt(District, path); LayoutReceipt.Invalidate(); }
                }
            if (GUILayout.Button("Recargar layout guardado")) { if (!Dirty || EditorUtility.DisplayDialog("Recargar", "Descartar los cambios del preview y leer el layout guardado.", "RECARGAR", "Cancelar")) Load(); }
            using (new EditorGUI.DisabledScope(!CanEdit || Dirty)) if (GUILayout.Button("Reconstruir distrito completo")) { LayoutRebuild.ForceFull = true; LayoutRebuild.Start(District, Application.dataPath); }
        }
        void SceneGUI(SceneView view) { if (Guides && doc != null) EnvDirectorScene.Draw(this, view); }
    }
}

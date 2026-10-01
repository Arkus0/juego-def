using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.Overlays;
using UnityEngine;
using UnityEngine.UIElements;

namespace JuegoDef.Env
{
    public static class EnvDirectorScene
    {
        static readonly Color Cyan = new Color(.24f, .8f, 1);
        static readonly Color Gold = new Color(1, .75f, .22f);
        static int dragGroup = -1;
        public static IEnumerable<JObject> Affected(EnvLayoutEditor window)
        {
            var p = window.Selected;
            return ((JArray)window.Doc["streets"]).OfType<JObject>().Where(s => p != null &&
                (p.kind == PtKind.Node ? (string)s["from"] == p.owner || (string)s["to"] == p.owner :
                 (p.kind == PtKind.Street || p.kind == PtKind.StreetVia) && (string)s["id"] == p.owner));
        }
        static bool Controller(EditPt p, IEnumerable<JObject> streets) => streets.Any(s =>
            p.kind == PtKind.Node && ((string)s["from"] == p.owner || (string)s["to"] == p.owner) || p.kind == PtKind.StreetVia && (string)s["id"] == p.owner);
        static Vector3[] Closed(IEnumerable<Vector3> pts) { var a = pts.ToList(); if (a.Count > 0) a.Add(a[0]); return a.ToArray(); }
        public static void Draw(EnvLayoutEditor w, SceneView view)
        {
            var previous = Handles.zTest; Handles.zTest = UnityEngine.Rendering.CompareFunction.Always;
            var affected = Affected(w).ToList();
            var selected = w.Selected;
            if (Event.current.type == EventType.MouseDown && Event.current.button == 0) { Undo.IncrementCurrentGroup(); dragGroup = Undo.GetCurrentGroup(); Undo.SetCurrentGroupName("Editar layout"); }
            foreach (var st in ((JArray)w.Doc["streets"]).OfType<JObject>())
            {
                var pts = LayoutDocument.StreetPoints(w.Doc, st); bool active = affected.Contains(st);
                float width = LayoutDocument.Width(w.Doc, st);
                for (int i = 1; i < pts.Count; ++i)
                {
                    var side = Vector3.Cross((pts[i] - pts[i - 1]).normalized, Vector3.up).normalized * width / 2;
                    var quad = new[] { pts[i - 1] - side, pts[i - 1] + side, pts[i] + side, pts[i] - side };
                    Handles.DrawSolidRectangleWithOutline(quad, active ? new Color(1, .75f, .2f, .16f) : new Color(.2f, .65f, .95f, .035f), active ? Gold : new Color(.25f, .75f, .9f, .35f));
                    Handles.color = active ? Gold : Cyan * new Color(1, 1, 1, .6f);
                    Handles.DrawAAPolyLine(active ? 5 : 2, pts[i - 1], pts[i]);
                    int control = GUIUtility.GetControlID(FocusType.Passive);
                    if (Event.current.type == EventType.Layout) HandleUtility.AddControl(control, HandleUtility.DistanceToLine(pts[i - 1], pts[i]));
                    if (Event.current.type == EventType.MouseDown && Event.current.button == 0 && !Event.current.alt && HandleUtility.nearestControl == control)
                    { w.Select(w.Points.First(p => p.kind == PtKind.Street && p.owner == (string)st["id"])); Event.current.Use(); }
                }
                if (active) Handles.Label((pts.First() + pts.Last()) / 2 + Vector3.up * .5f, $"{st["id"]} · {width:0.0} m", EditorStyles.whiteLargeLabel);
            }
            var off = LayoutDocument.Offset(w.Doc);
            foreach (var plaza in ((JArray)w.Doc["plazas"]).OfType<JObject>())
            {
                Handles.color = new Color(.4f, 1, .62f, .8f);
                float y = (float?)plaza["y"] ?? 0;
                if (plaza["poly"] is JArray polygon) Handles.DrawAAPolyLine(3, Closed(polygon.Select(a => new Vector3((float)a[0], y, (float)a[1]) + off)));
                if (plaza["disc"] is JArray disc) Handles.DrawWireDisc(new Vector3((float)disc[0], y, (float)disc[1]) + off, Vector3.up, (float)disc[2]);
            }
            if (w.Doc["river"]?["pts"] is JArray river)
            {
                Handles.color = new Color(.35f, .5f, 1, .7f);
                Handles.DrawAAPolyLine(4, river.Select(a => new Vector3((float)a[0], (float?)w.Doc["river"]["water"] ?? 0, (float)a[1]) + off).ToArray());
            }
            foreach (var p in w.Points.Where(p => p.kind != PtKind.Street))
            {
                bool current = p.Key == selected?.Key, controller = Controller(p, affected);
                if (!current && !controller && p.kind == PtKind.StreetVia && affected.Count > 0) continue;
                Handles.color = current || controller ? Gold : p.kind == PtKind.Landmark ? new Color(1, .5f, .75f) : p.kind.ToString().StartsWith("Plaza") ? new Color(.4f, 1, .62f) : Cyan;
                float size = HandleUtility.GetHandleSize(p.world) * (controller ? .065f : .045f);
                if (current) { if (Event.current.type == EventType.Repaint) Handles.DotHandleCap(0,p.world,Quaternion.identity,size,EventType.Repaint); }
                else if (Handles.Button(p.world, Quaternion.identity, size, size * 1.3f, p.kind == PtKind.Landmark ? Handles.CubeHandleCap : Handles.DotHandleCap)) w.Select(p);
                var screen = HandleUtility.WorldToGUIPoint(p.world);
                if (screen.x < 0 || screen.x > view.position.width || screen.y < 0 || screen.y > view.position.height) continue;
                if (current || controller || view.size < 45 || p.kind == PtKind.Landmark) Handles.Label(p.world + Vector3.up * size * 1.8f, p.label, current ? EditorStyles.whiteLargeLabel : EditorStyles.miniLabel);
            }
            if (selected != null)
            {
                if (w.CanEdit)
                {
                    if (selected.kind == PtKind.Street) Width(w, selected);
                    else if (selected.kind == PtKind.Landmark) Landmark(w, selected);
                    else Move(w, selected);
                }
                var conflict = LayoutPlacement.Validate(LayoutPlacement.PreviewSpec(w.Doc, w.Spec));
                if (selected.kind == PtKind.Landmark)
                    foreach (var row in ((JArray)LayoutPlacement.PreviewSpec(w.Doc, w.Spec)["rows"]).OfType<JObject>())
                        foreach (var plot in ((JArray)row["plots"]).OfType<JObject>().Where(p => (string)p["landmark"] == selected.owner))
                        { Handles.color = conflict == "" ? new Color(.3f, 1, .5f) : Color.red; Handles.DrawAAPolyLine(4, Closed(LayoutPlacement.Footprint(row, plot))); }
            }
            if (LayoutPlayHere.Target != Vector3.zero)
            { Handles.color = Color.blue; Handles.DrawWireDisc(LayoutPlayHere.Target, Vector3.up, .4f); Handles.Label(LayoutPlayHere.Target + Vector3.up, "PLAY HERE"); }
            if (Event.current.rawType == EventType.MouseUp && dragGroup >= 0) { Undo.CollapseUndoOperations(dragGroup); dragGroup = -1; }
            Handles.zTest = previous;
        }
        static void Move(EnvLayoutEditor w, EditPt p)
        {
            Handles.color = w.Height ? new Color(.4f, 1, .5f) : Gold;
            EditorGUI.BeginChangeCheck();
            bool supportsY = p.kind == PtKind.Node || p.kind == PtKind.StreetVia || p.kind == PtKind.PlazaVertex || p.kind == PtKind.PlazaDisc;
            var at = w.Height && supportsY ? Handles.Slider(p.world, Vector3.up) : Handles.Slider2D(p.world, Vector3.up, Vector3.right, Vector3.forward, HandleUtility.GetHandleSize(p.world) * .12f, Handles.RectangleHandleCap, Vector2.zero);
            if (EditorGUI.EndChangeCheck()) w.Edit("Mover " + p.label, d => LayoutDocument.Move(d, p, at, w.Height && supportsY));
            if (w.Height && !supportsY) Handles.Label(p.world + Vector3.up, "Este control modifica X/Z; no tiene altura independiente.");
        }
        static void Landmark(EnvLayoutEditor w, EditPt p)
        {
            if (!w.Height) Move(w, p); // planar position or explicit Y, never both in the same gesture
            if (w.Height)
            {
                EditorGUI.BeginChangeCheck(); var y = Handles.Slider(p.world, Vector3.up);
                if (EditorGUI.EndChangeCheck()) w.Edit("Altura de " + p.label, d => LayoutDocument.Move(d, p, y, true));
            }
            EditorGUI.BeginChangeCheck();
            var rotation = Handles.Disc(Quaternion.Euler(0, p.yaw, 0), p.world, Vector3.up, HandleUtility.GetHandleSize(p.world) * .55f, false, 0);
            if (EditorGUI.EndChangeCheck()) w.Edit("Girar " + p.label, d => { LayoutDocument.Move(d, p, p.world, true); LayoutDocument.Item(d, "landmarks", p.owner)["yaw"] = rotation.eulerAngles.y; });
        }
        static void Width(EnvLayoutEditor w, EditPt p)
        {
            var street = LayoutDocument.Item(w.Doc, "streets", p.owner); var points = LayoutDocument.StreetPoints(w.Doc, street);
            var mid = (points[0] + points[1]) / 2; var normal = Vector3.Cross((points[1] - points[0]).normalized, Vector3.up).normalized;
            float width = LayoutDocument.Width(w.Doc, street);
            foreach (float sign in new[] { -1f, 1f })
            {
                Handles.color = Gold; EditorGUI.BeginChangeCheck();
                var at = Handles.Slider(mid + normal * width / 2 * sign, normal * sign);
                if (EditorGUI.EndChangeCheck())
                { float newWidth = Mathf.Max(.5f, Vector3.Dot(at - mid, normal * sign) * 2); w.Edit("Anchura de " + p.label, d => LayoutDocument.Item(d, "streets", p.owner)["width"] = newWidth); }
            }
        }
    }

    [Overlay(typeof(SceneView), "ENV Director", true)]
    public class EnvDirectorOverlay : Overlay
    {
        public override VisualElement CreatePanelContent()
        {
            var panel = new VisualElement(); panel.style.minWidth = 260;
            panel.Add(new IMGUIContainer(() =>
            {
                var w = EnvLayoutEditor.Active;
                if (!w) { if (GUILayout.Button("ABRIR ENV DIRECTOR")) EnvLayoutEditor.Open(); return; }
                if (w.Doc == null) { GUILayout.Label("Carga CASCO desde el Director"); return; }
                GUILayout.Label(LayoutReceipt.State(EnvLayoutEditor.District, w.Dirty), EditorStyles.boldLabel);
                GUILayout.Label(w.Selected?.label ?? "Click en calle, punto, plaza o hito");
                w.DrawCompact();
                using (new EditorGUILayout.HorizontalScope())
                { if (GUILayout.Button("Planta")) w.View(0); if (GUILayout.Button("Encuadrar")) w.View(1); if (GUILayout.Button("A pie")) w.View(2); }
            }));
            return panel;
        }
    }
}

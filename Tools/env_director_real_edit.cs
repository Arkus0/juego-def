// Bounded operator trial on CASCO. Calls the same edits and SAVE used by native
// handles; the node's native pick/drag is proven separately. Revert after evidence.
var w = JuegoDef.Env.EnvLayoutEditor.Active;
w.Load();
System.IO.File.WriteAllText("Library/ENVDirector/trial-before.trace.json",System.IO.File.ReadAllText(JuegoDef.Env.LayoutDocument.TracePath(JuegoDef.Env.EnvLayoutEditor.District)));
var node=w.Points.First(p=>p.kind==JuegoDef.Env.PtKind.Node && p.owner=="E1");
w.Edit("Mover nodo y altura",d=>JuegoDef.Env.LayoutDocument.Move(d,node,node.world+new UnityEngine.Vector3(.25f,.15f,0),true));
var via=w.Points.First(p=>p.kind==JuegoDef.Env.PtKind.StreetVia);
w.Edit("Mover curva",d=>JuegoDef.Env.LayoutDocument.Move(d,via,via.world+new UnityEngine.Vector3(.1f,.05f,.1f),true));
w.Edit("Anchura de calle",d=>{var street=JuegoDef.Env.LayoutDocument.Item(d,"streets","Espina_E");street["width"]=JuegoDef.Env.LayoutDocument.Width(d,street)+.15f;});
var plaza=w.Points.First(p=>p.kind==JuegoDef.Env.PtKind.PlazaVertex);
w.Edit("Vértice de plaza",d=>JuegoDef.Env.LayoutDocument.Move(d,plaza,plaza.world+new UnityEngine.Vector3(0,0,-.15f),false));
var lm=w.Points.First(p=>p.kind==JuegoDef.Env.PtKind.Landmark && p.owner=="Torre");
w.Edit("Mover y girar landmark",d=>{JuegoDef.Env.LayoutDocument.Move(d,lm,lm.world+new UnityEngine.Vector3(2,.1f,-1),true);JuegoDef.Env.LayoutDocument.Item(d,"landmarks","Torre")["yaw"]=lm.yaw+5;});
w.Select(w.Points.First(p=>p.kind==JuegoDef.Env.PtKind.Landmark && p.owner=="Torre"));
var conflict=JuegoDef.Env.LayoutPlacement.Validate(JuegoDef.Env.LayoutPlacement.PreviewSpec(w.Doc,w.Spec));
if(conflict!="") throw new System.InvalidOperationException(conflict);
if(!w.Save(false)) throw new System.InvalidOperationException("SAVE trial failed");
System.IO.File.WriteAllText("Library/ENVDirector/trial-after.trace.json",w.Doc.ToString());
JuegoDef.Env.LayoutRebuild.phase=JuegoDef.Env.LayoutRebuild.Phase.None;
JuegoDef.Env.LayoutRebuild.AutoConfirm=true;JuegoDef.Env.LayoutRebuild.ForceFull=false;
JuegoDef.Env.LayoutRebuild.Start(JuegoDef.Env.EnvLayoutEditor.District,UnityEngine.Application.dataPath);
return new {phase=JuegoDef.Env.LayoutRebuild.phase.ToString(),changes=JuegoDef.Env.LayoutDocument.Changes(Newtonsoft.Json.Linq.JObject.Parse(System.IO.File.ReadAllText("Library/ENVDirector/trial-before.trace.json")),w.Doc).ToArray()};

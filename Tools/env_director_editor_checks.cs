// Run through Unity Pipeline eval_file. Uses real CASCO and the public owner action
// services; restores the original layout with REVERT before returning.
var results = new System.Collections.Generic.Dictionary<string, bool>();
void Check(string label, bool value) { if (!value) throw new System.InvalidOperationException(label); results[label] = value; }
var id = JuegoDef.Env.EnvLayoutEditor.District;
var path = JuegoDef.Env.LayoutDocument.TracePath(id);
var original = System.IO.File.ReadAllText(path);
var source = Newtonsoft.Json.Linq.JObject.Parse(original);
var testPath = "Library/ENVDirector/roundtrip.trace.json";
System.IO.Directory.CreateDirectory("Library/ENVDirector");
System.IO.File.WriteAllText(testPath, original);
Check("no_edit_save_preserves_bytes", !JuegoDef.Env.LayoutDocument.Save(testPath, original, source) && System.IO.File.ReadAllText(testPath) == original);
var unknown = (Newtonsoft.Json.Linq.JObject)source.DeepClone();
unknown["futureField"] = new Newtonsoft.Json.Linq.JObject { ["nested"] = new Newtonsoft.Json.Linq.JArray(1,"keep",true) };
var node = JuegoDef.Env.LayoutDocument.Points(unknown, null).First(p=>p.kind==JuegoDef.Env.PtKind.Node);
JuegoDef.Env.LayoutDocument.Move(unknown,node,node.world+UnityEngine.Vector3.right*.2f,false);
JuegoDef.Env.LayoutDocument.Save(testPath,original,unknown);
Check("unknown_fields_survive", Newtonsoft.Json.Linq.JToken.DeepEquals(unknown["futureField"],Newtonsoft.Json.Linq.JObject.Parse(System.IO.File.ReadAllText(testPath))["futureField"]));
Check("backup_before_replacement",System.IO.File.ReadAllText(testPath+".bak")==original);
bool rejected=false; try { JuegoDef.Env.LayoutDocument.Save(testPath,original,source); } catch(System.IO.IOException) { rejected=true; }
Check("external_writer_fails_closed",rejected);
var invalid=(Newtonsoft.Json.Linq.JObject)source.DeepClone(); invalid["streets"][0]["width"]=-1;
rejected=false; try { JuegoDef.Env.LayoutDocument.Save(testPath,System.IO.File.ReadAllText(testPath),invalid); } catch(System.IO.InvalidDataException) { rejected=true; }
Check("malformed_source_fails_closed",rejected);
var crossing=(Newtonsoft.Json.Linq.JObject)source.DeepClone();
crossing["plazas"][0].Remove(); // exercise an invalid collection member separately
crossing["plazas"].First.Replace(new Newtonsoft.Json.Linq.JValue("unsupported"));
rejected=false; try { JuegoDef.Env.LayoutDocument.Validate(crossing); } catch(System.IO.InvalidDataException) { rejected=true; }
Check("unsupported_collection_fails_closed",rejected);
var badCollection=(Newtonsoft.Json.Linq.JObject)source.DeepClone();badCollection["landmarks"]=new Newtonsoft.Json.Linq.JObject();
rejected=false;try {JuegoDef.Env.LayoutDocument.Validate(badCollection);}catch(System.IO.InvalidDataException){rejected=true;}
Check("malformed_landmark_collection_blocked",rejected);
var badRiver=(Newtonsoft.Json.Linq.JObject)source.DeepClone();badRiver["river"]["pts"][0][0]=double.NaN;
rejected=false;try {JuegoDef.Env.LayoutDocument.Validate(badRiver);}catch(System.IO.InvalidDataException){rejected=true;}
Check("nonfinite_river_blocked",rejected);
JuegoDef.Env.EnvLayoutEditor.Open(); var w=JuegoDef.Env.EnvLayoutEditor.Active; w.Load();
var selected=w.Points.First(p=>p.kind==JuegoDef.Env.PtKind.Node && p.owner=="E1"); w.Select(selected);
UnityEditor.Undo.IncrementCurrentGroup();
w.Edit("D1 real Undo proof", d=>JuegoDef.Env.LayoutDocument.Move(d,selected,selected.world+UnityEngine.Vector3.right*.2f,false));
UnityEditor.Undo.FlushUndoRecordObjects();
Check("preview_never_writes_authority",w.Dirty && System.IO.File.ReadAllText(path)==original);
UnityEditor.Undo.PerformUndo(); Check("undo_preview",!w.Dirty);
UnityEditor.Undo.PerformRedo(); Check("redo_preview",w.Dirty);
Check("save_real_layout",w.Save(false));
UnityEditor.Undo.PerformUndo(); Check("undo_after_save_keeps_saved_baseline",w.Dirty);
UnityEditor.Undo.PerformRedo(); Check("redo_after_save_is_clean",!w.Dirty);
w.Revert(false);
Check("revert_saved_authority",!w.Dirty && Newtonsoft.Json.Linq.JToken.DeepEquals(source,Newtonsoft.Json.Linq.JObject.Parse(System.IO.File.ReadAllText(path))));
w.Close(); JuegoDef.Env.EnvLayoutEditor.Open(); w=JuegoDef.Env.EnvLayoutEditor.Active;
Check("close_reopen_persistence",!w.Dirty && Newtonsoft.Json.Linq.JToken.DeepEquals(source,w.Doc));
var specPath=JuegoDef.Env.LayoutDocument.SpecPath(id); var specBytes=System.IO.File.ReadAllBytes(specPath);
try
{
    System.IO.File.AppendAllText(specPath," "); rejected=false;
    try { JuegoDef.Env.LayoutReceipt.CheckSpec(id); } catch(System.IO.IOException) { rejected=true; }
    Check("unrepresented_spec_edit_blocked",rejected);
}
finally { System.IO.File.WriteAllBytes(specPath,specBytes); }
var baselineSpec=Newtonsoft.Json.Linq.JObject.Parse(System.IO.File.ReadAllText(specPath));
var changed=(Newtonsoft.Json.Linq.JObject)baselineSpec.DeepClone();
changed["rows"][0]["ends"]["east"]="open-test";
Check("isolated_row_end_is_material",JuegoDef.Env.LayoutRebuild.SpecDiff.Compute(baselineSpec,changed).rowIdsChanged.Count==1);
changed=(Newtonsoft.Json.Linq.JObject)baselineSpec.DeepClone();
var seeded=((Newtonsoft.Json.Linq.JArray)changed["rows"]).SelectMany(r=>((Newtonsoft.Json.Linq.JArray)r["plots"]).OfType<Newtonsoft.Json.Linq.JObject>()).First(p=>p["seed"]!=null); seeded["seed"]=(int)seeded["seed"]+1;
Check("stateful_seed_change_is_material",JuegoDef.Env.LayoutRebuild.SpecDiff.Compute(baselineSpec,changed).rowsStateful==1);
changed=(Newtonsoft.Json.Linq.JObject)baselineSpec.DeepClone();
for(int i=0;i<7;i++)changed["rows"][i]["ends"]["east"]="test";
Check("batch_seven_detected",JuegoDef.Env.LayoutRebuild.SpecDiff.Compute(baselineSpec,changed).rowIdsChanged.Count==7);
changed=(Newtonsoft.Json.Linq.JObject)baselineSpec.DeepClone();changed["futureProductGeometry"]=new Newtonsoft.Json.Linq.JObject{["shape"]="changed"};
Check("unknown_product_field_is_material",JuegoDef.Env.LayoutRebuild.SpecDiff.Compute(baselineSpec,changed).otherChanged.Count==1);
var codePath="Assets/JuegoDef/Editor/Env/EnvDirectorScene.cs"; var codeBytes=System.IO.File.ReadAllBytes(codePath);
UnityEditor.AssetDatabase.DisallowAutoRefresh();
try
{
    System.IO.File.AppendAllText(codePath,"\n// temporary uncompiled recipe falsifier\n");
    JuegoDef.Env.LayoutRebuild.phase=JuegoDef.Env.LayoutRebuild.Phase.None;
    JuegoDef.Env.LayoutRebuild.Start(id,UnityEngine.Application.dataPath);
    Check("uncompiled_recipe_blocked",JuegoDef.Env.LayoutRebuild.phase==JuegoDef.Env.LayoutRebuild.Phase.Failed && !JuegoDef.Env.EnvRebuildTransaction.Pending);
}
finally {System.IO.File.WriteAllBytes(codePath,codeBytes);UnityEditor.AssetDatabase.AllowAutoRefresh();JuegoDef.Env.LayoutRebuild.Cancel("negative check complete");}
System.IO.File.WriteAllText("Library/ENVDirector/editor-checks.json", Newtonsoft.Json.JsonConvert.SerializeObject(results,Newtonsoft.Json.Formatting.Indented));
return Newtonsoft.Json.JsonConvert.SerializeObject(results);

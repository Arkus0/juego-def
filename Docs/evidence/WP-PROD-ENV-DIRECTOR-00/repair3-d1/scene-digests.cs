var root=UnityEngine.GameObject.Find("ENV01_Casco_District").transform.Find("Rows");
var results=new Newtonsoft.Json.Linq.JObject();
foreach(UnityEngine.Transform row in root)
{
 var lines=new System.Collections.Generic.List<string>();
 foreach(var t in row.GetComponentsInChildren<UnityEngine.Transform>(true))
 {
  var parts=new System.Collections.Generic.List<string>(); for(var c=t;c!=row;c=c.parent)parts.Add(c.name);parts.Reverse();
  string f(float v)=>System.Math.Round(v,3).ToString("F3",System.Globalization.CultureInfo.InvariantCulture);
  var pos=t.position;var rot=t.rotation.eulerAngles;var scale=t.lossyScale;var mesh=t.GetComponent<UnityEngine.MeshFilter>();var renderer=t.GetComponent<UnityEngine.Renderer>();
  lines.Add(string.Join("/",parts)+"|"+string.Join(",",new[]{pos.x,pos.y,pos.z,rot.x,rot.y,rot.z,scale.x,scale.y,scale.z}.Select(f))+"|"+t.gameObject.activeSelf+"|"+(mesh&&mesh.sharedMesh?mesh.sharedMesh.name+":"+mesh.sharedMesh.vertexCount:"")+"|"+(renderer?string.Join(",",renderer.sharedMaterials.Select(m=>m?m.name:"null")):"")+"|"+string.Join(",",t.GetComponents<UnityEngine.Component>().Select(c=>c?c.GetType().Name:"missing")));
 }
 lines.Sort(System.StringComparer.Ordinal);results[row.name]=JuegoDef.Env.OsmPin.Sha256Text(string.Join("\n",lines));
}
System.IO.File.WriteAllText("Library/ENVDirector/scene-digests.json",results.ToString());return new {rows=results.Count};
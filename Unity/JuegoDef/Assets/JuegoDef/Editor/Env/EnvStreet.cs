using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// Step 4 of the ENV factory: assembles a street from a data spec (Env/Specs/streets/*.json). A street is an
    /// axis along +x with a floor style, two building rows that reference library units by id (with overrides:
    /// palette, seed, floors, rows...) and placed templates (quay edge, stepped connector, clusters...). The
    /// assembler resolves party walls between neighbours, one quoin column per shared edge and exposed ends, so
    /// the operator asks for outcomes ("a lodging, then a narrow closed house, a 2 m alley...") not object paths.
    /// </summary>
    public static class EnvStreet
    {
        public const string StreetSpecs = EnvKit.Specs + "/streets";

        class Placed
        {
            public BuildingSpec spec;
            public float x0, width;
            public bool north;
        }

        [MenuItem("JuegoDef/ENV/4 Build Street Demos")]
        public static void BuildDemos()
        {
            foreach (var guid in AssetDatabase.FindAssets("t:TextAsset", new[] { StreetSpecs }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                if (path.EndsWith(".json")) BuildScene(path);
            }
        }

        /// <summary>Builds the street into a new scene with the project lighting and the bootstrap GC2 player, then
        /// saves it as Scenes/ENV/&lt;id&gt;.unity.</summary>
        public static string BuildScene(string specPath)
        {
            var spec = JObject.Parse(EnvKit.ReadText(specPath));
            var id = (string)spec["id"];
            var stage = EnvPreview.NewStage(id, ground: false);
            Object.DestroyImmediate(stage.gameObject);
            var root = Build(spec, null);
            BringPlayer(spec);
            EnvKit.EnsureFolder("Assets/JuegoDef/Scenes/ENV");
            var scenePath = $"Assets/JuegoDef/Scenes/ENV/{id}.unity";
            EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(), scenePath);
            // Glass and wet stone need the street itself in their reflections; without a probe they mirror the
            // default sky's brown lower hemisphere. One small baked probe per street is enough at this stage.
            var probeGo = new GameObject("StreetReflectionProbe");
            var rp = probeGo.AddComponent<ReflectionProbe>();
            float len = (float)spec["length"], wid = (float)spec["width"];
            probeGo.transform.position = new Vector3(len / 2f, 2f, wid / 2f);
            rp.size = new Vector3(len + 20f, 20f, wid + 20f);
            rp.mode = UnityEngine.Rendering.ReflectionProbeMode.Custom;
            rp.resolution = 128;
            rp.boxProjection = true;
            var cubePath = $"Assets/JuegoDef/Scenes/ENV/{id}_Reflection.exr";
            if (Lightmapping.BakeReflectionProbe(rp, cubePath))
            {
                AssetDatabase.ImportAsset(cubePath);
                rp.customBakedTexture = AssetDatabase.LoadAssetAtPath<Cubemap>(cubePath);
            }
            EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(), scenePath);
            Debug.Log($"JD_ENV_STREET {id} -> {scenePath} objects={root.GetComponentsInChildren<Transform>().Length}");
            return scenePath;
        }

        public static GameObject Build(JObject spec, Transform parent)
        {
            EnvKit.ClearCache();
            BuildingAssembler.ReloadGrammar();
            var units = JObject.Parse(EnvKit.ReadText(EnvKit.Specs + "/units.json"))["units"].ToDictionary(u => (string)u["id"], u => (JObject)u);
            var root = new GameObject((string)spec["id"]).transform;
            root.SetParent(parent, false);
            float length = (float)spec["length"], width = (float)spec["width"];
            string ground = (string)spec["ground"] ?? "kerbed";
            float datum = ground == "kerbed" ? EnvTemplates.PavementTop : 0f;
            EnvTemplates.StreetGround(root, length, width, ground, (float?)spec["pavement"] ?? 1.5f);

            var placed = new List<Placed>();
            foreach (var side in new[] { "south", "north" })
            {
                var row = spec["rows"]?[side] as JArray;
                if (row == null) continue;
                float x = (float?)spec["rowStart"]?[side] ?? 0f;
                var rowPlaced = new List<Placed>();
                foreach (JObject item in row)
                {
                    if (item["gap"] != null) { x += (float)item["gap"]; rowPlaced.Add(null); continue; }
                    var bs = Resolve(item, units);
                    var p = new Placed { spec = bs, x0 = x, width = bs.bays * 2, north = side == "north" };
                    rowPlaced.Add(p);
                    placed.Add(p);
                    x += p.width;
                }
                ResolveNeighbours(rowPlaced, spec["ends"]?[side] as JObject);
                var rowRoot = EnvKit.Group(root, "Row_" + side);
                foreach (var p in rowPlaced.Where(p => p != null))
                {
                    var go = BuildingAssembler.Build(p.spec, rowRoot);
                    go.transform.localPosition = p.north ? new Vector3(p.x0 + p.width, datum, width) : new Vector3(p.x0, datum, 0);
                    go.transform.localRotation = Quaternion.Euler(0, p.north ? 180 : 0, 0);
                }
            }

            if (spec["templates"] is JArray templates)
            {
                var troot = EnvKit.Group(root, "Templates");
                foreach (JObject t in templates)
                {
                    var holder = new GameObject((string)t["name"] ?? (string)t["kind"]).transform;
                    holder.SetParent(troot, false);
                    holder.localPosition = V((JArray)t["at"]);
                    holder.localRotation = Quaternion.Euler(0, (float?)t["rotY"] ?? 0, 0);
                    var unit = t["unit"] != null ? units[(string)t["unit"]] : new JObject { ["id"] = (string)t["kind"], ["kind"] = t["kind"], ["params"] = t["params"] };
                    EnvLibrary.BuildUnit(unit, holder);
                }
            }

            if (spec["route"] is JArray route)
            {
                var probe = new GameObject("RouteProbe");
                probe.transform.SetParent(root, false);
                probe.SetActive(false);
                var comp = probe.AddComponent<JuegoDef.Dev.JDRouteProbe>();
                comp.waypoints = route.Select(w => root.TransformPoint(V((JArray)w))).ToArray();
            }
            return root.gameObject;
        }

        static Vector3 V(JArray a) => new Vector3((float)a[0], (float)a[1], (float)a[2]);

        static BuildingSpec Resolve(JObject item, Dictionary<string, JObject> units)
        {
            JObject b;
            if (item["unit"] != null)
            {
                var uid = (string)item["unit"];
                if (!units.TryGetValue(uid, out var unit) || (string)unit["kind"] != "building")
                    throw new System.ArgumentException("ENV_STREET_UNKNOWN_BUILDING_UNIT " + uid);
                b = (JObject)unit["building"].DeepClone();
            }
            else b = new JObject();
            foreach (var kv in item)
                if (kv.Key != "unit") b[kv.Key] = kv.Value.DeepClone();
            var spec = b.ToObject<BuildingSpec>();
            spec.id = (string)item["name"] ?? ((string)item["unit"] ?? spec.type) + "_" + spec.seed;
            return spec;
        }

        /// <summary>West/east neighbours along the row (null entries are gaps/alleys). Shared storeys hide both side
        /// walls when the neighbour is at least as deep; the taller (or western, on a tie) building keeps the quoins of
        /// the shared edge; open ends expose.</summary>
        static void ResolveNeighbours(List<Placed> row, JObject ends)
        {
            bool westOpen = (string)ends?["west"] != "hidden", eastOpen = (string)ends?["east"] != "hidden";
            for (int i = 0; i < row.Count; i++)
            {
                var p = row[i];
                if (p == null) continue;
                var west = i > 0 ? row[i - 1] : null;
                var east = i < row.Count - 1 ? row[i + 1] : null;
                // a neighbour only covers our side wall if it is at least as deep (else the rear part would be a hole)
                int westParty = west != null ? (west.spec.depth >= p.spec.depth ? Mathf.Min(west.spec.floors, p.spec.floors) : 0) : (i == 0 && !westOpen ? p.spec.floors : 0);
                int eastParty = east != null ? (east.spec.depth >= p.spec.depth ? Mathf.Min(east.spec.floors, p.spec.floors) : 0) : (i == row.Count - 1 && !eastOpen ? p.spec.floors : 0);
                bool westExposed = west == null && (i > 0 || westOpen);
                bool eastExposed = east == null && (i < row.Count - 1 || eastOpen);
                bool westQuoins = west == null || p.spec.floors > west.spec.floors;
                bool eastQuoins = east == null || p.spec.floors >= east.spec.floors;
                // building local left = west for the south row, east for the north row (rotated 180)
                if (!p.north)
                {
                    p.spec.partyLeft = westParty; p.spec.partyRight = eastParty;
                    p.spec.exposeLeft |= westExposed; p.spec.exposeRight |= eastExposed;
                    p.spec.quoinsLeft = westQuoins; p.spec.quoinsRight = eastQuoins;
                }
                else
                {
                    p.spec.partyLeft = eastParty; p.spec.partyRight = westParty;
                    p.spec.exposeLeft |= eastExposed; p.spec.exposeRight |= westExposed;
                    p.spec.quoinsLeft = eastQuoins; p.spec.quoinsRight = westQuoins;
                }
            }
        }

        /// <summary>Copies the bootstrap GC2 player, camera and camera shot into the street scene at the spec's spawn.</summary>
        static void BringPlayer(JObject spec)
        {
            var active = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            var boot = EditorSceneManager.OpenScene("Assets/JuegoDef/Scenes/Bootstrap_GC2Core.unity", OpenSceneMode.Additive);
            var spawn = spec["spawn"] is JArray a ? V(a) : new Vector3(2, 0.2f, 4);
            foreach (var go in boot.GetRootGameObjects())
            {
                if (go.name != "Player" && go.name != "Main Camera" && go.name != "Camera Shot") continue;
                UnityEngine.SceneManagement.SceneManager.MoveGameObjectToScene(go, active);
                go.transform.position += spawn;  // keeps the bootstrap offsets (player pivot 1 m above its ground)
            }
            var oldCam = active.GetRootGameObjects().FirstOrDefault(g => g.name == "Main Camera" && !g.GetComponents<MonoBehaviour>().Any(m => m && m.GetType().Namespace != null && m.GetType().Namespace.StartsWith("GameCreator")));
            if (oldCam) Object.DestroyImmediate(oldCam);
            EditorSceneManager.CloseScene(boot, true);
        }
    }
}

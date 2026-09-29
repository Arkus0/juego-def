using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// Facade-row rules shared by the district builder (<see cref="EnvDistrict"/>): a row is an ordered list of
    /// placed buildings along one block edge; the resolver decides party walls between neighbours (height aware on
    /// sloping ground), one quoin column per shared edge, exposed ends and mitred block tips. Also brings the
    /// bootstrap GC2 player into a built scene. The v1 street-demo assembler (straight/path street specs and its
    /// street-life pass) was retired with the demos on 2026-09-29; it lives in git history (commit c3d7796).
    /// </summary>
    public static class EnvStreet
    {
        internal class Placed
        {
            public BuildingSpec spec;
            public float x0, width, setback, scale = 1f;
            public float y;          // ground-floor level (districts on sloping ground; 0 on flat streets)
            public bool north;
        }

        /// <summary>West/east neighbours along the row (null entries are gaps/alleys). Shared storeys hide both side
        /// walls when the neighbour is at least as deep; the taller (or western, on a tie) building keeps the quoins of
        /// the shared edge; open ends expose.</summary>
        internal static void ResolveNeighbours(List<Placed> row, JObject ends)
        {
            // row ends: open (exposed, quoins) | hidden (a neighbour beyond the spec) | tip_keep / tip_cede (convex block
            // tip at a bend: no side walls, one quoin) | concave (outer corner of a bend: side wall to the back notch, no quoins)
            string westKind = (string)ends?["west"] ?? "open", eastKind = (string)ends?["east"] ?? "open";
            bool westOpen = westKind == "open", eastOpen = eastKind == "open";
            for (int i = 0; i < row.Count; i++)
            {
                var p = row[i];
                if (p == null) continue;
                var west = i > 0 ? row[i - 1] : null;
                var east = i < row.Count - 1 ? row[i + 1] : null;
                // a neighbour only covers our side wall if it is at least as deep and on the same building line
                // (else the rear part, or the step of a setback, would be a hole)
                bool Covers(Placed o) => o.spec.depth >= p.spec.depth && Mathf.Abs(o.setback - p.setback) < 0.01f;
                // storeys of p (from the ground floor up) that lie entirely within the neighbour's height, so a
                // neighbour one step up or down a sloping street never leaves a sliver of missing side wall
                int Shared(Placed o)
                {
                    if (!Covers(o)) return 0;
                    float bottom = o.y - o.spec.basement - 0.05f, top = o.y + o.spec.floors * BuildingAssembler.Storey + 0.05f;
                    int n = 0;
                    for (int f = 0; f < p.spec.floors; f++)
                    {
                        if (p.y + f * BuildingAssembler.Storey < bottom || p.y + (f + 1) * BuildingAssembler.Storey > top) break;
                        n++;
                    }
                    return n;
                }
                int westParty = west != null ? Shared(west) : (i == 0 && !westOpen ? p.spec.floors : 0);
                int eastParty = east != null ? Shared(east) : (i == row.Count - 1 && !eastOpen ? p.spec.floors : 0);
                bool westExposed = west == null && (i > 0 || westOpen);
                bool eastExposed = east == null && (i < row.Count - 1 || eastOpen);
                bool westQuoins = west == null || p.spec.floors > west.spec.floors || westParty == 0;
                bool eastQuoins = east == null || p.spec.floors >= east.spec.floors || eastParty == 0;
                bool westTip = false, eastTip = false;
                if (i == 0 && west == null && westKind != "open" && westKind != "hidden")
                {
                    westParty = westKind.StartsWith("tip") ? p.spec.floors : 0;
                    westQuoins = westKind == "tip_keep";
                    westTip = westQuoins;
                }
                if (i == row.Count - 1 && east == null && eastKind != "open" && eastKind != "hidden")
                {
                    eastParty = eastKind.StartsWith("tip") ? p.spec.floors : 0;
                    eastQuoins = eastKind == "tip_keep";
                    eastTip = eastQuoins;
                }
                // building local left = west for the south row, east for the north row (rotated 180)
                if (!p.north)
                {
                    p.spec.partyLeft = westParty; p.spec.partyRight = eastParty;
                    p.spec.exposeLeft |= westExposed; p.spec.exposeRight |= eastExposed;
                    p.spec.quoinsLeft = westQuoins; p.spec.quoinsRight = eastQuoins;
                    p.spec.tipLeft = westTip; p.spec.tipRight = eastTip;
                }
                else
                {
                    p.spec.partyLeft = eastParty; p.spec.partyRight = westParty;
                    p.spec.exposeLeft |= eastExposed; p.spec.exposeRight |= westExposed;
                    p.spec.quoinsLeft = eastQuoins; p.spec.quoinsRight = westQuoins;
                    p.spec.tipLeft = eastTip; p.spec.tipRight = westTip;
                }
            }
        }

        /// <summary>Copies the bootstrap GC2 player, camera and camera shot into the built scene at the spec's spawn.</summary>
        internal static void BringPlayer(JObject spec)
        {
            var active = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            var boot = EditorSceneManager.OpenScene("Assets/JuegoDef/Scenes/Bootstrap_GC2Core.unity", OpenSceneMode.Additive);
            var spawn = spec["_spawnWorld"] is JArray a ? new Vector3((float)a[0], (float)a[1], (float)a[2]) : new Vector3(2, 0.2f, 4);
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

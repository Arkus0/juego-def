using System.Collections.Generic;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// Assembly templates for the non-building parts of a street (CITY layered street assembly: datum ->
    /// traversable surface -> kerb/drain edge -> retaining/threshold contact -> dressing). Each template builds under
    /// a parent in its local frame; the street assembler and the unit library both call them, so a template fix
    /// improves every street. Frames: x runs along the street/edge, +z is "towards the street/water", y up.
    /// </summary>
    public static class EnvTemplates
    {
        static readonly Dictionary<string, string> WetCobble = new Dictionary<string, string> { { "MI_RoundRocks", "ENV_Ground_WetCobble" } };
        public const float PavementTop = 0.15f;

        /// <summary>Street floor between two facade lines z = 0 and z = width.
        /// kerbed: cobbled carriageway at y = 0, flagged pavements (+0.15) of <paramref name="pavement"/> m with granite kerbs.
        /// pedestrian: single cobbled level at y = 0 with a central granite drainage channel.</summary>
        public static Transform StreetGround(Transform parent, float length, float width, string style = "kerbed", float pavement = 1.5f)
        {
            var root = EnvKit.Group(parent, "StreetGround");
            int nx = Mathf.CeilToInt(length / 2f);
            if (style == "pedestrian")
            {
                Tiles(root, "Floor_RoundRocks", 0, length, 0, width, 0, WetCobble);
                for (int i = 0; i < nx; i++) EnvKit.Place("ENV_Gutter_Channel_2m", root, new Vector3(1 + 2 * i, 0.001f, width / 2f), 0);
                return root;
            }
            Tiles(root, "Floor_RoundRocks", 0, length, pavement, width - pavement, 0, WetCobble);
            Tiles(root, "Floor_UnevenBrick", 0, length, 0, pavement, PavementTop, null);
            Tiles(root, "Floor_UnevenBrick", 0, length, width - pavement, width, PavementTop, null);
            for (int i = 0; i < nx; i++)
            {
                EnvKit.Place("ENV_Kerb_2m", root, new Vector3(1 + 2 * i, 0, pavement - 0.14f), 0);
                EnvKit.Place("ENV_Kerb_2m", root, new Vector3(1 + 2 * i, 0, width - pavement + 0.14f), 180);
            }
            return root;
        }

        /// <summary>Covers an x/z rectangle with 2 m kit floor tiles; the last row/column is scaled, never overlapped
        /// (overlapping coplanar tiles z-fight).</summary>
        public static void Tiles(Transform parent, string tile, float x0, float x1, float z0, float z1, float y, Dictionary<string, string> remap)
        {
            for (float x = x0; x < x1 - 0.01f; x += 2f)
            {
                float sx = Mathf.Min(2f, x1 - x);
                for (float z = z0; z < z1 - 0.01f; z += 2f)
                {
                    float sz = Mathf.Min(2f, z1 - z);
                    var go = EnvKit.Place(tile, parent, new Vector3(x + sx / 2f, y, z + sz / 2f), 0, new Vector3(sx / 2f, 1, sz / 2f));
                    EnvKit.Remap(go, remap);
                }
            }
        }

        /// <summary>Public working-water edge: rubble quay wall + granite coping at y = 0, flagged quay floor behind
        /// (z &lt; 0), mooring bollards, a ladder, optional guard rail (overlook), water 1.4 m below the coping.</summary>
        public static Transform QuayEdge(Transform parent, float length, bool railing, float quayDepth = 6f)
        {
            var root = EnvKit.Group(parent, "QuayEdge");
            int n = Mathf.CeilToInt(length / 4f);
            for (int i = 0; i < n; i++) EnvKit.Place("ENV_Quay_Wall_4m", root, new Vector3(2 + 4 * i, 0, 0), 0);
            Tiles(root, "Floor_UnevenBrick", 0, n * 4f, -quayDepth, -0.25f, 0.0f, null);
            for (float x = 3f; x < n * 4f; x += 8f)
                EnvKit.Place("ENV_Bollard_Mooring", root, new Vector3(x, 0.0f, -0.35f), 0);
            EnvKit.Place("ENV_Quay_Ladder", root, new Vector3(Mathf.Min(6f, n * 4f - 1), 0, 0), 0);
            if (railing)
                for (int i = 0; i < n * 2; i++) EnvKit.Place("ENV_Railing_Quay_2m", root, new Vector3(1 + 2 * i, 0, -0.55f), 0);
            var water = EnvKit.Place("ENV_Water_Plane_20m", root, new Vector3(n * 2f, -1.4f, 10f), 0, new Vector3(Mathf.Max(1f, n * 4f / 20f), 1, 1));
            water.name = "PortWater";
            return root;
        }

        /// <summary>Controlled work-yard boundary: galvanised palisade on a plinth with one sliding gate leaf parked
        /// in front of the fence line. Readably "you can see in, you cannot walk in".</summary>
        public static Transform YardBoundary(Transform parent, float length, int gateAt = 1)
        {
            var root = EnvKit.Group(parent, "YardBoundary");
            int n = Mathf.CeilToInt(length / 2f);
            for (int i = 0; i < n; i++)
            {
                if (i == gateAt) continue;
                EnvKit.Place("ENV_Fence_Yard_2m", root, new Vector3(1 + 2 * i, 0, 0), 0);
            }
            if (gateAt >= 0 && gateAt < n)
            {
                var gate = EnvKit.Place("ENV_Fence_Yard_2m", root, new Vector3(1 + 2 * gateAt, 0, 0.0f), 0);
                gate.name = "YardGate_Closed";
            }
            return root;
        }

        /// <summary>Stepped public connector rising <paramref name="height"/> m (1..3) from a lower datum (y = 0,
        /// z &gt; 1) to an upper terrace (y = height). The 2 m kit stair flights (1 m rise each, ascending towards -z)
        /// are cut into the terrace: rubble retaining walls line both sides and the terrace front (face at z = 1),
        /// guard rails run along every drop edge. Upper route continues at z &lt; 1 - 2*height.</summary>
        public static Transform SteppedConnector(Transform parent, int height, int terraceBays = 2)
        {
            var root = EnvKit.Group(parent, "SteppedConnector");
            height = Mathf.Clamp(height, 1, 3);
            string wall = "ENV_Retaining_Wall_2x" + height;
            for (int k = 0; k < height; k++)
            {
                float zc = -2f * k;
                EnvKit.Place("Stairs_Exterior_Straight", root, new Vector3(0, k, zc), 0);
                EnvKit.Place(wall, root, new Vector3(-1f, height, zc), 90);   // faces +x, into the stair
                EnvKit.Place(wall, root, new Vector3(1f, height, zc), -90);   // faces -x
                EnvKit.Place("ENV_Railing_Quay_2m", root, new Vector3(-1.45f, height, zc), 90);
                EnvKit.Place("ENV_Railing_Quay_2m", root, new Vector3(1.45f, height, zc), 90);
            }
            float head = 1f - 2f * height;           // z where the last flight arrives on the terrace
            float xw = 1f + terraceBays * 2f;        // terrace half width
            for (int b = 0; b < terraceBays; b++)
                for (int side = -1; side <= 1; side += 2)
                {
                    float x = side * (2f + 2f * b);
                    EnvKit.Place(wall, root, new Vector3(x, height, 1f), 0);
                    EnvKit.Place("ENV_Railing_Quay_2m", root, new Vector3(x, height, 0.7f), 0);
                }
            // terrace floor (kept clear of the copings to avoid coplanar faces), lower landing in front
            Tiles(root, "Floor_UnevenBrick", -xw, xw, head - 4f, head, height, null);
            Tiles(root, "Floor_UnevenBrick", -xw, -1.95f, head, 0.1f, height, null);
            Tiles(root, "Floor_UnevenBrick", 1.95f, xw, head, 0.1f, height, null);
            Tiles(root, "Floor_RoundRocks", -xw, xw, 1.1f, 5f, 0, WetCobble);
            return root;
        }

        /// <summary>Shallow shop interior behind a ground-floor frontage (building frame: street face z = 0, depth
        /// to -depthUsed): tiled floor, ceiling, back partition with a closed service door, counter, shelving and a
        /// warm interior light. The building's own walls provide the side faces.</summary>
        public static Transform ShopInterior(Transform parent, int bays, float doorX, float depthUsed = 4f)
        {
            var root = EnvKit.Group(parent, "Interior");
            float w = bays * 2f;
            Tiles(root, "Floor_Brick", 0.3f, w - 0.3f, -depthUsed, -0.4f, 0.01f, null);
            for (int i = 0; i < bays; i++)
            {
                var ceil = EnvKit.Place("Floor_WoodDark", root, new Vector3(1 + 2 * i, 2.95f, -depthUsed / 2f), 0, new Vector3(1, 1, depthUsed / 2f));
                ceil.transform.localRotation = Quaternion.Euler(180, 0, 0);
                string wall = i == bays - 1 ? "ENV_Wall_Plaster_Clean_Door" : "ENV_Wall_Plaster_Clean";
                var back = EnvKit.Place(wall, root, new Vector3(1 + 2 * i, 0, -depthUsed), 180);
                EnvKit.Remap(back, new Dictionary<string, string> { { "MI_Plaster", "ENV_Plaster_OffWhite" }, { "MI_WoodTrim", "ENV_Trim_White" } });
                if (i == bays - 1)
                {
                    EnvKit.Place("ENV_Door_Service", root, new Vector3(1 + 2 * i, 0, -depthUsed), 180);
                    var thr = new GameObject("THR_Service_Closed").transform;  // back-of-house: must stay shut
                    thr.SetParent(root, false);
                    thr.localPosition = new Vector3(1 + 2 * i, 0, -depthUsed);
                    thr.localRotation = Quaternion.Euler(0, 180, 0);
                }
            }
            EnvKit.Place("ENV_Counter_Shop", root, new Vector3(w * 0.5f, 0, -depthUsed + 1.6f), 0);
            EnvKit.Place("ENV_Prop_Shelf_Bottles", root, new Vector3(0.7f, 0, -depthUsed * 0.55f), 90);
            EnvKit.Place("ENV_Prop_Shelf_Simple", root, new Vector3(w - 0.7f, 0, -depthUsed * 0.55f), 270);
            // produce display on the side away from the public door: keep a clear 1.2 m lane door -> counter
            float side = doorX < w / 2f ? w - 1.1f : 1.1f;
            EnvKit.Place("ENV_Prop_FarmCrate_Apple", root, new Vector3(side, 0, -0.9f), 10);
            EnvKit.Place("ENV_Prop_FarmCrate_Carrot", root, new Vector3(side + (doorX < w / 2f ? -0.9f : 0.9f), 0, -0.9f), -8);
            var lightGo = new GameObject("InteriorLight");
            lightGo.transform.SetParent(root, false);
            lightGo.transform.localPosition = new Vector3(w / 2f, 2.6f, -depthUsed / 2f);
            var l = lightGo.AddComponent<Light>();
            l.type = LightType.Point;
            l.color = EnvKit.Hex("#E8B26A");
            l.intensity = 2.2f;
            l.range = 6f;
            l.shadows = LightShadows.None;
            return root;
        }

        /// <summary>Common lodging vestibule behind the portal bay, open to the next bay where the kit interior stair
        /// rises towards the back (to the rooms): flagged floor, ceiling over the entrance, side partitions to the
        /// building's back wall, a small reception counter and a warm light. Needs bays &gt;= portal + 2.</summary>
        public static Transform LodgingVestibule(Transform parent, int bay, int buildingBays, int depth)
        {
            if (bay + 1 >= buildingBays) throw new System.ArgumentException("lodging vestibule needs a bay right of the portal for the stair");
            var root = EnvKit.Group(parent, "Interior");
            float x = 1 + 2 * bay;
            float back = -depth + 0.32f;   // inner face of the building back wall
            var white = new Dictionary<string, string> { { "MI_Plaster", "ENV_Plaster_OffWhite" }, { "MI_WoodTrim", "ENV_Trim_White" } };
            Tiles(root, "Floor_Brick", x - 1f, x + 3f, back, -0.3f, 0.01f, null);
            var ceil = EnvKit.Place("Floor_WoodDark", root, new Vector3(x, 2.95f, back / 2f), 0, new Vector3(1, 1, -back / 2f));
            ceil.transform.localRotation = Quaternion.Euler(180, 0, 0);
            for (int j = 0; j < depth / 2; j++)
            {
                EnvKit.Remap(EnvKit.Place("ENV_Wall_Plaster_Clean", root, new Vector3(x - 1f, 0, -1 - 2 * j), 90), white);
                EnvKit.Remap(EnvKit.Place("ENV_Wall_Plaster_Clean", root, new Vector3(x + 3f, 0, -1 - 2 * j), 270), white);
            }
            EnvKit.Place("Stair_Interior_Solid", root, new Vector3(x + 2f, 0, back + 4.4f), 0);
            var counter = EnvKit.Place("ENV_Counter_Shop", root, new Vector3(x - 0.3f, 0, back + 1.2f), 0, new Vector3(0.6f, 1f, 1f));
            counter.name = "ReceptionCounter";
            EnvKit.Place("ENV_Plant_Small", root, new Vector3(x - 0.6f, 0, -0.8f), 0);
            var lightGo = new GameObject("InteriorLight");
            lightGo.transform.SetParent(root, false);
            lightGo.transform.localPosition = new Vector3(x + 0.5f, 2.6f, back / 2f);
            var l = lightGo.AddComponent<Light>();
            l.type = LightType.Point;
            l.color = EnvKit.Hex("#E8B26A");
            l.intensity = 2f;
            l.range = 6f;
            l.shadows = LightShadows.None;
            return root;
        }

        /// <summary>Places a list of (module, x, y, z, rotY) entries — small authored clusters (market stall, port
        /// props, furniture) described as data in units.json.</summary>
        public static Transform Cluster(Transform parent, string name, IEnumerable<(string module, Vector3 pos, float rot)> parts)
        {
            var root = EnvKit.Group(parent, name);
            foreach (var p in parts) EnvKit.Place(p.module, root, p.pos, p.rot);
            return root;
        }
    }
}

using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// Street life pass: the objects whose only job is to prove people use the street — lamps, bins, bicycles left
    /// against walls, rubbish by doors, goods outside shops, a bar terrace, parked vans that occlude a facade, street
    /// signs and name plates. Runs after buildings and ground, reads the facades (bay codes and THR_* thresholds) and
    /// keeps door lanes and the carriageway centre clear. Density follows the street hierarchy profile. Deterministic.
    /// Segment frame: x along the street, south facade line z = 0, north facade line z = width.
    /// </summary>
    public static class EnvLife
    {
        class Frontage
        {
            public float x;
            public char code;
            public bool north;
        }

        public static void DressSegment(Transform seg, string style, float length, float width, float pavement, float datum,
                                        IEnumerable<GameObject> buildings, int seed, bool vehicles = true)
        {
            var root = EnvKit.Group(seg, "Life");
            var rng = new System.Random(seed * 977 + 13);
            bool kerbed = EnvTemplates.IsKerbed(style);
            float p = kerbed ? pavement : 0f;
            var bays = new List<Frontage>();
            var thresholds = new List<(float x, bool north)>();
            foreach (var b in buildings)
            {
                bool north = Vector3.Dot(b.transform.forward, seg.forward * -1f) > 0.5f || seg.InverseTransformPoint(b.transform.position).z > width * 0.5f;
                var f0 = b.transform.Find("Front/F0");
                if (f0)
                    foreach (Transform slot in f0)
                        bays.Add(new Frontage { x = seg.InverseTransformPoint(slot.position).x, code = slot.name[0], north = north });
                foreach (var t in b.GetComponentsInChildren<Transform>().Where(t => t.name.StartsWith("THR_")))
                    thresholds.Add((seg.InverseTransformPoint(t.position).x, north));
            }
            bool Clear(float x, bool north, float r = 1.1f) => !thresholds.Any(t => t.north == north && Mathf.Abs(t.x - x) < r);
            Vector3 At(float x, bool north, float d, float y = 0) => new Vector3(x, datum + y, north ? width - d : d);
            float Face(bool north) => north ? 180f : 0f;

            // street lighting on kerbed streets: alternate sides every ~14 m on the pavement edge
            if (kerbed)
            {
                bool north = false;
                for (float x = 5f; x < length - 2f; x += 14f, north = !north)
                    if (Clear(x, north, 1.5f)) EnvKit.Place("ENV_Lamp_Post", root, At(x, north, p - 0.35f), Face(north));
                for (float x = 11f; x < length - 2f; x += 19f)
                {
                    bool n2 = rng.NextDouble() < 0.5;
                    if (Clear(x, n2)) EnvKit.Place("ENV_Bin_Street", root, At(x, n2, p - 0.3f), Face(n2) + 180);
                }
            }
            else if (style == "core")
            {
                // shared-surface core: light comes from wall lanterns; bins stand against the facades
                for (float x = 7f; x < length - 2f; x += 17f)
                {
                    bool n2 = rng.NextDouble() < 0.5;
                    if (Clear(x, n2)) EnvKit.Place("ENV_Bin_Street", root, At(x, n2, 0.35f), Face(n2) + 180);
                }
            }

            bool terraceDone = false;
            foreach (var f in bays)
            {
                float x = f.x;
                switch (f.code)
                {
                    case 'S':
                    case 'E':
                        if (rng.NextDouble() < 0.45 && Clear(x + 0.55f, f.north, 0.9f))
                        {
                            bool fruit = rng.NextDouble() < 0.5;
                            EnvKit.Place(fruit ? "ENV_Prop_FarmCrate_Apple" : "ENV_Box_Cardboard", root, At(x + 0.55f, f.north, 0.45f), Face(f.north) + rng.Next(-10, 10));
                            EnvKit.Place(fruit ? "ENV_Prop_FarmCrate_Carrot" : "ENV_Box_Cardboard", root, At(x - 0.35f, f.north, 0.45f), Face(f.north) + rng.Next(-12, 12));
                        }
                        break;
                    case 'P':
                        if (rng.NextDouble() < 0.2 && Clear(x, f.north, 1.3f))
                            EnvKit.Place("ENV_Bicycle", root, At(x, f.north, 0.32f), 90 + rng.Next(-6, 6));
                        break;
                    case 'D':
                    case 'A':
                    case 'V':
                        if (rng.NextDouble() < 0.2)
                            EnvKit.Place("ENV_Trash_Bags", root, At(x + 1.05f, f.north, 0.35f), rng.Next(360));
                        break;
                    case 'e':
                        if (!terraceDone && kerbed && p >= 1.7f)
                        {
                            // bar/shop terrace on the outer half of the pavement, door lane left free
                            float tx = x + 1.6f;
                            var d = p - 0.5f;
                            EnvKit.Place("ENV_Cafe_Table", root, At(tx, f.north, d), 0);
                            EnvKit.Place("ENV_Cafe_Chair", root, At(tx - 0.55f, f.north, d), 90);
                            EnvKit.Place("ENV_Cafe_Chair", root, At(tx + 0.55f, f.north, d), 270);
                            EnvKit.Place("ENV_Parasol", root, At(tx, f.north, d), 0, Vector3.one * 0.85f);
                            terraceDone = true;
                        }
                        break;
                }
            }

            // parked vehicles on main/secondary streets: against the kerb, away from thresholds; they occlude facades
            if (vehicles && kerbed)
            {
                var kinds = style == "main" ? new[] { "ENV_Vehicle_Van", "ENV_Vehicle_Car" } : new[] { "ENV_Vehicle_Car" };
                var paints = new[] { "ENV_Paint_White", "ENV_Paint_Red", "ENV_Paint_Blue", "ENV_Paint_Green" };
                for (int k = 0; k < kinds.Length; k++)
                {
                    bool north = k % 2 == 1;
                    for (int attempt = 0; attempt < 8; attempt++)
                    {
                        float x = length * (0.25f + 0.5f * (float)rng.NextDouble());
                        if (!Clear(x, north, 3.0f)) continue;
                        var v = EnvKit.Place(kinds[k], root, new Vector3(x, 0, north ? width - p - 0.95f : p + 0.95f), north ? 270 : 90);
                        var src = kinds[k] == "ENV_Vehicle_Van" ? "ENV_Paint_White" : "ENV_Paint_Red";
                        EnvKit.Remap(v, new Dictionary<string, string> { { src, paints[rng.Next(paints.Length)] } });
                        break;
                    }
                }
            }

            // signage: a street-name plate at the start of each facade line, a no-entry sign at the end of secondaries
            foreach (var north in new[] { false, true })
            {
                var first = bays.Where(b => b.north == north).OrderBy(b => b.x).FirstOrDefault();
                if (first != null)
                    EnvKit.Place("ENV_Street_Name_Plate", root, At(first.x - 0.4f, north, 0f, 3.35f), Face(north));
            }
            if (style == "secondary")
                EnvKit.Place("ENV_Sign_NoEntry", root, At(length - 0.6f, false, p - 0.3f), -90);
            if (style == "lane" || style == "pedestrian")
            {
                EnvKit.Place("ENV_Bollard_Street", root, new Vector3(0.4f, datum, width * 0.3f), 0);
                EnvKit.Place("ENV_Bollard_Street", root, new Vector3(0.4f, datum, width * 0.7f), 0);
            }
        }
    }
}

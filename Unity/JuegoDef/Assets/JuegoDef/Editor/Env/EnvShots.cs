using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEngine;

namespace JuegoDef.Env
{
    /// <summary>
    /// Fixed review viewpoints for a district (Env/Specs/districts/&lt;id&gt;.shots.json), so every iteration is judged
    /// from the same eye-level and aerial views (before/after, owner reviews). A shot is street-relative
    /// (<c>street</c>, <c>from</c>, <c>look</c>/<c>to</c>, <c>side</c>, <c>up</c>) or absolute (<c>eye</c>, <c>at</c>).
    /// Operator: <c>EnvShots.Capture("ENV01_Casco_District", "Docs/evidence/.../shots/after")</c>.
    /// </summary>
    public static class EnvShots
    {
        public static string Capture(string districtId, string outFolder, string only = null, int width = 1600, int height = 900)
        {
            var doc = JObject.Parse(EnvKit.ReadText($"{EnvDistrict.DistrictSpecs}/{districtId}.shots.json"));
            var want = string.IsNullOrEmpty(only) ? null : new HashSet<string>(only.Split(','));
            var done = new List<string>();
            foreach (JObject s in (JArray)doc["shots"])
            {
                var name = (string)s["name"];
                if (want != null && !want.Contains(name)) continue;
                Vector3 eye, at;
                if (s["eye"] is JArray e)
                {
                    eye = V(e);
                    at = V((JArray)s["at"]);
                }
                else
                {
                    var street = (string)s["street"];
                    eye = EnvDistrict.StreetPoint(street, (float)s["from"]) + Vector3.up * ((float?)s["up"] ?? 1.7f);
                    at = EnvDistrict.StreetPoint((string)s["look"] ?? street, (float)s["to"]) + Vector3.up * ((float?)s["lookUp"] ?? 2.0f);
                    var d = at - eye;
                    d.y = 0;
                    eye += new Vector3(-d.z, 0, d.x).normalized * ((float?)s["side"] ?? 0f);
                }
                EnvPreview.Capture($"{outFolder}/{name}.jpg", eye, at, (float?)s["fov"] ?? 60f, width, height);
                done.Add(name);
            }
            return $"JD_SHOTS {done.Count} -> {outFolder}: {string.Join(",", done)}";
        }

        static Vector3 V(JArray a) => new Vector3((float)a[0], (float)a[1], (float)a[2]);
    }
}

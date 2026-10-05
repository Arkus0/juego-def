using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace JuegoDef.EditorTools
{
    public static class SemanticEditHonda01
    {
        const string ScenePath = "Assets/JuegoDef/Scenes/ENV/ENV01_AUTHORED.unity";

        [MenuItem("JuegoDef/Semantic Edit Honda/1 Snapshot")]
        public static void Snapshot() => Run(apply: false);

        [MenuItem("JuegoDef/Semantic Edit Honda/2 Apply")]
        public static void Apply() => Run(apply: true);

        static void Run(bool apply)
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode)
            {
                Debug.LogError("SemanticEditHonda01: Edit mode only.");
                return;
            }

            var root = RepoRoot();
            var dir = Path.Combine(root, "Experiments", "SemanticEditHonda01");
            Directory.CreateDirectory(dir);
            var op = ReadOp(Path.Combine(dir, "operation.json"));
            var scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var matches = Find(scene, op.NameContains);
            if (matches.Count != 1)
            {
                Write(Path.Combine(dir, "result.json"), Result(op.NameContains, false, false, "", "", -1, "FAIL", "matches=" + matches.Count));
                Debug.LogError("SemanticEditHonda01 FAIL matches=" + matches.Count);
                return;
            }

            var target = matches[0];
            var before = Capture(scene, target);
            Write(Path.Combine(dir, "before.json"), before.Json);
            if (!apply)
            {
                Debug.Log("SemanticEditHonda01 snapshot " + before.Path + " hash=" + before.Hash);
                return;
            }

            if (!op.PassageSet)
            {
                Write(Path.Combine(dir, "result.json"), Result(before.Path, false, false, before.Hash, before.Hash, 0, "FAIL", "passageAabb is zero; set the corridor before apply"));
                return;
            }

            Undo.RecordObject(target.transform, "SemanticEditHonda01 move");
            target.transform.position += op.Offset;
            EditorUtility.SetDirty(target);
            var after = Capture(scene, target);
            Write(Path.Combine(dir, "after.json"), after.Json);
            var moved = target.transform.position != before.Position;
            var clear = !Intersects(target, op.Passage);
            var same = before.Hash == after.Hash && before.Count == after.Count;
            var unintended = same ? 0 : 1;
            var pass = moved && clear && same;
            Write(Path.Combine(dir, "result.json"), Result(before.Path, moved, clear, before.Hash, after.Hash, unintended, pass ? "PASS" : "FAIL", pass ? "" : "move, passage, or preservation failed"));
            Debug.Log("SemanticEditHonda01 " + (pass ? "PASS" : "FAIL") + " hashSame=" + same + " clear=" + clear);
        }

        static CaptureResult Capture(Scene scene, GameObject target)
        {
            var rows = new List<string>();
            foreach (var root in scene.GetRootGameObjects())
                Walk(root.transform, target.transform, rows);
            rows.Sort(StringComparer.Ordinal);
            var body = string.Join("\n", rows);
            var hash = Sha(body);
            var json = "{\n  \"target\": " + Q(PathOf(target.transform)) +
                       ",\n  \"position\": " + Vec(target.transform.position) +
                       ",\n  \"count\": " + rows.Count +
                       ",\n  \"preservationHash\": " + Q(hash) + "\n}";
            return new CaptureResult(PathOf(target.transform), target.transform.position, rows.Count, hash, json);
        }

        static void Walk(Transform node, Transform target, List<string> rows)
        {
            if (node != target)
            {
                var source = PrefabUtility.GetCorrespondingObjectFromSource(node.gameObject);
                var path = source == null ? "" : AssetDatabase.GetAssetPath(source);
                var p = node.localPosition;
                var r = node.localEulerAngles;
                var s = node.localScale;
                rows.Add(PathOf(node) + "\t" + path + "\t" + F(p.x) + "," + F(p.y) + "," + F(p.z) + "\t" + F(r.x) + "," + F(r.y) + "," + F(r.z) + "\t" + F(s.x) + "," + F(s.y) + "," + F(s.z));
            }
            for (var i = 0; i < node.childCount; i++)
                Walk(node.GetChild(i), target, rows);
        }

        static List<GameObject> Find(Scene scene, string token)
        {
            var found = new List<GameObject>();
            foreach (var root in scene.GetRootGameObjects())
                Find(root.transform, token, found);
            return found;
        }

        static void Find(Transform node, string token, List<GameObject> found)
        {
            if (node.name.IndexOf(token, StringComparison.OrdinalIgnoreCase) >= 0)
                found.Add(node.gameObject);
            for (var i = 0; i < node.childCount; i++)
                Find(node.GetChild(i), token, found);
        }

        static bool Intersects(GameObject target, Bounds passage)
        {
            var renderers = target.GetComponentsInChildren<Renderer>();
            if (renderers.Length == 0)
                return passage.Contains(target.transform.position);
            var bounds = renderers[0].bounds;
            for (var i = 1; i < renderers.Length; i++)
                bounds.Encapsulate(renderers[i].bounds);
            return bounds.Intersects(passage);
        }

        static Op ReadOp(string path)
        {
            var text = File.ReadAllText(path);
            return new Op(
                Between(text, "\"nameContains\"", ","),
                ReadVec(text, "offset"),
                ReadBounds(text),
                !text.Contains("\"min\": [0, 0, 0]") || !text.Contains("\"max\": [0, 0, 0]"));
        }

        static Bounds ReadBounds(string text)
        {
            var min = ReadVec(text, "min");
            var max = ReadVec(text, "max");
            var bounds = new Bounds();
            bounds.SetMinMax(min, max);
            return bounds;
        }

        static Vector3 ReadVec(string text, string key)
        {
            var token = "\"" + key + "\"";
            var at = text.IndexOf(token, StringComparison.Ordinal);
            var open = text.IndexOf('[', at);
            var close = text.IndexOf(']', open);
            var parts = text.Substring(open + 1, close - open - 1).Split(',');
            return new Vector3(float.Parse(parts[0], CultureInfo.InvariantCulture), float.Parse(parts[1], CultureInfo.InvariantCulture), float.Parse(parts[2], CultureInfo.InvariantCulture));
        }

        static string Between(string text, string key, string end)
        {
            var at = text.IndexOf(key, StringComparison.Ordinal);
            var q1 = text.IndexOf('"', text.IndexOf(':', at) + 1);
            var q2 = text.IndexOf('"', q1 + 1);
            return text.Substring(q1 + 1, q2 - q1 - 1);
        }

        static string Result(string target, bool moved, bool clear, string before, string after, int unintended, string result, string reason)
        {
            return "{\n  \"target\": " + Q(target) +
                   ",\n  \"operation\": \"move\"" +
                   ",\n  \"targetChanged\": " + (moved ? "true" : "false") +
                   ",\n  \"passageClear\": " + (clear ? "true" : "false") +
                   ",\n  \"preservationHashBefore\": " + Q(before) +
                   ",\n  \"preservationHashAfter\": " + Q(after) +
                   ",\n  \"unintendedChanges\": " + unintended +
                   ",\n  \"result\": " + Q(result) +
                   ",\n  \"reason\": " + Q(reason) + "\n}";
        }

        static string RepoRoot() => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", ".."));
        static string PathOf(Transform node) => AnimationUtility.CalculateTransformPath(node, null);
        static string F(float v) => v.ToString("0.####", CultureInfo.InvariantCulture);
        static string Vec(Vector3 v) => "[" + F(v.x) + ", " + F(v.y) + ", " + F(v.z) + "]";
        static string Q(string v) => "\"" + (v ?? "").Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
        static string Sha(string body)
        {
            using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(Encoding.UTF8.GetBytes(body))).Replace("-", "").ToLowerInvariant();
        }

        static void Write(string path, string text) => File.WriteAllText(path, text);

        struct Op
        {
            public Op(string name, Vector3 offset, Bounds passage, bool passageSet)
            {
                NameContains = name;
                Offset = offset;
                Passage = passage;
                PassageSet = passageSet;
            }
            public string NameContains;
            public Vector3 Offset;
            public Bounds Passage;
            public bool PassageSet;
        }

        struct CaptureResult
        {
            public CaptureResult(string path, Vector3 position, int count, string hash, string json)
            {
                Path = path;
                Position = position;
                Count = count;
                Hash = hash;
                Json = json;
            }
            public string Path;
            public Vector3 Position;
            public int Count;
            public string Hash;
            public string Json;
        }
    }
}

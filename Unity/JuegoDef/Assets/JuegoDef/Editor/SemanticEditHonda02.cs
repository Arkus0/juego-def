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
    public static class SemanticEditHonda02
    {
        const string ScenePath = "Assets/JuegoDef/Scenes/ENV/ENV01_AUTHORED.unity";

        [MenuItem("JuegoDef/Semantic Edit Honda/02 Snapshot")]
        public static void Snapshot() => Run(false);

        [MenuItem("JuegoDef/Semantic Edit Honda/02 Apply")]
        public static void Apply() => Run(true);

        static void Run(bool apply)
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode)
            {
                Debug.LogError("SemanticEditHonda02: Edit mode only.");
                return;
            }

            var dir = Path.Combine(RepoRoot(), "Experiments", "SemanticEditHonda02");
            Directory.CreateDirectory(dir);
            var prior = Path.Combine(RepoRoot(), "Experiments", "SemanticEditHonda01", "result.json");
            if (apply && (!File.Exists(prior) || File.ReadAllText(prior).IndexOf("\"result\": \"PASS\"", StringComparison.Ordinal) < 0))
            {
                Write(Path.Combine(dir, "result.json"), Result("", "", false, false, "", "", 1, "FAIL", "Honda-00 is not PASS"));
                return;
            }

            var op = ReadOp(Path.Combine(dir, "operation.json"));
            var scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var doors = Find(scene, op.TargetToken);
            var locked = Find(scene, op.LockedToken);
            if (doors.Count != 1 || locked.Count != 1)
            {
                Write(Path.Combine(dir, "result.json"), Result(op.TargetToken, op.LockedToken, false, false, "", "", -1, "FAIL", "doors=" + doors.Count + " locked=" + locked.Count));
                Debug.LogError("SemanticEditHonda02 FAIL doors=" + doors.Count + " locked=" + locked.Count);
                return;
            }

            var door = doors[0];
            var bakery = locked[0];
            if (door == bakery || door.transform.IsChildOf(bakery.transform))
            {
                Write(Path.Combine(dir, "result.json"), Result(PathOf(door.transform), PathOf(bakery.transform), false, true, "", "", 1, "FAIL", "entrance is the locked bakery or parented under it"));
                return;
            }

            var before = Capture(scene, door);
            var bakeryBefore = Row(bakery.transform);
            Write(Path.Combine(dir, "before.json"), before.Json);
            if (!apply)
            {
                Debug.Log("SemanticEditHonda02 snapshot door=" + before.Path + " bakery=" + PathOf(bakery.transform));
                return;
            }

            Undo.RecordObject(door.transform, "SemanticEditHonda02 setback");
            door.transform.localPosition += op.LocalOffset;
            EditorUtility.SetDirty(door);
            var after = Capture(scene, door);
            Write(Path.Combine(dir, "after.json"), after.Json);
            var moved = door.transform.localPosition != before.LocalPosition;
            var bakerySame = Row(bakery.transform) == bakeryBefore;
            var same = before.Hash == after.Hash && before.Count == after.Count && bakerySame;
            var pass = moved && bakerySame && same;
            Write(Path.Combine(dir, "result.json"), Result(before.Path, PathOf(bakery.transform), moved, bakerySame, before.Hash, after.Hash, same ? 0 : 1, pass ? "PASS" : "FAIL", pass ? "" : "setback, bakery lock, or preservation failed"));
            Debug.Log("SemanticEditHonda02 " + (pass ? "PASS" : "FAIL"));
        }

        static CaptureResult Capture(Scene scene, GameObject target)
        {
            var rows = new List<string>();
            foreach (var root in scene.GetRootGameObjects())
                Walk(root.transform, target.transform, rows);
            rows.Sort(StringComparer.Ordinal);
            var hash = Sha(string.Join("\n", rows));
            var json = "{\n  \"target\": " + Q(PathOf(target.transform)) +
                       ",\n  \"localPosition\": " + Vec(target.transform.localPosition) +
                       ",\n  \"count\": " + rows.Count +
                       ",\n  \"preservationHash\": " + Q(hash) + "\n}";
            return new CaptureResult(PathOf(target.transform), target.transform.localPosition, rows.Count, hash, json);
        }

        static void Walk(Transform node, Transform target, List<string> rows)
        {
            if (node != target)
                rows.Add(Row(node));
            for (var i = 0; i < node.childCount; i++)
                Walk(node.GetChild(i), target, rows);
        }

        static string Row(Transform node)
        {
            var source = PrefabUtility.GetCorrespondingObjectFromSource(node.gameObject);
            var path = source == null ? "" : AssetDatabase.GetAssetPath(source);
            var p = node.localPosition;
            var r = node.localEulerAngles;
            var s = node.localScale;
            return PathOf(node) + "\t" + path + "\t" + F(p.x) + "," + F(p.y) + "," + F(p.z) + "\t" + F(r.x) + "," + F(r.y) + "," + F(r.z) + "\t" + F(s.x) + "," + F(s.y) + "," + F(s.z);
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

        static Op ReadOp(string path)
        {
            var text = File.ReadAllText(path);
            return new Op(Between(text, "targetNameContains"), Between(text, "lockedNameContains"), ReadVec(text, "localOffset"));
        }

        static Vector3 ReadVec(string text, string key)
        {
            var at = text.IndexOf("\"" + key + "\"", StringComparison.Ordinal);
            var open = text.IndexOf('[', at);
            var close = text.IndexOf(']', open);
            var parts = text.Substring(open + 1, close - open - 1).Split(',');
            return new Vector3(float.Parse(parts[0], CultureInfo.InvariantCulture), float.Parse(parts[1], CultureInfo.InvariantCulture), float.Parse(parts[2], CultureInfo.InvariantCulture));
        }

        static string Between(string text, string key)
        {
            var at = text.IndexOf("\"" + key + "\"", StringComparison.Ordinal);
            var q1 = text.IndexOf('"', text.IndexOf(':', at) + 1);
            var q2 = text.IndexOf('"', q1 + 1);
            return text.Substring(q1 + 1, q2 - q1 - 1);
        }

        static string Result(string target, string locked, bool moved, bool bakerySame, string before, string after, int unintended, string result, string reason)
        {
            return "{\n  \"target\": " + Q(target) +
                   ",\n  \"locked\": " + Q(locked) +
                   ",\n  \"operation\": \"setback-local\"" +
                   ",\n  \"targetChanged\": " + (moved ? "true" : "false") +
                   ",\n  \"bakeryUnchanged\": " + (bakerySame ? "true" : "false") +
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
            public Op(string target, string locked, Vector3 offset)
            {
                TargetToken = target;
                LockedToken = locked;
                LocalOffset = offset;
            }
            public string TargetToken;
            public string LockedToken;
            public Vector3 LocalOffset;
        }

        struct CaptureResult
        {
            public CaptureResult(string path, Vector3 localPosition, int count, string hash, string json)
            {
                Path = path;
                LocalPosition = localPosition;
                Count = count;
                Hash = hash;
                Json = json;
            }
            public string Path;
            public Vector3 LocalPosition;
            public int Count;
            public string Hash;
            public string Json;
        }
    }
}

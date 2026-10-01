using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace JuegoDef.Env
{
    // Workspace-local durable journal. A scene also owns referenced generated assets:
    // recovering its YAML alone cannot recover a failed ground/lighting rebuild.
    public static class EnvRebuildTransaction
    {
        static string Root => Path.GetFullPath(".");
        static string Journal => Path.Combine(LayoutReceipt.LocalDirectory, "transaction.json");
        static string Backup => Path.Combine(LayoutReceipt.LocalDirectory, "transaction");
        public static bool Pending => File.Exists(Journal);
        static readonly string[] AssetRoots = { "Assets/JuegoDef/Derived/ENV", "Assets/JuegoDef/Rendering" };
        static string Relative(string p) => Path.GetRelativePath(Root, Path.GetFullPath(p)).Replace('\\', '/');
        static string Safe(string p)
        {
            var full = Path.GetFullPath(Path.Combine(Root, p));
            if (!full.StartsWith(Root + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) throw new IOException("Snapshot fuera del workspace");
            return full;
        }
        static List<string> Files(string id)
        {
            var paths = AssetRoots.Where(Directory.Exists).SelectMany(r => Directory.GetFiles(r, "*", SearchOption.AllDirectories)).Select(Relative).ToList();
            foreach (var p in new[] { $"{EnvDistrict.DistrictSpecs}/{id}.json", $"{EnvDistrict.DistrictSpecs}/{id}.generation.json", LayoutReceipt.ScenePath(id), LayoutReceipt.ScenePath(id) + ".meta", LayoutReceipt.PathOf(id) })
                paths.Add(Relative(p)); // absence must also be recovered
            return paths.Distinct().ToList();
        }
        public static void Open(string id, bool rowsOnly)
        {
            if (Pending) throw new IOException("Hay una recuperación pendiente; no se puede iniciar otro rebuild");
            Directory.CreateDirectory(Backup);
            var files = new JObject();
            foreach (var p in Files(id))
            {
                if (!File.Exists(p)) { files[p] = JValue.CreateNull(); continue; }
                var dest = Path.Combine(Backup, p); Directory.CreateDirectory(Path.GetDirectoryName(dest));
                File.Copy(p, dest, true); files[p] = OsmPin.Sha256File(dest);
            }
            var doc = new JObject { ["workspace"] = Root, ["id"] = id, ["rowsOnly"] = rowsOnly, ["previousScene"] = UnityEngine.SceneManagement.SceneManager.GetActiveScene().path, ["directories"] = new JArray(AssetRoots.Where(Directory.Exists).SelectMany(r => Directory.GetDirectories(r, "*", SearchOption.AllDirectories)).Select(Relative)), ["files"] = files };
            File.WriteAllText(Journal + ".tmp", doc.ToString()); File.Move(Journal + ".tmp", Journal);
        }
        public static void Commit()
        {
            // The journal deletion is the commit marker; previous snapshots remain for inspection.
            File.Delete(Journal);
        }
        public static void Restore()
        {
            if (!Pending) return;
            var doc = JObject.Parse(File.ReadAllText(Journal));
            if ((string)doc["workspace"] != Root) throw new IOException("El journal pertenece a otro workspace");
            var files = (JObject)doc["files"];
            // Verify every snapshot BEFORE restoring anything; retain the journal on any error.
            foreach (var f in files.Properties().Where(f => f.Value.Type != JTokenType.Null))
            {
                Safe(f.Name);
                var src = Path.Combine(Backup, f.Name);
                if (!File.Exists(src) || OsmPin.Sha256File(src) != (string)f.Value) throw new IOException("Snapshot incompleto: " + f.Name);
            }
            AssetDatabase.DisallowAutoRefresh();
            try
            {
                foreach (var p in Files((string)doc["id"]).Union(files.Properties().Select(f => f.Name)).ToList())
                {
                    var dest = Safe(p); var token = files[p];
                    if (token == null || token.Type == JTokenType.Null) { if (File.Exists(dest)) File.Delete(dest); }
                    else { Directory.CreateDirectory(Path.GetDirectoryName(dest)); File.Copy(Path.Combine(Backup, p), dest, true); }
                }
                var previousDirectories = new HashSet<string>(((JArray)doc["directories"]).Select(x => (string)x));
                foreach(var d in AssetRoots.Where(Directory.Exists).SelectMany(r=>Directory.GetDirectories(r,"*",SearchOption.AllDirectories)).OrderByDescending(x=>x.Length))
                    if(!previousDirectories.Contains(Relative(d)) && !Directory.EnumerateFileSystemEntries(d).Any()) Directory.Delete(Safe(d),false);
            }
            finally { AssetDatabase.AllowAutoRefresh(); }
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport | ImportAssetOptions.ForceUpdate);
            foreach (var f in files.Properties())
                if (f.Value.Type != JTokenType.Null && OsmPin.Sha256File(Safe(f.Name)) != (string)f.Value) throw new IOException("La recuperación no conservó bytes: " + f.Name);
            string previous = (string)doc["previousScene"];
            string scene = (bool)doc["rowsOnly"] ? LayoutReceipt.ScenePath((string)doc["id"]) : previous;
            if (!string.IsNullOrEmpty(scene) && File.Exists(Safe(scene))) EditorSceneManager.OpenScene(scene);
            else EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
            EnvKit.ClearCache(); EnvDistrict.ResetState(); EnvPolish.Auto.Clear();
            Commit();
        }
    }

    public static class LayoutReceipt
    {
        public static string WorkspaceKey => OsmPin.Sha256Text(Application.dataPath.ToLowerInvariant()).Substring(0, 16);
        public static string LocalDirectory => Path.GetFullPath("Library/ENVDirector");
        public static string PathOf(string id) => Path.Combine(LocalDirectory, id + ".build.json");
        public static string ScenePath(string id) => $"Assets/JuegoDef/Scenes/ENV/{id}.unity";
        public static string GenerationPath(string id) => $"{EnvDistrict.DistrictSpecs}/{id}.generation.json";
        static string Hash(string path) => File.Exists(path) ? OsmPin.Sha256File(path) : "";
        public static string CodeHash() => OsmPin.Sha256Text(string.Join("\n", Directory.GetFiles("Assets/JuegoDef/Editor/Env", "*.cs").OrderBy(x => x, StringComparer.Ordinal).Select(x => Path.GetFileName(x) + ":" + Hash(x))));
        public static string RecipeHash()
        {
            var files = Directory.GetFiles("Assets/JuegoDef/Editor/Env", "*.cs").Concat(Directory.GetFiles("Assets/JuegoDef/Env", "*.json", SearchOption.AllDirectories).Where(x => !x.Contains("districts")))
                .Concat(new[] { Path.GetFullPath("../../Tools/env_district_skeleton.py"), Path.GetFullPath("../../Tools/env_authoring.py") }).OrderBy(x => x, StringComparer.Ordinal);
            return OsmPin.Sha256Text(string.Join("\n", files.Select(x => Path.GetFileName(x) + ":" + Hash(x))));
        }
        static JObject Inputs(string id) => new JObject { ["trace"] = Hash($"{EnvDistrict.DistrictSpecs}/{id}.trace.json"), ["spec"] = Hash($"{EnvDistrict.DistrictSpecs}/{id}.json"), ["authoring"] = Hash($"{EnvDistrict.DistrictSpecs}/{id}.authoring.json"), ["polish"] = Hash($"{EnvDistrict.DistrictSpecs}/{id}.polish.json"), ["osm"] = OsmPin.PinnedSha(id), ["recipe"] = RecipeHash() };
        public static void CheckSpec(string id)
        {
            if (!File.Exists(GenerationPath(id))) throw new IOException("Falta la identidad de la spec aceptada; registrar sus correcciones upstream antes de reconstruir");
            var g = JObject.Parse(File.ReadAllText(GenerationPath(id)));
            if ((string)g["spec"] != Hash($"{EnvDistrict.DistrictSpecs}/{id}.json")) throw new IOException("La spec contiene cambios no registrados como inputs. Conserva esas correcciones en authoring antes de REBUILD");
        }
        public static void Record(string id)
        {
            if (!File.Exists(ScenePath(id))) throw new IOException("La escena reconstruida no se guardó");
            var inputs = Inputs(id);
            File.WriteAllText(GenerationPath(id), inputs.ToString()); AssetDatabase.ImportAsset(GenerationPath(id));
            inputs["scene"] = Hash(ScenePath(id)); Directory.CreateDirectory(LocalDirectory); File.WriteAllText(PathOf(id), inputs.ToString());
        }
        public static bool Matches(string id)
        {
            try { var r = JObject.Parse(File.ReadAllText(PathOf(id))); var inputs = Inputs(id); return inputs.Properties().All(p => JToken.DeepEquals(r[p.Name], p.Value)) && (string)r["scene"] == Hash(ScenePath(id)); }
            catch { return false; }
        }
        static double cacheAt;
        static string cachedId, cachedState;
        public static void Invalidate() { cacheAt = 0; }
        public static string State(string id, bool dirty)
        {
            if (dirty) return "PREVIEW · cambios sin guardar";
            if (cachedId != id || EditorApplication.timeSinceStartup - cacheAt > 1)
            {
                cachedId = id; cacheAt = EditorApplication.timeSinceStartup;
                cachedState = Matches(id) ? "RECONSTRUIDO · escena al día" : "GUARDADO · reconstrucción pendiente";
            }
            if (cachedState.StartsWith("RECONSTRUIDO") && UnityEngine.SceneManagement.SceneManager.GetActiveScene().path != ScenePath(id)) return "RECONSTRUIDO · abre el distrito para inspeccionarlo";
            if (UnityEngine.SceneManagement.SceneManager.GetActiveScene().isDirty) return "GUARDADO · escena con cambios locales";
            return cachedState;
        }
    }
}

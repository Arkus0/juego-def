using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UnityEditor;
using Debug = UnityEngine.Debug;
using UnityEngine;

namespace JuegoDef.Env
{
    // -------------------------------------------------------------------- osm source pin

    /// <summary>Pinned identity of the OSM extract that feeds REBUILD (repair 2, FAIL review 5366743166). A per-district
    /// sidecar committed next to the district spec ({id}.osm.json) records the adopted SHA-256; LayoutRebuild.Start
    /// hashes the configured file and refuses to run on any mismatch, so upstream drift (a refetch or an overwrite at
    /// the same path) can never piggyback a trace edit. Identity is content, not path: same bytes at a new path is the
    /// same source; different bytes at the same path is a new source and needs the explicit Adopt action. The raw
    /// extract itself stays out of the repository (ODbL hygiene) — only its identity is committed.</summary>
    public static class OsmPin
    {
        public static string SidecarPath(string id) => $"{EnvDistrict.DistrictSpecs}/{id}.osm.json";

        /// <summary>SHA-256 of the file's raw bytes, lowercase hex.</summary>
        public static string Sha256File(string path)
        {
            using var sha = System.Security.Cryptography.SHA256.Create();
            using var fs = File.OpenRead(path);
            var hash = sha.ComputeHash(fs);
            var sb = new StringBuilder(hash.Length * 2);
            foreach (var b in hash) sb.Append(b.ToString("x2"));
            return sb.ToString();
        }

        /// <summary>The adopted sha256, "" when the district never adopted a source (REBUILD must refuse).</summary>
        public static string PinnedSha(string id)
        {
            var p = SidecarPath(id);
            if (!File.Exists(p)) return "";
            try { return JObject.Parse(File.ReadAllText(p))?["sha256"]?.Value<string>() ?? ""; }
            catch { return ""; }
        }

        /// <summary>The explicit adoption: records the current file's identity in the sidecar. The UI wraps this with an
        /// old/new confirmation dialog; operator/MCP evidence runs may call it directly — the returned receipt line (also
        /// logged) is the record of the identity transition.</summary>
        public static string Adopt(string id, string osmPath)
        {
            var old = PinnedSha(id);
            var sha = Sha256File(osmPath);
            var pin = new JObject
            {
                ["sha256"] = sha,
                ["bytes"] = new FileInfo(osmPath).Length,
                ["adoptedUtc"] = System.DateTime.UtcNow.ToString("yyyy-MM-dd'T'HH:mm:ss'Z'"),
                ["path"] = osmPath.Replace('\\', '/'),
            };
            File.WriteAllText(SidecarPath(id), pin.ToString(Formatting.Indented), new UTF8Encoding(false));
            AssetDatabase.ImportAsset(SidecarPath(id));
            var line = $"osm-adopt district={id} old={(old == "" ? "(none)" : Short(old))} new={sha} bytes={pin["bytes"]}";
            Debug.Log("JD_LAYOUT_REBUILD " + line);
            return line;
        }

        public static string Sha256Text(string value)
        {
            using var sha = System.Security.Cryptography.SHA256.Create();
            return string.Concat(sha.ComputeHash(Encoding.UTF8.GetBytes(value)).Select(b => b.ToString("x2")));
        }
        public static string Short(string sha) => sha.Length <= 16 ? sha : sha.Substring(0, 16) + "…";
    }

    // -------------------------------------------------------------------- rebuild pipeline

    /// <summary>Frame-driven runner for REBUILD: regenerates the district spec with the existing skeleton tool, diffs
    /// it against the current one and runs the complete district factory through EnvDistrict.Begin/BuildRows/Finish.
    /// Row chunks yield between assembly batches; ground/finishing can still take several seconds.
    /// The promote of the regenerated spec is transactional: every consent/environment precondition runs BEFORE the
    /// spec authority is touched, the previous spec AND the saved district scene are snapshotted outside Assets, and
    /// any cancel, exception or domain reload after promotion attempts verified rollback. A failed recovery retains
    /// the durable journal and blocks further authoring/rebuild until recovery succeeds.</summary>
    [UnityEditor.InitializeOnLoad]
    public static class LayoutRebuild
    {
        public enum Phase { None, Regen, Confirm, BeginPhase, RowsChunk, FinishPhase, Done, Failed }

        /// <summary>Operator/MCP evidence hook: injects a failure at this point of the next rebuild (after the spec was
        /// promoted) to prove the transaction rolls spec and scene back. Resets itself after firing.</summary>
        public enum DebugFailPoint { None, AfterPromote, MidChunk }
        public static DebugFailPoint DebugFailAt = DebugFailPoint.None;

        public static Phase phase = Phase.None;
        public static string status = "";
        public static float progress;
        public static readonly List<string> log = new List<string>();
        /// <summary>Operator/MCP runs set this to skip the impact confirmation dialog (the summary is still logged).</summary>
        public static bool AutoConfirm = false;

        // The workspace-local journal survives domain reloads and editor restarts.
        public static bool ForceFull;
        static readonly Dictionary<string,string> inputHashes = new Dictionary<string,string>();
        static string traceInput, osmInput, recipeAtStart;
        static readonly string CompiledCode = LayoutReceipt.CodeHash();
        static bool txOpen;                // spec promoted, transaction not yet committed/rolled back

        static LayoutRebuild()
        {
            EditorApplication.update += RecoverInterruptedTick;
        }

        static string districtId, projectRoot, repoRoot, traceAbs, specAbs, candidatePath, osmShaUsed;
        static Process proc;
        static readonly StringBuilder stdout = new StringBuilder(), stderr = new StringBuilder();
        static JObject currentSpec, candidateSpec;
        static SpecDiff diff;
        static int chunkCursor;
        static double startedAt;

        public static void Start(string id, string dataPath)
        {
            if (EnvRebuildTransaction.Pending) { phase = Phase.Failed; Status("Hay una recuperación pendiente; resuélvela antes de reconstruir"); return; }
            try { StartCore(id, dataPath); }
            catch (System.Exception ex) { Status("REBUILD bloqueado: " + ex.Message); Finish(Phase.Failed); }
        }
        static void StartCore(string id, string dataPath)
        {
            if (phase != Phase.None) return;
            if (EditorApplication.isCompiling || EditorApplication.isUpdating || EditorUtility.scriptCompilationFailed || LayoutReceipt.CodeHash() != CompiledCode) throw new System.InvalidOperationException("Unity debe terminar una compilación correcta de la receta antes de REBUILD");
            if (EditorApplication.isPlayingOrWillChangePlaymode) throw new System.InvalidOperationException("Sal de Play Mode antes de REBUILD");
            districtId = id;
            projectRoot = Path.GetFullPath(Path.Combine(dataPath, ".."));
            repoRoot = Path.GetFullPath(Path.Combine(projectRoot, "..", ".."));
            traceAbs = Path.Combine(projectRoot, EnvDistrict.DistrictSpecs.Replace('/', Path.DirectorySeparatorChar), id + ".trace.json");
            specAbs = Path.Combine(projectRoot, EnvDistrict.DistrictSpecs.Replace('/', Path.DirectorySeparatorChar), id + ".json");
            var osm = EditorPrefs.GetString($"JuegoDef.ENV.Layout.{id}.OsmPath", "");
            if (osm == "" || !File.Exists(osm))
            {
                phase = Phase.Failed;
                Status("falta el extracto OSM — elígeló con «elegir...» en la ventana");
                return;
            }
            // The source is pinned by CONTENT, not by path (repair 2, review 5366743166): hash the actual bytes and
            // compare against the adopted pin before anything runs, so a refetch/overwrite at the same path can never
            // enter a rebuild as silent upstream drift.
            LayoutReceipt.CheckSpec(id);
            var pinnedSha = OsmPin.PinnedSha(id);
            var osmSha = OsmPin.Sha256File(osm);
            if (pinnedSha == "")
            {
                phase = Phase.Failed;
                Status($"OSM sin adoptar: falta el pin {OsmPin.SidecarPath(id)} — usa «Adoptar OSM» en la ventana. Un REBUILD nunca adopta una fuente nueva por sí mismo.");
                return;
            }
            if (osmSha != pinnedSha)
            {
                phase = Phase.Failed;
                Status($"OSM CAMBIÓ respecto al pin — REBUILD bloqueado antes de regenerar nada:\n  pineado {OsmPin.Short(pinnedSha)}\n  actual  {OsmPin.Short(osmSha)}\nSi el cambio es intencionado (nuevo fetch), adopta la fuente con «Adoptar OSM»; si no, restaura el extracto pineado.");
                return;
            }
            osmShaUsed = osmSha;
            var run = Path.Combine(LayoutReceipt.LocalDirectory, "inputs", System.Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(run); inputHashes.Clear(); recipeAtStart = LayoutReceipt.RecipeHash();
            var polish = $"{EnvDistrict.DistrictSpecs}/{id}.polish.json";
            inputHashes[polish] = File.Exists(polish) ? OsmPin.Sha256File(polish) : "";
            foreach (var source in new[] { traceAbs, specAbs, OsmPin.SidecarPath(id), $"{EnvDistrict.DistrictSpecs}/{id}.authoring.json", LayoutReceipt.GenerationPath(id) })
            {
                if (!File.Exists(source)) throw new IOException("Falta un input reproducible: " + source);
                inputHashes[source] = OsmPin.Sha256File(source);
                if (source.EndsWith(".trace.json") || source.EndsWith(".authoring.json")) File.Copy(source, Path.Combine(run, Path.GetFileName(source)));
            }
            traceInput = Path.Combine(run, Path.GetFileName(traceAbs)); osmInput = Path.Combine(run, "osm.json");
            // Python reads ONLY these verified snapshots. Deny writes/replacement while copying OSM.
            using (var source = new FileStream(osm, FileMode.Open, FileAccess.Read, FileShare.Read))
            using (var dest = new FileStream(osmInput, FileMode.CreateNew, FileAccess.Write, FileShare.None)) source.CopyTo(dest);
            if (OsmPin.Sha256File(osmInput) != pinnedSha) throw new IOException("OSM cambió durante el snapshot");
            foreach (var original in inputHashes.Keys.Where(x => x.EndsWith(".trace.json") || x.EndsWith(".authoring.json")))
                if (OsmPin.Sha256File(Path.Combine(run, Path.GetFileName(original))) != inputHashes[original]) throw new IOException("Input cambió durante su snapshot");
            candidatePath = Path.Combine(run, "candidate.json");
            log.Clear();
            Status($"regenerando spec: python Tools/env_district_skeleton.py --trace {id}.trace.json");
            Status($"fuente OSM verificada contra el pin: sha256:{osmSha} ✓ ({new FileInfo(osm).Length} bytes)");
            phase = Phase.Regen;
            progress = 0.02f;
            startedAt = EditorApplication.timeSinceStartup;

            var psi = new ProcessStartInfo
            {
                FileName = "python",
                WorkingDirectory = repoRoot,
                Arguments = $"Tools/env_district_skeleton.py --trace \"{traceInput}\" --osm \"{osmInput}\" --out \"{candidatePath}\"",
                UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true, CreateNoWindow = true,
            };
            stdout.Clear(); stderr.Clear();
            proc = Process.Start(psi);
            proc.OutputDataReceived += (_, e) => { if (e.Data != null) lock (stdout) stdout.AppendLine(e.Data); };
            proc.ErrorDataReceived += (_, e) => { if (e.Data != null) lock (stderr) stderr.AppendLine(e.Data); };
            proc.BeginOutputReadLine();
            proc.BeginErrorReadLine();
            EditorApplication.update -= Tick;
            EditorApplication.update += Tick;
        }

        public static void Cancel(string why)
        {
            if (txOpen) { Rollback("cancelado: " + why); return; }
            if (proc is { HasExited: false }) { try { proc.Kill(); } catch { } }
            phase = Phase.None;
            Status("REBUILD cancelado: " + why);
            EditorApplication.update -= Tick;
        }

        // ---------------------------------------------------------------- transaction

        // Consent precedes any authority/scene mutation. FULL replaces the open
        // scene, so continuing from a dirty scene is always an explicit decision.
        static bool TxGate()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode) { Cancel("no se reconstruye en Play Mode"); return false; }
            var scene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            if (scene.isDirty && !EditorUtility.DisplayDialog("REBUILD · escena con cambios", "La reconstrucción completa sustituirá la escena abierta. Sus cambios sin guardar se descartarán si continúas.", "CONTINUAR", "Cancelar"))
            { Cancel("se conserva la escena con cambios"); return false; }
            return true;
        }

        static void VerifyInputs(bool promoted = false)
        {
            if (LayoutReceipt.RecipeHash() != recipeAtStart) throw new IOException("La receta cambió durante REBUILD");
            foreach (var kv in inputHashes)
                if (!(promoted && kv.Key == specAbs) && (File.Exists(kv.Key) ? OsmPin.Sha256File(kv.Key) : "") != kv.Value) throw new IOException("Input cambió durante REBUILD: " + Path.GetFileName(kv.Key));
            if (OsmPin.Sha256File(osmInput) != osmShaUsed) throw new IOException("Snapshot OSM cambió");
            if (promoted && !JToken.DeepEquals(JObject.Parse(File.ReadAllText(specAbs)), candidateSpec)) throw new IOException("Spec cambió durante REBUILD");
        }
        static void TxOpen()
        {
            VerifyInputs(); EnvRebuildTransaction.Open(districtId, false); txOpen = true;
            Status("TX abierta: spec, escena y assets generados protegidos");
        }
        static void CommitTx()
        {
            if (!txOpen) return;
            VerifyInputs(true); LayoutReceipt.Record(districtId);
            EnvRebuildTransaction.Commit(); txOpen = false; LayoutReceipt.Invalidate();
            Status("TX commit: inputs verificados, spec y escena guardadas");
        }
        static void Rollback(string why)
        {
            if (proc is { HasExited: false }) { try { proc.Kill(); } catch { } }
            try { EnvRebuildTransaction.Restore(); txOpen = false; Status("TX rollback: spec, escena y assets recuperados · " + why); }
            catch (System.Exception ex) { txOpen = false; Status("RECUPERACIÓN PENDIENTE: " + ex.Message + " · snapshots conservados en Library/ENVDirector"); }
            LayoutReceipt.Invalidate(); Finish(Phase.Failed);
        }
        public static void RetryRecovery() { Rollback("recuperación solicitada"); }
        static void RecoverInterruptedTick()
        {
            if (EditorApplication.isPlaying || EditorApplication.isCompiling || EditorApplication.isUpdating) return;
            EditorApplication.update -= RecoverInterruptedTick;
            if (EnvRebuildTransaction.Pending) Rollback("rebuild interrumpido por recarga/cierre");
        }

        static void Status(string s)
        {
            status = s;
            log.Add(s);
            Debug.Log("JD_LAYOUT_REBUILD " + s);
        }

        static void Tick()
        {
            try
            {
                switch (phase)
                {
                    case Phase.Regen:
                        progress = Mathf.Min(0.25f, 0.02f + (float)((EditorApplication.timeSinceStartup - startedAt) / 60.0));
                        if (proc == null || proc.HasExited)
                        {
                            if (proc == null || proc.ExitCode != 0)
                            {
                                Status($"FALLO regenerando spec (exit {proc?.ExitCode}):\n{stderr}");
                                Finish(Phase.Failed);
                            }
                            else { proc.WaitForExit(); OnRegenDone(); }
                        }
                        else if (EditorApplication.timeSinceStartup - startedAt > 240) Cancel("timeout del skeleton (>4 min)");
                        break;
                    case Phase.Confirm: break;   // waiting for the dialog answer (dialog opened on regen done)
                    case Phase.BeginPhase:
                        Debug.Log(EnvDistrict.Begin(districtId));
                        chunkCursor = 0;
                        phase = Phase.RowsChunk;
                        break;
                    case Phase.RowsChunk:
                    {
                        var rows = (JArray)currentSpec["rows"];
                        Debug.Log(EnvDistrict.BuildRows(chunkCursor, 8));
                        chunkCursor += 8;
                        if (DebugFailAt == DebugFailPoint.MidChunk) { DebugFailAt = DebugFailPoint.None; throw new System.InvalidOperationException("JD_LAYOUT_DEBUG_FAIL MidChunk"); }
                        progress = 0.3f + 0.6f * Mathf.Min(1f, (float)chunkCursor / rows.Count);
                        if (chunkCursor >= rows.Count) phase = Phase.FinishPhase;
                        break;
                    }
                    case Phase.FinishPhase:
                        Debug.Log(EnvDistrict.Finish());
                        progress = 1f;
                        CommitTx();
                        Status($"JD_LAYOUT_REBUILD district completo ({(int)(EditorApplication.timeSinceStartup - startedAt)} s)");
                        Finish(Phase.Done);
                        break;
                }
            }
            catch (System.Exception ex)
            {
                Debug.LogException(ex);
                if (txOpen) Rollback("FALLO: " + ex.Message);
                else { Status("FALLO: " + ex.Message + "\n" + ex.StackTrace); Finish(Phase.Failed); }
            }
        }

        // Compare the staged candidate; confirm the impact before promoting it.
        static void OnRegenDone()
        {
            VerifyInputs();
            candidateSpec = JObject.Parse(File.ReadAllText(candidatePath));
            var placementConflict = LayoutPlacement.Validate(candidateSpec);
            if (placementConflict != "") throw new System.IO.InvalidDataException(placementConflict);
            currentSpec = File.Exists(specAbs) ? JObject.Parse(EnvKit.ReadText($"{EnvDistrict.DistrictSpecs}/{districtId}.json")) : new JObject();
            diff = SpecDiff.Compute(currentSpec, candidateSpec);
            progress = 0.3f;

            // CASCO finishing queries physics across rows, river, furniture and props.
            // A spec-local diff does not prove scene-local effects: always run the complete factory.
            var visibleScene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            bool sceneReady = visibleScene.path == LayoutReceipt.ScenePath(districtId) && !visibleScene.isDirty && GameObject.Find(districtId) != null;
            if (diff.Empty && !ForceFull && sceneReady && LayoutReceipt.Matches(districtId))
            {
                Status("la spec ya refleja el trace — nada que reconstruir");
                Finish(Phase.Done);
                return;
            }
            string route = "DISTRICT COMPLETO";
            Status($"impacto: {diff.Summary()}\nruta: {route}");

            bool proceed = AutoConfirm;
            if (!proceed)
                proceed = EditorUtility.DisplayDialog("REBUILD — impacto de la regeneración",
                    $"El pipeline regeneró la spec desde el trace guardado.\n\n{diff.Summary()}\n\nRuta: {route}\n\n¿Aplicar la spec nueva y reconstruir?\n(transaccional: si algo falla, spec y escena se restauran)", "REBUILD", "Cancelar");
            if (!proceed)
            {
                Cancel("cancelado en el diálogo de impacto");
                return;
            }

            // Transaction gate: every precondition and consent runs BEFORE the spec authority is touched, so a "no"
            // leaves every byte as it was (the reviewer repro SAVE->REBUILD->accept->dirty->Cancel ends here, clean).
            if (!TxGate()) return;

            TxOpen();
            File.Copy(candidatePath, specAbs, true);
            AssetDatabase.ImportAsset($"{EnvDistrict.DistrictSpecs}/{districtId}.json");
            Status($"spec promovida — fuente OSM sha256:{osmShaUsed}");
            currentSpec = candidateSpec;
            EnvDistrict.ResetState();
            if (DebugFailAt == DebugFailPoint.AfterPromote) { DebugFailAt = DebugFailPoint.None; throw new System.InvalidOperationException("JD_LAYOUT_DEBUG_FAIL AfterPromote"); }

            phase = Phase.BeginPhase;
        }

        static void SaveSceneIfDistrict()
        {
            var scene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            if (scene.path != LayoutReceipt.ScenePath(districtId) || !UnityEditor.SceneManagement.EditorSceneManager.SaveScene(scene)) throw new IOException("No se guardó la escena reconstruida");
        }

        static void Finish(Phase end)
        {
            phase = end == Phase.Done ? Phase.None : end;
            if (end == Phase.Done) phase = Phase.None;
            progress = end == Phase.Done ? 1f : 0f;
            EditorApplication.update -= Tick;
            SceneView.RepaintAll();
        }

        public class SpecDiff
        {
            public List<string> otherChanged = new List<string>();   // geometry collections other than rows
            public List<string> rowIdsChanged = new List<string>();
            public int rowsAssignOnly, rowsGeometry, rowsAdded, rowsRemoved, rowsStateful;
            static readonly string[] AssignFields =
                { "palette", "seed", "ground", "upper", "solana", "surrounds", "gate", "escudo", "basement", "awning", "tall", "thin", "wall" };

            public bool Empty => otherChanged.Count == 0 && rowIdsChanged.Count == 0 && rowsAdded == 0 && rowsRemoved == 0;

            public string Summary()
            {
                var sb = new StringBuilder();
                sb.Append(otherChanged.Count > 0 ? "suelo/calles/plazas/río/etc.: CAMBIAN (" + string.Join(", ", otherChanged) + ")" : "suelo/calles/plazas/río/etc.: intactos");
                sb.Append($"\nfilas: {rowsGeometry} cambian geometría · {rowsAssignOnly} re-tiran asignación (paleta/seed...)");
                if (rowsAdded + rowsRemoved > 0) sb.Append($"\nfilas añadidas/eliminadas: +{rowsAdded}/-{rowsRemoved}");
                return sb.ToString();
            }

            public static SpecDiff Compute(JObject cur, JObject newSpec)
            {
                var d = new SpecDiff();
                foreach (var key in cur.Properties().Select(p => p.Name).Union(newSpec.Properties().Select(p => p.Name)).Where(k => k != "rows" && k != "report"))
                {
                    var a = cur[key]; var b = newSpec[key];
                    if (a == null && b == null) continue;
                    if (JToken.DeepEquals(a, b)) continue;
                    if (key == "ground" && a is JObject ga && b is JObject gb)
                    {
                        var zones = ga.Properties().Select(p => p.Name).Union(gb.Properties().Select(p => p.Name))
                            .Where(z => !JToken.DeepEquals(ga[z], gb[z])).Select(z => "suelo:" + z).ToList();
                        d.otherChanged.AddRange(zones);
                    }
                    else if (a is JArray aa && b is JArray ab && aa.Count > 0 && aa[0] is JObject && ((JObject)aa[0])["id"] != null)
                        d.otherChanged.Add(key);
                    else
                        d.otherChanged.Add(key);
                }

                var ra = ((JArray?)cur["rows"])?.Cast<JObject>().ToDictionary(r => (string)r["id"]) ?? new Dictionary<string, JObject>();
                var rb = ((JArray?)newSpec["rows"])?.Cast<JObject>().ToDictionary(r => (string)r["id"]) ?? new Dictionary<string, JObject>();
                d.rowsAdded = rb.Keys.Except(ra.Keys).Count();
                d.rowsRemoved = ra.Keys.Except(rb.Keys).Count();
                foreach (var rid in ra.Keys.Intersect(rb.Keys))
                {
                    if (JToken.DeepEquals(ra[rid], rb[rid])) continue;
                    d.rowIdsChanged.Add(rid);
                    // Business uniqueness and neighbour hue consume earlier plots. A raw
                    // row-count diff does not prove that seed/type/style changes are local.
                    var left=(JObject)ra[rid].DeepClone(); var right=(JObject)rb[rid].DeepClone();
                    foreach(var row in new[]{left,right})
                    {
                        row.Remove("ends");
                        foreach(var plot in ((JArray)row["plots"]).OfType<JObject>()) foreach(var key in new[]{"y","basement","directPlacement"}) plot.Remove(key);
                    }
                    if(!JToken.DeepEquals(left,right)) d.rowsStateful++;
                    if (RowAssignOnly(ra[rid], rb[rid])) d.rowsAssignOnly++; else d.rowsGeometry++;
                }
                return d;
            }

            /// <summary>True when every changed field of the row is a stochastic assignment (palette/seed/finish picks
            /// re-rolled downstream of a geometry change), not geometry itself.</summary>
            static bool RowAssignOnly(JObject a, JObject b)
            {
                var names = a.Properties().Select(p => p.Name).Union(b.Properties().Select(p => p.Name));
                foreach (var name in names)
                {
                    if (JToken.DeepEquals(a[name], b[name])) continue;
                    if (name != "plots") { if (!AssignFields.Contains(name)) return false; continue; }
                    var pa = a["plots"] as JArray; var pb = b["plots"] as JArray;
                    if (pa == null || pb == null || pa.Count != pb.Count) return false;
                    for (int i = 0; i < pa.Count; i++)
                    {
                        var p1 = (JObject)pa[i]; var p2 = (JObject)pb[i];
                        var fields = p1.Properties().Select(q => q.Name).Union(p2.Properties().Select(q => q.Name));
                        foreach (var f in fields)
                            if (!JToken.DeepEquals(p1[f], p2[f]) && !AssignFields.Contains(f))
                                return false;
                    }
                }
                return true;
            }
        }
    }
}

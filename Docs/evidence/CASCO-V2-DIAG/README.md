# CASCO-V2-DIAG — diagnóstico mecánico del CASCO (input para CASCO-V2)

Paquete de evidencia del workpack de diagnóstico (Owner-directo, ejecutado sobre
`worker/prod-env-01` HEAD `246756c`). Leer primero `CASCO_DIAGNOSTIC.md`.

| archivo | contenido |
|---|---|
| `CASCO_DIAGNOSTIC.md` | informe principal (método, verificación, stats, hallazgos, ambigüedades) |
| `casco_diagnostic.json` | datos completos machine-readable (plots, vecinos, candidatos, overlay) |
| `plots.csv` · `candidates.csv` | tablas por parcela y por candidato |
| `stats.json` | estadísticas + checks |
| `scene_crosscheck.json` | 27/27 muestras vs escena commitada, delta máx 0,5 mm |
| `captures/map_01..06_*.png` | inspección visual (renders de datos, no SceneView) |
| `REPRODUCE.md` · `RUNBOOK_OVERLAY.md` | reproducción numérica · overlay Unity |

Restricciones respetadas: nada de ENV01 se movió, fusionó ni modificó; los
candidatos son datos geométricos; las heurísticas viven en
`Tools/casco_diagnostic.config.json`.

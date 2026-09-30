# REPRODUCE — cómo reproducir cada número del diagnóstico

Todo comando se ejecuta desde la raíz del repo (`C:\Juego Def`). Los dos tools son
read-only sobre spec/units/polish/escena; escriben sólo en `--out`.

```bash
# 1) diagnóstico completo (JSON + 2 CSV + stats)
python Tools/casco_diagnostic.py --out Docs/evidence/CASCO-V2-DIAG

# 2) cross-check contra los bytes commitados de la escena (streaming YAML, sin Unity)
python Tools/casco_diag_scene_crosscheck.py

# 3) determinismo: segunda corrida a carpeta temporal y comparar hashes
python Tools/casco_diagnostic.py --out "$TEMP/casco_diag_rerun"
sha256sum Docs/evidence/CASCO-V2-DIAG/casco_diagnostic.json "$TEMP/casco_diag_rerun/casco_diagnostic.json"
# (idem plots.csv, candidates.csv, stats.json — deben ser iguales par a par)

# 4) cambiar una heurística y ver el efecto (SÓLO datos; nada del casco cambia)
#    editar Tools/casco_diagnostic.config.json (p.ej. min_interior_footprint_m2: 30)
#    y re-ejecutar el paso 1 a otra carpeta; comparar flags/candidatos.
```

Hashes de la corrida congelada en este paquete (config por defecto):

```
casco_diagnostic.json  3784ae5f…(ver archivo; regenerar y comparar con sha256sum)
plots.csv              idem
candidates.csv         idem
stats.json             idem
```

Nota: el hash exacto de cada archivo está implícito en el propio output; para
verificar determinismo basta comparar dos corridas entre sí (mismo input + mismo
tool + mismo entorno ⇒ bytes idénticos). El manifest interno (`inputs`) lleva los
SHA256 de spec/units/polish/config/tool con los que se generó.

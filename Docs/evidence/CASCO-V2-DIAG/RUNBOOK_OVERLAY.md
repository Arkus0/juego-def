# RUNBOOK — overlay de debug del diagnóstico (operador Unity)

**Herramienta:** `JuegoDef/ENV/Casco Diagnostic Overlay` (EditorWindow
`EnvCascoDiag`, `Assets/JuegoDef/Editor/Env/EnvCascoDiag.cs`).

**Garantía no destructiva:** la ventana sólo dibuja con `Handles` en el SceneView y
lee `casco_diagnostic.json`. No crea GameObjects, no escribe la escena, no guarda
nada, no toca Undo. Cerrar la ventana elimina el dibujo.

## Pasos

1. Abrir la escena `Assets/JuegoDef/Scenes/ENV/ENV01_Casco_District.unity` (sin
   guardar cambios previos de otros trabajos).
2. Menú `JuegoDef/ENV/Casco Diagnostic Overlay`. La ventana carga
   `Docs/evidence/CASCO-V2-DIAG/casco_diagnostic.json` (editable en el campo).
3. En el SceneView (vista ortográfica desde arriba para el mapa completo; vista
   perspectiva a altura de calle para detalle):
   - **rojo** = parcela bajo el mínimo heurístico de interior (footprint o frontage);
   - **ámbar** = estrecha (≤ 4,6 m) pero sobre el mínimo;
   - **verde** = individualmente razonable;
   - **contorno azul + etiqueta** = candidato de agrupación 2–6 (sólo datos);
     el slider de tamaño y el toggle "solo con miembros flaggeados" reducen el
     ruido de 342 hulls;
   - **amarillo** = residual no clasificado; **cian** = espacio urbano deliberado
     (calles, plazas, agua, yards/huertas).
4. Botón `Verify 5 sampled buildings`: escribe en consola `JD_CASCO_DIAG …
   OK/FAIL` comparando transforms de K8_3_0, K14_3_0, K14_1_0, K11_0_1, K14_3_6
   contra el JSON (tolerancia 2 mm; la prueba completa 27/27 está en
   `scene_crosscheck.json`).

## Evidencia esperada (si se quiere captura)

- Capturar el SceneView (mapa completo + 2–3 calles en detalle) y copiar a
  `Docs/evidence/CASCO-V2-DIAG/captures/` (crear la carpeta).
- Recibo de no alteración: antes/después de la sesión,
  `git status --porcelain` limpio en escena/spec/trace y SHA256 de la escena
  idéntico (`41e2cefd…` en HEAD actual). Si Unity marcara la escena dirty sin
  cambios reales, descartar sin guardar.

## Estado

- [ ] Capturas del overlay — PENDIENTE de operador (este entorno no tenía Unity
      MCP disponible; el núcleo numérico no depende de Unity).
- [x] Verificación por consola implementada (read-only).

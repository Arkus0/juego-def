# Lote C — experimento descartado

Se probó una capa `FacadeLife` con hash independiente: repintado por planta en paños de revoco de ≥24 m² y manchas de alféizar/reparación en laterales expuestos de ≥18 m². Se excluyeron piedra, landmarks, laterales bloqueados y los cuatro edificios de las medianeras protegidas. No cambió ninguna llamada RNG heredada.

Se regeneraron 164 filas / 311 edificios, conservando Ground, overlays, plazas, río y lighting. El validador de escena devolvió 0 issues, 370 umbrales cerrados y 29342 renderers. Se capturaron las 12 estaciones representativas y las 20 aleatorias, ambas direcciones, antes y después (64+64 JPG a 1920×1080). El árbol preservó todos los paths anteriores; la diferencia incluía materiales y nuevos grupos, pero también postprocesos de props todavía no reaplicados.

La inspección a escala de paseo no confirmó mejora clara de lectura. La revisión visual independiente de ocho pares encontró cambios principalmente de cielo y vegetación, una silla que perdió su orientación útil y un caballete parcialmente visible. No se acepta un contador de edificios modificados como prueba de mejora.

**Decisión: REVERT completo del experimento**, incluidas sus variantes de material, código y escena. Se recuperó el backup de A antes de continuar. `VALIDATION_C.json` y `C_VISION_INDEPENDENT.jsonl` son evidencia del experimento descartado, no validación del candidato final.

La cifra original de 362 paredes lisas no es una medición física: el mapa clasifica 277 hallazgos textuales de pared lisa, 80 de remate, 1 de interior y 20 otros. Varias descripciones no corresponden a los píxeles. Se conserva el ledger como mapa de revisitación; no se declara solucionado por añadir kit. Los siguientes cambios se centran en fallos groseros y semántica, según la prioridad explícita del Owner.

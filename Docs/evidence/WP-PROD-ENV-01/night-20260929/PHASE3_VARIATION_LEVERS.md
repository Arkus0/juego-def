# Fase 3 — palancas de variación anti-procedural (informe de mapeo)

Date: 2026-09-29 (night session). Author: read-only research subagent, verified line-by-line against current code. Status: **READY TO IMPLEMENT** — consumed by the Fase 3 implementer after the Fase 2 visual gate.

## Hallazgo crítico previo

**RHYTHM_MONO_LINTELS hoy no mide el dintel, mide el tope del MURO.** En `Editor/Env/EnvSemantics.cs:962-975` el bucle toma `top = max(r.bounds.max.y)` sobre todos los renderers del slot — incluido el muro, que cubre la planta entera (`Wall_Plaster_Window_Wide_Flat` = Y 0.00–3.00). Como `Storey = 3f` constante (`BuildingAssembler.cs:70`) y el slot va en `y = f*Storey` (`:166,174`), `top - floorLine = 0.0` para toda ventana del distrito. **Variar la cabeza del hueco NO limpiará el finding ×22 sin arreglar la métrica.** Fix mínimo en `EnvSemantics.cs:966`: excluir del `max` los renderers cuyo módulo empiece por `ENV_Wall_` o `Wall_` (helper `EnvClearance.ModuleName`). Entonces la métrica leerá el tope real de carpintería/persiana/sillar.

## Regla de oro (determinismo)

El RNG principal (`BuildingAssembler.cs:117`, `new Random(s.seed*7919 + s.id.GetHashCode())`) es una secuencia compartida: Rows→Era→Shutters→History→Slots→Dress la consumen EN ORDEN. **Insertar draws en `Recipe` desplazaría todos los sorteos posteriores** y el diff del distrito sería enorme. Todo sorteo nuevo usa un `Random` dedicado (`s.seed * <primo> + <const>` o hash `(seed,floor,bay)`), nunca el `rng` compartido. Tampoco `s.id.GetHashCode()` (frágil). No tocar el orden de `EnvBusiness.Used` (estado con memoria, ya replayeado por dry-run).

## Cotas seguras (no violar reglas duras)

- Puerta: altura libre ≥ 2.22 m (`ENV_FACTORY.md:238`) → no desplazar cabezas en muros de PUERTA, solo ventana (`w`/`W` sin ashlar).
- Sill ≤ 0.10 m en umbrales; escalón `ENV_Door_Step` no se toca.
- Clearance GC2: cilindro 1.2 m frente a `THR_*` via `EnvClearance.TryPlace`; barra frontal de toldo ≥ ~2.15 m.
- Estructura: `Storey = 3f`, banda de forjado 2.76–3.00 → desplazamiento vive dentro del panel, sin tocar slot/Storey. Escalado de fila solo X.
- Coherencia por edificio: una línea de cabeza por edificio (o dos: principal vs superior), NUNCA por ventana individual (rompe lectura estructural, dispara TWIN/WINDOW_RUN).
- Módulos nuevos: registrar en `modules.json` → `boxCollider` (validador exige collider por bay); prohibido kit walls de `bannedModules`.
- Dintel ∈ 2.21–2.41 m (base 2.31 ±10 cm; ashlar tope 2.67 < 2.76). Alféizar ∈ 0.95–1.15. Fascia escala Y ≤ 1.13. Señales jitter ±0.10. Roller blinds bajada 1.85/2.45. Hierro de balcón solo materiales oscuros existentes.

## Quick wins ordenados (impacto/riesgo)

1. **Fix métrica lintels** — `EnvSemantics.cs:966` excluir muros del `max`. Riesgo ~0. Sin esto nada limpia el ×22.
2. **Suite de ventana parametrizada (2 alturas de cabeza)** — Blender: factorizar `window_suite(sill, head)` cortando `ENV_Wall_Plaster_Clean` (patrón cut+opening_cutter `env_derive.py:271-277,381-385`) + inserto parametrizado (`:556-568`); generar `..._Window_Hi` (cabeza 2.41) y `..._Window_Lo` (2.21); alta en `modules.json` boxCollider; elección por edificio con RNG dedicado en `FacadeGrammar.WideWindow()` `:401-406` (solo `w`/`W`, no ashlar; forzar `w` cuando cabeza ≠ 2.31 — persianas CERRADAS cubren el hueco, ABIERTAS se pliegan a un lado sin colisión). **El cambio que rompe de verdad "la única línea de dintel".**
3. **Jitter de alturas de rótulos/señales** — `EnvBusiness.cs:229,258,266,291,302,334,343,349` + `FacadeGrammar.cs:831`: `y + 0.10f*(rng-0.5)`. Visible en todas las calles comerciales, riesgo ~0.
4. **Persiana roller: 2 variantes de bajada** — recetas nuevas copiando `env_derive.py:1337-1351`; selección por hash `(seed,floor,bay)` en `FacadeGrammar.cs:416,432`. Riesgo 0.
5. **Hierro de balcón por color de edificio** — `FacadeGrammar.cs:497-502`: `With(stoneMap,"ENV_Metal_Iron", pick {negro, Verde, Azul})`. 1-2 líneas.
6. **Carpintería repintada aislada** — generalizar `history.oddWindow` (`BuildingAssembler.cs:173`) a "1 ventana distinta en 15 % de edificios" con paleta `OldJoinery` (`EnvCharacter.cs:63-67`). Sin geometría.
7. **Fascia: escala Y del tablero** — `EnvBusiness.cs:252`: k ∈ 0.9–1.1, clamp ≤1.13. 1 línea.
8. **Toldos: paleta ampliada + jitter** — `EnvBusiness.cs:279` + `EnvDistrict.cs:641` (2-3 canvas nuevos del atlas) y escala Y 0.95–1.05 en `:282`/`FacadeGrammar.cs:542`.

Ya variado por seed (no tocar): persianas W/c/w por planta, color carpintería por edificio (tablas OldJoinery/NewJoinery), portals, balcones tipo, escaparates/interiores, chimeneas, tejados, props posicionales (`Hash01`), muros de jardín (panelizado + pilares; palanca menor: altura base `h=2.2` → `2.0+0.4*Hash01(...,48)` en `EnvDistrict.cs:662`).

## Integración

Pasos 2 y 4 requieren Blender headless (`blender -b --factory-startup --python Tools/blender/env_derive.py -- --only NOMBRE`, ver `ENV_FACTORY.md:53-62`) + menús Unity 1→2→7→5; el resto es solo C#. Verificar determinismo con `EnvPolish.Fingerprint` antes/después de una fila; re-correr `JuegoDef > ENV > 5 Validate` (colliders de bays nuevos) + `EnvSemantics.Rhythm` (con la métrica ya arreglada).

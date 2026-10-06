# PLAN DE DEFINICIÓN DE IMAGEN — demo PS1 (informe para el Owner, 2026-10-06)

**Objetivo:** que la demo deje de leerse "borrosa / baja definición" sin renunciar al look PS1 ni tocar geometría, layout ni sistemas.
**Base del diagnóstico:** ~25 capturas de la sesión de auditoría (`Assets/Screenshots/`), el código de los shaders `City/StyleB/Shaders/*` y la configuración viva de la escena `CITY_B_PS1_DEMO`.

---

## 1. Diagnóstico — por qué se ve borroso

| # | Causa | Evidencia | Peso en la percepción |
|---|---|---|---|
| D1 | El raster 480×360 se estira al bloque sin estructura (sin escalado entero ni retícula) | `CityRetroScreen` → RawImage con AspectRatioFitter; ventana 1101×506 = bloque de ~2,3× | **Alto** |
| D2 | Los muros y suelos se mezclan deliberadamente con su mip borroso (anti-shimmer del mareo del 05-10) | `CITY_PSXAtlantic.shader` frag: `t0.rgb = lerp(broadTex, t0.rgb, 0.62)` en superficies mapeadas a metro; `CityLook.groundCalm = 0.35` calma además el pavimento | **Alto** |
| D3 | Paleta lavada: sombras frías claras (0,60/0,66/0,80) + cielo pálido + cuantización 5 bits | `PSXAtlantic` `_ShadowTint`, `CityLook` sky/bounce publicados en escena | Medio-alto |
| D4 | Cielo = degradado vacío que se funde con la bruma | Skybox `Cielo`; sin nubes ni horizonte definido | Medio |
| D5 | Bruma por material agresiva a media distancia (47–107 m en muros) | `CITY_PSXAtlantic` `_FogStart/_FogEnd` por material | Medio (solo vistas largas) |
| D6 | Ventanas planas sin interior (excepción: comedor de la pensión, que se lee genial) | SHOPFRONTS sin GENERO interior en la mayoría | Medio (content) |
| D7 | Texturas sueltas en Bilinear fuera del barrido PSX | 2 corregidas el 06-10 (`PSXDemoPolish`); quedaría revisar cielo/agua/NPC atípicos | Bajo |

**Lo que NO es el problema:** resolución de raster (480×360 es PS1 auténtico), geometría, layout, dressing semántico (auditado limpio), ni colliders/físicas (ya resuelto).

## 2. Plan por fases (orden por impacto; cada fase es independiente y reversible)

### FASE 1 — Definición de imagen (el "borroso" se ataca aquí)
1a. **Escalado entero con retícula opcional** — `CityRetroScreen`: en lugar de estirar al bloque, calcular el múltiplo entero máximo que cabe (p. ej. ×2 = 960×720) y pillarbox el resto; añadir (toggle F10) una retícula sutil alineada a la rejilla de píxel. Efecto: el píxel se lee nítido, no borroso. Riesgo: imagen algo menor en ventanas no múltiplo; solución: elegir 480×360↔960×720 como resolución interna por defecto.
1b. **Recuperar detalle en muros/suelos** — subir el lerp anti-shimmer `0.62 → 0.80` en `CITY_PSXAtlantic` (y su equivalente en `CITY_PSXGround` si existe), y bajar `CityLook.groundCalm 0.35 → 0.15`. Efecto: la sillería y el pavimento vuelven a tener arista. Riesgo: vuelve algo de shimmer a >30 m — se mitiga con 1a (retícula organiza el ruido) y midiendo en Play.
1c. **Sesgo de mips a cero** en los materiales que lo tengan (`_MipBias` 0.3 → 0.1).
**Verificación:** las 3 vistas fijas (plaza V2, Calle Mayor V7, calle baja V8) antes/después con cámara idéntica + close-up de fachada.

### FASE 2 — Contraste
- `CityLook`: sky 0,98→0,90; bounce 0,58→0,52; `PSXAtlantic._ShadowTint` (0,60/0,66/0,80) → (0,50/0,57/0,72) — sombras con más caída sin perder legibilidad.
- Regla dura: **nada por encima de 1,0** (el RT es LDR; ayer el clip a blanco fue el fallo original). Tras el cambio, captura de la plaza a pleno sol para confirmar que el máx queda ≤0,95.
- Efecto: la imagen deja de estar en gris medio; el dither 5 bits pasa de "lavar" a "texturizar".

### FASE 3 — Cielo y horizonte
- `CITY_PSXSky`: banda de nubes baja pintada (textura 256px, 2-3 tonos) o gradiente de 3 paradas con horizonte más denso que el cenit.
- Ajuste de bruma solo donde aplana hitos: en los 5 materiales de muro, `_FogEnd` 107→150 manteniendo `_FogStart` 47 — la torre y la iglesia recuperan silueta sin perder atmósfera de calle.
- Efecto: vistas largas (plaza, calle baja con el mar) dejan de fundirse en blanco.

### FASE 4 — Ventanas con vida (contenido; una calle por pasada, pensionero primero)
- Tarjeta interior simple (plano oscuro con variación de tono + marco) en las ventanas de las calles del recorrido, empezando por Leajarraga. El comedor de la pensión ya demuestra que el truco funciona.
- Alternativa mínima si no hay tiempo: brillo leve variable en el cristal (el shader ya tiene gloss) para romper el verde plano.

### Fuera de alcance (explícito)
Nada de regenerar fachadas ni terreno, nada de nuevos sistemas de física/AI, no subir la resolución interna más allá de 960×720 (opcional F6 ya existe), no tocar colliders/colocación ya arreglados.

## 3. Estado de la demo al cierre de hoy (para contexto del informe)

- Corregido y verificado: stack multi-escena con bootstrap, cámara 3ª persona con colisión (sustituye el shot GC2 que se enterraba), luz LDR (sol 0,82 elev 24° ámbar), raster nítido 480×360, 72 colliders de asientos/mesas, pensionistas sentados por pelvis, toldo de la Taberna fuera del rótulo.
- Auditorías: 159 NPCs limpios, 54 escaparates consistentes, 0 props flotando/atascando en el núcleo.
- Pendiente conocido: huertas del este con ~10 edificios que flotan de lejos (fuera del recorrido), escaparates genéricos por pintar, manos/caras NPC de nivel PS1 bajo (época-correcto).

## 4. Cómo se aprueba cada fase

1. Ejecutar la fase en la escena demo (Edit), guardar.
2. Capturas idénticas antes/después en V2, V7 y V8 + un close-up de fachada.
3. Play de 2 minutos por el recorrido (spawn plaza → Calle Mayor → calle baja) comprobando: sin shimmer mareante, sin clip a blanco, rótulos legibles.
4. Si el Owner da el visto bueno visual → siguiente fase. Rollback = revertir los valores (todos están documentados en este informe y en los comentarios del código).

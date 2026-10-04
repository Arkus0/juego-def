# Texturas del pueblo al modo Shenmue 2 — especificación v1

Estado: **v1. La calle tiene el visto bueno del Owner** (2026-10-04: "la primera escena, de la calle, magnífica"). Sustituye
la "Dreamcast+" de `CITY_STYLE_DCPLUS.md` en todo lo que toca a texturas.

## Diagnóstico (Owner, 2026-10-03)

Las texturas del kit eran hojas estilizadas, repintadas después con relieve horneado y suavizado. El resultado parecía
"un asset repintado por IA", no Dreamcast. Faltaba color y faltaba simpleza con carisma.

## Qué hace Shenmue 2 (medido)

Fuente del análisis: 74 capturas de Shenmue II (galería pública de RPGamer) y la captura del Owner. Se usaron solo como
medida, sin redistribuirlas. Recortes de superficies a 640×480:

| Superficie (Shenmue 2) | Saturación | Desviación de luminancia | Detalle nítido (Laplaciano) |
|---|---|---|---|
| pared pintada amarilla | 0,55 | 0,165 | 6,1 |
| ladrillo de casa | 0,38 | 0,175 | 4,2 |
| losas de acera | 0,08 | 0,147 | 3,3 |
| hormigón viejo | 0,33 | 0,108 | 3,7 |
| **antes, revoco nuestro** | 0,24–0,35 | 0,09–0,10 | 1,2–1,4 |

Leyendo las cifras:
1. **Las texturas son fotografías** de superficies reales, reducidas al tamaño de Dreamcast (unos 128 px/m a la
   distancia de juego) con un filtro nítido: nada de suavizado ni manchas difusas.
2. **La estructura se lee de lejos:** juntas, hiladas, adoquines y tejas oscuros y marcados (es la oclusión de la propia
   foto).
3. **Color de pintura de verdad,** saturado y con contraste (luminancia 0,14–0,24 dentro de la superficie), sin mapas de
   normales ni brillo.
4. **Color de 16 bits** (RGB565) y escalado bilineal a la salida: grano limpio, no ruido de foto.

## La regla (copiar, no adaptar)

| Capa | Regla |
|---|---|
| Fuente | foto CC0 de la superficie real (Poly Haven; procedencia en `Tools/city_ivanix/provenance/SHENMUE_KIT_SOURCES.json`) |
| Proceso | `tools/shenmue_kit.py`: reducir a 256 px por baldosa de unos 2 m (atlas de molduras a 1024), oclusión de la foto metida en el color, contraste y saturación hacia las cifras de arriba, máscara de enfoque ligera, RGB565 |
| Revocos | foto neutra con su luz y su suciedad; el color lo pone el material, con la paleta cántabra saturada de `CityShenmueKit.RenderColour` (cal, hueso, crema, arena, ocre, tostado, salmón, añil, verdín, gris). Coordenadas de mundo: una fachada es una superficie, no una pila de módulos de 2 m |
| Kit | `CityShenmueKit.Apply`: cada material DC sustituye su hoja estilizada por la superficie fotografiada equivalente, sin ruido macro ni brillo |
| Suelo | `CityPaving`: losas de granito (Calle Mayor y Muelle), adoquín de granito (plaza y abanicos), adoquín grande (calles), canto rodado (callejas) |
| Superficies singulares | `tools/paint_plaza.py`: cada rótulo, cartel o persiana pintado a mano con su texto y su desgaste |

## Pendiente

- **Luz:** la plaza sale plana. Hay demasiada luz ambiente y poco contacto entre edificios y suelo. Siguiente pasada:
  contraste y oclusión de contacto horneada (Owner, 2026-10-04).
- **Ventanas:** las de las viviendas se leen como pegatinas luminosas; hay que oscurecerlas.
- Las fuentes de los rótulos (Windows) siguen siendo solo look-dev.

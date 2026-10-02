# Estilo gráfico de la ciudad — "Dreamcast+ cantábrico"

Estado: **PROPUESTA (look-dev en curso)** · Owner 2026-10-02: "que deje de parecer assets mejorados y parezca un juego de
Dreamcast con nivel gráfico top; Shenmue 2 es el mínimo; con personalidad y estética cantábrica; la iluminación está bien".

## Qué hace que Shenmue 2 se vea como se ve

1. **El detalle vive en la textura, no en la geometría.** Fachadas y suelos con color, desgaste, grietas, sombras de
   contacto y luz suave *pintados dentro* del difuso; geometría limpia, siluetas claras, pocos polígonos bien puestos.
2. **Materiales simples.** Casi difusos: sin mapas de normales ni rugosidad visibles, un brillo mínimo sólo donde importa
   (cristal, metal pintado, charcos).
3. **Color local fuerte y legible.** Cada comercio tiene un color propio; el ojo recorre la calle por manchas de color.
4. **Personalidad a pie de calle.** Rótulos grandes y legibles, cajas luminosas, escaparates con género, carteles,
   máquinas, bicis, cajas de fruta: la calle cuenta quién vive y qué se vende.
5. **Luz clara y continua.** Ambiente generoso, sombras nítidas pero no negras, sin capas de post (ni AO de pantalla, ni
   viñeta); el "brillo" lo ponen los rótulos y los cristales.

## Traducción cantábrica (1999–2003)

- **Paleta:** revocos de cal y crema, ocres e indianos (azul añil, verde carruaje, salmón, verdín), carpintería granate,
  verde y blanca, galerías blancas acristaladas, piedra arenisca y caliza; tejas rojas lavadas por la lluvia; sobre todo
  ello, la luz atlántica velada que ya tenemos.
- **Personalidad de época:** bares con cajas luminosas y sillas de plástico, farmacia con cruz verde, estanco, quiosco de
  prensa y de la ONCE, Correos (buzón amarillo), cajas de ahorro con rótulo corporativo, panadería, pescadería,
  ultramarinos, sidrería, bombonas de butano naranjas en los portales, ropa tendida, Vespino y bicis, utilitarios
  genéricos de la época, barcas pintadas en el muelle, redes y nasas, hortensias en las puertas.
- **Nada asiático y nada de marcas reales:** nombres y logotipos inventados, tipografía de rotulista de los 90.

## Reglas técnicas (look-dev)

| Capa | Regla |
|---|---|
| Shader | `JuegoDef/City/DC Plus`: Lambert envolvente (wrap), sombra pintada en tono frío, ambiente por armónicos, oscurecido de zócalo, brillo opcional muy bajo, niebla de Unity, sombras en tiempo real nítidas |
| Texturas | máx. 512 px por superficie (1024 sólo en suelos grandes), suavizado que conserva bordes, relieve y cavidades del mapa de normales **horneados** en el color, saturación +10–15 %, filtrado bilineal con ligero sesgo de mip |
| Post | sin SSAO ni viñeta en la ciudad; tonemapping neutro; bloom sólo en emisivos (rótulos, farolas) |
| Geometría | se mantiene la del kit; los assets nuevos se modelan con siluetas limpias y detalle en textura |
| Rótulos | escala Shenmue: rótulos de fachada de 0,6–1 m de alto, banderolas, cajas luminosas; color propio por comercio |
| Objetos | entidades con huella, holguras y pertenencia (la sombrilla pertenece a la mesa, la mesa al bar); nada se coloca "donde cabe" |

## Fases

1. Look-dev en un tramo (calle Mayor y esquina de la plaza): shader, texturas, post y rótulos. Comparativa antes/después.
2. Assets propios en el estilo (Blender): coches, barcas, árboles y vegetación en tarjetas, mercadillo y terraza
   compuestos, objetos de época.
3. Despliegue a toda la ciudad con colocación por entidades, juntas de pavimento orgánicas y más densidad.
4. Paseo del Owner y correcciones.

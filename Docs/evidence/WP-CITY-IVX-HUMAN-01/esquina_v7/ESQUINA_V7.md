# Esquina de prueba V7 — boca de la Calle Mayor, todas las capas (2026-10-03)

Prueba del método antes de extenderlo al corte (brief, sección 0; Owner: "sí" a empezar por aquí, con cámara Shenmue
y 640×480 4:3). Se juzga contra Shenmue 2. La captura de referencia de Shenmue se compara fuera del repositorio: no se
redistribuye.

## Qué hay

| Capa | Hecho |
|---|---|
| Restar | todo el corte: 116 objetos (`RESTAR.json`); en la esquina, además, los toldos y el rótulo "Librería El Faro" del local cerrado |
| Superficies pintadas | `tools/paint_plaza.py`: 16 superficies únicas con su texto, desgaste y luz pintada (`superficies_pintadas.jpg`) |
| Se traspasa (`R0124`) | tres persianas echadas, cada una con su historia (cartel "SE TRASPASA" con teléfono; el cartel de fiestas de este año sobre el del año pasado arrancado; "PROHIBIDO FIJAR CARTELES" con un tag y carteles encima); cajones de persiana; el fantasma del rótulo "TEJIDOS LAVÍN"; chorreones bajo las ventanas |
| Sidrería Casa Bustamante (`R0152`) | el bar visto tras el cristal con la luz encendida (interior falso ENV, sala de bar, brillo de día); vinilos "COMIDAS y RACIONES / SIDRA NATURAL / Cerrado los lunes"; cartel de fiestas en la puerta; pizarra con el menú del día a 1.200 pts; barril-mesa con botella y dos culines; serrín en la puerta; chorreón de óxido bajo el balcón |
| Caja de Ahorros del Norte (`R0125`, flanco a la Calle Mayor) | el flanco ciego pasa a escaparate de aluminio nuevo en casa vieja, puerta y cajero 24 h empotrado con visera; rótulo corporativo; cartel del plan de pensiones; humedad en el zócalo |
| Fiestas (`V09_FIESTAS`) | tres cuerdas de banderines cruzando la Calle Mayor, ancladas a fachadas reales, a alturas distintas |
| Lo civil | placas de azulejo "CALLE MAYOR" a ambos lados de la boca |
| Suelo | clase LOSA (Calle Mayor y Muelle): granito labrado en hiladas pintado, con juntas, chicles y una mancha de aceite. **Cambia también el Muelle** (misma clase, mismo significado) |
| Luz | `CityIvanixLook`: martes 12:30 de septiembre; sol a 42° desde el sudeste, 5600 K; ambiente generoso; sombra al 62 %; bruma desde 90 m; cielo azul con nubes; saturación +14; sin viñeta. Es la luz de todo el pueblo |
| Cámara | plano GC2: radio 2,3 m, altura 0,35, hombro 0,35 (antes 3 / 1 / 0,5): más cerca y más baja |
| Imagen | `CityRetroScreen` en la Main Camera: 640×480, 4:3 con bandas, bilineal |

## Capturas

`g3_*`: cámara del juego (640×480 escalado ×2). `f3_*`: encuadre fijo viejo, comparable con `views/before_*`.

## Lo que falta para estar a la altura (siguiente iteración, ya en el corte entero)

- **Densidad a la altura de la cabeza:** banderolas y cajas de luz que salen sobre la calle a varias profundidades, más
  rótulos por encuadre.
- **Género que sale de las tiendas:** la frutería, el mercadillo, la pescadería.
- **Plantas altas con vida:** macetas, ropa tendida y persianas a distintas alturas. Hoy sigue la textura de kit en mosaico.
- **Suelo con más uso:** manchas de bajante, alcorques, tapas de registro.
- **Gente:** NPC, fuera de este WP.

## Comprobación

Lint limpio. La pizarra, el barril y la botella están en la viñeta `V10_SIDRERIA` de la escena de props y el lint los
cubre. NavMesh 18/18.

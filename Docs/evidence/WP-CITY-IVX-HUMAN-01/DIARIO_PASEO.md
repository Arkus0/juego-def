# Diario del paseo — Plaza Mayor y arranque de la Calle Mayor (Paso 1, 2026-10-03)

**Cómo se recorrió.** Dos pasadas sobre las escenas congeladas en `515e5c1`, de día. La primera con 18 paradas por la
ruta spawn → plaza → Calle Mayor → bocacalle → vuelta; la segunda con 8 paradas en los bordes de la plaza y sus bocas.
En cada parada se colocó el Player y se tomó la imagen con el **encuadre del juego medido en Play Mode** (cámara GC2:
3 m detrás, 2 m sobre los pies, 0,5 m sobre el hombro derecho, FOV 55; herramienta `CityViews`). El Play Mode se usó
para comprobar spawn, suelo y cámara (`Player` asentado, `IsGrounded=True`; la cámara orbita con el ratón). El maniquí
sale en pose T porque la imagen se hace en edición. Capturas en `diario/`; las 8 vistas fijas, en `views/before_*`.

Clases: **NE** no existiría · **SE** sitio equivocado · **FA** falta algo obvio · **ESC** escala · **EP** época/estética ·
**AP** asset pobre · **LK** look (no parece Shenmue 2, añadido del Owner).

| Parada | Qué chirría | Clase |
|---|---|---|
| `W01_spawn_al_sur` | Se nace contra la tapia lisa de la iglesia. Dos suelos chocan en diagonal sin junta, y al fondo el mercadillo ya se ve como una barrera de lonas. | SE · LK |
| `W02_entrada_norte` | La primera vista de la plaza es un muro de puestos de espaldas. La fuente queda tapada y hay una furgoneta blanca aparcada dentro de la plaza. | NE · SE |
| `W03_iglesia` | La "iglesia" es una nave de arenisca con una puerta pequeña: se lee como almacén. La torre del reloj es el único hito. Los puestos tienen lona de color plano, el género son cubos de color y la ropa planos colgados. | NE · AP · LK |
| `W05_mercado` | El Mercado de Abastos parece una casa larga de dos plantas con ventanas en arco: nada dice "mercado". Delante, tres puestos idénticos de rayas rojas. | NE · AP |
| `W06_diagonal_so` · `W07_diagonal_ne` · `W08_borde_sur_no` | Los puestos forman un anillo radial alrededor de la fuente, con la trasera hacia fuera: un laberinto de feria, no un mercadillo. Hay 19 puestos de 3 modelos y 3 colores, todos a la misma distancia. Una furgoneta plateada aparcada en la plaza. | NE · SE · AP |
| `W09_eje_calle_mayor` | Desde la plaza no se ve la boca de la Calle Mayor: la tapan la espalda de los puestos y dos farolas exentas. | SE |
| `W10_calle_mayor_alta` | Se lee como calle, pero el suelo de losas poligonales parece un camino de jardín, no el enlosado de una calle mayor. Las terrazas son sillas de plástico blancas de color plano. Las plantas bajas están cerradas: cristal oscuro y muros lisos. | AP · LK · FA |
| `W11_sidreria` | La Sidrería Casa Bustamante tiene un rótulo de fascia correcto, pero la fachada es muda: nada se ve dentro, solo dos barriles en la puerta y un aire acondicionado. La terraza de al lado no es de nadie. | FA · LK |
| `W12_calle_mayor_media` | Furgoneta roja de primitivas facetadas en mitad de la Calle Mayor. Del lado este la calle es una tirada de muros laterales de casas que dan a otras calles (hotel, R0127): plantas bajas ciegas. Farolas exentas cada pocos metros en una calle estrecha. | AP · NE · FA |
| `W13_bocacalle` | En la bocacalle hay un muro ciego enorme (flanco de R0161). La "Farmacia de la Plaza" está a 70 m de la plaza. | SE · FA |
| `W14_vuelta_norte` | Furgoneta roja aparcada en el eje y buzón en mitad de la acera. La calle no tiene remate: al fondo solo la farola de la fuente; la torre no se ve. | SE · FA |
| `W15_boca_plaza` | Contenedores amarillo, azul y gris en fila al borde de la plaza, junto a una terraza. | SE |
| `W17_poniente` | La Casa Consistorial lleva un rótulo de fascia de comercio, "CASA CONSISTORIAL", y una maceta en la puerta: parece una tienda, no un ayuntamiento. | NE · EP |
| `X01_borde_sur` | **El lado sur de la plaza son traseras**: la fila de Levante Sur (R0125…R0122) da su fachada a la otra calle. A la plaza le enseña zócalos ciegos, la plaza no tiene bar y ese lado está muerto. | NE · FA |
| `X02_borde_oeste` | El escudo, el farol y la parra de la Consistorial están bien, pero la fachada no es única; es una casa más. | FA |
| `X03_hacia_muelle` · `X04_puerta_muelle` | Desde la plaza no se ve el mar. Junto a la puerta hay contenedores en fila en mitad de la calle (fuera del corte). El "Bar El Puerto" de verdad está junto a la puerta (`R0043`); el de `R0185` es un duplicado. | SE · FA |
| `X05_esquina_ne` | La esquina iglesia–torre funciona; la calle de la Finca sale limpia. | — |
| `X06_levante` | La calle de Levante sale de la plaza sin uso: buen sitio para la trasera de carga del Mercado. | FA |
| `X07_poniente_desde_plaza` | Poniente tiene vida (Modas Carmen, panadería, sidrería), pero hay dos sidrerías a 40 m (`R0085`, `R0152`) y dos panaderías a 30 m (`R0058`, `M0184_01`). | SE |
| todas | El suelo de la plaza lo atraviesan cinco bandas radiales grises desde la fuente, que se leen como caminos pintados. No hay nadie, ni un objeto pequeño con letra impresa a la altura de la mano. Hay niebla de distancia a menos de 30 m y la luz es PBR apagada. | LK · AP |

Paradas sin información (cámara dentro de un puesto o entre dos muros): `W04`, `W16`, `W18`, `X08`; no se guardan.

## Lo que ya funciona y se conserva

La torre con su reloj como hito; la fuente-farola en el centro; el trazado de la plaza y sus seis bocas; la luz de día
como base; los rótulos de fascia y banderola con color propio por comercio; la pizarra "QUESOS del valle · SOBAOS ·
QUESADAS · MIEL"; el escudo y el farol de la Consistorial; la esquina iglesia–torre.

## Capturas del Owner

Pedidas en el checkpoint del brief.

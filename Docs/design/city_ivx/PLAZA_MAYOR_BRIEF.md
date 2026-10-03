# Plaza Mayor y arranque de la Calle Mayor — brief de lugar v1

Estado: **APROBADO POR EL OWNER (2026-10-03)**: brief sí; martes 12:30 con mercadillo; primero la esquina de prueba V7 con cámara Shenmue y 640×480 4:3; "Shenmue 2 gráficamente, pero en un pueblo cántabro: como haría el equipo un DLC de Shenmue 2 en Cantabria". (Checkpoint del Paso 2 de `WP-CITY-IVX-HUMAN-01`.)
Vista cenital anotada: [`PLAZA_MAYOR_PLAN.jpg`](PLAZA_MAYOR_PLAN.jpg). Diario del paseo y vistas
"antes": `Docs/evidence/WP-CITY-IVX-HUMAN-01/`.

## 0. El objetivo de imagen: un DLC de Shenmue 2 en un pueblo cántabro

Owner, 2026-10-03: *"quiero que el juego parezca un spin off de shenmue 2. Como un DLC con el mismo estilo gráfico"*;
*"la luz, y sobre todo, texturas con cada superficie pintada, es clave"*. Se mantiene el pueblo cántabro de 1999–2003:
nada de Hong Kong, nada de marcas reales. Este corte se juzga contra esto:

1. **Cada superficie pintada.** Ninguna textura en mosaico que se note; cada planta baja de comercio es una lámina única:
   su interior visible tras el cristal (estantes, género, luz cálida), su rótulo, sus carteles y pegatinas, su zócalo sucio.
   Las plantas altas llevan kit más una capa de suciedad (chorreones bajo vierteaguas, verdín, mancha de alero).
   Ningún objeto de color plano salvo cristal y goma.
2. **Luz horneada.** Oclusión en esquinas, bajo aleros, balcones y toldos; sol cálido, sombra fría, ambiente generoso.
   La luz va metida en el color (lightmap o vértice), no en efectos. Sin niebla a menos de unos 100 m; cielo pintado.
3. **Información a la altura de la cabeza.** En cada encuadre de calle, de 6 a 10 cosas legibles (rótulos, carteles,
   pizarras, escaparates, placas) y todas con dueño. Es la densidad con sentido de Shenmue: la cesta es de la tienda
   que tiene al lado.
4. **Geometría simple, sin complejos.** Cajas limpias y textura que lo cuenta todo; Quaternius o kit solo si encajan.
5. **Cámara e imagen (a decidir).** La de Shenmue va más baja y más cerca que la nuestra y mira un poco hacia arriba, a
   los rótulos. También hay que decidir si se renderiza a 640×480 en 4:3, sin post. Prueba hecha solo con la tubería de
   render: `Docs/evidence/WP-CITY-IVX-HUMAN-01/lookdev/RENDER_PATH_TEST_*.jpg`. El encuadre mejora mucho, pero sin
   textura pintada y sin densidad no parece Shenmue: esos dos puntos son el grueso del trabajo.

**Método:** primero una esquina, con todas las capas a la vez: la boca de la Calle Mayor con la Sidrería Bustamante,
Se traspasa, la Caja de Ahorros y los banderines (vista fija V7). Se pone al lado de Shenmue 2, la juzga el Owner y solo
entonces se extiende al resto del corte (regla AGENTS: nada de contenido en masa antes de tener la vía).

## 1. La historia del sitio

Fue el campo de la feria de ganado, fuera de la muralla del puerto viejo. En 1887 el indiano Fermín Cossío pagó el
empedrado y la fuente-farola de fundición. El Ayuntamiento se mudó a la casona de los Velarde en 1902, y el mismo año
puso el reloj en la torre de Santa María. El Mercado de Abastos se levantó en 1921 sobre las carnicerías viejas. En 2000
es el salón del pueblo: mercadillo los martes, vermú los domingos después de la misa de doce, verbena en fiestas. Las
tiendas de toda la vida aguantan como pueden desde que abrió el hiper de la ciudad.

**Momento que se construye:** martes 12 de septiembre de 2000, 12:30. Hay mercadillo y las fiestas de Nuestra Señora del
Muelle son del 15 al 17, así que los banderines ya están puestos y los carteles pegados. El mercadillo es una capa que se
retira entera: la plaza vacía también tiene que funcionar.

## 2. Habitantes (edificios con fachada al corte, ruta primero)

| Edificio | Quién / qué | Desde | Cómo está | Qué se ve desde 3 m / qué saca a la calle |
|---|---|---|---|---|
| `R0054` + torre | **Iglesia de Santa María**; párroco D. Anselmo Ceballos, sacristana Pili | s. XVI | cuidada, humedad en el zócalo | **pórtico sur** a la plaza con banco corrido de piedra; tablón con misas y esquelas; puerta entornada, penumbra y velas; escalones gastados; reloj que atrasa cuatro minutos |
| `M0186_00` | **Casa Consistorial** (alcalde D. Julio Bárcena) | 1902 | la mejor fachada de la plaza | **soportales de tres arcos**; balcón corrido con tres banderas; escudo labrado; "AYUNTAMIENTO" grabado en el friso (fuera el rótulo de tienda); tablón de bandos con el programa de fiestas; moto de la Policía Local |
| `R0083` (+ `R0111` detrás) | **Mercado de Abastos**: 14 puestos, 9 abiertos | 1921 | repintado en 1995, rejas verdes | **portalón abierto** con el interior iluminado (puestos, balanzas, precios); "MERCADO 1921" en el friso; la trasera `R0111` es el muelle de carga en la calle de Levante |
| `R0068` | **Casa Rectoral** (antes "3.º Mercado") | — | cansada, galería blanca | placa "Despacho parroquial martes y jueves 18–19 h" |
| `M0184_00` | **Notaría** de D. Íñigo Lavín y viviendas (antes "2.º Ayuntamiento") | 1974 | cuidada | placa de latón, portal con felpudo |
| `M0184_01` | **Estanco nº 1**, Maruja Arce (antes 2.ª panadería) | 1968 | — | chapa granate y amarilla "TABACOS", "SELLOS"; postales y mecheros en el escaparate |
| `R0125` | **Caja de Ahorros del Norte**, sucursal | 1994 | aluminio nuevo en casa de piedra vieja | **cajero automático**, rótulo corporativo azul, cartel del plan de pensiones; esquina Calle Mayor–plaza |
| `R0125_1` · `R0117` | **Lotería nº 1** · **Bar La Plaza** (Tino y Mari) (antes "Bar La Ribera", sin río) | 1981 | — | **abren su trasera a la plaza**: el lado sur deja de ser ciego. Lotería con "Navidad ya a la venta"; el bar con dos puertas, caja de luz y terraza a la plaza |
| `R0117_1` · `R0117_2` · `R0122` | viviendas · cochera · Barbería Toño | — | — | traseras dignas: ropa tendida, portal trasero, persiana de chapa de la cochera |
| `R0124` | **Se traspasa** (antes Tejidos Lavín) | cerró en 1998 | persiana echada | "SE TRASPASA" y teléfono; rótulo fantasma pintado; carteles de fiestas pegados encima |
| `R0152` | **Sidrería Casa Bustamante**, Pepe (3.ª generación) | 1932 | trabajada | barril-mesa con botella y culín; serrín en la puerta; pizarra "sidra del año"; la única sidrería del corte |
| `R0126` | **Hotel Comercio** (antes "Hotel Miramar", que estaba tierra adentro) | 1955 | — | el comedor da a la Calle Mayor: "Menú del día"; un coche de turista con baca |
| `R0127` | **Electrodomésticos Somarriba** en la planta baja de la Calle Mayor, viviendas arriba (antes "3.º Hotel") | 1977 | — | cuatro teles encendidas con el mismo telediario; "Instalamos antenas parabólicas" |
| `R0161` | portal de vecinos: Doña Remedios, la del 2.º | — | — | felpudo, hortensias, butano, bici, ropa tendida |
| `R0161_1` | **Farmacia Cossío** (antes "de la Plaza", a 70 m de la plaza) | 1960 | — | **cruz verde luminosa** que remata la Calle Mayor; báscula; cartel de guardias |
| `R0132_1` · `R0132_2` | Óptica Norte · Pescados Hnos. Ruiz | — | — | gafas en el escaparate · mostrador de mármol visible, suelo mojado |
| Poniente: `R0058` · `R0085` · `R0086` · `M0020_00` | Panadería La Espiga · **Confitería La Pasiega** (antes 2.ª sidrería) · Modas Carmen · viviendas | — | — | hogazas y cesta de reparto · sobaos y quesadas · escaparate que dobla la esquina hacia la plaza · portal |
| `R0128` · `R0185` | viviendas (antes "2.º Hotel") · **Taberna Casa Pedrín** (antes "Bar El Puerto"; el de verdad es `R0043`, en la puerta del muelle) | — | — | fuera de la ruta; sus calles se visten en el ledger |

El resto de fachadas del corte (Pozo, Medio, Solana, Hospital, Levante Sur) entran en `BUILDINGS.md` al construir.
Por defecto son viviendas con portal: se resta antes de sumar.

## 3. Usos por hora

**7–9:** descarga en el muelle del Mercado, el panadero en bici, montaje del mercadillo, cafés en La Plaza.
**9–14:** mercadillo, Ayuntamiento y Caja abiertos, señoras con carro, el cupón.
**13–15:** vermú y menú del día; el mercadillo recoge y deja cartones junto a los contenedores.
**17–21:** terrazas, críos en bici alrededor de la fuente, jubilados en el pórtico, misa de 19:30.
**Noche:** plaza vacía, el reloj, las cajas de luz apagadas; La Plaza cierra a la una.

## 4. Vistas y remates

- **Calle Mayor hacia el norte:** la fuente-farola en el eje y la boca de la plaza entre la esquina de la Caja y Se
  traspasa; los banderines conducen la mirada.
- **De la plaza a la Calle Mayor:** la perspectiva, con los banderines a tres alturas, termina en la cruz verde de la
  farmacia.
- **Hacia el Mercado:** la calle de puestos lleva a su portalón abierto.
- **Desde la boca de la Calle Mayor:** la torre del reloj.
- **Hacia el Muelle:** la Puerta del Muelle con un trozo de mar. Fuera del corte; se anota.

## 5. Recorridos y hueco libre

**Jugador:** spawn → calle del Muelle → plaza por el lado de la fuente → boca de la Calle Mayor → bocacalle.
**Línea de deseo de los vecinos:** Calle Mayor ↔ fuente ↔ Muelle, siempre libre.
**Reparto:** furgonetas por la calle de Levante al muelle del Mercado; el butanero sube la Calle Mayor; el pan en bici
por Poniente. La plaza es peatonal: bolardos y paso de cebra en la boca de la Calle Mayor, y ningún coche aparcado dentro.
**Hueco libre:** la mitad oeste, entre la fuente y la Consistorial, sin nada fijo (verbena, juegos).

## 6. Restar primero

- Fuera el anillo de 19 puestos. Quedan 6 puestos distintos y una churrería en una sola calle hacia el Mercado, con las
  caras a la gente.
- Fuera las furgonetas aparcadas en la plaza y en la Calle Mayor.
- Fuera las farolas exentas del centro de la plaza y de la Calle Mayor: farol de pared (palomilla) en las fachadas.
- Los contenedores van al rincón de Levante.
- Fuera los barriles salvo uno en la sidrería.
- Fuera el rótulo de tienda del Ayuntamiento.
- Fuera los duplicados de Hotel, Mercado y Ayuntamiento como tales.
- Fuera todo objeto de color plano hasta que esté pintado.

## 7. Viñetas (17)

Dueño · hora · motivo.

1. **Mercadillo del martes:** vendedores de la comarca · 8–14 · fruta de la huerta, Quesería La Montañesa, ropa "todo a
   500", menaje, plantas (hortensias), churrería en su caravana. Precios a mano en pesetas.
2. **Descarga del Mercado:** Pescados Hnos. Ruiz · 7–10 · furgoneta isoterma abierta, carretilla, cajas con hielo,
   charco y manguera.
3. **Pórtico de la iglesia:** parroquia · siempre · banco corrido, tablón con esquelas, velas tras la puerta.
4. **Balcón del Ayuntamiento:** Ayuntamiento · 9–14 · banderas, escudo, bandos, moto de la Policía Local.
5. **El cupón:** Manolo, de la ONCE · 9–14 y 17–20 · quiosco en la esquina sur-oeste, tiras de cupones, transistor.
6. **Esquina del Bar La Plaza:** Tino y Mari · todo el día · tres mesas distintas (dos cañas a medias y el periódico),
   sillas de plástico con la marca de una cerveza inventada, pizarra "Menú del día 1.200 pts", caja de botellines en la
   puerta de servicio, toldo medio recogido, un Vespino.
7. **Portal de Doña Remedios:** felpudo, hortensias desbordadas, bombona esperando al butanero, bici, ropa tendida.
8. **Lo cerrado:** Se traspasa, rótulo fantasma de "TEJIDOS LAVÍN", carteles de fiestas encima.
9. **Las fiestas:** comisión de N.ª S.ª del Muelle · banderines cruzando la Calle Mayor a tres alturas, cartel de la
   verbena con la orquesta "Los Satélites" en la esquina y en el bar.
10. **La sidrería:** Pepe Bustamante · mediodía · barril-mesa, culines, serrín, pizarra.
11. **Lo civil:** placas de calle en cada esquina, cebra y bolardos en la boca de la Calle Mayor, cabina y buzón amarillo
    en la boca del Muelle.
12. **La fuente:** placa de 1887 "siendo alcalde…", palomas, bici de crío apoyada.
13. **El escaparate de las teles:** Somarriba · horario comercial · cuatro teles, el mismo telediario, ofertas en pesetas.
14. **Farmacia de guardia:** Cossío · la cruz verde encendida, báscula, carrito de bebé esperando.
15. **La pescadería:** Hnos. Ruiz · mañana · mármol, pizarra "Bocarte 400 pts/kg", cubo y suelo mojado.
16. **El butanero:** martes y viernes · camión parado en la Calle Mayor, jaula de bombonas, una en cada portal que la
    pidió (enlaza con el reparto del plan maestro).
17. **El cajero nuevo:** Caja del Norte · cola de jubilados el día de la pensión, el aluminio reluciente en la piedra vieja.

## 8. Lo que necesito del Owner

1. Visto bueno al brief: programas, renombres, abrir las traseras del lado sur a la plaza, soportales en el
   Ayuntamiento, pórtico en la iglesia.
2. El momento: martes 12:30 con mercadillo (recomendado; la capa se puede retirar) o una tarde sin mercado.
3. El look: empezar por la esquina de prueba V7 (recomendado). ¿Pruebo también la cámara estilo Shenmue y el 640×480
   en 4:3?
4. Si tienes capturas de tu paseo, pásamelas.

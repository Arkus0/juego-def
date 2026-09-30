# LEDGER_MAP - SIN_TERMINAR, night-20260931

Fecha efectiva: 2026-09-30. `night-20260931` se conserva literalmente por el encargo; 31 de septiembre no es una fecha válida.

Fuente: `Docs/evidence/WP-PROD-ENV-01/night2-censo/ledger.json`. SHA256: `aea03eb660f3094e7874aba49c4a284aec9c212c30f1787e91c3a542c9a6c155`. La copia en Captures/censo_noche2 tiene el mismo hash. HEAD al mapear: `21613b9c4c04f242df4320d175215b7a6b73b781` (registro de contexto, no candidate freeze).

Esto es un mapa del censo existente, no un recenso ni una lista validada de objetos del mundo. No hubo acciones en Unity ni cambios de implementación. Todos los 378 registros se conservan con file, texto original, severidad, ubicación, calle, estación y dirección en `Unity/JuegoDef/Captures/n3_sinterminar/workset.json`.

## Recuentos reproducidos

| Concepto | Registros |
| --- | ---: |
| SIN_TERMINAR total | 378 |
| O / Y / R | 342 / 35 / 1 |
| pared_lisa (clasificación del texto) | 277 |
| remate_cubierta_cielo | 80 |
| interior_Ribera | 1 |
| otras | 20 |
| Registros que mencionan alero/alerón | 78 |
| Sujetos cubierta/cumbrera | 49 |
| Archivos diferentes con SIN_TERMINAR | 296 |
| Capturas SIN_TERMINAR faltantes | 0 |

La estimación de 362 paredes lisas no se reproduce. El reparto semántico suma 277 + 80 + 1 + 20 = 378. La etiqueta del ledger mezcla paredes, cubiertas, interiores y props. Las 47 repeticiones exactas de "Cubierta plana cortada contra el cielo sin alero" permanecen como 47 observaciones, sin deducir 47 objetos.

Prioridad de clasificación: interior rojo; pared/fachada/paño o caja arquitectónica lisa; remate/cubierta/cielo restante; otras. Las paredes con una queja mixta de alero se quedan en pared_lisa y llevan `mentions_eaves=true`. El total físico real de paredes o aleros pendientes sigue desconocido.

## Nueve referencias exactas de alero

Son una selección trazable de nueve registros, no un total de nueve aleros existentes ni nueve defectos visualmente confirmados. La lista completa de 80 remates y las 78 menciones literales está en el workset.

| ID / file | Sev | Ubicación | Texto original |
| --- | --- | --- | --- |
| SIN_TERMINAR_0001 / plazas/Cabeza_Puente_c_0_yaw0.jpg | Y | izq plano lejano | fachada naranja recortada contra cielo sin alero, silueta plana |
| SIN_TERMINAR_0165 / streets/Cantabra_eye_fwd_03.jpg | Y | centro fondo tejado | cumbrera sin alero visible contra el cielo en vertice derecho |
| SIN_TERMINAR_0213 / streets/Calle_Alta_C_eye_fwd_00.jpg | O | Fondo centro | Edificios del fondo volumenes simples sin aleros contra el cielo |
| SIN_TERMINAR_0272 / streets/Calle_Alta_C2_eye_fwd_00.jpg | O | centro plano lejano | Fachadas traseras simplificadas sin aleros contra el cielo |
| SIN_TERMINAR_0217 / streets/Calle_Alta_E_eye_fwd_04.jpg | O | Der plano medio-lejano | Edificio azul se corta plano contra el cielo sin alero |
| SIN_TERMINAR_0221 / streets/Calle_Alta_O_eye_fwd_02.jpg | O | Fondo der | Edificio se corta plano contra cielo sin alero |
| SIN_TERMINAR_0223 / streets/Calle_Alta_Salida_eye_fwd_01.jpg | O | Fondo centro | Edificio cortado plano contra el cielo sin alero |
| SIN_TERMINAR_0256 / streets/Ronda_Huertas_eye_fwd_06.jpg | O | Centro plano medio | Fachada del fondo lisa sin alero, cornisa minima |
| SIN_TERMINAR_0284 / streets/Callejon_Arco_eye_fwd_03.jpg | O | der plano lejano | Cubierta plana contra el cielo sin alero |

## Interior rojo de Ribera

`SIN_TERMINAR_0035`, `streets/Ribera_eye_fwd_01.jpg`; Ribera, estación 01, fwd, severidad R, ubicación: izq plano cercano garaje.

> Paredes y suelo del interior en color plano sin textura, caja sin terminar

Captura real: `Unity/JuegoDef/Captures/censo_noche2/streets/Ribera_eye_fwd_01.jpg`; xyz fuente: `[138.1997, 0.479752421, 194.803284]`. Se conserva como claim fuente; este subtrabajo no inspeccionó esa vista.

## Calles peor puntuadas por el censo

Orden: cantidad SIN_TERMINAR, luego R=5/O=2/Y=1, luego nombre. No representa un ranking independiente del producto real.

| Calle | SIN | R/O/Y | Pared lisa | Remate | Otras |
| --- | ---: | --- | ---: | ---: | ---: |
| Ronda_Huertas | 20 | 0/19/1 | 15 | 5 | 0 |
| Calle_Alta_E | 16 | 0/14/2 | 13 | 3 | 0 |
| Ribera | 15 | 1/14/0 | 11 | 2 | 1 |
| Llano | 15 | 0/15/0 | 12 | 3 | 0 |
| Cantabra | 15 | 0/13/2 | 9 | 4 | 2 |
| San_Pedro | 14 | 0/12/2 | 12 | 2 | 0 |
| San_Pedro_Salida | 14 | 0/12/2 | 12 | 2 | 0 |
| Espina_E | 12 | 0/12/0 | 10 | 2 | 0 |
| Capitan_Salida | 12 | 0/10/2 | 8 | 2 | 2 |
| El_Sol | 11 | 0/11/0 | 7 | 3 | 1 |
| Ronda_Mirador | 11 | 0/11/0 | 8 | 3 | 0 |
| Cervantes | 11 | 0/10/1 | 8 | 2 | 1 |

## Muestra 12 pares

Estación 01 de las 12 calles anteriores. Ambos archivos existen, comparten xyz y miran en sentido inverso según capture_positions.json. Las rutas son relativas a `Unity/JuegoDef/Captures/censo_noche2/`. Los hashes y xyz están en el workset.

| Estación | Vista fwd | Vista rev |
| --- | --- | --- |
| streets/Ronda_Huertas/01 | streets/Ronda_Huertas_eye_fwd_01.jpg | streets/Ronda_Huertas_eye_rev_01.jpg |
| streets/Calle_Alta_E/01 | streets/Calle_Alta_E_eye_fwd_01.jpg | streets/Calle_Alta_E_eye_rev_01.jpg |
| streets/Ribera/01 | streets/Ribera_eye_fwd_01.jpg | streets/Ribera_eye_rev_01.jpg |
| streets/Llano/01 | streets/Llano_eye_fwd_01.jpg | streets/Llano_eye_rev_01.jpg |
| streets/Cantabra/01 | streets/Cantabra_eye_fwd_01.jpg | streets/Cantabra_eye_rev_01.jpg |
| streets/San_Pedro/01 | streets/San_Pedro_eye_fwd_01.jpg | streets/San_Pedro_eye_rev_01.jpg |
| streets/San_Pedro_Salida/01 | streets/San_Pedro_Salida_eye_fwd_01.jpg | streets/San_Pedro_Salida_eye_rev_01.jpg |
| streets/Espina_E/01 | streets/Espina_E_eye_fwd_01.jpg | streets/Espina_E_eye_rev_01.jpg |
| streets/Capitan_Salida/01 | streets/Capitan_Salida_eye_fwd_01.jpg | streets/Capitan_Salida_eye_rev_01.jpg |
| streets/El_Sol/01 | streets/El_Sol_eye_fwd_01.jpg | streets/El_Sol_eye_rev_01.jpg |
| streets/Ronda_Mirador/01 | streets/Ronda_Mirador_eye_fwd_01.jpg | streets/Ronda_Mirador_eye_rev_01.jpg |
| streets/Cervantes/01 | streets/Cervantes_eye_fwd_01.jpg | streets/Cervantes_eye_rev_01.jpg |

## Control aleatorio de 20 estaciones

Seed 9303; Python `random.Random(9303).sample(pool, 20)`. Pool estable ordenado por calle e índice, restringido a las 12 peores calles del ledger. Excluye IDs y xyz de la muestra; deduplica puntos xyz compartidos conservando el primer ID lexicográfico. Pool: 43 estaciones. Los 20 puntos y los 12 de la muestra son disjuntos, y todos tienen dos JPG existentes.

| Orden de extracción | Estación | fwd | rev |
| ---: | --- | --- | --- |
| 1 | streets/Llano/00 | streets/Llano_eye_fwd_00.jpg | streets/Llano_eye_rev_00.jpg |
| 2 | streets/Cervantes/03 | streets/Cervantes_eye_fwd_03.jpg | streets/Cervantes_eye_rev_03.jpg |
| 3 | streets/Ribera/05 | streets/Ribera_eye_fwd_05.jpg | streets/Ribera_eye_rev_05.jpg |
| 4 | streets/Calle_Alta_E/00 | streets/Calle_Alta_E_eye_fwd_00.jpg | streets/Calle_Alta_E_eye_rev_00.jpg |
| 5 | streets/Espina_E/04 | streets/Espina_E_eye_fwd_04.jpg | streets/Espina_E_eye_rev_04.jpg |
| 6 | streets/Ronda_Huertas/02 | streets/Ronda_Huertas_eye_fwd_02.jpg | streets/Ronda_Huertas_eye_rev_02.jpg |
| 7 | streets/Calle_Alta_E/02 | streets/Calle_Alta_E_eye_fwd_02.jpg | streets/Calle_Alta_E_eye_rev_02.jpg |
| 8 | streets/Cantabra/02 | streets/Cantabra_eye_fwd_02.jpg | streets/Cantabra_eye_rev_02.jpg |
| 9 | streets/Ronda_Huertas/00 | streets/Ronda_Huertas_eye_fwd_00.jpg | streets/Ronda_Huertas_eye_rev_00.jpg |
| 10 | streets/Ronda_Mirador/03 | streets/Ronda_Mirador_eye_fwd_03.jpg | streets/Ronda_Mirador_eye_rev_03.jpg |
| 11 | streets/Cantabra/00 | streets/Cantabra_eye_fwd_00.jpg | streets/Cantabra_eye_rev_00.jpg |
| 12 | streets/Llano/05 | streets/Llano_eye_fwd_05.jpg | streets/Llano_eye_rev_05.jpg |
| 13 | streets/San_Pedro_Salida/03 | streets/San_Pedro_Salida_eye_fwd_03.jpg | streets/San_Pedro_Salida_eye_rev_03.jpg |
| 14 | streets/San_Pedro_Salida/04 | streets/San_Pedro_Salida_eye_fwd_04.jpg | streets/San_Pedro_Salida_eye_rev_04.jpg |
| 15 | streets/Espina_E/00 | streets/Espina_E_eye_fwd_00.jpg | streets/Espina_E_eye_rev_00.jpg |
| 16 | streets/Capitan_Salida/02 | streets/Capitan_Salida_eye_fwd_02.jpg | streets/Capitan_Salida_eye_rev_02.jpg |
| 17 | streets/San_Pedro/02 | streets/San_Pedro_eye_fwd_02.jpg | streets/San_Pedro_eye_rev_02.jpg |
| 18 | streets/Ribera/04 | streets/Ribera_eye_fwd_04.jpg | streets/Ribera_eye_rev_04.jpg |
| 19 | streets/Ronda_Huertas/05 | streets/Ronda_Huertas_eye_fwd_05.jpg | streets/Ronda_Huertas_eye_rev_05.jpg |
| 20 | streets/Calle_Alta_E/05 | streets/Calle_Alta_E_eye_fwd_05.jpg | streets/Calle_Alta_E_eye_rev_05.jpg |

## Spotcheck visual, seis vistas existentes

Prompt aplicado literalmente:

> Cataloga TODO defecto visible sin piedad. Juzga a escala de paseo y por tramo de calle. No confirmes la mejora: intenta falsarla. Enumera clase, gravedad R/O/Y, ubicación y descripción; distingue lo visible de lo inferido. Excluye solo el maniquí GC2 y la franja central de losas de la espina intencional.

Inspección directa de JPG originales 1920x1080 mediante view_image, sin editor. Juicios append en `Unity/JuegoDef/Captures/n3_sinterminar/ledger_observations.jsonl`, separando visible e inferido.

| File | Resultado contra SIN fuente | Observación |
| --- | --- | --- |
| streets/El_Sol_eye_fwd_01.jpg | not_corroborated | El paño izquierdo se ve de piedra con ventanas, banda y alero; no aparece la fachada lisa sin vanos descrita por el ledger. |
| streets/El_Sol_eye_rev_01.jpg | not_corroborated | La fachada de fondo tiene puerta, dos ventanas y cubierta de teja con remate visible; el portal izquierdo es madera legible. No se ve el parche de hierba inferior derecho reclamado por el ledger. |
| streets/Ronda_Mirador_eye_fwd_01.jpg | not_corroborated | El primer plano izquierdo es piedra y tiene puerta, banda y zócalo. Los tejados de las fachadas visibles llevan aleros; no se ven ramas de árbol atravesándolos. |
| streets/Ronda_Mirador_eye_rev_01.jpg | partially_corroborated | Hay grandes paños laterales sin vanos. El izquierdo tiene zócalo y bandas, así que no se confirma ausencia total de acabado. La vista no muestra la barandilla del mirador descrita por otra entrada. |
| streets/Cervantes_eye_fwd_01.jpg | different_visible_target | El primer plano izquierdo es mampostería, no pared de enfoscado. Hay un paño inferior muy amplio sin vanos en el edificio central del fondo; es un objetivo distinto al localizado por el ledger. El edificio tiene ventanas arriba, textura y bandas. |
| streets/Cervantes_eye_rev_01.jpg | not_corroborated | La fachada izquierda tiene piedra, puertas, balcones, ventanas y alero. No se confirma la pared lisa gigante sin vanos ni la hiedra atravesando alero en el lado derecho. |

Falsificador material: las listas de 15 defectos de Ronda_Mirador fwd01 y Cervantes fwd01 son idénticas y contienen ubicaciones/elementos que no corresponden a las JPG. El_Sol rev01 reclama un parche de hierba inferior derecho ausente en la imagen. Por tanto, los recuentos del ledger sirven para organizar revisitas; no autorizan colocar kits o afirmar mejora por alcanzar una cifra.

Ningún juicio aquí es PASS independiente, ni verifica comportamiento en Play Mode o el estado actual de la escena. No se inferirán IDs de GameObjects a partir de estas capturas.

## Seleccion operativa de 44 recapturas

Campos directos en workset: `sample_pairs` (12), `random_stations` (20) y `validation_files` (44 rutas relativas al censo). `validation_views` expone set, file, station_id, direction y source_position_raw.

Las 44 vistas son 24 de la muestra + una direccion por cada una de las 20 estaciones aleatorias. La direccion sigue el RNG seed 9303 despues de sample(pool,20); no se ha capturado ni alterado ninguna vista nueva.

| Orden | Vista aleatoria seleccionada |
| ---: | --- |
| 1 | streets/Llano_eye_rev_00.jpg |
| 2 | streets/Cervantes_eye_rev_03.jpg |
| 3 | streets/Ribera_eye_fwd_05.jpg |
| 4 | streets/Calle_Alta_E_eye_fwd_00.jpg |
| 5 | streets/Espina_E_eye_fwd_04.jpg |
| 6 | streets/Ronda_Huertas_eye_fwd_02.jpg |
| 7 | streets/Calle_Alta_E_eye_fwd_02.jpg |
| 8 | streets/Cantabra_eye_rev_02.jpg |
| 9 | streets/Ronda_Huertas_eye_rev_00.jpg |
| 10 | streets/Ronda_Mirador_eye_fwd_03.jpg |
| 11 | streets/Cantabra_eye_fwd_00.jpg |
| 12 | streets/Llano_eye_rev_05.jpg |
| 13 | streets/San_Pedro_Salida_eye_rev_03.jpg |
| 14 | streets/San_Pedro_Salida_eye_rev_04.jpg |
| 15 | streets/Espina_E_eye_rev_00.jpg |
| 16 | streets/Capitan_Salida_eye_rev_02.jpg |
| 17 | streets/San_Pedro_eye_fwd_02.jpg |
| 18 | streets/Ribera_eye_fwd_04.jpg |
| 19 | streets/Ronda_Huertas_eye_fwd_05.jpg |
| 20 | streets/Calle_Alta_E_eye_rev_05.jpg |

Los arrays originales de posicion son x,y,z,dir_x,dir_z. No se reinterpretan como una altura ocular garantizada: hay que seguir la convencion de captura existente al recapturar.

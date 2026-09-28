# Visión del juego

## Fantasía y premisa de trabajo

**Vida cotidiana -> investigación -> aventura.** Una persona llega o regresa a una ciudad portuaria ficticia del norte de España hacia 1999–2003 tras el asesinato de alguien cercano. Una fotografía vincula a la víctima con un lugar del puerto. Comercios y vecinos ofrecen versiones incompletas; el jugador debe entender personas, horarios y accesos para seguir el hilo. Víctima, culpable, conspiración, nombres y cronología exacta quedan abiertos.

Herencia de Shenmue II en la estructura: habitar una ciudad, preguntar y observar, alternar tareas cotidianas y avance dramático, y llegar a momentos de acción. Identidad narrativa, visual, espacial y de personajes propia.

## Bucle

1. Salir a la ciudad, elegir a quién preguntar o qué lugar visitar y aprender una referencia reconocible.
2. Contrastar pistas humanas y físicas: fotografía, recibo, llave, horarios, acceso o conducta observada.
3. Vivir el lugar para abrir posibilidades: esperar, trabajar, jugar, entrenar, ayudar, volver a otra hora.
4. Seguir una pista que cambie la situación: conversación, acceso, seguimiento, persecución o pelea.
5. Obtener un dato u objeto que cambie la interpretación de un sitio anterior y abra otra línea.

## Investigación y ciudad

La interfaz primaria es el espacio: escaparates, lonja, turno de un trabajador, entrada de servicio, bar, pensión y callejones. Preguntar «¿has visto a esta persona?», mostrar una foto, inspeccionar un objeto, seguir a alguien, entrar legalmente o mediante una alternativa y regresar más tarde deben sentirse naturales.

Pistas y diarios pueden ayudar a recordar, pero no deben sustituir la investigación por una cadena de waypoints amarillos o una lista abstracta de tareas.

El mapa crece por **cinco zonas compactas de producción**:

- Casco;
- Mercado;
- Muelle;
- Talleres;
- Viviendas.

Casco concentra la nightlife principal sin dejar de ser barrio mixto; Talleres ofrece una nightlife secundaria/alternativa; Mercado mantiene vida de tarde, Muelle trabajo nocturno y Viviendas contraste tranquilo. Ver [`PORT_TOWN_WORLD_MODEL.md`](PORT_TOWN_WORLD_MODEL.md).

El primer slice ocupa una zona pequeña y densa, no un plano de la ciudad entera. A largo plazo se pueden alcanzar 4–5 zonas plenamente útiles y unas 80–120 identidades visibles si producción/QA lo permiten; son orientaciones, no cuotas.

## Personas y tiempo

| Capa | Tratamiento |
| --- | --- |
| A — principales, referencia ~10–15 | Historia, relaciones, conversaciones variables y rutinas con cambios significativos; causalidad avanzada sólo donde aporta. |
| B — interactivos, referencia ~20–40 | Función clara, rutinas y diálogos contextuales, relación con pistas, trabajos o actividades. |
| C — población | Animación y movimiento/reacción local baratos; escasa persistencia individual salvo necesidad. |

Narrative depth y rutina son ejes distintos. Una persona de fondo puede tener un horario creíble sin memoria social profunda. La ciudad cambia a horas comprensibles —negocios abren/cierran, gente aparece en sitios concretos, nightlife altera flujos— sin simular la mente de cada transeúnte.

## Acción y vida cotidiana

- **Combate:** entrenamiento con maestro, sparring, pelea callejera, pequeño torneo o confrontación narrativa. La pelea debe conducir a información, relaciones o consecuencias.
- **Persecución:** reconocer a alguien, seguirlo por una ruta jugable, poder perderlo, conversar o pelear al alcanzarlo y conservar otra vía de investigación si escapa.
- **Actividades:** arcade, dardos, billar, pesca, reparto, descarga de cajas, fotografía, coleccionables o entrenamiento; elegir unos pocos por escena.
- **Progresión:** comprender personas y lugares, conseguir pruebas, ganar confianza y entrenar habilidad abre rutas. Dinero/objetos sostienen actividades; no sustituyen el misterio por un árbol abstracto de mejoras.

## Calidad visual

El juego debe evitar dos extremos: fotorealismo costoso y greybox vestido. La dirección vigente es estilizada low-poly/PS2+ con atmósfera atlántica húmeda, alta densidad peatonal y uso agresivo pero coherente de fuentes reutilizables. Ver [`VISUAL_BIBLE.md`](VISUAL_BIBLE.md).

## Slice conservable — objetivo futuro, 20–30 minutos

Pensión -> fotografía de la víctima -> preguntas en comercios -> pista en el puerto -> acceso por trabajo, permiso u otra entrada -> reconocer/seguir a una persona -> persecución jugable -> pelea o confrontación -> llave/prueba -> regreso a un sitio anterior -> respuesta cambiada -> nueva línea de investigación.

Bar, comercio, arcade, entrenamiento o pequeño trabajo puede ofrecer una distracción breve con valor narrativo/social. Duración, diversión, continuidad y acabado se validan jugando, nunca por documento.

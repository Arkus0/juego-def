# WP-CITY-B0-01 — Fase 1: B0 MERCADO–MUELLE, sector representativo

Status: **READY AFTER WP-CITY-SKELETON-00 PASS**
Class: PRODUCT / KEEPER SECTOR / UNITY
Depends on: `WP-CITY-MASTER-00`, `WP-CITY-SKELETON-00` PASS, bootstrap GC2, ENV kit + `ENV01_AUTHORED` como donante.
Absorbs: los criterios físicos de `WP-PROD-ENV-CASCO-V2-00` (decisión Owner D2, 2026-10-01).
Does not replace: el gate de contenido de `WP-CITY-URBAN-01` (civiles CHAR, diálogo/UI de investigación), que se aplica después sobre este B0 espacial.

## Objetivo / claim

B0 es un **sector terminado** en el sentido del encargo: escena persistente authored conectada a sus vecinos, rutas jugables con Player GC2, interiores en tres escalas recorribles, accesos públicos/servicio/privados verdaderos, revelación progresiva del puerto, ruta directa y ruta elevada con experiencias distintas, loops útiles para seguir y perseguir, y vida suficiente para que el recorrido tenga sentido. Demuestra escala, circulación, interiores y relación con el puerto y deja probado el **kit de interiores v1** que el resto de sectores reutiliza.

## Contenido obligatorio

- Alojamiento / ancla de retorno (Pensión M01, grande, 2 plantas jugables).
- Mercado/actividad (plaza A + Mercado de abastos M02, grande, dos cotas, conexión PUB-H).
- Comercio cotidiano y testigo (tienda S M03 con almacén SRV a la terraza; café-bar M04; pequeños M06–M12 según plan).
- Ruta comercial (B01–B03), revelación progresiva del puerto (A → E → P), borde portuario público (P–Q) separado de la zona laboral (patio y muelle de armadores, SRV/CTL), ruta elevada (terraza El Muro V–O y Escalera del Muro), loop de retorno, elección útil de follow/chase (E–P–Q–O–E, A–S–E–O–V–A).
- Bar del puerto U03 (mediano) en P; exterior completo del hotel M05 con vestíbulo accesible (resto del interior en el sector S2).
- Costuras reales con vecinos: arrival_w (Calle de la Ría), casco_n (Cuesta del Mercado, Escalera de la Atalaya), homes_ne (Calle Nueva), quay_e (Calle del Muelle).

## Criterios heredados de CASCO-V2-00

Programa y grafo de accesos congelados antes de la geometría; FacadeCells agrupadas en SemanticBuildings sin particiones/colliders internos heredados; ≥3 programas accesibles distintos; ≥6 estancias útiles de actividad; un edificio con ≥2 plantas jugables y un programa profundo de ≥3 estancias (Pensión); utilidad medida sobre geometría (A = m² útiles de actividad, U = puntos de acción distintos con receptor de runtime; sin estancias simuladas, pasillos ni marcadores duplicados); 100 % del suelo exterior de B0 particionado sin residuales; ninguna puerta al agua sin llegada real; ventanas de plantas no jugables honestas.

## Prueba de recorrido (Player GC2, grabada y con receptores)

El protagonista sale de la pensión, entra en un comercio, cruza la plaza y ve parcialmente el puerto. Puede bajar directamente (E–P) o tomar la terraza elevada (V–O). Observa a un NPC, lo sigue, lo pierde brevemente tras un giro y lo vuelve a encontrar; anticipa su destino porque conoce las conexiones. Una persecución corta usa un loop. Más tarde vuelve al comercio por otra ruta y encuentra actividad que da sentido al trayecto. Los NPC se mueven con instrucciones nativas GC2 (Move To / Wait) sobre NavMesh; la persecución y el seguimiento son pruebas espaciales representativas, **no** sistemas de gameplay implementados.

## Runtime adicional

- 6 agentes NPC de escala concurrentes durante 10 minutos (tendera, vendedor, cliente del bar, operario del puerto, dueña de la pensión, NPC seguido): 0 llegadas requeridas bloqueadas, 0 interpenetraciones que impidan el uso, 0 errores de runtime.
- Puertas GC2 Core (triggers) en todos los accesos jugables; condiciones SRV/PRV/PUB-H con variables GC2 de depuración.
- Cámara: giros de 360° en puntos de actividad, salidas en reversa, rellanos ocupados; perfil de cámara de interior en tercera persona; 0 defectos que oculten la interacción o la ruta.
- Negativos: patio CTL y muelle de armadores cerrados al público; puertas SRV/PRV no crean atajos públicos; plantas no jugables inaccesibles; sin escape al agua.
- Persistencia: guardar, reabrir, domain reload, reinicio del editor y Play.
- Profiler en vistas representativas, comparado con la Fase 0.

## Forbidden scope

Rediseñar CASCO/VIVIENDAS/TALLERES más allá de sus costuras; sistema de rutinas, reloj, diálogo, inventario o combate; generadores de interiores; compras; cambiar conectividad pública aceptada sin enmienda; atajos públicos a través de interiores; ensanchar toda la red para esquivar problemas locales.

## Evidencia y cierre

`Docs/evidence/WP-CITY-B0-01/`: programas y grafo de accesos previos a la geometría, planos y secciones, ledger de utilidad A/U, partición de suelo, ledger de edificios con FacadeCells, linaje del kit de interiores, receptores de rutas/puertas/escaleras/cámara/negativos/NPC, vídeo o secuencia de capturas de la prueba de recorrido, persistencia, profiler, limitaciones explícitas, pre-review estricto, SHA congelado, veredicto visual del Owner y Reviewer independiente fresco.

# CITY-00R — fuente y candidato de arquitectura

Status: **ACCEPTED / DOCSYNC COMPLETE**
Date: 2026-09-30

## Proveniencia aceptada

- Accepted candidate: `09f8b226f432ff8b1bec921ce2a33b88ce3820da`.
- Canonical PR: `#19`.
- Independent Reviewer PASS: review `#5369675521`.
- Merge commit: `8a371790c055f8088fafd231fd4eb7c8873f3012`.
- DocSync closure: [`DOCSYNC.md`](DOCSYNC.md).
- El PASS acepta CITY-00R y el contrato del piloto; **no** acepta la implementación CASCO-V2, ENV01, Director, ENV02 ni CITY01.

## Resultado causal y alcance

Los dos contratos y la [arquitectura propuesta](../../design/COMPACT_SEMANTIC_CITY_REBASELINE.md) separan grano visual, edificio funcional y programa interior. El cambio responde al acoplamiento `plot -> BuildingSpec -> Build` observado; preserva look, cinco identidades, B0 y trabajo útil de fábrica/Director. No hay implementación Unity ni modificación de ENV01. Las nuevas cotas numéricas son propuesta del Arquitecto, no evidencia de una ciudad V2 ni aceptación del Owner sobre esos detalles.

## Fuentes completas y estado exacto

- Base de este candidato documental: `main` **`088a23bc802145d1f4c322a8b6f936a1778c1921`**, consultada en GitHub y fetch el 2026-09-30; incluye las revisiones Director D4/extractabilidad/provider neutrality y ENV02, que aún no estaban en el checkout ENV01.
- ENV01: rama `worker/prod-env-01`, HEAD **`246756c72d7181cd034c04c6b5cde163d076cb66`**, [PR #10 abierta](https://github.com/Arkus0/juego-def/pull/10) al inspeccionar. Se leyó implementación/evidencia efectiva, distinguiendo los cambios locales. ENV01 no se marcó PASS/merged. Director D0 [PR #16 abierta](https://github.com/Arkus0/juego-def/pull/16); no se infirió aceptación de D0/D1.
- Leídos completos los nueve documentos pedidos: los cuatro design y CITY00/CITY01/ENV01/ENV02 en ENV01; Director completo en main. También se leyeron completos roadmap/índice actual, visión/biblia visual, research de pipelines, fuente/reuse/handoff CASCO y arquitectura GC2/autoría. CITY handoff/B0/knowledge y CITY00/CITY01/ENV01 eran idénticos entre esos dos commits; ENV02/Director/roadmap se reconciliaron con main actual.
- CITY00 conserva accepted candidate `e77e4b300e16bb2b880f8ace86ef488903fde450`, PR #6, merge `2fdd75d6db10d71e5676c0b0d1c161d100e11c15`; ASSET/bootstrap se consumen, no se re-prueban. ANIM01 aceptado sigue independiente. Las revisiones de contratos del Director no se confunden con PASS de su implementación.

El checkout original tenía cuatro archivos Editor ENV modificados, materiales/`EnvLayoutEditor` y evidencia nocturna sin commit. No se recogieron, revirtieron o incorporaron al candidato. Sus capturas/receipts sin commit no representan el SHA versionado. Para el piloto se exige una nueva referencia exacta reconstruida/capturada en aislamiento. Las capturas legacy sirven aquí para estudiar carácter, no para certificar un A/B exacto ni el estado del Editor.

## Observaciones reproducibles

Fuente de números: `Unity/JuegoDef/Assets/JuegoDef/Env/Specs/districts/ENV01_Casco_District.json` del SHA ENV01; mediciones y lista de K2 en [`SOURCE_MEASURES.json`](SOURCE_MEASURES.json).

- 311 plots no-wall, marco `district=[[0,0],[196,236]]`, 46.256 m² de marco.
- Frente min/mediana/max: 1,847 / 6,756 / 16,414 m; profundidades 4/6/8 m.
- Mediana del rectángulo frente×fondo: 47,488 m² **brutos nominales**, no área interior útil y no suma de huellas resueltas.
- K2: 23 plots no-wall, frente a plaza/Ribera/río, mezcla comercial/residencial y cotas. Se selecciona la manzana completa; K11 (19) también entraba en tamaño, pero concentra callejas/relieve y ofrece menos contacto con plaza/ribera. K10 (27) excede el rango inicial. No se eligió un fragmento fácil de una manzana mayor.
- `EnvDistrict.BuildRows` / `SpecOf` generan una unidad y `BuildingAssembler.Build` por plot. `BuildingSpec.depth` restringe cubiertas a fondos de kit; `floors` controla plantas exteriores; `interior` sólo plantilla shop/lodging. `EnvTemplates.ShopInterior` usa fondo por defecto 4 m. `GlassRoom` simula habitaciones detrás de vidrio: no prueba accesibilidad.
- [`VALIDATION.json` versionado](https://github.com/Arkus0/juego-def/blob/246756c72d7181cd034c04c6b5cde163d076cb66/Docs/evidence/WP-PROD-ENV-01/VALIDATION.json) declara 0 problemas, 370 thresholds cerrados y 0 abiertos walkable en CASCO. Es un reporte guardado, no una ejecución de Unity en esta tarea. Las sondas 139/139 históricas son evidencia de rutas, no de programa interior.
- El estudio histórico reporta 1.438 m de red / 69–23–8% de grades y 311 plots. Se conserva como referencia reportada. No se declara medido otra vez el recorrido ni se acepta toda la evidencia nocturna: `LEDGER_MAP`/`C_EXPERIMENT` muestran que conteos textuales o checks verdes pueden no demostrar mejora visible.

Inspección visual directa (archivos originales) de `captures/cohesion/after/S02_espina_comercios.jpg`, `A02_aerea_borde.jpg` y `micro-polish/pass2/alleys/_pair_Llano.jpg`: se ve ritmo de frentes estrechos, alternancia piedra/revoco y cubiertas/aleros; vista de conjunto más extendida y traseras menos resueltas. Son muestras de estilo a diferentes escalas, no auditoría completa ni prueba causal de todas las zonas residuales. El diagnóstico de inutilidad/threshold fino también consume la dirección explícita del Owner, no se deduce sólo de una foto.

## Dependencias y reutilización

CITY00R requiere CITY00 aceptado y referencia exacta como input; piloto requiere CITY00R/ASSET/bootstrap aceptados y snapshot ENV01 reproducible. Ninguno exige ENV02/Director/CITY01. ENV02 añade rebaseline/piloto a sus gates ENV01/Director; CITY01 añade la gramática/piloto y conserva M0/CHAR/ANIM/UI. Los [dos DAG](../../design/COMPACT_SEMANTIC_CITY_REBASELINE.md) distinguen gates y handoff.

| Candidato existente | Disposición en esta arquitectura | Motivo |
| --- | --- | --- |
| kit/derivados/catálogo/materiales ENV01 | USE | lenguaje visual y producción útil; no nueva adopción externa |
| ensamblador por plot / shop threshold | ADAPT posteriormente sólo si el piloto lo exige; USE como piezas | no autoridad suficiente para edificio/programa mayor |
| osm_building_grammar / estudio OSM/IGN | REFERENCE_ONLY aquí | ya dispositionados en ENV01; no volver a descargar ni copiar geometría para cerrar docs |
| Unity/GC2/operador/Blender admitidos | USE en futuro piloto | camino actual; cero llamadas Unity/Blender en este candidato |
| generadores Auto-Building / Geo-Buildings / interiores | DEFER | no necesidad demostrada; no compra/adopción |
| Director D0/D1 y reparación transaccional | USE como trabajo vigente independiente | no invalidar ni requerir su aceptación para el piloto |
| merge/programme/playable floors en Director | DEFER | sólo preguntas de handoff; contrato posterior depende de evidencia física |

## Pre-review documental

Releídas Acceptance, Forbidden scope y DoD de ambos nuevos contratos, más los contratos afectados. Revisión completa del diff de main al candidato: sólo Docs. No se emite PASS independiente.

Falsificadores intentados y cierres de contrato:

- Pocas propiedades en una ciudad enorme: envolvente/red/distancias también limitadas y espacios scenic internos contados.
- Cumplir orientación rellenando: no hay mínimos 90/30 ni requisito exacto 2–4; cierres/quietud permitidos con uso; presupuesto mayor requiere enmienda.
- 311 células mecánicamente agrupadas para conservar toda la superficie: queda explícitamente fuera de este piloto y requiere selección/reducción posterior, no mera división de IDs.
- Patio/gap «servicio» sin acceso: partición + prueba de capacidad/usuarios/soporte, no etiqueta.
- 6 edificios sólo renombrados: deben ser unidades contiguas con programa/circulación, sin paredes/colliders de cubículos heredados.
- Base cero produce ratio infinito: piloto añade pisos absolutos 120 m²/6 usos, programas y habitaciones, ocupación/cámara/verticalidad; multiplicadores nunca bastan.
- Mejor utility destruye look: gate conjunto, mismas vistas/settings y Owner + Reviewer; no compensación entre ejes.
- Cámara/NPCs solos esconden fallo: recorrido bidireccional, 4 agentes concurrentes/10 minutos y accesos negativos.
- Ciclo piloto→Director→piloto: Director genérico preservado; handoff semántico informativo/posterior; piloto operador/native sin gate Director.
- B0 reemplazado por CASCO: selección/roles/gates B0 se conservan y piloto no cuenta como integración ni batch Director.

Validación local: selección/medidas desde `git show` al exact ENV01 SHA; suma de presupuesto/partición esquemática; distancias del grafo; ausencia de ciclos; enlaces locales cambiados; `git diff --check`; scope únicamente Docs. No tests Unity, pruebas runtime o aprobación subjetiva nueva en esta tarea. El Reviewer deberá comprobar fuentes, viabilidad y contratos desde el SHA final mostrado en el handoff de revisión.

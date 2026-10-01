# Strict Worker pre-review — ENV01 authored

Resultado Worker: **READY FOR INDEPENDENT REVIEW**. No independent PASS, no merge. La identidad exacta final se fija por el único commit de esta migración y queda publicada como `PRODUCT_SHA` en la PR y entrega; cualquier commit posterior exige nuevo freeze.

## Relectura de contrato y diff completo

Se contrastaron Acceptance/DoD/Forbidden del WP con el brief Owner de migración, sin redesign, density, consolidation ni nuevo generator. Baseline `e3a012e4acf50b99413df16adfcd9444355cb691`. El diff de scripts existente sólo añade guards, la identidad pasiva y una migración/inspección explícita; dos llamadas del overlay previo requerían reparación mínima para compilar Unity 6. No se incluyen las modificaciones locales ajenas ni Director D1 local no versionado. No hay cambios en Packages, ProjectSettings, spec/trace, grammar, assets originales, interiores ni GC2/vendor privado.

El diff masivo de assets es el snapshot de 780 assets ya existentes, no nuevos módulos/art: GUIDs desacoplados, contenido/importer settings verificados y lineage completa. Dos escenas grandes se guardan en LFS. El inventario añadido contiene exactamente 49 contenedores/anchors sin geometría y 370 componentes pasivos de identidad. El transform de prueba volvió al original.

## Falsificadores intentados y resultado

| Posible falsificador | Evidencia / resultado |
|---|---|
| Sólo algunas fachadas coinciden; desaparecen otros edificios | comparación de todos los 29.176 renderers y 21.102 colliders, 311 grupos inventariados, shapes/estado/assets y matrices; digests source=reference=authored final |
| Renders verdes pero meshes/materiales/importers distintos | hashes reales del cierre congelado, metadata y subasset IDs; snapshots íntegros, cero refs a Derived/ENV/spec/prefab |
| Scene reload funciona por statics/caches; reiniciar destruye edición | prop movido y guardado; explicit domain reload y cambio real de proceso Unity 51204→51000 mantienen su transform y población completa |
| Play genera reemplazos o revierte el prop | edición persiste dentro/fuera de Play; población ambiental intacta; segundo Play con sources exactos candidato, cero prefabs/errores |
| Rebuild de un chunk/fila reautoriza aunque el menú esté protegido | seis rutas probadas y siete con sources limpios, incluyendo Begin/BuildRows/Finish/RebuildRow/ApplyOps/NewStage/BuildRig: rechazo anterior a la mutación |
| Protección sólo funciona en escena activa o sólo por nombre | prueba con escena ordinaria activa y authored cargada additively: bloqueado; guard también inspecciona marcador serializado en roots |
| Duplicate geometry escondida tras hierarchy cleanup | misma población y multisets completos; sólo 49 objetos organizativos, cero geometría nueva y cero IDs duplicados |
| Visual perdido desde escala de producto | vistas de plaza/Torre, río, aérea y captura real tercera persona en Play inspeccionadas; contenido conservado. Se mantienen shaders animados, por lo que no se exige igualdad temporal de píxeles |
| Fuente original sustituida/reconstruida durante migración | hash original y cada source asset/meta raw intactos; se preserva además reference versionada, sin ejecutar builder |
| Dependencia en cambios previos no incluidos en PR | compilación/auditoría/Play con sources exactos del índice y sin Director local; siete guards siguen bloqueando; bytes locales restaurados después |
| Todo funciona localmente pero Git excluye lo necesario / cambia EOL | export checkout-index con LFS smudge: 45 checks correctos, assets canónicos completos, sin original ignorada ni local untracked; escenas de 133.550.498 y 118.929.900 bytes presentes |
| Candidatos de agrupación usan edificios que no existen | 342 propuestas resueltas contra IDs y bounds reales; sin selección ni fusión. AABB se declara heurístico, no contacto exacto ni identidad gameplay |

## Procedencia y límites

Native Unity 6000.3.24f1, APIs inspeccionadas por reflection; assets existentes con la procedencia de ENV01, sin compras/adopciones nuevas. Research/reuse disposition en WP. Git LFS 3.5.1 ya instalado, sólo transporte de escenas grandes.

No se reclama nuevo NavMesh, road ownership por mesh, interior gameplay completo ni accepted look/density. Suelo por material conservado; street outlines son anotación, no autoridad para regenerar. GC2/Quaternius provisionados y rig/shaders de presentación permanecen. La referencia versionada comparte assets estáticos con authored; una edición posterior de un asset compartido debe tratarse deliberadamente.

Checks reproducibles en `VALIDATION.json`, `CANDIDATE_CLEAN_*.json`, `PORTABLE_CHECKOUT.json`; manifests y captura física en esta carpeta. Las pruebas verdes constituyen readiness de Worker; el Reviewer debe derivar sus propios falsificadores sobre el SHA congelado.

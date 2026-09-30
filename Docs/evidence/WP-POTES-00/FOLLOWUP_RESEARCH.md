# Additional source attempts and disposition

Retrieval: 2026-09-30 UTC. This document records the remaining source investigation;
it does not certify the missing exterior facts. Request URLs, response byte counts,
SHA-256 and retrieval times are in
[`sources/FOLLOWUP_RESEARCH_RECEIPTS.json`](sources/FOLLOWUP_RESEARCH_RECEIPTS.json).
Original regional responses remain in the external acquisition cache.

| Candidate / exact service | Observed result | Disposition |
| --- | --- | --- |
| Cantabria `Cartografia_Topografica/MapServer/273`, points on elevated construction | 76 points in the bounding rectangle. They carry point Z/Cota, but no classification as ridge, eave, roof-plane junction or doorway. Service group says CBT23; layer description references BTA 2010. Exact point survey epoch and vertical accuracy are unresolved. | **REFERENCE_ONLY**; cannot convert the largest nearby Z into a building's ridge height. |
| Same service `/274`, points on terrain | 3 points in the bounding rectangle; insufficient controls for all bridge decks, stairs, thresholds and landings. | **REFERENCE_ONLY**; not a substitute for the missing local level survey. |
| Same service `/277`, road planimetry | 128 line features, all **3,135** returned vertex Z values are **0**. Plan lines do not resolve the walking level or individual threshold. | **REFERENCE_ONLY**; do not flatten the selected town to Z=0. |
| Same service `/279`, other planimetry | No features returned in the bounding rectangle. | **NOT_MATERIAL** to closing the present gaps. |
| Same service `/280`, hydro planimetry | 71 line features, all **309** returned vertex Z values are **0**. River/land-cover lines are not certified retaining-wall crests or the parapet/bridge outline. | **REFERENCE_ONLY**. |

The first broad `f=pjson` request timed out; a bounded retry with `f=json` completed.
Successful data, rather than the timeout, determine the dispositions above.

Regional source links: [service](https://geoservicios.cantabria.es/inspire/rest/services/Cartografia_Topografica/MapServer),
[point layer](https://geoservicios.cantabria.es/inspire/rest/services/Cartografia_Topografica/MapServer/273).
These data are not silently licensed as IGN CC BY. Regional terms are
[Decree 87/2013](https://boc.cantabria.es/boces/verAnuncioAction.do?idAnuBlob=260596),
with the physical-support charges removed by
[Decree 102/2018](https://boc.cantabria.es/boces/verAnuncioAction.do?idAnuBlob=334009).
The [official usage FAQ](https://www.territoriodecantabria.es/cartografia-sig/descargas-y-politica-de-licencias/preguntas-frecuentes)
distinguishes auxiliary use in projects from direct resale and requires attribution
and acceptance of its terms on redistribution. The present commit retains research
receipts and source limitations, rather than redistributing these regional geometries
or adopting them as production authority. No paid dependency or licence purchase
was made.

## Supplementary street photograph

Google Maps photo `CIHM0ogKEICAgIDqp5OgwQE`, **Felix Ludeña (ANDiP.)**, displayed
**July 2021**, title **Calle Cántabra**:
[pinned view](https://www.google.com/maps/@43.1492857,-4.6254241,3a,75y,90t/data=!3m4!1e1!3m2!1sCIHM0ogKEICAgIDqp5OgwQE!2e10).

The street is narrow and the photograph shows paving, shop canopies, merchandise
and upper balconies. The displayed photo coordinate and POI point are well outside
the selected cadastral core. **Do not use that coordinate as the camera position.**
Unambiguous per-body/edge registration, complete ground openings and the hidden
upper/rear roof planes are not resolved. Disposition: **REFERENCE_ONLY**, low
confidence for individual-body assignment. No image is redistributed.

The March 2019 river panorama corroborates the exposed river frontage and bank-level
relationship. The individual cadastral photos supply stronger per-parent frontage
identities, but none of these sources supplies all the missing faces and controls.
Photographs are references to observed facts; existence of a URL does not close a
facade-coverage or calibration gap.

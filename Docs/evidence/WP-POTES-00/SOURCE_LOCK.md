# Source lock — WP-POTES-00

Status: **REPRODUCIBLE REFERENCE PRODUCT / EXTERIOR HANDOFF NOT READY**.
Retrieval: 2026-09-30 UTC. Exact URLs, response headers, bytes and SHA-256 values are
in [`sources/ACQUISITION.json`](sources/ACQUISITION.json); the source crop, transformed
local geometry and sample grid are in [`sources/LOCAL_SOURCE_PRODUCT.json`](sources/LOCAL_SOURCE_PRODUCT.json).
The source lock does not certify an unobserved facade or a street survey.

| ID | Identity / version | Authority and limit | State / confidence | Usage |
| --- | --- | --- | --- | --- |
| CAT-BU | DGC INSPIRE Buildings, municipality **39055-POTES**, ATOM release **2026-08-21**; `A.ES.SDGC.BU.39055.building.gml` in municipality ZIP | Pinned exterior surfaces, source identities, reported geometry accuracy and condition. A cadastral reference can have multiple disconnected exterior surfaces. A record is not automatically an independently verified physical building. | Source geometry `MEASURED`; identity cross-check `DERIVED`, medium | DGC INSPIRE licence; original archives not redistributed. |
| CAT-BU-PART | Same release, `A.ES.SDGC.BU.39055.buildingpart.gml` | Different floor counts and plan regions inside the exterior. **Parts do not create POT-B IDs.** Above/below-ground counts are not metric heights. | `MEASURED`, medium | Same licence. |
| CAT-CP | DGC INSPIRE Cadastral Parcels, 39055, **2026-08-21** | Parcel geometry and source reference, including cut outer parcels. This does not establish ownership, public access or a building identity. | `MEASURED` geometry; overlays `DERIVED` | Same licence. |
| CAT-AD | DGC INSPIRE Addresses, 39055, **2026-08-21** | Entrance locators, number and street reference. Not an opening survey, door width or the only entrance. Shared locators do not give every surface a door. | `MEASURED`, medium | Same licence. |
| CAT-PHOTO:`ref` | Official GML document link to `OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral=ref`; individual SHA-256/EXIF/retrieval receipts in source product | Photographic reference, explicitly **NotOfficial** in GML. Reviewed First Slice photographs mostly carry **2015-11-05** EXIF dates; some have no date. EXIF is a file timestamp, not an independently verified survey date. | Observations `VISUAL_ESTIMATE`; occluded/unseen facts `UNKNOWN` | Reference only. URLs/hash/view metadata committed; **no cadastral photo committed**. |
| IGN-MDT05 | IDEE WCS `Elevacion4258_5`, selected bbox, exact response hash | 5 m terrain sample grid and broader relief. Cannot resolve bridge decks, steps, doorway levels or retaining crests to 0.5 m. | Sample interpolation `DERIVED`, low for streets | IGN licence compatible with CC BY 4.0. |
| IGN-PNOA | IGN PNOA MA WMS `OI.OrthoimageCoverage`; EPSG:25830 bbox **367865,4779010,368080,4779250**, 1720×1920 raster; `OI.MosaicElement` GetFeatureInfo reports **2023-08**, native resolution **0.15 m**, true ortho **NO** | Roof/public-space visual cross-check. Roof displacement/parallax prevents treating a roof silhouette as the ground footprint. 0.125 m requested pixels do not improve native resolution. | Visual estimates, medium; source date measured from service response | Obra derivada de PNOA 2023, CC BY 4.0 IGN/CNIG y Gobierno de Cantabria. See map attribution below. |
| OSM | Overpass extract base **2026-09-30T20:08:35Z**, exact query + response SHA; each way version/time retained | Street topology, bridge/passage layers, plaza outline, river axis and building cross-check. **Centreline != width; river axis != banks.** Tags may have historical source dates. | Projected/clipped geometry `DERIVED`, medium | © OpenStreetMap contributors, ODbL 1.0. OSM-derived data remain identifiable and attributed. |

## Official acquisition and constraints

- [DGC INSPIRE service index](https://www.catastro.hacienda.gob.es/webinspire/)
  links the BU, CP and AD municipal ATOM feeds. Province 39 entries resolve
  municipality **39055**; exact feed-to-ZIP URLs are retained in the manifest.
- [DGC INSPIRE licence](https://www.catastro.hacienda.gob.es/webinspire/documentos/Licencia.pdf)
  permits transformed added-value products, including commercial use, and excludes
  redistribution of untransformed original data. This repository contains a
  bounded coordinate-transformed, annotated reconstruction reference product;
  not municipal GML/ZIP downloads or a replacement cadastral service.
- [IGN data policy](https://www.ign.es/web/politica-datos) and
  [IGN use licence](https://www.ign.es/resources/licencia/Condiciones_licenciaUso_IGN.pdf)
  govern the terrain and PNOA derivatives. Attribution: **Obra derivada de PNOA
  2023, CC BY 4.0, Instituto Geográfico Nacional/CNIG y Gobierno de Cantabria**;
  terrain: **Obra derivada de MDT05, CC BY 4.0 IGN**. Retrieval date is known;
  the underlying MDT survey date is `UNKNOWN`, not 2026.
- [OSM copyright/licence](https://www.openstreetmap.org/copyright): topology and
  cross-check derivatives use **© OpenStreetMap contributors, ODbL 1.0**. This
  reference database does not convert that licence into a proprietary one.
- A Google Maps public panorama was inspected as a supplementary reference:
  `CIHM0ogKEICAgICErL709gE`, **KTM Laranjinha**, displayed **March 2019**, at
  **43.1533337,-4.6245592**. It confirms the two river banks, bridge approach,
  retaining wall and different exposed levels. It does not resolve all distant
  or blurred openings. No screenshot/photo from Google is redistributed.
  [Open the pinned panorama](https://www.google.com/maps/@43.1533337,-4.6245592,3a,90y,90t/data=!3m4!1e1!3m2!1sCIHM0ogKEICAgICErL709gE!2e10).

## Reproduction

The bounded tool is [`Tools/potes_reference.py`](../../../Tools/potes_reference.py).
It uses Python, Shapely, PROJ/pyproj and Pillow; exact versions are in
[`sources/TOOL_VERSIONS.json`](sources/TOOL_VERSIONS.json). No runtime/game dependency
or paid tool is adopted. Install these from PyPI in an isolated tool environment.

```powershell
python Tools/potes_reference.py build
python Tools/potes_reference.py check
python Tools/potes_reference_checks.py
```

Those commands use the committed transformed source product offline. Acquisition
reproduction: fetch the manifest URLs and the exact `OSM_QUERY.txt` to an external
cache; check each recorded SHA-256; unzip the three municipality archives without
changing their files; then:

```powershell
python Tools/potes_reference.py import --cache <external-cache>
python Tools/potes_reference.py build
python Tools/potes_reference.py check
```

A later live endpoint response is not the pinned source merely because its URL is
the same. Hash mismatch requires explicit re-lock/revalidation. The committed
reference product retains all selected polygons and enough neighbouring surfaces
to reproduce membership/exclusion and sector seams after live services change.

For the OSM request, URL-encode the committed query as the `data` GET parameter on
the recorded interpreter endpoint. The OSM receipt records the response hash and
base epoch; HTTP response headers were not retained for that request. Do not infer
an absent header from another source. A historical re-query can recover topology,
but is not a byte-identical substitute for the pinned response/product without
verification.

Metric GeoJSON files explicitly declare EPSG:25830; they are **not RFC7946 WGS84**.
Set that CRS when opening them in GIS. Local-game geometry is separated from metric
source geometry; do not interpret eastings as Unity positions.

## Facts that remain unresolved

No source supplies a complete metric opening survey for the First Slice, full
coverage of each exposed rear/return facade, a complete traced compound roof graph,
or bridge/street/threshold levels. `UNKNOWN` is recorded per body and public element.
This is a material blocker to the WP's complete visual handoff, not permission to
randomize a facade or let the next visual Worker discover the missing layout.

Further regional cartography and a July 2021 public street photograph were
investigated; their exact receipts, limitations and REFERENCE_ONLY dispositions
are recorded in [`FOLLOWUP_RESEARCH.md`](FOLLOWUP_RESEARCH.md). They do not resolve
the missing street/roof point roles or complete opening coverage.

`check` exits **0** only when both geometry and WP readiness are clear, **1** for a
geometry/integrity error, and **2** for surviving material claim blockers. A green
geometry result is not a green workpack result.

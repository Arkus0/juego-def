# Sector 01 — pinned reference index

Status: **INDEX COMPLETE / EXTERIOR COVERAGE INCOMPLETE**. A linked image is not
certification of all faces, openings, roof planes or levels. No third-party facade
photograph is stored in this repository.

Source epochs, rights and acquisition receipts: [`../SOURCE_LOCK.md`](../SOURCE_LOCK.md),
`../sources/ACQUISITION.json` and `../sources/LOCAL_SOURCE_PRODUCT.json`.
Geometry is keyed by immutable POT ID and unchanged cadastral exterior surface;
a photograph keyed by a parent cadastral reference can show adjoining bodies.
Photo camera position, lens and capture date are UNKNOWN unless expressly recorded.
EXIF below is a file timestamp, not a certified survey date.

## Shared views and ground authority

- [PNOA 2023-08 reference](../maps/pnoa_2023_reference.jpg) and
  [body-ID overlay](../maps/pnoa_perimeter_overlay.jpg): roofs, broad public surfaces
  and adjoining context. Non-true-ortho displacement prevents metric ridge/ground equivalence.
- Footprints, source parts/floors, source entrance locators and non-party-edge
  candidates: [`BUILDING_LEDGER.json`](BUILDING_LEDGER.json). Edge candidates are
  not certified street facades. Source entrance locators do not measure doors.
- [Public panorama, KTM Laranjinha, March 2019](https://www.google.com/maps/@43.1533337,-4.6245592,3a,90y,95.32h,90t/data=!3m4!1e1!3m2!1sCIHM0ogKEICAgICErL709gE!2e10):
  river facade, both banks, paved upper approach and lower retaining/walk relationship.
  Visible perspective is supplementary; distant/blurred openings and street-side
  entrances remain unresolved. This panorama position is separate from the proposed
  comparison-camera positions in SECTOR_PACK.md. No screenshot is redistributed.

## Per-body photo, coverage and blockers

### POT-B004 — First Slice

- Unchanged source surface: `8093401UN6789S/surface-1`; plan area **68.446 m²**.
- [Pinned facade endpoint](https://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral=8093401UN6789S); receipt result **IMAGE**.
- SHA-256: `24744555c8b4af182b12e82b1e33ec6f0c2e16be7a4536729c33579299a640bd`.
- EXIF file timestamp: `UNKNOWN`; dimensions: `[1920, 1080]`.
- Photo viewpoint/calibration: **UNKNOWN**. The named parent record does not certify
  the ownership of every neighbouring facade visible in the picture.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8093401UN6789S`):
Corner volume: exposed timber grid over pale ochre render on two visible upper storeys; unequal wall planes; projecting eaves. Left return and right front have different opening rhythm. The visible facade is not a standard identical-bay row.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8093401UN6789S`):
Three unequal opening groups in each visible upper band; the middle top group is tall and guarded. Ground is outside the usable frame.

Registered plane `POT-B004-CIMAVILLA`: **footprint**, ring edges `[2]`; 6 observed opening groups.
Coordinates and source/photo hashes: [`../FACADE_TRANSCRIPTION.json`](../FACADE_TRANSCRIPTION.json).
Stations are visual estimates on the unchanged wall edge chain; unsolved stations stay UNKNOWN.
Upper two bands partly visible; ground and principal entrance unresolved.

| Photo band | Observed groups | Count coverage |
| --- | ---: | --- |
| U1 | 3 | OBSERVED_MINIMUM |
| U2 | 2 | OBSERVED_MINIMUM |
| U2-B | 1 | OBSERVED_MINIMUM |

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8093401UN6789S`):
Left plane has at least two guarded opening groups per upper band; its distant end is cropped/oblique. No station is solved from this photo.

Registered plane `POT-B004-CANTABRA`: **footprint**, ring edges `[1]`; 4 observed opening groups.
Coordinates and source/photo hashes: [`../FACADE_TRANSCRIPTION.json`](../FACADE_TRANSCRIPTION.json).
Stations are visual estimates on the unchanged wall edge chain; unsolved stations stay UNKNOWN.
Partial upper return. Numerical plan stations UNKNOWN; ground and far endpoint unresolved.

| Photo band | Observed groups | Count coverage |
| --- | ---: | --- |
| U1 | 2 | OBSERVED_MINIMUM |
| U2 | 2 | OBSERVED_MINIMUM |

Blocking facts:

- Principal entrance and complete ground storey are occluded.
- Numerical opening centres on both corner facades.
- Rear exposure/roof junction.
- Street-to-threshold elevation.

### POT-B005 — First Slice

- Unchanged source surface: `8093402UN6789S/surface-1`; plan area **35.088 m²**.
- [Pinned facade endpoint](https://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral=8093402UN6789S); receipt result **IMAGE**.
- SHA-256: `07675f30db1b7b5c8c0a2801f69cafaecb32bdf384373a7f1794b4501e78bd20`.
- EXIF file timestamp: `UNKNOWN`; dimensions: `[1920, 1080]`.
- Photo viewpoint/calibration: **UNKNOWN**. The named parent record does not certify
  the ownership of every neighbouring facade visible in the picture.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8093402UN6789S`):
Ochre corner volume. Near garden return has one horizontal and one tall opening in the visible band. Oblique street plane has at least three tall upper groups and one partially visible commercial glazing group behind signs. Higher bands are cropped. Foreground gate is a separate wall opening, not established as the principal building door.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8093402UN6789S`):
At least three tall upper groups on the oblique street plane and one ground commercial glazing group behind the sign. Higher/cropped bands cannot be replicated.

Registered plane `POT-B005-CIMAVILLA`: **footprint**, ring edges `[4]`; 4 observed opening groups.
Coordinates and source/photo hashes: [`../FACADE_TRANSCRIPTION.json`](../FACADE_TRANSCRIPTION.json).
Stations are visual estimates on the unchanged wall edge chain; unsolved stations stay UNKNOWN.
Partial street plane; station, full ground and upper coverage UNKNOWN.

| Photo band | Observed groups | Count coverage |
| --- | ---: | --- |
| G | 1 | OBSERVED_MINIMUM |
| U | 3 | OBSERVED_MINIMUM |

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8093402UN6789S`):
Two differently proportioned openings behind branches. The large foreground gate belongs to a separate wall and is not the principal building door.

Registered plane `POT-B005-GARDEN-RETURN`: **footprint**, ring edges `[5]`; 2 observed opening groups.
Coordinates and source/photo hashes: [`../FACADE_TRANSCRIPTION.json`](../FACADE_TRANSCRIPTION.json).
Stations are visual estimates on the unchanged wall edge chain; unsolved stations stay UNKNOWN.
One partially occluded band only; ground remains hidden by garden wall.

| Photo band | Observed groups | Count coverage |
| --- | ---: | --- |
| U | 1 | OBSERVED_MINIMUM |
| U-T | 1 | OBSERVED_MINIMUM |

Blocking facts:

- Ground-floor/entrance occlusion.
- Full exposed facade coverage and axes.
- Roof/return junction and exact street elevations.

### POT-B006 — First Slice

- Unchanged source surface: `8093403UN6789S/surface-1`; plan area **150.935 m²**.
- [Pinned facade endpoint](https://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral=8093403UN6789S); receipt result **IMAGE**.
- SHA-256: `391a87c760302984b4c7ba93cbe121a91c376ff23c18c21dd5689b9f8216fff2`.
- EXIF file timestamp: `UNKNOWN`; dimensions: `[1920, 1080]`.
- Photo viewpoint/calibration: **UNKNOWN**. The named parent record does not certify
  the ownership of every neighbouring facade visible in the picture.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8093403UN6789S`):
Rendered upper wall has THREE tall guarded glazed openings above the soportal. It is recessed behind the projecting porch edge; register this wall to source part3, not the footprint outer porch line. Return has a separate closed shutter. Ground rear opening coverage is incomplete. Right-hand Casa Favila frontage belongs to B007.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8093403UN6789S`):
Three tall guarded openings above the soportal, not two. Lower columns project outward from the registered upper wall. Return shutter excluded from this plane.

Registered plane `POT-B006-UPPER-SOPORTAL`: **building_part**, ring edges `[1]`; 3 observed opening groups.
Coordinates and source/photo hashes: [`../FACADE_TRANSCRIPTION.json`](../FACADE_TRANSCRIPTION.json).
Stations are visual estimates on the unchanged wall edge chain; unsolved stations stay UNKNOWN.
Main upper wall; ground rear openings and return window position remain unresolved.

| Photo band | Observed groups | Count coverage |
| --- | ---: | --- |
| U | 3 | OBSERVED_MINIMUM |

Blocking facts:

- Separate visible fronts by exact source-part boundary.
- Ground opening count and centres.
- Complete roof parts and level controls.

### POT-B007 — First Slice

- Unchanged source surface: `8093404UN6789S/surface-1`; plan area **111.306 m²**.
- [Pinned facade endpoint](https://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral=8093404UN6789S); receipt result **IMAGE**.
- SHA-256: `22e5519eacfb091c429e6c91ee2937a80d67a5ce159975cfa5c866e1fdb7c8bc`.
- EXIF file timestamp: `UNKNOWN`; dimensions: `[1920, 1080]`.
- Photo viewpoint/calibration: **UNKNOWN**. The named parent record does not certify
  the ownership of every neighbouring facade visible in the picture.

Observation (VISUAL_ESTIMATE, high; source `CAT-PHOTO:8093404UN6789S`):
Ochre three-storey front. Upper two storeys each show three glazed balcony-door axes. Top storey has one long shared iron balcony; middle storey has three individual guards. Ground has three visible glazed opening/door groups. Principal floor pattern may not be randomized to one balcony door per facade.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8093404UN6789S`):
Three axes in each upper band; one shared balcony on top, three guards beneath. Three ground opening groups visible, bottom edges cropped.

Registered plane `POT-B007-CANTABRA`: **footprint**, ring edges `[2]`; 9 observed opening groups.
Coordinates and source/photo hashes: [`../FACADE_TRANSCRIPTION.json`](../FACADE_TRANSCRIPTION.json).
Stations are visual estimates on the unchanged wall edge chain; unsolved stations stay UNKNOWN.
Upper rows complete within this street plane; ground lower edge and other exposed faces incomplete.

| Photo band | Observed groups | Count coverage |
| --- | ---: | --- |
| G | 3 | OBSERVED_MINIMUM |
| U1 | 3 | OBSERVED_COMPLETE_ROW |
| U2 | 3 | OBSERVED_COMPLETE_ROW |

Blocking facts:

- Metric opening centres/widths and visible height control.
- Other exposed facades and complete ridge shape.
- Street-to-threshold elevation.

### POT-B041 — First Slice

- Unchanged source surface: `8193801UN6789S/surface-1`; plan area **55.521 m²**.
- [Pinned facade endpoint](https://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral=8193801UN6789S); receipt result **IMAGE**.
- SHA-256: `2a2235d6fe6c33a910b745148edab8aa2e411352ea28a327e2d9ac263725a747`.
- EXIF file timestamp: `2015:11:05 17:35:29`; dimensions: `[2560, 1920]`.
- Photo viewpoint/calibration: **UNKNOWN**. The named parent record does not certify
  the ownership of every neighbouring facade visible in the picture.

Observation (VISUAL_ESTIMATE, high; source `CAT-PHOTO:8193801UN6789S`):
Low stone shop next to San Cayetano bridge; large rectangular timber glazed opening facing the walk and a smaller dark opening to its left. Red tile roof, two principal roof planes. Stone steps run along the left. Photograph is taken from above/bridge level; the window is not a tall ordinary portal.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8193801UN6789S`):
Two east-facing timber window groups; small southern and larger northern group. The low roof in the foreground is not assigned to this body.

Registered plane `POT-B041-RIVER-WALK`: **footprint**, ring edges `[1, 2]`; 2 observed opening groups.
Coordinates and source/photo hashes: [`../FACADE_TRANSCRIPTION.json`](../FACADE_TRANSCRIPTION.json).
Stations are visual estimates on the unchanged wall edge chain; unsolved stations stay UNKNOWN.
East wall partial lower occlusion; entrance and opposite wall unresolved.

| Photo band | Observed groups | Count coverage |
| --- | ---: | --- |
| G | 2 | OBSERVED_MINIMUM |

Blocking facts:

- Entrance on bridge/street side and other exposed faces.
- Metric opening locations.
- Bridge/landing/threshold level controls.

### POT-B042 — First Slice

- Unchanged source surface: `8193802UN6789S/surface-1`; plan area **165.597 m²**.
- [Pinned facade endpoint](https://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral=8193802UN6789S); receipt result **IMAGE**.
- SHA-256: `817c5d8650e6546e16d4449e49118aba209d9e9b793ce09113143ff82f87d5db`.
- EXIF file timestamp: `2015:11:05 17:40:34`; dimensions: `[2560, 1920]`.
- Photo viewpoint/calibration: **UNKNOWN**. The named parent record does not certify
  the ownership of every neighbouring facade visible in the picture.

Observation (VISUAL_ESTIMATE, high; source `CAT-PHOTO:8193802UN6789S`):
White main riverfront mass shows five unequal opening groups in each of four exposed bands. Upper attachments are open timber balconies/solanas with discrete backing windows, not a continuous glazed gallery. Source parts are all three above-ground storeys; visible river exposure includes the below-street band. Lower east white annex is not assigned to this body until ownership is resolved. Compound roof and San Cayetano frontage remain incomplete.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8193802UN6789S`):
Five unequal opening groups in four exposed river bands. Upper guards are OPEN timber balconies/solanas with discrete backing windows, not a continuous glazed gallery. Lower eastern white annex is not assigned to B042: all its locked parts have three above-ground floors.

Registered plane `POT-B042-RIVER`: **footprint**, ring edges `[15, 1, 2, 3]`; 20 observed opening groups.
Coordinates and source/photo hashes: [`../FACADE_TRANSCRIPTION.json`](../FACADE_TRANSCRIPTION.json).
Stations are visual estimates on the unchanged wall edge chain; unsolved stations stay UNKNOWN.
River main plane only. Small base vents, east return and San Cayetano street-facing wall not fully transcribed; annex ownership unresolved.

| Photo band | Observed groups | Count coverage |
| --- | ---: | --- |
| R0 | 5 | OBSERVED_COMPLETE_ROW |
| U1 | 5 | OBSERVED_COMPLETE_ROW |
| U2 | 5 | OBSERVED_COMPLETE_ROW |
| U3 | 5 | OBSERVED_COMPLETE_ROW |

Blocking facts:

- San Cayetano street-facing rear/front and entrance coverage.
- Individual opening centres on the river facade.
- Compound ridge graph and gallery returns.
- Walk-to-basement/upper-street level controls.

### POT-B043 — First Slice

- Unchanged source surface: `8193803UN6789S/surface-1`; plan area **46.885 m²**.
- [Pinned facade endpoint](https://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral=8193803UN6789S); receipt result **IMAGE**.
- SHA-256: `17059a96ad97aabf2a3bbd46b732f282466e8af2ed09879eb09abe4a09d98aa8`.
- EXIF file timestamp: `2015:11:05 17:36:30`; dimensions: `[2560, 1920]`.
- Photo viewpoint/calibration: **UNKNOWN**. The named parent record does not certify
  the ownership of every neighbouring facade visible in the picture.

Observation (VISUAL_ESTIMATE, high; source `CAT-PHOTO:8193803UN6789S`):
White three-storey front. Stone ground base shows barred opening left, timber principal door near centre, small barred opening right. Middle and top rows each have three tall glazed door/window axes with individual iron guards. Timber frames and red tile eaves. Opening type of each tall glazed element must follow image, not a random one-balcony-per-front rule.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8193803UN6789S`):
Nine visible openings on the south front: six guarded tall glazed doors, two barred ground windows and central timber entrance. Side balcony is a separate return attachment.

Registered plane `POT-B043-SOUTH`: **footprint**, ring edges `[5]`; 9 observed opening groups.
Coordinates and source/photo hashes: [`../FACADE_TRANSCRIPTION.json`](../FACADE_TRANSCRIPTION.json).
Stations are visual estimates on the unchanged wall edge chain; unsolved stations stay UNKNOWN.
Opening count complete on photographed south plane; other faces, metric heights and threshold incomplete.

| Photo band | Observed groups | Count coverage |
| --- | ---: | --- |
| G-D | 1 | OBSERVED_COMPLETE_ROW |
| G-W | 2 | OBSERVED_COMPLETE_ROW |
| U1 | 3 | OBSERVED_COMPLETE_ROW |
| U2 | 3 | OBSERVED_COMPLETE_ROW |

Blocking facts:

- Metric centres/widths and floor heights.
- Return/rear coverage and ridge topology.
- Threshold and riverwalk level controls.

### POT-B044 — First Slice

- Unchanged source surface: `8193804UN6789S/surface-1`; plan area **140.618 m²**.
- [Pinned facade endpoint](https://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral=8193804UN6789S); receipt result **IMAGE**.
- SHA-256: `0943a873ddbc7f9c063cbc7643e95b94e2052acda86bb7918c293c4294dca0c4`.
- EXIF file timestamp: `2015:11:05 17:37:16`; dimensions: `[2560, 1920]`.
- Photo viewpoint/calibration: **UNKNOWN**. The named parent record does not certify
  the ownership of every neighbouring facade visible in the picture.

Observation (VISUAL_ESTIMATE, high; source `CAT-PHOTO:8193804UN6789S`):
Small stone volume at a sloping lane junction. Principal glazed timber door/shop window group below a timber gallery/flower balcony on the left front; exposed stone return has separate small window. Upper exterior level can appear as a second storey while the source records one above and one below; do not flatten adjacent street levels.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8193804UN6789S`):
One visible compound opening group per exposed band; individual panes/door leaves are not independent wall openings.

Registered plane `POT-B044-JUNCTION-FRONT`: **footprint**, ring edges `[8, 9]`; 2 observed opening groups.
Coordinates and source/photo hashes: [`../FACADE_TRANSCRIPTION.json`](../FACADE_TRANSCRIPTION.json).
Stations are visual estimates on the unchanged wall edge chain; unsolved stations stay UNKNOWN.
Partial group count; flowers, vegetation and fence obscure edges.

| Photo band | Observed groups | Count coverage |
| --- | ---: | --- |
| G | 1 | OBSERVED_MINIMUM |
| U | 1 | OBSERVED_MINIMUM |

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8193804UN6789S`):
One small high window and one farther uphill doorway on the long rubble-stone return.

Registered plane `POT-B044-UPHILL-RETURN`: **footprint**, ring edges `[6, 7]`; 2 observed opening groups.
Coordinates and source/photo hashes: [`../FACADE_TRANSCRIPTION.json`](../FACADE_TRANSCRIPTION.json).
Stations are visual estimates on the unchanged wall edge chain; unsolved stations stay UNKNOWN.
Return openings visible but rear junction and roof levels incomplete.

| Photo band | Observed groups | Count coverage |
| --- | ---: | --- |
| G | 1 | OBSERVED_MINIMUM |
| U | 1 | OBSERVED_MINIMUM |

Blocking facts:

- Metric positions and side opening count.
- Roof ridge geometry and level relationship to both streets.

### POT-B045 — First Slice

- Unchanged source surface: `8193805UN6789S/surface-1`; plan area **140.168 m²**.
- [Pinned facade endpoint](https://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral=8193805UN6789S); receipt result **IMAGE**.
- SHA-256: `5cf2a084c5c46a76c6279f222b720ce914bff4a2a699bcdaa3e7781f9ce30612`.
- EXIF file timestamp: `2015:11:05 17:31:28`; dimensions: `[2560, 1920]`.
- Photo viewpoint/calibration: **UNKNOWN**. The named parent record does not certify
  the ownership of every neighbouring facade visible in the picture.

Observation (VISUAL_ESTIMATE, high; source `CAT-PHOTO:8193805UN6789S`):
White lane frontage shows FOUR upper windows: two narrow farther uphill/riverward and two wide above the main timber shop. Two main commercial ground groups are visible under a red tiled canopy. Far small doorway and return ownership remain unresolved. Right stone/rendered B046 remains a separate body.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8193805UN6789S`):
FOUR upper windows: two narrow farther uphill/riverward, two wide above the main timber shop. Two main ground groups are visible under canopy. Small far-left doorway is excluded pending body ownership.

Registered plane `POT-B045-LANE`: **footprint**, ring edges `[9, 10, 11, 12]`; 6 observed opening groups.
Coordinates and source/photo hashes: [`../FACADE_TRANSCRIPTION.json`](../FACADE_TRANSCRIPTION.json).
Stations are visual estimates on the unchanged wall edge chain; unsolved stations stay UNKNOWN.
Upper band count complete in view; full ground and farther small doorway ownership unresolved.

| Photo band | Observed groups | Count coverage |
| --- | ---: | --- |
| G | 1 | OBSERVED_MINIMUM |
| G-D | 1 | OBSERVED_MINIMUM |
| U | 4 | OBSERVED_COMPLETE_ROW |

Blocking facts:

- Complete principal shop-opening segmentation and metric centres.
- Return/rear coverage.
- Roof plan and street/threshold control.

### POT-B046 — First Slice

- Unchanged source surface: `8193806UN6789S/surface-1`; plan area **87.809 m²**.
- [Pinned facade endpoint](https://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral=8193806UN6789S); receipt result **IMAGE**.
- SHA-256: `64d40b11c6c5d15d75a66ec095e7760315565058cbf32c140c7898f4b7815f50`.
- EXIF file timestamp: `2015:11:05 17:30:32`; dimensions: `[2560, 1920]`.
- Photo viewpoint/calibration: **UNKNOWN**. The named parent record does not certify
  the ownership of every neighbouring facade visible in the picture.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8193806UN6789S`):
Pale rendered three-storey street wall with dressed-stone surrounds. Three tall guarded groups in the fully visible upper band; higher band cropped. N10 ground entry is visible but shop is partly hidden by awning. Timber/ochre facade opposite is B004 and is not part of this building.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8193806UN6789S`):
Rendered pale wall with dressed-stone surrounds. Three tall guarded U1 groups; U2 is cropped and two visible groups are retained without solved plan stations. Main ground N10 entry visible; shop behind awning unresolved. Opposite timber/ochre wall is B004.

Registered plane `POT-B046-CANTABRA`: **footprint**, ring edges `[7]`; 6 observed opening groups.
Coordinates and source/photo hashes: [`../FACADE_TRANSCRIPTION.json`](../FACADE_TRANSCRIPTION.json).
Stations are visual estimates on the unchanged wall edge chain; unsolved stations stay UNKNOWN.
U1 count complete; upper edge cropped and ground awning occlusion remain.

| Photo band | Observed groups | Count coverage |
| --- | ---: | --- |
| G | 1 | OBSERVED_MINIMUM |
| U1 | 3 | OBSERVED_COMPLETE_ROW |
| U2 | 2 | OBSERVED_MINIMUM |

Blocking facts:

- Photo does not show complete front opening count.
- Metric centres, rear/return coverage and ridge graph.
- Canopy ownership and threshold elevation.

### POT-B047 — First Slice

- Unchanged source surface: `8193807UN6789S/surface-1`; plan area **176.273 m²**.
- [Pinned facade endpoint](https://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral=8193807UN6789S); receipt result **IMAGE**.
- SHA-256: `79d58fd546e158291a94e17cd5de8183e1aa49cd61c3b009fd4004e56e166eb3`.
- EXIF file timestamp: `2015:11:05 17:29:50`; dimensions: `[2560, 1920]`.
- Photo viewpoint/calibration: **UNKNOWN**. The named parent record does not certify
  the ownership of every neighbouring facade visible in the picture.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8193807UN6789S`):
Brick-clad upper front, unequal windows/solid bands, large timber-clad/glazed top band. Ground restaurant frontage beneath canopy; image catches stone neighbour to the right. Cadastral parts range from one to four above-ground storeys. The low river-side part is not to be raised to match the front.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8193807UN6789S`):
Three shuttered windows in brick U1 band. One continuous top glazed band is visible but cropped; pane count not asserted. Left commercial group under awning and tall right entry are distinct.

Registered plane `POT-B047-CANTABRA`: **footprint**, ring edges `[6]`; 6 observed opening groups.
Coordinates and source/photo hashes: [`../FACADE_TRANSCRIPTION.json`](../FACADE_TRANSCRIPTION.json).
Stations are visual estimates on the unchanged wall edge chain; unsolved stations stay UNKNOWN.
U1 row observed; top band segmentation and full ground/river parts incomplete.

| Photo band | Observed groups | Count coverage |
| --- | ---: | --- |
| G | 1 | OBSERVED_MINIMUM |
| G-D | 1 | OBSERVED_MINIMUM |
| U1 | 3 | OBSERVED_COMPLETE_ROW |
| U2 | 1 | OBSERVED_MINIMUM |

Blocking facts:

- Ground opening layout obscured.
- Complete river-side/roof-part coverage.
- Metric height/axis controls and level relationships.

### POT-B048 — First Slice

- Unchanged source surface: `8193808UN6789S/surface-1`; plan area **195.525 m²**.
- [Pinned facade endpoint](https://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral=8193808UN6789S); receipt result **IMAGE**.
- SHA-256: `7f54ab56f47dc651681a33b46acac80834c8d4fb038e1e2eb5b6a97817a08b2c`.
- EXIF file timestamp: `2015:11:05 17:29:02`; dimensions: `[2560, 1920]`.
- Photo viewpoint/calibration: **UNKNOWN**. The named parent record does not certify
  the ownership of every neighbouring facade visible in the picture.

Observation (VISUAL_ESTIMATE, high; source `CAT-PHOTO:8193808UN6789S`):
White upper front has at least three projecting iron balconies in each of two bands, with tall glazed doors, shutters and flowers. Ground wall hidden by awning. Black horizontal wall attachment at right is not a proven window. Ground, returns and compound roof coverage remain incomplete.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8193808UN6789S`):
At least three tall guarded groups per upper band, with clipped top/right and left boundaries. Black wall object at right is not a proven horizontal window. Lower commercial wall is hidden by awning.

Registered plane `POT-B048-CANTABRA`: **footprint**, ring edges `[7]`; 6 observed opening groups.
Coordinates and source/photo hashes: [`../FACADE_TRANSCRIPTION.json`](../FACADE_TRANSCRIPTION.json).
Stations are visual estimates on the unchanged wall edge chain; unsolved stations stay UNKNOWN.
Six upper openings observed minimum; ground and all river-side parts incomplete.

| Photo band | Observed groups | Count coverage |
| --- | ---: | --- |
| U1 | 3 | OBSERVED_MINIMUM |
| U2 | 3 | OBSERVED_MINIMUM |

Blocking facts:

- Full ground frontage, side/rear coverage and metric axes.
- Compound roof parts/height and ground-level controls.

### POT-B049 — First Slice

- Unchanged source surface: `8193809UN6789S/surface-1`; plan area **169.752 m²**.
- [Pinned facade endpoint](https://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral=8193809UN6789S); receipt result **IMAGE**.
- SHA-256: `7d3dbd4506a7194587acbf9624b72ebcaf3d9e381481b2a2f73b40712d1e8597`.
- EXIF file timestamp: `2015:11:05 17:25:45`; dimensions: `[2560, 1920]`.
- Photo viewpoint/calibration: **UNKNOWN**. The named parent record does not certify
  the ownership of every neighbouring facade visible in the picture.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8193809UN6789S`):
Brick upper row has two broad white-frame windows and a cropped timber glazed band above. Ground commercial entry/dark opening group partly hidden by boards. Iron balconies visible at left belong to B048, not this frontage. Different river-side parts retain their source floors.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8193809UN6789S`):
Two broad white-frame windows in brick row. Upper timber glazing cropped. Ground left entrance and dark right group partly hidden by signs. Iron balconies visible to left belong to B048, not this front.

Registered plane `POT-B049-CANTABRA`: **footprint**, ring edges `[8]`; 5 observed opening groups.
Coordinates and source/photo hashes: [`../FACADE_TRANSCRIPTION.json`](../FACADE_TRANSCRIPTION.json).
Stations are visual estimates on the unchanged wall edge chain; unsolved stations stay UNKNOWN.
U1 count complete; top glazing extent and ground right type/extent unresolved.

| Photo band | Observed groups | Count coverage |
| --- | ---: | --- |
| G | 1 | OBSERVED_MINIMUM |
| G-R | 1 | OBSERVED_MINIMUM |
| U1 | 2 | OBSERVED_COMPLETE_ROW |
| U2 | 1 | OBSERVED_MINIMUM |

Blocking facts:

- Full ground opening count and metric centres.
- River-side elevation/compound roof graph.
- Street-to-river level control.

### POT-B050 — First Slice

- Unchanged source surface: `8193810UN6789S/surface-1`; plan area **185.470 m²**.
- [Pinned facade endpoint](https://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral=8193810UN6789S); receipt result **IMAGE**.
- SHA-256: `982b3a2b67268757397ac6eaba2d826e955fc633cc5f286efa68061190fc9f25`.
- EXIF file timestamp: `2015:11:05 17:23:30`; dimensions: `[2560, 1920]`.
- Photo viewpoint/calibration: **UNKNOWN**. The named parent record does not certify
  the ownership of every neighbouring facade visible in the picture.

Observation (VISUAL_ESTIMATE, high; source `CAT-PHOTO:8193810UN6789S`):
Main road frontage has six windows in each of two upper bands; two per row sit inside projecting metal/orange glazed bays. Ground left glazed entrance and four display groups are visible. Large pharmacy sign obscures another bay; no opening inferred behind it. Curved north return and Cántabra-side junction are separate planes.

Observation (VISUAL_ESTIMATE, medium; source `CAT-PHOTO:8193810UN6789S`):
Six windows in each main upper band; second and fifth are within projecting metal/orange glazed bays. Ground: left glazed entry plus four visible display groups. Large pharmacy sign obscures another bay; no opening is inferred behind it. Curved/right return excluded from this plane.

Registered plane `POT-B050-ROAD`: **footprint**, ring edges `[3]`; 17 observed opening groups.
Coordinates and source/photo hashes: [`../FACADE_TRANSCRIPTION.json`](../FACADE_TRANSCRIPTION.json).
Stations are visual estimates on the unchanged wall edge chain; unsolved stations stay UNKNOWN.
Main upper rows observed; ground under sign, lower edges and curved return remain incomplete.

| Photo band | Observed groups | Count coverage |
| --- | ---: | --- |
| G | 1 | OBSERVED_MINIMUM |
| G-W | 4 | OBSERVED_MINIMUM |
| U1 | 6 | OBSERVED_COMPLETE_ROW |
| U2 | 6 | OBSERVED_COMPLETE_ROW |

Blocking facts:

- Exact ground opening segmentation and metric axes.
- Return facade/roof annex ownership and ridge shape.
- Road/river/threshold elevation.

### POT-B051 — Sector context

- Unchanged source surface: `8193811UN6789S/surface-1`; plan area **83.020 m²**.
- [Pinned facade endpoint](https://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral=8193811UN6789S); receipt result **EMPTY_OR_UNREADABLE**.
- SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- EXIF file timestamp: `UNKNOWN`; dimensions: `UNKNOWN`.
- Photo viewpoint/calibration: **UNKNOWN**. The named parent record does not certify
  the ownership of every neighbouring facade visible in the picture.

No usable individual photographic observation. The empty endpoint is
recorded rather than replaced by a fabricated facade.

Blocking facts:

- Cadastral facade endpoint returned an empty body; complete frontage reference missing.
- Roof/massing/entrance and relationship to neighbouring 8193802.
- Levels.

## Handoff boundary

All 15 Sector 01 bodies and all 14 First Slice members have an indexed source
identity. None is certified production-ready. To close the pack, resolve the
listed exposed faces, transcribe observed openings onto the correct plan edge,
trace compound roof topology and supply independently controlled public/threshold
levels. The successor must receive those facts here; discovering them in Unity
or independently researching them is not an accepted handoff.

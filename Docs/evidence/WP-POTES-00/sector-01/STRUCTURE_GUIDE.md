# Sector 01 — hand-authored game structure

Authority: [Owner clarification](../OWNER_STRUCTURE_CLARIFICATION.md). This guide
is a **game construction brief**, with explicit estimates. It is not certification
that every hidden physical facade or roof junction has been surveyed. The unchanged
body/part geometry remains in [BUILDING_LEDGER.json](BUILDING_LEDGER.json).

## Coordinates, massing and vertical controls

Keep X east / Z north and the existing origin. Use **Y = orthometric height − 280 m**
as the reference construction datum; this is a coordinate convention, not terrain
flattening. Different streets, bridge, stairs, riverwalk and entrances retain their
different heights. The datum does not change any ground footprint or body identity.

[LIDAR_CONTROLS.json](../LIDAR_CONTROLS.json) retains the exact point indices and
observed distributions. [LIDAR_S01.csv.gz](../sources/LIDAR_S01.csv.gz) is the
complete bounded official source crop. Its building-class points can include
chimneys, attachments and neighbouring overhangs. **Do not use each body's maximum
or percentile as an automatic ridge.** Ground points around a wall can span more
than one terrace; do not average them into one flat street.

The following are rounded **VISUAL_ESTIMATE game controls** selected from those
points, source parts/floors, aerial roof context and facade photos. They provide
the major height relationships, rather than metric floor surveys. All values are
absolute orthometric metres; subtract 280 for local Y. Preserve source parts and
the photographed number of exposed bands; these controls do not require uniform
storey heights or a procedural floor stack.

| Body | Street / principal access control | Main roof height envelope | Major structure to author |
| --- | --- | --- | --- |
| B004 | Cimavilla 293.2; Cántabra side falls toward 292.0 | 300.8–303.3 | Irregular timber/render corner; two different street fronts and upper opening rhythms. Preserve shared B005/B006 boundaries. |
| B005 | Cimavilla 294.0; garden return rises toward 295.0 | 301.3–304.1 | Narrow ochre corner with distinct garden wall/gate. Ground commercial glazing and upper return remain separate. |
| B006 | Soportal approach 292.2 | Main shell about 300–304; lower source parts retained | Three upper guarded openings on the recessed part3 wall; outer porch/columns are a separate projecting structure. Do not put upper doors on the outer footprint porch line. |
| B007 | Cántabra 291.5 | 301.4–304.9 | Three-storey Casa Favila front, six upper balcony doors, shared top balcony and three individual middle guards. |
| B041 | West/bridge-side entrance about 287.6; lower river context about 281 | Main roof about 288.3–290.7 | Low stone shop beside bridge; two principal tile planes, south stair/landing relationship, two unequal east windows. Do not absorb the low foreground roof or B051. |
| B042 | San Cayetano entrance about 288.3; riverwalk about 280.9 | Main tile roof about 294.3–296.3 | Long river compound, four exposed opening bands, open timber balcony/solana returns. Keep the low eastern neighbouring mass separate. |
| B043 | South street/entry about 288.0; stepped lower side descends toward 284.7 | Main roof about 298.1–299.6 | White front with central entrance, two barred ground windows and six guarded upper openings. Preserve lower side exposure. |
| B044 | Lower front/court about 288–290; uphill return 291–292.6 | Main tile roof about 296.8–299.0 | Stone wedge at sloping junction, lower shop group and upper timber gallery; uphill side door at a higher level. |
| B045 | Shop/lane about 291.8, falling riverward toward 290.8 | Principal low roof about 298–299.6 | Two-storey white shop with four upper windows and tiled canopy. High isolated returns near B046 are not authority to raise the whole house. |
| B046 | Cántabra about 293.5 | Main roof about 303–307.1 | Tall rendered/ashlar front, three guarded openings per resolved upper band and N10 entry. Do not copy opposite B004 timber framing. |
| B047 | Cántabra about 293.5, interpolated between B046/B049 controls | Low river part about 297.5; tall main shell about 304–307.6 | Brick street front plus top glazing band; much lower river part remains distinct. Preserve all four source parts. |
| B048 | Cántabra about 293.6, interpolated between B046/B049 controls | Low river part about 297.2; intermediate about 305; tall shell about 307.8 | Six upper balcony-door groups and opaque/awning-covered commercial band; three source parts with differing lower exposure. |
| B049 | Cántabra about 293.6 | Low river part about 297.8; main shell about 304–306 | Two broad white-frame windows and upper timber glazing; adjoining B048 balconies stay on B048. Preserve five source parts. |
| B050 | Main road about 293.2 | Main east-facing sloping roof about 302.5–305.5 | Wide terminal front, twelve upper windows, two projecting glazed bays, separate curved north return and lower/secondary source part. |

The B047/B048 street controls are **DERIVED estimates**, not newly observed ground
under the awnings. Roof envelopes are construction controls, not ridge vertices.
The remaining roof-plan guide must identify the major ridge/fall/part relationships
before the structural package is marked ready; there is no permission to use an
oriented rectangle as a ridge or silently repeat one roof on compound parts.

## Facades and access

Use [FACADE_TRANSCRIPTION.json](../FACADE_TRANSCRIPTION.json): **109 observed opening
groups, 17 registered wall chains, all 14 bodies**. Each chain references actual
unchanged footprint or part edges. Source-photo hashes, image centres and approximate
plan stations are retained. A continuous glazed band is one compound group unless
its wall-opening segmentation is visible; its panes are not invented as separate
wall openings. G/U labels are photo bands, not surveyed floor elevations.

For a resolved principal door, use its transcribed station. For B004/B005 and the
B042 street side, the source **Entrance locator** gives the initial access position
in the body ledger. Retain its uncertainty and distinguish the locator from a
photographically measured portal. The construction guide still needs to bind these
locators to the intended wall/level; it must not choose a new entrance because an
ENV door module is convenient.

Unseen secondary pane/leaf segmentation, tiny services and inaccessible faces do
not require new research under this brief. Keep them UNKNOWN in the factual ledger.
The final construction guide must say which opaque/occluded surfaces can remain
simple authored surfaces, rather than inventing a randomized window layout. Principal
street frontage and access decisions remain explicit responsibilities of this WP.

## Public connections and comparison controls

The following source-point controls close the gross vertical relationship of the
bridge/streets and winding riverside stairs. IDs are stable, and each cited record
is present in the official crop. They are controls for game construction, not claims
of exact tread, threshold or bridge parapet dimensions.

| Control | Local X,Z | Height m | Point class / source record | Intended use |
| --- | --- | ---: | --- | --- |
| POT-H01 | −83.982, −76.272 | 287.947 | bridge 17 / 4787131 | North San Cayetano bridge-end walking control, near POT-V01. Ground-class points below the bridge do not define its deck. |
| POT-H02 | −76.862, −104.652 | 287.956 | ground 2 / 4864238 | San Cayetano street at POT-V02. |
| POT-H03 | −45.742, −102.822 | 291.728 | ground 2 / 5058887 | Rising Cántabra junction at POT-V03. |
| POT-H04 | −31.972, −107.282 | 293.508 | ground 2 / 5092672 | Cimavilla/Cántabra bend near POT-V04. |
| POT-H05 | −51.562, −94.132 | 288.318 | ground 2 / 5032951 | Ground near B042's source street-side Entrance locator. |
| POT-H06 | −85.062, −96.292 | 287.606 | bridge 17 / 4787784 | B041 west approach / bridge-related landing. |
| POT-H07 | −72.912, −89.422 | 281.307 | ground 2 / 4885973 | Lower north end of winding stair route OSM1094537777. |
| POT-H08 | −73.702, −102.462 | 284.126 | ground 2 / 4891425 | Intermediate turn of the same stair route. |
| POT-H09 | −82.712, −103.832 | 287.536 | ground 2 / 4810310 | Upper south end / connection toward San Cayetano. |

The stairs climb through **two material rises**, approximately 2.8 m and 3.4 m,
with a bend/landing, rather than one level connection. Preserve the winding source
axis and actual street/shop relationships. OSM's `step_count=23` is a source tag,
not a corroborated total for both flights. Individual risers may be authored at
game scale from the pinned rise/run controls; this does not permit flattening or
removing either flight. The intended extent/width and public-edge guide remain
to be made explicit here.

For source-derived comparison viewpoints V01–V04, use the nearby walking control
plus a chosen third-person eye height, recorded as a **game camera parameter**.
It does not need to recreate the unknown lens/height of a cadastral photograph.
V05 remains outside-slice context and does not add a reconstruction batch.

## Readiness boundary

This guide supplies useful construction structure now. It is still **WIP** until
the finite major roof, public-edge/connection and principal-access instructions are
complete and both Owner gates are decided. This is materially narrower than the
earlier demand for complete photographic/metric exterior coverage. No Unity
reconstruction or independent PASS is claimed here.

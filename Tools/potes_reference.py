"""Bounded WP-POTES-00 source conversion, measurement and audit. No Unity authoring.

python Tools/potes_reference.py import --cache <private acquisition cache>
python Tools/potes_reference.py build
python Tools/potes_reference.py check

Raw official archives/photos stay outside the repository. Import transforms source
geometry into a local, attributed reference product. Build is offline/repeatable.
"""
import argparse, csv, hashlib, heapq, importlib.metadata, json, math, pathlib, sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from shapely import __version__ as shapely_version
from shapely.affinity import translate
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box, mapping, shape
from shapely.ops import unary_union, polygonize
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'Docs/evidence/WP-POTES-00'
ORIGIN = (367985.1524553847, 4779218.261889531)
CRS = 'EPSG:25830'
GML_ID = '{http://www.opengis.net/gml/3.2}id'
XLINK = '{http://www.w3.org/1999/xlink}href'

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def local_name(tag):
    return tag.split('}')[-1]

def texts(e, tag):
    return [x.text for x in e.iter() if local_name(x.tag) == tag and x.text]

def polygons(e):
    result = []
    for p in e.iter():
        if local_name(p.tag) not in ('PolygonPatch', 'Polygon'):
            continue
        rings = []
        for r in p.iter():
            if local_name(r.tag) == 'LinearRing':
                pos = texts(r, 'posList')
                if pos:
                    v = list(map(float, pos[0].split()))
                    rings.append(list(zip(v[::2], v[1::2])))
        if rings:
            result.append(Polygon(rings[0], rings[1:]))
    return result

def loc(g):
    return translate(g, xoff=-ORIGIN[0], yoff=-ORIGIN[1])

def met(g):
    return translate(g, xoff=ORIGIN[0], yoff=ORIGIN[1])

def fact(value, state, sources, confidence='medium', method=None):
    f = dict(value=value, state=state, sources=sources, confidence=confidence)
    if method:
        f['method'] = method
    return f

def unknown(reason):
    return fact(None, 'UNKNOWN', [], 'none', reason)

def feature(ident, g, **props):
    return dict(type='Feature', id=ident, geometry=mapping(g), properties=dict(id=ident, **props))

def collection(fs, metric=False):
    d = dict(type='FeatureCollection', features=fs)
    if metric:
        d['coordinate_reference_system'] = CRS
        d['warning'] = 'Metric reference product, not RFC7946 longitude/latitude GeoJSON.'
    return d

def import_cache(cache):
    from pyproj import Transformer, __version__ as pyproj_version
    raw = read(cache / 'acquisition.json')
    # The records lock retrieval bytes, not a floating URL as sufficient identity.
    for r in raw:
        p = cache / r['file']
        if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() != r['sha256']:
            raise ValueError('source hash mismatch: ' + r['file'])
    write(OUT / 'sources/ACQUISITION.json', raw)
    osm = read(cache / 'osm.json')
    query = (cache / 'osm-query.txt').read_text(encoding='utf-8')
    (OUT / 'sources/OSM_QUERY.txt').parent.mkdir(parents=True, exist_ok=True)
    (OUT / 'sources/OSM_QUERY.txt').write_text(query + '\n', encoding='utf-8')
    T = Transformer.from_crs(4326, 25830, always_xy=True)
    crop = box(-150, -230, 110, 55)
    buildings, parts, parcels, addresses = [], [], [], []
    for member in ET.parse(cache / 'buildings/A.ES.SDGC.BU.39055.building.gml').getroot():
        e = list(member)[0]
        ps = polygons(e)
        ref = texts(e, 'localId')[0]
        for n, g in enumerate(ps, 1):
            g = loc(g)
            if not g.intersects(crop):
                continue
            props = {k: texts(e, k) for k in ['beginLifespanVersion', 'conditionOfConstruction', 'currentUse',
                     'horizontalGeometryEstimatedAccuracy', 'documentLink', 'sourceStatus', 'numberOfBuildingUnits',
                     'numberOfDwellings', 'numberOfFloorsAboveGround']}
            buildings.append(dict(key=f'{ref}/surface-{n}', ref=ref, component=n,
                                  geometry=mapping(g), attrs=props, source='CAT-BU'))
    for member in ET.parse(cache / 'buildings/A.ES.SDGC.BU.39055.buildingpart.gml').getroot():
        e = list(member)[0]
        ps = polygons(e)
        if not ps:
            continue
        g = loc(ps[0] if len(ps) == 1 else MultiPolygon(ps))
        if not g.intersects(crop):
            continue
        ident = texts(e, 'localId')[0]
        parts.append(dict(key=ident, ref=ident.split('_part')[0], geometry=mapping(g),
                          floors_above=texts(e, 'numberOfFloorsAboveGround'),
                          floors_below=texts(e, 'numberOfFloorsBelowGround')))
    for member in ET.parse(cache / 'CadastralParcels/A.ES.SDGC.CP.39055.cadastralparcel.gml').getroot():
        e = list(member)[0]
        ps = polygons(e)
        if not ps:
            continue
        g = loc(ps[0] if len(ps) == 1 else MultiPolygon(ps))
        if g.intersects(crop):
            parcels.append(dict(key=texts(e, 'localId')[0], geometry=mapping(g)))
    ad = ET.parse(cache / 'Addresses/A.ES.SDGC.AD.39055.gml').getroot()
    names = {e.attrib[GML_ID]: texts(e, 'text') for e in ad.iter() if local_name(e.tag) == 'ThoroughfareName'}
    for e in ad.iter():
        if local_name(e.tag) != 'Address':
            continue
        pt = loc(Point(list(map(float, texts(e, 'pos')[0].split()))))
        if not pt.intersects(crop):
            continue
        refs = [x.attrib.get(XLINK, '') for x in e.iter() if local_name(x.tag) == 'component']
        street = next((names.get(r.lstrip('#'), []) for r in refs if '.TN.' in r), [])
        addresses.append(dict(key=e.attrib[GML_ID], ref=e.attrib[GML_ID].split('.')[-1],
                              geometry=mapping(pt), street=street, number=texts(e, 'designator'),
                              specification=texts(e, 'specification')))
    ways, osm_buildings = [], []
    for e in osm['elements']:
        tags = e.get('tags', {})
        pts = [(x-ORIGIN[0], y-ORIGIN[1]) for x, y in
               [T.transform(p['lon'], p['lat']) for p in e.get('geometry', [])]]
        if len(pts) < 2:
            continue
        if 'highway' in tags or 'waterway' in tags:
            g = Polygon(pts) if tags.get('area') == 'yes' and pts[0] == pts[-1] else LineString(pts)
            if g.intersects(crop):
                ways.append(dict(key=e['id'], geometry=mapping(g), tags=tags, nodes=e.get('nodes', []),
                                 version=e.get('version'), timestamp=e.get('timestamp')))
        elif 'building' in tags and len(pts) >= 4 and pts[0] == pts[-1]:
            g = Polygon(pts)
            if g.intersects(crop):
                osm_buildings.append(dict(key=e['id'], geometry=mapping(g), tags=tags,
                                          version=e.get('version'), timestamp=e.get('timestamp')))
    im = Image.open(cache / 'mdt05.tif')
    tags = im.tag_v2
    elevation = dict(source='IGN-MDT05', origin_lon_lat=list(tags[33922][3:5]),
                     scale_lon_lat=list(tags[33550][:2]), width=im.width, height=im.height,
                     grid=[list(im.crop((0, j, im.width, j+1)).getdata()) for j in range(im.height)],
                     limit='5 m cells; integer elevation samples. Not bridge decks, steps or surveyed street/door levels.')
    photos = []
    for r in raw:
        if not r['file'].startswith('facades/'):
            continue
        try:
            im = Image.open(cache / r['file'])
            photos.append(dict(ref=pathlib.Path(r['file']).stem, source='CAT-PHOTO', url=r['url'],
                               sha256=r['sha256'], dimensions=[im.width, im.height],
                               exif_datetime=im.getexif().get(306), retrieved_utc=r['retrieved_utc'],
                               result='IMAGE', rights='Reference only; do not redistribute photograph.'))
        except Exception:
            photos.append(dict(ref=pathlib.Path(r['file']).stem, source='CAT-PHOTO', url=r['url'],
                               sha256=r['sha256'], result='EMPTY_OR_UNREADABLE', rights='Reference only.'))
    write(OUT / 'sources/LOCAL_SOURCE_PRODUCT.json', dict(origin_epsg25830=ORIGIN,
          buildings=buildings, building_parts=parts, parcels=parcels, addresses=addresses,
          ways=ways, osm_buildings=osm_buildings, elevation=elevation, photos=photos,
          osm_base=osm['osm3s']['timestamp_osm_base'],
          transformation='Bounded crop; metric-to-local coordinate transformation; source IDs; annotated reference product. Raw municipal GML and photos excluded.'))
    write(OUT / 'sources/TOOL_VERSIONS.json', dict(python=sys.version, pyproj=pyproj_version,
          proj=__import__('pyproj').proj_version_str, shapely=shapely_version,
          pillow=importlib.metadata.version('Pillow')))
    # IGN licenses this raster for redistribution with attribution. Catastro photos are not copied.
    (OUT / 'maps').mkdir(exist_ok=True)
    (OUT / 'maps/pnoa_2023_reference.jpg').write_bytes((cache / 'pnoa-core.jpg').read_bytes())
    print('Imported', len(buildings), 'source surfaces;', len(photos), 'photo receipts')

def dem_sampler(data):
    from pyproj import Transformer
    T = Transformer.from_crs(25830, 4326, always_xy=True)
    dem = data['elevation']
    lon0, lat0 = dem['origin_lon_lat']; dx, dy = dem['scale_lon_lat']
    def sample(x, y):
        lon, lat = T.transform(x + ORIGIN[0], y + ORIGIN[1])
        c, r = (lon-lon0)/dx-.5, (lat0-lat)/dy-.5
        c0, r0 = math.floor(c), math.floor(r)
        if not (0 <= c0 < dem['width']-1 and 0 <= r0 < dem['height']-1):
            return None
        fc, fr = c-c0, r-r0; z = dem['grid']
        return round(z[r0][c0]*(1-fc)*(1-fr) + z[r0][c0+1]*fc*(1-fr) +
                     z[r0+1][c0]*(1-fc)*fr + z[r0+1][c0+1]*fc*fr, 3)
    return sample

def build():
    data = read(OUT / 'sources/LOCAL_SOURCE_PRODUCT.json')
    decisions = read(OUT / 'reference_decisions.json')
    all_b = {b['key']: shape(b['geometry']) for b in data['buildings']}
    meta = {b['key']: b for b in data['buildings']}
    raw = Polygon(decisions['primary_initial_outer_polygon_local'])
    selected = set(k for k, g in all_b.items() if raw.intersection(g).area/g.area >= .5)
    selected.update(k for k, b in meta.items() if b['ref'] in decisions['explicit_outer_members'])
    core = unary_union([raw] + [all_b[k] for k in selected])
    # Adjustment is only of the outer perimeter; source geometries remain unchanged.
    for k, g in all_b.items():
        if k not in selected and core.intersection(g).area > .001:
            core = core.difference(g)
    if core.geom_type == 'MultiPolygon':
        islands = [g.area for g in core.geoms if g.area < .001]
        if any(g.area >= .001 for g in sorted(core.geoms, key=lambda g:g.area)[:-1]):
            raise ValueError('Disconnected material perimeter')
        core = max(core.geoms, key=lambda g:g.area)
    else:
        islands = []
    core = Polygon(core.exterior)  # preserve all inner fabric; holes are not exclusion devices
    # Retain the full source plaza and avoid cutting a canonical return axis by centimetres.
    # A boundary guard is a study perimeter choice, never authority for road width.
    additions=[]
    for w in data['ways']:
        g=shape(w['geometry'])
        if w['key'] in decisions.get('whole_public_space_way_ids',[]):
            additions.append(g)
        elif w['key'] in decisions.get('outer_return_axis_way_ids',[]):
            additions.append(g.intersection(core.buffer(2)).buffer(1))
    if additions:
        core=unary_union([core]+additions)
        final_select={k for k,g in all_b.items() if core.intersection(g).area/g.area>=.5}
        core=unary_union([core]+[all_b[k] for k in final_select])
        for k,g in all_b.items():
            if k not in final_select and core.intersection(g).area>.001:core=core.difference(g)
        if core.geom_type=='MultiPolygon':
            if any(g.area>=.001 for g in sorted(core.geoms,key=lambda g:g.area)[:-1]):
                raise ValueError('Material island after public-space seam adjustment')
            core=max(core.geoms,key=lambda g:g.area)
        core=Polygon(core.exterior)
    members = [k for k, g in all_b.items() if core.intersection(g).area/g.area > .999]
    partial = [(k, core.intersection(g).area/g.area) for k,g in all_b.items()
               if .001 < core.intersection(g).area/g.area < .999]
    if partial:
        raise ValueError('Material footprint cuts: ' + str(partial))
    # Registry does not renumber after an outer boundary amendment.
    reg_path = OUT / 'ID_REGISTRY.json'
    reg = read(reg_path) if reg_path.exists() else {}
    for k in sorted(members):
        if k not in reg:
            reg[k] = f'POT-B{len(reg)+1:03}'
    write(reg_path, reg)
    sample = dem_sampler(data)
    observations = read(OUT / 'FACADE_OBSERVATIONS.json')
    photo = {p['ref']:p for p in data['photos']}
    rows = []
    # Geometry boundary for production batches is derived independently from street paths;
    # per-body overrides keep complete buildings and make every shared seam explicit.
    s1_refs = {f'81938{n:02}UN6789S' for n in range(1,12)} | {'8093401UN6789S','8093402UN6789S','8093403UN6789S','8093404UN6789S'}
    s2_refs = {'8094017UN6789S','8194103UN6789S','8194104UN6789S','8194105UN6789S',
               '8194106UN6789S','8194503UN6789S','8194702UN6789S','8194703UN6789S'}
    s3_refs = {f'81930{n:02}UN6789S' for n in range(1,10)} | {'8093404UN6789S','8093405UN6789S',
               '8093406UN6789S','8093407UN6789S','8093409UN6789S',
               '8193401UN6789S','8193402UN6789S','8193403UN6789S'}
    sector_members = defaultdict(list)
    for k in sorted(members, key=lambda k:reg[k]):
        b, g = meta[k], all_b[k]
        ref = b['ref']; ident = reg[k]
        sector = 'POT-S01' if ref in s1_refs else 'POT-S02' if ref in s2_refs else 'POT-S03' if ref in s3_refs else 'POT-S04'
        sector_members[sector].append(ident)
        pr = [p for p in data['building_parts'] if p['ref'] == ref and shape(p['geometry']).intersection(g).area > .01]
        ad = [a for a in data['addresses'] if a['ref'] == ref]
        matches = [dict(osm_id=q['key'], overlap_fraction=round(shape(q['geometry']).intersection(g).area/g.area,4),
                        tags=q['tags']) for q in data['osm_buildings'] if shape(q['geometry']).intersection(g).area > 1]
        rect = list(g.minimum_rotated_rectangle.exterior.coords)
        dims = sorted([math.dist(rect[j],rect[j+1]) for j in range(2)])
        adj = []
        for ok, og in all_b.items():
            if ok == k:
                continue
            # 5 cm seam tolerance recognizes source digitization differences; adjacency is a candidate, not roof authority.
            length = g.boundary.intersection(og.boundary.buffer(.05)).length
            if length > .2:
                adj.append(dict(source_body=ok, pot_id=reg.get(ok) if ok in members else None,
                                shared_edge_candidate_m=round(length,3),
                                confidence='medium', state='DERIVED', sources=['CAT-BU'],
                                roof_dependency='UNKNOWN until roof observation'))
        obs = observations.get(ref, {})
        c = g.representative_point()
        # Derived source candidate facades retain every non-party edge. No facade is manufactured from frontage bays.
        facades=[]
        coords=list(g.exterior.coords)
        for j,(a,z) in enumerate(zip(coords[:-1],coords[1:])):
            edge=LineString([a,z])
            if edge.length < .3:
                continue
            covered=max((edge.intersection(og.boundary.buffer(.05)).length for ok,og in all_b.items() if ok!=k),default=0)
            if covered/edge.length < .9:
                facades.append(dict(id=f'{ident}-E{j+1:02}', geometry_local=mapping(edge), length_m=round(edge.length,4),
                    state='DERIVED', sources=['CAT-BU'], street_facing=unknown('Exposure candidate only; roof/massing and public sightline require photographic confirmation.'),
                    openings=unknown('No numerical opening placement inferred from a footprint. See referenced facade observations and coverage blockers.')))
        rows.append(dict(id=ident, source_body=k, cadastral_ref=ref, surface_component=b['component'], sector=sector,
            identity=fact('One unchanged source exterior surface; OSM/aerial cross-check retained below.', 'DERIVED', ['CAT-BU','OSM','IGN-PNOA'], 'medium'),
            footprint_metric=fact(mapping(met(g)), 'MEASURED', ['CAT-BU'], 'high', 'Official pinned source polygon; not a field survey.'),
            footprint_local=fact(mapping(g),'DERIVED',['CAT-BU'],'high','X=E-E0; Z=N-N0; units metres.'),
            source_accuracy_claim_m=fact(b['attrs']['horizontalGeometryEstimatedAccuracy'],'MEASURED',['CAT-BU'],'medium','Reported accuracy, not independently surveyed accuracy.'),
            area_m2=fact(round(g.area,6),'DERIVED',['CAT-BU'],'high','Planar polygon area with holes.'),
            oriented_dimensions_m=fact([round(v,4) for v in dims],'DERIVED',['CAT-BU'],'high','Minimum rotated rectangle; not frontage.'),
            frontage_m=unknown('Must identify the referenced facade plane; oriented dimensions are not frontage.'),
            dem_centroid_m=fact(sample(c.x,c.y),'DERIVED',['IGN-MDT05'],'low','Bilinear MDT05 at footprint representative point; not building floor or threshold level.'),
            ground_threshold_elevation_m=unknown('5 m MDT cannot resolve thresholds, retaining wall crests, bridge decks or terrace steps to 0.5 m.'),
            storey_parts=fact(pr,'MEASURED',['CAT-BU-PART'],'medium','Preserve each source part and differing above/below-floor counts; do not homogenize roof height.'),
            visible_height_m=unknown('No metric facade survey or rectified height control.'),
            roof=obs.get('roof',unknown('Roof topology/ridge not yet fully traced and cross-checked.')),
            adjacency=fact(adj,'DERIVED',['CAT-BU'],'medium','Coincident-edge candidate within 5 cm; openings in party walls must not be inferred.'),
            facade_edges=facades,
            cadastral_entrance_locators=fact(ad,'MEASURED',['CAT-AD'],'medium','Source Entrance locator, not door width/count. Locator may be shared by multiple bodies on the same reference.'),
            facade_observations=obs.get('facades',[]),
            material_observations=obs.get('materials',unknown('No sufficient photographic observation logged.')),
            attached_elements=obs.get('attachments',unknown('No complete observation of galleries, fixed services, steps and gates.')),
            parcel_relationship=fact([p['key'] for p in data['parcels'] if shape(p['geometry']).intersection(g).area/g.area>.5],
                                    'DERIVED',['CAT-CP'],'medium','Area overlay; does not establish legal ownership or courtyard access.'),
            osm_crosscheck=fact(matches,'DERIVED',['OSM','CAT-BU'],'medium','Independent source geometry overlap; discrepancies retained, no auto-merge/split.'),
            reference_photo=photo.get(ref,dict(result='NOT_ACQUIRED')),
            condition=fact(b['attrs']['conditionOfConstruction'],'MEASURED',['CAT-BU'],'medium'),
            source_record_date=b['attrs']['beginLifespanVersion'],
            production_ready=False,
            blocking_unknowns=obs.get('blocking_unknowns',['Full visible facade coverage/opening coordinates; ridge topology/height; surveyed street-to-threshold relationship.'])))
    by_id={b['id']:b for b in rows}
    # Street-based seed partition. The polygon edges are batch controls, not invented world walls.
    seeds=[Polygon([(-200,100),(150,100),(150,-56),(17,-79),(5,-64),(-35,-74),(-200,-87)]),
           Polygon([(-200,100),(150,100),(150,-90),(-30,-108),(-42,-115),(-63,-120),(-76,-113),(-200,-102)]),
           Polygon([(-200,100),(150,100),(150,-134),(-9,-136),(-33,-135),(-43,-147),(-61,-145),(-200,-133)])]
    bridge=next(w for w in data['ways'] if w['key']==160490852)
    bridge_context=shape(bridge['geometry']).buffer(2.5,cap_style='flat')
    geosectors={};remaining=core
    for sid,seed in zip(['POT-S02','POT-S01','POT-S03'],seeds):
        region=remaining.intersection(seed)
        if sid=='POT-S02':region=region.difference(bridge_context)
        if sid=='POT-S01':region=unary_union([region,remaining.intersection(bridge_context)])
        geosectors[sid]=region;remaining=remaining.difference(region)
    geosectors['POT-S04']=remaining
    # Assign whole bodies in a single partition operation. Shared source overlap stays a reported tolerance.
    built=unary_union([all_b[k] for k in members])
    for sid in geosectors:
        gs=[all_b[b['source_body']] for b in rows if b['sector']==sid]
        geosectors[sid]=unary_union([geosectors[sid].difference(built)]+gs).intersection(core)
    sectors=[]
    for sid,g in sorted(geosectors.items()):
        neighbours=[os for os,og in geosectors.items() if os!=sid and g.distance(og)<.01]
        seams=[]
        for b in rows:
            if b['sector']!=sid:continue
            for a in b['adjacency']['value']:
                oid=a['pot_id']
                if oid and by_id[oid]['sector']==sid:continue
                seams.append(dict(building=b['id'], neighbour=oid or a['source_body'], edge_candidate_m=a['shared_edge_candidate_m'],
                                  roof_dependency='UNKNOWN', sources=['CAT-BU']))
        sectors.append(dict(id=sid,geometry_local=mapping(g),members=sector_members[sid],neighbours=neighbours,
                            party_wall_roof_dependencies=seams,source_completeness='NOT_READY; source coverage gaps retained in ledgers',
                            sightline_dependencies=['Bridge ↔ both banks', 'Torre/plaza ↔ Cántabra', 'Cimavilla ↔ Solana alley mouths']))
    streets=[];fs=[]
    for w in sorted(data['ways'],key=lambda w:w['key']):
        g=shape(w['geometry']);clipped=g.intersection(core)
        if clipped.is_empty or (clipped.area<.01 and clipped.length<.1):continue
        tags=w['tags']
        kind='public_space' if g.geom_type=='Polygon' else 'river_axis' if 'waterway' in tags else 'bridge_axis' if 'bridge' in tags else 'steps_axis' if tags.get('highway')=='steps' else 'street_axis'
        sid=f'POT-{dict(public_space="P",river_axis="R",bridge_axis="BR",steps_axis="ST",street_axis="L")[kind]}-OSM{w["key"]}'
        samples=[]
        for gg in [clipped] if clipped.geom_type=='LineString' else list(clipped.geoms) if clipped.geom_type=='MultiLineString' else []:
            for n in range(max(2,int(gg.length/5)+1)):
                pt=gg.interpolate(n/(max(2,int(gg.length/5)+1)-1),normalized=True)
                samples.append([pt.x,pt.y,sample(pt.x,pt.y)])
        sectors_here=[s for s,sg in geosectors.items() if sg.intersection(clipped).length>.1 or sg.intersection(clipped).area>.01]
        entry=dict(id=sid,kind=kind,name=tags.get('name'),geometry_local=fact(mapping(clipped),'DERIVED',['OSM'],'medium','Metric projection, clipped at reference perimeter.'),
                   source_way=w['key'],source_version=w['version'],source_timestamp=w['timestamp'],source_tags=tags,
                   original_geometry_local=fact(mapping(g),'DERIVED',['OSM'],'medium'),
                   length_m=round(clipped.length,4),area_m2=round(clipped.area,4),sectors=sectors_here,
                   terrain_profile=fact(samples,'DERIVED',['IGN-MDT05','OSM'],'low','Terrain context only. Bridges/passage roofs must not inherit raster surface as walking level.'),
                   walking_elevation=unknown('Need independent deck/step/street controls; not supplied by OSM/5 m MDT.'),
                   surface=fact(tags.get('surface'),'DERIVED',['OSM'],'medium','OSM tag; photo cross-check required') if tags.get('surface') else unknown('No surface observation'),
                   width_m=unknown('Centreline is not exact carriageway or public-space edge geometry.'),
                   fixed_boundaries=unknown('Retaining/bank wall crest, gates, structural trees require explicit geolocated tracing.'))
        streets.append(entry);fs.append(feature(sid,met(clipped),kind=kind,sectors=sectors_here,name=tags.get('name')))
    profiles=[v[2] for s in streets for v in s['terrain_profile']['value'] if v[2] is not None and s['kind']!='river_axis']
    graph=defaultdict(dict)
    for w in data['ways']:
        if 'highway' not in w['tags'] or w['tags'].get('area')=='yes' or w['tags'].get('access') in ('no','private'):
            continue
        pts=shape(w['geometry']).coords
        for a,z,na,nz in zip(pts[:-1],pts[1:],w['nodes'][:-1],w['nodes'][1:]):
            seg=LineString([a,z]);part=seg.intersection(core)
            if part.is_empty or part.length<.1:continue
            if part.geom_type!='LineString':continue
            pp=list(part.coords)
            ka=str(na) if Point(a).distance(Point(pp[0]))<1e-5 else f'clip:{w["key"]}:{a}:{pp[0]}'
            kz=str(nz) if Point(z).distance(Point(pp[-1]))<1e-5 else f'clip:{w["key"]}:{z}:{pp[-1]}'
            graph[ka][kz]=part.length;graph[kz][ka]=part.length
    def distances(start):
        dist={start:0};todo=[(0,start)]
        while todo:
            d,u=heapq.heappop(todo)
            if d!=dist[u]:continue
            for v,l in graph[u].items():
                nd=d+l
                if nd<dist.get(v,float('inf')):dist[v]=nd;heapq.heappush(todo,(nd,v))
        return dist
    comps=[];visited=set()
    for v in graph:
        if v not in visited:
            ds=distances(v);comps.append(set(ds));visited.update(ds)
    largest=max(comps,key=len) if comps else set()
    diameter=0;endpoints=None
    for v in largest:
        ds=distances(v)
        if ds:
            z=max(ds,key=ds.get)
            if ds[z]>diameter:diameter=ds[z];endpoints=[v,z]
    street_lines=[shape(s['geometry_local']['value']) for s in streets if s['kind'] in ('street_axis','bridge_axis','steps_axis')]
    faces=[f for f in polygonize(unary_union(street_lines)) if core.covers(f.representative_point())]
    parcel_inside=[p for p in data['parcels'] if core.intersection(shape(p['geometry'])).area>.01]
    areas=sorted(b['area_m2']['value'] for b in rows)
    metrics=dict(building_count=len(rows),area_m2=round(core.area,4),bounds_local=list(core.bounds),
       dimensions_m=[round(core.bounds[2]-core.bounds[0],4),round(core.bounds[3]-core.bounds[1],4)],
       count_gt_100=sum(a>100 for a in areas),count_gt_200=sum(a>200 for a in areas),count_gt_400=sum(a>400 for a in areas),
       footprint_area_min_median_max_m2=[areas[0],(areas[len(areas)//2-1]+areas[len(areas)//2])/2,areas[-1]],
       walkable_axis_length_m=round(unary_union(street_lines).length,4),network_components=len(comps),
       largest_component_node_count=len(largest),path_diameter_m=round(diameter,4),diameter_osm_endpoints=endpoints,
       traversal_minutes_at_1_4_m_s=round(diameter/1.4/60,3),
       traversal_minutes_at_1_8_m_s=round(diameter/1.8/60,3),
       network_terrain_sample_range_m=[min(profiles),max(profiles)] if profiles else None,
       closed_network_face_count=len(faces),intersected_cadastral_parcel_count=len(parcel_inside),
       full_cadastral_parcel_count=sum(core.buffer(.005).covers(shape(p['geometry'])) for p in parcel_inside),
       source_numerical_sliver_areas_m2=islands,sector_counts={s:len(ms) for s,ms in sorted(sector_members.items())},
       photo_receipts=sum(b['reference_photo']['result']=='IMAGE' for b in rows),
       production_ready_buildings=sum(b['production_ready'] for b in rows),
       claim_limit='Counts are unchanged source exterior components; source conflicts and completeness must be resolved before independent PASS.')
    write(OUT/'BUILDING_LEDGER.json',dict(schema_version=1,crs=CRS,origin_epsg25830=ORIGIN,
           game_transform='Unity X=E-E0; Z=N-N0; Y=orthometric elevation minus a future independently controlled vertical datum. No uniform height/grade flattening.',buildings=rows))
    fields=['id','source_body','cadastral_ref','surface_component','sector','area_m2','short_side_m','long_side_m','dem_context_m','photo_result','production_ready','blocking_unknowns']
    with (OUT/'BUILDING_LEDGER.csv').open('w',encoding='utf-8',newline='') as fh:
        writer=csv.DictWriter(fh,fieldnames=fields);writer.writeheader()
        for b in rows:
            writer.writerow(dict(id=b['id'],source_body=b['source_body'],cadastral_ref=b['cadastral_ref'],surface_component=b['surface_component'],sector=b['sector'],area_m2=b['area_m2']['value'],
                short_side_m=b['oriented_dimensions_m']['value'][0],long_side_m=b['oriented_dimensions_m']['value'][1],dem_context_m=b['dem_centroid_m']['value'],
                photo_result=b['reference_photo']['result'],production_ready=b['production_ready'],blocking_unknowns='; '.join(b['blocking_unknowns'])))
    write(OUT/'STREET_PUBLIC_SPACE_LEDGER.json',dict(crs=CRS,origin_epsg25830=ORIGIN,entries=streets,
        unresolved_classes=['River bank polygons and retaining/parapet walls','Exact public-space edges/widths','Bridge deck elevation and full outline','Fixed structural vegetation','Stair riser count/levels and ramps']))
    for sector in sectors:
        sector['street_public_space_members']=[s['id'] for s in streets if sector['id'] in s['sectors']]
    write(OUT/'SECTORS.json',dict(sectors=sectors))
    write(OUT/'potes_core.geojson',collection([feature('POT-CORE-00',met(core),**metrics)],True))
    write(OUT/'buildings.geojson',collection([feature(b['id'],met(all_b[b['source_body']]),sector=b['sector'],source_body=b['source_body']) for b in rows],True))
    write(OUT/'sectors.geojson',collection([feature(s['id'],met(shape(s['geometry_local'])),members=s['members']) for s in sectors],True))
    write(OUT/'streets.geojson',collection(fs,True))
    write(OUT/'METRICS.json',metrics)
    first=[b['id'] for b in rows if b['sector']=='POT-S01' and b['cadastral_ref']!='8193811UN6789S']
    # Fourteen adjacent real source bodies, including the compound riverfront building, low bridge shop and irregular Llano corner.
    write(OUT/'sector-01/FIRST_SLICE.json',dict(ids=first,status='NOT_READY_REFERENCE_GAPS',geometry_scope='Whole original bodies only; every First Slice member belongs to Sector 01.'))
    write(OUT/'sector-01/BUILDING_LEDGER.json',dict(buildings=[b for b in rows if b['sector']=='POT-S01']))
    write(OUT/'sector-01/STREET_PUBLIC_SPACE_LEDGER.json',dict(entries=[s for s in streets if 'POT-S01' in s['sectors']]))
    write(OUT/'sector-01/SECTOR_GEOMETRY.geojson',collection([feature('POT-S01',met(geosectors['POT-S01']))],True))
    # Complete source exclusion audit: every interior exterior component must be counted.
    write(OUT/'MEMBERSHIP_AUDIT.json',dict(source_components=[dict(source_body=k,pot_id=reg.get(k) if k in members else None,
          selected=k in members,area_m2=g.area,core_overlap_fraction=core.intersection(g).area/g.area,
          footprint_changed=False) for k,g in all_b.items()],
          no_interior_deletion=not any(k not in members and core.covers(g.representative_point()) for k,g in all_b.items()),
          unresolved_identity=['8193301UN6789S is outside the primary perimeter: recent declined 6 m² record and older photo of a much larger building disagree. Do not import it as a separate invented narrow building.'],
          numerical_sliver_areas_m2=islands))
    gate_path=OUT/'OWNER_GATES.json'
    gates=read(gate_path)
    identities=[
        {'polygon_epsg25830':mapping(met(core)), 'buildings':[(b['id'],b['source_body']) for b in rows]},
        {'sectors':[(s['id'],s['geometry_local'],s['members']) for s in sectors], 'first_slice':first}
    ]
    for gate,identity in zip(gates['gates'],identities):
        fingerprint=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
        if gate['status']=='APPROVED' and gate.get('proposal_sha256')!=fingerprint:
            raise ValueError('Approved Owner gate identity changed: '+gate['name'])
        gate['proposal_sha256']=fingerprint
    write(gate_path,gates)
    render_maps(core,rows,all_b,streets,geosectors,data)
    reference_index(rows, first)
    print(json.dumps(metrics,indent=2))

def reference_index(rows, first):
    """Index pinned views and their limitations, without redistributing photographs."""
    lines = ['# Sector 01 — pinned reference index', '',
        'Status: **INDEX COMPLETE / EXTERIOR COVERAGE INCOMPLETE**. A linked image is not',
        'certification of all faces, openings, roof planes or levels. No third-party facade',
        'photograph is stored in this repository.', '',
        'Source epochs, rights and acquisition receipts: [`../SOURCE_LOCK.md`](../SOURCE_LOCK.md),',
        '`../sources/ACQUISITION.json` and `../sources/LOCAL_SOURCE_PRODUCT.json`.',
        'Geometry is keyed by immutable POT ID and unchanged cadastral exterior surface;',
        'a photograph keyed by a parent cadastral reference can show adjoining bodies.',
        'Photo camera position, lens and capture date are UNKNOWN unless expressly recorded.',
        'EXIF below is a file timestamp, not a certified survey date.', '',
        '## Shared views and ground authority', '',
        '- [PNOA 2023-08 reference](../maps/pnoa_2023_reference.jpg) and',
        '  [body-ID overlay](../maps/pnoa_perimeter_overlay.jpg): roofs, broad public surfaces',
        '  and adjoining context. Non-true-ortho displacement prevents metric ridge/ground equivalence.',
        '- Footprints, source parts/floors, source entrance locators and non-party-edge',
        '  candidates: [`BUILDING_LEDGER.json`](BUILDING_LEDGER.json). Edge candidates are',
        '  not certified street facades. Source entrance locators do not measure doors.',
        '- [Public panorama, KTM Laranjinha, March 2019](https://www.google.com/maps/@43.1533337,-4.6245592,3a,90y,95.32h,90t/data=!3m4!1e1!3m2!1sCIHM0ogKEICAgICErL709gE!2e10):',
        '  river facade, both banks, paved upper approach and lower retaining/walk relationship.',
        '  Visible perspective is supplementary; distant/blurred openings and street-side',
        '  entrances remain unresolved. This panorama position is separate from the proposed',
        '  comparison-camera positions in SECTOR_PACK.md. No screenshot is redistributed.', '',
        '## Per-body photo, coverage and blockers', '']
    for b in rows:
        if b['sector'] != 'POT-S01':
            continue
        p = b['reference_photo']
        lines += [f"### {b['id']} — {'First Slice' if b['id'] in first else 'Sector context'}", '',
            f"- Unchanged source surface: `{b['source_body']}`; plan area **{b['area_m2']['value']:.3f} m²**.",
            f"- [Pinned facade endpoint]({p['url']}); receipt result **{p['result']}**.",
            f"- SHA-256: `{p['sha256']}`.",
            f"- EXIF file timestamp: `{p.get('exif_datetime') or 'UNKNOWN'}`; dimensions: `{p.get('dimensions', 'UNKNOWN')}`.",
            '- Photo viewpoint/calibration: **UNKNOWN**. The named parent record does not certify',
            '  the ownership of every neighbouring facade visible in the picture.', '']
        for o in b['facade_observations']:
            lines += [f"Observation ({o['state']}, {o['confidence']}; source `{o['view']}`):", o['observations'], '']
        if not b['facade_observations']:
            lines += ['No usable individual photographic observation. The empty endpoint is',
                      'recorded rather than replaced by a fabricated facade.', '']
        lines += ['Blocking facts:', ''] + ['- '+v+'.' for v in b['blocking_unknowns']] + ['']
    lines += ['## Handoff boundary', '',
        'All 15 Sector 01 bodies and all 14 First Slice members have an indexed source',
        'identity. None is certified production-ready. To close the pack, resolve the',
        'listed exposed faces, transcribe observed openings onto the correct plan edge,',
        'trace compound roof topology and supply independently controlled public/threshold',
        'levels. The successor must receive those facts here; discovering them in Unity',
        'or independently researching them is not an accepted handoff.', '']
    (OUT/'sector-01/REFERENCE_INDEX.md').write_text('\n'.join(lines), encoding='utf-8')

def render_maps(core,rows,all_b,streets,geosectors,data):
    bounds=(-115,-215,105,40);scale=6;plot=box(*bounds)
    font_path='C:/Windows/Fonts/arial.ttf'
    try:font=ImageFont.truetype(font_path,16);head=ImageFont.truetype(font_path,27)
    except OSError:font=head=ImageFont.load_default()
    colors={'POT-S01':'#f1bf75','POT-S02':'#e78d81','POT-S03':'#96c5c0','POT-S04':'#b9b0dc'}
    def sc(pt):return ((pt[0]-bounds[0])*scale+35,(bounds[3]-pt[1])*scale+80)
    for sectorized in [False,True]:
        im=Image.new('RGB',(int((bounds[2]-bounds[0])*scale)+390,int((bounds[3]-bounds[1])*scale)+155),'#faf8f1');d=ImageDraw.Draw(im)
        d.text((25,15),'POTES-00 | '+('Sector proposal' if sectorized else 'Exact perimeter proposal')+' | north up',font=head,fill='#222')
        for x in range(-100,101,20):
            d.line([sc((x,bounds[1])),sc((x,bounds[3]))],fill='#deded8');d.text(sc((x,bounds[3])),str(x),font=font,fill='#888')
        for y in range(-200,41,20):
            d.line([sc((bounds[0],y)),sc((bounds[2],y))],fill='#deded8');d.text(sc((bounds[0],y)),str(y),font=font,fill='#888')
        for b in data['buildings']:
            g=shape(b['geometry']).intersection(plot)
            gs=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
            for gg in gs:
                if gg.geom_type=='Polygon' and not gg.is_empty:d.polygon([sc(v) for v in gg.exterior.coords],fill='#e6e3dc',outline='#aaa59c',width=1)
        for b in rows:
            g=all_b[b['source_body']]
            d.polygon([sc(v) for v in g.exterior.coords],fill=colors[b['sector']] if sectorized else '#b8cca5',outline='#645f51',width=2)
            for ring in g.interiors:d.polygon([sc(v) for v in ring.coords],fill='#faf8f1',outline='#645f51')
            d.text(sc(g.representative_point().coords[0]),b['id'].replace('POT-B',''),font=font,fill='#111')
        for s in streets:
            g=shape(s['geometry_local']['value'])
            gs=list(g.geoms) if g.geom_type.startswith('Multi') or g.geom_type=='GeometryCollection' else [g]
            for gg in gs:
                ps=list(gg.exterior.coords) if gg.geom_type=='Polygon' else list(gg.coords) if gg.geom_type=='LineString' else []
                if ps:d.line([sc(v) for v in ps],fill='#247fb0' if s['kind']=='river_axis' else '#85604d',width=3)
        if sectorized:
            for sid,g in geosectors.items():
                gs=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
                for gg in gs:
                    if gg.geom_type=='Polygon':d.line([sc(v) for v in gg.exterior.coords],fill='#835a98',width=3)
        d.line([sc(v) for v in core.exterior.coords],fill='#193e80',width=5)
        tower = next(b for b in rows if b['cadastral_ref']=='8194106UN6789S')
        tower_point=all_b[tower['source_body']].representative_point().coords[0]
        d.line([sc((20,14)),sc(tower_point)],fill='#5c3027',width=2)
        for text,pt in [('Torre del Infantado / B055',(-6,25)),('Plaza Capitan Palacios',(22,-62)),('CANTABRA',(-28,-96)),('CIMAVILLA',(-26,-132)),('LA SOLANA',(7,-174)),('San Cayetano / El Sol',(-105,-63))]:
            d.text(sc(pt),text,font=font,fill='#5c3027',stroke_width=1,stroke_fill='#fff8e7')
        for label,pt in [('I01',(65,-66)),('I02',(23,-179)),('I03',(30,-38))]:
            x,y=sc(pt);d.ellipse((x-7,y-7,x+7,y+7),fill='#114d6a');d.text((x+8,y-12),label,font=font,fill='#114d6a',stroke_width=1,stroke_fill='white')
        side=int((bounds[2]-bounds[0])*scale)+85
        notes=[f'{len(rows)} pinned exterior source bodies','Perimeter: full building edges','NO UNITY RECONSTRUCTION','Owner boundary gate: PENDING','Owner sector gate: PENDING','Visual handoff: NOT READY','','Game plane: X east, Z north','Origin EPSG:25830',f'{ORIGIN[0]:.6f}',f'{ORIGIN[1]:.6f}','','Labels = POT-Bxxx','Grey = excluded source fabric','Blue line = selected perimeter','Brown = OSM street axes','Blue = Quiviesa axis','','S01: bridge / Cantabra (15)','S02: Torre / plaza / return (8)','S03: Llano / Cimavilla (13)','S04: lower Solana / Riega (22)','','I01: civic/market seam','I02: residential seam','I03: downstream/workshop seam','','Street widths, decks, facade','gaps are explicit UNKNOWN.']
        for n,line in enumerate(notes):d.text((side,90+n*25),line,font=font,fill='#333')
        d.line([sc((-100,-200)),sc((-80,-200))],fill='black',width=5);d.text(sc((-100,-196)),'20 m',font=font,fill='black')
        d.text((25,im.height-46),'Derived Catastro INSPIRE 2026-08-21 + (c) OpenStreetMap contributors, ODbL 1.0. Geometry source precision != verified field accuracy.',font=font,fill='#333')
        im.save(OUT/'maps'/('sectorization.png' if sectorized else 'perimeter.png'))
    im=Image.open(OUT/'maps/pnoa_2023_reference.jpg').convert('RGB');d=ImageDraw.Draw(im)
    bb=(367865,4779010,368080,4779250)
    def ortho(pt):return ((pt[0]+ORIGIN[0]-bb[0])/(bb[2]-bb[0])*im.width,(bb[3]-(pt[1]+ORIGIN[1]))/(bb[3]-bb[1])*im.height)
    for b in rows:
        g=all_b[b['source_body']];d.line([ortho(v) for v in g.exterior.coords],fill='#fff04b',width=2)
        d.text(ortho(g.representative_point().coords[0]),b['id'].replace('POT-B',''),font=font,fill='white',stroke_width=2,stroke_fill='black')
    d.line([ortho(v) for v in core.exterior.coords],fill='#38efff',width=5)
    d.rectangle((0,0,im.width,42),fill='white');d.text((8,8),'Derived PNOA 2023-08 | CC BY 4.0 IGN/CNIG + Cantabria | ground footprint != displaced roof silhouette',font=font,fill='black')
    im.save(OUT/'maps/pnoa_perimeter_overlay.jpg')

def check():
    ledger=read(OUT/'BUILDING_LEDGER.json')['buildings'];core=shape(read(OUT/'potes_core.geojson')['features'][0]['geometry'])
    sectors=read(OUT/'SECTORS.json')['sectors'];audit=read(OUT/'MEMBERSHIP_AUDIT.json');errors=[]
    if not 55<=len(ledger)<=65:errors.append('Building count outside target')
    if not core.is_valid or core.geom_type!='Polygon' or core.interiors:errors.append('Perimeter not one valid hole-free polygon')
    if not audit['no_interior_deletion']:errors.append('Uncounted interior source body')
    ids=[b['id'] for b in ledger]
    if len(ids)!=len(set(ids)):errors.append('Duplicate IDs')
    if len({b['source_body'] for b in ledger})!=len(ledger):errors.append('Duplicate exterior-source ownership')
    if sorted(ids)!=sorted(i for s in sectors for i in s['members']):errors.append('Sector membership not exact partition')
    sources=read(OUT/'sources/LOCAL_SOURCE_PRODUCT.json')
    registry=read(OUT/'ID_REGISTRY.json')
    original_by_key={b['key']:b for b in sources['buildings']}
    for b in ledger:
        original=original_by_key[b['source_body']]
        if registry[b['source_body']]!=b['id']:errors.append('Registry identity changed '+b['id'])
        if not shape(original['geometry']).equals_exact(shape(b['footprint_local']['value']),1e-10):errors.append('Footprint changed '+b['id'])
        if not core.buffer(.005).covers(shape(b['footprint_metric']['value'])):errors.append('Material footprint cut '+b['id'])
        if not met(shape(b['footprint_local']['value'])).equals_exact(shape(b['footprint_metric']['value']),1e-8):errors.append('Coordinate transform mismatch '+b['id'])
    # Independently recompute complete-crop membership instead of trusting the generated audit flag.
    membership={b['source_body'] for b in ledger}
    for key,b in original_by_key.items():
        g=met(shape(b['geometry']));fraction=core.intersection(g).area/g.area
        if key not in membership and core.covers(g.representative_point()):errors.append('Uncounted interior body '+key)
        if .001<fraction<.999:errors.append('Partly cut source body '+key)
    sg=[met(shape(s['geometry_local'])) for s in sectors]
    sg_by_id={s['id']:met(shape(s['geometry_local'])) for s in sectors}
    for b in ledger:
        if not sg_by_id[b['sector']].buffer(.005).covers(shape(b['footprint_metric']['value'])):
            errors.append('Building not wholly owned by sector '+b['id'])
    if core.symmetric_difference(unary_union(sg)).area>.01:errors.append('Sector coverage gap')
    overlap=sum(a.intersection(b).area for n,a in enumerate(sg) for b in sg[n+1:])
    if overlap>.02:errors.append('Material sector overlap '+str(overlap))
    first=read(OUT/'sector-01/FIRST_SLICE.json')['ids']
    if not 8<=len(first)<=15 or len(first)!=len(set(first)):errors.append('First Slice cardinality')
    if not set(first).issubset(set(next(s['members'] for s in sectors if s['id']=='POT-S01'))):errors.append('First Slice outside Sector 01')
    evidence_errors=[]
    for b in ledger:
        if b['production_ready']:
            if b['blocking_unknowns']:
                evidence_errors.append('Ready flag contradicts recorded blockers '+b['id'])
            for key in ['frontage_m','ground_threshold_elevation_m','visible_height_m','roof']:
                if b[key]['state']=='UNKNOWN':
                    evidence_errors.append('Ready flag contradicts UNKNOWN '+b['id']+':'+key)
            if not b['facade_observations'] or any(o.get('opening_coordinates') is None for o in b['facade_observations']):
                evidence_errors.append('Ready flag lacks registered opening observations '+b['id'])
    ready=sum(b['production_ready'] for b in ledger if b['id'] in first)
    gates=read(OUT/'OWNER_GATES.json')
    for g in gates['gates']:
        if g['status']=='APPROVED' and not g.get('human_decision'):
            evidence_errors.append('Owner approval lacks direct human decision '+g['name'])
    claim_blockers=[f"Owner {g['name']} {g['status']}" for g in gates['gates'] if g['status']!='APPROVED']
    if ready!=len(first):claim_blockers.append('First Slice exterior reference incomplete: '+str(len(first)-ready)+' buildings not production ready')
    claim_blockers.extend(read(OUT/'STREET_PUBLIC_SPACE_LEDGER.json')['unresolved_classes'])
    result=dict(geometry_integrity_errors=errors,evidence_integrity_errors=evidence_errors,sector_overlap_m2=overlap,first_slice_ids=first,
                first_slice_reference_ready_count=ready,claim_blockers=claim_blockers,
                ready_for_independent_review=not errors and not evidence_errors and not claim_blockers,
                no_unity_edits_required=True)
    write(OUT/'VALIDATION.json',result);print(json.dumps(result,indent=2))
    # Green geometry must never look like full WP acceptance to an automated caller.
    return 1 if errors or evidence_errors else 2 if claim_blockers else 0

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['import','build','check']);parser.add_argument('--cache',type=pathlib.Path)
    args=parser.parse_args()
    if args.command=='import':import_cache(args.cache)
    elif args.command=='build':build()
    else:sys.exit(check())

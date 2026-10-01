"""Bounded official LiDAR crop and offline point controls for POTES-00.

Building-class points are height observations, not automatic roof vertices.
Ground-class points do not establish hidden thresholds or individual stair risers.
"""
import csv
import gzip
import hashlib
import io
import json
import pathlib
import sys
from collections import Counter

from shapely.geometry import Point, shape

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'Docs/evidence/WP-POTES-00'
CROP = OUT / 'sources/LIDAR_S01.csv.gz'
BOUNDS = (367894, 4779089, 367998, 4779153)
RAW_SHA = '8f87d0eebdd17c2382b458e4789f72bc4d75ce61c14cee539a1555f64fa49241'


def acquire_crop(path):
    import laspy
    if hashlib.sha256(path.read_bytes()).hexdigest() != RAW_SHA:
        raise ValueError('Official CNIG source bytes differ from the pinned acquisition')
    rows = io.StringIO(newline='')
    writer = csv.writer(rows, lineterminator='\n')
    writer.writerow(['source_record_index', 'easting_m', 'northing_m', 'orthometric_height_m', 'class', 'return_number', 'number_of_returns'])
    counts = Counter()
    offset = 0
    with laspy.open(path) as reader:
        if str(reader.header.parse_crs()) != 'EPSG:25830':
            raise ValueError('Unexpected source CRS')
        for chunk in reader.chunk_iterator(500000):
            mask = ((chunk.x >= BOUNDS[0]) & (chunk.x <= BOUNDS[2]) &
                    (chunk.y >= BOUNDS[1]) & (chunk.y <= BOUNDS[3]))
            for idx in mask.nonzero()[0]:
                idx=int(idx)
                cls = int(chunk.classification[idx])
                # Retain all crop returns, including overlap/noise labels, so the
                # source-role choice can be falsified. Analysis selects roles later.
                writer.writerow([offset + int(idx), f'{chunk.x[idx]:.2f}', f'{chunk.y[idx]:.2f}',
                    f'{chunk.z[idx]:.3f}', cls, int(chunk.return_number[idx]), int(chunk.number_of_returns[idx])])
                counts[cls] += 1
            offset += len(chunk)
    CROP.write_bytes(gzip.compress(rows.getvalue().encode(), mtime=0))
    lock = dict(source_id='IGN-LIDAR-2023-NPC03', disposition='USE',
        catalog_url='https://centrodedescargas.cnig.es/CentroDescargas/detalleArchivo?sec=12974974',
        acquired_utc='2026-10-01', file=path.name, raw_bytes=path.stat().st_size, raw_sha256=RAW_SHA,
        source_crs='EPSG:25830', heights='Orthometric, metres; source classes retained',
        license_url='https://www.ign.es/resources/licencia/Condiciones_licenciaUso_IGN.pdf',
        license='CC-BY 4.0 compatible IGN geographic-information license, as displayed on this exact CNIG catalog record',
        attribution='Obra derivada de LiDAR-PNOA-cob3 2022-2025 CC-BY 4.0 scne.es',
        crop_bounds_metric=list(BOUNDS), crop_file=CROP.name,
        crop_sha256=hashlib.sha256(CROP.read_bytes()).hexdigest(), crop_point_count=sum(counts.values()),
        crop_class_counts=dict(sorted(counts.items())),
        crop_method='Inclusive metric bbox, all source records/classes/returns retained in source order; XY 0.01 m and Z 0.001 m source precision. No sampling, interpolation, class rewrite or roof fitting.',
        tools=dict(laspy=laspy.__version__),
        regional_zip='REJECT for production: its separately bundled license restricts commercial use. The retained crop comes exclusively from independently downloaded official CNIG bytes.')
    (OUT/'sources/LIDAR_ACQUISITION.json').write_text(json.dumps(lock, indent=2)+'\n', encoding='utf8')
    print(json.dumps(dict(points=sum(counts.values()), classes=dict(counts), crop_bytes=CROP.stat().st_size), indent=2))


def load_points():
    lock=json.loads((OUT/'sources/LIDAR_ACQUISITION.json').read_text(encoding='utf8'))
    if hashlib.sha256(CROP.read_bytes()).hexdigest() != lock['crop_sha256']:
        raise ValueError('Pinned LiDAR crop changed')
    with gzip.open(CROP,'rt',encoding='utf8',newline='') as stream:
        points=[dict(index=int(p['source_record_index']), e=float(p['easting_m']), n=float(p['northing_m']),
            h=float(p['orthometric_height_m']), cls=int(p['class'])) for p in csv.DictReader(stream)]
    if len(points)!=lock['crop_point_count']:
        raise ValueError('LiDAR crop cardinality changed')
    return points


def build_controls():
    points=load_points()
    ledger=json.loads((OUT/'BUILDING_LEDGER.json').read_text(encoding='utf8'))['buildings']
    first=json.loads((OUT/'sector-01/FIRST_SLICE.json').read_text(encoding='utf8'))['ids']
    data=derive_controls(ledger,first,points)
    (OUT/'LIDAR_CONTROLS.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf8')


def derive_controls(ledger,first,points):
    result=[]
    for b in ledger:
        if b['id'] not in first:continue
        g=shape(b['footprint_metric']['value'])
        roof=[p for p in points if p['cls']==6 and g.covers(Point(p['e'],p['n']))]
        heights=sorted(p['h'] for p in roof)
        def percentile(f):
            return heights[round((len(heights)-1)*f)] if heights else None
        front_controls=[]
        for obs in b['facade_observations']:
            if not obs.get('registration'):continue
            chain=shape(obs['registration']['geometry_local'])
            near=[]
            origin=b['footprint_metric']['value']['coordinates'][0][0]
            local=b['footprint_local']['value']['coordinates'][0][0]
            e0,n0=origin[0]-local[0],origin[1]-local[1]
            for p in points:
                if p['cls']!=2:continue
                lp=Point(p['e']-e0,p['n']-n0)
                if chain.distance(lp)<=1.5 and not g.covers(Point(p['e'],p['n'])):
                    near.append(p)
            front_controls.append(dict(observation_id=obs['id'],state='DERIVED',confidence='medium',
                ground_class_point_count=len(near),
                ground_class_height_range_m=[min(p['h'] for p in near),max(p['h'] for p in near)] if near else None,
                samples=[dict(source_record_index=p['index'],local_xz=[round(p['e']-e0,6),round(p['n']-n0,6)],orthometric_height_m=p['h']) for p in near],
                caution='Ground-class returns within 1.5 m of registered wall chain, outside footprint. Inspect spatial levels; these are not door thresholds and may include both sides of a retaining step.'))
        result.append(dict(building_id=b['id'],state='DERIVED',sources=['IGN-LIDAR-2023-NPC03','CAT-BU'],
            confidence='medium',building_class_point_count=len(roof),
            point_height_percentiles_m=dict(p05=percentile(.05),p50=percentile(.5),p95=percentile(.95)),
            observed_height_range_m=[heights[0],heights[-1]] if heights else None,
            source_record_indices=[p['index'] for p in roof],
            ground_near_registered_fronts=front_controls,
            roof_graph_state='UNKNOWN',
            caution='Distribution of building-class returns in unchanged footprint, not ridge/eave extrema or a solved roof graph. Do not turn percentiles into facade heights.'))
    data=dict(status='HEIGHT_OBSERVATIONS_AVAILABLE_ROOF_GRAPH_INCOMPLETE',
        source_crop='sources/LIDAR_S01.csv.gz',
        attribution='Obra derivada de LiDAR-PNOA-cob3 2022-2025 CC-BY 4.0 scne.es',
        buildings=result,
        public_class_point_counts={str(k):v for k,v in sorted(Counter(p['cls'] for p in points if p['cls'] in (2,17)).items())},
        unresolved='Select and identify actual street/deck/landing samples; classification alone does not certify point roles or stair/threshold geometry.')
    return data


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='crop':acquire_crop(pathlib.Path(sys.argv[2]))
    else:build_controls()

"""Bounded manual-photo transcription support for WP-POTES-00. No reconstruction.

Plan stations are visual estimates, not a metric opening survey. Incomplete
coverage cannot turn a body into a production-ready one.
"""
import hashlib
import json
import math
from shapely.geometry import LineString, mapping


def geometry_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def registered_observations(body, document):
    observations = []
    for item in document['facades']:
        if item['building_id'] != body['id']:
            continue
        photo = body['reference_photo']
        if item['photo_sha256'] != photo['sha256']:
            raise ValueError('Transcription photo identity changed ' + item['id'])
        if item['footprint_sha256'] != geometry_digest(body['footprint_local']['value']):
            raise ValueError('Transcription footprint identity changed ' + item['id'])
        target = item['registration']
        if target['kind'] == 'footprint':
            polygon = body['footprint_local']['value']
        elif target['kind'] == 'building_part':
            polygon = next(p['geometry'] for p in body['storey_parts']['value']
                           if p['key'] == target['part_key'])
        else:
            raise ValueError('Unknown transcription plane kind ' + item['id'])
        if target['geometry_sha256'] != geometry_digest(polygon):
            raise ValueError('Registered source plane geometry changed ' + item['id'])
        if not target['ring_edge_numbers']:
            raise ValueError('Empty registered edge chain ' + item['id'])
        ring = polygon['coordinates'][0]
        coords = []
        for n in target['ring_edge_numbers']:
            if not 1 <= n < len(ring):
                raise ValueError('Unknown source edge ' + item['id'])
            a, b = ring[n - 1:n + 1]
            if coords and math.dist(coords[-1], a) > 1e-8:
                raise ValueError('Non-contiguous registered edge chain ' + item['id'])
            if not coords:
                coords.append(a)
            coords.append(b)
        line = LineString(coords)
        openings = []
        opening_ids = set()
        for row in item['rows']:
            for opening in row['openings']:
                if opening['id'] in opening_ids:
                    raise ValueError('Duplicate opening identity ' + item['id'])
                opening_ids.add(opening['id'])
                center = opening['image_center_fraction']
                if len(center) != 2 or any(not 0 <= v <= 1 for v in center):
                    raise ValueError('Image coordinate outside locked photo ' + item['id'])
                station = opening.get('station_fraction')
                interval = opening.get('station_interval')
                if station is not None and (not 0 <= station <= 1 or not interval
                        or len(interval) != 2 or not 0 <= interval[0] <= station <= interval[1] <= 1):
                    raise ValueError('Opening station outside registered source edges ' + item['id'])
                if station is None and interval is not None:
                    raise ValueError('Interval without a solved station ' + item['id'])
                point = line.interpolate(station, normalized=True) if station is not None else None
                openings.append(dict(**opening, row=row['row'], row_count_state=row['count_state'],
                    image_center_px=[round(v * size, 1) for v, size in zip(center, photo['dimensions'])],
                    center_local_xz=[round(v, 4) for v in point.coords[0]] if point else None,
                    absolute_y_m=None, metric_width_m=None, state='VISUAL_ESTIMATE',
                    confidence=item['confidence'], sources=[item['source'], 'CAT-BU-PART' if target['kind']=='building_part' else 'CAT-BU']))
        observations.append(dict(id=item['id'], view=item['source'], state='VISUAL_ESTIMATE',
            sources=[item['source'], 'CAT-BU-PART' if target['kind']=='building_part' else 'CAT-BU'],
            confidence=item['confidence'], observations=item['notes'],
            registration=dict(**target, geometry_local=mapping(line), station_direction='Start to end of the unchanged source edge chain',
                              basis=item['registration_basis'], state='VISUAL_ESTIMATE'),
            opening_coordinates=openings, coverage=item['coverage'], complete_exterior=False,
            position_method='Manual approximate station ranges after face/adjacency registration; image centers retained. No equal-bay inference, solved camera or metric height claim.'))
    return observations

"""Explicit incumbent ENV choices consumed by regeneration; never silently discard them.

Frontage policies precede plot construction. Plot attributes precede footprint/ground
calculation. End and stair corrections follow generation. Missing/misidentified targets
fail closed; removing a correction requires an explicit source-file change.
"""
import copy
import json
import math
from pathlib import Path


def load(trace_path):
    path = Path(trace_path).with_name(Path(trace_path).name.replace('.trace.json', '.authoring.json'))
    if not path.exists():
        trace = json.loads(Path(trace_path).read_text(encoding='utf-8-sig'))
        if trace.get('authoring', {}).get('required'):
            raise ValueError('ENV_AUTHORING_MISSING input: ' + str(path))
        return None
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    def finite(value):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError('ENV_AUTHORING_NONFINITE: ' + str(path))
        if isinstance(value, dict):
            for child in value.values(): finite(child)
        if isinstance(value, list):
            for child in value: finite(child)
    finite(data)
    if data.get('schema') != 1 or not isinstance(data.get('plots'), dict):
        raise ValueError('ENV_AUTHORING_UNSUPPORTED: ' + str(path))
    for id, profile in data['plots'].items():
        if not isinstance(profile, dict) or not isinstance(profile.get('items'), list) or len(profile.get('origin', [])) != 2 or len(profile.get('dir', [])) != 2:
            raise ValueError('ENV_AUTHORING_INVALID profile: ' + id)
        for item in profile['items']:
            if not isinstance(item, dict) or not isinstance(item.get('x0'), (int,float)) or not isinstance(item.get('w'), (int,float)) or item['w'] <= 0:
                raise ValueError('ENV_AUTHORING_INVALID plot: ' + id)
    for id, frontage in data.get('frontages', {}).items():
        if id not in data['plots'] or len(frontage['bays']) != len(frontage['source']) or any(not isinstance(v, (int,float)) or not math.isfinite(v) or v <= 0 for v in frontage['bays']):
            raise ValueError('ENV_AUTHORING_INVALID frontage: ' + id)
    if data.get('parcelPolicy', 'strict') not in {'strict', 'preserve-incumbent-count'}:
        raise ValueError('ENV_AUTHORING_UNSUPPORTED parcel policy: ' + str(path))
    data['_seen'] = set()
    return data


def edge_id(edge):
    return f"K{edge['block']}_{edge['i']}"


def guard(authoring, edge):
    if authoring is None:
        return None
    id = edge_id(edge)
    source = authoring['plots'].get(id)
    if source is None or id in authoring.get('disabled', []):
        return None
    origin = source['origin']
    # Origin is in Unity coordinates. The caller attaches the trace offset.
    ox, oy = authoring['_offset']
    distance = math.dist((edge['a'][0] + ox, edge['a'][1] + oy), origin)
    dot = sum(a * b for a, b in zip(edge['u'], source['dir']))
    if edge['street'] != source['street'] or edge['role'] != source['role'] or distance > 8 or dot < .85:
        raise ValueError(f'ENV_AUTHORING_CONFLICT {id}: semantic row moved/reidentified; migrate its authored profile explicitly')
    authoring['_seen'].add(id)
    return source


def apply_plots(authoring, edge):
    source = guard(authoring, edge)
    if source is None:
        return
    items = source['items']
    if len(edge['plots']) != len(items):
        if authoring.get('parcelPolicy') != 'preserve-incumbent-count':
            raise ValueError(f"ENV_AUTHORING_CONFLICT {edge_id(edge)}: {len(edge['plots'])} plots versus {len(items)} authored identities")
        # OSM intersection thresholds do not own the number of authored buildings.
        # Keep their identities and width proportions on the edited, guarded edge.
        # This is a bounded reshape, not permission to invent/reidentify a block.
        span = edge['s1'] - edge['s0']
        previous_span = sum(item['w'] for item in items)
        if not items or not .75 <= span / previous_span <= 1.25:
            raise ValueError('ENV_AUTHORING_CONFLICT parcel span: ' + edge_id(edge))
        at = edge['s0']
        edge['plots'] = []
        for saved in items:
            width = span * saved['w'] / previous_span
            edge['plots'].append({'x0': at, 'w': width})
            at += width
    apply_fields(edge['plots'], items)


def apply_fields(plots, items):
    for plot, saved in zip(plots, items):
        # Presence is deliberate too: a procedural field removed from an accepted
        # plot must not reappear simply because a new generator happens to emit it.
        for field in ('type','floors','depth','palette','seed','ground','upper','solana','surrounds','escudo','awning','tall','thin','wall','gate','casona','landmark','unit','corner','era','real','setback','bays'):
            if field in saved:
                plot[field] = copy.deepcopy(saved[field])
            else:
                plot.pop(field, None)
        for key, value in saved.items():
            if key not in {'x0','w','y','ys','basement'}:
                plot[key] = copy.deepcopy(value)


def finish(authoring, spec, terrain=None):
    if authoring is None:
        return
    expected = set(authoring['plots']) - set(authoring.get('disabled', []))
    missing = expected - authoring['_seen']
    if missing:
        raise ValueError('ENV_AUTHORING_MISSING: ' + ', '.join(sorted(missing)))
    rows = {r['id']: r for r in spec['rows']}
    for id, source in authoring['plots'].items():
        if id in authoring.get('disabled', []):
            continue
        if id not in rows or len(rows[id]['plots']) != len(source['items']):
            raise ValueError('ENV_AUTHORING_MISSING final plots: ' + id)
        apply_fields(rows[id]['plots'], source['items'])
    for id, correction in authoring.get('rowEnds', {}).items():
        if 'end:' + id in authoring.get('disabled', []):
            continue
        if id not in rows:
            raise ValueError('ENV_AUTHORING_MISSING end: ' + id)
        rows[id]['ends'].update(correction['values'])
    if 'garden' in authoring and 'garden' not in authoring.get('disabled', []):
        spec['garden'] = copy.deepcopy(authoring['garden'])
        if terrain is not None:
            ox, oz = authoring['_offset']
            for item in spec['garden']:
                generated_y = round(float(terrain([(item['at'][0] - ox, item['at'][1] - oz)])[0]), 3)
                if abs(generated_y - item['y']) > .005:
                    item['y'] = generated_y
    stairs = {s['id']: s for s in spec['stairs']}
    for id, correction in authoring.get('stairs', {}).items():
        if 'stair:' + id in authoring.get('disabled', []):
            continue
        if id not in stairs:
            raise ValueError('ENV_AUTHORING_MISSING stair: ' + id)
        pts = stairs[id]['pts']
        a, b = pts[-2], pts[-1]
        length = math.dist(a[:2], b[:2])
        if length < .001:
            raise ValueError('ENV_AUTHORING_DEGENERATE stair: ' + id)
        extension = correction['extendEnd']
        pts[-1] = [round(b[0] + (b[0] - a[0]) * extension / length, 3), round(b[1] + (b[1] - a[1]) * extension / length, 3), b[2]]

"""Bounded negative checks for POTES-00 reference integrity. Never writes Unity."""
import contextlib
import copy
import hashlib
import io
import json
import re
import sys

import potes_reference as reference

original_read = reference.read
original_write = reference.write
results = []

def run_case(name, mutate, expected_fragment=None):
    documents = {}
    captured = {}
    def read(path):
        key = path.relative_to(reference.OUT).as_posix()
        if key not in documents:
            documents[key] = copy.deepcopy(original_read(path))
            mutate(key, documents[key])
        return documents[key]
    def write(path, value):
        captured.update(value)
    reference.read, reference.write = read, write
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            code = reference.check()
        messages = captured['geometry_integrity_errors'] + captured['evidence_integrity_errors']
        passed = (code == 1 and any(expected_fragment in v for v in messages)) if expected_fragment else (code == 2 and not messages and not captured['ready_for_independent_review'])
        results.append(dict(case=name, passed=passed, code=code, detected_errors=messages))
    finally:
        reference.read, reference.write = original_read, original_write

run_case('Genuine WIP has clean geometry but refuses full acceptance', lambda k,d: None)

def shifted(k,d):
    if k == 'BUILDING_LEDGER.json':
        b=d['buildings'][0]
        for key in ['footprint_local','footprint_metric']:
            for ring in b[key]['value']['coordinates']:
                for p in ring:p[0] += .75
run_case('0.75 metre shifted body is rejected even with matching transform', shifted, 'Footprint changed')

def omitted(k,d):
    if k == 'BUILDING_LEDGER.json':d['buildings'].pop(3)
run_case('Interior omission cannot hide behind target cardinality', omitted, 'Uncounted interior body')

def wrong_sector(k,d):
    if k == 'BUILDING_LEDGER.json':
        next(b for b in d['buildings'] if b['id']=='POT-B007')['sector']='POT-S02'
    if k == 'SECTORS.json':
        next(s for s in d['sectors'] if s['id']=='POT-S01')['members'].remove('POT-B007')
        next(s for s in d['sectors'] if s['id']=='POT-S02')['members'].append('POT-B007')
run_case('Matching sector lists cannot hide half-building ownership', wrong_sector, 'Building not wholly owned by sector')

def false_ready(k,d):
    if k == 'BUILDING_LEDGER.json':
        next(b for b in d['buildings'] if b['id']=='POT-B042')['production_ready']=True
run_case('A ready boolean cannot erase explicit exterior gaps', false_ready, 'Ready flag contradicts recorded blockers')

def false_gate(k,d):
    if k == 'OWNER_GATES.json':
        d['gates'][0]['status']='APPROVED'
        d['gates'][0]['human_decision']=None
run_case('Owner gate needs a recorded human decision', false_gate, 'Owner approval lacks direct human decision')

def opening_station(k,d):
    if k=='FACADE_TRANSCRIPTION.json':d['facades'][0]['rows'][0]['openings'][0]['station_fraction']=1.2
run_case('A numerical opening outside its wall chain is rejected', opening_station, 'Opening station outside registered source edges')

def part_changed(k,d):
    if k=='BUILDING_LEDGER.json':
        part=next(b for b in d['buildings'] if b['id']=='POT-B006')['storey_parts']['value'][2]
        part['geometry']['coordinates'][0][0][0]+=.75
run_case('Recessed facade cannot silently move to a changed part boundary',part_changed,'Registered source plane geometry changed')

def photo_changed(k,d):
    if k=='FACADE_TRANSCRIPTION.json':d['facades'][0]['photo_sha256']='0'*64
run_case('An unchanged photo URL cannot replace pinned transcription bytes',photo_changed,'Transcription photo identity changed')

def lidar_changed(k,d):
    if k=='LIDAR_CONTROLS.json':d['buildings'][0]['point_height_percentiles_m']['p50']+=2
run_case('A fabricated height cannot hide in valid point-source evidence',lidar_changed,'LiDAR controls differ from pinned point-source derivation')

# Consume every evidence artifact and audit all structured bytes, not just a small fixture.
inventory=[]; link_errors=[]
for path in sorted(reference.OUT.rglob('*')):
    if not path.is_file() or path.name=='PRE_REVIEW_CHECKS.json':continue
    raw=path.read_bytes()
    canonical = raw.replace(b'\r\n',b'\n') if path.suffix in ('.json','.geojson','.csv','.md','.txt') else raw
    entry=dict(file=path.relative_to(reference.ROOT).as_posix(),canonical_bytes=len(canonical),
               sha256_lf_text_or_binary=hashlib.sha256(canonical).hexdigest())
    if path.suffix in ('.json','.geojson'):
        data=json.loads(raw)
        entry['json_root']=list(data) if isinstance(data,dict) else 'array'
    elif path.suffix=='.md':
        for target in re.findall(r'\]\(([^)]+)\)',raw.decode('utf-8')):
            if '://' in target or target.startswith('#'):continue
            if not (path.parent/target.split('#')[0]).exists():link_errors.append(str(path)+': '+target)
    inventory.append(entry)
result=dict(status='CHECKS_PASS_WP_NOT_READY' if all(r['passed'] for r in results) and not link_errors else 'CHECK_FAILURE',
    negative_checks=results,local_link_errors=link_errors,artifact_inventory=inventory,
    scope_limit='These guards test geometry/evidence honesty, not complete exterior authority. No independent PASS.')
original_write(reference.OUT/'PRE_REVIEW_CHECKS.json',result)
print(json.dumps(dict(status=result['status'],checks=len(results),artifacts=len(inventory),local_link_errors=link_errors),indent=2))
sys.exit(0 if result['status']=='CHECKS_PASS_WP_NOT_READY' else 1)

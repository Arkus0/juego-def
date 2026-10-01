"""Semantic/admission layer over ASSET-00; no new asset importer.

prepare -> Unity JDAnimationFactory.Run -> review -> build -> validate.
Only build can grant ADMIT, from matching source/policy/runtime/visual evidence.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import asset_catalog as substrate

ROOT = substrate.REPO
POLICY = ROOT / 'Docs/asset_catalog/anim_policy.json'
CATALOG = ROOT / 'Docs/asset_catalog/animations.json'
EVIDENCE = ROOT / 'Docs/evidence/WP-PROD-ANIM-01'
REQUEST = EVIDENCE / 'batch_request.json'
REPORT = EVIDENCE / 'runtime_report.json'
REVIEWS = EVIDENCE / 'visual_review.json'
FACTORY = ROOT / 'Unity/JuegoDef/Assets/JuegoDef/Editor/Animation/AnimationFactory.cs'
VAULT = Path('C:/Juego2-Assets')
FAMILIES = ['locomotion', 'conversation_acting', 'ambient_social', 'work_activity',
            'object_interaction', 'reactions_action', 'special_minigame_combat']

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def family(name):
    n = name.lower()
    if any(x in n for x in ['zombie', 'sword', 'shield', 'pistol', 'bow_', 'spell', 'ninja', 'monster', 'liftair', 'melee', 'punch', 'kick', 'wallrun', 'swim', 'climb', 'flip', 'roll', 'dodge', 'slide', 'jump', 'vault', 'stepup', 'getoffwall', 'kipup', 'bandage', 'death', 'rock', 'paper', 'scissors', 'dance', 'overhandthrow', 'fishing']):
        return 'special_minigame_combat'
    if any(x in n for x in ['talk', 'nodding', 'yes', 'idle_no', 'counter_angry', 'counter_show', 'rail_call']):
        return 'conversation_acting'
    if any(x in n for x in ['hit_', 'surprise', 'crying', 'celebration']):
        return 'reactions_action'
    if any(x in n for x in ['counter_', 'fixing', 'push_', 'carry', 'farm_', 'mining', 'treechopping', 'fish_']):
        return 'work_activity'
    if any(x in n for x in ['interact', 'pickup', 'chest_', 'drink', 'consume']):
        return 'object_interaction'
    if any(x in n for x in ['walk', 'jog', 'sprint', 'turn', 'crouch', 'crawl']):
        return 'locomotion'
    return 'ambient_social'

def inputs():
    source = read(substrate.CATALOG)
    policy = read(POLICY)
    items = [x for x in source['items'] if x['pack'] in ['ual1', 'ual2']]
    by_id = {x['id']: x for x in source['items']}
    if len(set(policy['targetIds'])) != len(policy['targetIds']) or not policy['targetIds']:
        raise ValueError('Missing/duplicate target bodies')
    seen = set()
    for choice in policy['batch']:
        key = choice['id']
        if key not in by_id or by_id[key]['type'] != 'animation' or key in seen:
            raise ValueError('Unknown/duplicate motion in policy: ' + key)
        if choice['family'] not in FAMILIES:
            raise ValueError('Unknown family: ' + key)
        seen.add(key)
    return source, policy, items, by_id

def prepare():
    source, policy, items, by_id = inputs()
    for pack in ['ual1', 'ual2', 'base']:
        substrate.assert_catalog_identity(VAULT, pack, source)
    selected = {x['id']: x for x in policy['batch']}
    request = {
        'schemaVersion': 1, 'policySha256': sha(POLICY),
        'targets': [{'id': key, 'path': by_id[key]['importPath'],
                     'sourceSha256': by_id[key]['sourceSha256']} for key in policy['targetIds']],
        'clips': [{
            'id': x['id'], 'path': x['importPath'], 'name': x['clipName'],
            'sourceSha256': x['sourceSha256'], 'sourceGuid': x['unityGuid'],
            'family': selected.get(x['id'], {}).get('family', family(x['name'])),
            'loop': x['name'].endswith('_Loop') and x['name'] != 'Idle_No_Loop',
            'sample': x['id'] in selected,
            'moving': selected.get(x['id'], {}).get('moving', False)
        } for x in items]
    }
    write(REQUEST, request)
    print('Prepared', len(items), 'clips;', len(selected), 'runtime selections')

def assemble():
    source, policy, items, by_id = inputs()
    request, report, reviews = read(REQUEST), read(REPORT), read(REVIEWS)
    if request['policySha256'] != sha(POLICY) or report['requestSha256'] != sha(REQUEST):
        raise ValueError('Stale policy/request/runtime identity')
    if reviews['runtimeReportSha256'] != sha(REPORT):
        raise ValueError('Visual decisions do not match this runtime report')
    if report['factorySha256'] != sha(FACTORY):
        raise ValueError('Runtime report was produced by different factory code')
    runtime = {x['id']: x for x in report['clips']}
    if len(runtime) != len(report['clips']) or set(runtime) != {x['id'] for x in items}:
        raise ValueError('Missing/duplicate/extra runtime entries')
    visual = {x['id']: x for x in reviews['clips']}
    if len(visual) != len(reviews['clips']):
        raise ValueError('Duplicate visual review')
    selected = {x['id']: x for x in policy['batch']}
    result = []
    for x in items:
        r, selection, review = runtime[x['id']], selected.get(x['id']), visual.get(x['id'])
        if r['sourceSha256'] != x['sourceSha256']:
            raise ValueError('Runtime source identity mismatch: ' + x['id'])
        status, notes = 'ADAPT', ['Indexed; not runtime/visually admitted for B0.']
        if x['name'] == 'A_TPose':
            status, notes = 'REJECT', ['Reference pose, not a usable motion; zero-motion validation fixture.']
        if selection:
            notes = selection['constraints'][:]
            status = 'ADAPT'
            if r['issues']:
                status = 'REJECT'
                notes += r['issues']
            elif review:
                status = review['status']
                if status not in ['ADMIT', 'ADAPT', 'REJECT']:
                    raise ValueError('Unknown review disposition: ' + x['id'])
                notes.append(review['observation'])
                if status == 'ADMIT' and (not report['playMode'] or not r['sampled'] or
                        len(r['targets']) != len(policy['targetIds']) or
                        {t['id'] for t in r['targets']} != set(policy['targetIds']) or
                        any(t['issues'] or not t['validAvatar'] or
                            t['sourceSha256'] != by_id[t['id']]['sourceSha256']
                            for t in r['targets'])):
                    raise ValueError('ADMIT without valid Play Mode retarget evidence: ' + x['id'])
            if status == 'ADMIT' and (not review.get('captures') or
                    review['captures'] != r['captures'] or
                    any(not (EVIDENCE / p).is_file() for p in review['captures'])):
                raise ValueError('ADMIT without visual evidence: ' + x['id'])
            if review:
                for capture in review['captures']:
                    if sha(EVIDENCE / capture) != review['captureSha256'].get(capture):
                        raise ValueError('Visual capture identity mismatch: ' + capture)
        result.append({
            'id': x['id'], 'sourceId': x['id'], 'name': x['name'],
            'path': x['importPath'], 'clipLocalId': r['localId'], 'unityGuid': x['unityGuid'],
            'sourcePath': x['sourcePath'], 'sourceSha256': x['sourceSha256'],
            'license': source['sourcePacks'][x['pack']]['licenseKind'],
            'licensePath': x['licensePath'], 'family': selection['family'] if selection else family(x['name']),
            'tags': selection['tags'] if selection else [x['name'].lower()],
            'rig': 'Unity Humanoid; Quaternius universal rig', 'humanoid': r['humanMotion'],
            'rootMotion': 'in_place; translation/rotation owned by consumer', 'loop': r['loop'],
            'preset': 'ual-in-place-v1', 'status': status, 'notes': notes,
            'compatibleBodies': policy['targetIds'] if status == 'ADMIT' else [],
            'runtimeEvidence': 'Docs/evidence/WP-PROD-ANIM-01/runtime_report.json#' + x['id'],
            'constraints': selection['constraints'] if selection else ['Not admitted'],
            'diagnostics': [{k: t[k] for k in ['id', 'rootDrift', 'loopPoseError',
                'footTravel', 'footFloorMinimum', 'estimatedGaitSpeed', 'forwardDot', 'issues']}
                for t in r['targets']],
        })
    return {'schemaVersion': 1, 'policySha256': sha(POLICY), 'runtimeReportSha256': sha(REPORT),
            'items': result, 'gaps': policy['gaps']}

def validate():
    data = assemble()
    if data != read(CATALOG):
        raise ValueError('Catalogue differs from evidence; build and review changes')
    source = read(substrate.CATALOG)
    problems = substrate.validate(VAULT, source)
    if problems:
        raise ValueError('; '.join(problems))
    admitted = [x for x in data['items'] if x['status'] == 'ADMIT']
    report = read(REPORT)
    if len(admitted) < 12 or len({x['family'] for x in admitted}) < 3:
        raise ValueError('Insufficient meaningful admitted batch')
    if sum(x['sampled'] for x in report['clips']) < 25:
        raise ValueError('Insufficient runtime batch')
    if not report['negativeCases'] or any(not x['detected'] for x in report['negativeCases']):
        raise ValueError('Bad-case detection not demonstrated')
    print(json.dumps({'clips': len(data['items']), 'status': dict(Counter(x['status'] for x in data['items'])),
                      'admittedFamilies': dict(Counter(x['family'] for x in admitted)), 'problems': []}, indent=2))

def main():
    global VAULT
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['prepare', 'build', 'validate', 'search'])
    p.add_argument('--family', choices=FAMILIES)
    p.add_argument('--query', default='')
    p.add_argument('--status', choices=['ADMIT', 'ADAPT', 'REJECT', 'GAP'])
    p.add_argument('--vault', type=Path, default=VAULT)
    a = p.parse_args()
    VAULT = a.vault
    if a.command == 'prepare': prepare()
    elif a.command == 'build':
        data = assemble()
        write(CATALOG, data)
        print(dict(Counter(x['status'] for x in data['items'])))
    elif a.command == 'validate': validate()
    else:
        data = read(CATALOG)
        for x in data['items'] + data['gaps']:
            if a.family and x['family'] != a.family: continue
            if a.status and x['status'] != a.status: continue
            if a.query.lower() not in json.dumps(x, ensure_ascii=False).lower(): continue
            print(x['id'], '|', x['status'], '|', x['family'], '|', ','.join(x.get('tags', [])))
    return 0

if __name__ == '__main__':
    try: sys.exit(main())
    except (ValueError, OSError, KeyError) as e:
        print('ANIM_CATALOG_ERROR:', e, file=sys.stderr)
        sys.exit(1)

"""Real CASCO regeneration checks; run with --osm <the adopted extract>.

Tests the accepted product, independently of the candidate's hash fixtures.
"""
import argparse
import copy
import json
import os
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path
import env_authoring
import env_district_skeleton as skeleton
from env_morphology import Frame

parser = argparse.ArgumentParser()
parser.add_argument('--osm', required=True)
args, remaining = parser.parse_known_args()
ROOT = Path(__file__).resolve().parents[1]
SPECS = ROOT / 'Unity/JuegoDef/Assets/JuegoDef/Env/Specs/districts'
TRACE_PATH = SPECS / 'ENV01_Casco_District.trace.json'
TRACE = json.loads(TRACE_PATH.read_text(encoding='utf-8-sig'))
OSM = json.loads(Path(args.osm).read_text(encoding='utf-8-sig'))
ACCEPTED = json.loads(subprocess.check_output(['git', 'show', '062e1e2a64fe21041d1f0ed08ac4780a24b6e7af:Unity/JuegoDef/Assets/JuegoDef/Env/Specs/districts/ENV01_Casco_District.json'], cwd=ROOT))

def generate(trace=None, authoring=None):
    trace = copy.deepcopy(trace or TRACE)
    a = authoring if authoring is not None else env_authoring.load(TRACE_PATH)
    spec, _, _ = skeleton.build(trace, OSM, Frame(*trace['reference']['origin']), a)
    spec['report'].pop('drops', None)
    return spec

class Inputs(unittest.TestCase):
    def test_01_complete_incumbent_and_repeatability(self):
        self.assertEqual(ACCEPTED, generate())
        self.assertEqual(ACCEPTED, generate())

    def test_02_height_edit_preserves_all_authored_plot_choices(self):
        trace = copy.deepcopy(TRACE)
        trace['nodes']['E1'][2] += .2
        result = generate(trace)
        self.assertNotEqual(ACCEPTED['streets'], result['streets'])
        profiles = env_authoring.load(TRACE_PATH)['plots']
        for row in result['rows']:
            for actual, saved in zip(row['plots'], profiles[row['id']]['items']):
                for key, value in saved.items():
                    if key not in {'x0', 'w'}:
                        self.assertEqual(value, actual.get(key), (row['id'], key))

    def test_03_unknown_authored_field_survives(self):
        a = env_authoring.load(TRACE_PATH)
        a['plots']['K5_4']['items'][0]['futureOwnerIntent'] = {'keep': True}
        result = generate(authoring=a)
        row = next(r for r in result['rows'] if r['id'] == 'K5_4')
        self.assertEqual({'keep': True}, row['plots'][0]['futureOwnerIntent'])

    def test_04_missing_semantic_identity_fails_closed(self):
        a = env_authoring.load(TRACE_PATH)
        a['plots']['missing-row'] = copy.deepcopy(a['plots']['K5_4'])
        with self.assertRaisesRegex(ValueError, 'ENV_AUTHORING_MISSING'):
            generate(authoring=a)

    def test_05_missing_required_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'district.trace.json'
            path.write_text(json.dumps(TRACE), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'ENV_AUTHORING_MISSING'):
                env_authoring.load(path)

    def test_06_explicit_retirement_is_deliberate_input(self):
        a = env_authoring.load(TRACE_PATH)
        a['disabled'].append('stair:Obispo_Escalera')
        result = generate(authoring=a)
        end = next(s for s in result['stairs'] if s['id'] == 'Obispo_Escalera')['pts'][-1]
        self.assertEqual([148.5, 174.5, 2.2], end)

    def test_07_nonfinite_authoring_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'district.trace.json'
            path.write_text(json.dumps(TRACE), encoding='utf-8')
            a = json.loads((SPECS / 'ENV01_Casco_District.authoring.json').read_text(encoding='utf-8'))
            a['plots']['K5_4']['origin'][0] = float('nan')
            path.with_name('district.authoring.json').write_text(json.dumps(a), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'ENV_AUTHORING_NONFINITE'):
                env_authoring.load(path)

    def test_08_node_reshape_preserves_incumbent_parcel_count(self):
        trace = copy.deepcopy(TRACE)
        trace['nodes']['J_A'][0] += 1
        result = generate(trace)
        profiles = env_authoring.load(TRACE_PATH)['plots']
        for row in result['rows']:
            saved = profiles[row['id']]['items']
            self.assertEqual(len(saved), len(row['plots']), row['id'])
            for plot, intent in zip(row['plots'], saved):
                for key,value in intent.items():
                    if key not in {'x0','w'}: self.assertEqual(value,plot.get(key),(row['id'],key))
        target = next(row for row in result['rows'] if row['id']=='K10_1')
        self.assertEqual(2,len(target['plots']))

    def test_09_cross_process_byte_repeatability(self):
        outputs = []
        with tempfile.TemporaryDirectory() as d:
            for seed in ('123', '987'):
                out = Path(d) / (seed + '.json')
                subprocess.run([sys.executable, str(ROOT / 'Tools/env_district_skeleton.py'),
                                '--trace', str(TRACE_PATH), '--osm', args.osm, '--out', str(out)],
                               cwd=ROOT, env=dict(os.environ, PYTHONHASHSEED=seed),
                               check=True, capture_output=True)
                outputs.append(out.read_bytes())
        self.assertEqual(outputs[0], outputs[1])
        self.assertEqual(ACCEPTED,json.loads(outputs[0]))

if __name__ == '__main__':
    unittest.main(argv=[__file__] + remaining)

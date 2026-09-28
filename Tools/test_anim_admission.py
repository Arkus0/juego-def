"""Regression probes for evidence/admission boundaries, using the real frozen batch."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import anim_catalog as factory


class AdmissionFailures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.paths = {}
        for key in ['POLICY', 'REQUEST', 'REPORT', 'REVIEWS']:
            original = getattr(factory, key)
            target = self.root / original.name
            target.write_bytes(original.read_bytes())
            self.paths[key] = target
            ctx = patch.object(factory, key, target)
            ctx.start()
            self.addCleanup(ctx.stop)

    def modify_report(self, action):
        report = factory.read(factory.REPORT)
        action(report)
        factory.write(factory.REPORT, report)
        review = factory.read(factory.REVIEWS)
        review['runtimeReportSha256'] = factory.sha(factory.REPORT)
        factory.write(factory.REVIEWS, review)

    def test_changed_policy_invalidates_runtime(self):
        policy = factory.read(factory.POLICY)
        policy['batch'][0]['tags'].append('new-demand')
        factory.write(factory.POLICY, policy)
        with self.assertRaisesRegex(ValueError, 'Stale policy'):
            factory.assemble()

    def test_duplicate_clip_is_not_extra_batch_evidence(self):
        self.modify_report(lambda r: r['clips'].append(copy.deepcopy(r['clips'][0])))
        with self.assertRaisesRegex(ValueError, 'Missing/duplicate/extra'):
            factory.assemble()

    def test_source_hash_swap_refused(self):
        self.modify_report(lambda r: r['clips'][0].update(sourceSha256='0'*64))
        with self.assertRaisesRegex(ValueError, 'source identity'):
            factory.assemble()

    def test_admitted_motion_needs_both_distinct_bodies(self):
        admitted = next(x['id'] for x in factory.read(factory.REVIEWS)['clips'] if x['status']=='ADMIT')
        def alter(r):
            clip = next(x for x in r['clips'] if x['id']==admitted)
            clip['targets'][1] = copy.deepcopy(clip['targets'][0])
        self.modify_report(alter)
        with self.assertRaisesRegex(ValueError, 'ADMIT without valid Play Mode'):
            factory.assemble()

    def test_edit_mode_report_cannot_prove_runtime(self):
        self.modify_report(lambda r: r.update(playMode=False))
        with self.assertRaisesRegex(ValueError, 'ADMIT without valid Play Mode'):
            factory.assemble()

    def test_missing_capture_prevents_admission(self):
        reviews = factory.read(factory.REVIEWS)
        admitted = next(x for x in reviews['clips'] if x['status']=='ADMIT')
        admitted['captures'] = ['captures/absent-file.png']
        factory.write(factory.REVIEWS, reviews)
        with self.assertRaisesRegex(ValueError, 'ADMIT without visual evidence'):
            factory.assemble()

    def test_changed_capture_hash_refused(self):
        reviews = factory.read(factory.REVIEWS)
        admitted = next(x for x in reviews['clips'] if x['status']=='ADMIT')
        admitted['captureSha256'][admitted['captures'][0]] = '0'*64
        factory.write(factory.REVIEWS, reviews)
        with self.assertRaisesRegex(ValueError, 'Visual capture identity mismatch'):
            factory.assemble()

    def test_wrong_body_source_identity_refused(self):
        admitted = next(x['id'] for x in factory.read(factory.REVIEWS)['clips'] if x['status']=='ADMIT')
        def alter(r):
            clip = next(x for x in r['clips'] if x['id']==admitted)
            clip['targets'][0]['sourceSha256'] = '0'*64
        self.modify_report(alter)
        with self.assertRaisesRegex(ValueError, 'ADMIT without valid Play Mode'):
            factory.assemble()


if __name__ == '__main__':
    unittest.main()

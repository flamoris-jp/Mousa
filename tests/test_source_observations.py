"""Historical holdouts cannot be described as fresh or silently fitted."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SourceObservationLedgerTests(unittest.TestCase):
    def test_known_holdout_observations_and_immutable_results(self):
        ledger = json.loads((ROOT / 'datasets/research-source-observations.json').read_text())
        rows = ledger['observations']
        self.assertEqual(len(rows), len({row['work_id'] for row in rows}))
        by_id = {row['work_id']: row for row in rows}
        self.assertTrue({'mutopia-640', 'mutopia-580', 'mutopia-370',
                         'mutopia-1578', 'mutopia-1558', 'mutopia-921'} <= by_id.keys())
        manifest = json.loads((ROOT / 'datasets/research-exploratory-multifamily-20261112.json').read_text())
        train = {row['work_id'] for row in manifest['works'] if row['split'] == 'train'}
        for row in rows:
            self.assertEqual(row['state'], 'predictive-observed')
            reassigned = row['work_id'] in {'mutopia-1578', 'mutopia-1558', 'mutopia-370'}
            self.assertEqual(row['training_used'], reassigned)
            if reassigned:
                change = row['training_reassignment']
                self.assertEqual(change['cycle'], 29)
                for key in ('assignment', 'result'):
                    self.assertEqual(hashlib.sha256((ROOT/change[key]).read_bytes()).hexdigest(),
                                     change[key+'_sha256'])
                assignment = json.loads((ROOT/change['assignment']).read_text())
                admitted = {w['work_id']: w for w in assignment['additions']}
                self.assertEqual(admitted[row['work_id']]['sha256'], row['source_sha256'])
                result = json.loads((ROOT/change['result']).read_text())
                self.assertEqual(result['conditions']['expanded']['training_events'], 1011)
                clearance = json.loads((ROOT/change['clearance']).read_text())
                self.assertEqual(clearance['status'], 'approved-for-local-experiment')
                self.assertEqual(clearance['assignment_sha256'], change['assignment_sha256'])
                self.assertEqual(clearance['plan_sha256'], result['plan_sha256'])
            self.assertNotIn(row['work_id'], train)
            self.assertEqual(len(row['source_sha256']), 64)
            result = ROOT / row['result']
            self.assertEqual(hashlib.sha256(result.read_bytes()).hexdigest(), row['result_sha256'])

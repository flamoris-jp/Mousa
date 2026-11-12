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
                         'mutopia-1578', 'mutopia-1558'} <= by_id.keys())
        manifest = json.loads((ROOT / 'datasets/research-exploratory-multifamily-20261112.json').read_text())
        train = {row['work_id'] for row in manifest['works'] if row['split'] == 'train'}
        for row in rows:
            self.assertEqual(row['state'], 'predictive-observed')
            self.assertFalse(row['training_used'])
            self.assertNotIn(row['work_id'], train)
            self.assertEqual(len(row['source_sha256']), 64)
            result = ROOT / row['result']
            self.assertEqual(hashlib.sha256(result.read_bytes()).hexdigest(), row['result_sha256'])

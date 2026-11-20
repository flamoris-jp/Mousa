"""Exploratory fit records bind actual results without rewriting old holdouts."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ExpansionUseRecordTests(unittest.TestCase):
    def test_new_handel_use_is_bound_to_nine_work_result(self):
        use = json.loads((ROOT / 'datasets/research-handel98-training-use-cycle29.json').read_text())
        result_path = ROOT / use['first_training_result']
        self.assertEqual(hashlib.sha256(result_path.read_bytes()).hexdigest(), use['result_sha256'])
        result = json.loads(result_path.read_text())
        self.assertEqual(result['conditions']['expanded']['work_count'], 9)
        self.assertEqual(result['conditions']['expanded']['training_events'], 1142)
        assignment = json.loads((ROOT / use['assignment']).read_text())
        rows = {row['work_id']: row for row in assignment['additions']}
        self.assertEqual(rows[use['work_id']]['sha256'], use['source_sha256'])
        self.assertEqual(rows[use['work_id']]['track'], use['selected_track'])
        self.assertNotIn('mutopia-640', rows)
        self.assertNotIn('mutopia-921', rows)
        self.assertEqual(use['state'], 'exploratory-training-used')

    def test_reassigned_sources_retain_observed_history(self):
        rows = json.loads((ROOT / 'datasets/research-source-observations.json').read_text())['observations']
        for row in rows:
            if row['work_id'] not in {'mutopia-1578', 'mutopia-1558', 'mutopia-370'}:
                continue
            self.assertEqual(row['state'], 'predictive-observed')
            self.assertTrue(row['training_used'])
            use = row['subsequent_training_use']
            path = ROOT / use['result']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), use['result_sha256'])
            historical = ROOT / row['result']
            self.assertEqual(hashlib.sha256(historical.read_bytes()).hexdigest(), row['result_sha256'])
            self.assertNotEqual(row['result'], use['result'])


if __name__ == '__main__':
    unittest.main()

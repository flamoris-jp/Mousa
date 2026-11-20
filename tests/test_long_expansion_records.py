"""Long-source fits stay bound to exact profiles and explicit usage records."""
import hashlib
import json
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((ROOT/name).read_text())


class LongExpansionRecordTests(unittest.TestCase):
    def test_registered_profile_and_completed_plans(self):
        profile = read('experiments/2026-11-12-long-interval-profile-plan.json')
        self.assertEqual(profile['max_intervals'], 2048)
        self.assertEqual(profile['threshold'], .8)
        for name, sha in profile['code_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), sha)
        for label, works, events in [('ten', 10, 2536), ('twelve', 12, 3263)]:
            prefix = f'experiments/2026-11-12-{label}-work-expansion-'
            plan = read(prefix+'plan.json')
            screen = read(prefix+'screen.json')
            result = read(prefix+'results.json')
            self.assertFalse(screen['blocked'])
            self.assertEqual(len(screen['crosssplit']), works*2)
            self.assertEqual(len(screen['withintrain']), works*(works-1)//2)
            self.assertTrue(all(row['complete'] for row in screen['crosssplit']+screen['withintrain']))
            self.assertEqual(result['plan_sha256'], hashlib.sha256((ROOT/(prefix+'plan.json')).read_bytes()).hexdigest())
            self.assertEqual(result['conditions']['expanded']['work_count'], works)
            self.assertEqual(result['conditions']['expanded']['training_events'], events)
            self.assertEqual(plan['comparison_profile']['max_intervals'], 2048)
            self.assertEqual(plan['comparison_profile']['threshold'], .8)

    def test_two_new_sources_have_actual_result_evidence(self):
        usage = read('datasets/research-new-cohorts-training-use-cycle30.json')
        self.assertEqual(usage['state'], 'exploratory-training-used')
        result = ROOT/usage['result']
        self.assertEqual(hashlib.sha256(result.read_bytes()).hexdigest(), usage['result_sha256'])
        assignment = read(usage['assignment'])
        assigned = {row['work_id']: row for row in assignment['additions']}
        self.assertEqual({row['id'] for row in usage['added_works']}, {'mutopia-904', 'mutopia-2080'})
        for row in usage['added_works']:
            self.assertEqual(row['source_sha256'], assigned[row['id']]['sha256'])
            self.assertEqual(row['track'], assigned[row['id']]['track'])


if __name__ == '__main__':
    unittest.main()

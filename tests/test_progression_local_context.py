"""Two/ eight-context identities are distinct and cannot be shape-relabelled."""
import copy
import hashlib
import json
import unittest
from test_progression_evaluation import E, fixture

LOCAL = 'mousa.major-progression-local2.weak-label.experimental.v1'


def local_fixture():
    data, fit = fixture()
    data['task_id'] = LOCAL
    for split in ('train', 'test'):
        for row in data[split]:
            row['input'] = [1] + row['input'][-2:]
            row['index'] -= 6
    for key in ('initial_test', 'final_test'):
        for row in fit[key]:
            row['index'] -= 6
    return data, fit


class LocalContextTests(unittest.TestCase):
    def test_local_profile_evaluates_all_six_models(self):
        data, fit = local_fixture(); output = E.evaluate(data, fit)
        self.assertEqual(output['task_id'], LOCAL)
        self.assertEqual(output['context_length'], 2)
        self.assertEqual(len(output['models']), 6)
        self.assertEqual(output['models']['trained_ai']['rows'][0]['index'], 2)

    def test_relabel_without_shape_change_rejected(self):
        for data, task in ((fixture()[0], LOCAL), (local_fixture()[0], E.TASK)):
            data['task_id'] = task
            with self.assertRaises(ValueError): E.validate_data(data)

    def test_unknown_task_rejected(self):
        data, _ = local_fixture(); data['task_id'] = 'unknown'
        with self.assertRaises(ValueError): E.validate_data(data)

    def test_local_minimum_index_and_target_extra_input_rejected(self):
        data, _ = local_fixture(); data['train'][0]['index'] = 1
        with self.assertRaises(ValueError): E.validate_data(data)
        data, _ = local_fixture(); data['train'][0]['input'].append(2)
        with self.assertRaises(ValueError): E.validate_data(data)

    def test_local_ai_index_mismatch_rejected(self):
        data, fit = local_fixture(); fit['final_test'][0]['index'] = 1
        with self.assertRaises(ValueError): E.evaluate(data, fit)

    def test_same_last_two_context_baselines(self):
        data8, fit8 = fixture(); data2, fit2 = local_fixture()
        a, b = E.evaluate(data8, fit8), E.evaluate(data2, fit2)
        for name in ('full_train_unigram', 'full_train_trigram', 'exposure_matched_unigram', 'exposure_matched_trigram'):
            self.assertEqual(a['models'][name]['metrics'], b['models'][name]['metrics'])

    def test_manifest_requires_exact_context(self):
        data, _ = local_fixture(); raw = json.dumps(data).encode(); result = b'results'
        manifest = {'schema': 'mousa.progression-model.experimental.v1', 'task_id': LOCAL,
                    'context_length': 2, 'complete': True, 'steps': 60, 'batch_size': 32, 'seed': 314,
                    'data_sha256': hashlib.sha256(raw).hexdigest(),
                    'results_sha256': hashlib.sha256(result).hexdigest()}
        E.verify_manifest(manifest, raw, result)
        for wrong in (8, True, None):
            bad = copy.deepcopy(manifest); bad['context_length'] = wrong
            with self.assertRaises(ValueError): E.verify_manifest(bad, raw, result)
        del manifest['context_length']
        with self.assertRaises(ValueError): E.verify_manifest(manifest, raw, result)


if __name__ == '__main__': unittest.main()

import copy
import hashlib
import importlib.util
from pathlib import Path
import math
import json
import unittest

PATH = Path(__file__).resolve().parents[1] / 'experiments/maidionis-annotated-events/evaluate.py'
SPEC = importlib.util.spec_from_file_location('annotated_event_evaluate', PATH)
E = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E)


def row(family, index, label, previous=(0, 0)):
    return {'family': family, 'index': index, 'label': label,
            'input': [1] + [v + 2 for v in previous]}


def fixture():
    train = [row('train-a', 8, 0), row('train-a', 9, 1), row('train-b', 8, 1, (1, 1))]
    test = [row('eval-a', 8, 0), row('eval-a', 9, 1), row('eval-b', 8, 1, (3, 3))]
    data = {'schema': 'mousa.annotated-event-training.experimental.v1', 'task_id': E.TASK,
            'train': train, 'test': test}
    scores = [{'family': r['family'], 'index': r['index'], 'target': r['label'],
               'prediction': 0, 'correct': r['label'] == 0, 'nll': 1.0} for r in test]
    indices = [0] * 1920
    fit = {'sampled_indices': indices, 'schedule_indices_sha256': hashlib.sha256(('0,' * 1920).encode()).hexdigest(),
           'initial_test': scores, 'final_test': copy.deepcopy(scores)}
    return data, fit


class EvaluationTests(unittest.TestCase):
    def test_laplace_unigram_and_trigram(self):
        d, _ = fixture()
        unigram = E.count_predictions(d['train'], d['test'], 0)
        trigram = E.count_predictions(d['train'], d['test'], 2)
        self.assertAlmostEqual(unigram[0]['nll'], -math.log(2 / 99))
        self.assertAlmostEqual(unigram[1]['nll'], -math.log(3 / 99))
        self.assertAlmostEqual(trigram[0]['nll'], -math.log(2 / 98))
        self.assertEqual(trigram[0]['prediction'], 0)
        self.assertAlmostEqual(trigram[2]['nll'], math.log(96))

    def test_exposure_and_full_train_are_distinct(self):
        d, f = fixture(); result = E.evaluate(d, f)
        self.assertEqual(len(result['models']), 6)
        self.assertEqual(result['denominators']['sample_unique_rows'], 1)
        self.assertAlmostEqual(result['models']['exposure_matched_unigram']['rows'][0]['nll'], -math.log(1921 / 2016))
        self.assertNotEqual(result['models']['full_train_unigram']['rows'], result['models']['exposure_matched_unigram']['rows'])
        self.assertEqual(result['label_mapping'].split(';')[0], 'relative_root_pc * 8 + quality_index')

    def test_micro_and_family_macro(self):
        d, f = fixture(); summary = E.evaluate(d, f)['models']['trained_ai']['metrics']
        self.assertAlmostEqual(summary['micro']['accuracy'], 1 / 3)
        self.assertAlmostEqual(summary['family_macro']['accuracy'], 1 / 4)
        self.assertEqual(summary['family_macro']['families'], 2)

    def test_no_mutation_or_test_fit(self):
        d, f = fixture(); before = copy.deepcopy((d, f)); E.evaluate(d, f)
        self.assertEqual((d, f), before)
        changed = copy.deepcopy(d['test']); changed[0]['label'] = 13
        a = E.count_predictions(d['train'], d['test'], 2)
        b = E.count_predictions(d['train'], changed, 2)
        self.assertEqual([r['prediction'] for r in a], [r['prediction'] for r in b])
        self.assertEqual(a[1:], b[1:])

    def test_family_leakage_rejected(self):
        d, f = fixture(); d['test'][0]['family'] = 'train-a'
        with self.assertRaisesRegex(ValueError, 'family leakage'): E.evaluate(d, f)

    def test_sample_count_range_bool_and_digest_rejected(self):
        for mutation in (lambda f: f['sampled_indices'].pop(),
                         lambda f: f['sampled_indices'].__setitem__(0, 3),
                         lambda f: f['sampled_indices'].__setitem__(0, True),
                         lambda f: f.update(schedule_indices_sha256='bad')):
            d, f = fixture(); mutation(f)
            with self.assertRaises(ValueError): E.evaluate(d, f)

    def test_score_coverage_identity_target_rejected(self):
        for mutation in (lambda f: f['initial_test'].pop(),
                         lambda f: f['initial_test'].__setitem__(1, copy.deepcopy(f['initial_test'][0])),
                         lambda f: f['initial_test'][0].update(index=99),
                         lambda f: f['initial_test'][0].update(target=2, correct=False)):
            d, f = fixture(); mutation(f)
            with self.assertRaises(ValueError): E.evaluate(d, f)

    def test_nonfinite_and_inconsistent_scores_rejected(self):
        for mutation in (lambda f: f['final_test'][0].update(nll=float('nan')),
                         lambda f: f['final_test'][0].update(correct=False),
                         lambda f: f['final_test'][0].update(prediction=True)):
            d, f = fixture(); mutation(f)
            with self.assertRaises(ValueError): E.evaluate(d, f)

    def test_manifest_binding(self):
        raw_data, raw_results = json.dumps(fixture()[0]).encode(), b'results'
        manifest = {'schema': 'mousa.annotated-event-model.experimental.v1', 'task_id': E.TASK,
                    'context_length': 2, 'complete': True, 'steps': 60, 'batch_size': 32, 'seed': 314,
                    'data_sha256': hashlib.sha256(raw_data).hexdigest(),
                    'results_sha256': hashlib.sha256(raw_results).hexdigest()}
        E.verify_manifest(manifest, raw_data, raw_results)
        with self.assertRaises(ValueError): E.verify_manifest(manifest, b'other', raw_results)
        manifest['complete'] = 1
        with self.assertRaises(ValueError): E.verify_manifest(manifest, raw_data, raw_results)

    def test_context2_boundary_and_full_vocabulary(self):
        d, _ = fixture()
        d['train'][0].update(index=2, input=[1, 97, 97], label=95)
        E.validate_data(d)
        for field, value in [('index', 1), ('label', 96), ('label', True), ('input', [1, 98, 2]), ('input', [1, 2, 2, 2])]:
            mutated = copy.deepcopy(d)
            mutated['train'][0][field] = value
            with self.assertRaises(ValueError): E.validate_data(mutated)
        for task in ('mousa.major-progression-local2.weak-label.experimental.v1', 'wrong'):
            mutated = copy.deepcopy(d); mutated['task_id'] = task
            with self.assertRaises(ValueError): E.validate_data(mutated)

    def test_manifest_hashes_and_protocol_strict(self):
        data, fit = fixture(); db = json.dumps(data).encode(); rb = json.dumps(fit).encode()
        base = {'schema': 'mousa.annotated-event-model.experimental.v1', 'task_id': E.TASK,
                'context_length': 2, 'complete': True, 'steps': 60, 'batch_size': 32, 'seed': 314,
                'data_sha256': hashlib.sha256(db).hexdigest(), 'results_sha256': hashlib.sha256(rb).hexdigest()}
        for key, value in [('schema', 'old'), ('task_id', 'old'), ('context_length', 8), ('seed', 315),
                           ('steps', 61), ('batch_size', True), ('data_sha256', 'wrong'), ('results_sha256', 'wrong')]:
            bad = dict(base); bad[key] = value
            with self.assertRaises(ValueError): E.verify_manifest(bad, db, rb)
        with self.assertRaises(ValueError): E.verify_manifest(base, db + b' ', rb)
        with self.assertRaises(ValueError): E.verify_manifest(base, db, rb + b' ')

    def test_reordered_native_rows_are_aligned(self):
        d, f = fixture(); expected = E.evaluate(d, f)
        f['initial_test'].reverse(); f['final_test'].reverse()
        self.assertEqual(E.evaluate(d, f), expected)


if __name__ == '__main__':
    unittest.main()

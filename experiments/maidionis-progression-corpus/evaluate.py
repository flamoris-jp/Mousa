"""Exposure-matched, fixed-Laplace count baselines for weak chord labels.

Labels mean root + 7 * seventh_flag (root 0..6, flag 0 or 1). Every baseline is
fitted only to train rows. The test set is scored once under fixed alpha=1;
there is no test-based tuning, model selection, or naturalness claim.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

TASK = 'mousa.major-progression.weak-label.experimental.v1'
TASK_CONTEXT = {TASK: 8, 'mousa.major-progression-local2.weak-label.experimental.v1': 2}
CLASSES = 14
ALPHA = 1
DRAWS = 60 * 32


def integer(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError('integer/range required')
    return value


def validate_data(data):
    if (set(data) != {'schema', 'task_id', 'train', 'test'}
            or data['schema'] != 'mousa.progression-training.experimental.v1'
            or data['task_id'] not in TASK_CONTEXT):
        raise ValueError('data identity')
    context_length = TASK_CONTEXT[data['task_id']]
    family_sets = {}
    for split, maximum in (('train', 16384), ('test', 4096)):
        rows = data[split]
        if type(rows) is not list or not 1 <= len(rows) <= maximum:
            raise ValueError('dataset bound')
        identities = set()
        families = set()
        for row in rows:
            if set(row) != {'family', 'input', 'label', 'index'}:
                raise ValueError('row schema')
            if type(row['family']) is not str or not 1 <= len(row['family']) <= 256:
                raise ValueError('family identity')
            integer(row['index'], context_length, 10000000)
            integer(row['label'], 0, CLASSES - 1)
            tokens = row['input']
            if type(tokens) is not list or len(tokens) != context_length + 1:
                raise ValueError('input length')
            integer(tokens[0], 1, 1)
            for token in tokens[1:]:
                integer(token, 2, 15)
            identity = (row['family'], row['index'])
            if identity in identities:
                raise ValueError('duplicate identity')
            identities.add(identity)
            families.add(row['family'])
        family_sets[split] = families
    if family_sets['train'] & family_sets['test']:
        raise ValueError('family leakage')


def context(row):
    """Two preceding labels, never the current test target."""
    return tuple(token - 2 for token in row['input'][-2:])


def count_predictions(training, testing, order):
    if order not in (0, 2):
        raise ValueError('only unigram or trigram is supported')
    counts = defaultdict(Counter)
    for row in training:
        counts[context(row) if order else ()][row['label']] += 1
    predictions = []
    for row in testing:
        # get() avoids modifying fitted state while scoring unseen contexts.
        frequencies = counts.get(context(row) if order else (), {})
        total = sum(frequencies.values())
        probabilities = [(frequencies.get(label, 0) + ALPHA) /
                         (total + ALPHA * CLASSES) for label in range(CLASSES)]
        prediction = max(range(CLASSES), key=probabilities.__getitem__)
        target = row['label']
        predictions.append({'family': row['family'], 'index': row['index'],
                            'target': target, 'prediction': prediction,
                            'correct': target == prediction,
                            'nll': -math.log(probabilities[target])})
    return predictions


def validate_ai_scores(scores, testing, context_length=8):
    if type(scores) is not list or len(scores) != len(testing):
        raise ValueError('AI score coverage')
    by_identity = {}
    for row in scores:
        required = {'family', 'index', 'target', 'prediction', 'correct', 'nll'}
        if type(row) is not dict or set(row) != required:
            raise ValueError('AI score schema')
        if type(row['family']) is not str:
            raise ValueError('AI family identity')
        integer(row['index'], context_length, 10000000)
        integer(row['target'], 0, CLASSES - 1)
        integer(row['prediction'], 0, CLASSES - 1)
        if (type(row['correct']) is not bool
                or row['correct'] != (row['target'] == row['prediction'])):
            raise ValueError('AI correctness mismatch')
        if (type(row['nll']) not in (int, float)
                or not math.isfinite(row['nll']) or row['nll'] < 0):
            raise ValueError('AI invalid NLL')
        identity = (row['family'], row['index'])
        if identity in by_identity:
            raise ValueError('AI duplicate identity')
        by_identity[identity] = row
    ordered = []
    for target_row in testing:
        identity = (target_row['family'], target_row['index'])
        if identity not in by_identity or by_identity[identity]['target'] != target_row['label']:
            raise ValueError('AI target identity mismatch')
        ordered.append(dict(by_identity[identity]))
    return ordered


def metrics(rows):
    if not rows:
        raise ValueError('empty score list')
    grouped = defaultdict(list)
    for row in rows:
        grouped[row['family']].append(row)

    def summarize(part):
        return {'rows': len(part), 'nll': sum(r['nll'] for r in part) / len(part),
                'accuracy': sum(r['correct'] for r in part) / len(part)}

    families = {family: summarize(part) for family, part in sorted(grouped.items())}
    return {'micro': summarize(rows),
            'family_macro': {'families': len(families),
                             'nll': sum(v['nll'] for v in families.values()) / len(families),
                             'accuracy': sum(v['accuracy'] for v in families.values()) / len(families)},
            'per_family': families}


def evaluate(data, fit):
    validate_data(data)
    indices = fit.get('sampled_indices')
    if type(indices) is not list or len(indices) != DRAWS:
        raise ValueError('expected actual 1920 sampled indices')
    for index in indices:
        integer(index, 0, len(data['train']) - 1)
    serialized_schedule = ''.join(str(index) + ',' for index in indices)
    digest = hashlib.sha256(serialized_schedule.encode()).hexdigest()
    if fit.get('schedule_indices_sha256') != digest:
        raise ValueError('sampled schedule digest mismatch')
    context_length = TASK_CONTEXT[data['task_id']]
    initial = validate_ai_scores(fit.get('initial_test'), data['test'], context_length)
    trained = validate_ai_scores(fit.get('final_test'), data['test'], context_length)
    exposure = [data['train'][index] for index in indices]
    models = {'initial_ai': initial, 'trained_ai': trained}
    for population, rows in (('exposure_matched', exposure), ('full_train', data['train'])):
        for name, order in (('unigram', 0), ('trigram', 2)):
            models[population + '_' + name] = count_predictions(rows, data['test'], order)
    return {'schema': 'mousa.progression-baseline-evaluation.v1', 'task_id': data['task_id'], 'context_length': context_length,
            'label_mapping': 'root + 7 * seventh_flag; root=0..6, seventh_flag=0..1',
            'protocol': {'alpha': ALPHA, 'classes': CLASSES,
                         'trigram_context': 'last two prior labels from input[-2:] minus 2',
                         'unseen_context': 'uniform Laplace distribution over 14 labels',
                         'tie_break': 'lowest numeric label',
                         'test_used_for_fit_or_tuning': False,
                         'baseline_exposure_is_observations_not_optimizer_steps': True},
            'denominators': {'train_rows': len(data['train']), 'test_rows': len(data['test']),
                             'train_families': len({r['family'] for r in data['train']}),
                             'test_families': len({r['family'] for r in data['test']}),
                             'sample_draws': len(indices), 'sample_unique_rows': len(set(indices)),
                             'sample_families': len({r['family'] for r in exposure})},
            'schedule_indices_sha256': digest,
            'models': {name: {'metrics': metrics(rows), 'rows': rows}
                       for name, rows in models.items()},
            'limitations': ['Weak labels are automatic analyses, not human harmonic truth.',
                            'Teacher-forced next-label evaluation is not musical quality.',
                            'Count models and neural optimization share observations, not identical learning dynamics.']}


def verify_manifest(manifest, data_bytes, results_bytes):
    data = json.loads(data_bytes)
    validate_data(data)
    expected = {'schema': 'mousa.progression-model.experimental.v1', 'task_id': data['task_id'],
                'context_length': TASK_CONTEXT[data['task_id']],
                'complete': True, 'steps': 60, 'batch_size': 32, 'seed': 314,
                'data_sha256': hashlib.sha256(data_bytes).hexdigest(),
                'results_sha256': hashlib.sha256(results_bytes).hexdigest()}
    if any(manifest.get(key) != value or type(manifest.get(key)) is not type(value)
           for key, value in expected.items()):
        raise ValueError('fit manifest identity or digest mismatch')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, help='optional saved fit manifest for data/results digest binding')
    args = parser.parse_args()
    data_bytes = args.data.read_bytes()
    results_bytes = args.results.read_bytes()
    if args.manifest:
        verify_manifest(json.loads(args.manifest.read_bytes()), data_bytes, results_bytes)
    result = evaluate(json.loads(data_bytes), json.loads(results_bytes))
    result['fit_manifest_digest_binding_verified'] = args.manifest is not None
    result['inputs_sha256'] = {'training_data': hashlib.sha256(data_bytes).hexdigest(),
                               'native_results': hashlib.sha256(results_bytes).hexdigest()}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x') as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({name: value['metrics'] for name, value in result['models'].items()}, indent=2))


if __name__ == '__main__':
    main()

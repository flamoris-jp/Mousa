"""Validate progression contracts without any fitting or corpus admission.

Use --binary, --data, --legacy and a new --out directory. The supplied data is
read only; one row per split is used for validation mutations. Positive checks
call validate, never train. The sole train invocation has a malformed target
that must be rejected before model construction or output creation.
"""
import argparse
import copy
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('binary', 'data', 'legacy', 'out'):
        parser.add_argument('--' + name, required=True, type=Path)
    args = parser.parse_args()
    data = json.loads(args.data.read_text())
    profiles = {'mousa.major-progression.weak-label.experimental.v1': 8,
                'mousa.major-progression-local2.weak-label.experimental.v1': 2}
    if (data.get('schema') != 'mousa.progression-training.experimental.v1'
            or data.get('task_id') not in profiles):
        raise ValueError('unexpected data identity')
    context_length = profiles[data['task_id']]
    base = {**data, 'train': [copy.deepcopy(data['train'][0])],
            'test': [copy.deepcopy(data['test'][0])]}
    if base['train'][0]['family'] == base['test'][0]['family']:
        raise ValueError('fixture already has family leakage')
    args.out.mkdir(parents=True, exist_ok=False)
    cases = []

    def add(name, mutate, expected):
        value = copy.deepcopy(base)
        mutate(value)
        cases.append((name, value, expected))

    add('valid', lambda d: None, None)
    add('legacy-task', lambda d: d.update(task_id='mousa.absolute-degree.experimental.v1'), 'data identity')
    add('legacy-schema', lambda d: d.update(schema='mousa.degree-training-data.experimental.v1'), 'data identity')
    add('extra-data-key', lambda d: d.update(extra=1), 'data identity')
    add('extra-row-key', lambda d: d['train'][0].update(extra=1), 'row schema')
    add('empty-family', lambda d: d['train'][0].update(family=''), 'family identity')
    add('long-family', lambda d: d['train'][0].update(family='x' * 257), 'family identity')
    add('index-too-small', lambda d: d['train'][0].update(index=context_length - 1), 'integer/range required')
    add('invalid-label', lambda d: d['train'][0].update(label=14), 'integer/range required')
    add('boolean-label', lambda d: d['train'][0].update(label=True), 'integer/range required')
    add('boolean-input', lambda d: d['train'][0]['input'].__setitem__(1, True), 'integer/range required')
    add('invalid-history', lambda d: d['train'][0]['input'].__setitem__(1, 16), 'integer/range required')
    add('invalid-task-token', lambda d: d['train'][0]['input'].__setitem__(0, 0), 'integer/range required')
    add('short-history', lambda d: d['train'][0]['input'].pop(), 'input length')
    add('current-label-extra-input', lambda d: d['train'][0]['input'].append(d['train'][0]['label'] + 2), 'input length')
    add('duplicate-train', lambda d: d['train'].append(copy.deepcopy(d['train'][0])), 'duplicate identity')
    add('duplicate-test', lambda d: d['test'].append(copy.deepcopy(d['test'][0])), 'duplicate identity')
    add('family-leak', lambda d: d['test'][0].update(family=d['train'][0]['family']), 'family leakage')
    add('empty-test', lambda d: d.update(test=[]), 'dataset bound')
    add('train-bound', lambda d: d.update(train=d['train'] * 16385), 'dataset bound')
    add('test-bound', lambda d: d.update(test=d['test'] * 4097), 'dataset bound')
    results = []
    binary = str(args.binary.resolve())
    for name, value, expected in cases:
        source = args.out / (name + '.json')
        source.write_text(json.dumps(value) + '\n')
        result = subprocess.run([binary, 'validate', str(source.resolve())],
                                text=True, capture_output=True, timeout=20, check=False)
        if expected is None:
            if result.returncode or 'no model construction or fitting' not in result.stdout:
                raise AssertionError((name, result.returncode, result.stderr))
        elif result.returncode != 1 or result.stderr.strip() != expected:
            raise AssertionError((name, result.returncode, result.stderr, expected))
        results.append({'case': name, 'passed': True, 'fit_executed': False,
                        'stdout': result.stdout.strip(), 'stderr': result.stderr.strip()})
    output = args.out / 'must-not-exist-model'
    result = subprocess.run([binary, 'train', str((args.out / 'invalid-label.json').resolve()),
                             str(output.resolve())], text=True, capture_output=True,
                            timeout=20, check=False)
    if result.returncode != 1 or result.stderr.strip() != 'integer/range required' or output.exists():
        raise AssertionError(('invalid-train-no-output', result.returncode, result.stderr))
    results.append({'case': 'invalid-train-no-output', 'passed': True, 'fit_executed': False})
    result = subprocess.run([binary, 'serve', str(args.legacy.resolve())],
                            text=True, capture_output=True, timeout=20, check=False)
    if result.returncode != 1 or result.stderr.strip() != 'model identity':
        raise AssertionError(('legacy-checkpoint', result.returncode, result.stderr))
    results.append({'case': 'legacy-checkpoint', 'passed': True, 'fit_executed': False})
    receipt = {'schema': 'mousa.progression-native-negative-tests.v1',
               'cases': results, 'passed': len(results), 'fits': 0, 'task_id': data['task_id'], 'context_length': context_length}
    (args.out / 'results.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()

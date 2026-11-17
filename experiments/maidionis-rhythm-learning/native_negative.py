"""Exercise native rejection paths without fitting or loading a checkpoint.

Usage: python native_negative.py --binary BUILD/rhythm_model \
    --data prepared.json --legacy existing-checkpoint --out new-test-directory

The input data is read only. Mutated cases and the rejection receipt are saved
outside the repository. Each case must fail during validation, before checkpoint
loading, fitting, or creation of its model output directory.
"""
import argparse
import copy
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--legacy', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.data.read_text())
    if data.get('schema') != 'mousa.degree-rhythm-training.experimental.v1':
        raise ValueError('unexpected data schema')
    if data.get('task_id') != 'mousa.degree-rhythm.experimental.v1':
        raise ValueError('unexpected task identity')
    # Restrict fixtures to one real row per role, and retain provenance labels.
    # This only tests rejection logic; it is not another model evaluation.
    base = {**data, 'train': [copy.deepcopy(data['train'][0])],
            'test': [copy.deepcopy(data['test'][0])]}
    if base['train'][0]['family'] == base['test'][0]['family']:
        raise ValueError('source fixture already has family leakage')
    args.out.mkdir(parents=True, exist_ok=False)
    cases = []

    def case(name, mutate, expected):
        value = copy.deepcopy(base)
        mutate(value)
        cases.append((name, value, expected))

    case('wrong-task', lambda d: d.update(task_id='mousa.absolute-degree.experimental.v1'), 'data schema')
    case('family-leak', lambda d: d['test'][0].update(family=d['train'][0]['family']), 'train/eval family leakage')
    case('duplicate', lambda d: d['train'].append(copy.deepcopy(d['train'][0])), 'duplicate identity')
    case('task-token', lambda d: d['train'][0]['input'].__setitem__(0, (d['train'][0]['task'] + 1) % 6 + 1), 'task token')
    case('unknown-row', lambda d: d['train'][0].update(unrecognized=1), 'unknown row key')
    case('short-input', lambda d: d['train'][0]['input'].pop(), 'input length')
    # Cardinality 1 guarantees ordinal label 1 is forbidden, independent of
    # the source fixture's scale. Earlier history values may also reject.
    def invalid_history(d):
        d['train'][0]['input'][1] = 7
        d['train'][0]['input'][3] = 120
    case('invalid-history-degree', invalid_history, 'history degree outside scale')

    def invalid_target(d):
        row = d['train'][0]
        row['task'] = 0
        row['input'][0] = 1
        count = row['input'][1] - 6
        if count == 64:
            row['label'] = 192  # all labels valid at cardinality 64; range rejection
        else:
            row['label'] = count
    expected = ('integer/range' if base['train'][0]['input'][1] == 70
                else 'target degree outside scale')
    case('invalid-target-degree', invalid_target, expected)
    case('bool-token', lambda d: d['train'][0]['input'].__setitem__(2, True), 'integer/range')
    case('rest-relation', lambda d: d['train'][0]['input'].__setitem__(6, 407 + ((d['train'][0]['input'][6] - 407 + 1) % 49)), 'history duration/rest relation')
    case('missing-identity', lambda d: d['train'][0].pop('target_index'), 'training row identity required')

    results = []
    for name, mutated, expected in cases:
        source = args.out / (name + '.json')
        source.write_text(json.dumps(mutated) + '\n')
        output = args.out / (name + '-model')
        process = subprocess.run(
            [str(args.binary.resolve()), 'train', str(source.resolve()),
             str(output.resolve()), str(args.legacy.resolve())],
            text=True, capture_output=True, timeout=15, check=False)
        error = process.stderr.strip()
        if process.returncode == 0 or output.exists() or error != expected:
            raise AssertionError((name, process.returncode, error, expected))
        results.append({'case': name, 'rejected_before_fit': True, 'error': error})
    receipt = {'schema': 'mousa.rhythm-native-negative-tests.v1',
               'cases': results, 'passed': len(results)}
    (args.out / 'results.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()

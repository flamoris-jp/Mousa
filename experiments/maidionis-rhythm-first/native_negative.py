"""Native contract tests: fourteen rejections and three no-fit preflights.

Pass --data an independent or rhythm_first prepared data JSON. The numerical
checkpoint is never loaded and no fit is performed: preflight tests use an
intentionally missing legacy directory after row validation. --legacy is used
only to confirm an old checkpoint is rejected by the new serve identity check.
All mutations and results are written to a newly created --out directory.
"""
import argparse
import copy
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ('binary', 'data', 'legacy', 'out'):
        parser.add_argument('--' + option, type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.data.read_text())
    if (data.get('schema') != 'mousa.rhythm-first-training.experimental.v1'
            or data.get('task_id') != 'mousa.rhythm-first-comparison.experimental.v1'
            or data.get('arm') not in ('independent', 'rhythm_first')):
        raise ValueError('unexpected data identity')
    # Source-derived rows keep the original family split. Normalize context to
    # the independent arm, then exercise each arm without teacher consumption.
    rows = {}
    for split in ('train', 'test'):
        row = copy.deepcopy(next(r for r in data[split] if r['task'] == 0))
        if len(row['input']) != 54:
            raise ValueError('expected 54 tokens')
        row['input'][51:] = [0, 0, 0]
        rows[split] = [row]
    if rows['train'][0]['family'] == rows['test'][0]['family']:
        raise ValueError('input has family leakage')
    base = {'schema': data['schema'], 'task_id': data['task_id'],
            'arm': 'independent', **rows}
    args.out.mkdir(parents=True, exist_ok=False)
    cases = []

    def add(name, mutate, expected):
        value = copy.deepcopy(base)
        mutate(value)
        cases.append((name, value, expected))

    def rhythm_first(value):
        value['arm'] = 'rhythm_first'
        for split in ('train', 'test'):
            value[split][0]['input'][51:] = [322, 370, 407]

    def timing_row(row):
        row['task'] = 1
        row['label'] = 11
        row['input'][0] = 2
        row['input'][51:] = [0, 0, 0]
        for index in range(8):
            row['input'][3 + 6 * index] = 183

    add('valid-independent-preflight', lambda d: None, 'input unavailable')
    add('valid-rhythm-first-preflight', rhythm_first, 'input unavailable')
    add('invalid-arm', lambda d: d.update(arm='joint'), 'invalid arm')
    add('old-schema', lambda d: d.update(schema='mousa.degree-rhythm-training.experimental.v1'), 'data schema')
    add('wrong-task', lambda d: d.update(task_id='mousa.degree-rhythm.experimental.v1'), 'data schema')
    add('old-length', lambda d: d['train'][0]['input'].__delitem__(slice(51, None)), 'input length')
    add('independent-current-leak', lambda d: d['train'][0]['input'].__setitem__(51, 322), 'integer/range')
    add('rhythm-first-missing-current', lambda d: d.update(arm='rhythm_first'), 'integer/range')

    def bad_relation(value):
        rhythm_first(value)
        value['train'][0]['input'][53] = 408
    add('current-relation', bad_relation, 'current duration/rest relation')

    def nondegree_context(value):
        rhythm_first(value)
        timing_row(value['train'][0])
        value['train'][0]['input'][51:] = [322, 370, 407]
    add('nondegree-current-leak', nondegree_context, 'integer/range')

    def current_degree(value):
        rhythm_first(value)
        value['train'][0]['input'][51] = 183
    add('current-degree-token', current_degree, 'integer/range')
    add('family-leak', lambda d: d['test'][0].update(family=d['train'][0]['family']), 'train/eval family leakage')
    add('bool-suffix', lambda d: d['train'][0]['input'].__setitem__(51, False), 'integer/range')
    add('unknown-current-field', lambda d: d['train'][0].update(current_degree=64), 'unknown row key')

    def pitch_history_leak(value):
        rhythm_first(value)
        timing_row(value['train'][0])
        # Label128 is a valid tonic at every cardinality, but not neutral64.
        value['train'][0]['input'][3] = 247
    add('rhythm-first-timing-pitch-leak', pitch_history_leak,
        'rhythm-first timing requires neutral degree history')

    def neutral_timing(value):
        rhythm_first(value)
        for split in ('train', 'test'):
            timing_row(value[split][0])
    add('valid-rhythm-first-neutral-timing-preflight', neutral_timing, 'input unavailable')

    # A missing legacy directory makes even an accidentally accepted mutation
    # fail before checkpoint loading and fitting. Exact errors detect that bug.
    missing = args.out / 'intentionally-missing-legacy'
    results = []
    binary = str(args.binary.resolve())
    for name, mutated, expected in cases:
        source = args.out / (name + '.json')
        source.write_text(json.dumps(mutated) + '\n')
        output = args.out / (name + '-model')
        process = subprocess.run(
            [binary, 'train', str(source.resolve()), str(output.resolve()),
             str(missing.resolve())], capture_output=True, text=True,
            timeout=20, check=False)
        if process.returncode == 0 or output.exists() or process.stderr.strip() != expected:
            raise AssertionError((name, process.returncode, process.stderr, expected))
        results.append({'case': name, 'passed': True, 'error': expected,
                        'fit_executed': False})
    process = subprocess.run([binary, 'serve', str(args.legacy.resolve())],
                             capture_output=True, text=True, timeout=20, check=False)
    if process.returncode == 0 or process.stderr.strip() != 'model identity':
        raise AssertionError(('old-model-identity', process.returncode, process.stderr))
    results.append({'case': 'old-model-identity', 'passed': True,
                    'error': 'model identity', 'fit_executed': False})
    receipt = {'schema': 'mousa.rhythm-first-native-negative-tests.v1',
               'cases': results, 'passed': len(results),
               'preflights': 3, 'rejections': 14, 'fits': 0}
    (args.out / 'results.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()

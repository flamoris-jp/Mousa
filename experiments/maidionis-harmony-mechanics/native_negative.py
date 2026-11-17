"""Check harmony-model contracts without fitting.

--data is an original-fixture training JSON; --legacy is an incompatible old
checkpoint directory. --out must be new. The valid case uses validate (no model
construction). Only an invalid chord-root case calls train, which must reject
before creating its output directory. Never run this tool with new teachers.
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
    if (data.get('schema') != 'mousa.harmony-degree-training.experimental.v1'
            or data.get('task_id') != 'mousa.harmony-degree-mechanics.experimental.v1'):
        raise ValueError('unexpected data identity')
    base = {**data, 'rows': [copy.deepcopy(data['rows'][0])]}
    args.out.mkdir(parents=True, exist_ok=False)
    cases = []

    def add(name, mutate, success=False):
        value = copy.deepcopy(base)
        mutate(value)
        cases.append((name, value, success))

    add('valid-fixture', lambda d: None, True)
    add('legacy-task', lambda d: d.update(task_id='mousa.absolute-degree.experimental.v1'))
    add('legacy-schema', lambda d: d.update(schema='mousa.degree-training-data.experimental.v1'))
    add('extra-data-key', lambda d: d.update(extra=1))
    add('extra-row-key', lambda d: d['rows'][0].update(extra=1))
    add('degree-cardinality', lambda d: d['rows'][0].update(degree_count=6))
    add('chord-root', lambda d: d['rows'][0].update(chord_root=7))
    add('chord-seventh', lambda d: d['rows'][0].update(chord_seventh=2))
    add('phase', lambda d: d['rows'][0].update(phase=8))
    add('gap-index', lambda d: d['rows'][0].update(gap_index=2))
    add('history-length', lambda d: d['rows'][0]['history'].pop())
    add('history-label', lambda d: d['rows'][0]['history'].__setitem__(0, 7))
    add('target-label', lambda d: d['rows'][0].update(target=7))
    add('boolean', lambda d: d['rows'][0].update(chord_seventh=True))
    add('empty-family', lambda d: d['rows'][0].update(family_id=''))
    results = []
    binary = str(args.binary.resolve())
    for name, mutated, success in cases:
        source = args.out / (name + '.json')
        source.write_text(json.dumps(mutated) + '\n')
        process = subprocess.run([binary, 'validate', str(source.resolve())],
                                 capture_output=True, text=True, timeout=15, check=False)
        if (process.returncode == 0) != success:
            raise AssertionError((name, process.returncode, process.stderr))
        expected_errors = {
            'legacy-task': 'training task mismatch', 'legacy-schema': 'training task mismatch',
            'extra-data-key': 'training task mismatch', 'extra-row-key': 'row schema',
            'degree-cardinality': 'integer/range required', 'chord-root': 'integer/range required',
            'chord-seventh': 'integer/range required', 'phase': 'integer/range required',
            'gap-index': 'integer/range required', 'history-length': 'history bound',
            'history-label': 'invalid degree label', 'target-label': 'invalid degree label',
            'boolean': 'integer/range required', 'empty-family': 'family identity',
        }
        if not success and (process.returncode != 1 or process.stderr.strip() != expected_errors[name]):
            raise AssertionError((name, process.returncode, process.stderr, expected_errors[name]))
        if success and 'no model construction or fitting' not in process.stdout:
            raise AssertionError('missing no-fit validation receipt')
        results.append({'case': name, 'passed': True, 'fit_executed': False,
                        'stdout': process.stdout.strip(), 'stderr': process.stderr.strip()})
    output = args.out / 'must-not-exist-model'
    process = subprocess.run(
        [binary, 'train', str((args.out / 'chord-root.json').resolve()), str(output.resolve())],
        capture_output=True, text=True, timeout=15, check=False)
    if process.returncode == 0 or output.exists() or process.stderr.strip() != 'integer/range required':
        raise AssertionError(('invalid-train-no-output', process.returncode, process.stderr))
    results.append({'case': 'invalid-train-no-output', 'passed': True, 'fit_executed': False})
    process = subprocess.run([binary, 'serve', str(args.legacy.resolve())],
                             capture_output=True, text=True, timeout=15, check=False)
    if process.returncode == 0 or 'incompatible harmony model' not in process.stderr:
        raise AssertionError(('legacy-checkpoint', process.returncode, process.stderr))
    results.append({'case': 'legacy-checkpoint', 'passed': True, 'fit_executed': False})
    receipt = {'schema': 'mousa.harmony-native-negative-tests.v1',
               'cases': results, 'passed': len(results), 'fits': 0}
    (args.out / 'results.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()

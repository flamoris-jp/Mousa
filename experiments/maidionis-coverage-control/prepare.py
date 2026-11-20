"""Freeze a coverage diagnostic; no fitting, scoring, or test selection."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import random

SOURCE_SHA256 = '49ff7ee03687d77d1707d82985266f9b51fa836154a924ef7529873ea9f6171f'
SEEDS = (42, 43, 44)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def validate_rows(rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError('nonempty rows required')
    seen = set()
    for row in rows:
        if not isinstance(row.get('family'), str) or not row['family']:
            raise ValueError('family required')
        if type(row.get('target_index')) is not int or row['target_index'] < 0:
            raise ValueError('invalid target index')
        key = row['family'], row['target_index']
        if key in seen:
            raise ValueError('duplicate row identity')
        seen.add(key)
        xs = row.get('input')
        if not isinstance(xs, list) or len(xs) != 9 or xs[0] != 1:
            raise ValueError('CLS plus eight intervals required')
        if any(type(x) is not int or not 2 <= x <= 50 for x in xs[1:]):
            raise ValueError('invalid interval token')
        if type(row.get('label')) is not int or not 0 <= row['label'] < 49:
            raise ValueError('invalid label')


def schedule(size, seed, batch_size=32):
    if size <= 0 or batch_size <= 0:
        raise ValueError('positive size and batch size required')
    indices = list(range(size))
    random.Random(seed).shuffle(indices)
    return [indices[i:i + batch_size] for i in range(0, size, batch_size)]


def build(train, test):
    validate_rows(train)
    validate_rows(test)
    if {r['family'] for r in train} & {r['family'] for r in test}:
        raise ValueError('train/test family overlap')
    arms = []
    for seed in SEEDS:
        batches = schedule(len(train), seed)
        if sorted(i for batch in batches for i in batch) != list(range(len(train))):
            raise ValueError('coverage is not exactly once')
        permuted = copy.deepcopy(train)
        rng = random.Random(100000 + seed)
        for original, row in zip(train, permuted):
            context = row['input'][1:]
            rng.shuffle(context)
            row['input'] = [1] + context
            if (row['family'], row['target_index'], row['label']) != (
                    original['family'], original['target_index'], original['label']):
                raise ValueError('permutation changed identity or target')
            if sorted(row['input'][1:]) != sorted(original['input'][1:]):
                raise ValueError('permutation changed token multiset')
        for condition, rows in [('coverage128_ordered', train),
                                ('coverage128_context_permuted', permuted)]:
            arms.append({'condition': condition, 'seed': seed,
                         'train': copy.deepcopy(rows), 'batches': copy.deepcopy(batches)})
    return {'test': copy.deepcopy(test), 'arms': arms}


def prepare(source, out):
    if out.exists():
        raise ValueError('output directory must not exist')
    raw = source.read_bytes()
    if digest(raw) != SOURCE_SHA256:
        raise ValueError('source digest mismatch')
    historical = json.loads(raw)
    ordered = [a for a in historical['arms'] if a['condition'] == 'train128_ordered']
    if len(ordered) != 3 or sorted(a['seed'] for a in ordered) != list(SEEDS):
        raise ValueError('historical ordered arms missing')
    train = ordered[0]['train']
    if any(a['train'] != train for a in ordered):
        raise ValueError('historical training rows differ by seed')
    test = historical['test']
    if (len(train), len({r['family'] for r in train}), len(test),
            len({r['family'] for r in test})) != (4084, 128, 512, 16):
        raise ValueError('unexpected historical cohort size')
    data = build(train, test)
    payload = encode(data)
    plan_path = Path(__file__).with_name('plan.json')
    receipt = {'status': 'prepared_not_fitted_or_scored',
               'source_sha256': SOURCE_SHA256, 'data_sha256': digest(payload),
               'plan_sha256': digest(plan_path.read_bytes()),
               'prepare_sha256': digest(Path(__file__).read_bytes()),
               'arms': 6, 'observations_per_arm': 4084, 'distinct_windows_per_arm': 4084,
               'batches_per_arm': 128, 'final_batch_size': 20,
               'test_status': 'previously observed; not fresh',
               'test_families': 16, 'test_windows': 512,
               'source_rights': 'reuse pinned PR14 PD/BY derivative; no new rights admission'}
    out.mkdir(parents=True, exist_ok=False)
    (out / 'data.json').write_bytes(payload)
    (out / 'preparation-receipt.json').write_bytes(encode(receipt))
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.source, args.out), indent=2))

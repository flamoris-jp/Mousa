"""Reanalyse unchanged private Cycle49 JSON; writes aggregate-only evidence."""
import argparse
import hashlib
import json
from pathlib import Path
from statistics import mean
import time
from order_cycle51 import pitch_groups, recurrence, shuffled_recurrences


def run(source):
    root = Path(__file__).resolve().parents[1]
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    plan = root / 'experiments/2026-11-13-order-cycle51-plan.json'
    ledger = root / 'experiments/2026-11-12-weighting-cycle49-reproduction.json'
    hashes = json.loads(ledger.read_text())['private_sha256']
    if len(hashes) != 36:
        raise ValueError('expected all 36 original outputs')
    rows = []
    start = time.process_time()
    for name, expected in sorted(hashes.items()):
        path = source / name
        if digest(path) != expected:
            raise ValueError(f'source hash mismatch: {name}')
        data = json.loads(path.read_text())
        groups = pitch_groups(data['notes'])
        if len(groups) != len(data['groups']):
            raise ValueError('group reconstruction mismatch')
        row = dict(name=name, source_sha256=expected, groups=len(groups), metrics={})
        for width in (2, 4):
            observed = recurrence(groups, width)
            controls = shuffled_recurrences(groups, width)
            eligible = observed is not None
            row['metrics'][str(width)] = dict(eligible=eligible, windows=max(0,len(groups)-width+1), observed=observed, control_mean=mean(controls) if eligible else None, controls=controls, difference=observed-mean(controls) if eligible else None)
        rows.append(row)
    after = {name: digest(source / name) for name in hashes}
    if after != hashes:
        raise ValueError('source changed during analysis')
    summary = {}
    for mode in ('raw', 'equal_work', 'equal_family'):
        summary[mode] = {}
        for width in ('2','4'):
            cohort = [r['metrics'][width] for r in rows if r['name'].startswith(mode+'-') and r['metrics'][width]['eligible']]
            summary[mode][width] = dict(total=12, eligible=len(cohort), **{key: mean(r[key] for r in cohort) if cohort else None for key in ('observed','control_mean','difference')})
    return dict(schema='mousa-order-cycle51-result-v1', plan_sha256=digest(plan), ledger_sha256=digest(ledger), code_sha256=digest(root/'tools/order_cycle51.py'), runner_sha256=digest(Path(__file__)), rows=rows, summary=summary, source_hashes_after=after, cpu_seconds=time.process_time()-start)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.source)
    with args.output.open('x') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    print(json.dumps(result['summary'], indent=2))

"""Cycle32 bounded nine-addition profile; original validators stay unchanged.

All original per-record gates are delegated to the saved original validator.
Global identity/hash uniqueness is additionally checked across the full list.
Scoped replacement is restored even after errors. No authority is conferred by
schema flags; actual parent review remains necessary for run.
"""
from contextlib import contextmanager
import json
from pathlib import Path
import compare_approved_expansion as base
import compare_long_approved_expansion as long_profile

_ORIGINAL_VALIDATE = base.validate_assignment


def validate_assignment(assignment, blocked_hashes=()):
    if type(assignment) is not dict:
        raise ValueError('assignment schema')
    works = assignment.get('additions')
    if type(works) is not list or not 1 <= len(works) <= 9:
        raise ValueError('one to nine additions required')
    ids, hashes = set(), set()
    for work in works:
        _ORIGINAL_VALIDATE({**assignment, 'additions': [work]}, blocked_hashes)
        if work['work_id'] in ids or work['sha256'] in hashes:
            raise ValueError('duplicate identity or bytes across additions')
        ids.add(work['work_id'])
        hashes.add(work['sha256'])
    return works


@contextmanager
def nine_addition_validation():
    previous = base.validate_assignment
    base.validate_assignment = validate_assignment
    try:
        yield
    finally:
        base.validate_assignment = previous


def prepare(root, corpus, extra, additions_root, assignment_path, diagnostic_paths, plan_dir):
    with nine_addition_validation():
        screen = long_profile.prepare(root, corpus, extra, additions_root, assignment_path, diagnostic_paths, plan_dir)
    path = plan_dir / 'plan.json'
    original = path.read_bytes()
    (plan_dir / 'long-profile-prepare-plan.json').write_bytes(original)
    plan = json.loads(original)
    plan['addition_profile'] = {'max_additions': 9, 'base_work_count': 5,
        'scope': 'Original per-record validation plus global work-ID and SHA uniqueness; scoped replacement only',
        'unchanged_budgets': 'CPU60, five generation seeds, exact2048 interval bound and exact8 OR .80 crosssplit gate'}
    for name in ('tools/compare_fourteen_approved_expansion.py', 'tests/test_fourteen_approved_expansion.py',
                 'datasets/RIGHTS_CYCLE32_CZERNY.md'):
        plan['frozen_hashes'][name] = base.digest(root / name)
    path.write_text(json.dumps(plan, indent=2) + '\n')
    screen['plan_sha256'] = base.digest(path)
    (plan_dir / 'screen.json').write_text(json.dumps(screen, indent=2) + '\n')
    return screen


def run(*args, **kwargs):
    with nine_addition_validation():
        return base.run(*args, **kwargs)


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage', choices=['prepare', 'run'], required=True)
    for key in ('corpus','extra','additions-root','assignment','adam','chopin','plan-dir'):
        p.add_argument('--'+key, type=Path, required=True)
    p.add_argument('--clearance', type=Path)
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    args = (Path(__file__).resolve().parents[1], a.corpus, a.extra, a.additions_root,
            a.assignment, {'640': a.adam, '921': a.chopin}, a.plan_dir)
    if a.stage == 'prepare':
        result = prepare(*args)
    else:
        if a.clearance is None or a.output is None:
            p.error('run requires bound clearance and output')
        result = run(*args, a.clearance, a.output)
    print(json.dumps(result, indent=2))

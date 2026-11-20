"""Corrected cycle32 profile: nine additions and fourteen context works.

Original intake and context modules remain immutable. Run-only model replacement
is restored on success or failure. New model/test/wrapper hashes bind the plan.
"""
from contextlib import contextmanager
import json
from pathlib import Path
import compare_fourteen_approved_expansion as intake
from mousa.fourteen_context_model import FourteenContextModel


@contextmanager
def fourteen_context_profile():
    previous = intake.base.ContextOnsetGateModel
    intake.base.ContextOnsetGateModel = FourteenContextModel
    try:
        yield
    finally:
        intake.base.ContextOnsetGateModel = previous


def synthetic_capability_preflight():
    # No original corpus inputs are accessed by this check.
    from mousa.onset_gate_model import OnsetGateModel
    from mousa.optimized_feasible_generation import generate_optimized
    sequences = [[(0, 1), (1, 2)] for _ in range(14)]
    pitches = [[60, 62] for _ in range(14)]
    factorized = OnsetGateModel([p for seq in sequences for p in seq], factorized=True)
    context = FourteenContextModel(sequences, pitches, timing_context=True, pitch_continuity=True)
    result = generate_optimized(context, 0, target_ticks=8, trailing_rest_ticks=1)
    assert factorized.n == 28 and context.base.n == 28
    assert result['status'] == 'complete'
    return dict(synthetic_only=True, work_count=14, event_count=28,
                factorized_constructed=True, context_constructed=True,
                legacy_optimized_generator_status=result['status'])


def prepare(*args):
    preflight = synthetic_capability_preflight()
    screen = intake.prepare(*args)
    root, *_, plan_dir = args
    path = plan_dir / 'plan.json'
    original = path.read_bytes()
    (plan_dir / 'intake-profile-prepare-plan.json').write_bytes(original)
    plan = json.loads(original)
    plan['synthetic_preflight_before_original_access'] = preflight
    plan['context_work_profile'] = dict(max_works=14,counts='integer sufficient-count merge with no inter-work transitions',
        previous_attempt='experiments/2026-11-12-fourteen-work-initial-failure.json',
        previous_source_state='Two new sources already entered factorized counts during failed run; not pristine')
    for name in ('src/mousa/fourteen_context_model.py','tests/test_fourteen_context_model.py',
                 'tools/compare_fourteen_context_expansion.py'):
        plan['frozen_hashes'][name] = intake.base.digest(root / name)
    path.write_text(json.dumps(plan,indent=2)+'\n')
    screen['plan_sha256'] = intake.base.digest(path)
    (plan_dir/'screen.json').write_text(json.dumps(screen,indent=2)+'\n')
    return screen


def run(*args):
    with fourteen_context_profile():
        return intake.run(*args)


if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage',choices=['prepare','run'],required=True)
    for key in ('corpus','extra','additions-root','assignment','adam','chopin','plan-dir'):
        p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--clearance',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args()
    args=(Path(__file__).resolve().parents[1],a.corpus,a.extra,a.additions_root,a.assignment,{'640':a.adam,'921':a.chopin},a.plan_dir)
    if a.stage=='prepare':result=prepare(*args)
    else:
        if a.clearance is None or a.output is None:p.error('run requires bound clearance and output')
        result=run(*args,a.clearance,a.output)
    print(json.dumps(result,indent=2))

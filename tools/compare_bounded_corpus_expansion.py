"""Prospective32-work profile using immutable original intake/score/generation."""
from contextlib import contextmanager
import json
from pathlib import Path
import compare_approved_expansion as base
import compare_long_approved_expansion as long_profile
from mousa.bounded_context_model import BoundedContextModel
from mousa.onset_gate_model import OnsetGateModel
from mousa.optimized_feasible_generation import generate_optimized
_ORIGINAL_VALIDATE=base.validate_assignment


def validate_assignment(a,blocked_hashes=()):
    if type(a) is not dict or type(a.get('additions')) is not list or not 1<=len(a['additions'])<=27:
        raise ValueError('one to twenty-seven additions required')
    ids=set();canonical=set();hashes=set()
    for work in a['additions']:
        _ORIGINAL_VALIDATE({**a,'additions':[work]},blocked_hashes)
        if work['work_id'] in ids or work['canonical_source_id'] in canonical or work['sha256'] in hashes:
            raise ValueError('duplicate identity, canonical work or bytes')
        ids.add(work['work_id']);canonical.add(work['canonical_source_id']);hashes.add(work['sha256'])
    return a['additions']


@contextmanager
def profile():
    validator,model=base.validate_assignment,base.ContextOnsetGateModel
    base.validate_assignment=validate_assignment;base.ContextOnsetGateModel=BoundedContextModel
    try:yield
    finally:base.validate_assignment=validator;base.ContextOnsetGateModel=model


def preflight(work_count):
    seq=[[(0,1),(1,2)] for _ in range(work_count)];pitch=[[60,62] for _ in seq]
    factor=OnsetGateModel([p for s in seq for p in s],factorized=True)
    context=BoundedContextModel(seq,pitch,timing_context=True,pitch_continuity=True)
    generated=generate_optimized(context,0,target_ticks=8,trailing_rest_ticks=1)
    if factor.n!=2*work_count or context.base.n!=factor.n or generated['status']!='complete':raise AssertionError('synthetic capability failure')
    return dict(synthetic_only=True,works=work_count,events=factor.n,factorized=True,context=True,generator_status=generated['status'])


def prepare(root,corpus,extra,source_root,assignment_path,targets,plan_dir):
    assignment=json.loads(assignment_path.read_text())
    works=validate_assignment(assignment,base.blocked_hashes(root))
    capability=preflight(5+len(works))
    with profile():screen=long_profile.prepare(root,corpus,extra,source_root,assignment_path,targets,plan_dir)
    path=plan_dir/'plan.json';old=path.read_bytes();(plan_dir/'prior-profile-plan.json').write_bytes(old)
    plan=json.loads(old);plan['bounded_corpus_profile']={'max_works':32,'actual_works':5+len(works),'aggregate_events':100000,
      'budgets':'Existing CPU60,5 seeds,exact2048 interval distance,.80/exact8 crosssplit rules unchanged',
      'identity_gate':'Additionally reject repeated canonical source IDs, not only work IDs/hash. No existing blocked source released.'}
    plan['synthetic_preflight_before_source_read']=capability
    for p in ['src/mousa/bounded_context_model.py','tools/compare_bounded_corpus_expansion.py','tests/test_bounded_context_model.py']:
        plan['frozen_hashes'][p]=base.digest(root/p)
    path.write_text(json.dumps(plan,indent=2)+'\n');screen['plan_sha256']=base.digest(path)
    (plan_dir/'screen.json').write_text(json.dumps(screen,indent=2)+'\n');return screen


def run(*args):
    with profile():return base.run(*args)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',choices=['prepare','run'],required=True)
    for k in ('corpus','extra','source-root','assignment','adam','chopin','plan-dir'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--clearance',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    args=(Path(__file__).resolve().parents[1],a.corpus,a.extra,a.source_root,a.assignment,{'640':a.adam,'921':a.chopin},a.plan_dir)
    if a.stage=='prepare':r=prepare(*args)
    else:
        if a.clearance is None or a.output is None:p.error('run requires reviewed clearance and output')
        r=run(*args,a.clearance,a.output)
    print(json.dumps(r,indent=2))

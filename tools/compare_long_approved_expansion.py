"""New bounded2048 comparison profile; prior frozen intake driver unchanged.

Only the read-only comparison used by prepare is replaced. Its exact formula and
.80 gate are unchanged. Final plan binds this wrapper and comparison module.
All parent rights, assignment, crosssplit, coverage, and fit authorization gates
remain those of compare_approved_expansion. No new source is authorized here.
"""
import argparse
import json
from pathlib import Path
import compare_approved_expansion as base
from bounded_interval_similarity import similarity


def prepare(root,corpus,extra,additions_root,assignment_path,diagnostic_paths,plan_dir):
    previous=base.similarity
    try:
        base.similarity=similarity
        screen=base.prepare(root,corpus,extra,additions_root,assignment_path,diagnostic_paths,plan_dir)
    finally:base.similarity=previous
    # Final frozen plan must bind the new profile before any model construction.
    plan_path=plan_dir/'plan.json';original=plan_path.read_bytes()
    (plan_dir/'legacy-prepare-plan.json').write_bytes(original)
    plan=json.loads(original)
    plan['comparison_profile']=dict(max_intervals=2048,formula='1 - exact Levenshtein(intervalsA,intervalsB)/max(lengthA,lengthB)',
        memory='Two rolling rows O(min length); interval extraction O(n+m)',threshold=.80,no_truncation=True,
        predeclared_bound_plan='experiments/2026-11-12-long-interval-profile-plan.json')
    for p in ['tools/compare_long_approved_expansion.py','tools/bounded_interval_similarity.py','experiments/2026-11-12-long-interval-profile-plan.json']:
        plan['frozen_hashes'][p]=base.digest(root/p)
    plan_path.write_text(json.dumps(plan,indent=2)+'\n')
    screen['plan_sha256']=base.digest(plan_path)
    screen['comparison_profile']='exact2048; same .80 and exact8 gate'
    (plan_dir/'screen.json').write_text(json.dumps(screen,indent=2)+'\n')
    return screen


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',choices=['prepare','run'],required=True)
    for k in ('corpus','extra','additions-root','assignment','adam','chopin','plan-dir'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--clearance',type=Path);p.add_argument('--output',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1];targets={'640':a.adam,'921':a.chopin}
    if a.stage=='prepare':result=prepare(root,a.corpus,a.extra,a.additions_root,a.assignment,targets,a.plan_dir)
    else:
        if a.clearance is None or a.output is None:p.error('run requires clearance and output')
        result=base.run(root,a.corpus,a.extra,a.additions_root,a.assignment,targets,a.plan_dir,a.clearance,a.output)
    print(json.dumps(result,indent=2))

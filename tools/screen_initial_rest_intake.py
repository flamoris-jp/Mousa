"""Fixed interval/identity screen for the explicit long-initial-rest candidate.

No fitted model, predictive scoring, source transformation or threshold change.
"""
import argparse
from itertools import combinations
import json
from pathlib import Path
from time import process_time
import compare_approved_expansion as base
import compare_bounded_corpus_expansion as bounded
from bounded_interval_similarity import similarity
from compare_onset_gate_models import phrases


def comparison(a,b):
    x=[n.pitch for n in a.notes];y=[n.pitch for n in b.notes]
    return dict(exact8=len(phrases(x)&phrases(y)),global_similarity=similarity(x,y))


def screen(root,corpus,extra,source_root,assignment,targets,out):
    if out.exists():raise ValueError('new output directory required')
    a=json.loads(assignment.read_text())
    with bounded.profile():b,added,diagnostics,sources,frozen=base.read_inputs(root,corpus,extra,source_root,a,targets)
    train={**b,**added}
    if len(train)!=17 or 'mutopia-2243' not in train:raise ValueError('fixed seventeen-work assignment required')
    prior=root/'datasets/research-cycle33-sixteen-work-assignment.json'
    if base.digest(prior)!=a['prior_assignment_sha256']:raise ValueError('prior assignment changed')
    plan=dict(assignment_sha256=base.digest(assignment),source_sha256=sorted(sources.values()),
        train_ids=list(train),diagnostic_ids=list(diagnostics),fit=False,
        rule='Fixed exact8 OR global interval edit similarity>=0.80 across training/diagnostic boundary blocks whole candidate assignment; withintrain motifs reported, no threshold retuning.',
        profile='exact2048 interval DP; no truncation; CPU60 cooperative check between comparisons',
        rights='Explicit rights-reviewed candidate Purcell2243; source roles remain reserve until actual authorized fit. Anonymous contributor identity unknown.',
        frozen_hashes={**frozen,**{p:base.digest(root/p) for p in ['tools/screen_initial_rest_intake.py','tools/bounded_interval_similarity.py','tools/compare_bounded_corpus_expansion.py','tools/compare_approved_expansion.py','tools/compare_onset_gate_models.py','datasets/research-cycle33-sixteen-work-assignment.json']}},
        timing='Only read original timing here. New firstsupport65536 must be separately validated; no unsupported first interval silently removed.')
    out.mkdir();(out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    start=process_time();cross=[];within=[]
    def checked(x,y):
        if process_time()-start>=60:raise RuntimeError('screen CPU budget exhausted')
        return comparison(x,y)
    for name,m in train.items():
        for ref,n in diagnostics.items():cross.append(dict(source=name,diagnostic=ref,**checked(m,n)))
    for (name,m),(ref,n) in combinations(train.items(),2):within.append(dict(source=name,reference=ref,**checked(m,n)))
    blocked=any(x['exact8'] or x['global_similarity'] is not None and x['global_similarity']>=.8 for x in cross)
    report=dict(plan_sha256=base.digest(out/'plan.json'),blocked=blocked,crosssplit=cross,withintrain=within,
        original_bytes_unchanged=all(base.digest(Path(p))==h for p,h in sources.items()),
        source_timing={k:dict(notes=len(v.notes),first_onset=min(n.start for n in v.notes),selected_eot=v.total_ticks) for k,v in train.items()},
        actual_fit=False,actual_prediction=False,cpu_seconds=process_time()-start)
    (out/'screen.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('corpus','extra','source-root','assignment','adam','chopin','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();r=screen(Path(__file__).resolve().parents[1],a.corpus,a.extra,a.source_root,a.assignment,{'640':a.adam,'921':a.chopin},a.output)
    print(json.dumps(dict(blocked=r['blocked'],crosssplit=len(r['crosssplit']),withintrain=len(r['withintrain']),cpu=r['cpu_seconds'])))

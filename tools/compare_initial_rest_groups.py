"""Fixed six-condition initial-rest comparison. Prepare never fits real data."""
import json
from pathlib import Path
from fractions import Fraction
from math import log
from statistics import mean
from time import process_time
from datetime import datetime, timezone
import compare_approved_expansion as base
import compare_bounded_corpus_expansion as bounded
from compare_onset_gate_models import phrases
from compare_context_onset_gate import metrics, summarize
from mousa.initial_rest_group_model import InitialRestGroupModel, observations, validate, generate

CONDITIONS = [(n, cap, arm) for n, cap in [(16, 12288), (16, 65536), (17, 65536)] for arm in (False, True)]


def prediction(model, seq):
    validate(seq, model.first_limit)
    first = -log(model.probability(seq[0][0]))
    later = sum(-log(model.probability(seq[i][0], len(seq[i-1][2]))) for i in range(1, len(seq)))
    return dict(groups=len(seq), first_groups=1, later_groups=len(seq)-1,
                first_nll=first, later_nll_sum=later,
                later_nll_per_group=later/(len(seq)-1) if len(seq)>1 else None,
                nll_per_group_delta=(first+later)/len(seq))


def outside_mass(model, target=9216):
    if type(target) is not int or not 1<=target<=9216: raise ValueError('bounded target required')
    _, weights, default = model.parameters(None)
    size = model.first_limit+1
    total = sum(weights.values()) + (size-len(weights))*default
    inside = target*default + sum(w-default for d,w in weights.items() if d<target)
    q = Fraction(total-inside,total)
    return dict(numerator=q.numerator, denominator=q.denominator, fraction=float(q),
                meaning='Unconditioned initial-delta probability at or beyond target; timing sampler conditions this away before template feasibility.')


def conditional_initial_signature(model, target=9216):
    if type(target) is not int or not 1<=target<=9216: raise ValueError('bounded target required')
    _, weights, default = model.parameters(None)
    eligible = {d:w for d,w in weights.items() if d<target}
    total = target*default + sum(w-default for w in eligible.values())
    def rational(n):
        q=Fraction(n,total);return [q.numerator,q.denominator]
    return dict(target=target, default_probability=rational(default),
                explicit_probabilities={str(d):rational(w) for d,w in sorted(eligible.items())})


def read_inputs(root, corpus, extra, source_root, assignment, targets):
    with bounded.profile():
        b,a,d,s,f = base.read_inputs(root,corpus,extra,source_root,json.loads(assignment.read_text()),targets)
    train={**b,**a}
    if len(train)!=17 or 'mutopia-2243' not in train: raise ValueError('exact17 prospective corpus required')
    seq={k:observations(v.notes,v.total_ticks) for k,v in {**train,**d}.items()}
    for value in seq.values(): validate(value,65536)
    return train,d,seq,s,f


def preflight():
    # Actual requested largest work count, including preserved long first rest.
    tiny=[[(0,60,((0,96,80,0),)),(96,62,((0,96,80,0),))] for _ in range(16)]
    extra=[(12672,48,((0,192,80,0),)),(192,50,((0,192,80,0),))]
    for n, cap, arm in CONDITIONS:
        m=InitialRestGroupModel(tiny+([extra] if n==17 else []),context=arm,first_limit=cap)
        prediction(m,tiny[0]);generate(m,0,target=768,tail=192)
    return dict(conditions=6,largest_work_count=17,real_sources_fitted=False)


def prepare(root,corpus,extra,source_root,assignment,targets,directory):
    if directory.exists():raise ValueError('new plan directory required')
    synthetic=preflight()
    train,diagnostics,seq,sources,frozen=read_inputs(root,corpus,extra,source_root,assignment,targets)
    ip=root/'experiments/2026-11-12-initial-rest-intake-plan.json'
    sp=root/'experiments/2026-11-12-initial-rest-intake-screen.json'
    intake=json.loads(ip.read_text());screen=json.loads(sp.read_text())
    if screen['blocked'] or screen['plan_sha256']!=base.digest(ip):raise ValueError('intake gate blocked or unbound')
    if intake['assignment_sha256']!=base.digest(assignment) or intake['source_sha256']!=sorted(sources.values()):raise ValueError('intake does not bind inputs')
    old=root/'datasets/research-cycle33-sixteen-work-assignment.json'
    old_records=json.loads(old.read_text())['additions'];new_records=json.loads(assignment.read_text())['additions']
    if old_records != [v for v in new_records if v['work_id']!='mutopia-2243']:raise ValueError('old16 records changed')
    for name in ('tools/compare_initial_rest_groups.py','tests/test_initial_rest_groups_driver.py',
                 'src/mousa/initial_rest_group_model.py','tests/test_initial_rest_group_model.py',
                 'src/mousa/group_onset_model.py','src/mousa/onset_groups.py',
                 'tools/compare_bounded_corpus_expansion.py','tools/compare_approved_expansion.py',
                 'tools/compare_context_onset_gate.py','tools/compare_onset_gate_models.py',
                 'experiments/2026-11-12-initial-rest-intake-plan.json','experiments/2026-11-12-initial-rest-intake-screen.json',
                 'datasets/research-cycle33-sixteen-work-assignment.json','experiments/2026-11-12-group-onset-final2-plan.json',
                 'experiments/2026-11-12-group-onset-results.json','experiments/2026-11-12-initial-rest-profile-proposal.json',
                 'experiments/2026-11-12-initial-rest-independent-profile-check.json'):
        frozen[name]=base.digest(root/name)
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),assignment_sha256=base.digest(assignment),source_sha256=sorted(sources.values()),
              train_ids=list(train),diagnostic_ids=list(diagnostics),frozen_hashes=frozen,conditions=CONDITIONS,synthetic_preflight=synthetic,
              seeds=list(range(5)),cpu_seconds=60,copy_guard='Same all17 training+observed640/921 exact8interval guard for every condition, generated and canonical note order; retain all flags/failures.',
              data_summary={k:dict(notes=len(v.notes),groups=len(seq[k]),selected_eot=v.total_ticks,source_eot=v.source_total_ticks,first_delta=seq[k][0][0]) for k,v in {**train,**diagnostics}.items()},
              outcome='Teacher-forced group delta only, first and later contributions separate. Equal-work diagnostic means. Not joint template/pitch/gate NLL or raw-event NLL.',
              contrasts='16oldcap versus16newcap isolates first prior support.16newcap versus17newcap measures extra training source under same profile; source also changes template/anchor/later counts, not timing alone.',
              conditional_check='Exact normalized sparse eligible first-delta masses must match16newcap/17newcap because extra first onset12672 is outside9216. Does not imply later/template/anchor or full seeded output parity.',
              source_role='Purcell2243 prospective additional training after intake; not fresh holdout.640/921 previously observed untrained diagnostics;580excluded; blocked/pending roles unchanged.',
              generation='Frozen generator target9216,tail384,256note/group limit,64attempts/group; empirical whole templates<=3, no clipping. Expanded first law conditioned to finite remaining target. Same RNG call policy, not aligned later decisions.',
              budget='Shared CPU60 before each fit/evaluation/generation and each generation proposal; not hard preemption within a single operation.',
              limitations=['No musical quality claim.','Allwithintrain links including583↔2243 retained;17works are not17independent families.','More first support reduces unseen-point prior; report target-outside mass explicitly.','Private candidates only; no raw generated notes in Git/training materials.'])
    directory.mkdir();(directory/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');return plan


def run(root,corpus,extra,source_root,assignment,targets,directory,clearance,output):
    if output.exists():raise ValueError('new output required')
    plan=json.loads((directory/'plan.json').read_text());decision=json.loads(clearance.read_text());ph=base.digest(directory/'plan.json')
    if decision.get('status')!='approved-for-local-experiment' or decision.get('plan_sha256')!=ph or not decision.get('review_reference'):raise ValueError('parent bound clearance required')
    if base.digest(assignment)!=plan['assignment_sha256']:raise ValueError('assignment changed')
    for name,digest in plan['frozen_hashes'].items():
        if base.digest(root/name)!=digest:raise ValueError('frozen dependency changed')
    preflight()
    train,diagnostics,seq,sources,_=read_inputs(root,corpus,extra,source_root,assignment,targets)
    if sorted(sources.values())!=plan['source_sha256']:raise ValueError('source hashes changed')
    output.mkdir();(output/'before-fit.json').write_text(json.dumps(dict(plan_sha256=ph,clearance_sha256=base.digest(clearance)))+'\n')
    forbidden=set().union(*(phrases([n.pitch for n in m.notes]) for m in [*train.values(),*diagnostics.values()]))
    start=process_time();results={}
    for n,cap,arm in CONDITIONS:
        label=f'works{n}_first{cap}_'+('context' if arm else 'global')
        if process_time()-start>=60:results[label]=dict(status='cpu_budget_skipped');continue
        keys=[k for k in train if n==17 or k!='mutopia-2243']
        model=InitialRestGroupModel([seq[k] for k in keys],context=arm,first_limit=cap);pred={}
        for k in diagnostics:
            pred[k]=prediction(model,seq[k]) if process_time()-start<60 else dict(status='cpu_budget_skipped')
        rows=[]
        for seed in range(5):
            if process_time()-start>=60:rows.append(dict(seed=seed,status='cpu_budget_skipped'));continue
            g=generate(model,seed,cpu_deadline=start+60);notes=g['notes'];canonical=sorted(notes,key=lambda v:(v['start'],v['end'],v['pitch']))
            hits=len((phrases([v['pitch'] for v in notes])|phrases([v['pitch'] for v in canonical]))&forbidden)
            row={k:v for k,v in g.items() if k not in ('notes','groups')};row.update(seed=seed,copy_matches=hits,metrics=metrics(notes,9216),group_count=len(g['groups']),distinct_later_onsets=all(b['onset']>a['onset'] for a,b in zip(g['groups'],g['groups'][1:])),template_fields_preserved=all(tuple(map(tuple,gr['template'])) in model.templates for gr in g['groups']))
            if hits:row['pre_copy_status']=row['status'];row['status']='copy_guard_blocked'
            path=output/f'{label}-{seed}-private.json';path.write_text(json.dumps(dict(notes=notes,groups=g['groups']),sort_keys=True)+'\n');row['private_sha256']=base.digest(path);rows.append(row)
        means,denom=summarize(rows)
        results[label]=dict(training_ids=keys,first_limit=cap,context=arm,prediction=pred,equal_work_nll=mean(v['nll_per_group_delta'] for v in pred.values()) if all('nll_per_group_delta' in v for v in pred.values()) else None,initial_outside_target_mass=outside_mass(model),conditional_initial_signature=conditional_initial_signature(model),training_groups=model.template_occurrences,template_types=len(model.templates),ineligible_template_occurrences=model.ineligible_occurrences,ineligible_fraction=model.ineligible_occurrences/model.template_occurrences,outputs=rows,complete_only_means=means,metric_denominators=denom)
    conditional_checks={}
    for arm in ('global','context'):
        a=results.get('works16_first65536_'+arm,{}).get('conditional_initial_signature')
        b=results.get('works17_first65536_'+arm,{}).get('conditional_initial_signature')
        conditional_checks[arm]=dict(compared=a is not None and b is not None,exact_equal=a==b if a is not None and b is not None else None)
    report=dict(plan_sha256=ph,conditions=results,conditional_initial_16new_vs17new=conditional_checks,cpu_seconds=process_time()-start,originals_unchanged=all(base.digest(Path(p))==sha for p,sha in sources.items()),matched_seed_statuses=[dict(seed=i,conditions={k:next((r['status'] for r in v.get('outputs',[]) if r['seed']==i),'not_run') for k,v in results.items()}) for i in range(5)],limitations=plan['limitations'])
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['prepare','run'],required=True)
    for k in ('corpus','extra','source-root','assignment','adam','chopin','plan-dir'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--clearance',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    args=(Path(__file__).resolve().parents[1],a.corpus,a.extra,a.source_root,a.assignment,{'640':a.adam,'921':a.chopin},a.plan_dir)
    if a.stage=='prepare':result=prepare(*args)
    else:
        if a.clearance is None or a.output is None:p.error('run requires clearance/output')
        result=run(*args,a.clearance,a.output)
    print(json.dumps(result,indent=2))

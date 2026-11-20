"""Prospective fixed four-arm timing evaluation; Dowland is never fitted."""
import json
from pathlib import Path
from datetime import datetime, timezone
from time import process_time
from math import log
from statistics import mean
import compare_approved_expansion as base
from compare_initial_rest_groups import read_inputs
from compare_gate_context_groups import preflight
from screen_initial_rest_intake import comparison
from mousa.overlap_midi import read_midi
from mousa.initial_rest_group_model import observations, validate
from mousa.gate_context_group_model import GateContextGroupModel, ARMS
ROOT=Path(__file__).resolve().parents[1]
SHARED=ROOT.parent

def write(path,value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

def inputs():
    train,old,seq,sources,frozen=read_inputs(ROOT,SHARED/'mousa-transfer-corpus-20261112',SHARED/'mousa-cycle10-rights-20261112/cornelius-ein-ton.mid',SHARED,ROOT/'datasets/research-cycle36-seventeen-work-assignment.json',{'640':SHARED/'mousa-cycle16-rights-20261112/640-minuit_chretiens.mid','921':SHARED/'mousa-cycle21-rights/Chop-28-4a.mid'})
    new={k:read_midi(SHARED/f'mousa-cycle39-rights/{k}.mid',1) for k in ('21','1691')}
    for k,m in new.items():
        seq[k]=observations(m.notes,m.total_ticks);validate(seq[k],65536)
        sources[str(SHARED/f'mousa-cycle39-rights/{k}.mid')]=base.digest(SHARED/f'mousa-cycle39-rights/{k}.mid')
    return train,old,new,seq,sources,frozen

def prepare(out):
    if out.exists():raise ValueError('new directory required')
    synthetic=preflight();train,old,new,seq,sources,frozen=inputs()
    prior=ROOT/'experiments/2026-11-12-gate-context-plan.json'
    # Resolve the frozen final plan by the clearance, never guess a mutable model.
    clearance=json.loads((ROOT/'experiments/2026-11-12-gate-context-clearance.json').read_text())
    candidates=list((ROOT/'experiments').glob('*gate-context*plan*.json'))
    prior=next(p for p in candidates if base.digest(p)==clearance['plan_sha256'])
    oldplan=json.loads(prior.read_text())
    for name,digest in oldplan['frozen_hashes'].items():
        if base.digest(ROOT/name)!=digest:raise ValueError('prior model dependency changed: '+name)
    frozen.update(oldplan['frozen_hashes'])
    ledger=json.loads((ROOT/'datasets/research-dowland-reserved-cycle39-20261112.json').read_text())
    if ledger['status']!='rights-reviewed-reserve-screen-clear-not-fit-not-scored':raise ValueError('rights role changed')
    for w in ledger['works']:
        k=w['id'].split('-')[-1]
        if base.digest(SHARED/f'mousa-cycle39-rights/{k}.mid')!=w['source_sha256']:raise ValueError('new source changed')
    screen=json.loads((ROOT/'experiments/2026-11-12-dowland-cycle39-screen.json').read_text())
    if any(row['flagged'] for row in screen['comparisons']):raise ValueError('previous fixed screen blocked')
    if screen['plan_sha256']!=base.digest(ROOT/'experiments/2026-11-12-dowland-cycle39-screen-plan.json'):raise ValueError('unbound screen')
    # Recheck split directly with the exact current sources; blocked references
    # remain covered by the unchanged original screen and their hash verification.
    sp=json.loads((ROOT/'experiments/2026-11-12-dowland-cycle39-screen-plan.json').read_text())
    blocked=[SHARED/'mousa-cycle18-rights-20261112/1692/Duett-Telemann-1.mid',SHARED/'mousa-cycle22-rights/sonatina-1-1.mid',SHARED/'mousa-cycle25-rights/1741-LiederOhneWorte_-_Op30_No6.mid']
    refs={**train,**old,**{p.name:read_midi(p,1) for p in blocked}}
    if sorted([v for p,v in sources.items() if not p.endswith(('/21.mid','/1691.mid'))]+[base.digest(p) for p in blocked])!=sp['reference_sha256']:raise ValueError('reference set changed')
    checks=[dict(candidate=k,reference=r,**comparison(m,n)) for k,m in new.items() for r,n in refs.items()]
    checks.append(dict(candidate='21',reference='1691',**comparison(new['21'],new['1691'])))
    if any(x['exact8'] or x['global_similarity']>=.8 for x in checks):raise ValueError('fixed split blocked')
    for name in ('tools/evaluate_dowland_cycle40.py','tests/test_dowland_cycle40.py','datasets/research-dowland-reserved-cycle39-20261112.json','datasets/research-cycle36-seventeen-work-assignment.json','experiments/2026-11-12-dowland-cycle39-screen.json','experiments/2026-11-12-dowland-cycle39-screen-plan.json'):
        frozen[name]=base.digest(ROOT/name)
    plan=dict(created_utc=datetime.now(timezone.utc).isoformat(),frozen_hashes=frozen,source_sha256=sorted(sources.values()),conditions=list(ARMS),train_ids=list(train),train_notes=sum(len(m.notes) for m in train.values()),train_groups=sum(len(seq[k]) for k in train),evaluation_ids=list(new),prior_plan_sha256=base.digest(prior),synthetic_preflight=synthetic,split_recheck=checks,
        evaluation_summary={k:dict(notes=len(m.notes),groups=len(seq[k]),first_delta=seq[k][0][0],eot=m.total_ticks,source_eot=m.source_total_ticks,ppq=m.ppq) for k,m in new.items()},
        metric='Teacher-forced group-delta natural-log loss only. First and later losses separate; equal-work mean primary, pooled group-weighted mean secondary. Report all four arms and both works; no event-NLL or musical-quality claim.',
        role='Two previously unscored works in one Dowland1597/PeterChubb cohort; representation and rights previously inspected. Not two independent cohorts. Both become observed at first predictive attempt; neither enters training.640/921 remain old observed diagnostics and are not rescored here.',
        support='Frozen first65536/later12288/gates12288; all source notes/templates and exact ticks. No rescaling, clipping, filtering or training on evaluation data.',cpu_seconds=60,budget='Cooperative check before each fit/evaluate/audit; no hard preemption inside one bounded call.',journal='Append-only flush+fsync before and after every prediction attempt, including failed attempts; any attempt irreversibly marks work observed. Repeat is replay, not fresh evaluation.',generation=False,actual_real_fit=False,actual_prediction=False)
    out.mkdir();write(out/'plan.json',plan);return plan

def run(plan_dir,clearance,output):
    if output.exists():raise ValueError('new output directory required')
    plan=json.loads((plan_dir/'plan.json').read_text());ph=base.digest(plan_dir/'plan.json');c=json.loads(clearance.read_text())
    if c.get('status')!='approved-for-local-experiment' or c.get('plan_sha256')!=ph:raise ValueError('bound approval required')
    for name,h in plan['frozen_hashes'].items():
        if base.digest(ROOT/name)!=h:raise ValueError('changed dependency '+name)
    train,old,new,seq,sources,_=inputs()
    if sorted(sources.values())!=plan['source_sha256']:raise ValueError('source mismatch')
    output.mkdir();write(output/'before-fit.json',dict(plan_sha256=ph,clearance_sha256=base.digest(clearance),train_ids=list(train),evaluation_not_training=list(new)))
    import os
    def journal(event,**fields):
        with (output/'prediction-journal.jsonl').open('a') as f:
            f.write(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(),event=event,plan_sha256=ph,**fields))+'\n');f.flush();os.fsync(f.fileno())
    start=process_time();results={}
    for arm in ARMS:
        if process_time()-start>=60:results[arm]={'status':'cpu_budget_skipped'};continue
        journal('fit_attempt',arm=arm,training_ids=list(train))
        model=GateContextGroupModel([seq[k] for k in train],arm=arm);journal('fit_complete',arm=arm)
        rows={}
        for k in new:
            if process_time()-start>=60:rows[k]={'status':'cpu_budget_skipped'};continue
            journal('prediction_attempt',arm=arm,work=k,irreversibly_observed=True)
            try:
                value=model.evaluate(seq[k]);journal('prediction_complete',arm=arm,work=k)
                # Independent aggregate from exact probability calls, reset history.
                previous=None;horizon=0;losses=[]
                for delta,anchor,template in seq[k]:
                    losses.append(-log(model.probability(delta,previous)));horizon,previous=model.advance(horizon,delta,template)
                error=abs(sum(losses)/len(losses)-value['nll_per_group_delta'])
                if error>1e-12:raise ValueError('aggregate audit mismatch')
                rows[k]=dict(status='complete',**value,independent_aggregate_absolute_error=error)
            except Exception as e:
                rows[k]={'status':'failed','error':str(e)};journal('prediction_failure',arm=arm,work=k,error=str(e))
        complete=[v for v in rows.values() if v['status']=='complete']
        results[arm]=dict(prediction=rows,complete_works=len(complete),expected_works=2,equal_work_nll=mean(v['nll_per_group_delta'] for v in complete) if len(complete)==2 else None,pooled_group_nll=sum(v['first_nll']+v['later_nll_sum'] for v in complete)/sum(v['groups'] for v in complete) if len(complete)==2 else None)
    report=dict(plan_sha256=ph,conditions=results,cpu_seconds=process_time()-start,originals_unchanged=all(base.digest(Path(p))==h for p,h in sources.items()),evaluation_fitted=False,limits=plan['role'])
    write(output/'report.json',report);return report

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','run']);p.add_argument('--plan-dir',type=Path,required=True);p.add_argument('--clearance',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    v=prepare(a.plan_dir) if a.stage=='prepare' else run(a.plan_dir,a.clearance,a.output)
    print(json.dumps(v,indent=2))

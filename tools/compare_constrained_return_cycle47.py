"""Frozen four-policy replay on six already-observed candidates; no fitting."""
from pathlib import Path
import json,hashlib,time
from datetime import datetime,timezone
from statistics import mean
from compare_weighted_maple_cycle45 import read,ROOT,public_structure
from mousa.constrained_return_cycle47 import compare_policy
from mousa.group_timeline_metrics import timeline_metrics
from compare_context_onset_gate import metrics
ARMS=[('postreject_strict',False,False),('constrained_strict',True,False),('postreject_singleton',False,True),('constrained_singleton',True,True)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def prepare(out):
    if out.exists():raise ValueError('retain plan')
    train,diag,_,sources,_,_=read()
    priorpath=ROOT/'experiments/2026-11-12-silence-return-cycle46-final-plan.json';prior=json.loads(priorpath.read_text());frozen=dict(prior['frozen_hashes'])
    for f,h in frozen.items():
        if sha(ROOT/f)!=h:raise ValueError('frozen changed')
    own=['src/mousa/constrained_return_cycle47.py','tools/compare_constrained_return_cycle47.py','tests/test_constrained_return_cycle47.py','tests/test_constrained_return_cycle47_driver.py','experiments/2026-11-12-silence-return-cycle46-final-plan.json','experiments/2026-11-12-silence-return-cycle46-results.json']
    frozen.update({f:sha(ROOT/f) for f in own});pool=[]
    previous=json.loads((ROOT/'experiments/2026-11-12-silence-return-cycle46-results.json').read_text())
    for cohort,c in previous['cohorts'].items():
        for row in c['rows']:
            path=ROOT.parent/f'mousa-cycle46-silence-initial/{cohort}-{row["seed"]}-private.json'
            if sha(path)!=row['private_sha256']:raise ValueError('old candidate changed')
            pool.append(dict(historical_cohort=cohort,seed=row['seed'],file=str(path.relative_to(ROOT.parent)),sha256=sha(path)))
    p=dict(created_utc=datetime.now(timezone.utc).isoformat(),frozen_hashes=frozen,source_sha256=sorted(sources.values()),copy_reference_ids=list(train)+list(diag),pool=pool,arms=ARMS,cpu_seconds=60,state_cap=4096,transition_cap=200000,
      rules='Keep gap192 and original segments1/3. Target>=2groups. Strictsource>=2;fallbackallows source1 but labels singleton_fallback_complete, never counts as phraseeligible success. Emptyreject; noothersegmentsearch. SameoriginalAordinal+2pitchclass; wholetemplates/time/vel/EOT retained.',
      exact_search='Constrainedstate=(lastanchor,allstillactive target pitches/ends). Check fixed external notes against each candidate including futureoverlap. Halfopen ends<=onset expire. Same-state dominance only min(cost,lexpath). AlllegalMIDI candidates; max4096states/200000transitions. If cap hit report failure, no partialsolution. Copyguard remains afterchosenpath withoutalternative search.',
      design='2x2postreject/constrained x strict/singleton. Each cell applied to same6alreadyobserved originals. Historical known/new_random labels retained only for provenance, neitherfresh. No fit/no newgeneration/no humanratings.',
      reporting='All24attempts, status and failure reasons, stricteligible and singletonfallback separate denominators, perhistoricalcohort and metric-common seeds. Rawintervals/anchor arrays private. Compare legacy strict postreject status and notes/groups to frozenCycle46.',
      limitations=['Collision-aware optimum changes feasibility and may increase objective. Not probability-equivalent to oldpostreject method.','Singleton repetition is not learned phrase or melodic return.','Copy fail stillrejects no optimizationaround it.','Minpitchanchor proxy is not voice/harmonytruth or attractiveness.','Sameobserved6 is exploratory and small;conditionorder underCPUlimit affects availability.'])
    out.mkdir(parents=True);write(out/'plan.json',p);return p
def run(planpath,clearance,out):
    if out.exists():raise ValueError('retain run')
    p=json.loads(planpath.read_text());c=json.loads(clearance.read_text())
    if c.get('approved') is not True or c.get('plan_sha256')!=sha(planpath):raise ValueError('bound approval')
    for f,h in p['frozen_hashes'].items():
        if sha(ROOT/f)!=h:raise ValueError('frozen changed')
    start=time.process_time();train,diag,_,sources,_,_=read()
    if sorted(sources.values())!=p['source_sha256']:raise ValueError('sources changed')
    refs=[[n.pitch for n in m.notes] for m in [*train.values(),*diag.values()]]
    out.mkdir();write(out/'before-analysis.json',dict(plan_sha256=sha(planpath),no_model_fit=True,no_new_generation=True));rows=[];parity_checks=0
    for item in p['pool']:
        path=ROOT.parent/item['file']
        if sha(path)!=item['sha256']:raise ValueError('pool changed')
        original=json.loads(path.read_text());g=original['original'];row=dict(seed=item['seed'],historical_cohort=item['historical_cohort'],arms={})
        private={}
        for label,constrained,singleton in p['arms']:
            if time.process_time()-start>=60:raw=dict(status='cpu_budget_skipped')
            else:raw=compare_policy(g['notes'],g['groups'],refs,collision_constrained=constrained,allow_singleton=singleton,cpu_deadline=start+60)
            if label=='postreject_strict' and raw['status'] not in ('cpu_budget_skipped','cpu_budget_blocked'):
                old=original['comparison']['intervention']
                if raw['status']!=old['status']:raise ValueError('legacy status drift')
                for k in ('notes','groups'):
                    if k in old and raw.get(k)!=old[k]:raise ValueError('legacy output drift')
                parity_checks+=1
            private[label]=raw
            public={k:v for k,v in raw.items() if k not in ('notes','groups')}
            if 'notes' in raw:public.update(metrics=metrics(raw['notes'],9216),timeline=timeline_metrics(raw['notes'],9216),structure=public_structure(raw['notes'],raw['groups']))
            row['arms'][label]=public
        q=out/f'{item["historical_cohort"]}-{item["seed"]}-private.json';write(q,private);row['private_sha256']=sha(q);rows.append(row);write(out/'progress.json',rows)
    summaries={}
    for cohort in ('known','new_random'):
        subset=[r for r in rows if r['historical_cohort']==cohort];summaries[cohort]={}
        common=[r['seed'] for r in subset if all(r['arms'][a[0]]['status']=='complete' for a in p['arms'])]
        for label,_,_ in p['arms']:
            items=[r['arms'][label] for r in subset]
            summary=dict(attempts=len(items),status_counts={s:sum(v['status']==s for v in items) for s in {v['status'] for v in items}},multi_group_complete=sum(v['status']=='complete' for v in items),singleton_complete=sum(v['status']=='singleton_fallback_complete' for v in items),all4_multi_group_common_seeds=common)
            eligible=[r['arms'][label] for r in subset if r['seed'] in common]
            summary['common_metrics']={k:dict(mean=mean(v['metrics'][k] for v in eligible if v['metrics'][k] is not None) if any(v['metrics'][k] is not None for v in eligible) else None,denominator=sum(v['metrics'][k] is not None for v in eligible)) for k in eligible[0]['metrics']} if eligible else {}
            summaries[cohort][label]=summary
    report=dict(plan_sha256=sha(planpath),rows=rows,summaries=summaries,legacy_status_output_parity_checks=parity_checks,legacy_all6_status_output_parity=parity_checks==6,cpu_seconds=time.process_time()-start,originals_unchanged=all(sha(Path(f))==h for f,h in sources.items()),no_fit=True,no_new_generation=True,limitations=p['limitations'])
    write(out/'report.json',report);return report
if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('mode',choices=['prepare','run']);a.add_argument('--output',type=Path,required=True);a.add_argument('--plan',type=Path);a.add_argument('--clearance',type=Path);v=a.parse_args()
    if v.mode=='run' and (v.plan is None or v.clearance is None):a.error('plan/clearance')
    print(json.dumps(prepare(v.output) if v.mode=='prepare' else run(v.plan,v.clearance,v.output),indent=2))

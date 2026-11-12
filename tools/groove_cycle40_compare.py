"""Four parent-gated fixed marginal laws; training-group weights only."""
from datetime import datetime,timezone
from fractions import Fraction
from pathlib import Path
from hashlib import sha256
import argparse
import json
import math
import time
from mousa.groove_cycle40_weighted import WeightedGrooveMarginal,equal_group_weights,CONDITIONS
from compare_groove_ioi import check_clearance,summarize_drummers
from prepare_groove_split import read_events

REPO=Path(__file__).resolve().parents[1]
PRIOR='experiments/2026-11-12-groove-cycle39-fit-plan.json'
OLD='experiments/2026-11-12-groove-cycle39-results.json'
FILES=['src/mousa/groove_cycle40_weighted.py','tests/test_groove_cycle40_weighted.py','tools/groove_cycle40_compare.py','tests/test_groove_cycle40_compare.py',PRIOR,OLD,'datasets/research-groove-usage-cycle39-20261112.json']
def sha(p):return sha256(p.read_bytes()).hexdigest()
def rational(x):return {'numerator':x.numerator,'denominator':x.denominator,'decimal':float(x)}


def weight_diagnostics(lengths,weights,groups):
    if len(lengths)!=len(weights) or len(lengths)!=len(groups) or not lengths:raise ValueError('aligned metadata required')
    mass=sum((n*w for n,w in zip(lengths,weights)),Fraction());squares=sum((n*w*w for n,w in zip(lengths,weights)),Fraction())
    return {'weighted_event_mass':rational(mass),'sum_event_weights_squared':rational(squares),
            'Kish_event_ESS':rational(mass*mass/squares),'min_event_weight':rational(min(weights)),'max_event_weight':rational(max(weights)),
            'drummer_mass':{g:rational(sum((n*w for n,w,gg in zip(lengths,weights,groups) if gg==g),Fraction())) for g in sorted(set(groups))},
            'interpretation':'Kish calculation treats weights algebraically; strongly dependent musical events mean this is NOT an independent observation count or a calibrated statistical sample size.'}


def prepare(output):
    if output.exists():raise ValueError('retain old plan')
    prior=json.loads((REPO/PRIOR).read_text());rows=prior['training'];lengths=[r['event_count'] for r in rows];groups=[r['drummer'] for r in rows]
    if len(rows)!=58 or sum(lengths)!=32141 or set(groups)!={f'drummer{i}' for i in range(1,7)}:raise ValueError('fixed training inventory')
    weights={'raw':[Fraction(1)]*58,'equal_drummer':equal_group_weights(lengths,groups)}
    hashes={**prior['frozen_hashes'],**{f:sha(REPO/f) for f in FILES}}
    for f,h in hashes.items():
        if sha(REPO/f)!=h:raise ValueError('frozen dependency changed')
    plan={'created_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Four fixed conditions on same58 train/16 observed; no new material, fresh evaluation or weight tuning.',
          'frozen_hashes':hashes,'inventory_sha256':prior['inventory_sha256'],'training':rows,'diagnostics':prior['diagnostics'],'duplicate_aliases_excluded':prior['duplicate_aliases_excluded'],
          'conditions':{'weighting':['raw','equal_drummer'],'model':list(CONDITIONS)},
          'weights':{label:[{'id':r['id'],'drummer':r['drummer'],'weight':rational(w)} for r,w in zip(rows,ws)] for label,ws in weights.items()},
          'weight_diagnostics':{label:weight_diagnostics(lengths,ws,groups) for label,ws in weights.items()},
          'fixed_mass':32141,'formula':'Each raw event weight1; each equal-drummer event weight32141/(6*N_drummer), computed from train only. Every performance uses its drummer weight in full. Both total event masses exactly32141.',
          'prior_control':'Global exact, quotient and residual total counts remain32141 in both weightings; each existing prior total1 unchanged. No local context/k is modeled, avoiding local-count shrinkage-strength confounding. Weighted factorized update still differs from exact-IOI update as in original Cycle34.',
          'metrics':'All four conditions per-recording/per-drummer/pooled and macro-recording NLL on same16observed; raw32 work-condition sums must equal Cycle39. Report equal-minus-raw differences without selecting weights or winners.',
          'bounds':{'works':60,'training_events':60000,'events_per_work':4096,'cpu_seconds':60,'weight_fraction_numerator_denominator_max':1000000000},
          'journal':'Before-fit sources/gate evidence, per-constructor condition/weighting/sourceIDs saved before construction and completion/failure afterward.',
          'roles':'58train/16alreadyobserved/1076unscored unchanged;40evalreserve and duplicate alias remain excluded.',
          'limitations':['Equal event mass per drummer is not equal independent works, sessions, stylistic coverage or musical quality.',
                         'Drummer3 has fewer events, so its idiosyncratic patterns receive larger weights; weighted event ESS may decrease. No claim of reduced overfitting before evaluation.',
                         'Kish event ESS is only an algebraic descriptor because notes/IOIs within performances are strongly dependent.',
                         'All16diagnostics already observed; results cannot establish new-condition generalization.',
                         'No generation, voice/beat labels, audio, model selection or new-source admission.']}
    output.mkdir(parents=True);(output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');return plan


def construct_journaled(works,weights,condition,label,ids,output):
    path=output/'fit-journal.json';journal=json.loads(path.read_text()) if path.exists() else {'stages':[]}
    stage={'weighting':label,'model':condition,'train_ids':ids,'status':'construction_started'};journal['stages'].append(stage);path.write_text(json.dumps(journal,indent=2)+'\n')
    try:model=WeightedGrooveMarginal(works,weights,condition=condition)
    except Exception as exc:
        stage['status']='construction_failed';stage['exception_type']=type(exc).__name__;path.write_text(json.dumps(journal,indent=2)+'\n');raise
    stage['status']='construction_completed';stage['raw_events']=model.raw_events;stage['weighted_mass']=rational(model.n);path.write_text(json.dumps(journal,indent=2)+'\n');return model


def run(root,plan_path,clearance,output):
    if output.exists():raise ValueError('retain previous run')
    start=time.process_time();check_clearance(plan_path,json.loads(clearance.read_text()));p=json.loads(plan_path.read_text())
    for f,h in p['frozen_hashes'].items():
        if sha(REPO/f)!=h:raise ValueError('frozen dependency changed')
    if sha(root/'private-inventory.json')!=p['inventory_sha256']:raise ValueError('inventory changed')
    def budget():
        if time.process_time()-start>60:raise RuntimeError('CPU budget exceeded')
    works={};paths={}
    for r in p['training']+p['diagnostics']:
        budget();path=(root/r['relative_path']).resolve()
        if not path.is_relative_to(root.resolve()):raise ValueError('unsafe path')
        events=read_events(path,r['sha256']);prev=0;work=[]
        for tick,key in events:work.append((tick-prev,key));prev=tick
        if len(work)!=r['event_count']:raise ValueError('count mismatch')
        works[r['id']]=work;paths[r['id']]=path
    output.mkdir(parents=True);(output/'before-fit.json').write_text(json.dumps({'plan_sha256':sha(plan_path),'clearance_sha256':sha(clearance),'sources_verified':True},indent=2)+'\n')
    old=json.loads((REPO/OLD).read_text());results={};parities=0;ids=[r['id'] for r in p['training']]
    for label in ('raw','equal_drummer'):
        weights=[Fraction(r['weight']['numerator'],r['weight']['denominator']) for r in p['weights'][label]]
        if [r['id'] for r in p['weights'][label]]!=ids:raise ValueError('weight ID alignment')
        result={}
        for condition in CONDITIONS:
            budget();m=construct_journaled([works[i] for i in ids],weights,condition,label,ids,output);splits={}
            for split in ('validation','test'):
                per=[]
                for r in p['diagnostics']:
                    if r['proposed_split']!=split:continue
                    budget();v={'id':r['id'],'drummer':r['drummer'],**m.evaluate(works[r['id']])};per.append(v)
                    if label=='raw':
                        historic=next(x for x in old['results']['deduplicated58'][condition]['splits'][split]['per_recording'] if x['id']==r['id'])
                        if v['sum_nll_nats']!=historic['sum_nll_nats']:raise ValueError('raw historical parity')
                        parities+=1
                n=sum(x['events'] for x in per);splits[split]={'events':n,'recordings':len(per),'drummers':len({x['drummer'] for x in per}),'per_recording':per,'per_drummer':summarize_drummers(per),'pooled_mean_nll_nats':math.fsum(x['sum_nll_nats'] for x in per)/n,'macro_mean_nll_nats':math.fsum(x['mean_nll_nats'] for x in per)/len(per)}
            result[condition]={'weighted_mass':rational(m.n),'raw_events':m.raw_events,'works':m.work_count,'splits':splits}
        results[label]=result
    for r in p['training']+p['diagnostics']:
        if sha(paths[r['id']])!=r['sha256']:raise ValueError('source changed')
    report={'plan_sha256':sha(plan_path),'clearance_sha256':sha(clearance),'results':results,'raw_historical_exact_checks':parities,'all_sources_unchanged':True,'weight_diagnostics':p['weight_diagnostics'],'new_source_roles':False,'new_independent_validation':False,'cpu_seconds':time.process_time()-start,'limitations':p['limitations']}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','run']);p.add_argument('--output',type=Path,required=True);p.add_argument('--root',type=Path);p.add_argument('--plan',type=Path);p.add_argument('--clearance',type=Path);a=p.parse_args()
    if a.mode=='run' and any(x is None for x in (a.root,a.plan,a.clearance)):p.error('actual parent clearance/root/plan required')
    print(json.dumps(prepare(a.output) if a.mode=='prepare' else run(a.root,a.plan,a.clearance,a.output),indent=2))

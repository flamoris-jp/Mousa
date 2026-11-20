"""Cycle34: all fixed conditions on an already observed rhythm cohort."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
import math
from pathlib import Path
import time
from mousa.drum_ioi_multiscale import MultiscaleDrumIOI,CONDITIONS
from mousa.drum_ioi_baseline import validate_work
from compare_groove_ioi import check_clearance,summarize_drummers
from prepare_groove_split import read_events

REPO=Path(__file__).resolve().parents[1]
BASE='experiments/2026-11-12-groove-ioi-fit-final-plan.json'
OLD='experiments/2026-11-12-groove-ioi-results.json'
FILES=['src/mousa/drum_ioi_multiscale.py','tests/test_drum_ioi_multiscale.py','tools/compare_groove_multiscale.py','tests/test_groove_multiscale_driver.py',OLD,'datasets/research-groove-usage-cycle33-20261112.json']
def sha(p):return sha256(p.read_bytes()).hexdigest()


def prepare(output):
    if output.exists():raise ValueError('retain old output')
    base=json.loads((REPO/BASE).read_text())
    hashes={**base['frozen_hashes'],BASE:sha(REPO/BASE),**{f:sha(REPO/f) for f in FILES}}
    for f,h in hashes.items():
        if sha(REPO/f)!=h:raise ValueError('baseline hash changed')
    plan={'created_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Exploratory comparison on fixed previously observed Groove diagnostics; no fresh cohort or musical quality claims',
          'frozen_hashes':hashes,'sources':base['sources'],'inventory_sha256':base['inventory_sha256'],
          'conditions':list(CONDITIONS),'exact_backoff_k_values':[4,32,256],'selection':'All conditions reported; no winner-based selection or test-tuned k.',
          'support':{'min':0,'max':30720,'size':30721,'ppq':480,'unit':120,'q_range':[0,256],'q256_valid_residuals':[0]},
          'factorization':'dt=120*q+r exactly; q prior cap(q)/30721; residual empirical counts plus 1/120 per value, restricted and renormalized to legal r<cap(q). q count backoff k4 only in quotient_context condition; residual factor always global.',
          'prior_caveat':'Prior-only shape is uniform across ticks because (cap/30721)*(1/cap)=1/30721. After data, factorized pseudo-count updates are not identical to adding one joint uniform prior; factorization, count sharing and smoothing allocation change together.',
          'controls':'unigram and exact_k4 must reproduce Cycle33 per-work NLL exactly before new-condition reporting; no source/drop/rounding changes.',
          'metrics':'Every condition per-work, per-drummer and pooled/macro NLL for both already observed diagnostic splits; denominator events/performances/drummers explicit. Delta versus new-run exact control; no parameter ranking recommendation.',
          'resource_limits':{'cpu_seconds':60,'max_events':30000,'per_work_events':4096,'total_works':20},
          'randomness':'None; deterministic probabilities and counts. No generation or audio.',
          'limitations':base['limitations']+['Cycle33 validation/test have already been scored; this is not prospective independent validation.',
            'Quotient/residual represent coarse inter-onset interval and fine remainder, not beat position, meter, phase, or identified expressive microtiming.',
            'The last q bucket has one outcome, other buckets have120. No quantization, clipping or target rounding.',
            'All six conditions may worsen; retain negative results. Style, drummer, duration, instrument distribution and exact tick sparsity are confounded.']}
    output.mkdir(parents=True);(output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');return plan


def run(root,plan_path,clearance_path,output):
    if output.exists():raise ValueError('retain output')
    start=time.process_time();check_clearance(plan_path,json.loads(clearance_path.read_text()))
    plan=json.loads(plan_path.read_text())
    for f,h in plan['frozen_hashes'].items():
        if sha(REPO/f)!=h:raise ValueError('frozen file changed: '+f)
    if sha(root/'private-inventory.json')!=plan['inventory_sha256']:raise ValueError('inventory changed')
    def budget():
        if time.process_time()-start>60:raise RuntimeError('CPU budget exceeded')
    works={};paths={}
    for r in plan['sources']:
        budget();p=(root/r['relative_path']).resolve()
        if not p.is_relative_to(root.resolve()):raise ValueError('unsafe source path')
        events=read_events(p,r['sha256']);previous=0;work=[]
        for tick,key in events:work.append((tick-previous,key));previous=tick
        validate_work(work)
        if len(work)!=r['event_count']:raise ValueError('event count mismatch')
        works[r['id']]=work;paths[r['id']]=p
    if len(works)!=20 or sum(map(len,works.values()))>30000:raise ValueError('corpus bound')
    training=[works[r['id']] for r in plan['sources'] if r['proposed_split']=='train']
    if len(training)!=12:raise ValueError('fixed train count')
    old=json.loads((REPO/OLD).read_text());results={};parities=0
    for condition in CONDITIONS:
        budget();model=MultiscaleDrumIOI(training,condition=condition);splits={}
        for split in ('validation','test'):
            per=[]
            for r in plan['sources']:
                if r['proposed_split']!=split:continue
                budget();v={'id':r['id'],'drummer':r['drummer'],**model.evaluate(works[r['id']])};per.append(v)
                if condition in ('unigram','exact_k4'):
                    oldname='unigram' if condition=='unigram' else 'previous_instrument_count_shrinkage_k4'
                    oldrow=next(x for x in old['results'][oldname]['split_results'][split]['per_performance'] if x['id']==r['id'])
                    if v['sum_nll_nats']!=oldrow['sum_nll_nats']:raise ValueError('old control parity failed')
                    parities+=1
            events=sum(x['events'] for x in per)
            splits[split]={'events':events,'performances':len(per),'drummers':len({x['drummer'] for x in per}),
                           'per_performance':per,'per_drummer':summarize_drummers(per),
                           'pooled_mean_nll_nats':math.fsum(x['sum_nll_nats'] for x in per)/events,
                           'macro_mean_nll_nats':math.fsum(x['mean_nll_nats'] for x in per)/len(per)}
        results[condition]={'train_events':model.base.n,'context_transition_events':sum(model.base.context_totals.values()),'split_results':splits}
    for condition,result in results.items():
        for split,v in result['split_results'].items():
            v['pooled_delta_vs_unigram']=v['pooled_mean_nll_nats']-results['unigram']['split_results'][split]['pooled_mean_nll_nats']
    for r in plan['sources']:
        if sha(paths[r['id']])!=r['sha256']:raise ValueError('source changed')
    report={'plan_sha256':sha(plan_path),'clearance_sha256':sha(clearance_path),'results':results,
            'historical_exact_work_condition_parities':parities,'all_sources_unchanged':True,'already_observed_cohort':True,
            'new_independent_validation':False,'cpu_seconds':time.process_time()-start,'limitations':plan['limitations']}
    output.mkdir(parents=True);(output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','run']);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--root',type=Path);p.add_argument('--plan',type=Path);p.add_argument('--clearance',type=Path);a=p.parse_args()
    if a.mode=='run' and any(x is None for x in (a.root,a.plan,a.clearance)):p.error('run requires root, plan, actual parent clearance')
    print(json.dumps(prepare(a.output) if a.mode=='prepare' else run(a.root,a.plan,a.clearance,a.output),indent=2))

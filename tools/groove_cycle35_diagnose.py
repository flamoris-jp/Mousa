"""Posthoc frozen-cohort error accounting. No new estimator or parameter search."""
import argparse
from collections import Counter,defaultdict
from datetime import datetime,timezone
from hashlib import sha256
import json
import math
from pathlib import Path
import time
from mousa.drum_ioi_multiscale import MultiscaleDrumIOI,CONDITIONS
from prepare_groove_split import read_events

REPO=Path(__file__).resolve().parents[1]
PRIOR_PLAN='experiments/2026-11-12-groove-multiscale-plan.json'
PRIOR_RESULT='experiments/2026-11-12-groove-multiscale-results.json'
SELF='tools/groove_cycle35_diagnose.py'
TEST='tests/test_groove_cycle35.py'


def sha(path):return sha256(path.read_bytes()).hexdigest()


def exposure_bin(n):
    if type(n) is not int or n<0:raise ValueError('nonnegative integer count required')
    return '0' if n==0 else '1-9' if n<10 else '10-99' if n<100 else '100+'


def summarize(losses,controls):
    if len(losses)!=len(controls) or not losses:raise ValueError('paired nonempty losses')
    total=math.fsum(losses);base=math.fsum(controls)
    return {'events':len(losses),'sum_nll_nats':total,'mean_nll_nats':total/len(losses),
            'delta_vs_unigram_sum_nll':total-base,'delta_vs_unigram_mean_nll':(total-base)/len(losses)}


def prepare(output):
    if output.exists():raise ValueError('new plan destination required')
    prior=json.loads((REPO/PRIOR_PLAN).read_text())
    hashes={**prior['frozen_hashes'],PRIOR_PLAN:sha(REPO/PRIOR_PLAN),PRIOR_RESULT:sha(REPO/PRIOR_RESULT),SELF:sha(REPO/SELF),TEST:sha(REPO/TEST)}
    for f,h in hashes.items():
        if sha(REPO/f)!=h:raise ValueError('frozen dependency mismatch')
    plan={'created_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Posthoc accounting of six frozen Cycle34 conditions on same already observed eight recordings; no new condition fit or tuning.',
          'frozen_hashes':hashes,'sources':prior['sources'],'inventory_sha256':prior['inventory_sha256'],'conditions':list(CONDITIONS),
          'dimensions':['previous_instrument','context_train_exposure_bin','global_and_local_exact_IOI_seen','global_and_local_quotient_seen','global_residual_seen','current_instrument_train_seen','zero_IOI'],
          'exposure_bins':['0','1-9','10-99','100+'],
          'accounting':'Every dimension independently partitions all evaluation events within each drummer. Report counts, NLL sum/mean and delta versus unigram; dimensions overlap each other, so never add between dimensions.',
          'verification':'All48 recording-condition NLL sums must exactly equal stored Cycle34 values. Reconstructed counts use only same train12 with work resets. Repeat result except CPU identical.',
          'resources':{'cpu_seconds':60,'sources':20,'max_events':30000},
          'new_conditions':'None authorized or executed. Any proposed estimator must have a separate pre-run plan and parent review; same eight never become fresh.',
          'limitations':['No new corpus reading beyond fixed20; 1130 remain unused by this model experiment.',
                         'Previous-instrument order includes same-tick source ordering, not causal drum relations.',
                         'Error contributions reflect observed data and denominators, not causal attribution to drummer or style.',
                         'Six conditions differ in count backoff or quotient/residual factorization; exact tick outcomes remain unchanged.',
                         'Longer recordings dominate pooled means; four diagnostic recordings per split represent only two drummers.']}
    output.mkdir(parents=True);(output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');return plan


def run(root,plan_path,output):
    if output.exists():raise ValueError('retain prior diagnostic')
    start=time.process_time();plan=json.loads(plan_path.read_text())
    for f,h in plan['frozen_hashes'].items():
        if sha(REPO/f)!=h:raise ValueError('frozen dependency changed')
    if sha(root/'private-inventory.json')!=plan['inventory_sha256']:raise ValueError('inventory changed')
    def budget():
        if time.process_time()-start>60:raise RuntimeError('diagnostic CPU cap')
    works={};paths={}
    for r in plan['sources']:
        budget();p=(root/r['relative_path']).resolve()
        if not p.is_relative_to(root.resolve()):raise ValueError('unsafe path')
        events=read_events(p,r['sha256']);prev=0;work=[]
        for tick,key in events:work.append((tick-prev,key));prev=tick
        if len(work)!=r['event_count']:raise ValueError('count mismatch')
        works[r['id']]=work;paths[r['id']]=p
    if sum(map(len,works.values()))>30000:raise ValueError('event cap')
    training=[works[r['id']] for r in plan['sources'] if r['proposed_split']=='train']
    if len(training)!=12:raise ValueError('fixed train count')
    models={c:MultiscaleDrumIOI(training,condition=c) for c in CONDITIONS}
    m=models['quotient_context_k4_residual'];keys=Counter(k for w in training for _,k in w)
    stored=json.loads((REPO/PRIOR_RESULT).read_text());bucket=defaultdict(list);drummer_losses=defaultdict(list);per=[];parities=0
    for r in plan['sources']:
        if r['proposed_split']=='train':continue
        previous=None;losses={c:[] for c in CONDITIONS}
        for dt,key in works[r['id']]:
            budget();known=previous in m.base.contexts;q,res=divmod(dt,120)
            local=m.base.contexts.get(previous,{});localq=m.contexts.get(previous,{})
            labels={'previous_instrument':'initial' if previous is None else str(previous),
                    'context_train_exposure_bin':exposure_bin(m.base.context_totals.get(previous,0)),
                    'global_and_local_exact_IOI_seen':f'global={bool(m.base.counts[dt])};local={bool(local.get(dt,0)) if known else None}',
                    'global_and_local_quotient_seen':f'global={bool(m.quotients[q])};local={bool(localq.get(q,0)) if known else None}',
                    'global_residual_seen':str(bool(m.residuals[res])),
                    'current_instrument_train_seen':str(bool(keys[key])),'zero_IOI':str(dt==0)}
            event_losses={c:-math.log(float(model.probability(dt,previous_instrument=previous))) for c,model in models.items()}
            drummer_losses[(r['proposed_split'],r['drummer'])].append(event_losses)
            for dim,label in labels.items():bucket[(r['proposed_split'],r['drummer'],dim,label)].append(event_losses)
            for c,value in event_losses.items():losses[c].append(value)
            previous=key
        condition_reports={}
        for c in CONDITIONS:
            original=next(x for x in stored['results'][c]['split_results'][r['proposed_split']]['per_performance'] if x['id']==r['id'])
            assert math.fsum(losses[c])==original['sum_nll_nats'];parities+=1
            condition_reports[c]=summarize(losses[c],losses['unigram'])
        per.append({'id':r['id'],'drummer':r['drummer'],'split':r['proposed_split'],'conditions':condition_reports})
    def all_conditions(rows):return {c:summarize([x[c] for x in rows],[x['unigram'] for x in rows]) for c in CONDITIONS}
    summaries=[]
    for (split,drummer,dim,label),rows in sorted(bucket.items()):
        denominator=len(drummer_losses[(split,drummer)])
        summaries.append({'split':split,'drummer':drummer,'dimension':dim,'category':label,'events':len(rows),'drummer_event_denominator':denominator,'event_fraction':len(rows)/denominator,'conditions':all_conditions(rows)})
    for group,rows in drummer_losses.items():
        for dim in plan['dimensions']:
            assert sum(x['events'] for x in summaries if (x['split'],x['drummer'])==group and x['dimension']==dim)==len(rows)
    for r in plan['sources']:
        assert sha(paths[r['id']])==r['sha256']
    report={'plan_sha256':sha(plan_path),'prior_results_sha256':sha(REPO/PRIOR_RESULT),'new_conditions_fit':False,
            'fixed_count_reconstruction_only':True,'exact_historical_NLL_checks':parities,'source_bytes_unchanged':True,
            'train_events':m.base.n,'training_instrument_event_counts':dict(sorted(keys.items())),
            'training_previous_instrument_transition_counts':dict(sorted(m.base.context_totals.items())),
            'per_recording':per,'per_drummer':[{'split':s,'drummer':d,'recordings':sum(x['drummer']==d for x in per),'events':len(rows),'conditions':all_conditions(rows)} for (s,d),rows in sorted(drummer_losses.items())],
            'partitioned_contributions':summaries,'dimensions_partition_events_independently':True,
            'cpu_seconds':time.process_time()-start,'limitations':plan['limitations']}
    output.mkdir(parents=True);(output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','run']);p.add_argument('--output',type=Path,required=True);p.add_argument('--root',type=Path);p.add_argument('--plan',type=Path);a=p.parse_args()
    if a.mode=='run' and (a.root is None or a.plan is None):p.error('run requires root and plan')
    print(json.dumps(prepare(a.output) if a.mode=='prepare' else run(a.root,a.plan,a.output),indent=2))

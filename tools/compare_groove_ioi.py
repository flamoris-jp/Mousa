"""Frozen, parent-gated exact-tick drum prediction experiment. No generation."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from pathlib import Path
import time
from mousa.drum_ioi_baseline import DrumIOIModel, validate_work
from prepare_groove_split import read_events

REPO=Path(__file__).resolve().parents[1]
REPORT='experiments/2026-11-12-groove-split-preparation.json'
RIGHTS='datasets/research-groove-rights-cycle32-20261112.json'
FILES=[REPORT,RIGHTS,'tools/prepare_groove_split.py','tests/test_groove_split.py',
       'experiments/2026-11-12-groove-split-baseline-final-plan.json',
       'experiments/2026-11-12-groove-split-pattern-candidates.json',
       'src/mousa/drum_ioi_baseline.py','tools/compare_groove_ioi.py','tests/test_drum_ioi_baseline.py',
       'tests/test_groove_ioi_driver.py']


def sha(path):return sha256(path.read_bytes()).hexdigest()


def check_clearance(plan_path,clearance):
    if clearance.get('approved') is not True or clearance.get('plan_sha256')!=sha(plan_path):
        raise ValueError('missing parent clearance for exact plan')


def prepare(root,output):
    if output.exists():raise ValueError('new output required')
    prep=json.loads((REPO/REPORT).read_text())
    inv_path=root/'private-inventory.json';inv=json.loads(inv_path.read_text())
    if sha(inv_path)!=prep['inventory_sha256'] or prep['status']!='prepared_pending_parent_review':
        raise ValueError('preparation/inventory mismatch')
    selected=prep['candidates']
    if len(selected)!=20 or any(x['status']!='eligible_pending_parent_review' for x in selected):
        raise ValueError('candidate review unresolved')
    by_id={r['id']:r for r in inv['records']}
    sources=[]
    for x in selected:
        r=by_id[x['id']]
        if r['sha256']!=x['sha256']:raise ValueError('candidate source mismatch')
        sources.append({**x,'relative_path':r['relative_path']})
    plan={'created_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Groove rhythm-only predictive pilot; no fit until actual parent clearance',
          'frozen_hashes':{f:sha(REPO/f) for f in FILES},'inventory_sha256':sha(inv_path),'sources':sources,
          'training_split':'train','diagnostic_splits':['validation','test'],
          'source_count':20,'train_performances':12,'validation_performances':4,'test_performances':4,
          'target':'Ordered positive-velocity channel9 note-on IOI in original PPQ480 ticks. First IOI from tick0; simultaneous events retain source order.',
          'support':{'min_ioi':0,'max_ioi':30720,'size':30721,'uniform_prior_total_mass':1},
          'conditions':['unigram','previous_instrument_count_shrinkage_k4'],
          'formula':'Control: (global_count(dt)+1/30721)/(N+1). Seen context: (local_count(dt)+4*global_count(dt)/N+1/30721)/(local_N+4+1). Unseen/initial context: control.',
          'shrinkage_interpretation':'Empirical counts plus k4 global-empirical pseudo-counts then uniform prior1; not fixed mixture of smoothed predictive distributions.',
          'evaluation':'Per-performance NLL nats, pooled event-weighted and macro performance means for each split and each drummer, with explicit performance/event/drummer denominators; paired per-performance context-minus-control differences. Four held-out recordings per split are two drummers, not four independent performers. Support must be complete, no dropping or quantization.',
          'resource_limits':{'cpu_seconds':60,'maximum_events':30000,'max_events_per_performance':4096,'work_count':20},
          'reproducibility':'Deterministic counts/Fraction probabilities; no random draws or generated outputs.',
          'limitations':['Original release splits are historical only. Performer groups separate but residual common-pattern overlap is not ruled out.',
                         'Metadata and screening already observed; no model scores observed before this plan. Tiny pilot and unequal performance lengths/styles preclude broad generalization claims.',
                         'Previous-instrument context depends on source ordering for simultaneous hits; not causal groove learning.',
                         'Note-on/off pairing, gates, velocity/controller semantics are not modeled or verified by this prediction task.',
                         'Drum keys are instrument labels, not melodic pitches. No generation or musical attractiveness evaluation.',
                         'Rights snapshot remains historical prospective reserve; actual parent clearance authorizes this scoped fit, not arbitrary schema flags or public release.']}
    output.mkdir(parents=True);(output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    return plan


def summarize_drummers(per):
    result=[]
    for drummer in sorted({x['drummer'] for x in per}):
        rows=[x for x in per if x['drummer']==drummer]
        events=sum(x['events'] for x in rows)
        result.append({'drummer':drummer,'performances':len(rows),'events':events,
                       'pooled_mean_nll_nats':math.fsum(x['sum_nll_nats'] for x in rows)/events,
                       'macro_mean_nll_nats':math.fsum(x['mean_nll_nats'] for x in rows)/len(rows)})
    return result


def run(root,plan_path,clearance_path,output):
    start=time.process_time()
    if output.exists():raise ValueError('new output required')
    check_clearance(plan_path,json.loads(clearance_path.read_text()))
    plan=json.loads(plan_path.read_text())
    for f,h in plan['frozen_hashes'].items():
        if sha(REPO/f)!=h:raise ValueError('frozen hash mismatch: '+f)
    if sha(root/'private-inventory.json')!=plan['inventory_sha256']:raise ValueError('inventory changed')
    works={};paths={}
    def budget():
        if time.process_time()-start>plan['resource_limits']['cpu_seconds']:raise RuntimeError('CPU budget exceeded')
    for row in plan['sources']:
        budget();p=(root/row['relative_path']).resolve()
        if not p.is_relative_to(root.resolve()):raise ValueError('unsafe path')
        events=read_events(p,row['sha256']);previous=0;work=[]
        for tick,key in events:work.append((tick-previous,key));previous=tick
        validate_work(work)
        if len(work)!=row['event_count']:raise ValueError('count mismatch')
        works[row['id']]=work;paths[row['id']]=p
    training=[works[r['id']] for r in plan['sources'] if r['proposed_split']=='train']
    if len(training)!=12 or sum(map(len,works.values()))>30000:raise ValueError('training/total bound')
    results={}
    for condition,context in [('unigram',False),('previous_instrument_count_shrinkage_k4',True)]:
        budget();model=DrumIOIModel(training,context=context);splits={}
        for split in ('validation','test'):
            per=[]
            for r in plan['sources']:
                if r['proposed_split']!=split:continue
                budget();per.append({'id':r['id'],'drummer':r['drummer'],**model.evaluate(works[r['id']])})
            events=sum(x['events'] for x in per)
            splits[split]={'performances':len(per),'events':events,'per_performance':per,
                           'pooled_mean_nll_nats':math.fsum(x['sum_nll_nats'] for x in per)/events,
                           'macro_mean_nll_nats':math.fsum(x['mean_nll_nats'] for x in per)/len(per),
                           'drummer_count':len({x['drummer'] for x in per}), 'per_drummer':summarize_drummers(per)}
        results[condition]={'train_events':model.n,'train_performances':model.work_count,
                            'context_transition_events':sum(model.context_totals.values()),'split_results':splits}
    paired={s:[{'id':a['id'],'context_minus_control_mean_nll':b['mean_nll_nats']-a['mean_nll_nats']}
               for a,b in zip(results['unigram']['split_results'][s]['per_performance'],results['previous_instrument_count_shrinkage_k4']['split_results'][s]['per_performance'])]
            for s in ('validation','test')}
    for r in plan['sources']:
        if sha(paths[r['id']])!=r['sha256']:raise ValueError('source changed during run')
    report={'plan_sha256':sha(plan_path),'clearance_sha256':sha(clearance_path),'fit_performed':True,
            'train_ids':[r['id'] for r in plan['sources'] if r['proposed_split']=='train'],
            'diagnostics_now_predictively_observed':True,'all_source_hashes_unchanged':True,
            'results':results,'paired_performance_differences':paired,'cpu_seconds':time.process_time()-start,
            'limitations':plan['limitations']}
    output.mkdir(parents=True);(output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','run']);p.add_argument('--root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--plan',type=Path);p.add_argument('--clearance',type=Path)
    a=p.parse_args()
    if a.mode=='run' and (a.plan is None or a.clearance is None):p.error('run requires plan and actual parent clearance')
    print(json.dumps(prepare(a.root,a.output) if a.mode=='prepare' else run(a.root,a.plan,a.clearance,a.output),indent=2))

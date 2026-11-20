"""Prospective heldout-performer recording probe; no new model selection.

A fresh recording is not a fresh performer. Old observed records are excluded
by both identity and bytes. Freeze the plan before screening or prediction.
"""
import argparse
from datetime import datetime,timezone
from pathlib import Path
import json,math,time
from hashlib import sha256
from prepare_groove_split import read_events,features,compare,split_for
from mousa.drum_ioi_multiscale import CONDITIONS
from groove_cycle36_fit import construct_journaled
from compare_groove_ioi import summarize_drummers
ROOT=Path(__file__).resolve().parents[1]
PRIOR='experiments/2026-11-12-groove-cycle36-fit-final-plan.json'
USAGE='datasets/research-groove-usage-cycle36-20261112.json'
SELF='tools/groove_fresh_recording_probe.py'


def sha(p):return sha256(p.read_bytes()).hexdigest()


def select(rows,known):
    ids={r['id'] for r in known};hashes={r['sha256'] for r in known};selected=[]
    for drummer in ('drummer7','drummer8','drummer9','drummer10'):
        eligible=[r for r in rows if r['drummer']==drummer and not r['session'].endswith('/eval_session')
                  and r['id'] not in ids and r['sha256'] not in hashes and 1<=r['metrics']['note_on_positive']<=4096]
        selected.extend(sorted(eligible,key=lambda r:(r['sha256'],r['id']))[:2])
    return selected


def prepare(corpus,out):
    if out.exists():raise ValueError('new plan required')
    prior=json.loads((ROOT/PRIOR).read_text());inv=corpus/'private-inventory.json'
    if sha(inv)!=prior['inventory_sha256']:raise ValueError('inventory changed')
    rows=json.loads(inv.read_text())['records'];known=prior['training']+prior['diagnostics']+prior['duplicate_aliases_excluded']
    selected=select(rows,known)
    if len(selected)!=8 or sum(r['metrics']['note_on_positive'] for r in selected)>32768:raise ValueError('fixed eight whole-recording bound')
    sources=[dict(id=r['id'],sha256=r['sha256'],relative_path=r['relative_path'],drummer=r['drummer'],session=r['session'],proposed_split=split_for(r['drummer']),event_count=r['metrics']['note_on_positive']) for r in selected]
    hashes={**prior['frozen_hashes'],**{p:sha(ROOT/p) for p in [PRIOR,USAGE,SELF,'tests/test_groove_fresh_probe.py']}}
    for p,h in hashes.items():
        if sha(ROOT/p)!=h:raise ValueError('frozen dependency changed')
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),inventory_sha256=sha(inv),frozen_hashes=hashes,
              training=prior['training'],baseline_train_ids=prior['baseline_train_ids'],old_diagnostics=prior['diagnostics'],fresh_diagnostics=sources,
              conditions=list(CONDITIONS),selection='Two per drummer7–10, original source SHA then ID;exclude prior train/observed/alias IDs and bytes and all eval_session;1..4096events whole recording. No score-guided replacement.',
              screen='All8selected versus every other non-eval recording; existing exact-byte/exact onset-key/tempo-offset normalized/windowJaccard>=.80 strong rules. Any strong flag or unsupported IOI blocks entire cohort, no replacement. Weak windows reported.',
              experiment='Fixed baseline12 and deduplicated35 with all six unchanged estimators; same support/priors. No new model winner selection. Record all per-recording/drummer/pooled/macro scores.',
              bounds=dict(cpu_seconds=60,screen_sources=1500,screen_events=500000,screen_comparisons=15000,train_events=30000,diagnostic_events=32768),
              roles='These8 are technically inventoried but never predictively scored/fitted. After authorized scoring mark observed/untrained, never fresh again. Other1107 role history preserved; unchanged35train and40evalreserve.',
              limits=['New recordings from previously observed heldout performers, NOT new independent performers.','Selection is by predetermined hash order, not representative genre sampling.','Previously developed models have seen other recordings from these performers only as diagnostics, never training.','Screen cannot prove all musical independence; no human quality or causal genre claim.'])
    out.mkdir();(out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');return plan


def verify(corpus,planpath):
    p=json.loads(planpath.read_text())
    for name,h in p['frozen_hashes'].items():
        if sha(ROOT/name)!=h:raise ValueError('frozen file changed')
    if sha(corpus/'private-inventory.json')!=p['inventory_sha256']:raise ValueError('inventory changed')
    return p


def screen(corpus,planpath,out):
    if out.exists():raise ValueError('new screen required')
    p=verify(corpus,planpath);start=time.process_time()
    def budget():
        if time.process_time()-start>60:raise RuntimeError('screen CPU limit')
    rows=json.loads((corpus/'private-inventory.json').read_text())['records'];fs={};total=0
    if len(rows)>1500:raise ValueError('source cap')
    for r in rows:
        budget();path=(corpus/r['relative_path']).resolve()
        if not path.is_relative_to(corpus.resolve()):raise ValueError('path escape')
        ev=read_events(path,r['sha256']);total+=len(ev)
        if total>500000 or len(ev)!=r['metrics']['note_on_positive']:raise ValueError('event cap/count')
        fs[r['id']]=features(ev)
    hits=[];strong=[];pairs=0
    for a in p['fresh_diagnostics']:
        if fs[a['id']]['unsupported_iois']:strong.append(dict(a=a['id'],reason='unsupported IOI'))
        for b in rows:
            if b['id']==a['id'] or b['session'].endswith('/eval_session'):continue
            budget();pairs+=1
            if pairs>15000:raise ValueError('comparison cap')
            x=compare(fs[a['id']],fs[b['id']]);same=a['sha256']==b['sha256']
            if x['shared_unique_windows'] or x['strong_unresolved'] or same:hits.append(dict(a=a['id'],b=b['id'],exact_bytes=same,**x))
            if x['strong_unresolved'] or same:strong.append(dict(a=a['id'],b=b['id'],exact_bytes=same,**x))
    r=dict(plan_sha256=sha(planpath),blocked=bool(strong),strong=strong,hits=hits,comparisons=pairs,source_hashes_verified=True,cpu_seconds=time.process_time()-start,prediction_performed=False)
    out.mkdir();(out/'screen.json').write_text(json.dumps(r,indent=2)+'\n');return r


def run(corpus,planpath,screenpath,clearance,out):
    if out.exists():raise ValueError('new run required')
    p=verify(corpus,planpath);s=json.loads(screenpath.read_text());c=json.loads(clearance.read_text())
    if s['blocked'] or s['plan_sha256']!=sha(planpath):raise ValueError('screen blocked/unbound')
    if c.get('approved') is not True or c.get('plan_sha256')!=sha(planpath) or c.get('screen_sha256')!=sha(screenpath):raise ValueError('bound actual approval required')
    start=time.process_time()
    def budget():
        if time.process_time()-start>60:raise RuntimeError('run CPU limit')
    works={};paths={}
    for r in p['training']+p['fresh_diagnostics']:
        budget();path=(corpus/r['relative_path']).resolve()
        if not path.is_relative_to(corpus.resolve()):raise ValueError('path escape')
        ev=read_events(path,r['sha256']);previous=0;seq=[]
        for tick,key in ev:seq.append((tick-previous,key));previous=tick
        if len(seq)!=r['event_count']:raise ValueError('count changed')
        works[r['id']]=seq;paths[r['id']]=path
    out.mkdir();(out/'before-fit.json').write_text(json.dumps(dict(plan_sha256=sha(planpath),screen_sha256=sha(screenpath),clearance_sha256=sha(clearance)))+'\n')
    results={};prediction_stages=[]
    for label,ids in [('baseline12',p['baseline_train_ids']),('deduplicated35',[r['id'] for r in p['training']])]:
        results[label]={}
        for condition in CONDITIONS:
            budget();model=construct_journaled([works[i] for i in ids],condition,ids,label,out);scores=[]
            for r in p['fresh_diagnostics']:
                budget();stage=dict(condition=condition,training_group=label,source_id=r['id'],status='prediction_started');prediction_stages.append(stage)
                (out/'prediction-progress.json').write_text(json.dumps(dict(stages=prediction_stages))+'\n')
                score=dict(id=r['id'],drummer=r['drummer'],split=r['proposed_split'],**model.evaluate(works[r['id']]))
                scores.append(score);stage['status']='prediction_completed'
                (out/'prediction-progress.json').write_text(json.dumps(dict(stages=prediction_stages))+'\n')
            splits={}
            for split in ('validation','test'):
                rows=[r for r in scores if r['split']==split];n=sum(r['events'] for r in rows)
                splits[split]=dict(events=n,recordings=len(rows),drummers=2,per_recording=rows,per_drummer=summarize_drummers(rows),pooled_nll=math.fsum(r['sum_nll_nats'] for r in rows)/n,macro_nll=math.fsum(r['mean_nll_nats'] for r in rows)/len(rows))
            results[label][condition]=splits
    unchanged=all(sha(paths[r['id']])==r['sha256'] for r in p['training']+p['fresh_diagnostics'])
    report=dict(plan_sha256=sha(planpath),screen_sha256=sha(screenpath),results=results,originals_unchanged=unchanged,cpu_seconds=time.process_time()-start,new_training_sources=0,fresh_recordings_now_observed=8,limits=p['limits'])
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('mode',choices=['prepare','screen','run']);a.add_argument('--corpus',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    for k in ('plan','screen','clearance'):a.add_argument('--'+k,type=Path)
    x=a.parse_args()
    if x.mode=='prepare':r=prepare(x.corpus,x.output)
    elif x.mode=='screen':r=screen(x.corpus,x.plan,x.output)
    else:r=run(x.corpus,x.plan,x.screen,x.clearance,x.output)
    print(json.dumps(r,indent=2))

"""Explicit prepare/run interface for a precommitted corpus-scale count trial."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from math import log
from pathlib import Path
import platform
import os
import random
import time
from statistics import mean
from corpus_learning_trial import MusicFeatureCounts, read_projection, sha

SUPPORTS={'pitch_interval':49,'rhythm_ioi':25}
SEEDS=[53101,53102,53103]

def write(path,data):
    with path.open('x') as f:
        json.dump(data,f,indent=2,ensure_ascii=False);f.write('\n')

def prepare(split_path, plan_path):
    # Freeze before opening MIDI/features or observing any predictive outcomes.
    root=Path(__file__).parent
    plan={'schema':'mousa-corpus-learning-v1','created_at':datetime.now(timezone.utc).isoformat(),
      'split_sha256':sha(split_path),'scripts':{p.name:sha(p) for p in [root/'corpus_learning_trial.py',Path(__file__)]},
      'supports':SUPPORTS,'seeds':SEEDS,'max_onsets_per_family':2048,
      'models':['uniform','unigram','bigram','trigram','shuffled_trigram'],
      'conditions':['full_train','nested18_each_seed','full_equal_event_budget_each_seed'],
      'unigram_prior_total_mass':1,'context_backoff_mass':4,'cpu_limit_seconds':180,
      'projection':'Highest non-drum pitch at each exact onset across tracks; not an annotated melody; ignores duration/velocity/tempo/instrumentation/lower simultaneous notes.',
      'pitch_interval':'Semitone differences clipped[-24,24],shift24. Fixed49support.',
      'rhythm_ioi':'Positive onset differences in quarter-note beats; round(2log2(IOI)) clipped[-12,12],shift12. Fixed25support.',
      'targets':'Teacher forcing, same indices>=2 for every model; no cross-family transitions.',
      'subsets':'Primary18 exactly from split manifest flags, seed0 label; secondary three deterministic shuffled family orders first18TRAINfamilies. Not historically observed18works.',
      'equal_budget':'Full TRAIN per-family deterministic prefixes allocated round-robin up to each nested18 event total; preserves boundaries, but shorter-prefix bias remains.',
      'metrics':'Per-family natural-log NLL/accuracy; family macro primary, pooled secondary. No tuning/selection on validation or test.',
      'failure_policy':'Hash/role mismatch abort. Projection failures retained as explicit exclusions; no replacements. Fewer18usabletrain abort.',
      'scope':'New prospective prediction diagnostic, not artistic quality, causal proof that more works always helps, originality certification, Maidionis-trained model or Cantabile integration.',
      'generation':False,'checkpoint':'Private count-table JSON with source attribution retained; not published weights.'}
    write(plan_path,plan);return plan

def allocate_prefixes(sequences,budget):
    lengths=[0]*len(sequences)
    while budget:
        changed=False
        for i,s in enumerate(sequences):
            if lengths[i]<len(s):lengths[i]+=1;budget-=1;changed=True
            if not budget:break
        if not changed:break
    return [s[:n] for s,n in zip(sequences,lengths)]

def aggregate(rows):
    valid=[r for r in rows if r['n']]
    n=sum(r['n'] for r in valid)
    return {'families':len(valid),'events':n,'family_macro_nll':mean(r['nll'] for r in valid) if valid else None,
      'pooled_nll':sum(r['nll_sum'] for r in valid)/n if n else None,
      'family_macro_accuracy':mean(r['accuracy'] for r in valid) if valid else None,
      'pooled_accuracy':sum(r['correct'] for r in valid)/n if n else None}

# Manifest adapter is intentionally strict and populated after split schema review.
def records_from_split(split):
    return [dict(r, family=r['family_id'],local_path=r['source_path']) for r in split['members']]

def run(split_path,plan_path,out):
    plan=json.loads(plan_path.read_text());split=json.loads(split_path.read_text())
    if plan['supports']!=SUPPORTS or plan['seeds']!=SEEDS or plan['max_onsets_per_family']!=2048 or plan['cpu_limit_seconds']!=180 or plan['models']!=['uniform','unigram','bigram','trigram','shuffled_trigram'] or plan['unigram_prior_total_mass']!=1 or plan['context_backoff_mass']!=4:raise ValueError('protocol parameters changed')
    if sha(split_path)!=plan['split_sha256']:raise ValueError('split changed')
    for name,h in plan['scripts'].items():
        if sha(Path(__file__).parent/name)!=h:raise ValueError('frozen code changed')
    out.mkdir(exist_ok=False);start=time.process_time();rows=[];failures=[];sequences={};records=records_from_split(split)
    if len({r['family'] for r in records})!=len(records):raise ValueError('duplicate family')
    for key,h in split['input_sha256'].items():
        if sha(Path(split['input_paths'][key]))!=h:raise ValueError('input evidence changed')
    if any(r['previously_seen_source_ids'] and r['split']!='train' for r in records):raise ValueError('prior observation leaked')
    if any(r['corpus'] not in ['pd','by'] for r in records):raise ValueError('unapproved license family')
    def journal(event,**kw):
        with (out/'journal.jsonl').open('a') as handle:
            handle.write(json.dumps(dict(event=event,**kw))+'\n');handle.flush();os.fsync(handle.fileno())
    journal('run_started',plan_sha256=sha(plan_path),split_sha256=sha(split_path))
    for record in records:
        family=record['family'];role=record['split']
        if role not in ['train','validation','test'] or family in sequences:raise ValueError('split invariant')
        # A corrupt hash is never downgraded to an ordinary projection exclusion.
        path=Path(record['local_path'])
        if sha(path)!=record['sha256']:raise ValueError('source hash mismatch')
        try:
            features,total,_=read_projection(path,record['sha256'],plan['max_onsets_per_family'])
            if min(map(len,features.values()))<3:raise ValueError('too few projected events')
            sequences[family]={'role':role,'features':features,'total_onsets':total}
        except (ValueError,EOFError) as e:failures.append({'family':family,'error':str(e)})
    train=sorted(k for k,v in sequences.items() if v['role']=='train')
    if len(train)<18:raise ValueError('fewer18trainingfamilies')
    subsets={'0':[r['family'] for r in records if r['nested_18_family_training_subset'] and r['family'] in train]}
    if len(subsets['0'])!=18:raise ValueError('primary18 projection failure; abort instead of replace')
    for seed in SEEDS:
        ids=list(train);random.Random(seed).shuffle(ids);subsets[str(seed)]=ids[:18]
    write(out/'fitted-subsets.json',subsets)
    conditions=[('full_train',None,train)]+[(kind,seed,subsets[str(seed)] if kind=='nested18' else train) for seed in [0]+SEEDS for kind in ['nested18','full_equal_budget']]
    model_sizes=[];checkpoint={}
    for feature,support in SUPPORTS.items():
        for label,seed,ids in conditions:
            training=[sequences[k]['features'][feature] for k in ids]
            if label=='full_equal_budget':
                budget=sum(len(sequences[k]['features'][feature]) for k in subsets[str(seed)])
                training=allocate_prefixes(training,budget)
            for model_name in plan['models']:
                if time.process_time()-start>plan['cpu_limit_seconds']:raise RuntimeError('CPU ceiling reached')
                order={'uniform':0,'unigram':0,'bigram':1,'trigram':2,'shuffled_trigram':2}[model_name]
                journal('fit_started',feature=feature,condition=label,seed=seed,model=model_name,training_family_ids=ids)
                model=MusicFeatureCounts([] if model_name=='uniform' else training,support,order,
                                         (seed or SEEDS[0]) if model_name=='shuffled_trigram' else None)
                journal('fit_complete',feature=feature,condition=label,seed=seed,model=model_name)
                model_sizes.append({'feature':feature,'condition':label,'seed':seed,'model':model_name,
                   'families_with_events':sum(bool(s) for s in training),'available_training_events':sum(map(len,training)),
                   'fitted_events':0 if model_name=='uniform' else sum(map(len,training)),
                   'effective_ngram_transitions':{str(n):0 if model_name=='uniform' else sum(max(0,len(s)-n) for s in training) for n in range(1,order+1)},
                   'contexts':sum(map(len,model.local))})
                if label=='full_train' and model_name=='trigram':
                    checkpoint[feature]={'support':support,'order':2,'marginal':dict(model.marginal),
                      'contexts':[[{'context':list(k),'counts':dict(v)} for k,v in level.items()] for level in model.local]}
                for family,seq in sequences.items():
                    if seq['role']=='train':continue
                    journal('score_started',family=family,split=seq['role'],feature=feature,condition=label,seed=seed,model=model_name)
                    r=model.score(seq['features'][feature]);rows.append(dict(feature=feature,condition=label,seed=seed,model=model_name,split=seq['role'],family=family,**r))
                    journal('score_complete',family=family,split=seq['role'],feature=feature,condition=label,seed=seed,model=model_name)
    summaries=[]
    for feature in SUPPORTS:
        for label,seed,_ in conditions:
            for model_name in plan['models']:
                for role in ['validation','test']:
                    selected=[r for r in rows if (r['feature'],r['condition'],r['seed'],r['model'],r['split'])==(feature,label,seed,model_name,role)]
                    summaries.append(dict(feature=feature,condition=label,seed=seed,model=model_name,split=role,**aggregate(selected)))
    result={'schema':plan['schema'],'plan_sha256':sha(plan_path),'split_sha256':sha(split_path),'rows':rows,'summary':summaries,
      'exclusions':failures,'usable_families_by_split':dict(Counter(v['role'] for v in sequences.values())),
      'model_sizes':model_sizes,'cpu_seconds':time.process_time()-start,'python':platform.python_version(),
      'projection_counts':{k:dict(role=v['role'],total_onsets=v['total_onsets'],used_features=len(v['features']['pitch_interval'])) for k,v in sequences.items()},
      'source_hashes_rechecked':all(sha(Path(r['local_path']))==r['sha256'] for r in records),
      'generation_performed':False,'historical_cycle52_comparison':'Different representation, old observed18 and retrospectivefolds; no numerical improvement ratio across protocols.'}
    write(out/'results.json',result);write(out/'private-full-count-model.json',{'schema':'mousa-private-music-feature-counts-v1','plan_sha256':sha(plan_path),'split_sha256':sha(split_path),'attribution_sidecar':'split-protocol.json members[].attribution with exactlicense/source links','modification_notice':plan['projection'],'models':checkpoint})
    write(out/'actual-use-ledger.json',{'plan_sha256':sha(plan_path),'split_sha256':sha(split_path),'observed_at':datetime.now(timezone.utc).isoformat(),'members':[dict(family=r['family'],source_ids=r['source_ids'],role=('fitted_train' if r['split']=='train' else 'observed_untrained_'+r['split']) if r['family'] in sequences else 'projection_failed_not_scored',selected_sha256=r['sha256']) for r in records],'future_fresh_test_reuse_forbidden':True})
    return result

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('mode',choices=['prepare','run']);a.add_argument('--split',type=Path,required=True);a.add_argument('--plan',type=Path,required=True);a.add_argument('--out',type=Path);args=a.parse_args()
    if args.mode=='prepare':print(json.dumps(prepare(args.split,args.plan),indent=2))
    else:
        try:
            r=run(args.split,args.plan,args.out);print(json.dumps({k:r[k] for k in ['usable_families_by_split','cpu_seconds','exclusions']},indent=2))
        except Exception as e:
            if args.out and args.out.is_dir():
                with (args.out/'failure.jsonl').open('a') as f:f.write(json.dumps({'failed_at':datetime.now(timezone.utc).isoformat(),'error':str(e),'freshness':'All score_started families in journal are observed; do not reset freshness.'})+'\n')
            raise

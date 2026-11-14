"""Freeze then run an explicitly retrospective learning diagnostic."""
import argparse, hashlib, json, os, platform, time
from pathlib import Path
from datetime import datetime, timezone
from itertools import combinations
from math import log
from statistics import mean
from compare_weighted_maple_cycle45 import read, ROOT
from screen_initial_rest_intake import comparison
from learning_cycle52 import components, shuffled_model, score, summary
from mousa.gate_context_group_model import GateContextGroupModel
SEEDS=list(range(52000,52020))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):
    with p.open('x') as f: json.dump(v,f,indent=2);f.write('\n')
def prepare(path):
    train,_,seq,sources,maps,_=read();start=time.process_time();screen=[]
    for a,b in combinations(train,2):
        if time.process_time()-start>60:raise RuntimeError('screen budget exhausted')
        r=comparison(train[a],train[b])
        if r['global_similarity'] is None:raise ValueError('incomplete similarity')
        screen.append(dict(a=a,b=b,**r))
    links=[(r['a'],r['b']) for r in screen if r['exact8']>0 or r['global_similarity']>=.8]
    groups=components(list(train),maps[18],links)
    if len(groups)<2:raise ValueError('no disjoint folds')
    frozen={str(p.relative_to(ROOT)):sha(p) for folder,glob in [('src/mousa','*.py'),('tools','*.py'),('tests','*.py'),('datasets','*.json')] for p in sorted((ROOT/folder).glob(glob))}
    plan=dict(schema='mousa-learning-cycle52-v1',created_utc=datetime.now(timezone.utc).isoformat(),source_hashes={str(Path(k).relative_to(ROOT.parent)):v for k,v in sources.items()},frozen=frozen,screen=screen,folds=groups,ids=list(train),seeds=SEEDS,
      scope='Retrospective cross-validation on 18 historically trained/observed works, not a fresh prospective test. Each fold fits anew without its evaluation works or linked siblings. Prior research/model choice saw this corpus. No held-out/reserved work enters fit or score.',
      grouping='Transitive closure of fixed11 source/editor/contributor families plus every current exact8 interval motif or global interval edit similarity>=.8 pair. All153 pairs screened before any fit. This limited screen is not proof of independence or legal originality.',
      conditions=['uniform_no_data','global','previous_max_gate_binned','shuffled_context_20_seeds'],
      hypothesis='Does true previous-duration context transfer better than no-data, learned marginal and within-work shuffled-context controls?',
      shuffle='Permute previous-max-gate-bin labels over later transitions independently within each training work; preserve timing marginal and local context totals, break alignment. Each seed fitted independently, no best-seed selection.',
      metrics='Primary mean of fold work-macro later-delta NLL. Also per-work, work-macro over18, pooled over4172 later groups; first losses separate. Natural logs, lower better. Mean shuffled NLL, not likelihood of a mixture. Teacher-forced previous template only; no pitch/gate/joint quality or significance claim.',
      supports={'first':[0,65536],'later':[1,12288],'uniform_prior_total_mass':1,'local_backoff_mass':4},cpu_limit_seconds=120,seed_policy='All20 seeds fixed, retain failures; no tuning.',no_generation=True,no_new_admission=True,screen_cpu_seconds=time.process_time()-start)
    write(path,plan);return dict(folds=groups,screen_pairs=len(screen),plan_sha256=sha(path))
def run(planpath,out):
    plan=json.loads(planpath.read_text())
    if out.exists():raise ValueError('new output directory required')
    for rel,h in plan['frozen'].items():
        if sha(ROOT/rel)!=h:raise ValueError('code/evidence changed '+rel)
    for rel,h in plan['source_hashes'].items():
        if sha(ROOT.parent/rel)!=h:raise ValueError('source changed')
    train,_,seq,_,maps,_=read()
    links=[(r['a'],r['b']) for r in plan['screen'] if r['exact8']>0 or r['global_similarity']>=.8]
    if plan['ids']!=list(train) or plan['folds']!=components(list(train),maps[18],links) or plan['seeds']!=SEEDS:raise ValueError('plan mismatch')
    out.mkdir();start=time.process_time();rows=[]
    def journal(event,**kw):
        with (out/'journal.jsonl').open('a') as f:
            f.write(json.dumps(dict(event=event,**kw))+'\n');f.flush();os.fsync(f.fileno())
    for fi,held in enumerate(plan['folds']):
        ids=[k for k in train if k not in held];training=[seq[k] for k in ids]
        if set(ids)&set(held):raise AssertionError('split leakage')
        conditions=[('global',None),('previous_max_gate_binned',None)]+[('shuffled_context',s) for s in SEEDS]
        for label,seed in conditions:
            journal('fit_attempt',fold=fi,condition=label,seed=seed,train_ids=ids,evaluation_ids=held)
            if time.process_time()-start>plan['cpu_limit_seconds']:raise RuntimeError('CPU budget; partial journal retained')
            model=shuffled_model(training,seed) if seed is not None else GateContextGroupModel(training,arm=label)
            journal('fit_complete',fold=fi,condition=label,seed=seed)
            for k in held:
                journal('prediction_attempt',fold=fi,condition=label,seed=seed,work=k)
                r=score(model,seq[k]);rows.append(dict(fold=fi,work=k,condition=label,seed=seed,**r))
                journal('prediction_complete',fold=fi,condition=label,seed=seed,work=k)
        for k in held:
            n=len(seq[k])-1
            rows.append(dict(fold=fi,work=k,condition='uniform_no_data',seed=None,first_nll=log(65537),later_count=n,later_nll_sum=n*log(12288),later_mean_nll=log(12288)))
    aggregates={}
    for label in plan['conditions']:
        if label=='shuffled_context_20_seeds':
            reduced=[]
            for k in train:
                rr=[r for r in rows if r['work']==k and r['condition']=='shuffled_context']
                reduced.append(dict(work=k,fold=rr[0]['fold'],later_count=rr[0]['later_count'],later_nll_sum=mean(r['later_nll_sum'] for r in rr),later_mean_nll=mean(r['later_mean_nll'] for r in rr)))
        else:reduced=[r for r in rows if r['condition']==label]
        folds=[dict(fold=fi,**summary([r for r in reduced if r['fold']==fi])) for fi in range(len(plan['folds']))]
        aggregates[label]=dict(**summary(reduced),fold_macro=mean(r['work_macro'] for r in folds),folds=folds)
    unchanged=all(sha(ROOT.parent/rel)==h for rel,h in plan['source_hashes'].items())
    if not unchanged:raise ValueError('source mutated')
    result=dict(plan_sha256=sha(planpath),rows=rows,aggregates=aggregates,cpu_seconds=time.process_time()-start,python=platform.python_version(),sources_unchanged=unchanged,scope=plan['scope'],new_midi=0)
    write(out/'results.json',result);return aggregates
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','run']);p.add_argument('--plan',type=Path,required=True);p.add_argument('--out',type=Path);a=p.parse_args()
    print(json.dumps(prepare(a.plan) if a.mode=='prepare' else run(a.plan,a.out),indent=2))

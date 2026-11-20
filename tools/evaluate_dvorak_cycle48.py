"""Fixed six-arm timing diagnostic. prepare never fits or compares real music."""
import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from math import log, isfinite
from fractions import Fraction
from pathlib import Path
from time import process_time
from compare_weighted_maple_cycle45 import read, ROOT
from mousa.overlap_midi import read_midi
from mousa.initial_rest_group_model import observations, validate
from mousa.weighted_group_cycle45 import WeightedGroupModel, pool_weights
from screen_initial_rest_intake import comparison

SHARED = ROOT.parent
MASSES = (17, 3411, 3428)
CONDITIONS = [(f'{n}_{mode}', n, mode) for mode in ('raw','equal_work','equal_family') for n in (17,18)]
D_SOURCE = 'mousa-cycle47-dvorak/score.mid'
S_SOURCE = 'mousa-cycle46-rights/37.mid'
S_DERIVED = 'mousa-cycle47-satie/37-derived-redundant-offs.mid'
STATUS = 'datasets/research-dvorak1948-status-cycle47-20261112.json'
SCREEN = 'experiments/2026-11-12-dvorak1948-cycle47-screen.json'
SCREEN_PLAN = 'experiments/2026-11-12-dvorak1948-cycle47-screen-plan.json'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v): p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def journal(path,event,**fields):
    with path.open('a') as f:
        f.write(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(),event=event,**fields))+'\n')
        f.flush(); os.fsync(f.fileno())

def blocked(result):
    exact=result.get('exact8');score=result.get('global_similarity')
    if type(exact) is not int or exact<0:return True
    if type(score) not in (int,float) or not isfinite(score) or not 0<=score<=1:return True
    return exact>0 or score>=.8

def reference_map(sources):
    refs={str(Path(p).relative_to(SHARED)):h for p,h in sources.items()}
    extra=['mousa-cycle18-rights-20261112/1692/Duett-Telemann-1.mid',
           'mousa-cycle22-rights/sonatina-1-1.mid',
           'mousa-cycle25-rights/1741-LiederOhneWorte_-_Op30_No6.mid',
           'mousa-cycle42-rights/lully.mid','mousa-cycle46-rights/38.mid']
    for rel in extra:refs[rel]=sha(SHARED/rel)
    expected=json.loads((ROOT/SCREEN_PLAN).read_text())['reference_sha256']
    if len(refs)!=27 or sorted(refs.values())!=sorted(expected):raise ValueError('original reference map differs')
    return refs

def verify_config(cfg,train,maps):
    expected=next(((n,mode) for label,n,mode in CONDITIONS if label==cfg['label']),None)
    if expected is None:raise ValueError('unknown condition')
    n,mode=expected;ids=list(train)[:n]
    if cfg['train_ids']!=ids or cfg['families']!=[maps[n][k] for k in ids] or cfg['mode']!=mode or tuple(cfg['masses'])!=MASSES:
        raise ValueError('fixed condition mismatch')

def verify_model_mass(model):
    actual=[sum(model.first.values(),Fraction()),sum(model.later.values(),Fraction()),sum(model.template_counts.values(),Fraction()),sum(model.anchor_counts.values(),Fraction())]
    if actual!=[Fraction(v) for v in (*MASSES,MASSES[2])]:raise ValueError('fitted Counter mass mismatch')
    return [dict(numerator=v.numerator,denominator=v.denominator) for v in actual]

def supplemental_stop(plan,ph,status,start):
    return dict(plan_sha256=ph,status=status,cpu_seconds=process_time()-start,prediction_attempted=False,not_original_clearance=True,evaluation_fitted=False,
                results={cfg['label']:dict(status='blocked',reason=status) for cfg in plan['conditions']})

def check_support(seq):
    if not seq or type(seq[0][0]) is not int or not 0<=seq[0][0]<=65536:
        raise ValueError("first support")
    if any(type(d) is not int or not 1<=d<=12288 for d,_,_ in seq[1:]):
        raise ValueError("later support; no clipping/rescaling")

def inputs():
    train,old,seq,sources,maps,assignment=read()
    refs=reference_map(sources)
    # Original sources returned by read cover every training file plus four observed works.
    # Excluding the candidate from this superset is stronger than train-only exclusion;
    # do not join legacy display IDs, which differ between historic ledgers.
    if len(train)!=18 or sha(SHARED/D_SOURCE) in sources.values():raise ValueError('candidate/train identity leakage')
    status=json.loads((ROOT/STATUS).read_text())
    if status['fit'] or status['score'] or status['admitted'] or status['references']!=27 or status['flagged']:
        raise ValueError('reserve role changed')
    report=json.loads((ROOT/SCREEN).read_text())
    if report['plan_sha256']!=sha(ROOT/SCREEN_PLAN) or status['screen_report_sha256']!=sha(ROOT/SCREEN):
        raise ValueError('unbound original screen')
    if len(report['rows'])!=27 or any(blocked(r) for r in report['rows']):
        raise ValueError('original screen blocked/incomplete')
    m=read_midi(SHARED/D_SOURCE,1)
    if sha(SHARED/D_SOURCE)!=status['selected_member_sha256']: raise ValueError('candidate changed')
    s=observations(m.notes,m.total_ticks);validate(s,65536)
    check_support(s)
    for k in train:check_support(seq[k])
    if len(s)!=123 or len(m.notes)!=123: raise ValueError('selected representation changed')
    derived=read_midi(SHARED/S_DERIVED,1)
    review=json.loads((ROOT/'experiments/2026-11-12-satie37-cycle47-independent-review.json').read_text())
    if sha(SHARED/S_SOURCE)!=review['source_sha256'] or sha(SHARED/S_DERIVED)!=review['derived_sha256']:
        raise ValueError('Satie bytes changed')
    for rel in (D_SOURCE,S_SOURCE,S_DERIVED):sources[str(SHARED/rel)]=sha(SHARED/rel)
    return train,seq,maps,m,s,derived,sources,refs

def prepare(out):
    if out.exists(): raise ValueError('new plan directory required')
    train,seq,maps,m,s,derived,sources,refs=inputs()
    # Conservative entire implementation/evidence freeze; no fitting/scoring here.
    paths=set(ROOT.glob('src/mousa/*.py')) | set(ROOT.glob('tools/*.py')) | set(ROOT.glob('tests/*.py'))
    paths |= set(ROOT.glob('datasets/*.json')) | set(ROOT.glob('experiments/*.json'))
    frozen={str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)}
    configs=[]
    for label,n,mode in CONDITIONS:
        ids=list(train)[:n]
        families=[maps[n][k] for k in ids]
        lengths=([1]*n,[len(seq[k])-1 for k in ids],[len(seq[k]) for k in ids])
        totals=[]
        for ns,mass in zip(lengths,MASSES):
            ws=pool_weights(ns,families,mode,mass)
            total=sum((n*w for n,w in zip(ns,ws)),Fraction())
            if total!=mass:raise ValueError('exact pool mass mismatch')
            totals.append(dict(numerator=total.numerator,denominator=total.denominator))
        configs.append(dict(label=label,train_ids=ids,mode=mode,masses=list(MASSES),families=families,exact_pool_totals=totals))
    plan=dict(schema='mousa-cycle48-fixed-timing-v1',created_utc=datetime.now(timezone.utc).isoformat(),frozen_hashes=frozen,
        source_sha256={str(Path(p).relative_to(SHARED)):h for p,h in sources.items()},conditions=configs,
        original_reference_map=refs,original_comparisons=27,supplemental_comparisons=1,
        supplemental_policy='Dvorak versus Satie37 derivative only. exact8>0 OR global_similarity>=0.80 OR unavailable blocks all predictions. No match permits limited research timing evaluation, NOT 28-original clearance. Original Satie stays technical-blocked; derivative remains unadmitted/untrained. No inferred notation/audio equivalence.',
        role='One previously unscored Dvorak/Janda/Simrock Op75 first-piece violin cohort, representation inspected. All four pieces/12forms and related Op75a excluded from fit. First prediction attempt marks cohort observed even on failure; replay is not fresh.',
        metrics=dict(primary='later_nll_sum / 122',secondary=['first_nll','nll_per_group_delta'],groups=123,later_groups=122),
        support=dict(first=[0,65536],later=[1,12288],prior_mass=1,ppq=m.ppq),
        limits=['Timing only, not pitch/template prediction, phrase structure or attractiveness.','One work/cohort, no independent-sample or significance claim.','17 vs18 confounds added work content and size; family labels are linked series not proven independent groups.','4/4 candidate does not imply model meter conditioning.','Original URL bibliographic inconsistency retained; no invented corrected source.','No generation; A-D human ratings unanswered.'],
        cpu_seconds=60,budget='Cooperative checks before bounded calls; not hard preemption.',
        journal='Append fsync before/after each prediction; failure also observed. Entire run blocked if supplemental flags.',
        actual_fit=False,actual_prediction=False,actual_supplemental_comparison=False)
    out.mkdir();write(out/'plan.json',plan);return plan

def timing_metrics(model,seq):
    v=model.evaluate(seq)
    losses=[-log(model.probability(d,None if i==0 else 1)) for i,(d,_,_) in enumerate(seq)]
    if abs(sum(losses)/len(losses)-v['nll_per_group_delta'])>1e-12:raise ValueError('aggregate mismatch')
    return dict(**v,later_groups=len(seq)-1,later_mean_nll=v['later_nll_sum']/(len(seq)-1),independent_error=abs(sum(losses)/len(losses)-v['nll_per_group_delta']))

def run(planpath,clearance,out):
    if out.exists():raise ValueError('new output directory required')
    p=json.loads(planpath.read_text());c=json.loads(clearance.read_text());ph=sha(planpath)
    if c.get('approved') is not True or c.get('plan_sha256')!=ph:raise ValueError('bound parent review required')
    for rel,h in p['frozen_hashes'].items():
        if sha(ROOT/rel)!=h:raise ValueError('dependency changed: '+rel)
    for rel,h in p['source_sha256'].items():
        if sha(SHARED/rel)!=h:raise ValueError('source changed')
    train,seq,maps,m,target,derived,sources,refs=inputs()
    if refs!=p['original_reference_map']:raise ValueError('reference map changed')
    for rel,h in refs.items():
        if sha(SHARED/rel)!=h:raise ValueError('original reference changed')
    if [cfg['label'] for cfg in p['conditions']]!=[row[0] for row in CONDITIONS]:raise ValueError('condition sequence changed')
    for cfg in p['conditions']:verify_config(cfg,train,maps)
    if {str(Path(k).relative_to(SHARED)):v for k,v in sources.items()}!=p['source_sha256']:raise ValueError('source set changed')
    out.mkdir();jp=out/'journal.jsonl';start=process_time()
    journal(jp,'supplemental_comparison_attempt',plan_sha256=ph,original_comparisons=27,derived_comparisons=1)
    try: supplement=comparison(m,derived)
    except Exception as exc:
        journal(jp,'supplemental_comparison_failure',exception=type(exc).__name__)
        report=supplemental_stop(p,ph,'supplemental_failed',start);write(out/'report.json',report);return report
    journal(jp,'supplemental_comparison_complete',**supplement)
    write(out/'supplemental.json',dict(plan_sha256=ph,original_comparisons=27,derived_comparisons=1,not_original_clearance=True,**supplement))
    results={}
    if blocked(supplement):
        report=supplemental_stop(p,ph,'supplemental_blocked',start);write(out/'report.json',report);return report
    attempted=False
    for cfg in p['conditions']:
        label=cfg['label']
        if process_time()-start>=60:results[label]=dict(status='cpu_budget_skipped');continue
        journal(jp,'fit_attempt',condition=label,train_ids=cfg['train_ids'])
        try:
            model=WeightedGroupModel([seq[k] for k in cfg['train_ids']],cfg['families'],mode=cfg['mode'],masses=tuple(cfg['masses']))
            mass_check=verify_model_mass(model)
        except Exception as exc:
            journal(jp,'fit_failure',condition=label,exception=type(exc).__name__);results[label]=dict(status='fit_failed',exception=type(exc).__name__);continue
        journal(jp,'fit_complete',condition=label,exact_counter_masses=mass_check)
        if process_time()-start>=60:results[label]=dict(status='cpu_budget_skipped');continue
        journal(jp,'prediction_attempt',condition=label,cohort='dvorak-op75-b150-simrock-janda',irreversibly_observed=True);attempted=True
        try:
            result=timing_metrics(model,target);results[label]=dict(status='complete',**result)
            journal(jp,'prediction_complete',condition=label)
        except Exception as exc:
            journal(jp,'prediction_failure',condition=label,exception=type(exc).__name__)
            results[label]=dict(status='prediction_failed',exception=type(exc).__name__)
    report=dict(plan_sha256=ph,status='completed_with_explicit_condition_statuses',prediction_attempted=attempted,results=results,cpu_seconds=process_time()-start,not_original_clearance=True,evaluation_fitted=False,original_bytes_unchanged=all(sha(SHARED/k)==v for k,v in p['source_sha256'].items()))
    write(out/'report.json',report);return report

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('stage',choices=['prepare','run']);a.add_argument('--plan',type=Path,required=True);a.add_argument('--clearance',type=Path);a.add_argument('--output',type=Path)
    v=a.parse_args();result=prepare(v.plan) if v.stage=='prepare' else run(v.plan,v.clearance,v.output)
    print(json.dumps(result,indent=2))

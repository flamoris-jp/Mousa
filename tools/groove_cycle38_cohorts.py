"""Saved-score cohort accounting only; no source access or model construction."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
import math
from pathlib import Path
import time

REPO=Path(__file__).resolve().parents[1]
OLD_PLAN='experiments/2026-11-12-groove-cycle36-fit-final-plan.json'
NEW_PLAN='experiments/2026-11-12-groove-fresh-recording-plan.json'
OLD_RESULTS='experiments/2026-11-12-groove-cycle36-results.json'
NEW_RESULTS='experiments/2026-11-12-groove-fresh-recording-results.json'
FILES=[OLD_PLAN,NEW_PLAN,OLD_RESULTS,NEW_RESULTS,'tools/groove_cycle38_cohorts.py','tests/test_groove_cycle38.py','datasets/research-groove-fresh-observations-cycle37.json','datasets/research-groove-usage-cycle36-20261112.json','datasets/research-groove-rights-cycle32-20261112.json']

def sha(p):return sha256(p.read_bytes()).hexdigest()

def direction(x):
    if not math.isfinite(x):raise ValueError('finite score difference required')
    return 'numerical_tie' if abs(x)<=1e-12 else 'worse' if x>0 else 'better'


def summarize_pairs(baseline,expanded):
    left={x['id']:x for x in baseline};right={x['id']:x for x in expanded}
    if not left or len(left)!=len(baseline) or len(right)!=len(expanded) or left.keys()!=right.keys():raise ValueError('unique paired recording IDs required')
    paired=[]
    for key in sorted(left):
        a,b=left[key],right[key]
        if a['events']!=b['events'] or a['drummer']!=b['drummer'] or type(a['events']) is not int or a['events']<=0:raise ValueError('paired denominators differ')
        for row in (a,b):
            if not math.isfinite(row['sum_nll_nats']) or not math.isclose(row['mean_nll_nats'],row['sum_nll_nats']/row['events'],abs_tol=1e-12,rel_tol=0):raise ValueError('stored NLL inconsistency')
        paired.append({'id':key,'drummer':a['drummer'],'events':a['events'],'baseline_sum_nll':a['sum_nll_nats'],'expanded_sum_nll':b['sum_nll_nats'],'mean_delta':b['mean_nll_nats']-a['mean_nll_nats']})
    n=sum(x['events'] for x in paired);base=math.fsum(x['baseline_sum_nll'] for x in paired)/n;new=math.fsum(x['expanded_sum_nll'] for x in paired)/n
    mb=math.fsum(left[x['id']]['mean_nll_nats'] for x in paired)/len(paired);mn=math.fsum(right[x['id']]['mean_nll_nats'] for x in paired)/len(paired)
    return {'recordings':len(paired),'drummers':len({x['drummer'] for x in paired}),'events':n,'baseline_pooled_nll':base,'expanded_pooled_nll':new,'pooled_delta':new-base,'pooled_direction':direction(new-base),'baseline_macro_recording_nll':mb,'expanded_macro_recording_nll':mn,'macro_delta':mn-mb,'macro_direction':direction(mn-mb),'pooled_macro_direction_disagree':direction(new-base)!=direction(mn-mb),'per_recording':paired}


def prepare(output):
    if output.exists():raise ValueError('retain previous output')
    a=json.loads((REPO/OLD_PLAN).read_text());b=json.loads((REPO/NEW_PLAN).read_text())
    if {(r['id'],r['sha256']) for r in a['training']}!={(r['id'],r['sha256']) for r in b['training']} or set(a['baseline_train_ids'])!=set(b['baseline_train_ids']):raise ValueError('training changed across cohorts')
    old={r['id'] for r in a['diagnostics']};new={r['id'] for r in b['fresh_diagnostics']}
    if len(old)!=8 or len(new)!=8 or old&new:raise ValueError('cohort identities not eight disjoint recordings')
    plan={'created_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Posthoc comparison of saved predictions for two already observed recording cohorts; no MIDI read, fit, score or model change.',
          'frozen_hashes':{f:sha(REPO/f) for f in FILES},'conditions':a['conditions'],
          'cohorts':{'earlier_observed8':sorted(old),'cycle37_now_observed8':sorted(new)},
          'comparisons':'Within each cohort: paired12-to35 NLL change per drummer, split and all eight recordings, pooled and macro recording means. Cross-cohort directions per same drummer/condition and split/condition, descriptive difference of differences; recordings differ, not paired across cohorts.',
          'sign_rule':'Delta=expanded minus baseline; positive worse, negative better; abs<=1e-12 numerical tie only. Report every condition and every sign reversal, no selection.',
          'sample_scope':'16distinct recordings from the same four drummers, not16independent performers. Two recordings per drummer per cohort; four per drummer when combined.',
          'combined_summary':'Optional descriptive combined16 within each split/drummer, not a fresh or independent confirmation result.',
          'fixed_training':{'baseline_works':12,'baseline_events':5034,'expanded_unique_works':35,'expanded_events':19409},
          'roles_unchanged':{'training':35,'already_observed_recordings':16,'unscored_recordings':1099},
          'cpu_seconds':60,'source_access':'Existing plan/result/ledger JSON only; no source MIDI or model constructors.',
          'limitations':['Both cohorts now observed. The historically fresh label in original filenames does not make it fresh again.',
                         'Same drummers across cohorts, differing recordings, lengths, session/style/instrument mix and event weights.',
                         'Prediction change is not causal data-size effect, musical appeal, unobserved-condition robustness or general population effect.',
                         'No condition tuning or new model/material selection; any further analysis needs a separate prospective scope.']}
    output.mkdir(parents=True);(output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');return plan


def extract(report,old,condition,training,split):
    v=report['results'][training][condition]
    return v['splits'][split]['per_recording'] if old else v[split]['per_recording']


def run(plan_path,output):
    if output.exists():raise ValueError('retain previous result')
    start=time.process_time();p=json.loads(plan_path.read_text())
    for f,h in p['frozen_hashes'].items():
        if sha(REPO/f)!=h:raise ValueError('frozen input changed')
    old=json.loads((REPO/OLD_RESULTS).read_text());new=json.loads((REPO/NEW_RESULTS).read_text())
    if old['plan_sha256']!=sha(REPO/OLD_PLAN) or new['plan_sha256']!=sha(REPO/NEW_PLAN):raise ValueError('historical source plan binding')
    result=[];raw={}
    for cohort,report,is_old in [('earlier_observed8',old,True),('cycle37_now_observed8',new,False)]:
        raw[cohort]={}
        for c in p['conditions']:
            if time.process_time()-start>60:raise RuntimeError('CPU bound')
            raw[cohort][c]={}
            all_a=[];all_b=[]
            for split in ('validation','test'):
                a=extract(report,is_old,c,'baseline12',split);b=extract(report,is_old,c,'deduplicated35',split)
                raw[cohort][c][split]=(a,b);all_a+=a;all_b+=b
                result.append({'cohort':cohort,'condition':c,'level':'split','group':split,**summarize_pairs(a,b)})
                for drummer in sorted({x['drummer'] for x in a}):
                    result.append({'cohort':cohort,'condition':c,'level':'drummer','group':drummer,'split':split,**summarize_pairs([x for x in a if x['drummer']==drummer],[x for x in b if x['drummer']==drummer])})
            if {r['id'] for r in all_a}!=set(p['cohorts'][cohort]):raise ValueError('unexpected evaluated cohort')
            result.append({'cohort':cohort,'condition':c,'level':'all_recordings','group':'all',**summarize_pairs(all_a,all_b)})
    contrasts=[]
    for oldrow in [r for r in result if r['cohort']=='earlier_observed8']:
        newrow=next(r for r in result if r['cohort']=='cycle37_now_observed8' and (r['condition'],r['level'],r['group'])==(oldrow['condition'],oldrow['level'],oldrow['group']))
        contrasts.append({'condition':oldrow['condition'],'level':oldrow['level'],'group':oldrow['group'],
                          'earlier_recordings':oldrow['recordings'],'later_recordings':newrow['recordings'],'earlier_events':oldrow['events'],'later_events':newrow['events'],
                          'earlier_pooled_delta':oldrow['pooled_delta'],'later_pooled_delta':newrow['pooled_delta'],
                          'pooled_delta_difference':newrow['pooled_delta']-oldrow['pooled_delta'],
                          'pooled_sign_reversal':{oldrow['pooled_direction'],newrow['pooled_direction']}=={'better','worse'},
                          'macro_sign_reversal':{oldrow['macro_direction'],newrow['macro_direction']}=={'better','worse'},
                          'earlier_macro_delta':oldrow['macro_delta'],'later_macro_delta':newrow['macro_delta']})
    combined=[]
    for c in p['conditions']:
        for split in ('validation','test'):
            a=[];b=[]
            for cohort in raw:
                aa,bb=raw[cohort][c][split];a+=aa;b+=bb
            combined.append({'condition':c,'level':'split','group':split,**summarize_pairs(a,b)})
            for drummer in sorted({r['drummer'] for r in a}):combined.append({'condition':c,'level':'drummer','group':drummer,**summarize_pairs([x for x in a if x['drummer']==drummer],[x for x in b if x['drummer']==drummer])})
    report={'plan_sha256':sha(plan_path),'new_source_read':False,'new_fit_or_predictive_score':False,'roles_changed':False,'cohort_summaries':result,'cross_cohort_contrasts':contrasts,'combined_descriptive_summaries':combined,'pooled_macro_disagreements':[{'cohort':r['cohort'],'condition':r['condition'],'level':r['level'],'group':r['group'],'events':r['events']} for r in result if r['pooled_macro_direction_disagree']],
            'cpu_seconds':time.process_time()-start,'limitations':p['limitations']}
    output.mkdir(parents=True);(output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','run']);p.add_argument('--output',type=Path,required=True);p.add_argument('--plan',type=Path);a=p.parse_args()
    if a.mode=='run' and a.plan is None:p.error('run requires fixed plan')
    print(json.dumps(prepare(a.output) if a.mode=='prepare' else run(a.plan,a.output),indent=2))

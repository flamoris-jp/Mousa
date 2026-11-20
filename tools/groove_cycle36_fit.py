"""Parent-gated nested12 vs deduplicated35 whole-performance comparison."""
import argparse
from datetime import datetime,timezone
from pathlib import Path
from hashlib import sha256
import json
import math
import time
from mousa.drum_ioi_35work_profile import DrumIOI35WorkProfile
from mousa.drum_ioi_multiscale import CONDITIONS
from compare_groove_ioi import check_clearance,summarize_drummers
from prepare_groove_split import read_events

REPO=Path(__file__).resolve().parents[1]
CANDIDATE='experiments/2026-11-12-groove-cycle36-prepare-plan.json'
SCREEN='experiments/2026-11-12-groove-cycle36-screen.json'
OLD='experiments/2026-11-12-groove-multiscale-results.json'
NEWFILES=['src/mousa/drum_ioi_35work_profile.py','tests/test_groove_cycle36_profile.py','tools/groove_cycle36_fit.py','tests/test_groove_cycle36_fit.py',CANDIDATE,SCREEN,OLD]

def sha(p):return sha256(p.read_bytes()).hexdigest()


def deduplicate(rows,baseline_ids):
    grouped={}
    for r in rows:grouped.setdefault(r['sha256'],[]).append(r)
    retain=[];aliases=[]
    for group in grouped.values():
        prior=[r for r in group if r['id'] in baseline_ids]
        if len(prior)>1:raise ValueError('baseline contains duplicate performances; cannot silently drop')
        keep=prior[0] if prior else min(group,key=lambda r:r['id'])
        retain.append(keep)
        for r in group:
            if r['id']!=keep['id']:aliases.append({**r,'role':'duplicate-alias-excluded-from-fit','retained_id':keep['id']})
    retain.sort(key=lambda r:(r['drummer'],r['sha256'],r['id']))
    if not set(baseline_ids).issubset({r['id'] for r in retain}):raise ValueError('baseline lost')
    return retain,aliases


def prepare(output):
    if output.exists():raise ValueError('retain old plan')
    p=json.loads((REPO/CANDIDATE).read_text());screen=json.loads((REPO/SCREEN).read_text())
    if screen['plan_sha256']!=sha(REPO/CANDIDATE) or screen['status']!='screen_clear_pending_profile_and_parent_review':raise ValueError('screen binding/clearance')
    training,aliases=deduplicate(p['proposed_training'],p['baseline_train_ids'])
    if len(training)!=35 or sum(r['event_count'] for r in training)!=19409:raise ValueError('reviewed dedup inventory mismatch')
    hashes={**p['frozen_hashes'],**{f:sha(REPO/f) for f in NEWFILES}}
    for f,h in hashes.items():
        if sha(REPO/f)!=h:raise ValueError('frozen dependency changed')
    plan={'created_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Fixed six-condition exploratory comparison: original12 vs deduplicated35 training performances. Same eight observed diagnostics, not fresh validation.',
          'frozen_hashes':hashes,'inventory_sha256':p['inventory_sha256'],'baseline_train_ids':p['baseline_train_ids'],
          'training':training,'duplicate_aliases_excluded':aliases,'diagnostics':p['unchanged_observed_diagnostics'],
          'conditions':list(CONDITIONS),'deduplication_rule':'Retain baseline identity if present, otherwise lexicographically smallest ID per exact-byte hash; no replacement.36candidate historical screen unchanged.',
          'bounds':{'works':35,'train_events':30000,'events_per_work':4096,'cpu_seconds':60},
          'actual':{'baseline_train_works':12,'baseline_train_events':5034,'expanded_train_works':35,'expanded_train_events':19409,'newly_train_used_if_success':23,'excluded_alias_count':1,'observed_diagnostics':8,'diagnostic_events':6608},
          'formulas':'All six frozen Cycle34 formulas unchanged; separate standalone35-work profile reconstructs counts with per-work resets and delegates safe probability/evaluate only. No new sampler or generation.',
          'metrics':'All conditions per-recording/per-drummer/pooled/macro exact-IOI NLL; delta expanded-minus-baseline for every pair. Exactly48 baseline work-condition sums must reproduce historical Cycle34. No winner selection.',
          'verification':'Every source hash before/after, frozen dependency hashes, repeat equality excluding CPU, full support with no dropped/quantized events. After gates/source checks, before-fit record and per-constructor journal persist attempted IDs/condition, completed or failed construction even if later evaluation fails.',
          'role_policy':'Roles change only after actual authorized fit. Historical12train/8observed ledger remains immutable. Successful expanded fit uses23 formerly unused recordings; alias remains excluded. Of old1130unused,1107remain not fitted:40reserved eval+1alias+1066other.',
          'limitations':p['limitations']+['Thirty-five unique bytes are not thirty-five independent compositions or performers; six training drummers unchanged.',
             'Coverage changes instrument/style/duration mix as well as event counts; this is not an isolated data-volume causal estimate.',
             'The same eight recordings have guided prior research. No unobserved-condition or population generalization conclusion.',
             'Separate profile raises only work count to35; original30000-event cap stays unchanged. No raw MIDI/audio or fitted counts are published.']}
    output.mkdir(parents=True);(output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');return plan


def construct_journaled(works,condition,train_ids,group,output):
    journal=output/'fit-journal.json'
    state=json.loads(journal.read_text()) if journal.exists() else {'stages':[]}
    stage={'group':group,'condition':condition,'train_ids':list(train_ids),'status':'construction_started','actual_use':'These source IDs may enter construction; retain attempted use even on failure.'}
    state['stages'].append(stage);journal.write_text(json.dumps(state,indent=2)+'\n')
    try:
        model=DrumIOI35WorkProfile(works,condition=condition)
    except Exception as exc:
        stage['status']='construction_failed';stage['exception_type']=type(exc).__name__
        journal.write_text(json.dumps(state,indent=2)+'\n');raise
    stage['status']='construction_completed';stage['train_events']=model.base.n
    journal.write_text(json.dumps(state,indent=2)+'\n');return model


def run(root,plan_path,clearance,output):
    if output.exists():raise ValueError('retain prior results')
    start=time.process_time();check_clearance(plan_path,json.loads(clearance.read_text()));p=json.loads(plan_path.read_text())
    for f,h in p['frozen_hashes'].items():
        if sha(REPO/f)!=h:raise ValueError('frozen file changed')
    if sha(root/'private-inventory.json')!=p['inventory_sha256']:raise ValueError('inventory changed')
    def budget():
        if time.process_time()-start>60:raise RuntimeError('fixed CPU budget exceeded')
    rows=p['training']+p['diagnostics'];works={};paths={}
    for r in rows:
        budget();path=(root/r['relative_path']).resolve()
        if not path.is_relative_to(root.resolve()):raise ValueError('source path')
        events=read_events(path,r['sha256']);previous=0;work=[]
        for tick,key in events:work.append((tick-previous,key));previous=tick
        if len(work)!=r['event_count']:raise ValueError('source count')
        works[r['id']]=work;paths[r['id']]=path
    # Alias is integrity-checked but never tokenized or counted in fitting.
    for r in p['duplicate_aliases_excluded']:
        path=(root/r['relative_path']).resolve()
        if not path.is_relative_to(root.resolve()) or sha(path)!=r['sha256']:raise ValueError('alias integrity')
    output.mkdir(parents=True)
    (output/'before-fit.json').write_text(json.dumps({'plan_sha256':sha(plan_path),'clearance_sha256':sha(clearance),'sources_verified':True,'status':'before_first_constructor'},indent=2)+'\n')
    old=json.loads((REPO/OLD).read_text());results={};parities=0
    for label,ids in [('baseline12',p['baseline_train_ids']),('deduplicated35',[r['id'] for r in p['training']])]:
        result={}
        for condition in CONDITIONS:
            budget();model=construct_journaled([works[i] for i in ids],condition,ids,label,output);splits={}
            for split in ('validation','test'):
                per=[]
                for r in p['diagnostics']:
                    if r['proposed_split']!=split:continue
                    budget();v={'id':r['id'],'drummer':r['drummer'],**model.evaluate(works[r['id']])};per.append(v)
                    if label=='baseline12':
                        historic=next(x for x in old['results'][condition]['split_results'][split]['per_performance'] if x['id']==r['id'])
                        if v['sum_nll_nats']!=historic['sum_nll_nats']:raise ValueError('historical baseline mismatch')
                        parities+=1
                events=sum(v['events'] for v in per)
                splits[split]={'events':events,'recordings':len(per),'drummers':len({v['drummer'] for v in per}),'per_recording':per,'per_drummer':summarize_drummers(per),'pooled_mean_nll_nats':math.fsum(v['sum_nll_nats'] for v in per)/events,'macro_mean_nll_nats':math.fsum(v['mean_nll_nats'] for v in per)/len(per)}
            result[condition]={'train_works':len(ids),'train_events':model.base.n,'context_transitions':sum(model.base.context_totals.values()),'splits':splits}
        results[label]=result
    contrasts={}
    for c in CONDITIONS:
        contrasts[c]={}
        for s in ('validation','test'):
            a=results['baseline12'][c]['splits'][s];b=results['deduplicated35'][c]['splits'][s]
            contrasts[c][s]={'pooled_delta_expanded_minus_baseline':b['pooled_mean_nll_nats']-a['pooled_mean_nll_nats'],'per_recording':[{'id':x['id'],'mean_nll_delta':y['mean_nll_nats']-x['mean_nll_nats']} for x,y in zip(a['per_recording'],b['per_recording'])]}
    for r in rows:
        if sha(paths[r['id']])!=r['sha256']:raise ValueError('original changed during experiment')
    report={'plan_sha256':sha(plan_path),'clearance_sha256':sha(clearance),'fit_performed':True,'historical_baseline_exact_checks':parities,'source_hashes_unchanged':True,'duplicate_alias_fitted':False,'results':results,'expanded_minus_baseline':contrasts,'cpu_seconds':time.process_time()-start,'new_independent_validation':False,'limitations':p['limitations']}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','run']);p.add_argument('--output',type=Path,required=True);p.add_argument('--root',type=Path);p.add_argument('--plan',type=Path);p.add_argument('--clearance',type=Path);a=p.parse_args()
    if a.mode=='run' and any(x is None for x in (a.root,a.plan,a.clearance)):p.error('actual bound clearance/root/plan required')
    print(json.dumps(prepare(a.output) if a.mode=='prepare' else run(a.root,a.plan,a.clearance,a.output),indent=2))

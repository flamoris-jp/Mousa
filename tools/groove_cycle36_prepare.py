"""Nested drum-training coverage preparation only. Never constructs a model."""
import argparse
from collections import Counter,defaultdict
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import time
from prepare_groove_split import features,compare,read_events,split_for

REPO=Path(__file__).resolve().parents[1]
PRIOR='experiments/2026-11-12-groove-multiscale-plan.json'
RIGHTS='datasets/research-groove-rights-cycle32-20261112.json'
FILES=['tools/groove_cycle36_prepare.py','tests/test_groove_cycle36_prepare.py','tools/prepare_groove_split.py','tests/test_groove_split.py',RIGHTS,PRIOR,
       'experiments/2026-11-12-groove-cycle35-training-coverage-proposal.json','datasets/research-groove-usage-cycle34-20261112.json']

def sha(p):return sha256(p.read_bytes()).hexdigest()


def select_training(rows):
    selected=[];excluded=[]
    for i in range(1,7):
        eligible=[]
        for row in rows:
            if row['drummer']!=f'drummer{i}' or row['session'].endswith('/eval_session'):continue
            count=row['metrics']['note_on_positive']
            if type(count) is not int or not 1<=count<=4096:excluded.append(row['id']);continue
            eligible.append(row)
        selected.extend(sorted(eligible,key=lambda r:(r['sha256'],r['id']))[:6])
    return selected,excluded


def prepare(root,output):
    if output.exists():raise ValueError('new plan output required')
    prior=json.loads((REPO/PRIOR).read_text());inv_path=root/'private-inventory.json'
    if sha(inv_path)!=prior['inventory_sha256']:raise ValueError('inventory mismatch')
    rows=json.loads(inv_path.read_text())['records'];train,excluded=select_training(rows)
    oldtrain=[r for r in prior['sources'] if r['proposed_split']=='train']
    diagnostics=[r for r in prior['sources'] if r['proposed_split']!='train']
    if not {r['id'] for r in oldtrain}.issubset({r['id'] for r in train}):raise ValueError('nested baseline not retained')
    expanded=[]
    for row in train:
        expanded.append({'id':row['id'],'sha256':row['sha256'],'relative_path':row['relative_path'],'drummer':row['drummer'],'session':row['session'],'event_count':row['metrics']['note_on_positive'],'proposed_split':'train','original_split':row['split'],'previously_train_used':row['id'] in {r['id'] for r in oldtrain}})
    if len(expanded)>36 or sum(r['event_count'] for r in expanded)>60000:raise ValueError('predeclared whole-source bound')
    files={**prior['frozen_hashes'],**{f:sha(REPO/f) for f in FILES}}
    for f,h in files.items():
        if sha(REPO/f)!=h:raise ValueError('old frozen files changed')
    plan={'created_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Prospective nested training coverage preparation. No model fit, source admission or new predictive score.',
          'frozen_hashes':files,'inventory_sha256':sha(inv_path),'baseline_train_ids':[r['id'] for r in oldtrain],
          'proposed_training':expanded,'unchanged_observed_diagnostics':diagnostics,'over_cap_training_ids':excluded,
          'selection':'Original source SHA then ID, up to6 whole non-eval performances per drummer1–6,4096events each; retain all prior12. No score-guided replacement. Drummers7–10 never enter training.',
          'source_roles':'All40 eval_session recordings reserved. Proposed extra24 retain old unused status until actual parent-approved fitting succeeds; original release split is historical metadata only.',
          'fixed_screen':'Exact byte duplicates across drummer split groups block. All44 selected records vs every non-eval record in a different proposed split use full exact onset/instrument fingerprint, full tempo/offset-normalized instrument/IOI fingerprint, and fixed8-event coarse IOI120tick window-set Jaccard>=0.80. Any strong unresolved selected source blocks fit; do not silently replace/drop.',
          'screen_limits':{'cpu_seconds':60,'maximum_sources':1500,'maximum_total_events':500000,'maximum_cross_comparisons':50000},
          'future_model_conditions':prior['conditions'],'future_model_support':'unchanged original exact0..30720tick support; original PPQ480/timing unmodified; no new outcome or smoothing parameters',
          'anticipated_bounds':{'training_works':len(expanded),'training_events':sum(r['event_count'] for r in expanded),'evaluation_works':len(diagnostics),'evaluation_events':sum(r['event_count'] for r in diagnostics),'old_model_work_cap':20,'old_model_event_cap':30000,'proposed_separate_work_cap':36},
          'limitations':['This plan does not override the frozen model work cap. A separate reviewed profile is required before fitting36works even when event count stays below30000.',
                         'Increasing recordings changes content/instrument/style/duration as well as counts; neither recording count nor split implies independent compositions.',
                         'Screening is bounded, not a proof of pattern independence or legal originality. Common eight-event matches need interpretation.',
                         'Same eight diagnostics already observed; no fresh-condition generalization claim.',
                         'No raw MIDI/audio uploaded or committed; original rights attribution remains unchanged.']}
    output.mkdir(parents=True);(output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');return plan


def screen(root,plan_path,output):
    if output.exists():raise ValueError('new screen output required')
    start=time.process_time();plan=json.loads(plan_path.read_text())
    for f,h in plan['frozen_hashes'].items():
        if sha(REPO/f)!=h:raise ValueError('frozen dependency changed')
    inv_path=root/'private-inventory.json'
    if sha(inv_path)!=plan['inventory_sha256']:raise ValueError('inventory changed')
    rows=json.loads(inv_path.read_text())['records'];selected=plan['proposed_training']+plan['unchanged_observed_diagnostics']
    if len(rows)>1500:raise ValueError('source cap')
    def budget():
        if time.process_time()-start>60:raise RuntimeError('screen CPU budget exceeded; no fit permitted')
    fs={};total=0
    for r in rows:
        budget();p=(root/r['relative_path']).resolve()
        if not p.is_relative_to(root.resolve()):raise ValueError('source path escape')
        events=read_events(p,r['sha256']);total+=len(events)
        if total>500000 or len(events)!=r['metrics']['note_on_positive']:raise ValueError('inventory event bound')
        fs[r['id']]=features(events)
    non_eval=[r for r in rows if not r['session'].endswith('/eval_session')]
    by_hash=defaultdict(list)
    for r in non_eval:by_hash[r['sha256']].append(r)
    byte_cross=[[r['id'] for r in group] for group in by_hash.values() if len({split_for(r['drummer']) for r in group})>1]
    hits=[];strong=set();unsupported=[];count=0
    for a in selected:
        if fs[a['id']]['unsupported_iois']:unsupported.append(a['id'])
        for b in non_eval:
            if split_for(a['drummer'])==split_for(b['drummer']):continue
            budget();count+=1
            if count>50000:raise ValueError('cross comparison cap')
            v=compare(fs[a['id']],fs[b['id']])
            if v['shared_unique_windows'] or v['exact_onset_key'] or v['tempo_offset_normalized']:hits.append({'a':a['id'],'b':b['id'],**v})
            if v['strong_unresolved']:strong.add(a['id'])
    within=[];training=plan['proposed_training']
    for i,a in enumerate(training):
        for b in training[i+1:]:
            v=compare(fs[a['id']],fs[b['id']])
            if a['sha256']==b['sha256'] or v['strong_unresolved']:
                within.append({'a':a['id'],'b':b['id'],'exact_byte':a['sha256']==b['sha256'],'same_drummer':a['drummer']==b['drummer'],**v})
    report={'plan_sha256':sha(plan_path),'status':'blocked_for_parent_review' if byte_cross or strong or unsupported else 'screen_clear_pending_profile_and_parent_review',
            'fit_performed':False,'new_predictive_score':False,'source_roles_changed':False,
            'inventory_count':len(rows),'inventory_events_verified':total,'reserved_eval_count':len(rows)-len(non_eval),
            'proposed_train_count':len(training),'proposed_train_events':sum(r['event_count'] for r in training),
            'additional_count':sum(not r['previously_train_used'] for r in training),'per_training_drummer':[{'drummer':d,'recordings':sum(r['drummer']==d for r in training),'events':sum(r['event_count'] for r in training if r['drummer']==d)} for d in sorted({r['drummer'] for r in training})],
            'unchanged_diagnostic_count':8,'unchanged_diagnostic_events':6608,'cross_comparisons':count,'weak_or_strong_hits':len(hits),
            'strong_selected_ids':sorted(strong),'cross_byte_groups':byte_cross,'unsupported_selected_ids':unsupported,
            'within_training_pair_count':len(training)*(len(training)-1)//2,'within_training_strong_candidates':within,
            'model_profile_required':{'work_cap':36,'observed_training_events':sum(r['event_count'] for r in training),'existing_event_cap30000_sufficient':sum(r['event_count'] for r in training)<=30000,'must_not_reuse_old20work_constructor_silently':True},
            'cpu_seconds':time.process_time()-start,'limitations':plan['limitations']}
    output.mkdir(parents=True);(output/'report.json').write_text(json.dumps(report,indent=2)+'\n');(output/'pair-evidence.json').write_text(json.dumps(hits,indent=2)+'\n');return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','screen']);p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--plan',type=Path);a=p.parse_args()
    if a.mode=='screen' and a.plan is None:p.error('screen requires frozen plan')
    print(json.dumps(prepare(a.root,a.output) if a.mode=='prepare' else screen(a.root,a.plan,a.output),indent=2))

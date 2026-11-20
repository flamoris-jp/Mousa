"""Whole-output return editing; prepare reads sources but never fits/generates."""
from pathlib import Path
import json,hashlib,time
from datetime import datetime,timezone
from statistics import mean
from evaluate_dowland_cycle40 import inputs,ROOT
from mousa.gate_context_group_model import GateContextGroupModel,generate
from mousa.phrase_groups_cycle41 import compare_return
from mousa.group_timeline_metrics import timeline_metrics
from compare_context_onset_gate import metrics

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')

def prepare(out):
    if out.exists():raise ValueError('retain old plan')
    train,old,new,seq,sources,_=inputs()
    historical=ROOT/'experiments/2026-11-12-dowland-cycle40-plan.json'
    prior=json.loads(historical.read_text());frozen=dict(prior['frozen_hashes'])
    if sorted(sources.values())!=prior['source_sha256']:raise ValueError('frozen source set changed')
    if len(train)!=17 or len(old)!=2 or len(new)!=2:raise ValueError('exact17+4 refs required')
    for n,h in frozen.items():
        if digest(ROOT/n)!=h:raise ValueError('frozen dependency changed')
    own=['src/mousa/phrase_groups_cycle41.py','tools/compare_phrase_groups_cycle41.py','tests/test_phrase_groups_cycle41.py',
         'experiments/2026-11-12-dowland-cycle40-plan.json','experiments/2026-11-12-phrase-groups-cycle41-design.json']
    frozen.update({n:digest(ROOT/n) for n in own})
    p=dict(created_utc=datetime.now(timezone.utc).isoformat(),frozen_hashes=frozen,source_sha256=sorted(sources.values()),train_ids=list(train),copy_reference_ids=list(train)+list(old)+list(new),train_notes=sum(len(m.notes) for m in train.values()),train_groups=sum(len(seq[k]) for k in train),seeds=list(range(5)),arm='global',cpu_seconds=60,
           conditions=['unchanged8bar','protected_A_B_Aplus2_D'],target=9216,tail=384,max_notes=256,max_attempts=64,pitch_support=[0,127],fixed_boundaries=[2304,4608,6912],fixed_transposition=2,
           intervention='Whole8bar generated once per seed; replace C groups in[4608,6912) by A[0,2304) shifted+4608ticks/+2semitones. Boundaries with any sustained note crossing are rejected, end==nextstart legal. Never clip, move boundaries, shorten rests or substitute seeds. C replacement is generated-output editing, not original-data deletion.',
           superseded_unrun_design='Four independent2bar fragments was proposed but never executed; current control is unchanged full8bar generation.',
           roles='17training;640/921/Dowland21/1691 already observed and copyguard only, not training or new prediction.',
           copyguard='All21 original pitch sequences, identical exact8-note interval guard generated/canonical order on complete outputs, including joins. Intended internal repetition is not exempt.',
           outcomes='All5seeds/statuses, inherited generation failures/rejections and effort, boundary crossings, removed/added notes/groups/gate sums, pitch repetition/diversity/leaps and true silence/polyphony descriptors. Complete-only and common-success denominators, no beauty score; construction repetition is tautological not proof.',
           limitations=['Not learnedphrase, tonal cadence or voice leading. +2 may be tonally inappropriate.','C replacement changes density/register/rests; source A rests are preserved but output silence may differ.','Fixedboundary feasibility and survival selection confound comparisons; all failed rows retained.','Same old seeds may reproduce earlier candidates; not independent new sampling or fresh evaluation. No human ratings.','Global timing arm fixed, not selected as winner. Prior Cycle6 already tried handcrafted transposition; novel scope is intact group/sustain-safe editing.'])
    out.mkdir(parents=True);write(out/'plan.json',p);return p

def run(planpath,clearance,out):
    if out.exists():raise ValueError('retain old run')
    p=json.loads(planpath.read_text());c=json.loads(clearance.read_text());ph=digest(planpath)
    if c.get('approved') is not True or c.get('plan_sha256')!=ph:raise ValueError('bound parent approval required')
    for n,h in p['frozen_hashes'].items():
        if digest(ROOT/n)!=h:raise ValueError('frozen dependency changed')
    start=time.process_time()
    train,old,new,seq,sources,_=inputs()
    if sorted(sources.values())!=p['source_sha256'] or list(train)!=p['train_ids']:raise ValueError('source changed')
    refs=[[n.pitch for n in m.notes] for m in [*train.values(),*old.values(),*new.values()]]
    if len(refs)!=21:raise ValueError('all21refs required')
    out.mkdir();write(out/'before-fit.json',dict(plan_sha256=ph,train_ids=list(train),copy_reference_ids=p['copy_reference_ids']))
    write(out/'fit-journal.json',dict(status='construction_started',train_ids=list(train)))
    if time.process_time()-start>=60:raise RuntimeError('CPU exhausted before fit')
    try:m=GateContextGroupModel([seq[k] for k in train],arm='global')
    except Exception as exc:
        write(out/'fit-journal.json',dict(status='construction_failed',exception=type(exc).__name__));raise
    write(out/'fit-journal.json',dict(status='construction_completed',train_ids=list(train)))
    rows=[]
    for seed in p['seeds']:
        if time.process_time()-start>=60:
            rows.append(dict(seed=seed,generation_status='cpu_budget_skipped',control=dict(status='cpu_budget_skipped'),intervention=dict(status='cpu_budget_skipped')));continue
        g=generate(m,seed,cpu_deadline=start+60)
        private=out/f'seed-{seed}-private.json'
        row=dict(seed=seed,generation_status=g['status'],generation_attempts=g['attempts'],generation_rejections=g['rejections'])
        if g['status']!='complete':
            v=dict(control=dict(status=g['status']),intervention=dict(status='baseline_unavailable'))
        else:v=compare_return(g['notes'],g['groups'],refs)
        write(private,dict(original=g,comparison=v));row['private_sha256']=digest(private)
        for label in ('control','intervention'):
            raw=v[label];item={k:x for k,x in raw.items() if k not in ('notes','groups')}
            if 'notes' in raw:
                item['metrics']=metrics(raw['notes'],9216);item['timeline_metrics']=timeline_metrics(raw['notes'],9216)
                item['notes']=len(raw['notes']);item['groups']=len(raw['groups'])
            row[label]=item
        rows.append(row);write(out/'progress.json',rows)
    summaries={}
    common=[r['seed'] for r in rows if all(r[k]['status']=='complete' for k in ('control','intervention'))]
    for label in ('control','intervention'):
        complete=[r[label] for r in rows if r[label]['status']=='complete']
        summaries[label]=dict(total_candidates=5,complete=len(complete),status_counts={s:sum(r[label]['status']==s for r in rows) for s in sorted({r[label]['status'] for r in rows})},
          timeline_complete_means={k:mean(v['timeline_metrics'][k] for v in complete) for k in ('silence_ticks','leading_silence_ticks','internal_silence_ticks','trailing_silence_ticks','polyphonic_time_fraction')} if complete else {})
    report=dict(plan_sha256=ph,rows=rows,summaries=summaries,common_complete_seeds=common,all_sources_unchanged=all(digest(Path(k))==h for k,h in sources.items()),cpu_seconds=time.process_time()-start,limitations=p['limitations'])
    write(out/'report.json',report);return report

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('mode',choices=['prepare','run']);a.add_argument('--output',type=Path,required=True);a.add_argument('--plan',type=Path);a.add_argument('--clearance',type=Path);x=a.parse_args()
    if x.mode=='run' and (x.plan is None or x.clearance is None):a.error('plan and clearance required')
    print(json.dumps(prepare(x.output) if x.mode=='prepare' else run(x.plan,x.clearance,x.output),indent=2))

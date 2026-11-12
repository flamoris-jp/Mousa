"""Octave register comparison of pitch-only anchor return; prepare reads sources but never fits/generates."""
from pathlib import Path
import json,hashlib,time
from datetime import datetime,timezone
from statistics import mean
from evaluate_dowland_cycle40 import inputs,ROOT
from mousa.gate_context_group_model import GateContextGroupModel,generate
from mousa.phrasewide_register_cycle44 import compare_phrasewide
from mousa.anchor_register_cycle43 import compare_octaves
from mousa.group_timeline_metrics import timeline_metrics
from compare_context_onset_gate import metrics

CONDITIONS=('control','nearest_octave','phrasewide')

def cpu_skipped_row(seed):
    return dict(seed=seed,generation_status='cpu_budget_skipped',**{label:dict(status='cpu_budget_skipped') for label in CONDITIONS})

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')

def anchor_gaps(groups):
    buckets={k:[] for k in ('overall','C_entry','C_internal','C_exit')}
    for a,b in zip(groups,groups[1:]):
        gap=abs(b['anchor']-a['anchor']);buckets['overall'].append(gap)
        ca=4608<=a['onset']<6912;cb=4608<=b['onset']<6912
        key='C_internal' if ca and cb else 'C_entry' if cb else 'C_exit' if ca else None
        if key:buckets[key].append(gap)
    return {k:dict(transitions=len(v),sum_abs=sum(v),mean_abs=mean(v) if v else None) for k,v in buckets.items()}

def prepare(out):
    if out.exists():raise ValueError('retain old plan')
    train,old,new,seq,sources,_=inputs()
    historical=ROOT/'experiments/2026-11-12-dowland-cycle40-plan.json'
    prior=json.loads(historical.read_text());frozen=dict(prior['frozen_hashes'])
    if sorted(sources.values())!=prior['source_sha256']:raise ValueError('frozen source set changed')
    if len(train)!=17 or len(old)!=2 or len(new)!=2:raise ValueError('exact17+4 refs required')
    for n,h in frozen.items():
        if digest(ROOT/n)!=h:raise ValueError('frozen dependency changed')
    own=['src/mousa/phrase_groups_cycle41.py','src/mousa/anchor_return_cycle42.py','tools/compare_anchor_return_cycle42.py','tests/test_anchor_return_cycle42.py','tools/compare_anchor_register_cycle43.py','src/mousa/anchor_register_cycle43.py','tests/test_anchor_register_cycle43.py','tests/test_anchor_register_cycle43_driver.py','src/mousa/phrasewide_register_cycle44.py','tools/compare_phrasewide_register_cycle44.py','tests/test_phrasewide_register_cycle44.py','tests/test_phrasewide_register_cycle44_driver.py',
         'experiments/2026-11-12-dowland-cycle40-plan.json','experiments/2026-11-12-anchor-return-cycle41-next-proposal.json']
    frozen.update({n:digest(ROOT/n) for n in own})
    proposal_path=ROOT/'experiments/2026-11-12-anchor-return-cycle41-next-proposal.json'
    if digest(proposal_path)!='81f561a1fea459be7247435a657f530eb451d5660a0624bc4601f16d556b7ef4':raise ValueError('approved proposal changed')
    proposal=json.loads(proposal_path.read_text())
    p=dict(created_utc=datetime.now(timezone.utc).isoformat(),frozen_hashes=frozen,source_sha256=sorted(sources.values()),train_ids=list(train),copy_reference_ids=list(train)+list(old)+list(new),train_notes=sum(len(m.notes) for m in train.values()),train_groups=sum(len(seq[k]) for k in train),
           seeds=list(range(5)),arm='global',cpu_seconds=60,conditions=list(CONDITIONS),target=9216,tail=384,max_notes=256,max_attempts=64,pitch_support=[0,127],
           proposal_sha256=digest(proposal_path),previous_intervention=proposal,
           intervention='Original A[j mod len(A)]anchor+2 pitchclass. Enumerate ALL legal MIDI anchors for each C template. Exact DP minimizes entrance absolute anchor difference + sum internal absolute differences + exit difference. Missing entrance/exit contribute zero. Ties choose lexicographically lowest entire anchor sequence. No future voice labels; this is a complete-output editing objective. After chosen path, reject collisions/copy without next-best search.',
           dp_budget='1..256 groups, <=11 legal anchors/group, <=255*121 transition evaluations; explicit guards. Each state retains cheapest lexicographic path for its last anchor.',
           empty_cases='Aempty/Cempty blocked; unchanged wholeanchor mapping no_effect; no legal octave candidate blocked.',
           comparison='Same one generated pool, same21refs/guards. Greedy nearest-octave and control retained unchanged; no safety relaxation. Known0..4seeds replay, all3arms reported.',
           diagnostic='Report absolute adjacent group-anchor differences overall/C-entry/C-internal/C-exit separately, plus existing event-order gaps, repeat/diversity and complete/common denominators. Minimized total proxy is not independent evidence; individual entrance/exit gaps can worsen when total ties.',
           roles='Same17train+observed640/921/Dowland21/1691. No new sources, predictive evaluations or actual human ratings.',
           outcomes='All5statuses/all3arms, same temporal invariants, eventorder and groupanchor gap descriptors; complete-only and all-three common means with denominators. Raw anchor arrays private.',
           limitations=proposal['interpretation_limits']+['The known global0..4 pool is replayed, not independent new random draws. No re-selection after results.','Same timeline means density and silence are fixed by design, not quality gains.','No_effect is not an accepted nontrivial recurrence; emptyA/C are blocked.','Phrasewide minimization targets groupanchor total variation, not voice leading, harmony or listener preference. Individual boundaries may worsen.','Octave alternatives change intervention law, not a probability-equivalent sampler. Raw melody-event intervals include simultaneity.'])
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
            rows.append(cpu_skipped_row(seed));continue
        g=generate(m,seed,cpu_deadline=start+60)
        private=out/f'seed-{seed}-private.json'
        row=dict(seed=seed,generation_status=g['status'],generation_attempts=g['attempts'],generation_rejections=g['rejections'])
        if g['status']!='complete':
            v=dict(control=dict(status=g['status']),nearest_octave=dict(status='baseline_unavailable'),phrasewide=dict(status='baseline_unavailable'))
        else:
            wide=compare_phrasewide(g['notes'],g['groups'],refs);octave=compare_octaves(g['notes'],g['groups'],refs)
            assert wide['control']==octave['control']
            v=dict(control=wide['control'],nearest_octave=octave['intervention'],phrasewide=wide['intervention'])
        write(private,dict(original=g,comparison=v));row['private_sha256']=digest(private)
        for label in CONDITIONS:
            raw=v[label];item={k:x for k,x in raw.items() if k not in ('notes','groups')}
            if 'edit' in item:
                item['edit']={k:v for k,v in item['edit'].items() if k not in ('original_C_anchors','mapped_C_anchors')}
            if 'notes' in raw:
                item['metrics']=metrics(raw['notes'],9216);item['timeline_metrics']=timeline_metrics(raw['notes'],9216)
                item['notes']=len(raw['notes']);item['groups']=len(raw['groups']);item['anchor_gaps']=anchor_gaps(raw['groups'])
            row[label]=item
        rows.append(row);write(out/'progress.json',rows)
    summaries={}
    common=[r['seed'] for r in rows if all(r[k]['status']=='complete' for k in CONDITIONS)]
    for label in CONDITIONS:
        complete=[r[label] for r in rows if r[label]['status']=='complete']
        summaries[label]=dict(total_candidates=5,complete=len(complete),status_counts={s:sum(r[label]['status']==s for r in rows) for s in sorted({r[label]['status'] for r in rows})},
          timeline_complete_means={k:mean(v['timeline_metrics'][k] for v in complete) for k in ('silence_ticks','leading_silence_ticks','internal_silence_ticks','trailing_silence_ticks','polyphonic_time_fraction')} if complete else {})
    common_means={}
    for label in CONDITIONS:
        eligible=[r[label] for r in rows if r['seed'] in common]
        common_means[label]=dict(denominator=len(eligible),metrics={k:mean(v['metrics'][k] for v in eligible if v['metrics'][k] is not None) if any(v['metrics'][k] is not None for v in eligible) else None for k in eligible[0]['metrics']} if eligible else {})
    report=dict(common_success_means=common_means,plan_sha256=ph,rows=rows,summaries=summaries,common_complete_seeds=common,all_sources_unchanged=all(digest(Path(k))==h for k,h in sources.items()),cpu_seconds=time.process_time()-start,limitations=p['limitations'])
    write(out/'report.json',report);return report

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('mode',choices=['prepare','run']);a.add_argument('--output',type=Path,required=True);a.add_argument('--plan',type=Path);a.add_argument('--clearance',type=Path);x=a.parse_args()
    if x.mode=='run' and (x.plan is None or x.clearance is None):a.error('plan and clearance required')
    print(json.dumps(prepare(x.output) if x.mode=='prepare' else run(x.plan,x.clearance,x.output),indent=2))

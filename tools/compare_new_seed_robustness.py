"""Frozen 2x2 model, new random seeds; not independent music validation."""
import argparse
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction
import json
from pathlib import Path
from statistics import mean
from time import process_time
from mousa.separated_count_context import SeparatedCountContext
from mousa.overlap_midi import read_midi
from mousa.optimized_feasible_generation import generate_optimized
from mousa.research_intake import validate_manifest
from compare_context_onset_gate import digest,metrics
from compare_onset_gate_models import pairs,phrases

SEEDS=tuple(range(100,110))
METRICS=('repeated_pitch_fraction','notes','distinct_pitches','overlap_onset_fraction')
CELLS=('timing0_pitch0','timing0_pitch1','timing1_pitch0','timing1_pitch1')


def used_seeds(value):
    found=set()
    if isinstance(value,dict):
        if type(value.get('seed')) is int:found.add(value['seed'])
        for key,v in value.items():
            if key=='seeds' and isinstance(v,list):found.update(x for x in v if type(x) is int)
            found.update(used_seeds(v))
    elif isinstance(value,list):
        for v in value:found.update(used_seeds(v))
    return found


def contrasts(conditions):
    """Complete-all-four intersection only, explicit denominator per metric."""
    rows={k:{r['seed']:r for r in conditions[k]['outputs'] if r['status']=='complete'} for k in CELLS}
    common=sorted(set.intersection(*(set(v) for v in rows.values())))
    result={}
    for metric in METRICS:
        values=[]
        for seed in common:
            v=[rows[k][seed]['metrics'][metric] for k in CELLS]
            if any(x is None for x in v):continue
            values.append(dict(seed=seed,value=v[3]-v[2]-v[1]+v[0]))
        result[metric]=dict(mean=mean(v['value'] for v in values) if values else None,
                            denominator=len(values),per_seed=values)
    return dict(common_complete_seeds=common,definition='both - timing_only - pitch_only + neither',metrics=result)


def run(root,corpus,cornelius,adam,chopin,output):
    if output.exists():raise ValueError('new output required')
    oldpath=root/'experiments/2026-11-12-separated-augmentation-results.json'
    old=json.loads(oldpath.read_text());frozen=old['plan']
    for p,sha in frozen['code_sha256'].items():
        if digest(root/p)!=sha:raise ValueError('frozen dependency changed')
    # Audit previous stored experiment records, not every possible local test RNG.
    historical={}
    for p in sorted((root/'experiments').glob('*.json')):
        # Own published replay records do not make seeds prior experiments.
        if p.name in {f'2026-11-12-new-seed-robustness-{suffix}.json'
                      for suffix in ('initial-plan','results','replay-plan','repeat-verification')}:continue
        historical[str(p.relative_to(root))]=used_seeds(json.loads(p.read_text()))
    conflicts={p:sorted(set(SEEDS)&s) for p,s in historical.items() if set(SEEDS)&s}
    if conflicts:raise ValueError('requested seeds already in experiment records: '+str(conflicts))
    manifest=json.loads((root/'datasets/research-exploratory-multifamily-20261112.json').read_text());validate_manifest(manifest,corpus)
    train=[]
    for w in manifest['works']:
        if w['work_id'] in frozen['train_sha256']:
            if digest(corpus/w['file'])!=frozen['train_sha256'][w['work_id']]:raise ValueError('old source changed')
            train.append(read_midi(corpus/w['file'],w['track_index']))
    if len(train)!=4 or digest(cornelius)!=frozen['extra_sha256']:raise ValueError('training source changed')
    for w,p in [('640',adam),('921',chopin)]:
        if digest(p)!=frozen['target_sha256'][w]:raise ValueError('copy-reference source changed')
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),scope='New random draw robustness; not independent work or musical-data generalization',
        seeds=list(SEEDS),historical_seed_audit=dict(json_files=len(historical),conflicts=conflicts,scope='Stored seed/seeds fields in repository experiments; does not claim no software test used same RNG number'),
        conditions=list(CELLS),generation='Frozen cycle24 adapter/models; mix1/4,feasible,tail384,target9216,max256notes; no retry or selection',
        budget='Maximum40 candidates, process CPU60seconds checked before each bounded candidate; skipped status retained',
        metrics=list(METRICS),interaction='both - timing_only - pitch_only + neither, same complete-all-four seed subset and per-metric denominators',
        old_batch='Previous5seeds0..4 retained as observed comparison, never pooled as independent works',
        statuses='All failures, copy blocks and CPU skips reported; no winner selection',
        copy_guard='All5train and observed640/921, exact8interval on generated/canonical ordering;580 excluded from evaluation, no new prediction scores',
        caveats=['Paired seed labels do not align random draws after sampler branching.','One frozen training set; seed repeats are not independent compositions or human judgments.','Complete-only descriptors and intersection contrasts are conditional on success.'],
        frozen_hashes=frozen['code_sha256'],prior_report_sha256=digest(oldpath),
        new_code_sha256={p:digest(root/p) for p in ['tools/compare_new_seed_robustness.py','tests/test_new_seed_robustness.py']})
    output.mkdir(parents=True);(output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    extra=read_midi(cornelius,1);alltrain=[*train,extra]
    refs=[*alltrain,read_midi(adam,2),read_midi(chopin,1)]
    forbidden=set().union(*(phrases([n.pitch for n in m.notes]) for m in refs))
    conditions={};start=process_time()
    for t,p in ((False,False),(False,True),(True,False),(True,True)):
        name=f'timing{int(t)}_pitch{int(p)}';tm=alltrain if t else train;pm=alltrain if p else train
        model=SeparatedCountContext([pairs(m) for m in tm],[[n.pitch for n in m.notes] for m in tm],
            [pairs(m) for m in pm],[[n.pitch for n in m.notes] for m in pm]);rows=[]
        for seed in SEEDS:
            if process_time()-start>=60:
                rows.append(dict(seed=seed,status='cpu_budget_skipped'));continue
            g=generate_optimized(model,seed,uniform_mix=Fraction(1,4),trailing_rest_ticks=384)
            ns=g['notes'];canon=sorted(ns,key=lambda n:(n['start'],n['end'],n['pitch']))
            hits=len((phrases([n['pitch'] for n in ns])|phrases([n['pitch'] for n in canon]))&forbidden)
            row={k:v for k,v in g.items() if k!='notes'};row.update(seed=seed,copy_matches=hits,metrics=metrics(ns,9216))
            if hits:row['status']='copy_guard_blocked'
            f=output/f'{name}-{seed}-notes.json';f.write_text(json.dumps(ns,sort_keys=True)+'\n');row['private_notes_sha256']=digest(f);rows.append(row)
        means={};denominators={}
        for metric in METRICS:
            values=[r['metrics'][metric] for r in rows if r['status']=='complete' and r['metrics'][metric] is not None]
            means[metric]=mean(values) if values else None;denominators[metric]=len(values)
        conditions[name]=dict(outputs=rows,status_counts=dict(Counter(r['status'] for r in rows)),complete_only_means=means,metric_denominators=denominators)
    report=dict(plan=plan,conditions=conditions,interaction=contrasts(conditions),old_batch_interaction=contrasts(old['conditions']),
        old_batch_means={k:{m:v['complete_only_means'][m] for m in METRICS} for k,v in old['conditions'].items()},
        cpu_seconds=process_time()-start,no_predictive_scores=True,no_new_training_data=True)
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:dict(status=v['status_counts'],means=v['complete_only_means']) for k,v in conditions.items()},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('corpus','cornelius','adam','chopin','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();run(Path(__file__).resolve().parents[1],a.corpus,a.cornelius,a.adam,a.chopin,a.output)

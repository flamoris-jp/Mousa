"""Predeclared tiny family-subset generation comparison, no fresh scores."""
import argparse
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction
import json
from pathlib import Path
import time
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.optimized_feasible_generation import generate_optimized
from mousa.overlap_midi import read_midi,write_midi,OverlapMelody
from mousa.tick_midi import TickNote
from mousa.research_intake import validate_manifest
from compare_context_onset_gate import digest,summarize
from compare_timing_generation_transfer import descriptors
from compare_onset_gate_models import pairs,phrases
from compare_training_quantity import FAMILIES,TARGETS


def generation_specs():
    return [(f'family{i}',tuple(family)) for i,family in enumerate(FAMILIES)]+[('full',tuple(w for family in FAMILIES for w in family))]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('corpus','brahms','adam','output'):parser.add_argument('--'+name,type=Path,required=True)
    a=parser.parse_args();root=Path(__file__).resolve().parents[1]
    if a.output.exists():raise ValueError('new output required')
    frozen=json.loads((root/'experiments/2026-11-12-efficient-ending-plan.json').read_text())
    for path in ('src/mousa/optimized_feasible_generation.py','src/mousa/context_onset_gate.py','src/mousa/onset_gate_model.py',
                 'src/mousa/feasible_context_generation.py','datasets/research-exploratory-multifamily-20261112.json'):
        if digest(root/path)!=frozen['code_sha256'][path]:raise ValueError('frozen input changed')
    paths={'580':a.brahms,'640':a.adam}
    for name,(sha,track) in TARGETS.items():
        if digest(paths[name])!=sha:raise ValueError('observed reference changed')
    tracked=['tools/compare_quantity_generation.py','tools/compare_training_quantity.py',
        'tools/compare_timing_generation_transfer.py','tools/compare_context_onset_gate.py','tools/compare_onset_gate_models.py',
        'src/mousa/context_onset_gate.py','src/mousa/optimized_feasible_generation.py','src/mousa/feasible_context_generation.py',
        'src/mousa/onset_gate_model.py','src/mousa/overlap_midi.py','datasets/research-exploratory-multifamily-20261112.json']
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),scope='Cycle21 exploratory quantity/content generation comparison; no fresh predictive scoring',
        conditions=generation_specs(),selection='Every singlefamily subset plusfull; not selected byprevious NLL ranking.888/889inseparable.',
        model='ContexttimingTrue,pitchcontinuityTrue,strength4,uniformmix1/4,optimizedjointfeasibility',
        constraints=dict(target_ticks=9216,max_trailing_rest_ticks=384,max_notes=256,max_polyphony=3,max_attempts=64,seeds=list(range(5))),
        candidate_budget=20,cpu_budget='30CPUseconds checked between candidates; remainingcandidates explicitly skipped if exhausted.Each call independently bounded256notes/12289delta support. No retry/selection.',
        order='For eachseed0..4 run family0,1,2,full. Cache/order remains localbenchmark caveat.',
        confounds='Familycount/content/eventcount/pitchvocabulary allchange. No isolatedquantity causality; subset vocabulary retained, not forcedcommon range.',
        copyguard='Same exact8onset interval screen againstallold4+observed580+observed640 regardlesssubset, generatedandcanonicalorder; fail no retry',
        metrics=['allstatuses/cpu skips/rejections/draws','CPU/wall','repeat/unique/leaps/density','overlap/rest/shortgates/tail','pitchvocab size/range','exactMIDIroundtrip'],
        aggregation='Percondition all5statuses andsuccessfulmeans with denominators; commonacceptedseed subset remains success-conditioned',
        no_predictive_evaluation=True,no_new_source=True,no_audio=True,no_winner_tuning=True,
        code_sha256={p:digest(root/p) for p in tracked})
    a.output.mkdir(parents=True);(a.output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    manifest=json.loads((root/'datasets/research-exploratory-multifamily-20261112.json').read_text());validate_manifest(manifest,a.corpus)
    all_ids={w for family in FAMILIES for w in family};training={};hashes={}
    for w in manifest['works']:
        if w['work_id'] not in all_ids:continue
        training[w['work_id']]=read_midi(a.corpus/w['file'],w['track_index']);hashes[w['work_id']]=digest(a.corpus/w['file'])
    if set(training)!=all_ids:raise ValueError('missing training source')
    refs=[[n.pitch for n in m.notes] for m in training.values()]
    for name,(sha,track) in TARGETS.items():refs.append([n.pitch for n in read_midi(paths[name],track).notes])
    forbidden=set().union(*(phrases(r) for r in refs));models={};model_info={}
    for name,ids in generation_specs():
        seqs=[pairs(training[w]) for w in ids];pss=[[n.pitch for n in training[w].notes] for w in ids]
        m=ContextOnsetGateModel(seqs,pss,timing_context=True,pitch_continuity=True,strength=4);models[name]=m
        model_info[name]=dict(work_ids=ids,training_events=sum(map(len,seqs)),work_count=len(ids),
            pitch_vocabulary=list(m.vocabulary),pitch_vocabulary_size=len(m.vocabulary),pitch_range=[min(m.vocabulary),max(m.vocabulary)])
    before=dict(plan_sha256=digest(a.output/'plan.json'),train_sha256=hashes,models=model_info,
                observed_copy_reference_sha256={k:v[0] for k,v in TARGETS.items()})
    (a.output/'before-generation.json').write_text(json.dumps(before,indent=2)+'\n')
    rows={name:[] for name in models};cpu_start=time.process_time()
    for seed in range(5):
        for name,m in models.items():
            if time.process_time()-cpu_start>=30:
                rows[name].append(dict(seed=seed,status='skipped_cpu_budget',rejections=0,timing_draws=0,pitch_draws=0,
                    generation_timing=dict(wall_seconds=0,cpu_seconds=0)));continue
            wall=time.perf_counter();cpu=time.process_time()
            result=generate_optimized(m,seed,uniform_mix=Fraction(1,4),trailing_rest_ticks=384)
            timing=dict(wall_seconds=time.perf_counter()-wall,cpu_seconds=time.process_time()-cpu)
            ns=result['notes'];row={k:v for k,v in result.items() if k!='notes'}
            row.update(seed=seed,metrics=descriptors(ns),generation_timing=timing)
            if result['status']=='complete':
                notes=tuple(sorted((TickNote(n['start'],n['end'],n['pitch'],80,0) for n in ns),key=lambda n:(n.start,n.end,n.pitch)))
                matches=(phrases([n['pitch'] for n in ns])|phrases([n.pitch for n in notes]))&forbidden
                row['copy_matches']=len(matches)
                if matches:row['status']='copy_guard_blocked'
                else:
                    events=[]
                    for i,n in enumerate(ns):events.extend(((n['start'],1,i,'note_on',n['pitch'],80),(n['end'],0,i,'note_off',n['pitch'],0)))
                    stream=((0,'program',0,0),)+tuple((t,k,p,v) for t,_,i,k,p,v in sorted(events))
                    melody=OverlapMelody(notes,9216,(6,8),ppq=384,channel_events=stream)
                    path=a.output/f'{name}-{seed}.mid';write_midi(melody,path)
                    if read_midi(path,1)!=melody:raise ValueError('MIDIroundtrip failed')
                    row.update(midi_sha256=digest(path),exact_roundtrip=True)
            rows[name].append(row)
    conditions={}
    for name,outputs in rows.items():
        means,den=summarize(outputs)
        conditions[name]=dict(model=model_info[name],outputs=outputs,statuses=dict(Counter(r['status'] for r in outputs)),
            rejections=sum(r['rejections'] for r in outputs),timing_draws=sum(r['timing_draws'] for r in outputs),
            generation_timing={k:sum(r['generation_timing'][k] for r in outputs) for k in ('wall_seconds','cpu_seconds')},
            complete_only_means=means,metric_denominators=den)
    common=sorted(set.intersection(*(set(r['seed'] for r in outputs if r['status']=='complete') for outputs in rows.values())))
    paired={}
    for name,outputs in rows.items():
        means,den=summarize([r for r in outputs if r['seed'] in common]);paired[name]=dict(means=means,metric_denominators=den)
    report=dict(plan=plan,before_generation=before,conditions=conditions,common_accepted_seed_analysis=dict(seeds=common,conditions=paired),
        originals_unchanged=all(digest(paths[k])==v[0] for k,v in TARGETS.items()),
        limitations=['Fivefixed seeds percondition, not independentlargebenchmark.',
            'Samplequantity andmusicalcontent andpitchsupport confounded; no uniformmoredataisbetter claim.',
            'Samepitchrate isnot entiremonotony; density/polyphony cantradeoff.',
            'Copyguard narrow, not perceptual orlegalclearance; no listeninglabels.',
            '30secondguard is betweenbounded calls, not a hardinterrupt midgeneration.'])
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({n:{k:c[k] for k in ('model','statuses','generation_timing','complete_only_means')} for n,c in conditions.items()},indent=2))


if __name__=='__main__':main()

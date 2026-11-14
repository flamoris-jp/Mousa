"""Fixed generation-only timing-context comparison; no new predictive scores."""
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
from compare_context_onset_gate import digest,metrics,summarize
from compare_onset_gate_models import pairs,phrases

TRAIN_IDS=('mutopia-376','mutopia-888','mutopia-889','mutopia-789')


def make_models(sequences,pitch_sequences):
    return {f'timing{int(context)}':ContextOnsetGateModel(sequences,pitch_sequences,
        timing_context=context,pitch_continuity=True,strength=4) for context in (False,True)}


def descriptors(notes,target=9216):
    result=metrics(notes,target)
    result.update(short_gate_count=sum(n['end']-n['start']<24 for n in notes),
        last_quarter_onsets=sum(n['start']>=target-384 for n in notes),
        actual_silent_tail_ticks=target-max(n['end'] for n in notes) if notes else None)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('corpus','brahms','adam','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();root=Path(__file__).resolve().parents[1]
    if a.output.exists():raise ValueError('new output required')
    frozen=json.loads((root/'experiments/2026-11-12-efficient-ending-plan.json').read_text())
    for path in ('src/mousa/optimized_feasible_generation.py','src/mousa/feasible_context_generation.py',
                 'src/mousa/context_onset_gate.py','src/mousa/onset_gate_model.py',
                 'datasets/research-exploratory-multifamily-20261112.json'):
        if digest(root/path)!=frozen['code_sha256'][path]:raise ValueError('frozen dependency changed')
    registry=json.loads((root/'datasets/research-source-observations.json').read_text())
    if not any(r['work_id']=='mutopia-640' and r['state']=='predictive-observed' for r in registry['observations']):
        raise ValueError('640must remain explicitly observed')
    tracked=['tools/compare_timing_generation_transfer.py','src/mousa/context_onset_gate.py',
        'src/mousa/optimized_feasible_generation.py','src/mousa/feasible_context_generation.py',
        'src/mousa/onset_gate_model.py','src/mousa/overlap_midi.py','tools/compare_context_onset_gate.py',
        'tools/compare_onset_gate_models.py','datasets/research-exploratory-multifamily-20261112.json',
        'datasets/research-source-observations.json']
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),scope='Cycle18 fixed generation comparison, no fresh or repeated predictive evaluation',
        train_ids=list(TRAIN_IDS),observed_copy_only=[580,640],reserved_never_load=[583],
        difference='Only previousgate->delta context off/on; shrinkagestrength4 whencontextseen',
        identical_controls='pitchcontinuityTrue,uniformmix1/4,optimized jointfeasibility,target9216,tail<=384,max256notes,poly<=3',
        seeds=list(range(10)),conditions=['timing0','timing1'],execution='Alternate conditionorder byseedparity, no seedselection or regeneration',
        copy_screen='Exact8onset interval windows againsttrain4+observed580+observed640 in generatedandcanonicalorder, no retry',
        metrics=['completion/copyfailure/rejections','CPU/wall generationonly','notes/repeat/unique/leaps','overlap/voicecoverage/rest','shortgates<24','tailonsets>=target-384','actualsilenttail'],
        aggregation='All10statuses each; completedonly means withpermetricdenominators; commonacceptedseed paired subset remains success-conditioned',
        interpretation='Better known timingNLL neednot improvegeneration features or appeal; no predictive calls, no newfitdata, no hypothesis tuning',
        no_tonal_cadence_claim=True,code_sha256={x:digest(root/x) for x in tracked})
    a.output.mkdir(parents=True);(a.output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    manifest=json.loads((root/'datasets/research-exploratory-multifamily-20261112.json').read_text());validate_manifest(manifest,a.corpus)
    sequences=[];pitch_sequences=[];hashes={}
    for w in manifest['works']:
        if w['work_id'] not in TRAIN_IDS:continue
        m=read_midi(a.corpus/w['file'],w['track_index']);sequences.append(pairs(m));pitch_sequences.append([n.pitch for n in m.notes])
        hashes[w['work_id']]=digest(a.corpus/w['file'])
    if len(sequences)!=4:raise ValueError('missingtrainwork')
    expected={580:'dcd5efac22b5e91b7c87685058784396adb9ec5d69915764265ad68158dbb6e1',
              640:'13ec851eb00ca9aba345cad50f03bdb3b189f566f38d094a1e6b839765b3d678'}
    refs=list(pitch_sequences)
    for id,path,track in ((580,a.brahms,1),(640,a.adam,2)):
        if digest(path)!=expected[id]:raise ValueError('observed reference hash mismatch')
        m=read_midi(path,track);refs.append([n.pitch for n in m.notes])
    before=dict(plan_sha256=digest(a.output/'plan.json'),training_events=sum(map(len,sequences)),train_sha256=hashes,
                observed_copy_reference_sha256=expected)
    (a.output/'before-generation.json').write_text(json.dumps(before,indent=2)+'\n')
    forbidden=set().union(*(phrases(r) for r in refs));models=make_models(sequences,pitch_sequences)
    rows={name:[] for name in models}
    for seed in range(10):
        for name in (('timing0','timing1') if seed%2==0 else ('timing1','timing0')):
            wall=time.perf_counter();cpu=time.process_time()
            generated=generate_optimized(models[name],seed,uniform_mix=Fraction(1,4),trailing_rest_ticks=384)
            timing=dict(wall_seconds=time.perf_counter()-wall,cpu_seconds=time.process_time()-cpu)
            ns=generated['notes'];row={k:v for k,v in generated.items() if k!='notes'}
            row.update(seed=seed,metrics=descriptors(ns),generation_timing=timing)
            if generated['status']=='complete':
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
                    if read_midi(path,1)!=melody:raise ValueError('MIDIroundtrip failure')
                    row.update(midi_sha256=digest(path),exact_roundtrip=True)
            rows[name].append(row)
    conditions={}
    for name,outputs in rows.items():
        means,denominators=summarize(outputs)
        conditions[name]=dict(outputs=outputs,statuses=dict(Counter(r['status'] for r in outputs)),
            rejections=sum(r['rejections'] for r in outputs),timing_draws=sum(r['timing_draws'] for r in outputs),
            generation_timing={k:sum(r['generation_timing'][k] for r in outputs) for k in ('wall_seconds','cpu_seconds')},
            complete_only_means=means,metric_denominators=denominators)
    common=sorted(set.intersection(*(set(r['seed'] for r in outputs if r['status']=='complete') for outputs in rows.values())))
    paired={}
    for name,outputs in rows.items():
        means,denominators=summarize([r for r in outputs if r['seed'] in common]);paired[name]=dict(means=means,metric_denominators=denominators)
    report=dict(plan=plan,before_generation=before,conditions=conditions,common_accepted_seed_analysis=dict(seeds=common,conditions=paired),
        originals_unchanged=digest(a.brahms)==expected[580] and digest(a.adam)==expected[640],
        limitations=['No new predictive scores; allheldout references here alreadyobserved.',
            'Descriptors are structural,not appeal; onsetorder notvoiceleading.',
            'Tiny deterministic sample, no significance or broadgeneralization inference.',
            'Wall/CPU measuredlocally; cache/pairedexecution effects remain.',
            'Copyguard is narrow, not perceptual/legalclearance.'])
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({n:{k:c[k] for k in ('statuses','generation_timing','complete_only_means')} for n,c in conditions.items()},indent=2))


if __name__=='__main__':main()

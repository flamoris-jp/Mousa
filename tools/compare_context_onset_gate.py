"""Predeclared exploratory factorial reanalysis, never a fresh580 benchmark."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from statistics import mean
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.overlap_midi import read_midi, write_midi, OverlapMelody
from mousa.tick_midi import TickNote
from mousa.research_intake import validate_manifest
from compare_onset_gate_models import pairs, phrases, similarity


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def metrics(notes,target):
    """Intervals follow generated event order, not an inferred polyphonic voice."""
    pitches=[n['pitch'] for n in notes];iv=[abs(b-a) for a,b in zip(pitches,pitches[1:])]
    changes=Counter()
    for n in notes:changes[n['start']]+=1;changes[n['end']]-=1
    previous=0;active=0;occupied=0;voice_ticks=0;maximum=0
    for tick,delta in sorted(changes.items()):
        span=tick-previous
        occupied+=span*bool(active);voice_ticks+=span*active
        active+=delta;maximum=max(maximum,active);previous=tick
    overlaps=sum(any(p['end']>n['start'] for p in notes[:i]) for i,n in enumerate(notes))
    return dict(notes=len(notes),overlap_onset_fraction=overlaps/len(notes) if notes else None,
        mean_active_voices=voice_ticks/target,max_active_voices=maximum,
        mean_abs_pitch_interval=mean(iv) if iv else None,
        above_octave_fraction=sum(v>12 for v in iv)/len(iv) if iv else None,
        distinct_pitches=len(set(pitches)),repeated_pitch_fraction=iv.count(0)/len(iv) if iv else None,
        rest_ticks=target-occupied,rest_fraction=(target-occupied)/target)


def summarize(rows):
    """Complete-only metric means with explicit missing-value denominators."""
    complete=[r for r in rows if r['status']=='complete']
    if not complete:return {},{}
    means={};denominators={}
    for key in complete[0]['metrics']:
        values=[r['metrics'][key] for r in complete if r['metrics'][key] is not None]
        means[key]=mean(values) if values else None
        denominators[key]=len(values)
    return means,denominators


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('corpus','source','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();root=Path(__file__).resolve().parents[1]
    if a.output.exists():raise ValueError('new output directory required')
    tracked=['src/mousa/context_onset_gate.py','src/mousa/onset_gate_model.py','src/mousa/overlap_midi.py',
             'tools/compare_context_onset_gate.py','tools/compare_onset_gate_models.py',
             'datasets/research-exploratory-multifamily-20261112.json','datasets/research-brahms580-rights-20261112.json']
    frozen=json.loads((root/'experiments/2026-11-12-frozen-transfer-plan.json').read_text())
    for path,sha in frozen['sha256'].items():
        if digest(root/path)!=sha:raise ValueError('frozen input changed')
    cycle12=json.loads((root/'experiments/2026-11-12-onset-gate-results.json').read_text())
    if digest(root/'src/mousa/onset_gate_model.py')!=cycle12['before_scoring']['model_sha256']:
        raise ValueError('cycle12 model changed')
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),scope='Cycle13 exploratory reanalysis of observed580, not fresh evaluation',
        train_ids=['mutopia-376','mutopia-888','mutopia-889','mutopia-789'],diagnostic_id=580,reserved_never_loaded=[583],
        timing='previous-gate context counts for nextdelta, per-work reset; w=n/(n+4), raw counts w*local+(1-w)*global then uniform prior1',
        gate='unchanged global marginal with uniform prior1',support='delta0..12288,gate1..12288,PPQ384',
        pitch='control uniform same training vocabulary; continuity train unigram first, then train interval counts with total uniform prior1 renormalized on vocabulary',
        factorial=['timing0_pitch0','timing0_pitch1','timing1_pitch0','timing1_pitch1'],seeds=list(range(10)),
        target_ticks=9216,max_polyphony=3,max_notes=256,max_attempts=64,
        source_screen='exact8interval match or wholeinterval similarity>=0.80 blocks; conservative actualcycle12 threshold, not its original0.90 plan',
        output_copy_guard='training sources plus observed580; no retry aftercopy rejection',
        metrics=['overlap_onset_fraction','mean/max_active_voices','mean_abs_pitch_interval','above_octave_fraction',
                 'distinct_pitches','repeated_pitch_fraction','notes','rest_ticks/fraction','statuses','rejections','580timingNLL'],
        aggregation='means over complete accepted outputs only WITH denominators; partial output metrics separately retained',
        interpretation='pitch order is generated event order, not recovered voices; no attractiveness or generalization claim',
        baseline='new factorial baseline uses rng.choices uniform pitch; not same seed sequences as cycle12 rng.choice',
        resource='bounded CPU only; no selection or tuning after results',code_sha256={n:digest(root/n) for n in tracked})
    a.output.mkdir(parents=True);(a.output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    manifest=json.loads((root/'datasets/research-exploratory-multifamily-20261112.json').read_text())
    validate_manifest(manifest,a.corpus)
    sequences=[];pitch_sequences=[];source_hashes={};sources={}
    for work in manifest['works']:
        if work['work_id'] not in plan['train_ids']:continue
        m=read_midi(a.corpus/work['file'],work['track_index']);sequences.append(pairs(m))
        pitch_sequences.append([n.pitch for n in m.notes]);sources[work['work_id']]=pitch_sequences[-1]
        source_hashes[work['work_id']]=digest(a.corpus/work['file'])
    if len(sources)!=4:raise ValueError('missing training works')
    expected='dcd5efac22b5e91b7c87685058784396adb9ec5d69915764265ad68158dbb6e1'
    if digest(a.source)!=expected:raise ValueError('580 hash mismatch')
    rights=json.loads((root/'datasets/research-brahms580-rights-20261112.json').read_text())
    if rights['encoding_rights']['status']!='PD-dedication-supported':raise ValueError('rights review absent')
    test=read_midi(a.source,1);test_pairs=pairs(test);test_pitches=[n.pitch for n in test.notes]
    screens=[]
    for name,ps in sources.items():
        matches=len(phrases(ps)&phrases(test_pitches));near=similarity(ps,test_pitches)
        screens.append(dict(source=name,matches=matches,whole_interval_similarity=near))
        if matches or (near is not None and near>=.80):raise ValueError('source screen requires review')
    before=dict(plan_sha256=digest(a.output/'plan.json'),source_sha256=source_hashes,test_sha256=expected,
                training_events=sum(map(len,sequences)),test_events=len(test_pairs),screens=screens)
    (a.output/'before-scoring.json').write_text(json.dumps(before,indent=2)+'\n')
    forbidden=set().union(*(phrases(ps) for ps in list(sources.values())+[test_pitches]))
    conditions={}
    for timing in (False,True):
        for pitch in (False,True):
            name=f'timing{int(timing)}_pitch{int(pitch)}'
            model=ContextOnsetGateModel(sequences,pitch_sequences,timing_context=timing,pitch_continuity=pitch,strength=4)
            evaluation=model.evaluate(test_pairs);rows=[]
            for seed in range(10):
                result=model.generate(seed,target_ticks=9216);ns=result['notes']
                row={k:v for k,v in result.items() if k!='notes'}
                row.update(seed=seed,metrics=metrics(ns,9216))
                if result['status']=='complete':
                    # Screen canonical source order AND actual generated order.
                    notes=tuple(sorted((TickNote(n['start'],n['end'],n['pitch'],80,0) for n in ns),key=lambda n:(n.start,n.end,n.pitch)))
                    matches=(phrases([n['pitch'] for n in ns])|phrases([n.pitch for n in notes]))&forbidden
                    row['source_copy_matches']=len(matches)
                    if matches:row['status']='copy_guard_blocked'
                    else:
                        events=[]
                        for i,n in enumerate(ns):
                            events.extend(((n['start'],1,i,'note_on',n['pitch'],80),(n['end'],0,i,'note_off',n['pitch'],0)))
                        stream=((0,'program',0,0),)+tuple((t,k,p,v) for t,_,i,k,p,v in sorted(events))
                        melody=OverlapMelody(notes,9216,(6,8),ppq=384,channel_events=stream)
                        path=a.output/f'{name}-{seed}.mid';write_midi(melody,path)
                        if read_midi(path,1)!=melody:raise ValueError('MIDI roundtrip mismatch')
                        row.update(midi_sha256=digest(path),exact_roundtrip=True)
                rows.append(row)
            complete=[r for r in rows if r['status']=='complete']
            summary,denominators=summarize(rows)
            conditions[name]=dict(diagnostic=evaluation,outputs=rows,complete_count=len(complete),
                statuses=dict(Counter(r['status'] for r in rows)),total_rejections=sum(r['rejections'] for r in rows),
                complete_only_means=summary,metric_denominators=denominators)
    common_seeds=sorted(set.intersection(*(set(r['seed'] for r in c['outputs'] if r['status']=='complete')
                                          for c in conditions.values())))
    common_summary={}
    for name,condition in conditions.items():
        means,denominators=summarize([r for r in condition['outputs'] if r['seed'] in common_seeds])
        common_summary[name]=dict(means=means,metric_denominators=denominators)
    report=dict(plan=plan,before_scoring=before,conditions=conditions,
        common_accepted_seed_analysis=dict(seeds=common_seeds,conditions=common_summary,
            scope='Post-result reporting-only paired subset, still conditional on all four treatments succeeding; not independent evaluation'),
        original_unchanged=digest(a.source)==expected,
        limitations=['580 already predictive-observed; no fresh generalization claim.',
            'Training pitch intervals are onset-order transitions, not voice-leading/harmony.',
            'Conditioned generation distribution differs from unconditional diagnostic NLL.',
            'Output copying screen includes observed580, not model fitting.',
            'No human listening labels; structural proxies do not establish appeal.',
            'Completed-only means can be biased by failures; all partial metrics/statuses retained.'])
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:{'nll':v['diagnostic']['nll_per_event'],'statuses':v['statuses'],'means':v['complete_only_means']} for k,v in conditions.items()},indent=2))


if __name__=='__main__':main()

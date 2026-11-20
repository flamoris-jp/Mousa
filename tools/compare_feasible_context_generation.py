"""Predeclared joint-feasibility and uniform-pitch-mixture factorial experiment."""
import argparse
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction
import json
import time
from pathlib import Path
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.feasible_context_generation import generate_feasible
from mousa.overlap_midi import read_midi,write_midi,OverlapMelody
from mousa.tick_midi import TickNote
from mousa.research_intake import validate_manifest
from compare_context_onset_gate import metrics,summarize,digest
from compare_onset_gate_models import pairs,phrases,similarity


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('corpus','source','output'):parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args();root=Path(__file__).resolve().parents[1]
    if args.output.exists():raise ValueError('new output directory required')
    frozen=json.loads((root/'experiments/2026-11-12-frozen-transfer-plan.json').read_text())
    for path,sha in frozen['sha256'].items():
        if digest(root/path)!=sha:raise ValueError('old frozen dependency changed')
    tracked=['src/mousa/feasible_context_generation.py','src/mousa/context_onset_gate.py','src/mousa/onset_gate_model.py',
        'src/mousa/overlap_midi.py','tools/compare_feasible_context_generation.py','tools/compare_context_onset_gate.py',
        'tools/compare_onset_gate_models.py','datasets/research-exploratory-multifamily-20261112.json',
        'datasets/research-brahms580-rights-20261112.json']
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),scope='Cycle14 exploratory generation only,580 already observed and583 reserved',
        train_ids=['mutopia-376','mutopia-888','mutopia-889','mutopia-789'],never_load=[583],
        model='Frozen cycle13 timing_context=True,pitch_continuity=True,strength4',
        factorial='exact_joint_feasibility off/on x whole-vocabulary uniform_probability_mixture alpha0/0.25',
        feasibility='delta mass times conditional gate mass times total legal pitch weight; polyphony3 delta mass0; sampledelta then gate then legalpitch',
        distribution='Same next-accepted-event law as joint rejection at fixed alpha/state, NOT same RNG path or finite64retryfailurelaw. Pitch-only mask rejected before experiment.',
        pitch_mixture='(1-alpha)*normalized continuity distribution+alpha/|trainvocabulary| BEFORE feasible conditioning',
        constraints=dict(target_ticks=9216,max_notes=256,max_attempts=64,max_polyphony=3,seeds=list(range(10))),
        completion='exact gate end at target; no clipping, implicit timeadvance, fallback or winner selection',
        copy_guard='train plus580 exact8onset pitchintervals, both canonical and generatedorder; no retry on guardfailure',
        baseline='maskoff alpha0 must exactly reproduce original context generator notes/status/rejections perseed',
        metrics=['completion/block/copyguard status','rejectionreason','lastacceptedstate andlastproposal',
            'timingdraws,pitchdraws','repeat/unique/leap descriptors','overlap/restcoverage','exactMIDIroundtrip'],
        aggregation='all10 statuses; complete-only means with denominators; commonacceptedseed subset remains success-conditioned',
        post_initial_reporting_extension='Added after initial results: gates<24tick and onsets>=8832tick diagnostics, arbitrary thresholds not tuned; generationwallseconds excludes MIDI/export/paritycheck',
        nonclaims=['musical appeal','fresh evaluation','same finite-failure distribution','neural efficiency or training gain'],
        source_screen='exact8interval or wholeinterval similarity>=0.80 blocks aspreviousactualscreen',
        code_sha256={p:digest(root/p) for p in tracked})
    args.output.mkdir(parents=True);(args.output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    manifest=json.loads((root/'datasets/research-exploratory-multifamily-20261112.json').read_text());validate_manifest(manifest,args.corpus)
    seqs=[];pss=[];source_hashes={}
    for work in manifest['works']:
        if work['work_id'] not in plan['train_ids']:continue
        melody=read_midi(args.corpus/work['file'],work['track_index'])
        seqs.append(pairs(melody));pss.append([n.pitch for n in melody.notes]);source_hashes[work['work_id']]=digest(args.corpus/work['file'])
    if len(seqs)!=4:raise ValueError('missing training works')
    expected='dcd5efac22b5e91b7c87685058784396adb9ec5d69915764265ad68158dbb6e1'
    if digest(args.source)!=expected:raise ValueError('580 hash mismatch')
    rights=json.loads((root/'datasets/research-brahms580-rights-20261112.json').read_text())
    if rights['encoding_rights']['status']!='PD-dedication-supported':raise ValueError('source rights evidence absent')
    test=read_midi(args.source,1);testp=[n.pitch for n in test.notes];screens=[]
    for pitches in pss:
        match=len(phrases(pitches)&phrases(testp));near=similarity(pitches,testp)
        screens.append(dict(matches=match,similarity=near))
        if match or (near is not None and near>=.80):raise ValueError('source screen blocks')
    before=dict(plan_sha256=digest(args.output/'plan.json'),train_hashes=source_hashes,test_sha256=expected,
                training_events=sum(map(len,seqs)),screens=screens)
    (args.output/'before-generation.json').write_text(json.dumps(before,indent=2)+'\n')
    forbidden=set().union(*(phrases(ps) for ps in pss+[testp]))
    model=ContextOnsetGateModel(seqs,pss,timing_context=True,pitch_continuity=True,strength=4)
    conditions={}
    for mask in (False,True):
        for mix in (Fraction(0),Fraction(1,4)):
            name=f'feasible{int(mask)}_mix{int(bool(mix))}';rows=[]
            for seed in range(10):
                started=time.perf_counter()
                result=generate_feasible(model,seed,feasible_mask=mask,uniform_mix=mix)
                generation_seconds=time.perf_counter()-started
                if not mask and mix==0:
                    original=model.generate(seed)
                    if any(result[k]!=v for k,v in original.items()):raise ValueError('baseline parity failed')
                ns=result['notes'];row={k:v for k,v in result.items() if k!='notes'}
                row.update(seed=seed,metrics=metrics(ns,9216),generation_seconds=generation_seconds,
                    artifact_diagnostics=dict(short_gate_count=sum(n['end']-n['start']<24 for n in ns),
                        last_quarter_onset_count=sum(n['start']>=8832 for n in ns),
                        last_quarter_short_gate_count=sum(n['start']>=8832 and n['end']-n['start']<24 for n in ns),
                        thresholds='post-initial diagnostic: gate<24ticks; onset>=target-384ticks, not quality labels'))
                if result['status']=='complete':
                    notes=tuple(sorted((TickNote(n['start'],n['end'],n['pitch'],80,0) for n in ns),key=lambda n:(n.start,n.end,n.pitch)))
                    matches=(phrases([n['pitch'] for n in ns])|phrases([n.pitch for n in notes]))&forbidden
                    row['source_copy_matches']=len(matches)
                    if matches:row['status']='copy_guard_blocked'
                    else:
                        events=[]
                        for i,n in enumerate(ns):events.extend(((n['start'],1,i,'note_on',n['pitch'],80),(n['end'],0,i,'note_off',n['pitch'],0)))
                        stream=((0,'program',0,0),)+tuple((t,k,p,v) for t,_,i,k,p,v in sorted(events))
                        melody=OverlapMelody(notes,9216,(6,8),ppq=384,channel_events=stream)
                        path=args.output/f'{name}-{seed}.mid';write_midi(melody,path)
                        if read_midi(path,1)!=melody:raise ValueError('MIDI roundtrip failed')
                        row.update(midi_sha256=digest(path),exact_roundtrip=True)
                rows.append(row)
            means,denominators=summarize(rows)
            conditions[name]=dict(outputs=rows,statuses=dict(Counter(r['status'] for r in rows)),
                total_rejections=sum(r['rejections'] for r in rows),generation_seconds=sum(r['generation_seconds'] for r in rows),
                rejection_reasons={k:sum(r['rejection_reasons'][k] for r in rows) for k in ('active_pitch','polyphony','no_legal_pitch')},
                timing_draws=sum(r['timing_draws'] for r in rows),pitch_draws=sum(r['pitch_draws'] for r in rows),
                complete_only_means=means,metric_denominators=denominators)
    seeds=sorted(set.intersection(*(set(r['seed'] for r in c['outputs'] if r['status']=='complete') for c in conditions.values())))
    common={}
    for name,c in conditions.items():
        means,denominators=summarize([r for r in c['outputs'] if r['seed'] in seeds]);common[name]=dict(means=means,metric_denominators=denominators)
    report=dict(plan=plan,before_generation=before,conditions=conditions,common_accepted_seed_analysis=dict(seeds=seeds,conditions=common),
        original_unchanged=digest(args.source)==expected,
        limitations=['No new predictive scoring or source fitting;580used only copy/source screen.',
            'Joint conditioning preserves acceptednext-event law but removes finite retry failure;notseedidentity.',
            'Uniformmix changes pitchdistribution beforeconditioning; no promise of better music.',
            'Drawcounts measure proposal overhead, not wallclock: exactconditioning computes bounded delta masses.',
            'Completed-only andcommonseed summaries remain success-conditioned; allfailures retained.',
            'Polyphonic onset-order pitchintervals are not voice-leading measurements.'])
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({n:{k:v[k] for k in ('statuses','total_rejections','rejection_reasons','timing_draws','pitch_draws','complete_only_means')} for n,v in conditions.items()},indent=2))


if __name__=='__main__':main()

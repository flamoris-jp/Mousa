"""Equivalent sampler benchmark and separately declared trailing-rest experiment."""
import argparse
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction
import json
import time
from pathlib import Path
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.feasible_context_generation import generate_feasible
from mousa.optimized_feasible_generation import generate_optimized
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
    tracked=['src/mousa/optimized_feasible_generation.py','src/mousa/feasible_context_generation.py','src/mousa/context_onset_gate.py','src/mousa/onset_gate_model.py',
        'src/mousa/overlap_midi.py','tools/compare_optimized_endpoint.py','tools/compare_context_onset_gate.py',
        'tools/compare_onset_gate_models.py','datasets/research-exploratory-multifamily-20261112.json',
        'datasets/research-brahms580-rights-20261112.json']
    previous_report=json.loads((root/'experiments/2026-11-12-feasible-generation-results.json').read_text())
    for path in ('src/mousa/feasible_context_generation.py','src/mousa/context_onset_gate.py'):
        if digest(root/path)!=previous_report['plan']['code_sha256'][path]:raise ValueError('frozen generator changed')
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),scope='Cycle15 exact sampler optimization and bounded trailing-rest policy',
        train_ids=['mutopia-376','mutopia-888','mutopia-889','mutopia-789'],never_load=[583],
        model='Frozen cycle13 timing_context=True,pitch_continuity=True,strength4',
        optimization='legal pitch total minus occupied dictionary weights, cached between release ticks; same integer masses and RNG order',
        benchmark='exact-end20paired generations: alpha0/.25,seeds0..9; alternate original-first/optimized-first byseedparity; CPUandwall measured generationonly, paritychecked',
        endpoint_policy='After eachacceptednote stop if maxexistingend>=target-384; EOTremains9216. Noemptyoutput or modifiedgate. Separate changedstoprule, NOTdistribution-equivalent toexactend.',
        factorial='exact-end versus trailingrest<=384 x uniformprobabilitymix alpha0/0.25',
        constraints=dict(target_ticks=9216,max_notes=256,max_attempts=64,max_polyphony=3,seeds=list(range(10))),
        copy_guard='train plus580 exact8onset pitchintervals, canonical andgeneratedorders, no retries',
        source_screen='exact8interval or wholeinterval similarity>=0.80 blocks',
        metrics=['statuses/rejections','drawcounts','pairedCPU/wall','gates<24tick','onsets>=target-384',
                 'actualsilenttail','notes','repeat/unique/leap/overlap/rest descriptors','MIDIroundtrip'],
        diagnostic_thresholds='24ticks is arbitrary1/16quarter; tail384 is1quarter, not learnedcadence',
        aggregation='completeonly means withdenominators pluscommonacceptedseed subset; keepallfailedstates',
        nonclaims=['musicalquality','fresh580evaluation','learnedcadence','tailpolicy distributionequivalence'],
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
    for tail in (0,384):
        for mix in (Fraction(0),Fraction(1,4)):
            name=f'tail{tail}_mix{int(bool(mix))}';rows=[]
            for seed in range(10):
                benchmarks={}
                def run_timed(label,call):
                    wall=time.perf_counter();cpu=time.process_time();value=call()
                    benchmarks[label]=dict(wall_seconds=time.perf_counter()-wall,cpu_seconds=time.process_time()-cpu)
                    return value
                if tail==0:
                    calls={'original':lambda:generate_feasible(model,seed,feasible_mask=True,uniform_mix=mix),
                           'optimized':lambda:generate_optimized(model,seed,uniform_mix=mix)}
                    results={}
                    for label in (('original','optimized') if seed%2==0 else ('optimized','original')):
                        results[label]=run_timed(label,calls[label])
                    result=results['optimized']
                    if any(result[k]!=v for k,v in results['original'].items()):raise ValueError('exact sampler parity failed')
                else:
                    result=run_timed('optimized',lambda:generate_optimized(model,seed,uniform_mix=mix,trailing_rest_ticks=tail))
                generation_seconds=benchmarks['optimized']['wall_seconds']
                ns=result['notes'];row={k:v for k,v in result.items() if k!='notes'}
                row.update(seed=seed,metrics=metrics(ns,9216),generation_seconds=generation_seconds,benchmarks=benchmarks,
                    artifact_diagnostics=dict(short_gate_count=sum(n['end']-n['start']<24 for n in ns),
                        last_quarter_onset_count=sum(n['start']>=8832 for n in ns),
                        last_quarter_short_gate_count=sum(n['start']>=8832 and n['end']-n['start']<24 for n in ns),
                        thresholds='predeclared gate<24ticks; onset>=target-384ticks, not quality labels'))
                row['metrics'].update(short_gate_count=row['artifact_diagnostics']['short_gate_count'],
                    last_quarter_onset_count=row['artifact_diagnostics']['last_quarter_onset_count'],
                    last_quarter_short_gate_count=row['artifact_diagnostics']['last_quarter_short_gate_count'],
                    actual_silent_tail_ticks=9216-max(n['end'] for n in ns) if ns else None)
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
            benchmark_totals={label:{metric:sum(r['benchmarks'][label][metric] for r in rows) for metric in ('wall_seconds','cpu_seconds')}
                              for label in (('original','optimized') if tail==0 else ('optimized',))}
            conditions[name]=dict(outputs=rows,benchmark_totals=benchmark_totals,statuses=dict(Counter(r['status'] for r in rows)),
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
        limitations=['No source fitting changes;580copy/screen only and583neverloaded.',
            'Sameinteger masses andRNG verified only for unchanged exact-end policy.',
            'Trailingrest changes stopping andmay remove phrases; no learnedcadence or appealclaim.',
            'Wall/CPU timings are small localpaired measurements, not infrastructure benchmarks.',
            'Completed/commonseed summaries are success-conditioned; failures retained.',
            'Pitch descriptors followpolyphonic onsetorder, not inferredvoices.'])
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({n:{k:v[k] for k in ('statuses','total_rejections','rejection_reasons','timing_draws','pitch_draws','complete_only_means')} for n,v in conditions.items()},indent=2))


if __name__=='__main__':main()

"""Exploratory exact-tick recurrence analysis of the already observed20 outputs.

No quantization, new samples, selection, source training or quality labels.
Onsets belong to their starting bar; sounding gates are never clipped at bars.
Polyphonic event-order pitch sequences are not recovered melodic voices.
"""
import argparse
from collections import Counter
from datetime import datetime,timezone
import json
from math import sqrt
from pathlib import Path
from statistics import mean,pstdev
from mousa.overlap_midi import read_midi
from compare_context_onset_gate import digest


BAR_TICKS=1152
TOTAL_TICKS=9216


def edit_similarity(left,right):
    if not left or not right:return None
    if len(left)>256 or len(right)>256:raise ValueError('sequence bound')
    row=list(range(len(right)+1))
    for i,a in enumerate(left,1):
        new=[i]
        for j,b in enumerate(right,1):new.append(min(new[-1]+1,row[j]+1,row[j-1]+(a!=b)))
        row=new
    return 1-row[-1]/max(len(left),len(right))


def analyze_notes(notes):
    """Notes must follow source note-on order, not note-off order."""
    if not isinstance(notes,(list,tuple)) or len(notes)>256:raise ValueError('bounded notes required')
    bars=[[] for _ in range(8)];previous=-1
    for note in notes:
        if type(note) is not dict or set(note)!={'start','end','pitch'}:raise ValueError('exact note fields required')
        start,end,pitch=note['start'],note['end'],note['pitch']
        if any(type(v) is not int for v in (start,end,pitch)) or not 0<=start<end<=TOTAL_TICKS or start<previous or not 0<=pitch<=127:
            raise ValueError('invalid source-ordered notes')
        bars[start//BAR_TICKS].append((start%BAR_TICKS,end-start,pitch));previous=start
    signatures=[]
    for bar in bars:
        signatures.append(dict(rhythm=tuple((offset,gate) for offset,gate,pitch in bar),
            relative_pitch=tuple(pitch-bar[0][2] for _,_,pitch in bar) if bar else (),
            full=tuple((offset,gate,pitch-bar[0][2]) for offset,gate,pitch in bar) if bar else ()))
    comparisons=[]
    for i in range(8):
        for j in range(i+1,8):
            if not bars[i] or not bars[j]:continue
            a,b=signatures[i],signatures[j]
            comparisons.append(dict(first_bar=i+1,second_bar=j+1,adjacent=j==i+1,
                rhythm_exact=a['rhythm']==b['rhythm'],relative_pitch_exact=a['relative_pitch']==b['relative_pitch'],
                transposition_invariant_full_exact=a['full']==b['full'],
                relative_pitch_edit_similarity=edit_similarity(a['relative_pitch'],b['relative_pitch'])))
    def summarize(rows):
        n=len(rows)
        return dict(eligible_pairs=n,
            rhythm_exact_count=sum(r['rhythm_exact'] for r in rows),
            full_exact_count=sum(r['transposition_invariant_full_exact'] for r in rows),
            relative_pitch_exact_count=sum(r['relative_pitch_exact'] for r in rows),
            rhythm_exact_rate=sum(r['rhythm_exact'] for r in rows)/n if n else None,
            full_exact_rate=sum(r['transposition_invariant_full_exact'] for r in rows)/n if n else None,
            mean_relative_pitch_edit_similarity=mean(r['relative_pitch_edit_similarity'] for r in rows) if n else None)
    pitches=[n['pitch'] for n in notes];adjacent_intervals=[b-a for a,b in zip(pitches,pitches[1:])]
    counts=[len(bar) for bar in bars];density=mean(counts)
    return dict(bar_onset_counts=counts,nonempty_bars=sum(bool(bar) for bar in bars),empty_bars=sum(not bar for bar in bars),
        single_onset_bars=sum(len(bar)==1 for bar in bars),
        onset_count_cv=pstdev(counts)/density if density else None,
        adjacent_same_pitch_fraction=adjacent_intervals.count(0)/len(adjacent_intervals) if adjacent_intervals else None,
        adjacent_pitch_pairs=len(adjacent_intervals),all_nonempty_pairs=summarize(comparisons),
        nonadjacent_nonempty_pairs=summarize([r for r in comparisons if not r['adjacent']]),bar_pairs=comparisons,
        cross_bar_sounding_gates=sum(n['end']>(n['start']//BAR_TICKS+1)*BAR_TICKS for n in notes))


def source_order_notes(melody):
    by_onset={(n.start,n.pitch):n for n in melody.notes}
    result=[]
    for tick,kind,pitch,velocity in melody.channel_events:
        if kind=='note_on':
            note=by_onset[(tick,pitch)];result.append(dict(start=note.start,end=note.end,pitch=pitch))
    if len(result)!=len(melody.notes):raise ValueError('source-order note reconstruction failed')
    return result


def correlation(pairs):
    """Descriptive Pearson only; no significance/causality/generalization claim."""
    pairs=[(a,b) for a,b in pairs if a is not None and b is not None]
    if len(pairs)<2:return dict(n=len(pairs),r=None)
    xs,ys=zip(*pairs);mx,my=mean(xs),mean(ys)
    xx=sum((x-mx)**2 for x in xs);yy=sum((y-my)**2 for y in ys)
    return dict(n=len(pairs),r=sum((x-mx)*(y-my) for x,y in pairs)/sqrt(xx*yy) if xx and yy else None)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pool',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();root=Path(__file__).resolve().parents[1]
    if args.output.exists():raise ValueError('new output directory required')
    report_path=args.pool/'report.json';source=json.loads(report_path.read_text())
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),scope='Cycle19 exploratory reanalysis of cycle18same20outputs; not new independent samples',
        hypothesis='Bar-scale recurrence/variation can carry information distinct from adjacent same-pitch rate; timingcontext may change those descriptors without guaranteeing appeal.',
        bar_partition='8bars6/8,PPQ384,1152ticks/bar,9216tick total. Assign by onset; keep actual gate acrossboundaries without clipping.',
        metrics='For eachnonemptybarpair: exact rhythm(offset,gate), exact relativepitch sequence(p-firstpitch), exact full(offset,gate,p-firstpitch), normalized Levenshtein relativepitch similarity; also onsetcountCV acrossall8bars.',
        denominators='Exclude anypair with anemptybar; report countandrate, nonadjacentpairs separately. Empty/single-onset bars explicitly counted. No empty-empty recurrence.',
        note_order='Original modeledchannel note-on order, notnote-off order. Simultaneous pitches/overlap are not voice-disambiguated.',
        analysis='Per-output values, equal-output condition means with denominators, pairedseed differences, exploratory Pearson with adjacent samepitch. No statistical significance or outcome selection.',
        no_generation=True,no_model_fitting=True,no_predictive_evaluation=True,
        limitations=['Exacttick equality is sensitive tosmallrhythmchanges; no quantization/tolerance.',
            'Relativepitch removesglobaltransposition, not harmonic/function/key differences.',
            'Singleonset bars trivially share relativepitch0; counts disclose this.',
            'Bar boundaries assume generated6/8start atzero, not inferred phrase boundaries.',
            'Pitchsequence edit similarity ignoresrhythm; report alongside strictrhythm/fullmetrics.',
            'No human appeal labels; recurrence can be appealing or monotonous dependingcontext.'],
        source_report_sha256=digest(report_path),code_sha256={p:digest(root/p) for p in
            ('tools/analyze_bar_recurrence.py','src/mousa/overlap_midi.py','tools/compare_context_onset_gate.py')})
    args.output.mkdir(parents=True);(args.output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    conditions={};allrows=[]
    for name,condition in source['conditions'].items():
        rows=[]
        for output in condition['outputs']:
            if output['status']!='complete':raise ValueError('poolmembership changed; expected20complete')
            path=args.pool/f'{name}-{output["seed"]}.mid'
            if digest(path)!=output['midi_sha256']:raise ValueError('observedartifact hash differs')
            melody=read_midi(path,1)
            if melody.ppq!=384 or melody.total_ticks!=TOTAL_TICKS or len(melody.meter_map)!=1 or melody.meter!=(6,8):
                raise ValueError('poolmeter/clock mismatch, no conversion')
            result=analyze_notes(source_order_notes(melody));rows.append(dict(seed=output['seed'],midi_sha256=output['midi_sha256'],analysis=result));allrows.append(result)
        descriptors={}
        for key,fn in {
            'adjacent_same_pitch_fraction':lambda x:x['adjacent_same_pitch_fraction'],
            'onset_count_cv':lambda x:x['onset_count_cv'],
            'nonadjacent_rhythm_exact_rate':lambda x:x['nonadjacent_nonempty_pairs']['rhythm_exact_rate'],
            'nonadjacent_full_exact_rate':lambda x:x['nonadjacent_nonempty_pairs']['full_exact_rate'],
            'nonadjacent_relative_pitch_similarity':lambda x:x['nonadjacent_nonempty_pairs']['mean_relative_pitch_edit_similarity']}.items():
            values=[fn(r['analysis']) for r in rows];values=[v for v in values if v is not None]
            descriptors[key]=dict(mean=mean(values) if values else None,n=len(values))
        conditions[name]=dict(outputs=rows,equal_output_means=descriptors)
    if set(conditions)!={'timing0','timing1'} or any(len(v['outputs'])!=10 for v in conditions.values()):raise ValueError('expectedpaired20pool')
    paired=[]
    for seed in range(10):
        a=next(r['analysis'] for r in conditions['timing0']['outputs'] if r['seed']==seed)
        b=next(r['analysis'] for r in conditions['timing1']['outputs'] if r['seed']==seed)
        paired.append(dict(seed=seed,delta_samepitch=b['adjacent_same_pitch_fraction']-a['adjacent_same_pitch_fraction'],
            delta_onset_count_cv=b['onset_count_cv']-a['onset_count_cv'],
            delta_nonadjacent_relative_pitch_similarity=(b['nonadjacent_nonempty_pairs']['mean_relative_pitch_edit_similarity']-a['nonadjacent_nonempty_pairs']['mean_relative_pitch_edit_similarity'])
                if b['nonadjacent_nonempty_pairs']['mean_relative_pitch_edit_similarity'] is not None and a['nonadjacent_nonempty_pairs']['mean_relative_pitch_edit_similarity'] is not None else None))
    result=dict(plan=plan,conditions=conditions,paired_seed_differences=paired,
        pooled_descriptive_correlation=dict(
            samepitch_vs_nonadjacent_pitch_similarity=correlation([(r['adjacent_same_pitch_fraction'],r['nonadjacent_nonempty_pairs']['mean_relative_pitch_edit_similarity']) for r in allrows]),
            samepitch_vs_onset_count_cv=correlation([(r['adjacent_same_pitch_fraction'],r['onset_count_cv']) for r in allrows])),
        source_report_unchanged=digest(report_path)==plan['source_report_sha256'],
        caution='Pooled20alreadyobserved outputs mix two conditions; correlation is descriptive only,not independent observations or causal evidence.')
    (args.output/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v['equal_output_means'] for k,v in conditions.items()},indent=2))


if __name__=='__main__':main()

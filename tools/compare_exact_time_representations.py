"""Lossless timing representation diagnostics, no fitting or melody scoring."""
import argparse
from dataclasses import replace
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import time
from mousa.tick_midi import read_midi,inspect_grid_error
from mousa.rational_events import to_events,events_to_notes,to_json_data,from_json_data


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root',type=Path,required=True);p.add_argument('--rights-review',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('new output required')
    rights=json.loads(a.rights_review.read_text());rows=[]
    # Named, separately rights-reviewed Schubert sources. No pending1040.
    chosen=[1578,1585,1587];a.output.mkdir(parents=True)
    for id in chosen:
        w=next(r for r in rights if r['id']==id);path=a.source_root/f'{id}.mid'
        original=hashlib.sha256(path.read_bytes()).hexdigest()
        if original!=w['files']['mid']['sha256']:raise ValueError('source hash mismatch')
        melody=read_midi(path,1);start=time.perf_counter();events=to_events(melody)
        serialized=to_json_data(events);returned=from_json_data(serialized)
        notes,end=events_to_notes(returned,melody.ppq)
        if notes!=melody.notes or end!=melody.total_ticks:raise AssertionError('rational roundtrip')
        elapsed=time.perf_counter()-start
        # Same quarter-note timeline at doubled PPQ, with all metadata ticks
        # scaled. Derived in-memory only: original is never rewritten.
        scaled=replace(melody,notes=tuple(replace(n,start=n.start*2,end=n.end*2) for n in melody.notes),
            total_ticks=melody.total_ticks*2,source_total_ticks=melody.source_total_ticks*2,ppq=melody.ppq*2,
            tempo_map=tuple((t*2,v) for t,v in melody.tempo_map),volume_map=tuple((t*2,v) for t,v in melody.volume_map),
            program_map=tuple((t*2,v) for t,v in melody.program_map),
            channel_events=tuple((t*2,k,v,vel) for t,k,v,vel in melody.channel_events))
        if to_events(scaled)!=events:raise AssertionError('PPQ invariance')
        grid=inspect_grid_error(melody);resolution=grid['min_exact_steps_per_quarter']
        exact_length=Fraction(melody.total_ticks*resolution,melody.ppq)
        if exact_length.denominator!=1:raise AssertionError('exact resolution')
        full_json=json.dumps(serialized,sort_keys=True,separators=(',',':')).encode()
        # Pitch/duration-only compact formats compared separately from full
        # event JSON that includes velocity. No grid corpus is generated.
        compact=[[e.pitch,e.duration.numerator,e.duration.denominator] for e in events]
        tick_compact=[[e.pitch,int(e.duration*melody.ppq)] for e in events]
        row=dict(work_id=f'mutopia-{id}',original_sha256=original,notes=len(notes),events=len(events),
            rest_events=sum(e.pitch==-1 for e in events),duration_symbols=len({e.duration for e in events}),
            exact_ticks_preserved=True,velocities_preserved=True,ppq_invariance=True,grid_diagnostic=grid,
            exact_grid_steps_per_quarter=resolution,exact_grid_length=int(exact_length),
            nominal_sixteenth_length=str(Fraction(melody.total_ticks*4,melody.ppq)),
            exact_grid_resolution_multiplier=Fraction(resolution,4),
            hypothetical_uint8_grid_bytes=int(exact_length),
            compact_rational_json_bytes=len(json.dumps(compact,separators=(',',':')).encode()),
            compact_tick_json_bytes=len(json.dumps(dict(ppq=melody.ppq,events=tick_compact),separators=(',',':')).encode()),
            full_rational_json_bytes=len(full_json),full_rational_json_sha256=hashlib.sha256(full_json).hexdigest(),
            conversion_wall_seconds=elapsed,model_fitted=False,model_scored=False,
            byte_comparison_limit='uint8 grid counts pitch/rest/HOLD only; full event JSON also carries velocities, formats differ')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=original:raise AssertionError('source changed')
        rows.append(row)
    repo=Path(__file__).resolve().parents[1]
    report=dict(scope='Representation fidelity/cost only; no model or attractiveness comparison',
        code_sha256={n:hashlib.sha256((repo/n).read_bytes()).hexdigest() for n in
            ['src/mousa/rational_events.py','src/mousa/tick_midi.py','tools/compare_exact_time_representations.py']},
        rights_review_sha256=hashlib.sha256(a.rights_review.read_bytes()).hexdigest(),works=rows,
        limitation='No fine-grid arrays or quantized corpus emitted. Fractions preserve timing but do not solve generative modeling or expressive semantics.')
    (a.output/'report.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
    print(json.dumps([dict(work=x['work_id'],notes=x['notes'],events=x['events'],grid=x['exact_grid_length']) for x in rows]))

if __name__=='__main__':main()

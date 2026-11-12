"""Exact selected ornament performance and onset/gate diagnostic, not model scoring."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import mido
from mousa.overlap_midi import read_midi,write_midi


def signature(path,index):
    now=0;out=[]
    for e in mido.MidiFile(path).tracks[index]:
        now+=e.time
        if e.is_meta:continue
        if e.type=='note_on' and e.velocity==0:e=mido.Message('note_off',channel=e.channel,note=e.note,velocity=0)
        out.append((now,tuple(e.bytes())))
    return out


def onset_gate_rows(notes,ppq):
    # Onset-delta and gate duration are distinct; negative rest is never needed.
    previous=0;out=[]
    for n in notes:
        out.append(dict(delta=Fraction(n.start-previous,ppq),gate=Fraction(n.end-n.start,ppq),pitch=n.pitch,
            velocity=n.velocity,release_velocity=n.release_velocity))
        previous=n.start
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('new output required')
    expected='dcd5efac22b5e91b7c87685058784396adb9ec5d69915764265ad68158dbb6e1'
    if hashlib.sha256(a.source.read_bytes()).hexdigest()!=expected:raise ValueError('reviewed source hash differs')
    root=Path(__file__).resolve().parents[1]
    rights=json.loads((root/'datasets/research-brahms580-rights-20261112.json').read_text())
    assert rights['encoding_rights']['status']=='PD-dedication-supported'
    m=read_midi(a.source,1);a.output.mkdir(parents=True);out=a.output/'selected-exact.mid';write_midi(m,out)
    assert read_midi(out,1)==m
    assert signature(a.source,1)==signature(out,1)
    rows=onset_gate_rows(m.notes,m.ppq);now=Fraction();rebuilt=[]
    for row in rows:
        now+=row['delta'];start=now*m.ppq;end=(now+row['gate'])*m.ppq
        assert start.denominator==end.denominator==1
        rebuilt.append((int(start),int(end),row['pitch'],row['velocity'],row['release_velocity']))
    assert rebuilt==[(n.start,n.end,n.pitch,n.velocity,n.release_velocity) for n in m.notes]
    active=set();maximum=0;overlap_ticks=0;previous=0
    for tick,kind,value,velocity in m.channel_events:
        if len(active)>1:overlap_ticks+=tick-previous
        previous=tick
        if kind=='note_on':active.add(value)
        elif kind=='note_off':active.remove(value)
        maximum=max(maximum,len(active))
    # Lossy mono shortcut would truncate these gates. Diagnose only, never emit it.
    losses=[max(0,a.end-b.start) for a,b in zip(m.notes,m.notes[1:])]
    report=dict(scope='Rights-reviewed representation intake only; no fitting or predictive evaluation',source_sha256=expected,
        original_unchanged=hashlib.sha256(a.source.read_bytes()).hexdigest()==expected,
        notes=len(m.notes),meter_map=[vars(c) for c in m.meter_map],total_ticks=m.total_ticks,ppq=m.ppq,
        exact_modeled_roundtrip=True,independent_channel_signature_equal=True,onset_gate_note_roundtrip=True,
        max_simultaneous_notes=maximum,overlap_timeline_ticks=overlap_ticks,
        hypothetical_monophonic_clipping={'affected_notes':sum(v>0 for v in losses),'sum_gate_ticks_removed':sum(losses),'performed':False},
        onset_gate_fields='Exact rational onset delta (zero allowed), positive rational sounding gate, pitch and velocities. Source channel stream resolves same-tick event ordering.',
        tail_ticks=m.total_ticks-max(n.end for n in m.notes),
        selected_midi_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
        code_sha256={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ['src/mousa/overlap_midi.py','tools/probe_overlap_representation.py','datasets/research-brahms580-rights-20261112.json']},
        model_policy=['Never feed these overlapping gates into the old monophonic REST/HOLD model.',
            'A future model must distinguish onset delta (including zero) from gate duration and track active pitches.',
            'Mask same-pitch retriggers while active; bound polyphony and remaining endpoints; do not repair by truncation.',
            'Fix joint outcome support and compare like tasks before any predictive evaluation.',
            'Metadata/maps/EOT remain sidecar state; onset/gate rows alone are not complete MIDI preservation.'],
        source_state='Inspected and representation-tested, untrained and predictive-unscored; not untouched data. Independent family screening required before future held-out scoring.')
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['notes','max_simultaneous_notes','overlap_timeline_ticks','hypothetical_monophonic_clipping']}))
if __name__=='__main__':main()

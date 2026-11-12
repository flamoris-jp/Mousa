"""Verified private eight-bar preview; metadata meter is not learned structure."""
import argparse
import hashlib
import json
from pathlib import Path
from mousa.overlap_midi import OverlapMelody, read_midi, write_midi
from mousa.tick_midi import TickNote
from render_overlap_preview import render


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export(source, expected_sha, output):
    if source.stat().st_size > 100000 or digest(source) != expected_sha:
        raise ValueError('bounded matching generated-note source required')
    if output.exists():
        raise ValueError('new private output directory required')
    rows=json.loads(source.read_text())
    if type(rows) is not list or not 1 <= len(rows) <= 256:
        raise ValueError('bounded nonempty note list required')
    for n in rows:
        if type(n) is not dict or set(n) != {'start','end','pitch'} or any(type(n[k]) is not int for k in n):
            raise ValueError('exact integer note fields required')
    notes=tuple(sorted((TickNote(n['start'],n['end'],n['pitch'],80,0) for n in rows),key=lambda n:(n.start,n.end,n.pitch)))
    events=[]
    for i,n in enumerate(rows):
        events.extend(((n['start'],1,i,'note_on',n['pitch'],80),(n['end'],0,i,'note_off',n['pitch'],0)))
    stream=((0,'program',0,0),)+tuple((t,k,p,v) for t,_,i,k,p,v in sorted(events))
    melody=OverlapMelody(notes,9216,(6,8),ppq=384,channel_events=stream)
    output.mkdir(parents=True)
    midi=output/'preview.mid';write_midi(melody,midi)
    parsed=read_midi(midi,1)
    if parsed.notes != notes or parsed.total_ticks != 9216 or parsed.meter != (6,8):
        raise ValueError('note/timeline roundtrip failed')
    if parsed.channel_events != melody.channel_events:
        raise ValueError('modeled event order changed')
    repeat=output/'roundtrip.mid';write_midi(parsed,repeat)
    if midi.read_bytes()!=repeat.read_bytes():
        raise ValueError('MIDI byte roundtrip failed')
    wav=output/'preview.wav';audio=render(midi,wav)
    wav2=output/'repeat.wav';again=render(midi,wav2)
    if wav.read_bytes()!=wav2.read_bytes() or audio!=again:
        raise ValueError('audio repeat mismatch')
    result=dict(generated_notes_sha256=expected_sha,midi_sha256=digest(midi),audio=audio,
                exact_note_gate_order_roundtrip=True,midi_byte_roundtrip=True,wav_repeat_identical=True,
                horizon_ticks=9216,ppq=384,meter=[6,8],bars=8,
                limits=['6/8 header is a fixed export convention, not learned meter or phrase structure.',
                        'Analytic fixed-gain preview, not actual Cantabile rendering or human listening.',
                        'Source-copy clearance must already be reviewed separately; this exporter does not grant originality or publication permission.'])
    (output/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--expected-sha',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(export(a.source,a.expected_sha,a.output),indent=2))

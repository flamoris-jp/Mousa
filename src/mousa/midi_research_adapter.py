"""Explicit adapter around the pinned, strict grid-v1 reader.

Preserves end-of-track silence and optionally original pitches. Still only the
reader's narrow monophonic 4/4 sixteenth-grid profile, not general MIDI support.
"""
from fractions import Fraction
import math
from pathlib import Path


def read_grid(path, track_index, reader, *, preserve_pitch=True):
    import mido  # optional research dependency, not needed by core unit tests
    path=Path(path)
    if not path.is_file() or path.is_symlink() or path.stat().st_size>1048576:
        raise ValueError('bounded regular MIDI file required')
    tokens,details=reader(path,track_index)
    midi=mido.MidiFile(path)
    tick=0;end=None
    for event in midi.tracks[track_index]:
        tick+=event.time
        if event.type=='end_of_track':end=tick
    if end is None:raise ValueError('explicit end_of_track required')
    steps=Fraction(end*4,midi.ticks_per_beat)
    if steps.denominator!=1:raise ValueError('off-grid end_of_track')
    length=max(len(tokens),math.ceil(steps/16)*16)
    if length>4096:raise ValueError('end_of_track exceeds grid bounds')
    result=tokens+[0]*(length-len(tokens))
    shift=details['transposition_semitones']
    if preserve_pitch:
        result=[t-shift if t>=2 else t for t in result]
        if any(t<0 or t>26 for t in result) or any(t>=2 and not 2<=t<=26 for t in result):
            raise ValueError('original pitch outside bounded vocabulary')
        # Reject restored note pitches that collide with REST/HOLD sentinels.
        if any(t>=2 and not 2<=t-shift<=26 for t in tokens):
            raise ValueError('original pitch outside bounded vocabulary')
    return result,{**details,'steps':length,'end_of_track_steps':int(steps),
                  'pitch_normalization_applied':not preserve_pitch,
                  'trailing_steps_restored':length-len(tokens)}

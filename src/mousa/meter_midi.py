"""Bounded monophonic research MIDI in explicit constant 4/4 or 6/8.

Extends the strict profile in Mousa PR #6 (Apache-2.0) without modifying it.
No quantization or automatic transposition. Preserves chosen-track end-of-track
silence, note pitch/onset/end/velocity and a constant tempo. It is not lossless
MIDI editing: lyrics, key signatures and descriptive metadata are not exported;
Cantabile remains the editable project authority. Accompaniment is excluded.
"""
from dataclasses import dataclass
from fractions import Fraction
import io
from pathlib import Path


@dataclass(frozen=True)
class MeterNote:
    start: int
    end: int
    pitch: int
    velocity: int = 80
    release_velocity: int = 0


@dataclass(frozen=True)
class MeterMelody:
    notes: tuple[MeterNote, ...]
    total_steps: int
    meter: tuple[int, int]
    ppq: int = 480
    tempo: int = 500000  # microseconds per quarter, including in 6/8
    channel: int = 0
    program: int = 0
    tempo_defaulted: bool = False

    @property
    def steps_per_bar(self):
        return 16 if self.meter == (4, 4) else 12

    @property
    def bars(self):
        return Fraction(self.total_steps, self.steps_per_bar)


def _integer(value, low, high, name):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f'{name} must be an integer in {low}..{high}')


def validate(melody):
    if not isinstance(melody, MeterMelody):
        raise ValueError('MeterMelody required')
    if type(melody.meter) is not tuple or melody.meter not in ((4, 4), (6, 8)) or any(type(n) is not int for n in melody.meter):
        raise ValueError('explicit 4/4 or 6/8 meter required')
    _integer(melody.total_steps, 1, melody.steps_per_bar * 256, 'total_steps')
    _integer(melody.ppq, 1, 32767, 'PPQ')
    _integer(melody.tempo, 1, 16777215, 'tempo')
    _integer(melody.channel, 0, 15, 'channel')
    if melody.channel == 9:
        raise ValueError('percussion channel is not a melody')
    _integer(melody.program, 0, 127, 'program')
    if type(melody.tempo_defaulted) is not bool:
        raise ValueError('tempo_defaulted must be boolean')
    if type(melody.notes) is not tuple or len(melody.notes) > 4096:
        raise ValueError('bounded tuple of notes required')
    last_end = 0
    for note in melody.notes:
        if not isinstance(note, MeterNote):
            raise ValueError('MeterNote required')
        for value,low,high,name in ((note.start,0,melody.total_steps-1,'start'),
                                   (note.end,1,melody.total_steps,'end'),
                                   (note.pitch,0,127,'pitch'),(note.velocity,1,127,'velocity'),
                                   (note.release_velocity,0,127,'release_velocity')):
            _integer(value,low,high,name)
        if note.end <= note.start or note.start < last_end:
            raise ValueError('non-positive note or polyphonic/unsorted sequence')
        last_end = note.end
    return melody


def read_midi(path, track_index, *, allow_empty=False):
    """Read exactly one chosen melody track; unsupported semantics reject.

    All meter declarations must agree and one must exist at tick zero. Duplicate
    declarations of the same meter/tempo are accepted, but changes are rejected.
    Tempo defaults to the SMF standard only when absent, with a visible flag.
    """
    import mido  # optional research dependency
    if type(allow_empty) is not bool:
        raise ValueError('allow_empty must be boolean')
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 1048576:
        raise ValueError('bounded regular MIDI file required')
    data = path.read_bytes()
    if len(data) > 1048576:
        raise ValueError('MIDI byte limit')
    midi = mido.MidiFile(file=io.BytesIO(data), clip=False)
    if midi.type not in (0, 1) or not 1 <= midi.ticks_per_beat <= 32767:
        raise ValueError('SMF0/1 with PPQ timing required')
    if not 1 <= len(midi.tracks) <= 256 or sum(map(len,midi.tracks)) > 100000:
        raise ValueError('MIDI track/event limit')
    _integer(track_index,0,len(midi.tracks)-1,'explicit melody track')
    timed=[]; meters=[]; tempos=[]
    for track in midi.tracks:
        now=0; events=[]
        for event in track:
            _integer(event.time,0,2**28-1,'delta tick')
            now+=event.time
            if now > midi.ticks_per_beat*4*256:
                raise ValueError('MIDI timeline exceeds research bound')
            events.append((now,event))
            if event.type == 'time_signature':meters.append((now,event.numerator,event.denominator))
            if event.type == 'set_tempo':tempos.append((now,event.tempo))
            if event.type == 'sysex':raise ValueError('SysEx outside research profile')
        timed.append(events)
    if not meters or not any(t == 0 for t,_,_ in meters):
        raise ValueError('explicit meter at tick zero required')
    meter_set={(n,d) for _,n,d in meters}
    if len(meter_set)!=1 or next(iter(meter_set)) not in ((4,4),(6,8)):
        raise ValueError('constant 4/4 or 6/8 required; meter changes are not converted')
    meter=next(iter(meter_set))
    if tempos and (not any(t==0 for t,_ in tempos) or len({v for _,v in tempos})!=1):
        raise ValueError('constant tempo at tick zero required')
    tempo=tempos[0][1] if tempos else 500000
    track=timed[track_index]
    endings=[t for t,e in track if e.type=='end_of_track']
    if len(endings)!=1 or not track or track[-1][1].type!='end_of_track':
        raise ValueError('exactly one final end_of_track required')
    end_tick=endings[0]
    channels={e.channel for _,e in track if e.type in ('note_on','note_off')}
    if len(channels)>1 or 9 in channels:
        raise ValueError('single non-percussion melody channel required')
    if not channels:
        channels={e.channel for _,e in track if e.type=='program_change'}
        if len(channels)>1 or 9 in channels:
            raise ValueError('ambiguous empty-track channel')
    channel=next(iter(channels),0)
    for i,other in enumerate(timed):
        if i != track_index and any(not e.is_meta and getattr(e,'channel',None)==channel for _,e in other):
            raise ValueError('unselected track shares melody channel; semantics are ambiguous')
    active={};notes=[];programs=[]
    for now,event in track:
        if not event.is_meta and event.type not in ('note_on','note_off','program_change'):
            raise ValueError('unsupported melody control, pressure or pitch bend')
        if event.type=='program_change':
            if now != 0 or event.channel != channel:
                raise ValueError('program changes must be initial on the melody channel')
            programs.append(event.program)
        if event.type=='note_on' and event.velocity>0:
            if active:raise ValueError('polyphonic or ambiguous overlapping notes')
            active[(event.channel,event.note)]=(now,event.velocity)
        elif event.type=='note_off' or (event.type=='note_on' and event.velocity==0):
            key=(event.channel,event.note)
            if key not in active:raise ValueError('unmatched note-off')
            start,velocity=active.pop(key)
            if now<=start:raise ValueError('non-positive note duration')
            notes.append((start,now,event.note,velocity,event.velocity))
    if active or (not notes and not allow_empty):
        raise ValueError('unterminated notes or empty melody')
    if len(set(programs))>1:raise ValueError('conflicting initial programs')
    def step(tick):
        value=Fraction(tick*4,midi.ticks_per_beat)
        if value.denominator!=1:
            raise ValueError('off-grid timing: exact sixteenths required, no quantization')
        return int(value)
    melody=MeterMelody(tuple(MeterNote(step(s),step(e),p,v,r) for s,e,p,v,r in notes),
                       step(end_tick),meter,midi.ticks_per_beat,tempo,channel,
                       programs[0] if programs else 0,not bool(tempos))
    return validate(melody)


def to_tokens(melody, *, transpose_semitones=0, pitch_low=60, pitch_high=84):
    """Explicit projection: REST=0, HOLD=1, pitches start at 2.

    Original MIDI pitches stay in MeterMelody. Callers must record any requested
    transposition and vocabulary bounds. No clipping or automatic normalization.
    """
    validate(melody)
    _integer(transpose_semitones,-127,127,'transposition')
    _integer(pitch_low,0,127,'pitch_low');_integer(pitch_high,pitch_low,127,'pitch_high')
    result=[0]*melody.total_steps
    for note in melody.notes:
        pitch=note.pitch+transpose_semitones
        if not pitch_low <= pitch <= pitch_high:
            raise ValueError('pitch outside explicit vocabulary; no automatic transposition')
        result[note.start]=pitch-pitch_low+2
        for i in range(note.start+1,note.end):result[i]=1
    return result


def from_tokens(tokens, *, meter, pitch_low=60, pitch_high=84, ppq=480,
                tempo=500000, velocity=80, channel=0, program=0):
    _integer(pitch_low,0,127,'pitch_low');_integer(pitch_high,pitch_low,127,'pitch_high')
    _integer(velocity,1,127,'velocity')
    if not isinstance(tokens,list) or not 1<=len(tokens)<=4096:
        raise ValueError('bounded token list required')
    notes=[]; start=None; pitch=None
    for i,token in enumerate(tokens+[0]):
        _integer(token,0,pitch_high-pitch_low+2,'token')
        if token==1 and pitch is None:raise ValueError('HOLD without an active note')
        if token!=1:
            if pitch is not None:notes.append(MeterNote(start,i,pitch,velocity,0))
            start,pitch=(i,pitch_low+token-2) if token>=2 else (None,None)
    return validate(MeterMelody(tuple(notes),len(tokens),meter,ppq,tempo,channel,program))


def write_midi(melody, path):
    """Export research melody only, preserving exact grid/EOT and initial setup."""
    import mido
    validate(melody)
    path=Path(path)
    if path.exists() or path.is_symlink():raise FileExistsError(path)
    def tick(step):
        value=Fraction(step*melody.ppq,4)
        if value.denominator!=1:
            raise ValueError('PPQ cannot exactly represent requested grid; no rounding')
        return int(value)
    midi=mido.MidiFile(type=1,ticks_per_beat=melody.ppq)
    meta,track=mido.MidiTrack(),mido.MidiTrack();midi.tracks.extend([meta,track])
    meta.extend([mido.MetaMessage('time_signature',numerator=melody.meter[0],denominator=melody.meter[1],
                                  clocks_per_click=36 if melody.meter==(6,8) else 24,time=0),
                 mido.MetaMessage('set_tempo',tempo=melody.tempo,time=0),mido.MetaMessage('end_of_track',time=0)])
    track.append(mido.Message('program_change',channel=melody.channel,program=melody.program,time=0))
    events=[]
    for note in melody.notes:
        events.extend([(tick(note.start),1,note.pitch,note.velocity),(tick(note.end),0,note.pitch,note.release_velocity)])
    previous=0
    for now,on,pitch,velocity in sorted(events):
        track.append(mido.Message('note_on' if on else 'note_off',note=pitch,velocity=velocity,
                                  channel=melody.channel,time=now-previous));previous=now
    track.append(mido.MetaMessage('end_of_track',time=tick(melody.total_steps)-previous))
    # Exclusive file creation avoids overwriting an existing asset even on races.
    with path.open('xb') as stream:midi.save(file=stream)
    return dict(notes=len(melody.notes),steps=melody.total_steps,meter=f'{melody.meter[0]}/{melody.meter[1]}',
                bars=str(melody.bars),pitch_policy='explicit; preserved')

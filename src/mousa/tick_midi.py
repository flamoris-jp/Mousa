"""Exact-tick selected melody preservation, not a complete MIDI editor.

Strict track/control checks follow meter_midi (Apache-2.0). Arbitrary metadata,
lyrics and accompaniment are not preserved. Selected channel-event ordering,
notes, selected EOT, tempo map, CC7 volume map, channel, program map and velocities
are preserved. Zero-velocity note-on is normalized to note-off; cross-track
metadata ordering and redundant tempo declarations are not retained.
Direct construction without channel_events builds a canonical stream; replacing
modeled fields requires channel_events=None to explicitly rebuild that stream.
No quantization or automatic source admission is performed.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import gcd, lcm
import io
from pathlib import Path
from mousa.meter_midi import _integer, MeterNote, MeterMelody, to_tokens as _grid_tokens


@dataclass(frozen=True)
class TickNote:
    start: int
    end: int
    pitch: int
    velocity: int = 80
    release_velocity: int = 0


@dataclass(frozen=True)
class TickMelody:
    notes: tuple[TickNote, ...]
    total_ticks: int
    meter: tuple[int, int]
    ppq: int = 480
    tempo_map: tuple[tuple[int, int], ...] = ((0, 500000),)
    channel: int = 0
    program: int = 0
    tempo_defaulted: bool = False
    volume_map: tuple[tuple[int, int], ...] = ()
    source_total_ticks: int | None = None
    program_map: tuple[tuple[int, int], ...] = ()
    program_defaulted: bool = False
    channel_events: tuple[tuple[int, str, int, int], ...] | None = None

    def __post_init__(self):
        if self.program_map == ():
            object.__setattr__(self,'program_map',((0,self.program),))
        if self.source_total_ticks is None:
            # In-memory construction defaults to the largest modeled timeline.
            end=max((t for t,_ in self.tempo_map),default=0)
            object.__setattr__(self,'source_total_ticks',max(self.total_ticks,end))
        if self.channel_events is None:
            # Direct construction has no source ordering: explicit canonical order.
            events=[]
            for note in self.notes:
                events.extend(((note.start,'note_on',note.pitch,note.velocity),
                               (note.end,'note_off',note.pitch,note.release_velocity)))
            events.extend((t,'volume',v,0) for t,v in self.volume_map)
            events.extend((t,'program',v,0) for t,v in self.program_map
                          if not (t==0 and self.program_defaulted))
            priority={'program':0,'volume':1,'note_off':2,'note_on':3}
            object.__setattr__(self,'channel_events',tuple(sorted(events,key=lambda e:(e[0],priority[e[1]],e[2:]))))

    def seconds_at_tick(self, tick):
        """Exact Fraction seconds, integrating all changes up to requested tick."""
        validate(self)
        _integer(tick, 0, self.ppq * 4 * 256, 'tick')
        elapsed=Fraction(0); previous=0; tempo=self.tempo_map[0][1]
        for now, new_tempo in self.tempo_map[1:]:
            if now > tick:break
            elapsed += Fraction((now-previous)*tempo, self.ppq*1000000)
            previous,tempo=now,new_tempo
        return elapsed+Fraction((tick-previous)*tempo,self.ppq*1000000)


def validate(melody):
    if not isinstance(melody, TickMelody):raise ValueError('TickMelody required')
    if type(melody.meter) is not tuple or melody.meter not in ((4,4),(6,8)) or any(type(n) is not int for n in melody.meter):
        raise ValueError('explicit constant 4/4 or 6/8 required')
    _integer(melody.ppq,1,32767,'PPQ')
    _integer(melody.total_ticks,1,melody.ppq*(4 if melody.meter==(4,4) else 3)*256,'total_ticks')
    _integer(melody.channel,0,15,'channel')
    if melody.channel==9:raise ValueError('percussion channel is not a melody')
    _integer(melody.program,0,127,'program')
    if type(melody.program_defaulted) is not bool:raise ValueError('boolean program_defaulted required')
    if type(melody.program_map) is not tuple or not 1<=len(melody.program_map)<=100000:
        raise ValueError('bounded program map required')
    previous=-1
    for item in melody.program_map:
        if type(item) is not tuple or len(item)!=2:raise ValueError('program tick/value pair required')
        tick,value=item
        _integer(tick,0,melody.total_ticks,'program tick');_integer(value,0,127,'program value')
        if tick<=previous:raise ValueError('program ticks must be strictly increasing')
        previous=tick
    if melody.program_map[0]!=(0,melody.program):raise ValueError('initial program must match program map')
    if melody.program_defaulted and melody.program!=0:raise ValueError('implicit GM program must be zero')
    if type(melody.tempo_defaulted) is not bool:raise ValueError('boolean tempo_defaulted required')
    if type(melody.tempo_map) is not tuple or not 1<=len(melody.tempo_map)<=100000:
        raise ValueError('bounded nonempty tempo map required')
    previous=-1
    for item in melody.tempo_map:
        if type(item) is not tuple or len(item)!=2:raise ValueError('tempo tick/value pair required')
        tick,tempo=item
        _integer(tick,0,melody.ppq*4*256,'tempo tick');_integer(tempo,1,16777215,'tempo')
        if tick<=previous:raise ValueError('tempo ticks must be strictly increasing')
        previous=tick
    if melody.tempo_map[0][0]!=0:raise ValueError('effective tempo at zero required')
    if melody.tempo_defaulted and melody.tempo_map[0]!=(0,500000):
        raise ValueError('default tempo must be standard 500000')
    _integer(melody.source_total_ticks,melody.total_ticks,melody.ppq*4*256,'source_total_ticks')
    if melody.tempo_map[-1][0]>melody.source_total_ticks:
        raise ValueError('tempo event beyond source timeline')
    if type(melody.volume_map) is not tuple or len(melody.volume_map)>100000:
        raise ValueError('bounded volume map required')
    previous=-1
    for item in melody.volume_map:
        if type(item) is not tuple or len(item)!=2:raise ValueError('volume tick/value pair required')
        tick,value=item
        _integer(tick,0,melody.total_ticks,'volume tick');_integer(value,0,127,'volume')
        if tick<=previous:raise ValueError('volume ticks must be strictly increasing')
        previous=tick
    if type(melody.notes) is not tuple or len(melody.notes)>4096:raise ValueError('bounded notes tuple required')
    previous=0
    for note in melody.notes:
        if not isinstance(note,TickNote):raise ValueError('TickNote required')
        for value,low,high,name in ((note.start,0,melody.total_ticks-1,'start'),(note.end,1,melody.total_ticks,'end'),
                                   (note.pitch,0,127,'pitch'),(note.velocity,1,127,'velocity'),
                                   (note.release_velocity,0,127,'release_velocity')):
            _integer(value,low,high,name)
        if note.start<previous or note.end<=note.start:raise ValueError('overlap or nonpositive duration')
        previous=note.end
    _validate_channel_events(melody)
    # Writer emits time signature + two EOTs, explicit tempos, and the channel
    # stream. Match the reader's aggregate limit, not just per-map limits.
    serialized_events = 3 + len(melody.tempo_map) - int(melody.tempo_defaulted) + len(melody.channel_events)
    if serialized_events > 100000:
        raise ValueError('aggregate serialized MIDI event limit')
    return melody


def _validate_channel_events(melody):
    """Replay source ordering; reject stale streams after dataclass replacement."""
    if type(melody.channel_events) is not tuple or len(melody.channel_events)>100000:
        raise ValueError('bounded channel event tuple required')
    previous=0; active=None; notes=[]; volumes={}; programs={}
    for event in melody.channel_events:
        if type(event) is not tuple or len(event)!=4:raise ValueError('channel event tuple required')
        tick,kind,value,velocity=event
        _integer(tick,previous,melody.total_ticks,'channel event tick')
        _integer(value,0,127,'channel event value');_integer(velocity,0,127,'channel event velocity')
        previous=tick
        if kind in ('program','volume'):
            if velocity!=0:raise ValueError('control event reserved velocity must be zero')
            mapping=programs if kind=='program' else volumes
            if tick in mapping and mapping[tick]!=value:raise ValueError('conflicting same-tick channel state')
            mapping[tick]=value
        elif kind=='note_on':
            if active is not None or velocity==0:raise ValueError('ambiguous channel note-on')
            active=(tick,value,velocity)
        elif kind=='note_off':
            if active is None or active[1]!=value or tick<=active[0]:raise ValueError('invalid channel note-off')
            notes.append(TickNote(active[0],tick,value,active[2],velocity));active=None
        else:raise ValueError('unsupported channel event kind')
    if active is not None or tuple(notes)!=melody.notes:raise ValueError('channel stream differs from notes')
    if melody.program_defaulted:
        if 0 in programs:raise ValueError('explicit initial program contradicts defaulted flag')
        programs[0]=0
    if tuple(sorted(programs.items()))!=melody.program_map or tuple(sorted(volumes.items()))!=melody.volume_map:
        raise ValueError('channel stream differs from state maps')


def read_midi(path, track_index, *, allow_empty=False):
    """Read exactly one chosen melody track; unsupported semantics reject.

    Constant meter required; tempo changes retain their exact ticks. Conflicting
    tempo declarations at the same tick reject, even on separate tracks.
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
    tempo_by_tick={}
    for tick, tempo in tempos:
        if tick in tempo_by_tick and tempo_by_tick[tick] != tempo:
            raise ValueError('conflicting same-tick tempo declarations')
        tempo_by_tick[tick]=tempo
    defaulted=0 not in tempo_by_tick
    if defaulted:tempo_by_tick[0]=500000
    tempo_map=tuple(sorted(tempo_by_tick.items()))
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
    active={};notes=[];programs={};volumes={};channel_events=[]
    for now,event in track:
        if not event.is_meta and event.type not in ('note_on','note_off','program_change','control_change'):
            raise ValueError('unsupported melody control, pressure or pitch bend')
        if event.type=='control_change':
            if event.control!=7 or event.channel!=channel:
                raise ValueError('only selected-channel CC7 volume is supported')
            if now in volumes and volumes[now]!=event.value:
                raise ValueError('conflicting same-tick volume declarations')
            volumes[now]=event.value
            channel_events.append((now,'volume',event.value,0))
        if event.type=='program_change':
            if event.channel != channel:
                raise ValueError('program changes must use the selected melody channel')
            if now in programs and programs[now]!=event.program:
                raise ValueError('conflicting same-tick program declarations')
            programs[now]=event.program
            channel_events.append((now,'program',event.program,0))
        if event.type=='note_on' and event.velocity>0:
            channel_events.append((now,'note_on',event.note,event.velocity))
            if active:raise ValueError('polyphonic or ambiguous overlapping notes')
            active[(event.channel,event.note)]=(now,event.velocity)
        elif event.type=='note_off' or (event.type=='note_on' and event.velocity==0):
            channel_events.append((now,'note_off',event.note,event.velocity))
            key=(event.channel,event.note)
            if key not in active:raise ValueError('unmatched note-off')
            start,velocity=active.pop(key)
            if now<=start:raise ValueError('non-positive note duration')
            notes.append((start,now,event.note,velocity,event.velocity))
    if active or (not notes and not allow_empty):
        raise ValueError('unterminated notes or empty melody')
    program_defaulted=0 not in programs
    if program_defaulted:programs[0]=0
    melody=TickMelody(tuple(TickNote(*note) for note in notes),end_tick,meter,
                      midi.ticks_per_beat,tempo_map,channel,
                      programs[0],defaulted,tuple(sorted(volumes.items())),
                      max((t for events in timed for t,_ in events),default=0),
                      tuple(sorted(programs.items())),program_defaulted,tuple(channel_events))
    return validate(melody)


def to_tokens(melody, *, transpose_semitones=0, pitch_low=60, pitch_high=84):
    """Exact sixteenth projection only. Rhythm tokens IGNORE tempo, CC7 volume and program/timbre maps.

    Caller must retain TickMelody as original and record projection/transpose.
    Tempo changes need not be grid-aligned because they are not note tokens.
    """
    validate(melody)
    def step(tick):
        value=Fraction(tick*4,melody.ppq)
        if value.denominator!=1:raise ValueError('off-grid timing; no quantization')
        return int(value)
    grid=MeterMelody(tuple(MeterNote(step(n.start),step(n.end),n.pitch,n.velocity,n.release_velocity)
                           for n in melody.notes),step(melody.total_ticks),melody.meter,melody.ppq,
                     melody.tempo_map[0][1],melody.channel,melody.program,melody.tempo_defaulted)
    return _grid_tokens(grid,transpose_semitones=transpose_semitones,pitch_low=pitch_low,pitch_high=pitch_high)


def inspect_grid_error(melody):
    """Diagnostic only: onset/end/EOT occurrences; nearest ties round upward.

    Duplicate boundary occurrences count separately. Tempo events are excluded
    from rhythm-token error. Fractions retain exact tick-error statistics.
    min_exact_steps_per_quarter is the LCM of reduced boundary denominators;
    it describes representability, not recommended model resolution.
    """
    validate(melody)
    ticks=[t for n in melody.notes for t in (n.start,n.end)]+[melody.total_ticks]
    def nearest(tick):return (tick*8+melody.ppq)//(2*melody.ppq)
    errors=[abs(Fraction(nearest(t)*melody.ppq,4)-t) for t in ticks]
    resolution=1
    for tick in ticks:resolution=lcm(resolution,melody.ppq//gcd(tick,melody.ppq))
    return dict(boundary_count=len(ticks),off_grid_count=sum(e!=0 for e in errors),
                max_tick_error=max(errors),mean_tick_error=sum(errors,Fraction(0))/len(errors),
                collapsed_notes_if_rounded=sum(nearest(n.start)==nearest(n.end) for n in melody.notes),
                min_exact_steps_per_quarter=resolution,
                rounding_rule='nearest sixteenth; ties upward; diagnostic only',
                tempo_map_ignored_by_rhythm_tokens=True,volume_map_ignored_by_rhythm_tokens=True,program_map_ignored_by_rhythm_tokens=True)


def write_midi(melody,path):
    """Export modeled fields exactly, never overwrite. No source-file editing."""
    import mido
    validate(melody)
    path=Path(path)
    if path.exists() or path.is_symlink():raise FileExistsError(path)
    midi=mido.MidiFile(type=1,ticks_per_beat=melody.ppq)
    meta,track=mido.MidiTrack(),mido.MidiTrack();midi.tracks.extend((meta,track))
    meta.append(mido.MetaMessage('time_signature',numerator=melody.meter[0],denominator=melody.meter[1],
                                 clocks_per_click=36 if melody.meter==(6,8) else 24,time=0))
    previous=0
    for tick,tempo in melody.tempo_map:
        # Preserve absence of an explicit initial declaration when defaulted.
        if tick==0 and melody.tempo_defaulted:continue
        meta.append(mido.MetaMessage('set_tempo',tempo=tempo,time=tick-previous));previous=tick
    meta.append(mido.MetaMessage('end_of_track',time=melody.source_total_ticks-previous))
    previous=0
    for tick,kind,value,velocity in melody.channel_events:
        if kind=='program':
            event=mido.Message('program_change',channel=melody.channel,program=value,time=tick-previous)
        elif kind=='volume':
            event=mido.Message('control_change',channel=melody.channel,control=7,value=value,time=tick-previous)
        else:
            event=mido.Message(kind,channel=melody.channel,note=value,velocity=velocity,time=tick-previous)
        track.append(event);previous=tick
    track.append(mido.MetaMessage('end_of_track',time=melody.total_ticks-previous))
    with path.open('xb') as stream:midi.save(file=stream)
    return dict(notes=len(melody.notes),total_ticks=melody.total_ticks,tempo_events=len(melody.tempo_map),source_total_ticks=melody.source_total_ticks,
                quantized=False,scope='modeled selected melody fields only')

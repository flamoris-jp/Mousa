"""Explicit variable-meter research profile; no quantization or bar conversion.

Reuses frozen tick_midi channel/tempo checks through a temporary 4/4 metadata
carrier. That carrier is an implementation detail, NOT a musical conversion:
absolute ticks never change, original files are untouched, and real meters are
restored in the returned object and export. No implicit compatibility with
fixed-meter models is claimed. Cantabile remains project authority.

Preserves modeled fields from tick_midi plus meter changes and metronome fields.
Same-tick conflicting declarations reject; identical duplicates collapse.
Metadata ordering across tracks, lyrics and accompaniment are not preserved.
"""
from dataclasses import dataclass, fields
import io
from pathlib import Path
import tempfile

from mousa import tick_midi
from mousa.meter_midi import _integer


@dataclass(frozen=True)
class MeterChange:
    tick: int
    numerator: int
    denominator: int
    clocks_per_click: int = 24
    notated_32nd_notes_per_beat: int = 8


@dataclass(frozen=True)
class VariableMeterMelody(tick_midi.TickMelody):
    meter_map: tuple[MeterChange, ...] = ()

    def seconds_at_tick(self, tick):
        validate(self)
        return _carrier(self).seconds_at_tick(tick)


def _carrier(melody):
    values={f.name:getattr(melody,f.name) for f in fields(tick_midi.TickMelody)}
    values['meter']=(4,4)
    return tick_midi.TickMelody(**values)


def _validate_map(meter_map, end):
    if type(meter_map) is not tuple or not 1<=len(meter_map)<=100000:
        raise ValueError('bounded nonempty meter map required')
    previous=-1
    for change in meter_map:
        if not isinstance(change,MeterChange):raise ValueError('MeterChange required')
        _integer(change.tick,0,end,'meter tick')
        _integer(change.numerator,1,32,'meter numerator')
        if type(change.denominator) is not int or change.denominator not in (1,2,4,8,16,32):
            raise ValueError('unsupported meter denominator')
        _integer(change.clocks_per_click,0,255,'clocks_per_click')
        _integer(change.notated_32nd_notes_per_beat,1,255,'notated_32nd_notes_per_beat')
        if change.tick<=previous:raise ValueError('strictly increasing meter ticks required')
        previous=change.tick
    if meter_map[0].tick!=0:raise ValueError('explicit meter at zero required')


def validate(melody):
    if not isinstance(melody,VariableMeterMelody):raise ValueError('VariableMeterMelody required')
    tick_midi.validate(_carrier(melody))
    _validate_map(melody.meter_map,melody.source_total_ticks)
    first=melody.meter_map[0]
    if type(melody.meter) is not tuple or any(type(x) is not int for x in melody.meter) or melody.meter!=(first.numerator,first.denominator):
        raise ValueError('initial meter differs from meter map')
    count=2+len(melody.meter_map)+len(melody.tempo_map)-int(melody.tempo_defaulted)+len(melody.channel_events)
    if count>100000:raise ValueError('aggregate serialized MIDI event limit')
    return melody


def read_midi(path, track_index, *, allow_empty=False):
    import mido
    path=Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size>1048576:
        raise ValueError('bounded regular MIDI file required')
    data=path.read_bytes()
    if len(data)>1048576:raise ValueError('MIDI byte limit')
    midi=mido.MidiFile(file=io.BytesIO(data),clip=False)
    if midi.type not in (0,1) or not 1<=midi.ticks_per_beat<=32767:
        raise ValueError('SMF0/1 with PPQ required')
    if not 1<=len(midi.tracks)<=256 or sum(map(len,midi.tracks))>100000:
        raise ValueError('MIDI track/event limit')
    _integer(track_index,0,len(midi.tracks)-1,'explicit melody track')
    selected=midi.tracks[track_index]
    if sum(e.type=='end_of_track' for e in selected)!=1 or not selected or selected[-1].type!='end_of_track':
        raise ValueError('exactly one final end_of_track required before carrier normalization')
    changes={}; end=0
    for track in midi.tracks:
        tick=0
        for index,event in enumerate(track):
            _integer(event.time,0,2**28-1,'delta tick');tick+=event.time
            if tick>midi.ticks_per_beat*1024:raise ValueError('MIDI timeline limit')
            end=max(end,tick)
            if event.type=='time_signature':
                change=MeterChange(tick,event.numerator,event.denominator,event.clocks_per_click,
                                   event.notated_32nd_notes_per_beat)
                if tick in changes and changes[tick]!=change:
                    raise ValueError('conflicting same-tick meter declarations')
                changes[tick]=change
                track[index]=event.copy(numerator=4,denominator=4)
    meter_map=tuple(changes[t] for t in sorted(changes))
    _validate_map(meter_map,end)
    # No monkey-patching or modifying the frozen reader. Bound output as well.
    buffer=io.BytesIO();midi.save(file=buffer)
    if len(buffer.getvalue())>1048576:raise ValueError('normalized carrier byte limit')
    with tempfile.TemporaryDirectory() as directory:
        carrier_path=Path(directory)/'carrier.mid'
        carrier_path.write_bytes(buffer.getvalue())
        base=tick_midi.read_midi(carrier_path,track_index,allow_empty=allow_empty)
    values={f.name:getattr(base,f.name) for f in fields(tick_midi.TickMelody)}
    values['meter']=(meter_map[0].numerator,meter_map[0].denominator)
    return validate(VariableMeterMelody(**values,meter_map=meter_map))


def write_midi(melody,path):
    import mido
    validate(melody)
    path=Path(path)
    if path.exists() or path.is_symlink():raise FileExistsError(path)
    with tempfile.TemporaryDirectory() as directory:
        carrier_path=Path(directory)/'carrier.mid'
        tick_midi.write_midi(_carrier(melody),carrier_path)
        midi=mido.MidiFile(carrier_path)
    meta=mido.MidiTrack();events=[]
    for change in melody.meter_map:
        events.append((change.tick,0,mido.MetaMessage('time_signature',numerator=change.numerator,
            denominator=change.denominator,clocks_per_click=change.clocks_per_click,
            notated_32nd_notes_per_beat=change.notated_32nd_notes_per_beat)))
    for tick,tempo in melody.tempo_map:
        if tick==0 and melody.tempo_defaulted:continue
        events.append((tick,1,mido.MetaMessage('set_tempo',tempo=tempo)))
    previous=0
    for tick,_,event in sorted(events,key=lambda item:item[:2]):
        meta.append(event.copy(time=tick-previous));previous=tick
    meta.append(mido.MetaMessage('end_of_track',time=melody.source_total_ticks-previous))
    midi.tracks[0]=meta
    buffer=io.BytesIO();midi.save(file=buffer)
    if len(buffer.getvalue())>1048576:raise ValueError('serialized MIDI byte limit')
    with path.open('xb') as stream:stream.write(buffer.getvalue())
    return dict(notes=len(melody.notes),meter_events=len(melody.meter_map),
                total_ticks=melody.total_ticks,source_total_ticks=melody.source_total_ticks,
                quantized=False,scope='selected modeled performance with variable meter')

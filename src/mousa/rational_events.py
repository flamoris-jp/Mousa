"""Exact rational quarter-note durations, without quantization or model fitting.

Event lists preserve note articulation and velocities, NOT tempo, volume,
program, source ordering or meter metadata. Keep the original TickMelody for
those fields; this representation is not a replacement MIDI/project authority.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import lcm

from mousa.meter_midi import _integer
from mousa.tick_midi import TickNote, validate as validate_ticks

MAX_EVENTS = 8193
MAX_QUARTERS = 1024
MAX_DENOMINATOR = 32767


@dataclass(frozen=True)
class BeatEvent:
    pitch: int  # -1 rest, otherwise absolute MIDI pitch, NOT a grid token
    duration: Fraction  # quarter-note units, including compound meters
    velocity: int = 80
    release_velocity: int = 0


def validate(events):
    if type(events) is not tuple or not 1 <= len(events) <= MAX_EVENTS:
        raise ValueError('bounded nonempty tuple of BeatEvent required')
    total = Fraction(0)
    note_count = 0
    common_ppq = 1
    for event in events:
        if not isinstance(event, BeatEvent):
            raise ValueError('BeatEvent required')
        _integer(event.pitch, -1, 127, 'pitch')
        if type(event.duration) is not Fraction or event.duration <= 0:
            raise ValueError('positive exact Fraction duration required')
        if event.duration.denominator > MAX_DENOMINATOR or event.duration > MAX_QUARTERS:
            raise ValueError('duration exceeds exact PPQ/timeline bounds')
        common_ppq = lcm(common_ppq, event.duration.denominator)
        if common_ppq > MAX_DENOMINATOR:
            raise ValueError('combined durations need a PPQ beyond the MIDI bound')
        _integer(event.velocity, 0, 127, 'velocity')
        _integer(event.release_velocity, 0, 127, 'release_velocity')
        if event.pitch == -1:
            if event.velocity != 0 or event.release_velocity != 0:
                raise ValueError('rests require zero velocity and release velocity')
        else:
            if event.velocity == 0:
                raise ValueError('note velocity must be positive')
            note_count += 1
        total += event.duration
        if total > MAX_QUARTERS:
            raise ValueError('event timeline exceeds research bound')
    if note_count > 4096:
        raise ValueError('note limit exceeded')
    return events


def to_events(melody):
    """Preserve every note onset and exact leading/inter-note/trailing silence."""
    validate_ticks(melody)
    events = []
    previous = 0
    for note in melody.notes:
        if note.start > previous:
            events.append(BeatEvent(-1, Fraction(note.start - previous, melody.ppq), 0, 0))
        events.append(BeatEvent(note.pitch, Fraction(note.end - note.start, melody.ppq),
                                note.velocity, note.release_velocity))
        previous = note.end
    if previous < melody.total_ticks:
        events.append(BeatEvent(-1, Fraction(melody.total_ticks - previous, melody.ppq), 0, 0))
    return validate(tuple(events))


def events_to_notes(events, ppq):
    """Return (TickNote tuple, total_ticks); reject inexact PPQ, never round.

    Adjacent notes of the same pitch remain separate articulations. Original
    metadata cannot be reconstructed from events: callers retain TickMelody.
    """
    validate(events)
    _integer(ppq, 1, 32767, 'PPQ')
    notes = []
    tick = 0
    for event in events:
        duration = event.duration * ppq
        if duration.denominator != 1:
            raise ValueError('duration is not exactly representable at requested PPQ')
        end = tick + int(duration)
        if event.pitch != -1:
            notes.append(TickNote(tick, end, event.pitch, event.velocity, event.release_velocity))
        tick = end
    return tuple(notes), tick


def to_json_data(events):
    """Canonical numeric numerator/denominator objects; no floats or strings."""
    validate(events)
    return [dict(pitch=e.pitch, duration=dict(numerator=e.duration.numerator,
                                            denominator=e.duration.denominator),
                 velocity=e.velocity, release_velocity=e.release_velocity) for e in events]


def from_json_data(data):
    """Strict bounded canonical form: reject floats, bools, extra keys, 2/4."""
    if type(data) is not list or not 1 <= len(data) <= MAX_EVENTS:
        raise ValueError('bounded nonempty JSON event list required')
    events = []
    for item in data:
        if type(item) is not dict or set(item) != {'pitch', 'duration', 'velocity', 'release_velocity'}:
            raise ValueError('exact event fields required')
        duration = item['duration']
        if type(duration) is not dict or set(duration) != {'numerator', 'denominator'}:
            raise ValueError('exact rational fields required')
        numerator, denominator = duration['numerator'], duration['denominator']
        _integer(denominator, 1, MAX_DENOMINATOR, 'denominator')
        _integer(numerator, 1, MAX_QUARTERS * MAX_DENOMINATOR, 'numerator')
        value = Fraction(numerator, denominator)
        if value.numerator != numerator or value.denominator != denominator:
            raise ValueError('fraction must use canonical reduced form')
        events.append(BeatEvent(item['pitch'], value, item['velocity'], item['release_velocity']))
    return validate(tuple(events))

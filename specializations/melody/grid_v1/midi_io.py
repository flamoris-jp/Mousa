"""Bounded, explicit MIDI -> sixteenth-grid conversion and MIDI output.

Only a chosen monophonic track in a constant 4/4 meter is admitted. Source MIDI
bytes stay unchanged. Uniform pitch transposition is recorded, never clamping.
"""
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
import io
import math

import mido


@dataclass(frozen=True)
class Note:
    start: int
    end: int
    pitch: int
    velocity: int


def midi_tokens(path, track_index):
    path = Path(path)
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 1024 * 1024:
        raise ValueError("MIDI must be a regular file at most 1 MiB")
    midi = mido.MidiFile(file=io.BytesIO(path.read_bytes()), clip=False)
    if midi.type not in (0, 1) or not 1 <= midi.ticks_per_beat <= 32767:
        raise ValueError("only SMF0/1 with PPQ timing is supported")
    if type(track_index) is not int or not 0 <= track_index < len(midi.tracks):
        raise ValueError("an explicit valid melody track is required")
    if sum(len(track) for track in midi.tracks) > 100000:
        raise ValueError("MIDI event limit")
    meters = set()
    for track in midi.tracks:
        for event in track:
            if event.type == "time_signature":
                meters.add((event.numerator, event.denominator))
    if meters and meters != {(4, 4)}:
        raise ValueError("this initial task requires constant 4/4")
    active, notes, now = {}, [], 0
    for event in midi.tracks[track_index]:
        now += event.time
        if now > midi.ticks_per_beat * 4 * 256:
            raise ValueError("selected track exceeds 256 bars")
        if getattr(event, "channel", None) == 9 and event.type in ("note_on", "note_off"):
            raise ValueError("drum channel cannot be a melody source")
        if event.type == "pitchwheel" and event.pitch != 0:
            raise ValueError("pitch bends cannot be represented in this task")
        if event.type == "control_change" and event.control in (64, 66) and event.value >= 64:
            raise ValueError("pedal sustain is outside this task")
        if event.type == "note_on" and event.velocity > 0:
            key = (event.channel, event.note)
            if key in active:
                raise ValueError("overlapping instances of the same note")
            active[key] = (now, event.velocity)
        elif event.type == "note_off" or (event.type == "note_on" and event.velocity == 0):
            key = (event.channel, event.note)
            if key not in active:
                raise ValueError("unmatched note-off")
            start, velocity = active.pop(key)
            if now <= start:
                raise ValueError("non-positive note duration")
            notes.append(Note(start, now, event.note, velocity))
    if active or not notes:
        raise ValueError("unterminated notes or empty track")
    notes.sort(key=lambda note: (note.start, note.pitch))
    if any(a.end > b.start for a, b in zip(notes, notes[1:])):
        raise ValueError("chosen track is polyphonic; no top-note flattening is performed")
    unit = Fraction(midi.ticks_per_beat, 4)
    grid_notes = []
    for note in notes:
        start, end = Fraction(note.start) / unit, Fraction(note.end) / unit
        if start.denominator != 1 or end.denominator != 1:
            raise ValueError("off-grid timing: exact sixteenth boundaries required")
        grid_notes.append(Note(int(start), int(end), note.pitch, note.velocity))
    low, high = min(n.pitch for n in notes), max(n.pitch for n in notes)
    if high - low > 24:
        raise ValueError("melody range exceeds the 25-pitch vocabulary")
    shift = 60 - low
    length = math.ceil(grid_notes[-1].end / 16) * 16
    if not 16 <= length <= 4096:
        raise ValueError("token sequence outside initial bounds")
    tokens = [0] * length
    for note in grid_notes:
        tokens[note.start] = note.pitch + shift - 58
        for position in range(note.start + 1, note.end):
            tokens[position] = 1
    return tokens, {
        "track_index": track_index, "source_note_count": len(notes), "source_ppq": midi.ticks_per_beat,
        "meter": "4/4", "meter_defaulted": not bool(meters), "grid": "exact-sixteenth",
        "source_pitch_range": [low, high], "transposition_semitones": shift,
        "normalized_pitch_range": [low + shift, high + shift], "steps": length,
        "velocity_policy": "source retained; model does not learn velocity in v1",
        "initial_rest_steps": next(i for i, token in enumerate(tokens) if token >= 2),
    }


def validate_tokens(tokens, *, max_steps=4096):
    if not isinstance(tokens, list) or not 1 <= len(tokens) <= max_steps:
        raise ValueError("token length")
    sounding = False
    for token in tokens:
        if type(token) is not int or not 0 <= token <= 26:
            raise ValueError("token value")
        if token == 1 and not sounding:
            raise ValueError("HOLD without a sounding note")
        sounding = token != 0
    return tokens


def tokens_to_notes(tokens):
    validate_tokens(tokens)
    notes, start, pitch = [], None, None
    for i, token in enumerate([*tokens, 0]):
        if token != 1:
            if pitch is not None:
                notes.append(Note(start, i, pitch, 80))
            start, pitch = (i, token + 58) if token >= 2 else (None, None)
    return notes


def write_midi(tokens, path, *, bpm=120):
    if not 30 <= bpm <= 240:
        raise ValueError("tempo out of bounds")
    path = Path(path)
    if path.exists():
        raise FileExistsError(path)
    notes = tokens_to_notes(tokens)
    midi = mido.MidiFile(type=1, ticks_per_beat=480)
    meta, track = mido.MidiTrack(), mido.MidiTrack()
    midi.tracks.extend([meta, track])
    meta.extend([mido.MetaMessage("track_name", name="Maidionis music research"),
                 mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm)),
                 mido.MetaMessage("time_signature", numerator=4, denominator=4),
                 mido.MetaMessage("end_of_track", time=0)])
    track.extend([mido.MetaMessage("track_name", name="Generated melody"),
                  mido.Message("program_change", channel=0, program=0)])
    events = []
    for note in notes:
        events.append((note.start * 120, 1, note.pitch, 80))
        events.append((note.end * 120, 0, note.pitch, 0))
    previous = 0
    for tick, on, pitch, velocity in sorted(events):
        track.append(mido.Message("note_on" if on else "note_off", channel=0,
                                  note=pitch, velocity=velocity, time=tick - previous))
        previous = tick
    track.append(mido.MetaMessage("end_of_track", time=len(tokens) * 120 - previous))
    path.parent.mkdir(parents=True, exist_ok=True)
    midi.save(path)
    return {"notes": len(notes), "steps": len(tokens), "bars": len(tokens) / 16,
            "bpm": bpm, "seconds": len(tokens) * 60 / bpm / 4}


def write_preview_wav(tokens, path, *, bpm=120, sample_rate=22050):
    """Neutral sine preview, explicitly not Cantabile/FluidSynth or AI listening."""
    import array
    import wave
    path = Path(path)
    if path.exists():
        raise FileExistsError(path)
    duration = len(tokens) * 60 / bpm / 4
    values = [0.0] * (int((duration + .15) * sample_rate) + 1)
    step_seconds = 60 / bpm / 4
    for note in tokens_to_notes(tokens):
        begin = int(note.start * step_seconds * sample_rate)
        count = int((note.end - note.start) * step_seconds * sample_rate)
        frequency = 440 * 2 ** ((note.pitch - 69) / 12)
        for i in range(count):
            t = i / sample_rate
            envelope = min(1.0, t / .008, (count - i) / sample_rate / .035)
            values[begin + i] = .28 * max(0.0, envelope) * (
                math.sin(2 * math.pi * frequency * t) + .2 * math.sin(4 * math.pi * frequency * t))
    pcm = array.array("h", [round(max(-1, min(1, value)) * 32767) for value in values])
    import sys
    if sys.byteorder != "little":
        pcm.byteswap()
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(pcm.tobytes())

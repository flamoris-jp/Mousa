"""Small, bounded, experimental symbolic music data object.

This note-only prototype is NOT a standard for MIDI interchange, a MIDI parser,
an editable project format, or a frozen Maidionis specialization interface.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re

_PART_RE = re.compile(r"[A-Za-z0-9._-]{1,64}\Z")
_NOTE_FIELDS = frozenset({"part_id", "start_tick", "duration_ticks", "pitch", "velocity"})
_SCORE_FIELDS = frozenset({"ppq", "tempo_us_per_quarter", "notes"})
_MAX_NOTES = 4096
_MAX_TICK = 10_000_000


def _integer(value: object, name: str, low: int, high: int) -> int:
    # bool is an int subclass in Python; reject it explicitly.
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} must be an integer in [{low}, {high}]")
    return value


@dataclass(frozen=True)
class NoteEvent:
    part_id: str
    start_tick: int
    duration_ticks: int
    pitch: int
    velocity: int

    def __post_init__(self) -> None:
        if not isinstance(self.part_id, str) or not _PART_RE.fullmatch(self.part_id):
            raise ValueError("part_id must be 1..64 ASCII letters/digits/dot/underscore/hyphen")
        _integer(self.start_tick, "start_tick", 0, _MAX_TICK)
        _integer(self.duration_ticks, "duration_ticks", 1, _MAX_TICK)
        if self.start_tick + self.duration_ticks > _MAX_TICK:
            raise ValueError("note end exceeds maximum tick")
        _integer(self.pitch, "pitch", 0, 127)
        _integer(self.velocity, "velocity", 1, 127)

    @classmethod
    def from_dict(cls, payload: object) -> "NoteEvent":
        if not isinstance(payload, dict) or payload.keys() != _NOTE_FIELDS:
            raise ValueError("unknown/missing NoteEvent fields")
        return cls(**payload)


@dataclass(frozen=True)
class MusicIR:
    ppq: int
    tempo_us_per_quarter: int
    notes: tuple[NoteEvent, ...]

    def __post_init__(self) -> None:
        _integer(self.ppq, "ppq", 24, 9600)
        _integer(self.tempo_us_per_quarter, "tempo_us_per_quarter", 10000, 6000000)
        if not isinstance(self.notes, tuple) or len(self.notes) > _MAX_NOTES:
            raise ValueError("notes must be a bounded tuple")
        if any(not isinstance(note, NoteEvent) for note in self.notes):
            raise ValueError("notes must contain NoteEvent values")

    def to_dict(self) -> dict:
        return {"ppq": self.ppq, "tempo_us_per_quarter": self.tempo_us_per_quarter,
                "notes": [asdict(note) for note in self.notes]}

    @classmethod
    def from_dict(cls, payload: object) -> "MusicIR":
        if not isinstance(payload, dict) or payload.keys() != _SCORE_FIELDS:
            raise ValueError("unknown/missing MusicIR fields")
        if not isinstance(payload["notes"], list) or len(payload["notes"]) > _MAX_NOTES:
            raise ValueError("notes must be a bounded list")
        return cls(
            ppq=payload["ppq"],
            tempo_us_per_quarter=payload["tempo_us_per_quarter"],
            notes=tuple(NoteEvent.from_dict(note) for note in payload["notes"]),
        )

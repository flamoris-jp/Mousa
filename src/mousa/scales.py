"""Experimental scale/key conditions; no trainer or Cantabile project mutation."""

from dataclasses import dataclass
import hashlib
from importlib.resources import files
import json
import math
import re

from .music_ir import _integer

_ID = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}\Z")
_KEY = re.compile(r"([A-Ga-g])([#b]?)(-1|[0-9])\Z")
_PITCH_CLASSES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def _number(value, name, low, high):
    if type(value) not in (int, float) or not low <= value <= high or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number in [{low}, {high}]")
    return float(value)


def _text(value, name, limit=256):
    if type(value) is not str or not 1 <= len(value) <= limit:
        raise ValueError(f"invalid {name}")


def _closed(value, fields, name):
    if type(value) is not dict or value.keys() != set(fields):
        raise ValueError(f"unknown/missing {name} fields")


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def strict_json(text):
    if type(text) is not str or len(text.encode("utf-8")) > 65536:
        raise ValueError("JSON exceeds 64 KiB")
    try:
        def finite_float(value):
            number = float(value)
            if not math.isfinite(number):
                raise ValueError("nonfinite JSON number")
            return number
        return json.loads(text, object_pairs_hook=_object,
                          parse_float=finite_float,
                          parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    except (RecursionError, json.JSONDecodeError) as error:
        raise ValueError("invalid JSON") from error


@dataclass(frozen=True)
class Scale:
    scale_id: str
    name: str
    intervals_cents: tuple[float, ...]
    period_cents: float
    traditions: tuple[str, ...]
    genre_tags: tuple[str, ...]
    approximation: str
    source_urls: tuple[str, ...]

    def __post_init__(self):
        if type(self.scale_id) is not str or not _ID.fullmatch(self.scale_id):
            raise ValueError("invalid scale_id")
        _text(self.name, "scale name")
        _text(self.approximation, "approximation", 1024)
        _number(self.period_cents, "period_cents", 100, 4800)
        if type(self.intervals_cents) is not tuple or not 1 <= len(self.intervals_cents) <= 64:
            raise ValueError("scale requires 1..64 intervals")
        for value in self.intervals_cents:
            _number(value, "interval", 0, self.period_cents)
        if self.intervals_cents[0] != 0 or self.intervals_cents[-1] >= self.period_cents:
            raise ValueError("root must be 0; repeated endpoint is excluded")
        if any(a >= b for a, b in zip(self.intervals_cents, self.intervals_cents[1:])):
            raise ValueError("scale intervals must be strictly increasing")
        for name in ("traditions", "genre_tags", "source_urls"):
            values = getattr(self, name)
            if type(values) is not tuple or len(values) > 16:
                raise ValueError(f"invalid {name}")
            for value in values:
                _text(value, name, 1024)
        if not self.source_urls or any(not url.startswith("https://") for url in self.source_urls):
            raise ValueError("source_urls requires HTTPS references")

    @classmethod
    def from_dict(cls, payload):
        _closed(payload, cls.__dataclass_fields__, "scale")
        result = dict(payload)
        for name in ("intervals_cents", "traditions", "genre_tags", "source_urls"):
            if type(result[name]) is not list or len(result[name]) > 64:
                raise ValueError(f"invalid {name}")
            result[name] = tuple(result[name])
        return cls(**result)

    def to_dict(self):
        return {name: list(value) if type(value) is tuple else value
                for name, value in vars(self).items()}

    @property
    def digest(self):
        canonical = json.dumps(self.to_dict(), ensure_ascii=True, sort_keys=True,
                               separators=(",", ":"), allow_nan=False)
        return hashlib.sha256(canonical.encode()).hexdigest()


@dataclass(frozen=True)
class Key:
    """Tonic anchor, its micro-offset, and independent concert tuning reference."""

    tonic_midi: int
    tonic_offset_cents: float = 0.0
    reference_a4_hz: float = 440.0

    def __post_init__(self):
        _integer(self.tonic_midi, "tonic_midi", 0, 127)
        _number(self.tonic_offset_cents, "tonic_offset_cents", -100, 100)
        _number(self.reference_a4_hz, "reference_a4_hz", 300, 600)

    @classmethod
    def from_name(cls, name, *, tonic_offset_cents=0.0, reference_a4_hz=440.0):
        match = _KEY.fullmatch(name) if type(name) is str else None
        if match is None:
            raise ValueError("key must include scientific octave, e.g. C4, F#3 or Bb4")
        letter, accidental, octave = match.groups()
        note = (int(octave) + 1) * 12 + _PITCH_CLASSES[letter.upper()]
        note += {"": 0, "#": 1, "b": -1}[accidental]
        return cls(note, tonic_offset_cents, reference_a4_hz)

    @classmethod
    def from_dict(cls, payload):
        _closed(payload, cls.__dataclass_fields__, "key")
        return cls(**payload)

    def to_dict(self):
        return {"tonic_midi": self.tonic_midi,
                "tonic_offset_cents": float(self.tonic_offset_cents),
                "reference_a4_hz": float(self.reference_a4_hz)}


def load_catalogue():
    payload = strict_json(files("mousa").joinpath("data/scales.json").read_text(encoding="utf-8"))
    _closed(payload, ("schema_version", "checked_on", "provenance_note", "scales"), "catalogue")
    if payload["schema_version"] != "mousa.scale-catalogue.experimental.v1":
        raise ValueError("unsupported catalogue version")
    if type(payload["scales"]) is not list or not 1 <= len(payload["scales"]) <= 64:
        raise ValueError("invalid catalogue size")
    scales = tuple(Scale.from_dict(value) for value in payload["scales"])
    if len({scale.scale_id for scale in scales}) != len(scales):
        raise ValueError("duplicate scale_id")
    return {scale.scale_id: scale for scale in scales}


@dataclass(frozen=True)
class ScaleCondition:
    scale: Scale
    key: Key

    def __post_init__(self):
        if type(self.scale) is not Scale or type(self.key) is not Key:
            raise ValueError("condition requires a validated Scale and Key")

    def pitch_cents(self, degree, period=0):
        """Nominal pitch relative to MIDI 0, in the selected A4 tuning system."""
        _integer(degree, "degree", 0, len(self.scale.intervals_cents) - 1)
        _integer(period, "period", -16, 16)
        return (self.key.tonic_midi * 100 + self.key.tonic_offset_cents
                + period * self.scale.period_cents + self.scale.intervals_cents[degree])

    def frequency_hz(self, degree, period=0):
        return self.key.reference_a4_hz * 2 ** ((self.pitch_cents(degree, period) - 6900) / 1200)

    def contains_pitch(self, cents, tolerance_cents=0.01):
        _number(cents, "pitch_cents", -100000, 100000)
        _number(tolerance_cents, "tolerance_cents", 0, 1)
        offset = (cents - self.pitch_cents(0)) % self.scale.period_cents
        return any(min(abs(offset - value), self.scale.period_cents - abs(offset - value))
                   <= tolerance_cents for value in self.scale.intervals_cents)

    def candidate_mask(self, candidates_cents):
        """Eligibility only; callers must handle an all-false mask explicitly."""
        if type(candidates_cents) not in (list, tuple) or len(candidates_cents) > 4096:
            raise ValueError("candidates must be a bounded sequence")
        return tuple(self.contains_pitch(value) for value in candidates_cents)

    def to_dict(self):
        return {"schema_version": "mousa.scale-condition.experimental.v1",
                "scale_id": self.scale.scale_id, "scale_sha256": self.scale.digest,
                "key": self.key.to_dict()}

    @classmethod
    def from_dict(cls, payload, catalogue=None):
        _closed(payload, ("schema_version", "scale_id", "scale_sha256", "key"), "condition")
        if payload["schema_version"] != "mousa.scale-condition.experimental.v1":
            raise ValueError("unsupported condition version")
        _text(payload["scale_id"], "scale_id", 64)
        catalogue = load_catalogue() if catalogue is None else catalogue
        if payload["scale_id"] not in catalogue:
            raise ValueError("unknown scale_id")
        scale = catalogue[payload["scale_id"]]
        if payload["scale_sha256"] != scale.digest:
            raise ValueError("scale digest mismatch")
        return cls(scale, Key.from_dict(payload["key"]))

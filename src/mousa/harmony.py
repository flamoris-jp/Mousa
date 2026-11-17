"""Bounded degree-relative harmony rules, independent of model vocabularies."""

from dataclasses import dataclass, replace
import random

from .degrees import Degree
from .music_ir import _integer
from .scales import ScaleCondition, _closed, _number

SCHEMA = "mousa.chord-progression.experimental.v1"
RULE_ID = "mousa.major-harmony-rules.experimental.v1"
PPQ = 480
MAJOR_CENTS = (0, 200, 400, 500, 700, 900, 1100)
INTERVALS = {
    "major": (0, 4, 7), "minor": (0, 3, 7), "diminished": (0, 3, 6),
    "major7": (0, 4, 7, 11), "minor7": (0, 3, 7, 10),
    "dominant7": (0, 4, 7, 10), "half_diminished7": (0, 3, 6, 10),
}
TRIADS = ("major", "minor", "minor", "major", "major", "minor", "diminished")
SEVENTHS = ("major7", "minor7", "minor7", "major7", "dominant7", "minor7", "half_diminished7")
# Experimental same-function candidate sets; not a claim of equivalent effect.
SUBSTITUTES = ((5, 2), (3,), (0, 5), (1,), (6,), (0, 2), (4,))


@dataclass(frozen=True)
class Chord:
    root: Degree
    quality: str
    duration_ticks: int

    def __post_init__(self):
        if type(self.root) is not Degree or self.root.degree > 6:
            raise ValueError("chord root requires a zero-based major-scale Degree 0..6")
        if type(self.quality) is not str or self.quality not in INTERVALS:
            raise ValueError("unsupported chord quality")
        _integer(self.duration_ticks, "duration_ticks", 1, 32 * 12 * PPQ * 2)

    def to_dict(self):
        return {"root": {"degree": self.root.degree, "period": self.root.period},
                "quality": self.quality, "duration_ticks": self.duration_ticks}

    @classmethod
    def from_dict(cls, payload):
        _closed(payload, ("root", "quality", "duration_ticks"), "chord")
        _closed(payload["root"], ("degree", "period"), "root")
        return cls(Degree(**payload["root"]), payload["quality"], payload["duration_ticks"])


@dataclass(frozen=True)
class Progression:
    chords: tuple[Chord, ...]
    bars: int
    numerator: int = 4
    denominator: int = 4

    def __post_init__(self):
        if type(self.chords) is not tuple or not 1 <= len(self.chords) <= 128:
            raise ValueError("progression requires 1..128 chords")
        if any(type(chord) is not Chord for chord in self.chords):
            raise ValueError("validated Chord values required")
        _integer(self.bars, "bars", 1, 32)
        _integer(self.numerator, "numerator", 1, 12)
        if type(self.denominator) is not int or self.denominator not in (2, 4, 8, 16):
            raise ValueError("supported meter denominators: 2, 4, 8, 16")
        if sum(ch.duration_ticks for ch in self.chords) != self.end_tick:
            raise ValueError("chord durations must exactly fill the declared bars; no padding/truncation")

    @property
    def ticks_per_bar(self):
        return self.numerator * PPQ * 4 // self.denominator

    @property
    def end_tick(self):
        return self.bars * self.ticks_per_bar

    def to_dict(self):
        return {"schema_version": SCHEMA, "ppq": PPQ, "bars": self.bars,
                "numerator": self.numerator, "denominator": self.denominator,
                "chords": [ch.to_dict() for ch in self.chords]}

    @classmethod
    def from_dict(cls, payload):
        _closed(payload, ("schema_version", "ppq", "bars", "numerator", "denominator", "chords"), "progression")
        if payload["schema_version"] != SCHEMA or type(payload["ppq"]) is not int or payload["ppq"] != PPQ:
            raise ValueError("unsupported progression schema/PPQ")
        if type(payload["chords"]) is not list or not 1 <= len(payload["chords"]) <= 128:
            raise ValueError("bounded chord list required")
        return cls(tuple(Chord.from_dict(ch) for ch in payload["chords"]), payload["bars"],
                   payload["numerator"], payload["denominator"])


# Independently encoded elementary teaching examples; no imported song/MIDI.
PATTERNS = {
    "I-V-vi-IV": (0, 4, 5, 3),
    "ii-V-I-I": (1, 4, 0, 0),
    "I-vi-IV-V": (0, 5, 3, 4),
    "I-IV-V-I": (0, 3, 4, 0),
}


def make_progression(pattern="I-V-vi-IV", *, repeats=1):
    if type(pattern) is not str or pattern not in PATTERNS:
        raise ValueError("unknown major progression pattern")
    _integer(repeats, "repeats", 1, 8)
    return Progression(tuple(Chord(Degree(d), TRIADS[d], 4 * PPQ)
                             for d in PATTERNS[pattern] * repeats), 4 * repeats)


def validate_condition(condition):
    """This foundation deliberately supports only exact, concert-440 major."""
    if type(condition) is not ScaleCondition:
        raise ValueError("ScaleCondition required")
    if condition.scale.intervals_cents != MAJOR_CENTS or condition.scale.period_cents != 1200:
        raise ValueError("harmony v1 requires the seven-note 12-TET major scale")
    if condition.key.tonic_offset_cents != 0 or condition.key.reference_a4_hz != 440:
        raise ValueError("harmony v1 requires zero tonic offset and A4=440; no tuning fallback")


def resolve_progression(progression, condition):
    """Resolve explicit quality intervals and reject every off-scale chord tone."""
    if type(progression) is not Progression:
        raise ValueError("Progression required")
    validate_condition(condition)
    rows = []
    start = 0
    for index, chord in enumerate(progression.chords):
        root_cents = condition.pitch_cents(chord.root.degree, chord.root.period)
        pitches = [root_cents + 100 * interval for interval in INTERVALS[chord.quality]]
        if any(not condition.contains_pitch(p) for p in pitches):
            raise ValueError(f"chord {index}: quality conflicts with scale; chromatic/borrowed chords deferred")
        if any(not 0 <= p <= 12700 or p % 100 != 0 for p in pitches):
            raise ValueError(f"chord {index}: unsupported MIDI pitch range")
        rows.append({"index": index, **chord.to_dict(), "start_tick": start,
                     "start_bar": start // progression.ticks_per_bar,
                     "tick_in_bar": start % progression.ticks_per_bar,
                     "midi_notes": [int(p // 100) for p in pitches]})
        start += chord.duration_ticks
    return rows


def vary_progression(progression, condition, *, amount=0.0, seed=0):
    """Change at most floor(amount * internal chords) slots; no quality score.

    Fixed seed gives a nested sequence of changed slots as amount increases.
    First/last chords, all durations, meter, register and slot count are kept.
    """
    resolve_progression(progression, condition)
    amount = _number(amount, "amount", 0, 1)
    _integer(seed, "seed", 0, 2**32 - 1)
    rng = random.Random(seed)
    slots = list(range(1, len(progression.chords) - 1))
    rng.shuffle(slots)
    budget = int(amount * len(slots))
    chords = list(progression.chords)
    changes = []
    # Construct the same entire candidate sequence at every amount.
    for rank, index in enumerate(slots):
        before = chords[index]
        d = before.root.degree
        candidates = []
        if before.quality == TRIADS[d]:
            candidates.append((replace(before, quality=SEVENTHS[d]), "add_seventh"))
        for target in SUBSTITUTES[d]:
            quality = SEVENTHS[target] if len(INTERVALS[before.quality]) == 4 else TRIADS[target]
            candidate = replace(before, root=Degree(target, before.root.period), quality=quality)
            candidates.append((candidate, "substitute_degree"))
        legal = []
        for candidate, operation in candidates:
            trial = list(progression.chords)
            trial[index] = candidate
            try:
                resolve_progression(replace(progression, chords=tuple(trial)), condition)
            except ValueError:
                continue
            legal.append((candidate, operation))
        if not legal:
            continue
        after, operation = rng.choice(legal)
        if rank < budget:
            chords[index] = after
            changes.append({"index": index, "operation": operation,
                            "before": before.to_dict(), "after": after.to_dict()})
    result = replace(progression, chords=tuple(chords))
    resolve_progression(result, condition)
    return result, {"rule_id": RULE_ID, "variation_source": "fixed_rules", "seed": seed,
                    "amount": amount, "eligible_slots": len(slots), "slot_budget": budget,
                    "changed_slots": len(changes), "changes": sorted(changes, key=lambda c: c["index"]),
                    "musical_quality_claim": False}

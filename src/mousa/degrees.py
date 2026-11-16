"""Degree-native music semantics: model labels never mean semitones or Hz."""

from dataclasses import dataclass

from .music_ir import _integer
from .scales import ScaleCondition, _number

STRIDE = 64
OUTPUT_WIDTH = 192
VOCABULARY = 259
TASK_ID = "mousa.absolute-degree.experimental.v1"


@dataclass(frozen=True)
class Degree:
    degree: int
    period: int = 0

    def __post_init__(self):
        _integer(self.degree, "degree", 0, 63)
        _integer(self.period, "period", -1, 1)

    @property
    def label(self):
        return (self.period + 1) * STRIDE + self.degree

    @classmethod
    def from_label(cls, label, degree_count):
        _integer(degree_count, "degree_count", 1, 64)
        _integer(label, "degree label", 0, OUTPUT_WIDTH - 1)
        slot, degree = divmod(label, STRIDE)
        if degree >= degree_count:
            raise ValueError("degree label does not exist in this scale")
        return cls(degree, slot - 1)


def encode_history(history, degree_count):
    _integer(degree_count, "degree_count", 1, 64)
    if type(history) not in (list, tuple) or len(history) != 8:
        raise ValueError("eight preceding degree labels required")
    for label in history:
        Degree.from_label(label, degree_count)
    return [1, 194 + degree_count] + [label + 2 for label in history]


def degree_for_pitch(condition, pitch_cents, tolerance_cents=0.01):
    """Explicit annotation helper; rejects outside notes instead of snapping."""
    if type(condition) is not ScaleCondition:
        raise ValueError("scale condition required")
    _number(pitch_cents, "pitch_cents", -100000, 100000)
    if type(tolerance_cents) not in (int, float) or not 0 <= tolerance_cents <= 0.01:
        raise ValueError("invalid annotation tolerance")
    matches = [Degree(degree, period) for period in (-1, 0, 1)
               for degree in range(len(condition.scale.intervals_cents))
               if abs(condition.pitch_cents(degree, period) - pitch_cents) <= tolerance_cents]
    if len(matches) != 1:
        raise ValueError("pitch is off scale, ambiguous, or outside the three-period degree profile")
    return matches[0]


def decoded_pitches(labels, condition):
    if type(condition) is not ScaleCondition or type(labels) not in (list, tuple) or not 1 <= len(labels) <= 128:
        raise ValueError("bounded degree sequence and scale condition required")
    result = []
    for label in labels:
        value = Degree.from_label(label, len(condition.scale.intervals_cents))
        result.append({"degree": value.degree, "period": value.period,
                       "pitch_cents": condition.pitch_cents(value.degree, value.period),
                       "frequency_hz": condition.frequency_hz(value.degree, value.period)})
    return result


def symbolic_training_fixture():
    """Original ordinal motifs for mechanical fit testing, not musical quality.

    No MIDI, scale interval, tonic, Hz or source composition is read. Variants
    share motif family IDs; every row is train-only and never a held-out claim.
    """
    motifs = {
        "arch": [0, 1, 2, 3, 4, 3, 2, 1],
        "turn": [0, 2, 1, 3, 2, 4, 2, 1],
        "neighbor": [0, 1, 0, 2, 1, 3, 2, 0],
        "period-crossing": [-2, -1, 0, 1, 2, 1, 0, -1],
    }
    rows = []
    for count in (5, 7, 24):
        for family, motif in motifs.items():
            sequence = []
            for offset in (motif * 5):
                period, degree = divmod(offset, count)
                sequence.append(Degree(degree, period).label)
            for index in range(8, len(sequence)):
                rows.append({"family_id": "original-degree-motif:" + family,
                             "degree_count": count, "history": sequence[index-8:index],
                             "target": sequence[index]})
    return {"schema": "mousa.degree-training-data.experimental.v1", "task_id": TASK_ID,
            "provenance": "original symbolic motifs; train-only mechanics; Apache-2.0",
            "rows": rows}

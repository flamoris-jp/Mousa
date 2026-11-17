"""Bounded experimental joint degree/rhythm semantics, not a quality judge."""
import math
from collections import Counter
from .degrees import Degree

TASK_ID = 'mousa.degree-rhythm.experimental.v1'
SIZES = (192, 48, 48, 49, 4, 2)
OFFSETS = (119, 311, 359, 407, 456, 460)
UNIT_TICKS = 40
BAR_UNITS = 48
VELOCITIES = (40, 64, 88, 112)


def integer(x, low, high):
    if type(x) is not int or not low <= x <= high:
        raise ValueError('integer out of range')
    return x


def validate_event(event, count):
    if type(event) not in (tuple, list) or len(event) != 6:
        raise ValueError('six event labels required')
    for v, size in zip(event, SIZES):
        integer(v, 0, size - 1)
    Degree.from_label(event[0], count)
    if event[2] > event[1] or event[3] != event[1] - event[2]:
        raise ValueError('duration/rest must sum to IOI')


def encode(history, count, position, task):
    integer(count, 1, 64); integer(position, 0, 47); integer(task, 0, 5)
    if type(history) not in (tuple, list) or len(history) != 8:
        raise ValueError('eight preceding events required')
    result = [task + 1, count + 6, position + 71]
    for event in history:
        validate_event(event, count)
        result.extend(v + offset for v, offset in zip(event, OFFSETS))
    return result


def categorical(probabilities, rng):
    if not probabilities or any(not math.isfinite(p) or p < 0 for p in probabilities):
        raise ValueError('invalid probabilities')
    total = sum(probabilities)
    if total <= 0:
        raise ValueError('empty legal support')
    u = rng.random() * total
    for i, p in enumerate(probabilities):
        u -= p
        if u < 0:
            return i
    return max(i for i,p in enumerate(probabilities) if p > 0)


def sample_event(probabilities, count, remaining, rng):
    """Sample learned distributions conditioned on deterministic validity.

    IOI limited only by remaining piece length (ties may cross bar boundaries).
    Duration/rest use their learned product on legal pairs, not a fixed gate.
    Phrase is an auxiliary learned boundary proposal, never a quality label.
    """
    integer(remaining, 1, 384)
    if len(probabilities) != 6 or any(len(p) != n for p,n in zip(probabilities,SIZES)):
        raise ValueError('task probability dimensions')
    p = [list(x) for x in probabilities]
    for k in range(192):
        if k % 64 >= count:
            p[0][k] = 0.0
    degree = categorical(p[0], rng)
    ioi = categorical([x if k < remaining else 0.0 for k,x in enumerate(p[1])], rng)
    duration = categorical([p[2][d] * p[3][ioi-d] if d <= ioi else 0.0 for d in range(48)], rng)
    event = [degree, ioi, duration, ioi-duration, categorical(p[4],rng), categorical(p[5],rng)]
    validate_event(event,count)
    return event


def descriptors(events):
    """Descriptive proxies only; none establishes naturalness or quality."""
    if not events:
        raise ValueError('empty sequence')
    iois = [e['labels'][1]+1 for e in events]
    counts = Counter(iois); n = len(events)
    ent = -sum(v/n * math.log2(v/n) for v in counts.values())
    pairs = [(e['labels'][1],e['labels'][2],e['labels'][3]) for e in events]
    bigrams = list(zip(pairs,pairs[1:]))
    return {'notes':n, 'ioi_entropy_bits':ent, 'distinct_rhythm_triples':len(set(pairs)),
            'adjacent_rhythm_repeat_fraction':sum(a==b for a,b in bigrams)/max(1,len(bigrams)),
            'silence_fraction':sum(e['labels'][3] for e in events)/sum(iois),
            'offbeat_onset_fraction':sum(e['onset_unit']%12 != 0 for e in events)/n,
            'triplet_grid_nonstraight_fraction':sum(e['onset_unit']%3 != 0 and e['onset_unit']%4 == 0 for e in events)/n,
            'accent_classes':len({e['labels'][4] for e in events}),
            'phrase_proposals':sum(e['labels'][5] for e in events)}

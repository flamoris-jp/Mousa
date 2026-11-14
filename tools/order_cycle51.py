"""Exploratory order-sensitive recurrence, not musical quality or plagiarism."""
from collections import defaultdict
from random import Random


def pitch_groups(notes):
    groups = defaultdict(list)
    for note in notes:
        start, pitch = note['start'], note['pitch']
        if type(start) is not int or start < 0 or type(pitch) is not int or not 0 <= pitch <= 127:
            raise ValueError('invalid start or MIDI pitch')
        groups[start].append(pitch)
    return tuple(tuple(sorted(groups[start])) for start in sorted(groups))


def recurrence(tokens, width):
    if type(width) is not int or width < 1:
        raise ValueError('width must be a positive integer')
    count = len(tokens) - width + 1
    if count <= 0:
        return None
    windows = [tuple(tokens[i:i + width]) for i in range(count)]
    return (count - len(set(windows))) / count


def shuffled_recurrences(tokens, width, seeds=range(51000, 51100)):
    values = []
    for seed in seeds:
        copy = list(tokens)
        Random(seed).shuffle(copy)
        values.append(recurrence(copy, width))
    return values

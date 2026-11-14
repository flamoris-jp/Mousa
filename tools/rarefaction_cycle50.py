"""Exploratory exact note-count normalization of already-observed outputs."""
from collections import Counter
from fractions import Fraction
from math import comb


def expected_distinct(pitches, k):
    """Expected distinct exact MIDI pitches in uniform k-note subsets.

    Ignores order, time, velocity and harmony. None means not enough notes,
    not zero diversity. No random sampling or source modification occurs.
    """
    if type(k) is not int or k < 0:
        raise ValueError('k must be a nonnegative integer')
    if any(type(p) is not int or not 0 <= p <= 127 for p in pitches):
        raise ValueError('MIDI pitches must be integer 0..127')
    n = len(pitches)
    if n < k:
        return None
    denominator = comb(n, k)
    return sum((1 - Fraction(comb(n - c, k), denominator)
                for c in Counter(pitches).values()), Fraction(0))

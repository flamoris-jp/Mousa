import importlib
import sys
import unittest
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
from unittest.mock import patch

with patch.object(sys, 'path', [str(Path(__file__).resolve().parents[1] / 'tools'), *sys.path]):
    metric = importlib.import_module('rarefaction_cycle50')


class Rarefaction50Tests(unittest.TestCase):
    def test_exhaustive_subsets(self):
        for n in range(6):
            for pitches in product(range(3), repeat=n):
                for k in range(n + 1):
                    counts = [len(set(pitches[i] for i in indices))
                              for indices in combinations(range(n), k)]
                    self.assertEqual(metric.expected_distinct(pitches, k),
                                     Fraction(sum(counts), len(counts)))

    def test_ineligible_not_zero(self):
        self.assertIsNone(metric.expected_distinct([60], 2))
        self.assertEqual(metric.expected_distinct([], 0), 0)
        self.assertEqual(metric.expected_distinct([60, 60, 72], 3), 2)

    def test_validation(self):
        for k in [-1, True, 1.5]:
            with self.assertRaises(ValueError):
                metric.expected_distinct([60], k)
        for p in [-1, 128, True, 1.5]:
            with self.assertRaises(ValueError):
                metric.expected_distinct([p], 1)

    def test_source_unchanged(self):
        pitches = [60, 64, 60, 72]
        before = pitches[:]
        metric.expected_distinct(pitches, 3)
        self.assertEqual(pitches, before)

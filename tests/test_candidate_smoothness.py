import importlib.util
from pathlib import Path
import unittest
from fractions import Fraction

spec=importlib.util.spec_from_file_location('smoothness',Path(__file__).resolve().parents[1]/'tools/compare_candidate_smoothness.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class SmoothnessTests(unittest.TestCase):
    def test_sparse_not_winner(self):
        self.assertIsNone(module.features([0,0]))
        self.assertIsNone(module.features([2,1,1,0]))
    def test_onsets_not_holds(self):
        f=module.features([2,1,1,15,0,15])
        self.assertEqual(f['leap_fraction'],Fraction(1,2))
        self.assertEqual(f['zero_interval_fraction'],Fraction(1,2))
        self.assertEqual(f['unique_pitches'],2)
        self.assertEqual(f['onsets'],3)
    def test_octave_not_above_octave(self):
        self.assertEqual(module.features([2,14])['leap_fraction'],0)

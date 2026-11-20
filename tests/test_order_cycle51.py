import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from order_cycle51 import pitch_groups, recurrence, shuffled_recurrences

class OrderCycle51Tests(unittest.TestCase):
    def test_known_windows(self):
        self.assertEqual(recurrence('ABABAB', 2), 3/5)
        self.assertEqual(recurrence('ABABAB', 4), 1/3)
        self.assertEqual(recurrence('AAAAAA', 2), 4/5)
        self.assertEqual(recurrence('ABCDEF', 2), 0)
    def test_order_matters_inventory_does_not_change(self):
        self.assertEqual(sorted('ABABAB'), sorted('AAABBB'))
        self.assertNotEqual(recurrence('ABABAB', 2), recurrence('AAABBB', 2))
    def test_sparse_and_invalid(self):
        self.assertIsNone(recurrence([], 2))
        self.assertIsNone(recurrence('ABC', 4))
        self.assertEqual(recurrence('ABCD', 4), 0)
        for w in (0, -1, True, 1.5):
            with self.assertRaises(ValueError): recurrence('ABCD', w)
    def test_simultaneous_canonical_and_multiplicity(self):
        notes = [{'start': 2, 'pitch': 60}, {'start': 0, 'pitch': 64}, {'start': 0, 'pitch': 60}, {'start': 0, 'pitch': 60}]
        before = repr(notes)
        self.assertEqual(pitch_groups(notes), ((60,60,64),(60,)))
        self.assertEqual(pitch_groups(notes), pitch_groups(list(reversed(notes))))
        self.assertEqual(repr(notes), before)
        with self.assertRaises(ValueError): pitch_groups([{'start': 0,'pitch':128}])
    def test_controls_repeat_and_do_not_mutate(self):
        tokens = list('ABABAB')
        before = tokens[:]
        a = shuffled_recurrences(tokens, 2)
        self.assertEqual(a, shuffled_recurrences(tokens, 2))
        self.assertEqual(tokens, before)
        self.assertEqual(len(a), 100)
        self.assertTrue(all(0 <= x <= 1 for x in a))
        self.assertEqual(shuffled_recurrences('AAAAAA', 2), [4/5]*100)

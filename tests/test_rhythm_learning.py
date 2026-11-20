import random
import unittest
from mousa.rhythm_learning import encode, sample_event, validate_event, SIZES

class RhythmTests(unittest.TestCase):
    def test_codec(self):
        event=[64,5,4,1,2,0]
        row=encode([event]*8,7,0,0)
        self.assertEqual(len(row),51)
        self.assertEqual(row[:9],[1,13,71,183,316,363,408,458,460])
    def test_invalid(self):
        for event in ([64,5,5,1,2,0],[71,5,4,1,2,0],[64,True,0,1,2,0]):
            with self.assertRaises(ValueError):validate_event(event,7)
    def test_constraints(self):
        p=[[1/n]*n for n in SIZES]
        rng=random.Random(42)
        for remaining in range(1,49):
            event=sample_event(p,7,remaining,rng)
            validate_event(event,7)
            self.assertLessEqual(event[1]+1,remaining)
    def test_learned_duration_rest(self):
        p=[[0.0]*n for n in SIZES]
        for task,index in enumerate([64,11,7,4,3,1]):p[task][index]=1
        self.assertEqual(sample_event(p,7,48,random.Random(1)),[64,11,7,4,3,1])
    def test_empty_support(self):
        with self.assertRaises(ValueError):sample_event([[0]*n for n in SIZES],7,48,random.Random(1))

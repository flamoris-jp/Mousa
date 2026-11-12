import random
from pathlib import Path
import sys
import tracemalloc
import unittest
TOOLS=Path(__file__).resolve().parents[1]/'tools';sys.path.insert(0,str(TOOLS))
try:
    from bounded_interval_similarity import similarity
    from compare_onset_gate_models import similarity as old
finally:sys.path.pop(0)

class BoundedSimilarityTests(unittest.TestCase):
    def test_random_exact_parity(self):
        rng=random.Random(3001)
        for _ in range(40):
            a=[rng.randrange(48,84) for _ in range(rng.randrange(1,65))]
            b=[rng.randrange(48,84) for _ in range(rng.randrange(1,65))]
            self.assertEqual(similarity(a,b),old(a,b))
            self.assertEqual(similarity(a,b),similarity(b,a))
        a=[60,61]*256+[60];b=[61,60]*256+[61]
        self.assertEqual(similarity(a,b),old(a,b))

    def test_long_formula_and_threshold(self):
        self.assertEqual(similarity([60]*1394,[72]*1394),1)
        self.assertEqual(similarity([60]*2049,[61]*1025),.5)
        self.assertEqual(similarity([60]*1001,[70]*801),.8)
        self.assertLess(similarity([60]*1001,[70]*800),.8)
        self.assertIsNone(similarity([60],[60,61]))

    def test_bounds_and_small_shortside_memory(self):
        with self.assertRaises(ValueError):similarity([60]*2050,[60]*2)
        with self.assertRaises(ValueError):similarity([True,60],[60,61])
        a=[60]*2049;b=[60]*33
        tracemalloc.start()
        try:
            similarity(a,b);_,peak=tracemalloc.get_traced_memory()
        finally:tracemalloc.stop()
        # Wide margin for integer/list overhead; a full DP table is much larger.
        self.assertLess(peak,300000)

if __name__=='__main__':unittest.main()

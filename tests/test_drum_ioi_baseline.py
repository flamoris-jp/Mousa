from fractions import Fraction
import unittest
from mousa.drum_ioi_baseline import DrumIOIModel, SUPPORT_SIZE, MAX_IOI

class DrumIOITests(unittest.TestCase):
    def test_normalization_and_formula(self):
        m=DrumIOIModel([[(0,36),(120,38),(120,42)],[(240,38)]],context=True)
        self.assertEqual(m.probability(120,previous_instrument=36),(1+4*Fraction(2,4)+Fraction(1,SUPPORT_SIZE))/6)
        for previous in (None,36,38,127):
            self.assertEqual(sum((m.probability(dt,previous_instrument=previous) for dt in range(SUPPORT_SIZE)),Fraction()),1)
        self.assertGreater(m.probability(MAX_IOI,previous_instrument=36),0)
    def test_unknown_backoff_and_reset(self):
        works=[[(0,36),(120,38)],[(240,42)]]
        m=DrumIOIModel(works,context=True);base=DrumIOIModel(works)
        self.assertEqual(dict(m.contexts),{36:{120:1}})
        for dt in (0,120,240,MAX_IOI):
            self.assertEqual(m.probability(dt,previous_instrument=127),base.probability(dt))
        a=m.evaluate([(240,42)]);b=m.evaluate([(240,42)])
        self.assertEqual(a,b);self.assertEqual(a['initial_context_events'],1)
        self.assertEqual(m.n,3)
    def test_bad_args_fail_without_clipping(self):
        for works in ([],[[]],[[(True,36)]],[[(MAX_IOI+1,36)]],[[(1,128)]],[[(1,True)]], [[(1,36)]]*21, [[(1,36)]*4097]):
            with self.assertRaises(ValueError):DrumIOIModel(works)
        m=DrumIOIModel([[(1,36)]])
        with self.assertRaises(ValueError):m.probability(-1)
        with self.assertRaises(ValueError):m.probability(1,previous_instrument=True)
        with self.assertRaises(ValueError):m.evaluate([])
        with self.assertRaises(ValueError):DrumIOIModel([[(1,36)]],context=1)
    def test_count_shrinkage_is_not_fixed_probability_mix(self):
        m=DrumIOIModel([[(0,36),(1,38)]],context=True)
        p=m.probability(1,previous_instrument=36)
        smoothed_local=(1+Fraction(1,SUPPORT_SIZE))/2
        global_p=(1+Fraction(1,SUPPORT_SIZE))/3
        self.assertNotEqual(p,Fraction(1,5)*smoothed_local+Fraction(4,5)*global_p)

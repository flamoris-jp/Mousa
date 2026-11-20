from fractions import Fraction
import unittest
from mousa.groove_cycle40_weighted import WeightedGrooveMarginal,equal_group_weights,CONDITIONS
from mousa.drum_ioi_60work_profile import DrumIOI60WorkProfile

class Groove40WeightedTests(unittest.TestCase):
    works=[[(0,36),(120,38)],[(121,42),(240,36),(30720,38),(119,42)]]
    def test_equal_group_mass_and_complete_work_weight(self):
        weights=equal_group_weights([2,4],['a','b']);self.assertEqual(weights,[Fraction(3,2),Fraction(3,4)])
        self.assertEqual([weights[0]*2,weights[1]*4],[3,3])
        m=WeightedGrooveMarginal(self.works,weights,condition='unigram')
        self.assertEqual(m.n,6);self.assertEqual(m.counts[0],Fraction(3,2));self.assertEqual(m.counts[30720],Fraction(3,4));self.assertEqual(m.work_count,2)
    def test_raw_probability_and_nll_parity(self):
        for c in CONDITIONS:
            a=WeightedGrooveMarginal(self.works,[Fraction(1)]*2,condition=c);b=DrumIOI60WorkProfile(self.works,condition=c)
            for dt in (0,1,119,120,121,30719,30720):self.assertEqual(a.probability(dt),b.probability(dt))
            for work in self.works:self.assertEqual(a.evaluate(work),b.evaluate(work))
    def test_weighted_normalization_endpoint_and_support(self):
        for c in CONDITIONS:
            m=WeightedGrooveMarginal(self.works,equal_group_weights([2,4],['a','b']),condition=c)
            self.assertEqual(sum((m.probability(dt) for dt in range(30721)),Fraction()),1)
            self.assertGreater(m.probability(30719),0)
            if c=='quotient_residual':self.assertEqual(m.probability(30720),(Fraction(3,4)+Fraction(1,30721))/7)
            self.assertEqual(m.evaluate(self.works[0]),m.evaluate(self.works[0]))
    def test_no_unintended_mass_or_bound_changes(self):
        for weights in ([Fraction(2)]*2,[1,1],[Fraction(-1),Fraction(2)],[]):
            with self.assertRaises(ValueError):WeightedGrooveMarginal(self.works,weights,condition='unigram')
        with self.assertRaises(ValueError):equal_group_weights([True],['a'])
        with self.assertRaises(ValueError):WeightedGrooveMarginal(self.works,[Fraction(1)]*2,condition='exact_k4')
        m=WeightedGrooveMarginal(self.works,[Fraction(1)]*2,condition='unigram')
        self.assertFalse(hasattr(m,'generate'))
        for dt in (-1,True,30721):
            with self.assertRaises(ValueError):m.probability(dt)

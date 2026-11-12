import unittest
import sys
from pathlib import Path
from fractions import Fraction
from math import log
from mousa.initial_rest_group_model import InitialRestGroupModel

old_path=list(sys.path)
try:
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
    from compare_initial_rest_groups import prediction,outside_mass,preflight,CONDITIONS,conditional_initial_signature
finally:
    sys.path[:]=old_path


class InitialRestDriverTests(unittest.TestCase):
    def test_synthetic_actual17_preflight(self):
        self.assertEqual(preflight()['largest_work_count'],17)
        self.assertEqual(len(CONDITIONS),6)

    def test_likelihood_decomposition(self):
        t=((0,96,80,0),);seq=[(12672,60,t),(96,61,t)]
        m=InitialRestGroupModel([seq],first_limit=65536)
        r=prediction(m,seq)
        self.assertEqual(r['groups'],2)
        self.assertAlmostEqual(r['first_nll'],-log(m.probability(12672)))
        self.assertAlmostEqual((r['first_nll']+r['later_nll_sum'])/2,m.evaluate(seq)['nll_per_group_delta'])
        one=prediction(m,[seq[0]])
        self.assertEqual(one['later_groups'],0);self.assertIsNone(one['later_nll_per_group'])

    def test_initial_conditioning_cancels_new_outside_count(self):
        t=((0,96,80,0),)
        before=InitialRestGroupModel([[(0,60,t)],[(384,62,t)]],first_limit=65536)
        after=InitialRestGroupModel([[(0,60,t)],[(384,62,t)],[(12672,48,t)]],first_limit=65536)
        self.assertEqual(conditional_initial_signature(before),conditional_initial_signature(after))
        self.assertNotEqual(outside_mass(before),outside_mass(after))

    def test_outside_mass_exact(self):
        t=((0,96,80,0),)
        for cap in (12288,65536):
            m=InitialRestGroupModel([[(0,60,t)],[(cap,60,t)]],first_limit=cap)
            r=outside_mass(m,3)
            expected=1-sum(m.probability(i) for i in range(3))
            self.assertEqual(Fraction(r['numerator'],r['denominator']),expected)
        with self.assertRaises(ValueError):outside_mass(m,65536)


if __name__=='__main__':unittest.main()

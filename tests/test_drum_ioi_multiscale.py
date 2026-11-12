from fractions import Fraction
import unittest
from mousa.drum_ioi_baseline import DrumIOIModel,SUPPORT_SIZE,MAX_IOI
from mousa.drum_ioi_multiscale import MultiscaleDrumIOI,CONDITIONS

class MultiscaleDrumTests(unittest.TestCase):
    works=[[(0,36),(119,38),(120,42)],[(30720,36),(241,38)]]
    def test_exact_control_parity_and_reset(self):
        for new,context in [('unigram',False),('exact_k4',True)]:
            a=MultiscaleDrumIOI(self.works,condition=new);b=DrumIOIModel(self.works,context=context)
            for prev in (None,36,38,127):
                for dt in (0,1,119,120,121,30719,30720):self.assertEqual(a.probability(dt,previous_instrument=prev),b.probability(dt,previous_instrument=prev))
            for work in self.works:self.assertEqual(a.evaluate(work)['sum_nll_nats'],b.evaluate(work)['sum_nll_nats'])
            self.assertEqual(sum(a.context_totals.values()),3)
    def test_all_conditions_normalized_with_endpoint(self):
        for condition in CONDITIONS:
            m=MultiscaleDrumIOI(self.works,condition=condition)
            for previous in (36,127):
                self.assertEqual(sum((m.probability(dt,previous_instrument=previous) for dt in range(SUPPORT_SIZE)),Fraction()),1)
                self.assertGreater(m.probability(30719,previous_instrument=previous),0)
            if condition.startswith('quotient'):
                self.assertEqual(m.probability(30720), (1+Fraction(1,SUPPORT_SIZE))/6)
    def test_lossless_decomposition_unknown_and_bad_args(self):
        for dt in (0,119,120,121,30719,30720):
            q,r=divmod(dt,120);self.assertEqual(q*120+r,dt)
        m=MultiscaleDrumIOI(self.works,condition='exact_k32')
        self.assertEqual(m.probability(17,previous_instrument=127),m.probability(17))
        self.assertEqual(m.evaluate(self.works[0]),m.evaluate(self.works[0]))
        for dt in (True,-1,30721,1.1):
            with self.assertRaises(ValueError):m.probability(dt)
        with self.assertRaises(ValueError):m.probability(1,previous_instrument=True)
        with self.assertRaises(ValueError):MultiscaleDrumIOI(self.works,condition='choose_best')

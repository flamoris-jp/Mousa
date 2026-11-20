from fractions import Fraction
from collections import Counter,defaultdict
import unittest
from mousa.drum_ioi_35work_profile import DrumIOI35WorkProfile
from mousa.drum_ioi_multiscale import MultiscaleDrumIOI,CONDITIONS
from mousa.drum_ioi_baseline import SUPPORT_SIZE

class Groove35WorkTests(unittest.TestCase):
    def works(self,n):return [[(i%3,36+i%3),(120+i,38),(30720,42)] for i in range(n)]
    def test_old_profile_exact_probability_and_nll_parity(self):
        for n in (1,12,20):
            w=self.works(n)
            for c in CONDITIONS:
                a=DrumIOI35WorkProfile(w,condition=c);b=MultiscaleDrumIOI(w,condition=c)
                for prev in (None,36,38,127):
                    for dt in (0,119,120,149,30719,30720):self.assertEqual(a.probability(dt,previous_instrument=prev),b.probability(dt,previous_instrument=prev))
                self.assertEqual(a.evaluate(w[0]),b.evaluate(w[0]))
    def test35_reset_counts_and_normalization(self):
        w=self.works(35);counts=Counter(dt for work in w for dt,k in work);local=defaultdict(Counter)
        for work in w:
            for (_,k),(dt,_) in zip(work,work[1:]):local[k][dt]+=1
        for c in CONDITIONS:
            m=DrumIOI35WorkProfile(w,condition=c)
            self.assertEqual(m.base.counts,counts);self.assertEqual(m.base.contexts,local)
            self.assertEqual(m.base.n,105);self.assertEqual(sum(m.base.context_totals.values()),70)
            self.assertEqual(sum((m.probability(dt,previous_instrument=36) for dt in range(SUPPORT_SIZE)),Fraction()),1)
        with self.assertRaises(ValueError):MultiscaleDrumIOI(w,condition='unigram')
    def test_no_silent_limit_expansion_or_sampler(self):
        for w in ([],self.works(36),[[(0,36)]*4097],[[(0,36)]]+[[(-1,36)]], [[(0,36)]*1000]*31):
            with self.assertRaises(ValueError):DrumIOI35WorkProfile(w,condition='unigram')
        m=DrumIOI35WorkProfile(self.works(21),condition='unigram')
        self.assertFalse(isinstance(m,MultiscaleDrumIOI));self.assertFalse(hasattr(m,'generate'))

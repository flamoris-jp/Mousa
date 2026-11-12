from fractions import Fraction
import unittest
from mousa.drum_ioi_35work_profile import DrumIOI35WorkProfile
from mousa.drum_ioi_60work_profile import DrumIOI60WorkProfile
from mousa.drum_ioi_multiscale import CONDITIONS

class Groove60ProfileTests(unittest.TestCase):
    def fixture(self,n):return [[(i%3,36),(120+i,38),(30720,42)] for i in range(n)]
    def test_old_profile_parity(self):
        for n in (1,12,35):
            for c in CONDITIONS:
                a=DrumIOI35WorkProfile(self.fixture(n),condition=c);b=DrumIOI60WorkProfile(self.fixture(n),condition=c)
                for prev in (None,36,38,127):
                    for dt in (0,119,120,30720):self.assertEqual(a.probability(dt,previous_instrument=prev),b.probability(dt,previous_instrument=prev))
                self.assertEqual(a.evaluate(self.fixture(1)[0]),b.evaluate(self.fixture(1)[0]))
    def test_new_bound_normalization_and_chunk_reset(self):
        for c in CONDITIONS:
            m=DrumIOI60WorkProfile(self.fixture(60),condition=c)
            self.assertEqual(m.base.n,180);self.assertEqual(sum(m.base.context_totals.values()),120)
            self.assertEqual(sum((m.probability(dt,previous_instrument=36) for dt in range(30721)),Fraction()),1)
        m=DrumIOI60WorkProfile([[(0,36)]*2000]*30,condition='unigram')
        self.assertEqual(m.base.n,60000);self.assertEqual(sum(m.base.context_totals.values()),59970)
        for w in (self.fixture(61),[[(0,36)]*1001]*60,[[(0,36)]*4097]):
            with self.assertRaises(ValueError):DrumIOI60WorkProfile(w,condition='unigram')
        with self.assertRaises(ValueError):DrumIOI35WorkProfile(self.fixture(60),condition='unigram')

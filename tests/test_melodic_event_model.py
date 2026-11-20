import unittest
from mousa.melodic_event_model import MelodicEventModel
from mousa.factorized_baseline import FixedEventModel,PITCHES,DURATIONS

class MelodicTests(unittest.TestCase):
    def test_normalized_probabilities(self):
        for relative in (False,True):
            for prior in ('uniform','empirical','typed'):
                m=MelodicEventModel([[(2,1),(-1,68),(4,2)]],relative=relative,duration_prior=prior)
                for history in ([],[(26,1)],[(-1,2)]):
                    p,d=m.distributions(history)
                    self.assertAlmostEqual(sum(p.values()),1)
                    for group in d.values():self.assertAlmostEqual(sum(group.values()),1)
    def test_uniform_absolute_reproduces_factorized_control_nll(self):
        train=[[(2,1),(4,2),(-1,4),(2,1)]];test=[(3,2),(4,1),(-1,3)]
        expected=FixedEventModel(train,factorized=True).evaluate(test)
        actual=MelodicEventModel(train).evaluate(test)
        self.assertAlmostEqual(actual['nll_per_event'],expected['nll_per_event'])
    def test_rest_durations_not_used_as_note_prior(self):
        m=MelodicEventModel([[(2,1),(-1,68),(3,1)]],duration_prior='typed')
        p,d=m.distributions([])
        self.assertGreater(d[False][1],d[False][68]);self.assertGreater(d[True][68],d[True][1])
    def test_relative_encoding_skips_rests(self):
        m=MelodicEventModel([[(2,1),(3,1)]],relative=True)
        encoded,last=m.encode([(5,1),(-1,4),(7,2)])
        self.assertEqual(encoded,[(-9,1),(-99,4),(2,2)]);self.assertEqual(last,7)
    def test_generation_bounds_and_repeat(self):
        for relative in (False,True):
            m=MelodicEventModel([[(2,1),(3,1),(-1,4)]],relative=relative,duration_prior='typed')
            a=m.generate(7);self.assertEqual(a,m.generate(7));self.assertEqual(len(a['tokens']),128)
    def test_no_source_boundary_context(self):
        m=MelodicEventModel([[(2,1)],[(3,1)]],relative=True)
        self.assertEqual(len(m.tables[1]),0)
    def test_invalid_variant(self):
        with self.assertRaises(ValueError):MelodicEventModel([[(2,1)]],duration_prior='test-fitted')

import unittest
from mousa.factorized_baseline import FixedEventModel, onset_phrases, PITCHES, DURATIONS

class FactorizedTests(unittest.TestCase):
    def test_probabilities_sum_to_one(self):
        for factorized in (False,True):
            m=FixedEventModel([[(2,2),(3,4),(2,2)]],factorized=factorized)
            d=m.distribution([])
            self.assertAlmostEqual(sum(m.probability((p,t),d) for p in PITCHES for t in DURATIONS),1)
    def test_separate_marginals_support_unseen_pair(self):
        seq=[(2,2)]*3+[(3,4)]*3
        j=FixedEventModel([seq]);f=FixedEventModel([seq],factorized=True)
        self.assertGreater(f.probability((2,4),f.distribution([])),j.probability((2,4),j.distribution([])))
    def test_metrics_same_denominator_and_support(self):
        for f in (False,True):
            r=FixedEventModel([[(2,2)]],factorized=f).evaluate([(3,4),(2,2)])
            self.assertEqual(r['events'],2);self.assertEqual(r['support_size'],3328)
    def test_transposition_invariance(self):
        a=[x for p in range(2,10) for x in (p,1)]
        b=[x for p in range(4,12) for x in (p,1)]
        self.assertEqual(onset_phrases(a),onset_phrases(b))
    def test_rhythm_and_gap_matter(self):
        a=list(range(2,10));b=[2,0]+list(range(3,10))
        self.assertNotEqual(onset_phrases(a),onset_phrases(b))
    def test_guard_is_reproducible_and_blocks_exact_phrase(self):
        source=list(range(2,10))*4
        seq=[(p,1) for p in source]
        m=FixedEventModel([seq],prior=.000001)
        a=m.generate(7,source_grids=[source],guard=True)
        self.assertEqual(a,m.generate(7,source_grids=[source],guard=True))
        self.assertEqual(a['status'],'blocked')
        self.assertGreater(a['rejections'],0)
        self.assertFalse(set(onset_phrases(a['tokens'])) & set(onset_phrases(source)))
    def test_reject_long_duration(self):
        with self.assertRaises(ValueError):FixedEventModel([[(2,129)]])
    def test_candidate_length(self):
        for f in (False,True):
            r=FixedEventModel([[(2,2),(3,4)]],factorized=f).generate(17)
            self.assertEqual(len(r['tokens']),128)

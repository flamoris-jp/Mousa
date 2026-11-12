from fractions import Fraction as F
import random
import unittest
from mousa.duration_support import DurationSupport, DurationSupportError


class DurationSupportTests(unittest.TestCase):
    def test_fixed_normalization_formula(self):
        m=DurationSupport([F(1),F(1),F(2)],prior_mass=F(2))
        self.assertEqual(m.support_size,12288)
        self.assertEqual(m.probability(F(1)),(2+F(2,12288))/5)
        self.assertEqual(sum((m.probability(F(t,384)) for t in range(1,12289)),F(0)),1)
        self.assertEqual(len(m.counts),2)

    def test_unseen_and_oov_distinct(self):
        m=DurationSupport([F(1)])
        self.assertEqual(m.classify(F(1)),'seen')
        self.assertEqual(m.classify(F(1,384)),'unseen')
        self.assertGreater(m.probability(F(1,384)),0)
        self.assertEqual(m.classify(F(1,5)),'incompatible_grid')
        self.assertEqual(m.classify(F(33)),'outside_duration_range')
        for d in (F(1,5),F(33)):
            with self.assertRaises(DurationSupportError):m.probability(d)
            with self.assertRaises(DurationSupportError):DurationSupport([d])

    def test_empty_prior_uniform(self):
        m=DurationSupport()
        self.assertEqual(m.probability(F(32)),F(1,12288))
        self.assertEqual(m.sample(random.Random(1),remaining_ticks=1),F(1,384))

    def test_generation_legal_and_reproducible(self):
        m=DurationSupport([F(30),F(1),F(1,384)],prior_mass=F(3,2))
        def run():
            rng=random.Random(71)
            remaining=777;out=[]
            while remaining:
                d=m.sample(rng,remaining_ticks=remaining,max_duration_ticks=100)
                ticks=m.to_ticks(d)
                self.assertLessEqual(ticks,min(100,remaining))
                self.assertGreaterEqual(ticks,1)
                out.append(d);remaining-=ticks
            return out
        self.assertEqual(run(),run())
        self.assertEqual(sum(run(),F(0)),F(777,384))

    def test_sparse_restricted_sampling_exact_weights(self):
        # PPQ2: legal ticks1,2; counts(1)=1, prior=1 over2ticks.
        # Integer weights are3,1. Enumerate RNG branch draws, not statistical fit.
        class Draw(random.Random):
            def __init__(self,value):self.value=value
            def randrange(self,stop):
                assert stop==4
                return self.value
        m=DurationSupport([F(1,2)],ppq=2,max_quarters=1)
        self.assertEqual([m.sample(Draw(i),remaining_ticks=2) for i in range(4)],
                         [F(1,2),F(1,2),F(1,2),F(1)])

    def test_invalid_arguments(self):
        for kwargs in ({'ppq':True},{'ppq':0},{'max_quarters':33},{'prior_mass':0},
                       {'prior_mass':0.5},{'prior_mass':True}):
            with self.assertRaises(ValueError):DurationSupport(**kwargs)
        m=DurationSupport()
        for d in (1,True,F(0),F(-1),F(1,32768)):
            with self.assertRaises(ValueError):m.probability(d)
        for kwargs in ({'remaining_ticks':0},{'remaining_ticks':True},
                       {'remaining_ticks':1,'max_duration_ticks':0},
                       {'remaining_ticks':1,'max_duration_ticks':12289}):
            with self.assertRaises(ValueError):m.sample(random.Random(0),**kwargs)


if __name__=='__main__':unittest.main()

import random
import unittest
from fractions import Fraction
from mousa.group_onset_model import GroupOnsetModel, generate, LIMIT
from mousa.initial_rest_group_model import InitialRestGroupModel, MAX_INITIAL

T = ((0, 96, 80, 7),)


class InitialRestTests(unittest.TestCase):
    def test_old_probability_and_seed_parity(self):
        seq = [[(0, 60, T), (96, 62, T), (192, 64, T)], [(384, 65, T), (96, 67, T)]]
        for arm in (False, True):
            old = GroupOnsetModel(seq, context=arm)
            new = InitialRestGroupModel(seq, context=arm)
            for previous in (None, 1, 2, 128):
                for d in ([0] if previous is None else []) + [1, 96, 192, 384, LIMIT]:
                    self.assertEqual(old.probability(d, previous), new.probability(d, previous))
            self.assertEqual(old.evaluate(seq[0]), new.evaluate(seq[0]))
            for seed in range(10):
                self.assertEqual(generate(old, seed), generate(new, seed))

    def test_initial_long_and_sparse_normalization(self):
        for first_limit in (12672, 65536, MAX_INITIAL):
            seq = [[(12672, 60, T), (96, 61, T)], [(first_limit, 62, T)]]
            model = InitialRestGroupModel(seq, first_limit=first_limit)
            seen = set(model.first)
            total = sum(model.probability(d) for d in seen)
            total += (first_limit + 1 - len(seen)) * model.probability(0)
            self.assertEqual(total, Fraction(1))
            self.assertGreater(model.probability(first_limit - 1), 0)
            self.assertEqual(model.first[12672], 2 if first_limit == 12672 else 1)
            model.evaluate(seq[0])
            self.assertEqual(seq[0][0][0], 12672)
        tiny = InitialRestGroupModel([[(0, 60, T)]])
        self.assertEqual(sum(tiny.probability(d) for d in range(LIMIT+1)), 1)

    def test_later_law_unchanged_and_unknown(self):
        seq = [[(0, 60, T), (96, 61, T), (192, 62, T)]]
        for arm in (False, True):
            old = GroupOnsetModel(seq, context=arm)
            new = InitialRestGroupModel(seq, context=arm, first_limit=MAX_INITIAL)
            for prev in (1, 2):
                self.assertEqual(sum(new.probability(d, prev) for d in range(1, LIMIT+1)), 1)
                for d in (1, 96, 192, LIMIT):
                    self.assertEqual(old.probability(d, prev), new.probability(d, prev))
            self.assertNotEqual(old.probability(0), new.probability(0))
            with self.assertRaises(ValueError): new.probability(MAX_INITIAL+1)
            with self.assertRaises(ValueError): new.probability(12672, 1)
            with self.assertRaises(ValueError): new.probability(0, 1)

    def test_bounded_generation_and_no_silence_clipping(self):
        model = InitialRestGroupModel([[(MAX_INITIAL, 60, T), (96, 62, T)]], first_limit=MAX_INITIAL)
        for seed in range(5):
            g = generate(model, seed)
            self.assertIn(g['status'], ('complete', 'blocked'))
            self.assertTrue(all(0 <= n['start'] < n['end'] <= 9216 for n in g['notes']))
            self.assertTrue(all(b['onset'] > a['onset'] for a,b in zip(g['groups'],g['groups'][1:])))
        self.assertEqual(model.first, {MAX_INITIAL:1})
        self.assertIsNone(model.sample_delta(random.Random(0), None, 0))
        self.assertIsNone(model.sample_delta(random.Random(0), 1, 1))
        self.assertEqual(generate(model,0,cpu_deadline=0)['status'], 'cpu_budget_exhausted')

    def test_integer_draw_boundary(self):
        class Draw:
            def __init__(self, k): self.k=k
            def randrange(self,n): self.n=n; return self.k
        model=InitialRestGroupModel([[(1,60,T)]],first_limit=12672)
        # support0,1,2 weights1,12674,1; exact integer cumulative boundaries.
        for k,expected in [(0,0),(1,1),(12674,1),(12675,2)]:
            r=Draw(k);self.assertEqual(model.sample_delta(r,None,3),expected)
            self.assertEqual(r.n,12676)

    def test_invalid_and_support_bounds(self):
        for limit in (True, LIMIT-1, MAX_INITIAL+1, 12672.0):
            with self.assertRaises(ValueError): InitialRestGroupModel([[(0,60,T)]],first_limit=limit)
        for seq in ([[(MAX_INITIAL+1,60,T)]], [[(0,60,T),(12672,62,T)]], [[(0,60,T),(0,62,T)]], [None]):
            with self.assertRaises(ValueError): InitialRestGroupModel(seq,first_limit=MAX_INITIAL)
        m=InitialRestGroupModel([[(0,60,T)]])
        with self.assertRaises(ValueError):m.sample_delta(random.Random(0),None,MAX_INITIAL)


if __name__ == '__main__': unittest.main()

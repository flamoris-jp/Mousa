from collections import Counter, defaultdict
from fractions import Fraction
import unittest
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.fourteen_context_model import FourteenContextModel
from mousa.optimized_feasible_generation import generate_optimized
from mousa.onset_gate_model import GATE_SIZE


class FourteenContextTests(unittest.TestCase):
    def fixture(self,n):
        return [[(i%3,1+i%4),(1,2)] for i in range(n)], [[60+i%5,61+i%5] for i in range(n)]

    def test_original_parity(self):
        for count in (1,5,12):
            s,p=self.fixture(count)
            old=ContextOnsetGateModel(s,p,timing_context=True,pitch_continuity=True,strength=4)
            new=FourteenContextModel(s,p,timing_context=True,pitch_continuity=True,strength=4)
            for prev in (None,1,2,3,4,9):
                for pair in ((0,1),(1,2),(2,3),(12288,12288)):
                    self.assertEqual(old.probability(pair,previous_gate=prev),new.probability(pair,previous_gate=prev))
            for seed in range(3):
                self.assertEqual(generate_optimized(old,seed,target_ticks=24,trailing_rest_ticks=2,uniform_mix=Fraction(1,4)),
                                 generate_optimized(new,seed,target_ticks=24,trailing_rest_ticks=2,uniform_mix=Fraction(1,4)))

    def test_fourteen_exact_counts_and_boundaries(self):
        s,p=self.fixture(14);m=FourteenContextModel(s,p,timing_context=True,pitch_continuity=True)
        contexts=defaultdict(Counter);intervals=Counter()
        for seq,ps in zip(s,p):
            for a,b in zip(seq,seq[1:]):contexts[a[1]][b[0]]+=1
            intervals.update(b-a for a,b in zip(ps,ps[1:]))
        self.assertEqual(m.contexts,contexts);self.assertEqual(m.intervals,intervals)
        self.assertEqual(sum(m.intervals.values()),14)
        self.assertEqual(m.pitch_counts,Counter(x for ps in p for x in ps))
        self.assertEqual(m.base.n,28)
        self.assertEqual(m.base.dt_counts,Counter(a for seq in s for a,b in seq))
        gates=Counter(b for seq in s for a,b in seq)
        self.assertEqual(m.base.gate_counts,gates)
        self.assertEqual(m._gate_prefix,[sum(n for g,n in gates.items() if g<=i) for i in range(1,GATE_SIZE+1)])
        self.assertEqual(m._delta_cache,{})
        self.assertEqual(m.vocabulary,tuple(sorted(set(x for ps in p for x in ps))))
        self.assertIsInstance(m,ContextOnsetGateModel)
        g=generate_optimized(m,0,target_ticks=24,trailing_rest_ticks=2)
        self.assertTrue(all(type(n['start']) is int and type(n['end']) is int for n in g['notes']))

    def test_rejections(self):
        for n in (0,15):
            s,p=self.fixture(n)
            with self.assertRaises(ValueError):FourteenContextModel(s,p)
        s,p=self.fixture(14)
        with self.assertRaises(ValueError):ContextOnsetGateModel(s,p)
        p[-1][-1]=True
        with self.assertRaises(ValueError):FourteenContextModel(s,p)
        for kwargs in ({'strength':True},{'timing_context':1},{'pitch_continuity':1}):
            s,p=self.fixture(14)
            with self.assertRaises(ValueError):FourteenContextModel(s,p,**kwargs)
        s,p=self.fixture(14);s[-1][0]=(0,0)
        with self.assertRaises(ValueError):FourteenContextModel(s,p)

    def test_wrapper_preflight_and_restoration(self):
        import sys
        from pathlib import Path
        from unittest.mock import patch
        with patch.object(sys, 'path', [str(Path(__file__).resolve().parents[1] / 'tools'), *sys.path]):
            import compare_fourteen_context_expansion as wrapper
        old = wrapper.intake.base.ContextOnsetGateModel
        self.assertTrue(wrapper.synthetic_capability_preflight()['synthetic_only'])
        with self.assertRaises(RuntimeError):
            with wrapper.fourteen_context_profile():
                self.assertIs(wrapper.intake.base.ContextOnsetGateModel,FourteenContextModel)
                raise RuntimeError('synthetic failure')
        self.assertIs(wrapper.intake.base.ContextOnsetGateModel,old)

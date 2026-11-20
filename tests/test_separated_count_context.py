import unittest
from fractions import Fraction
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.separated_count_context import SeparatedCountContext
from mousa.optimized_feasible_generation import generate_optimized
from mousa.onset_gate_model import DT_SIZE,GATE_SIZE

class SeparatedCountsTests(unittest.TestCase):
    def setUp(self):
        self.s=[[(0,96),(96,192),(192,96)]]; self.p=[[60,62,64]]
        self.a=self.s+[[(0,384),(384,384)]];self.q=self.p+[[65,65]]

    def test_same_inputs_reproduce_frozen_model(self):
        for seq,p in [(self.s,self.p),(self.a,self.q)]:
            old=ContextOnsetGateModel(seq,p,timing_context=True,pitch_continuity=True,strength=4)
            new=SeparatedCountContext(seq,p,seq,p)
            self.assertEqual(new.evaluate(self.s[0]),old.evaluate(self.s[0]))
            self.assertEqual(generate_optimized(new,0,target_ticks=768,uniform_mix=Fraction(1,4),trailing_rest_ticks=384),
                             generate_optimized(old,0,target_ticks=768,uniform_mix=Fraction(1,4),trailing_rest_ticks=384))

    def test_paths_do_not_leak(self):
        neither=SeparatedCountContext(self.s,self.p,self.s,self.p)
        pitch=SeparatedCountContext(self.s,self.p,self.a,self.q)
        timing=SeparatedCountContext(self.a,self.q,self.s,self.p)
        self.assertEqual(neither.evaluate(self.a[1]),pitch.evaluate(self.a[1]))
        self.assertEqual(neither.pitch_counts,timing.pitch_counts)
        self.assertEqual(neither.intervals,timing.intervals)
        self.assertNotEqual(neither.pitch_counts,pitch.pitch_counts)
        self.assertEqual(pitch.intervals,{2:2,0:1}) # no 64 -> 65 cross-work transition

    def test_probability_normalization_and_unseen_support(self):
        m=SeparatedCountContext(self.a,self.q,self.s,self.p)
        for prev in (None,96,384,17):
            counts,total,_,_=m._delta_parameters(prev)
            self.assertEqual(sum(counts.values()),total)
            self.assertEqual(sum((c+Fraction(1,DT_SIZE))/(total+1) for c in counts.values())+
                             Fraction(DT_SIZE-len(counts),DT_SIZE)/(total+1),1)
            self.assertEqual(Fraction(sum(m.base.gate_counts.values())+1,m.base.n+1),1)
            self.assertGreater(m.probability((17,19),previous_gate=prev),0)
        with self.assertRaises(ValueError):m.probability((DT_SIZE,1))
        with self.assertRaises(ValueError):SeparatedCountContext(self.s,self.p,self.a,self.p)

if __name__=='__main__':unittest.main()

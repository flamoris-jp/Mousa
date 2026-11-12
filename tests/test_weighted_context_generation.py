from fractions import Fraction
import random
import unittest
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.weighted_timing_diagnostic import WeightedTimingDiagnostic
from mousa.weighted_context_generation import WeightedContextModel,feasible_masses,generate,integer_weights

class WeightedContextTests(unittest.TestCase):
    def setUp(self):
        self.s=[[(0,2),(1,3),(2,1)],[(0,1),(1,2)]];self.p=[[60,62,60],[61,61]]

    def test_raw_and_weighted_probability_parity(self):
        raw=ContextOnsetGateModel(self.s,self.p,timing_context=True,pitch_continuity=True,strength=4)
        new=WeightedContextModel(self.s,self.p,[1,1])
        weighted=WeightedContextModel(self.s,self.p,[Fraction(2,3),Fraction(3,2)])
        timing=WeightedTimingDiagnostic(self.s,[Fraction(2,3),Fraction(3,2)],context=True)
        for prev in (None,1,2,3,9):
            for pair in ((0,1),(1,2),(2,3),(12288,12288)):
                self.assertEqual(new.probability(pair,previous_gate=prev),raw.probability(pair,previous_gate=prev))
                self.assertEqual(weighted.probability(pair,previous_gate=prev),timing.probability(pair,previous_gate=prev))
        self.assertEqual(weighted.weighted_mass,5)
        self.assertEqual(weighted.intervals,{2:Fraction(2,3),-2:Fraction(2,3),0:Fraction(3,2)})

    def test_exact_feasible_masses_match_enumeration(self):
        m=WeightedContextModel(self.s,self.p,[Fraction(2,3),Fraction(3,2)])
        for notes in ([],[dict(start=0,end=2,pitch=60),dict(start=0,end=3,pitch=61)],
                      [dict(start=0,end=1,pitch=60),dict(start=0,end=2,pitch=61),dict(start=0,end=3,pitch=62)]):
            weights=m.mixed_pitch_weights(60);masses=feasible_masses(m,0,2,notes,4,weights);expected=[]
            for dt in range(4):
                active=[n for n in notes if n['end']>dt];occupied={n['pitch'] for n in active};mass=Fraction(0)
                if len(active)<3:
                    for gate in range(1,5-dt):
                        for pitch,w in zip(m.vocabulary,weights):
                            if pitch not in occupied:mass+=m.probability((dt,gate),previous_gate=2)*Fraction(w,sum(weights))
                expected.append(mass)
            self.assertEqual([Fraction(x,sum(masses)) for x in masses],[x/sum(expected) for x in expected])

    def test_generation_reproducible_safe_and_bounded(self):
        m=WeightedContextModel(self.s,self.p,[Fraction(2,3),Fraction(3,2)])
        a=generate(m,31,target_ticks=24,trailing_rest_ticks=3)
        self.assertEqual(a,generate(m,31,target_ticks=24,trailing_rest_ticks=3))
        self.assertEqual(a['status'],'complete')
        for n in a['notes']:
            self.assertTrue(0<=n['start']<n['end']<=24)
            active=[v for v in a['notes'] if v['start']<=n['start']<v['end']]
            self.assertLessEqual(len(active),3);self.assertEqual(len(active),len({v['pitch'] for v in active}))
        self.assertLessEqual(a['actual_silent_tail_ticks'],3)
        self.assertIn(generate(m,2,max_notes=1)['status'],('blocked','complete'))

    def test_legacy_sampler_routes_rejected(self):
        from mousa.optimized_feasible_generation import generate_optimized
        from mousa.feasible_context_generation import generate_feasible
        m=WeightedContextModel([[(0,1),(1,2)]],[[60,61]],[Fraction(1,100)])
        self.assertNotIsInstance(m,ContextOnsetGateModel)
        with self.assertRaises(ValueError):m.sample_pair(random.Random(0),remaining_ticks=4)
        with self.assertRaises(ValueError):m.generate(0)
        with self.assertRaises(ValueError):generate_optimized(m,0)
        with self.assertRaises(ValueError):generate_feasible(m,0)
        # Supported route still produces integer bounded events for the exact
        # counterexample that formerly leaked a fractional out-of-range gate.
        g=generate(m,0,target_ticks=4,trailing_rest_ticks=0)
        for note in g['notes']:
            self.assertIs(type(note['start']),int)
            self.assertIs(type(note['end']),int)
            self.assertTrue(0<=note['start']<note['end']<=4)

    def test_invalid_resources(self):
        for weight in (True,0,1.1,Fraction(1,1000001)):
            with self.assertRaises(ValueError):WeightedContextModel(self.s,self.p,[weight,1])
        with self.assertRaises(ValueError):integer_weights([Fraction(1,1<<2049)])
        with self.assertRaises(ValueError):generate(WeightedContextModel(self.s,self.p,[1,1]),0,target_ticks=0)

if __name__=='__main__':unittest.main()

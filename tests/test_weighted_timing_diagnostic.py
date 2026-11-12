from fractions import Fraction
import unittest
from mousa.weighted_timing_diagnostic import WeightedTimingDiagnostic
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.onset_gate_model import DT_SIZE,GATE_SIZE

class WeightedTimingTests(unittest.TestCase):
    def test_unit_weights_exactly_match_existing_model(self):
        seqs=[[(0,3),(2,4),(3,3)],[(1,2),(2,4)]];ps=[[60,62,64],[61,63]]
        for context in (False,True):
            old=ContextOnsetGateModel(seqs,ps,timing_context=context,strength=4)
            new=WeightedTimingDiagnostic(seqs,[1,1],context=context)
            for previous in (None,2,3,4,17):
                for pair in [(0,3),(2,4),(12288,12288)]:
                    self.assertEqual(old.probability(pair,previous_gate=previous),new.probability(pair,previous_gate=previous))

    def test_fractional_marginal_normalization_and_support(self):
        m=WeightedTimingDiagnostic([[(0,3),(2,4)],[(1,2)]],[Fraction(1,3),Fraction(2,5)],context=True)
        self.assertEqual(m.mass,Fraction(16,15))
        for prev in (None,3,999):
            counts=m.delta_counts(prev);total=sum(counts.values())
            dt_mass=sum((v+Fraction(1,DT_SIZE))/(total+1) for v in counts.values())+(DT_SIZE-len(counts))*Fraction(1,DT_SIZE)/(total+1)
            gate_mass=sum((v+Fraction(1,GATE_SIZE))/(m.mass+1) for v in m.gate.values())+(GATE_SIZE-len(m.gate))*Fraction(1,GATE_SIZE)/(m.mass+1)
            self.assertEqual(dt_mass*gate_mass,1)
            self.assertGreater(m.probability((12288,12288),previous_gate=prev),0)

    def test_invalid_weights_and_work_boundaries(self):
        for weight in (0,-1,1.0,True,1001):
            with self.assertRaises(ValueError):WeightedTimingDiagnostic([[(0,1)]],[weight])
        m=WeightedTimingDiagnostic([[(0,1)],[(2,3)]],[1,1],context=True)
        self.assertFalse(m.local)

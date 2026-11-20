from fractions import Fraction as F
import random
import unittest
from unittest.mock import patch
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.onset_gate_model import DT_SIZE,GATE_SIZE


class ContextTests(unittest.TestCase):
    def model(self,**kwargs):
        return ContextOnsetGateModel([[(0,2),(1,3),(2,2)],[(4,4),(1,2)]],[[60,62,64],[67,65]],**kwargs)

    def test_context_reset_and_backoff(self):
        m=self.model(timing_context=True)
        self.assertEqual(m.contexts[2],{1:1}) # no cross-work lastgate2 ->delta4
        self.assertNotIn(3,m.intervals) # no cross-work64 ->67
        self.assertEqual(m.delta_counts(99),m.base.dt_counts)
        self.assertEqual(m.delta_counts(None),m.base.dt_counts)

    def test_exact_counts_normalized_and_control(self):
        m=self.model(timing_context=True)
        self.assertEqual(m.delta_counts(2)[1],F(1,5)+F(4,5)*2)
        for previous in (None,2,3,99):
            counts=m.delta_counts(previous);total=sum(counts.values())
            self.assertEqual(sum((counts.get(d,0)+F(1,DT_SIZE))/(total+1) for d in range(DT_SIZE)),1)
            gate_mass=sum(F(m.base.gate_counts[g]*GATE_SIZE+1,(m.base.n+1)*GATE_SIZE) for g in range(1,GATE_SIZE+1))
            self.assertEqual(gate_mass,1)
        control=self.model()
        for pair in ((0,1),(12000,12000),(1,2)):
            self.assertEqual(control.probability(pair,previous_gate=2),control.base.probability(pair))

    def test_pitch_support_and_positive_backoff(self):
        m=self.model(pitch_continuity=True)
        self.assertTrue(all(w>0 for w in m.pitch_weights(67)))
        self.assertEqual(set(m.vocabulary),{60,62,64,65,67})
        self.assertEqual(self.model().pitch_weights(60),[1]*5)
        with self.assertRaises(ValueError):m.pitch_weights(127)

    def test_reproducibility_and_legal_generation(self):
        for timing in (False,True):
            for pitch in (False,True):
                m=self.model(timing_context=timing,pitch_continuity=pitch)
                a=m.generate(3,target_ticks=16,max_notes=20,max_attempts=8)
                self.assertEqual(a,m.generate(3,target_ticks=16,max_notes=20,max_attempts=8))
                self.assertLessEqual(len(a['notes']),20)
                for i,n in enumerate(a['notes']):
                    active=[x for x in a['notes'][:i] if x['end']>n['start']]
                    self.assertLess(len(active),3)
                    self.assertNotIn(n['pitch'],[x['pitch'] for x in active])
                    self.assertTrue(0<=n['start']<n['end']<=16)
                if a['status']=='complete':self.assertEqual(max(n['end'] for n in a['notes']),16)

    def test_blocked_explicit(self):
        m=ContextOnsetGateModel([[(0,2)]],[[60]])
        with patch.object(m,'sample_pair',return_value=(0,2)):
            r=m.generate(1,target_ticks=10,max_attempts=2)
        self.assertEqual(r['status'],'blocked');self.assertEqual(r['rejections'],2)

    def test_summary_all_undefined_intervals(self):
        import importlib.util
        from pathlib import Path
        import sys
        tools=Path(__file__).resolve().parents[1]/'tools'
        sys.path.insert(0,str(tools))
        try:
            spec=importlib.util.spec_from_file_location('context_driver_test',tools/'compare_context_onset_gate.py')
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        finally:
            sys.path.pop(0)
        rows=[dict(status='complete',metrics=module.metrics([dict(start=0,end=10,pitch=60)],10)),
              dict(status='blocked',metrics=module.metrics([],10))]
        means,denominators=module.summarize(rows)
        self.assertIsNone(means['mean_abs_pitch_interval'])
        self.assertEqual(denominators['mean_abs_pitch_interval'],0)
        self.assertEqual(means['notes'],1)
        self.assertEqual(denominators['notes'],1)
        self.assertEqual(module.summarize([]),({},{}))

    def test_conditional_sample_and_invalid(self):
        m=self.model(timing_context=True)
        for remaining in (1,2,30):
            dt,gate=m.sample_pair(random.Random(0),remaining_ticks=remaining,previous_gate=2)
            self.assertTrue(dt>=0 and gate>0 and dt+gate<=remaining)
        for kwargs in (dict(strength=-1),dict(strength=True),dict(timing_context=1)):
            with self.assertRaises(ValueError):self.model(**kwargs)
        with self.assertRaises(ValueError):m.probability((0,1),previous_gate=True)
        with self.assertRaises(ValueError):m.generate(0,target_ticks=0)
        with self.assertRaises(ValueError):ContextOnsetGateModel([[(0,1)]],[[True]])


if __name__=='__main__':unittest.main()

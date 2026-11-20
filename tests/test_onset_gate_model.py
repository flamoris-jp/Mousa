from fractions import Fraction as F
import math
import random
import unittest
from unittest.mock import patch
from mousa.onset_gate_model import OnsetGateModel, PPQ, MAX_TICKS, DT_SIZE, GATE_SIZE, SUPPORT_SIZE


class OnsetGateTests(unittest.TestCase):
    def test_same_support_formula_normalization(self):
        pairs=[(0,1),(0,1),(2,3)]
        joint=OnsetGateModel(pairs);factor=OnsetGateModel(pairs,factorized=True)
        self.assertEqual(joint.probability((0,1)),F(2*SUPPORT_SIZE+1,4*SUPPORT_SIZE))
        self.assertEqual(factor.probability((0,1)),F(2*DT_SIZE+1,4*DT_SIZE)*F(2*GATE_SIZE+1,4*GATE_SIZE))
        # Exact algebra over entire Cartesian support without allocating150M pairs.
        joint_mass=sum(joint.probability(p) for p in joint.counts)+(SUPPORT_SIZE-len(joint.counts))*F(1,4*SUPPORT_SIZE)
        self.assertEqual(joint_mass,1)
        dt_mass=sum(F(factor.dt_counts[d]*DT_SIZE+1,4*DT_SIZE) for d in range(DT_SIZE))
        gate_mass=sum(F(factor.gate_counts[g]*GATE_SIZE+1,4*GATE_SIZE) for g in range(1,GATE_SIZE+1))
        self.assertEqual(dt_mass*gate_mass,1)

    def test_unseen_and_evaluation(self):
        for factorized in (False,True):
            m=OnsetGateModel([(1,2)],factorized=factorized)
            self.assertGreater(m.probability((MAX_TICKS,MAX_TICKS)),0)
            report=m.evaluate([(0,1),(MAX_TICKS,MAX_TICKS)])
            self.assertTrue(math.isfinite(report['nll_per_event']))
            self.assertEqual(report['support_size'],SUPPORT_SIZE)
            self.assertFalse(report['conditional_generation_masks_applied'])

    def test_pair_sample_legal_reproducible(self):
        for factorized in (False,True):
            m=OnsetGateModel([(12000,12000),(0,1)],factorized=factorized)
            a=random.Random(9);b=random.Random(9)
            for remaining in (1,2,20,MAX_TICKS*3):
                x=m.sample_pair(a,remaining_ticks=remaining)
                self.assertEqual(x,m.sample_pair(b,remaining_ticks=remaining))
                self.assertLessEqual(sum(x),remaining)
                self.assertTrue(0<=x[0]<=MAX_TICKS and 1<=x[1]<=MAX_TICKS)

    def test_generation_safety_and_determinism(self):
        for factorized in (False,True):
            m=OnsetGateModel([(0,3),(2,4)],factorized=factorized)
            args=dict(target_ticks=12,pitches=[60,64,67])
            result=m.generate(12,**args)
            self.assertEqual(result,m.generate(12,**args))
            notes=result['notes']
            self.assertLessEqual(len(notes),256)
            for i,n in enumerate(notes):
                self.assertTrue(0<=n['start']<n['end']<=12)
                active=[x for x in notes[:i] if x['end']>n['start']]
                self.assertLess(len(active),3)
                self.assertFalse(any(x['pitch']==n['pitch'] for x in active))
            if result['status']=='complete':self.assertEqual(max(n['end'] for n in notes),12)

    def test_explicit_blocking_not_clipping(self):
        m=OnsetGateModel([])
        with patch.object(m,'sample_pair',return_value=(0,3)):
            r=m.generate(0,target_ticks=10,pitches=[60],max_attempts=2)
        self.assertEqual(r['status'],'blocked')
        self.assertEqual(r['rejections'],2)
        self.assertEqual(r['notes'],[dict(start=0,end=3,pitch=60)])
        with patch.object(m,'sample_pair',return_value=(0,3)):
            r=m.generate(0,target_ticks=10,pitches=[60],max_notes=1)
        self.assertEqual(r['reason'],'note budget exhausted')

    def test_empty_training_uniform(self):
        for factorized in (False,True):
            m=OnsetGateModel([],factorized=factorized)
            self.assertEqual(m.probability((0,1)),F(1,SUPPORT_SIZE))
            self.assertEqual(m.sample_pair(random.Random(0),remaining_ticks=1),(0,1))

    def test_invalid_inputs(self):
        m=OnsetGateModel([])
        for p in ((-1,1),(0,0),(12289,1),(0,12289),(True,1),(F(1,2),1),[0,1]):
            with self.assertRaises(ValueError):m.probability(p)
        for pairs in ([],[(0,1)]*100001):
            with self.assertRaises(ValueError):m.evaluate(pairs)
        for settings in (dict(target_ticks=0,pitches=[60]),dict(target_ticks=1,pitches=[]),
                         dict(target_ticks=1,pitches=[True]),dict(target_ticks=1,pitches=[60],max_notes=257)):
            with self.assertRaises(ValueError):m.generate(0,**settings)


if __name__=='__main__':unittest.main()

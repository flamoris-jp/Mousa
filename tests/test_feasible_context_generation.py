from fractions import Fraction as F
import unittest
from unittest.mock import patch
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.feasible_context_generation import pitch_distribution,generate_feasible,feasible_masses,_weights


class FeasibleTests(unittest.TestCase):
    def model(self):
        return ContextOnsetGateModel([[(0,3),(1,4),(2,2)]],[[60,62,64]],timing_context=True,pitch_continuity=True)

    def test_mixture_before_mask_exact(self):
        m=self.model();base=pitch_distribution(m,60);mix=pitch_distribution(m,60,uniform_mix=F(1,4))
        for p in base:self.assertEqual(mix[p],F(3,4)*base[p]+F(1,4*len(base)))
        masked=pitch_distribution(m,60,uniform_mix=F(1,4),forbidden=[60])
        self.assertEqual(sum(masked.values()),1)
        for p in masked:self.assertEqual(masked[p],mix[p]/(1-mix[60]))
        self.assertEqual(pitch_distribution(m,60,forbidden=m.vocabulary),{})

    def test_baseline_exact_parity(self):
        m=self.model()
        for seed in range(5):
            a=m.generate(seed,target_ticks=30,max_notes=20,max_attempts=8)
            b=generate_feasible(m,seed,target_ticks=30,max_notes=20,max_attempts=8)
            for key in a:self.assertEqual(a[key],b[key])
            self.assertEqual(b['timing_draws'],b['pitch_draws'])

    def test_no_time_advance_when_blocked(self):
        m=self.model()
        with patch('mousa.feasible_context_generation._sample_feasible',return_value=None):
            result=generate_feasible(m,0,feasible_mask=True,target_ticks=10,max_attempts=2)
        self.assertEqual(result['status'],'blocked')
        self.assertEqual(result['pitch_draws'],0)
        self.assertEqual(result['last_accepted_state']['onset'],0)
        self.assertEqual(result['notes'],[])

    def test_exact_joint_feasibility_mass_enumeration(self):
        m=self.model()
        notes=[dict(start=0,end=1,pitch=60),dict(start=0,end=2,pitch=62),dict(start=0,end=2,pitch=64)]
        for mix in (F(0),F(1,4)):
            weights=_weights(m,60,mix)
            masses=feasible_masses(m,previous=0,previous_gate=3,notes=notes,remaining_ticks=3,pitch_weights=weights)
            exact=[]
            for dt in range(3):
                active=[n for n in notes if n['end']>dt]
                allowed=[] if len(active)>=3 else [p for p in m.vocabulary if p not in {n['pitch'] for n in active}]
                mass=sum((m.probability((dt,g),previous_gate=3)*F(weights[m.vocabulary.index(p)],sum(weights))
                          for g in range(1,4-dt) for p in allowed),F(0))
                exact.append(mass)
            self.assertEqual([F(x,sum(masses)) for x in masses],[x/sum(exact) for x in exact])
            self.assertEqual(masses[0],0)
            self.assertGreater(masses[1],0)

    def test_reproducibility_and_safety(self):
        m=self.model()
        for mask in (False,True):
            for mix in (F(0),F(1,4)):
                args=dict(feasible_mask=mask,uniform_mix=mix,target_ticks=30)
                r=generate_feasible(m,12,**args)
                self.assertEqual(r,generate_feasible(m,12,**args))
                self.assertEqual(r['timing_draws'],len(r['notes'])+r['rejections'])
                for i,n in enumerate(r['notes']):
                    active=[p for p in r['notes'][:i] if p['end']>n['start']]
                    self.assertLess(len(active),3);self.assertNotIn(n['pitch'],[p['pitch'] for p in active])
                    self.assertTrue(0<=n['start']<n['end']<=30)

    def test_invalid_inputs(self):
        m=self.model()
        for kwargs in (dict(uniform_mix=.25),dict(uniform_mix=F(-1)),dict(feasible_mask=1),
                       dict(max_attempts=0),dict(target_ticks=0)):
            with self.assertRaises(ValueError):generate_feasible(m,0,**kwargs)


if __name__=='__main__':unittest.main()

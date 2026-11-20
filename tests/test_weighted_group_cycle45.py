import unittest,random
from fractions import Fraction
from mousa.weighted_group_cycle45 import WeightedGroupModel,pool_weights,integerize,generate
from mousa.gate_context_group_model import GateContextGroupModel,generate as oldgenerate
T=((0,96,80,4),)
class Weighted45Tests(unittest.TestCase):
    def test_old_raw_exact_prob_and_sampler_parity(self):
        seq=[[(0,60,T),(96,62,T)],[(12,64,T),(192,65,T),(96,66,T)]]
        old=GateContextGroupModel(seq,arm='global');new=WeightedGroupModel(seq,['a','b'],masses=(2,3,5))
        for prev in (None,1):
            for d in ([0] if prev is None else [])+[1,12,96,192,12288]:
                self.assertEqual(old.probability(d,prev),new.probability(d,prev))
        for seed in range(10):self.assertEqual(oldgenerate(old,seed),generate(new,seed))
        with self.assertRaises(ValueError):oldgenerate(new,0)
        with self.assertRaises(ValueError):generate(old,0)
    def test_weight_pools_and_resets(self):
        seq=[[(0,60,T)],[(12,62,T),(96,64,T)],[(24,65,T),(192,67,T),(96,69,T)]]
        for mode in ('raw','equal_work','equal_family'):
            m=WeightedGroupModel(seq,['a','a','b'],mode=mode,masses=(3,3,6))
            self.assertEqual(sum(m.first.values()),3);self.assertEqual(sum(m.later.values()),3)
            self.assertEqual(sum(m.template_counts.values()),6)
            self.assertNotIn(12,m.later);self.assertNotIn(24,m.later)
            self.assertEqual(m.pool_weights[1][0],0)
        self.assertEqual(pool_weights([1,1,1],['a','a','b'],'equal_family',3),[Fraction(3,4),Fraction(3,4),Fraction(3,2)])
    def test_uniform_prior_and_exact_scaling_normalization(self):
        m=WeightedGroupModel([[(0,60,T),(1,61,T)],[(12,62,T),(2,63,T),(2,64,T)]],['a','b'],mode='equal_work',masses=(17,3411,3428))
        for prev,lo,hi,counts,mass in [(None,0,65536,m.first,17),(1,1,12288,m.later,3411)]:
            size=hi-lo+1
            self.assertEqual(sum((m.probability(d,prev) for d in range(lo,hi+1)),Fraction()),1)
            for d in [lo,2,hi]:
                self.assertEqual(m.probability(d,prev),(counts[d]+Fraction(1,size))/(mass+1))
        self.assertGreater(m.probability(999,1),0)
        for seed in range(10):
            v=generate(m,seed,target=384,tail=96);self.assertIn(v['status'],('complete','blocked'))
            self.assertTrue(all(n['end']<=384 for n in v['notes']))
    def test_bounds_no_silent_scale_changes(self):
        with self.assertRaises(ValueError):integerize({'x':Fraction(1,2**2049)})
        with self.assertRaises(ValueError):WeightedGroupModel([[(0,60,T)]],['a'])
        with self.assertRaises(ValueError):pool_weights([1],['a'],'invalid',1)
        with self.assertRaises(ValueError):generate(WeightedGroupModel([[(0,60,T),(96,62,T)]],['a']),0,max_attempts=65)
if __name__=='__main__':unittest.main()

import unittest
from mousa.gate_context_group_model import GateContextGroupModel,generate,gate_bin,ARMS
from mousa.initial_rest_group_model import InitialRestGroupModel,generate as old_generate

T=((0,96,80,0),);L=((0,1536,80,0),)


class GateContextTests(unittest.TestCase):
    def test_old_controls_parity(self):
        seq=[[(0,60,T),(96,62,T),(192,64,T)],[(12672,48,T),(96,50,T)]]
        for arm,context in [('global',False),('cardinality',True)]:
            m=GateContextGroupModel(seq,arm=arm);old=InitialRestGroupModel(seq,context=context,first_limit=65536)
            for prev in (None,1,2):
                for delta in ([0] if prev is None else [])+[1,96,12288]:
                    self.assertEqual(m.probability(delta,prev),old.probability(delta,prev))
            for seed in range(10): self.assertEqual(generate(m,seed),old_generate(old,seed))

    def test_horizon_old_sustain_and_reset(self):
        seq=[[(0,60,L),(192,62,T),(192,64,T)],[(0,60,T),(384,62,T)]]
        p=GateContextGroupModel(seq,arm='previous_max_gate_binned')
        h=GateContextGroupModel(seq,arm='active_horizon_binned')
        self.assertEqual(p.local[1][192],1)
        self.assertEqual(h.local[4][192],2)
        self.assertEqual(h.local[1][384],1)
        self.assertNotIn(0,h.later)  # boundary not used as transition
        horizon,key=h.advance(1536,192,T)
        self.assertEqual((horizon,key),(1344,4))
        self.assertEqual(p.advance(1536,192,T),(1344,1))

    def test_normalization_known_unknown_and_first(self):
        seq=[[(0,60,L),(192,62,T),(192,64,T)]]
        models=[GateContextGroupModel(seq,arm=a) for a in ARMS]
        for m in models:
            for key in (1,4,5):
                self.assertEqual(sum(m.probability(d,key) for d in range(1,12289)),1)
            self.assertEqual(m.probability(12672),models[0].probability(12672))
            self.assertGreater(m.probability(377,5),0)
        for d,b in [(1,1),(192,1),(193,2),(384,2),(385,3),(768,3),(769,4),(1536,4),(1537,5)]:self.assertEqual(gate_bin(d),b)
        for v in (0,True,1.0):
            with self.assertRaises(ValueError):gate_bin(v)

    def test_old_generator_rejects_gate_model(self):
        m=GateContextGroupModel([[(0,60,T)]],arm='active_horizon_binned')
        with self.assertRaises(ValueError):old_generate(m,0)

    def test_bounded_generation_cpu(self):
        for arm in ARMS:
            m=GateContextGroupModel([[(12672,60,T),(192,62,T)]],arm=arm)
            self.assertEqual(generate(m,0,cpu_deadline=0)['status'],'cpu_budget_exhausted')
            g=generate(m,0)
            self.assertTrue(all(0<=n['start']<n['end']<=9216 for n in g['notes']))


if __name__=='__main__':unittest.main()

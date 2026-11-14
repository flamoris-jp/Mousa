import sys
from pathlib import Path
import unittest
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from learning_cycle52 import components, shuffled_model, score, summary
from mousa.gate_context_group_model import GateContextGroupModel
T=((0,96,80,0),); L=((0,1536,80,0),)
class LearningTests(unittest.TestCase):
    def test_transitive_split(self):
        self.assertEqual(components(['a','b','c','d'],dict(a='x',b='x',c='y',d='z'),[('b','c')]),[['a','b','c'],['d']])
    def test_invalid_split(self):
        with self.assertRaises(ValueError):components(['a'],{},[])
        with self.assertRaises(ValueError):components(['a'],{'a':'x'},[('a','b')])
    def test_shuffle_preserves_marginals(self):
        s=[[(0,60,T),(96,62,L),(1536,64,T),(96,65,L)]]
        a=GateContextGroupModel(s,arm='previous_max_gate_binned');b=shuffled_model(s,52)
        self.assertEqual(a.first,b.first);self.assertEqual(a.later,b.later)
        self.assertEqual({k:sum(v.values()) for k,v in a.local.items()},{k:sum(v.values()) for k,v in b.local.items()})
        self.assertEqual(sum(b.local.values(),Counter()),b.later)
        self.assertEqual(b.local,shuffled_model(s,52).local)
    def test_closed_form(self):
        s=[[(0,60,T),(96,62,L),(1536,64,T),(96,65,L)]]
        for arm in ('global','previous_max_gate_binned'):
            m=GateContextGroupModel(s,arm=arm);r=score(m,s[0]);v=m.evaluate(s[0])
            self.assertAlmostEqual(r['later_nll_sum'],v['later_nll_sum'])
    def test_macro_denominators(self):
        r=summary([dict(first_nll=0,later_nll_sum=4,later_count=2,later_mean_nll=2),dict(first_nll=0,later_nll_sum=9,later_count=3,later_mean_nll=3)])
        self.assertEqual(r['work_macro'],2.5);self.assertEqual(r['pooled'],2.6)

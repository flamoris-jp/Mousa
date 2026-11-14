import importlib.util
from pathlib import Path
import unittest
s=importlib.util.spec_from_file_location('groove38',Path(__file__).resolve().parents[1]/'tools/groove_cycle38_cohorts.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

class Groove38Tests(unittest.TestCase):
    def row(self,id,n,mean):return {'id':id,'events':n,'drummer':'drummer7','sum_nll_nats':n*mean,'mean_nll_nats':mean}
    def test_pooled_macro_reversal_and_id_join(self):
        a=[self.row('a',100,2.),self.row('b',1,3.)];b=[self.row('b',1,1.),self.row('a',100,2.1)]
        r=m.summarize_pairs(a,b);self.assertTrue(r['pooled_macro_direction_disagree']);self.assertEqual(r['pooled_direction'],'worse');self.assertEqual(r['macro_direction'],'better');self.assertEqual(r['drummers'],1);self.assertEqual(r['events'],101)
    def test_invalid_pair_or_denominator(self):
        a=[self.row('a',2,1.)]
        for b in ([],[self.row('b',2,1.)],[self.row('a',3,1.)],a+a):
            with self.assertRaises(ValueError):m.summarize_pairs(a,b)
        with self.assertRaises(ValueError):m.direction(float('nan'))
        self.assertEqual(m.direction(1e-14),'numerical_tie')

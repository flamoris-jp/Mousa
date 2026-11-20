import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

class GrooveCycle35Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tools=Path(__file__).resolve().parents[1]/'tools'
        with patch.object(sys,'path',[str(tools),*sys.path]):
            spec=importlib.util.spec_from_file_location('groove35',tools/'groove_cycle35_diagnose.py')
            cls.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.m)
    def test_predeclared_exposure_bins(self):
        self.assertEqual([self.m.exposure_bin(n) for n in (0,1,9,10,99,100,5000)],['0','1-9','1-9','10-99','10-99','100+','100+'])
        for n in (True,-1,1.0):
            with self.assertRaises(ValueError):self.m.exposure_bin(n)
    def test_additive_contribution_denominators(self):
        all=self.m.summarize([1.,3.,8.],[2.,2.,2.]);a=self.m.summarize([1.],[2.]);b=self.m.summarize([3.,8.],[2.,2.])
        self.assertEqual(all['events'],a['events']+b['events'])
        self.assertEqual(all['delta_vs_unigram_sum_nll'],a['delta_vs_unigram_sum_nll']+b['delta_vs_unigram_sum_nll'])
        self.assertEqual(all['mean_nll_nats'],4.)
        for a,b in (([],[]),([1.],[])):
            with self.assertRaises(ValueError):self.m.summarize(a,b)

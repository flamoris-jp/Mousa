import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('diversity',Path(__file__).resolve().parents[1]/'tools/compare_diversity_selection.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def row(seed,leap,unique,repeated):
    return dict(seed=seed,status='complete',features=dict(leap_fraction=leap,unique_pitches=unique,zero_interval_fraction=repeated))

class DiversityTests(unittest.TestCase):
    def test_collapse_rejected(self):
        control=row(0,'1/5',10,'1/4');collapsed=row(1,'0',2,'3/4')
        picked,n=m.choose([control,collapsed],control)
        self.assertEqual(picked['seed'],0);self.assertEqual(n,1)
    def test_better_eligible(self):
        control=row(0,'1/5',10,'1/4');candidate=row(1,'1/10',11,'1/5')
        self.assertEqual(m.choose([control,candidate],control)[0]['seed'],1)
    def test_exact_fraction_tie_first(self):
        a=row(0,'1/3',10,'1/4');b=row(1,'2/6',11,'1/4')
        self.assertEqual(m.choose([a,b],a)[0]['seed'],0)
    def test_empty_group_kept(self):
        out=m.run({'groups':[{'group':0,'candidates':[]}]})
        self.assertEqual(out['complete_groups'],0);self.assertEqual(len(out['groups']),1)

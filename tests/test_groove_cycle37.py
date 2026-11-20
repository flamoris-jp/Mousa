import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from fractions import Fraction
from mousa.drum_ioi_35work_profile import DrumIOI35WorkProfile

class Groove37Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tools=Path(__file__).resolve().parents[1]/'tools'
        with patch.object(sys,'path',[str(tools),*sys.path]):
            s=importlib.util.spec_from_file_location('groove37',tools/'groove_cycle37_diagnose.py');cls.m=importlib.util.module_from_spec(s);s.loader.exec_module(cls.m)
    def test_mass_partition_matches_full_enumeration(self):
        for c in ('unigram','quotient_context_k4_residual'):
            m=DrumIOI35WorkProfile([[(0,36),(120,38),(241,42)]],condition=c)
            old={0,120};new=old|{241,30720};a=self.m.support_mass(m,36,old,new)
            self.assertEqual(sum(a.values()),1)
            self.assertEqual(a['still_unseen'],sum((m.probability(dt,previous_instrument=36) for dt in range(30721) if dt not in new),Fraction()))
    def test_nested_membership_and_loss_pairing(self):
        self.assertEqual([self.m.transition(a,b) for a,b in [(True,True),(False,True),(False,False)]],['old_seen','newly_seen','still_unseen'])
        with self.assertRaises(ValueError):self.m.transition(True,False)
        self.assertEqual(self.m.summarize([(2.,3.),(5.,3.)])['expanded_minus_baseline_sum_nll'],-1.)
        with self.assertRaises(ValueError):self.m.summarize([])

import importlib.util
from pathlib import Path
from fractions import Fraction
import json
import tempfile
import sys
import unittest
from unittest.mock import patch

class Groove40CompareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tools=Path(__file__).resolve().parents[1]/'tools'
        with patch.object(sys,'path',[str(tools),*sys.path]):
            s=importlib.util.spec_from_file_location('groove40',tools/'groove_cycle40_compare.py');cls.m=importlib.util.module_from_spec(s);s.loader.exec_module(cls.m)
    def test_ess_algebra_and_equal_mass(self):
        a=self.m.weight_diagnostics([2,4],[Fraction(1)]*2,['a','b']);b=self.m.weight_diagnostics([2,4],[Fraction(3,2),Fraction(3,4)],['a','b'])
        self.assertEqual(a['Kish_event_ESS']['decimal'],6)
        self.assertAlmostEqual(b['Kish_event_ESS']['decimal'],16/3)
        self.assertEqual(b['weighted_event_mass']['decimal'],6)
        self.assertEqual(b['drummer_mass']['a']['decimal'],3)
    def test_gate_and_failure_journal(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);p=d/'plan';p.write_text('{}');c=d/'clear';c.write_text('{}')
            with self.assertRaises(ValueError):self.m.run(d/'none',p,c,d/'output')
            self.assertFalse((d/'output').exists())
            with patch.object(self.m,'WeightedGrooveMarginal',side_effect=ValueError('synthetic')):
                with self.assertRaises(ValueError):self.m.construct_journaled([[(0,36)]],[Fraction(1)],'unigram','raw',['synthetic'],d)
            self.assertEqual(json.loads((d/'fit-journal.json').read_text())['stages'][0]['status'],'construction_failed')

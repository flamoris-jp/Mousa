import importlib.util
from pathlib import Path
from fractions import Fraction
import unittest
from mousa.tick_midi import TickNote
spec=importlib.util.spec_from_file_location('overlap_probe',Path(__file__).resolve().parents[1]/'tools/probe_overlap_representation.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class ProjectionTests(unittest.TestCase):
    def test_overlap_gate_not_clipped(self):
        rows=m.onset_gate_rows((TickNote(0,200,60),TickNote(100,300,64)),100)
        self.assertEqual([r['delta'] for r in rows],[Fraction(0),Fraction(1)])
        self.assertEqual([r['gate'] for r in rows],[Fraction(2),Fraction(2)])
    def test_simultaneous_onsets_zero_delta(self):
        rows=m.onset_gate_rows((TickNote(5,100,60),TickNote(5,200,64)),100)
        self.assertEqual(rows[1]['delta'],0)
        self.assertEqual(rows[0]['delta'],Fraction(1,20))

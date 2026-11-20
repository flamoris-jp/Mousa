import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from mousa.tick_midi import TickNote

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
try:
    spec=importlib.util.spec_from_file_location('rest_intake',ROOT/'tools/screen_initial_rest_intake.py')
    intake=importlib.util.module_from_spec(spec);spec.loader.exec_module(intake)
finally:sys.path.pop(0)

class InitialRestIntakeTests(unittest.TestCase):
    def test_timing_does_not_relax_pitch_copy_guard(self):
        a=SimpleNamespace(notes=tuple(TickNote(i*10,i*10+5,60+i) for i in range(10)))
        b=SimpleNamespace(notes=tuple(TickNote(12672+i*100,12672+i*100+50,65+i) for i in range(10)))
        r=intake.comparison(a,b)
        self.assertGreater(r['exact8'],0)
        self.assertEqual(r['global_similarity'],1)

    def test_similarity_bound_fail_closed(self):
        a=SimpleNamespace(notes=(TickNote(0,1,60),)*2050)
        with self.assertRaises(ValueError):intake.comparison(a,a)

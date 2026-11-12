import importlib.util
from pathlib import Path
import sys
import unittest
path=Path(__file__).resolve().parents[1]/'tools'
sys.path.insert(0,str(path))
try:
    spec=importlib.util.spec_from_file_location('ending_repetition',path/'compare_ending_repetition.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
finally:sys.path.pop(0)

class EndingRepetitionTests(unittest.TestCase):
    def test_repeated_final_tone_is_distinct_variant(self):
        notes=[dict(start=8000,end=8400,pitch=60),dict(start=8500,end=9000,pitch=60)]
        self.assertTrue(m.qualifying(notes));self.assertFalse(m.qualifying(notes,step_only=True))
    def test_step_accepted(self):
        notes=[dict(start=8000,end=8400,pitch=60),dict(start=8500,end=9000,pitch=62)]
        self.assertTrue(m.qualifying(notes,step_only=True))
    def test_simultaneous_not_melodic_approach(self):
        notes=[dict(start=8500,end=8900,pitch=60),dict(start=8500,end=9000,pitch=62)]
        self.assertFalse(m.qualifying(notes));self.assertFalse(m.qualifying(notes,step_only=True))

import unittest,sys,importlib,tempfile
from pathlib import Path
from unittest.mock import patch
with patch.object(sys,'path',[str(Path(__file__).resolve().parents[1]/'tools'),*sys.path]):
    d=importlib.import_module('compare_silence_return_cycle46')
class Driver46Tests(unittest.TestCase):
    def test_skip_all_conditions_and_gate(self):
        self.assertEqual(set(d.skipped(1)),{'seed','control','silence_return'})
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'p').write_text('{}');(p/'c').write_text('{}')
            with patch.object(d,'read',side_effect=AssertionError('no sources')):
                with self.assertRaises(ValueError):d.run(p/'p',p/'c',p/'out')
            self.assertFalse((p/'out').exists())
if __name__=='__main__':unittest.main()

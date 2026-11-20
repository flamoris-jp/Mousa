import unittest,sys,importlib,tempfile
from pathlib import Path
from unittest.mock import patch
with patch.object(sys,'path',[str(Path(__file__).resolve().parents[1]/'tools'),*sys.path]):
    d=importlib.import_module('compare_constrained_return_cycle47')
class Driver47Tests(unittest.TestCase):
    def test_factorial_and_failclosed(self):
        self.assertEqual({(a,b) for _,a,b in d.ARMS},{(False,False),(False,True),(True,False),(True,True)})
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'p').write_text('{}');(p/'c').write_text('{}')
            with patch.object(d,'read',side_effect=AssertionError('no source')):
                with self.assertRaises(ValueError):d.run(p/'p',p/'c',p/'out')
            self.assertFalse((p/'out').exists())
if __name__=='__main__':unittest.main()

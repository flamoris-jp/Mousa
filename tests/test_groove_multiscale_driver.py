import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

class GrooveMultiscaleDriverTests(unittest.TestCase):
    def test_fail_closed_clearance_before_source_access(self):
        tools=Path(__file__).resolve().parents[1]/'tools'
        with patch.object(sys,'path',[str(tools),*sys.path]):
            spec=importlib.util.spec_from_file_location('multiscale_driver',tools/'compare_groove_multiscale.py')
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);plan=d/'plan.json';plan.write_text('{}');clearance=d/'clearance.json';clearance.write_text('{}')
            with self.assertRaises(ValueError):m.run(d/'missing_sources',plan,clearance,d/'output')
            self.assertFalse((d/'output').exists())

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

class GrooveIOIDriverTests(unittest.TestCase):
    def test_clearance_bound_to_exact_plan(self):
        tools=Path(__file__).resolve().parents[1]/'tools'
        with patch.object(sys,'path',[str(tools),*sys.path]):
            spec=importlib.util.spec_from_file_location('groove_driver',tools/'compare_groove_ioi.py')
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        rows=[{'drummer':'drummer9','events':2,'sum_nll_nats':4.,'mean_nll_nats':2.}, {'drummer':'drummer9','events':1,'sum_nll_nats':5.,'mean_nll_nats':5.}]
        summary=m.summarize_drummers(rows)
        self.assertEqual(summary,[{'drummer':'drummer9','performances':2,'events':3,'pooled_mean_nll_nats':3.,'macro_mean_nll_nats':3.5}])
        self.assertEqual(m.summarize_drummers([]),[])
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'plan.json';p.write_text('{}')
            for clearance in ({},{'approved':True,'plan_sha256':'wrong'},{'approved':1,'plan_sha256':m.sha(p)}):
                with self.assertRaises(ValueError):m.check_clearance(p,clearance)
            m.check_clearance(p,{'approved':True,'plan_sha256':m.sha(p)})
            p.write_text('{"changed":true}')
            with self.assertRaises(ValueError):m.check_clearance(p,{'approved':True,'plan_sha256':'wrong'})

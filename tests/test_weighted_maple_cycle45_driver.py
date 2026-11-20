import unittest,sys,importlib,tempfile,json
from pathlib import Path
from unittest.mock import patch
with patch.object(sys,'path',[str(Path(__file__).resolve().parents[1]/'tools'),*sys.path]):
    d=importlib.import_module('compare_weighted_maple_cycle45')
class Driver45Tests(unittest.TestCase):
    def test_seven_conditions_and_skips(self):
        self.assertEqual(len(d.CONDITIONS),7);self.assertEqual(len({v[0] for v in d.CONDITIONS}),7)
        self.assertEqual(d.CONDITIONS[-1][3],(18,4172,4190))
        rows=d.skipped_rows();self.assertEqual([r['seed'] for r in rows],[45000,45001,45002])
        self.assertTrue(all(r['status']=='cpu_budget_skipped' for r in rows))
    def test_public_structure_omits_reconstructible_arrays(self):
        groups=[dict(onset=0,anchor=60),dict(onset=96,anchor=62)]
        public=d.public_structure([],groups)
        self.assertTrue(all('anchor_intervals' not in b for b in public['blocks']))
        self.assertEqual(public['blocks'][0]['interval_count'],1)
        self.assertEqual(public['blocks'][0]['interval_status'],'available')
        self.assertIn('block_interval_pairs',public)
        self.assertIn('anchor_interval_3gram',public)
        self.assertEqual(d.structure([],groups)['blocks'][0]['anchor_intervals'],[2])

    def test_clearance_before_sources(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);(p/'plan').write_text('{}');(p/'clearance').write_text('{}')
            with patch.object(d,'read',side_effect=AssertionError('must not read')):
                with self.assertRaises(ValueError):d.run(p/'plan',p/'clearance',p/'out')
            self.assertFalse((p/'out').exists())
if __name__=='__main__':unittest.main()

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

class Groove36FitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tools=Path(__file__).resolve().parents[1]/'tools'
        with patch.object(sys,'path',[str(tools),*sys.path]):
            s=importlib.util.spec_from_file_location('fit36',tools/'groove_cycle36_fit.py');cls.m=importlib.util.module_from_spec(s);s.loader.exec_module(cls.m)
    def test_dedup_baseline_priority_then_id_no_replacement(self):
        rows=[{'id':i,'sha256':h,'drummer':'drummer1'} for i,h in [('b','same'),('a','same'),('c','other')]]
        selected,aliases=self.m.deduplicate(rows,['b']);self.assertEqual({r['id'] for r in selected},{'b','c'});self.assertEqual(aliases[0]['id'],'a')
        selected,aliases=self.m.deduplicate(rows,[]);self.assertEqual({r['id'] for r in selected},{'a','c'})
        with self.assertRaises(ValueError):self.m.deduplicate(rows,['a','b'])
    def test_clearance_before_source_or_fit(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d);p=d/'plan';p.write_text('{}');c=d/'clear';c.write_text('{}')
            with self.assertRaises(ValueError):self.m.run(d/'none',p,c,d/'output')
            self.assertFalse((d/'output').exists())

    def test_failed_constructor_preserves_attempted_ids_journal(self):
        import json
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)
            with patch.object(self.m,'DrumIOI35WorkProfile',side_effect=ValueError('synthetic constructor failure')):
                with self.assertRaises(ValueError):self.m.construct_journaled([[(0,36)]],'unigram',['synthetic-A'],'expanded',out)
            stage=json.loads((out/'fit-journal.json').read_text())['stages'][0]
            self.assertEqual(stage['train_ids'],['synthetic-A']);self.assertEqual(stage['status'],'construction_failed')
            self.assertEqual(stage['condition'],'unigram')
            model=self.m.construct_journaled([[(0,36)]],'unigram',['synthetic-A'],'baseline',out)
            stages=json.loads((out/'fit-journal.json').read_text())['stages']
            self.assertEqual(len(stages),2);self.assertEqual(stages[1]['status'],'construction_completed')
            self.assertEqual(stages[1]['train_events'],1)

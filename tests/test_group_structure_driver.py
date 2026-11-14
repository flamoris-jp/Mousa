import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

P=Path(__file__).resolve().parents[1]/'tools/diagnose_group_structure.py'
spec=importlib.util.spec_from_file_location('structure_audit',P)
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)

class GroupStructureDriverTests(unittest.TestCase):
    def test_bound_hash_and_unchanged_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);candidate=root/'global-0-private.json'
            candidate.write_text(json.dumps({'notes':[dict(start=0,end=10,pitch=60,velocity=80,release_velocity=0)]}))
            sha=driver.digest(candidate);results=root/'results.json'
            results.write_text(json.dumps({'conditions':{'global':{'outputs':[dict(seed=0,status='complete',private_sha256=sha,target_ticks=20)]}}}))
            result=driver.audit(root,results)
            self.assertEqual(result['rows'][0]['structure']['groups'],1)
            self.assertEqual(sha,driver.digest(candidate))
            candidate.write_text('{}')
            with self.assertRaises(ValueError):driver.audit(root,results)

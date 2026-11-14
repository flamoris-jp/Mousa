"""Admission tests never construct a predictive model or read real source MIDI."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
TOOLS=Path(__file__).resolve().parents[1]/'tools'
sys.path.insert(0,str(TOOLS))
try:
    spec=importlib.util.spec_from_file_location('mendelssohn_test',TOOLS/'evaluate_mendelssohn1741_transfer.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
finally:sys.path.pop(0)


class MendelssohnAdmissionTests(unittest.TestCase):
    def test_clearance_fail_closed(self):
        valid=dict(status='cleared',source_sha256=m.EXPECTED,flagged=False,screen_threshold=.8)
        m.check_clearance(valid)
        for field,value in [('status','pending'),('source_sha256','other'),('flagged',True),('flagged',None),('screen_threshold',.81)]:
            with self.subTest(field=field,value=value):
                with self.assertRaises(ValueError):m.check_clearance(dict(valid,**{field:value}))
        with self.assertRaises(ValueError):m.check_clearance({})

    def test_blocked_admission_never_constructs_models(self):
        for reason in ('clearance','local_match','unsupported'):
            with self.subTest(reason=reason),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);pd=root/'plan';pd.mkdir();source=root/'source';extra=root/'extra'
                plan=dict(code_sha256={});(pd/'plan.json').write_text(json.dumps(plan))
                screen=dict(plan_sha256=m.digest(pd/'plan.json'),any_flagged=reason=='local_match',
                            coverage=dict(unsupported_events=['unsupported'] if reason=='unsupported' else []))
                (pd/'prescore-screen.json').write_text(json.dumps(screen));clear=root/'clear.json'
                decision=dict(status='cleared',source_sha256=m.EXPECTED,flagged=False,screen_threshold=.8)
                if reason=='clearance':decision['status']='pending'
                clear.write_text(json.dumps(decision));real_digest=m.digest
                def digest(p):
                    return m.EXPECTED if p==source else m.EXTRA if p==extra else real_digest(p)
                with patch.object(m,'digest',side_effect=digest),patch.object(m,'OnsetGateModel') as model,patch.object(m,'ContextOnsetGateModel') as ctx,patch.object(m,'read_midi') as reader:
                    with self.assertRaises(ValueError):m.score(root,root,source,extra,pd,clear,root/'out')
                    model.assert_not_called();ctx.assert_not_called();reader.assert_not_called()
                    self.assertFalse((root/'out').exists())

if __name__=='__main__':unittest.main()

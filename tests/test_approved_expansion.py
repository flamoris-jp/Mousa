import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
TOOLS=Path(__file__).resolve().parents[1]/'tools';sys.path.insert(0,str(TOOLS))
try:
    spec=importlib.util.spec_from_file_location('approved_expansion_test',TOOLS/'compare_approved_expansion.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
finally:sys.path.pop(0)


def assignment():
    return dict(schema_version=1,related_evaluation_exclusions=['mutopia-580'],diagnostic_families={'640':['adam'],'921':['chopin']},
        additions=[dict(work_id='synthetic-new',canonical_source_id='fixture-1',family_id='fixturefamily',file='fixture.mid',sha256='a'*64,
        rights_evidence='fixture-rights.json',rights_evidence_sha256='b'*64,track=1,rights_approved=True,family_reviewed=True,review_reference='fictional unit fixture, not actual consent')])


class ApprovedExpansionTests(unittest.TestCase):
    def test_assignment_and_forbidden_sources(self):
        self.assertEqual(len(m.validate_assignment(assignment())),1)
        for key,value in [('work_id','mutopia-804'),('canonical_source_id','mutopia-1741'),('track',True),('rights_approved',False),('family_reviewed',False),('family_id','adam')]:
            a=assignment();a['additions'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):m.validate_assignment(a)
        with self.assertRaises(ValueError):m.validate_assignment(assignment(),{'a'*64})
        a=assignment();a['additions']*=2
        with self.assertRaises(ValueError):m.validate_assignment(a)
        a=assignment();a['diagnostic_families'].pop('640')
        with self.assertRaises(ValueError):m.validate_assignment(a)

    def test_relative_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.assertEqual(m.safe_path(root,'x'),root/'x')
            for value in ('../escape','/absolute',''):
                with self.assertRaises(ValueError):m.safe_path(root,value)

    def test_no_review_or_blocked_screen_never_fit(self):
        for blocked in (True,False):
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);pd=root/'plan';pd.mkdir();ap=root/'assignment';ap.write_text(json.dumps(assignment()))
                plan=dict(assignment_sha256=m.digest(ap));(pd/'plan.json').write_text(json.dumps(plan))
                (pd/'screen.json').write_text(json.dumps(dict(plan_sha256=m.digest(pd/'plan.json'),blocked=blocked)))
                clear=root/'clear';clear.write_text('{}')
                with patch.object(m,'read_inputs') as reader,patch.object(m,'OnsetGateModel') as fit,patch.object(m,'ContextOnsetGateModel') as context:
                    with self.assertRaises(ValueError):m.run(root,root,root/'extra',root,ap,{},pd,clear,root/'out')
                    reader.assert_not_called();fit.assert_not_called();context.assert_not_called()
                    self.assertFalse((root/'out').exists())

if __name__=='__main__':unittest.main()

import copy
import unittest
import sys
from pathlib import Path
from unittest.mock import patch
with patch.object(sys, 'path', [str(Path(__file__).resolve().parents[1] / 'tools'), *sys.path]):
    import compare_approved_expansion as base
    import compare_fourteen_approved_expansion as new


def fixture(n):
    works = [dict(work_id=f'new-{i}', canonical_source_id=f'new-{i}', family_id='new-family',
        file=f'{i}.mid', rights_evidence='evidence.json', review_reference='synthetic test only',
        sha256=f'{i:064x}', rights_evidence_sha256='a'*64, track=1,
        rights_approved=True, family_reviewed=True) for i in range(n)]
    return dict(schema_version=1, related_evaluation_exclusions=['mutopia-580'],
        diagnostic_families={'640':['adam'], '921':['chopin']}, additions=works)


class FourteenProfileTests(unittest.TestCase):
    def test_bounds_and_original_unchanged(self):
        with self.assertRaises(ValueError): base.validate_assignment(fixture(8))
        self.assertEqual(len(new.validate_assignment(fixture(9))), 9)
        for n in (0,10):
            with self.assertRaises(ValueError): new.validate_assignment(fixture(n))

    def test_global_duplicates(self):
        for key in ('work_id','sha256'):
            a=fixture(9);a['additions'][8][key]=a['additions'][0][key]
            with self.assertRaises(ValueError): new.validate_assignment(a)

    def test_original_gates_remain(self):
        for key,value in [('canonical_source_id','mutopia-1692'),('work_id','mutopia-804'),
                          ('family_id','adam'),('rights_approved',False),('track',True)]:
            a=fixture(9);a['additions'][8][key]=value
            with self.assertRaises(ValueError):new.validate_assignment(a)
        with self.assertRaises(ValueError):new.validate_assignment(fixture(9),{f'{8:064x}'})

    def test_scoped_restoration(self):
        old=base.validate_assignment
        with new.nine_addition_validation():
            self.assertIs(base.validate_assignment,new.validate_assignment)
            self.assertEqual(len(base.validate_assignment(fixture(9))),9)
        self.assertIs(base.validate_assignment,old)
        with self.assertRaises(RuntimeError):
            with new.nine_addition_validation():raise RuntimeError('synthetic failure')
        self.assertIs(base.validate_assignment,old)
        with self.assertRaises(ValueError):base.validate_assignment(fixture(8))

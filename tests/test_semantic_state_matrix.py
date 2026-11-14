"""Systematic fictional-state combinations, never actual listener evidence."""
from itertools import product
from test_semantic_evidence import fictional_record
from mousa.semantic_evidence import validate,training_eligible,summarize
import unittest


def state_matrix():
    rows=[]
    for i,(kind,state,actor,fictional,use) in enumerate(product(
        ('observed-source','human-report','hypothesis'),
        ('missing','pending','rejected','approved'),
        ('synthetic-observer','fictional-listener','synthetic-researcher'),
        (False,True),('none','synthetic-schema-test','train'))):
        r=fictional_record(kind,f'matrix-{i}')
        r['review']['state']=state;r['provenance'].update(actor_role=actor,fictional=fictional);r['permitted_use']=use
        rows.append(r)
    return rows


class SemanticStateMatrixTests(unittest.TestCase):
    def test_all216_states_fail_closed_for_training(self):
        rows=state_matrix();result=summarize(rows)
        self.assertEqual(len(rows),216);self.assertEqual(result['accepted'],24)
        self.assertEqual(result['rejected'],192);self.assertEqual(result['actual_human_reports'],0)
        self.assertEqual(result['training_eligible'],0)
        for r in rows:
            try:validate(r)
            except ValueError:continue
            self.assertFalse(training_eligible(r))
            self.assertIs(r['provenance']['fictional'],True)
            self.assertNotEqual(r['permitted_use'],'train')

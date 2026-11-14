import unittest
from mousa.semantic_split_guard import audit


def row(i,family,source,artifact,split):
    return dict(item_id=str(i),family_id=family,source_sha256=source*64,artifact_sha256=artifact*64,split=split,synthetic=True)


class SemanticSplitTests(unittest.TestCase):
    def test_distinct_groups_not_permission(self):
        r=audit([row(1,'a','1','2','train'),row(2,'b','3','4','test')])
        self.assertTrue(r['partition_consistent']);self.assertFalse(r['training_authorized'])
        self.assertEqual(r['actual_human_reports'],0)

    def test_transformed_sibling_cannot_cross_split(self):
        r=audit([row(1,'a','1','2','train'),row(2,'a','3','4','test')])
        self.assertEqual([v['reason'] for v in r['violations']],['cross_split_family_id'])

    def test_changed_family_label_does_not_hide_duplicate_source(self):
        r=audit([row(1,'a','1','2','train'),row(2,'b','1','3','test')])
        self.assertFalse(r['partition_consistent'])
        self.assertIn('cross_split_source_sha256',[v['reason'] for v in r['violations']])
        self.assertIn('conflicting_source_family',[v['reason'] for v in r['violations']])

    def test_same_clip_multiple_comments_are_not_independent_artifacts(self):
        r=audit([row(1,'a','1','2','test'),row(2,'a','1','2','test')])
        self.assertTrue(r['partition_consistent']);self.assertEqual(r['row_counts']['test'],2)
        self.assertEqual(r['artifact_counts']['test'],1);self.assertEqual(r['family_counts']['test'],1)

    def test_malformed_and_real_inputs_rejected(self):
        r=row(1,'a','1','2','test');r['synthetic']=False
        with self.assertRaises(ValueError):audit([r])
        with self.assertRaises(ValueError):audit([row(1,'a','1','2','test')]*2)
        r=row(1,'a','1','2','test');r['split']='approved'
        with self.assertRaises(ValueError):audit([r])

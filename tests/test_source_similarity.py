import unittest
from mousa.source_similarity import interval_edit_similarity


class SourceSimilarityTests(unittest.TestCase):
    def test_transposition_and_rhythm_invariance(self):
        a=[4,6,7,5]*6;b=sum(([t+3,1,0] for t in a),[])
        r=interval_edit_similarity(a,b)
        self.assertTrue(r['comparable']);self.assertEqual(r['normalized_similarity'],1)

    def test_changed_note_not_identical(self):
        a=[4,6,7,5]*6;b=a.copy();b[12]=10
        r=interval_edit_similarity(a,b)
        self.assertGreater(r['normalized_similarity'],.8);self.assertLess(r['normalized_similarity'],1)
        self.assertEqual(r['edit_distance'],2)

    def test_short_and_bound(self):
        self.assertFalse(interval_edit_similarity([4],[5])['comparable'])
        self.assertIsNone(interval_edit_similarity([4],[5])['normalized_similarity'])
        with self.assertRaises(ValueError):interval_edit_similarity([4]*513,[5]*513)
        with self.assertRaises(ValueError):interval_edit_similarity([1],[5])

    def test_symmetry_insert_delete(self):
        a=[4,6,7,5]*6;b=a[:10]+[12]+a[10:]
        self.assertEqual(interval_edit_similarity(a,b)['edit_distance'],interval_edit_similarity(b,a)['edit_distance'])

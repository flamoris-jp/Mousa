import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('groove_split',Path(__file__).resolve().parents[1]/'tools/prepare_groove_split.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class GrooveSplitTests(unittest.TestCase):
    def test_full_normalization_offset_and_tempo(self):
        a=[(10,36),(110,38),(110,42),(310,36)]
        b=[(100+3*t,k) for t,k in a]
        r=m.compare(m.features(a),m.features(b))
        self.assertTrue(r['tempo_offset_normalized']);self.assertTrue(r['strong_unresolved'])
        self.assertFalse(r['exact_onset_key'])
        b[-1]=(b[-1][0],40)
        self.assertFalse(m.compare(m.features(a),m.features(b))['tempo_offset_normalized'])
    def test_common_windows_are_not_duplicate_verdict(self):
        a=[(i*120,36 if i%2 else 38) for i in range(12)]
        b=a+[(2000+i*130,40+i%3) for i in range(20)]
        r=m.compare(m.features(a),m.features(b))
        self.assertGreater(r['shared_unique_windows'],0)
        self.assertFalse(r['strong_unresolved'])
        self.assertEqual(r['first_matching_event_indices'],(0,0))
    def test_integer_timing_not_mutated_and_bounds(self):
        a=[(0,36),(61,38),(30782,42)]
        original=list(a);f=m.features(a)
        self.assertEqual(a,original);self.assertEqual(f['unsupported_iois'],1)
        for bad in ([],[(True,36)],[(1,128)],[(2,36),(1,38)]):
            with self.assertRaises(ValueError):m.features(bad)
    def test_drummer_split_includes_sessions(self):
        self.assertEqual(m.split_for('drummer1'),'train')
        self.assertEqual(m.split_for('drummer8'),'validation')
        self.assertEqual(m.split_for('drummer10'),'test')
        with self.assertRaises(ValueError):m.split_for('drummer11')

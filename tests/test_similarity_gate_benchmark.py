import importlib.util
from pathlib import Path
import sys
import unittest
TOOLS=Path(__file__).resolve().parents[1]/'tools';sys.path.insert(0,str(TOOLS))
try:
    spec=importlib.util.spec_from_file_location('synthetic_gate_test',TOOLS/'benchmark_similarity_gate.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
finally:sys.path.pop(0)

class SimilarityBenchmarkTests(unittest.TestCase):
    def test_reproducible_bounded_design(self):
        cases=m.cases();self.assertEqual(cases,m.cases());self.assertEqual(len(cases),80)
        self.assertEqual(len({r['id'] for r in cases}),80)
        for c in cases:
            for v in (c['reference'],c['target']):
                self.assertEqual(len(v['pitches']),len(v['durations']))
                self.assertTrue(all(0<=p<=127 for p in v['pitches']))
                self.assertTrue(all(d>0 for d in v['durations']))

    def inspect(self,p,q,a,b):
        return m.inspect(dict(id='unit',seed=0,category='transposition',construction='derived',
            reference=dict(pitches=p,durations=a),target=dict(pitches=q,durations=b)))

    def test_short_match_global_not_exact8(self):
        r=self.inspect(list(range(7)),list(range(7)),[1]*7,[2]*7)
        self.assertEqual(r['unique_exact8_interval_matches'],0)
        self.assertEqual(r['global_interval_similarity'],1)
        self.assertTrue(r['blocked'])

    def test_locations_rhythm_does_not_override_gate(self):
        r=self.inspect(list(range(10)),list(range(20,30)),[2]*10,[6]*10)
        self.assertEqual(r['exact8_location_pairs'],9)
        self.assertEqual(len(r['locations']),8);self.assertTrue(r['locations_truncated'])
        self.assertEqual(r['exact_rhythm_location_pairs'],0)
        self.assertEqual(r['scaled_rhythm_location_pairs'],9)
        self.assertTrue(r['blocked'])

    def test_empty_strata_and_large_rejection(self):
        self.assertTrue(all(v['denominator']==0 for v in m.summarize([]).values()))
        with self.assertRaises(ValueError):self.inspect([1]*65,[1]*8,[1]*65,[1]*8)

if __name__=='__main__':unittest.main()

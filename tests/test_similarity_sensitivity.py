import importlib.util
from pathlib import Path
import sys
import unittest
TOOLS=Path(__file__).resolve().parents[1]/'tools';sys.path.insert(0,str(TOOLS))
try:
    spec=importlib.util.spec_from_file_location('similarity_sensitivity_test',TOOLS/'probe_similarity_sensitivity.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
finally:sys.path.pop(0)


class SimilaritySensitivityTests(unittest.TestCase):
    def row(self,name):
        r=next(r for r in module.fixtures() if r['name']==name)
        return module.compare(r['reference'],r['candidate'])

    def test_transposition_and_origin_invariance(self):
        for name in ('identical_distinctive','transpose_plus5','shift_origin'):
            r=self.row(name);self.assertEqual(r['exact8_interval_matches'],1)
            self.assertEqual(r['exact8_interval_onset_gate_matches'],1)

    def test_scaling_vs_metadata_tempo(self):
        r=self.row('duration_scale2')
        self.assertEqual(r['exact8_interval_onset_gate_matches'],0)
        self.assertEqual(r['scale_normalized8_interval_onset_gate_matches'],1)
        self.assertEqual(self.row('tempo_metadata_only')['exact8_interval_onset_gate_matches'],1)

    def test_jitter_brittleness(self):
        for name in ('onset_jitter1tick','gate_jitter1tick'):
            r=self.row(name);self.assertEqual(r['exact8_interval_matches'],1)
            self.assertEqual(r['exact8_interval_onset_gate_matches'],0)
            self.assertEqual(r['scale_normalized8_interval_onset_gate_matches'],0)

    def test_common_pattern_counterexamples(self):
        for name in ('common_scale_different_rhythm','common_repeat_different_rhythm'):
            r=self.row(name);self.assertEqual(r['exact8_interval_matches'],1)
            self.assertEqual(r['exact8_interval_onset_gate_matches'],0)
        self.assertEqual(self.row('common_scale_scaled')['scale_normalized8_interval_onset_gate_matches'],1)

    def test_window_length_and_edit(self):
        r=self.row('seven_note_identity');self.assertEqual(r['exact8_interval_matches'],0)
        self.assertEqual(r['whole_interval_edit_similarity'],1)
        for name in ('insert_note','delete_note','alter_one_pitch'):
            r=self.row(name);self.assertEqual(r['exact8_interval_matches'],0)
            self.assertTrue(0<r['whole_interval_edit_similarity']<1)
        self.assertEqual(self.row('match_embedded_longer')['exact8_interval_matches'],1)

    def test_invalid_order_and_zero_gate(self):
        for n in (((60,0,0),),((60,0,1),(62,0,1)),((True,0,1),)):
            with self.assertRaises(ValueError):module.windows(n,rhythm=True,normalized=True)


if __name__=='__main__':unittest.main()

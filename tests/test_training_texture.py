import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

P=Path(__file__).resolve().parents[1]/'tools/analyze_training_texture.py'
SPEC=importlib.util.spec_from_file_location('training_texture_test',P)
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)


class TrainingTextureTests(unittest.TestCase):
    def test_simultaneous_is_not_voice_label(self):
        ns=[SimpleNamespace(start=s,pitch=p) for s,p in [(0,60),(0,72),(96,59),(192,59)]]
        r=M.describe(ns)
        self.assertEqual(r['pitch_transitions'],3)
        self.assertEqual(r['strata']['simultaneous_onset']['absolute_interval_sum'],12)
        self.assertEqual(r['strata']['later_onset']['above_octave'],1)
        self.assertEqual(r['strata']['later_onset']['repeated_pitch'],1)
        self.assertEqual(r['max_notes_sharing_onset'],2)

    def test_single_note_and_order_validation(self):
        self.assertEqual(M.describe([SimpleNamespace(start=1,pitch=60)])['pitch_transitions'],0)
        with self.assertRaises(ValueError):M.describe([])
        with self.assertRaises(ValueError):M.describe([SimpleNamespace(start=2,pitch=60),SimpleNamespace(start=1,pitch=60)])


if __name__=='__main__':unittest.main()

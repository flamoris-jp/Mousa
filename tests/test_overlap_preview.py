import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
spec=importlib.util.spec_from_file_location('overlap_preview_test',Path(__file__).resolve().parents[1]/'tools/render_overlap_preview.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class OverlapPreviewTests(unittest.TestCase):
    def test_overlap_added_not_overwritten_and_silence_preserved(self):
        note=SimpleNamespace(start=0,end=96,pitch=60)
        a,ma=m.samples([note],192);b,mb=m.samples([note,note],192)
        self.assertAlmostEqual(mb['peak_linear'],2*ma['peak_linear'])
        self.assertEqual(len(a),len(b));self.assertEqual(a[-100:],bytes(100))
        self.assertEqual(ma['frames'],5512)

    def test_invalid_duration_and_frequency_rejected(self):
        with self.assertRaises(ValueError):m.samples([SimpleNamespace(start=0,end=100,pitch=60)],96)
        with self.assertRaises(ValueError):m.samples([SimpleNamespace(start=0,end=96,pitch=127)],96)

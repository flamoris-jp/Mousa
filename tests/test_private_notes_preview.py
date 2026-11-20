import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
TOOLS=Path(__file__).resolve().parents[1]/'tools';sys.path.insert(0,str(TOOLS))
try:
    spec=importlib.util.spec_from_file_location('private_notes_preview_test',TOOLS/'export_private_notes_preview.py')
    M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
finally:sys.path.pop(0)
try:
    import mido
except ImportError:
    mido=None


class PrivatePreviewTests(unittest.TestCase):
    def test_hash_mismatch_blocks_output(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'notes.json';p.write_text('[]')
            with self.assertRaises(ValueError):M.export(p,'0'*64,Path(t)/'out')
            self.assertFalse((Path(t)/'out').exists())

    @unittest.skipUnless(mido,'optional mido unavailable')
    def test_overlap_tail_and_audio_repeat(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'notes.json';p.write_text(json.dumps([dict(start=0,end=384,pitch=60),dict(start=192,end=576,pitch=67)]))
            r=M.export(p,hashlib.sha256(p.read_bytes()).hexdigest(),Path(t)/'out')
            self.assertTrue(r['exact_note_gate_order_roundtrip'])
            self.assertTrue(r['wav_repeat_identical'])
            self.assertEqual(r['audio']['frames'],264600)
            self.assertEqual(r['audio']['clipped_samples'],0)
            self.assertEqual(r['bars'],8)

if __name__=='__main__':unittest.main()

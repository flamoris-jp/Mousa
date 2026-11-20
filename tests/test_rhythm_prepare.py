"""Synthetic preparation tests; no corpus or external files required."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

from mousa.rhythm_learning import encode

_PATH = Path(__file__).resolve().parents[1]/'experiments/maidionis-rhythm-learning/prepare.py'
_SPEC = importlib.util.spec_from_file_location('rhythm_prepare', _PATH)
PREP = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(PREP)
try:
    import mido
except ImportError:
    mido = None


class CodecParity(unittest.TestCase):
    def test_encoding(self):
        history = [[64,11,5,6,2,0]]*8
        for task in range(6):
            self.assertEqual(PREP.encode(history,7,12,task),encode(history,7,12,task))

    def test_bad_values(self):
        for event in ([64,48,5,6,2,0],[71,11,5,6,2,0],[64,11,5,6,4,0]):
            with self.assertRaises(ValueError):PREP.encode([event]*8,7,0,0)


@unittest.skipIf(mido is None, 'mido optional')
class Extraction(unittest.TestCase):
    def fixture(self, root, pitches=None, numerator=4, keys=('C',), gate=240, step=480):
        midi=mido.MidiFile(ticks_per_beat=480);track=mido.MidiTrack();midi.tracks.append(track)
        track.append(mido.MetaMessage('time_signature',numerator=numerator,denominator=4))
        for key in keys:track.append(mido.MetaMessage('key_signature',key=key))
        for index,pitch in enumerate(pitches or [60]*20):
            track.append(mido.Message('note_on',note=pitch,velocity=64,time=0 if index==0 else step-gate))
            track.append(mido.Message('note_off',note=pitch,velocity=0,time=gate))
        path=Path(root)/'test.mid';midi.save(path);return path

    def test_causal_windows_and_labels(self):
        with tempfile.TemporaryDirectory() as root:
            rows,events,info=PREP.event_rows(self.fixture(root))
        self.assertEqual(len(events),19);self.assertEqual(len(rows),11)
        self.assertEqual(rows[0]['target_index'],8)
        self.assertEqual(rows[0]['labels'],[64,11,5,6,1,0])
        self.assertEqual(rows[0]['history'],[[64,11,5,6,1,0]]*8)
        self.assertEqual(info['quantization_max_error_beats'],dict(onset=0.0,ioi=0.0,duration=0.0))

    def test_invalid_degree_breaks_history(self):
        with tempfile.TemporaryDirectory() as root:
            rows,_,info=PREP.event_rows(self.fixture(root,pitches=[60]*9+[61]+[60]*12))
        indices=[r['target_index'] for r in rows]
        self.assertEqual(indices,[8,18,19,20]);self.assertEqual(info['rejected']['off_scale_or_register'],1)

    def test_large_ioi_breaks(self):
        with tempfile.TemporaryDirectory() as root:
            rows,events,info=PREP.event_rows(self.fixture(root,step=2401))
        self.assertEqual(rows,[]);self.assertEqual(events,[])
        self.assertEqual(info['rejected']['ioi_outside_4beats_or_nonpositive_gate'],19)

    def test_meter_and_key_rejected(self):
        for kwargs in ({'numerator':3},{'keys':()},{'keys':('C','G')}):
            with tempfile.TemporaryDirectory() as root:
                with self.assertRaises(ValueError):PREP.event_rows(self.fixture(root,**kwargs))

    def test_phrase_is_weak_rest_label(self):
        with tempfile.TemporaryDirectory() as root:
            rows,_,_=PREP.event_rows(self.fixture(root,step=960,gate=240))
        self.assertEqual(rows[0]['labels'],[64,23,5,18,1,1])

    def test_maximum_event_bound(self):
        with tempfile.TemporaryDirectory() as root:
            rows,events,info=PREP.event_rows(self.fixture(root,pitches=[60]*180))
        self.assertEqual(len(events),128);self.assertEqual(len(rows),120)
        self.assertEqual(info['source_notes_bounded'],129)


if __name__ == '__main__':unittest.main()

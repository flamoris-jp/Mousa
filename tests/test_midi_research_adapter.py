import importlib.util
from pathlib import Path
import tempfile
import unittest
from mousa.midi_research_adapter import read_grid

@unittest.skipUnless(importlib.util.find_spec('mido'),'optional mido research dependency')
class AdapterTests(unittest.TestCase):
    def setUp(self):
        import mido
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'fixture.mid'
        midi=mido.MidiFile(ticks_per_beat=480)
        track=mido.MidiTrack();midi.tracks.append(track)
        track.extend([mido.Message('note_on',note=65,time=0),mido.Message('note_off',note=65,time=120),mido.MetaMessage('end_of_track',time=15240)])
        midi.save(self.path)
    @staticmethod
    def reader(path,index):return [2]+[0]*15,{'transposition_semitones':-5}
    def test_restores_end_of_track(self):
        t,d=read_grid(self.path,0,self.reader)
        self.assertEqual(len(t),128);self.assertEqual(d['trailing_steps_restored'],112)
    def test_original_pitch_retained(self):
        t,d=read_grid(self.path,0,self.reader);self.assertEqual(t[0],7)
        n,_=read_grid(self.path,0,self.reader,preserve_pitch=False);self.assertEqual(n[0],2)
    def test_out_of_vocabulary_rejected(self):
        with self.assertRaises(ValueError):read_grid(self.path,0,lambda p,i:([2],{'transposition_semitones':3}))
    def test_symlink_rejected(self):
        p=self.path.with_name('link.mid');p.symlink_to(self.path)
        with self.assertRaises(ValueError):read_grid(p,0,self.reader)

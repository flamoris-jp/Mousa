import importlib.util
from pathlib import Path
import tempfile
import unittest

P=Path(__file__).resolve().parents[1]/'experiments/maidionis-checkpoint-generation/validate_export.py'
spec=importlib.util.spec_from_file_location('generated_guard',P);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)

def events():return [{'pitch':60+i%3,'onset_tick':i*480,'duration_tick':432} for i in range(32)]

class GeneratedGuardTests(unittest.TestCase):
    def test_eight_bar_valid(self):
        f=g.validate_events(events());self.assertEqual(len(f['pitch']),31);self.assertEqual(f['rhythm'],[12]*31)
    def test_invalid_time(self):
        xs=events();xs[1]['onset_tick']=0
        with self.assertRaises(ValueError):g.validate_events(xs)
    def test_pitch_and_duration(self):
        for key,value in [('pitch',85),('duration_tick',481)]:
            xs=events();xs[2][key]=value
            with self.assertRaises(ValueError):g.validate_events(xs)
    def test_last_gap_and_initial(self):
        for mutate in [lambda xs:xs.pop(),lambda xs:xs[0].update(pitch=61)]:
            xs=events();mutate(xs)
            with self.assertRaises(ValueError):g.validate_events(xs)
    def test_transposition_invariant_pitch_guard(self):
        f=g.validate_events(events());r={'family':'r','pitch':f['pitch'],'rhythm':[10]*31}
        self.assertTrue(g.copy_screen(f,[r])['blocked'])
        self.assertEqual(g.copy_screen(f,[r])['max_pitch_interval_run'],31)
    def test_pair_threshold(self):
        f={'pitch':list(range(8)),'rhythm':[12]*8};r={'family':'r',**f}
        self.assertTrue(g.copy_screen(f,[r])['blocked'])
        f={'pitch':list(range(7)),'rhythm':[12]*7};r={'family':'r',**f}
        self.assertFalse(g.copy_screen(f,[r])['blocked'])
    def test_contiguous_not_subsequence(self):
        self.assertEqual(g.longest_contiguous([1,2,3],[1,9,2,9,3]),1)
        self.assertEqual(g.longest_contiguous([1,2,1,2,3],[9,1,2,3]),3)
    @unittest.skipUnless(importlib.util.find_spec('mido'),'optional MIDI dependency')
    def test_midi_roundtrip_overwrite_corruption(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'candidate.mid';xs=events();g.write_midi(xs,p);self.assertTrue(g.verify_midi(xs,p))
            with self.assertRaises(ValueError):g.write_midi(xs,p)
            import mido
            m=mido.MidiFile(p);m.ticks_per_beat=960;m.save(p)
            with self.assertRaises(ValueError):g.verify_midi(xs,p)

if __name__=='__main__':unittest.main()

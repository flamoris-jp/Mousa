from dataclasses import replace
import importlib.util
from pathlib import Path
import tempfile
import unittest
from mousa.tick_midi import TickNote
from mousa.variable_meter_midi import MeterChange
from mousa.overlap_midi import OverlapMelody, validate, read_midi, write_midi


class OverlapTests(unittest.TestCase):
    def model(self):
        return OverlapMelody(notes=(TickNote(1,300,60,81,3),TickNote(30,100,64,82,4),
                                     TickNote(50,200,67,83,5)),total_ticks=400,meter=(3,2),
            volume_map=((1,70),),program_map=((0,0),(1,71)),
            tempo_map=((0,500000),(200,700000)),source_total_ticks=600,
            meter_map=(MeterChange(0,3,2,48),MeterChange(500,2,2,48)),
            channel_events=((0,'program',0,0),(1,'note_on',60,81),(1,'volume',70,0),
                (1,'program',71,0),(30,'note_on',64,82),(50,'note_on',67,83),
                (100,'note_off',64,4),(200,'note_off',67,5),(300,'note_off',60,3)))

    def test_three_overlapping_notes_no_truncation(self):
        m=validate(self.model())
        self.assertEqual([n.end for n in m.notes],[300,100,200])
        self.assertGreater(m.notes[0].end,m.notes[2].end)

    def test_same_pitch_ambiguity_rejected(self):
        m=OverlapMelody((TickNote(0,20,60),TickNote(10,30,60)),40,(4,4))
        with self.assertRaisesRegex(ValueError,'same-pitch'):validate(m)

    def test_same_pitch_adjacent_rearticulation_preserved(self):
        m=OverlapMelody((TickNote(0,20,60),TickNote(20,30,60)),40,(4,4))
        self.assertEqual(len(validate(m).notes),2)

    def test_stale_stream_and_resource_bounds(self):
        m=self.model()
        with self.assertRaises(ValueError):validate(replace(m,notes=m.notes[:2]))
        with self.assertRaises(ValueError):validate(replace(m,total_ticks=480*1024+1))
        with self.assertRaises(ValueError):validate(replace(m,meter_map=(MeterChange(0,3,3),)))

    @unittest.skipUnless(importlib.util.find_spec('mido'),'optional mido unavailable')
    def test_roundtrip_all_fields_and_old_profiles_reject(self):
        from mousa import variable_meter_midi
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'poly.mid';m=self.model()
            write_midi(m,path)
            self.assertEqual(read_midi(path,1),m)
            with self.assertRaises(ValueError):variable_meter_midi.read_midi(path,1)
            with self.assertRaises(FileExistsError):write_midi(m,path)

    @unittest.skipUnless(importlib.util.find_spec('mido'),'optional mido unavailable')
    def test_raw_same_pitch_and_controls_reject(self):
        import mido
        for extra in (mido.Message('note_on',note=60,velocity=70),
                      mido.Message('control_change',control=64,value=127),
                      mido.Message('pitchwheel',pitch=0)):
            with tempfile.TemporaryDirectory() as directory:
                path=Path(directory)/'bad.mid';write_midi(self.model(),path)
                midi=mido.MidiFile(path)
                # Insert after original first onset at tick1, delta0.
                midi.tracks[1].insert(2,extra)
                midi.save(path)
                with self.assertRaises(ValueError):read_midi(path,1)

    @unittest.skipUnless(importlib.util.find_spec('mido'),'optional mido unavailable')
    def test_tied_noteoffs_wrong_pitch_reject(self):
        import mido
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'bad.mid';write_midi(self.model(),path)
            midi=mido.MidiFile(path)
            for event in midi.tracks[1]:
                if event.type=='note_off':event.note=61;break
            midi.save(path)
            with self.assertRaisesRegex(ValueError,'unmatched'):read_midi(path,1)


if __name__=='__main__':unittest.main()

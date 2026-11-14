from dataclasses import replace
from fractions import Fraction
import importlib.util
from pathlib import Path
import tempfile
import unittest
from mousa.tick_midi import TickNote
from mousa.variable_meter_midi import VariableMeterMelody, MeterChange, validate, read_midi, write_midi


class VariableMeterTests(unittest.TestCase):
    def model(self):
        return VariableMeterMelody(notes=(TickNote(1,127,60,81,23),),total_ticks=481,
            meter=(2,2),ppq=384,tempo_map=((0,500000),(130,700000)),
            volume_map=((1,75),),program_map=((0,0),(1,71)),
            channel_events=((0,'program',0,0),(1,'note_on',60,81),(1,'volume',75,0),
                            (1,'program',71,0),(127,'note_off',60,23)),
            source_total_ticks=600,
            meter_map=(MeterChange(0,2,2,48),MeterChange(200,3,2,48),MeterChange(550,6,8,36)))

    def test_validate_seconds(self):
        m=validate(self.model())
        self.assertEqual(m.seconds_at_tick(130),Fraction(130*500000,384000000))
        self.assertEqual(m.notes[0].start,1)

    def test_invalid_maps(self):
        m=self.model()
        for changes in ((),(MeterChange(1,2,2),),
                        (MeterChange(0,2,2),MeterChange(0,3,2)),
                        (MeterChange(0,2,3),),(MeterChange(0,True,2),),
                        (MeterChange(0,2,2),MeterChange(601,3,2))):
            with self.assertRaises(ValueError):validate(replace(m,meter_map=changes))
        with self.assertRaises(ValueError):validate(replace(m,meter=(4,4)))

    @unittest.skipUnless(importlib.util.find_spec('mido'),'optional mido unavailable')
    def test_roundtrip_all_fields_and_old_reader_remains_strict(self):
        from mousa import tick_midi
        for changes in ((MeterChange(0,2,2,48),),(MeterChange(0,3,2,48),),self.model().meter_map):
            m=replace(self.model(),meter=(changes[0].numerator,changes[0].denominator),meter_map=changes)
            with tempfile.TemporaryDirectory() as directory:
                path=Path(directory)/'melody.mid'
                write_midi(m,path)
                self.assertEqual(read_midi(path,1),m)
                with self.assertRaises(ValueError):tick_midi.read_midi(path,1)
                with self.assertRaises(FileExistsError):write_midi(m,path)

    @unittest.skipUnless(importlib.util.find_spec('mido'),'optional mido unavailable')
    def test_same_tick_conflicts_and_missing_initial(self):
        import mido
        for changes in ([mido.MetaMessage('time_signature',numerator=2,denominator=2),
                         mido.MetaMessage('time_signature',numerator=3,denominator=2)],
                        [mido.MetaMessage('time_signature',numerator=2,denominator=2,time=1)],
                        [mido.MetaMessage('time_signature',numerator=2,denominator=2),
                         mido.MetaMessage('time_signature',numerator=2,denominator=2,clocks_per_click=48)]):
            with tempfile.TemporaryDirectory() as directory:
                midi=mido.MidiFile();midi.tracks.append(mido.MidiTrack(changes))
                midi.tracks.append(mido.MidiTrack([mido.Message('note_on',note=60),
                    mido.Message('note_off',note=60,time=120),mido.MetaMessage('end_of_track')]))
                path=Path(directory)/'bad.mid';midi.save(path)
                with self.assertRaises(ValueError):read_midi(path,1)

    @unittest.skipUnless(importlib.util.find_spec('mido'),'optional mido unavailable')
    def test_unsupported_control_stays_rejected(self):
        import mido
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'bad.mid';write_midi(self.model(),path)
            midi=mido.MidiFile(path)
            midi.tracks[1].insert(0,mido.Message('control_change',control=64,value=127))
            midi.save(path)
            with self.assertRaises(ValueError):read_midi(path,1)

    @unittest.skipUnless(importlib.util.find_spec('mido'),'optional mido unavailable')
    def test_duplicate_identical_meter_collapses(self):
        import mido
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'copy.mid';write_midi(self.model(),path)
            midi=mido.MidiFile(path);midi.tracks[0].insert(0,midi.tracks[0][0].copy());midi.save(path)
            self.assertEqual(read_midi(path,1),self.model())


if __name__=='__main__':unittest.main()

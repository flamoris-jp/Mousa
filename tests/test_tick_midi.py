from dataclasses import replace
from fractions import Fraction
import importlib.util
from pathlib import Path
import tempfile
import unittest
from mousa.tick_midi import TickNote, TickMelody, validate, to_tokens, inspect_grid_error, read_midi, write_midi


class TickValueTests(unittest.TestCase):
    def test_seconds_integrates_tempo(self):
        m=TickMelody((TickNote(0,480,60),),960,(4,4),tempo_map=((0,500000),(480,1000000)))
        self.assertEqual(m.seconds_at_tick(240),Fraction(1,4))
        self.assertEqual(m.seconds_at_tick(960),Fraction(3,2))

    def test_projection_exact_no_quantization(self):
        m=TickMelody((TickNote(0,120,60),),480,(4,4),tempo_map=((0,500000),(17,600000)))
        self.assertEqual(to_tokens(m),[2,0,0,0])
        with self.assertRaises(ValueError):to_tokens(replace(m,notes=(TickNote(1,120,60),)))
        with self.assertRaises(ValueError):to_tokens(replace(m,total_ticks=481))
        self.assertEqual(m.tempo_map[1][0],17)

    def test_grid_diagnostic_only(self):
        m=TickMelody((TickNote(1,2,60),),121,(4,4))
        r=inspect_grid_error(m)
        self.assertEqual(r['boundary_count'],3)
        self.assertEqual(r['off_grid_count'],3)
        self.assertEqual(r['max_tick_error'],2)
        self.assertEqual(r['mean_tick_error'],Fraction(4,3))
        self.assertEqual(r['collapsed_notes_if_rounded'],1)
        self.assertEqual(r['min_exact_steps_per_quarter'],480)
        self.assertEqual(m.notes[0].start,1)

    def test_invalid_maps_and_notes(self):
        m=TickMelody((TickNote(0,120,60),),480,(4,4))
        for changes in (dict(tempo_map=((1,500000),)),dict(tempo_map=((0,500000),(0,600000))),
                        dict(volume_map=((0,128),)),dict(notes=(TickNote(0,0,60),)),dict(ppq=-1)):
            with self.assertRaises(ValueError):validate(replace(m,**changes))


@unittest.skipUnless(importlib.util.find_spec('mido'),'optional mido unavailable')
class TickFileTests(unittest.TestCase):
    def setUp(self):
        import mido
        self.mido=mido
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'input.mid'

    def fixture(self,extras=(),meta_extras=()):
        m=self.mido
        midi=m.MidiFile(ticks_per_beat=480)
        midi.tracks.append(m.MidiTrack([m.MetaMessage('time_signature',numerator=6,denominator=8),
                                       m.MetaMessage('set_tempo',tempo=500000),*meta_extras]))
        midi.tracks.append(m.MidiTrack([m.Message('program_change',program=3),*extras,
                                       m.Message('note_on',note=60,velocity=81,time=1),
                                       m.Message('note_off',note=60,velocity=23,time=121),
                                       m.MetaMessage('end_of_track',time=17)]))
        midi.save(self.path)

    def test_roundtrip_all_modeled_fields(self):
        original=TickMelody((TickNote(1,122,60,81,23),TickNote(127,255,64,95,10)),
                            491,(6,8),480,((0,500000),(117,800000),(700,300000)),2,5,
                            False,((0,70),(18,100),(491,0)),900)
        write_midi(original,self.path)
        self.assertEqual(read_midi(self.path,1),original)
        with self.assertRaises(FileExistsError):write_midi(original,self.path)

    def test_implicit_initial_tempo_roundtrip(self):
        original=TickMelody((TickNote(0,120,60),),480,(4,4),tempo_map=((0,500000),(240,1000000)),tempo_defaulted=True)
        write_midi(original,self.path)
        self.assertEqual(read_midi(self.path,1),original)

    def test_change_preserved_conflict_rejected(self):
        m=self.mido
        self.fixture(meta_extras=[m.MetaMessage('set_tempo',tempo=700000,time=7)])
        got=read_midi(self.path,1)
        self.assertEqual(got.tempo_map,((0,500000),(7,700000)))
        self.assertEqual(got.notes[0],TickNote(1,122,60,81,23))
        self.assertEqual(got.total_ticks,139)
        self.fixture(extras=[m.MetaMessage('set_tempo',tempo=600000)])
        with self.assertRaisesRegex(ValueError,'conflicting same-tick'):read_midi(self.path,1)

    def test_volume_preserved_other_controls_conflicts_reject(self):
        m=self.mido
        self.fixture(extras=[m.Message('control_change',control=7,value=40)])
        self.assertEqual(read_midi(self.path,1).volume_map,((0,40),))
        for extras in ([m.Message('control_change',control=64,value=0)],
                       [m.Message('pitchwheel',pitch=0)],
                       [m.Message('control_change',control=7,value=40),m.Message('control_change',control=7,value=41)]):
            self.fixture(extras=extras)
            with self.assertRaises(ValueError):read_midi(self.path,1)

    def test_noninitial_program_roundtrip(self):
        original=TickMelody((TickNote(120,360,60),),480,(4,4),
                            program_map=((0,0),(120,71),(240,22)),program_defaulted=True)
        write_midi(original,self.path)
        self.assertEqual(read_midi(self.path,1),original)
        self.assertEqual(to_tokens(original),[0,2,1,0])

    def test_program_volume_same_tick_source_order_preserved(self):
        m=self.mido
        for kind in ('program_change','control_change'):
            for after in (False,True):
                control=m.Message(kind,**({'program':71} if kind=='program_change' else {'control':7,'value':50}))
                onset=m.Message('note_on',note=62,velocity=70)
                pair=[onset,control] if after else [control,onset]
                pair[0].time=1
                self.fixture(extras=pair+[m.Message('note_off',note=62,time=1)])
                original=read_midi(self.path,1)
                output=Path(self.tmp.name)/f'{kind}-{after}.mid'
                write_midi(original,output)
                self.assertEqual(read_midi(output,1),original)
                exported=m.MidiFile(output).tracks[1]
                relevant=[e.type for e in exported if not e.is_meta][1:3]
                self.assertEqual(relevant,[e.type for e in pair])

    def test_stale_channel_stream_rejected(self):
        original=TickMelody((TickNote(0,120,60),),480,(4,4))
        for changes in (dict(notes=(TickNote(0,121,60),)),dict(volume_map=((0,70),)),
                        dict(program=1,program_map=((0,1),))):
            with self.assertRaises(ValueError):validate(replace(original,**changes))
        # Explicitly request canonical reconstruction when intentionally changing fields.
        validate(replace(original,notes=(TickNote(0,121,60),),channel_events=None))

    def test_program_conflict_wrong_channel_rejected(self):
        m=self.mido
        for extras in ([m.Message('program_change',program=71)],
                       [m.Message('program_change',channel=1,program=71,time=1)]):
            self.fixture(extras=extras)
            with self.assertRaises(ValueError):read_midi(self.path,1)

    def test_corrupt_overlap_meter_sysex(self):
        m=self.mido
        for extras in ([m.Message('note_on',note=61,velocity=70)],
                       [m.Message('note_off',note=61)], [m.Message('sysex',data=(1,))]):
            self.fixture(extras=extras)
            with self.assertRaises(ValueError):read_midi(self.path,1)
        self.fixture(meta_extras=[m.MetaMessage('time_signature',numerator=4,denominator=4,time=2)])
        with self.assertRaises(ValueError):read_midi(self.path,1)
        self.path.write_bytes(b'corrupt')
        with self.assertRaises((ValueError,EOFError,OSError)):read_midi(self.path,1)


if __name__=='__main__':unittest.main()

import importlib.util
from pathlib import Path
import tempfile
import unittest
from mousa.meter_midi import MeterNote, MeterMelody, read_midi, write_midi, to_tokens, from_tokens, validate


class MeterTokenTests(unittest.TestCase):
    def test_explicit_68_bar_size(self):
        m=from_tokens([2,1]+[0]*94,meter=(6,8))
        self.assertEqual(m.steps_per_bar,12);self.assertEqual(m.bars,8)
        self.assertEqual(to_tokens(m),[2,1]+[0]*94)
    def test_pitch_is_not_automatically_shifted(self):
        m=MeterMelody((MeterNote(0,2,59),),12,(6,8))
        with self.assertRaises(ValueError):to_tokens(m)
        self.assertEqual(to_tokens(m,transpose_semitones=1)[0],2)
        self.assertEqual(m.notes[0].pitch,59)
    def test_hold_needs_note(self):
        with self.assertRaises(ValueError):from_tokens([0,1],meter=(4,4))
    def test_meter_and_bounds(self):
        for meter in ((3,4),(True,4),(6,4)):
            with self.assertRaises(ValueError):from_tokens([2],meter=meter)
        with self.assertRaises(ValueError):from_tokens([2]+[0]*3072,meter=(6,8))
    def test_polyphony_unsorted_zero_duration(self):
        for notes in ((MeterNote(0,2,60),MeterNote(1,3,62)),(MeterNote(1,1,60),)):
            with self.assertRaises(ValueError):validate(MeterMelody(notes,12,(6,8)))


@unittest.skipUnless(importlib.util.find_spec('mido'),'optional mido research dependency')
class MeterMidiTests(unittest.TestCase):
    def setUp(self):
        import mido
        self.mido=mido;self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
    def fixture(self,notes=((0,2,60),),meter=(6,8),end=96,extra=(),ppq=480,metas=()):
        m=self.mido.MidiFile(type=1,ticks_per_beat=ppq);meta=self.mido.MidiTrack();track=self.mido.MidiTrack();m.tracks.extend([meta,track])
        if meter:meta.append(self.mido.MetaMessage('time_signature',numerator=meter[0],denominator=meter[1],time=0))
        meta.extend(metas);meta.append(self.mido.MetaMessage('end_of_track',time=0))
        events=[]
        for s,e,p in notes:events.extend([(s*ppq//4,1,self.mido.Message('note_on',note=p,velocity=70)),(e*ppq//4,0,self.mido.Message('note_off',note=p,velocity=11))])
        events.extend(extra);previous=0
        for tick,order,event in sorted(events,key=lambda v:v[:2]):track.append(event.copy(time=tick-previous));previous=tick
        track.append(self.mido.MetaMessage('end_of_track',time=end*ppq//4-previous))
        path=self.root/f'fixture-{len(list(self.root.iterdir()))}.mid';m.save(path);return path
    def test_68_trailing_silence_and_pitch_roundtrip(self):
        a=read_midi(self.fixture(notes=((0,2,65),(3,6,64))),1)
        self.assertEqual(a.total_steps,96);self.assertEqual(a.meter,(6,8));self.assertEqual(a.notes[0].pitch,65)
        p=self.root/'out.mid';write_midi(a,p);b=read_midi(p,1)
        self.assertEqual(a.notes,b.notes);self.assertEqual(a.total_steps,b.total_steps);self.assertEqual(a.tempo,b.tempo)
    def test_44_and_same_note_rearticulation(self):
        a=read_midi(self.fixture(notes=((0,2,60),(2,3,60)),meter=(4,4),end=128),1)
        self.assertEqual(a.bars,8);self.assertEqual(len(a.notes),2)
    def test_meter_missing_or_change(self):
        for path in (self.fixture(meter=None),self.fixture(metas=(self.mido.MetaMessage('time_signature',numerator=4,denominator=4,time=480),))):
            with self.assertRaises(ValueError):read_midi(path,1)
    def test_late_meter_without_initial_rejected(self):
        with self.assertRaises(ValueError):read_midi(self.fixture(meter=None,metas=(self.mido.MetaMessage('time_signature',numerator=6,denominator=8,time=480),)),1)
    def test_tempo_change_rejected(self):
        metas=(self.mido.MetaMessage('set_tempo',tempo=500000,time=0),self.mido.MetaMessage('set_tempo',tempo=600000,time=480))
        with self.assertRaises(ValueError):read_midi(self.fixture(metas=metas),1)
    def test_offgrid_onset_and_eot_rejected(self):
        p=self.fixture();m=self.mido.MidiFile(p);m.tracks[1][0].time=1;m.save(p)
        with self.assertRaises(ValueError):read_midi(p,1)
        p=self.fixture();m=self.mido.MidiFile(p);m.tracks[1][-1].time+=1;m.save(p)
        with self.assertRaises(ValueError):read_midi(p,1)
    def test_polyphony_and_unmatched_off(self):
        p=self.fixture(notes=((0,4,60),(2,6,62)))
        with self.assertRaises(ValueError):read_midi(p,1)
        p=self.fixture(extra=((0,-1,self.mido.Message('note_off',note=62)),))
        with self.assertRaises(ValueError):read_midi(p,1)
    def test_control_bend_pressure_and_sysex_rejected(self):
        messages=(self.mido.Message('control_change',control=64,value=127),self.mido.Message('pitchwheel',pitch=0),self.mido.Message('aftertouch',value=0),self.mido.Message('sysex',data=(1,)))
        for msg in messages:
            with self.subTest(msg=msg),self.assertRaises(ValueError):read_midi(self.fixture(extra=((0,-1,msg),)),1)
    def test_track_index_and_percussion(self):
        p=self.fixture()
        for i in (True,-1,2):
            with self.assertRaises(ValueError):read_midi(p,i)
        m=self.mido.MidiFile(p)
        for e in m.tracks[1]:
            if not e.is_meta:e.channel=9
        m.save(p)
        with self.assertRaises(ValueError):read_midi(p,1)
    def test_symlink_and_overwrite(self):
        p=self.fixture();link=self.root/'link.mid';link.symlink_to(p)
        with self.assertRaises(ValueError):read_midi(link,1)
        with self.assertRaises(FileExistsError):write_midi(read_midi(p,1),p)
    def test_writer_refuses_inexact_ppq(self):
        m=MeterMelody((MeterNote(0,1,60),),12,(6,8),ppq=1)
        with self.assertRaises(ValueError):write_midi(m,self.root/'bad.mid')
    def test_preserves_partial_bar_without_padding(self):
        m=read_midi(self.fixture(end=14),1)
        self.assertEqual(m.total_steps,14);self.assertEqual(m.bars.numerator,7);self.assertEqual(m.bars.denominator,6)
    def test_shared_channel_other_track_rejected(self):
        p=self.fixture();m=self.mido.MidiFile(p)
        m.tracks[0].insert(0,self.mido.Message('control_change',channel=0,control=64,value=127,time=0));m.save(p)
        with self.assertRaises(ValueError):read_midi(p,1)

    def test_empty_melody_requires_explicit_admission(self):
        melody=from_tokens([0]*96,meter=(6,8),channel=2,program=73)
        path=self.root/'empty.mid';write_midi(melody,path)
        with self.assertRaises(ValueError):read_midi(path,1)
        restored=read_midi(path,1,allow_empty=True)
        self.assertEqual(restored,melody)
    def test_explicit_ppq_no_tick_rounding(self):
        m=read_midi(self.fixture(ppq=384),1)
        self.assertEqual(m.ppq,384)
        path=self.root/'ppq.mid';write_midi(m,path)
        self.assertEqual(read_midi(path,1).notes,m.notes)
    def test_unterminated_note(self):
        path=self.fixture();m=self.mido.MidiFile(path)
        m.tracks[1]=self.mido.MidiTrack(e for e in m.tracks[1] if e.type!='note_off');m.save(path)
        with self.assertRaises(ValueError):read_midi(path,1)

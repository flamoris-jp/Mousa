import importlib.util
import io
from pathlib import Path
import sys
import unittest
from zipfile import ZipFile,ZipInfo
TOOLS=Path(__file__).resolve().parents[1]/'tools';sys.path.insert(0,str(TOOLS))
try:
    import inventory_groove_midi as m
finally:sys.path.pop(0)

class GrooveInventoryTests(unittest.TestCase):
    def test_path_security(self):
        self.assertEqual(str(m.safe_name('groove/drummer1/a.mid')),'groove/drummer1/a.mid')
        for name in ('/groove/a.mid','groove/../a.mid','groove/./a.mid','groove\\a.mid','groove/a:mid','groove/a\x00.mid'):
            with self.subTest(name=name),self.assertRaises(ValueError):m.safe_name(name)

    def test_symlink_and_unexpected_media_rejected(self):
        for special in ('symlink','audio'):
            buffer=io.BytesIO()
            with ZipFile(buffer,'w') as z:
                info=ZipInfo('groove/a.mid' if special=='symlink' else 'groove/a.wav')
                if special=='symlink':info.external_attr=0o120777<<16
                z.writestr(info,b'x')
            with ZipFile(io.BytesIO(buffer.getvalue())) as z,self.assertRaises(ValueError):m.inspect_archive(z)

    def test_csv_exact_match(self):
        data=b'drummer,session,id,style,bpm,beat_type,time_signature,midi_filename,audio_filename,duration,split\ndrummer1,drummer1/session1,id1,funk,120,beat,4-4,drummer1/session1/a.mid,a.wav,1,train\n'
        self.assertEqual(len(m.csv_rows(data,['groove/drummer1/session1/a.mid'])),1)
        with self.assertRaises(ValueError):m.csv_rows(data,[])
        with self.assertRaises(ValueError):m.csv_rows(data+data.splitlines(keepends=True)[1],['groove/drummer1/session1/a.mid'])

    @unittest.skipUnless(importlib.util.find_spec('mido'),'optional mido unavailable')
    def test_drum_event_metrics_no_pitch_training(self):
        import mido
        midi=mido.MidiFile();track=mido.MidiTrack();midi.tracks.append(track)
        track.extend([mido.Message('note_on',channel=9,note=36,velocity=100,time=0),
                      mido.Message('note_on',channel=9,note=36,velocity=0,time=120),
                      mido.MetaMessage('end_of_track',time=10)])
        buf=io.BytesIO();midi.save(file=buf);r=m.note_metrics(buf.getvalue())
        self.assertEqual(r['note_on_positive'],1);self.assertEqual(r['note_off_equivalent'],1)
        self.assertEqual(r['note_channel_counts'],{9:1});self.assertEqual(r['end_tick'],130)

if __name__=='__main__':unittest.main()

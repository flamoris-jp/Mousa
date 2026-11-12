import unittest,sys,tempfile
import importlib.util
from pathlib import Path
old=list(sys.path)
try:
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
    from export_group_audition import melody_from_rows,analytic_pcm,verify_midi,write_midi
finally:sys.path[:]=old


def n(s,e,p,v=90,rv=64):return dict(start=s,end=e,pitch=p,velocity=v,release_velocity=rv)


class AuditionTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec('mido'), 'optional mido unavailable')
    def test_fivefield_order_roundtrip(self):
        rows=[n(0,192,67),n(0,96,60,127,0),n(192,384,67,30,42)]
        m=melody_from_rows(rows)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'synthetic.mid';write_midi(m,path);p=verify_midi(path,m)
        self.assertEqual(sorted((x.start,x.end,x.pitch,x.velocity,x.release_velocity) for x in p.notes),sorted(tuple(x[k] for k in ('start','end','pitch','velocity','release_velocity')) for x in rows))
    def test_velocity_release_and_repeat(self):
        a,am=analytic_pcm(melody_from_rows([n(0,384,60,127,0)]).notes)
        b,bm=analytic_pcm(melody_from_rows([n(0,384,60,64,0)]).notes)
        c,cm=analytic_pcm(melody_from_rows([n(0,384,60,127,127)]).notes)
        self.assertNotEqual(a,b);self.assertNotEqual(a,c);self.assertGreater(am['rms_linear'],bm['rms_linear'])
        self.assertEqual((a,am),analytic_pcm(melody_from_rows([n(0,384,60,127,0)]).notes))
        self.assertEqual(am['clipped_samples'],0);self.assertEqual(am['duration_seconds'],12)
    def test_reject_loss_or_overlap(self):
        for rows in [[dict(start=0,end=1,pitch=60)],[n(0,100,60),n(50,150,60)],[n(0,9220,60)]]:
            with self.assertRaises(ValueError):melody_from_rows(rows)
        with self.assertRaises(ValueError):analytic_pcm(melody_from_rows([n(0,96,127)]).notes)


if __name__=='__main__':unittest.main()

import unittest
from mousa.silence_segments_cycle46 import segments
class Silence46Tests(unittest.TestCase):
    def test_old_sustained_frontier_not_last_gate(self):
        g=[dict(onset=0,template=((0,1000,80,0),)),dict(onset=100,template=((0,10,80,0),)),dict(onset=500,template=((0,10,80,0),)),dict(onset=1192,template=((0,10,80,0),))]
        n=[dict(start=x['onset'],end=x['onset']+t[1]) for x in g for t in x['template']]
        v=segments(n,g);self.assertEqual(v['segments'],[[0,1,2],[3]])
        self.assertEqual(v['boundaries'][0]['silence_ticks'],192)
    def test_exact_gap_threshold_and_simultaneous_members(self):
        for gap,count in [(0,1),(191,1),(192,2),(193,2)]:
            g=[dict(onset=100,template=((0,300,80,0),(7,100,80,0))),dict(onset=400+gap,template=((0,10,80,0),))]
            n=[dict(start=x['onset'],end=x['onset']+t[1]) for x in g for t in x['template']]
            self.assertEqual(len(segments(n,g)['segments']),count)

    def test_empty_leading_and_threshold(self):
        self.assertEqual(segments([],[])['segments'],[])
        g=[dict(onset=5000,template=((0,10,80,0),)),dict(onset=5201,template=((0,10,80,0),))]
        n=[dict(start=x['onset'],end=x['onset']+10) for x in g]
        self.assertEqual(segments(n,g)['segments'],[[0,1]])
        with self.assertRaises(ValueError):segments([],g)
if __name__=='__main__':unittest.main()

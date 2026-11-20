import unittest
from copy import deepcopy
from mousa.anchor_return_cycle42 import compare_anchors
from mousa.group_timeline_metrics import timeline_metrics
REFS=[[1]]*21
def fixture(spec):
    ns=[];gs=[];prev=0
    for onset,anchor,t in list(spec)+[(9120,40,((0,96,80,0),))]:
        gs.append(dict(onset=onset,delta=onset-prev,count=len(t),anchor=anchor,template=t));prev=onset
        for off,gate,v,rv in t:ns.append(dict(start=onset,end=onset+gate,pitch=anchor+off,velocity=v,release_velocity=rv))
    return ns,gs
T=((0,96,80,4),)
class Anchor42Tests(unittest.TestCase):
    def test_cycle_and_all_fields_with_sustain(self):
        n,g=fixture([(100,60,((0,2400,70,5),)),(1000,62,T),(4700,65,T),(5000,66,T),(6800,67,((0,400,43,8),))])
        original=deepcopy((n,g));v=compare_anchors(n,g,REFS)
        self.assertEqual(v['intervention']['status'],'complete')
        out=v['intervention'];self.assertEqual(out['edit']['mapped_C_anchors'],[62,64,62])
        self.assertEqual((n,g),original)
        for x,y in zip(n,out['notes']):
            self.assertEqual({k:v for k,v in x.items() if k!='pitch'},{k:v for k,v in y.items() if k!='pitch'})
        self.assertEqual(timeline_metrics(n,9216),timeline_metrics(out['notes'],9216))
        self.assertEqual(v,compare_anchors(n,g,REFS))
    def test_incoming_and_outgoing_sustained_collision(self):
        for spec in (
          [(0,60,T),(4500,62,((0,400,80,0),)),(4700,65,T)],
          [(0,60,T),(6800,65,((0,400,80,0),)),(7000,62,T)]):
            n,g=fixture(spec);self.assertEqual(compare_anchors(n,g,REFS)['intervention']['status'],'safety_blocked')
        n,g=fixture([(0,60,T),(4500,62,((0,200,80,0),)),(4700,65,T)])
        self.assertEqual(compare_anchors(n,g,REFS)['intervention']['status'],'complete')
    def test_empty_noop_and_range(self):
        for spec,status in [([(3000,60,T),(5000,65,T)],'empty_A_blocked'), ([(0,60,T)],'empty_C_blocked'), ([(0,60,T),(5000,62,T)],'no_effect'), ([(0,127,T),(5000,65,T)],'pitch_range_blocked')]:
            n,g=fixture(spec);self.assertEqual(compare_anchors(n,g,REFS)['intervention']['status'],status)
    def test_join_copy_guard_and_group_offsets(self):
        n,g=fixture([(0,60,T),(1000,64,T),(3000,61,T),(3200,63,T),(3400,66,T),(3600,70,T),(4700,80,T),(4900,82,T),(5100,84,T),(5300,86,T)])
        ref=[61,63,66,70,62,66,62,66]
        v=compare_anchors(n,g,[ref]+REFS[:20])
        self.assertEqual(v['control']['status'],'complete')
        self.assertEqual(v['intervention']['status'],'copy_guard_blocked')
        n,g=fixture([(0,60,T),(5000,80,((0,96,50,4),(7,192,60,8)))])
        out=compare_anchors(n,g,REFS)['intervention']
        self.assertEqual(out['status'],'complete')
        self.assertEqual(out['groups'][1]['template'],g[1]['template'])
        with self.assertRaises(ValueError):compare_anchors(n,g,REFS[:20])
if __name__=='__main__':unittest.main()

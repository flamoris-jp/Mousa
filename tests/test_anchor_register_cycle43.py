import unittest
from copy import deepcopy
from mousa.anchor_register_cycle43 import nearest_anchor,compare_octaves
from mousa.group_timeline_metrics import timeline_metrics
REFS=[[1]]*21
T=((0,96,80,4),)
def fixture(spec):
    ns=[];gs=[];prev=0
    for onset,anchor,t in list(spec)+[(9120,40,T)]:
        gs.append(dict(onset=onset,delta=onset-prev,count=len(t),anchor=anchor,template=t));prev=onset
        ns.extend(dict(start=onset,end=onset+gate,pitch=anchor+off,velocity=v,release_velocity=rv) for off,gate,v,rv in t)
    return ns,gs
class Register43Tests(unittest.TestCase):
    def test_exhaustive_choice_and_tie(self):
        for base in (2,60,129):
            for offset in (0,7,120,127):
                for prev in range(128):
                    valid=[x for x in range(128-offset) if (x-base)%12==0]
                    expected=min(valid,key=lambda x:(abs(x-prev),x)) if valid else None
                    self.assertEqual(nearest_anchor(base,offset,prev),expected)
        self.assertEqual(nearest_anchor(60,0,66),60)
    def test_original_A_sequential_C_and_time_fields(self):
        n,g=fixture([(0,84,T),(1000,50,T),(3000,60,T),(4700,90,T),(5000,92,T)])
        old=deepcopy((n,g));v=compare_octaves(n,g,REFS)['intervention']
        self.assertEqual(v['status'],'complete')
        self.assertEqual(v['edit']['mapped_C_anchors'],[62,64])
        self.assertEqual((n,g),old)
        self.assertEqual(timeline_metrics(n,9216),timeline_metrics(v['notes'],9216))
        for a,b in zip(n,v['notes']):
            self.assertEqual({k:v for k,v in a.items() if k!='pitch'},{k:v for k,v in b.items() if k!='pitch'})
        self.assertEqual(v,compare_octaves(n,g,REFS)['intervention'])
    def test_collision_no_next_best_retry(self):
        n,g=fixture([(0,60,T),(4500,62,((0,500,80,0),)),(4700,80,T)])
        v=compare_octaves(n,g,REFS)['intervention']
        self.assertEqual(v['status'],'safety_blocked') # 50 or74 could avoid; no retry.
    def test_empty_noop_and_no_legal_register(self):
        n,g=fixture([(3000,60,T),(5000,80,T)])
        self.assertEqual(compare_octaves(n,g,REFS)['intervention']['status'],'empty_A_blocked')
        n,g=fixture([(0,60,T),(3000,62,T),(5000,62,T)])
        self.assertEqual(compare_octaves(n,g,REFS)['intervention']['status'],'no_effect')
        n,g=fixture([(0,60,T),(5000,0,((0,96,80,0),(127,96,80,0)))])
        self.assertEqual(compare_octaves(n,g,REFS)['intervention']['status'],'no_legal_register')
if __name__=='__main__':unittest.main()

import unittest
from copy import deepcopy
from mousa.phrase_groups_cycle41 import compare_return,validate_notes,validate_groups,phrases

def fixture(spec):
    spec=list(spec)+[(9120,40,((0,96,80,0),))]
    ns=[];gs=[];prev=0
    for onset,anchor,t in spec:
        gs.append(dict(onset=onset,delta=onset-prev,count=len(t),anchor=anchor,template=t));prev=onset
        ns.extend(dict(start=onset,end=onset+gate,pitch=anchor+off,velocity=vel,release_velocity=rv) for off,gate,vel,rv in t)
    return ns,gs

T=((0,96,80,7),)

class Phrase41Tests(unittest.TestCase):
    def test_preserves_all_fields_order_and_rest_endpoints(self):
        ns,gs=fixture([(100,60,((0,300,80,7),(7,96,41,3))),(1000,62,T),(2400,67,T),(5000,71,T),(7000,65,T)])
        original=deepcopy((ns,gs));v=compare_return(ns,gs,[[1,4]])
        self.assertEqual((ns,gs),original);self.assertEqual(v['control']['notes'],ns)
        out=v['intervention'];self.assertEqual(out['status'],'complete')
        copied=[n for n in out['notes'] if 4608<=n['start']<6912]
        self.assertEqual(copied,[{**n,'start':n['start']+4608,'end':n['end']+4608,'pitch':n['pitch']+2} for n in ns if n['start']<2304])
        self.assertEqual(out['target_ticks'],9216)
        self.assertEqual(compare_return(ns,gs,[[1,4]]),v)

    def test_crossings_rejected_not_shortened_and_half_open_legal(self):
        for b in (2304,4608,6912):
            ns,gs=fixture([(0,50,T),(b-5,60,((0,10,80,0),))])
            v=compare_return(ns,gs,[[1]])
            self.assertEqual(v['intervention']['status'],'boundary_sustain_blocked')
            self.assertEqual(v['control']['notes'],ns)
        ns,gs=fixture([(0,50,((0,2304,80,0),)),(2304,50,T),(4608,51,T),(6912,50,T)])
        self.assertEqual(compare_return(ns,gs,[[1]])['intervention']['status'],'complete')

    def test_join_copy_is_screened(self):
        ns,gs=fixture([(0,60,T),(500,62,T),(1000,65,T),(1500,69,T),(2500,61,T),(3000,64,T),(3500,68,T),(4000,73,T),(5000,40,T)])
        # A' first four notes join preceding B's four notes.
        reference=[61,64,68,73,62,64,67,71]
        v=compare_return(ns,gs,[reference])
        self.assertEqual(v['control']['status'],'complete')
        self.assertEqual(v['intervention']['status'],'copy_guard_blocked')

    def test_empty_A_and_note_budget(self):
        ns,gs=fixture([(2400,60,T)])
        self.assertEqual(compare_return(ns,gs,[[1]])['intervention']['status'],'empty_A_blocked')
        # 130 A notes plus126 B/D; replacing empty C must exceed256.
        spec=[(i*10,60,((0,5,80,0),)) for i in range(130)]
        spec += [(2400+i*10,61,((0,5,80,0),)) for i in range(125)]
        ns,gs=fixture(spec)
        v=compare_return(ns,gs,[[1]])
        self.assertEqual(len(ns),256)
        self.assertEqual(v['intervention']['status'],'safety_blocked')

    def test_pitch_safety_and_bounds(self):
        ns,gs=fixture([(0,127,T)])
        self.assertEqual(compare_return(ns,gs,[[1]])['intervention']['status'],'pitch_range_blocked')
        for spec in ([(0,60,((0,100,80,0),(0,20,80,0)))],[(0,60,((0,100,80,0),(1,100,80,0),(2,100,80,0),(3,100,80,0)))]):
            n,g=fixture(spec)
            with self.assertRaises(ValueError):compare_return(n,g,[[1]])
        with self.assertRaises(ValueError):validate_notes([])
        ns,gs=fixture([(0,60,T)]);gs[0]['delta']=1
        with self.assertRaises(ValueError):validate_groups(ns,gs)
        self.assertEqual(phrases([1,2,3,4,5,6,7]),set())
        self.assertEqual(phrases([1,2,3,4,5,6,7,8]),{(1,)*7})

if __name__=='__main__':unittest.main()

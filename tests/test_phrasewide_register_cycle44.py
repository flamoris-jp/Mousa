import unittest,random,itertools
from copy import deepcopy
from mousa.phrasewide_register_cycle44 import optimal_anchors,compare_phrasewide
from mousa.group_timeline_metrics import timeline_metrics
T=((0,96,80,4),);REFS=[[1]]*21
def fixture(spec):
    ns=[];gs=[];prev=0
    for onset,anchor,t in list(spec)+[(9120,40,T)]:
        gs.append(dict(onset=onset,delta=onset-prev,count=len(t),anchor=anchor,template=t));prev=onset
        ns.extend(dict(start=onset,end=onset+gate,pitch=anchor+off,velocity=v,release_velocity=rv) for off,gate,v,rv in t)
    return ns,gs
class Phrasewide44Tests(unittest.TestCase):
    def test_exhaustive_oracle(self):
        rng=random.Random(44017)
        for _ in range(100):
            size=rng.randrange(1,4);bases=[rng.randrange(130) for _ in range(size)];offsets=[rng.randrange(128) for _ in bases]
            left=rng.choice([None,rng.randrange(128)]);right=rng.choice([None,rng.randrange(128)])
            cs=[[v for v in range(128-o) if (v-b)%12==0] for b,o in zip(bases,offsets)]
            allpaths=list(itertools.product(*cs))
            def cost(p):return (abs(p[0]-left) if left is not None else 0)+sum(abs(a-b) for a,b in zip(p,p[1:]))+(abs(p[-1]-right) if right is not None else 0)
            expected=min(((cost(p),p) for p in allpaths),default=None)
            got=optimal_anchors(bases,offsets,left,right)
            self.assertEqual(got,None if expected is None else dict(objective=expected[0],anchors=list(expected[1])))
    def test_tie_exit_and_bounds(self):
        self.assertEqual(optimal_anchors([60],[0],66,66),dict(anchors=[60],objective=12))
        self.assertEqual(optimal_anchors([60,62],[0,0],60,86)['anchors'],[60,62]) # lex tie
        for args in [([],[],0,0),([0],[128],0,0),([0],[0],True,0),([0]*257,[0]*257,0,0)]:
            with self.assertRaises(ValueError):optimal_anchors(*args)
        self.assertIsNone(optimal_anchors([62],[127],0,0))
    def test_all_temporal_fields_original_reference(self):
        ns,gs=fixture([(0,84,((0,2400,80,4),)),(1000,50,T),(3000,60,T),(4700,90,T),(5000,92,T),(6800,94,((0,500,80,4),)),(7500,64,T)])
        before=deepcopy((ns,gs));v=compare_phrasewide(ns,gs,REFS)['intervention']
        self.assertEqual(v['status'],'complete');self.assertEqual((ns,gs),before)
        self.assertEqual(timeline_metrics(ns,9216),timeline_metrics(v['notes'],9216))
        self.assertTrue(all({k:v for k,v in a.items() if k!='pitch'}=={k:v for k,v in b.items() if k!='pitch'} for a,b in zip(ns,v['notes'])))
        self.assertTrue(all((g['anchor']-[86,52][j%2])%12==0 for j,g in enumerate([x for x in v['groups'] if 4608<=x['onset']<6912])))
    def test_collision_not_reoptimized(self):
        ns,gs=fixture([(0,60,T),(4500,62,((0,500,80,0),)),(4700,80,T),(7000,62,T)])
        self.assertEqual(compare_phrasewide(ns,gs,REFS)['intervention']['status'],'safety_blocked')
        ns,gs=fixture([(3000,60,T),(5000,80,T)])
        self.assertEqual(compare_phrasewide(ns,gs,REFS)['intervention']['status'],'empty_A_blocked')
if __name__=='__main__':unittest.main()

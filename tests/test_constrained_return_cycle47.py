import unittest,itertools,random
from mousa.constrained_return_cycle47 import constrained_path,compare_policy
from mousa.silence_return_cycle46 import compare_segments
T=((0,96,80,0),)
def fixture(spec):
    ns=[];gs=[];prev=0
    for onset,anchor,t in spec+[(9120,40,T)]:
        gs.append(dict(onset=onset,delta=onset-prev,count=len(t),anchor=anchor,template=t));prev=onset
        ns.extend(dict(start=onset,end=onset+gate,pitch=anchor+off,velocity=v,release_velocity=rv) for off,gate,v,rv in t)
    return ns,gs
class Constrained47Tests(unittest.TestCase):
    def test_exhaustive_oracle_nonadjacent_active(self):
        rng=random.Random(47017)
        for _ in range(60):
            ns,gs=fixture([(0,60,T),(500,70,((0,450,80,0),)),(600,75,T),(700,80,T),(1100,65,T)])
            ix=[1,2,3];bases=[rng.randrange(50,80) for _ in ix]
            legal=[[a for a in range(128) if (a-b)%12==0] for b in bases]
            possibilities=[]
            for path in itertools.product(*legal):
                # first target persists across all three; second ends before third.
                if path[0]==path[1] or path[0]==path[2]:continue
                cost=abs(60-path[0])+sum(abs(a-b) for a,b in zip(path,path[1:]))+abs(path[-1]-65)
                possibilities.append((cost,path))
            expected=min(possibilities);got=constrained_path(gs,ix,bases,ns)
            self.assertEqual((got['objective'],tuple(got['anchors'])),expected)
    def test_bound_and_future_fixed_collision(self):
        ns,gs=fixture([(0,60,T),(500,70,((0,900,80,0),)),(1000,62,T)])
        got=constrained_path(gs,[1],[62],ns)
        self.assertNotEqual(got['anchors'],[62])
        self.assertEqual(constrained_path(gs,[1],[62],ns,cpu_deadline=0)['status'],'cpu_budget_blocked')
        self.assertEqual(constrained_path(gs,[1],[62],ns,transition_cap=1)['status'],'dp_budget_blocked')
    def test_singleton_is_not_phrase_success(self):
        ns,gs=fixture([(0,60,T),(500,65,T),(600,67,T),(1000,80,T),(1100,82,T)])
        refs=[[1]]*22
        self.assertEqual(compare_policy(ns,gs,refs)['status'],'source_segment_too_short')
        self.assertEqual(compare_policy(ns,gs,refs,allow_singleton=True)['status'],'singleton_fallback_complete')
    def test_old_policy_status_and_fields(self):
        ns,gs=fixture([(0,60,T),(100,62,T),(500,65,T),(600,67,T),(1000,80,T),(1100,82,T)])
        refs=[[1]]*22;old=compare_segments(ns,gs,refs)['intervention'];new=compare_policy(ns,gs,refs)
        self.assertEqual(old['status'],'complete');self.assertEqual(new['status'],'complete')
        self.assertEqual(old['notes'],new['notes']);self.assertEqual(old['groups'],new['groups'])
if __name__=='__main__':unittest.main()

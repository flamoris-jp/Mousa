import unittest
from copy import deepcopy
from mousa.silence_return_cycle46 import compare_segments
from mousa.group_timeline_metrics import timeline_metrics
T=((0,96,80,4),);REFS=[[1]]*22
def make(spec):
    ns=[];gs=[];previous=0
    for onset,anchor in spec+[(9120,40)]:
        gs.append(dict(onset=onset,delta=onset-previous,count=1,anchor=anchor,template=T));previous=onset
        ns.append(dict(start=onset,end=onset+96,pitch=anchor,velocity=80,release_velocity=4))
    return ns,gs
class SilenceReturn46Tests(unittest.TestCase):
    def test_fixed_first_third_all_temporal_invariants(self):
        n,g=make([(0,60),(100,62),(500,65),(600,67),(1000,80),(1100,82),(1500,64)])
        old=deepcopy((n,g));out=compare_segments(n,g,REFS)['intervention']
        self.assertEqual(out['status'],'complete');self.assertEqual((n,g),old)
        self.assertEqual(timeline_metrics(n,9216),timeline_metrics(out['notes'],9216))
        self.assertEqual(out['edit']['target_segment_ordinal'],3)
        self.assertEqual(out['groups'][2:4],g[2:4])
        for a,b in zip(n,out['notes']):
            self.assertEqual({k:v for k,v in a.items() if k!='pitch'},{k:v for k,v in b.items() if k!='pitch'})
    def test_short_first_no_search(self):
        n,g=make([(0,60),(500,62),(600,64),(1000,70),(1100,72)])
        self.assertEqual(compare_segments(n,g,REFS)['intervention']['status'],'source_segment_too_short')
    def test_short_third_no_fourth_substitution(self):
        n,g=make([(0,60),(100,62),(500,65),(600,67),(1000,80),(1500,81),(1600,82)])
        self.assertEqual(compare_segments(n,g,REFS)['intervention']['status'],'target_segment_missing_or_short')
if __name__=='__main__':unittest.main()

import unittest
from copy import deepcopy
from mousa.group_structure_cycle45 import structure
class Structure45Tests(unittest.TestCase):
    def test_crossing_union_empty_and_single(self):
        notes=[dict(start=2200,end=4700),dict(start=2304,end=2400)]
        groups=[dict(onset=2200,anchor=60),dict(onset=2304,anchor=62)]
        old=deepcopy((notes,groups));v=structure(notes,groups);self.assertEqual((notes,groups),old)
        self.assertEqual([b['occupied_ticks'] for b in v['blocks']],[104,2304,92,0])
        self.assertEqual([b['note_onsets'] for b in v['blocks']],[1,1,0,0])
        self.assertEqual([b['sounding_notes'] for b in v['blocks']],[1,2,1,0])
        self.assertEqual(v['comparable_pairs'],0)
        self.assertTrue(all(p['equal'] is None for p in v['block_interval_pairs']))
        self.assertEqual(v['blocks'][0]['interval_status'],'missing_single_group')
        self.assertEqual(v['blocks'][2]['interval_status'],'missing_empty')
    def test_known_transposed_blocks_and_ngram_denominator(self):
        gs=[dict(onset=t,anchor=60+i) for i,t in enumerate([0,100,200,300,2400,2500,2600,2700])]
        v=structure([],gs)
        self.assertEqual(v['comparable_pairs'],1);self.assertEqual(v['equal_pairs'],1)
        self.assertEqual(v['anchor_interval_3gram'],dict(intervals=7,windows=5,unique=1,repeated_windows_after_first=4,repeat_fraction=.8))
    def test_empty_and_invalid(self):
        v=structure([],[]);self.assertEqual(v['anchor_interval_3gram']['repeat_fraction'],None)
        self.assertTrue(all(b['silence_ticks']==2304 for b in v['blocks']))
        with self.assertRaises(ValueError):structure([dict(start=10,end=10)],[])
if __name__=='__main__':unittest.main()

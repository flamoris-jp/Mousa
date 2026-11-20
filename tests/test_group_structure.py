import unittest
from mousa.tick_midi import TickNote
from mousa.group_structure import describe

class GroupStructureTests(unittest.TestCase):
    def test_sustained_earlier_group_not_false_boundary(self):
        notes=(TickNote(0,1000,48),TickNote(0,100,72),TickNote(100,200,60),TickNote(900,950,65),TickNote(1480,1500,67))
        d=describe(notes,2000,ppq=480)
        self.assertEqual(d['internal_silent_ticks'],[0,0,480])
        self.assertEqual(d['silence_boundary_profiles'][0]['segment_group_counts'],[3,1])
        self.assertEqual(d['silence_boundary_profiles'][1]['segment_group_counts'],[4])
        self.assertEqual(d['within_group_span_sum'],24)
        self.assertEqual(d['anchor_absolute_interval_sum'],19)
        self.assertEqual(d['trailing_silence_ticks'],500)

    def test_order_transposition_and_timing_scale_invariance(self):
        ns=(TickNote(10,50,60),TickNote(10,90,72),TickNote(110,120,62))
        a=describe(ns,200,ppq=20)
        self.assertEqual(a,describe(tuple(reversed(ns)),200,ppq=20))
        b=describe(tuple(TickNote(n.start*3,n.end*3,n.pitch+5) for n in ns),600,ppq=60)
        for k in ('silence_boundary_profiles','anchor_absolute_interval_sum','within_group_span_sum'):
            self.assertEqual(a[k],b[k])
        self.assertEqual(b['internal_silent_ticks'],[x*3 for x in a['internal_silent_ticks']])

    def test_empty_single_and_invalid(self):
        self.assertIsNone(describe((),100,ppq=48)['anchor_mean_absolute_interval'])
        self.assertEqual(describe((),100,ppq=48)['silence_boundary_profiles'][0]['segment_group_counts'],[])
        self.assertEqual(describe((TickNote(0,10,60),),100,ppq=48)['transitions'],0)
        for ppq,gaps in ((True,(1,)),(0,(1,)),(48,()),(48,(True,)),(48,(-1,))):
            with self.assertRaises(ValueError):describe((),100,ppq=ppq,gap_beats=gaps)

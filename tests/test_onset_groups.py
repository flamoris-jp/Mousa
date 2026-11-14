import unittest
from dataclasses import replace
from mousa.tick_midi import TickNote
from mousa.onset_groups import group_notes, restore_notes, OnsetGroup, IndexedNote


class OnsetGroupTests(unittest.TestCase):
    def test_unsorted_overlap_and_performance_fields(self):
        notes = (TickNote(20,90,64,17,8), TickNote(0,100,60,90,4), TickNote(0,30,72,70,9), TickNote(20,50,67,120,2))
        grouped = group_notes(notes, 120)
        self.assertEqual([g.onset for g in grouped], [0,20])
        self.assertEqual([len(g.members) for g in grouped], [2,2])
        restored = restore_notes(grouped,120)
        self.assertEqual(restored,notes)
        for a,b in zip(notes,restored):self.assertIs(a,b)

    def test_silence_and_no_melody_inference(self):
        self.assertEqual(restore_notes(group_notes((),100),100),())
        notes=(TickNote(10,100,60),TickNote(10,40,60))
        self.assertEqual(restore_notes(group_notes(notes,150),150),notes)
        # Ambiguous retriggers are preserved here; this is not MIDI validation.

    def test_reject_malformed_and_incomplete_views(self):
        n=TickNote(0,20,60);g=OnsetGroup(0,(IndexedNote(0,n),))
        bad=[(g,g),(OnsetGroup(0,(IndexedNote(1,n),)),), (OnsetGroup(1,g.members),), (OnsetGroup(0,()),)]
        for groups in bad:
            with self.assertRaises(ValueError):restore_notes(groups,30)
        for n in (TickNote(0,20,True),TickNote(0,20,60,0),TickNote(0,20,60,80,128),TickNote(0,31,60)):
            with self.assertRaises(ValueError):group_notes((n,),30)
        with self.assertRaises(ValueError):group_notes((TickNote(0,1,60),)*4097,30)
        with self.assertRaises(ValueError):group_notes((),True)

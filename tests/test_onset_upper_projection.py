import unittest
from mousa.tick_midi import TickNote
from mousa.onset_upper_projection import project,project_with_loss

class OnsetProjectionTests(unittest.TestCase):
    def test_highest_not_longest_and_original_gates(self):
        notes=(TickNote(0,100,60),TickNote(0,50,72),TickNote(25,120,64))
        selected,loss=project_with_loss(notes,140)
        self.assertEqual(selected,(notes[1],notes[2]))
        self.assertIs(selected[0],notes[1])
        self.assertEqual(loss['dropped_notes'],1)
        self.assertEqual(loss['dropped_summed_gate_ticks'],100)
        self.assertEqual(loss['after']['max_polyphony'],2)
        self.assertEqual(loss['lost_sounding_union_ticks'],0)

    def test_tie_and_silence_loss_explicit(self):
        notes=(TickNote(0,100,60),TickNote(0,20,72),TickNote(0,30,72))
        selected,loss=project_with_loss(notes,120)
        self.assertEqual(selected,(notes[2],))
        self.assertEqual(loss['lost_sounding_union_ticks'],70)
        self.assertEqual(loss['after']['rest_ticks'],90)

    def test_different_onsets_identity(self):
        notes=(TickNote(0,40,60),TickNote(20,70,61))
        self.assertEqual(project(notes),notes)
        self.assertEqual(project(project(notes)),project(notes))
        with self.assertRaises(ValueError):project([])
        with self.assertRaises(ValueError):project_with_loss(notes,50)

if __name__=='__main__':unittest.main()

import unittest
from mousa.event_baseline import events_from_grid, EventNGram, longest_shared_run

class EventTests(unittest.TestCase):
    def test_roundtrip_and_rearticulation(self):
        self.assertEqual(events_from_grid([0,0,2,1,2,1,0]),[(-1,2),(2,2),(2,2),(-1,1)])
    def test_invalid_hold(self):
        for tokens in ([1],[0,1],[True],[27]):
            with self.assertRaises(ValueError): events_from_grid(tokens)
    def test_no_cross_work_context(self):
        model=EventNGram([[(2,1)],[(3,1)]],2)
        self.assertEqual(len(model.tables[1]),0)
    def test_unseen_is_explicit(self):
        result=EventNGram([[(2,1)]]).evaluate([(4,1)])
        self.assertEqual(result['unseen_events'],1); self.assertEqual(result['correct_events'],0)
    def test_generate_is_bounded_reproducible(self):
        for order in range(3):
            m=EventNGram([[(-1,3),(2,2),(3,1),(2,2)]],order)
            a=m.generate(7);self.assertEqual(a,m.generate(7));self.assertEqual(len(a),128)
            events_from_grid(a)
    def test_longest_run(self):
        self.assertEqual(longest_shared_run([0,2,1,0],[2,1,0,4]),3)
    def test_settings(self):
        for order in (True,-1,3):
            with self.assertRaises(ValueError):EventNGram([[(2,1)]],order)

import unittest
from mousa.group_timeline_metrics import timeline_metrics


class TimelineTests(unittest.TestCase):
    def test_earlier_long_sustain_bridges_later_onsets(self):
        m=timeline_metrics([dict(start=0,end=100),dict(start=10,end=20),dict(start=50,end=60)],120)
        self.assertEqual(m['internal_silence_ticks'],0)
        self.assertEqual(m['silence_ticks'],20)
        self.assertEqual(m['polyphonic_ticks'],20)
        self.assertEqual(m['active_voice_tick_integral'],120)
    def test_disjoint_touch_and_empty(self):
        m=timeline_metrics([dict(start=5,end=10),dict(start=10,end=15),dict(start=20,end=25)],30)
        self.assertEqual((m['leading_silence_ticks'],m['internal_silence_ticks'],m['trailing_silence_ticks']),(5,5,5))
        self.assertEqual(m['max_contiguous_silence_ticks'],5)
        self.assertEqual(m['internal_gap_count'],1)
        e=timeline_metrics([],30);self.assertTrue(e['empty_timeline']);self.assertEqual(e['silence_ticks'],30)
    def test_invalid(self):
        with self.assertRaises(ValueError):timeline_metrics([dict(start=0,end=31)],30)
        with self.assertRaises(ValueError):timeline_metrics([dict(start=True,end=4)],30)


if __name__=='__main__':unittest.main()

"""Synthetic fixtures only: clock conditioning is not musical quality evidence."""
import math
import unittest
from unittest.mock import patch

from mousa.factorized_baseline import PITCHES, DURATIONS
from mousa.melodic_event_model import MelodicEventModel
from mousa.position_event_model import PositionEventModel


class PositionEventTests(unittest.TestCase):
    songs = [((6, 8), [(14, 6), (-1, 6), (16, 12), (18, 3)]),
             ((4, 4), [(20, 8), (22, 8), (24, 16)])]

    def test_control_identical(self):
        model = PositionEventModel(self.songs, relative=True, duration_prior='empirical')
        base = MelodicEventModel([s for _, s in self.songs], relative=True, duration_prior='empirical')
        for meter, sequence in self.songs:
            for i in range(len(sequence)):
                self.assertEqual(model.distributions(sequence[:i], meter=meter), base.distributions(sequence[:i]))
            self.assertEqual(model.evaluate(sequence, meter=meter), base.evaluate(sequence))

    def test_normalization_positive_equal_support(self):
        for relative in (False, True):
            model = PositionEventModel(self.songs, meter_position=True, phrase_position=True, relative=relative)
            for history in ([], [(26, 1)], [(2, 128)], [(-1, 12)]):
                ps, ds = model.distributions(history, meter=(6, 8))
                self.assertEqual(set(ps), set(PITCHES))
                self.assertAlmostEqual(sum(ps.values()), 1.)
                for rest in (False, True):
                    self.assertEqual(set(ds[rest]), set(DURATIONS))
                    self.assertAlmostEqual(sum(ds[rest].values()), 1.)
                    self.assertTrue(all(v > 0 for v in ds[rest].values()))
                self.assertTrue(all(v > 0 for v in ps.values()))
            result = model.evaluate([(2, 128)], meter=(4, 4))
            self.assertEqual(result['support_size'], 3328)
            self.assertTrue(math.isfinite(result['nll_per_event']))

    def test_clock_meter_and_phrase(self):
        model = PositionEventModel(self.songs, meter_position=True, phrase_position=True)
        self.assertEqual(model.position_key((6, 8), 15), ((6, 8), 3, 1))
        self.assertEqual(model.position_key((4, 4), 15), ((4, 4), 15, 0))
        self.assertEqual(model.position_key((6, 8), 48), ((6, 8), 0, 0))

    def test_song_clock_and_transition_reset(self):
        songs = [((6, 8), [(14, 3), (16, 2)]), ((6, 8), [(20, 4)])]
        model = PositionEventModel(songs, meter_position=True)
        start = model.position_key((6, 8), 0)
        self.assertEqual(model.position_counts[start], {(14, 3): 1, (20, 4): 1})
        self.assertFalse(any(previous == (16, 2) for _, previous in model.transition_counts))
        self.assertNotIn(model.position_key((6, 8), 5), model.position_counts)

    def test_position_then_control_backoff(self):
        model = PositionEventModel(self.songs, meter_position=True)
        # Seen clock, unseen previous event -> position unigram.
        counts, _ = model.context([(2, 6)], meter=(6, 8))
        self.assertEqual(counts, {(-99, 6): 1})
        # Unseen clock -> control's event-context/unigram backoff.
        self.assertEqual(model.context([(2, 5)], meter=(6, 8)), model.control.context([(2, 5)]))
        counts, _ = model.context([(14, 6)], meter=(6, 8))
        self.assertEqual(counts, {(-99, 6): 1})

    def test_meter_counts_do_not_collide(self):
        model = PositionEventModel(self.songs, meter_position=True)
        self.assertEqual(model.context([], meter=(6, 8))[0], {(14, 6): 1, (16, 12): 1, (18, 3): 1})
        self.assertEqual(model.context([], meter=(4, 4))[0], {(20, 8): 1, (24, 16): 1})

    def test_deterministic_generation_and_rest_mask(self):
        model = PositionEventModel([((6, 8), [(-1, 12)] * 20)], meter_position=True)
        for cap in (0, 3, 12, None):
            kwargs = dict(meter=(6, 8), steps=96, max_rest_run=cap)
            result = model.generate(17, **kwargs)
            self.assertEqual(result, model.generate(17, **kwargs))
            self.assertEqual(result['status'], 'complete')
            self.assertEqual(len(result['tokens']), 96)
            run = 0
            for t in result['tokens']:
                run = run + 1 if t == 0 else 0
                if cap is not None:
                    self.assertLessEqual(run, cap)

    def test_evaluation_not_affected_by_generation_mask(self):
        model = PositionEventModel(self.songs, meter_position=True)
        sequence = [(-1, 128), (2, 1)]
        before = model.evaluate(sequence, meter=(6, 8))
        model.generate(0, meter=(6, 8), max_rest_run=0)
        self.assertEqual(before, model.evaluate(sequence, meter=(6, 8)))

    def test_copy_rejection_bounded(self):
        model = PositionEventModel(self.songs)
        with patch('mousa.position_event_model.onset_phrases', return_value=['match']):
            result = model.generate(0, meter=(6, 8), source_grids=[[2]], max_attempts=3)
            self.assertEqual(result['status'], 'blocked')
            self.assertEqual(result['tokens'], [])
            self.assertEqual(result['rejections'], 3)
            result = model.generate(0, meter=(6, 8), source_grids=[[2]], guard=False)
            self.assertEqual(result['status'], 'complete')

    def test_actual_eight_onset_copy_block(self):
        model = PositionEventModel(self.songs)
        ps = {p: float(p == 14) for p in PITCHES}
        ds = {rest: {d: float(d == 1) for d in DURATIONS} for rest in (False, True)}
        with patch.object(model, 'distributions', return_value=(ps, ds)):
            result = model.generate(0, meter=(6, 8), steps=12,
                                    source_grids=[[14] * 8], max_attempts=4)
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['tokens'], [14] * 7)
        self.assertEqual(result['rejections'], 4)

    def test_settings_reject(self):
        for settings in ({'phrase_bars': 0}, {'meter_position': 1}, {'phrase_position': None}):
            with self.assertRaises(ValueError):
                PositionEventModel(self.songs, **settings)
        model = PositionEventModel(self.songs)
        for settings in ({'max_rest_run': -1}, {'max_rest_run': True}, {'max_attempts': 0},
                         {'max_attempts': 65}, {'steps': 0}, {'guard': 1}):
            with self.assertRaises(ValueError):
                model.generate(0, meter=(6, 8), **settings)
        for meter in ((3, 4), (True, 4), [6, 8]):
            with self.assertRaises(ValueError):
                model.evaluate([(2, 1)], meter=meter)


if __name__ == '__main__':
    unittest.main()

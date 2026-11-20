import unittest
from unittest.mock import patch

from mousa.phrase_baseline import generate_phrase_form
from mousa.position_event_model import PositionEventModel


class FixtureModel:
    def __init__(self, tokens):
        self.tokens = tokens
        self.calls = []

    def generate(self, seed, **kwargs):
        self.calls.append((seed, kwargs))
        return dict(status='complete', tokens=self.tokens.copy(), rejections=0)


class PhraseBaselineTests(unittest.TestCase):
    def test_structure_lengths_and_determinism(self):
        for meter, steps in (((6, 8), 24), ((4, 4), 32)):
            motif = [14] + [1] * (steps - 1)
            model = FixtureModel(motif)
            result = generate_phrase_form(model, 42, meter=meter)
            self.assertEqual(result, generate_phrase_form(model, 42, meter=meter))
            self.assertEqual(result['status'], 'complete')
            self.assertEqual(len(result['tokens']), 4 * steps)
            self.assertEqual(result['tokens'][:steps], motif)
            self.assertEqual(result['tokens'][2*steps:3*steps], motif)
            transforms = result['decisions'][-1]['transforms']
            for block, shift in ((1, transforms[1]), (3, transforms[3])):
                self.assertEqual(result['tokens'][block*steps], 14 + shift)
                self.assertEqual(result['tokens'][block*steps+1:(block+1)*steps], motif[1:])
            self.assertNotEqual(model.calls[0][0], model.calls[1][0])

    def test_cross_boundary_copy_rejected(self):
        # Each 2-bar fragment has only four onsets, so cannot trigger 8-onset
        # matching alone. Build an actual eight-onset source across A/A'.
        motif = sum(([p] + [1]*5 for p in (14, 15, 17, 16)), [])
        baseline = generate_phrase_form(FixtureModel(motif), 5, meter=(6, 8), max_attempts=1)
        source = baseline['tokens'][:48]
        result = generate_phrase_form(FixtureModel(motif), 5, meter=(6, 8),
                                      source_grids=[source], max_attempts=1)
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['rejections']['source_copy'], 1)
        self.assertEqual(result['tokens'], [])

    def test_rest_join_rejected(self):
        motif = [0]*8 + [14] + [1]*7 + [0]*8
        result = generate_phrase_form(FixtureModel(motif), 5, meter=(6, 8), max_rest_run=12, max_attempts=3)
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['rejections']['rest_boundary'], 3)
        self.assertEqual(len(result['decisions']), 3)

    def test_pitch_extremes_reject_not_clip(self):
        motif = [2] + [1]*11 + [26] + [1]*11
        model = FixtureModel(motif)
        result = generate_phrase_form(model, 0, meter=(6, 8), max_attempts=2)
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['rejections']['pitch_bounds'], 2)
        self.assertEqual(len(model.calls), 4)

    def test_fragment_failure_and_invalid_tokens(self):
        for motif in ([1]*24, [27]*24, [14]*23):
            result = generate_phrase_form(FixtureModel(motif), 0, meter=(6, 8), max_attempts=1)
            self.assertEqual(result['rejections']['fragment'], 1)
        model = FixtureModel([14]*24)
        with patch.object(model, 'generate', return_value=dict(status='blocked', tokens=[], rejections=16)):
            result = generate_phrase_form(model, 0, meter=(6, 8), max_attempts=2)
        self.assertEqual(result['fragment_rejections'], 64)
        self.assertEqual(result['status'], 'blocked')

    def test_real_model_deterministic_bounded(self):
        model = PositionEventModel([((6, 8), [(14, 3), (16, 3), (17, 6)])])
        kwargs = dict(meter=(6, 8), max_rest_run=3, max_attempts=4)
        result = generate_phrase_form(model, 81, **kwargs)
        self.assertEqual(result, generate_phrase_form(model, 81, **kwargs))
        self.assertLessEqual(len(result['decisions']), 4)
        if result['status'] == 'complete':
            self.assertEqual(len(result['tokens']), 96)
            self.assertTrue(all(0 <= t <= 26 for t in result['tokens']))

    def test_invalid_settings(self):
        for kwargs in ({'max_attempts': 0}, {'max_attempts': 65}, {'max_rest_run': -1},
                       {'max_rest_run': True}, {'source_grids': [[], ]*13}):
            with self.assertRaises(ValueError):
                generate_phrase_form(FixtureModel([14]*24), 0, meter=(6, 8), **kwargs)
        with self.assertRaises(ValueError):
            generate_phrase_form(FixtureModel([14]*24), True, meter=(6, 8))
        with self.assertRaises(ValueError):
            generate_phrase_form(FixtureModel([14]*24), 0, meter=(3, 4))


if __name__ == '__main__':
    unittest.main()

from dataclasses import replace
import json
import math
import unittest

from mousa.scales import Key, Scale, ScaleCondition, load_catalogue, strict_json
from mousa.scale_midi import make_exercise


class ScaleTests(unittest.TestCase):
    def setUp(self):
        self.catalogue = load_catalogue()
        self.major = self.catalogue["major_12tet"]
        self.condition = ScaleCondition(self.major, Key.from_name("C4"))

    def test_catalogue_contains_explicit_approximations_and_microtones(self):
        self.assertEqual(len(self.catalogue), 6)
        self.assertEqual(self.catalogue["ryukyu_12tet"].intervals_cents, (0, 400, 500, 700, 1100))
        self.assertEqual(len(self.catalogue["equal_24_test"].intervals_cents), 24)
        for scale in self.catalogue.values():
            self.assertTrue(scale.source_urls)
            self.assertTrue(scale.approximation)
            self.assertEqual(Scale.from_dict(scale.to_dict()), scale)

    def test_transposition_preserves_intervals_in_all_twelve_keys(self):
        for tonic in range(60, 72):
            condition = ScaleCondition(self.major, Key(tonic))
            self.assertEqual(tuple(condition.pitch_cents(n) - condition.pitch_cents(0)
                                   for n in range(7)), self.major.intervals_cents)

    def test_key_spelling_and_scientific_octave(self):
        self.assertEqual(Key.from_name("C4").tonic_midi, 60)
        self.assertEqual(Key.from_name("F#3"), Key.from_name("Gb3"))
        self.assertEqual(Key.from_name("Cb4"), Key.from_name("B3"))
        self.assertEqual(Key.from_name("B#3"), Key.from_name("C4"))
        for name in ["C", "H4", "C4;exit", "C10", "Cb-1", 60, None]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                Key.from_name(name)

    def test_tonic_micro_offset_and_concert_tuning_are_independent(self):
        a = ScaleCondition(self.major, Key(69))
        b = ScaleCondition(self.major, Key(69, reference_a4_hz=442))
        c = ScaleCondition(self.major, Key(69, tonic_offset_cents=50))
        self.assertEqual(a.frequency_hz(0), 440)
        self.assertEqual(b.frequency_hz(0), 442)
        self.assertEqual(a.pitch_cents(0), b.pitch_cents(0))
        self.assertAlmostEqual(c.frequency_hz(0) / a.frequency_hz(0), 2 ** (50 / 1200))

    def test_scale_degree_candidates_are_constrained_without_rounding(self):
        self.assertEqual(self.condition.candidate_mask([6000, 6100, 6200, 6300]),
                         (True, False, True, False))
        micro = ScaleCondition(self.catalogue["equal_24_test"], Key(60))
        self.assertTrue(micro.contains_pitch(6050))
        self.assertFalse(self.condition.contains_pitch(6050))
        self.assertTrue(self.condition.contains_pitch(4800))
        self.assertEqual(self.condition.candidate_mask([6100, 6300]), (False, False))

    def test_non_octave_period_is_not_silently_replaced(self):
        scale = replace(self.major, period_cents=1300)
        condition = ScaleCondition(scale, Key(60))
        self.assertEqual(condition.pitch_cents(0, 1), 7300)
        self.assertTrue(condition.contains_pitch(7300))

    def test_condition_roundtrip_and_definition_binding(self):
        payload = strict_json(json.dumps(self.condition.to_dict()))
        self.assertEqual(ScaleCondition.from_dict(payload), self.condition)
        altered = replace(self.major, intervals_cents=(0, 100, 400, 500, 700, 900, 1100))
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            ScaleCondition.from_dict(payload, {altered.scale_id: altered})
        payload["chords"] = []
        with self.assertRaisesRegex(ValueError, "unknown/missing"):
            ScaleCondition.from_dict(payload)

    def test_reject_bad_numeric_values_and_boolean_coercion(self):
        for value in [True, "50", math.nan, math.inf, -math.inf]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                Key(60, tonic_offset_cents=value)
        for args in [(True,), (-1,), (128,), (60, 101), (60, 0, 0)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                Key(*args)
        for degree in [True, -1, 7, 1.5]:
            with self.subTest(degree=degree), self.assertRaises(ValueError):
                self.condition.pitch_cents(degree)

    def test_reject_invalid_scale_sets(self):
        for intervals in [(), (100, 200), (0, 200, 100), (0, 100, 100),
                          (0, 1200), (0, math.nan), (0, True), tuple(range(65))]:
            with self.subTest(intervals=intervals), self.assertRaises(ValueError):
                replace(self.major, intervals_cents=intervals)

    def test_strict_json_and_closed_key(self):
        for text in ['{"a":1,"a":2}', '{"a":NaN}', '{"a":1e999}', '[]' * 40000]:
            with self.assertRaises(ValueError):
                strict_json(text)
        with self.assertRaises(ValueError):
            Key.from_dict({"tonic_midi": 60})
        with self.assertRaises(ValueError):
            self.condition.candidate_mask([6000] * 4097)


class ScaleMidiTests(unittest.TestCase):
    def test_all_scales_and_keys_produce_deterministic_mono_exercises(self):
        families = set()
        for scale in load_catalogue().values():
            for tonic in range(60, 72):
                condition = ScaleCondition(scale, Key(tonic))
                midi, metadata = make_exercise(condition)
                self.assertEqual((midi, metadata), make_exercise(condition))
                self.assertEqual(midi[:14], b"MThd\x00\x00\x00\x06\x00\x00\x00\x01\x01\xe0")
                self.assertEqual(len(metadata["notes"]), 2 * len(scale.intervals_cents) + 1)
                for row in metadata["notes"]:
                    self.assertTrue(condition.contains_pitch(row["pitch_cents"]))
                    self.assertLess(abs(row["pitch_error_cents"]), 0.013)
                families.add(metadata["family_id"])
        self.assertEqual(families, {"mousa:synthetic-scale-exercises:v1"})

    def test_microtonal_pitchbend_and_tuning_are_present(self):
        condition = ScaleCondition(load_catalogue()["equal_24_test"], Key(60))
        midi, metadata = make_exercise(condition)
        self.assertIn(b"\xb0\x65\x00\x00\xb0\x64\x00\x00\xb0\x06\x02", midi)
        row = metadata["notes"][1]
        self.assertEqual(row["pitch_cents"], 6050)
        self.assertEqual(row["pitch_bend_14bit"], 6144)
        self.assertEqual(row["midi_note"], 61)
        self.assertEqual(metadata["notes"][24]["pitch_cents"], 7200)
        self.assertEqual(metadata["notes"][-1]["pitch_cents"], 6000)

    def test_bounds_fail_without_silent_pitch_clipping(self):
        condition = ScaleCondition(load_catalogue()["major_12tet"], Key(120))
        with self.assertRaisesRegex(ValueError, "range"):
            make_exercise(condition)
        for options in [{"bpm": True}, {"bpm": 0}, {"duration_ticks": 481}]:
            with self.assertRaises(ValueError):
                make_exercise(ScaleCondition(load_catalogue()["major_12tet"], Key(60)), **options)


if __name__ == "__main__":
    unittest.main()

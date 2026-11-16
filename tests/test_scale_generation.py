import tempfile
from pathlib import Path
import unittest

from mousa import Key, ScaleCondition, load_catalogue
from mousa.scale_generation import (
    MANIFEST_SHA, WEIGHTS_SHA, RESULT_SCHEMA, allowed_labels, make_request,
    run_generation, validate_result,
)


def synthetic_result(condition):
    result = {"schema": RESULT_SCHEMA, "request": make_request(condition),
              "manifest_sha256": MANIFEST_SHA, "weights_sha256": WEIGHTS_SHA,
              "trained": False, "ppq": 480, "end_tick": 15360,
              "tempo_bpm": 100, "meter": [4, 4], "samples": []}
    for seed in (101, 102, 103):
        events, trace = [], []
        ph, rh = [24, 26, 26, 23, 24, 22, 26, 24], [10, 10, 12, 10, 10, 12, 10, 10]
        for tick in range(0, 15360, 480):
            pitch = condition.key.tonic_midi
            events.append({"pitch": pitch, "onset_tick": tick, "duration_ticks": 432,
                           "channel": 0, "velocity": 80})
            trace.append({"allowed_pitch_labels": list(allowed_labels(condition, pitch)),
                          "history_pitch": ph, "history_rhythm": rh, "onset_tick": tick,
                          "pitch_label": 24, "rhythm_label": 12, "gap_ticks": 480,
                          "raw_pitch_logits": [0 if k == 24 else -1000 for k in range(49)],
                          "pitch_rng_word": 2147483648,
                          "constrained_pitch_probabilities": [int(k == 24) for k in range(49)]})
            ph, rh = ph[1:] + [24], rh[1:] + [12]
        result["samples"].append({"seed": seed, "events": events, "trace": trace,
                                  "event_count": len(events), "synthetic_primer_emitted": False})
    return result


class ScaleGenerationTests(unittest.TestCase):
    def setUp(self):
        self.condition = ScaleCondition(load_catalogue()["major_12tet"], Key.from_name("C4"))

    def test_scale_and_key_change_allowed_next_notes(self):
        self.assertIn(26, allowed_labels(self.condition, 60))
        self.assertNotIn(25, allowed_labels(self.condition, 60))
        ryukyu = ScaleCondition(load_catalogue()["ryukyu_12tet"], Key.from_name("D4"))
        self.assertNotIn(26, allowed_labels(ryukyu, 62))
        self.assertIn(28, allowed_labels(ryukyu, 62))
        with self.assertRaises(ValueError):
            allowed_labels(self.condition, 61)

    def test_missing_condition_has_no_unconstrained_fallback(self):
        with self.assertRaises(ValueError):
            make_request(None)

    def test_unsupported_microtones_fail_before_model_or_output(self):
        condition = ScaleCondition(load_catalogue()["equal_24_test"], Key(60))
        with tempfile.TemporaryDirectory() as root:
            output = Path(root) / "out"
            with self.assertRaisesRegex(ValueError, "unsupported tuning"):
                run_generation("missing-binary", "missing-checkpoint", condition, output)
            self.assertFalse(output.exists())

    def test_tonic_micro_offset_and_retuning_are_explicitly_unsupported(self):
        for key in (Key(60, 50), Key(60, reference_a4_hz=442), Key(96)):
            with self.assertRaises(ValueError):
                make_request(ScaleCondition(self.condition.scale, key))

    def test_valid_trace_and_tampered_condition(self):
        result = synthetic_result(self.condition)
        report = validate_result(result, self.condition)
        self.assertEqual(report["off_scale_notes"], 0)
        other = ScaleCondition(self.condition.scale, Key(62))
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            validate_result(result, other)

    def test_forbidden_probability_is_exactly_zero(self):
        result = synthetic_result(self.condition)
        result["samples"][0]["trace"][0]["constrained_pitch_probabilities"][25] = 1e-30
        with self.assertRaisesRegex(ValueError, "off-scale probability"):
            validate_result(result, self.condition)

    def test_probabilities_must_follow_actual_masked_logits(self):
        result = synthetic_result(self.condition)
        result["samples"][0]["trace"][0]["raw_pitch_logits"] = [0] * 49
        with self.assertRaisesRegex(ValueError, "masked model logits"):
            validate_result(result, self.condition)

    def test_sample_must_follow_the_recorded_constrained_distribution(self):
        result = synthetic_result(self.condition)
        step = result["samples"][0]["trace"][0]
        allowed = step["allowed_pitch_labels"]
        step["raw_pitch_logits"] = [0] * 49
        step["constrained_pitch_probabilities"] = [1 / len(allowed) if k in allowed else 0 for k in range(49)]
        step["pitch_rng_word"] = 0
        with self.assertRaisesRegex(ValueError, "sampled pitch"):
            validate_result(result, self.condition)

    def test_outside_note_or_choice_is_rejected(self):
        for mutate in [lambda sample: sample["events"][1].update(pitch=61),
                       lambda sample: sample["trace"][0].update(pitch_label=25)]:
            result = synthetic_result(self.condition)
            mutate(result["samples"][0])
            with self.assertRaises(ValueError):
                validate_result(result, self.condition)

    def test_history_must_follow_constrained_choice(self):
        result = synthetic_result(self.condition)
        result["samples"][0]["trace"][1]["history_pitch"] = [0] * 8
        with self.assertRaisesRegex(ValueError, "history"):
            validate_result(result, self.condition)

    def test_checkpoint_and_timing_cannot_be_substituted(self):
        for key, value in [("weights_sha256", "bad"), ("end_tick", 1), ("trained", True)]:
            result = synthetic_result(self.condition)
            result[key] = value
            with self.assertRaises(ValueError):
                validate_result(result, self.condition)


if __name__ == "__main__":
    unittest.main()

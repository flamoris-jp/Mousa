from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from mousa import Key, ScaleCondition, load_catalogue
from mousa.degrees import Degree, TASK_ID, decoded_pitches, degree_for_pitch, encode_history, symbolic_training_fixture
from mousa.degree_generation import generate_degrees, generation_request, render_generated


class DegreeTests(unittest.TestCase):
    def setUp(self):
        self.catalogue = load_catalogue()

    def test_label_is_ordinal_and_register_not_a_semitone_interval(self):
        value = Degree(1)
        self.assertEqual(value.label, 65)
        major = ScaleCondition(self.catalogue["major_12tet"], Key(60))
        micro = ScaleCondition(self.catalogue["equal_24_test"], Key(60))
        self.assertEqual(decoded_pitches([value.label], major)[0]["pitch_cents"], 6200)
        self.assertEqual(decoded_pitches([value.label], micro)[0]["pitch_cents"], 6050)

    def test_same_ordinal_moves_follow_different_scale_shapes(self):
        labels = [Degree(n).label for n in (0, 1, 2, 3, 4)]
        major = ScaleCondition(self.catalogue["major_pentatonic_12tet"], Key(60))
        ryukyu = ScaleCondition(self.catalogue["ryukyu_12tet"], Key(60))
        self.assertEqual([r["pitch_cents"] for r in decoded_pitches(labels, major)], [6000,6200,6400,6700,6900])
        self.assertEqual([r["pitch_cents"] for r in decoded_pitches(labels, ryukyu)], [6000,6400,6500,6700,7100])

    def test_key_changes_rendering_not_model_request_or_history(self):
        c = ScaleCondition(self.catalogue["major_12tet"], Key(60))
        d = ScaleCondition(c.scale, Key(62))
        labels = [Degree(2).label, Degree(4, -1).label]
        self.assertEqual(generation_request(7), generation_request(len(d.scale.intervals_cents)))
        for a,b in zip(decoded_pitches(labels,c), decoded_pitches(labels,d)):
            self.assertEqual(b["pitch_cents"]-a["pitch_cents"],200)

    def test_non_octave_repetition_uses_the_declared_period(self):
        scale = replace(self.catalogue["major_12tet"], period_cents=1300)
        row = decoded_pitches([Degree(1,1).label], ScaleCondition(scale,Key(60)))[0]
        self.assertEqual(row["pitch_cents"],7500)

    def test_missing_degrees_and_invalid_tokens_fail_without_snapping(self):
        for label,count in [(69,5),(192,7),(-1,7),(True,7)]:
            with self.assertRaises(ValueError):Degree.from_label(label,count)
        for degree,period in [(True,0),(64,0),(0,2)]:
            with self.assertRaises(ValueError):Degree(degree,period)

    def test_history_carries_cardinality_and_past_degrees_only(self):
        self.assertEqual(encode_history([64]*8,7),[1,201]+[66]*8)
        with self.assertRaises(ValueError):encode_history([69]*8,5)
        with self.assertRaises(ValueError):encode_history([64]*7,7)

    def test_annotation_requires_explicit_matching_scale_and_key(self):
        condition = ScaleCondition(self.catalogue["equal_24_test"],Key(60,33.333,442))
        pitch = condition.pitch_cents(1)
        self.assertEqual(degree_for_pitch(condition,pitch),Degree(1))
        with self.assertRaises(ValueError):degree_for_pitch(condition,pitch+20)
        with self.assertRaises(ValueError):degree_for_pitch(condition,1e20)

    def test_training_fixture_has_no_scale_or_key_pitch_information(self):
        data = symbolic_training_fixture()
        self.assertEqual(data["task_id"],TASK_ID)
        self.assertEqual(len(data["rows"]),384)
        self.assertEqual({row["degree_count"] for row in data["rows"]},{5,7,24})
        for row in data["rows"]:
            self.assertEqual(set(row),{"family_id","degree_count","history","target"})
            encode_history(row["history"],row["degree_count"])
            Degree.from_label(row["target"],row["degree_count"])

    def test_legacy_model_fails_before_loading_weights_or_calling_binary(self):
        with tempfile.TemporaryDirectory() as root:
            root=Path(root);model=root/"legacy";model.mkdir()
            (model/"manifest.json").write_text(json.dumps({"schema":"mousa-offline-music-checkpoint-v1"}))
            with self.assertRaisesRegex(ValueError,"cannot be reinterpreted"):
                generate_degrees("missing",model,7,root/"out")
            self.assertFalse((root/"out").exists())

    def test_microtonal_degree_output_renders_with_bend(self):
        condition = ScaleCondition(self.catalogue["equal_24_test"],Key(60))
        midi,metadata = render_generated([64,65,66,67],condition)
        self.assertEqual([r["pitch_cents"] for r in metadata["notes"]],[6000,6050,6100,6150])
        self.assertNotEqual(metadata["notes"][1]["pitch_bend_14bit"],8192)
        self.assertEqual(metadata["midi_sha256"],hashlib.sha256(midi).hexdigest())

    def test_alternate_tuning_and_microtonal_tonic_render_without_legacy_rejection(self):
        condition = ScaleCondition(self.catalogue["equal_24_test"],Key(60,33.333,442))
        _,metadata = render_generated([64,65],condition)
        self.assertAlmostEqual(metadata["notes"][1]["pitch_cents"],6083.333)
        self.assertLess(abs(metadata["notes"][1]["pitch_error_cents"]),0.013)

    def test_out_of_range_render_does_not_clip_or_change_degree(self):
        condition = ScaleCondition(self.catalogue["major_12tet"],Key(127))
        with self.assertRaises(ValueError):render_generated([Degree(6,1).label],condition)


if __name__ == "__main__":
    unittest.main()

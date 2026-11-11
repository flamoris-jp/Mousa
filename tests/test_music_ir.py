import unittest

from mousa.music_ir import MusicIR, NoteEvent


class MusicIRTests(unittest.TestCase):
    def test_roundtrip(self):
        source = MusicIR(ppq=480, tempo_us_per_quarter=500000, notes=(
            NoteEvent(part_id="melody", start_tick=0, duration_ticks=240, pitch=64, velocity=96),
            NoteEvent(part_id="bass", start_tick=0, duration_ticks=480, pitch=40, velocity=88),
        ))
        self.assertEqual(MusicIR.from_dict(source.to_dict()), source)

    def test_empty_score_allowed(self):
        score = MusicIR(ppq=960, tempo_us_per_quarter=750000, notes=())
        self.assertEqual(score.to_dict()["notes"], [])

    def test_reject_pitch_out_of_range(self):
        with self.assertRaises(ValueError):
            NoteEvent("melody", 0, 120, 128, 100)

    def test_reject_bool_in_integer_field(self):
        with self.assertRaises(ValueError):
            NoteEvent("melody", True, 120, 60, 100)

    def test_reject_negative_duration(self):
        with self.assertRaises(ValueError):
            NoteEvent("melody", 0, -1, 60, 100)

    def test_reject_invalid_part_id(self):
        with self.assertRaises(ValueError):
            NoteEvent("../secrets", 0, 120, 60, 100)

    def test_reject_unknown_fields(self):
        data = MusicIR(480, 500000, ()).to_dict()
        data["remote_action"] = "download"
        with self.assertRaises(ValueError):
            MusicIR.from_dict(data)

    def test_reject_note_overflow(self):
        with self.assertRaises(ValueError):
            NoteEvent("melody", 10_000_000, 1, 60, 100)

    def test_reject_too_many_notes(self):
        data = {"ppq": 480, "tempo_us_per_quarter": 500000,
                "notes": [{}] * 4097}
        with self.assertRaises(ValueError):
            MusicIR.from_dict(data)


if __name__ == "__main__":
    unittest.main()

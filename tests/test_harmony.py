"""Harmony semantics and independently parsed synthetic MIDI; no corpus."""

from dataclasses import replace
import io
import json
import unittest

from mousa.degrees import Degree, decoded_pitches
from mousa.harmony import (Chord, Progression, PATTERNS, make_progression,
                           resolve_progression, vary_progression)
from mousa.harmony_midi import make_comparison, render_progression
from mousa.scales import Key, ScaleCondition, load_catalogue

try:
    import mido
except ImportError:
    mido = None


def condition(key="C3", scale="major_12tet"):
    return ScaleCondition(load_catalogue()[scale], Key.from_name(key))


class HarmonyTests(unittest.TestCase):
    def test_key_relative_progression(self):
        p = make_progression()
        for key, expected in (
            ("C3", [[48, 52, 55], [55, 59, 62], [57, 60, 64], [53, 57, 60]]),
            ("D3", [[50, 54, 57], [57, 61, 64], [59, 62, 66], [55, 59, 62]]),
            ("Bb3", [[58, 62, 65], [65, 69, 72], [67, 70, 74], [63, 67, 70]]),
        ):
            with self.subTest(key=key):
                self.assertEqual([r["midi_notes"] for r in resolve_progression(p, condition(key))], expected)

    def test_all_tonics_patterns_and_amounts(self):
        for tonic in range(48, 60):
            c = ScaleCondition(load_catalogue()["major_12tet"], Key(tonic))
            for pattern in PATTERNS:
                p = make_progression(pattern, repeats=2)
                for amount in (0, 0.25, 0.5, 0.75, 1):
                    v, trace = vary_progression(p, c, amount=amount, seed=17)
                    self.assertEqual(trace["changed_slots"], int(amount * 6))
                    self.assertEqual(v.end_tick, p.end_tick)
                    for row in resolve_progression(v, c):
                        self.assertTrue(all(c.contains_pitch(n * 100) for n in row["midi_notes"]))

    def test_degree_and_register_compatibility(self):
        c = condition()
        d = Degree(4, -1)
        p = Progression((Chord(d, "dominant7", 1920),), 1)
        root = resolve_progression(p, c)[0]["midi_notes"][0]
        self.assertEqual(root * 100, decoded_pitches([d.label], c)[0]["pitch_cents"])
        self.assertEqual(Degree.from_label(d.label, 7), d)

    def test_explicit_quality_and_conflict(self):
        p = Progression((Chord(Degree(4), "dominant7", 1920),), 1)
        self.assertEqual(resolve_progression(p, condition())[0]["midi_notes"], [55, 59, 62, 65])
        conflict = replace(p, chords=(Chord(Degree(4), "major7", 1920),))
        with self.assertRaisesRegex(ValueError, "conflicts with scale"):
            resolve_progression(conflict, condition())
        for degree, quality in ((0, "major7"), (1, "minor7"), (6, "half_diminished7")):
            resolve_progression(replace(p, chords=(Chord(Degree(degree), quality, 1920),)), condition())

    def test_meter_split_and_cross_bar_chord(self):
        p = Progression((Chord(Degree(0), "major", 720), Chord(Degree(4), "major", 2160)),
                        bars=2, numerator=3, denominator=4)
        self.assertEqual(p.end_tick, 2880)
        self.assertEqual([(r["start_bar"], r["tick_in_bar"]) for r in resolve_progression(p, condition())],
                         [(0, 0), (0, 720)])
        with self.assertRaisesRegex(ValueError, "exactly fill"):
            replace(p, bars=3)
        with self.assertRaises(ValueError):
            replace(p, denominator=3)

    def test_strict_roundtrip(self):
        p = make_progression()
        self.assertEqual(Progression.from_dict(json.loads(json.dumps(p.to_dict()))), p)
        for field, value in (("ppq", 960), ("bars", True), ("schema_version", "other"), ("extra", 0)):
            payload = {**p.to_dict(), field: value}
            with self.assertRaises(ValueError):
                Progression.from_dict(payload)
        payload = p.to_dict()
        payload["chords"][0]["root"]["extra"] = 0
        with self.assertRaises(ValueError):
            Progression.from_dict(payload)

    def test_unsupported_inputs(self):
        for d, q, ticks in ((Degree(0), "7th", 480), (Degree(7), "major", 480),
                            (Degree(0), "major", True), (Degree(0), "major", 0)):
            with self.assertRaises(ValueError):
                Chord(d, q, ticks)
        for scale in ("natural_minor_12tet", "major_pentatonic_12tet", "equal_24_test"):
            with self.assertRaisesRegex(ValueError, "major scale"):
                resolve_progression(make_progression(), condition(scale=scale))
        for key in (Key(48, 0.1), Key(48, 0, 442)):
            with self.assertRaisesRegex(ValueError, "no tuning fallback"):
                resolve_progression(make_progression(), ScaleCondition(load_catalogue()["major_12tet"], key))
        with self.assertRaisesRegex(ValueError, "MIDI pitch range"):
            resolve_progression(make_progression(), condition("C9"))
        for amount in (-1, 1.01, True, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                vary_progression(make_progression(), condition(), amount=amount)
        for seed in (-1, True, 2**32):
            with self.assertRaises(ValueError):
                vary_progression(make_progression(), condition(), seed=seed)

    def test_variation_nested_replay_and_trace(self):
        p = make_progression(repeats=2)
        before = p.to_dict()
        previous = {}
        for amount in (0, 0.25, 0.5, 0.75, 1):
            v, trace = vary_progression(p, condition(), amount=amount, seed=17)
            self.assertEqual((v, trace), vary_progression(p, condition(), amount=amount, seed=17))
            self.assertEqual(v.chords[0], p.chords[0])
            self.assertEqual(v.chords[-1], p.chords[-1])
            self.assertEqual([x.duration_ticks for x in v.chords], [x.duration_ticks for x in p.chords])
            current = {i: ch for i, ch in enumerate(v.chords) if ch != p.chords[i]}
            self.assertTrue(previous.items() <= current.items())
            self.assertEqual(len(current), trace["changed_slots"])
            for change in trace["changes"]:
                self.assertEqual(change["before"], p.chords[change["index"]].to_dict())
                self.assertEqual(change["after"], v.chords[change["index"]].to_dict())
            previous = current
        self.assertEqual(p.to_dict(), before)

    def test_single_chord_and_range_limited_variation(self):
        p = Progression((Chord(Degree(0), "major", 1920),), 1)
        self.assertEqual(vary_progression(p, condition(), amount=1)[0], p)
        # The triad fits; its seventh exceeds MIDI127. No clamping or failure.
        high = ScaleCondition(load_catalogue()["major_12tet"], Key(117))
        p = Progression((Chord(Degree(0), "major", 640),) * 3, 1)
        v, trace = vary_progression(p, high, amount=1)
        resolve_progression(v, high)
        self.assertLessEqual(trace["changed_slots"], trace["slot_budget"])


@unittest.skipIf(mido is None, "Mido independent parser is verification-only")
class MidiTests(unittest.TestCase):
    def parse(self, data):
        midi = mido.MidiFile(file=io.BytesIO(data))
        absolute = 0
        active = {}
        notes = []
        controls = []
        for msg in midi.tracks[0]:
            absolute += msg.time
            if msg.type == "note_on" and msg.velocity:
                self.assertNotIn(msg.note, active)
                active[msg.note] = (absolute, msg.velocity)
            elif msg.type in ("note_off", "note_on"):
                start, velocity = active.pop(msg.note)
                notes.append((start, absolute - start, msg.note, velocity))
            else:
                controls.append((absolute, msg.dict()))
        self.assertFalse(active)
        self.assertEqual((midi.type, midi.ticks_per_beat), (0, 480))
        return absolute, sorted(notes), controls

    def test_comparison_same_controls_and_real_note_events(self):
        p = make_progression(repeats=2)
        files, meta = make_comparison(p, condition(), seed=17, amount=0.5)
        controls = []
        for name, arm in (("base.mid", "base"), ("varied.mid", "varied")):
            end, notes, ctl = self.parse(files[name])
            self.assertEqual(end, 15360)
            expected = sorted((r["start_tick"], r["duration_ticks"], n, 80)
                              for r in meta[arm]["resolved_chords"] for n in r["midi_notes"])
            self.assertEqual(notes, expected)
            controls.append(ctl)
        self.assertEqual(controls[0], controls[1])
        self.assertNotEqual(files["base.mid"], files["varied.mid"])

    def test_zero_amount_byte_identical(self):
        files, _ = make_comparison(make_progression(), condition(), amount=0)
        self.assertEqual(files["base.mid"], files["varied.mid"])

    def test_shared_tones_off_before_on_and_cross_bar(self):
        p = Progression((Chord(Degree(0), "major", 720), Chord(Degree(0), "major7", 2160)),
                        2, 3, 4)
        midi, _ = render_progression(p, condition(), bpm=120, velocity=91, program=4)
        end, notes, controls = self.parse(midi)
        self.assertEqual(end, 2880)
        self.assertIn((720, 2160, 48, 91), notes)
        self.assertTrue(any(c[1].get("numerator") == 3 for c in controls))
        self.assertTrue(any(c[1].get("tempo") == 500000 for c in controls))
        self.assertTrue(any(c[1].get("program") == 4 for c in controls))


if __name__ == "__main__":
    unittest.main()

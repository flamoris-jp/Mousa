from dataclasses import replace
from fractions import Fraction
import json
import unittest

from mousa.rational_events import BeatEvent, validate, to_events, events_to_notes, to_json_data, from_json_data
from mousa.tick_midi import TickMelody, TickNote


class RationalEventTests(unittest.TestCase):
    def test_equivalent_ppq_and_joint_resolution_bound(self):
        a=TickMelody((TickNote(96,192,60),TickNote(192,384,60)),480,(4,4),ppq=384)
        b=TickMelody((TickNote(120,240,60),TickNote(240,480,60)),600,(4,4),ppq=480)
        self.assertEqual(to_events(a),to_events(b))
        with self.assertRaisesRegex(ValueError,'combined durations'):
            validate((BeatEvent(60,Fraction(1,32749)),BeatEvent(61,Fraction(1,32719))))

    def test_non_grid_exact_roundtrip_and_rearticulation(self):
        melody = TickMelody((TickNote(1, 13, 60, 81, 23), TickNote(13, 35, 60, 93, 17),
                             TickNote(51, 99, 127, 127, 127)), 107, (6, 8), ppq=384)
        events = to_events(melody)
        self.assertEqual([e.pitch for e in events], [-1, 60, 60, -1, 127, -1])
        self.assertEqual(events[0].duration, Fraction(1, 384))
        self.assertEqual(events_to_notes(events, 384), (melody.notes, melody.total_ticks))
        self.assertEqual(from_json_data(json.loads(json.dumps(to_json_data(events)))), events)

    def test_empty_melody_silence_retained(self):
        melody = TickMelody((), 7, (4, 4), ppq=480)
        self.assertEqual(to_events(melody), (BeatEvent(-1, Fraction(7,480), 0, 0),))
        self.assertEqual(events_to_notes(to_events(melody), 480), ((), 7))

    def test_inexact_ppq_rejected_without_rounding(self):
        events = (BeatEvent(60, Fraction(1,3)),)
        self.assertEqual(events_to_notes(events, 480)[1], 160)
        with self.assertRaises(ValueError): events_to_notes(events, 100)
        for ppq in (0, 32768, True, 480.0):
            with self.assertRaises(ValueError): events_to_notes(events, ppq)

    def test_metadata_not_mutated_or_claimed(self):
        melody = TickMelody((TickNote(0, 120, 60),), 240, (4,4),
                            tempo_map=((0,500000),(60,700000)), volume_map=((0,80),),
                            program_map=((0,0),(20,71)))
        before = repr(melody)
        events = to_events(melody)
        self.assertEqual(repr(melody), before)
        self.assertEqual(events_to_notes(events,480),(melody.notes,240))
        self.assertNotIn('tempo',json.dumps(to_json_data(events)))

    def test_invalid_event_fields(self):
        good = BeatEvent(60,Fraction(1,4))
        for changes in (dict(duration=0.25),dict(duration=Fraction(0)),dict(duration=Fraction(-1)),
                        dict(duration=Fraction(1,32768)),dict(pitch=True),dict(pitch=128),
                        dict(velocity=0),dict(release_velocity=128),dict(pitch=-1)):
            with self.assertRaises(ValueError): validate((replace(good,**changes),))
        with self.assertRaises(ValueError): validate([good])
        with self.assertRaises(ValueError): validate(())

    def test_resource_bounds(self):
        with self.assertRaises(ValueError): validate((BeatEvent(60,Fraction(1)),)*4097)
        with self.assertRaises(ValueError): validate((BeatEvent(-1,Fraction(1,100),0),)*8194)
        with self.assertRaises(ValueError): validate((BeatEvent(60,Fraction(600)),)*2)
        validate((BeatEvent(-1,Fraction(1024),0),))

    def test_json_strict_canonical(self):
        data=to_json_data((BeatEvent(60,Fraction(1,2)),))
        for duration in ({'numerator':2,'denominator':4},{'numerator':1.0,'denominator':2},
                         {'numerator':True,'denominator':2},{'numerator':1,'denominator':0},
                         {'numerator':1,'denominator':2,'extra':0}):
            with self.assertRaises(ValueError):from_json_data([{**data[0],'duration':duration}])
        with self.assertRaises(ValueError):from_json_data([{**data[0],'extra':0}])


if __name__=='__main__': unittest.main()

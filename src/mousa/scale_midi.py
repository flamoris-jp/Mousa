"""Original monophonic scale exercises, not a general MIDI/project editor."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

from .music_ir import _integer
from .scales import Key, ScaleCondition, load_catalogue


def _vlq(value):
    _integer(value, "MIDI delta/length", 0, 0x0fffffff)
    result = [value & 127]
    while value >> 7:
        value >>= 7
        result.insert(0, (value & 127) | 128)
    return bytes(result)


def _meta(kind, data):
    return bytes((255, kind)) + _vlq(len(data)) + data


def make_exercise(condition, *, bpm=100, step_ticks=480, duration_ticks=360):
    """SMF type 0; MIDI channel 1; explicit +/-2-semitone pitch bend range.

    One ascending/descending period with a single top note; no chords/ornaments.
    Returns MIDI bytes plus authoritative condition and per-note target metadata.
    """
    if type(condition) is not ScaleCondition:
        raise ValueError("condition must be a ScaleCondition")
    _integer(bpm, "bpm", 20, 300)
    _integer(step_ticks, "step_ticks", 24, 9600)
    _integer(duration_ticks, "duration_ticks", 1, step_ticks)
    count = len(condition.scale.intervals_cents)
    indices = list(range(count + 1)) + list(range(count - 1, -1, -1))
    notes = []
    tuning_shift = 1200 * math.log2(condition.key.reference_a4_hz / 440)
    for index, scale_step in enumerate(indices):
        period, degree = divmod(scale_step, count)
        nominal = condition.pitch_cents(degree, period)
        absolute = nominal + tuning_shift
        note = min(127, max(0, math.floor(absolute / 100 + 0.5)))
        bend = round(8192 + (absolute - note * 100) / 200 * 8192)
        if not 0 <= bend <= 16383 or not 0 <= nominal <= 12700:
            raise ValueError("exercise exceeds supported MIDI pitch/bend range; choose another key")
        realized = note * 100 + (bend - 8192) * 200 / 8192
        notes.append({"degree": degree, "period": period,
                      "start_tick": index * step_ticks, "duration_ticks": duration_ticks,
                      "pitch_cents": nominal, "frequency_hz": condition.frequency_hz(degree, period),
                      "midi_note": note, "pitch_bend_14bit": bend,
                      "pitch_error_cents": realized - absolute})
    metadata = {"schema_version": "mousa.scale-exercise.experimental.v1",
                "condition": condition.to_dict(), "scale": condition.scale.to_dict(),
                "family_id": "mousa:synthetic-scale-exercises:v1",
                "scale_family_id": condition.scale.scale_id,
                "purpose": "synthetic_scale_rule_fixture_not_musical_quality_training",
                "provenance": "Original algorithmic up/down exercise; no source MIDI or melody copied",
                "license": "Apache-2.0 (original synthetic exercise/metadata only; sources retain their rights)",
                "midi_profile": "SMF0_PPQ480_mono_channel1_pitchbend_range_2",
                "ppq": 480, "bpm": bpm, "notes": notes}
    track = bytearray()
    def event(delta, data):
        track.extend(_vlq(delta) + data)
    event(0, _meta(3, condition.scale.scale_id.encode("ascii")))
    event(0, _meta(1, json.dumps(condition.to_dict(), sort_keys=True, separators=(",", ":")).encode("ascii")))
    event(0, _meta(81, round(60000000 / bpm).to_bytes(3, "big")))
    event(0, bytes((192, 0)))
    # Pitch bend sensitivity RPN 0,0; set semitones/cents, then null RPN.
    for controller, value in [(101, 0), (100, 0), (6, 2), (38, 0), (101, 127), (100, 127)]:
        event(0, bytes((176, controller, value)))
    for index, note in enumerate(notes):
        bend = note["pitch_bend_14bit"]
        event(0 if index == 0 else step_ticks - duration_ticks,
              bytes((224, bend & 127, bend >> 7)))
        event(0, bytes((144, note["midi_note"], 80)))
        event(duration_ticks, bytes((128, note["midi_note"], 0)))
    event(0, bytes((224, 0, 64)))
    event(0, _meta(47, b""))
    midi = b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480) + b"MTrk" + struct.pack(">I", len(track)) + track
    metadata["midi_sha256"] = hashlib.sha256(midi).hexdigest()
    return midi, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scale", required=True)
    parser.add_argument("--key", required=True, help="scientific pitch, e.g. C4, F#3, Bb4; C4=MIDI60")
    parser.add_argument("--tonic-cents", type=float, default=0)
    parser.add_argument("--a4-hz", type=float, default=440)
    parser.add_argument("--out", type=Path, required=True, help="new output directory outside Git")
    args = parser.parse_args()
    catalogue = load_catalogue()
    if args.scale not in catalogue:
        parser.error("unknown scale; choose " + ", ".join(catalogue))
    condition = ScaleCondition(catalogue[args.scale], Key.from_name(
        args.key, tonic_offset_cents=args.tonic_cents, reference_a4_hz=args.a4_hz))
    midi, metadata = make_exercise(condition)
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / "exercise.mid").write_bytes(midi)
    (args.out / "exercise.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"scale_id": args.scale, "key": args.key, "notes": len(metadata["notes"]),
                      "midi_sha256": metadata["midi_sha256"]}))


if __name__ == "__main__":
    main()

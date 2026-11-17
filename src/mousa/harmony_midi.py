"""Narrow block-chord A/B fixture exporter; no editable project authority."""

import argparse
import hashlib
import json
from pathlib import Path
import struct

from .harmony import (PPQ, PATTERNS, make_progression, resolve_progression,
                      vary_progression)
from .music_ir import _integer
from .scale_midi import _meta, _vlq
from .scales import Key, ScaleCondition, load_catalogue


def render_progression(progression, condition, *, bpm=100, velocity=80, program=0):
    """SMF0, PPQ480, root-position chords, full slot sustain; off before on."""
    rows = resolve_progression(progression, condition)
    _integer(bpm, "bpm", 20, 300)
    _integer(velocity, "velocity", 1, 127)
    _integer(program, "program", 0, 127)
    track = bytearray()

    def event(delta, data):
        track.extend(_vlq(delta) + data)

    event(0, _meta(3, b"Mousa harmony fixture"))
    event(0, _meta(81, round(60000000 / bpm).to_bytes(3, "big")))
    event(0, _meta(88, bytes((progression.numerator, progression.denominator.bit_length() - 1, 24, 8))))
    fifths = (0, -5, 2, -3, 4, -1, 6, 1, -4, 3, -2, 5)[condition.key.tonic_midi % 12]
    event(0, _meta(89, struct.pack("bB", fifths, 0)))
    event(0, bytes((192, program)))
    for row in rows:
        for note in row["midi_notes"]:
            event(0, bytes((144, note, velocity)))
        for i, note in enumerate(row["midi_notes"]):
            event(row["duration_ticks"] if i == 0 else 0, bytes((128, note, 0)))
    event(0, _meta(47, b""))
    midi = (b"MThd" + struct.pack(">IHHH", 6, 0, 1, PPQ) + b"MTrk"
            + struct.pack(">I", len(track)) + track)
    return midi, {"schema_version": "mousa.harmony-render.experimental.v1",
                  "condition": condition.to_dict(), "progression": progression.to_dict(),
                  "profile": "SMF0_PPQ480_12tet_block_chords_channel1",
                  "bpm": bpm, "velocity": velocity, "program": program,
                  "end_tick": progression.end_tick, "resolved_chords": rows,
                  "midi_sha256": hashlib.sha256(midi).hexdigest()}


def make_comparison(progression, condition, *, amount=0.5, seed=0, bpm=100,
                    velocity=80, program=0):
    """All controls except chord content are shared between both arms."""
    variant, changes = vary_progression(progression, condition, amount=amount, seed=seed)
    base_midi, base = render_progression(progression, condition, bpm=bpm, velocity=velocity, program=program)
    varied_midi, varied = render_progression(variant, condition, bpm=bpm, velocity=velocity, program=program)
    manifest = {"schema_version": "mousa.harmony-comparison.experimental.v1",
                "variation": changes, "base": base, "varied": varied,
                "human_listening": False, "musical_quality_claim": False,
                "provenance": "Caller-provided symbolic progression; rendering grants no input rights"}
    return {"base.mid": base_midi, "varied.mid": varied_midi}, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pattern", choices=tuple(PATTERNS), default="I-V-vi-IV")
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--key", default="C3", help="tonic register, e.g. C3, F#3, Bb3")
    parser.add_argument("--amount", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--bpm", type=int, default=100)
    parser.add_argument("--out", type=Path, required=True, help="new directory outside Git")
    args = parser.parse_args()
    condition = ScaleCondition(load_catalogue()["major_12tet"], Key.from_name(args.key))
    progression = make_progression(args.pattern, repeats=args.repeats)
    files, manifest = make_comparison(progression, condition, amount=args.amount, seed=args.seed, bpm=args.bpm)
    manifest["provenance"] = {
        "source": "Independently encoded elementary degree-pattern teaching fixtures; no external work imported",
        "license": "Apache-2.0 (fixture code and generated symbolic examples)",
        "pattern": args.pattern, "repeats": args.repeats,
        "family_id": "mousa:major-chord-rule-fixtures:v1",
        "training_status": "mechanical rule fixtures; not evidence of learned music or held-out evaluation"}
    args.out.mkdir(parents=True, exist_ok=False)
    for name, content in files.items():
        (args.out / name).write_bytes(content)
    (args.out / "comparison.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pattern": args.pattern, "changed_slots": manifest["variation"]["changed_slots"],
                      "slot_budget": manifest["variation"]["slot_budget"],
                      "end_tick": manifest["base"]["end_tick"],
                      "sha256": {k: hashlib.sha256(v).hexdigest() for k, v in files.items()}}))


if __name__ == "__main__":
    main()

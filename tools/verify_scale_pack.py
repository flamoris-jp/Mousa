"""Independently parse generated fixtures with optional mido==1.3.3.

Mido is a verification dependency only, not a Mousa runtime dependency.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path

import mido


def verify_pack(root):
    root = Path(root)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    total_notes = 0
    maximum_error = 0.0
    for entry in manifest["files"]:
        for field, pin in [("midi", "midi_sha256"), ("metadata", "metadata_sha256")]:
            name = entry[field]
            if Path(name).name != name:
                raise ValueError("fixture name must be flat")
            if hashlib.sha256((root / name).read_bytes()).hexdigest() != entry[pin]:
                raise ValueError("fixture digest mismatch")
        metadata = json.loads((root / entry["metadata"]).read_text(encoding="utf-8"))
        midi = mido.MidiFile(root / entry["midi"])
        if midi.type != 0 or len(midi.tracks) != 1 or midi.ticks_per_beat != 480:
            raise ValueError("wrong SMF profile")
        tick, bend, index = 0, 0, 0
        active = None
        controls = []
        condition_echo = None
        for event in midi.tracks[0]:
            tick += event.time
            if event.type == "text":
                condition_echo = json.loads(event.text)
            elif event.type == "control_change":
                controls.append((event.control, event.value))
            elif event.type == "pitchwheel":
                if active is not None:
                    raise ValueError("pitch bend changed while a note was active")
                bend = event.pitch
            elif event.type == "note_on" and event.velocity:
                if active is not None:
                    raise ValueError("exercise is not monophonic")
                row = metadata["notes"][index]
                if event.channel != 0 or (tick, event.note) != (row["start_tick"], row["midi_note"]):
                    raise ValueError("note/time mismatch")
                if bend + 8192 != row["pitch_bend_14bit"]:
                    raise ValueError("pitch bend mismatch")
                actual_hz = 440 * 2 ** ((event.note - 69 + bend * 2 / 8192) / 12)
                error = abs(1200 * math.log2(actual_hz / row["frequency_hz"]))
                maximum_error = max(maximum_error, error)
                if error > 0.013:
                    raise ValueError("microtonal pitch was rounded or incorrectly bent")
                active = event.note
            elif event.type == "note_off" or (event.type == "note_on" and not event.velocity):
                row = metadata["notes"][index]
                if active != event.note or tick != row["start_tick"] + row["duration_ticks"]:
                    raise ValueError("note-off mismatch")
                active = None
                index += 1
        if index != len(metadata["notes"]) or active is not None or bend != 0:
            raise ValueError("incomplete notes or unrestored pitch bend")
        if controls != [(101, 0), (100, 0), (6, 2), (38, 0), (101, 127), (100, 127)]:
            raise ValueError("pitch bend sensitivity RPN missing")
        if condition_echo != entry["condition"] or metadata["condition"] != entry["condition"]:
            raise ValueError("condition metadata mismatch")
        total_notes += index
    return {"midi_files_parsed": len(manifest["files"]), "note_events_checked": total_notes,
            "maximum_pitch_error_cents": maximum_error,
            "parser": "mido", "parser_version": str(mido.version_info),
            "audio_playback_verified": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify_pack(args.directory), indent=2))

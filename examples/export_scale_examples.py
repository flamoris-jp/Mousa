"""Create the original six-scale/twelve-key fixture pack outside the repository."""

import argparse
import hashlib
import json
from pathlib import Path

from mousa import Key, ScaleCondition, load_catalogue
from mousa.scale_midi import make_exercise


def export_pack(output):
    output = Path(output)
    catalogue = load_catalogue()
    generated = []
    # Build all outputs before creating a directory; no partial pitch-range run.
    for scale in catalogue.values():
        for tonic in range(60, 72):
            condition = ScaleCondition(scale, Key(tonic))
            midi, metadata = make_exercise(condition)
            stem = f"{scale.scale_id}_tonic{tonic}"
            generated.append((stem, midi, metadata))
    output.mkdir(parents=True, exist_ok=False)
    manifest = {"schema_version": "mousa.scale-fixture-pack.experimental.v1",
                "purpose": "rule and transposition fixtures, not a held-out music corpus",
                "family_id": "mousa:synthetic-scale-exercises:v1", "files": []}
    for stem, midi, metadata in generated:
        (output / (stem + ".mid")).write_bytes(midi)
        text = json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
        (output / (stem + ".json")).write_text(text, encoding="utf-8")
        manifest["files"].append({"midi": stem + ".mid", "metadata": stem + ".json",
                                  "midi_sha256": metadata["midi_sha256"],
                                  "metadata_sha256": hashlib.sha256(text.encode()).hexdigest(),
                                  "condition": metadata["condition"]})
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (output / "README.txt").write_text(
        "Mousa scale/key fixtures: 6 scales x 12 tonic anchors (MIDI 60..71).\n"
        "C4=MIDI60. Every MIDI plays one ascending/descending period, 100 BPM.\n"
        "JSON sidecars are authoritative for names, traditions, tuning, condition and pitches.\n"
        "Traditional scales are 12-TET approximations; 24-EDO is only a mathematical test.\n"
        "Microtones need pitch-bend reception and RPN +/-2-semitone sensitivity.\n"
        "No chords, ornaments, source melodies, trained model or audio are included.\n"
        "All fixtures share one synthetic family. Do not split their transpositions across train/test.\n"
        "Original synthetic exercises/metadata: Apache-2.0. Source references retain their own rights.\n",
        encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    manifest = export_pack(args.out)
    print(json.dumps({"files": len(manifest["files"]), "family_id": manifest["family_id"]}))

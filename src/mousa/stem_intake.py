"""Offline AudioAnalyzer stem intake and explicit, digest-bound review export.

This module stores annotations, not trained models. It neither runs an analyzer
nor follows paths/commands from JSON. No network, corpus publication or MIDI-grid
conversion occurs. Rights declarations are operator evidence, not legal clearance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import tempfile

MAX_JSON, MAX_WAV = 16 * 1024**2, 512 * 1024**2
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
HEX = re.compile(r"[0-9a-f]{64}\Z")
ROLES = {"vocals": "melody", "bass": "bass", "drums": "drums", "harmony": "harmony", "mix": "arrangement"}
WARNINGS = ["estimates_not_ground_truth", "voicing_is_not_note_correctness", "unknown_is_not_rest",
            "same_pitch_onsets_and_polyphony_not_resolved", "stem_beats_are_not_global_song_tempo"]


def require(condition, message):
    if not condition: raise ValueError(message)


def fields(value, expected):
    require(type(value) is dict and set(value) == set(expected.split()), "unknown or missing fields")
    return value


def num(value, low, high, *, integer=False):
    require(type(value) is int if integer else type(value) in (int, float), "numeric type")
    require(low <= value <= high, "numeric range")
    require(math.isfinite(value), "nonfinite number")
    return value


def identifier(value):
    require(type(value) is str and ID.fullmatch(value) is not None, "opaque identifier")
    return value


def digest_text(value):
    require(type(value) is str and HEX.fullmatch(value) is not None, "SHA-256 format")
    return value


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def path_local(value, *, existing=True):
    path = Path(os.path.abspath(value))
    for component in (path, *path.parents):
        if not component.exists() and not component.is_symlink(): continue
        info = component.lstat()
        require(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400, "linked path")
    require(not existing or path.is_file(), "regular local input required")
    return path


def load_json(path):
    path = path_local(path)
    require(0 < path.stat().st_size <= MAX_JSON, "JSON size limit")
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key"); result[key] = value
        return result
    def invalid(_):
        raise ValueError("nonfinite JSON number")
    raw = path.read_bytes()
    require(len(raw) <= MAX_JSON, "JSON size limit")
    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=invalid)
    except (RecursionError, UnicodeError) as exc:
        raise ValueError("JSON encoding/depth") from exc
    count = 0
    stack = [(data, 0)]
    while stack:
        value, depth = stack.pop(); count += 1
        require(depth <= 16 and count <= 400000, "JSON structural limit")
        if type(value) is dict: stack.extend((v, depth+1) for v in value.values())
        elif type(value) is list: stack.extend((v, depth+1) for v in value)
    return data


def publish(path, value):
    path = path_local(path, existing=False)
    require(not path.exists() and path.parent.is_dir(), "new output path required")
    raw = canonical(value); require(len(raw) <= MAX_JSON, "output size limit")
    fd, name = tempfile.mkstemp(prefix=".mousa-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        os.link(name, path)
    finally:
        os.unlink(name)


def validate_features(a, source):
    fields(a, "format schemaVersion algorithm mode source duration sampleRate waveform bpm beats tonality chords preview")
    require(a["format"] == "flamoris.audio-features" and type(a["schemaVersion"]) is int and a["schemaVersion"] == 1,
            "unsupported audio features schema")
    require(a["algorithm"] == "stream-audio-1.0.0" and a["mode"] == "analyze" and a["preview"] is None, "unsupported audio features profile")
    fields(a["source"], "sha256 sizeBytes mtimeUtcTicks")
    require(a["source"]["sha256"] == source["sha256"] and type(a["source"]["sizeBytes"]) is int
            and a["source"]["sizeBytes"] == source["sizeBytes"], "feature source mismatch")
    require(type(a["source"]["mtimeUtcTicks"]) is str and re.fullmatch(r"[0-9]{1,20}", a["source"]["mtimeUtcTicks"]) is not None, "source timestamp")
    duration = num(a["duration"], 0.00001, 600)
    require(abs(duration-source["duration"]) <= .01 and type(a["sampleRate"]) is int and a["sampleRate"] == 11025, "feature timing profile")
    require(type(a["waveform"]) is list and 0 < len(a["waveform"]) <= 6001, "waveform limit")
    last = -1
    for point in a["waveform"]:
        fields(point, "time min max rms"); at = num(point["time"], 0, duration)
        require(at > last, "waveform ordering"); last = at
        require(num(point["min"], -1, 1) <= num(point["max"], -1, 1), "waveform extrema")
        num(point["rms"], 0, 1)
    if a["bpm"] is not None: num(a["bpm"], 1, 400)
    require(type(a["beats"]) is list and len(a["beats"]) <= 6000, "beat limit")
    last = -1
    for beat in a["beats"]:
        num(beat, 0, duration); require(beat > last, "beat ordering"); last = beat
    if a["tonality"] is not None:
        t = fields(a["tonality"], "key scale similarity")
        require(t["key"] in ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
                and t["scale"] in ("major", "minor"), "tonality label")
        num(t["similarity"], 0, 1)
    require(type(a["chords"]) is list and len(a["chords"]) <= 6000, "chord limit")
    last = 0
    for chord in a["chords"]:
        fields(chord, "start end label")
        start = num(chord["start"], last, duration); last = num(chord["end"], start, duration)
        require(last > start and type(chord["label"]) is str and re.fullmatch(r"(?:[A-G]#?m?|N)", chord["label"]) is not None, "chord range/label")


def validate_analysis(a):
    fields(a, "format schemaVersion producer source identity time audioFeatures pitch warnings")
    require(a["format"] == "flamoris.stem-analysis" and type(a["schemaVersion"]) is int and a["schemaVersion"] == 1, "stem schema")
    p = fields(a["producer"], "name version workerSha256 stemWorkerSha256 dependencies")
    require(p["name"] == "AudioAnalyzer" and p["version"] == "stem-analysis-0.1.0", "producer profile")
    digest_text(p["workerSha256"]); digest_text(p["stemWorkerSha256"])
    fields(p["dependencies"], "numpy soundfile librosa")
    for version in p["dependencies"].values():
        require(type(version) is str and re.fullmatch(r"[0-9A-Za-z.+-]{1,64}", version) is not None, "dependency version")
    require(p["dependencies"]["librosa"] == "0.11.0", "pYIN dependency version")
    s = fields(a["source"], "sha256 sizeBytes duration sampleRate channels")
    digest_text(s["sha256"]); num(s["sizeBytes"], 1, MAX_WAV, integer=True)
    duration = num(s["duration"], .00001, 600); num(s["sampleRate"], 8000, 192000, integer=True); num(s["channels"], 1, 2, integer=True)
    ident = fields(a["identity"], "songId familyId stemId role")
    for key in ("songId", "familyId", "stemId"): identifier(ident[key])
    require(type(ident["role"]) is str and ident["role"] in ROLES, "stem role")
    t = fields(a["time"], "unit start end songOffset")
    require(t["unit"] == "seconds", "time unit")
    start, end = num(t["start"], 0, duration), num(t["end"], 0, duration)
    num(t["songOffset"], -600, 86400); require(.1-1e-9 <= end-start <= 30, "excerpt duration")
    validate_features(a["audioFeatures"], s)
    require(a["warnings"] == WARNINGS, "required uncertainty labels")
    pitch = fields(a["pitch"], "method settings frames notes reviewRequired")
    require(pitch["reviewRequired"] is True, "review must be required")
    require(type(pitch["frames"]) is list and type(pitch["notes"]) is list, "pitch arrays")
    if ident["role"] not in ("vocals", "bass"):
        require(pitch["method"] == "not_applicable" and pitch["settings"] is None and not pitch["frames"] and not pitch["notes"], "unsupported role has notes")
        return a
    require(pitch["method"] == "librosa.pyin", "pitch method")
    settings = fields(pitch["settings"], "sampleRate hopLength frameLength fmin fmax resolution voicingThreshold rmsThreshold channelMix")
    expected = dict(sampleRate=16000, hopLength=160, frameLength=2048 if ident["role"]=="vocals" else 4096,
                    fmin=65.4 if ident["role"]=="vocals" else 32.7, fmax=1108.0 if ident["role"]=="vocals" else 392.0,
                    resolution=.2, voicingThreshold=.5, rmsThreshold=1e-4, channelMix="mean")
    require(settings == expected and all(type(settings[k]) is int for k in ("sampleRate", "hopLength", "frameLength")), "pitch settings profile")
    frames = pitch["frames"]
    require(0 < len(frames) <= 3000 and len(frames) == math.ceil((end-start)*100 - 1e-7), "pitch frame count")
    for i, f in enumerate(frames):
        fields(f, "time state f0Hz midi voicingProbability rms")
        at = num(f["time"], start, end); require(abs(at - (start+i*.01)) < 1e-6 and at < end, "pitch time sequence")
        probability = num(f["voicingProbability"], 0, 1); energy = num(f["rms"], 0, 1.01)
        require(f["state"] in ("voiced", "low_energy", "unknown"), "pitch state")
        if f["state"] == "voiced":
            hz = num(f["f0Hz"], settings["fmin"], settings["fmax"])
            midi = num(f["midi"], 0, 127)
            require(abs(midi-(69+12*math.log2(hz/440))) < 1e-5 and probability >= .5 and energy >= 1e-4, "voiced values")
        else:
            require(f["f0Hz"] is None and f["midi"] is None, "unknown/low-energy pitch must be null")
            if f["state"] == "low_energy": require(energy < 1e-4, "low-energy threshold")
    require(len(pitch["notes"]) <= 1500, "note count")
    last = start
    for i, n in enumerate(pitch["notes"]):
        fields(n, "id start end pitch medianMidi voicingProbabilityMean reviewState")
        require(n["id"] == f"n{i+1}" and n["reviewState"] == "pending", "note identity/state")
        a0, b0 = num(n["start"], last, end), num(n["end"], start, end)
        require(b0-a0 >= .08-1e-9, "candidate length"); last = b0
        num(n["pitch"], 0, 127, integer=True); num(n["medianMidi"], 0, 127); num(n["voicingProbabilityMean"], .5, 1)
        first = round((a0-start)*100); stop = math.ceil((b0-start)*100 - 1e-7)
        require(0 <= first < stop <= len(frames) and abs(frames[first]["time"]-a0) < 1e-6
                and all(f["state"] == "voiced" for f in frames[first:stop]), "candidate crosses unknown region")
    return a


def check_wav(path, source):
    path = path_local(path)
    before = path.stat()
    require(path.suffix.lower() == ".wav" and 0 < before.st_size <= MAX_WAV and before.st_size == source["sizeBytes"], "WAV size/profile")
    h = hashlib.sha256()
    with path.open("rb") as stream:
        header = stream.read(12)
        require(header[:4] == b"RIFF" and header[8:12] == b"WAVE", "WAV header")
        h.update(header)
        while block := stream.read(1024*1024): h.update(block)
    after = path.stat()
    require((before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
            and h.hexdigest() == source["sha256"], "WAV identity mismatch")


def intake(analysis_path, wav_path, output):
    analysis = validate_analysis(load_json(analysis_path)); check_wav(wav_path, analysis["source"])
    value = {"format": "flamoris.mousa.stem-intake", "schemaVersion": 1, "state": "pending_review",
             "analysisSha256": digest(analysis), "splitGroup": "work-family:"+analysis["identity"]["familyId"],
             "specialization": ROLES[analysis["identity"]["role"]], "trainingEligible": False, "analysis": analysis}
    publish(output, value); return value


def read_intake(path):
    value = fields(load_json(path), "format schemaVersion state analysisSha256 splitGroup specialization trainingEligible analysis")
    require(value["format"] == "flamoris.mousa.stem-intake" and type(value["schemaVersion"]) is int and value["schemaVersion"] == 1
            and value["state"] == "pending_review" and value["trainingEligible"] is False, "intake state/schema")
    a = validate_analysis(value["analysis"])
    require(value["analysisSha256"] == digest(a) and value["splitGroup"] == "work-family:"+a["identity"]["familyId"]
            and value["specialization"] == ROLES[a["identity"]["role"]], "intake digest/group binding")
    return value


def review_template(intake_path, output):
    entry = read_intake(intake_path)
    result = {"format": "flamoris.mousa.stem-review", "schemaVersion": 1,
              "analysisSha256": entry["analysisSha256"], "decision": "pending", "reviewerId": "unassigned",
              "rights": {"trainingAllowed": False, "evidenceId": "unassigned"}, "notes": []}
    publish(output, result); return result


def export_reviewed(intake_path, review_path, output):
    entry = read_intake(intake_path); a = entry["analysis"]
    r = fields(load_json(review_path), "format schemaVersion analysisSha256 decision reviewerId rights notes")
    require(r["format"] == "flamoris.mousa.stem-review" and type(r["schemaVersion"]) is int and r["schemaVersion"] == 1, "review schema")
    require(r["analysisSha256"] == entry["analysisSha256"] and r["decision"] == "approved", "explicit matching approval required")
    require(identifier(r["reviewerId"]) != "unassigned", "reviewer required")
    fields(r["rights"], "trainingAllowed evidenceId")
    require(r["rights"]["trainingAllowed"] is True and identifier(r["rights"]["evidenceId"]) != "unassigned", "training rights review required")
    require(entry["specialization"] in ("melody", "bass"), "no note-task adapter for this stem role")
    require(type(r["notes"]) is list and 0 < len(r["notes"]) <= 1500, "select reviewed notes explicitly")
    originals = {n["id"]: n for n in a["pitch"]["notes"]}; seen = set(); notes = []; last = a["time"]["start"]
    for note in r["notes"]:
        fields(note, "id start end pitch")
        require(type(note["id"]) is str and note["id"] in originals and note["id"] not in seen, "review note reference")
        seen.add(note["id"])
        start = num(note["start"], last, a["time"]["end"]); end = num(note["end"], start, a["time"]["end"])
        require(end > start, "review note length"); last = end
        num(note["pitch"], 0, 127, integer=True)
        notes.append({"candidateId": note["id"], "sourceStartSeconds": start, "durationSeconds": end-start,
                      "songStartSeconds": start+a["time"]["songOffset"], "pitch": note["pitch"],
                      "corrected": any(note[k] != originals[note["id"]][k] for k in ("start", "end", "pitch"))})
    result = {"format": "flamoris.mousa.note-examples", "schemaVersion": 1,
              "analysisSha256": entry["analysisSha256"], "reviewSha256": digest(r), "reviewerId": r["reviewerId"],
              "rightsEvidenceId": r["rights"]["evidenceId"], "sourceSha256": a["source"]["sha256"],
              "identity": a["identity"], "splitGroup": entry["splitGroup"], "specialization": entry["specialization"],
              "quality": "human_reviewed_transcription", "preferenceLabel": None,
              "gapPolicy": "unknown_not_inferred_as_rest", "modelTrainingPerformed": False, "notes": notes}
    publish(output, result); return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("import"); p.add_argument("--analysis", required=True); p.add_argument("--wav", required=True); p.add_argument("--output", required=True)
    p = commands.add_parser("review-template"); p.add_argument("--intake", required=True); p.add_argument("--output", required=True)
    p = commands.add_parser("export-reviewed"); p.add_argument("--intake", required=True); p.add_argument("--review", required=True); p.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        if args.command == "import": intake(args.analysis, args.wav, args.output)
        elif args.command == "review-template": review_template(args.intake, args.output)
        else: export_reviewed(args.intake, args.review, args.output)
    except (ValueError, OSError, TypeError, KeyError, OverflowError):
        parser.exit(1, "Intake rejected; check source identity, schema, approval, rights and new output path.\n")
    print(json.dumps({"status": "saved", "modelTrainingPerformed": False}))


if __name__ == "__main__":
    main()

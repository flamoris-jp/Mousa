"""Degree-native generation first, scale/key rendering second."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

from .degrees import Degree, OUTPUT_WIDTH, TASK_ID, decoded_pitches
from .music_ir import _integer
from .scale_midi import render_degrees
from .scales import Key, ScaleCondition, load_catalogue


def generation_request(degree_count, *, seed=101, length=64):
    _integer(degree_count, "degree_count", 1, 64)
    _integer(seed, "seed", 0, 2147483647)
    _integer(length, "length", 1, 128)
    return {"schema": "mousa.degree-request.experimental.v1", "task_id": TASK_ID,
            "degree_count": degree_count, "seed": seed, "length": length}


def validate_result(result, request, manifest_sha256, weights_sha256):
    if (result.get("schema") != "mousa.degree-result.experimental.v1"
            or result.get("task_id") != TASK_ID or result.get("request") != request
            or result.get("manifest_sha256") != manifest_sha256
            or result.get("weights_sha256") != weights_sha256):
        raise ValueError("degree model/request identity mismatch")
    labels, trace = result.get("labels"), result.get("trace")
    if type(labels) is not list or type(trace) is not list or len(labels) != request["length"] or len(trace) != len(labels):
        raise ValueError("incomplete degree generation")
    count, history = request["degree_count"], [64] * 8
    for label, step in zip(labels, trace):
        Degree.from_label(label, count)
        if step.get("history") != history or step.get("label") != label:
            raise ValueError("degree-history recurrence mismatch")
        probabilities, logits = step.get("probabilities"), step.get("logits")
        for values in (probabilities, logits):
            if type(values) is not list or len(values) != OUTPUT_WIDTH or any(
                    type(v) not in (int, float) or not math.isfinite(v) for v in values):
                raise ValueError("invalid degree probability/logit trace")
        allowed = [k for k in range(OUTPUT_WIDTH) if k % 64 < count]
        if any(probabilities[k] != 0 for k in range(OUTPUT_WIDTH) if k % 64 >= count):
            raise ValueError("nonexistent degree has nonzero probability")
        if any(not 0 <= p <= 1 for p in probabilities) or abs(sum(probabilities)-1) > 1e-12:
            raise ValueError("invalid normalized degree distribution")
        maximum = max(logits[k] for k in allowed)
        weights = {k: math.exp(logits[k]-maximum) for k in allowed}
        mass = sum(weights.values())
        if any(abs(probabilities[k]-weights[k]/mass) > 1e-12 for k in allowed):
            raise ValueError("degree probabilities disagree with model logits")
        word = step.get("rng_word")
        _integer(word, "sampling word", 0, 2 ** 32 - 1)
        total, selected = 0.0, None
        for k in allowed:
            total += probabilities[k]
            if word / 2 ** 32 < total:
                selected = k
                break
        if selected != label:
            raise ValueError("degree sampling trace mismatch")
        history = history[1:] + [label]
    return labels


def generate_degrees(binary, model_directory, degree_count, output, *, seed=101, length=64):
    request = generation_request(degree_count, seed=seed, length=length)
    model_directory, output = Path(model_directory), Path(output)
    if output.exists():
        raise FileExistsError("new output directory required")
    manifest_bytes = (model_directory / "manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != "mousa.degree-model.experimental.v1" or manifest.get("task_id") != TASK_ID:
        raise ValueError("incompatible degree model; semitone checkpoint cannot be reinterpreted")
    weights_sha = hashlib.sha256((model_directory / "weights.pt").read_bytes()).hexdigest()
    if weights_sha != manifest.get("weights_sha256"):
        raise ValueError("degree weights digest mismatch")
    output.mkdir(parents=True)
    request_path = output / "request.json"
    request_path.write_text(json.dumps(request) + "\n", encoding="utf-8")
    result_path = output / "degrees-private.json"
    subprocess.run([str(Path(binary).resolve()), "generate", str(model_directory.resolve()),
                    str(request_path.resolve()), str(result_path.resolve())],
                   check=True, capture_output=True, timeout=120)
    if result_path.stat().st_size > 4 * 1024 * 1024:
        raise ValueError("degree result exceeds bound")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    labels = validate_result(result, request, hashlib.sha256(manifest_bytes).hexdigest(), weights_sha)
    return labels, result


def render_generated(labels, condition, *, generation_identity=None):
    pitches = decoded_pitches(labels, condition)
    choices = [(p["degree"], p["period"]) for p in pitches]
    midi, metadata = render_degrees(condition, choices, step_ticks=240, duration_ticks=216, pad_final_step=True)
    metadata.update(purpose="degree_native_generation", degree_task_id=TASK_ID,
                    degree_labels=list(labels), generation_identity=generation_identity)
    return midi, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--scale", required=True, choices=tuple(load_catalogue()))
    parser.add_argument("--key", required=True)
    parser.add_argument("--tonic-cents", type=float, default=0)
    parser.add_argument("--a4-hz", type=float, default=440)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    condition = ScaleCondition(load_catalogue()[args.scale], Key.from_name(
        args.key, tonic_offset_cents=args.tonic_cents, reference_a4_hz=args.a4_hz))
    labels, result = generate_degrees(args.binary, args.model, len(condition.scale.intervals_cents), args.out)
    midi, metadata = render_generated(labels, condition, generation_identity={
        "manifest_sha256": result["manifest_sha256"], "weights_sha256": result["weights_sha256"]})
    (args.out / "candidate.mid").write_bytes(midi)
    (args.out / "candidate.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"notes": len(labels), "midi_sha256": metadata["midi_sha256"],
                      "degree_task_id": TASK_ID}))


if __name__ == "__main__":
    main()

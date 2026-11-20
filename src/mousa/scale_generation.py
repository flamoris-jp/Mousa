"""Mandatory scale rule for the saved pitch/rhythm encoder generation path.

The saved model scores semitone intervals, not scale definitions. Its native
decoder masks logits BEFORE sampling and feeds the chosen interval back into
the next model call. Microtonal definitions remain available to future models
but are explicitly unsupported by this historical semitone-only checkpoint.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

from .scales import Key, ScaleCondition, load_catalogue

REQUEST_SCHEMA = "mousa.scale-generation-request.experimental.v1"
RESULT_SCHEMA = "mousa.scale-generation-result.experimental.v1"
MANIFEST_SHA = "123c378362a73c4e2ff54da539fa47b4ebabbd29afc2767d540b751cc36bd4db"
WEIGHTS_SHA = "34dd1e168367a12390d2b10c1bf534459c24413a8460e74555da63b625d5d7f7"


def make_request(condition):
    if type(condition) is not ScaleCondition:
        raise ValueError("scale condition is required; there is no unconstrained mode")
    # Fail before model startup rather than silently rounding/dropping degrees.
    if (condition.key.tonic_offset_cents != 0 or condition.key.reference_a4_hz != 440
            or condition.scale.period_cents % 100
            or any(value % 100 for value in condition.scale.intervals_cents)):
        raise ValueError("unsupported tuning for the semitone-only saved checkpoint")
    if not 48 <= condition.key.tonic_midi <= 84:
        raise ValueError("tonic outside saved-model generation range 48..84")
    return {"schema": REQUEST_SCHEMA, "condition": condition.to_dict(),
            "scale": condition.scale.to_dict(), "seeds": [101, 102, 103]}


def allowed_labels(condition, current_pitch):
    make_request(condition)
    if type(current_pitch) is not int or not 48 <= current_pitch <= 84:
        raise ValueError("invalid current pitch")
    if not condition.contains_pitch(current_pitch * 100, tolerance_cents=0):
        raise ValueError("current pitch violates scale")
    return tuple(label for label in range(12, 37)
                 if 48 <= current_pitch + label - 24 <= 84
                 and condition.contains_pitch((current_pitch + label - 24) * 100, tolerance_cents=0))


def validate_result(result, condition):
    """Independent postcondition; no snapping or unconstrained fallback."""
    request = make_request(condition)
    if result.get("schema") != RESULT_SCHEMA or result.get("request") != request:
        raise ValueError("generation condition identity mismatch")
    if result.get("manifest_sha256") != MANIFEST_SHA or result.get("weights_sha256") != WEIGHTS_SHA:
        raise ValueError("checkpoint identity mismatch")
    if result.get("trained") is not False or (result.get("ppq"), result.get("end_tick"),
            result.get("tempo_bpm"), result.get("meter")) != (480, 15360, 100, [4, 4]):
        raise ValueError("generation profile mismatch")
    samples = result.get("samples")
    if type(samples) is not list or [sample.get("seed") for sample in samples] != [101, 102, 103]:
        raise ValueError("generation seeds/order mismatch")
    counts = []
    for sample in samples:
        events, trace = sample.get("events"), sample.get("trace")
        if type(events) is not list or not 1 <= len(events) <= 128 or type(trace) is not list or len(trace) != len(events):
            raise ValueError("incomplete generation trace")
        if sample.get("event_count") != len(events) or sample.get("synthetic_primer_emitted") is not False:
            raise ValueError("generation event count/primer mismatch")
        ph, rh = [24, 26, 26, 23, 24, 22, 26, 24], [10, 10, 12, 10, 10, 12, 10, 10]
        current, tick = condition.key.tonic_midi, 0
        for event, step in zip(events, trace):
            if any(type(event.get(k)) is not int for k in ("pitch", "onset_tick", "duration_ticks", "velocity", "channel")):
                raise ValueError("invalid integer generation event")
            if event["pitch"] != current or event["onset_tick"] != tick or event["velocity"] != 80 or event["channel"] != 0:
                raise ValueError("generation event recurrence mismatch")
            allowed = allowed_labels(condition, current)
            if step.get("allowed_pitch_labels") != list(allowed):
                raise ValueError("scale support mismatch")
            if step.get("history_pitch") != ph or step.get("history_rhythm") != rh or step.get("onset_tick") != tick:
                raise ValueError("model history did not follow constrained choices")
            label, rhythm = step.get("pitch_label"), step.get("rhythm_label")
            if type(label) is not int or label not in allowed or type(rhythm) is not int or rhythm not in (8, 10, 12, 14):
                raise ValueError("sampled label violates generation rules")
            probabilities = step.get("constrained_pitch_probabilities")
            if type(probabilities) is not list or len(probabilities) != 49:
                raise ValueError("invalid probability trace")
            if any(type(p) not in (int, float) or not math.isfinite(p) or not 0 <= p <= 1 for p in probabilities):
                raise ValueError("invalid probability trace")
            if any(probabilities[k] != 0 for k in range(49) if k not in allowed):
                raise ValueError("off-scale probability is nonzero")
            if abs(sum(probabilities) - 1) > 1e-12 or probabilities[label] <= 0:
                raise ValueError("constrained distribution is not normalized")
            logits = step.get("raw_pitch_logits")
            if type(logits) is not list or len(logits) != 49 or any(
                    type(value) not in (int, float) or not math.isfinite(value) for value in logits):
                raise ValueError("invalid raw model logits")
            maximum = max(logits[k] for k in allowed)
            weights = {k: math.exp(logits[k] - maximum) for k in allowed}
            mass = sum(weights.values())
            if any(abs(probabilities[k] - weights[k] / mass) > 1e-12 for k in allowed):
                raise ValueError("probabilities did not use the masked model logits")
            word = step.get("pitch_rng_word")
            if type(word) is not int or not 0 <= word < 2 ** 32:
                raise ValueError("invalid sampling word")
            cumulative, expected_label = 0.0, allowed[-1]
            for candidate in allowed:
                cumulative += probabilities[candidate]
                if word / 2 ** 32 < cumulative:
                    expected_label = candidate
                    break
            if label != expected_label:
                raise ValueError("sampled pitch did not follow constrained probabilities")
            gap = 120 * (1 << ((rhythm - 8) // 2))
            if tick + gap > 15360 or step.get("gap_ticks") != gap or event["duration_ticks"] != gap * 9 // 10:
                raise ValueError("generated timing violates profile")
            ph, rh = ph[1:] + [label], rh[1:] + [rhythm]
            current, tick = current + label - 24, tick + gap
        if tick != 15360:
            raise ValueError("incomplete eight-bar generation")
        counts.append(len(events))
    return {"scale_condition": condition.to_dict(), "events_per_seed": counts,
            "off_scale_notes": 0, "forbidden_probability_mass": 0,
            "history_recurrence_verified": True, "trained": False}


def run_generation(binary, checkpoint, condition, output):
    request = make_request(condition)
    output = Path(output)
    if output.exists():
        raise FileExistsError("output directory must be new")
    checkpoint = Path(checkpoint)
    # Native code independently checks the same pins before loading any tensors.
    for name, expected in [("manifest.json", MANIFEST_SHA), ("weights.pt", WEIGHTS_SHA)]:
        if hashlib.sha256((checkpoint / name).read_bytes()).hexdigest() != expected:
            raise ValueError("checkpoint digest mismatch")
    output.mkdir(parents=True)
    request_path = output / "request.json"
    request_path.write_text(json.dumps(request, ensure_ascii=True, sort_keys=True) + "\n", encoding="utf-8")
    result_path = output / "candidates-private.json"
    subprocess.run([str(Path(binary).resolve()), str(checkpoint.resolve()),
                    str(request_path.resolve()), str(result_path.resolve())],
                   check=True, capture_output=True, timeout=90)
    if result_path.stat().st_size > 4 * 1024 * 1024:
        raise ValueError("native result exceeds bound")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    report = validate_result(result, condition)
    (output / "scale-verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--scale", required=True, choices=tuple(load_catalogue()))
    parser.add_argument("--key", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    condition = ScaleCondition(load_catalogue()[args.scale], Key.from_name(args.key))
    print(json.dumps(run_generation(args.binary, args.checkpoint, condition, args.out), indent=2))


if __name__ == "__main__":
    main()

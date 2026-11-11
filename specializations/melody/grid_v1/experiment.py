"""Run a reproducible, bounded MIDI next-token experiment using Maidionis Core.

No remote execution, online teacher, automatic aesthetic selection or live
Cantabile edit is performed. The output is editable Standard MIDI and evidence.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import subprocess

from maidionis_education.contracts import canonical, digest, loads
from maidionis_education.datasets import freeze, prepare_sample, validate_dataset

from descriptor import (HERE, ROOT, IDENTITY, DESCRIPTOR, CONFIGS, build_digest,
                        component_files, dataset_hooks, dataset_profiles, ref, registry)
from midi_io import midi_tokens, validate_tokens, write_midi, write_preview_wav, tokens_to_notes

UPSTREAM = "a987eeeea11e3971d3b9708bfff6b3545cdb601f"
DATASET_ID = "research.music.mutopia-three-works.v1"


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as target:
        target.write(canonical(value))


def read_corpus(manifest_path):
    manifest_path = Path(manifest_path).resolve()
    corpus = json.loads(manifest_path.read_text())
    if corpus.get("schema_version") != "music.corpus.v1":
        raise ValueError("corpus schema")
    works = [item for item in corpus["works"] if item["status"] == "usable"]
    if not 3 <= len(works) <= 12:
        raise ValueError("initial experiment needs 3..12 explicitly selected works")
    ids, hashes, normalized = set(), set(), set()
    result, reports = [], []
    for index, work in enumerate(works):
        if work["work_id"] in ids or work["sha256"] in hashes:
            raise ValueError("duplicate work or file; versions must not cross splits")
        ids.add(work["work_id"])
        hashes.add(work["sha256"])
        if work["license"] != "Public Domain" or not work.get("license_evidence"):
            raise ValueError("this trial allowlist requires recorded Public Domain evidence")
        path = (manifest_path.parent / work["file"]).resolve()
        if not path.is_relative_to(manifest_path.parent):
            raise ValueError("corpus path escape")
        if digest(path.read_bytes()) != work["sha256"]:
            raise ValueError("source MIDI digest mismatch")
        evidence = (manifest_path.parent / work["source_page_file"]).resolve()
        if not evidence.is_relative_to(manifest_path.parent) or digest(evidence.read_bytes()) != work["source_page_sha256"]:
            raise ValueError("source license evidence digest mismatch")
        tokens, details = midi_tokens(path, work["track_index"])
        validate_tokens(tokens)
        # Uniform-transposition duplicates are caught as an additional mechanical
        # check. The catalog work ID remains the grouping authority for variants.
        normalized_digest = digest(canonical(tokens))
        if normalized_digest in normalized:
            raise ValueError("duplicate normalized melody; regroup the source works")
        normalized.add(normalized_digest)
        split = "train" if index < len(works) - 2 else ("dev" if index == len(works) - 2 else "test")
        result.append(dict(work_sha256=work["sha256"], tokens=tokens, split=split))
        reports.append({**work, **details, "split": split,
                        "normalized_token_sha256": normalized_digest})
    return {"schema_version": "music.sources.v1", "works": result}, reports


def prepare_dataset(manifest_path, output):
    output = Path(output)
    sources, imports = read_corpus(manifest_path)
    profiles, reg, hooks = dataset_profiles(sources), registry(), dataset_hooks(sources)
    time = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    rows, proofs = [], []
    for work, origin in zip(sources["works"], imports):
        sha = work["work_sha256"]
        for index in range(8, len(work["tokens"])):
            sid = f"midi:{sha}:{index}"
            payload = dict(work_sha256=sha, tokens=work["tokens"][index - 8:index], position=index % 16)
            target = dict(token=work["tokens"][index])
            row = dict(schema_version="maidionis.sample.v1", sample_id=sid, family_id="work:" + sha,
                       dataset_id=DATASET_ID, **IDENTITY, input_schema=ref("input"), input=payload,
                       target_schema=ref("target"), target=target, provenance_id="source:" + sid,
                       verification_profile=profiles["verify"], verification_status="verified",
                       tags=["midi", "monophonic", "meter-4-4", "sixteenth", "source-label"], supersedes=None)
            row = prepare_sample(row, reg, hooks, 42)
            proof = dict(schema_version="maidionis.provenance.v1", provenance_id=row["provenance_id"],
                         sample_id=sid, ancestry=[sha], source_digest=digest(canonical(payload)),
                         source_license=origin["license"], generator=profiles["generator"], teacher=None,
                         reviewer=None, non_model_source_reason="Observed next MIDI token, verified against inventoried source sequence; not an attractiveness label",
                         prompt_digest=None, sampling_digest=None, raw_response_digest=None,
                         proposed_target=target, reviewed_target=target, final_target=target,
                         verification_profile=profiles["verify"], outcome="verified", disposition="accepted",
                         human_audit_ref=None, created_at=time, supersedes=None)
            rows.append(row)
            proofs.append(proof)
    members = {**component_files(), "sources.json": canonical(sources),
               "source-import-report.json": canonical(imports)}
    limits = ["Only three distinct compositions in the bundled trial, one per train/dev/test split.",
              "Selected for license and representation compatibility, not attractiveness.",
              "MIDI source labels are verified; musical appeal and generalization are unproven.",
              "A chosen mono track is transposed uniformly; dynamics, accompaniment and tempo are not learned.",
              "Public development and test materials are tiny diagnostics, not a sealed benchmark."]
    sha = freeze(output, rows, proofs, reg, hooks, members, dataset_id=DATASET_ID, seed=42,
                 created_at=time, generator=dict(code_digest=build_digest(), config_digest=profiles["generator"]["config_digest"]),
                 license_summary="Per-work Mutopia Public Domain declarations; code is Apache-2.0.",
                 limitations=limits, purpose="research_fixture")
    validated, checked = validate_dataset(output, sha, reg, hooks)
    return sha, sources, imports, checked, validated


def build_driver(build_dir):
    import cmake
    import nlohmann_json
    import torch
    cmake_binary = str(Path(cmake.CMAKE_BIN_DIR) / "cmake")
    subprocess.run([cmake_binary, "-S", str(HERE / "native"), "-B", str(build_dir),
                    "-DCMAKE_BUILD_TYPE=Release", "-DMAIDIONIS_ROOT=" + str(ROOT),
                    "-DCMAKE_PREFIX_PATH=" + torch.utils.cmake_prefix_path,
                    "-DNLOHMANN_JSON_INCLUDE_DIR=" + str(nlohmann_json.get_include())], check=True, timeout=120)
    subprocess.run([cmake_binary, "--build", str(build_dir), "--target", "maidionis_music_driver", "-j", "2"],
                   check=True, timeout=600)
    return Path(build_dir) / "maidionis_music_driver"


def native(driver, *args, timeout=180):
    process = subprocess.run([str(driver), *map(str, args)], capture_output=True, timeout=timeout)
    if process.returncode:
        raise RuntimeError(process.stderr.decode(errors="replace"))
    if len(process.stdout) > 16 * 1024 * 1024:
        raise ValueError("native response byte limit")
    # Native output contains full 27-class predictions, so use Python JSON here;
    # persisted Maidionis records remain subject to Core's own strict limits.
    return json.loads(process.stdout)


def metrics(targets, probabilities):
    if len(targets) != len(probabilities) or not targets:
        raise ValueError("complete prediction accounting required")
    loss, correct, note_correct, notes = 0.0, 0, 0, 0
    for target, p in zip(targets, probabilities):
        if len(p) != 27 or any(not math.isfinite(v) or v < 0 for v in p) or abs(sum(p) - 1) > 1e-4:
            raise ValueError("invalid categorical probabilities")
        guess = max(range(27), key=lambda index: p[index])
        loss -= math.log(max(p[target], 1e-30))
        correct += guess == target
        if target >= 2:
            notes += 1
            note_correct += guess == target
    return dict(samples=len(targets), cross_entropy_nats=loss / len(targets),
                token_accuracy=correct / len(targets), correct_tokens=correct,
                note_onset_samples=notes, note_onset_correct=note_correct,
                note_onset_token_accuracy=note_correct / notes if notes else None)


def simple_baselines(train_rows, test_rows):
    global_counts, conditional = Counter(), defaultdict(Counter)
    for row in train_rows:
        target = row["target"]["token"]
        global_counts[target] += 1
        conditional[(row["input"]["tokens"][-1], row["input"]["position"])][target] += 1
    def distribution(counts):
        total = sum(counts.values()) + 27
        return [(counts[k] + 1) / total for k in range(27)]
    unigram = distribution(global_counts)
    bigrams = [distribution(conditional.get((r["input"]["tokens"][-1], r["input"]["position"]), global_counts))
               for r in test_rows]
    targets = [row["target"]["token"] for row in test_rows]
    return {"train_unigram": metrics(targets, [unigram] * len(targets)),
            "train_previous_token_and_position": metrics(targets, bigrams)}


def softmax(logits):
    high = max(logits)
    p = [math.exp(value - high) for value in logits]
    total = sum(p)
    return [value / total for value in p]


def matching_note_events(a, b):
    """Transposition-invariant exact interval/onset/duration run diagnostic.

    A common short run is not an infringement or originality verdict.
    """
    def events(tokens):
        notes = tokens_to_notes(tokens)
        return [(y.pitch - x.pitch, y.start - x.start, y.end - y.start)
                for x, y in zip(notes, notes[1:])]
    left, right = events(a), events(b)
    previous, best = [0] * (len(right) + 1), 0
    for x in left:
        current = [0] * (len(right) + 1)
        for j, y in enumerate(right, 1):
            if x == y:
                current[j] = previous[j - 1] + 1
                best = max(best, current[j])
        previous = current
    return best


def run_experiment(output, corpus, driver, epochs=30):
    output = Path(output).resolve()
    if output.exists():
        raise FileExistsError("Choose a new run directory; evidence is never overwritten")
    output.mkdir(parents=True)
    identity = native(driver, "build-identity")
    if identity["build_digest"] != build_digest():
        raise ValueError("native/Python music build identity mismatch; rebuild after source changes")
    data_sha, sources, imports, rows, manifest = prepare_dataset(corpus, output / "dataset")
    preregistration = dict(schema_version="music.trial-plan.v1", upstream_commit=UPSTREAM,
                           build_digest=build_digest(), dataset_digest=data_sha, seed=42, epochs=epochs,
                           batch_size=32, learning_rate=.005, selection_scope="dev",
                           corpus_order=[dict(work_id=w["work_id"], split=w["split"]) for w in imports],
                           measurements=["token cross-entropy", "token accuracy", "note-onset token accuracy"],
                           baselines=["train-unigram", "train-previous-token-and-position"],
                           subjective_evaluation="not performed", generated_seeds=[7, 19],
                           temperature=.9, generated_steps=120, primer_tokens=[2, 1, 4, 1, 6, 1, 9, 1],
                           limitations=manifest["limitations"])
    write_json(output / "preregistration.json", preregistration)
    training = native(driver, "train", output / "dataset", data_sha, output / "checkpoints", output / "export", 0, 0, epochs)
    write_json(output / "training-summary.json", training)
    train_rows = [row for row in rows if row["split"] == "train"]
    all_metrics = {}
    for split in ("train", "dev", "test"):
        selected = [row for row in rows if row["split"] == split]
        request_path = output / (split + "-inputs.json")
        write_json(request_path, [row["input"] for row in selected])
        predicted = native(driver, "infer", output / "dataset", data_sha, output / "export", request_path, training["export_digest"])
        write_json(output / (split + "-predictions.json"), predicted)
        predictions = predicted["predictions"]
        if len(predictions) != len(selected):
            raise ValueError("missing inference results")
        probabilities = [softmax(row["raw_output"]) for row in predictions]
        targets = [row["target"]["token"] for row in selected]
        all_metrics[split] = {"maidionis_dense": metrics(targets, probabilities),
                              **simple_baselines(train_rows, selected)}
    primer = dict(work_sha256=digest(b"original-four-note-primer-v1"),
                  tokens=preregistration["primer_tokens"], position=8)
    write_json(output / "primer.json", primer)
    candidates = []
    for index, seed in enumerate(preregistration["generated_seeds"], 1):
        generated = native(driver, "generate", output / "dataset", data_sha, output / "export",
                           output / "primer.json", 120, seed, .9, training["export_digest"])
        tokens = primer["tokens"] + generated["generated_tokens"]
        validate_tokens(tokens, max_steps=128)
        midi_path = output / f"candidate-{index:02d}.mid"
        info = write_midi(tokens, midi_path, bpm=120)
        write_preview_wav(tokens, output / f"candidate-{index:02d}.wav", bpm=120)
        write_json(output / f"candidate-{index:02d}-generation.json", generated)
        similarity = {origin["work_id"]: matching_note_events(tokens, source["tokens"])
                      for origin, source in zip(imports, sources["works"])}
        candidates.append(dict(file=midi_path.name, midi_sha256=digest(midi_path.read_bytes()), seed=seed,
                               primer_steps=8, generated_steps=120, **info,
                               longest_exact_interval_rhythm_run=similarity,
                               similarity_interpretation="Diagnostic only; no originality or legal conclusion"))
    report = dict(schema_version="music.trial-report.v1", status="research_only",
                  upstream_commit=UPSTREAM, dataset_digest=data_sha, export_digest=training["export_digest"],
                  build_digest=build_digest(), architecture=CONFIGS["architecture"],
                  source_works=[{key: work[key] for key in ("work_id", "title", "split", "source_note_count", "steps", "transposition_semitones")}
                                for work in imports], metrics=all_metrics, candidates=candidates,
                  training=training, musical_attractiveness_evaluated=False,
                  limitations=preregistration["limitations"] + [
                      "Two beats of context cannot model song structure or an eight-bar musical plan.",
                      "Most grid targets are HOLD; overall token accuracy is not melody quality.",
                      "WAV is a neutral local synthesizer preview, not Cantabile rendering or verified AI listening.",
                      "This export is a checksum-verified offline research checkpoint, not an admitted Maidionis serving artifact."])
    write_json(output / "report.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--driver", type=Path)
    parser.add_argument("--build-dir", type=Path, default=Path(".cache/mousa-grid-v1-build"))
    parser.add_argument("--epochs", type=int, default=30)
    args = parser.parse_args()
    if not 1 <= args.epochs <= 100:
        parser.error("epochs must be 1..100")
    driver = args.driver.resolve() if args.driver else build_driver(args.build_dir)
    report = run_experiment(args.output, args.corpus, driver, args.epochs)
    print(json.dumps({"report": str(args.output / "report.json"), "status": report["status"],
                      "sources": len(report["source_works"]), "candidates": report["candidates"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

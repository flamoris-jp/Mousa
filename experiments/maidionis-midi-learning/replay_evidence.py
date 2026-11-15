"""Verify the private historical evidence and recreate inputs, without fitting.

Keep --out outside Git: it contains source-derived private token windows.
The historical scripts, plan and measurements remain byte-for-byte unchanged.
"""

import argparse
from collections import defaultdict
import hashlib
import io
import json
from pathlib import Path
import statistics
import subprocess
import sys
import zipfile


HERE = Path(__file__).resolve().parent
ARCHIVE_SHA256 = "7a67cd00707c6bb0d72bc2722572ace8940404fc5e5d7f6e0d201b991e7851b3"
MAX_ARCHIVE_BYTES = 2 * 1024 * 1024
MAX_MEMBER_BYTES = 8 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require_equal(actual, expected, description):
    if actual != expected:
        raise ValueError(description + " mismatch")


def load_evidence(path):
    with Path(path).open("rb") as source:
        data = source.read(MAX_ARCHIVE_BYTES + 1)
    if len(data) > MAX_ARCHIVE_BYTES:
        raise ValueError("evidence archive too large")
    require_equal(digest(data), ARCHIVE_SHA256, "evidence archive SHA-256")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = archive.infolist()
        names = [member.filename for member in members]
        if len(names) != len(set(names)):
            raise ValueError("duplicate archive member")
        if any(member.file_size > MAX_MEMBER_BYTES for member in members):
            raise ValueError("evidence member too large")
        # Read only inventoried flat names; never extract paths or execute ZIP code.
        expected_names = [
            "plan.json", "native-freeze-audit.json", "midi-preparation-audit.json",
            "freeze_native_frozen.py", "midi_diagnostic.cpp", "summary.json",
            "midi-attribution.json", "baselines-summary.json", "midi-plan.json",
            "midi-dataset-private.json", "results.json",
        ]
        evidence = {name: archive.read(name) for name in expected_names}
    for name in expected_names[:8]:
        require_equal(evidence[name], (HERE / name).read_bytes(), name)
    plan = json.loads(evidence["plan.json"])
    audit = json.loads(evidence["native-freeze-audit.json"])
    pins = {
        "plan.json": audit["plan_sha256"],
        "midi_diagnostic.cpp": plan["native_harness_sha256"],
        "freeze_native_frozen.py": plan["freeze_script_sha256"],
        "midi-plan.json": plan["supersedes_plan_sha256"],
        "midi-dataset-private.json": plan["private_windows_sha256"],
        "results.json": json.loads(evidence["summary.json"])["raw_result_sha256"],
    }
    for name, expected in pins.items():
        require_equal(digest(evidence[name]), expected, name + " SHA-256")
    return evidence


def replay(archive_path, output):
    output = Path(output)
    if output.exists():
        raise FileExistsError("output must be a new directory")
    evidence = load_evidence(archive_path)
    # Only repository-owned, hash-verified code is run. No network or native fit.
    output.mkdir(parents=True)
    for name in ["midi-plan.json", "midi-dataset-private.json",
                 "midi-preparation-audit.json", "midi_diagnostic.cpp"]:
        (output / name).write_bytes(evidence[name])
    (output / "freeze_native_frozen.py").write_bytes(
        (HERE / "freeze_native_frozen.py").read_bytes())
    subprocess.run([sys.executable, str(output.resolve() / "freeze_native_frozen.py")],
                   check=True, capture_output=True, timeout=30)
    expected_data = json.loads(evidence["native-freeze-audit.json"])["private_dataset_sha256"]
    require_equal(digest((output / "data.json").read_bytes()), expected_data,
                  "regenerated native data SHA-256")
    baselines = json.loads((output / "baselines.json").read_bytes())
    for result in baselines["results"]:
        families = defaultdict(list)
        for row in result.pop("rows"):
            families[row["family"]].append(row)
        result["per_family"] = [
            {"family": family, "n": len(rows),
             "nll": statistics.mean(row["nll"] for row in rows),
             "accuracy": statistics.mean(row["correct"] for row in rows)}
            for family, rows in families.items()
        ]
    require_equal(baselines, json.loads(evidence["baselines-summary.json"]),
                  "regenerated count baselines")
    (output / "recorded-results.json").write_bytes(evidence["results.json"])
    subprocess.run([sys.executable, str(HERE / "summarize.py"),
                    str(output.resolve() / "recorded-results.json"),
                    str(output.resolve() / "recorded-summary.json")],
                   check=True, capture_output=True, timeout=30)
    require_equal(json.loads((output / "recorded-summary.json").read_bytes()),
                  json.loads(evidence["summary.json"]), "reaggregated recorded results")
    report = {"archive_sha256": ARCHIVE_SHA256,
              "regenerated_data_sha256": expected_data,
              "count_baselines_exact": True, "recorded_summary_exact": True,
              "native_training_replayed": False}
    (output / "replay-verification.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-zip", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(replay(args.evidence_zip, args.out), indent=2))


if __name__ == "__main__":
    main()

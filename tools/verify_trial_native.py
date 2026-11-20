"""Verify a newly executed trial, never treating archived reports as a new run."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

LAB = Path(__file__).resolve().parents[1] / "specializations/melody/grid_v1"
sys.path.insert(0, str(LAB))
from experiment import native, write_json


def verify(driver, run):
    run = Path(run).resolve()
    report = json.loads((run / "report.json").read_text())
    training = report["training"]
    data, export = run / "dataset", run / "export"
    sha, export_sha = report["dataset_digest"], report["export_digest"]
    checks = {}
    checks["parameters_updated"] = training["parameters_changed"] and training["gradient_l1"] > 0
    checks["parameter_count"] = training["parameter_count"] == 16667
    checks["work_separated_counts"] = [report["metrics"][s]["maidionis_dense"]["samples"] for s in ("train", "dev", "test")] == [648, 248, 248]
    repeat = native(driver, "generate", data, sha, export, run / "primer.json", 120, 7, .9, export_sha)
    original = json.loads((run / "candidate-01-generation.json").read_text())
    checks["repeat_seed_generation"] = repeat == original
    wrong = subprocess.run([str(driver), "infer", str(data), sha, str(export), str(run / "test-inputs.json"), "0" * 64], capture_output=True, timeout=90)
    checks["reject_wrong_export_pin"] = wrong.returncode != 0 and not wrong.stdout and b"trusted music export manifest digest" in wrong.stderr
    verification = run / "verification"
    verification.mkdir()
    corrupt = verification / "tampered-export"
    shutil.copytree(export, corrupt)
    weights = bytearray((corrupt / "best.pt").read_bytes())
    weights[len(weights) // 2] ^= 1
    (corrupt / "best.pt").write_bytes(weights)
    tampered = subprocess.run([str(driver), "infer", str(data), sha, str(corrupt), str(run / "test-inputs.json"), export_sha], capture_output=True, timeout=90)
    checks["reject_tampered_weights"] = tampered.returncode != 0 and not tampered.stdout and b"inventory digest" in tampered.stderr
    shutil.rmtree(corrupt)
    native(driver, "train", data, sha, verification / "checkpoints", verification / "first-two", 2, 0, 30)
    resumed = native(driver, "train", data, sha, verification / "checkpoints", verification / "resumed", 0, 1, 30)
    checks["resume_final_weights"] = resumed["final_sha256"] == training["final_sha256"]
    checks["resume_best_weights"] = resumed["best_sha256"] == training["best_sha256"]
    checks["resume_full_state"] = resumed["state"] == training["state"]
    result = {"schema_version": "mousa.native-verification.v1", "all_passed": all(checks.values()),
              "checks": checks, "build_digest": report["build_digest"], "dataset_digest": sha,
              "export_digest": export_sha, "environment": training["environment"],
              "test_metrics": report["metrics"]["test"],
              "scope": "Same-build offline research mechanics, not musical quality or Runtime serving"}
    write_json(run / "native-verification.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["all_passed"]:
        raise RuntimeError("Native acceptance failed; preserve the evidence")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--driver", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    verify(args.driver.resolve(), args.run)

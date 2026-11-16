"""Small original-symbolic fit/transport check, not a trained music product."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from mousa import Key, ScaleCondition, load_catalogue
from mousa.degrees import TASK_ID, symbolic_training_fixture
from mousa.degree_generation import generate_degrees, render_generated


def run_trial(binary, output):
    binary, output = Path(binary).resolve(), Path(output)
    output.mkdir(parents=True, exist_ok=False)
    plan = {"task_id": TASK_ID, "training_seed":314, "steps":60,
            "generation_seed":101, "generated_notes":64,
            "training_counts":[5,7,24], "data_scope":"original symbolic motifs, all train",
            "heldout_or_quality_claim":False, "gpu":False}
    (output/"plan.json").write_text(json.dumps(plan,indent=2)+"\n")
    data = output/"training-data.json"
    data.write_text(json.dumps(symbolic_training_fixture(),indent=2)+"\n")
    model = output/"model"
    subprocess.run([str(binary),"train",str(data.resolve()),str(model.resolve())],
                   check=True,capture_output=True,timeout=180)
    return render_trial(binary, output)


def render_trial(binary, output):
    """Also usable after a separately completed fixed mechanical fit."""
    binary, output = Path(binary).resolve(), Path(output)
    model = output/"model"
    manifest = json.loads((model/"manifest.json").read_text())
    streams = {}
    for count in (5,7,24):
        labels,result = generate_degrees(binary,model,count,output/f"degree-count-{count}")
        streams[count] = (labels,result)
    pack = output/"midi";pack.mkdir(exist_ok=False)
    entries, results = [], []
    for scale in load_catalogue().values():
        labels,result = streams[len(scale.intervals_cents)]
        condition = ScaleCondition(scale,Key(60))
        midi,meta = render_generated(labels,condition,generation_identity={
            "manifest_sha256":result["manifest_sha256"],"weights_sha256":result["weights_sha256"]})
        meta.update(provenance="Fresh degree-native model fitted only on original symbolic motifs",
                    license="Apache-2.0 (original synthetic trial only; source references retain rights)")
        stem = scale.scale_id
        (pack/(stem+".mid")).write_bytes(midi)
        metadata = json.dumps(meta,ensure_ascii=False,indent=2)+"\n"
        (pack/(stem+".json")).write_text(metadata,encoding="utf-8")
        entries.append({"midi":stem+".mid","metadata":stem+".json",
                        "midi_sha256":meta["midi_sha256"],
                        "metadata_sha256":hashlib.sha256(metadata.encode()).hexdigest(),
                        "condition":condition.to_dict()})
        _,shifted = render_generated(labels,ScaleCondition(scale,Key(62)))
        for original,other in zip(meta["notes"],shifted["notes"]):
            if abs(other["pitch_cents"]-original["pitch_cents"]-200)>1e-8:
                raise ValueError("key failed to transpose the ordinal sequence")
        results.append({"scale_id":stem,"notes":len(labels),
                        "fractional_semitone_notes":sum(row["pitch_cents"]%100!=0 for row in meta["notes"]),
                        "midi_sha256":meta["midi_sha256"],"end_tick":meta["end_tick"]})
    (pack/"manifest.json").write_text(json.dumps({"files":entries},indent=2)+"\n")
    report={"task_id":TASK_ID,"training_rows":manifest["training_rows"],
            "initial_training_nll":manifest["initial_training_nll"],
            "final_training_nll":manifest["final_training_nll"],
            "embedding_delta_l1":manifest["embedding_delta_l1"],
            "reload_logits_exact":manifest["reload_logits_exact"],
            "training_cpu_seconds":manifest["cpu_seconds"],
            "weights_sha256":manifest["weights_sha256"],"legacy_weights_reused":False,
            "midi_files":len(entries),"key_transposition_in_memory":True,
            "same_cardinality_stream_reused_across_scale_shapes":True,"scales":results,
            "music_quality_or_generalization_claim":False}
    (output/"trial-verification.json").write_text(json.dumps(report,indent=2)+"\n")
    return report


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    print(json.dumps(run_trial(args.binary,args.out),indent=2))

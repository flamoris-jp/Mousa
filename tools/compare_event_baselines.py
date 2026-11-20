"""Explicit CPU-only comparison using a separate, pinned Trial 001 checkout.

No downloads, neural training, Cantabile edits or publication. Outputs stay local.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
from collections import Counter

from mousa.research_intake import validate_manifest
from mousa.event_baseline import events_from_grid, EventNGram, longest_shared_run


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--trial-root',type=Path,required=True)
    p.add_argument('--corpus',type=Path,required=True)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    sha=subprocess.check_output(['git','-C',str(a.trial_root),'rev-parse','HEAD'],text=True).strip()
    if sha!='83ca8d477b84a7a8ceff0d80e0af4050b5d27b37': raise ValueError('unexpected trial commit')
    subprocess.run(['git','-C',str(a.trial_root),'diff','--quiet','HEAD'],check=True)
    if a.output.exists(): raise ValueError('new output directory required')
    manifest=json.loads(a.manifest.read_text())
    validate_manifest(manifest,a.corpus)
    sys.path.insert(0,str(a.trial_root/'specializations/melody/grid_v1'))
    from midi_io import midi_tokens,write_midi
    sources={}; report={}; training=[]
    for w in manifest['works']:
        if w['review_state']!='approved':continue
        tokens,details=midi_tokens(a.corpus/w['file'],w['track_index'])
        sources[w['work_id']]=(tokens,events_from_grid(tokens),w['split'])
        if w['split']=='train':training.append(events_from_grid(tokens))
    a.output.mkdir(parents=True)
    config=dict(orders=[0,1,2],alpha=.5,seeds=[7,17,29],steps=128,
        manifest_sha256=hashlib.sha256(a.manifest.read_bytes()).hexdigest(),trial_commit=sha,
        source_hashes={name:hashlib.sha256((Path(__file__).resolve().parents[1]/name).read_bytes()).hexdigest() for name in ("src/mousa/event_baseline.py","tools/compare_event_baselines.py")},
        role='already-inspected three-work diagnostic, not sealed benchmark',
        metrics='next full pitch-duration event; not comparable to grid token accuracy',
        generation='unknown category excluded; last event clipped to eight bars',
        hypothesis='event representation removes HOLD-dominated evaluation; higher order may overfit tiny corpus')
    (a.output/'preregistration.json').write_text(json.dumps(config,indent=2))
    for order in config['orders']:
        started=time.perf_counter();model=EventNGram(training,order,config['alpha'])
        metrics={k:dict(split=split,**model.evaluate(events)) for k,(_,events,split) in sources.items()}
        candidates=[]
        for seed in config['seeds']:
            tokens=model.generate(seed,config['steps']);path=a.output/f'order-{order}-seed-{seed}.mid'
            write_midi(tokens,path)
            reimported, reimport_details=midi_tokens(path,1)
            notes=[x for x in tokens if x>=2]
            exact=max(longest_shared_run(tokens,t) for t,_,split in sources.values() if split=='train')
            candidates.append(dict(seed=seed,file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                disposition='quarantined: similarity and human review required',
                exact_match_alert=exact>=32,reimported_steps=len(reimported),
                reimport_transposition_semitones=reimport_details['transposition_semitones'],note_onsets=len(notes),distinct_pitch_tokens=len(set(notes)),rest_steps=tokens.count(0),
                largest_pitch_share=max(Counter(notes).values())/len(notes) if notes else None,
                longest_exact_training_grid_run=exact,human_review='not performed',
                similarity_limit='exact grid run only; long HOLD/rest runs inflate it; no near/transposed clearance'))
        report[str(order)]=dict(metrics=metrics,candidates=candidates,wall_seconds=time.perf_counter()-started)
    result=dict(config=config,models=report,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                python=sys.version.split()[0],cpu_only=True)
    (a.output/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()

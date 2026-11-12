"""Frozen cross-work probe with exact 4/4 and 6/8 timing, no meter conversion."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
from mousa.research_intake import validate_manifest
from mousa.event_baseline import events_from_grid
from mousa.factorized_baseline import onset_phrases
from mousa.melodic_event_model import MelodicEventModel
from mousa.meter_midi import read_midi,to_tokens,from_tokens,write_midi


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('corpus','manifest','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('new output required')
    manifest=json.loads(a.manifest.read_text());validate_manifest(manifest,a.corpus)
    sources={};input_report={}
    for w in manifest['works']:
        if w['review_state']!='approved':continue
        melody=read_midi(a.corpus/w['file'],w['track_index']);shift=60-min(n.pitch for n in melody.notes)
        tokens=to_tokens(melody,transpose_semitones=shift)
        sources[w['work_id']]=(tokens,events_from_grid(tokens),w['split'])
        input_report[w['work_id']]=dict(meter=list(melody.meter),steps=melody.total_steps,bars=str(melody.bars),
            notes=len(melody.notes),explicit_transposition=shift,split=w['split'],role=w['evaluation_role'])
    duplicates=[]
    for i,(name,(tokens,events,split)) in enumerate(sources.items()):
        for other,(t,e,s) in list(sources.items())[:i]:
            shared=len(set(onset_phrases(tokens))&set(onset_phrases(t)))
            duplicates.append(dict(a=name,b=other,full_normalized_equal=tokens==t,shared_8_note_phrases=shared))
            if split!=s and (tokens==t or shared):raise ValueError('cross-split duplicate signal requires review')
    train=[e for t,e,s in sources.values() if s=='train'];grids=[t for t,e,s in sources.values() if s=='train']
    names=('src/mousa/meter_midi.py','src/mousa/melodic_event_model.py','src/mousa/factorized_baseline.py','tools/probe_meter_transfer.py')
    config=dict(models=['absolute-uniform','absolute-empirical','relative-empirical'],order=1,prior_mass=1.,
        seeds=[7,17,29],generation_meter=[6,8],generation_steps=96,
        selection='relative-empirical selected by lowest prior-cycle dev NLL before new work evaluation; controls retained',
        limitation='event model has no bar-position features; exact meter-aware IO is not learned 6/8 phrasing',
        manifest_sha256=hashlib.sha256(a.manifest.read_bytes()).hexdigest(),
        source_hashes={n:hashlib.sha256((Path(__file__).resolve().parents[1]/n).read_bytes()).hexdigest() for n in names})
    a.output.mkdir(parents=True);(a.output/'preregistration.json').write_text(json.dumps(config,indent=2))
    results={}
    for name in config['models']:
        relative,prior=name.split('-');start=time.perf_counter()
        model=MelodicEventModel(train,relative=relative=='relative',duration_prior=prior)
        metrics={name:dict(split=s,**model.evaluate(e)) for name,(t,e,s) in sources.items()}
        candidates=[]
        for seed in config['seeds']:
            outcome=model.generate(seed,steps=96,source_grids=grids,guard=True);tokens=outcome.pop('tokens')
            path=a.output/f'{name}-seed-{seed}-6-8.mid'
            if outcome['status']=='complete':
                melody=from_tokens(tokens,meter=(6,8));write_midi(melody,path)
                returned=to_tokens(read_midi(path,1,allow_empty=True));digest=hashlib.sha256(path.read_bytes()).hexdigest()
                equal=returned==tokens
            else:digest=None;equal=None
            candidates.append(dict(seed=seed,**outcome,sha256=digest,file=path.name if digest else None,
                exact_roundtrip=equal,steps=len(tokens),note_onsets=sum(t>=2 for t in tokens),
                human_quality_review='not performed',originality='not cleared'))
        results[name]=dict(metrics=metrics,candidates=candidates,wall_seconds=time.perf_counter()-start)
    result=dict(config=config,inputs=input_report,duplicate_checks=duplicates,models=results,
                peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,python=sys.version.split()[0])
    (a.output/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()

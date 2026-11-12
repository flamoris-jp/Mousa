"""Fixed four-candidate smoothness selection; no new music-quality labels."""
import argparse
import hashlib
import json
from pathlib import Path
from fractions import Fraction
from statistics import mean
from mousa.event_baseline import events_from_grid
from mousa.factorized_baseline import onset_phrases
from mousa.meter_midi import read_midi,to_tokens,from_tokens,write_midi
from mousa.position_event_model import PositionEventModel
from mousa.research_intake import validate_manifest


def features(tokens):
    pitches=[x for x in tokens if x>=2];intervals=[abs(b-a) for a,b in zip(pitches,pitches[1:])]
    # Silence or single-note outputs are ineligible, not zero-leap winners.
    if not intervals:return None
    return dict(leap_fraction=Fraction(sum(x>12 for x in intervals),len(intervals)),
        mean_abs_interval=Fraction(sum(intervals),len(intervals)),unique_pitches=len(set(pitches)),
        onsets=len(pitches),rest_steps=tokens.count(0),zero_interval_fraction=Fraction(intervals.count(0),len(intervals)))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('corpus','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();root=Path(__file__).resolve().parents[1]
    if a.output.exists():raise ValueError('new output required')
    freeze=json.loads((root/'experiments/2026-11-12-frozen-transfer-plan.json').read_text())
    for path,sha in freeze['sha256'].items():
        if hashlib.sha256((root/path).read_bytes()).hexdigest()!=sha:raise ValueError('frozen input changed')
    manifest=json.loads((root/'datasets/research-exploratory-multifamily-20261112.json').read_text())
    validate_manifest(manifest,a.corpus)
    origins={f"mutopia-{x['id']}":x['origin_steps'] for x in json.loads((root/'datasets/research-metrical-origins-20261112.json').read_text())['works']}
    songs=[];refs=[]
    for w in manifest['works']:
        m=read_midi(a.corpus/w['file'],w['track_index']);t=to_tokens(m,transpose_semitones=60-min(n.pitch for n in m.notes));refs.append(t)
        if w['work_id'] in freeze['train_ids']:songs.append((m.meter,events_from_grid(t),origins[w['work_id']]))
    assert len(songs)==4
    model=PositionEventModel(songs,**freeze['selected_model']);a.output.mkdir(parents=True)
    forbidden={p for r in refs for p in onset_phrases(r)};rows=[]
    for group in range(20):
        candidates=[]
        for offset in range(4):
            seed=group*4+offset;s=model.generate(seed,meter=(6,8),steps=96,source_grids=refs,max_rest_run=12)
            row=dict(seed=seed,status=s['status'],rejections=s.get('rejections'))
            if s['status']=='complete':
                t=s['tokens'];f=features(t)
                if f is None:row['status']='ineligible_too_few_onsets'
                else:
                    assert not set(onset_phrases(t))&forbidden
                    path=a.output/f'{seed}.mid';write_midi(from_tokens(t,meter=(6,8)),path)
                    assert to_tokens(read_midi(path,1))==t
                    row.update(features=f,midi_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),copy_matches=0,exact_roundtrip=True)
            candidates.append(row)
        valid=[r for r in candidates if r['status']=='complete']
        selected=min(valid,key=lambda r:r['features']['leap_fraction']) if valid else None
        rows.append(dict(group=group,candidates=candidates,control_seed=valid[0]['seed'] if valid else None,selected_seed=selected['seed'] if selected else None))
    summary={}
    for method in ('control','selected'):
        fs=[next(c['features'] for c in r['candidates'] if c['seed']==r[method+'_seed']) for r in rows if r[method+'_seed'] is not None]
        summary[method]={k:float(mean(f[k] for f in fs)) for k in fs[0]} if fs else {}
    report=dict(scope='Exploratory candidate selection, expected objective reduction not proof of appeal',groups=rows,summary=summary,
        empty_groups=sum(r['selected_seed'] is None for r in rows),blocked_candidates=sum(c['status']!='complete' for r in rows for c in r['candidates']),
        code_sha256={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in ['tools/compare_candidate_smoothness.py','experiments/2026-11-12-smoothness-plan.json']},
        frozen_plan_sha256=hashlib.sha256((root/'experiments/2026-11-12-frozen-transfer-plan.json').read_bytes()).hexdigest(),
        limitations=['Four times candidate generation budget versus first-candidate control; no efficiency claim.','Intervals span rests, so this metric does not recognize new phrase beginnings.','Exact eight-onset guard is narrow, not perceptual or legal originality clearance.','No new source admitted or used, no human preference data, no audio release.'])
    (a.output/'report.json').write_text(json.dumps(report,indent=2,default=str)+'\n');print(json.dumps(summary))
if __name__=='__main__':main()

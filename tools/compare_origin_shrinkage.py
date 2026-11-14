"""Exploratory source-aligned position and count-shrinkage diagnostics."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from mousa.event_baseline import events_from_grid
from mousa.meter_midi import read_midi,to_tokens,from_tokens,write_midi
from mousa.position_event_model import PositionEventModel
from mousa.factorized_baseline import onset_phrases
from mousa.research_intake import validate_manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('corpus','manifest','origins','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('new output required')
    manifest=json.loads(a.manifest.read_text());validate_manifest(manifest,a.corpus)
    origins={f"mutopia-{w['id']}":w['origin_steps'] for w in json.loads(a.origins.read_text())['works']}
    sources={}
    for w in manifest['works']:
        m=read_midi(a.corpus/w['file'],w['track_index']);tokens=to_tokens(m,transpose_semitones=60-min(n.pitch for n in m.notes))
        sources[w['work_id']]=dict(events=events_from_grid(tokens),meter=m.meter,tokens=tokens,split=w['split'],family=w['family_id'])
    repo=Path(__file__).resolve().parents[1]
    files=['src/mousa/position_event_model.py','tools/compare_origin_shrinkage.py']
    config=dict(scope='exploratory; all sources previously observed',position_strengths=[0,1,4,16,64],
        alignment=['naive','score'],relative=True,duration_prior='empirical',context='bar only; phrase origin not annotated',
        seeds=[7,17,29],rest_limit=12,generation_origin=0,generation_meter=[6,8],steps=96,
        manifests={str(x.name):hashlib.sha256(x.read_bytes()).hexdigest() for x in [a.manifest,a.origins]},
        code_sha256={x:hashlib.sha256((repo/x).read_bytes()).hexdigest() for x in files})
    a.output.mkdir(parents=True);(a.output/'preregistration.json').write_text(json.dumps(config,indent=2)+'\n')
    train={n:s for n,s in sources.items() if s['split']=='train'};references=[s['tokens'] for s in sources.values()]
    families=sorted({s['family'] for s in train.values()});results={}
    start=time.perf_counter()
    for alignment in config['alignment']:
        for k in config['position_strengths']:
            origin=lambda n:origins[n] if alignment=='score' else 0
            def fit(data):
                return PositionEventModel([(s['meter'],s['events'],origin(n)) for n,s in data.items()],
                    meter_position=True,relative=True,duration_prior='empirical',position_strength=k)
            model=fit(train)
            metrics={n:model.evaluate(s['events'],meter=s['meter'],origin_steps=origin(n)) for n,s in sources.items()}
            folds={}
            for family in families:
                fitting={n:s for n,s in train.items() if s['family']!=family};held={n:s for n,s in train.items() if s['family']==family}
                fold=fit(fitting)
                folds[family]=dict(train_ids=list(fitting),held_ids=list(held),
                    scores={n:fold.evaluate(s['events'],meter=s['meter'],origin_steps=origin(n)) for n,s in held.items()})
            candidates=[]
            for seed in config['seeds']:
                r=model.generate(seed,meter=(6,8),steps=96,source_grids=references,max_rest_run=12)
                tokens=r.pop('tokens');path=a.output/f'{alignment}-k{k}-seed{seed}.mid'
                digest=equal=None
                if r['status']=='complete':
                    write_midi(from_tokens(tokens,meter=(6,8)),path)
                    equal=to_tokens(read_midi(path,1,allow_empty=True))==tokens
                    if not equal:raise AssertionError('roundtrip')
                    digest=hashlib.sha256(path.read_bytes()).hexdigest()
                candidates.append(dict(seed=seed,**r,sha256=digest,exact_roundtrip=equal,
                    file=path.name if digest else None,note_onsets=sum(t>=2 for t in tokens)))
            # Equal family weighting, then equal work weighting inside family.
            macro=sum(sum(v['nll_per_event'] for v in f['scores'].values())/len(f['scores']) for f in folds.values())/len(folds)
            results[f'{alignment}-k{k}']=dict(metrics=metrics,family_folds=folds,family_macro_nll=macro,candidates=candidates)
    report=dict(config=config,results=results,wall_seconds=time.perf_counter()-start,
        limitations=['all source families observed; leave-family-out diagnoses fit, not sealed generalization',
        'single fixed seed set and tiny corpus; no human evaluation','shrinkage mixes counts before factorization, not joint probabilities'])
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({n:r['family_macro_nll'] for n,r in results.items()}))

if __name__=='__main__':main()

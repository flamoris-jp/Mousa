"""Second diagnostic: fixed-support factorization, guarded sampling and MIDI timing."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time
from mousa.research_intake import validate_manifest
from mousa.event_baseline import events_from_grid, longest_shared_run
from mousa.factorized_baseline import FixedEventModel, onset_phrases
from mousa.midi_research_adapter import read_grid


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('trial-root','corpus','manifest','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    sha=subprocess.check_output(['git','-C',str(a.trial_root),'rev-parse','HEAD'],text=True).strip()
    if sha!='83ca8d477b84a7a8ceff0d80e0af4050b5d27b37':raise ValueError('unexpected trial commit')
    subprocess.run(['git','-C',str(a.trial_root),'diff','--quiet','HEAD'],check=True)
    if a.output.exists():raise ValueError('new output directory required')
    manifest=json.loads(a.manifest.read_text());validate_manifest(manifest,a.corpus)
    sys.path.insert(0,str(a.trial_root/'specializations/melody/grid_v1'))
    from midi_io import midi_tokens,write_midi
    sources={}
    for w in manifest['works']:
        if w['review_state']!='approved':continue
        # Corpus normalized explicitly, but generated output kept at original pitch.
        tokens,details=read_grid(a.corpus/w['file'],w['track_index'],midi_tokens,preserve_pitch=False)
        sources[w['work_id']]=(tokens,events_from_grid(tokens),w['split'])
    train=[e for t,e,s in sources.values() if s=='train'];grids=[t for t,e,s in sources.values() if s=='train']
    forbidden={x for t in grids for x in onset_phrases(t)}
    a.output.mkdir(parents=True)
    names=('src/mousa/event_baseline.py','src/mousa/factorized_baseline.py','src/mousa/midi_research_adapter.py','tools/compare_factorization.py')
    config=dict(order=1,prior_mass=1.,duration_support=[1,128],pitch_tokens=[-1,2,26],
        support_size=3328,seeds=[7,17,29],steps=128,guard_phrase_notes=8,
        manifest_sha256=hashlib.sha256(a.manifest.read_bytes()).hexdigest(),trial_commit=sha,
        source_hashes={n:hashlib.sha256((Path(__file__).resolve().parents[1]/n).read_bytes()).hexdigest() for n in names},
        role='already-inspected three-work diagnostic, not sealed benchmark',
        hypothesis='same-support factorization improves unseen pair prediction; phrase guard blocks long source note sequences',
        comparison_warning='Do not compare NLL directly with previous train-vocabulary+UNK experiment')
    (a.output/'preregistration.json').write_text(json.dumps(config,indent=2))
    report={}
    for factorized in (False,True):
        name='factorized' if factorized else 'joint';started=time.perf_counter()
        model=FixedEventModel(train,factorized=factorized)
        metrics={k:dict(split=s,**model.evaluate(e)) for k,(t,e,s) in sources.items()}
        candidates=[]
        for guard in (False,True):
            for seed in config['seeds']:
                result=model.generate(seed,source_grids=grids,guard=guard);tokens=result.pop('tokens')
                result.pop('matching_8_note_phrases',None)
                path=a.output/f'{name}-guard-{int(guard)}-seed-{seed}.mid'
                if result['status']=='complete':
                    write_midi(tokens,path);returned,details=read_grid(path,1,midi_tokens)
                    roundtrip=returned==tokens;digest=hashlib.sha256(path.read_bytes()).hexdigest()
                else:roundtrip=None;digest=None
                candidates.append(dict(seed=seed,guard=guard,**result,file=path.name if digest else None,sha256=digest,
                    exact_roundtrip=roundtrip,steps=len(tokens),note_onsets=sum(t>=2 for t in tokens),
                    longest_exact_grid_run=max(longest_shared_run(tokens,t) for t in grids),
                    matching_8_note_phrases=sum(x in forbidden for x in onset_phrases(tokens)),
                    disposition='research only; near-copy and human quality not cleared'))
        report[name]=dict(metrics=metrics,candidates=candidates,wall_seconds=time.perf_counter()-started)
    result=dict(config=config,models=report,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                python=sys.version.split()[0],cpu_only=True)
    (a.output/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()

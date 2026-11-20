"""Exploratory multifamily, position and rest-limit factorial experiment.

All corpus works have already been observed. Never label these results sealed test
performance. Generation constraints do not change teacher-forced likelihood.
"""
import argparse
import hashlib
import json
import itertools
from pathlib import Path
import resource
import time
from mousa.research_intake import validate_manifest
from mousa.event_baseline import events_from_grid
from mousa.factorized_baseline import onset_phrases
from mousa.position_event_model import PositionEventModel
from mousa.meter_midi import read_midi, to_tokens, from_tokens, write_midi


def structural(tokens, bar_steps=12):
    longest = run = longest_note = note_run = 0
    for token in tokens:
        run = run + 1 if token == 0 else 0
        longest = max(longest, run)
        note_run = 1 if token >= 2 else note_run + 1 if token == 1 else 0
        longest_note = max(longest_note, note_run)
    return dict(note_onsets=sum(t >= 2 for t in tokens), rest_steps=tokens.count(0),
                longest_rest_run=longest, longest_note_steps=longest_note,
                bar_onset_counts=[sum(t >= 2 for t in tokens[i:i+bar_steps])
                                  for i in range(0, len(tokens), bar_steps)])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('corpus', 'manifest', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('new output directory required')
    manifest = json.loads(args.manifest.read_text())
    validate_manifest(manifest, args.corpus)
    sources = {}
    for work in manifest['works']:
        if work['review_state'] != 'approved':
            continue
        melody = read_midi(args.corpus/work['file'], work['track_index'])
        shift = 60-min(n.pitch for n in melody.notes)
        tokens = to_tokens(melody, transpose_semitones=shift)
        sources[work['work_id']] = dict(tokens=tokens, events=events_from_grid(tokens),
            meter=melody.meter, split=work['split'], family=work['family_id'])
    duplicate_checks = []
    for i, (name, s) in enumerate(sources.items()):
        for other, t in list(sources.items())[:i]:
            shared = len(set(onset_phrases(s['tokens'])) & set(onset_phrases(t['tokens'])))
            equal = s['tokens'] == t['tokens']
            duplicate_checks.append(dict(a=name,b=other,equal=equal,shared_8_note_phrases=shared))
            if s['split'] != t['split'] and (shared or equal):
                raise ValueError('cross-split similarity requires review')
    paths = ['src/mousa/position_event_model.py', 'src/mousa/melodic_event_model.py',
             'src/mousa/meter_midi.py','tools/compare_position_generation.py']
    repo = Path(__file__).resolve().parents[1]
    config = dict(scope='exploratory; all six sources previously observed',
        train_conditions=['single','multi'],position_conditions=['none','bar','phrase'],
        rest_limits=[None,12],seeds=[7,17,29,43,59],generation_meter=[6,8],steps=96,
        relative=True,duration_priors=['empirical','typed'],phrase_bars=4,
        hypothesis='Position may improve structural regularity but sparse contexts may overfit; rest cap is a policy constraint, not learned preference.',
        manifest_sha256=hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
        code_sha256={p:hashlib.sha256((repo/p).read_bytes()).hexdigest() for p in paths})
    args.output.mkdir(parents=True)
    (args.output/'preregistration.json').write_text(json.dumps(config,indent=2)+'\n')
    results = {}
    for train in config['train_conditions']:
        selected = {n:s for n,s in sources.items() if s['split']=='train' and
                    (train=='multi' or n=='mutopia-376')}
        songs = [(s['meter'],s['events']) for s in selected.values()]
        # Guard every known reference, not just fitted works; disclose the use of
        # diagnostic references for risk filtering, never feed them to fit().
        references = [s['tokens'] for s in sources.values()]
        for position, prior in itertools.product(config['position_conditions'],config['duration_priors']):
            start = time.perf_counter()
            model = PositionEventModel(songs,meter_position=position!='none',
                phrase_position=position=='phrase',phrase_bars=4,
                relative=True,duration_prior=prior)
            metrics = {n:model.evaluate(s['events'],meter=s['meter']) for n,s in sources.items()}
            candidates = []
            for limit in config['rest_limits']:
                for seed in config['seeds']:
                    outcome = model.generate(seed,meter=(6,8),steps=96,source_grids=references,
                                             guard=True,max_rest_run=limit)
                    tokens = outcome.pop('tokens')
                    path = args.output/f'{train}-{position}-{prior}-rest{limit}-seed{seed}.mid'
                    digest = roundtrip = None
                    if outcome['status']=='complete':
                        write_midi(from_tokens(tokens,meter=(6,8)),path)
                        roundtrip = to_tokens(read_midi(path,1,allow_empty=True))==tokens
                        if not roundtrip: raise AssertionError('roundtrip failed')
                        digest = hashlib.sha256(path.read_bytes()).hexdigest()
                    shared = sum(len(set(onset_phrases(tokens)) & set(onset_phrases(t))) for t in references)
                    if shared: raise AssertionError('guard failed')
                    candidates.append(dict(seed=seed,rest_limit=limit,**outcome,**structural(tokens),
                        sha256=digest,exact_roundtrip=roundtrip,shared_8_note_phrases=shared,
                        file=path.name if digest else None))
            results[train+'-'+position+'-'+prior] = dict(training_ids=list(selected),
                training_families=len({s['family'] for s in selected.values()}),
                metrics=metrics,candidates=candidates,wall_seconds=time.perf_counter()-start)
    report = dict(config=config,duplicate_checks=duplicate_checks,models=results,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        human_review='not performed',originality='not cleared; only exact transposed phrase screen')
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({n:dict(wall_seconds=r['wall_seconds'],samples=len(r['candidates'])) for n,r in results.items()}))


if __name__ == '__main__':
    main()

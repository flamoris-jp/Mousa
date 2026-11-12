"""Post-hoc event-order texture descriptors, not voice or musical-quality labels."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from mousa.overlap_midi import read_midi


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def describe(notes):
    if not 1 <= len(notes) <= 100000:
        raise ValueError('bounded nonempty note sequence required')
    strata = {k: dict(transitions=0, absolute_interval_sum=0, repeated_pitch=0,
                      above_octave=0) for k in ('simultaneous_onset', 'later_onset')}
    for before, after in zip(notes, notes[1:]):
        if after.start < before.start:
            raise ValueError('onset order required')
        interval = abs(after.pitch-before.pitch)
        row = strata['simultaneous_onset' if before.start == after.start else 'later_onset']
        row['transitions'] += 1
        row['absolute_interval_sum'] += interval
        row['repeated_pitch'] += interval == 0
        row['above_octave'] += interval > 12
    for row in strata.values():
        n = row['transitions']
        row['mean_absolute_interval'] = row['absolute_interval_sum']/n if n else None
    starts = Counter(note.start for note in notes)
    return dict(notes=len(notes), pitch_transitions=max(0, len(notes)-1),
                distinct_onsets=len(starts), max_notes_sharing_onset=max(starts.values()),
                initial_delta_zero=notes[0].start == 0, strata=strata)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ('corpus', 'extra', 'additions-root', 'assignment', 'output'):
        p.add_argument('--'+key, type=Path, required=True)
    a = p.parse_args(); root = Path(__file__).resolve().parents[1]
    if a.output.exists():
        raise ValueError('new output required')
    manifest = json.loads((root/'datasets/research-exploratory-multifamily-20261112.json').read_text())
    assignment = json.loads(a.assignment.read_text())
    sources = [(w['work_id'], a.corpus/w['file'], w['track_index'], w['sha256'])
               for w in manifest['works'] if w['split'] == 'train']
    sources.append(('mutopia-583', a.extra, 1, '631bcd481e09c1493191959ec3264c3513c4a93177ffc6d833dea4f4952b659b'))
    for w in assignment['additions']:
        f = (a.additions_root/w['file']).resolve()
        if not f.is_relative_to(a.additions_root.resolve()):
            raise ValueError('source outside approved root')
        sources.append((w['work_id'], f, w['track'], w['sha256']))
    if len(sources) != 12 or len({w for w,_,_,_ in sources}) != 12:
        raise ValueError('fixed twelve-work inventory required')
    a.output.mkdir(parents=True)
    plan = dict(created_at_utc=datetime.now(timezone.utc).isoformat(),
                scope='Post-hoc descriptive audit motivated by observed leap/overlap increase; not unseen hypothesis test',
                assignment_sha256=digest(a.assignment), source_sha256={w:sha for w,_,_,sha in sources},
                code_sha256=digest(Path(__file__)), metric='Absolute adjacent-event pitch interval, grouped by equal versus later onset; source reader order unchanged',
                limits='Same-onset events are not melodic succession; later-onset event order is not identified voice-leading. No aesthetic or causal conclusion.')
    (a.output/'plan.json').write_text(json.dumps(plan, indent=2)+'\n')
    rows=[]
    for work,path,track,sha in sources:
        if digest(path) != sha:
            raise ValueError('original source hash changed')
        music = read_midi(path, track)
        rows.append(dict(work_id=work, source_sha256=sha, track=track, **describe(music.notes)))
    total = {k: {f:sum(r['strata'][k][f] for r in rows)
                 for f in ('transitions','absolute_interval_sum','repeated_pitch','above_octave')}
             for k in ('simultaneous_onset','later_onset')}
    report = dict(plan_sha256=digest(a.output/'plan.json'), rows=rows, totals=total,
                  total_notes=sum(r['notes'] for r in rows), total_transitions=sum(r['pitch_transitions'] for r in rows),
                  originals_unchanged=all(digest(path)==sha for _,path,_,sha in sources),
                  no_model_fit_or_score=True, no_new_labels=True)
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(total,indent=2))


if __name__ == '__main__':
    main()

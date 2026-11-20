"""Posthoc structural audit of previously generated private Cycle34 candidates."""
import argparse
import hashlib
import json
from pathlib import Path
from mousa.tick_midi import TickNote
from mousa.group_structure import describe


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(directory, results_path):
    report=json.loads(results_path.read_text())
    rows=[]
    for arm,condition in report['conditions'].items():
        for row in condition['outputs']:
            path=directory/f"{arm}-{row['seed']}-private.json"
            if digest(path)!=row['private_sha256']:
                raise ValueError('private candidate hash mismatch')
            data=json.loads(path.read_text())
            notes=tuple(TickNote(**n) for n in data['notes'])
            rows.append(dict(arm=arm,seed=row['seed'],status=row['status'],candidate_sha256=digest(path),
                             structure=describe(notes,row['target_ticks'],ppq=384)))
    return dict(scope='Posthoc descriptive audit; previously generated candidates, not new generation or human evaluation.',
                results_sha256=digest(results_path),ppq=384,rows=rows,
                limitations=['Minimum pitch is not a true melodic/bass voice or harmonic role.',
                             'One/two quarter-note silence thresholds are arbitrary analytic conventions, not phrase labels.',
                             'Rests may separate gestures, but phrases may have no rests; no recall/precision without human labels.',
                             'Whole simultaneous groups and all notes remain unchanged. No new fitting or source admission.'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('results',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args()
    if a.output.exists():p.error('new output required')
    a.output.write_text(json.dumps(audit(a.directory,a.results),indent=2)+'\n')

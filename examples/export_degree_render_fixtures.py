"""Deterministic ordinal transport checks; no model or learning required."""
import argparse
import hashlib
import json
from pathlib import Path

from mousa import Degree, Key, ScaleCondition, load_catalogue
from mousa.degree_generation import render_generated


def export(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False);entries=[]
    for scale in load_catalogue().values():
        n=len(scale.intervals_cents)
        labels=[Degree(0,-1).label,Degree(0).label,Degree(1).label,
                Degree(n-1).label,Degree(2).label,Degree(0,1).label]
        condition=ScaleCondition(scale,Key(60,33.333,442))
        midi,metadata=render_generated(labels,condition)
        name=scale.scale_id
        (output/(name+'.mid')).write_bytes(midi)
        text=json.dumps(metadata,ensure_ascii=False,indent=2)+'\n'
        (output/(name+'.json')).write_text(text,encoding='utf-8')
        entries.append({'midi':name+'.mid','metadata':name+'.json',
                        'midi_sha256':metadata['midi_sha256'],
                        'metadata_sha256':hashlib.sha256(text.encode()).hexdigest(),
                        'condition':condition.to_dict()})
    (output/'manifest.json').write_text(json.dumps({'files':entries},indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
    export(p.parse_args().out)

"""Fixed-support timing comparison and constrained generation, not appeal labels."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from mousa.overlap_midi import read_midi,write_midi,OverlapMelody
from mousa.tick_midi import TickNote
from mousa.research_intake import validate_manifest
from mousa.onset_gate_model import OnsetGateModel


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def pairs(m):
    previous=0;result=[]
    for n in m.notes:
        dt=Fraction((n.start-previous)*384,m.ppq);gate=Fraction((n.end-n.start)*384,m.ppq)
        if dt.denominator!=1 or gate.denominator!=1:raise ValueError('incompatible fixed PPQ, no rounding')
        result.append((int(dt),int(gate)));previous=n.start
    return result

def intervals(pitches):return [b-a for a,b in zip(pitches,pitches[1:])]
def phrases(pitches):
    iv=intervals(pitches);return {tuple(iv[i:i+7]) for i in range(len(iv)-6)}

def similarity(a,b):
    a,b=intervals(a),intervals(b)
    if max(len(a),len(b))>512:raise ValueError('screen bound')
    row=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        new=[i]
        for j,y in enumerate(b,1):new.append(min(new[-1]+1,row[j]+1,row[j-1]+(x!=y)))
        row=new
    return 1-row[-1]/max(len(a),len(b)) if a and b else None

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('corpus','source','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();root=Path(__file__).resolve().parents[1]
    if a.output.exists():raise ValueError('new output required')
    plan=root/'experiments/2026-11-12-onset-gate-plan.json'
    manifest=json.loads((root/'datasets/research-exploratory-multifamily-20261112.json').read_text());validate_manifest(manifest,a.corpus)
    train=[];sources={};hashes={}
    for w in manifest['works']:
        if w['work_id'] not in ('mutopia-376','mutopia-888','mutopia-889','mutopia-789'):continue
        m=read_midi(a.corpus/w['file'],w['track_index']);train+=pairs(m);sources[w['work_id']]=[n.pitch for n in m.notes];hashes[w['work_id']]=digest(a.corpus/w['file'])
    if len(sources)!=4:raise ValueError('frozen train ids missing')
    expected='dcd5efac22b5e91b7c87685058784396adb9ec5d69915764265ad68158dbb6e1'
    if digest(a.source)!=expected:raise ValueError('reviewed580 digest differs')
    rights=json.loads((root/'datasets/research-brahms580-rights-20261112.json').read_text())
    if rights['encoding_rights']['status']!='PD-dedication-supported':raise ValueError('rights evidence absent')
    test=read_midi(a.source,1);testp=[n.pitch for n in test.notes];screens=[]
    for name,pitch in sources.items():
        match=len(phrases(pitch)&phrases(testp));near=similarity(pitch,testp)
        screens.append(dict(train=name,exact8_pitch_interval_matches=match,whole_interval_similarity=near))
        if match or (near is not None and near>=.80):raise ValueError('source similarity needs review before scoring')
    # Freeze plan, sources and driver before evaluation; no tuning afterward.
    a.output.mkdir(parents=True)
    before=dict(plan_sha256=digest(plan),train_sha256=hashes,test_sha256=expected,screen=screens,
        model_sha256=digest(root/'src/mousa/onset_gate_model.py'),driver_sha256=digest(Path(__file__)))
    (a.output/'before-scoring.json').write_text(json.dumps(before,indent=2)+'\n')
    testpairs=pairs(test);forbidden={p for notes in sources.values() for p in phrases(notes)}
    # Evaluation-only reference also participates in output copying rejection,
    # never fitting or model/pitch selection. Report that distinction explicitly.
    forbidden|=phrases(testp)
    pitches=sorted({p for notes in sources.values() for p in notes});models={}
    for name,factorized in [('joint',False),('factorized',True)]:
        model=OnsetGateModel(train,factorized=factorized)
        evaluation=model.evaluate(testpairs);outputs=[]
        for seed in range(10):
            generated=model.generate(seed,target_ticks=9216,pitches=pitches)
            row={k:v for k,v in generated.items() if k!='notes'};row['seed']=seed;row['attempted_note_count']=len(generated['notes'])
            if generated['status']=='complete':
                ns=generated['notes'];notes=tuple(sorted((TickNote(n['start'],n['end'],n['pitch'],80,0) for n in ns),key=lambda n:(n.start,n.end,n.pitch)))
                match=len(phrases([n.pitch for n in notes])&forbidden)
                row['source_8_onset_interval_matches']=match
                if match:row['status']='copy_guard_blocked'
                else:
                    m=OverlapMelody(notes,9216,(6,8),ppq=384);path=a.output/f'{name}-{seed}.mid';write_midi(m,path)
                    assert read_midi(path,1)==m
                    overlaps=sum(any(p.end>n.start for p in notes[:i]) for i,n in enumerate(notes))
                    row.update(overlapping_onsets=overlaps,notes_count=len(notes),distinct_pitches=len({n.pitch for n in notes}),midi_sha256=digest(path),exact_roundtrip=True)
            outputs.append(row)
        models[name]=dict(evaluation=evaluation,outputs=outputs)
    report=dict(before_scoring=before,training_events=len(train),test_events=len(testpairs),models=models,
        test_support=dict(in_support=len(testpairs),unsupported=0,seen_joint_pairs=sum(p in set(train) for p in testpairs),seen_deltas=sum(p[0] in {x[0] for x in train} for p in testpairs),seen_gates=sum(p[1] in {x[1] for x in train} for p in testpairs)),
        scope='Timing-pair predictive comparison, one representation-inspected newcomposer/contributor family; no broad or musicalquality claim',
        status='580 now predictive-observed; never relabel fresh. No fitting on580or583.',
        limitations=['No pitch predictive likelihood or learned phrase structure.','Generation pitches sampled from train support, not coherent pitch model.',
        '580 used only for postgeneration copying rejection, not fitting or tuning.','Copy screen is exact8onset intervals and wholeinterval edit, not perceptual/legalclearance.',
        'NLLtasks differ from previous REST/HOLD event reports; do not directlycompare them.'])
    (a.output/'report.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
    print(json.dumps({n:dict(evaluation=v['evaluation'],statuses=[r['status'] for r in v['outputs']]) for n,v in models.items()},default=str))
if __name__=='__main__':main()

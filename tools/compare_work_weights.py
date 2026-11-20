"""Predeclared exact weighting diagnostic on observed640/921; no selection."""
import argparse
from datetime import datetime,timezone
from fractions import Fraction
import json
from pathlib import Path
from statistics import mean
from mousa.weighted_timing_diagnostic import WeightedTimingDiagnostic
from mousa.overlap_midi import read_midi
from mousa.research_intake import validate_manifest
from compare_context_onset_gate import digest
from compare_onset_gate_models import pairs
from compare_cornelius_augmentation import EXTRA_SHA,TARGETS,validate_roles


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('corpus','cornelius','adam','chopin','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();root=Path(__file__).resolve().parents[1]
    if a.output.exists():raise ValueError('new output required')
    manifest=json.loads((root/'datasets/research-exploratory-multifamily-20261112.json').read_text());validate_manifest(manifest,a.corpus)
    assignment=json.loads((root/'datasets/research-cornelius583-training-assignment.json').read_text());validate_roles(assignment)
    if digest(a.cornelius)!=EXTRA_SHA:raise ValueError('extra bytes changed')
    paths={'640':a.adam,'921':a.chopin}
    for w,(sha,_) in TARGETS.items():
        if digest(paths[w])!=sha:raise ValueError('observed source changed')
    old=[pairs(read_midi(a.corpus/w['file'],w['track_index'])) for w in manifest['works'] if w['split']=='train']
    extra=pairs(read_midi(a.cornelius,1));aug=old+[extra]
    if list(map(len,old))!=[159,38,47,120] or len(extra)!=80:raise ValueError('fixed training lengths changed')
    conditions={
        'raw_old4':(old,[Fraction(1)]*4),
        'raw_augmented5':(aug,[Fraction(1)]*5),
        'mass364_augmented5':(aug,[Fraction(364,444)]*5),
        'equal_work_mass364_old4':(old,[Fraction(364,4*len(s)) for s in old]),
        'equal_work_mass364_augmented5':(aug,[Fraction(364,5*len(s)) for s in aug]),
    }
    tracked=['src/mousa/weighted_timing_diagnostic.py','tools/compare_work_weights.py','tools/compare_cornelius_augmentation.py',
             'src/mousa/onset_gate_model.py','src/mousa/overlap_midi.py','tools/compare_onset_gate_models.py',
             'datasets/research-exploratory-multifamily-20261112.json','datasets/research-cornelius583-training-assignment.json']
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),scope='Exploratory weighting diagnostic, all640/921alreadyobserved',
        conditions={n:dict(events=list(map(len,s)),per_event_weights=[str(w) for w in weights]) for n,(s,weights) in conditions.items()},
        methods=['factorized','contextk4'],support='Unchanged PPQ384 pair support and marginalprior1; exact Fractioncounts',
        hypotheses='Distinguish overallcountmass from equal-work weighting, without tuning weights to outcomes',
        limits=['Weights alter effectiveprior and contexts relative tok4; fixedtotalmass isnot pure causalcontent control.',
                'Equalwork isnot equalgenre/family;888889remain correlated.',
                'No generation implementation for fractionalweights; allconditions reported, no winneradopted.',
                '580excluded because583related; no freshholdout claim.'],
        code_sha256={f:digest(root/f) for f in tracked},extra_sha256=EXTRA_SHA,
        source_sha256={w:sha for w,(sha,_) in TARGETS.items()})
    a.output.mkdir();(a.output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    probes={w:pairs(read_midi(paths[w],track)) for w,(_,track) in TARGETS.items()};rows={}
    for name,(seqs,weights) in conditions.items():
        scores={}
        for context in (False,True):
            model=WeightedTimingDiagnostic(seqs,weights,context=context)
            result={w:model.evaluate(seq) for w,seq in probes.items()}
            scores['contextk4' if context else 'factorized']=dict(works=result,equal_work_nll=mean(r['nll_per_event'] for r in result.values()),weighted_mass=str(model.mass))
        rows[name]=scores
    result=dict(plan=plan,conditions=rows,no_model_selection=True,no_generation=True,no_new_training_sources=True)
    (a.output/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({n:{k:v['equal_work_nll'] for k,v in r.items()} for n,r in rows.items()},indent=2))
if __name__=='__main__':main()

"""Fixed60-event prefix composition contrast, observed diagnostics only."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
from statistics import mean
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.onset_gate_model import OnsetGateModel
from mousa.overlap_midi import read_midi
from mousa.research_intake import validate_manifest
from compare_context_onset_gate import digest
from compare_onset_gate_models import pairs
from compare_training_quantity import TARGETS

ALLOCATIONS = {
    'family376': {'mutopia-376':60},
    'family888889': {'mutopia-888':30,'mutopia-889':30},
    'family789': {'mutopia-789':60},
    'balanced_three_families': {'mutopia-376':20,'mutopia-888':10,'mutopia-889':10,'mutopia-789':20},
}


def prefixes(training, allocation):
    seqs=[];pss=[]
    for work,count in allocation.items():
        melody=training[work]
        if len(melody.notes)<count:raise ValueError('insufficient prefix; no replacement')
        seqs.append(pairs(melody)[:count]);pss.append([n.pitch for n in melody.notes[:count]])
    return seqs,pss


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('corpus','brahms','adam','output'):parser.add_argument('--'+key,type=Path,required=True)
    a=parser.parse_args();root=Path(__file__).resolve().parents[1]
    if a.output.exists():raise ValueError('new output required')
    manifest=json.loads((root/'datasets/research-exploratory-multifamily-20261112.json').read_text())
    validate_manifest(manifest,a.corpus)
    sources={w['work_id']:w for w in manifest['works'] if w['split']=='train'}
    expected=set().union(*(set(x) for x in ALLOCATIONS.values()))
    if set(sources)!=expected:raise ValueError('fixed corpus changed')
    paths={'580':a.brahms,'640':a.adam}
    for w,(sha,_) in TARGETS.items():
        if digest(paths[w])!=sha:raise ValueError('observed diagnostic bytes changed')
    tracked=['tools/compare_fixed_event_budget.py','tools/compare_training_quantity.py',
             'tools/compare_onset_gate_models.py','src/mousa/onset_gate_model.py','src/mousa/context_onset_gate.py',
             'src/mousa/overlap_midi.py','datasets/research-exploratory-multifamily-20261112.json']
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),scope='Exploratory fixed60-event composition contrast;580/640 already observed',
        allocations=ALLOCATIONS,models=['factorized','previous_gate_context_k4'],
        support='UnchangedPPQ384delta0..12288gate1..12288,prior1,contextk4',
        sampling='FirstNoriginal onset/gate events perwork; original order and firstdelta retained; context reset at every work. No synthetic joins, no replacement, no source rewrites.',
        grouping='888and889 remain samefamily; both always included together. Reserved/pending sources excluded.',
        purpose='Hold totaltraining events at60; compare composition/family mix, not a causal effect of diversity.',
        limits=['Prefix bias and worklength differ; this isnotrandomsampling or stylebalanced calibration.',
                'Work-boundary counts1/2/1/4 change available withinwork transitions.',
                'Balancedmix gives fewer observations perwork, not an equivalent larger corpus.',
                'No newholdout/selection/humanappeal inference; outcomes do not modify allocation.'],
        code_sha256={p:digest(root/p) for p in tracked},
        train_sha256={w:digest(a.corpus/s['file']) for w,s in sources.items()},
        diagnostic_sha256={w:sha for w,(sha,_) in TARGETS.items()})
    a.output.mkdir();(a.output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    training={w:read_midi(a.corpus/s['file'],s['track_index']) for w,s in sources.items()}
    probes={w:pairs(read_midi(paths[w],track)) for w,(_,track) in TARGETS.items()}
    rows={}
    for name,allocation in ALLOCATIONS.items():
        seqs,pss=prefixes(training,allocation);flat=[p for seq in seqs for p in seq]
        if len(flat)!=60:raise ValueError('event budget differs')
        models={'factorized':OnsetGateModel(flat,factorized=True),
                'previous_gate_context_k4':ContextOnsetGateModel(seqs,pss,timing_context=True,pitch_continuity=True,strength=4)}
        scores={}
        for model_name,model in models.items():
            works={w:model.evaluate(probe) for w,probe in probes.items()}
            scores[model_name]=dict(works=works,equal_work_nll=mean(s['nll_per_event'] for s in works.values()))
        rows[name]=dict(work_event_counts=allocation,total_events=len(flat),work_count=len(seqs),
                        within_work_transition_count=sum(len(seq)-1 for seq in seqs),models=scores)
    result=dict(plan=plan,conditions=rows,originals_unchanged=all(digest(paths[w])==sha for w,(sha,_) in TARGETS.items()),
                note='Allconditions reported; no newmodelselected, no training source added, no generatedmedia.')
    (a.output/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({n:{m:s['equal_work_nll'] for m,s in r['models'].items()} for n,r in rows.items()},indent=2))

if __name__=='__main__':main()

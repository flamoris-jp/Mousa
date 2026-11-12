"""Exhaustive tiny family-count curve on observed diagnostics, never fresh tests."""
import argparse
from datetime import datetime, timezone
from itertools import combinations
import json
from pathlib import Path
from statistics import mean
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.onset_gate_model import OnsetGateModel
from mousa.overlap_midi import read_midi
from mousa.research_intake import validate_manifest
from compare_context_onset_gate import digest
from compare_onset_gate_models import pairs

FAMILIES = (('mutopia-376',), ('mutopia-888', 'mutopia-889'), ('mutopia-789',))
TARGETS = {'580': ('dcd5efac22b5e91b7c87685058784396adb9ec5d69915764265ad68158dbb6e1', 1),
           '640': ('13ec851eb00ca9aba345cad50f03bdb3b189f566f38d094a1e6b839765b3d678', 2)}


def subsets():
    return [(n, indexes, tuple(work for i in indexes for work in FAMILIES[i]))
            for n in (1, 2, 3) for indexes in combinations(range(3), n)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('corpus', 'brahms', 'adam', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    a = parser.parse_args(); root = Path(__file__).resolve().parents[1]
    if a.output.exists(): raise ValueError('new output required')
    manifest_path = root/'datasets/research-exploratory-multifamily-20261112.json'
    manifest = json.loads(manifest_path.read_text()); validate_manifest(manifest, a.corpus)
    sources = {w['work_id']: w for w in manifest['works'] if w['split']=='train'}
    if set(sources) != {w for f in FAMILIES for w in f}: raise ValueError('fixed train membership changed')
    paths = {'580': a.brahms, '640': a.adam}
    for name, (sha, track) in TARGETS.items():
        if digest(paths[name]) != sha: raise ValueError('observed diagnostic changed')
    tracked = ('tools/compare_training_quantity.py','src/mousa/context_onset_gate.py',
               'src/mousa/onset_gate_model.py','src/mousa/overlap_midi.py',
               'tools/compare_onset_gate_models.py','datasets/research-exploratory-multifamily-20261112.json')
    plan = dict(created_at_utc=datetime.now(timezone.utc).isoformat(),
        scope='Exploratory quantity curve;580and640 already predictively observed, never fresh again',
        families=FAMILIES,subsets=subsets(),models=['factorized','previous_gate_context_k4'],
        fixed_support='PPQ384,delta0..12288,gate1..12288; prior1 per marginal; contextk4',
        fixed_controls='Same model parameters/support/task; no transposition, augmentation, resampling, tuning or generation',
        training='Only existing rights-reviewed4works/3conservativefamilies;888/889inseparable',
        diagnostics='Report both observed works separately plus equal-work NLL mean; no modelselection',
        aggregate='Equal subset mean at each familycount; disclose work/event totals and every subset. Not independent replications.',
        quantity_caveat='Familycount, workcount, eventcount and content change together; no isolated sample-size causality',
        resources='14smallCPUmodel fits,28diagnostic evaluations; no GPU/fees/downloads',
        train_sha256={w:digest(a.corpus/sources[w]['file']) for w in sources},
        diagnostic_sha256={w:sha for w,(sha,_) in TARGETS.items()},
        code_sha256={p:digest(root/p) for p in tracked})
    a.output.mkdir(); (a.output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    # All predictive calls below occur only after plan persistence.
    training = {w:read_midi(a.corpus/s['file'],s['track_index']) for w,s in sources.items()}
    diagnostics = {w:pairs(read_midi(paths[w],track)) for w,(_,track) in TARGETS.items()}
    rows=[]
    for count,indexes,works in subsets():
        seqs=[pairs(training[w]) for w in works]
        pss=[[n.pitch for n in training[w].notes] for w in works]
        flat=[x for seq in seqs for x in seq]
        models={'factorized':OnsetGateModel(flat,factorized=True),
                'previous_gate_context_k4':ContextOnsetGateModel(seqs,pss,timing_context=True,pitch_continuity=True,strength=4)}
        results={}
        for name,model in models.items():
            scores={w:model.evaluate(probe) for w,probe in diagnostics.items()}
            results[name]=dict(works=scores,equal_work_nll=mean(s['nll_per_event'] for s in scores.values()))
        rows.append(dict(family_count=count,family_indexes=indexes,work_ids=works,work_count=len(works),
                         training_events=len(flat),models=results))
    summaries=[]
    for count in (1,2,3):
        selected=[r for r in rows if r['family_count']==count]
        summaries.append(dict(family_count=count,subset_count=len(selected),
            event_counts=[r['training_events'] for r in selected],work_counts=[r['work_count'] for r in selected],
            models={name:dict(mean_equal_work_nll=mean(r['models'][name]['equal_work_nll'] for r in selected),
                             per_subset_equal_work_nll=[r['models'][name]['equal_work_nll'] for r in selected])
                    for name in ('factorized','previous_gate_context_k4')}))
    report=dict(plan=plan,rows=rows,summaries=summaries,
        unchanged=all(digest(paths[w])==sha for w,(sha,_) in TARGETS.items()),
        limits=['Only4works/3families, not large-scale learning.',
                'Observed diagnostics informed earlier research; no sealed generalization claim.',
                'More events and different content confounded; subset observations dependent.',
                'Timing likelihood only, not pitch/harmony/attractiveness or originality.'])
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(summaries,indent=2))

if __name__=='__main__': main()

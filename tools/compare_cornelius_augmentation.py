"""Explicit single-pitch source augmentation; exclude related580 from evaluation."""
import argparse
from datetime import datetime,timezone
from fractions import Fraction
import json
from pathlib import Path
from statistics import mean
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.onset_gate_model import OnsetGateModel
from mousa.overlap_midi import read_midi
from mousa.optimized_feasible_generation import generate_optimized
from mousa.research_intake import validate_manifest
from compare_context_onset_gate import digest,metrics,summarize
from compare_onset_gate_models import pairs,phrases,similarity

EXTRA_SHA='631bcd481e09c1493191959ec3264c3513c4a93177ffc6d833dea4f4952b659b'
TARGETS={'640':('13ec851eb00ca9aba345cad50f03bdb3b189f566f38d094a1e6b839765b3d678',2),
         '921':('b19f8e0d783915e80e33cc4f622ef9623994ab89f114a53983c3f628265b798b',1)}


def validate_roles(assignment):
    if assignment['related_evaluation_exclusions']!=['mutopia-580']:
        raise ValueError('related family exclusion required')
    if set(assignment['diagnostic_ids'])!={'mutopia-640','mutopia-921'}:
        raise ValueError('only fixed observed diagnostics permitted')
    if assignment['source_sha256']!=EXTRA_SHA:raise ValueError('wrong augmented source')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('corpus','cornelius','adam','chopin','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();root=Path(__file__).resolve().parents[1]
    if a.output.exists():raise ValueError('new output required')
    manifest_path=root/'datasets/research-exploratory-multifamily-20261112.json'
    manifest=json.loads(manifest_path.read_text());validate_manifest(manifest,a.corpus)
    assignment_path=root/'datasets/research-cornelius583-training-assignment.json'
    assignment=json.loads(assignment_path.read_text());validate_roles(assignment)
    if digest(a.cornelius)!=EXTRA_SHA:raise ValueError('583 bytes changed')
    rights=json.loads((root/assignment['rights_evidence']).read_text())
    if rights['files'][1]['sha256']!=EXTRA_SHA or 'sufficient for local research' not in rights['recommendation']:
        raise ValueError('reviewed rights evidence absent')
    paths={'640':a.adam,'921':a.chopin}
    for w,(sha,_) in TARGETS.items():
        if digest(paths[w])!=sha:raise ValueError('diagnostic bytes changed')
    old={w['work_id']:read_midi(a.corpus/w['file'],w['track_index']) for w in manifest['works'] if w['split']=='train'}
    if set(old)!={'mutopia-376','mutopia-888','mutopia-889','mutopia-789'}:raise ValueError('old split changed')
    extra=read_midi(a.cornelius,1);targets={w:read_midi(paths[w],track) for w,(_,track) in TARGETS.items()}
    tracked=['tools/compare_cornelius_augmentation.py','src/mousa/context_onset_gate.py','src/mousa/onset_gate_model.py',
             'src/mousa/optimized_feasible_generation.py','src/mousa/feasible_context_generation.py',
             'tools/compare_context_onset_gate.py','tools/compare_onset_gate_models.py',
             'datasets/research-exploratory-multifamily-20261112.json','datasets/research-cornelius583-training-assignment.json',
             assignment['rights_evidence'],'src/mousa/overlap_midi.py']
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),scope='Exploratory4versus5work augmentation; no newsealedtest',
        old_train_ids=list(old),added='mutopia-583',excluded_related_evaluation=['580'],
        diagnostics=['640','921'],diagnostic_role='already observed, neverfresh; neverfit',
        models=['factorized','previous_gate_context_k4'],support='unchangedPPQ384delta0..12288gate1..12288priors1',
        generation='contextonly,seeds0..4,mix1/4,optimizedfeasible,tail384,target9216,max256notes; no outputselection',
        copy_guard='All5trainplus2diagnostics for BOTHconditions, generated andcanonicalorder, exact8interval; no retries',
        confounds=['Extra80events andsinglepitchcontent change together; familycount isnotgenrecount.',
                   'No baselineimprovement or appeal inferred from quantity alone; allfailures reported.'],
        code_sha256={k:digest(root/k) for k in tracked},extra_sha256=EXTRA_SHA,
        train_sha256={w['work_id']:digest(a.corpus/w['file']) for w in manifest['works'] if w['split']=='train'},
        target_sha256={w:sha for w,(sha,_) in TARGETS.items()})
    a.output.mkdir();(a.output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    screen=[]
    for w,target in targets.items():
        ps=[n.pitch for n in target.notes]
        for source,m in {**old,'mutopia-583':extra}.items():
            ref=[n.pitch for n in m.notes];exact=len(phrases(ref)&phrases(ps));near=similarity(ref,ps)
            screen.append(dict(source=source,target=w,exact8=exact,global_similarity=near,flagged=bool(exact or (near is not None and near>=.80))))
    (a.output/'before-fit-screen.json').write_text(json.dumps(screen,indent=2)+'\n')
    if any(r['flagged'] for r in screen):raise ValueError('crosssplit similarity blocks fitting')
    forbidden=set().union(*(phrases([n.pitch for n in m.notes]) for m in [*old.values(),extra,*targets.values()]))
    results={}
    for condition,music in [('old4',list(old.values())),('augmented5',[*old.values(),extra])]:
        seqs=[pairs(m) for m in music];pss=[[n.pitch for n in m.notes] for m in music];flat=[p for seq in seqs for p in seq]
        models={'factorized':OnsetGateModel(flat,factorized=True),
                'previous_gate_context_k4':ContextOnsetGateModel(seqs,pss,timing_context=True,pitch_continuity=True,strength=4)}
        prediction={}
        for name,model in models.items():
            scores={w:model.evaluate(pairs(m)) for w,m in targets.items()}
            prediction[name]=dict(works=scores,equal_work_nll=mean(s['nll_per_event'] for s in scores.values()))
        outputs=[]
        for seed in range(5):
            generated=generate_optimized(models['previous_gate_context_k4'],seed,uniform_mix=Fraction(1,4),trailing_rest_ticks=384)
            ns=generated['notes'];canonical=sorted(ns,key=lambda n:(n['start'],n['end'],n['pitch']))
            hits=len((phrases([n['pitch'] for n in ns])|phrases([n['pitch'] for n in canonical]))&forbidden)
            row={k:v for k,v in generated.items() if k!='notes'}
            row.update(seed=seed,metrics=metrics(ns,9216),copy_matches=hits)
            if hits:row['status']='copy_guard_blocked'
            # Generated symbolic notes remain private; report digests, not source material.
            f=a.output/f'{condition}-{seed}-notes.json';f.write_text(json.dumps(ns,sort_keys=True)+'\n')
            row['private_notes_sha256']=digest(f);outputs.append(row)
        means,denominators=summarize(outputs)
        results[condition]=dict(training_events=len(flat),work_count=len(music),pitch_vocabulary=len(models['previous_gate_context_k4'].vocabulary),
                               prediction=prediction,outputs=outputs,complete_only_means=means,metric_denominators=denominators)
    report=dict(plan=plan,screen=screen,conditions=results,
                source_state='583 now explicitlyused for exploratorytraining;580not evaluated;640/921remain observed anduntrained',
                originals_unchanged=digest(a.cornelius)==EXTRA_SHA and all(digest(paths[w])==sha for w,(sha,_) in TARGETS.items()),
                limitations=['Generation is structuraldiagnostic only, no MIDI/audio delivery or humanappeal claim.',
                            'No newindependenttest claim; future evaluation must keep583/580family together.'])
    (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({n:{'training_events':r['training_events'],'nll':{m:v['equal_work_nll'] for m,v in r['prediction'].items()},'statuses':[x['status'] for x in r['outputs']]} for n,r in results.items()},indent=2))

if __name__=='__main__':main()

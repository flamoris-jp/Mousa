"""Predeclared timing-count x pitch-count augmentation; observed diagnostics only."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import json
from pathlib import Path
from statistics import mean
from time import perf_counter
from mousa.separated_count_context import SeparatedCountContext
from mousa.overlap_midi import read_midi
from mousa.optimized_feasible_generation import generate_optimized
from compare_cornelius_augmentation import validate_roles, EXTRA_SHA, TARGETS
from compare_context_onset_gate import digest, metrics, summarize
from compare_onset_gate_models import pairs, phrases, similarity
from mousa.research_intake import validate_manifest


def run(root, corpus, extra_path, adam, chopin, output):
    if output.exists(): raise ValueError('new output required')
    old_report=json.loads((root/'experiments/2026-11-12-cornelius-augmentation-results.json').read_text())
    # Includes source assignment, rights evidence, frozen models, and intake helpers.
    prior=old_report['plan']
    for p,sha in prior['code_sha256'].items():
        if digest(root/p)!=sha: raise ValueError('previous frozen dependency changed')
    assignment=json.loads((root/'datasets/research-cornelius583-training-assignment.json').read_text())
    validate_roles(assignment)
    manifest=json.loads((root/'datasets/research-exploratory-multifamily-20261112.json').read_text())
    validate_manifest(manifest,corpus)
    old={}
    for w in manifest['works']:
        if w['work_id'] in prior['old_train_ids']:
            if digest(corpus/w['file'])!=prior['train_sha256'][w['work_id']]:raise ValueError('training bytes changed')
            old[w['work_id']]=read_midi(corpus/w['file'],w['track_index'])
    if set(old)!=set(prior['old_train_ids']):raise ValueError('training inventory changed')
    if digest(extra_path)!=EXTRA_SHA:raise ValueError('extra bytes changed')
    target_paths={'640':adam,'921':chopin}
    for w,(sha,track) in TARGETS.items():
        if digest(target_paths[w])!=sha:raise ValueError('target bytes changed')
    tracked=['src/mousa/separated_count_context.py','tools/compare_separated_augmentation.py',
             'tests/test_separated_count_context.py','experiments/2026-11-12-cornelius-augmentation-results.json']
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),scope='Exploratory pathway ablation; no fresh scores',
        design='2x2: add583 to timing counts off/on x add583 to pitch counts off/on; no work weighting or fractional counts',
        timing='Frozen context k4 global gate and previous-gate/delta counts. Pitch path cannot alter teacher-forced timing NLL.',
        pitch='Frozen unigram initial pitch and interval counts plus vocabulary. Includes all three changes, not isolated interval effect.',
        predictions='640/921 observed only, equal-work timing NLL;580 related family excluded',
        generation='Each cell seeds0..4; fixed optimized feasibility,mix1/4,tail384,target9216,max256notes. No selection or retry.',
        metrics='All statuses, copy checks, notes, overlap, active voices, repeats, distinct pitches, leaps, rest; elapsed wall time descriptive only.',
        copy_guard='All5 training plus640/921 exact8interval in onset sequence and canonical order for every condition.',
        interpretation='Neither vs both reproduce cycle23; cross cells probe count pathways, not proof of single-pitch causality or musical appeal. Quantity and source content remain confounded.',
        train_sha256=prior['train_sha256'],extra_sha256=EXTRA_SHA,target_sha256=prior['target_sha256'],
        code_sha256={**prior['code_sha256'],**{p:digest(root/p) for p in tracked}})
    output.mkdir(parents=True);(output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    extra=read_midi(extra_path,1);targets={w:read_midi(target_paths[w],track) for w,(_,track) in TARGETS.items()}
    all_train=[*old.values(),extra];screen=[]
    for w,m in targets.items():
        for source,ref in zip([*old,'mutopia-583'],all_train):
            rp=[n.pitch for n in ref.notes];tp=[n.pitch for n in m.notes]
            exact=len(phrases(rp)&phrases(tp));near=similarity(rp,tp)
            screen.append(dict(source=source,target=w,exact8=exact,similarity=near,flagged=bool(exact or near is not None and near>=.8)))
    (output/'prescreen.json').write_text(json.dumps(screen,indent=2)+'\n')
    if any(s['flagged'] for s in screen):raise ValueError('crosssplit screen blocked')
    forbidden=set().union(*(phrases([n.pitch for n in m.notes]) for m in [*all_train,*targets.values()]))
    conditions={}
    for t,p in ((False,False),(False,True),(True,False),(True,True)):
        name=f'timing{int(t)}_pitch{int(p)}';tm=all_train if t else list(old.values());pm=all_train if p else list(old.values())
        model=SeparatedCountContext([pairs(m) for m in tm],[[n.pitch for n in m.notes] for m in tm],
                                    [pairs(m) for m in pm],[[n.pitch for n in m.notes] for m in pm])
        scores={w:model.evaluate(pairs(m)) for w,m in targets.items()};outputs=[];started=perf_counter()
        for seed in range(5):
            generated=generate_optimized(model,seed,uniform_mix=Fraction(1,4),trailing_rest_ticks=384)
            ns=generated['notes'];canon=sorted(ns,key=lambda n:(n['start'],n['end'],n['pitch']))
            hits=len((phrases([n['pitch'] for n in ns])|phrases([n['pitch'] for n in canon]))&forbidden)
            row={k:v for k,v in generated.items() if k!='notes'};row.update(seed=seed,copy_matches=hits,metrics=metrics(ns,9216))
            if hits:row['status']='copy_guard_blocked'
            f=output/f'{name}-{seed}-notes.json';f.write_text(json.dumps(ns,sort_keys=True)+'\n');row['private_notes_sha256']=digest(f);outputs.append(row)
        elapsed=perf_counter()-started;means,denominators=summarize(outputs)
        conditions[name]=dict(timing_events=sum(len(m.notes) for m in tm),pitch_events=sum(len(m.notes) for m in pm),
            pitch_vocabulary=len(model.vocabulary),scores=scores,equal_work_nll=mean(s['nll_per_event'] for s in scores.values()),
            outputs=outputs,complete_only_means=means,metric_denominators=denominators,generation_wall_seconds=elapsed)
    # Frozen endpoint controls must match prior generation bytes and timing scores.
    for new,old_name in [('timing0_pitch0','old4'),('timing1_pitch1','augmented5')]:
        ref=old_report['conditions'][old_name];cur=conditions[new]
        assert cur['scores']==ref['prediction']['previous_gate_context_k4']['works']
        assert [r['private_notes_sha256'] for r in cur['outputs']]==[r['private_notes_sha256'] for r in ref['outputs']]
    report=dict(plan=plan,screen=screen,conditions=conditions,endpoint_controls_reproduce_cycle23=True,
                limitations=['Only observed diagnostics, no genre or attractiveness labels.','Timing prediction has no pitch likelihood; pitch-only NLL equality is architectural, not evidence pitch is useless.',
                             'Same-pitch source also changes pitch counts, vocabulary and work length; single-pitch causal effect not isolated.','Private JSON only, not MIDI/audio or verified human listening.'])
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({n:dict(nll=r['equal_work_nll'],statuses=[x['status'] for x in r['outputs']],means=r['complete_only_means']) for n,r in conditions.items()},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('corpus','cornelius','adam','chopin','output'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();run(Path(__file__).resolve().parents[1],a.corpus,a.cornelius,a.adam,a.chopin,a.output)

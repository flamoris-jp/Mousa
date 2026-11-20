"""Fixed source projection x weighting comparison; no true melody labels."""
import argparse
from datetime import datetime,timezone
from fractions import Fraction
import json
from pathlib import Path
from statistics import mean
from time import process_time
from types import SimpleNamespace
from compare_weighted_twelve import inputs
from compare_approved_expansion import digest
from compare_context_onset_gate import metrics,summarize
from compare_onset_gate_models import phrases
from evaluate_chopin921_transfer import timing_coverage
from mousa.onset_upper_projection import project_with_loss
from mousa.weighted_context_generation import WeightedContextModel,generate


def prepare(root,output):
    if output.exists():raise ValueError('new plan required')
    previous=json.loads((root/'experiments/2026-11-12-weighted-twelve-final-plan.json').read_text())
    for p,h in previous['frozen_hashes'].items():
        if digest(root/p)!=h:raise ValueError('previous frozen dependency changed')
    tracked=['src/mousa/onset_upper_projection.py','tools/compare_onset_projection.py','tests/test_onset_upper_projection.py',
             'experiments/2026-11-12-weighted-twelve-results.json']
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),scope='Exploratory deterministic projection, no human melody ground truth',
        conditions=['fullstaff_event_proportional','fullstaff_equal_work','onset_upper_event_proportional','onset_upper_equal_work'],
        projection='Per exact onset select highest pitch; ties longest gate then original index. Preserve note object, start/end/velocity. No gate clipping or monophony claim.',
        weighting='All4conditions weighted note mass3263. Event-proportional weight3263/retained_total; equalwork3263/(12*retained_work_notes). Fullstaff event-proportional equals raw1.',
        prediction='Contextk4 same640/921 originalstaff timing likelihood. Targets NOT projected; no semantic/pitch/true-melody evaluation.',
        generation='New cycle31 exactinteger sampler for ALL4conditions, seeds0..4,mix1/4,poly3,noactive samepitch,target9216,tail384,max256notes',
        cpu_limit_seconds=120,cpu_limit_scope='Global fixed-order process CPU check before bounded fits/scores/generation; no hardpreemption. Late skips not fair comparisons.',
        copy_guard='All ORIGINAL12training staffs plus640/921, generated andcanonical onset order exact8; no threshold change or retry',
        loss_metrics='Per-source droppednote count,summedgate length lost,union sounding coverage lost,overlap timeline,polyphony,rest; originalEOT unchanged',
        generation_metrics='notes,repeatedpitch,distinctpitch,meanabsinterval,octaveleaps,overlap,rest,failures,copyflags; completed-only denominators',
        confounds=['Projection changes vocabulary, transition counts and musical texture; massfixed does not hold localcontext support or k4 relationship fixed.',
                   'Upper note is not annotated melody; overlapping earlier onsets remain and inner/lower lines may be the salient voice.',
                   'Observed diagnostics and5RNGseeds, not independent work generalization or appeal.','No original edits, MIDI/audio output or human ratings.'],
        source_sha256=previous['source_sha256'],train_ids=previous['ordered_train_ids'],
        frozen_hashes={**previous['frozen_hashes'],**{p:digest(root/p) for p in tracked}})
    output.mkdir(parents=True);(output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')


def run(root,corpus,extra,source_root,targets,plan_dir,output):
    if output.exists():raise ValueError('new output required')
    plan=json.loads((plan_dir/'plan.json').read_text())
    for p,h in plan['frozen_hashes'].items():
        if digest(root/p)!=h:raise ValueError('frozen code changed')
    music,diag,sources,_,_=inputs(root,corpus,extra,source_root,targets)
    if sorted(sources.values())!=plan['source_sha256'] or list(music)!=plan['train_ids']:raise ValueError('source inventory changed')
    output.mkdir(parents=True);(output/'before-fit.json').write_text(json.dumps(dict(plan_sha256=digest(plan_dir/'plan.json')),indent=2)+'\n')
    projected={};losses={}
    for work,m in music.items():
        selected,loss=project_with_loss(m.notes,m.total_ticks);projected[work]=SimpleNamespace(notes=selected,ppq=m.ppq,total_ticks=m.total_ticks);losses[work]=loss
    (output/'projection-loss.json').write_text(json.dumps(losses,indent=2)+'\n')
    forbidden=set().union(*(phrases([n.pitch for n in m.notes]) for m in [*music.values(),*diag.values()]))
    started=process_time();results={}
    for name in plan['conditions']:
        material=projected if name.startswith('onset_upper') else music;lengths=[len(m.notes) for m in material.values()];total=sum(lengths)
        ws=[Fraction(3263,12*n) for n in lengths] if name.endswith('equal_work') else [Fraction(3263,total)]*12
        if process_time()-started>=120:results[name]=dict(status='cpu_budget_skipped');continue
        seqs=[]
        for m in material.values():
            coverage,seq=timing_coverage(m)
            if coverage['unsupported_events']:raise ValueError('projection outside fixed support; no quantization')
            seqs.append(seq)
        model=WeightedContextModel(seqs,[[n.pitch for n in m.notes] for m in material.values()],ws)
        scores={}
        for work,m in diag.items():
            if process_time()-started>=120:scores[work]=dict(status='cpu_budget_skipped')
            else:scores[work]=model.evaluate(timing_coverage(m)[1])
        outputs=[]
        for seed in range(5):
            if process_time()-started>=120:outputs.append(dict(seed=seed,status='cpu_budget_skipped'));continue
            try:g=generate(model,seed)
            except ValueError as e:outputs.append(dict(seed=seed,status='resource_or_validation_rejected',reason=str(e)));continue
            ns=g.pop('notes');canonical=sorted(ns,key=lambda n:(n['start'],n['end'],n['pitch']))
            hits=len((phrases([n['pitch'] for n in ns])|phrases([n['pitch'] for n in canonical]))&forbidden)
            if hits:g['status']='copy_guard_blocked'
            f=output/f'{name}-{seed}-notes.json';f.write_text(json.dumps(ns,sort_keys=True)+'\n')
            g.update(seed=seed,metrics=metrics(ns,9216),copy_matches=hits,private_notes_sha256=digest(f));outputs.append(g)
        means,denominators=summarize(outputs)
        results[name]=dict(retained_notes=total,unweighted_transitions=sum(n-1 for n in lengths),weighted_note_mass=str(model.weighted_mass),
            weighted_transition_mass=str(sum(model.intervals.values())),vocabulary=list(model.vocabulary),weights=[str(w) for w in ws],
            prediction=scores,equal_work_nll=mean(v['nll_per_event'] for v in scores.values()) if all('nll_per_event' in v for v in scores.values()) else None,
            outputs=outputs,complete_only_means=means,metric_denominators=denominators)
    report=dict(plan_sha256=digest(plan_dir/'plan.json'),projection_loss=losses,conditions=results,cpu_seconds=process_time()-started,
                originals_unchanged=all(digest(Path(p))==h for p,h in sources.items()),limitations=plan['confounds'])
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',choices=['prepare','run'],required=True);p.add_argument('--plan-dir',type=Path,required=True)
    for k in ('corpus','extra','source-root','adam','chopin','output'):p.add_argument('--'+k,type=Path)
    a=p.parse_args();root=Path(__file__).resolve().parents[1]
    if a.stage=='prepare':prepare(root,a.plan_dir)
    else:
        if any(getattr(a,k) is None for k in ('corpus','extra','source_root','adam','chopin','output')):p.error('run requires all source/output paths')
        r=run(root,a.corpus,a.extra,a.source_root,{'640':a.adam,'921':a.chopin},a.plan_dir,a.output)
        print(json.dumps({n:dict(nll=v.get('equal_work_nll'),metrics=v.get('complete_only_means'),statuses=[r['status'] for r in v.get('outputs',[])]) for n,v in r['conditions'].items()},indent=2))

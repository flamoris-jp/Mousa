"""Fixed-mass exact weighting experiment; actual fit requires bound parent review."""
import argparse
from datetime import datetime,timezone
from fractions import Fraction
import json
from pathlib import Path
from statistics import mean
from time import process_time
from mousa.weighted_context_generation import WeightedContextModel,generate
from mousa.weighted_timing_diagnostic import WeightedTimingDiagnostic
from evaluate_chopin921_transfer import timing_coverage
from compare_approved_expansion import read_inputs,digest
from compare_onset_gate_models import phrases
from compare_context_onset_gate import metrics,summarize

ASSIGNMENT='datasets/research-cycle30-twelve-work-assignment.json'


def weight_sets(ids,lengths,groups):
    if len(ids)!=12 or len(lengths)!=12 or sum(lengths)!=3263 or len(groups)!=9:raise ValueError('fixed12 inventory required')
    flat=[w for members in groups.values() for w in members]
    if sorted(flat)!=sorted(ids) or len(set(flat))!=12:raise ValueError('one declared family per work required')
    by_id=dict(zip(ids,lengths));family_mass={w:sum(by_id[k] for k in members) for members in groups.values() for w in members}
    weights={'raw':[Fraction(1)]*12,'equal_work':[Fraction(3263,12*n) for n in lengths],
             'equal_declared_family':[Fraction(3263,9*family_mass[w]) for w in ids]}
    if any(sum(w*n for w,n in zip(values,lengths))!=3263 for values in weights.values()):raise AssertionError('mass differs')
    return weights


def inputs(root,corpus,extra,source_root,targets):
    assignment=json.loads((root/ASSIGNMENT).read_text())
    base,added,diag,sources,frozen=read_inputs(root,corpus,extra,source_root,assignment,targets)
    music={**base,**added}
    if len(music)!=12:raise ValueError('expected12works')
    weights=weight_sets(list(music),[len(m.notes) for m in music.values()],assignment['family_groups'])
    return music,diag,sources,frozen,weights


def prepare(root,corpus,extra,source_root,targets,plan_dir):
    if plan_dir.exists():raise ValueError('new plan required')
    music,diag,sources,frozen,weights=inputs(root,corpus,extra,source_root,targets)
    prior=json.loads((root/'experiments/2026-11-12-twelve-work-expansion-plan.json').read_text())
    for p,sha in prior['frozen_hashes'].items():
        if digest(root/p)!=sha:raise ValueError('prior source profile changed')
    if sorted(sources.values())!=prior['source_sha256']:raise ValueError('inventory changed')
    tracked=['src/mousa/weighted_context_generation.py','src/mousa/weighted_timing_diagnostic.py',
             'tools/compare_weighted_twelve.py','tests/test_weighted_context_generation.py',ASSIGNMENT,
             'experiments/2026-11-12-twelve-work-expansion-results.json','experiments/2026-11-12-twelve-work-expansion-screen.json']
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),scope='Observed640/921diagnostics and new exact-sampler generation, no fresh evaluation',
        weights={k:[str(w) for w in v] for k,v in weights.items()},ordered_train_ids=list(music),
        note_counts=[len(m.notes) for m in music.values()],total_weighted_note_mass=3263,
        family_policy='9declaredgroups. Equal family mass3263/9, each member same per-event weight within family; longer works contribute more within family. Not contributor equality.',
        conditions=['raw','equal_work','equal_declared_family'],prediction='Factorized and contextk4, same PPQ384 support/prior1; teacherforced timing only',
        generation='ALLconditions new exact integer pitch RNG, seeds0..4,mix1/4,wholejoint feasibility,max3voices,noactive samepitch,target9216,tail384,max256notes',
        raw_control='Raw probabilities match frozenmodel; new RNG pitch algorithm means historical output bytes/metrics NOT control. Rerun raw alongside weighted.',
        constraints='ExactFraction counts; weightsdenominator<=1e6; sampling integer bitlength<=2048. Explicit failure if exceeded. No corpus replication/rounding.',
        cpu_limit_seconds=120,cpu_limit_scope='process CPU checked before bounded fit/score/generate; not hardpreemption',
        metrics='All failures/copy flags; samepitchrepeat,distinctpitches,notes,leaps,overlap,rest,completed denominators; no objective appeal score.',
        copy_guard='All12train plus640/921 for all outputs; same exact8 local check on generated and canonical order. No retry/selection.',
        limitations=['Fixed note mass controls total marginal prior mass, but local context mass/k4 ratio and transition counts still change.',
                    'SharedNigelHolmes/contributors and publishers mean9groups are not independent contributors.',
                    'Raw training pitches same across3conditions; weighted intervals, initialunigram and timing all change together.',
                    'No new source admission, human labels, genre claim or musical quality conclusion.',
                    'Global CPU budget processes conditions in fixed order; late-condition skips preclude fair outcome or speed ranking.'],
        source_sha256=sorted(sources.values()),frozen_hashes={**prior['frozen_hashes'],**frozen,**{p:digest(root/p) for p in tracked}})
    plan_dir.mkdir(parents=True);(plan_dir/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    return dict(plan_sha256=digest(plan_dir/'plan.json'),status='waiting actual parent review; no fits/scores')


def run(root,corpus,extra,source_root,targets,plan_dir,clearance,output):
    if output.exists():raise ValueError('new output required')
    plan=json.loads((plan_dir/'plan.json').read_text());review=json.loads(clearance.read_text());sha=digest(plan_dir/'plan.json')
    if review.get('status')!='approved-for-local-experiment' or review.get('plan_sha256')!=sha or not review.get('review_reference'):
        raise ValueError('parent bound review declaration required; JSON alone not authority')
    for p,h in plan['frozen_hashes'].items():
        if digest(root/p)!=h:raise ValueError('frozen dependency changed')
    music,diag,sources,_,weights=inputs(root,corpus,extra,source_root,targets)
    if list(music)!=plan['ordered_train_ids'] or sorted(sources.values())!=plan['source_sha256']:raise ValueError('source inventory changed')
    if {k:[str(w) for w in v] for k,v in weights.items()}!=plan['weights']:raise ValueError('weight plan changed')
    seqs=[timing_coverage(m)[1] for m in music.values()];pitches=[[n.pitch for n in m.notes] for m in music.values()]
    if any(timing_coverage(m)[0]['unsupported_events'] for m in [*music.values(),*diag.values()]):raise ValueError('unsupported source')
    forbidden=set().union(*(phrases([n.pitch for n in m.notes]) for m in [*music.values(),*diag.values()]))
    output.mkdir(parents=True);(output/'before-fit.json').write_text(json.dumps(dict(plan_sha256=sha,clearance_sha256=digest(clearance)),indent=2)+'\n')
    started=process_time();conditions={}
    for name,ws in weights.items():
        if process_time()-started>=120:conditions[name]=dict(status='cpu_budget_skipped');continue
        try:model=WeightedContextModel(seqs,pitches,ws);factor=WeightedTimingDiagnostic(seqs,ws)
        except ValueError as e:conditions[name]=dict(status='model_rejected',reason=str(e));continue
        scores={}
        for label,scorer in [('factorized',factor),('contextk4',model)]:
            per_work={}
            for w,m in diag.items():
                if process_time()-started>=120:per_work[w]=dict(status='cpu_budget_skipped')
                else:per_work[w]=scorer.evaluate(timing_coverage(m)[1])
            scores[label]=dict(works=per_work,equal_work_nll=mean(r['nll_per_event'] for r in per_work.values()) if all('nll_per_event' in r for r in per_work.values()) else None)
        outputs=[]
        for seed in range(5):
            if process_time()-started>=120:outputs.append(dict(seed=seed,status='cpu_budget_skipped'));continue
            try:g=generate(model,seed)
            except ValueError as e:outputs.append(dict(seed=seed,status='resource_or_validation_rejected',reason=str(e)));continue
            ns=g.pop('notes');canon=sorted(ns,key=lambda n:(n['start'],n['end'],n['pitch']))
            hits=len((phrases([n['pitch'] for n in ns])|phrases([n['pitch'] for n in canon]))&forbidden)
            if hits:g['status']='copy_guard_blocked'
            f=output/f'{name}-{seed}-notes.json';f.write_text(json.dumps(ns,sort_keys=True)+'\n')
            g.update(seed=seed,metrics=metrics(ns,9216),copy_matches=hits,private_notes_sha256=digest(f));outputs.append(g)
        means,denominators=summarize(outputs)
        conditions[name]=dict(weighted_note_mass=str(model.weighted_mass),weighted_transition_mass=str(sum(model.intervals.values())),
            vocabulary_size=len(model.vocabulary),gate_scale_bit_length=model.gate_scale.bit_length(),
            max_cached_delta_weight_bit_length=max((w.bit_length() for entry in model._delta_cache.values() for w in [entry[2],*entry[3].values()]),default=0),
            prediction=scores,outputs=outputs,complete_only_means=means,metric_denominators=denominators)
    report=dict(plan_sha256=sha,conditions=conditions,cpu_seconds=process_time()-started,
                originals_unchanged=all(digest(Path(p))==h for p,h in sources.items()),limitations=plan['limitations'])
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',choices=['prepare','run'],required=True)
    for k in ('corpus','extra','source-root','adam','chopin','plan-dir'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--clearance',type=Path);p.add_argument('--output',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1];targets={'640':a.adam,'921':a.chopin}
    if a.stage=='prepare':r=prepare(root,a.corpus,a.extra,a.source_root,targets,a.plan_dir)
    else:
        if a.clearance is None or a.output is None:p.error('run requires clearance and output')
        r=run(root,a.corpus,a.extra,a.source_root,targets,a.plan_dir,a.clearance,a.output)
    print(json.dumps(r,indent=2))

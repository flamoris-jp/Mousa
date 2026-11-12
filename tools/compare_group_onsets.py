"""Fixed same-outcome group timing comparison; prepare never fits real sources."""
import json
from pathlib import Path
from statistics import mean
from time import process_time
from datetime import datetime,timezone
import compare_approved_expansion as base
import compare_bounded_corpus_expansion as bounded
from compare_onset_gate_models import phrases
from compare_context_onset_gate import metrics,summarize
from mousa.group_onset_model import GroupOnsetModel,observations,generate,_validate


def inputs(root,corpus,extra,source_root,assignment,targets):
    with bounded.profile():
        b,a,d,s,f=base.read_inputs(root,corpus,extra,source_root,json.loads(assignment.read_text()),targets)
    train={**b,**a}
    seq={k:observations(v.notes,v.total_ticks) for k,v in {**train,**d}.items()}
    for value in seq.values():_validate(value)
    return train,d,seq,s,f


def prepare(root,corpus,extra,source_root,assignment,targets,directory,screen_path):
    if directory.exists():raise ValueError('new plan directory required')
    # Actual requested work-count synthetic preflight before original MIDI read.
    n=5+len(json.loads(assignment.read_text())['additions'])
    synthetic=[[(0,60,((0,1,80,0),)),(1,62,((0,2,70,7),))] for _ in range(n)]
    for arm in (False,True):
        m=GroupOnsetModel(synthetic,context=arm)
        assert generate(m,0,target=8,tail=1)['status']=='complete'
    train,diagnostics,seq,sources,frozen=inputs(root,corpus,extra,source_root,assignment,targets)
    screen=json.loads(screen_path.read_text())
    if screen['blocked']:raise ValueError('prior intake screen blocked')
    intake_plan_path=root/'experiments/2026-11-12-sixteen-work-expansion-plan.json'
    intake_plan=json.loads(intake_plan_path.read_text())
    if (base.digest(intake_plan_path)!=screen['plan_sha256']
        or intake_plan['assignment_sha256']!=base.digest(assignment)
        or intake_plan['source_sha256']!=sorted(sources.values())):
        raise ValueError('intake screen not bound to these exact sources/assignment')
    frozen[str(intake_plan_path.relative_to(root))]=base.digest(intake_plan_path)
    frozen[str(screen_path.resolve().relative_to(root.resolve()))]=base.digest(screen_path)
    for name in ('src/mousa/group_onset_model.py','src/mousa/onset_groups.py','tests/test_group_onset_model.py',
                 'tools/compare_group_onsets.py','tools/compare_bounded_corpus_expansion.py','tools/compare_approved_expansion.py',
                 'tools/compare_onset_gate_models.py','tools/compare_context_onset_gate.py'):
        frozen[name]=base.digest(root/name)
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),assignment_sha256=base.digest(assignment),
        prior_intake_screen_sha256=base.digest(screen_path),prior_intake_plan_sha256=screen['plan_sha256'],
        train_ids=list(train),diagnostic_ids=list(diagnostics),source_sha256=sorted(sources.values()),frozen_hashes=frozen,
        outcome='Group-onset delta only. Initial0..12288, later1..12288; separate first/later pools. All sourcegroups retained for fit.',
        arms=['global','previous_cardinality_k4'],formula='Uniform prior total1. Context=(local_count+4*global_smoothed_probability)/(local_count_total+4); unseencontext global.',
        generation='Botharms empirical <=3note templates frequencyweighted, empirical anchor frequencyweighted, same RNG call policy. Template fields=(relativepitch,gate,velocity,releasevelocity) in originalgroupmember order. Count implicit. Groupdelta draw truncated to remaining support then template/anchor stages;64 whole-group rejection attempts,256totalnotes/groups,9216ticks,tail<=384,seeds0..4. No clipping or quantization.',
        generation_likelihood='Timing teacher-forced NLL is NOT joint template/pitch/gate probability and NOT feasibility-conditioned generation likelihood.',
        template_exclusions='>3note templates excluded from generation only; full counts and fraction reported. Pitchrange/gateoverflow/activepolyphony/samepitch/note-budget rejects counted. No template-only copy waiver.',
        copy_guard='All16 training plus observed640/921. Exact8interval check on generated and canonical note order. Allflags/failures retained, no retries or selection.',
        cpu_seconds=60,cpu_policy='Shared process CPU budget checked before bounded fits/evaluations/generation AND each generation proposal, not hardpreemption of a single delta enumeration/fit/evaluation. Missingarms/seeds explicit; incomplete runs preclude fair outcome ranking.',
        metrics='Equal-work groupdeltaNLL and groupcounts, generated note metrics complete-only means with denominators, matchedseed statuses, distinctonset validation, exacttemplate retention and events/group distribution.',
        synthetic_preflight=dict(works=n,botharms=True,real_fit=False),
        data_summary={k:dict(notes=len(v.notes),groups=len(seq[k])) for k,v in {**train,**diagnostics}.items()},
        limitations=['No raw eventNLL comparison: group and event outcomes differ.','Alreadyobserved diagnostics, not fresh test; withintrain links from intake retained.','No truevoice, chordfunction, melody or human quality labels.','Raw template reuse yields private research candidates only, not public-release clearance.','Same seeds do not align later random decisions after different groupdelta draws/rejections.'])
    directory.mkdir();(directory/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');return plan


def run(root,corpus,extra,source_root,assignment,targets,directory,clearance,output):
    if output.exists():raise ValueError('new output required')
    plan=json.loads((directory/'plan.json').read_text());decision=json.loads(clearance.read_text());ph=base.digest(directory/'plan.json')
    if decision.get('status')!='approved-for-local-experiment' or decision.get('plan_sha256')!=ph or not decision.get('review_reference'):raise ValueError('actual parent bound clearance required')
    if base.digest(assignment)!=plan['assignment_sha256']:raise ValueError('assignment changed')
    for name,digest in plan['frozen_hashes'].items():
        if base.digest(root/name)!=digest:raise ValueError('frozen dependency changed')
    train,diagnostics,seq,sources,_=inputs(root,corpus,extra,source_root,assignment,targets)
    if sorted(sources.values())!=plan['source_sha256']:raise ValueError('source inventory changed')
    output.mkdir();(output/'before-fit.json').write_text(json.dumps(dict(plan_sha256=ph,clearance_sha256=base.digest(clearance)))+'\n')
    forbidden=set().union(*(phrases([n.pitch for n in m.notes]) for m in [*train.values(),*diagnostics.values()]))
    start=process_time();results={}
    for label,arm in [('global',False),('previous_cardinality_k4',True)]:
        if process_time()-start>=60:results[label]={'status':'cpu_budget_skipped'};continue
        model=GroupOnsetModel([seq[k] for k in train],context=arm);pred={}
        for k in diagnostics:
            pred[k]=model.evaluate(seq[k]) if process_time()-start<60 else dict(status='cpu_budget_skipped')
        rows=[]
        for seed in range(5):
            if process_time()-start>=60:rows.append(dict(seed=seed,status='cpu_budget_skipped'));continue
            g=generate(model,seed,cpu_deadline=start+60);notes=g['notes'];canonical=sorted(notes,key=lambda n:(n['start'],n['end'],n['pitch']))
            hits=len((phrases([n['pitch'] for n in notes])|phrases([n['pitch'] for n in canonical]))&forbidden)
            row={k:v for k,v in g.items() if k not in ('notes','groups')};row.update(seed=seed,copy_matches=hits,metrics=metrics(notes,9216),group_count=len(g['groups']),
                distinct_later_onsets=all(b['onset']>a['onset'] for a,b in zip(g['groups'],g['groups'][1:])),template_fields_preserved=all(tuple(map(tuple,gr['template'])) in model.templates for gr in g['groups']))
            if hits:row['status']='copy_guard_blocked'
            path=output/f'{label}-{seed}-private.json';path.write_text(json.dumps(dict(notes=notes,groups=g['groups']),sort_keys=True)+'\n');row['private_sha256']=base.digest(path);rows.append(row)
        means,denom=summarize(rows)
        results[label]=dict(prediction=pred,equal_work_nll=mean(v['nll_per_group_delta'] for v in pred.values()) if all('nll_per_group_delta' in v for v in pred.values()) else None,
            training_groups=model.template_occurrences,template_types=len(model.templates),ineligible_template_occurrences=model.ineligible_occurrences,
            ineligible_fraction=model.ineligible_occurrences/model.template_occurrences,outputs=rows,complete_only_means=means,metric_denominators=denom)
    report=dict(plan_sha256=ph,conditions=results,cpu_seconds=process_time()-start,originals_unchanged=all(base.digest(Path(p))==sha for p,sha in sources.items()),
        matched_seed_statuses=[dict(seed=i,arms={k:next((r['status'] for r in v.get('outputs',[]) if r['seed']==i),'not_run') for k,v in results.items()}) for i in range(5)],limitations=plan['limitations'])
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['prepare','run'],required=True)
    for k in ('corpus','extra','source-root','assignment','adam','chopin','plan-dir'):
        p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--screen',type=Path);p.add_argument('--clearance',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    args=(Path(__file__).resolve().parents[1],a.corpus,a.extra,a.source_root,a.assignment,{'640':a.adam,'921':a.chopin},a.plan_dir)
    if a.stage=='prepare':
        if a.screen is None:p.error('prepare requires intake screen')
        result=prepare(*args,a.screen)
    else:
        if a.clearance is None or a.output is None:p.error('run requires clearance/output')
        result=run(*args,a.clearance,a.output)
    print(json.dumps(result,indent=2))

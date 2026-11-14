"""Four fixed observed-history contexts; prepare never fits real sources."""
import json
from pathlib import Path
from statistics import mean
from time import process_time
from datetime import datetime, timezone
import compare_approved_expansion as base
from compare_initial_rest_groups import read_inputs, outside_mass, conditional_initial_signature
from compare_onset_gate_models import phrases
from compare_context_onset_gate import metrics, summarize
from mousa.gate_context_group_model import GateContextGroupModel, ARMS, BIN_UPPER, generate
from mousa.group_timeline_metrics import timeline_metrics


def preflight():
    tiny=[[(0,60,((0,1536,80,0),)),(192,62,((0,96,80,0),)),(192,64,((0,96,80,0),))] for _ in range(16)]
    tiny.append([(12672,48,((0,192,80,0),)),(192,50,((0,192,80,0),))])
    for arm in ARMS:
        m=GateContextGroupModel(tiny,arm=arm);m.evaluate(tiny[0]);generate(m,0)
    return dict(conditions=4,works=17,real_sources_fitted=False)


def prepare(root,corpus,extra,source_root,assignment,targets,directory):
    if directory.exists():raise ValueError('new plan directory required')
    synthetic=preflight()
    train,diagnostics,seq,sources,frozen=read_inputs(root,corpus,extra,source_root,assignment,targets)
    ip=root/'experiments/2026-11-12-initial-rest-intake-plan.json'
    sp=root/'experiments/2026-11-12-initial-rest-intake-screen.json'
    intake=json.loads(ip.read_text());screen=json.loads(sp.read_text())
    if screen['blocked'] or screen['plan_sha256']!=base.digest(ip):raise ValueError('intake gate blocked or unbound')
    if intake['assignment_sha256']!=base.digest(assignment) or intake['source_sha256']!=sorted(sources.values()):raise ValueError('intake does not bind inputs')
    prior=root/'experiments/2026-11-12-initial-rest-comparison-plan.json'
    oldplan=json.loads(prior.read_text())
    for name,digest in oldplan['frozen_hashes'].items():
        if base.digest(root/name)!=digest:raise ValueError('old frozen dependency changed')
        frozen[name]=digest
    for name in ('tools/compare_gate_context_groups.py','tests/test_gate_context_groups_driver.py',
                 'src/mousa/gate_context_group_model.py','src/mousa/group_timeline_metrics.py',
                 'tests/test_gate_context_group_model.py','tests/test_group_timeline_metrics.py',
                 'experiments/2026-11-12-initial-rest-comparison-plan.json',
                 'experiments/2026-11-12-initial-rest-comparison-results.json',
                 'experiments/2026-11-12-gate-context-final-design.json'):
        frozen[name]=base.digest(root/name)
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),assignment_sha256=base.digest(assignment),source_sha256=sorted(sources.values()),
              train_ids=list(train),diagnostic_ids=list(diagnostics),frozen_hashes=frozen,conditions=ARMS,synthetic_preflight=synthetic,
              seeds=list(range(5)),cpu_seconds=60,first_limit=65536,later_limit=12288,gate_bin_upper=BIN_UPPER,
              copy_guard='Same all17 training+observed640/921 exact8interval guard for every arm;generated and canonical note order;retain all flags/failures.',
              data_summary={k:dict(notes=len(v.notes),groups=len(seq[k]),selected_eot=v.total_ticks,source_eot=v.source_total_ticks,first_delta=seq[k][0][0]) for k,v in {**train,**diagnostics}.items()},
              outcome='Teacher-forced group delta only, first/later separate;equal-work diagnostic means;not joint template/pitch/gate or raw-event NLL.',
              formula='All local contexts k4:(local_count+4*smoothed_global_probability)/(local_N+4).Global uniform prior total1;unseencontext global;allfirst laws identical.',
              state='After accepted/current teacher-forced group: H=max(H_previous-delta,current_max_gate).Next timing key computed before next delta from previous group size/maxgate or H. Reset every work. Rejected generation proposals do not advance state.',
              metrics='Exact union-of-note-interval silence, leading/internal/trailing and maxgap;activevoice integral/polyphonic time. Do not treat onset gaps as silence. Complete-only denominators and common seeds reported;empty timeline leading/trailing overlap explicitly.',
              source_role='Same17training;640/921 observed untrained diagnostics;not fresh. All withintrain/familylinks retained.',
              generation='Same template/anchor sampler stages and whole-group rejection;target9216,tail384,64attempts/group,256notes/groups,max3voices;no clipping. Context is timing-only,not learnedjointmodel.',
              budget='SharedCPU60 checked beforefit/eval/generation and eachproposal;not hardpreemption inside one operation.',
              limitations=['No musical quality or voice/chordfunction claim.','Private generated candidates only;not source training materials.','Prior exactgate3arm proposal was unrun;fixed4arms and bins chosen before outcomes.'])
    directory.mkdir();(directory/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');return plan


def run(root,corpus,extra,source_root,assignment,targets,directory,clearance,output):
    if output.exists():raise ValueError('new output required')
    plan=json.loads((directory/'plan.json').read_text());decision=json.loads(clearance.read_text());ph=base.digest(directory/'plan.json')
    if decision.get('status')!='approved-for-local-experiment' or decision.get('plan_sha256')!=ph or not decision.get('review_reference'):raise ValueError('parent bound clearance required')
    if base.digest(assignment)!=plan['assignment_sha256']:raise ValueError('assignment changed')
    for name,digest in plan['frozen_hashes'].items():
        if base.digest(root/name)!=digest:raise ValueError('frozen dependency changed')
    preflight()
    train,diagnostics,seq,sources,_=read_inputs(root,corpus,extra,source_root,assignment,targets)
    if sorted(sources.values())!=plan['source_sha256']:raise ValueError('source hashes changed')
    output.mkdir();(output/'before-fit.json').write_text(json.dumps(dict(plan_sha256=ph,clearance_sha256=base.digest(clearance)))+'\n')
    forbidden=set().union(*(phrases([n.pitch for n in m.notes]) for m in [*train.values(),*diagnostics.values()]))
    start=process_time();results={}
    for arm in ARMS:
        label=arm
        if process_time()-start>=60:results[label]=dict(status='cpu_budget_skipped');continue
        keys=list(train)
        model=GateContextGroupModel([seq[k] for k in keys],arm=arm);pred={}
        for k in diagnostics:
            pred[k]=model.evaluate(seq[k]) if process_time()-start<60 else dict(status='cpu_budget_skipped')
        rows=[]
        for seed in range(5):
            if process_time()-start>=60:rows.append(dict(seed=seed,status='cpu_budget_skipped'));continue
            g=generate(model,seed,cpu_deadline=start+60);notes=g['notes'];canonical=sorted(notes,key=lambda v:(v['start'],v['end'],v['pitch']))
            hits=len((phrases([v['pitch'] for v in notes])|phrases([v['pitch'] for v in canonical]))&forbidden)
            row={k:v for k,v in g.items() if k not in ('notes','groups')};row.update(seed=seed,copy_matches=hits,metrics=metrics(notes,9216),timeline_metrics=timeline_metrics(notes,9216),group_count=len(g['groups']),distinct_later_onsets=all(b['onset']>a['onset'] for a,b in zip(g['groups'],g['groups'][1:])),template_fields_preserved=all(tuple(map(tuple,gr['template'])) in model.templates for gr in g['groups']))
            if hits:row['pre_copy_status']=row['status'];row['status']='copy_guard_blocked'
            path=output/f'{label}-{seed}-private.json';path.write_text(json.dumps(dict(notes=notes,groups=g['groups']),sort_keys=True)+'\n');row['private_sha256']=base.digest(path);rows.append(row)
        means,denom=summarize(rows)
        complete=[r for r in rows if r['status']=='complete']
        timeline_means={k:mean(r['timeline_metrics'][k] for r in complete) for k in ('silence_ticks','leading_silence_ticks','trailing_silence_ticks','internal_silence_ticks','max_contiguous_silence_ticks','active_voice_tick_integral','polyphonic_time_fraction')} if complete else {}
        results[label]=dict(training_ids=keys,first_limit=65536,context_arm=arm,prediction=pred,equal_work_nll=mean(v['nll_per_group_delta'] for v in pred.values()) if all('nll_per_group_delta' in v for v in pred.values()) else None,initial_outside_target_mass=outside_mass(model),conditional_initial_signature=conditional_initial_signature(model),training_groups=model.template_occurrences,template_types=len(model.templates),ineligible_template_occurrences=model.ineligible_occurrences,ineligible_fraction=model.ineligible_occurrences/model.template_occurrences,outputs=rows,timeline_complete_only_means=timeline_means,timeline_denominator=len(complete),complete_only_means=means,metric_denominators=denom)
    signatures=[v.get('conditional_initial_signature') for v in results.values()]
    initial_equal=len(signatures)==4 and all(s is not None and s==signatures[0] for s in signatures)
    report=dict(plan_sha256=ph,conditions=results,conditional_initial_allarms_equal=initial_equal,cpu_seconds=process_time()-start,originals_unchanged=all(base.digest(Path(p))==sha for p,sha in sources.items()),matched_seed_statuses=[dict(seed=i,conditions={k:next((r['status'] for r in v.get('outputs',[]) if r['seed']==i),'not_run') for k,v in results.items()}) for i in range(5)],limitations=plan['limitations'])
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['prepare','run'],required=True)
    for k in ('corpus','extra','source-root','assignment','adam','chopin','plan-dir'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--clearance',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    args=(Path(__file__).resolve().parents[1],a.corpus,a.extra,a.source_root,a.assignment,{'640':a.adam,'921':a.chopin},a.plan_dir)
    if a.stage=='prepare':result=prepare(*args)
    else:
        if a.clearance is None or a.output is None:p.error('run requires clearance/output')
        result=run(*args,a.clearance,a.output)
    print(json.dumps(result,indent=2))

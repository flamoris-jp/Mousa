"""Pre-score freeze and separately cleared timing-only transfer to Chopin921.

Prepare writes a new immutable-by-contract plan and coverage/similarity screen,
without calling probability or evaluate. Score requires independent clearance,
checks that plan/input/model hashes remain unchanged, then reports all models.
No fitting on921, no unsupported-outcome deletion, no tuning or generation.
"""
import argparse
from datetime import datetime,timezone
from fractions import Fraction
import json
from pathlib import Path
from mousa.onset_gate_model import OnsetGateModel,DT_SIZE,GATE_SIZE,SUPPORT_SIZE
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.overlap_midi import read_midi
from mousa.research_intake import validate_manifest
from compare_context_onset_gate import digest
from compare_onset_gate_models import phrases,similarity,pairs

EXPECTED='b19f8e0d783915e80e33cc4f622ef9623994ab89f114a53983c3f628265b798b'
TRAIN_IDS=('mutopia-376','mutopia-888','mutopia-889','mutopia-789')


def timing_coverage(melody):
    previous=0;accepted=[];unsupported=[]
    for index,note in enumerate(melody.notes):
        dt=Fraction((note.start-previous)*384,melody.ppq);gate=Fraction((note.end-note.start)*384,melody.ppq)
        reason=None
        if dt.denominator!=1 or gate.denominator!=1:reason='incompatible_PPQ384'
        elif not 0<=dt<DT_SIZE or not 1<=gate<=GATE_SIZE:reason='outside_fixed_duration_support'
        if reason:unsupported.append(dict(index=index,delta=str(dt),gate=str(gate),reason=reason))
        else:accepted.append((int(dt),int(gate)))
        previous=note.start
    return dict(total_events=len(melody.notes),supported_events=len(accepted),unsupported_events=unsupported),accepted


def prepare(root,corpus,source,plan_dir):
    if plan_dir.exists():raise ValueError('new plan directory required')
    if digest(source)!=EXPECTED:raise ValueError('921 hash mismatch')
    frozen12=json.loads((root/'experiments/2026-11-12-onset-gate-results.json').read_text())
    frozen13=json.loads((root/'experiments/2026-11-12-context-onset-gate-results.json').read_text())
    if digest(root/'src/mousa/onset_gate_model.py')!=frozen12['before_scoring']['model_sha256']:
        raise ValueError('cycle12 model changed')
    if digest(root/'src/mousa/context_onset_gate.py')!=frozen13['plan']['code_sha256']['src/mousa/context_onset_gate.py']:
        raise ValueError('cycle13 model changed')
    rights=json.loads((root/'datasets/research-chopin921-reserved-20261112.json').read_text())
    if rights['encoding_rights']['status']!='PD-dedication-supported':raise ValueError('rights evidence absent')
    manifest=json.loads((root/'datasets/research-exploratory-multifamily-20261112.json').read_text());validate_manifest(manifest,corpus)
    train_hashes={w['work_id']:digest(corpus/w['file']) for w in manifest['works'] if w['work_id'] in TRAIN_IDS}
    if train_hashes!=frozen12['before_scoring']['train_sha256']:raise ValueError('training source bytes changed')
    tracked=['src/mousa/onset_gate_model.py','src/mousa/context_onset_gate.py','src/mousa/overlap_midi.py',
             'tools/evaluate_chopin921_transfer.py','tools/compare_onset_gate_models.py','tools/compare_context_onset_gate.py',
             'datasets/research-exploratory-multifamily-20261112.json','datasets/research-chopin921-reserved-20261112.json']
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),scope='First predictive timing evaluation of previously representation-inspected Chopin921',
        source=dict(id=921,track=1,sha256=EXPECTED,prior_state='rights-reviewed,representation-inspected,predictive-unscored'),
        train_ids=list(TRAIN_IDS),train_sha256=train_hashes,
        models=['cycle12_joint','cycle12_factorized','cycle13_previous_gate_context_strength4'],
        support=dict(ppq=384,delta_ticks=[0,12288],gate_ticks=[1,12288],size=SUPPORT_SIZE),
        priors='joint totaluniformmass1;factorized uniformmass1 per marginal; contextk4 rawcount shrinkage plusdelta prior1, sameglobalgateprior1',
        task='Teacherforced onset-delta/gate pair likelihood, original onset order; firstdelta fromtick0; previousgate reset perwork',
        coverage='Reject and report all unsupported outcomes; no quantization, no dropping or partial conditional NLL',
        screening='Before scores: exact8pitchinterval match OR normalizedwholeinterval edit similarity>=0.80 against train and independentallknowncohort screen blocks. No threshold relaxation.',
        independence='Chopin/Goretzki candidate newcomposer/contributor vs old4; sharedMutopia remains a confound. Independentfamilyclearance REQUIRED before score.',
        inference='One work92events expected, no confidence/generalization/appeal proof; compare same outcome support and report allmodels regardlessranking',
        no_tuning_or_refitting=True,no_pitch_likelihood=True,no_generation=True,
        after_evaluation='Mark921 predictive-observed; never call fresh again. Observationregistry updated separately; immutable reserved snapshot retained.',
        code_sha256={p:digest(root/p) for p in tracked})
    plan_dir.mkdir(parents=True)
    with (plan_dir/'plan.json').open('x') as stream:json.dump(plan,stream,indent=2);stream.write('\n')
    # This pass computes representation and similarity only, never a model score.
    target=read_midi(source,1);targetp=[n.pitch for n in target.notes];coverage,_=timing_coverage(target)
    screens=[]
    for w in manifest['works']:
        ref=read_midi(corpus/w['file'],w['track_index']);refp=[n.pitch for n in ref.notes]
        exact=len(phrases(refp)&phrases(targetp));near=similarity(refp,targetp)
        screens.append(dict(reference=w['work_id'],training=w['work_id'] in TRAIN_IDS,
                            exact8_interval_matches=exact,whole_interval_similarity=near,
                            flagged=bool(exact or (near is not None and near>=.80))))
    result=dict(plan_sha256=digest(plan_dir/'plan.json'),source_sha256=EXPECTED,coverage=coverage,screens=screens,
                any_flagged=any(r['flagged'] for r in screens),status='waiting_independent_family_and_allknown_similarity_clearance; no predictive scores')
    with (plan_dir/'prescore-screen.json').open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    return result


def score(root,corpus,source,plan_dir,output,clearance):
    if output.exists():raise ValueError('new result directory required')
    plan=json.loads((plan_dir/'plan.json').read_text());screen=json.loads((plan_dir/'prescore-screen.json').read_text())
    if digest(plan_dir/'plan.json')!=screen['plan_sha256']:raise ValueError('pre-score plan changed')
    for path,sha in plan['code_sha256'].items():
        if digest(root/path)!=sha:raise ValueError('frozen dependency changed')
    if digest(source)!=plan['source']['sha256']:raise ValueError('source changed')
    decision=json.loads(clearance.read_text())
    if decision.get('status')!='cleared' or decision.get('source_sha256')!=EXPECTED or decision.get('flagged') is not False or decision.get('screen_threshold')!=.80:
        raise ValueError('independent explicit clearance missing or flagged')
    if screen['any_flagged'] or screen['coverage']['unsupported_events']:raise ValueError('pre-score screen or coverage blocks')
    manifest=json.loads((root/'datasets/research-exploratory-multifamily-20261112.json').read_text());validate_manifest(manifest,corpus)
    seqs=[];pss=[]
    for w in manifest['works']:
        if w['work_id'] not in plan['train_ids']:continue
        if digest(corpus/w['file'])!=plan['train_sha256'][w['work_id']]:raise ValueError('training source changed')
        m=read_midi(corpus/w['file'],w['track_index']);seqs.append(pairs(m));pss.append([n.pitch for n in m.notes])
    if len(seqs)!=4:raise ValueError('missing train work')
    target=read_midi(source,1);coverage,probe=timing_coverage(target)
    if coverage!=screen['coverage'] or coverage['unsupported_events']:raise ValueError('coverage changed orunsupported')
    output.mkdir(parents=True)
    before=dict(plan_sha256=digest(plan_dir/'plan.json'),independent_clearance_sha256=digest(clearance),
                source_sha256=EXPECTED,train_sha256=plan['train_sha256'],models_sha256=plan['code_sha256'],coverage=coverage)
    with (output/'before-scoring.json').open('x') as stream:json.dump(before,stream,indent=2);stream.write('\n')
    flat=[pair for seq in seqs for pair in seq]
    models={'cycle12_joint':OnsetGateModel(flat), 'cycle12_factorized':OnsetGateModel(flat,factorized=True),
            'cycle13_previous_gate_context_strength4':ContextOnsetGateModel(seqs,pss,timing_context=True,pitch_continuity=True,strength=4)}
    # First predictive calls occur only here, after the persisted freeze+clearance.
    results={name:model.evaluate(probe) for name,model in models.items()}
    report=dict(before_scoring=before,training_events=len(flat),test_events=len(probe),results=results,
        support_observations=dict(seen_joint_pairs=sum(p in set(flat) for p in probe),
            seen_deltas=sum(d in {x[0] for x in flat} for d,g in probe),seen_gates=sum(g in {x[1] for x in flat} for d,g in probe)),
        source_state='Chopin921 now predictive-observed; no refit, no retuning, never fresh again',
        source_unchanged=digest(source)==EXPECTED,
        limitations=['One representation-inspected work, not untouchedblind data or broadgeneralization.',
            'Predictive task timingonly, not pitches/harmony/appeal; no newgeneration.',
            'Joint andfactorized priors differ, though fulloutcome support matches.',
            'SharedMutopia pipeline remains despite composer/contributor separation.',
            'Allmodels reported withoutselection/refit; 580results not pooled asfresh.'])
    with (output/'report.json').open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',choices=['prepare','score'],required=True)
    for key in ('corpus','source','plan-dir'):parser.add_argument('--'+key,type=Path,required=True)
    parser.add_argument('--output',type=Path);parser.add_argument('--clearance',type=Path)
    args=parser.parse_args();root=Path(__file__).resolve().parents[1]
    if args.stage=='prepare':result=prepare(root,args.corpus,args.source,args.plan_dir)
    else:
        if args.output is None or args.clearance is None:parser.error('score requires output andclearance')
        result=score(root,args.corpus,args.source,args.plan_dir,args.output,args.clearance)
    print(json.dumps(result,indent=2))

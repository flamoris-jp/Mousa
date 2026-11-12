"""Prepare-only until independent clearance: fixed old4 and augmented5 timing models.

No model construction in prepare. Source1741 remains unscored until the explicit
score stage. No weighting selection, quantization, unsupported-event deletion,
pitch likelihood, or semantic evaluation. All five model conditions reported.
"""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
from mousa.overlap_midi import read_midi
from mousa.onset_gate_model import OnsetGateModel,SUPPORT_SIZE
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.research_intake import validate_manifest
from compare_context_onset_gate import digest
from compare_onset_gate_models import pairs,phrases,similarity
from evaluate_chopin921_transfer import timing_coverage

EXPECTED='3de7c0dae2206d5bdd2ddb5f49c3e2851df0d218472c868c0212d0f98b19ccaf'
EXTRA='631bcd481e09c1493191959ec3264c3513c4a93177ffc6d833dea4f4952b659b'
TRAIN_IDS=('mutopia-376','mutopia-888','mutopia-889','mutopia-789')


def check_clearance(decision):
    if (decision.get('status')!='cleared' or decision.get('source_sha256')!=EXPECTED
        or decision.get('flagged') is not False or decision.get('screen_threshold')!=.80):
        raise ValueError('independent allknown explicit clearance missing or flagged')


def prepare(root,corpus,source,cornelius,rights_path,plan_dir):
    if plan_dir.exists():raise ValueError('new plan required')
    if digest(source)!=EXPECTED or digest(cornelius)!=EXTRA:raise ValueError('source bytes changed')
    prior=json.loads((root/'experiments/2026-11-12-cornelius-augmentation-results.json').read_text())['plan']
    for path,sha in prior['code_sha256'].items():
        if digest(root/path)!=sha:raise ValueError('prior frozen dependency changed')
    # Parent-reviewed rights evidence is frozen, not inferred from free access.
    rights=json.loads((root/rights_path).read_text())
    if EXPECTED not in json.dumps(rights):raise ValueError('rights snapshot lacks source digest')
    manifest=json.loads((root/'datasets/research-exploratory-multifamily-20261112.json').read_text())
    validate_manifest(manifest,corpus)
    hashes={w['work_id']:digest(corpus/w['file']) for w in manifest['works'] if w['work_id'] in TRAIN_IDS}
    if hashes!=prior['train_sha256']:raise ValueError('old training bytes changed')
    assignment=json.loads((root/'datasets/research-cornelius583-training-assignment.json').read_text())
    if assignment['source_sha256']!=EXTRA or assignment['related_evaluation_exclusions']!=['mutopia-580']:
        raise ValueError('583 source/family assignment changed')
    tracked=['tools/evaluate_mendelssohn1741_transfer.py','tools/evaluate_chopin921_transfer.py',
             'experiments/2026-11-12-cornelius-augmentation-results.json',rights_path]
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),source=dict(id=1741,track=1,sha256=EXPECTED,expected_events=161),
        question='Does raw-count583 augmentation timing-loss pattern recur on this one previously unscored work?',
        models=['old4_joint','old4_factorized','old4_context_k4','augmented5_factorized','augmented5_context_k4'],
        counts='Raw event counts only; priormass1,contextstrength4. No explored weighting adopted.',
        task='Teacherforced onset-delta/gate likelihood; firstdelta fromtick0, per-work previousgate reset; no pitch/semantic/appeal evaluation',
        support=dict(ppq=384,delta=[0,12288],gate=[1,12288],size=SUPPORT_SIZE),
        coverage='Reject entire score on any unsupported outcome; no quantization, splitting or deletion',
        screening='Independent allknown family/exact8interval or normalized wholeinterval similarity>=.80 blocks before scoring; thresholds fixed.',
        training_ids=list(TRAIN_IDS),augmentation='mutopia-583',excluded_related_evaluation='mutopia-580',
        assignment_scope='Prior583training authorization reused;1741 is a separately authorized new evaluation, not a modification of historical640/921 diagnostic assignment.',
        train_sha256=hashes,extra_sha256=EXTRA,code_sha256={**prior['code_sha256'],**{p:digest(root/p) for p in tracked}},
        all_conditions_required=True,no_tuning=True,after_score='1741 observed, never fresh again',
        limitations=['One source inspected for rights/representation, not untouched music or broadgeneralization.','SharedMutopia pipeline; no genre count inferred from composer.','Joint/factorized prior parameterizations differ on samefull support.'])
    plan_dir.mkdir(parents=True);(plan_dir/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    target=read_midi(source,1);coverage,_=timing_coverage(target);tp=[n.pitch for n in target.notes];screens=[]
    references=[(w['work_id'],read_midi(corpus/w['file'],w['track_index'])) for w in manifest['works']]
    references.append(('mutopia-583',read_midi(cornelius,1)))
    for name,ref in references:
        rp=[n.pitch for n in ref.notes];exact=len(phrases(rp)&phrases(tp));near=similarity(rp,tp)
        screens.append(dict(reference=name,exact8=exact,similarity=near,flagged=bool(exact or near is not None and near>=.80)))
    screen=dict(plan_sha256=digest(plan_dir/'plan.json'),source_sha256=EXPECTED,coverage=coverage,screens=screens,
                any_flagged=any(r['flagged'] for r in screens),status='waiting independent allknown clearance; no model construction or predictive score')
    (plan_dir/'prescore-screen.json').write_text(json.dumps(screen,indent=2)+'\n');return screen


def score(root,corpus,source,cornelius,plan_dir,clearance,output):
    if output.exists():raise ValueError('new output required')
    plan=json.loads((plan_dir/'plan.json').read_text());screen=json.loads((plan_dir/'prescore-screen.json').read_text())
    if digest(plan_dir/'plan.json')!=screen['plan_sha256']:raise ValueError('plan changed')
    for path,sha in plan['code_sha256'].items():
        if digest(root/path)!=sha:raise ValueError('frozen dependency changed')
    if digest(source)!=EXPECTED or digest(cornelius)!=EXTRA:raise ValueError('source changed')
    decision=json.loads(clearance.read_text());check_clearance(decision)
    if screen['any_flagged'] or screen['coverage']['unsupported_events']:raise ValueError('prescore screen blocks')
    manifest=json.loads((root/'datasets/research-exploratory-multifamily-20261112.json').read_text());validate_manifest(manifest,corpus)
    old=[]
    for w in manifest['works']:
        if w['work_id'] not in TRAIN_IDS:continue
        if digest(corpus/w['file'])!=plan['train_sha256'][w['work_id']]:raise ValueError('train changed')
        old.append(read_midi(corpus/w['file'],w['track_index']))
    if len(old)!=4:raise ValueError('missing training work')
    extra=read_midi(cornelius,1);target=read_midi(source,1);coverage,probe=timing_coverage(target)
    if coverage!=screen['coverage'] or coverage['unsupported_events']:raise ValueError('coverage changed or unsupported')
    if coverage['total_events']!=161:raise ValueError('target count differs from plan')
    output.mkdir(parents=True)
    before=dict(plan_sha256=digest(plan_dir/'plan.json'),independent_clearance_sha256=digest(clearance),source_sha256=EXPECTED,
                train_sha256=plan['train_sha256'],extra_sha256=EXTRA,code_sha256=plan['code_sha256'],coverage=coverage)
    (output/'before-scoring.json').write_text(json.dumps(before,indent=2)+'\n')
    results={};counts={}
    for label,music in [('old4',old),('augmented5',old+[extra])]:
        seqs=[pairs(m) for m in music];pitch_seqs=[[n.pitch for n in m.notes] for m in music];flat=[p for s in seqs for p in s]
        counts[label]=len(flat)
        if label=='old4':results['old4_joint']=OnsetGateModel(flat).evaluate(probe)
        results[label+'_factorized']=OnsetGateModel(flat,factorized=True).evaluate(probe)
        results[label+'_context_k4']=ContextOnsetGateModel(seqs,pitch_seqs,timing_context=True,pitch_continuity=True,strength=4).evaluate(probe)
    report=dict(before_scoring=before,training_event_counts=counts,test_events=len(probe),results=results,
                state='1741 now predictive-observed; no refit or retuning; not fresh again',limitations=plan['limitations'],
                timing_only=True,all_sources_unchanged=(digest(source)==EXPECTED and digest(cornelius)==EXTRA))
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',choices=['prepare','score'],required=True)
    for k in ('corpus','source','cornelius','plan-dir'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--rights-path');p.add_argument('--clearance',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args();root=Path(__file__).resolve().parents[1]
    if a.stage=='prepare':
        if a.rights_path is None:p.error('prepare requires rights-path')
        r=prepare(root,a.corpus,a.source,a.cornelius,a.rights_path,a.plan_dir)
    else:
        if a.clearance is None or a.output is None:p.error('score requires clearance and output')
        r=score(root,a.corpus,a.source,a.cornelius,a.plan_dir,a.clearance,a.output)
    print(json.dumps(r,indent=2))

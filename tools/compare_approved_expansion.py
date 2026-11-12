"""Bounded reusable intake/experiment stages; review declarations are NOT authority.

An actual parent-reviewed assignment is required in addition to JSON validation.
Do not execute on real additions until the parent specifies admitted sources.
Prepare never fits; run requires a separately bound review decision after screens.
"""
import argparse
from datetime import datetime,timezone
import hashlib
from fractions import Fraction
import json
from pathlib import Path
import re
from statistics import mean
from time import process_time
from mousa.overlap_midi import read_midi
from mousa.onset_gate_model import OnsetGateModel
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.optimized_feasible_generation import generate_optimized
from mousa.research_intake import validate_manifest
from evaluate_chopin921_transfer import timing_coverage
from compare_onset_gate_models import phrases,similarity
from compare_context_onset_gate import metrics,summarize

BLOCKED_IDS={'mutopia-1692','mutopia-804','mutopia-1741'}
DIAGNOSTICS={'640':('13ec851eb00ca9aba345cad50f03bdb3b189f566f38d094a1e6b839765b3d678',2),
             '921':('b19f8e0d783915e80e33cc4f622ef9623994ab89f114a53983c3f628265b798b',1)}


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_path(root,name):
    if type(name) is not str or not name or Path(name).is_absolute():raise ValueError('relative path required')
    p=(root/name).resolve()
    if not p.is_relative_to(root.resolve()):raise ValueError('path outside approved root')
    return p


def validate_assignment(a,blocked_hashes=()):
    if type(a) is not dict or a.get('schema_version')!=1:raise ValueError('assignment schema')
    if a.get('related_evaluation_exclusions')!=['mutopia-580']:raise ValueError('580 exclusion required')
    families=a.get('diagnostic_families')
    if type(families) is not dict or set(families)!={'640','921'}:raise ValueError('both diagnostics required')
    for fs in families.values():
        if type(fs) is not list or not fs or any(type(f) is not str or not f.strip() for f in fs):raise ValueError('reviewed diagnostic families required')
    works=a.get('additions')
    if type(works) is not list or not 1<=len(works)<=7:raise ValueError('one to seven additions required')
    ids=set();hashes=set()
    for w in works:
        if type(w) is not dict:raise ValueError('work record required')
        for key in ('work_id','canonical_source_id','family_id','rights_evidence','file','review_reference'):
            if type(w.get(key)) is not str or not w[key].strip():raise ValueError('missing work evidence')
        if w['work_id'] in ids or w['canonical_source_id'] in BLOCKED_IDS or w['work_id'] in BLOCKED_IDS:raise ValueError('duplicate or blocked identity')
        ids.add(w['work_id'])
        for key in ('sha256','rights_evidence_sha256'):
            if type(w.get(key)) is not str or not re.fullmatch('[a-f0-9]{64}',w[key]):raise ValueError('digest required')
        if w['sha256'] in hashes or w['sha256'] in blocked_hashes:raise ValueError('duplicate or blocked bytes')
        hashes.add(w['sha256'])
        if type(w.get('track')) is not int or not 0<=w['track']<256:raise ValueError('explicit track required')
        if w.get('rights_approved') is not True or w.get('family_reviewed') is not True:raise ValueError('review flags absent')
        if any(w['family_id'] in fs for fs in families.values()):raise ValueError('crosssplit family conflict; diagnostic cannot silently disappear')
    return works


def blocked_hashes(root):
    return {json.loads((root/f'experiments/2026-11-12-{name}-independent-screen.json').read_text())['source_sha256']
            for name in ('telemann1692','clementi804','mendelssohn1741')}


def read_inputs(root,corpus,extra_path,additions_root,assignment,diagnostic_paths):
    prior=json.loads((root/'experiments/2026-11-12-cornelius-augmentation-results.json').read_text())['plan']
    for p,sha in prior['code_sha256'].items():
        if digest(root/p)!=sha:raise ValueError('frozen base changed')
    works=validate_assignment(assignment,blocked_hashes(root))
    manifest=json.loads((root/'datasets/research-exploratory-multifamily-20261112.json').read_text());validate_manifest(manifest,corpus)
    train={};source_files={};seen=set()
    for w in manifest['works']:
        if w['work_id'] not in prior['train_sha256']:continue
        f=corpus/w['file'];sha=digest(f)
        if sha!=prior['train_sha256'][w['work_id']]:raise ValueError('base bytes changed')
        train[w['work_id']]=read_midi(f,w['track_index']);source_files[str(f.resolve())]=sha;seen.add(sha)
    if len(train)!=4 or digest(extra_path)!=prior['extra_sha256']:raise ValueError('base583 changed')
    train['mutopia-583']=read_midi(extra_path,1);source_files[str(extra_path.resolve())]=digest(extra_path);seen.add(digest(extra_path))
    added={};evidence={}
    for w in works:
        f=safe_path(additions_root,w['file']);e=safe_path(root,w['rights_evidence'])
        if digest(f)!=w['sha256'] or digest(e)!=w['rights_evidence_sha256']:raise ValueError('addition or rights bytes changed')
        if w['work_id'] in train or w['sha256'] in seen:raise ValueError('duplicate base/addition')
        seen.add(w['sha256']);added[w['work_id']]=read_midi(f,w['track']);source_files[str(f)]=w['sha256'];evidence[w['rights_evidence']]=w['rights_evidence_sha256']
    diagnostics={}
    for w,(sha,track) in DIAGNOSTICS.items():
        f=diagnostic_paths[w]
        if digest(f)!=sha:raise ValueError('diagnostic bytes changed')
        if sha in seen:raise ValueError('diagnostic used as training')
        diagnostics[w]=read_midi(f,track);source_files[str(f.resolve())]=sha
    return train,added,diagnostics,source_files,{**prior['code_sha256'],**evidence}


def prepare(root,corpus,extra,additions_root,assignment_path,diagnostic_paths,plan_dir):
    if plan_dir.exists():raise ValueError('new plan required')
    a=json.loads(assignment_path.read_text())
    base,added,diagnostics,sources,frozen=read_inputs(root,corpus,extra,additions_root,a,diagnostic_paths)
    tracked=['tools/compare_approved_expansion.py','src/mousa/context_onset_gate.py','src/mousa/onset_gate_model.py',
             'src/mousa/optimized_feasible_generation.py','tools/evaluate_chopin921_transfer.py']
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),scope='Prospective approved-addition comparison; observed640/921diagnostics only',
        assignment_sha256=digest(assignment_path),base_ids=list(base),addition_ids=list(added),diagnostics=['640','921'],
        models=['factorized','contextk4'],weights='raw natural event counts; per-work boundaries preserved',
        generation='contextonly,seeds0..4,mix1/4,optimizedfeasible,tail384,target9216,max256notes; all statuses/no retries',
        cpu_limit_seconds=60,resource_scope='process CPU checked before each bounded fit/evaluate/generate; no hard OS preemption',
        screens='Exact byte duplicate reject; train-vs640/921 exact8 OR .80global blocks. Withintrain overlaps reported/grouped, not automatic common-pattern rejection.',
        authorization='Schema flags do not prove authority; separate actual parent rights/assignment review required before run.',
        frozen_hashes={**frozen,**{p:digest(root/p) for p in tracked}},source_sha256=sorted(sources.values()),
        limitations=['Small natural-budget comparison confounds quantity/content/vocabulary.','Observed diagnostics not fresh, family declarations are reviewed externally not inferred by this script.','No genre/semantic/listener claims.'])
    plan_dir.mkdir(parents=True);(plan_dir/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    coverage={k:timing_coverage(m)[0] for k,m in {**base,**added,**diagnostics}.items()}
    cross=[];within=[];alltrain={**base,**added}
    def comparison(x,y):
        px=[n.pitch for n in x.notes];py=[n.pitch for n in y.notes]
        exact=len(phrases(px)&phrases(py))
        try:near=similarity(px,py)
        except ValueError:return dict(exact8=exact,global_similarity=None,complete=False,reason='global interval bound exceeded')
        return dict(exact8=exact,global_similarity=near,complete=True)
    for w,m in alltrain.items():
        for d,ref in diagnostics.items():
            r=comparison(m,ref);r.update(source=w,diagnostic=d);cross.append(r)
    items=list(alltrain.items())
    for i,(w,m) in enumerate(items):
        for v,ref in items[i+1:]:within.append(dict(source=w,reference=v,**comparison(m,ref)))
    blocked=any(c['unsupported_events'] or c['total_events']==0 for c in coverage.values()) or any(not r['complete'] or r['exact8'] or r['global_similarity'] is not None and r['global_similarity']>=.80 for r in cross)
    total=sum(len(m.notes) for m in alltrain.values())
    if total>100000:blocked=True
    screen=dict(plan_sha256=digest(plan_dir/'plan.json'),coverage=coverage,crosssplit=cross,withintrain=within,
                augmented_events=total,blocked=blocked,status='blocked' if blocked else 'awaiting actual parent review and bound clearance',
                withintrain_interpretation='Includes common motifs; no automatic legal-copy allegation or rejection. Review family declarations in assignment.')
    (plan_dir/'screen.json').write_text(json.dumps(screen,indent=2)+'\n');return screen


def run(root,corpus,extra,additions_root,assignment_path,diagnostic_paths,plan_dir,clearance_path,output):
    if output.exists():raise ValueError('new output required')
    plan=json.loads((plan_dir/'plan.json').read_text());screen=json.loads((plan_dir/'screen.json').read_text());decision=json.loads(clearance_path.read_text())
    if digest(plan_dir/'plan.json')!=screen['plan_sha256'] or digest(assignment_path)!=plan['assignment_sha256']:raise ValueError('plan or assignment changed')
    if screen['blocked']:raise ValueError('screen blocked')
    if (decision.get('status')!='approved-for-local-experiment' or decision.get('plan_sha256')!=screen['plan_sha256']
        or decision.get('assignment_sha256')!=plan['assignment_sha256'] or not decision.get('review_reference')):raise ValueError('bound parent review declaration required; not authority by itself')
    for p,sha in plan['frozen_hashes'].items():
        if digest(root/p)!=sha:raise ValueError('frozen dependency changed')
    a=json.loads(assignment_path.read_text());base,added,diagnostics,sources,_=read_inputs(root,corpus,extra,additions_root,a,diagnostic_paths)
    if sorted(sources.values())!=plan['source_sha256']:raise ValueError('source inventory changed')
    output.mkdir(parents=True);(output/'before-fit.json').write_text(json.dumps(dict(plan_sha256=screen['plan_sha256'],clearance_sha256=digest(clearance_path)),indent=2)+'\n')
    alltrain={**base,**added};forbidden=set().union(*(phrases([n.pitch for n in m.notes]) for m in [*alltrain.values(),*diagnostics.values()]))
    started=process_time();results={}
    for condition,music in [('base5',list(base.values())),('expanded',list(alltrain.values()))]:
        if process_time()-started>=60:
            results[condition]=dict(status='cpu_budget_skipped');continue
        seqs=[timing_coverage(m)[1] for m in music];ps=[[n.pitch for n in m.notes] for m in music];flat=[p for s in seqs for p in s]
        models={'factorized':OnsetGateModel(flat,factorized=True),'contextk4':ContextOnsetGateModel(seqs,ps,timing_context=True,pitch_continuity=True,strength=4)}
        predictions={}
        for name,model in models.items():
            scores={}
            for w,m in diagnostics.items():
                if process_time()-started>=60:scores[w]=dict(status='cpu_budget_skipped')
                else:scores[w]=model.evaluate(timing_coverage(m)[1])
            predictions[name]=dict(works=scores,equal_work_nll=mean(s['nll_per_event'] for s in scores.values()) if all('nll_per_event' in s for s in scores.values()) else None)
        rows=[]
        for seed in range(5):
            if process_time()-started>=60:rows.append(dict(seed=seed,status='cpu_budget_skipped'));continue
            g=generate_optimized(models['contextk4'],seed,uniform_mix=Fraction(1,4),trailing_rest_ticks=384)
            ns=g['notes'];canon=sorted(ns,key=lambda n:(n['start'],n['end'],n['pitch']));hits=len((phrases([n['pitch'] for n in ns])|phrases([n['pitch'] for n in canon]))&forbidden)
            row={k:v for k,v in g.items() if k!='notes'};row.update(seed=seed,metrics=metrics(ns,9216),copy_matches=hits)
            if hits:row['status']='copy_guard_blocked'
            f=output/f'{condition}-{seed}-notes.json';f.write_text(json.dumps(ns,sort_keys=True)+'\n');row['private_notes_sha256']=digest(f);rows.append(row)
        means,denominators=summarize(rows)
        results[condition]=dict(training_events=len(flat),work_count=len(music),predictions=predictions,outputs=rows,complete_only_means=means,metric_denominators=denominators)
    report=dict(plan_sha256=screen['plan_sha256'],conditions=results,cpu_seconds=process_time()-started,
        originals_unchanged=all(digest(Path(p))==sha for p,sha in sources.items()),limitations=plan['limitations'])
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--stage',choices=['prepare','run'],required=True)
    for k in ('corpus','extra','additions-root','assignment','adam','chopin','plan-dir'):parser.add_argument('--'+k,type=Path,required=True)
    parser.add_argument('--clearance',type=Path);parser.add_argument('--output',type=Path);a=parser.parse_args();root=Path(__file__).resolve().parents[1];targets={'640':a.adam,'921':a.chopin}
    if a.stage=='prepare':result=prepare(root,a.corpus,a.extra,a.additions_root,a.assignment,targets,a.plan_dir)
    else:
        if a.clearance is None or a.output is None:parser.error('run requires bound clearance and output')
        result=run(root,a.corpus,a.extra,a.additions_root,a.assignment,targets,a.plan_dir,a.clearance,a.output)
    print(json.dumps(result,indent=2))

"""Fixed silence-boundary pitch return; known/new random cohorts separate."""
from pathlib import Path
import json,time,hashlib,subprocess
from datetime import datetime,timezone
from statistics import mean
from compare_weighted_maple_cycle45 import read,ROOT,public_structure
from mousa.weighted_group_cycle45 import WeightedGroupModel,generate
from mousa.silence_return_cycle46 import compare_segments
from mousa.group_timeline_metrics import timeline_metrics
from compare_context_onset_gate import metrics
SEEDS={'known':[45000,45001,45002],'new_random':[46600,46601,46602]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def seed_scan():
    files=subprocess.check_output(['git','ls-files','experiments','datasets'],cwd=ROOT,text=True).splitlines();hits=[]
    def walk(x,path):
        if isinstance(x,dict):
            for k,v in x.items():
                if 'seed' in k.lower():
                    vals=v if isinstance(v,list) else [v]
                    if any(type(n) is int and n in SEEDS['new_random'] for n in vals):hits.append(path+':'+k)
                walk(v,path)
        elif isinstance(x,list):
            for v in x:walk(v,path)
    count=0
    for f in files:
        if f.endswith('.json'):
            try:v=json.loads((ROOT/f).read_text())
            except ValueError:continue
            count+=1;walk(v,f)
    return dict(tracked_json_count=count,matches=hits,scope='Tracked seed-named fields only; no proof of unrecorded nonuse.')
def prepare(out):
    if out.exists():raise ValueError('retain plan')
    train,diag,seq,sources,maps,a=read();priorpath=ROOT/'experiments/2026-11-12-weighted-maple-cycle45-final4-plan.json'
    prior=json.loads(priorpath.read_text());frozen=dict(prior['frozen_hashes'])
    for f,h in frozen.items():
        if sha(ROOT/f)!=h:raise ValueError('frozen changed')
    own=['src/mousa/silence_segments_cycle46.py','src/mousa/silence_return_cycle46.py','src/mousa/phrasewide_register_cycle44.py','src/mousa/phrase_groups_cycle41.py','tools/compare_silence_return_cycle46.py','tests/test_silence_segments_cycle46.py','tests/test_silence_return_cycle46.py','tests/test_silence_return_cycle46_driver.py','experiments/2026-11-12-weighted-maple-cycle45-final4-plan.json','experiments/2026-11-12-silence-cycle46-diagnosis.json']
    frozen.update({f:sha(ROOT/f) for f in own})
    scan=seed_scan()
    if scan['matches']:raise ValueError('new cohort already recorded')
    p=dict(created_utc=datetime.now(timezone.utc).isoformat(),frozen_hashes=frozen,source_sha256=sorted(sources.values()),train_ids=list(train),families=[maps[18][i] for i in train],copy_reference_ids=list(train)+list(diag),seeds=SEEDS,seed_scan=scan,cpu_seconds=60,conditions=['control','silence_return'],mode='raw',masses=[17,3411,3428],
       intervention='Use all-prior max noteend; gap>=192ticks forms a segment. Leading/trailing silence not segments. Original segment1 and segment3 fixed, eachrequires>=2groups, no searchsubstitution. Third anchors match originalfirst ordinal modulo length +2 pitchclass; exact DP minimizes entrance/internal/exit anchor differences, missingendpoints0, lexlow tie; collision/copy afterchoice rejects, no alternative.',
       invariants='Alltime/gate/velocity/release/templates/memberorder/notes/rests/EOT fixed;22refs bothorders exact8;max3/256notes/pitch0..127/target9216/tail384. Not restamount or density intervention.',
       reporting='Every6seed status grouped separately by known versus new_random; complete/common percohort denominators, gap/repeat/diversity/true silence and fixed block structure. Private anchor arrays only. Copy/CPU failure and no_effect not success.',
       limitations=['Threshold192 is arbitrary halfquarter atPPQ384, not phrase truth. Internal gaps below192 may still exist.','Groupanchor is not melodic voice; minimized proxy and repeated pitchclass do not prove musical appeal.','Newrandom seeds are not new musical works or newhumanratings;known cohort previouslydiagnosed.','Original long introductions preserved, not trimmed.','Maple2/4 added to unconditioned model, output8x6/8 convention not meterunderstanding.','Fixed condition/seed order under shared CPU60; late skipped rows may limit faircomparison.'])
    out.mkdir(parents=True);write(out/'plan.json',p);return p
def skipped(seed):return dict(seed=seed,control=dict(status='cpu_budget_skipped'),silence_return=dict(status='cpu_budget_skipped'))
def run(planpath,clearance,out):
    if out.exists():raise ValueError('retain run')
    p=json.loads(planpath.read_text());c=json.loads(clearance.read_text())
    if c.get('approved') is not True or c.get('plan_sha256')!=sha(planpath):raise ValueError('boundapproval')
    for f,h in p['frozen_hashes'].items():
        if sha(ROOT/f)!=h:raise ValueError('frozenchanged')
    start=time.process_time();train,diag,seq,sources,maps,_=read()
    if sorted(sources.values())!=p['source_sha256'] or list(train)!=p['train_ids']:raise ValueError('sourcechanged')
    refs=[[n.pitch for n in m.notes] for m in [*train.values(),*diag.values()]]
    out.mkdir();write(out/'before-fit.json',dict(plan_sha256=sha(planpath),train_ids=list(train)))
    write(out/'fit-journal.json',dict(status='construction_started',ids=list(train)))
    try:m=WeightedGroupModel([seq[i] for i in train],p['families'],mode='raw',masses=p['masses'])
    except Exception as exc:
        write(out/'fit-journal.json',dict(status='construction_failed',exception=type(exc).__name__));raise
    write(out/'fit-journal.json',dict(status='construction_completed',ids=list(train)))
    cohorts={}
    for cohort,seeds in p['seeds'].items():
        rows=[]
        for seed in seeds:
            if time.process_time()-start>=60:rows.append(skipped(seed));continue
            g=generate(m,seed,cpu_deadline=start+60)
            v=compare_segments(g['notes'],g['groups'],refs) if g['status']=='complete' else dict(control=dict(status=g['status']),intervention=dict(status='baseline_unavailable'))
            q=out/f'{cohort}-{seed}-private.json';write(q,dict(original=g,comparison=v))
            row=dict(seed=seed,private_sha256=sha(q),generation_attempts=g['attempts'],generation_rejections=g['rejections'])
            for dest,src in [('control','control'),('silence_return','intervention')]:
                raw=v[src];item={k:x for k,x in raw.items() if k not in ('notes','groups')}
                if 'edit' in item:item['edit']={k:x for k,x in item['edit'].items() if k not in ('original_C_anchors','mapped_C_anchors')}
                if 'notes' in raw:item.update(metrics=metrics(raw['notes'],9216),timeline=timeline_metrics(raw['notes'],9216),structure=public_structure(raw['notes'],raw['groups']))
                row[dest]=item
            rows.append(row);write(out/('progress-'+cohort+'.json'),rows)
        common=[r['seed'] for r in rows if all(r[k]['status']=='complete' for k in p['conditions'])]
        summary={}
        for condition in p['conditions']:
            summary[condition]=dict(status_counts={s:sum(r[condition]['status']==s for r in rows) for s in {r[condition]['status'] for r in rows}})
            for label,eligible in [('complete',[r[condition] for r in rows if r[condition]['status']=='complete']),('common',[r[condition] for r in rows if r['seed'] in common])]:
                means={};den={}
                if eligible:
                    for k in eligible[0]['metrics']:
                        vals=[r['metrics'][k] for r in eligible if r['metrics'][k] is not None];means[k]=mean(vals) if vals else None;den[k]=len(vals)
                summary[condition][label]=dict(candidates=len(eligible),means=means,metric_denominators=den)
        cohorts[cohort]=dict(rows=rows,summary=summary,common_seeds=common)
    report=dict(plan_sha256=sha(planpath),cohorts=cohorts,cpu_seconds=time.process_time()-start,originals_unchanged=all(sha(Path(f))==h for f,h in sources.items()),limitations=p['limitations'])
    write(out/'report.json',report);return report
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['prepare','run']);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--plan',type=Path);ap.add_argument('--clearance',type=Path);a=ap.parse_args()
    if a.mode=='run' and (a.plan is None or a.clearance is None):ap.error('plan/clearance')
    print(json.dumps(prepare(a.output) if a.mode=='prepare' else run(a.plan,a.clearance,a.output),indent=2))

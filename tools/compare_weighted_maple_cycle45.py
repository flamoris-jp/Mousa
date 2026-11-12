"""Seven fixed music-profile conditions; prepare never fits real sources."""
from pathlib import Path
import json,hashlib,time,math
from fractions import Fraction
from collections import Counter
from datetime import datetime,timezone
from statistics import mean
from evaluate_dowland_cycle40 import inputs,ROOT
from mousa.overlap_midi import read_midi
from mousa.initial_rest_group_model import observations,validate
from mousa.weighted_group_cycle45 import WeightedGroupModel,generate,pool_weights
from mousa.group_timeline_metrics import timeline_metrics
from mousa.group_structure_cycle45 import structure
from compare_context_onset_gate import metrics
from compare_onset_gate_models import phrases
ASSIGN='datasets/research-maple-training-assignment-cycle45-20261112.json'
SEEDS=[45000,45001,45002]
CONDITIONS=[(f'{n}_{mode}',n,mode,(17,3411,3428)) for mode in ('raw','equal_work','equal_family') for n in (17,18)]+[('18_natural_raw',18,'raw',(18,4172,4190))]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def rat(x):return dict(numerator=x.numerator,denominator=x.denominator)
def read():
    assignment=json.loads((ROOT/ASSIGN).read_text())
    for f,h in [(assignment['base_assignment'],assignment['base_assignment_sha256']),(assignment['family_audit'],assignment['family_audit_sha256']),(assignment['addition']['rights_ledger'],assignment['addition']['rights_sha256'])]:
        if sha(ROOT/f)!=h:raise ValueError('assignment dependency changed')
    train,old,new,seq,sources,_=inputs()
    if list(train)!=assignment['old_train_ids']:raise ValueError('old17 changed')
    p=(ROOT.parent/assignment['addition']['file']).resolve()
    if not p.is_relative_to(ROOT.parent.resolve()) or sha(p)!=assignment['addition']['sha256']:raise ValueError('Maple bytes changed')
    maple=read_midi(p,assignment['addition']['track']);sources[str(p)]=sha(p)
    expanded={**train,assignment['addition']['id']:maple}
    seq['mutopia-23']=observations(maple.notes,maple.total_ticks);validate(seq['mutopia-23'],65536)
    if list(expanded)!=assignment['expanded_train_ids']:raise ValueError('18ids changed')
    audit=json.loads((ROOT/assignment['family_audit']).read_text());maps={}
    for n,key in [(17,'old17_proposed_groups'),(18,'prospective18_proposed_groups')]:
        groups=audit[key];mapping={}
        for f,ids in groups.items():
            for i in ids:
                if i in mapping:raise ValueError('duplicate family membership')
                mapping[i]=f
        if len(groups)!=11 or set(mapping)!=set(list(expanded)[:n]):raise ValueError('family coverage')
        maps[n]=mapping
    expected=assignment['expected']
    if (sum(len(m.notes) for m in train.values()),sum(len(seq[i]) for i in train),sum(len(m.notes) for m in expanded.values()),sum(len(seq[i]) for i in expanded))!=(expected['old_notes'],expected['old_groups'],expected['new_notes'],expected['new_groups']):raise ValueError('counts changed')
    return expanded,{**old,**new},seq,sources,maps,assignment

def prepare(out):
    if out.exists():raise ValueError('retain old plan')
    train,diagnostics,seq,sources,maps,a=read()
    previous=json.loads((ROOT/'experiments/2026-11-12-dowland-cycle40-plan.json').read_text())
    frozen=dict(previous['frozen_hashes'])
    for f,h in frozen.items():
        if sha(ROOT/f)!=h:raise ValueError('frozen dependency changed')
    own=[ASSIGN,a['family_audit'],a['addition']['rights_ledger'],'src/mousa/weighted_group_cycle45.py','tools/compare_weighted_maple_cycle45.py','tests/test_weighted_group_cycle45.py','tests/test_weighted_maple_cycle45_driver.py','src/mousa/group_structure_cycle45.py','tests/test_group_structure_cycle45.py','tools/evaluate_dowland_cycle40.py','experiments/2026-11-12-dowland-cycle40-plan.json']
    frozen.update({f:sha(ROOT/f) for f in own})
    configs=[]
    for label,n,mode,masses in CONDITIONS:
        ids=list(train)[:n];families=[maps[n][i] for i in ids];lens=[len(seq[i]) for i in ids]
        lengths=[[1]*n,[v-1 for v in lens],lens]
        weights=[pool_weights(ls,families,mode,m) for ls,m in zip(lengths,masses)]
        configs.append(dict(label=label,works=n,mode=mode,masses=masses,ids=ids,families=families,pool_weights=[[rat(w) for w in ws] for ws in weights],pool_effective_event_ESS=[rat(Fraction(m*m)/sum((length*w*w for length,w in zip(ls,ws)),Fraction())) for ls,ws,m in zip(lengths,weights,masses)]))
    plan=dict(created_utc=datetime.now(timezone.utc).isoformat(),frozen_hashes=frozen,source_sha256=sorted(sources.values()),conditions=configs,seeds=SEEDS,cpu_seconds=60,copy_reference_ids=list(train)+list(diagnostics),
      source_counts={i:dict(notes=len(m.notes),groups=len(seq[i]),ineligible_template_occurrences=sum(len(t)>3 for _,_,t in seq[i])) for i,m in train.items()},
      weights='Pool-specific first/later/template-anchor normalization. Raw events equal; work-equal nonempty works equal; family-equal nonempty11declaredseries equal with event-proportional contribution withinseries. Emptylater work contributes0; entireempty pool rejected. Fixed mass17/3411/3428; naturalraw18 mass18/4172/4190. Uniform prior total1 each timingpool, all integer scaling includes prior.',
      generation='Same bounded whole-template generator; initial0..65536, later1..12288; 9216target/tail384/max256notes/max3active/64tries. All templates learned, >3members excluded only at generation. No phrase editing in this quantity comparison.',
      limits='Standalone exactFraction profile with2048bit integer scaling guard;7conditions×3same seeds=21candidates. Shared CPU60; fixed condition order, retain failures and skipped rows. No generation restart or source cropping.',
      structure_metrics='Four fixed2304tickblocks: onsetgroup/noteonset/soundingnote counts; occupied union/silence via measurement-only interval clipping. Signed withinblock anchorinterval exact equality for>=2groups; empty/1group missing,6pair eligibility denominators. Whole signed anchorinterval3gram (4groups) overlappingwindows, repeat=(windows-distinct)/windows, missingif0. Not voice/phrasing/appeal truth. Raw anchorinterval arrays omitted frompublic rows; exact reconstruction remains possible fromprivategroups only.',
      roles='Maple training only, same263cohort;18potentialtrain+4alreadyobserved =22copyrefs for every condition. No fresh score or newhumanratings. Parent actual-use ledger follows journaled first fit attempt.',
      seed_scope='45000..45002 absent from old tracked seed-field records per parent audit; not proof of unrecorded nonuse. New random draws, not independent music or newhumanratings.',
      metrics='Allstatus/copy/effort, per-output eventgap/repeat/diversity/density and actual silence/overlap. Complete-only and all7common seeds with explicitdenominators. Weighted >3 eligibilitymass and raw counts separately. No musicalquality inference.',
      limitations=['Naturalraw18 changes prior concentration aswellascomposition; masscontrolled comparisons holdpoolmass only.','First/later normalization is not one universal perworkweight.','Family internal longwork dominance remains;11linkedseries notindependentcontributors.','Fixed order underCPUbudget can leave laterconditions unattempted; no fairquality ranking then.','Weighted ESS is algebraic eventdispersion, not independentobservations.','Maple original2/4 and all original meter/time remain intact. Generator has no meter conditioning;9216 is an8x6/8 output convention, not learned6/8phrase understanding. Fixed block descriptors are output measurements, not source phrase annotations.','Natural18 and controlledraw18 template/anchor laws are exact-proportion equivalent but integer scaling changes randrange bit consumption. Same seed does not align draws; output differences cannot be attributed solely to timing prior strength from3seeds.'])
    out.mkdir(parents=True);write(out/'plan.json',plan);return plan

def public_structure(notes,groups):
    value=structure(notes,groups)
    value['blocks']=[{k:v for k,v in b.items() if k!='anchor_intervals'} for b in value['blocks']]
    return value

def skipped_rows():
    return [dict(seed=s,status='cpu_budget_skipped') for s in SEEDS]

def run(planpath,clearance,out):
    if out.exists():raise ValueError('retain run')
    p=json.loads(planpath.read_text());c=json.loads(clearance.read_text())
    if c.get('approved') is not True or c.get('plan_sha256')!=sha(planpath):raise ValueError('bound approval')
    for f,h in p['frozen_hashes'].items():
        if sha(ROOT/f)!=h:raise ValueError('frozen changed')
    start=time.process_time();train,diag,seq,sources,maps,a=read()
    if sorted(sources.values())!=p['source_sha256']:raise ValueError('source set')
    out.mkdir();write(out/'before-fit.json',dict(plan_sha256=sha(planpath),source_sha256=p['source_sha256']))
    forbidden=set().union(*(phrases([n.pitch for n in m.notes]) for m in [*train.values(),*diag.values()]))
    journal=[];results={}
    for cfg in p['conditions']:
        label=cfg['label']
        if time.process_time()-start>=60:results[label]=dict(status='cpu_budget_skipped',outputs=skipped_rows());continue
        stage=dict(condition=label,ids=cfg['ids'],status='construction_started');journal.append(stage);write(out/'fit-journal.json',journal)
        try:m=WeightedGroupModel([seq[i] for i in cfg['ids']],cfg['families'],mode=cfg['mode'],masses=cfg['masses'])
        except Exception as exc:
            stage.update(status='construction_failed',exception=type(exc).__name__);write(out/'fit-journal.json',journal);results[label]=dict(status='construction_failed',outputs=[dict(seed=s,status='model_unavailable') for s in SEEDS]);continue
        stage['status']='construction_completed';write(out/'fit-journal.json',journal)
        if [[rat(w) for w in ws] for ws in m.pool_weights]!=cfg['pool_weights']:raise ValueError('weight drift')
        rows=[]
        for seed in SEEDS:
            if time.process_time()-start>=60:rows.append(dict(seed=seed,status='cpu_budget_skipped'));continue
            g=generate(m,seed,cpu_deadline=start+60);ns=g['notes'];canonical=sorted(ns,key=lambda n:(n['start'],n['end'],n['pitch']))
            hits=len((phrases([n['pitch'] for n in ns])|phrases([n['pitch'] for n in canonical]))&forbidden)
            row={k:v for k,v in g.items() if k not in ('notes','groups')};row.update(seed=seed,copy_matches=hits,metrics=metrics(ns,9216),timeline=timeline_metrics(ns,9216),structure=public_structure(ns,g['groups']))
            if hits:row['pre_copy_status']=row['status'];row['status']='copy_guard_blocked'
            q=out/f'{label}-{seed}-private.json';write(q,g);row['private_sha256']=sha(q);rows.append(row)
        results[label]=dict(status='fitted',outputs=rows,weighted_template_mass=rat(m.template_occurrences),weighted_ineligible_mass=rat(m.ineligible_occurrences),raw_ineligible_occurrences=sum(len(t)>3 for i in cfg['ids'] for _,_,t in seq[i]),raw_groups=sum(len(seq[i]) for i in cfg['ids']),integer_scale_bits=dict(template=m.template_scale.bit_length(),anchor=m.anchor_scale.bit_length()))
        write(out/'progress.json',results)
    common=[s for s in SEEDS if all(any(row['seed']==s and row['status']=='complete' for row in v['outputs']) for v in results.values())]
    for v in results.values():
        rows=v['outputs'];v['status_counts']={s:sum(r['status']==s for r in rows) for s in {r['status'] for r in rows}}
        for key,subset in [('complete_only',[r for r in rows if r['status']=='complete']),('common_success',[r for r in rows if r['seed'] in common])]:
            means={};den={}
            if subset:
                for k in subset[0]['metrics']:
                    values=[r['metrics'][k] for r in subset if r['metrics'][k] is not None];means[k]=mean(values) if values else None;den[k]=len(values)
            v[key]=dict(candidates=len(subset),means=means,metric_denominators=den)
    report=dict(plan_sha256=sha(planpath),conditions=results,common_complete_seeds=common,cpu_seconds=time.process_time()-start,originals_unchanged=all(sha(Path(f))==h for f,h in sources.items()),limitations=p['limitations'])
    write(out/'report.json',report);return report

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['prepare','run']);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--plan',type=Path);ap.add_argument('--clearance',type=Path);args=ap.parse_args()
    if args.mode=='run' and (args.plan is None or args.clearance is None):ap.error('plan/clearance')
    print(json.dumps(prepare(args.output) if args.mode=='prepare' else run(args.plan,args.clearance,args.output),indent=2))

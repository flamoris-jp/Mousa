"""Bounded fixed18-work generation comparison; prepare does not fit or generate."""
import argparse,hashlib,json,os,subprocess,time
from pathlib import Path
from statistics import mean,median
from itertools import combinations
from compare_weighted_maple_cycle45 import read,ROOT,public_structure,rat
from mousa.weighted_group_cycle45 import WeightedGroupModel,generate,pool_weights
from mousa.overlap_midi import read_midi
from mousa.group_timeline_metrics import timeline_metrics
from compare_context_onset_gate import metrics
from compare_onset_gate_models import phrases
from evaluate_dvorak_cycle48 import check_support,verify_model_mass,journal
SHARED=ROOT.parent
SEEDS=list(range(49000,49012));MODES=['raw','equal_work','equal_family'];MASSES=(17,3411,3428)
ROLE='datasets/research-dvorak1948-observation-cycle48-20261112.json'
D_SOURCE='mousa-cycle47-dvorak/score.mid'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def seed_records(v,path='$',active=False):
    found=[]
    if isinstance(v,dict):
        for k,x in v.items():found+=seed_records(x,path+'.'+k,active or 'seed' in k.lower())
    elif isinstance(v,list):
        for i,x in enumerate(v):found+=seed_records(x,path+f'[{i}]',active)
    elif active and type(v) is int and v in SEEDS:found.append(dict(json_path=path,value=v))
    return found

def audit_seeds():
    paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0');paths=[p for p in paths if p]
    entries=[];hits=[]
    for rel in paths:
        if not rel.endswith('.json'):continue
        p=ROOT/rel
        try:v=json.loads(p.read_text())
        except (ValueError,UnicodeError):continue
        entries.append(dict(path=rel,sha256=sha(p)))
        for row in seed_records(v):hits.append(dict(path=rel,**row))
    return dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),tracked_json_files=entries,candidate_seed_hits=hits,
        scope='Recursive integer values under JSON keys containing seed in currently tracked JSON files; not proof of all historical/untracked/unrecorded nonuse. Code seed algorithms/ranges and non-JSON logs are outside this structured audit. Existing45000-2 explicitly previously observed.')

def inputs():
    train,old,seq,sources,maps,a=read()
    if len(train)!=18 or len(old)!=4:raise ValueError('fixed18+4 required')
    role=json.loads((ROOT/ROLE).read_text());p=SHARED/D_SOURCE
    if role['fit'] or not role['score'] or role['training_admitted'] or sha(p)!=role['source_sha256']:raise ValueError('Dvorak role/hash')
    if sha(p) in sources.values():raise ValueError('candidate cannot be training source')
    d=read_midi(p,1);sources[str(p)]=sha(p)
    refs={**train,**old,'dvorak-1948-observed':d}
    if len(refs)!=23:raise ValueError('23 identical copy refs required')
    for k in train:check_support(seq[k])
    return train,seq,maps[18],refs,sources

def configs(train,seq,mapping):
    out=[];ids=list(train);families=[mapping[k] for k in ids]
    lengths=([1]*18,[len(seq[k])-1 for k in ids],[len(seq[k]) for k in ids])
    for mode in MODES:
        weights=[[rat(w) for w in pool_weights(ns,families,mode,m)] for ns,m in zip(lengths,MASSES)]
        out.append(dict(label=mode,mode=mode,ids=ids,families=families,masses=list(MASSES),pool_weights=weights))
    return out

def prepare(out):
    if out.exists():raise ValueError('new plan directory')
    train,seq,mapping,refs,sources=inputs();audit=audit_seeds()
    if audit['candidate_seed_hits']:raise ValueError('candidate recorded seed collision')
    paths=set(ROOT.glob('src/mousa/*.py'))|set(ROOT.glob('tools/*.py'))|set(ROOT.glob('tests/*.py'))|set(ROOT.glob('datasets/*.json'))|set(ROOT.glob('experiments/*.json'))
    plan=dict(schema='mousa-cycle49-generation-v1',frozen_hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)},source_sha256={str(Path(p).relative_to(SHARED)):h for p,h in sources.items()},conditions=configs(train,seq,mapping),seeds=SEEDS,prior_observed_seeds=[45000,45001,45002],seed_audit=audit,copy_reference_ids=list(refs),copy_rule='Same23refs every arm: exact7 signed interval window in generated event-order OR canonical(start,end,pitch) order versus each source canonical order. Any hit blocks whole candidate; no generation retry/seed replacement. Not a legal similarity clearance.',
      settings=dict(target=9216,tail=384,max_notes=256,max_attempts=64),cpu_seconds=60,
      metrics='All36 statuses, attempts/rejections, first onset, exact occupied/internal/leading/trailing silence, notes per full target and post-first-onset available horizon, distinct pitches and distinct/notes (length-confounded), event-order jumps (not voice inference), group/block repetition and explicit valid denominators. Complete-only summaries plus all-output rows; no failure removal.',
      across_diversity='All output pairs among complete non-copy-blocked candidates only, with attempted/eligible denominators. Exact canonical full note-event equality includes pitch/start/end/vel/release, not pitch-only duplicate claims; also signed anchor3-interval-window set Jaccard, missing if either set empty. Per mode and cross-mode strata; pairs/windows are not independent.',
      limits=['18sameworks5512notes4190groups; no new material fit. Dvorak copy-only never fitted.','8x6/8 9216tick convention atPPQ384, not source meter-conditioned generation or learned phrase understanding.','Same seeds across weights are not aligned RNG draws because integerization changes random-bit consumption.','New seed identifiers do not make training corpora/music statistically independent.','Historical3seed22ref outputs are exploratory background, not identical23ref conditions.','Source timing/rests preserved; generated leading silence is never trimmed/forced.','A-D human ratings unanswered; no proxy appeal ranking.','CPU60 cooperative checks before bounded calls and inside generator, not hard OS preemption; fixed order may bias remaining attempts on exhaustion.'],actual_fit=False,actual_generation=False)
    out.mkdir();write(out/'plan.json',plan);return plan

def diversity(a,b):
    signature=lambda x:tuple(sorted((n['start'],n['end'],n['pitch'],n['velocity'],n.get('release_velocity',0)) for n in x['notes']))
    def grams(x):
        anchors=[g['anchor'] for g in x['groups']];iv=[b-a for a,b in zip(anchors,anchors[1:])]
        return {tuple(iv[i:i+3]) for i in range(max(0,len(iv)-2))}
    x,y=grams(a),grams(b)
    return dict(exact_canonical_note_events_equal=signature(a)==signature(b),anchor3gram_jaccard=len(x&y)/len(x|y) if x and y else None,interpretation='Descriptor equality/overlap, not duplicate-work or plagiarism determination; timings and dynamics included only in exact event equality.')

def density(notes,timeline):
    first=min((n['start'] for n in notes),default=None);available=9216-first if first is not None else 0
    return dict(first_onset=first,notes_per_quarter_full=len(notes)*384/9216,notes_per_quarter_postfirst=len(notes)*384/available if available else None,postfirst_available_ticks=available,distinct_pitch_per_note=len({n['pitch'] for n in notes})/len(notes) if notes else None,warning='Ratios depend on sample length; postfirst denominator retains all subsequent rests, not evidence of musical quality.')

def run(planpath,clearance,out):
    if out.exists():raise ValueError('new output directory')
    p=json.loads(planpath.read_text());c=json.loads(clearance.read_text());ph=sha(planpath)
    if c.get('approved') is not True or c.get('plan_sha256')!=ph:raise ValueError('bound review required')
    for rel,h in p['frozen_hashes'].items():
        if sha(ROOT/rel)!=h:raise ValueError('dependency changed:'+rel)
    train,seq,mapping,refs,sources=inputs()
    if {str(Path(k).relative_to(SHARED)):v for k,v in sources.items()}!=p['source_sha256']:raise ValueError('source drift')
    if p['conditions']!=configs(train,seq,mapping) or p['seeds']!=SEEDS or p['copy_reference_ids']!=list(refs):raise ValueError('fixed configuration drift')
    out.mkdir();jp=out/'journal.jsonl';start=time.process_time();results={};accepted={}
    forbidden=set().union(*(phrases([n.pitch for n in m.notes]) for m in refs.values()))
    for cfg in p['conditions']:
        label=cfg['label'];rows=[];results[label]=dict(outputs=rows)
        if time.process_time()-start>=60:
            rows.extend(dict(seed=s,status='cpu_budget_skipped') for s in SEEDS);continue
        journal(jp,'fit_attempt',condition=label,ids=cfg['ids'])
        try:
            m=WeightedGroupModel([seq[k] for k in cfg['ids']],cfg['families'],mode=label,masses=MASSES)
            mass=verify_model_mass(m)
            if [[rat(w) for w in ws] for ws in m.pool_weights]!=cfg['pool_weights']:raise ValueError('weights differ')
            journal(jp,'fit_complete',condition=label,counter_masses=mass)
        except Exception as exc:
            journal(jp,'fit_failure',condition=label,exception=type(exc).__name__)
            rows.extend(dict(seed=s,status='fit_failed',exception=type(exc).__name__) for s in SEEDS);continue
        for seed in SEEDS:
            if time.process_time()-start>=60:rows.append(dict(seed=seed,status='cpu_budget_skipped'));continue
            journal(jp,'generation_attempt',condition=label,seed=seed)
            try:
                g=generate(m,seed,cpu_deadline=start+60,**p['settings']);ns=g['notes'];canonical=sorted(ns,key=lambda n:(n['start'],n['end'],n['pitch']))
                hits=len((phrases([n['pitch'] for n in ns])|phrases([n['pitch'] for n in canonical]))&forbidden)
                row={k:v for k,v in g.items() if k not in ('notes','groups')};row.update(seed=seed,copy_matches=hits,metrics=metrics(ns,9216),timeline=timeline_metrics(ns,9216),structure=public_structure(ns,g['groups']))
                row['density']=density(ns,row['timeline'])
                if hits:row['pre_copy_status']=row['status'];row['status']='copy_guard_blocked'
                q=out/f'{label}-{seed}-private.json';write(q,g);row['private_sha256']=sha(q);rows.append(row)
                if row['status']=='complete':accepted[(label,seed)]=g
                journal(jp,'generation_complete',condition=label,seed=seed,status=row['status'])
            except Exception as exc:
                rows.append(dict(seed=seed,status='generation_failed',exception=type(exc).__name__));journal(jp,'generation_failure',condition=label,seed=seed,exception=type(exc).__name__)
            write(out/'progress.json',results)
    pairrows=[]
    for (a,x),(b,y) in combinations(accepted.items(),2):
        if time.process_time()-start>=60:break
        pairrows.append(dict(left=list(a),right=list(b),stratum='within_mode' if a[0]==b[0] else 'across_modes',**diversity(x,y)))
    for label,v in results.items():
        rows=v['outputs'];v['status_counts']={status:sum(r['status']==status for r in rows) for status in sorted({r['status'] for r in rows})}
        complete=[r for r in rows if r['status']=='complete'];summ={}
        for field in ('notes','distinct_pitches','mean_abs_pitch_interval','above_octave_fraction'):
            values=[r['metrics'][field] for r in complete if r['metrics'][field] is not None]
            summ[field]=dict(n=len(values),mean=mean(values) if values else None,median=median(values) if values else None,min=min(values) if values else None,max=max(values) if values else None)
        v['complete_only_summary']=summ;v['all_expected_outputs']=12
    expected=len(accepted)*(len(accepted)-1)//2
    report=dict(plan_sha256=ph,conditions=results,across_output_pairs=pairrows,pair_eligible=expected,pair_measured=len(pairrows),pair_status='complete' if len(pairrows)==expected else 'cpu_budget_truncated',complete_candidates=len(accepted),expected_candidates=36,cpu_seconds=time.process_time()-start,originals_unchanged=all(sha(Path(k))==v for k,v in sources.items()),dvorak_fit=False,limits=p['limits'])
    write(out/'report.json',report);return report
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('stage',choices=['prepare','run']);a.add_argument('--plan',type=Path,required=True);a.add_argument('--clearance',type=Path);a.add_argument('--output',type=Path);v=a.parse_args();r=prepare(v.plan) if v.stage=='prepare' else run(v.plan,v.clearance,v.output);print(json.dumps(r,indent=2))

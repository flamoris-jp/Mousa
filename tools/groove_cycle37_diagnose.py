"""Fixed-count expansion error/mass accounting. No new conditions or tuning."""
import argparse
from collections import Counter,defaultdict
from datetime import datetime,timezone
from fractions import Fraction
from hashlib import sha256
import json
import math
from pathlib import Path
import time
from mousa.drum_ioi_35work_profile import DrumIOI35WorkProfile
from mousa.drum_ioi_multiscale import CONDITIONS
from prepare_groove_split import read_events

REPO=Path(__file__).resolve().parents[1]
PRIOR='experiments/2026-11-12-groove-cycle36-fit-final-plan.json'
RESULT='experiments/2026-11-12-groove-cycle36-results.json'
FILES=['tools/groove_cycle37_diagnose.py','tests/test_groove_cycle37.py',PRIOR,RESULT,'datasets/research-groove-usage-cycle36-20261112.json']
def sha(p):return sha256(p.read_bytes()).hexdigest()
def fraction(value):return {'numerator':value.numerator,'denominator':value.denominator,'decimal':float(value)}


def transition(old,new):
    if old and not new:raise ValueError('nested counts cannot lose observed support')
    return 'old_seen' if old else 'newly_seen' if new else 'still_unseen'


def support_mass(model,previous,old_seen,new_seen):
    if not old_seen<=new_seen or any(type(x) is not int or not 0<=x<=30720 for x in new_seen):raise ValueError('nested exact support required')
    a=sum((model.probability(x,previous_instrument=previous) for x in sorted(old_seen)),Fraction())
    b=sum((model.probability(x,previous_instrument=previous) for x in sorted(new_seen-old_seen)),Fraction())
    c=1-a-b
    if min(a,b,c)<0:raise ValueError('invalid probability partition')
    return {'old_seen':a,'newly_seen':b,'still_unseen':c}


def summarize(pairs):
    if not pairs:raise ValueError('nonempty paired losses required')
    old=math.fsum(x[0] for x in pairs);new=math.fsum(x[1] for x in pairs)
    return {'events':len(pairs),'baseline_sum_nll':old,'expanded_sum_nll':new,'expanded_minus_baseline_sum_nll':new-old,'expanded_minus_baseline_mean_nll':(new-old)/len(pairs)}


def prepare(output):
    if output.exists():raise ValueError('retain old output')
    p=json.loads((REPO/PRIOR).read_text());hashes={**p['frozen_hashes'],**{f:sha(REPO/f) for f in FILES}}
    for f,h in hashes.items():
        if sha(REPO/f)!=h:raise ValueError('prior dependency changed')
    plan={'created_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Posthoc fixed12/35 count reconstruction; no new fitted condition, parameter change or fresh validation.',
          'frozen_hashes':hashes,'inventory_sha256':p['inventory_sha256'],'training':p['training'],'diagnostics':p['diagnostics'],'baseline_train_ids':p['baseline_train_ids'],'duplicate_aliases_excluded':p['duplicate_aliases_excluded'],'conditions':list(CONDITIONS),
          'dimensions':['global_exact_IOI_transition','local_exact_IOI_transition','global_quotient_transition','local_quotient_transition','global_residual_transition','previous_context_exposure_change','previous_context_support_size_change'],
          'transition_labels':['old_seen','newly_seen','still_unseen'],'context_exposure_bins':['0','1-9','10-99','100+'],
          'metrics':'Per-recording/per-drummer and separate dimension partitions of expanded-minus-baseline NLL for all six conditions. Each dimension separately covers all events; do not add across dimensions.',
          'mass_analysis':'For every previous-instrument context used by fixed diagnostics (including initial None), exact Fraction mass over same fixed disjoint global IOI sets: baseline-seen, expanded-newly-seen, unseen in both. Sum sparse seen sets and exact complement1; no target bins or quantization. Also frequency-weighted context mixtures per drummer as descriptive teacher-forced context accounting, not autonomous generation distributions.',
          'prior_accounting':'Report uniform global prior coefficient1/(N+1), context pseudo/global and uniform coefficients for exact-k updates, q-contextk4 coefficients, and quotient/residual smoothing caveat. Increased N changes effective prior strength even with fixed nominal priors.',
          'verification':'All96 work-condition NLL sums equal stored Cycle36 exactly; exact mass partitions sum1; originals unchanged; repeat except CPU identical.',
          'cpu_seconds':60,'maximum_contexts':129,'support_size':30721,'maximum_source_events':30000,
          'roles':'35 train (23 newly used in priorcycle), eight already observed,1107 not fitted unchanged. Duplicate alias remains excluded; no other corpus originals read.',
          'limitations':['Posthoc descriptors do not identify causal drummer/style effects or prove robustness under unobserved conditions.',
                         'Training volume, content, duration, instrument mix and prior-to-count ratio changed together.',
                         'Quotient/residual shares components across exact outcomes; it is not beat phase or expressive timing ground truth.',
                         'Same eight have guided prior studies; any new condition requires a separate prospective proposal and review.']}
    output.mkdir(parents=True);(output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');return plan


def run(root,plan_path,output):
    if output.exists():raise ValueError('retain earlier result')
    start=time.process_time();p=json.loads(plan_path.read_text())
    for f,h in p['frozen_hashes'].items():
        if sha(REPO/f)!=h:raise ValueError('frozen dependency changed')
    if sha(root/'private-inventory.json')!=p['inventory_sha256']:raise ValueError('inventory changed')
    def budget():
        if time.process_time()-start>60:raise RuntimeError('diagnostic CPU bound exceeded')
    works={};paths={}
    for r in p['training']+p['diagnostics']:
        budget();path=(root/r['relative_path']).resolve()
        if not path.is_relative_to(root.resolve()):raise ValueError('unsafe path')
        events=read_events(path,r['sha256']);previous=0;work=[]
        for tick,key in events:work.append((tick-previous,key));previous=tick
        if len(work)!=r['event_count']:raise ValueError('source count')
        works[r['id']]=work;paths[r['id']]=path
    if sum(len(works[r['id']]) for r in p['training'])>30000:raise ValueError('train event bound')
    models={}
    for label,ids in [('baseline12',p['baseline_train_ids']),('deduplicated35',[r['id'] for r in p['training']])]:
        models[label]={c:DrumIOI35WorkProfile([works[i] for i in ids],condition=c) for c in CONDITIONS}
    oldm=models['baseline12']['quotient_context_k4_residual'];newm=models['deduplicated35']['quotient_context_k4_residual']
    oldseen=set(oldm.base.counts);newseen=set(newm.base.counts);assert oldseen<=newseen
    historical=json.loads((REPO/RESULT).read_text());cells=defaultdict(list);drummer=defaultdict(list);contextfreq=defaultdict(Counter);per=[];parities=0
    def bin_count(n):return '0' if n==0 else '1-9' if n<10 else '10-99' if n<100 else '100+'
    for r in p['diagnostics']:
        previous=None;loss={label:{c:[] for c in CONDITIONS} for label in models}
        for dt,key in works[r['id']]:
            budget();q,res=divmod(dt,120)
            a=oldm.base.contexts.get(previous,{});b=newm.base.contexts.get(previous,{})
            aq=oldm.contexts.get(previous,{});bq=newm.contexts.get(previous,{})
            labels={'global_exact_IOI_transition':transition(dt in oldseen,dt in newseen),
                    'local_exact_IOI_transition':'initial' if previous is None else transition(bool(a.get(dt,0)),bool(b.get(dt,0))),
                    'global_quotient_transition':transition(bool(oldm.quotients[q]),bool(newm.quotients[q])),
                    'local_quotient_transition':'initial' if previous is None else transition(bool(aq.get(q,0)),bool(bq.get(q,0))),
                    'global_residual_transition':transition(bool(oldm.residuals[res]),bool(newm.residuals[res])),
                    'previous_context_exposure_change':bin_count(sum(a.values()))+'->'+bin_count(sum(b.values())),
                    'previous_context_support_size_change':str(len(a))+'->'+str(len(b))}
            values={}
            for c in CONDITIONS:
                pair=[]
                for label in models:
                    x=-math.log(float(models[label][c].probability(dt,previous_instrument=previous)))
                    loss[label][c].append(x);pair.append(x)
                values[c]=tuple(pair)
            for dim,category in labels.items():cells[(r['drummer'],r['proposed_split'],dim,category)].append(values)
            drummer[(r['drummer'],r['proposed_split'])].append(values);contextfreq[r['drummer']][previous]+=1
            previous=key
        for label in models:
            for c in CONDITIONS:
                orig=next(x for x in historical['results'][label][c]['splits'][r['proposed_split']]['per_recording'] if x['id']==r['id'])
                assert math.fsum(loss[label][c])==orig['sum_nll_nats'];parities+=1
        per.append({'id':r['id'],'drummer':r['drummer'],'split':r['proposed_split'],'conditions':{c:summarize(list(zip(loss['baseline12'][c],loss['deduplicated35'][c]))) for c in CONDITIONS}})
    def allconditions(rows):return {c:summarize([x[c] for x in rows]) for c in CONDITIONS}
    partitions=[{'drummer':d,'split':s,'dimension':dim,'category':cat,'conditions':allconditions(rows)} for (d,s,dim,cat),rows in sorted(cells.items())]
    for (d,s),rows in drummer.items():
        for dim in p['dimensions']:assert sum(x['conditions']['unigram']['events'] for x in partitions if x['drummer']==d and x['dimension']==dim)==len(rows)
    contexts=set().union(*(set(c) for c in contextfreq.values()))
    if len(contexts)>129:raise ValueError('context bound')
    masses={};massrows=[];coefficients=[]
    for previous in sorted(contexts,key=lambda x:-1 if x is None else x):
        for label,condition_models in models.items():
            for c,model in condition_models.items():
                budget();mass=support_mass(model,previous,oldseen,newseen);assert sum(mass.values())==1
                masses[(previous,label,c)]=mass
                massrows.append({'previous_instrument':previous,'training':label,'condition':c,'mass':{k:fraction(v) for k,v in mass.items()}})
        for label,model in [('baseline12',oldm),('deduplicated35',newm)]:
            n=model.base.n;local=model.base.context_totals.get(previous,0)
            coefficients.append({'previous_instrument':previous,'training':label,'global_events':n,'local_events':local,'local_distinct_IOIs':len(model.base.contexts.get(previous,{})),
                'global_uniform_prior_weight':fraction(Fraction(1,n+1)),
                'exact_context_weights_if_known':{str(k):{'local_empirical':fraction(Fraction(local,local+k+1)),'global_empirical':fraction(Fraction(k,local+k+1)),'uniform_prior':fraction(Fraction(1,local+k+1))} for k in (4,32,256)} if local else None,
                'note':'Unknown/initial exact context uses global control. Quotient-context uses analogous k4 weights on quotient outcomes; residual factor is separately smoothed and legally truncated. These component weights must not be summed as one joint uniform prior.'})
    mixtures=[]
    for d,freq in sorted(contextfreq.items()):
        n=sum(freq.values())
        for label in models:
            for c in CONDITIONS:
                mix={kind:sum((Fraction(count,n)*masses[(prev,label,c)][kind] for prev,count in freq.items()),Fraction()) for kind in ('old_seen','newly_seen','still_unseen')}
                assert sum(mix.values())==1
                mixtures.append({'drummer':d,'events':n,'training':label,'condition':c,'mass':{k:fraction(v) for k,v in mix.items()}})
    for r in p['training']+p['diagnostics']:
        assert sha(paths[r['id']])==r['sha256']
    report={'plan_sha256':sha(plan_path),'exact_historical_NLL_checks':parities,'new_conditions_fit':False,'fixed_counts_reconstructed_only':True,'source_bytes_unchanged':True,
            'support_partition_counts':{'old_seen':len(oldseen),'newly_seen':len(newseen-oldseen),'still_unseen':30721-len(newseen)},
            'per_recording':per,'per_drummer':[{'drummer':d,'split':s,'recordings':2,'conditions':allconditions(rows)} for (d,s),rows in sorted(drummer.items())],
            'partitioned_loss_changes':partitions,'context_probability_masses':massrows,'observed_context_frequency_weighted_masses':mixtures,
            'context_prior_and_exposure_accounting':coefficients,'mass_scope':'Exact support partitions with same membership under both models. Drummer mixtures use observed context frequencies, not a generated trajectory probability.',
            'cpu_seconds':time.process_time()-start,'limitations':p['limitations']}
    output.mkdir(parents=True);(output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','run']);p.add_argument('--output',type=Path,required=True);p.add_argument('--root',type=Path);p.add_argument('--plan',type=Path);a=p.parse_args()
    if a.mode=='run' and (a.root is None or a.plan is None):p.error('run requires root and plan')
    print(json.dumps(prepare(a.output) if a.mode=='prepare' else run(a.root,a.plan,a.output),indent=2))

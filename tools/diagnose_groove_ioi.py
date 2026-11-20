"""Post-result decomposition of frozen sufficient counts; no model fit or tuning."""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
import json
import math
from pathlib import Path
from prepare_groove_split import read_events


def diagnose(root,plan_path,report_path):
    plan=json.loads(plan_path.read_text());report=json.loads(report_path.read_text())
    if sha256(plan_path.read_bytes()).hexdigest()!=report['plan_sha256']:raise ValueError('plan/report mismatch')
    works={}
    for r in plan['sources']:
        path=(root/r['relative_path']).resolve()
        if not path.is_relative_to(root.resolve()):raise ValueError('source path')
        events=read_events(path,r['sha256']);previous=0;work=[]
        for tick,key in events:work.append((tick-previous,key));previous=tick
        works[r['id']]=work
    counts=Counter();local=defaultdict(Counter)
    for r in plan['sources']:
        if r['proposed_split']!='train':continue
        previous=None
        for dt,key in works[r['id']]:
            counts[dt]+=1
            if previous is not None:local[previous][dt]+=1
            previous=key
    n=sum(counts.values());assert n==5034
    totals={k:sum(c.values()) for k,c in local.items()}
    buckets=defaultdict(list);per=[]
    for r in plan['sources']:
        if r['proposed_split']=='train':continue
        previous=None;loss0=[];loss1=[];work_buckets=defaultdict(list)
        for dt,key in works[r['id']]:
            status='initial' if previous is None else 'unknown' if previous not in local else 'known'
            global_seen=bool(counts[dt]);local_seen=bool(local[previous][dt]) if status=='known' else None
            category=f'context={status};global_seen={global_seen};local_seen={local_seen}'
            p0=(counts[dt]+Fraction(1,30721))/(n+1)
            p1=p0 if status!='known' else (local[previous][dt]+4*Fraction(counts[dt],n)+Fraction(1,30721))/(totals[previous]+5)
            a=-math.log(float(p0));b=-math.log(float(p1));loss0.append(a);loss1.append(b)
            buckets[(r['proposed_split'],category)].append((a,b));work_buckets[category].append((a,b))
            previous=key
        def summarize(values):
            a=math.fsum(x[0] for x in values);b=math.fsum(x[1] for x in values)
            return {'events':len(values),'control_sum_nll':a,'context_sum_nll':b,'context_minus_control_sum_nll':b-a,'context_minus_control_mean_nll':(b-a)/len(values)}
        for condition,loss in [('unigram',loss0),('previous_instrument_count_shrinkage_k4',loss1)]:
            original=next(x for x in report['results'][condition]['split_results'][r['proposed_split']]['per_performance'] if x['id']==r['id'])
            assert math.fsum(loss)==original['sum_nll_nats']
        per.append({'id':r['id'],'split':r['proposed_split'],'drummer':r['drummer'],'categories':{k:summarize(v) for k,v in sorted(work_buckets.items())}})
    return {'scope':'Posthoc decomposition of the already observed fixed result; original source-derived sufficient counts reconstructed for audit only, no model constructor, refit, retune or new evaluation cohort.',
            'plan_sha256':report['plan_sha256'],'results_sha256':sha256(report_path.read_bytes()).hexdigest(),
            'per_performance_original_nll_reproduced':True,'exact_float_sum_equality_all_16_work_condition_checks':True,'train_events':n,'context_transition_events':sum(totals.values()),
            'category_definition':'Mutually exclusive cross-tab of initial/unknown/known previous-instrument context, global IOI membership, and local IOI membership (None when context unavailable). Exact integer IOIs, no timing bins.',
            'split_categories':[{'split':s,'category':c,**summarize(v)} for (s,c),v in sorted(buckets.items())],
            'per_performance':per,'limitations':['Post-result explanatory bookkeeping, not causal evidence or a new independent test.',
            'Drummer, style labels, recording length, instrument distributions and finite exact-tick counts are confounded; no label is established as the cause.',
            'No parameter or candidate selection changes are authorized by these categories.']}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--plan',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('retain original diagnostic')
    a.output.write_text(json.dumps(diagnose(a.root,a.plan,a.report),indent=2)+'\n')

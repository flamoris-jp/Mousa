"""Authored synthetic construction benchmark; not legal/music ground truth."""
import argparse
from collections import Counter,defaultdict
from datetime import datetime,timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
from compare_onset_gate_models import phrases,similarity

SEEDS=tuple(range(2700,2708))
CATEGORIES=('transposition','time_scale','timing_jitter','insertions','deletions','seven_note_excerpt',
            'independent_scale','independent_repeat','independent_alternation','independent_random')


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def melody(seed):
    rng=random.Random(seed);p=[60]
    for _ in range(15):p.append(p[-1]+rng.choice((-3,-2,-1,1,2,3)))
    return dict(pitches=p,durations=[rng.choice((48,96,144,192)) for _ in p])


def cases():
    """All rules fixed independently of screen outcomes; fresh authored fixtures."""
    result=[]
    for seed in SEEDS:
        base=melody(seed);p=base['pitches'];d=base['durations']
        inserts=[];ids=[]
        for i,(pitch,duration) in enumerate(zip(p,d)):
            if i in (3,7,11):inserts.extend((pitch,pitch+5));ids.extend((duration//2,duration//2))
            else:inserts.append(pitch);ids.append(duration)
        transforms={
            'transposition':dict(pitches=[x+5 for x in p],durations=d.copy()),
            'time_scale':dict(pitches=p.copy(),durations=[x*2 for x in d]),
            'timing_jitter':dict(pitches=p.copy(),durations=[x+(1 if i%2 else -1) for i,x in enumerate(d)]),
            'insertions':dict(pitches=inserts,durations=ids),
            'deletions':dict(pitches=[x for i,x in enumerate(p) if i not in (3,7,11)],durations=[x for i,x in enumerate(d) if i not in (3,7,11)]),
            'seven_note_excerpt':dict(pitches=p[4:11],durations=d[4:11])}
        for category,target in transforms.items():
            result.append(dict(id=f'{seed}-{category}',seed=seed,category=category,construction='derived',reference=base,target=target))
        # Independent construction means no object/sequence transformation, NOT
        # independent musical provenance: both recipes deliberately share rules.
        for category in ('independent_scale','independent_repeat','independent_alternation'):
            def construct(offset,clock):
                ps=[offset+i for i in range(16)] if category=='independent_scale' else [offset]*16 if category=='independent_repeat' else [offset+(i%2)*2 for i in range(16)]
                return dict(pitches=ps,durations=[clock]*16)
            result.append(dict(id=f'{seed}-{category}',seed=seed,category=category,construction='independent_recipe',
                reference=construct(50+seed%3,48),target=construct(68+seed%5,144)))
        result.append(dict(id=f'{seed}-independent_random',seed=seed,category='independent_random',construction='independent_recipe',reference=base,target=melody(seed+10000)))
    return result


def inspect(case):
    a,b=case['reference'],case['target'];pa,pb=a['pitches'],b['pitches']
    if not 1<=len(pa)<=64 or not 1<=len(pb)<=64:raise ValueError('synthetic bound')
    exact=len(phrases(pa)&phrases(pb));global_score=similarity(pa,pb)
    blocked=bool(exact or global_score is not None and global_score>=.80)
    iva=[y-x for x,y in zip(pa,pa[1:])];ivb=[y-x for x,y in zip(pb,pb[1:])]
    locations=[];total=0;rhythm_exact=0;rhythm_scaled=0
    for i in range(len(pa)-7):
        for j in range(len(pb)-7):
            if iva[i:i+7]!=ivb[j:j+7]:continue
            total+=1;ra=a['durations'][i:i+7];rb=b['durations'][j:j+7]
            same=ra==rb;scaled=[Fraction(x,ra[0]) for x in ra]==[Fraction(x,rb[0]) for x in rb]
            rhythm_exact+=same;rhythm_scaled+=scaled
            if len(locations)<8:locations.append(dict(reference_note_index=i,target_note_index=j,intervals=iva[i:i+7],
                reference_onset_deltas=ra,target_onset_deltas=rb,exact_rhythm=same,scale_normalized_rhythm=scaled))
    return dict(id=case['id'],seed=case['seed'],category=case['category'],construction=case['construction'],
        blocked=blocked,unique_exact8_interval_matches=exact,global_interval_similarity=global_score,
        exact8_location_pairs=total,exact_rhythm_location_pairs=rhythm_exact,scaled_rhythm_location_pairs=rhythm_scaled,
        locations=locations,locations_truncated=total>8)


def summarize(rows):
    out={}
    for category in CATEGORIES:
        selected=[r for r in rows if r['category']==category];blocked=sum(r['blocked'] for r in selected)
        label=selected[0]['construction'] if selected else None
        out[category]=dict(denominator=len(selected),blocked=blocked,passed=len(selected)-blocked,construction=label,
            constructed_misses=len(selected)-blocked if label=='derived' else None,
            constructed_false_alarms=blocked if label=='independent_recipe' else None)
    return out


def prepare(root,output):
    if output.exists():raise ValueError('new plan directory required')
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),scope='New authored synthetic construction cases; not population error rates or legal/music truth',
        seeds=list(SEEDS),notes=16,cases_per_category=8,categories=list(CATEGORIES),
        transforms='transpose+5;time-scale2;alternating+-1duration;insert+5afterindices3/7/11splittingduration;deleteindices3/7/11;excerpt[4:11]',
        independent_recipes='Shared common-scale/repeat/alternation recipes generated separately with different pitch offsets/clocks; random-control seeds+10000',
        gate='Unchanged production exact7-interval (=8note) overlap OR wholeinterval edit similarity>=.80',
        diagnostics='All interval-match location pair counts; first8locations with exact and normalized onset-rhythm comparisons; rhythm never changes gate',
        reference_truth='Derived transformations vs independently executed recipes are construction labels only, not plagiarism, perceptual similarity or musical independence.',
        prior_cycle20='Previous15examples already observed; none reused bytewise; categories motivated by that work, not unobserved hypotheses.',
        no_real_source_application=True,no_threshold_tuning=True,no_blocked_candidate_release=True,
        code_sha256={p:digest(root/p) for p in ['tools/benchmark_similarity_gate.py','tools/compare_onset_gate_models.py','tests/test_similarity_gate_benchmark.py']})
    output.mkdir(parents=True);(output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    # Construction only, no screen calls before plan persisted.
    (output/'fixtures.json').write_text(json.dumps(cases(),indent=2)+'\n')


def run(root,plan_dir,output):
    if output.exists():raise ValueError('new result required')
    plan=json.loads((plan_dir/'plan.json').read_text())
    for p,sha in plan['code_sha256'].items():
        if digest(root/p)!=sha:raise ValueError('frozen code changed')
    fixtures=json.loads((plan_dir/'fixtures.json').read_text())
    if fixtures!=cases():raise ValueError('fixture construction changed')
    rows=[inspect(c) for c in fixtures]
    report=dict(plan_sha256=digest(plan_dir/'plan.json'),fixtures_sha256=digest(plan_dir/'fixtures.json'),
        rows=rows,strata=summarize(rows),case_count=len(rows),
        limits=['Eight variants per stratum are not population error rates or independent musical works.',
                'Common-pattern false alarms refer only to constructed no-transform labels; common recipe sharing is intentional.',
                'Derived misses do not establish legal copying or perceptual identity.',
                'No production threshold change, no real-source rescoring or release.'])
    output.mkdir(parents=True);(output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['strata'],indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',choices=['prepare','run'],required=True)
    p.add_argument('--plan-dir',type=Path,required=True);p.add_argument('--output',type=Path);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    if a.stage=='prepare':prepare(root,a.plan_dir)
    else:
        if a.output is None:p.error('run requires output')
        run(root,a.plan_dir,a.output)

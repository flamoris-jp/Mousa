"""Synthetic fixed-outcome duration experiment, no corpus access or fitting."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import random
from mousa.duration_support import DurationSupport, DurationSupportError


def run():
    # Artificial values only. Includes unseen ornaments and incompatible septuplet.
    train = [Fraction(x,384) for x in [96,96,192,384,384,384,12]]
    probe = [Fraction(x,384) for x in [96,192,384,12,22,1]] + [Fraction(1,7),Fraction(33)]
    model=DurationSupport(train)
    counts=Counter(int(d*384) for d in train)
    rows=[]
    for duration in probe:
        row={'quarter_duration':str(duration),'classification':model.classify(duration),
             'sixteenth_exact':(duration*4).denominator==1}
        try:
            p=model.probability(duration)
            ticks=int(duration*384)
            integer_p=(counts[ticks]+Fraction(1,12288))/8
            assert p==integer_p
            row.update(probability=str(p),integer_tick_probability=str(integer_p),nll=-math.log(float(p)))
        except DurationSupportError as exc:
            row.update(rejected=str(exc),probability=None)
        rows.append(row)
    def generate(seed):
        rng=random.Random(seed);remaining=384*24;seq=[]
        # Hard event-count bound: failure, never silently repair, if exceeded.
        for _ in range(4096):
            if not remaining:return seq
            d=model.sample(rng,remaining_ticks=remaining,max_duration_ticks=384*2)
            ticks=model.to_ticks(d);assert 1<=ticks<=min(remaining,768)
            seq.append(ticks);remaining-=ticks
        raise RuntimeError('bounded generation did not fill target')
    samples=[generate(seed) for seed in range(20)]
    assert samples==[generate(seed) for seed in range(20)]
    assert all(sum(s)==9216 for s in samples)
    # Independent integer-label sampler, same inverse-CDF order and RNG draws.
    def integer_generate(seed):
        rng=random.Random(seed);remaining=9216;seq=[]
        for _ in range(4096):
            if remaining==0:return seq
            upper=min(remaining,768);legal=sorted((t,c) for t,c in counts.items() if t<=upper)
            draw=rng.randrange(sum(c for _,c in legal)*12288+upper)
            for tick,count in legal:
                if draw<count*12288:break
                draw-=count*12288
            else:tick=draw+1
            seq.append(tick);remaining-=tick
        raise RuntimeError('integer-label generation bound')
    assert samples==[integer_generate(seed) for seed in range(20)]
    repo=Path(__file__).resolve().parents[1]
    return {'scope':'Synthetic duration contract, not music quality or unseen-work evaluation',
        'source_music_used':False,'support_size':12288,'synthetic_training_observations':len(train),
        'probability_mass':str(sum((model.probability(Fraction(t,384)) for t in range(1,12289)),Fraction())),
        'probe':rows,'probe_coverage':{'common_support':6,'sixteenth_only':3,'total':8,
            'note':'Sixteenth count excludes the over-range 33-quarter probe; exact grid alone is insufficient'},
        'generation':{'seeds':list(range(20)),'target_ticks':9216,'duration_cap_ticks':768,
            'all_exact_end':True,'representation_samples_identical':True,
            'event_counts':[len(s) for s in samples],
            'sample_sha256':hashlib.sha256(json.dumps(samples,separators=(',',':')).encode()).hexdigest()},
        'code_sha256':{p:hashlib.sha256((repo/p).read_bytes()).hexdigest() for p in
            ['src/mousa/duration_support.py','tools/compare_duration_support.py','experiments/2026-11-12-duration-comparison-plan.json']},
        'limitations':['Uniform tick prior is not uniform over reduced rational denominators.',
            'Duration-only IID counts do not model meter, ornament semantics, phrase or pitch.',
            'Generation is conditioned on remaining length; displayed NLL is unconditional.',
            'Coarse control conditional likelihood is deliberately not reported as comparable.',
            'No source events have been rounded, split, deleted or reused as fresh test data.']}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('new output path required')
    report=run();a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['generation']))

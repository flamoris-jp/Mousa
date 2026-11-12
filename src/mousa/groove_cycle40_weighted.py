"""Two fixed marginal timing laws with exact mass-preserving group weighting.

No previous-instrument context or transition model is introduced. Full source
work boundaries and original events are validated; weights apply per event of
an entire training performance. No sampler, generation or authority API.
"""
from collections import Counter
from fractions import Fraction
import math
from mousa.drum_ioi_baseline import validate_work

CONDITIONS=('unigram','quotient_residual')
SUPPORT=30721
UNIT=120


def equal_group_weights(lengths,groups):
    if type(lengths) not in (list,tuple) or type(groups) not in (list,tuple) or not 1<=len(lengths)<=60 or len(lengths)!=len(groups):raise ValueError('aligned bounded work metadata required')
    if any(type(n) is not int or not 1<=n<=4096 for n in lengths) or sum(lengths)>60000:raise ValueError('event bounds')
    if any(type(g) is not str or not 1<=len(g)<=64 for g in groups) or len(set(groups))>6:raise ValueError('one to six explicit groups required')
    totals=Counter()
    for n,g in zip(lengths,groups):totals[g]+=n
    total=sum(lengths);number=len(totals)
    return [Fraction(total,number*totals[g]) for g in groups]


class WeightedGrooveMarginal:
    def __init__(self,works,weights,*,condition):
        if condition not in CONDITIONS:raise ValueError('two fixed marginal conditions only')
        if type(works) not in (list,tuple) or not 1<=len(works)<=60 or type(weights) not in (list,tuple) or len(weights)!=len(works):raise ValueError('bounded aligned works/weights')
        if any(type(w) not in (list,tuple) for w in works) or sum(len(w) for w in works)>60000:raise ValueError('raw event bound')
        for work in works:validate_work(work)
        if any(type(w) is not Fraction or w<=0 or w.numerator>10**9 or w.denominator>10**9 for w in weights):raise ValueError('bounded positive exact Fraction weights')
        total=sum(map(len,works));mass=sum((len(work)*weight for work,weight in zip(works,weights)),Fraction())
        if mass!=total:raise ValueError('total effective event mass must equal raw event count')
        self.n=mass;self.raw_events=total;self.work_count=len(works);self.condition=condition
        self.counts=Counter();self.quotients=Counter();self.residuals=Counter()
        for work,weight in zip(works,weights):
            for dt,key in work:
                self.counts[dt]+=weight;q,r=divmod(dt,UNIT)
                self.quotients[q]+=weight;self.residuals[r]+=weight
        self.residual_mass={cap:sum((self.residuals[r] for r in range(cap)),Fraction())+Fraction(cap,UNIT) for cap in (1,UNIT)}

    def probability(self,dt):
        if type(dt) is not int or not 0<=dt<SUPPORT:raise ValueError('exact IOI support')
        if self.condition=='unigram':return (self.counts[dt]+Fraction(1,SUPPORT))/(self.n+1)
        q,r=divmod(dt,UNIT);cap=min(UNIT,SUPPORT-q*UNIT)
        return ((self.quotients[q]+Fraction(cap,SUPPORT))/(self.n+1))*((self.residuals[r]+Fraction(1,UNIT))/self.residual_mass[cap])

    def evaluate(self,work):
        validate_work(work);loss=[-math.log(float(self.probability(dt))) for dt,key in work]
        return {'events':len(work),'sum_nll_nats':math.fsum(loss),'mean_nll_nats':math.fsum(loss)/len(work)}

"""Explicit35-work/30000-event profile; unchanged Cycle34 predictive formulas.

Standalone rather than silently raising a frozen constructor bound. Only safe
probability/evaluate operations are delegated. No sampler or generation API.
Each validation chunk and every original work has independent context resets.
"""
from collections import Counter,defaultdict
from fractions import Fraction
from types import SimpleNamespace
from mousa.drum_ioi_baseline import DrumIOIModel
from mousa.drum_ioi_multiscale import MultiscaleDrumIOI,CONDITIONS,UNIT


class DrumIOI35WorkProfile:
    def __init__(self,works,*,condition):
        if condition not in CONDITIONS:raise ValueError('fixed condition required')
        if type(works) not in (tuple,list) or not 1<=len(works)<=35:raise ValueError('explicit35-work bound')
        if any(type(w) not in (tuple,list) for w in works) or sum(len(w) for w in works)>30000:raise ValueError('original30000-event bound')
        chunks=[DrumIOIModel(works[i:i+20],context=True) for i in range(0,len(works),20)]
        counts=Counter();contexts=defaultdict(Counter)
        for chunk in chunks:
            counts.update(chunk.counts)
            for key,c in chunk.contexts.items():contexts[key].update(c)
        self.base=SimpleNamespace(n=sum(counts.values()),counts=counts,contexts=contexts,
                                  context_totals={k:sum(c.values()) for k,c in contexts.items()},work_count=len(works))
        self.condition=condition;self.quotients=Counter();self.residuals=Counter();self.contexts=defaultdict(Counter)
        for work in works:
            previous=None
            for dt,key in work:
                q,r=divmod(dt,UNIT);self.quotients[q]+=1;self.residuals[r]+=1
                if previous is not None:self.contexts[previous][q]+=1
                previous=key
        self.context_totals={k:sum(c.values()) for k,c in self.contexts.items()}
        self.residual_mass={cap:sum(self.residuals[r] for r in range(cap))+Fraction(cap,UNIT) for cap in (1,UNIT)}

    def probability(self,dt,*,previous_instrument=None):
        return MultiscaleDrumIOI.probability(self,dt,previous_instrument=previous_instrument)

    def evaluate(self,work):
        return MultiscaleDrumIOI.evaluate(self,work)

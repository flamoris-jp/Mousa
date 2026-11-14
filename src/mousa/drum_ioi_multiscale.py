"""Observed-cohort rhythm diagnostics: stronger count backoff and exact q/r joint.

Unit120 is a fixed IOI decomposition, not inferred beat phase or expressive
microtiming. Every original integer dt is retained as dt=120*q+r. The final
q=256 admits only r=0; residual probabilities are renormalized on that support.
"""
from collections import Counter, defaultdict
from fractions import Fraction
import math
from mousa.drum_ioi_baseline import DrumIOIModel, validate_work, SUPPORT_SIZE, MAX_IOI

CONDITIONS=('unigram','exact_k4','exact_k32','exact_k256','quotient_residual','quotient_context_k4_residual')
UNIT=120


class MultiscaleDrumIOI:
    def __init__(self,works,*,condition):
        if condition not in CONDITIONS:raise ValueError('fixed condition required')
        # Existing validation/count boundaries; no mutation of frozen model.
        self.base=DrumIOIModel(works,context=True)
        self.condition=condition
        self.quotients=Counter();self.residuals=Counter();self.contexts=defaultdict(Counter)
        for work in works:
            previous=None
            for dt,key in work:
                q,r=divmod(dt,UNIT)
                self.quotients[q]+=1;self.residuals[r]+=1
                if previous is not None:self.contexts[previous][q]+=1
                previous=key
        self.context_totals={k:sum(c.values()) for k,c in self.contexts.items()}
        self.residual_mass={cap:sum(self.residuals[r] for r in range(cap))+Fraction(cap,UNIT) for cap in (1,UNIT)}

    def probability(self,dt,*,previous_instrument=None):
        # Validates exact dt/context bounds and supplies shared control.
        if type(dt) is not int or not 0<=dt<=MAX_IOI:raise ValueError('IOI support')
        if previous_instrument is not None and (type(previous_instrument) is not int or not 0<=previous_instrument<=127):raise ValueError('instrument support')
        n=self.base.n;prior=Fraction(1,SUPPORT_SIZE);global_count=self.base.counts[dt]
        known=previous_instrument in self.base.contexts
        if self.condition=='unigram' or self.condition.startswith('exact_') and not known:
            return (global_count+prior)/(n+1)
        if self.condition.startswith('exact_'):
            k=int(self.condition.split('k')[1]);local=self.base.contexts[previous_instrument]
            return (local[dt]+k*Fraction(global_count,n)+prior)/(self.base.context_totals[previous_instrument]+k+1)
        q,r=divmod(dt,UNIT);cap=min(UNIT,MAX_IOI-q*UNIT+1);qprior=Fraction(cap,SUPPORT_SIZE)
        if self.condition=='quotient_context_k4_residual' and known:
            pq=(self.contexts[previous_instrument][q]+4*Fraction(self.quotients[q],n)+qprior)/(self.context_totals[previous_instrument]+5)
        else:pq=(self.quotients[q]+qprior)/(n+1)
        pr=(self.residuals[r]+Fraction(1,UNIT))/self.residual_mass[cap]
        return pq*pr

    def evaluate(self,work):
        validate_work(work);previous=None;loss=[]
        for dt,key in work:
            loss.append(-math.log(float(self.probability(dt,previous_instrument=previous))))
            previous=key
        return {'events':len(work),'sum_nll_nats':math.fsum(loss),'mean_nll_nats':math.fsum(loss)/len(work)}

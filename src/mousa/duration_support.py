"""Fixed exact PPQ duration support, independent of observed vocabulary.

A bounded research counting distribution, not a musical-quality model.
Out-of-support durations are explicitly classified, never quantized. Sampling
conditions on feasible durations without clipping or expanding the support.
"""
from collections import Counter
from fractions import Fraction
import random


class DurationSupportError(ValueError):
    """A positive rational duration lies outside the declared fixed support."""


class DurationSupport:
    def __init__(self, durations=(), *, ppq=384, max_quarters=32, prior_mass=Fraction(1)):
        if type(ppq) is not int or not 1 <= ppq <= 32767:
            raise ValueError('integer PPQ in 1..32767 required')
        if type(max_quarters) is not int or not 1 <= max_quarters <= 32:
            raise ValueError('integer max_quarters in 1..32 required')
        if type(prior_mass) is int:
            prior_mass=Fraction(prior_mass)
        if type(prior_mass) is not Fraction or not 0 < prior_mass <= 1000000:
            raise ValueError('positive exact rational prior mass <=1000000 required')
        if prior_mass.denominator>1000000:
            raise ValueError('prior denominator exceeds bound')
        if not isinstance(durations,(list,tuple)) or len(durations)>100000:
            raise ValueError('bounded duration list/tuple required')
        self.ppq,self.max_quarters,self.prior_mass=ppq,max_quarters,prior_mass
        self.support_size=ppq*max_quarters
        self.counts=Counter(self.to_ticks(d) for d in durations)
        self.observations=sum(self.counts.values())

    def classify(self, duration):
        """Return seen/unseen, incompatible_grid, or outside_duration_range.

        Invalid input types/nonpositive values raise rather than becoming OOV.
        Incompatible grid takes precedence over range when both fail.
        """
        if type(duration) is not Fraction or duration<=0:
            raise ValueError('positive Fraction duration required')
        if duration.denominator>32767 or duration.numerator>32767*1024:
            raise ValueError('duration rational components exceed research bounds')
        ticks=duration*self.ppq
        if ticks.denominator!=1:return 'incompatible_grid'
        if not 1<=ticks<=self.support_size:return 'outside_duration_range'
        return 'seen' if self.counts.get(int(ticks),0) else 'unseen'

    def to_ticks(self,duration):
        # During fitting counts does not exist yet; avoid observed-vocabulary use.
        if type(duration) is not Fraction or duration<=0:
            raise ValueError('positive Fraction duration required')
        if duration.denominator>32767 or duration.numerator>32767*1024:
            raise ValueError('duration rational components exceed research bounds')
        ticks=duration*self.ppq
        if ticks.denominator!=1:raise DurationSupportError('incompatible_grid')
        if not 1<=ticks<=self.support_size:raise DurationSupportError('outside_duration_range')
        return int(ticks)

    def probability(self,duration):
        ticks=self.to_ticks(duration)
        return (self.counts[ticks]+self.prior_mass/self.support_size)/(self.observations+self.prior_mass)

    def sample(self, rng, *, remaining_ticks, max_duration_ticks=None):
        """Sample the exact conditional distribution with sparse integer weights.

        rng must be random.Random. No floating probabilities or large support
        array: draw either an empirical observation or a uniform legal tick.
        Returns Fraction quarter-note duration. Zero remaining time is invalid.
        """
        if not isinstance(rng,random.Random):raise ValueError('random.Random required')
        if type(remaining_ticks) is not int or not 1<=remaining_ticks<=self.ppq*1024:
            raise ValueError('bounded positive remaining_ticks required')
        if max_duration_ticks is not None and (type(max_duration_ticks) is not int
                or not 1<=max_duration_ticks<=self.support_size):
            raise ValueError('max_duration_ticks must lie within fixed support')
        upper=min(remaining_ticks,self.support_size,
                  self.support_size if max_duration_ticks is None else max_duration_ticks)
        legal=[(t,c) for t,c in sorted(self.counts.items()) if t<=upper]
        # Scale each empirical count by denominator*support_size and each
        # uniform tick by numerator. This is exactly the restricted mass.
        scale=self.prior_mass.denominator*self.support_size
        observed=sum(c for _,c in legal)*scale
        draw=rng.randrange(observed+self.prior_mass.numerator*upper)
        if draw>=observed:
            tick=1+(draw-observed)//self.prior_mass.numerator
        else:
            for tick,count in legal:
                draw-=count*scale
                if draw<0:break
        return Fraction(tick,self.ppq)

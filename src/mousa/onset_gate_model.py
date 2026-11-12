"""Synthetic-ready exact timing comparison on a fixed shared Cartesian support.

PPQ384, onset delta0..12288, gate1..12288. Uniform total prior mass1.
Joint and independent-marginal variants describe the SAME outcomes; this is
not a polyphonic musical-quality model. Generation constraints are separate
from unconditional evaluation. No quantization, clipping or source fitting here.
"""
from collections import Counter
from fractions import Fraction
import math
import random

PPQ=384
MAX_TICKS=12288
DT_SIZE=MAX_TICKS+1
GATE_SIZE=MAX_TICKS
SUPPORT_SIZE=DT_SIZE*GATE_SIZE


def _pair(pair):
    if type(pair) is not tuple or len(pair)!=2:raise ValueError('timing pair tuple required')
    dt,gate=pair
    if type(dt) is not int or type(gate) is not int or not 0<=dt<=MAX_TICKS or not 1<=gate<=MAX_TICKS:
        raise ValueError('timing outside fixed integer-tick support; no rounding')
    return pair


def _pairs(pairs,empty=False):
    if not isinstance(pairs,(list,tuple)) or not (0 if empty else 1)<=len(pairs)<=100000:
        raise ValueError('bounded timing sequence required')
    for pair in pairs:_pair(pair)


class OnsetGateModel:
    def __init__(self,pairs,*,factorized=False):
        _pairs(pairs,empty=True)
        if type(factorized) is not bool:raise ValueError('boolean factorized required')
        self.factorized=factorized
        self.counts=Counter(pairs);self.dt_counts=Counter(dt for dt,_ in pairs)
        self.gate_counts=Counter(g for _,g in pairs);self.n=len(pairs)

    def probability(self,pair):
        dt,g=_pair(pair)
        if self.factorized:
            return Fraction(self.dt_counts[dt]*DT_SIZE+1,(self.n+1)*DT_SIZE)*Fraction(self.gate_counts[g]*GATE_SIZE+1,(self.n+1)*GATE_SIZE)
        return Fraction(self.counts[pair]*SUPPORT_SIZE+1,(self.n+1)*SUPPORT_SIZE)

    def evaluate(self,pairs):
        _pairs(pairs)
        return dict(events=len(pairs),nll_per_event=sum(-math.log(self.probability(p)) for p in pairs)/len(pairs),
                    support_size=SUPPORT_SIZE,ppq=PPQ,conditional_generation_masks_applied=False)

    def sample_pair(self,rng,*,remaining_ticks):
        """Exact conditional draw over dt+gate<=remaining_ticks; integer weights.

        Never allocates the Cartesian support. Factorized mode traverses at
        most12289 delta values and sparse gate counts; joint uses sparse pairs.
        """
        if not isinstance(rng,random.Random):raise ValueError('random.Random required')
        if type(remaining_ticks) is not int or not 1<=remaining_ticks<=PPQ*1024:
            raise ValueError('bounded positive remaining_ticks required')
        upper=min(MAX_TICKS,remaining_ticks-1)
        gate_counts=sorted(self.gate_counts.items())
        gate_prefix=[];running=0;index=0
        # Ascending gate cap, enabling one pass over sparse observed gates.
        for cap in range(1,MAX_TICKS+1):
            while index<len(gate_counts) and gate_counts[index][0]<=cap:
                running+=gate_counts[index][1];index+=1
            gate_prefix.append(running)
        if self.factorized:
            masses=[(self.dt_counts[d]*DT_SIZE+1)*(gate_prefix[min(MAX_TICKS,remaining_ticks-d)-1]*GATE_SIZE+min(MAX_TICKS,remaining_ticks-d))
                    for d in range(upper+1)]
        else:
            by_delta=Counter()
            for (d,g),count in self.counts.items():
                if d+g<=remaining_ticks:by_delta[d]+=count
            masses=[by_delta[d]*SUPPORT_SIZE+min(MAX_TICKS,remaining_ticks-d) for d in range(upper+1)]
        draw=rng.randrange(sum(masses))
        for dt,mass in enumerate(masses):
            if draw<mass:break
            draw-=mass
        cap=min(MAX_TICKS,remaining_ticks-dt)
        if self.factorized:
            observed=[(g,c) for g,c in gate_counts if g<=cap];scale=GATE_SIZE
        else:
            observed=sorted((g,c) for (d,g),c in self.counts.items() if d==dt and g<=cap);scale=SUPPORT_SIZE
        draw=rng.randrange(sum(c for _,c in observed)*scale+cap)
        for gate,count in observed:
            if draw<count*scale:return dt,gate
            draw-=count*scale
        return dt,draw+1

    def generate(self,seed,*,target_ticks,pitches,max_notes=256,max_attempts=64):
        """Timing then uniform pitch from caller-supplied training vocabulary.

        Gates may overlap, but same-pitch retriggers while active reject and
        positive-duration polyphony is bounded3. Success means at least one
        gate ends exactly at target; other notes cannot exceed it. This may
        finish with sustained notes and does not imply a phrase or cadence.
        Exhausted attempts or note budget returns explicit blocked partial data.
        """
        if type(seed) is not int or type(target_ticks) is not int or not 1<=target_ticks<=PPQ*1024:
            raise ValueError('bounded target and integer seed required')
        if type(max_notes) is not int or not 1<=max_notes<=256 or type(max_attempts) is not int or not 1<=max_attempts<=64:
            raise ValueError('bounded generation budgets required')
        if not isinstance(pitches,(list,tuple)) or not 1<=len(pitches)<=128 or any(type(p) is not int or not 0<=p<=127 for p in pitches):
            raise ValueError('explicit bounded training-pitch vocabulary required')
        vocabulary=sorted(set(pitches));rng=random.Random(seed);notes=[];previous=0;rejections=0
        for _ in range(max_notes):
            for _ in range(max_attempts):
                dt,gate=self.sample_pair(rng,remaining_ticks=target_ticks-previous)
                start=previous+dt;end=start+gate;pitch=rng.choice(vocabulary)
                active=[n for n in notes if n['end']>start]
                if len(active)>=3 or any(n['pitch']==pitch for n in active):
                    rejections+=1;continue
                notes.append(dict(start=start,end=end,pitch=pitch));previous=start
                if end==target_ticks:
                    return dict(status='complete',notes=notes,rejections=rejections,target_ticks=target_ticks)
                break
            else:return dict(status='blocked',notes=notes,rejections=rejections,reason='attempt budget exhausted')
        return dict(status='blocked',notes=notes,rejections=rejections,reason='note budget exhausted')

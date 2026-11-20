"""Music-specific empirical onset-group weighting, not a generic ML core.

Separate first/later/template pools, with exact count/prior scaling. No inherited
old sampling API: only this module's bounded generator accepts this model.
"""
from collections import Counter
from fractions import Fraction
from math import lcm,log,isfinite
from time import process_time
import random
from mousa.initial_rest_group_model import validate
from mousa.group_onset_model import _draw

MODES=('raw','equal_work','equal_family')
BITS=2048

def integerize(counts,default=None):
    """Scale ALL probabilities, including unseen prior, by the same denominator."""
    values=list(counts.values())+([] if default is None else [default]);scale=1
    for value in values:
        if not isinstance(value,Fraction) or value<0:raise ValueError('nonnegative Fraction masses')
        scale=lcm(scale,value.denominator)
        if scale.bit_length()>BITS:raise ValueError('integer scaling budget exceeded')
    out={k:int(v*scale) for k,v in counts.items()}
    fallback=None if default is None else int(default*scale)
    if any(v.bit_length()>BITS for v in out.values()) or (fallback is not None and fallback.bit_length()>BITS):raise ValueError('integer mass budget exceeded')
    return out,fallback,scale

def pool_weights(lengths,families,mode,mass):
    if not isinstance(lengths,(list,tuple)) or not 1<=len(lengths)<=32 or not isinstance(families,(list,tuple)) or len(lengths)!=len(families) or any(type(n) is not int or not 0<=n<=4096 for n in lengths) or any(type(f) is not str or not f for f in families):
        raise ValueError('bounded pool lengths/family labels')
    if mode not in MODES or type(mass) is not int or not 1<=mass<=100000:
        raise ValueError('fixed mode and positive bounded mass')
    active=[i for i,n in enumerate(lengths) if n]
    if not active:raise ValueError('empty whole pool cannot have positive mass')
    if mode=='raw':return [Fraction(mass,sum(lengths)) if n else Fraction() for n in lengths]
    if mode=='equal_work':return [Fraction(mass,len(active)*n) if n else Fraction() for n in lengths]
    totals=Counter()
    for n,f in zip(lengths,families):totals[f]+=n
    activefamilies=sum(v>0 for v in totals.values())
    return [Fraction(mass,activefamilies*totals[f]) if n else Fraction() for n,f in zip(lengths,families)]

class WeightedGroupModel:
    def __init__(self,sequences,families,*,mode='raw',masses=(17,3411,3428)):
        if type(sequences) is not list or not 1<=len(sequences)<=32 or not isinstance(families,(tuple,list)) or len(families)!=len(sequences):
            raise ValueError('bounded aligned works/families')
        if any(type(f) is not str or not 1<=len(f)<=128 for f in families):raise ValueError('declared family labels required')
        if not isinstance(masses,(tuple,list)) or len(masses)!=3:raise ValueError('three pool masses')
        for seq in sequences:validate(seq,65536)
        if sum(len(s) for s in sequences)>100000 or sum(len(t) for s in sequences for _,_,t in s)>100000:raise ValueError('source budget')
        lengths=([1]*len(sequences),[len(s)-1 for s in sequences],[len(s) for s in sequences])
        self.pool_weights=[pool_weights(ns,families,mode,m) for ns,m in zip(lengths,masses)]
        self.first=Counter();self.later=Counter();self.template_counts=Counter();self.anchor_counts=Counter()
        for i,seq in enumerate(sequences):
            self.first[seq[0][0]]+=self.pool_weights[0][i]
            for delta,_,_ in seq[1:]:self.later[delta]+=self.pool_weights[1][i]
            for _,anchor,template in seq:
                self.template_counts[template]+=self.pool_weights[2][i];self.anchor_counts[anchor]+=self.pool_weights[2][i]
        self.masses=tuple(masses);self.cache={};self.first_limit=65536
        self.templates,_,self.template_scale=integerize(self.template_counts)
        self.anchors,_,self.anchor_scale=integerize(self.anchor_counts)
        self.template_occurrences=sum(self.template_counts.values())
        self.ineligible_occurrences=sum(v for t,v in self.template_counts.items() if len(t)>3)
    def parameters(self,previous):
        first=previous is None;key=first
        if key not in self.cache:
            size=65537 if first else 12288;counts=self.first if first else self.later
            # Each explicit mass c*S+1; unseen prior1, scale together.
            explicit={d:c*size+1 for d,c in counts.items()}
            weights,default,scale=integerize(explicit,Fraction(1))
            self.cache[key]=(0 if first else 1,weights,default,scale)
        return self.cache[key]
    def probability(self,delta,previous=None):
        lo,weights,default,_=self.parameters(previous);hi=65536 if previous is None else 12288
        if type(delta) is not int or not lo<=delta<=hi:raise ValueError('stage support')
        total=sum(weights.values())+(hi-lo+1-len(weights))*default
        return Fraction(weights.get(delta,default),total)
    def sample_delta(self,rng,previous,remaining):
        if type(remaining) is not int or not 0<=remaining<=9216:raise ValueError('remaining output bound')
        lo,weights,default,_=self.parameters(previous);hi=min(65536 if previous is None else 12288,remaining-1)
        if hi<lo:return None
        total=(hi-lo+1)*default+sum(v-default for d,v in weights.items() if lo<=d<=hi)
        draw=rng.randrange(total)
        for d in range(lo,hi+1):
            weight=weights.get(d,default)
            if draw<weight:return d
            draw-=weight
        raise AssertionError('bounded draw')
    def advance(self,horizon,delta,template):
        return max(horizon-delta,max(t[1] for t in template)),1
    def evaluate(self,seq):
        validate(seq,65536);first=-log(self.probability(seq[0][0]))
        later=sum(-log(self.probability(d,1)) for d,_,_ in seq[1:])
        return dict(groups=len(seq),first_nll=first,later_nll_sum=later,nll_per_group_delta=(first+later)/len(seq))


def generate(model,seed,*,target=9216,tail=384,max_notes=256,max_attempts=64,cpu_deadline=None):
    if not isinstance(model,WeightedGroupModel) or type(seed) is not int:raise ValueError('model/seed required')
    if any(type(x) is not int for x in (target,tail,max_notes,max_attempts)) or not 1<=target<=9216 or not 0<=tail<=min(384,target-1) or not 1<=max_notes<=256 or not 1<=max_attempts<=64:
        raise ValueError('bounded generation required')
    if cpu_deadline is not None and (type(cpu_deadline) not in (int,float) or not isfinite(cpu_deadline) or cpu_deadline<0):
        raise ValueError('finite nonnegative CPU deadline required')
    templates=Counter({t:n for t,n in model.templates.items() if len(t)<=3})
    rng=random.Random(seed);notes=[];groups=[];previous=0;previous_count=None;horizon=0;rejects=Counter();attempts=0
    def finish(status,reason=None):
        return dict(status=status,reason=reason,notes=notes,groups=groups,attempts=attempts,rejections=dict(rejects),
                    ineligible_template_occurrences=float(model.ineligible_occurrences),total_template_occurrences=float(model.template_occurrences),
                    available_template_types=len(templates),target_ticks=target,
                    actual_tail=target-max(n['end'] for n in notes) if notes else None)
    if not templates:return finish('blocked','no <=3-note template')
    for _ in range(max_notes):
        accepted=False
        for _ in range(max_attempts):
            if cpu_deadline is not None and process_time()>=cpu_deadline:return finish('cpu_budget_exhausted','shared CPU deadline reached before next bounded proposal')
            attempts+=1;delta=model.sample_delta(rng,previous_count,target-previous)
            if delta is None:return finish('blocked','no later distinct onset fits')
            onset=previous+delta;template=_draw(rng,templates);anchor=_draw(rng,model.anchors)
            if len(notes)+len(template)>max_notes:rejects['note_budget']+=1;continue
            new=[dict(start=onset,end=onset+g,pitch=anchor+o,velocity=v,release_velocity=rv) for o,g,v,rv in template]
            if any(n['pitch']>127 for n in new):rejects['pitch_range']+=1;continue
            if any(n['end']>target for n in new):rejects['gate_overflow']+=1;continue
            active=[n for n in notes if n['end']>onset]
            if len(active)+len(new)>3:rejects['polyphony']+=1;continue
            if {n['pitch'] for n in active}&{n['pitch'] for n in new}:rejects['same_pitch_overlap']+=1;continue
            notes.extend(new);groups.append(dict(onset=onset,delta=delta,count=len(new),anchor=anchor,template=template))
            previous=onset;horizon,previous_count=model.advance(horizon,delta,template);accepted=True;break
        if not accepted:return finish('blocked','attempt budget exhausted')
        if max(n['end'] for n in notes)>=target-tail:return finish('complete')
    return finish('blocked','note/group budget exhausted')

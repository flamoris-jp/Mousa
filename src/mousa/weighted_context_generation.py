"""Exact rational-count research model and bounded feasible sampler.

No corpus replication. Counts use Fraction; integer sampling vectors have an
explicit2048-bit ceiling. Exact integer pitch draws replace historical
random.choices float draws for ALL conditions, including the raw control.
Thus probability parity, not historical seed-byte parity, is promised.
"""
from collections import Counter,defaultdict
from fractions import Fraction
from math import lcm
import random
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.onset_gate_model import DT_SIZE,GATE_SIZE,MAX_TICKS

MAX_BITS=2048


def checked_int(x):
    if type(x) is not int or x<0 or x.bit_length()>MAX_BITS:raise ValueError('integer sampling resource bound')
    return x


def integer_weights(values):
    if not values or len(values)>128:raise ValueError('bounded pitch vector required')
    scale=1
    for value in values:
        q=Fraction(value)
        if q<=0:raise ValueError('positive weights required')
        scale=checked_int(lcm(scale,q.denominator))
    return [checked_int(int(Fraction(v)*scale)) for v in values]


class WeightedContextModel:
    # Reuse only audited likelihood/count methods. Deliberately not a subtype:
    # historical samplers assume integer gate counts and must reject this model.
    delta_counts = ContextOnsetGateModel.delta_counts
    _delta_parameters = ContextOnsetGateModel._delta_parameters
    probability = ContextOnsetGateModel.probability
    evaluate = ContextOnsetGateModel.evaluate

    def sample_pair(self, *args, **kwargs):
        raise ValueError('use weighted sample_feasible; legacy timing sampler unsupported')

    def generate(self, *args, **kwargs):
        raise ValueError('use weighted module generate; legacy generator unsupported')

    def __init__(self,sequences,pitches,weights):
        if type(weights) is not list or len(weights)!=len(sequences):raise ValueError('aligned weight list required')
        if any(type(w) not in (int,Fraction) or not 0<w<=1000 or Fraction(w).denominator>1000000 for w in weights):
            raise ValueError('bounded positive exact weights required')
        validated = ContextOnsetGateModel(sequences,pitches,timing_context=True,pitch_continuity=True,strength=4)
        self.base = validated.base
        self.vocabulary = validated.vocabulary
        self.timing_context, self.pitch_continuity, self.strength = True, True, 4
        self.contexts=defaultdict(Counter);self.pitch_counts=Counter();self.intervals=Counter()
        dt=Counter();gates=Counter();mass=Fraction(0)
        for seq,ps,weight in zip(sequences,pitches,weights):
            weight=Fraction(weight)
            for (d,g),p in zip(seq,ps):dt[d]+=weight;gates[g]+=weight;self.pitch_counts[p]+=weight;mass+=weight
            for previous,current in zip(seq,seq[1:]):self.contexts[previous[1]][current[0]]+=weight
            for p,q in zip(ps,ps[1:]):self.intervals[q-p]+=weight
        self.base.dt_counts=dt;self.base.gate_counts=gates;self.base.n=mass
        self._delta_cache={};self.weighted_mass=mass
        scale=1
        for value in gates.values():scale=checked_int(lcm(scale,value.denominator))
        self.gate_scale=scale;self.gate_excess={g:checked_int(int(c*GATE_SIZE*scale)) for g,c in gates.items()}
        self.gate_prefix=[];total=0
        for gate in range(1,GATE_SIZE+1):total=checked_int(total+self.gate_excess.get(gate,0));self.gate_prefix.append(total)

    def pitch_weights(self,previous_pitch=None):
        if previous_pitch is not None and (type(previous_pitch) is not int or previous_pitch not in self.vocabulary):raise ValueError('pitch outside vocabulary')
        counts=self.pitch_counts if previous_pitch is None else self.intervals
        return integer_weights([counts[p if previous_pitch is None else p-previous_pitch]*len(self.vocabulary)+1 for p in self.vocabulary])

    def mixed_pitch_weights(self,previous_pitch=None):
        weights=self.pitch_weights(previous_pitch);total=sum(weights);size=len(weights)
        return [checked_int(3*w*size+total) for w in weights] # fixed1/4 uniform probability mixture


def feasible_masses(model,previous,previous_gate,notes,remaining,pitch_weights):
    if not isinstance(model,WeightedContextModel):raise ValueError('weighted model required')
    if type(previous) is not int or previous<0 or type(remaining) is not int or not 1<=remaining<=9216 or len(notes)>256:
        raise ValueError('bounded timing state required')
    _,_,scale,weights=model._delta_parameters(previous_gate);checked_int(scale)
    for w in weights.values():checked_int(w)
    active=[n for n in notes if n['end']>previous]
    if len(active)>3 or len({n['pitch'] for n in active})!=len(active):raise ValueError('invalid active voices')
    by_pitch=dict(zip(model.vocabulary,pitch_weights));total=sum(pitch_weights)
    releases=sorted((n['end']-previous,n['pitch']) for n in active);occupied=sum(by_pitch[n['pitch']] for n in active);count=len(active);idx=0;result=[]
    for d in range(min(MAX_TICKS,remaining-1)+1):
        while idx<len(releases) and releases[idx][0]<=d:
            occupied-=by_pitch[releases[idx][1]];count-=1;idx+=1
        legal=0 if count>=3 else total-occupied;cap=min(MAX_TICKS,remaining-d)
        gate_mass=model.gate_prefix[cap-1]+cap*model.gate_scale
        result.append(checked_int(weights.get(d,scale)*gate_mass*legal))
    checked_int(sum(result));return result


def draw_index(rng,weights):
    total=checked_int(sum(weights))
    if not total:return None
    draw=rng.randrange(total)
    for i,weight in enumerate(weights):
        if draw<weight:return i
        draw-=weight
    raise AssertionError('integer draw out of range')


def sample_feasible(model,rng,previous,previous_gate,previous_pitch,notes,remaining):
    pw=model.mixed_pitch_weights(previous_pitch)
    d=draw_index(rng,feasible_masses(model,previous,previous_gate,notes,remaining,pw))
    if d is None:return None
    cap=min(MAX_TICKS,remaining-d);draw=rng.randrange(model.gate_prefix[cap-1]+cap*model.gate_scale)
    gate=None
    for value,weight in sorted(model.gate_excess.items()):
        if value>cap:break
        if draw<weight:gate=value;break
        draw-=weight
    if gate is None:gate=draw//model.gate_scale+1
    occupied={n['pitch'] for n in notes if n['end']>previous+d}
    weights=[w if p not in occupied else 0 for p,w in zip(model.vocabulary,pw)]
    pi=draw_index(rng,weights)
    if pi is None:raise AssertionError('selected infeasible pitch mass')
    return d,gate,model.vocabulary[pi]


def generate(model,seed,*,target_ticks=9216,max_notes=256,trailing_rest_ticks=384):
    if not isinstance(model,WeightedContextModel) or type(seed) is not int:raise ValueError('weighted model and integer seed required')
    if type(target_ticks) is not int or not 1<=target_ticks<=9216 or type(max_notes) is not int or not 1<=max_notes<=256:
        raise ValueError('generation bound')
    if type(trailing_rest_ticks) is not int or not 0<=trailing_rest_ticks<=min(384,target_ticks-1):raise ValueError('tail bound')
    rng=random.Random(seed);notes=[];previous=0;pg=pp=None
    def finish(status,reason=None):
        return dict(status=status,reason=reason,notes=notes,target_ticks=target_ticks,rejections=0,
                    timing_draws=len(notes),pitch_draws=len(notes),actual_silent_tail_ticks=target_ticks-max(n['end'] for n in notes) if notes else None)
    for _ in range(max_notes):
        proposal=sample_feasible(model,rng,previous,pg,pp,notes,target_ticks-previous)
        if proposal is None:return finish('blocked','no feasible continuation')
        d,g,p=proposal;previous+=d;pg=g;pp=p
        notes.append(dict(start=previous,end=previous+g,pitch=p))
        if max(n['end'] for n in notes)>=target_ticks-trailing_rest_ticks:return finish('complete')
    return finish('blocked','note budget exhausted')

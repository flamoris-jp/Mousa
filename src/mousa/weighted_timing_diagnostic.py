"""Exact weighted-count timing diagnostic only; no generator or label authority."""
from collections import Counter,defaultdict
from fractions import Fraction
from math import log
from mousa.onset_gate_model import _pairs,DT_SIZE,GATE_SIZE,SUPPORT_SIZE


class WeightedTimingDiagnostic:
    def __init__(self,sequences,weights,*,context=False,strength=4):
        if type(sequences) is not list or not 1<=len(sequences)<=12 or len(weights)!=len(sequences):
            raise ValueError('bounded aligned works required')
        if type(context) is not bool or type(strength) is not int or not 0<=strength<=100000:
            raise ValueError('invalid context parameters')
        self.dt=Counter();self.gate=Counter();self.local=defaultdict(Counter);self.mass=Fraction(0)
        for seq,weight in zip(sequences,weights):
            _pairs(seq)
            if type(weight) not in (int,Fraction) or not 0<weight<=1000:raise ValueError('positive exact bounded weight required')
            weight=Fraction(weight)
            for dt,gate in seq:self.dt[dt]+=weight;self.gate[gate]+=weight;self.mass+=weight
            for prior,current in zip(seq,seq[1:]):self.local[prior[1]][current[0]]+=weight
        self.context,self.strength=context,strength

    def delta_counts(self,previous_gate):
        if previous_gate is not None and (type(previous_gate) is not int or not 1<=previous_gate<=GATE_SIZE):
            raise ValueError('previous gate outside support')
        local=self.local.get(previous_gate) if self.context else None
        if not local:return self.dt
        n=sum(local.values());w=n/(n+self.strength)
        return Counter({d:w*local[d]+(1-w)*self.dt[d] for d in local.keys()|self.dt.keys()})

    def probability(self,pair,*,previous_gate=None):
        _pairs([pair]);dt,gate=pair;counts=self.delta_counts(previous_gate)
        pd=(counts.get(dt,0)+Fraction(1,DT_SIZE))/(sum(counts.values())+1)
        pg=(self.gate.get(gate,0)+Fraction(1,GATE_SIZE))/(self.mass+1)
        return pd*pg

    def evaluate(self,sequence):
        _pairs(sequence);previous=None;loss=0
        for pair in sequence:
            loss-=log(self.probability(pair,previous_gate=previous));previous=pair[1]
        return dict(events=len(sequence),nll_per_event=loss/len(sequence),support_size=SUPPORT_SIZE,
                    weighted_training_mass=str(self.mass),scope='timing likelihood only; no generation masking')

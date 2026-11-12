"""Exploratory previous-gate/delta and pitch-continuity factorial ablation.

No learned harmony/form or musical appeal claim. Per-work contexts reset.
Count shrinkage is not a mixture of complete probability distributions. Gate
marginal and fixed outcome support match the factorized cycle12 control.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from math import lcm, log
import random
from mousa.onset_gate_model import OnsetGateModel, DT_SIZE, GATE_SIZE, SUPPORT_SIZE, PPQ, MAX_TICKS, _pairs


class ContextOnsetGateModel:
    def __init__(self, sequences, pitch_sequences, *, timing_context=False,
                 pitch_continuity=False, strength=4):
        if type(sequences) is not list or not 1<=len(sequences)<=12:
            raise ValueError('bounded work list required')
        if type(pitch_sequences) is not list or len(pitch_sequences)!=len(sequences):
            raise ValueError('aligned pitch work list required')
        if type(timing_context) is not bool or type(pitch_continuity) is not bool:
            raise ValueError('boolean ablation flags required')
        if type(strength) is not int or not 0<=strength<=100000:
            raise ValueError('bounded nonnegative integer shrinkage required')
        self.contexts=defaultdict(Counter);self.pitch_counts=Counter();self.intervals=Counter()
        all_pairs=[]
        for seq,pitches in zip(sequences,pitch_sequences):
            _pairs(seq)
            if not isinstance(pitches,(list,tuple)) or len(pitches)!=len(seq) or any(type(p) is not int or not 0<=p<=127 for p in pitches):
                raise ValueError('aligned absolute MIDI pitches required')
            # No last-event/pitch carry between works, including identical gates.
            for previous,current in zip(seq,seq[1:]):self.contexts[previous[1]][current[0]]+=1
            self.intervals.update(b-a for a,b in zip(pitches,pitches[1:]))
            self.pitch_counts.update(pitches);all_pairs.extend(seq)
        _pairs(all_pairs)
        self.base=OnsetGateModel(all_pairs,factorized=True)
        self.timing_context,self.pitch_continuity,self.strength=timing_context,pitch_continuity,strength
        self.vocabulary=tuple(sorted(self.pitch_counts))
        self._delta_cache={}
        prefix=[];total=0
        for gate in range(1,GATE_SIZE+1):
            total+=self.base.gate_counts[gate];prefix.append(total)
        self._gate_prefix=prefix

    def delta_counts(self,previous_gate):
        if previous_gate is not None and (type(previous_gate) is not int or not 1<=previous_gate<=MAX_TICKS):
            raise ValueError('previous gate outside support')
        global_counts=self.base.dt_counts
        local=self.contexts.get(previous_gate) if self.timing_context else None
        if not local:return global_counts
        n=sum(local.values());weight=Fraction(n,n+self.strength)
        return Counter({d:weight*local[d]+(1-weight)*global_counts[d]
                        for d in local.keys()|global_counts.keys()})

    def _delta_parameters(self,previous_gate):
        key=previous_gate if self.timing_context else None
        # Validate even if the context-independent result is already cached.
        counts=self.delta_counts(previous_gate)
        if key not in self._delta_cache:
            total=sum(counts.values());den=1
            weights={d:Fraction(c)*DT_SIZE+1 for d,c in counts.items()}
            for value in weights.values():den=lcm(den,value.denominator)
            self._delta_cache[key]=(counts,total,den,{d:int(w*den) for d,w in weights.items()})
        return self._delta_cache[key]

    def probability(self,pair,*,previous_gate=None):
        self.base.probability(pair) # validate support without changing counts
        dt,gate=pair;counts,total,_,_=self._delta_parameters(previous_gate)
        pd=(counts.get(dt,0)+Fraction(1,DT_SIZE))/(total+1)
        pg=Fraction(self.base.gate_counts[gate]*GATE_SIZE+1,(self.base.n+1)*GATE_SIZE)
        return pd*pg

    def evaluate(self,sequence):
        _pairs(sequence);previous=None;loss=0.
        for pair in sequence:
            loss-=log(self.probability(pair,previous_gate=previous));previous=pair[1]
        return dict(events=len(sequence),nll_per_event=loss/len(sequence),support_size=SUPPORT_SIZE,
                    conditional_generation_masks_applied=False)

    def sample_pair(self,rng,*,remaining_ticks,previous_gate=None):
        if not isinstance(rng,random.Random):raise ValueError('random.Random required')
        if type(remaining_ticks) is not int or not 1<=remaining_ticks<=PPQ*1024:
            raise ValueError('bounded positive remaining ticks required')
        _,_,scale,dt_weights=self._delta_parameters(previous_gate)
        upper=min(MAX_TICKS,remaining_ticks-1)
        masses=[]
        for d in range(upper+1):
            cap=min(MAX_TICKS,remaining_ticks-d)
            masses.append(dt_weights.get(d,scale)*(self._gate_prefix[cap-1]*GATE_SIZE+cap))
        draw=rng.randrange(sum(masses))
        for dt,mass in enumerate(masses):
            if draw<mass:break
            draw-=mass
        cap=min(MAX_TICKS,remaining_ticks-dt)
        draw=rng.randrange(self._gate_prefix[cap-1]*GATE_SIZE+cap)
        for gate,count in sorted(self.base.gate_counts.items()):
            if gate>cap:break
            mass=count*GATE_SIZE
            if draw<mass:return dt,gate
            draw-=mass
        return dt,draw+1

    def pitch_weights(self,previous_pitch=None):
        if previous_pitch is not None and (type(previous_pitch) is not int or previous_pitch not in self.vocabulary):
            raise ValueError('previous pitch must lie in train vocabulary')
        # Control is uniform over the SAME training vocabulary. Continuity
        # starts with train unigram and then interval counts, renormalized on
        # valid decoded pitches. Out-of-vocabulary shifts never clip.
        if not self.pitch_continuity:return [1]*len(self.vocabulary)
        counts=self.pitch_counts if previous_pitch is None else self.intervals
        return [counts[p if previous_pitch is None else p-previous_pitch]*len(self.vocabulary)+1 for p in self.vocabulary]

    def generate(self,seed,*,target_ticks=9216,max_notes=256,max_attempts=64):
        if type(seed) is not int or type(target_ticks) is not int or not 1<=target_ticks<=PPQ*1024:
            raise ValueError('integer seed and bounded target required')
        if type(max_notes) is not int or not 1<=max_notes<=256 or type(max_attempts) is not int or not 1<=max_attempts<=64:
            raise ValueError('bounded generation budgets required')
        rng=random.Random(seed);notes=[];previous=0;previous_gate=None;previous_pitch=None;rejections=0
        for _ in range(max_notes):
            for _ in range(max_attempts):
                dt,gate=self.sample_pair(rng,remaining_ticks=target_ticks-previous,previous_gate=previous_gate)
                start=previous+dt;end=start+gate
                pitch=rng.choices(self.vocabulary,weights=self.pitch_weights(previous_pitch))[0]
                active=[n for n in notes if n['end']>start]
                if len(active)>=3 or any(n['pitch']==pitch for n in active):
                    rejections+=1;continue
                notes.append(dict(start=start,end=end,pitch=pitch))
                previous,previous_gate,previous_pitch=start,gate,pitch
                if end==target_ticks:return dict(status='complete',notes=notes,rejections=rejections,target_ticks=target_ticks)
                break
            else:return dict(status='blocked',notes=notes,rejections=rejections,reason='attempt budget exhausted')
        return dict(status='blocked',notes=notes,rejections=rejections,reason='note budget exhausted')

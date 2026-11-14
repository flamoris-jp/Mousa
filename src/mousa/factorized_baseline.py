"""Fixed-support music-event comparison and a narrow phrase-copy guard.

No quality oracle or legal originality guarantee. Does not change grid-v1.
"""
from collections import Counter
import math
import random
from mousa.event_baseline import EventNGram, _events, events_from_grid

PITCHES = (-1, *range(2, 27))
DURATIONS = tuple(range(1, 129))


def onset_phrases(tokens, length=8):
    """Transposition-invariant windows: intervals, note lengths, inter-note gaps."""
    if type(length) is not int or not 2 <= length <= 32:
        raise ValueError('bounded phrase length required')
    notes=[]; tick=0
    for pitch,duration in events_from_grid(tokens):
        if pitch != -1: notes.append((pitch,duration,tick))
        tick+=duration
    result=[]
    for i in range(len(notes)-length+1):
        window=notes[i:i+length]
        result.append((tuple(b[0]-a[0] for a,b in zip(window,window[1:])),
                       tuple(n[1] for n in window),
                       tuple(b[2]-a[2]-a[1] for a,b in zip(window,window[1:]))))
    return result


class FixedEventModel:
    """Both variants use identical contexts, fixed support and total prior mass.

    Factorized estimates pitch and duration marginals from the SAME backed-off
    context counts. Joint estimates the full event. Durations outside 1..128
    reject rather than being silently quantized. No vocabulary fitting on test.
    """
    def __init__(self,sequences,*,factorized=False,order=1,prior=1.0):
        if type(factorized) is not bool or type(prior) not in (int,float) or not math.isfinite(prior) or prior <= 0:
            raise ValueError('invalid model settings')
        self.base=EventNGram(sequences,order)
        for sequence in sequences:self.validate(sequence)
        self.factorized,self.prior=factorized,prior

    @staticmethod
    def validate(sequence):
        _events(sequence)
        if any(d>128 for _,d in sequence):raise ValueError('duration outside fixed support')

    def distribution(self,history):
        counts=self.base.counts(history); n=sum(counts.values())
        pitches=Counter(); durations=Counter()
        for (p,d),c in counts.items():pitches[p]+=c;durations[d]+=c
        return counts,pitches,durations,n

    def probability(self,event,distribution):
        counts,pitches,durations,n=distribution;p,d=event;s=self.prior
        if self.factorized:
            return (pitches[p]+s/len(PITCHES))/(n+s)*(durations[d]+s/len(DURATIONS))/(n+s)
        return (counts[event]+s/(len(PITCHES)*len(DURATIONS)))/(n+s)

    def evaluate(self,sequence):
        self.validate(sequence)
        loss=0.;joint=pitch=duration=0
        for i,event in enumerate(sequence):
            distribution=self.distribution(sequence[:i]);counts,ps,ds,n=distribution
            loss-=math.log(self.probability(event,distribution))
            if self.factorized:
                prediction=(min(PITCHES,key=lambda p:(-ps[p],p)),min(DURATIONS,key=lambda d:(-ds[d],d)))
            else:prediction=min(counts,key=lambda e:(-counts[e],e))
            joint+=prediction==event;pitch+=prediction[0]==event[0];duration+=prediction[1]==event[1]
        return dict(events=len(sequence),correct_events=joint,correct_pitch=pitch,correct_duration=duration,
                    nll_per_event=loss/len(sequence),support_size=len(PITCHES)*len(DURATIONS))

    def generate(self,seed,*,steps=128,source_grids=(),guard=False):
        if type(seed) is not int or type(steps) is not int or not 1<=steps<=4096 or type(guard) is not bool:
            raise ValueError('invalid generation settings')
        if len(source_grids)>12:raise ValueError('bounded source list required')
        forbidden={phrase for source in source_grids for phrase in onset_phrases(source)}
        rng=random.Random(seed);events=[];tokens=[];rejections=0
        while len(tokens)<steps:
            counts,ps,ds,n=self.distribution(events)
            for attempt in range(64):
                if self.factorized:
                    p=rng.choices(PITCHES,weights=[ps[p]+self.prior/len(PITCHES) for p in PITCHES])[0]
                    d=rng.choices(DURATIONS,weights=[ds[d]+self.prior/len(DURATIONS) for d in DURATIONS])[0]
                elif rng.random()<self.prior/(n+self.prior):
                    p,d=rng.choice(PITCHES),rng.choice(DURATIONS)
                else:
                    p,d=rng.choices(sorted(counts),weights=[counts[e] for e in sorted(counts)])[0]
                d=min(d,steps-len(tokens));addition=[0]*d if p==-1 else [p]+[1]*(d-1)
                candidate=tokens+addition
                if guard and any(phrase in forbidden for phrase in onset_phrases(candidate)):
                    rejections+=1;continue
                tokens=candidate;events.append((p,d));break
            else:
                return dict(status='blocked',tokens=tokens,rejections=rejections,reason='64 consecutive phrase-copy rejections')
        return dict(status='complete',tokens=tokens,rejections=rejections,
                    matching_8_note_phrases=sum(p in forbidden for p in onset_phrases(tokens)))

"""Ablations for pitch-relative contexts and train-only duration priors.

Music-specific counting models; no universal music quality score or neural Core.
"""
from collections import Counter, defaultdict
import math
import random
from mousa.factorized_baseline import FixedEventModel, PITCHES, DURATIONS, onset_phrases


class MelodicEventModel:
    def __init__(self,sequences,*,relative=False,duration_prior='uniform',prior_mass=1.):
        if type(relative) is not bool or duration_prior not in ('uniform','empirical','typed'):
            raise ValueError('unknown ablation')
        if type(prior_mass) not in (int,float) or not math.isfinite(prior_mass) or prior_mass<=0:
            raise ValueError('positive finite prior required')
        if not isinstance(sequences,list) or not 1<=len(sequences)<=12:raise ValueError('bounded work list required')
        self.relative,self.duration_prior,self.prior_mass=relative,duration_prior,prior_mass
        self.tables=[defaultdict(Counter),defaultdict(Counter)]
        self.duration_global={None:Counter(),True:Counter(),False:Counter()}
        for sequence in sequences:
            FixedEventModel.validate(sequence)
            encoded,_=self.encode(sequence)
            for i,(event,raw) in enumerate(zip(encoded,sequence)):
                self.tables[0][()][event]+=1
                if i:self.tables[1][(encoded[i-1],)][event]+=1
                self.duration_global[None][raw[1]]+=1
                self.duration_global[raw[0]==-1][raw[1]]+=1

    def encode(self,sequence):
        last=14;encoded=[]
        for p,d in sequence:
            q=-99 if p==-1 else (p-last if self.relative else p)
            encoded.append((q,d))
            if p!=-1:last=p
        return encoded,last

    def context(self,history):
        encoded,last=self.encode(history)
        key=(encoded[-1],) if encoded else ()
        counts=self.tables[1].get(key,self.tables[0][()])
        return counts,last

    def distributions(self,history):
        counts,last=self.context(history);pc=Counter();dc={None:Counter(),True:Counter(),False:Counter()}
        for (q,d),c in counts.items():
            pc[q]+=c;dc[None][d]+=c;dc[q==-99][d]+=c
        mapped={p:(-99 if p==-1 else p-last if self.relative else p) for p in PITCHES}
        # Renormalize on valid decoded pitches; interval probability beyond the
        # fixed pitch register is excluded consistently for evaluation/generation.
        total=sum(pc[q] for q in mapped.values());s=self.prior_mass
        pitches={p:(pc[q]+s/len(PITCHES))/(total+s) for p,q in mapped.items()}
        durations={}
        for rest in (False,True):
            group=rest if self.duration_prior=='typed' else None
            global_counts=self.duration_global[group];global_total=sum(global_counts.values())
            context_counts=dc[group];n=sum(context_counts.values())
            prior={d:1/len(DURATIONS) if self.duration_prior=='uniform' else
                   (global_counts[d]+.5/len(DURATIONS))/(global_total+.5) for d in DURATIONS}
            durations[rest]={d:(context_counts[d]+s*prior[d])/(n+s) for d in DURATIONS}
        return pitches,durations

    def evaluate(self,sequence):
        FixedEventModel.validate(sequence)
        correct=pitch_ok=duration_ok=0;loss=0.
        for i,(p,d) in enumerate(sequence):
            ps,ds=self.distributions(sequence[:i]);probability=ps[p]*ds[p==-1][d]
            loss-=math.log(probability)
            predicted_pitch=min(PITCHES,key=lambda p:(-ps[p],p))
            # A marginal duration measure remains comparable when conditioning
            # duration on rest/note changes the joint decoder.
            duration_probability={d:sum(ps[p]*ds[p==-1][d] for p in PITCHES) for d in DURATIONS}
            predicted_duration=min(DURATIONS,key=lambda d:(-duration_probability[d],d))
            best_duration={rest:min(DURATIONS,key=lambda d:(-ds[rest][d],d)) for rest in (False,True)}
            predicted_joint=min(((p,best_duration[p==-1]) for p in PITCHES),
                                key=lambda e:(-ps[e[0]]*ds[e[0]==-1][e[1]],e))
            correct+=predicted_joint==(p,d);pitch_ok+=predicted_pitch==p;duration_ok+=predicted_duration==d
        return dict(events=len(sequence),correct_events=correct,correct_pitch_marginal=pitch_ok,
                    correct_duration_marginal=duration_ok,nll_per_event=loss/len(sequence),support_size=3328)

    def generate(self,seed,*,steps=128,source_grids=(),guard=True):
        if type(seed) is not int or type(steps) is not int or not 1<=steps<=4096 or type(guard) is not bool:
            raise ValueError('invalid generation settings')
        if len(source_grids)>12:raise ValueError('bounded source list required')
        forbidden={p for t in source_grids for p in onset_phrases(t)}
        rng=random.Random(seed);history=[];tokens=[];rejections=0
        while len(tokens)<steps:
            ps,ds=self.distributions(history)
            for attempt in range(64):
                pitch=rng.choices(PITCHES,weights=[ps[p] for p in PITCHES])[0]
                duration=rng.choices(DURATIONS,weights=[ds[pitch==-1][d] for d in DURATIONS])[0]
                duration=min(duration,steps-len(tokens))
                addition=[0]*duration if pitch==-1 else [pitch]+[1]*(duration-1)
                candidate=tokens+addition
                if guard and any(p in forbidden for p in onset_phrases(candidate)):
                    rejections+=1;continue
                tokens=candidate;history.append((pitch,duration));break
            else:return dict(status='blocked',tokens=tokens,rejections=rejections)
        return dict(status='complete',tokens=tokens,rejections=rejections)

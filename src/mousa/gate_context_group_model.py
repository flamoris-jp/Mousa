"""Fixed observed-history group timing contexts; no inferred voice labels."""
from collections import defaultdict, Counter
from math import log, isfinite
from time import process_time
import random
from mousa.initial_rest_group_model import InitialRestGroupModel, validate
from mousa.group_onset_model import _draw

ARMS = ('global', 'cardinality', 'previous_max_gate_binned', 'active_horizon_binned')
BIN_UPPER = (192, 384, 768, 1536)


def gate_bin(value):
    if type(value) is not int or value < 1:
        raise ValueError('positive integer history horizon required')
    return next((i+1 for i, hi in enumerate(BIN_UPPER) if value<=hi),5)


class GateContextGroupModel:
    def __init__(self, sequences, *, arm='global'):
        if arm not in ARMS: raise ValueError('fixed context arm required')
        baseline=InitialRestGroupModel(sequences, context=False, first_limit=65536)
        self.__dict__.update(baseline.__dict__)
        self.arm=arm; self.context=arm!='global'; self.local=defaultdict(Counter); self.cache={}
        for seq in sequences:
            previous=None; horizon=0
            for delta, _, template in seq:
                if previous is not None: self.local[previous][delta]+=1
                horizon, previous=self.advance(horizon,delta,template)

    # Standalone class rejects old generators' isinstance contract. Reusing
    # their sequence-state update would silently pass cardinality to gate arms.
    probability = InitialRestGroupModel.probability
    sample_delta = InitialRestGroupModel.sample_delta

    def parameters(self, previous):
        if previous is not None and (type(previous) is not int or not 1<=previous<=128):
            raise ValueError('previous key outside support')
        key=previous if self.context else (None if previous is None else -1)
        if key not in self.cache:
            first=previous is None;lo=0 if first else 1
            size=self.first_limit+1 if first else 12288
            counts=self.first if first else self.later
            denominator=(sum(counts.values())+1)*size
            weights={d:c*size+1 for d,c in counts.items()};default=1
            local=self.local.get(previous) if self.context and not first else None
            if local:
                weights={d:local[d]*denominator+4*(counts[d]*size+1) for d in local.keys()|counts.keys()}
                default=4
            self.cache[key]=(lo,weights,default)
        return self.cache[key]

    def advance(self, horizon, delta, template):
        maximum=max(t[1] for t in template)
        horizon=max(horizon-delta,maximum)
        if self.arm=='global': key=1
        elif self.arm=='cardinality': key=len(template)
        elif self.arm=='previous_max_gate_binned': key=gate_bin(maximum)
        else: key=gate_bin(horizon)
        return horizon,key

    def evaluate(self, seq):
        validate(seq,self.first_limit)
        previous=None; horizon=0; first=0.; later=0.
        for i,(delta,_,template) in enumerate(seq):
            loss=-log(self.probability(delta,previous))
            if i==0:first=loss
            else:later+=loss
            horizon,previous=self.advance(horizon,delta,template)
        return dict(groups=len(seq),first_groups=1,later_groups=len(seq)-1,
                    first_nll=first,later_nll_sum=later,
                    later_nll_per_group=later/(len(seq)-1) if len(seq)>1 else None,
                    nll_per_group_delta=(first+later)/len(seq))


def generate(model,seed,*,target=9216,tail=384,max_notes=256,max_attempts=64,cpu_deadline=None):
    if not isinstance(model,GateContextGroupModel) or type(seed) is not int:raise ValueError('model/seed required')
    if any(type(x) is not int for x in (target,tail,max_notes,max_attempts)) or not 1<=target<=9216 or not 0<=tail<=min(384,target-1) or not 1<=max_notes<=256 or not 1<=max_attempts<=64:
        raise ValueError('bounded generation required')
    if cpu_deadline is not None and (type(cpu_deadline) not in (int,float) or not isfinite(cpu_deadline) or cpu_deadline<0):
        raise ValueError('finite nonnegative CPU deadline required')
    templates=Counter({t:n for t,n in model.templates.items() if len(t)<=3})
    rng=random.Random(seed);notes=[];groups=[];previous=0;previous_count=None;horizon=0;rejects=Counter();attempts=0
    def finish(status,reason=None):
        return dict(status=status,reason=reason,notes=notes,groups=groups,attempts=attempts,rejections=dict(rejects),
                    ineligible_template_occurrences=model.ineligible_occurrences,total_template_occurrences=model.template_occurrences,
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

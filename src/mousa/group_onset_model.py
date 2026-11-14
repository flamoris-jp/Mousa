"""Group-onset timing research, not a melodic or harmonic truth model.

Both arms predict the same distinct-onset delta. First support is0..12288;
subsequent support1..12288. Initial and subsequent count pools are separate.
Templates/anchor sampling is a separate empirical generation stage; its
probabilities are NOT included in reported timing NLL. Original notes unmodified.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from math import log, isfinite
from time import process_time
import random
from mousa.onset_groups import group_notes

LIMIT = 12288


def observations(notes, total_ticks):
    groups = group_notes(notes, total_ticks)
    previous = 0
    result = []
    for group in groups:
        anchor = min(m.note.pitch for m in group.members)
        template = tuple((m.note.pitch-anchor, m.note.end-m.note.start,
                          m.note.velocity, m.note.release_velocity) for m in group.members)
        result.append((group.onset-previous, anchor, template))
        previous = group.onset
    return result


def _validate(seq):
    if type(seq) is not list or not 1 <= len(seq) <= 4096:
        raise ValueError('bounded nonempty group sequence required')
    for i, event in enumerate(seq):
        if type(event) is not tuple or len(event) != 3:
            raise ValueError('delta/anchor/template required')
        delta,anchor,template=event
        if type(delta) is not int or not (0 if i==0 else 1) <= delta <= LIMIT:
            raise ValueError('distinct-onset delta outside support')
        if type(anchor) is not int or not 0<=anchor<=127 or type(template) is not tuple or not 1<=len(template)<=128:
            raise ValueError('bounded anchor/template required')
        seen=set()
        for member in template:
            if type(member) is not tuple or len(member)!=4 or any(type(x) is not int for x in member):
                raise ValueError('integer template fields required')
            offset,gate,velocity,release=member
            if not 0<=offset<=127-anchor or not 1<=gate<=LIMIT or not 1<=velocity<=127 or not 0<=release<=127:
                raise ValueError('template outside note support')
            if offset in seen:raise ValueError('same-pitch simultaneous template ambiguity')
            seen.add(offset)
        if min(seen)!=0:raise ValueError('template anchor must be minimum pitch')


class GroupOnsetModel:
    def __init__(self, sequences, *, context=False):
        if type(sequences) is not list or not 1<=len(sequences)<=32 or type(context) is not bool:
            raise ValueError('bounded works and boolean arm required')
        if any(type(s) is not list for s in sequences):raise ValueError('group work lists required')
        if sum(len(s) for s in sequences)>100000:raise ValueError('aggregate group bound')
        self.first=Counter();self.later=Counter();self.local=defaultdict(Counter)
        self.templates=Counter();self.anchors=Counter();self.context=context;self.cache={}
        for seq in sequences:
            _validate(seq)
            previous=None
            for delta,anchor,template in seq:
                if previous is None:self.first[delta]+=1
                else:self.later[delta]+=1;self.local[previous][delta]+=1
                self.templates[template]+=1;self.anchors[anchor]+=1;previous=len(template)
        if sum(len(t)*n for t,n in self.templates.items())>100000:raise ValueError('aggregate note bound')
        self.template_occurrences=sum(self.templates.values())
        self.ineligible_occurrences=sum(n for t,n in self.templates.items() if len(t)>3)

    def parameters(self, previous_count):
        if previous_count is not None and (type(previous_count) is not int or not 1<=previous_count<=128):
            raise ValueError('previous count outside support')
        key=previous_count if self.context else (None if previous_count is None else -1)
        if key not in self.cache:
            first=previous_count is None;lo=0 if first else 1;size=LIMIT-lo+1
            counts=self.first if first else self.later
            global_den=(sum(counts.values())+1)*size
            weights={d:c*size+1 for d,c in counts.items()};default=1
            local=self.local.get(previous_count) if self.context and not first else None
            if local:
                weights={d:local[d]*global_den+4*(counts[d]*size+1) for d in local.keys()|counts.keys()}
                default=4
            self.cache[key]=(lo,weights,default)
        return self.cache[key]

    def probability(self, delta, previous_count=None):
        lo,weights,default=self.parameters(previous_count)
        if type(delta) is not int or not lo<=delta<=LIMIT:raise ValueError('delta outside stage support')
        total=sum(weights.values())+(LIMIT-lo+1-len(weights))*default
        return Fraction(weights.get(delta,default),total)

    def evaluate(self, seq):
        _validate(seq);loss=0.;previous=None
        for delta,anchor,template in seq:
            loss-=log(self.probability(delta,previous));previous=len(template)
        return dict(groups=len(seq),nll_per_group_delta=loss/len(seq),outcome='distinct-onset delta only; teacher-forced previous cardinality',template_pitch_gate_likelihood_included=False)

    def sample_delta(self,rng,previous_count,remaining):
        lo,weights,default=self.parameters(previous_count);hi=min(LIMIT,remaining-1)
        if hi<lo:return None
        total=sum(weights.get(d,default) for d in range(lo,hi+1));draw=rng.randrange(total)
        for delta in range(lo,hi+1):
            w=weights.get(delta,default)
            if draw<w:return delta
            draw-=w
        raise AssertionError('delta draw')


def _draw(rng,counts):
    draw=rng.randrange(sum(counts.values()))
    for item,weight in counts.items():
        if draw<weight:return item
        draw-=weight
    raise AssertionError('empirical draw')


def generate(model,seed,*,target=9216,tail=384,max_notes=256,max_attempts=64,cpu_deadline=None):
    if not isinstance(model,GroupOnsetModel) or type(seed) is not int:raise ValueError('model/seed required')
    if any(type(x) is not int for x in (target,tail,max_notes,max_attempts)) or not 1<=target<=9216 or not 0<=tail<=min(384,target-1) or not 1<=max_notes<=256 or not 1<=max_attempts<=64:
        raise ValueError('bounded generation required')
    if cpu_deadline is not None and (type(cpu_deadline) not in (int,float) or not isfinite(cpu_deadline) or cpu_deadline<0):
        raise ValueError('finite nonnegative CPU deadline required')
    templates=Counter({t:n for t,n in model.templates.items() if len(t)<=3})
    rng=random.Random(seed);notes=[];groups=[];previous=0;previous_count=None;rejects=Counter();attempts=0
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
            previous=onset;previous_count=len(new);accepted=True;break
        if not accepted:return finish('blocked','attempt budget exhausted')
        if max(n['end'] for n in notes)>=target-tail:return finish('complete')
    return finish('blocked','note/group budget exhausted')

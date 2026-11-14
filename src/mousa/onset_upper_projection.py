"""Declared lossy upper-note-per-onset projection, NOT melody ground truth.

Selected original note objects and gates remain unchanged. Notes starting at
different times may still overlap. No voice separation or quantization occurs.
"""
from collections import defaultdict


def project(notes):
    if not isinstance(notes,(list,tuple)) or not 1<=len(notes)<=4096:raise ValueError('bounded nonempty notes required')
    groups=defaultdict(list)
    for i,n in enumerate(notes):
        if any(type(v) is not int for v in (n.start,n.end,n.pitch)) or not 0<=n.start<n.end or not 0<=n.pitch<=127:
            raise ValueError('exact note fields required')
        groups[n.start].append((i,n))
    # Highest pitch; deterministic longest gate, then earliest input index tie.
    result=[]
    for start,group in sorted(groups.items()):
        _,n=max(group,key=lambda pair:(pair[1].pitch,pair[1].end,-pair[0]))
        result.append(n)
    return tuple(result)


def describe(notes,total_ticks):
    if type(total_ticks) is not int or not 1<=total_ticks<=32767*1024:raise ValueError('bounded timeline required')
    events=defaultdict(int);gates=0
    for n in notes:
        if not 0<=n.start<n.end<=total_ticks:raise ValueError('note outside timeline')
        events[n.start]+=1;events[n.end]-=1;gates+=n.end-n.start
    previous=0;active=0;sounding=0;overlap=0;maximum=0
    for tick,change in sorted(events.items()):
        if active:sounding+=tick-previous
        if active>1:overlap+=tick-previous
        active+=change;maximum=max(maximum,active);previous=tick
    return dict(notes=len(notes),summed_gate_ticks=gates,sounding_union_ticks=sounding,
                overlap_timeline_ticks=overlap,max_polyphony=maximum,rest_ticks=total_ticks-sounding,total_ticks=total_ticks)


def project_with_loss(notes,total_ticks):
    selected=project(notes);before=describe(notes,total_ticks);after=describe(selected,total_ticks)
    loss=dict(dropped_notes=len(notes)-len(selected),dropped_summed_gate_ticks=before['summed_gate_ticks']-after['summed_gate_ticks'],
              lost_sounding_union_ticks=before['sounding_union_ticks']-after['sounding_union_ticks'],before=before,after=after,
              interpretation='Deterministic lossy note selection, not verified melody. Original selected gates preserved; remaining overlaps allowed.')
    return selected,loss

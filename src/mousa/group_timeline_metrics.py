"""Actual occupied time from note intervals, not gaps between onsets."""
from collections import Counter


def timeline_metrics(notes, target):
    if type(target) is not int or target<1 or type(notes) is not list or len(notes)>100000:
        raise ValueError('bounded note timeline required')
    events=Counter()
    for n in notes:
        if type(n) is not dict or any(type(n.get(k)) is not int for k in ('start','end')):
            raise ValueError('integer note endpoints required')
        if not 0<=n['start']<n['end']<=target: raise ValueError('note outside target')
        events[n['start']]+=1;events[n['end']]-=1
    active=0;previous=0;integral=0;poly=0;occupied=0;gaps=[]
    for tick, change in sorted(events.items()):
        duration=tick-previous
        if active==0 and duration:gaps.append((previous,tick))
        if active>0:occupied+=duration
        if active>1:poly+=duration
        integral+=active*duration
        active+=change;previous=tick
    if previous<target:gaps.append((previous,target))
    leading=next((b-a for a,b in gaps if a==0),0)
    trailing=next((b-a for a,b in gaps if b==target),0)
    internal=sum(b-a for a,b in gaps if a>0 and b<target)
    return dict(target_ticks=target,occupied_ticks=occupied,silence_ticks=target-occupied,
                leading_silence_ticks=leading,trailing_silence_ticks=trailing,
                internal_silence_ticks=internal,max_contiguous_silence_ticks=max((b-a for a,b in gaps),default=0),
                internal_gap_count=sum(a>0 and b<target for a,b in gaps),
                active_voice_tick_integral=integral,mean_active_voices=integral/target,
                polyphonic_ticks=poly,polyphonic_time_fraction=poly/target,
                empty_timeline=not notes,
                silence_accounting='Empty timeline leading/trailing both describe same whole interval; do not sum them. Otherwise categories are disjoint.')

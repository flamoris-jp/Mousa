"""Fixed post-generation group return; not learned phrase or tonal cadence."""
from copy import deepcopy
from collections import Counter

TARGET = 9216
BAR_PAIR = 2304
FIELDS = ('start', 'end', 'pitch', 'velocity', 'release_velocity')


def phrases(pitches):
    """Same seven-interval/eight-note exact window as the fixed copy gate."""
    intervals = [b-a for a,b in zip(pitches,pitches[1:])]
    return {tuple(intervals[i:i+7]) for i in range(len(intervals)-6)}


def validate_notes(notes):
    if type(notes) is not list or not 1 <= len(notes) <= 256:
        raise ValueError('1..256 complete notes required')
    previous = -1
    events = []
    for n in notes:
        if type(n) is not dict or set(n) != set(FIELDS) or any(type(n[k]) is not int for k in FIELDS):
            raise ValueError('exact five integer fields required')
        if not 0 <= n['start'] < n['end'] <= TARGET or n['start'] < previous:
            raise ValueError('ordered complete notes within target required')
        if not 0 <= n['pitch'] <= 127 or not 1 <= n['velocity'] <= 127 or not 0 <= n['release_velocity'] <= 127:
            raise ValueError('MIDI fields outside fixed generator support')
        previous=n['start']
        events.extend([(n['start'],1,n['pitch']), (n['end'],-1,n['pitch'])])
    if TARGET-max(n['end'] for n in notes)>384:
        raise ValueError('complete output must retain tail<=384')
    active=Counter()
    for _,kind,pitch in sorted(events):  # release before onset: half-open gates
        active[pitch]+=kind
        if any(v>1 for v in active.values()):
            raise ValueError('same pitch overlap')
        if sum(active.values())>3:
            raise ValueError('max3 active voices')
    return True


def validate_groups(notes,groups):
    if type(groups) is not list or not 1 <= len(groups) <= 256:
        raise ValueError('bounded onset groups required')
    reconstructed=[];previous=0
    for i,g in enumerate(groups):
        if type(g) is not dict or set(g) != {'onset','delta','count','anchor','template'}:
            raise ValueError('exact generator group fields required')
        if any(type(g[k]) is not int for k in ('onset','delta','count','anchor')):
            raise ValueError('integer group fields')
        onset=g['onset']
        if onset<0 or (i and onset<=previous) or g['delta']!=onset-previous:
            raise ValueError('group delta or ordering inconsistent')
        t=g['template']
        if not isinstance(t,(tuple,list)) or len(t)!=g['count'] or not 1<=len(t)<=3:
            raise ValueError('whole nonempty <=3-member template')
        for member in t:
            if not isinstance(member,(tuple,list)) or len(member)!=4 or any(type(x) is not int for x in member):
                raise ValueError('template must retain four integer fields')
            offset,gate,velocity,release=member
            if offset<0 or gate<1:raise ValueError('nonnegative offset and positive gate')
            reconstructed.append(dict(start=onset,end=onset+gate,pitch=g['anchor']+offset,velocity=velocity,release_velocity=release))
        previous=onset
    if reconstructed!=notes:raise ValueError('groups do not exactly reconstruct all ordered note fields')
    return True


def compare_return(notes,groups,source_pitch_sequences):
    """Return both arms, including blocked intervention; never mutate sources.

    Copy refs must comprise complete ordered pitch sequences. Caller binds their
    original-source IDs/hashes and checks source count21 in the frozen driver.
    """
    validate_notes(notes);validate_groups(notes,groups)
    if not isinstance(source_pitch_sequences,(tuple,list)) or not 1<=len(source_pitch_sequences)<=21:
        raise ValueError('bounded complete copy references required')
    forbidden=set()
    for seq in source_pitch_sequences:
        if not isinstance(seq,(list,tuple)) or not 1<=len(seq)<=8192 or any(type(x) is not int or not 0<=x<=127 for x in seq):
            raise ValueError('bounded original MIDI pitch references required')
        forbidden.update(phrases(seq))
    def result(ns,gs):
        validate_notes(ns);validate_groups(ns,gs)
        canonical=sorted(ns,key=lambda n:(n['start'],n['end'],n['pitch']))
        hits=(phrases([n['pitch'] for n in ns]) | phrases([n['pitch'] for n in canonical])) & forbidden
        return dict(status='copy_guard_blocked' if hits else 'complete',copy_matches=len(hits),notes=ns,groups=gs,target_ticks=TARGET)
    control=result(deepcopy(notes),deepcopy(groups))
    boundaries=(BAR_PAIR,2*BAR_PAIR,3*BAR_PAIR)
    crossings=[dict(note_index=i,boundary=b,start=n['start'],end=n['end'])
               for i,n in enumerate(notes) for b in boundaries if n['start']<b<n['end']]
    if crossings:
        return dict(control=control,intervention=dict(status='boundary_sustain_blocked',crossings=crossings,target_ticks=TARGET))
    a=[g for g in groups if g['onset']<BAR_PAIR]
    c=[g for g in groups if 2*BAR_PAIR<=g['onset']<3*BAR_PAIR]
    if not a:return dict(control=control,intervention=dict(status='empty_A_blocked',target_ticks=TARGET))
    if any(g['anchor']+offset+2>127 for g in a for offset,_,_,_ in g['template']):
        return dict(control=control,intervention=dict(status='pitch_range_blocked',target_ticks=TARGET))
    selected=[]
    for g in groups:
        if g['onset']<2*BAR_PAIR:selected.append(deepcopy(g))
    for g in a:
        v=deepcopy(g);v['onset']+=2*BAR_PAIR;v['anchor']+=2;selected.append(v)
    selected.extend(deepcopy(g) for g in groups if g['onset']>=3*BAR_PAIR)
    out=[];previous=0
    for g in selected:
        g['delta']=g['onset']-previous;previous=g['onset']
        for offset,gate,vel,rv in g['template']:
            out.append(dict(start=g['onset'],end=g['onset']+gate,pitch=g['anchor']+offset,velocity=vel,release_velocity=rv))
    try:
        intervention=result(out,selected)
    except ValueError as exc:
        intervention=dict(status='safety_blocked',reason=str(exc),target_ticks=TARGET)
    intervention['edit']=dict(fixed_semitone_shift=2,source_window=[0,BAR_PAIR],replacement_window=[2*BAR_PAIR,3*BAR_PAIR],
                              removed_note_count=sum(g['count'] for g in c),added_note_count=sum(g['count'] for g in a),
                              removed_group_count=len(c),added_group_count=len(a),
                              removed_gate_ticks=sum(t[1] for g in c for t in g['template']),
                              added_gate_ticks=sum(t[1] for g in a for t in g['template']))
    return dict(control=control,intervention=intervention)

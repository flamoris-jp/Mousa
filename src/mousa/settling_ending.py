"""Bounded candidate selection for an explicit non-tonal ending proxy.

No assumed key, tonic, learned cadence or appeal claim. Both selectors see
exactly the same four generated candidates. Selecting a proxy necessarily
biases proxy metrics; failures are retained, never repaired or hidden.
"""
from fractions import Fraction
from mousa.optimized_feasible_generation import generate_optimized


def ending_features(notes,*,target_ticks=9216):
    if type(target_ticks) is not int or not 1152<=target_ticks<=384*1024:
        raise ValueError('target must permit the fixed final-three-quarter window')
    if not isinstance(notes,(list,tuple)) or len(notes)>256:
        raise ValueError('bounded note list required')
    previous=-1
    for n in notes:
        if type(n) is not dict or not {'start','end','pitch'}<=n.keys():raise ValueError('note fields required')
        if any(type(n[k]) is not int for k in ('start','end','pitch')):
            raise ValueError('integer note fields required')
        if not previous<=n['start']<n['end']<=target_ticks or n['start']<0 or not 0<=n['pitch']<=127:
            raise ValueError('invalid onset-ordered notes')
        previous=n['start']
    if len(notes)<2:return dict(eligible=False,reasons=['fewer_than_two_onsets'],last_gate_ticks=None,final_abs_interval=None,final_onset_tick=None)
    last=notes[-1];gate=last['end']-last['start'];interval=abs(last['pitch']-notes[-2]['pitch'])
    reasons=[]
    if last['start']<target_ticks-1152:reasons.append('last_onset_outside_final_three_quarters')
    if gate<384:reasons.append('last_gate_shorter_than_quarter')
    if interval>2:reasons.append('final_onset_interval_above_two_semitones')
    if last['end']<max(n['end'] for n in notes):reasons.append('earlier_note_outlasts_last_onset')
    return dict(eligible=not reasons,reasons=reasons,last_gate_ticks=gate,final_abs_interval=interval,
                final_onset_tick=last['start'],silent_tail_ticks=target_ticks-max(n['end'] for n in notes))


def _phrases(pitches):
    intervals=[b-a for a,b in zip(pitches,pitches[1:])]
    return {tuple(intervals[i:i+7]) for i in range(len(intervals)-6)}


def select_candidates(candidates):
    """First successful source-screened candidate versus first proxy-eligible."""
    if type(candidates) is not list or not 1<=len(candidates)<=4:raise ValueError('one to four candidates required')
    valid=[r for r in candidates if r['status']=='complete']
    eligible=[r for r in valid if r['ending']['eligible']]
    return dict(baseline_seed=valid[0]['seed'] if valid else None,
                selected_seed=eligible[0]['seed'] if eligible else None,
                baseline_status='complete' if valid else 'blocked',
                selected_status='complete' if eligible else 'no_eligible_candidate',
                successful_candidates=len(valid),eligible_candidates=len(eligible),candidate_budget=len(candidates))


def generate_group(model,group,*,source_pitches=(),target_ticks=9216):
    """Generate all four, never early-stop or resample unsuccessful groups.

    Existing optimized generator: uniformmix1/4, maxtrailingrest384,
    max256notes, maxpolyphony3. Exact8-onset intervals screen both generated
    and canonical onset orders; it is not perceptual/legal originality proof.
    """
    if type(group) is not int or not 0<=group<=9999:raise ValueError('bounded integer group required')
    if type(target_ticks) is not int or not 1152<=target_ticks<=384*1024:raise ValueError('bounded target required')
    if not isinstance(source_pitches,(list,tuple)) or len(source_pitches)>12:raise ValueError('bounded source list required')
    for source in source_pitches:
        if not isinstance(source,(list,tuple)) or not 1<=len(source)<=512 or any(type(p) is not int or not 0<=p<=127 for p in source):
            raise ValueError('bounded MIDI pitch source required')
    forbidden=set().union(*(_phrases(p) for p in source_pitches))
    candidates=[]
    for offset in range(4):
        seed=group*4+offset
        result=generate_optimized(model,seed,uniform_mix=Fraction(1,4),target_ticks=target_ticks,trailing_rest_ticks=384)
        notes=result['notes'];row=dict(result,seed=seed,ending=ending_features(notes,target_ticks=target_ticks))
        if result['status']=='complete':
            canonical=sorted(notes,key=lambda n:(n['start'],n['end'],n['pitch']))
            matches=(_phrases([n['pitch'] for n in notes])|_phrases([n['pitch'] for n in canonical]))&forbidden
            row['copy_matches']=len(matches)
            if matches:row['status']='copy_guard_blocked'
        candidates.append(row)
    return dict(group=group,candidates=candidates,**select_candidates(candidates))

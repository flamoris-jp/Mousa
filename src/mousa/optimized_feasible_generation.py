"""Equivalent feasible sampler optimization plus separately named endpoint policy.

Release-boundary caching changes computation only, preserving exact integer
masses and RNG draw order. Optional bounded trailing silence changes the stop
rule, not learned cadence: original gates are never clipped or extended.
"""
from fractions import Fraction
import random
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.feasible_context_generation import _weights
from mousa.onset_gate_model import MAX_TICKS, GATE_SIZE, PPQ


def optimized_masses(model,*,previous,previous_gate,notes,remaining_ticks,pitch_weights):
    """Same integer delta masses, legal pitch sum updated only on releases."""
    if type(previous) is not int or not 0<=previous<=PPQ*1024 or type(remaining_ticks) is not int or not 1<=remaining_ticks<=PPQ*1024:
        raise ValueError('bounded integer timing state required')
    if not isinstance(notes,(list,tuple)) or len(notes)>256:
        raise ValueError('bounded note state required')
    if len(pitch_weights)!=len(model.vocabulary) or any(type(w) is not int or w<=0 for w in pitch_weights):
        raise ValueError('positive integer pitch weights required')
    _,_,scale,delta_weights=model._delta_parameters(previous_gate)
    active=[n for n in notes if n['end']>previous]
    if len(active)>3 or len({n['pitch'] for n in active})!=len(active):
        raise ValueError('invalid active polyphony or same-pitch overlap')
    weight_by_pitch=dict(zip(model.vocabulary,pitch_weights));total=sum(pitch_weights)
    releases=sorted((n['end']-previous,n['pitch']) for n in active)
    occupied={n['pitch'] for n in active}
    active_count=len(active);occupied_mass=sum(weight_by_pitch.get(p,0) for p in occupied)
    legal=0 if active_count>=3 else total-occupied_mass
    index=0;masses=[]
    for dt in range(min(MAX_TICKS,remaining_ticks-1)+1):
        changed=False
        while index<len(releases) and releases[index][0]<=dt:
            _,pitch=releases[index];index+=1;active_count-=1
            # Generation ensures unique active pitches, so each release removes
            # exactly its weight. No voices are inferred or silently merged.
            occupied_mass-=weight_by_pitch.get(pitch,0);changed=True
        if changed:legal=0 if active_count>=3 else total-occupied_mass
        cap=min(MAX_TICKS,remaining_ticks-dt)
        masses.append(delta_weights.get(dt,scale)*(model._gate_prefix[cap-1]*GATE_SIZE+cap)*legal)
    return masses


def sample_optimized(model,rng,*,previous,previous_gate,notes,remaining_ticks,pitch_weights):
    masses=optimized_masses(model,previous=previous,previous_gate=previous_gate,notes=notes,
                            remaining_ticks=remaining_ticks,pitch_weights=pitch_weights)
    total=sum(masses)
    if not total:return None
    draw=rng.randrange(total)
    for dt,mass in enumerate(masses):
        if draw<mass:break
        draw-=mass
    cap=min(MAX_TICKS,remaining_ticks-dt)
    draw=rng.randrange(model._gate_prefix[cap-1]*GATE_SIZE+cap)
    gate=None
    for value,count in sorted(model.base.gate_counts.items()):
        if value>cap:break
        if draw<count*GATE_SIZE:
            gate=value;break
        draw-=count*GATE_SIZE
    if gate is None:gate=draw+1
    occupied={n['pitch'] for n in notes if n['end']>previous+dt}
    legal=[(p,w) for p,w in zip(model.vocabulary,pitch_weights) if p not in occupied]
    vocab,weights=zip(*legal)
    return dt,gate,rng.choices(vocab,weights=weights)[0]


def generate_optimized(model,seed,*,uniform_mix=Fraction(0),target_ticks=9216,
                       max_notes=256,max_attempts=64,trailing_rest_ticks=0):
    """Generate with exact conditioning; optionally stop near the endpoint.

    Stop after an accepted note when max existing end >= target-rest bound.
    No empty output may satisfy that rule. EOT is target_ticks and silence is
    explicit metadata; no existing note changes. max_attempts is retained for
    contract parity but exact conditioning needs no repeated rejected draws.
    """
    if not isinstance(model,ContextOnsetGateModel):raise ValueError('fitted context model required')
    if type(seed) is not int or type(target_ticks) is not int or not 1<=target_ticks<=PPQ*1024:
        raise ValueError('integer seed and bounded target required')
    if type(max_notes) is not int or not 1<=max_notes<=256 or type(max_attempts) is not int or not 1<=max_attempts<=64:
        raise ValueError('bounded generation budgets required')
    if type(trailing_rest_ticks) is not int or not 0<=trailing_rest_ticks<=min(384,target_ticks-1):
        raise ValueError('trailing rest bound must be0..min(384,target-1)')
    _weights(model,None,uniform_mix)
    rng=random.Random(seed);notes=[];previous=0;previous_gate=None;previous_pitch=None
    draws=0;last_proposal=None
    def finish(status,reason=None):
        result=dict(status=status,notes=notes,rejections=0,rejection_reasons=dict(active_pitch=0,polyphony=0,no_legal_pitch=0),
            timing_draws=draws,pitch_draws=draws,target_ticks=target_ticks,
            last_accepted_state=dict(onset=previous,gate=previous_gate,pitch=previous_pitch,remaining_ticks=target_ticks-previous),
            last_proposal=last_proposal,endpoint_policy=dict(max_trailing_rest_ticks=trailing_rest_ticks,
                actual_silent_tail_ticks=target_ticks-max(n['end'] for n in notes) if notes else None))
        if reason:result['reason']=reason
        return result
    for _ in range(max_notes):
        proposal=sample_optimized(model,rng,previous=previous,previous_gate=previous_gate,notes=notes,
            remaining_ticks=target_ticks-previous,pitch_weights=_weights(model,previous_pitch,uniform_mix))
        if proposal is None:
            result=finish('blocked','no feasible joint continuation')
            result['rejections']=1;result['rejection_reasons']['no_legal_pitch']=1
            return result
        dt,gate,pitch=proposal;draws+=1;start=previous+dt;end=start+gate
        occupied=sorted(n['pitch'] for n in notes if n['end']>start)
        last_proposal=dict(start=start,end=end,active_pitches=occupied,pitch=pitch)
        notes.append(dict(start=start,end=end,pitch=pitch));previous,previous_gate,previous_pitch=start,gate,pitch
        if max(n['end'] for n in notes)>=target_ticks-trailing_rest_ticks:return finish('complete')
    return finish('blocked','note budget exhausted')

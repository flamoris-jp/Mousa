"""Instrumented generation ablation without modifying frozen context models.

Whole-vocabulary pitch probability mixture precedes feasible-pitch masking.
Feasibility conditions the full timing/pitch proposal on acceptance. Its next
accepted-event law matches rejection sampling, but its RNG path and finite
retry failure law do NOT. The original bounded baseline remains available.
No implicit time advance, clipping, or musical-quality selection is performed.
"""
from fractions import Fraction
import random
from mousa.context_onset_gate import ContextOnsetGateModel
from mousa.onset_gate_model import PPQ, MAX_TICKS, GATE_SIZE


def _weights(model, previous_pitch, uniform_mix):
    if type(uniform_mix) is not Fraction or not 0<=uniform_mix<=1 or uniform_mix.denominator>1000000:
        raise ValueError('bounded Fraction uniform_mix in0..1 required')
    weights=model.pitch_weights(previous_pitch)
    if uniform_mix==0:return weights # preserve original cumulative weights/RNG
    total=sum(weights);size=len(weights);a=uniform_mix
    return [(a.denominator-a.numerator)*w*size+a.numerator*total for w in weights]


def pitch_distribution(model,previous_pitch=None,*,uniform_mix=Fraction(0),forbidden=()):
    """Exact renormalized probabilities; {} explicitly means no legal pitch."""
    if not isinstance(model,ContextOnsetGateModel):raise ValueError('fitted context model required')
    if not isinstance(forbidden,(tuple,list,set,frozenset)) or len(forbidden)>128:
        raise ValueError('bounded forbidden pitches required')
    if any(type(p) is not int or not 0<=p<=127 for p in forbidden):raise ValueError('invalid forbidden pitch')
    weights=_weights(model,previous_pitch,uniform_mix)
    allowed={p:w for p,w in zip(model.vocabulary,weights) if p not in forbidden}
    total=sum(allowed.values())
    return {p:Fraction(w,total) for p,w in allowed.items()}


def feasible_masses(model,*,previous,previous_gate,notes,remaining_ticks,pitch_weights):
    """Integer delta masses proportional to accepted joint proposal mass.

    Active notes at previous onset number at most3 in validated generation.
    Gate feasibility depends on delta; pitch feasibility depends on active
    gates at the proposed onset. No Cartesian outcome array is materialized.
    """
    _,_,scale,delta_weights=model._delta_parameters(previous_gate)
    active_before=[n for n in notes if n['end']>previous]
    masses=[]
    for dt in range(min(MAX_TICKS,remaining_ticks-1)+1):
        active=[n for n in active_before if n['end']>previous+dt]
        if len(active)>=3:
            masses.append(0);continue
        occupied={n['pitch'] for n in active}
        legal_weight=sum(w for p,w in zip(model.vocabulary,pitch_weights) if p not in occupied)
        cap=min(MAX_TICKS,remaining_ticks-dt)
        gate_mass=model._gate_prefix[cap-1]*GATE_SIZE+cap
        masses.append(delta_weights.get(dt,scale)*gate_mass*legal_weight)
    return masses


def _sample_feasible(model,rng,*,previous,previous_gate,notes,remaining_ticks,pitch_weights):
    masses=feasible_masses(model,previous=previous,previous_gate=previous_gate,notes=notes,
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
    pitch=rng.choices(vocab,weights=weights)[0]
    return dt,gate,pitch


def generate_feasible(model,seed,*,feasible_mask=False,uniform_mix=Fraction(0),
                      target_ticks=9216,max_notes=256,max_attempts=64):
    if not isinstance(model,ContextOnsetGateModel):raise ValueError('fitted context model required')
    if type(feasible_mask) is not bool:raise ValueError('boolean feasible_mask required')
    if type(seed) is not int or type(target_ticks) is not int or not 1<=target_ticks<=PPQ*1024:
        raise ValueError('integer seed and bounded target required')
    if type(max_notes) is not int or not 1<=max_notes<=256 or type(max_attempts) is not int or not 1<=max_attempts<=64:
        raise ValueError('bounded generation budgets required')
    _weights(model,None,uniform_mix)
    rng=random.Random(seed);notes=[];previous=0;previous_gate=None;previous_pitch=None
    reasons=dict(active_pitch=0,polyphony=0,no_legal_pitch=0)
    timing_draws=pitch_draws=0;last_proposal=None
    def finish(status,reason=None):
        result=dict(status=status,notes=notes,rejections=sum(reasons.values()),rejection_reasons=reasons.copy(),
            timing_draws=timing_draws,pitch_draws=pitch_draws,target_ticks=target_ticks,
            last_accepted_state=dict(onset=previous,gate=previous_gate,pitch=previous_pitch,
                remaining_ticks=target_ticks-previous),last_proposal=last_proposal)
        if reason:result['reason']=reason
        return result
    for _ in range(max_notes):
        for _ in range(max_attempts):
            weights=_weights(model,previous_pitch,uniform_mix)
            if feasible_mask:
                proposal=_sample_feasible(model,rng,previous=previous,previous_gate=previous_gate,
                    notes=notes,remaining_ticks=target_ticks-previous,pitch_weights=weights)
                if proposal is None:
                    reasons['no_legal_pitch']+=1
                    return finish('blocked','no feasible joint continuation')
                dt,gate,pitch=proposal
                timing_draws+=1;pitch_draws+=1
            else:
                dt,gate=model.sample_pair(rng,remaining_ticks=target_ticks-previous,previous_gate=previous_gate)
                timing_draws+=1
                pitch=rng.choices(model.vocabulary,weights=weights)[0];pitch_draws+=1
            start=previous+dt;end=start+gate
            active=[n for n in notes if n['end']>start]
            occupied={n['pitch'] for n in active}
            last_proposal=dict(start=start,end=end,active_pitches=sorted(occupied),pitch=pitch)
            # Baseline checks occur AFTER drawing pitch, matching original RNG.
            if len(active)>=3:
                reasons['polyphony']+=1;continue
            if pitch in occupied:
                reasons['active_pitch']+=1;continue
            notes.append(dict(start=start,end=end,pitch=pitch))
            previous,previous_gate,previous_pitch=start,gate,pitch
            if end==target_ticks:return finish('complete')
            break
        else:return finish('blocked','attempt budget exhausted')
    return finish('blocked','note budget exhausted')

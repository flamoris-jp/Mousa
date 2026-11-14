"""Handcrafted A-A'-B-A'' comparator, not learned form or quality selection.

Two-bar motifs retain their exact rhythm/rest pattern under semitone shifts.
All constraints are checked again on the assembled eight bars, including joins.
The narrow eight-onset copy guard is not an originality or rights guarantee.
"""
import random

from mousa.factorized_baseline import onset_phrases
from mousa.position_event_model import _bar_steps


def _rest_ok(tokens, cap):
    run = 0
    for token in tokens:
        run = run + 1 if token == 0 else 0
        if cap is not None and run > cap:
            return False
    return True


def _valid_fragment(result, steps):
    if not isinstance(result, dict) or result.get('status') != 'complete':
        return False
    tokens = result.get('tokens')
    if not isinstance(tokens, list) or len(tokens) != steps:
        return False
    active = False
    for token in tokens:
        if type(token) is not int or not 0 <= token <= 26:
            return False
        if token == 1 and not active:
            return False
        active = token != 0
    return True


def generate_phrase_form(model, seed, *, meter, source_grids=(),
                         max_rest_run=12, max_attempts=16):
    """Generate A-A'-B-A'' with independent B and nonzero bounded shifts.

    Uses model.generate, never model fitting or score-based selection. Shifts
    are sampled from +/-1, +/-2 semitones; inadmissible pitches reject the
    attempt, never clip. Each attempt makes exactly two bounded model calls.
    Each source is a bounded grid; supplied sources guard both fragments and
    the final form. Whole-form rejection returns no partial approved output.
    """
    bar = _bar_steps(meter)
    if type(seed) is not int or type(max_attempts) is not int or not 1 <= max_attempts <= 64:
        raise ValueError('integer seed and 1..64 attempts required')
    if max_rest_run is not None and (type(max_rest_run) is not int or not 0 <= max_rest_run <= 4096):
        raise ValueError('max_rest_run must be None or 0..4096')
    if not isinstance(source_grids, (list, tuple)) or len(source_grids) > 12:
        raise ValueError('bounded source list required')
    # onset_phrases performs bounded grid validation, including HOLD semantics.
    forbidden = {phrase for source in source_grids for phrase in onset_phrases(source)}
    rng = random.Random(seed)
    decisions = []
    counts = dict(fragment=0, pitch_bounds=0, rest_boundary=0, source_copy=0)
    fragment_rejections = 0
    for attempt in range(1, max_attempts + 1):
        a_seed, b_seed = rng.getrandbits(64), rng.getrandbits(64)
        shifts = [rng.choice((-2, -1, 1, 2)) for _ in range(2)]
        decision = dict(attempt=attempt, a_seed=a_seed, b_seed=b_seed,
                        transforms=[0, shifts[0], None, shifts[1]])
        args = dict(meter=meter, steps=2 * bar, source_grids=source_grids,
                    guard=True, max_rest_run=max_rest_run, max_attempts=16)
        a, b = model.generate(a_seed, **args), model.generate(b_seed, **args)
        fragment_rejections += sum(r.get('rejections', 0) for r in (a, b) if isinstance(r, dict))
        if not all(_valid_fragment(r, 2 * bar) for r in (a, b)):
            reason = 'fragment'
        else:
            motifs = [[t if t < 2 else t + shift for t in a['tokens']] for shift in shifts]
            if any(not 2 <= t + shift <= 26 for shift in shifts for t in a['tokens'] if t >= 2):
                reason = 'pitch_bounds'
            else:
                tokens = a['tokens'] + motifs[0] + b['tokens'] + motifs[1]
                if not _rest_ok(tokens, max_rest_run):
                    reason = 'rest_boundary'
                elif any(p in forbidden for p in onset_phrases(tokens)):
                    reason = 'source_copy'
                else:
                    decision['status'] = 'accepted'
                    decisions.append(decision)
                    return dict(status='complete', tokens=tokens, form=["A", "A'", "B", "A''"],
                                handcrafted=True, steps=8 * bar, meter=meter,
                                max_rest_run=max_rest_run, decisions=decisions,
                                rejections=counts, fragment_rejections=fragment_rejections,
                                matching_8_note_phrases=0)
        counts[reason] += 1
        decision.update(status='rejected', reason=reason)
        decisions.append(decision)
    return dict(status='blocked', tokens=[], handcrafted=True, steps=8 * bar, meter=meter,
                max_rest_run=max_rest_run, decisions=decisions, rejections=counts,
                fragment_rejections=fragment_rejections, reason='bounded form attempts exhausted')

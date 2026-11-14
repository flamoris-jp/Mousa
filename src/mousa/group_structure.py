"""Descriptive note-group structure, never inferred voices or phrase truth.

Silence-boundary thresholds are explicit analytic conventions, not annotated
phrases. No notes are changed or used as semantic training labels.
"""
from fractions import Fraction
from mousa.onset_groups import group_notes


def describe(notes, total_ticks, *, ppq, gap_beats=(1, 2)):
    if type(ppq) is not int or ppq <= 0:
        raise ValueError('positive integer PPQ required')
    if type(gap_beats) is not tuple or not gap_beats or any(type(x) is not int or x <= 0 for x in gap_beats):
        raise ValueError('positive integer gap thresholds required')
    groups = group_notes(notes, total_ticks)
    anchors = [min(m.note.pitch for m in g.members) for g in groups]
    spans = [max(m.note.pitch for m in g.members)-min(m.note.pitch for m in g.members) for g in groups]
    transitions = [abs(b-a) for a,b in zip(anchors,anchors[1:])]
    previous_end = 0
    gaps = []
    # Running maximum includes every earlier sounding note, not just previous group.
    for i,g in enumerate(groups):
        if i: gaps.append(max(0, g.onset-previous_end))
        previous_end = max(previous_end, max(m.note.end for m in g.members))
    profiles = []
    for threshold in gap_beats:
        boundaries = [i+1 for i,gap in enumerate(gaps) if gap >= threshold*ppq]
        cuts = [0,*boundaries,len(groups)] if groups else [0]
        profiles.append(dict(threshold_beats=threshold, boundary_group_indices=boundaries,
                             segment_group_counts=[b-a for a,b in zip(cuts,cuts[1:])]))
    return dict(groups=len(groups), notes=len(notes), transitions=len(transitions),
                anchor_absolute_interval_sum=sum(transitions),
                anchor_mean_absolute_interval=float(Fraction(sum(transitions),len(transitions))) if transitions else None,
                anchor_repeat_count=sum(x==0 for x in transitions),
                within_group_span_sum=sum(spans),
                internal_silent_ticks=gaps, silence_boundary_profiles=profiles,
                first_onset=groups[0].onset if groups else None,
                trailing_silence_ticks=total_ticks-previous_end,
                interpretation='Minimum pitch is an anchor, not an inferred bass/voice. Silence segments are threshold conventions, not human phrase labels.')

"""Bounded, transposition-invariant approximate source screen, not clearance."""
from mousa.factorized_baseline import onset_phrases


def interval_edit_similarity(left, right):
    """Normalized Levenshtein similarity of onset pitch intervals.

    Ignores rhythm/gaps deliberately to flag rhythmic rewrites; exact phrase
    guard remains separate. Whole-sequence metric may miss short borrowed
    excerpts. Reject >512 onsets rather than silently skip an expensive screen.
    """
    onset_phrases(left);onset_phrases(right)  # existing strict grid validation
    pitches=[[t for t in grid if t>=2] for grid in (left,right)]
    if max(map(len,pitches))>512:raise ValueError('approximate screen limited to 512 onsets per work')
    a,b=[[y-x for x,y in zip(p,p[1:])] for p in pitches]
    previous=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        row=[i]
        for j,y in enumerate(b,1):row.append(min(row[-1]+1,previous[j]+1,previous[j-1]+(x!=y)))
        previous=row
    distance=previous[-1];denominator=max(len(a),len(b))
    # Empty pitch-interval strings do not prove identity of two short songs.
    similarity=1-distance/denominator if denominator else None
    return dict(left_intervals=len(a),right_intervals=len(b),edit_distance=distance,
                normalized_similarity=similarity,comparable=min(len(a),len(b))>=16,
                rhythm_ignored=True,scope='whole pitch-interval sequence, not perceptual similarity')

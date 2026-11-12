"""Exact old normalized interval edit score, larger explicit resource profile.

No banding, early acceptance, truncation, quantization, or threshold change.
Two integer rows retain O(min(interval lengths)) memory; time is O(n*m).
This descriptor is not musical meaning or a legal-copy decision.
"""
MAX_INTERVALS=2048


def similarity(a,b):
    if not isinstance(a,(list,tuple)) or not isinstance(b,(list,tuple)):
        raise ValueError('pitch sequences required')
    if len(a)>MAX_INTERVALS+1 or len(b)>MAX_INTERVALS+1:
        raise ValueError('2048 interval comparison bound exceeded')
    if any(type(p) is not int or not 0<=p<=127 for p in (*a,*b)):
        raise ValueError('absolute MIDI pitches required')
    x=[v-u for u,v in zip(a,a[1:])];y=[v-u for u,v in zip(b,b[1:])]
    if not x or not y:return None
    denominator=max(len(x),len(y))
    if len(y)>len(x):x,y=y,x
    row=list(range(len(y)+1))
    for i,value in enumerate(x,1):
        new=[i]
        for j,other in enumerate(y,1):
            new.append(min(new[-1]+1,row[j]+1,row[j-1]+(value!=other)))
        row=new
    return 1-row[-1]/denominator

"""Descriptive block occupancy/anchor recurrence, never an appeal score."""
from collections import Counter

def structure(notes,groups,target=9216):
    if target!=9216 or type(notes) is not list or type(groups) is not list or len(notes)>256 or len(groups)>256:
        raise ValueError('fixed bounded8bar output required')
    if any(type(n) is not dict or type(n.get('start')) is not int or type(n.get('end')) is not int or not 0<=n['start']<n['end']<=target for n in notes):
        raise ValueError('bounded exact note endpoints')
    if any(type(g) is not dict or type(g.get('onset')) is not int or type(g.get('anchor')) is not int or not 0<=g['onset']<target or not 0<=g['anchor']<=127 for g in groups):
        raise ValueError('bounded group fields')
    if any(a['onset']>=b['onset'] for a,b in zip(groups,groups[1:])):raise ValueError('strict group ordering')
    blocks=[];sequences=[]
    for i,label in enumerate('ABCD'):
        start=i*2304;end=start+2304
        local=[g for g in groups if start<=g['onset']<end]
        anchors=[g['anchor'] for g in local];iv=[b-a for a,b in zip(anchors,anchors[1:])] if len(anchors)>=2 else None
        sequences.append(iv)
        intervals=sorted((max(start,n['start']),min(end,n['end'])) for n in notes if n['start']<end and n['end']>start)
        occupied=0;front=start
        for a,b in intervals:
            occupied+=max(0,b-max(front,a));front=max(front,b)
        blocks.append(dict(block=label,start=start,end=end,onset_groups=len(local),note_onsets=sum(start<=n['start']<end for n in notes),
                           sounding_notes=len(intervals),occupied_ticks=occupied,silence_ticks=2304-occupied,
                           anchor_intervals=iv,interval_status='missing_empty' if not anchors else 'missing_single_group' if len(anchors)==1 else 'available',
                           interval_count=max(0,len(anchors)-1)))
    pairs=[]
    for i in range(4):
        for j in range(i+1,4):
            a,b=sequences[i],sequences[j]
            pairs.append(dict(blocks='ABCD'[i]+'ABCD'[j],comparable=a is not None and b is not None,equal=(a==b) if a is not None and b is not None else None))
    anchors=[g['anchor'] for g in groups];iv=[b-a for a,b in zip(anchors,anchors[1:])]
    grams=Counter(tuple(iv[i:i+3]) for i in range(max(0,len(iv)-2)))
    windows=sum(grams.values());repeat=windows-len(grams)
    return dict(blocks=blocks,block_interval_pairs=pairs,comparable_pairs=sum(p['comparable'] for p in pairs),
                equal_pairs=sum(p['equal'] is True for p in pairs),anchor_interval_3gram=dict(intervals=len(iv),windows=windows,unique=len(grams),repeated_windows_after_first=repeat,repeat_fraction=repeat/windows if windows else None),
                meaning='Half-open2barblocks. Onset counts differ from sounding notes. Occupancy uses exact interval union clipped ONLY for measurement. Block intervals are signed consecutive minimum-pitch anchors, not melodyvoice; equality requires>=2groups, no alignment.3gram uses overlapping windows of3signed anchor intervals (4groups), repeated occurrences beyondfirst; windows notindependent.')

"""Exact occupied-sound boundaries; segmentation is not phrase truth."""
def segments(notes,groups,threshold=192):
    if type(threshold) is not int or threshold!=192:raise ValueError('fixed192tick diagnostic')
    if not isinstance(notes,list) or not isinstance(groups,list) or len(notes)>100000 or len(groups)>4096:raise ValueError('bounded inputs')
    # Group maximum gate includes all prior still-sounding voices, not last group.
    frontier=0;result=[];current=[];gaps=[]
    for i,g in enumerate(groups):
        onset=g['onset']
        if type(onset) is not int or onset<0 or (i and onset<=groups[i-1]['onset']):raise ValueError('ordered groups')
        end=max(onset+t[1] for t in g['template'])
        if current and onset-frontier>=threshold:
            result.append(current);gaps.append(dict(previous_end=frontier,next_start=onset,silence_ticks=onset-frontier));current=[]
        current.append(i);frontier=max(frontier,end)
    if current:result.append(current)
    # Caller retains full original notes; verify group reconstruction endpoint multiset.
    expected=sorted((g['onset'],g['onset']+t[1]) for g in groups for t in g['template'])
    if expected!=sorted((n['start'],n['end']) for n in notes):raise ValueError('note/group timing mismatch')
    return dict(segments=result,boundaries=gaps,threshold_ticks=192,interpretation='Complete-sound gaps>=192ticks; leading/trailing silence not independent segments. No melodic voice or phrase annotation.')

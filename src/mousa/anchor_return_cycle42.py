"""Post-result exploratory pitch-only return, not a learned phrase model."""
from copy import deepcopy
from mousa.phrase_groups_cycle41 import validate_notes, validate_groups, phrases

def compare_anchors(notes,groups,source_pitch_sequences):
    validate_notes(notes);validate_groups(notes,groups)
    if not isinstance(source_pitch_sequences,(tuple,list)) or len(source_pitch_sequences)!=21:
        raise ValueError('exact21 complete original references required')
    forbidden=set()
    for seq in source_pitch_sequences:
        if not isinstance(seq,(list,tuple)) or not 1<=len(seq)<=8192 or any(type(p) is not int or not 0<=p<=127 for p in seq):
            raise ValueError('bounded MIDI pitch references required')
        forbidden.update(phrases(seq))
    def checked(ns,gs):
        validate_notes(ns);validate_groups(ns,gs)
        canonical=sorted(ns,key=lambda n:(n['start'],n['end'],n['pitch']))
        matches=(phrases([n['pitch'] for n in ns])|phrases([n['pitch'] for n in canonical]))&forbidden
        return dict(status='copy_guard_blocked' if matches else 'complete',copy_matches=len(matches),notes=ns,groups=gs,target_ticks=9216)
    control=checked(deepcopy(notes),deepcopy(groups))
    a=[g for g in groups if g['onset']<2304]
    ci=[i for i,g in enumerate(groups) if 4608<=g['onset']<6912]
    def blocked(status,**kw):
        return dict(control=control,intervention=dict(status=status,target_ticks=9216,**kw))
    if not a:return blocked('empty_A_blocked')
    if not ci:return blocked('empty_C_blocked')
    outgroups=deepcopy(groups);changed=0;changednotes=0
    for j,i in enumerate(ci):
        anchor=a[j%len(a)]['anchor']+2
        if anchor!=groups[i]['anchor']:
            changed+=1;changednotes+=groups[i]['count']
        outgroups[i]['anchor']=anchor
    edit=dict(A_groups=len(a),C_groups=len(ci),full_cycles=len(ci)//len(a),remainder=len(ci)%len(a),
              changed_anchors=changed,changed_notes=changednotes,shift=2,
              original_C_anchors=[groups[i]['anchor'] for i in ci],
              mapped_C_anchors=[outgroups[i]['anchor'] for i in ci])
    # Anchor arrays stay in private candidate data; public driver omits them.
    if not changed:return blocked('no_effect',edit=edit)
    out=[]
    for g in outgroups:
        for offset,gate,vel,release in g['template']:
            out.append(dict(start=g['onset'],end=g['onset']+gate,pitch=g['anchor']+offset,velocity=vel,release_velocity=release))
    if any(not 0<=n['pitch']<=127 for n in out):
        return blocked('pitch_range_blocked',edit=edit)
    try:v=checked(out,outgroups)
    except ValueError as exc:return blocked('safety_blocked',reason=str(exc),edit=edit)
    assert len(out)==len(notes)
    assert all({k:v for k,v in x.items() if k!='pitch'}=={k:v for k,v in y.items() if k!='pitch'} for x,y in zip(notes,out))
    v.update(edit=edit,temporal_velocity_order_preserved=True,templates_preserved=all(x['template']==y['template'] for x,y in zip(groups,outgroups)))
    return dict(control=control,intervention=v)

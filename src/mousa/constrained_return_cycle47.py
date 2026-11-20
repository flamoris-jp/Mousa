"""Collision-constrained exact octave search; singleton fallback is not phrase."""
from copy import deepcopy
from time import process_time
from mousa.phrase_groups_cycle41 import validate_notes,validate_groups,phrases
from mousa.silence_segments_cycle46 import segments
from mousa.phrasewide_register_cycle44 import optimal_anchors

def constrained_path(groups,indices,bases,notes,*,state_cap=4096,transition_cap=200000,cpu_deadline=None):
    if not 1<=len(indices)<=256 or len(indices)!=len(bases) or type(state_cap) is not int or not 1<=state_cap<=4096 or type(transition_cap) is not int or not 1<=transition_cap<=200000:
        raise ValueError('bounded aligned DP')
    if indices!=list(range(indices[0],indices[-1]+1)) or any(type(i) is not int or not 0<=i<len(groups) for i in indices) or any(type(b) is not int or not 0<=b<=129 for b in bases):raise ValueError('contiguous bounded indices/pitchclasses')
    entrance=groups[indices[0]-1]['anchor'] if indices[0] else None
    exit_anchor=groups[indices[-1]+1]['anchor'] if indices[-1]+1<len(groups) else None
    target_onsets={groups[i]['onset'] for i in indices}
    fixed=[n for n in notes if n['start'] not in target_onsets]
    # State retains last anchor and ALL still active selected note pitches/ends.
    states={(entrance,()):(0,())};transitions=0;peak=1
    for i,base in zip(indices,bases):
        g=groups[i];onset=g['onset'];offset=max(t[0] for t in g['template'])
        choices=[v for v in range(128-offset) if (v-base)%12==0]
        if not choices:return dict(status='no_legal_register',transitions=transitions,peak_states=peak)
        nextstates={}
        for (previous,active),(cost,path) in states.items():
            alive=tuple((p,e) for p,e in active if e>onset)
            for anchor in choices:
                if cpu_deadline is not None and process_time()>=cpu_deadline:return dict(status='cpu_budget_blocked',transitions=transitions,peak_states=peak)
                transitions+=1
                if transitions>transition_cap:return dict(status='dp_budget_blocked',transitions=transitions,peak_states=peak)
                new=tuple((anchor+o,onset+gate) for o,gate,_,_ in g['template'])
                if any(p==q for p,_ in new for q,_ in alive):continue
                if any(n['pitch']==p and n['start']<end and n['end']>onset for p,end in new for n in fixed):continue
                key=(anchor,tuple(sorted(alive+new)))
                candidate=(cost+(abs(anchor-previous) if previous is not None else 0),path+(anchor,))
                if key not in nextstates or candidate<nextstates[key]:nextstates[key]=candidate
                if len(nextstates)>state_cap:return dict(status='dp_budget_blocked',transitions=transitions,peak_states=len(nextstates))
        if not nextstates:return dict(status='no_collision_free_path',transitions=transitions,peak_states=peak)
        states=nextstates;peak=max(peak,len(states))
    cost,path=min((cost+(abs(last-exit_anchor) if exit_anchor is not None else 0),path) for (last,_),(cost,path) in states.items())
    return dict(status='optimal',anchors=list(path),objective=cost,transitions=transitions,peak_states=peak)

def compare_policy(notes,groups,refs,*,collision_constrained=False,allow_singleton=False,cpu_deadline=None):
    if type(collision_constrained) is not bool or type(allow_singleton) is not bool:raise ValueError('fixed boolean policies')
    validate_notes(notes);validate_groups(notes,groups)
    if type(refs) is not list or len(refs)!=22:raise ValueError('22 original references')
    forbidden=set()
    for ref in refs:
        if not isinstance(ref,(list,tuple)) or not 1<=len(ref)<=8192 or any(type(p) is not int or not 0<=p<=127 for p in ref):raise ValueError('MIDI pitchrefs')
        forbidden|=phrases(ref)
    split=segments(notes,groups)['segments'];a=split[0] if split else [];ci=split[2] if len(split)>=3 else []
    def blocked(status,**extra):return dict(status=status,**extra)
    if not a or (len(a)==1 and not allow_singleton):return blocked('source_segment_too_short',source_groups=len(a))
    if len(ci)<2:return blocked('target_segment_missing_or_short',target_groups=len(ci),segment_count=len(split))
    bases=[groups[a[j%len(a)]]['anchor']+2 for j in range(len(ci))]
    if collision_constrained:solution=constrained_path(groups,ci,bases,notes,cpu_deadline=cpu_deadline)
    else:
        entrance=groups[ci[0]-1]['anchor'] if ci[0] else None
        exit_anchor=groups[ci[-1]+1]['anchor'] if ci[-1]+1<len(groups) else None
        value=optimal_anchors(bases,[max(t[0] for t in groups[i]['template']) for i in ci],entrance,exit_anchor)
        solution=dict(status='optimal',**value) if value else dict(status='no_legal_register')
    if solution['status']!='optimal':return blocked(solution['status'],dp={k:v for k,v in solution.items() if k!='anchors'})
    gs=deepcopy(groups)
    for i,anchor in zip(ci,solution['anchors']):gs[i]['anchor']=anchor
    changed=sum(gs[i]['anchor']!=groups[i]['anchor'] for i in ci)
    metadata=dict(source_groups=len(a),target_groups=len(ci),singleton_fallback=len(a)==1,objective=solution['objective'],changed_anchors=changed)
    if not changed:return blocked('no_effect',**metadata)
    ns=[dict(start=g['onset'],end=g['onset']+gate,pitch=g['anchor']+o,velocity=v,release_velocity=rv) for g in gs for o,gate,v,rv in g['template']]
    try:validate_notes(ns);validate_groups(ns,gs)
    except ValueError as exc:return blocked('safety_blocked',reason=str(exc),**metadata)
    canonical=sorted(ns,key=lambda n:(n['start'],n['end'],n['pitch']))
    hits=(phrases([n['pitch'] for n in ns])|phrases([n['pitch'] for n in canonical]))&forbidden
    status='copy_guard_blocked' if hits else 'singleton_fallback_complete' if len(a)==1 else 'complete'
    return dict(status=status,copy_matches=len(hits),notes=ns,groups=gs,**metadata,dp={k:v for k,v in solution.items() if k not in ('anchors','status','objective')})

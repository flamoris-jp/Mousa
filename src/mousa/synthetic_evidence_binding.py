"""Bind fictional records to exact fixture bytes and symbolic measurements.

Digest agreement is not origin/authorship verification, consent, semantic truth
or training permission. No natural-language claim or listener report is judged.
"""
import hashlib
import json
from mousa.semantic_evidence import validate


def bind(record,source_bytes,artifact_bytes):
    validate(record)
    if type(source_bytes) is not bytes or type(artifact_bytes) is not bytes or not 1<=len(source_bytes)<=100000 or not 1<=len(artifact_bytes)<=100000:
        raise ValueError('bounded fixture bytes required')
    for name,data in (('source',source_bytes),('artifact',artifact_bytes)):
        if hashlib.sha256(data).hexdigest()!=record[name]['sha256']:
            raise ValueError('digest mismatch')
    try:artifact=json.loads(artifact_bytes.decode('utf-8'))
    except (UnicodeDecodeError,json.JSONDecodeError) as exc:raise ValueError('fixture JSON required') from exc
    if type(artifact) is not dict or set(artifact)!={'synthetic','ppq','total_ticks','notes'} or artifact['synthetic'] is not True:
        raise ValueError('synthetic fixture fields required')
    if type(artifact['ppq']) is not int or not 1<=artifact['ppq']<=32767 or type(artifact['total_ticks']) is not int or not 1<=artifact['total_ticks']<=1024*artifact['ppq']:
        raise ValueError('fixture clock bounds')
    segment=record['segment']
    if segment['ppq']!=artifact['ppq'] or segment['artifact_total_ticks']!=artifact['total_ticks'] or segment['track']!=1:
        raise ValueError('scope/clock mismatch')
    notes=artifact['notes']
    if type(notes) is not list or len(notes)>256:raise ValueError('fixture note bound')
    a,b=segment['start_tick'],segment['end_tick'];intervals=[];pitches=set();onsets=0
    for note in notes:
        if type(note) is not dict or set(note)!={'start','end','pitch'} or any(type(note[k]) is not int for k in note):
            raise ValueError('fixture note fields')
        start,end,pitch=note['start'],note['end'],note['pitch']
        if not 0<=start<end<=artifact['total_ticks'] or not 0<=pitch<=127:raise ValueError('fixture note bounds')
        if a<=start<b:onsets+=1
        if start<b and end>a:intervals.append((max(start,a),min(end,b)));pitches.add(pitch)
    # Union of sounding intervals, including held notes starting before scope.
    sounding=0;left=right=None
    for start,end in sorted(intervals):
        if left is None:left,right=start,end
        elif start<=right:right=max(right,end)
        else:sounding+=right-left;left,right=start,end
    if left is not None:sounding+=right-left
    return dict(exact_fixture_hashes_match=True,artifact_scope_matches=True,
                measurements=dict(scope_ticks=b-a,sounding_ticks=sounding,rest_ticks=b-a-sounding,
                                  onsets_in_scope=onsets,distinct_sounding_pitches=len(pitches)),
                declared_evidence_kind=record['evidence']['kind'],wording_verified=False,
                origin_or_actor_verified=False,consent_verified=False,training_eligible=False,
                interpretation='Exact fictional bytes and arithmetic only; not musical meaning, preference or authorization.')

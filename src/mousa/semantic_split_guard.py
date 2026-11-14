"""Fictional semantic split audit, not consent, identity or training admission.

Family/source/artifact declarations are checked for internal coherence only.
Actual family identification and byte provenance require separate review.
"""
from collections import Counter,defaultdict
import re


def audit(rows):
    if type(rows) not in (list,tuple) or len(rows)>1000:raise ValueError('bounded rows required')
    ids=set();groups={k:defaultdict(set) for k in ('family_id','source_sha256','artifact_sha256')}
    source_families=defaultdict(set);artifact_sources=defaultdict(set)
    counts=Counter();families=defaultdict(set);artifacts=defaultdict(set)
    for r in rows:
        if type(r) is not dict or set(r)!={'item_id','family_id','source_sha256','artifact_sha256','split','synthetic'}:
            raise ValueError('exact fictional split fields required')
        if r['synthetic'] is not True:raise ValueError('synthetic only')
        if any(type(r[k]) is not str or not r[k].strip() or len(r[k])>128 for k in ('item_id','family_id')):
            raise ValueError('bounded identity strings required')
        if r['item_id'] in ids:raise ValueError('duplicate item id')
        ids.add(r['item_id'])
        if r['split'] not in ('train','validation','test'):raise ValueError('split role')
        for k in ('source_sha256','artifact_sha256'):
            if type(r[k]) is not str or not re.fullmatch('[a-f0-9]{64}',r[k]):raise ValueError('digest format')
        for k in groups:groups[k][r[k]].add(r['split'])
        source_families[r['source_sha256']].add(r['family_id'])
        artifact_sources[r['artifact_sha256']].add(r['source_sha256'])
        counts[r['split']]+=1;families[r['split']].add(r['family_id']);artifacts[r['split']].add(r['artifact_sha256'])
    violations=[]
    for kind,values in groups.items():
        for key,roles in sorted(values.items()):
            if len(roles)>1:violations.append(dict(reason='cross_split_'+kind,key=key,splits=sorted(roles)))
    for key,values in sorted(source_families.items()):
        if len(values)>1:violations.append(dict(reason='conflicting_source_family',key=key))
    for key,values in sorted(artifact_sources.items()):
        if len(values)>1:violations.append(dict(reason='conflicting_artifact_source',key=key))
    return dict(schema_rows=len(rows),partition_consistent=not violations,violations=violations,
                row_counts=dict(counts),family_counts={s:len(v) for s,v in families.items()},
                artifact_counts={s:len(v) for s,v in artifacts.items()},training_authorized=False,
                actual_human_reports=0,
                limitation='Declared synthetic groups only; no verified family labels, identities, real feedback or permissions.')

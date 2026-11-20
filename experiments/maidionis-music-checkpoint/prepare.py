"""Prepare pinned historical-only pitch/rhythm task rows; never fit or score."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import random

HISTORICAL_SHA = '49ff7ee03687d77d1707d82985266f9b51fa836154a924ef7529873ea9f6171f'
SPLIT_SHA = 'a08f7201e846e09c91e79036c74fefe687e8c431e353f33163d6c935cfbad517'
EXTRACTOR_SHA = 'ea05cc3df8206ebab9d5488fd33f63690370897d975eb892a3bbc389d09cc1ae'


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encoded(value): return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
def checked(path, expected):
    if sha(path) != expected:
        raise ValueError('pinned file digest mismatch')
    return json.loads(Path(path).read_text())


def task_rows(pitch, rhythm, indices, family, cohort):
    if not family or cohort not in ('train', 'historical_observed'):
        raise ValueError('family/cohort invalid')
    if len(pitch) != len(rhythm) or len(set(indices)) != len(indices):
        raise ValueError('unaligned features or repeated indices')
    for seq, support in ((pitch,49),(rhythm,25)):
        if any(type(v) is not int or not 0 <= v < support for v in seq):
            raise ValueError('feature label outside support')
    rows = []
    for i in indices:
        if type(i) is not int or not 8 <= i < len(pitch):
            raise ValueError('invalid target index')
        history = [v for j in range(i-8,i) for v in (pitch[j]+3,rhythm[j]+52)]
        for task,control,label in [('pitch',1,pitch[i]),('rhythm',2,rhythm[i])]:
            rows.append({'family':family,'target_index':i,'cohort':cohort,'task':task,
                         'input':[control]+history,'label':label})
    return rows


def schedules(size):
    if type(size) is not int or size <= 0: raise ValueError('positive row count required')
    epochs = []
    for epoch in range(3):
        order = list(range(size)); random.Random(42+epoch).shuffle(order)
        epochs.append({'epoch':epoch,'seed':42+epoch,
                       'batches':[order[i:i+32] for i in range(0,size,32)]})
    return epochs


def validate_split(train, test):
    if {r['family'] for r in train} & {r['family'] for r in test}:
        raise ValueError('train/test family overlap')
    for rows in (train,test):
        keys=[(r['family'],r['target_index'],r['task']) for r in rows]
        if len(keys)!=len(set(keys)):raise ValueError('duplicate task row')


def prepare(historical, split_path, extractor, out):
    if out.exists(): raise ValueError('output must not exist')
    h=checked(historical,HISTORICAL_SHA);s=checked(split_path,SPLIT_SHA)
    if sha(extractor)!=EXTRACTOR_SHA:raise ValueError('extractor digest mismatch')
    train_arms=[a for a in h['arms'] if a['condition']=='train128_ordered']
    if len(train_arms)!=3 or any(a['train']!=train_arms[0]['train'] for a in train_arms):
        raise ValueError('historical arms inconsistent')
    old={'train':train_arms[0]['train'],'historical_observed':h['test']}
    if {r['family'] for r in old['train']} & {r['family'] for r in old['historical_observed']}:
        raise ValueError('historical family overlap')
    if (len(old['train']),len(old['historical_observed']),len({r['family'] for r in old['train']}),len({r['family'] for r in old['historical_observed']}))!=(4084,512,128,16):
        raise ValueError('unexpected historical cohort')
    # Hash every metadata dependency before using the rights/family assignment.
    for key,expected in s['input_sha256'].items():
        if sha(s['input_paths'][key])!=expected:raise ValueError('evidence digest mismatch: '+key)
    allows={c:json.loads(Path(s['input_paths'][c+'_allowlist']).read_text()) for c in ['pd','by']}
    rights={c:{r['mutopia_id']:r for r in json.loads(Path(s['input_paths'][c+'_rights']).read_text())['records']} for c in ['pd','by']}
    members={r['family_id']:r for r in s['members']}
    spec=importlib.util.spec_from_file_location('pinned_midi_extractor',extractor)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    outputs={};sources=[]
    for cohort,rows in old.items():
        groups={}
        for row in rows:groups.setdefault(row['family'],[]).append(row)
        result=[]
        for family, selected in groups.items():
            member=members[family];c=member['corpus']
            if c not in ('pd','by') or 'ShareAlike' in member['license']:
                raise ValueError('source not PD/BY')
            if member['split']!=('train' if cohort=='train' else 'test'):
                raise ValueError('historical role mismatch')
            matching=[f for f in allows[c]['files'] if f['path']==member['midi_relative_path'] and f['sha256']==member['sha256']]
            if len(matching)!=1 or not matching[0]['eligible_for_note_event_training'] or not rights[c][member['selected_source_id']]['rights_eligible']:
                raise ValueError('rights or exact-file allowlist failed')
            if sha(member['source_path'])!=member['sha256']:raise ValueError('raw source digest mismatch')
            features,total,_=mod.read_projection(Path(member['source_path']),member['sha256'],2048)
            pitch,rhythm=features['pitch_interval'],features['rhythm_ioi']
            for r in selected:
                i=r['target_index']
                if [1]+[v+2 for v in pitch[i-8:i]]!=r['input'] or pitch[i]!=r['label']:
                    raise ValueError('reextracted pitch disagrees with pinned historical row')
            result.extend(task_rows(pitch,rhythm,[r['target_index'] for r in selected],family,cohort))
            sources.append({k:member[k] for k in ('family_id','selected_source_id','corpus','split','sha256','source_page','license','license_url','attribution')}|{'source_path':member['source_path'],'onsets_total':total,'event_windows':len(selected),'cohort':cohort})
        outputs['train' if cohort=='train' else 'test']=result
    validate_split(outputs['train'],outputs['test'])
    if (len(outputs['train']),len(outputs['test']))!=(8168,1024):raise ValueError('task row totals')
    schedule=schedules(len(outputs['train']))
    outputs['epochs']=[epoch['batches'] for epoch in schedule]
    outputs['schedule_metadata']=[{k:v for k,v in epoch.items() if k!='batches'} for epoch in schedule]
    data=encoded(outputs)
    receipt={'status':'prepared_not_fitted','data_sha256':hashlib.sha256(data).hexdigest(),'prepare_sha256':sha(__file__),'preparation_plan_sha256':sha(Path(__file__).with_name('preparation-plan.json')),'historical_sha256':HISTORICAL_SHA,'split_sha256':SPLIT_SHA,'extractor_sha256':EXTRACTOR_SHA,'train_families':128,'test_families':16,'train_event_windows':4084,'test_event_windows':512,'train_task_rows':8168,'test_task_rows':1024,'test_status':'previously observed historical only; no reserved8 or20 raw files read','epochs':3,'batches_per_epoch':256,'last_batch_size':8,'source_files_verified':len(sources)}
    out.mkdir(parents=True,exist_ok=False)
    (out/'data.json').write_bytes(data)
    (out/'preparation-receipt.json').write_bytes(encoded(receipt))
    (out/'source-attribution-private.json').write_bytes(encoded({'sources':sources,'modification':'highest-onset projection; pitch and quantized log-IOI features; eight strictly prior paired events, no raw mutation'}))
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('historical','split','extractor','out'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();print(json.dumps(prepare(a.historical,a.split,a.extractor,a.out),indent=2))

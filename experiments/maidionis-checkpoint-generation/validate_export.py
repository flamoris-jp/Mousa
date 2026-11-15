"""Fixed structural/copy screens and private MIDI export, not musical clearance."""
import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
from math import log2
from pathlib import Path

HISTORICAL_SHA='49ff7ee03687d77d1707d82985266f9b51fa836154a924ef7529873ea9f6171f'
SPLIT_SHA='a08f7201e846e09c91e79036c74fefe687e8c431e353f33163d6c935cfbad517'
EXTRACTOR_SHA='ea05cc3df8206ebab9d5488fd33f63690370897d975eb892a3bbc389d09cc1ae'
REFERENCE_SHA='35c7eae3219aed805ed8f872290107d7067c9056690e3406d1f1ce3f80bef6b3'
PPQ=480
END_TICK=15360
GAPS=(120,240,480,960)

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encoded(value):return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode()
def checked(path,digest):
    if sha(path)!=digest:raise ValueError('pinned digest mismatch')
    return json.loads(Path(path).read_text())

def prepare_references(historical,split,extractor,out):
    if out.exists():raise ValueError('output exists')
    h=checked(historical,HISTORICAL_SHA);s=checked(split,SPLIT_SHA)
    if sha(extractor)!=EXTRACTOR_SHA:raise ValueError('extractor digest mismatch')
    arms=[a for a in h['arms'] if a['condition']=='train128_ordered']
    if len(arms)!=3 or any(a['train']!=arms[0]['train'] for a in arms):raise ValueError('historical arms mismatch')
    rows=arms[0]['train'];families={r['family'] for r in rows}
    if len(rows)!=4084 or len(families)!=128:raise ValueError('historical training size')
    for key,digest in s['input_sha256'].items():
        if sha(s['input_paths'][key])!=digest:raise ValueError('metadata digest mismatch')
    allows={c:json.loads(Path(s['input_paths'][c+'_allowlist']).read_text()) for c in ('pd','by')}
    rights={c:{r['mutopia_id']:r for r in json.loads(Path(s['input_paths'][c+'_rights']).read_text())['records']} for c in ('pd','by')}
    members={r['family_id']:r for r in s['members']}
    spec=importlib.util.spec_from_file_location('pinned_extractor',extractor);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    refs=[]
    for family in sorted(families):
        m=members[family];c=m['corpus']
        if c not in ('pd','by') or m['split']!='train' or 'ShareAlike' in m['license']:raise ValueError('not authorized historical training source')
        matches=[f for f in allows[c]['files'] if f['path']==m['midi_relative_path'] and f['sha256']==m['sha256']]
        if len(matches)!=1 or not matches[0]['eligible_for_note_event_training'] or not rights[c][m['selected_source_id']]['rights_eligible']:raise ValueError('rights/allowlist failed')
        if sha(m['source_path'])!=m['sha256']:raise ValueError('raw hash failed')
        features,total,_=mod.read_projection(Path(m['source_path']),m['sha256'],2048)
        pitch=features['pitch_interval'];rhythm=features['rhythm_ioi']
        if len(pitch)!=len(rhythm):raise ValueError('projection alignment')
        for r in (x for x in rows if x['family']==family):
            i=r['target_index']
            if pitch[i]!=r['label'] or [1]+[v+2 for v in pitch[i-8:i]]!=r['input']:raise ValueError('historical projection mismatch')
        refs.append({'family':family,'source_sha256':m['sha256'],'source_id':m['selected_source_id'],'source_path':m['source_path'],'license':m['license'],'source_page':m['source_page'],'attribution':m['attribution'],'total_source_onsets':total,'pitch':pitch,'rhythm':rhythm})
    payload={'schema':'mousa-generated-copy-references-v1','historical_sha256':HISTORICAL_SHA,'split_sha256':SPLIT_SHA,'extractor_sha256':EXTRACTOR_SHA,'references':refs,'scope':'128 trained families only, first2048 projected onsets; no heldout/reserved files read'}
    out.mkdir(parents=True,exist_ok=False);(out/'references-private.json').write_bytes(encoded(payload))
    receipt={'reference_families':128,'reference_sha256':sha(out/'references-private.json'),'source_hashes_verified':128,'historical_targets_verified':4084,'raw_files_mutated':False,'heldout_or_reserve_read':False,'reference_onset_prefix_limit':2048}
    (out/'reference-receipt.json').write_bytes(encoded(receipt));return receipt

def validate_events(events):
    if not isinstance(events,list) or not 1<=len(events)<=128:raise ValueError('event count')
    for i,event in enumerate(events):
        if any(type(event.get(k)) is not int for k in ('pitch','onset_tick','duration_tick')):raise ValueError('integer event fields required')
        if not 48<=event['pitch']<=84:raise ValueError('pitch range')
        if event.get('velocity',80)!=80:raise ValueError('fixed velocity')
        onset=event['onset_tick'];next_onset=events[i+1]['onset_tick'] if i+1<len(events) else END_TICK
        if type(next_onset) is not int or not 0<=onset<END_TICK or onset%120:raise ValueError('onset grid/range')
        gap=next_onset-onset
        if gap not in GAPS:raise ValueError('gap outside frozen set')
        if event['duration_tick']!=gap*9//10:raise ValueError('duration must be90percent of gap')
        if 'gap_tick' in event and event['gap_tick']!=gap:raise ValueError('gap trace mismatch')
        if i and abs(event['pitch']-events[i-1]['pitch'])>12:raise ValueError('interval range')
    if events[0]['onset_tick']!=0 or events[0]['pitch']!=60:raise ValueError('initial event differs from protocol')
    return {'pitch':[b['pitch']-a['pitch']+24 for a,b in zip(events,events[1:])],
            'rhythm':[round(2*log2((b['onset_tick']-a['onset_tick'])/PPQ))+12 for a,b in zip(events,events[1:])]}

def longest_contiguous(a,b):
    """Exact longest contiguous run; intervals make pitch comparison transpose-invariant."""
    locations=defaultdict(list)
    for j,value in enumerate(b):locations[value].append(j)
    previous={};best=0
    for value in a:
        current={j:previous.get(j-1,0)+1 for j in locations.get(value,())}
        if current:best=max(best,max(current.values()))
        previous=current
    return best

def copy_screen(features,references):
    if not references:raise ValueError('no copy references')
    comparisons=[]
    for ref in references:
        if len(ref['pitch'])!=len(ref['rhythm']):raise ValueError('reference alignment')
        pitch=longest_contiguous(features['pitch'],ref['pitch'])
        paired=longest_contiguous(list(zip(features['pitch'],features['rhythm'])),list(zip(ref['pitch'],ref['rhythm'])))
        comparisons.append({'family':ref['family'],'pitch_interval_run':pitch,'paired_interval_ioi_run':paired,'blocked':pitch>=12 or paired>=8})
    return {'blocked':any(r['blocked'] for r in comparisons),'max_pitch_interval_run':max(r['pitch_interval_run'] for r in comparisons),'max_paired_interval_ioi_run':max(r['paired_interval_ioi_run'] for r in comparisons),'comparisons':comparisons}

def write_midi(events,path):
    import mido
    validate_events(events)
    if path.exists():raise ValueError('MIDI output exists')
    midi=mido.MidiFile(type=0,ticks_per_beat=PPQ);track=mido.MidiTrack();midi.tracks.append(track)
    track.extend([mido.MetaMessage('set_tempo',tempo=600000,time=0),mido.MetaMessage('time_signature',numerator=4,denominator=4,time=0),mido.Message('program_change',channel=0,program=0,time=0)])
    tick=0
    for event in events:
        track.append(mido.Message('note_on',channel=0,note=event['pitch'],velocity=80,time=event['onset_tick']-tick))
        track.append(mido.Message('note_off',channel=0,note=event['pitch'],velocity=0,time=event['duration_tick']))
        tick=event['onset_tick']+event['duration_tick']
    track.append(mido.MetaMessage('end_of_track',time=END_TICK-tick))
    with path.open('xb') as f:midi.save(file=f)
    verify_midi(events,path)

def verify_midi(events,path):
    import mido
    midi=mido.MidiFile(path)
    if midi.type!=0 or midi.ticks_per_beat!=PPQ or len(midi.tracks)!=1:raise ValueError('MIDI header mismatch')
    tick=0;active=None;restored=[];tempos=[];meters=[];programs=[];ended=False
    for msg in midi.tracks[0]:
        tick+=msg.time
        if msg.type=='note_on' and msg.velocity:
            if active is not None or msg.channel!=0 or msg.velocity!=80:raise ValueError('overlap/channel/velocity')
            active=(msg.note,tick)
        elif msg.type=='note_off' or (msg.type=='note_on' and not msg.velocity):
            if active is None or msg.channel!=0 or msg.note!=active[0]:raise ValueError('unmatched noteoff')
            restored.append({'pitch':active[0],'onset_tick':active[1],'duration_tick':tick-active[1]});active=None
        elif msg.type=='set_tempo':tempos.append((tick,msg.tempo))
        elif msg.type=='time_signature':meters.append((tick,msg.numerator,msg.denominator))
        elif msg.type=='program_change':programs.append((tick,msg.channel,msg.program))
        elif msg.type=='end_of_track':
            if active is not None or tick!=END_TICK:raise ValueError('end tick/active note')
            ended=True
        else:raise ValueError('unexpected MIDI message')
    expected=[{k:e[k] for k in ('pitch','onset_tick','duration_tick')} for e in events]
    if restored!=expected or tempos!=[(0,600000)] or meters!=[(0,4,4)] or programs!=[(0,0,0)] or not ended:raise ValueError('MIDI roundtrip mismatch')
    return True


def export_candidates(native_path,reference_path,receipt_path,out):
    if out.exists():raise ValueError('output exists')
    receipt=json.loads(receipt_path.read_text())
    if sha(reference_path)!=REFERENCE_SHA or receipt['reference_sha256']!=REFERENCE_SHA or receipt['reference_families']!=128:raise ValueError('reference receipt mismatch')
    refs=json.loads(reference_path.read_text())['references']
    if len(refs)!=128 or len({r['family'] for r in refs})!=128:raise ValueError('reference family count')
    native=json.loads(native_path.read_text())
    if (native.get('ppq'),native.get('end_tick'),native.get('tempo_bpm'),native.get('meter'))!=(480,15360,100,[4,4]):raise ValueError('native timing header mismatch')
    candidates=native['samples']
    if [c['seed'] for c in candidates]!=[101,102,103]:raise ValueError('candidate seeds/order mismatch')
    out.mkdir(parents=True,exist_ok=False);private=[];public=[]
    for c in candidates:
        record={'seed':c['seed'],'generated_events':len(c['events'])}
        try:
            if c.get('synthetic_primer_emitted') is not False or c.get('event_count')!=len(c['events']):raise ValueError('native event metadata mismatch')
            if len(c['trace'])!=len(c['events']):raise ValueError('native trace count')
            events=[]
            for i,(e,t) in enumerate(zip(c['events'],c['trace'])):
                if e.get('channel')!=0 or e.get('velocity')!=80:raise ValueError('native channel/velocity')
                gap=(c['events'][i+1]['onset_tick'] if i+1<len(c['events']) else END_TICK)-e['onset_tick']
                if t['onset_tick']!=e['onset_tick'] or t['gap_ticks']!=gap:raise ValueError('native gap trace mismatch')
                if t['rhythm_label']!=round(2*log2(gap/PPQ))+12:raise ValueError('native rhythm trace mismatch')
                if i+1<len(c['events']) and t['pitch_label']!=c['events'][i+1]['pitch']-e['pitch']+24:raise ValueError('native pitch trace mismatch')
                events.append({'pitch':e['pitch'],'onset_tick':e['onset_tick'],'duration_tick':e['duration_ticks']})
            features=validate_events(events);screen=copy_screen(features,refs)
            record.update(screen,structurally_valid=True,exported=False)
            if not screen['blocked']:
                path=out/f"mousa-checkpoint-seed{c['seed']}-8bars.mid";write_midi(events,path)
                record.update(exported=True,midi_file=path.name,midi_sha256=sha(path),midi_bytes=path.stat().st_size,roundtrip_verified=True)
        except ValueError as error:record.update(structurally_valid=False,exported=False,error=str(error))
        private.append(record);public.append({k:v for k,v in record.items() if k!='comparisons'})
    base={'schema':'mousa-checkpoint-generation-export-v1','native_sha256':sha(native_path),'reference_sha256':sha(reference_path),'reference_families':128,'copy_thresholds':{'pitch_interval_run':12,'paired_interval_ioi_run':8},'limitations':'Bounded first2048-onset128-training-family exact-run screen, not broad plagiarism/copyright clearance or musical quality; no regeneration/retries','no_human_audition':True}
    for name,records in [('report-private.json',private),('report-public.json',public)]:
        (out/name).write_bytes(encoded(dict(base,candidates=records)))
    return dict(base,candidates=public)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    prep=sub.add_parser('prepare-references')
    for key in ('historical','split','extractor','out'):prep.add_argument('--'+key,type=Path,required=True)
    export=sub.add_parser('export')
    for key in ('native','references','receipt','out'):export.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args()
    result=prepare_references(a.historical,a.split,a.extractor,a.out) if a.command=='prepare-references' else export_candidates(a.native,a.references,a.receipt,a.out)
    print(json.dumps(result,indent=2))

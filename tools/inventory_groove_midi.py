"""Bounded private MIDI-only intake inventory; no music-model fit or audio.

Official distribution splits are recorded, not certified independent performers
or patterns. Near-duplicate and pattern-family analysis remains pending.
"""
import argparse
from collections import Counter,defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path,PurePosixPath
import re
import stat
from zipfile import ZipFile

EXPECTED='651cbc524ffb891be1a3e46d89dc82a1cecb09a57c748c7b45b844c4841dcc1e'
MAX_TOTAL=20_000_000


def sha(data):return hashlib.sha256(data).hexdigest()


def safe_name(name):
    if type(name) is not str or not name or '\\' in name or ':' in name or any(ord(c)<32 for c in name):raise ValueError('unsafe ZIP path')
    path=PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or '.' in name.split('/') or not path.parts or path.parts[0]!='groove':raise ValueError('unsafe ZIP path')
    return path


def inspect_archive(z):
    infos=z.infolist()
    if len(infos)>2000 or sum(i.file_size for i in infos)>MAX_TOTAL:raise ValueError('archive resource bound')
    names=set();accepted=[];ignored=[]
    for i in infos:
        mode=i.external_attr>>16
        if i.flag_bits&1 or stat.S_ISLNK(mode):raise ValueError('encrypted/symlink member')
        # Known zero-byte macOS decoration: explicitly omit, never materialize.
        if i.filename.endswith('/Icon\r') and i.file_size==0:
            safe_name(i.filename[:-5]+'Icon');ignored.append('zero-byte Icon carriage-return decoration');continue
        name=safe_name(i.filename);normalized=str(name)
        if normalized in names:raise ValueError('duplicate normalized path')
        names.add(normalized)
        if i.file_size>2_000_000:raise ValueError('member size bound')
        if i.is_dir():continue
        if not (i.filename.endswith('.mid') or i.filename in ('groove/info.csv','groove/LICENSE','groove/README')):raise ValueError('unexpected non-MIDI member')
        accepted.append(i)
    return accepted,ignored


def csv_rows(data,midi_names):
    if len(data)>1_000_000:raise ValueError('CSV byte bound')
    reader=csv.DictReader(io.StringIO(data.decode('utf-8')))
    fields={'drummer','session','id','style','bpm','beat_type','time_signature','midi_filename','audio_filename','duration','split'}
    if set(reader.fieldnames or [])!=fields:raise ValueError('unexpected CSV fields')
    rows=list(reader)
    if not 1<=len(rows)<=1500:raise ValueError('CSV row bound')
    ids=set();filenames=set()
    for r in rows:
        if set(r)!=fields or any(type(v) is not str or len(v)>1000 for v in r.values()):raise ValueError('malformed row')
        name='groove/'+r['midi_filename'];safe_name(name)
        if name in filenames or r['id'] in ids:raise ValueError('duplicate CSV identity')
        filenames.add(name);ids.add(r['id'])
        if not re.fullmatch(r'drummer[0-9]{1,2}',r['drummer']):raise ValueError('non-anonymous drummer ID')
        if not r['session'].startswith(r['drummer']+'/') or not r['midi_filename'].startswith(r['session']+'/'):raise ValueError('session path mismatch')
        if r['split'] not in ('train','validation','test'):raise ValueError('unexpected split')
        if not 0<float(r['bpm'])<1000 or not 0<float(r['duration'])<86400:raise ValueError('invalid descriptive time metadata')
    if filenames!=set(midi_names):raise ValueError('CSV/ZIP MIDI inventory mismatch')
    return rows


def note_metrics(data):
    import mido
    midi=mido.MidiFile(file=io.BytesIO(data))
    if len(midi.tracks)>64 or not 1<=midi.ticks_per_beat<=32767 or sum(len(t) for t in midi.tracks)>250000:raise ValueError('MIDI resource bound')
    on=off=zero=0;keys=Counter();channels=Counter();velocities=Counter();types=Counter();ticks=0;tempos=0;meters=set()
    for track in midi.tracks:
        absolute=0
        for msg in track:
            if type(msg.time) is not int or msg.time<0:raise ValueError('invalid MIDI delta')
            absolute+=msg.time
            if absolute>midi.ticks_per_beat*4*10000:raise ValueError('MIDI timeline bound')
            types[msg.type]+=1
            if msg.type=='note_on' and msg.velocity>0:
                on+=1;keys[msg.note]+=1;channels[msg.channel]+=1;velocities[msg.velocity]+=1
            elif msg.type=='note_off' or msg.type=='note_on' and msg.velocity==0:
                off+=1;zero+=msg.type=='note_on'
            elif msg.type=='set_tempo':tempos+=1
            elif msg.type=='time_signature':meters.add(f'{msg.numerator}/{msg.denominator}')
        ticks=max(ticks,absolute)
    return dict(ppq=midi.ticks_per_beat,tracks=len(midi.tracks),note_on_positive=on,note_off_equivalent=off,zero_velocity_note_on=zero,
        drum_key_counts=dict(keys),note_channel_counts=dict(channels),velocity_min=min(velocities,default=None),velocity_max=max(velocities,default=None),
        end_tick=ticks,tempo_events=tempos,time_signatures=sorted(meters),message_type_counts=dict(types),
        scope='Event counts only; drum key numbers are instrument labels, not melodic pitch. Note pairing/near-pattern analysis not claimed.')


def run(archive,output):
    if output.exists():raise ValueError('new private destination required')
    if archive.stat().st_size>5_000_000:raise ValueError('archive size bound')
    raw=archive.read_bytes()
    if sha(raw)!=EXPECTED:raise ValueError('not reviewed original MIDI-only release')
    with ZipFile(io.BytesIO(raw)) as z:
        members,ignored=inspect_archive(z);midi_names=[i.filename for i in members if i.filename.endswith('.mid')]
        rows=csv_rows(z.read('groove/info.csv'),midi_names)
        if len(rows)!=1150:raise ValueError('official release expected1150')
        output.mkdir(parents=True);extracted=output/'originals';extracted.mkdir()
        records=[];hashgroups=defaultdict(list);split=Counter();styles=Counter();drummers=defaultdict(set);sessions=defaultdict(set);patterns=defaultdict(list)
        for row in rows:
            name='groove/'+row['midi_filename'];data=z.read(name)
            path=extracted.joinpath(*safe_name(name).parts);path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(data)
            if sha(path.read_bytes())!=sha(data):raise ValueError('write verification mismatch')
            met=note_metrics(data);record=dict(**row,sha256=sha(data),bytes=len(data),relative_path=str(path.relative_to(output)),metrics=met)
            records.append(record);hashgroups[record['sha256']].append(row['id']);split[row['split']]+=1;styles[row['style']]+=1
            drummers[row['drummer']].add(row['split']);sessions[row['session']].add(row['split'])
            if '/eval_session' in row['session']:patterns[row['style']].append(dict(id=row['id'],drummer=row['drummer'],split=row['split']))
        for name in ('groove/info.csv','groove/LICENSE','groove/README'):
            target=extracted.joinpath(*safe_name(name).parts);target.write_bytes(z.read(name))
        inventory=dict(archive_sha256=EXPECTED,records=records,storage_files=[dict(relative_path=r['relative_path'],sha256=r['sha256'],bytes=r['bytes']) for r in records],
                       purpose='Private original MIDI storage inventory; no audio files retrieved, no corpus fit')
        (output/'private-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
        report=dict(archive_sha256=EXPECTED,archive_bytes=len(raw),archive_entries=len(z.infolist()),archive_uncompressed_bytes=sum(i.file_size for i in z.infolist()),
            midi_files=len(records),unique_midi_hashes=len(hashgroups),midi_bytes=sum(r['bytes'] for r in records),csv_exact_inventory_match=True,all_original_hashes_verified=True,
            ignored_zero_byte_decorations=len(ignored),split_counts=dict(split),style_label_counts=dict(styles),top_level_style_counts=dict(Counter(r['style'].split('/')[0] for r in rows)),
            drummer_splits={k:sorted(v) for k,v in drummers.items()},sessions=len(sessions),session_splits={k:sorted(v) for k,v in sessions.items()},
            drummer_cross_split=[k for k,v in drummers.items() if len(v)>1],session_cross_split=[k for k,v in sessions.items() if len(v)>1],
            exact_byte_duplicate_groups=[dict(sha256=k,ids=v,splits=sorted({r['split'] for r in rows if r['id'] in v})) for k,v in hashgroups.items() if len(v)>1],
            eval_pattern_series=dict(patterns),metrics=dict(note_on_positive=sum(r['metrics']['note_on_positive'] for r in records),
                note_off_equivalent=sum(r['metrics']['note_off_equivalent'] for r in records),
                ppq_values=sorted({r['metrics']['ppq'] for r in records}),note_channels=sorted({k for r in records for k in r['metrics']['note_channel_counts']})),
            metadata_duration_seconds_sum=sum(float(r['duration']) for r in rows),
            limitations=['Separate drum corpus, never combined with pitched melody12training; model fits0/audio downloads0.',
                        'Original split recorded, not independent unseen drummer/session/pattern validation.',
                        'Eval sessions share10named patterns; cross-performer series explicitly grouped, near-duplicate timing/pattern analysis still pending.',
                        'Exact bytes only deduplication; not composition independence or musical originality.',
                        'Style labels are source metadata, not verified genre diversity; anonymous drummer IDs retained.'])
        (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--archive',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    print(json.dumps(run(a.archive,a.output),indent=2))

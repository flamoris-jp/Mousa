"""Paired private audition using the saved joint model; no fit or retries."""
import argparse, hashlib, importlib.util, json, random, subprocess
from pathlib import Path
from math import log2
from mousa.rhythm_learning import encode,sample_event,descriptors,VELOCITIES
from mousa.degrees import Degree
from mousa.scales import ScaleCondition,Key,load_catalogue

def write_midi(events,path,end):
    import mido
    m=mido.MidiFile(type=0,ticks_per_beat=480);t=mido.MidiTrack();m.tracks.append(t)
    t.extend([mido.MetaMessage('set_tempo',tempo=600000),mido.MetaMessage('time_signature',numerator=4,denominator=4),mido.Message('program_change',program=0)])
    last=0
    for e in events:
        start=e['onset_unit']*40;duration=(e['labels'][2]+1)*40
        t.append(mido.Message('note_on',note=e['pitch'],velocity=VELOCITIES[e['labels'][4]],time=start-last))
        t.append(mido.Message('note_off',note=e['pitch'],velocity=0,time=duration));last=start+duration
    t.append(mido.MetaMessage('end_of_track',time=end*40-last))
    with path.open('xb') as f:m.save(file=f)
    # Independent parser roundtrip reconstructs exact note-on/off sequence.
    read=mido.MidiFile(path);absolute=0;active=None;got=[]
    for msg in read.tracks[0]:
        absolute+=msg.time
        if msg.type=='note_on' and msg.velocity:
            assert active is None;active=(absolute,msg.note,msg.velocity)
        elif msg.type=='note_off':
            assert active and msg.note==active[1]
            got.append((*active,absolute-active[0]));active=None
    expected=[(e['onset_unit']*40,e['pitch'],VELOCITIES[e['labels'][4]],(e['labels'][2]+1)*40) for e in events]
    assert got==expected and active is None and absolute==end*40
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--binary',required=True);p.add_argument('--model',required=True);p.add_argument('--references',type=Path,required=True);p.add_argument('--gate',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(exist_ok=False,parents=True)
    spec=importlib.util.spec_from_file_location('gate',a.gate);gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
    assert gate.sha(a.references)==gate.REFERENCE_SHA
    refs=json.loads(a.references.read_text())['references']
    process=subprocess.Popen([a.binary,'serve',a.model],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    condition=ScaleCondition(load_catalogue()['major_12tet'],Key.from_name('C4'))
    reports=[]
    try:
        for seed in (101,102,103):
            rng=random.Random(seed);history=[[64,11,8,3,2,0] for _ in range(8)];events=[];traces=[];onset=0
            while onset<384:
                rows=[{'input':encode(history,7,onset%48,task),'label':64 if task==0 else 0,'task':task,'family':'generated'} for task in range(6)]
                process.stdin.write(json.dumps(rows)+'\n');process.stdin.flush()
                line=process.stdout.readline()
                if not line:raise RuntimeError('inference process ended')
                result=json.loads(line);probs=[r['probabilities'] for r in result]
                event=sample_event(probs,7,384-onset,rng)
                degree=Degree.from_label(event[0],7);pitch=round(condition.pitch_cents(degree.degree,degree.period)/100)
                events.append({'onset_unit':onset,'labels':event,'pitch':pitch})
                traces.append({'history':history,'position':onset%48,'scores':result,'selected':event})
                history=history[1:]+[event];onset+=event[1]+1
                assert len(events)<=384
            fixed=[{'onset_unit':i*12,'labels':[e['labels'][0],11,8,3,2,0],'pitch':e['pitch']} for i,e in enumerate(events)]
            for name,notes,end in [('learned',events,384),('fixed',fixed,len(fixed)*12)]:
                pitch=[notes[i]['pitch']-notes[i-1]['pitch']+24 for i in range(1,len(notes))]
                rhythm=[round(2*log2((notes[i]['onset_unit']-notes[i-1]['onset_unit'])/12))+12 for i in range(1,len(notes))]
                screen=gate.copy_screen({'pitch':pitch,'rhythm':rhythm},refs)
                row={'seed':seed,'variant':name,'end_tick':end*40,'seconds':end/12*.6,'descriptors':descriptors(notes),'screen':screen,'exported':not screen['blocked']}
                if row['exported']:row['midi_sha256']=write_midi(notes,a.out/f'{name}-{seed}.mid',end)
                reports.append(row)
            (a.out/f'trace-{seed}.json').write_text(json.dumps({'events':events,'trace':traces}))
    finally:
        process.stdin.close();process.wait(timeout=20)
    assert process.returncode==0
    (a.out/'report.json').write_text(json.dumps(reports,indent=2))
    print(json.dumps([{k:v for k,v in r.items() if k!='screen'} for r in reports],indent=2))
if __name__=='__main__':main()

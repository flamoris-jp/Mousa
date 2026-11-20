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
    p=argparse.ArgumentParser();p.add_argument('--binary',required=True);p.add_argument('--model',required=True);p.add_argument('--arm',choices=['independent','rhythm_first'],required=True);p.add_argument('--references',type=Path,required=True);p.add_argument('--gate',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(exist_ok=False,parents=True)
    spec=importlib.util.spec_from_file_location('gate',a.gate);gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
    assert gate.sha(a.references)==gate.REFERENCE_SHA
    refs=json.loads(a.references.read_text())['references']
    process=subprocess.Popen([a.binary,'serve',a.model],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    def query(rows):
        process.stdin.write(json.dumps(rows)+'\n');process.stdin.flush()
        line=process.stdout.readline()
        if not line:raise RuntimeError('inference process ended')
        return json.loads(line)
    condition=ScaleCondition(load_catalogue()['major_12tet'],Key.from_name('C4'));reports=[]
    from mousa.rhythm_learning import categorical
    try:
        for seed in (101,102,103):
            timing_rng=random.Random(seed);degree_rng=random.Random(seed+1000000)
            history=[[64,11,8,3,2,0] for _ in range(8)];events=[];traces=[];onset=0
            def timing(history,onset):
                rows=[{'input':encode(history,7,onset%48,task)+[0,0,0],'label':0,'task':task,'family':'generated'} for task in range(1,6)]
                result=query(rows);dummy=[0.0]*192;dummy[64]=1.0
                event=sample_event([dummy]+[r['probabilities'] for r in result],7,384-onset,timing_rng)
                return event,result
            def pitch_fill(history,onset,event):
                suffix=[event[1]+311,event[2]+359,event[3]+407] if a.arm=='rhythm_first' else [0,0,0]
                row={'input':encode(history,7,onset%48,0)+suffix,'label':64,'task':0,'family':'generated'}
                score=query([row])[0];event=list(event)
                event[0]=categorical(score['probabilities'],degree_rng)
                degree=Degree.from_label(event[0],7);pitch=round(condition.pitch_cents(degree.degree,degree.period)/100)
                return event,pitch,row,score
            if a.arm=='rhythm_first':
                plan=[]
                while onset<384:
                    event,result=timing(history,onset)
                    assert event[0]==64
                    plan.append({'onset':onset,'event':event,'timing_history':history,'scores':result})
                    history=history[1:]+[event];onset+=event[1]+1
                    assert len(plan)<=384
                # Complete all rhythm choices before the first actual degree query.
                history=[[64,11,8,3,2,0] for _ in range(8)]
                for step in plan:
                    onset=step['onset'];event,pitch,row,score=pitch_fill(history,onset,step['event'])
                    events.append({'onset_unit':onset,'labels':event,'pitch':pitch})
                    traces.append({'history':history,'timing_history':step['timing_history'],'position':onset%48,'timing_scores':step['scores'],'degree_input':row['input'],'degree_score':score,'selected':event})
                    history=history[1:]+[event]
            else:
                while onset<384:
                    event,result=timing(history,onset)
                    event,pitch,row,score=pitch_fill(history,onset,event)
                    events.append({'onset_unit':onset,'labels':event,'pitch':pitch})
                    traces.append({'history':history,'timing_history':history,'position':onset%48,'timing_scores':result,'degree_input':row['input'],'degree_score':score,'selected':event})
                    history=history[1:]+[event];onset+=event[1]+1
                    assert len(events)<=384
            pitch=[events[i]['pitch']-events[i-1]['pitch']+24 for i in range(1,len(events))]
            rhythm=[round(2*log2((events[i]['onset_unit']-events[i-1]['onset_unit'])/12))+12 for i in range(1,len(events))]
            screen=gate.copy_screen({'pitch':pitch,'rhythm':rhythm},refs)
            row={'seed':seed,'variant':a.arm,'end_tick':15360,'seconds':19.2,'descriptors':descriptors(events),'screen':screen,'exported':not screen['blocked']}
            if row['exported']:row['midi_sha256']=write_midi(events,a.out/f'{a.arm}-{seed}.mid',384)
            reports.append(row)
            (a.out/f'trace-{seed}.json').write_text(json.dumps({'events':events,'trace':traces}))
    finally:
        process.stdin.close();process.wait(timeout=20)
    assert process.returncode==0
    (a.out/'report.json').write_text(json.dumps(reports,indent=2))
    print(json.dumps([{k:v for k,v in r.items() if k!='screen'} for r in reports],indent=2))
if __name__=='__main__':main()

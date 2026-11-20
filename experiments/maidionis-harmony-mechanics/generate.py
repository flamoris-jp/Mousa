"""Private fixed-rule vs learned-arpeggio mechanics preview, not music benchmark."""
import argparse,json,hashlib,random,subprocess
from pathlib import Path
from mousa.harmony import make_progression,vary_progression,resolve_progression
from mousa.scales import ScaleCondition,Key,load_catalogue
from mousa.degrees import Degree
from prepare import teacher,FAMILY

def sample(p,rng):
    x=rng.random();total=0
    for i,v in enumerate(p):
        total+=v
        if x<total:return i
    raise ValueError('invalid distribution')

def midi(notes,chords,path):
    import mido
    m=mido.MidiFile(type=0,ticks_per_beat=480);t=mido.MidiTrack();m.tracks.append(t)
    t.extend([mido.MetaMessage('set_tempo',tempo=600000),mido.MetaMessage('time_signature',numerator=4,denominator=4),mido.Message('program_change',channel=0,program=0),mido.Message('program_change',channel=1,program=0)])
    events=[]
    for row in chords:
        for p in row['midi_notes']:
            events.extend([(row['start_tick'],1,0,p,48),(row['start_tick']+row['duration_ticks'],0,0,p,0)])
    for n in notes:events.extend([(n['tick'],1,1,n['pitch'],80),(n['tick']+180,0,1,n['pitch'],0)])
    last=0
    for tick,on,ch,p,v in sorted(events):t.append(mido.Message('note_on' if on else 'note_off',channel=ch,note=p,velocity=v,time=tick-last));last=tick
    t.append(mido.MetaMessage('end_of_track',time=15360-last))
    with path.open('xb') as f:m.save(file=f)
    parsed=mido.MidiFile(path);active={};got=[];tick=0
    for msg in parsed.tracks[0]:
        tick+=msg.time
        if msg.type=='note_on' and msg.velocity:
            assert (msg.channel,msg.note) not in active;active[(msg.channel,msg.note)]=tick
        elif msg.type=='note_off':assert (msg.channel,msg.note) in active;start=active.pop((msg.channel,msg.note));got.append((start,tick,msg.channel,msg.note))
    expected=[(n['tick'],n['tick']+180,1,n['pitch']) for n in notes]+[(r['start_tick'],r['start_tick']+r['duration_ticks'],0,p) for r in chords for p in r['midi_notes']]
    assert not active and tick==15360 and sorted(got)==sorted(expected)
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--binary',required=True);p.add_argument('--model',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(exist_ok=False,parents=True)
    proc=subprocess.Popen([a.binary,'serve',a.model],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    def query(rows):
        proc.stdin.write(json.dumps(rows)+'\n');proc.stdin.flush();line=proc.stdout.readline()
        if not line:raise RuntimeError('model terminated')
        return json.loads(line)
    harmony=ScaleCondition(load_catalogue()['major_12tet'],Key.from_name('C3'));melody=ScaleCondition(load_catalogue()['major_12tet'],Key.from_name('C4'));base=make_progression(repeats=2);varied,variation=vary_progression(base,harmony,amount=.5,seed=17);reports=[]
    try:
        for variant,progression in [('base',base),('varied',varied)]:
            chords=resolve_progression(progression,harmony)
            for mode in ('fixed','model'):
                history=[64]*8;notes=[];trace=[];rng=random.Random(101)
                for i in range(64):
                    chord=progression.chords[i//8];phase=i%8;root=chord.root.degree;seventh=int(chord.quality.endswith('7'))
                    row={'family_id':FAMILY,'degree_count':7,'history':history,'target':64,'chord_root':root,'chord_seventh':seventh,'phase':phase,'gap_index':0}
                    if mode=='model':
                        altered={**row,'chord_root':(root+1)%7};original,other=query([row,altered]);p=original['probabilities'];label=sample(p,rng)
                        trace.append({'row':row,'probabilities':p,'label':label,'counterfactual_root':altered['chord_root'],'counterfactual_l1':sum(abs(x-y) for x,y in zip(p,other['probabilities']))})
                    else:label=teacher(root,seventh,phase,0)
                    degree=Degree.from_label(label,7);pitch=round(melody.pitch_cents(degree.degree,degree.period)/100)
                    notes.append({'tick':i*240,'pitch':pitch,'label':label});history=history[1:]+[label]
                name=f'{variant}-{mode}';digest=midi(notes,chords,a.out/(name+'.mid'))
                report={'name':name,'notes':64,'end_tick':15360,'midi_sha256':digest,'chord_tone_fraction':sum(n['pitch']%12 in {p%12 for p in chords[i//8]['midi_notes']} for i,n in enumerate(notes))/64,'mean_root_counterfactual_l1':sum(t['counterfactual_l1'] for t in trace)/len(trace) if trace else None}
                reports.append(report);(a.out/(name+'.json')).write_text(json.dumps({'notes':notes,'chords':chords,'trace':trace},indent=2))
        (a.out/'report.json').write_text(json.dumps({'teacher_only':True,'quality_claim':False,'variation':variation,'candidates':reports},indent=2))
    finally:proc.stdin.close();proc.wait(timeout=20)
    assert proc.returncode==0
    print(json.dumps(reports,indent=2))
if __name__=='__main__':main()

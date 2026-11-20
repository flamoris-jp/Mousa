"""Original rule-teacher fixture, one train-only family; not real chord annotations."""
import argparse,json
from pathlib import Path
from mousa.harmony import PATTERNS,make_progression,vary_progression
from mousa.scales import ScaleCondition,Key,load_catalogue
TASK='mousa.harmony-degree-mechanics.experimental.v1'
FAMILY='mousa:major-chord-rule-fixtures:v1'

def teacher(root,seventh,phase,gap_index):
    # Deliberate simple arpeggio teacher. Learning this is rule distillation only.
    offsets=(0,2,4,6) if seventh else (0,2,4)
    ordinal=root+offsets[(phase//(1+gap_index))%len(offsets)]
    return 64+(ordinal%7)+64*(ordinal//7)

def sequence(progression,gap_index):
    history=[64]*8;rows=[];gap=240*(1+gap_index)
    for chord in progression.chords:
        root=chord.root.degree;seventh=int(chord.quality.endswith('7'))
        for tick in range(0,chord.duration_ticks,gap):
            phase=(tick//240)%8;target=teacher(root,seventh,phase,gap_index)
            rows.append({'family_id':FAMILY,'degree_count':7,'history':list(history),'target':target,'chord_root':root,'chord_seventh':seventh,'phase':phase,'gap_index':gap_index})
            history=history[1:]+[target]
    return rows

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    condition=ScaleCondition(load_catalogue()['major_12tet'],Key.from_name('C3'));rows=[]
    for pattern in PATTERNS:
        base=make_progression(pattern,repeats=2)
        for amount in (0,.5,1):
            progression,_=vary_progression(base,condition,amount=amount,seed=17)
            for gap_index in (0,1):rows+=sequence(progression,gap_index)
    data={'schema':'mousa.harmony-degree-training.experimental.v1','task_id':TASK,'rows':rows}
    a.out.mkdir(exist_ok=False,parents=True);(a.out/'data.json').write_text(json.dumps(data,indent=2)+'\n')
    (a.out/'provenance.json').write_text(json.dumps({'family_id':FAMILY,'source':'original #21 major progression rule fixtures + original deterministic arpeggio teacher','license':'Apache-2.0 synthetic fixture code only','train_only':True,'rows':len(rows),'external_music_read':False,'real_chord_annotations':False,'heldout':False,'chord_variations':'fixed #21 rule, not learned'},indent=2)+'\n')
if __name__=='__main__':main()

"""Synthetic transform sensitivity, not plagiarism labels or admission thresholds."""
import argparse
from datetime import datetime,timezone
from fractions import Fraction
import json
from pathlib import Path
from compare_context_onset_gate import digest
from compare_onset_gate_models import phrases,similarity


def validate(notes):
    if type(notes) is not tuple or not 1<=len(notes)<=64:raise ValueError('bounded synthetic note tuple required')
    previous=-1
    for note in notes:
        if type(note) is not tuple or len(note)!=3:raise ValueError('pitch,onset,gate tuple required')
        pitch,onset,gate=note
        if any(type(x) is not int for x in note) or not 0<=pitch<=127 or not 0<=onset<=100000 or not 1<=gate<=10000 or onset<=previous:
            raise ValueError('invalid synthetic monophonic-onset fixture')
        previous=onset
    return notes


def windows(notes,*,rhythm=False,normalized=False):
    validate(notes);result=set()
    for i in range(len(notes)-7):
        w=notes[i:i+8]
        intervals=tuple(b[0]-a[0] for a,b in zip(w,w[1:]))
        if not rhythm:result.add(intervals);continue
        deltas=tuple(b[1]-a[1] for a,b in zip(w,w[1:]));gates=tuple(n[2] for n in w)
        if normalized:
            scale=deltas[0]
            deltas=tuple(Fraction(d,scale) for d in deltas);gates=tuple(Fraction(g,scale) for g in gates)
        result.add((intervals,deltas,gates))
    return result


def compare(reference,candidate):
    validate(reference);validate(candidate)
    p=[n[0] for n in reference];q=[n[0] for n in candidate]
    result=dict(reference_notes=len(reference),candidate_notes=len(candidate),
        exact8_interval_matches=len(phrases(p)&phrases(q)),
        whole_interval_edit_similarity=similarity(p,q))
    for key,normalize in (('exact8_interval_onset_gate_matches',False),('scale_normalized8_interval_onset_gate_matches',True)):
        result[key]=len(windows(reference,rhythm=True,normalized=normalize)&windows(candidate,rhythm=True,normalized=normalize))
    return result


def fixtures():
    # Explicitly authored artificial contours; no external compositions/data.
    pitches=(60,61,66,63,70,64,65,72)
    deltas=(96,144,192,48,120,168,72)
    gates=(60,100,160,36,96,120,48,180)
    now=0;base=[]
    for i,p in enumerate(pitches):
        base.append((p,now,gates[i]))
        if i<7:now+=deltas[i]
    base=tuple(base)
    scale=tuple((60+2*i,96*i,72) for i in range(8))
    repeated=tuple((60,96*i,72) for i in range(8))
    def row(name,reference,candidate,relation):
        return dict(name=name,reference=reference,candidate=candidate,known_transform_relation=relation)
    jitter=list(base);p,t,g=jitter[4];jitter[4]=(p,t+1,g)
    insert=base[:4]+((68,base[3][1]+24,12),)+base[4:]
    delete=base[:4]+base[5:]
    alter=list(base);p,t,g=alter[4];alter[4]=(p+1,t,g)
    return [
        row('identical_distinctive',base,base,'exact artificial identity'),
        row('transpose_plus5',base,tuple((p+5,t,g) for p,t,g in base),'uniform pitch transposition'),
        row('tempo_metadata_only',base,base,'ticks identical; externaltempo doubles, not represented by these descriptors'),
        row('duration_scale2',base,tuple((p,t*2,g*2) for p,t,g in base),'all onset deltas/gates doubled; distinct from metadata-only tempo change'),
        row('onset_jitter1tick',base,tuple(jitter),'one onset shifted1tick'),
        row('gate_jitter1tick',base,tuple((p,t,g+int(i==4)) for i,(p,t,g) in enumerate(base)),'one gate extended1tick'),
        row('insert_note',base,insert,'one extra artificial note inserted'),
        row('delete_note',base,delete,'one artificial note removed; candidatebelow8note support'),
        row('alter_one_pitch',base,tuple(alter),'one pitch raised1semitone'),
        row('shift_origin',base,tuple((p,t+1000,g) for p,t,g in base),'global onset origin offset'),
        row('common_scale_different_rhythm',scale,tuple((p,120*i,30+10*i) for i,(p,t,g) in enumerate(scale)),'same authored scale contour,different rhythm; no legal label'),
        row('common_repeat_different_rhythm',repeated,tuple((67,120*i,30+10*i) for i in range(8)),'same constant-pitch contour atdifferentpitch/rhythm; no legal label'),
        row('common_scale_scaled',scale,tuple((p+3,t*2,g*2) for p,t,g in scale),'transposed/scaled common pattern; normalized matchingnotdistinctiveness'),
        row('seven_note_identity',base[:7],base[:7],'identical butbothbelow8note support'),
        row('match_embedded_longer',base,((70,0,50),)+tuple((p,t+96,g) for p,t,g in base)+((59,1200,50),),'exact8note core embedded withprefix/suffix'),
    ]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise ValueError('new output required')
    root=Path(__file__).resolve().parents[1]
    inputs=fixtures() # authored synthetic transforms only, no scoring yet
    plan=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),scope='Cycle20 synthetic sensitivity experiment only, no real-source admission/scoring',
        fixtures=[dict(name=x['name'],known_transform_relation=x['known_transform_relation']) for x in inputs],
        metrics=['existing exact8pitchinterval set intersectioncount','existing wholeinterval normalized Levenshtein',
                 'exact8(intervals,7onsetdeltas,8gates)','samewindow withonsetdeltas/gates dividedbyfirstpositiveonsetdelta'],
        denominators='Matches countdistinctwindow signatures, not occurrence counts. Shorterthan8 haszero eligiblewindows; edit metric maystillmatch.',
        predictions=['Exactinterval ignores transpose/rhythm/tempo; canmatch commoncontours.',
            'Exactrhythm rejects a1tick edit anduniformtimescaling; normalization removesglobaltimescale butnotlocaljitter.',
            'Insertion/deletion maybreak8window coverage; wholeintervaledit respondsgradually.',
            'Tempo-metadataonly changes are invisible because these descriptors omit tempo.'],
        no_threshold_selection=True,no_real_music_loaded=True,no_legal_groundtruth=True,
        truth='Onlyexplicit synthetic transform relations areknown; not plagiarism, perceptualmeaning, uniqueness or musicalquality labels.',
        limitations=['Normalization addsinvariance butalso commonpatterncollisions.',
            'No octaveequivalence, ornamentsensitivity, voice-disambiguation or humantest claimed.',
            'Small handauthoredfixtures cannot calibrate falsepositive/negative rates onrealmusic.'],
        code_sha256={p:digest(root/p) for p in ('tools/probe_similarity_sensitivity.py','tools/compare_onset_gate_models.py')})
    args.output.mkdir(parents=True);(args.output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    rows=[dict(name=x['name'],known_transform_relation=x['known_transform_relation'],measurements=compare(x['reference'],x['candidate'])) for x in inputs]
    result=dict(plan=plan,results=rows,source_music_used=False,thresholds_selected=False,
                conclusion_scope='Sensitivity observations only; no new acceptance policy and no application toTelemann orotherrealworks.')
    (args.output/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(rows,indent=2))


if __name__=='__main__':main()

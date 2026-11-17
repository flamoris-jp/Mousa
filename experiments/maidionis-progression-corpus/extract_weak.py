"""Conservative score-only weak bar labels. Never reads harmony/lyrics text.

No inferred label is expert ground truth. Written order, not repeat unfolding.
Caller owns rights admission and family splits. Rejected bars remain explicit.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

SCHEMA='mousa.score-bar-weak-chords.v1'
POLICY={'coverage_min':.70,'margin_min':.03,'minimum_pitch_classes':3,
        'outside_penalty':.5,'missing_fraction_penalty':.15,'seventh_penalty':.02}
MAJOR=(0,2,4,5,7,9,11)
DURATIONS={'long':Fraction(16),'breve':Fraction(8),'whole':Fraction(4),
           'half':Fraction(2),'quarter':Fraction(1),'eighth':Fraction(1,2),
           '16th':Fraction(1,4),'32nd':Fraction(1,8),'64th':Fraction(1,16),
           '128th':Fraction(1,32)}
IGNORED={'Clef','KeySig','TimeSig','BarLine','Beam','Dynamic','Tempo','StaffText',
         'SystemText','Text','RehearsalMark','Fermata','Spanner','Breath','Ambitus'}
BARRIERS={'startRepeat','endRepeat','Jump','Marker','MeasureRepeat','RepeatMeasure','Volta'}
UNSUPPORTED={'Tuplet','endTuplet','location','tick','move','Tremolo'}


def choose(profile,tonic):
    total=sum(profile)
    if total<=0:return {'label':None,'reason':'silent_bar','coverage':0,'margin':0}
    candidates=[]
    for seventh in (0,1):
        for root in range(7):
            tones={(tonic+MAJOR[(root+k)%7])%12 for k in ((0,2,4,6) if seventh else (0,2,4))}
            coverage=sum(profile[p] for p in tones)/total
            missing=sum(profile[p]==0 for p in tones)/len(tones)
            score=coverage-.5*(1-coverage)-.15*missing-.02*seventh
            candidates.append({'label':root+7*seventh,'root_degree':root,'seventh':bool(seventh),
                               'pitch_classes':sorted(tones),'coverage':float(coverage),'score':float(score)})
    candidates.sort(key=lambda x:(-x['score'],x['label']))
    winner=candidates[0];margin=winner['score']-candidates[1]['score']
    reason=None
    if sum(x>0 for x in profile)<3:reason='fewer_than_three_pitch_classes'
    elif winner['coverage']<.70:reason='low_coverage'
    elif margin<.03:reason='ambiguous_margin'
    return {'label':None if reason else winner['label'],'reason':reason,'coverage':winner['coverage'],
            'margin':margin,'winner':winner,'runner_up':candidates[1]}


def duration(event,width):
    kind=event.findtext('durationType')
    explicit=event.findtext('duration')
    if kind=='measure':
        if event.tag!='Rest':raise ValueError('measure_duration_on_nonrest')
        value=width
    elif kind in DURATIONS:
        dots=int(event.findtext('dots','0'))
        if not 0<=dots<=3:raise ValueError('unsupported_dots')
        value=DURATIONS[kind]*sum((Fraction(1,2**i) for i in range(dots+1)),Fraction(0))
    else:raise ValueError('unsupported_duration_type')
    if explicit is not None and Fraction(explicit)*4!=value:raise ValueError('explicit_duration_mismatch')
    if value<=0:raise ValueError('nonpositive_duration')
    return value


def extract(path):
    path=Path(path)
    if path.suffix.lower()!='.mscx':raise ValueError('only mscx scores accepted')
    raw=path.read_bytes()
    if len(raw)>16*1024*1024 or b'<!DOCTYPE' in raw or b'<!ENTITY' in raw:raise ValueError('unsafe_or_large_XML')
    tree=ET.fromstring(raw)
    if tree.tag!='museScore' or not tree.get('version','').startswith('3'):raise ValueError('MuseScore3_only')
    score=tree.find('Score')
    if score is None:raise ValueError('missing_score')
    copyright_values=[x.text or '' for x in score.findall('metaTag') if x.get('name')=='copyright']
    if copyright_values!=['OpenScore (CC0)']:raise ValueError('missing_or_unsupported_CC0_metadata')
    # Inspect only the exact copyright declaration, never lyrics/annotation/title text.
    for inst in score.findall('./Part/Instrument'):
        for child in inst:
            if 'transpose' in child.tag.lower() and int(child.text or '0')!=0:raise ValueError('transposing_instrument')
    if score.findall('.//InstrumentChange'):raise ValueError('instrument_change')
    if any(x.get('type')=='Volta' for x in score.findall('.//Spanner')) or score.findall('.//Volta'):
        raise ValueError('volta_span_unsupported_entire_score')
    staves=score.findall('Staff')
    if not staves:raise ValueError('no_score_staves')
    measures=[s.findall('Measure') for s in staves]
    if len({len(x) for x in measures})!=1 or not measures[0]:raise ValueError('staff_measure_mismatch')
    keys=[];meters=[]
    for staff in measures:
        for index,m in enumerate(staff):
            for k in m.findall('.//KeySig'):
                value=k.findtext('accidental')
                if value is None or any(x.tag not in ('accidental','mode','showCourtesy','forInstrumentChange','visible') for x in k):raise ValueError('unsupported_key_signature')
                value=int(value)
                if not -7<=value<=7:raise ValueError('key_signature_range')
                keys.append((index,value))
            for ts in m.findall('.//TimeSig'):
                n=int(ts.findtext('sigN','0'));d=int(ts.findtext('sigD','0'))
                if not 1<=n<=12 or d not in (2,4,8,16):raise ValueError('unsupported_meter')
                meters.append((index,n,d))
    if not keys or min(i for i,v in keys)!=0 or len({v for i,v in keys})!=1:raise ValueError('missing_or_changing_key')
    if not meters or min(i for i,n,d in meters)!=0 or len({(n,d) for i,n,d in meters})!=1:raise ValueError('missing_or_changing_meter')
    fifths=keys[0][1];tonic=7*fifths%12;n,d=meters[0][1:];normal=Fraction(4*n,d)
    bars=[];score_tick=Fraction(0)
    for index in range(len(measures[0])):
        group=[s[index] for s in measures];widths=[Fraction(m.get('len'))*4 if m.get('len') else normal for m in group]
        reasons=[];profile=[Fraction(0)]*12;voice_lengths=[];notehead_count=0
        if len(set(widths))!=1:raise ValueError('staff_bar_width_mismatch')
        width=widths[0]
        if width<=0 or width>48:raise ValueError('bar_width_range')
        if width!=normal:reasons.append('irregular_or_pickup_bar')
        for m in group:
            tags={x.tag for x in m.iter()}
            if tags&BARRIERS:reasons.append('repeat_or_jump_boundary')
            # Spanner next/prev/location references do not move the voice cursor.
            timing_tags={x.tag for voice in m.findall('voice') for x in voice}
            timing_tags.update(x.tag for chord in m.findall('./voice/Chord') for x in chord)
            if timing_tags&UNSUPPORTED or any('grace' in tag.lower() or 'acciaccatura' in tag.lower() or 'appoggiatura' in tag.lower() for tag in tags):reasons.append('unsupported_timing_construct')
            if any(x.tag not in {'voice','LayoutBreak','no','irregular','stretch','breakMultiMeasureRest','vspacerDown','vspacerUp','startRepeat','endRepeat'} for x in m):reasons.append('unsupported_measure_element')
            for voice in m.findall('voice'):
                cursor=Fraction(0)
                for event in voice:
                    if event.tag in IGNORED or event.tag=='Harmony':continue # do not read annotation text
                    if event.tag not in ('Chord','Rest'):
                        reasons.append('unsupported_voice_element:'+event.tag);continue
                    try:
                        length=duration(event,width)
                        if event.tag=='Chord':
                            notes=event.findall('Note')
                            if not notes:raise ValueError('empty_chord')
                            for note in notes:
                                pitch=int(note.findtext('pitch','-1'))
                                if not 0<=pitch<=127:raise ValueError('pitch_range')
                                profile[pitch%12]+=length;notehead_count+=1
                        cursor+=length
                    except (ValueError,ZeroDivisionError):reasons.append('invalid_event_duration_or_pitch')
                voice_lengths.append(str(cursor))
                if cursor!=width:reasons.append('voice_does_not_fill_bar')
        decision=choose(profile,tonic) if not reasons else {'label':None,'reason':'structural_rejection'}
        bars.append({'measure_index':index,'score_start_qb':str(score_tick),'width_qb':str(width),
                     'pitch_duration_qb':[str(x) for x in profile],'voice_lengths_qb':voice_lengths,'notehead_count':notehead_count,
                     'structural_reasons':sorted(set(reasons)),**decision})
        score_tick+=width
    return {'schema':SCHEMA,'source_sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),
            'score_copyright_marker':'OpenScore (CC0)','musescore_format':tree.get('version'),'key_fifths':fifths,'major_orientation_tonic_pc':tonic,'meter':[n,d],
            'policy':POLICY,'bars':bars,'accepted_bars':sum(r['label'] is not None for r in bars),
            'limitations':['weak deterministic bar summary, not expert chord truth','major key-signature orientation, not inferred mode/local key',
                          'score durations across staves; not performance durations','written measure order; no repeat unfolding',
                          'null bars must break all learning histories','rights admission remains caller responsibility']}


def main():
    p=argparse.ArgumentParser();p.add_argument('score',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    result=extract(a.score)
    with a.out.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
if __name__=='__main__':main()

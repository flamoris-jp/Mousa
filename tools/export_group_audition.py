"""Private five-field MIDI and common-gain analytic PCM; no listening ratings."""
from array import array
from hashlib import sha256
from math import sin,pi,log10,sqrt,isfinite
from pathlib import Path
import json,sys,wave,subprocess,time
from mousa.overlap_midi import OverlapMelody,read_midi,write_midi
from mousa.tick_midi import TickNote

TOTAL=9216
RATE=22050
FIELDS={'start','end','pitch','velocity','release_velocity'}


def digest(path):return sha256(path.read_bytes()).hexdigest()


def melody_from_rows(rows):
    if type(rows) is not list or not 1<=len(rows)<=256:raise ValueError('bounded nonempty notes required')
    for n in rows:
        if type(n) is not dict or set(n)!=FIELDS or any(type(v) is not int for v in n.values()):raise ValueError('allfiveintegerfields required')
        if not 0<=n['start']<n['end']<=TOTAL or not 0<=n['pitch']<=127 or not 1<=n['velocity']<=127 or not 0<=n['release_velocity']<=127:raise ValueError('note field out of bounds')
    for n in rows:
        active=[v for v in rows if v['start']<=n['start']<v['end']]
        if len(active)>3 or len({v['pitch'] for v in active})!=len(active):raise ValueError('polyphony or samepitch overlap')
    notes=tuple(sorted((TickNote(**n) for n in rows),key=lambda n:(n.start,n.end,n.pitch)))
    ev=[]
    for i,n in enumerate(rows):
        ev.extend(((n['start'],1,i,'note_on',n['pitch'],n['velocity']),(n['end'],0,i,'note_off',n['pitch'],n['release_velocity'])))
    stream=((0,'program',0,0),)+tuple((t,k,p,v) for t,_,i,k,p,v in sorted(ev))
    return OverlapMelody(notes,TOTAL,(6,8),ppq=384,channel_events=stream)


def analytic_pcm(notes):
    scale=RATE*.5/384;frames=12*RATE;mix=array('d',[0.])*frames
    for note in notes:
        start=round(note.start*scale);end=round(note.end*scale);length=end-start
        freq=440*2**((note.pitch-69)/12)
        if length<1 or 2*freq>=RATE/2:raise ValueError('sample resolution or Nyquist bound')
        attack=min(round(.005*RATE),max(1,length//2))
        release=min(round((.005+.030*note.release_velocity/127)*RATE),max(1,length//2))
        gain=.18*note.velocity/127
        for i in range(length):
            envelope=min(1.,i/attack,(length-1-i)/release)
            phase=2*pi*freq*i/RATE
            mix[start+i]+=gain*envelope*(.8*sin(phase)+.2*sin(2*phase))
    if any(not isfinite(v) for v in mix):raise ValueError('nonfinite PCM')
    peak=max(map(abs,mix),default=0.);rms=sqrt(sum(v*v for v in mix)/frames)
    clipped=sum(abs(v)>=1 for v in mix)
    if clipped:raise ValueError('clipping;no hidden normalization')
    pcm=array('h',(round(v*32767) for v in mix))
    nonzero=sum(v!=0 for v in pcm)
    if sys.byteorder!='little':pcm.byteswap()
    return pcm.tobytes(),dict(rate=RATE,channels=1,pcm_bits=16,frames=frames,duration_seconds=12,
        common_gain=.18,per_file_normalization=False,peak_linear=peak,rms_linear=rms,
        peak_dbfs=20*log10(peak) if peak else None,rms_dbfs=20*log10(rms) if rms else None,
        clipped_samples=clipped,nonzero_pcm_samples=nonzero,max_endpoint_rounding_samples=.5,
        release_mapping='Declared own simple timbre:release_velocity controls in-gate5..35ms ramp,not a standard instrument interpretation.')


def write_wav(path,data):
    with wave.open(str(path),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(data)


def verify_midi(path,expected):
    parsed=read_midi(path,1)
    if parsed.notes!=expected.notes or parsed.total_ticks!=TOTAL or parsed.source_total_ticks!=TOTAL or parsed.ppq!=384 or parsed.meter!=(6,8) or parsed.tempo_map!=((0,500000),):raise ValueError('MIDI fivefields/timeline/convention mismatch')
    if parsed.channel_events!=expected.channel_events:raise ValueError('modeled event order mismatch')
    return parsed


def export(source,expected_sha,out,label,cantabile):
    if out.exists() or label not in 'ABCD' or len(label)!=1:raise ValueError('new private directory and opaque label required')
    if source.stat().st_size>100000 or digest(source)!=expected_sha:raise ValueError('source bound/hash')
    obj=json.loads(source.read_text())
    if type(obj) is not dict or set(obj)!= {'notes','groups'}:raise ValueError('generated group JSON required')
    model=melody_from_rows(obj['notes']);out.mkdir(parents=True)
    midi=out/f'{label}.mid';write_midi(model,midi);parsed=verify_midi(midi,model)
    roundtrip=out/'internal-roundtrip.mid';write_midi(parsed,roundtrip)
    if midi.read_bytes()!=roundtrip.read_bytes():raise ValueError('internal MIDI byte parity')
    project=out/'isolated-cantabile.json';native=out/'cantabile-roundtrip.mid'
    calls=[]
    for args in [('import-midi',str(midi),str(project)),('export-midi',str(project),str(native))]:
        r=subprocess.run([str(cantabile),*args],capture_output=True,text=True,timeout=20)
        calls.append(dict(operation=args[0],returncode=r.returncode))
        if r.returncode:raise RuntimeError('isolated Cantabile operation failed')
    verify_midi(native,model)
    pcm,audio=analytic_pcm(parsed.notes);wav=out/f'{label}.wav';write_wav(wav,pcm)
    pcm2,audio2=analytic_pcm(parsed.notes);repeat=out/'repeat.wav';write_wav(repeat,pcm2)
    if audio!=audio2 or wav.read_bytes()!=repeat.read_bytes():raise ValueError('PCM repeat mismatch')
    if digest(source)!=expected_sha:raise ValueError('source changed')
    report=dict(label=label,notes=len(model.notes),source_hash_checked=True,source_unchanged=True,
        midi_sha256=digest(midi),wav_sha256=digest(wav),midi_bytes=midi.stat().st_size,wav_bytes=wav.stat().st_size,
        note_five_fields_and_order_verified=True,internal_midi_byte_parity=True,cantabile_operations=calls,
        cantabile_roundtrip_fields_order_metadata_eot=True,cantabile_midi_byte_equal=midi.read_bytes()==native.read_bytes(),
        wav_repeat_byte_equal=True,audio=audio,role='generated-private/listening-only/not-training',
        limitations=['Export6/8/8bars/120BPM convention,not learnedmeter.','Analytic own oscillator,not Cantabile audio or a real-instrument recording.','No human listening or rating performed.','Private candidate only,no public-release clearance.'])
    (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n');return report


def run(planpath,keypath,source_dir,output,cantabile):
    if output.exists():raise ValueError('new private run directory required')
    plan=json.loads(planpath.read_text())
    if digest(keypath)!=plan['private_label_key_sha256']:raise ValueError('private label key changed')
    root=Path(__file__).resolve().parents[1]
    for f,h in plan['frozen_hashes'].items():
        if digest(root/f)!=h:raise ValueError('frozen dependency changed')
    if digest(cantabile)!=plan['cantabile_executable_sha256']:raise ValueError('Cantabile binary changed')
    key=json.loads(keypath.read_text());expected={r['arm']:r for r in plan['sources']}
    prior=json.loads((root/'experiments/2026-11-12-gate-context-results.json').read_text())
    for label,entry in key['labels'].items():
        row=next(r for r in prior['conditions'][entry['arm']]['outputs'] if r['seed']==0)
        if row['status']!='complete' or row['copy_matches'] or row['private_sha256']!=expected[entry['arm']]['source_sha256']:raise ValueError('source not cleared by fixed result')
    output.mkdir();start=time.process_time();reports=[]
    for label,entry in key['labels'].items():
        if time.process_time()-start>60:raise RuntimeError('CPU60 exceeded before next bounded clip')
        source=source_dir/entry['source_filename'];reports.append(export(source,expected[entry['arm']]['source_sha256'],output/label,label,cantabile))
    result=dict(plan_sha256=digest(planpath),clips=reports,cpu_seconds=time.process_time()-start,
        roles='generated-private/listening-only/not-training',selection='Deterministic seed0 chosen after existing experiment results;not preregistered before generation.',human_ratings=None)
    (output/'verification.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    for k in ('plan','key','source-dir','output','cantabile'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();print(json.dumps(run(a.plan,a.key,a.source_dir,a.output,a.cantabile),indent=2))

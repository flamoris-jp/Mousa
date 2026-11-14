"""Read-only reanalysis of nine already-observed Cycle45 outputs; never fit/generate."""
import hashlib,json
from pathlib import Path
from statistics import mean,median
MODES=('raw','equal_work','equal_family')
SEEDS=(45000,45001,45002)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def summarize(rows):
    if len(rows)!=3 or [r['seed'] for r in rows]!=list(SEEDS):raise ValueError('fixed observed cohort')
    if any(r['status']!='complete' for r in rows):raise ValueError('retain explicit failed cohort, no complete-only substitution')
    fields={
      'notes':[r['metrics']['notes'] for r in rows],
      'distinct_pitches':[r['metrics']['distinct_pitches'] for r in rows],
      'mean_abs_event_pitch_interval':[r['metrics']['mean_abs_pitch_interval'] for r in rows],
      'above_octave_fraction':[r['metrics']['above_octave_fraction'] for r in rows],
      'silence_ticks':[r['timeline']['silence_ticks'] for r in rows],
      'leading_silence_ticks':[r['timeline']['leading_silence_ticks'] for r in rows],
      'attempts':[r['attempts'] for r in rows]}
    return {k:dict(n=len(v),mean=mean(v),median=median(v),minimum=min(v),maximum=max(v)) for k,v in fields.items()}
def diagnose(source,out):
    if out.exists():raise ValueError('new output only')
    report=json.loads((source/'report.json').read_text());result={};hashes={}
    for mode in MODES:
        name='18_'+mode;rows=report['conditions'][name]['outputs']
        public=[]
        for r in rows:
            p=source/f"{name}-{r['seed']}-private.json";v=json.loads(p.read_text());hashes[p.name]=sha(p)
            if len(v['notes'])!=r['metrics']['notes'] or min(n['start'] for n in v['notes'])!=r['timeline']['leading_silence_ticks']:raise ValueError('saved output/report mismatch')
            public.append(dict(seed=r['seed'],status=r['status'],notes=r['metrics']['notes'],distinct_pitches=r['metrics']['distinct_pitches'],leading_silence_ticks=r['timeline']['leading_silence_ticks'],silence_ticks=r['timeline']['silence_ticks'],mean_abs_event_pitch_interval=r['metrics']['mean_abs_pitch_interval'],above_octave_fraction=r['metrics']['above_octave_fraction'],historical_22ref_copy_matches=r['copy_matches']))
        result[mode]=dict(summary=summarize(rows),outputs=public)
    value=dict(schema='mousa-cycle49-observed-weighting-diagnostic-v1',source_report_sha256=sha(source/'report.json'),source_plan_sha256=report['plan_sha256'],private_output_sha256=hashes,conditions=result,
        role='Exploratory reanalysis: nine condition-output instances, three previously observed seeds, same18work corpus. Not nine independent music samples. No new fit/generation/prediction.',
        copy='Historical22refs only; Dvorak became observed later and has NOT been screened against these outputs here. Do not claim current23ref clearance.',
        limits=['No causal paired-draw interpretation: integer scaling alters RNG consumption across weights.','Leading silence alone changes available output horizon and can depress counts; never trim source or drop sparse output.','Global event pitch intervals include polyphonic ordering, not inferred melodic voice.','NLL on Dvorak is timing-only and cannot rank these outputs for musical charm.','A-D human feedback unanswered.'])
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(value,indent=2)+'\n');return value
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True);a.add_argument('--output',type=Path,required=True);v=a.parse_args();diagnose(v.source,v.output)

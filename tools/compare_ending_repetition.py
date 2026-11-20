"""Existing-pool endpoint-repetition ablation, never new predictive evaluation."""
import argparse
import hashlib
import json
from pathlib import Path
from mousa.overlap_midi import read_midi
from mousa.settling_ending import ending_features
from compare_context_onset_gate import metrics,summarize


def qualifying(notes,*,step_only=False):
    f=ending_features(notes)
    distinct=len(notes)>=2 and notes[-1]['start']>notes[-2]['start']
    return f['eligible'] and distinct and (not step_only or f['final_abs_interval'] in (1,2))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidates',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('new output required')
    root=Path(__file__).resolve().parents[1];source=root/'experiments/2026-11-12-settling-ending-results.json'
    old=json.loads(source.read_text());groups=[]
    for group in old['groups']:
        rows=[]
        for candidate in group['candidates']:
            if candidate['status']!='complete':continue
            path=a.candidates/f'candidate-{candidate["seed"]}.mid'
            if hashlib.sha256(path.read_bytes()).hexdigest()!=candidate['midi_sha256']:raise ValueError('candidate hash differs')
            m=read_midi(path,1)
            # Generated event order matters; recover note-on sequence explicitly.
            by_key={(n.start,n.pitch):n for n in m.notes}
            notes=[dict(start=t,end=by_key[(t,v)].end,pitch=v) for t,k,v,vel in m.channel_events if k=='note_on']
            rows.append(dict(seed=candidate['seed'],status='complete',metrics=metrics(notes,9216),
                final_interval=ending_features(notes)['final_abs_interval'],
                repeated_allowed=qualifying(notes),step_only=qualifying(notes,step_only=True)))
        groups.append(dict(group=group['group'],candidates=rows,
            selected={method:next((r['seed'] for r in rows if r[method]),None) for method in ('repeated_allowed','step_only')}))
    summaries={}
    for method in ('repeated_allowed','step_only'):
        selected=[next(r for r in g['candidates'] if r['seed']==g['selected'][method]) for g in groups if g['selected'][method] is not None]
        means,den=summarize(selected)
        summaries[method]=dict(selected_groups=len(selected),missing_groups=10-len(selected),means=means,metric_denominators=den,
            candidate_examinations=sum(4 if g['selected'][method] is None else g['selected'][method]-4*g['group']+1 for g in groups))
    report=dict(scope='Observed-pool structural selection only; no musicalappeal claim',groups=groups,summary=summaries,
        source_report_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        code_sha256={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ['tools/compare_ending_repetition.py','experiments/2026-11-12-ending-repetition-plan.json']},
        warning='Different selected-group denominators; do not present their means as an unbiased treatment effect. Repeated final tones can be musically appropriate.')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(summaries))
if __name__=='__main__':main()

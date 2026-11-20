"""Reanalyse observed candidates with explicit diversity floors, not new scoring."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from statistics import mean


def choose(candidates,control):
    c=control['features']
    eligible=[r for r in candidates if r['status']=='complete' and
        r['features']['unique_pitches']>=c['unique_pitches'] and
        Fraction(r['features']['zero_interval_fraction'])<=Fraction(c['zero_interval_fraction'])]
    if not eligible:raise ValueError('control absent from eligible set')
    return min(eligible,key=lambda r:Fraction(r['features']['leap_fraction'])),len(eligible)


def run(source):
    rows=[]
    for group in source['groups']:
        valid=[r for r in group['candidates'] if r['status']=='complete']
        if not valid:
            rows.append(dict(group=group['group'],status='empty'));continue
        control=next(r for r in valid if r['seed']==group['control_seed'])
        selected,count=choose(valid,control)
        unconstrained=next(r for r in valid if r['seed']==group['selected_seed'])
        rows.append(dict(group=group['group'],status='complete',eligible_count=count,
            control=control,unconstrained=unconstrained,constrained=selected))
    complete=[r for r in rows if r['status']=='complete']
    summary={method:{k:float(mean(Fraction(r[method]['features'][k]) for r in complete))
        for k in complete[0][method]['features']} for method in ('control','unconstrained','constrained')} if complete else {}
    return dict(groups=rows,summary=summary,complete_groups=len(complete),
        only_control_eligible=sum(r['eligible_count']==1 for r in complete),
        constrained_changes_from_control=sum(r['control']['seed']!=r['constrained']['seed'] for r in complete),
        scope='Observed cycle10 exploratory reanalysis; diversity proxies are constraints, not appeal labels')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('new output required')
    root=Path(__file__).resolve().parents[1];path=root/'experiments/2026-11-12-smoothness-results.json'
    report=run(json.loads(path.read_text()));report['source_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    report['code_sha256']={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ['tools/compare_diversity_selection.py','experiments/2026-11-12-diversity-plan.json']}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['summary']))

"""Read-only posthoc knownpool/training density diagnosis, no model fit."""
from pathlib import Path
import json,hashlib
from compare_weighted_maple_cycle45 import read,ROOT
from mousa.silence_segments_cycle46 import segments
from mousa.group_timeline_metrics import timeline_metrics
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def describe(notes,groups,target):
    timeline=timeline_metrics(notes,target);seg=segments(notes,groups)
    return dict(notes=len(notes),groups=len(groups),target_ticks=target,timeline=timeline,segment_group_counts=[len(s) for s in seg['segments']],qualifying_silence_lengths=[b['silence_ticks'] for b in seg['boundaries']],leading_fraction=timeline['leading_silence_ticks']/target)
def run(output):
    if output.exists():raise ValueError('retain prior')
    train,_,seq,sources,_,_=read();training={}
    for i,m in train.items():
        notes=[dict(start=n.start,end=n.end) for n in m.notes];groups=[];onset=0
        for delta,anchor,t in seq[i]:
            onset+=delta;groups.append(dict(onset=onset,template=t))
        training[i]=describe(notes,groups,m.total_ticks)
    resultpath=ROOT/'experiments/2026-11-12-weighted-maple-cycle45-results.json';old=json.loads(resultpath.read_text());generated={}
    for label,c in old['conditions'].items():
        generated[label]=[]
        for row in c['outputs']:
            p=ROOT.parent/f'mousa-cycle45-maple-initial/{label}-{row["seed"]}-private.json'
            if digest(p)!=row['private_sha256']:raise ValueError('private candidate changed')
            g=json.loads(p.read_text())
            generated[label].append(dict(seed=row['seed'],status=row['status'],private_sha256=digest(p),**describe(g['notes'],g['groups'],9216)))
    out=dict(kind='posthoc_readonly_existing21_and_training18_no_fit',source_result_sha256=digest(resultpath),training=training,generated=generated,originals_unchanged=all(digest(Path(p))==h for p,h in sources.items()),limitations=['Counts and occupiedtime are descriptive, not phrase annotations or appeal.','Originalsource horizons and meters differ; raw source note counts not normalized8bar comparable.','Threshold192 is arbitrary halfquarter atPPQ384, no selection of threshold from outcomes.','Known generatedpool, not new randomdraw or fresh music.'])
    output.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.output)

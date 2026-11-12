import sys,json,hashlib,time
from pathlib import Path
from statistics import mean,median
import argparse
a=argparse.ArgumentParser();a.add_argument('--source', type=Path, required=True);a.add_argument('--output', type=Path, required=True)
args=a.parse_args()
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from rarefaction_cycle50 import expected_distinct
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=R/'experiments/2026-11-13-rarefaction-cycle50-plan.json'
ledger=R/'experiments/2026-11-12-weighting-cycle49-reproduction.json'
hashes=json.loads(ledger.read_text())['private_sha256']
assert len(hashes)==36
rows=[];start=time.process_time()
for mode in ('raw','equal_work','equal_family'):
 for seed in range(49000,49012):
  p=args.source/f'{mode}-{seed}-private.json'
  h=sha(p);assert h==hashes[p.name]
  data=json.loads(p.read_text());pitches=[n['pitch'] for n in data['notes']]
  values={}
  for k in [4,8,16]:
   result=expected_distinct(pitches,k)
   values[str(k)]=dict(status='eligible' if result is not None else 'insufficient_notes',expected_distinct=float(result) if result is not None else None,exact=str(result) if result is not None else None)
  rows.append(dict(mode=mode,seed=seed,source_sha256=h,n=len(pitches),observed_distinct=len(set(pitches)),rarefaction=values))
summary={}
for mode in ('raw','equal_work','equal_family'):
 selected=[r for r in rows if r['mode']==mode];s={}
 for k in [4,8,16]:
  v=[r['rarefaction'][str(k)]['expected_distinct'] for r in selected if r['rarefaction'][str(k)]['status']=='eligible']
  s[str(k)]=dict(total=12,eligible=len(v),ineligible=12-len(v),mean=mean(v) if v else None,median=median(v) if v else None)
 summary[mode]=s
out=dict(schema='mousa-cycle50-observed-rarefaction-v1',plan_sha256=sha(plan),reproduction_ledger_sha256=sha(ledger),code_sha256=sha(R/'tools/rarefaction_cycle50.py'),rows=rows,summary=summary,cpu_seconds=time.process_time()-start,limits=json.loads(plan.read_text())['interpretation'],source_hashes_after={p.name:sha(p) for p in sorted(args.source.glob('*-private.json'))})
assert out['source_hashes_after']==hashes
p=args.output;assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(summary,indent=2))

"""Aggregate persisted growth versions without selecting a winner."""
import argparse,json,hashlib,statistics,math
from pathlib import Path
from collections import defaultdict

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def aggregate(rows):
 out={}
 for task in ('pitch','rhythm'):
  groups=defaultdict(list)
  for row in rows:
   if row['task']==task:groups[row['family']].append(row)
  per=[{'family':f,'nll':statistics.mean(r['nll'] for r in rs),'accuracy':statistics.mean(r['prediction']==r['target'] for r in rs),'n':len(rs)} for f,rs in sorted(groups.items())]
  out[task]={'families':len(per),'targets':sum(x['n'] for x in per),'family_macro_nll':statistics.mean(x['nll'] for x in per),'family_macro_accuracy':statistics.mean(x['accuracy'] for x in per),'per_family':per}
 return out

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();data=json.loads((a.root/'data.json').read_text());pin=json.loads(Path(__file__).with_name('input-pin.json').read_text());assert sha(a.root/'data.json')==pin['data_sha256'];out={'schema':'mousa-persistent-music-growth-v1','data_sha256':pin['data_sha256'],'test_status':'historical16 observed, no fresh generalization or musical quality claim','versions':[]};previous=None
 for name in ('v1','v2'):
  d=a.root/name;m=json.loads((d/'manifest.json').read_text());r=json.loads((d/'results.json').read_text());assert m['complete'] and m['data_sha256']==pin['data_sha256']
  for file,key in [('weights.pt','weights_sha256'),('optimizer.pt','optimizer_sha256'),('results.json','results_sha256')]:assert sha(d/file)==m[key]
  for phase in ('initial_test','final_test'):
   assert [(x['family'],x['target_index'],x['task'],x['target']) for x in r[phase]]==[(x['family'],x['target_index'],x['task'],x['label']) for x in data['test']]
   assert all(math.isfinite(x['nll']) and 0<=x['prediction']<(25 if x['task']=='rhythm' else 49) for x in r[phase])
  assert len(r['losses'])==256 and all(math.isfinite(x) for x in r['losses']) and r['embedding_delta_l1']>0
  assert r['checkpoint_reload_parameters_exact'] and r['checkpoint_reload_optimizer_exact'] and r['checkpoint_reload_logits_exact']
  if previous is not None:assert previous==r['initial_test'];assert m['resume']['fresh_process_probe_exact'] and m['resume']['optimizer_steps_restored']==256
  previous=r['final_test'];out['versions'].append({'version':name,'completed_epochs':m['completed_epochs'],'total_steps':m['total_steps'],'phase_steps':r['steps'],'cpu_seconds':r['cpu_seconds'],'initial':aggregate(r['initial_test']),'final':aggregate(r['final_test']),'model_config':m['model_config'],'weights_sha256':m['weights_sha256'],'optimizer_sha256':m['optimizer_sha256'],'model_bytes':(d/'weights.pt').stat().st_size,'optimizer_bytes':(d/'optimizer.pt').stat().st_size,'reload_exact':True,'resume':m['resume']})
 with (a.root/'summary-private.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
 for v in out['versions']:
  for phase in ('initial','final'):
   for task in ('pitch','rhythm'):v[phase][task].pop('per_family')
 with (a.root/'summary-public.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()

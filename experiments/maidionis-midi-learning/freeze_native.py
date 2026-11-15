"""Adapt rights-checked private windows to fixed native harness; no neural scores."""
import json,hashlib,random,copy,math
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone
p=Path(__file__).parent
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
def save(n,v):
 with (p/n).open('x') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
d=json.loads((p/'midi-dataset-private.json').read_text());plan=json.loads((p/'midi-plan.json').read_text());plan.update(frozen_utc=datetime.now(timezone.utc).isoformat(),supersedes_plan_sha256=sha(p/'midi-plan.json'),superseded_reason='Static preparation before neural outcomes: drop18shuffle arm to bound compute; specify native harness schema and batching.',conditions=['train18_ordered','train128_ordered','train128_context_permuted'],maximum_cpu_seconds=300,batching='100 uniform-with-replacement batches32 using random.Random(seed+54000); identical128 indices for ordered/shuffled; 18 same RNG seed mapped to18window count.',permutation='Per window SHA256(seed:family:target_index) as random.Random seed; only8content tokens permuted, CLS and label unchanged; test ordered always.',native_harness_sha256=sha(p/'midi_diagnostic.cpp'),freeze_script_sha256=sha(Path(__file__)),private_windows_sha256=sha(p/'midi-dataset-private.json'),metrics='per-family NLL and accuracy, family-macro primary; pooled secondary; initial/final test and final train; finite gradient and first parameter update')
save('plan.json',plan)
for rows in d.values():
 for r in rows:r['label']=r.pop('target')
arms=[]
for seed in [42,43,44]:
 for condition,key in [('train18_ordered','train18'),('train128_ordered','train128'),('train128_context_permuted','train128')]:
  rows=copy.deepcopy(d[key]);rng=random.Random(seed+54000);batches=[[rng.randrange(len(rows)) for _ in range(32)] for _ in range(100)]
  if condition.endswith('permuted'):
   for r in rows:
    content=r['input'][1:];h=hashlib.sha256(f"{seed}:{r['family']}:{r['target_index']}".encode()).hexdigest();random.Random(h).shuffle(content);r['input']=[1]+content
  arms.append(dict(condition=condition,seed=seed,train=rows,batches=batches))
save('data.json',dict(test=d['test'],arms=arms))
results=[]
for key in ['train18','train128']:
 rows=d[key];marg=Counter(r['label'] for r in rows);local=[defaultdict(Counter),defaultdict(Counter)]
 for r in rows:
  for n in [1,2]:local[n-1][tuple(v-2 for v in r['input'][-n:])][r['label']]+=1
 for model in ['uniform','unigram','trigram']:
  scores=[]
  for r in d['test']:
   probs=[1/49]*49 if model=='uniform' else [(marg[i]+1/49)/(len(rows)+1) for i in range(49)]
   if model=='trigram':
    for n in [1,2]:
     c=local[n-1].get(tuple(v-2 for v in r['input'][-n:]),{});z=sum(c.values());probs=[(c.get(i,0)+4*probs[i])/(z+4) for i in range(49)]
   scores.append({'family':r['family'],'target_index':r['target_index'],'nll':-math.log(probs[r['label']]),'correct':int(max(range(49),key=lambda i:probs[i])==r['label'])})
  fam={}
  for r in scores:fam.setdefault(r['family'],[]).append(r)
  results.append({'condition':key,'model':model,'family_count':len(fam),'windows':len(scores),'family_macro_nll':sum(sum(r['nll'] for r in v)/len(v) for v in fam.values())/len(fam),'family_macro_accuracy':sum(sum(r['correct'] for r in v)/len(v) for v in fam.values())/len(fam),'rows':scores})
save('baselines.json',{'note':'Smoothed window-target counts only, backoff totalmass4/unigramtotalmass1; exactly same selected histories and targets. Already-observed Cycle53 test, no tuning.','results':results})
assert all(a['batches']==b['batches'] for a,b in zip(arms[1::3],arms[2::3]))
save('native-freeze-audit.json',{'frozen_before_neural_fit':True,'seed_matching_128_batches':True,'private_dataset_sha256':sha(p/'data.json'),'plan_sha256':sha(p/'plan.json'),'source_audit_sha256':sha(p/'midi-preparation-audit.json'),'baseline_sha256':sha(p/'baselines.json'),'no_sa':True,'rights_and_source_hashes_verified':True,'already_observed_test':True,'data_publication_allowed':False,'counts':{k:len(v) for k,v in d.items()}})
print(json.dumps(json.loads((p/'native-freeze-audit.json').read_text()),indent=2))

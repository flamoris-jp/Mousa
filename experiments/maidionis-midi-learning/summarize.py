import json,sys,statistics,collections,hashlib,pathlib
p=pathlib.Path(sys.argv[1]);r=json.loads(p.read_text())
def score(rows):
 g=collections.defaultdict(list)
 for x in rows:g[x['family']].append(x)
 f=[{'family':k,'n':len(v),'nll':statistics.mean(x['nll'] for x in v),'accuracy':statistics.mean(x['prediction']==x['target'] for x in v)} for k,v in g.items()]
 return {'families':len(f),'events':len(rows),'family_macro_nll':statistics.mean(x['nll'] for x in f),'family_macro_accuracy':statistics.mean(x['accuracy'] for x in f),'pooled_nll':statistics.mean(x['nll'] for x in rows),'pooled_accuracy':statistics.mean(x['prediction']==x['target'] for x in rows),'per_family':f}
o={'cpu_seconds':r['cpu_seconds'],'environment':r['environment'],'raw_result_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'runs':[]}
for run in r['runs']:
 d={k:v for k,v in run.items() if k not in ['initial_test','final_test','final_train']}
 for key in ['initial_test','final_test','final_train']:d[key]=score(run[key])
 o['runs'].append(d)
json.dump(o,open(sys.argv[2],'w'),indent=2)
for r in o['runs']:print(r['condition'],r['seed'],'NLL',r['initial_test']['family_macro_nll'],'->',r['final_test']['family_macro_nll'],'acc',r['final_test']['family_macro_accuracy'],'train',r['final_train']['family_macro_nll'])

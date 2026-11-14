import hashlib,itertools,json,pathlib,datetime
root=pathlib.Path(__file__).parent
pairs=sorted(itertools.combinations(range(2,10),2), key=lambda p:hashlib.sha256(('mousa-order-toy-v1:'+','.join(map(str,p))).encode()).hexdigest())
rows={s:[{'pair':list(p),'input':[1,*order],'label':int(order[0]<order[1])} for p in ps for order in (p,p[::-1])] for s,ps in [('train',pairs[:20]),('test',pairs[20:])]}
assert set(v for r in rows['train'] for v in r['pair'])==set(range(2,10))
assert len(rows['train'])==40 and len(rows['test'])==16
assert not ({tuple(r['pair']) for r in rows['train']} & {tuple(r['pair']) for r in rows['test']})
plan={'id':'mousa-maidionis-order-toy-v1','upstream_commit':'c288e92979d5005742a1bc3f86b389eadbc873d3','seeds':[42,43,44],'steps':100,'learning_rate':0.0003,'weight_decay':0.0,'max_grad_norm':1.0,'dropout_milli':0,'vocabulary':10,'controls':[1],'hidden_width':256,'output_width':2,'batch':'all 40 training rows each step','selection':'final step only; no dev or test selection','target':'label1 iff first content ID < second content ID','split':'20 unordered pairs train,8 test; both orientations same split','cpu_threads':1,'maximum_run_cpu_seconds':300,'limitations':['synthetic ordinal-token relation, not MIDI or composition quality','heldout pairs share seen token identities; not unseen pitch vocabulary','native diagnostic optimizer harness calls unmodified Core Model/loss, not full Core education/artifact lifecycle','3 preregistered seeds; no test-driven tuning','pooled permutation invariance predicts at most 50 percent deterministic accuracy on balanced reverse pairs']}
for name,data in [('dataset.json',rows),('plan.json',plan)]:
 p=root/name
 with p.open('x') as f:json.dump(data,f,sort_keys=True,indent=2);f.write('\n')
print(hashlib.sha256((root/'dataset.json').read_bytes()).hexdigest())
print(hashlib.sha256((root/'plan.json').read_bytes()).hexdigest())
